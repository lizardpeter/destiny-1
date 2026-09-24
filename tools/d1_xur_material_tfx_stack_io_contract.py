#!/usr/bin/env python3
"""Fail-closed D1 ROI material-TFX stack/IO contract for the exact Xur corpus.

This tool deliberately does not trust inherited post-D1 opcode names in the
0x42..0x4B region.  It proves only behavior forced by the retail byte streams.

Candidate behavioral effects tested here:
- 0x42 u8: consume one expression value and target one stage CBuffer/output vec4;
- 0x4A u8: produce one vec4-like value;
- 0x4B u8: produce one vec4-like value;
- repeated 49 <index> 47 <destination> pairs are the independently proven D1
  PS resource-assignment structure and do not participate in expression-stack math.

The proof requires every one of the 108 Xur stage programs to execute without
stack underflow and finish at depth zero under those effects.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter

UNARY={
    'Saturate','Permute','Jitter','LerpConstant','VecRotCos','Frac',
    'Wander','PermuteAllX'
}
BINARY={'Multiply','Add','Cubic','Merge_1_3','Merge_2_2','Merge_3_1'}
TERNARY={'MultiplyAdd','Lerp'}
PUSH={'PushExternInputFloat','PushConstantVec4'}

def zero4(v):
    return isinstance(v,list) and len(v)==4 and all(float(x)==0.0 for x in v)

def simulate(ops):
    depth=0; p=0; trace=[]
    while p<len(ops):
        op=ops[p]; name=op['name']
        # Retail-proven resource-assignment structure. Keep it out of arithmetic stack.
        if name=='Unk49' and p+1<len(ops) and ops[p+1]['name']=='PopTemp':
            a,b=op,ops[p+1]
            idx=int(a['operand_bytes'][0]); dst=int(b['operand_bytes'][0])
            if dst != 0x21+idx:
                return None,[f'resource_destination_rule:{idx}:{dst:#x}'],trace
            trace.append({'op_index':p,'kind':'resource_assignment','texture_index':idx,'destination_code':dst,'depth_before':depth,'depth_after':depth})
            p+=2; continue
        before=depth
        if name in PUSH or name in ('Unk4a','Unk4b'):
            depth+=1
        elif name=='Unk42':
            depth-=1
        elif name in UNARY:
            pass
        elif name in BINARY:
            depth-=1
        elif name in TERNARY:
            depth-=2
        else:
            return None,[f'unsupported_op:{name}:0x{op["opcode"]}'],trace
        trace.append({'op_index':p,'name':name,'opcode':op['opcode'],'depth_before':before,'depth_after':depth})
        if depth<0:
            return None,[f'underflow:{p}:{name}'],trace
        p+=1
    return depth,[],trace

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--material-state',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    d=json.loads(a.material_state.read_text()); violations=[]
    if d.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or d.get('violations'):
        violations.append('material_state_not_exact')
    mats=d.get('materials') or {}
    if len(mats)!=54: violations.append(f'material_count:{len(mats)}!=54')

    stage_rows=[]; op42=[]; op4a=[]; op4b=[]; resource_pairs=[]
    stage_hist=Counter(); shader_hist=Counter()
    for mh,m in sorted(mats.items()):
        for stage in ('vs','ps'):
            s=m.get(stage) or {}; dis=s.get('tfx_disassembly') or {}
            if dis.get('complete') is not True:
                violations.append(f'{mh}:{stage}:framing_incomplete'); continue
            ops=dis.get('ops') or []; cb=(s.get('cbuffers') or {}).get('items') or []
            final,errs,trace=simulate(ops)
            if errs: violations.extend(f'{mh}:{stage}:{x}' for x in errs)
            if final!=0: violations.append(f'{mh}:{stage}:final_stack_depth:{final}')
            stage_hist[stage]+=1; shader_hist[f'{stage}:{s.get("shader")}']+=1
            written=set()
            for oi,op in enumerate(ops):
                if op['name']=='Unk49' and oi+1<len(ops) and ops[oi+1]['name']=='PopTemp':
                    idx=int(op['operand_bytes'][0]); dst=int(ops[oi+1]['operand_bytes'][0])
                    resource_pairs.append({'material':mh,'stage':stage,'shader':s.get('shader'),'texture_index':idx,'destination_code':dst})
                if op['name']=='Unk42':
                    target=int(op['d1_unk42_u8'])
                    valid=target<len(cb)
                    serialized=cb[target]['value'] if valid else None
                    row={'material':mh,'stage':stage,'shader':s.get('shader'),'op_index':oi,'target':target,
                         'target_valid_cbuffer_index':valid,'serialized_target_value':serialized,
                         'serialized_target_is_zero4':zero4(serialized)}
                    op42.append(row); written.add(target)
                elif op['name']=='Unk4a':
                    slot=int(op['operand_bytes'][0])
                    valid=slot<len(cb)
                    op4a.append({'material':mh,'stage':stage,'shader':s.get('shader'),'op_index':oi,'operand':slot,
                                'operand_is_valid_cbuffer_index':valid,'operand_written_earlier_by_0x42':slot in written,
                                'serialized_operand_value':cb[slot]['value'] if valid else None})
                elif op['name']=='Unk4b':
                    arg=int(op['operand_bytes'][0])
                    later=[x for x in ops[oi+1:] if x['name']=='Unk42']
                    target=int(later[0]['d1_unk42_u8']) if later else None
                    op4b.append({'material':mh,'stage':stage,'shader':s.get('shader'),'op_index':oi,'operand':arg,
                                'next_0x42_target':target,
                                'next_target_serialized_value':cb[target]['value'] if target is not None and target<len(cb) else None,
                                'following_names':[x['name'] for x in ops[oi:oi+5]]})
            stage_rows.append({'material':mh,'stage':stage,'shader':s.get('shader'),'op_count':len(ops),'final_stack_depth':final})

    if len(stage_rows)!=108: violations.append(f'stage_program_count:{len(stage_rows)}!=108')
    if len(op42)!=54: violations.append(f'op42_count:{len(op42)}!=54')
    if not all(x['target_valid_cbuffer_index'] for x in op42): violations.append('op42_invalid_target')
    if not all(x['serialized_target_is_zero4'] for x in op42): violations.append('op42_nonzero_serialized_target')
    if len(op4a)!=43: violations.append(f'op4a_count:{len(op4a)}!=43')
    if len(op4b)!=4: violations.append(f'op4b_count:{len(op4b)}!=4')
    if not all(x['following_names']==['Unk4b','PushConstantVec4','PushConstantVec4','Lerp','Unk42'] for x in op4b):
        violations.append('op4b_lerp_store_pattern_changed')

    out={
      'schema_version':1,
      'status':'D1_XUR_MATERIAL_TFX_STACK_IO_CONTRACT_EXACT' if not violations else 'D1_XUR_MATERIAL_TFX_STACK_IO_CONTRACT_VIOLATIONS',
      'material_count':len(mats),'stage_program_count':len(stage_rows),
      'stage_program_histogram':dict(stage_hist),'shader_program_histogram':dict(sorted(shader_hist.items())),
      'stack_model':{
        '0x42':'consume one expression value; one-u8 operand addresses a stage CBuffer/output vec4 in this corpus',
        '0x4A':'produce one vec4-like expression value; exact engine source/name remains open',
        '0x4B':'produce one vec4-like expression value; exact engine source/name remains open',
        '0x49_index_0x47_destination':'resource-assignment pair; zero arithmetic-stack effect',
        'Cubic':'binary: coefficients + x -> cubic result',
      },
      'all_108_programs_zero_final_depth':all(x['final_stack_depth']==0 for x in stage_rows),
      'op42_count':len(op42),
      'op42_all_targets_valid_cbuffer_indices':all(x['target_valid_cbuffer_index'] for x in op42),
      'op42_all_serialized_targets_zero4':all(x['serialized_target_is_zero4'] for x in op42),
      'op42_rows':op42,
      'op4a_count':len(op4a),
      'op4a_valid_cbuffer_operand_count':sum(x['operand_is_valid_cbuffer_index'] for x in op4a),
      'op4a_read_after_0x42_same_slot_count':sum(x['operand_written_earlier_by_0x42'] for x in op4a),
      'op4a_rows':op4a,
      'op4b_count':len(op4b),
      'op4b_operand_histogram':dict(Counter(str(x['operand']) for x in op4b)),
      'op4b_exact_lerp_then_0x42_pattern':all(x['following_names']==['Unk4b','PushConstantVec4','PushConstantVec4','Lerp','Unk42'] for x in op4b),
      'op4b_rows':op4b,
      'resource_assignment_pair_count':len(resource_pairs),
      'resource_assignment_destination_rule_all':all(x['destination_code']==0x21+x['texture_index'] for x in resource_pairs),
      'resource_assignment_pairs':resource_pairs,
      'semantic_promotions':{
        '0x42_scoped_cbuffer_output_store_stack_effect_closed':not violations,
        '0x4A_push_one_stack_effect_closed':not violations,
        '0x4B_push_one_stack_effect_closed':not violations,
        '0x4A_exact_engine_source_closed':False,
        '0x4B_exact_engine_source_closed':False,
        '0x49_0x47_resource_assignment_structure_closed':not violations,
      },
      'violations':violations,
      'policy':'This proof promotes behavior forced by exact retail stack balance and serialized target structure. It does not import later-strategy numeric opcode names. 0x42 is promoted only as a scoped stage-CBuffer/output store behavior; 0x4A/0x4B are push-one operations until their exact engine sources are independently closed.'
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','stage_program_count','all_108_programs_zero_final_depth','op42_count','op42_all_targets_valid_cbuffer_indices','op42_all_serialized_targets_zero4','op4a_count','op4a_valid_cbuffer_operand_count','op4a_read_after_0x42_same_slot_count','op4b_count','op4b_operand_histogram','op4b_exact_lerp_then_0x42_pattern','resource_assignment_pair_count','violations']},indent=2))
    return 0 if not violations else 2
if __name__=='__main__': raise SystemExit(main())
