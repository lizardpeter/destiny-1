#!/usr/bin/env python3
"""Symbolically replay the exact current Xur pixel-stage TFX programs.

Purpose:
- turn every D1 0x42 store in the current 54-material visible PS set into a
  deterministic symbolic expression;
- preserve only truly unresolved producer opcodes as explicit source symbols;
- prove how much of the visible PS runtime material state is already closed.

This is intentionally PS-only. VS TFX is handled separately because its remaining
producer dependencies affect deformation/UV behavior rather than the visible PS
material equations directly.

Established inputs:
- 0x42 consumes one expression and stores it to a stage CBuffer/output Vec4 slot;
- 0x4A and 0x4B each push one Vec4-like value, but their exact engine source
  identities remain open;
- 0x49 <texture-index>, 0x47 <0x21+index> is resource assignment and has no
  arithmetic stack effect.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from collections import Counter,defaultdict

UNARY={'Saturate','Permute','Jitter','LerpConstant','VecRotCos','Frac','Wander','PermuteAllX'}
BINARY={'Multiply','Add','Cubic','Merge_1_3','Merge_2_2','Merge_3_1'}
TERNARY={'MultiplyAdd','Lerp'}
PUSH={'PushExternInputFloat','PushConstantVec4'}
SRC_RX=re.compile(r'(?:U4A|U4B|Frame)\[\d+\]')

def fnum(x):
    return format(float(x),'.9g')

def vec(v):
    if v is None:return '<?>'
    return '('+','.join(fnum(x) for x in v)+')'

def source_refs(expr):
    return sorted(set(SRC_RX.findall(expr)))

def replay_stage(stage):
    ops=(stage.get('tfx_disassembly') or {}).get('ops') or []
    stack=[];stores=[];p=0
    while p<len(ops):
        op=ops[p];name=op['name']

        # Exact current D1 material resource-assignment pair.
        if name=='Unk49' and p+1<len(ops) and ops[p+1]['name']=='PopTemp':
            idx=int(op['operand_bytes'][0]);dst=int(ops[p+1]['operand_bytes'][0])
            if dst != 0x21+idx:
                raise ValueError(f'resource assignment mismatch {idx}->{dst:#x}')
            p+=2;continue

        if name=='PushConstantVec4':
            idx=int(op['constant_index'])
            stack.append(f'C{idx}{vec(op.get("buffer1_candidate"))}')
        elif name=='PushExternInputFloat':
            stack.append(f'{op.get("extern_name","Extern")}[{int(op.get("extern_element",0))}]')
        elif name=='Unk4a':
            stack.append(f'U4A[{int(op["operand_bytes"][0])}]')
        elif name=='Unk4b':
            stack.append(f'U4B[{int(op["operand_bytes"][0])}]')
        elif name=='Unk42':
            if not stack: raise ValueError('0x42 stack underflow')
            target=int(op['d1_unk42_u8'])
            expr=stack.pop()
            stores.append({'target':target,'expression':expr,'source_refs':source_refs(expr)})
        elif name in BINARY:
            if len(stack)<2: raise ValueError(f'{name} stack underflow')
            a,b=stack[-2:];del stack[-2:]
            if name=='Multiply':e=f'({a}*{b})'
            elif name=='Add':e=f'({a}+{b})'
            elif name=='Cubic':e=f'cubic({a},{b})'
            elif name=='Merge_1_3':e=f'merge13({a},{b})'
            elif name=='Merge_2_2':e=f'merge22({a},{b})'
            else:e=f'merge31({a},{b})'
            stack.append(e)
        elif name in TERNARY:
            if len(stack)<3: raise ValueError(f'{name} stack underflow')
            a,b,c=stack[-3:];del stack[-3:]
            # Existing D1 TFX lineage/replay uses stack order a,b,c.
            if name=='MultiplyAdd': stack.append(f'(({a}*{b})+{c})')
            else: stack.append(f'lerp({b},{c},{a})')
        elif name=='LerpConstant':
            if not stack: raise ValueError('LerpConstant stack underflow')
            t=stack.pop();idx=int(op['constant_start'])
            vv=op.get('buffer1_candidates') or [None,None]
            stack.append(f'lerp(C{idx}{vec(vv[0])},C{idx+1}{vec(vv[1])},{t})')
        elif name=='Permute':
            if not stack: raise ValueError('Permute stack underflow')
            a=stack.pop();stack.append(f'{a}{op.get("permute","")}')
        elif name in {'Saturate','Jitter','Wander','VecRotCos','Frac','PermuteAllX'}:
            if not stack: raise ValueError(f'{name} stack underflow')
            a=stack.pop();stack.append(f'{name.lower()}({a})')
        else:
            raise ValueError(f'unsupported PS TFX opcode {name}')

        if len(stack)>128: raise ValueError('stack runaway')
        p+=1

    if stack:
        raise ValueError(f'final PS stack depth {len(stack)}')
    return stores

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--material-state',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    d=json.loads(a.material_state.read_text());viol=[]
    if d.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or d.get('violations'):
        viol.append('material_state_not_exact')
    mats=d.get('materials') or {}
    if len(mats)!=54:viol.append(f'material_count:{len(mats)}!=54')

    rows=[];store_count=0;target_hist=Counter();source_hist=Counter();shader_hist=Counter()
    unknown_dep_rows=[];fully_closed_rows=[]
    family_exprs=defaultdict(set)
    for mh,m in sorted(mats.items()):
        ps=m.get('ps') or {}
        shader=str(ps.get('shader') or '')
        try:
            stores=replay_stage(ps)
        except Exception as ex:
            viol.append(f'{mh}:{shader}:{ex!r}');stores=[]
        if stores:
            shader_hist[shader]+=1
        for s in stores:
            store_count+=1;target_hist[str(s['target'])]+=1
            for src in s['source_refs']:source_hist[src]+=1
            rec={'material':mh,'pixel_shader':shader,**s}
            rows.append(rec);family_exprs[shader].add((s['target'],s['expression']))
            if any(x.startswith(('U4A[','U4B[')) for x in s['source_refs']):unknown_dep_rows.append(rec)
            else:fully_closed_rows.append(rec)

    families=[]
    for sh,exprs in sorted(family_exprs.items()):
        rr=[r for r in rows if r['pixel_shader']==sh]
        families.append({
            'pixel_shader':sh,
            'material_count':len({r['material'] for r in rr}),
            'store_count':len(rr),
            'stores':[{'target':t,'expression':e,'source_refs':source_refs(e)} for t,e in sorted(exprs)],
            'unresolved_source_symbols':sorted({x for r in rr for x in r['source_refs'] if x.startswith(('U4A[','U4B['))}),
        })

    expected_unknown={('8087688E',1,'U4A[4]'),('8087630D',32,'U4B[53]'),('809D836C',32,'U4B[53]'),('809D8370',32,'U4B[53]')}
    got_unknown={(r['pixel_shader'],r['target'],next(x for x in r['source_refs'] if x.startswith(('U4A[','U4B[')))) for r in unknown_dep_rows}
    if got_unknown!=expected_unknown:
        viol.append(f'unresolved_source_set_changed:{sorted(got_unknown)!r}')

    out={
      'schema_version':1,
      'status':'D1_XUR_VISIBLE_PS_TFX_SYMBOLIC_CONTRACT_EXACT' if not viol else 'D1_XUR_VISIBLE_PS_TFX_SYMBOLIC_CONTRACT_VIOLATIONS',
      'material_count':len(mats),
      'pixel_stage_store_count':store_count,
      'store_target_histogram':dict(target_hist),
      'source_reference_histogram':dict(source_hist),
      'pixel_shader_store_family_histogram':dict(shader_hist),
      'fully_source_named_store_count':len(fully_closed_rows),
      'unresolved_producer_dependent_store_count':len(unknown_dep_rows),
      'unresolved_producer_symbols':sorted({x for r in unknown_dep_rows for x in r['source_refs'] if x.startswith(('U4A[','U4B['))}),
      'critical_reduction':{
        'visible_ps_runtime_store_count':store_count,
        'stores_closed_without_0x4A_or_0x4B_identity':len(fully_closed_rows),
        'stores_still_requiring_exact_producer_identity':len(unknown_dep_rows),
        'remaining_exact_source_symbols':['U4A[4]','U4B[53]'],
        'remaining_shader_families':['8087688E','8087630D','809D836C','809D8370'],
      },
      'families':families,
      'stores':rows,
      'unresolved_dependency_rows':unknown_dep_rows,
      'violations':viol,
      'policy':'Every expression is replayed from exact current D1 PS TFX bytecode and private constants. Frame externs retain their source-owned element indices. 0x4A/0x4B are not renamed; only the two exact operand instances that still affect visible PS CBuffer stores remain symbolic.',
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','pixel_stage_store_count','store_target_histogram','source_reference_histogram','fully_source_named_store_count','unresolved_producer_dependent_store_count','unresolved_producer_symbols','critical_reduction','violations']},indent=2))
    return 0 if not viol else 2

if __name__=='__main__':raise SystemExit(main())
