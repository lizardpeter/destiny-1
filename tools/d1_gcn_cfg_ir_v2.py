#!/usr/bin/env python3
"""Lift CLRX GFX700 text into a destination-neutral structural D1 GCN IR.

This layer is intentionally below semantic decompilation. It preserves instruction
order, control-flow edges, register operands, shader interpolators/exports, native
image resource provenance and EXEC-mask mutation sites without pretending divergent
VGPR values are ordinary scalar SSA.

Schema v2 adds explicit GCN multi-destination handling for integer vector arithmetic
whose CLRX syntax carries a VCC destination as operand 1 (for example
``v_add_i32 v16, vcc, 1, v25``). Misclassifying that VCC as a use can corrupt later
predicate provenance, so these opcodes are handled as structural instruction facts
rather than inferred by a generic first-operand rule.
"""
from __future__ import annotations
import argparse,json,re
from collections import Counter
from pathlib import Path

ADDR_RE=re.compile(r'^/\*([0-9A-Fa-f]+):\s+([0-9A-Fa-f ]+)\*/\s*(\S+)\s*(.*)$')
LABEL_RE=re.compile(r'^(\.L\w+):$')
REG_RE=re.compile(r'(?<![A-Za-z0-9_])(?:v\[(\d+):(\d+)\]|s\[(\d+):(\d+)\]|v(\d+)|s(\d+)|vcc(?:_lo|_hi)?|exec(?:_lo|_hi)?|m0|scc)(?![A-Za-z0-9_])')
ATTR_RE=re.compile(r'\battr(\d+)(?:\.([xyzw]))?\b')
PARAM_RE=re.compile(r'\bparam(\d+)\b')
COND_PREFIX='s_cbranch_'; UNCOND={'s_branch'}; TERMINAL={'s_endpgm'}
NO_DEST=('s_branch','s_cbranch_','s_waitcnt','s_barrier','exp','ds_write','buffer_store','flat_store','global_store','image_store','s_endpgm')
RMW=('v_mac','v_mac_legacy','v_interp_p2','v_addc','v_subb','s_addc','s_subb')
VCC_SECOND_DEST={
    'v_add_i32','v_sub_i32','v_subrev_i32',
    'v_add_u32','v_sub_u32','v_subrev_u32',
    'v_addc_u32','v_subb_u32','v_subbrev_u32',
}
VCC_CARRY_IN={'v_addc_u32','v_subb_u32','v_subbrev_u32'}


def regs(text):
    out=[]
    for m in REG_RE.finditer(text):
        if m.group(1): out += [f'v{i}' for i in range(int(m.group(1)),int(m.group(2))+1)]
        elif m.group(3): out += [f's{i}' for i in range(int(m.group(3)),int(m.group(4))+1)]
        elif m.group(5): out.append('v'+m.group(5))
        elif m.group(6): out.append('s'+m.group(6))
        else: out.append(m.group(0))
    return list(dict.fromkeys(out))

def ops(s): return [x.strip() for x in s.split(',') if x.strip()]

def classify(op,a):
    if not a:return [],[]
    no=op in TERMINAL or op in UNCOND or op.startswith(COND_PREFIX) or any(op.startswith(x) for x in NO_DEST)
    if no:
        d=[];u=regs(','.join(a))
    elif op.startswith('s_cmp'):
        d=['scc'];u=regs(','.join(a))
    elif op in VCC_SECOND_DEST and len(a)>=2 and a[1].startswith('vcc'):
        d=list(dict.fromkeys(regs(a[0])+regs(a[1])))
        u=regs(','.join(a[2:]))
        if op in VCC_CARRY_IN and any(x.startswith('vcc') for x in a[2:]):
            u=list(dict.fromkeys(u+['vcc']))
    else:
        d=regs(a[0]);u=regs(','.join(a[1:]))
        if op.startswith(RMW):u=list(dict.fromkeys(u+d))
    if op.startswith('s_cbranch_scc'):u=list(dict.fromkeys(u+['scc']))
    if op.startswith('s_cbranch_vcc'):u=list(dict.fromkeys(u+['vcc']))
    if op.startswith('s_cbranch_exec'):u=list(dict.fromkeys(u+['exec']))
    if op.endswith('saveexec_b64'):
        d=list(dict.fromkeys(d+['exec']));u=list(dict.fromkeys(u+['exec']))
    return d,u


def parse(p):
    ins=[];labels=[]
    for raw in p.read_text(errors='replace').splitlines():
        t=raw.strip();lm=LABEL_RE.match(t)
        if lm:labels.append(lm.group(1));continue
        m=ADDR_RE.match(t)
        if not m:continue
        addr=int(m.group(1),16);rawhex=''.join(m.group(2).split()).lower();op=m.group(3);rest=m.group(4).strip();a=ops(rest);d,u=classify(op,a)
        target=None
        if op in UNCOND or op.startswith(COND_PREFIX):
            q=re.search(r'(\.L\w+)',rest);target=q.group(1) if q else None
        ins.append({'index':len(ins),'address':addr,'address_hex':f'{addr:012X}','encoding_hex':rawhex,'labels':labels,'opcode':op,'operands':a,'defs':d,'uses':u,'branch_target_label':target,'assembly':t})
        labels=[]
    return ins


def blocks(ins):
    l2i={l:x['index'] for x in ins for l in x['labels']};starts={0}
    for x in ins:
        if x['labels']:starts.add(x['index'])
        if x['opcode'] in UNCOND or x['opcode'].startswith(COND_PREFIX) or x['opcode'] in TERMINAL:
            if x['index']+1<len(ins):starts.add(x['index']+1)
        if x['branch_target_label'] in l2i:starts.add(l2i[x['branch_target_label']])
    ss=sorted(starts);bb=[];i2b={}
    for bi,s in enumerate(ss):
        e=ss[bi+1]-1 if bi+1<len(ss) else len(ins)-1
        b={'id':bi,'start_instruction':s,'end_instruction':e,'start_address':ins[s]['address_hex'],'labels':ins[s]['labels'],'successors':[],'predecessors':[]}
        bb.append(b)
        for i in range(s,e+1):i2b[i]=bi
    for b in bb:
        x=ins[b['end_instruction']];succ=[]
        if x['branch_target_label'] and x['branch_target_label'] in l2i:succ.append(i2b[l2i[x['branch_target_label']]])
        if x['opcode'].startswith(COND_PREFIX):
            if x['index']+1<len(ins):succ.append(i2b[x['index']+1])
        elif x['opcode'] not in UNCOND and x['opcode'] not in TERMINAL:
            if x['index']+1<len(ins):succ.append(i2b[x['index']+1])
        b['successors']=list(dict.fromkeys(succ))
    for b in bb:
        for s in b['successors']:bb[s]['predecessors'].append(b['id'])
    back=[]
    for b in bb:
        for s in b['successors']:
            if bb[s]['start_instruction']<=b['start_instruction']:back.append({'from_block':b['id'],'to_block':s})
    return bb,back


def image_annotate(ins,report,shader):
    if report.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':raise ValueError('image usage report is not exact')
    rows=[x for x in report.get('shaders',[]) if str(x.get('shader')).upper()==shader.upper()]
    if len(rows)!=1:raise ValueError(f'{shader}: expected one image usage row, got {len(rows)}')
    r=rows[0]
    if r.get('unmatched_image_instruction_count')!=0:raise ValueError(f'{shader}: unmatched image instructions')
    by={int(x['address'],16):x for x in r.get('instructions',[])}
    for x in ins:
        z=by.get(x['address'])
        if z:x['image']={'opcode':z['opcode'],'dmask':z.get('dmask'),'dmask_channels':z.get('dmask_channels'),'textures':[int(a['texture_index']) for a in z.get('resources',[])],'samplers':[int(a['sampler_index']) for a in z.get('samplers',[])],'resource_provenance':z.get('resources',[]),'sampler_provenance':z.get('samplers',[])}
    got=sum('image' in x for x in ins)
    if got!=r['image_instruction_count']:raise ValueError((got,r['image_instruction_count']))
    return r


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--disasm',type=Path,required=True);ap.add_argument('--shader',required=True);ap.add_argument('--image-usage',type=Path);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
    shader=a.shader.upper().removeprefix('0X').zfill(8);ins=parse(a.disasm);bb,back=blocks(ins);usage=None
    if a.image_usage:usage=image_annotate(ins,json.load(open(a.image_usage)),shader)
    attrs=sorted({f'attr{m.group(1)}'+(f'.{m.group(2)}' if m.group(2) else '') for x in ins for m in ATTR_RE.finditer(x['assembly'])})
    params=sorted({f'param{m.group(1)}' for x in ins for m in PARAM_RE.finditer(x['assembly'])})
    exports=[{'instruction':x['index'],'address':x['address_hex'],'target':x['operands'][0] if x['operands'] else None,'operands':x['operands'][1:]} for x in ins if x['opcode']=='exp']
    exec_sites=[{'instruction':x['index'],'address':x['address_hex'],'opcode':x['opcode'],'operands':x['operands']} for x in ins if 'exec' in x['defs'] or 'exec' in x['uses'] or any('exec' in y for y in x['operands'])]
    multi=[{'instruction':x['index'],'opcode':x['opcode'],'defs':x['defs'],'uses':x['uses']} for x in ins if x['opcode'] in VCC_SECOND_DEST]
    control={'conditional_branch_count':sum(x['opcode'].startswith(COND_PREFIX) for x in ins),'unconditional_branch_count':sum(x['opcode'] in UNCOND for x in ins),'back_edges':back,'exec_mutation_sites':exec_sites,'divergent_exec_present':bool(exec_sites)}
    out={'schema_version':2,'status':'D1_GCN_STRUCTURAL_IR_COMPLETE','shader':shader,'instruction_count':len(ins),'basic_block_count':len(bb),'cfg_edge_count':sum(len(x['successors']) for x in bb),'opcode_counts':dict(sorted(Counter(x['opcode'] for x in ins).items())),'interpolator_inputs':attrs,'parameter_exports':params,'exports':exports,'control_flow':control,'multi_destination_overrides':multi,'image_usage_summary':None if usage is None else {'image_instruction_count':usage['image_instruction_count'],'used_texture_indices':usage['used_texture_indices'],'image_opcodes':usage['image_opcodes'],'unmatched_image_instruction_count':usage['unmatched_image_instruction_count']},'instructions':ins,'basic_blocks':bb,'semantic_boundary':{'register_def_use_classification':'STRUCTURAL_WITH_GCN_MULTI_DEST_OVERRIDES','divergent_vgpr_ssa':'NOT_YET_PROMOTED','exec_mask_symbolic_dataflow':'NEXT_GATE','output_expression_lifting':'WITHHELD_UNTIL_EXEC_MASK_DATAFLOW'},'policy':'Instruction encodings/text, CFG edges, operands, attrs/exports and exact Sony image-resource provenance are promoted. Known GCN multi-destination integer arithmetic explicitly records its VCC destination. Divergent EXEC still makes naive VGPR SSA unsound, so output-expression claims remain withheld until symbolic EXEC-mask dataflow is implemented.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ('status','shader','instruction_count','basic_block_count','cfg_edge_count','multi_destination_overrides','interpolator_inputs','parameter_exports','exports','control_flow','image_usage_summary','semantic_boundary')},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
