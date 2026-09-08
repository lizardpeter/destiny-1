#!/usr/bin/env python3
"""Recover structured lane-selective EXEC regions from D1 GCN structural IR.

This pass is intentionally narrower than arbitrary SSA. It recognizes the canonical
GCN saveexec/complement/restore form and emits destination-neutral structured regions
that preserve the per-lane predicate boundary. For simple non-nested, non-loop regions
it can also promote exact lane-merge assignments and a bounded conditional-multiplier
pattern useful to both Blender adapters and a Rust/WGSL renderer.

No texture role, visual meaning, or high-level shader intent is inferred.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

PAIR_RE=re.compile(r'^s\[(\d+):(\d+)\]$')
VREG_RE=re.compile(r'^v(\d+)$')
CMP={
 'v_cmp_lt_f32':'<','v_cmp_gt_f32':'>','v_cmp_le_f32':'<=','v_cmp_ge_f32':'>=',
 'v_cmp_eq_f32':'==','v_cmp_neq_f32':'!=','v_cmp_lg_f32':'!=',
 'v_cmp_lt_i32':'<','v_cmp_gt_i32':'>','v_cmp_le_i32':'<=','v_cmp_ge_i32':'>=',
 'v_cmp_eq_i32':'==','v_cmp_neq_i32':'!=','v_cmp_lg_i32':'!=',
 'v_cmp_lt_u32':'<','v_cmp_gt_u32':'>','v_cmp_le_u32':'<=','v_cmp_ge_u32':'>=',
 'v_cmp_eq_u32':'==','v_cmp_neq_u32':'!=','v_cmp_lg_u32':'!=',
}


def prev_def(ins,reg,before):
    for x in reversed(ins[:before]):
        if reg in x.get('defs',[]):return x
    return None


def loop_ranges(ir):
    out=[];by={b['id']:b for b in ir['basic_blocks']}
    for e in ir['control_flow'].get('back_edges',[]):
        a=by[e['to_block']]['start_instruction'];b=by[e['from_block']]['end_instruction']
        out.append({'start_instruction':a,'end_instruction':b,'from_block':e['from_block'],'to_block':e['to_block']})
    return out


def intersects(a,b,r):return not (b<r['start_instruction'] or a>r['end_instruction'])


def cmp_pred(x):
    if not x:return None
    op=x['opcode'];a=x['operands'];sym=CMP.get(op)
    if sym and len(a)>=3 and a[0].startswith('vcc'):
        return {'instruction':x['index'],'opcode':op,'lhs':a[1],'operator':sym,'rhs':a[2],'expression':f'{a[1]} {sym} {a[2]}'}
    return {'instruction':x['index'],'opcode':op,'operands':a,'expression':'WITHHELD_UNSUPPORTED_COMPARE_FORM'}


def vdefs(ins,a,b):
    out={}
    for x in ins[a:b+1]:
        for d in x.get('defs',[]):
            if VREG_RE.match(d):out[d]=x
    return out


def image_rows(ins,a,b):
    out=[]
    for x in ins[a:b+1]:
        if 'image' not in x:continue
        z=x['image'];out.append({'instruction':x['index'],'opcode':x['opcode'],'textures':z.get('textures',[]),'samplers':z.get('samplers',[]),'dmask_channels':z.get('dmask_channels')})
    return out


def simple_assignment(x):return {'instruction':x['index'],'opcode':x['opcode'],'operands':x['operands']}


def conditional_multiplier(merges):
    rows=[];factor=None
    for m in merges:
        t=m['then_assignment'];e=m['else_assignment'];dst=m['register']
        if t['opcode']!='v_mul_f32' or len(t['operands'])!=3:return None
        if e['opcode']!='v_mov_b32' or len(e['operands'])!=2:return None
        if t['operands'][0]!=dst or e['operands'][0]!=dst:return None
        base=e['operands'][1]
        if t['operands'][1]==base:fac=t['operands'][2]
        elif t['operands'][2]==base:fac=t['operands'][1]
        else:return None
        if factor is None:factor=fac
        elif factor!=fac:return None
        rows.append({'output':dst,'base':base,'then_factor':fac})
    return {'kind':'CONDITIONAL_MULTIPLY_OR_PASSTHROUGH','factor_register':factor,'outputs':rows,
            'equation':'output = predicate ? (base * factor) : base'} if rows else None


def computed_or_zero(merges):
    if len(merges)!=1:return None
    m=merges[0];e=m['else_assignment']
    if e['opcode']=='v_mov_b32' and len(e['operands'])==2 and e['operands'][1] in ('0','0.0'):
        return {'kind':'CONDITIONAL_COMPUTED_OR_ZERO','output':m['register'],'then_assignment':m['then_assignment'],
                'equation':'output = predicate ? computed_then_value : 0'}
    return None


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ir',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
    ir=json.load(open(a.ir));viol=[];regions=[]
    try:
        assert ir['status']=='D1_GCN_STRUCTURAL_IR_COMPLETE'
        assert int(ir.get('schema_version',0))>=2,'structural IR v2 required for VCC destination provenance'
        ins=ir['instructions'];loops=loop_ranges(ir)
        for x in ins:
            if x['opcode']!='s_and_saveexec_b64' or len(x['operands'])<2 or not PAIR_RE.match(x['operands'][0]):continue
            saved=x['operands'][0];start=x['index'];restore=None
            for y in ins[start+1:]:
                if y['opcode']=='s_mov_b64' and y['operands'][:2]==['exec',saved]:restore=y['index'];break
                if y['opcode']=='s_and_saveexec_b64' and y['operands'] and y['operands'][0]==saved:break
            if restore is None:continue
            complements=[y['index'] for y in ins[start+1:restore] if y['opcode']=='s_andn2_b64' and y['operands'][:3]==['exec',saved,'exec']]
            complement=complements[-1] if complements else None
            pred=prev_def(ins,'vcc',start);nested=[y['index'] for y in ins[start+1:restore] if y['opcode']=='s_and_saveexec_b64']
            lr=[r for r in loops if intersects(start,restore,r)]
            row={'region_id':len(regions),'saveexec_instruction':start,'saved_exec_register':saved,'restore_instruction':restore,
                 'predicate':cmp_pred(pred),'complement_switch_instruction':complement,'nested_saveexec_instructions':nested,
                 'loop_intersections':lr,'structure':'IF_THEN_ELSE' if complement is not None else 'IF_THEN',
                 'then_range':None,'else_range':None,'then_image_ops':[],'else_image_ops':[],
                 'lane_merges':[],'promoted_patterns':[],'promotion':'STRUCTURAL_ONLY'}
            if complement is not None:
                row['then_range']=[start+1,complement-1];row['else_range']=[complement+1,restore-1]
                row['then_image_ops']=image_rows(ins,start+1,complement-1);row['else_image_ops']=image_rows(ins,complement+1,restore-1)
                td=vdefs(ins,start+1,complement-1);ed=vdefs(ins,complement+1,restore-1)
                common=sorted(set(td)&set(ed),key=lambda q:int(q[1:]))
                row['lane_merges']=[{'register':r,'then_assignment':simple_assignment(td[r]),'else_assignment':simple_assignment(ed[r])} for r in common]
                if not nested and not lr and row['lane_merges']:
                    row['promotion']='EXACT_SIMPLE_LANE_MERGE'
                    for p in (conditional_multiplier(row['lane_merges']),computed_or_zero(row['lane_merges'])):
                        if p:row['promoted_patterns'].append(p)
            else:
                row['then_range']=[start+1,restore-1];row['then_image_ops']=image_rows(ins,start+1,restore-1)
            regions.append(row)
        assert regions,'no canonical saveexec regions found'
    except Exception as ex:viol.append(repr(ex))
    exact=[r for r in regions if r['promotion']=='EXACT_SIMPLE_LANE_MERGE']
    patterns=[{'region_id':r['region_id'],**p} for r in exact for p in r['promoted_patterns']]
    out={'schema_version':1,'status':'D1_GCN_EXEC_REGION_IR_COMPLETE' if regions and not viol else 'D1_GCN_EXEC_REGION_IR_PARTIAL','shader':ir.get('shader'),
         'region_count':len(regions),'exact_simple_lane_merge_count':len(exact),'promoted_pattern_count':len(patterns),
         'regions':regions,'promoted_patterns':patterns,'violations':viol,
         'semantic_boundary':{'arbitrary_exec_ssa':'NOT_YET_PROMOTED','loop_carried_lane_values':'WITHHELD','nested_exec_lane_merges':'WITHHELD','simple_saveexec_lane_merges':'PROMOTED_WHEN_EXACT'},
         'policy':'Canonical saveexec/complement/restore regions are structural GCN facts. Piecewise VGPR merges are promoted only for simple regions with no nested saveexec and no CFG back-edge intersection. Visual meanings and texture-role names remain withheld.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
