#!/usr/bin/env python3
"""Attach exact live descriptor provenance to an existing D1 GCN renderer program.

Only descriptor-producing instructions proven by D1_GCN_DESCRIPTOR_LIVE_PROVENANCE_EXACT
are promoted. Existing stronger proof tiers are retained and receive corroborating tags.
"""
from __future__ import annotations
import argparse, collections, copy, json
from pathlib import Path


def contiguous(values):
    v=sorted(set(values));out=[]
    if not v:return out
    a=b=v[0]
    for x in v[1:]:
        if x==b+1:b=x
        else:out.append((a,b));a=b=x
    out.append((a,b));return out


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--program',type=Path,required=True)
    ap.add_argument('--descriptor-provenance',type=Path,required=True)
    ap.add_argument('--ir',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    base=json.load(open(a.program));dp=json.load(open(a.descriptor_provenance));ir=json.load(open(a.ir))
    violations=[];out={}
    try:
        assert base['status']=='D1_GCN_RENDERER_PROGRAM_IR_EXACT_PARTIAL' and not base['violations']
        p=base['program'];c=p['coverage']
        assert p['material']=='80D777B6' and p['pixel_shader']=='808EE505' and p['instruction_count']==456
        assert c['primary_resolution_counts']=={
          'CONTROL_EXACT':18,'EXPRESSION_EXACT':161,'INPUT_PROVENANCE_EXACT':19,
          'RECURRENCE_EXACT':36,'STRUCTURAL_ONLY':222},c
        assert c['exact_nonstructural_instruction_count']==234
        assert ir['status']=='D1_GCN_STRUCTURAL_IR_COMPLETE' and ir['shader']=='808EE505' and ir['instruction_count']==456
        assert dp['status']=='D1_GCN_DESCRIPTOR_LIVE_PROVENANCE_EXACT' and not dp['violations'],dp
        q=dp['proof'];assert q['shader']=='808EE505' and q['image_instruction_count']==14
        exact=q['exact_descriptor_load_instructions']
        assert exact==[4,8,132,133,196,197,198,266,329,330,373,374],exact
        assert q['exact_descriptor_load_count']==12
        events={int(x['instruction']):x for x in q['descriptor_loads']}
        assert set(events)==set(exact)

        out=copy.deepcopy(base);op=out['program'];rows=op['instruction_resolution']
        promoted=[];corroborated=[]
        for i in exact:
            ev=events[i]
            tag=('RESOURCE_TABLE_DESCRIPTOR_LOAD_EXACT' if ev['resolution']=='EXACT_RESOURCE_TABLE_DESCRIPTOR'
                 else 'EXTENDED_USER_DATA_DESCRIPTOR_LOAD_EXACT')
            r=rows[i]
            if r['primary_resolution']=='STRUCTURAL_ONLY':
                r['primary_resolution']='INPUT_PROVENANCE_EXACT';promoted.append(i)
            else:
                corroborated.append(i)
            r['evidence_tags']=sorted(set(r.get('evidence_tags',[])+['DESCRIPTOR_LIVE_PROVENANCE_EXACT',tag]))
        assert promoted==[4,8,132,133,196,197,198,329,330,373,374],promoted
        assert corroborated==[266],corroborated

        op['descriptor_live_provenance']=q
        counts=collections.Counter(r['primary_resolution'] for r in rows)
        structural={i for i,r in enumerate(rows) if r['primary_resolution']=='STRUCTURAL_ONLY'}
        spans=[];ins=ir['instructions']
        for lo,hi in contiguous(structural):
            rr=ins[lo:hi+1];ops=collections.Counter(x['opcode'] for x in rr)
            spans.append({
              'start_instruction':lo,'end_instruction':hi,'instruction_count':hi-lo+1,
              'opcode_histogram':dict(sorted(ops.items())),
              'image_instructions':[x['index'] for x in rr if 'image' in x],
              'branch_instructions':[x['index'] for x in rr if x['opcode'].startswith('s_cbranch') or x['opcode']=='s_branch'],
              'exec_write_instructions':[x['index'] for x in rr if 'exec' in x.get('defs',[])],
              'boundary':'STRUCTURAL_ONLY_NO_VALUE_EXPRESSION_PROMOTION'})
        c=op['coverage'];c['primary_resolution_counts']=dict(sorted(counts.items()))
        c['exact_nonstructural_instruction_count']=456-counts['STRUCTURAL_ONLY']
        c['structural_only_instruction_count']=counts['STRUCTURAL_ONLY']
        c['structural_only_spans']=spans
        c['descriptor_provenance_exact_load_instructions']=exact
        c['descriptor_provenance_promoted_instructions']=promoted
        c['descriptor_provenance_promoted_instruction_count']=len(promoted)
        c['descriptor_provenance_corroborated_existing_instructions']=corroborated

        expected={'CONTROL_EXACT':18,'EXPRESSION_EXACT':161,'INPUT_PROVENANCE_EXACT':30,'RECURRENCE_EXACT':36,'STRUCTURAL_ONLY':211}
        assert c['primary_resolution_counts']==expected,c
        assert c['exact_nonstructural_instruction_count']==245
        assert c['structural_only_instruction_count']==211
        out['schema_version']=max(5,int(out.get('schema_version',0)))
        out.setdefault('semantic_boundary',{})['live_resource_sampler_descriptor_provenance']='EXACT_GFX7'
        out['semantic_boundary']['sampler_state_bit_decode']='NOT_DECODED_BY_THIS_LAYER'
    except Exception as exc:
        violations.append(repr(exc))

    if violations:
        result={'schema_version':1,'status':'D1_GCN_RENDERER_DESCRIPTOR_PROVENANCE_PARTIAL','violations':violations};rc=2
    else:
        result=out;result['status']='D1_GCN_RENDERER_PROGRAM_IR_EXACT_PARTIAL';result['violations']=[];rc=0
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result.get('status'),'coverage':result.get('program',{}).get('coverage',{}).get('primary_resolution_counts'),
                      'exact_nonstructural':result.get('program',{}).get('coverage',{}).get('exact_nonstructural_instruction_count'),
                      'violations':violations},indent=2))
    return rc


if __name__=='__main__':
    raise SystemExit(main())
