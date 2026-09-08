#!/usr/bin/env python3
"""Upgrade a frozen renderer-program IR with path-sensitive export-kill control.

This adapter is intentionally selective. It accepts an already-green renderer program,
a source-proven implicit-status structural IR, and the v2 path-sensitive kill proof.
Only the previously omitted predicate arithmetic and empty-mask SCC branch are promoted.
The terminal MRT payload is rewritten to carry the new per-path kill relation instead
of the old coarse governed_kill field.
"""
from __future__ import annotations
import argparse, collections, copy, json
from pathlib import Path


def contiguous(values):
    vals = sorted(set(values))
    if not vals:
        return []
    out=[]; a=b=vals[0]
    for x in vals[1:]:
        if x == b + 1:
            b=x
        else:
            out.append((a,b)); a=b=x
    out.append((a,b)); return out


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--program',type=Path,required=True)
    ap.add_argument('--kill-v2',type=Path,required=True)
    ap.add_argument('--ir-implicit',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    base=json.load(open(a.program)); km=json.load(open(a.kill_v2)); ir=json.load(open(a.ir_implicit))
    violations=[]; out={}
    try:
        assert base['status']=='D1_GCN_RENDERER_PROGRAM_IR_EXACT_PARTIAL' and not base['violations']
        p=base['program']; assert p['material']=='80D777B6' and p['pixel_shader']=='808EE505' and p['instruction_count']==456
        cov=p['coverage']
        assert cov['primary_resolution_counts']=={
            'CONTROL_EXACT':16,'EXPRESSION_EXACT':161,'INPUT_PROVENANCE_EXACT':19,
            'RECURRENCE_EXACT':36,'STRUCTURAL_ONLY':224},cov
        assert cov['exact_nonstructural_instruction_count']==232

        assert ir['status']=='D1_GCN_STRUCTURAL_IR_COMPLETE' and int(ir.get('schema_version',0))>=3
        assert ir['shader']=='808EE505' and ir['instruction_count']==456
        assert km['status']=='D1_GCN_EXPORT_KILL_MASK_PATH_SENSITIVE_COMPLETE' and not km['violations']
        assert km['shader']=='808EE505' and km['material']=='80D777B6' and len(km['contracts'])==1
        k=km['contracts'][0]
        assert k['predicate']['arithmetic_instruction']==335
        assert k['predicate']['compare_instruction']==336
        assert k['kill_instruction']==337
        assert k['empty_mask_branch']['instruction']==338
        assert k['empty_mask_branch']['source_scc_instruction']==337
        assert k['empty_mask_branch']['target_instruction']==443
        assert k['empty_mask_branch']['fallthrough_instruction']==339
        assert ir['instructions'][337]['opcode']=='s_andn2_b64' and 'scc' in ir['instructions'][337]['defs']
        assert ir['instructions'][338]['opcode']=='s_cbranch_scc0' and 'scc' in ir['instructions'][338]['uses']

        paths={int(q['instruction']):q for q in k['export_path_relations']}
        assert set(paths)=={449,454},paths
        assert paths[449]['target']=='mrt1' and paths[449]['vm'] is False
        assert paths[449]['nonempty_mask_path']['exec_relation']=='WQM_OF_MASKED_EXEC'
        assert paths[449]['empty_mask_branch_path']['exec_relation']=='PRE_PATH_EXEC_UNCHANGED'
        assert paths[449]['kill_mask_binding']=='VM_FALSE_EXEC_EFFECT_WITHHELD'
        assert paths[454]['target']=='mrt0' and paths[454]['vm'] is True
        assert paths[454]['nonempty_mask_path']['exec_relation']=='DIRECT_MOV_MASK'
        assert paths[454]['empty_mask_branch_path']['exec_relation']=='DIRECT_MOV_MASK'
        assert paths[454]['kill_mask_binding']=='DIRECT_VALID_MASK_ON_ALL_PATHS'
        assert k['directly_mask_governed_exports']==[{
            'instruction':454,'target':'mrt0','vm':True,'binding':'DIRECT_VALID_MASK_ON_ALL_PATHS'}]

        out=copy.deepcopy(base); op=out['program']; rows=op['instruction_resolution']
        for i,tag in ((335,'PERSISTENT_EXPORT_KILL_PREDICATE_ARITHMETIC'),(338,'PERSISTENT_EXPORT_KILL_EMPTY_MASK_BRANCH')):
            assert rows[i]['primary_resolution']=='STRUCTURAL_ONLY',rows[i]
            rows[i]['primary_resolution']='CONTROL_EXACT'
            rows[i]['evidence_tags']=sorted(set(rows[i].get('evidence_tags',[])+[tag,'PERSISTENT_EXPORT_KILL_V2']))

        op['persistent_export_kills']=km['contracts']
        op['implicit_status_destinations']=ir.get('implicit_status_destinations',[])

        # Replace the terminal export's old coarse kill relation with exact path data.
        terminal=op.get('terminal_mrt_expression')
        assert terminal and {int(x['instruction']) for x in terminal['exports']}=={449,454}
        for ex in terminal['exports']:
            ei=int(ex['instruction'])
            ex.pop('governed_kill',None)
            ex['kill_path_relation']=paths[ei]
        terminal.setdefault('semantic_boundary',{})['persistent_export_kill_relation']='EXACT_PATH_SENSITIVE_V2'
        terminal['semantic_boundary']['mrt1_vm_false_exec_effect']='WITHHELD'
        terminal['semantic_boundary']['mrt0_persistent_mask_binding']='DIRECT_VALID_MASK_ON_ALL_PATHS'

        counts=collections.Counter(r['primary_resolution'] for r in rows)
        structural={i for i,r in enumerate(rows) if r['primary_resolution']=='STRUCTURAL_ONLY'}
        spans=[]
        ins=ir['instructions']
        for lo,hi in contiguous(structural):
            rr=ins[lo:hi+1]; ops=collections.Counter(x['opcode'] for x in rr)
            spans.append({
                'start_instruction':lo,'end_instruction':hi,'instruction_count':hi-lo+1,
                'opcode_histogram':dict(sorted(ops.items())),
                'image_instructions':[x['index'] for x in rr if 'image' in x],
                'branch_instructions':[x['index'] for x in rr if x['opcode'].startswith('s_cbranch') or x['opcode']=='s_branch'],
                'exec_write_instructions':[x['index'] for x in rr if 'exec' in x.get('defs',[])],
                'boundary':'STRUCTURAL_ONLY_NO_VALUE_EXPRESSION_PROMOTION',
            })
        op['coverage']['primary_resolution_counts']=dict(sorted(counts.items()))
        op['coverage']['exact_nonstructural_instruction_count']=456-counts['STRUCTURAL_ONLY']
        op['coverage']['structural_only_instruction_count']=counts['STRUCTURAL_ONLY']
        op['coverage']['structural_only_spans']=spans
        op['coverage']['kill_v2_promoted_instructions']=[335,338]
        op['coverage']['kill_v2_promoted_instruction_count']=2

        out['schema_version']=max(4,int(out.get('schema_version',0)))
        out.setdefault('semantic_boundary',{})['persistent_export_kill_control']='EXACT_PATH_SENSITIVE_V2'
        out['semantic_boundary']['mrt1_vm_false_exec_effect']='WITHHELD_NOT_SOURCE_CLOSED'
        out['semantic_boundary']['mrt0_persistent_mask_binding']='EXACT_DIRECT_VALID_MASK_ON_ALL_PATHS'

        expected={'CONTROL_EXACT':18,'EXPRESSION_EXACT':161,'INPUT_PROVENANCE_EXACT':19,'RECURRENCE_EXACT':36,'STRUCTURAL_ONLY':222}
        assert op['coverage']['primary_resolution_counts']==expected,op['coverage']
        assert op['coverage']['exact_nonstructural_instruction_count']==234
        assert op['coverage']['structural_only_instruction_count']==222
    except Exception as exc:
        violations.append(repr(exc))

    if violations:
        result={'schema_version':1,'status':'D1_GCN_RENDERER_PROGRAM_KILL_V2_PARTIAL','violations':violations}
        rc=2
    else:
        result=out; result['status']='D1_GCN_RENDERER_PROGRAM_IR_EXACT_PARTIAL'; result['violations']=[]; rc=0

    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({
        'status':result.get('status'),
        'coverage':result.get('program',{}).get('coverage',{}).get('primary_resolution_counts'),
        'exact_nonstructural':result.get('program',{}).get('coverage',{}).get('exact_nonstructural_instruction_count'),
        'violations':violations,
    },indent=2))
    return rc


if __name__=='__main__':
    raise SystemExit(main())
