#!/usr/bin/env python3
"""Attach independently exact straight-line expression DAGs to a renderer-program IR.

The base program and each straight-line proof are already-green checkpoint products.
This adapter changes only instruction proof tiers/evidence and embeds the exact DAG
payloads. It refuses overlaps that are not already EXPRESSION_EXACT, refuses shader or
material mismatches, and recomputes structural spans mechanically from the base native
instruction ledger. No native semantics are inferred here.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path


def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def contiguous(values):
    vals=sorted(set(values));out=[]
    if not vals:return out
    a=b=vals[0]
    for x in vals[1:]:
        if x==b+1:b=x
        else:out.append((a,b));a=b=x
    out.append((a,b));return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--program',type=Path,required=True)
    ap.add_argument('--straightline-expr',type=Path,action='append',default=[])
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args();viol=[];out={}
    try:
        base=json.load(open(a.program))
        assert base['status']=='D1_GCN_RENDERER_PROGRAM_IR_EXACT_PARTIAL' and not base['violations']
        p=base['program'];shader=norm(p['pixel_shader']);material=norm(p['material'])
        rows=p['instruction_resolution'];n=int(p['instruction_count'])
        assert len(rows)==n and [int(x['instruction']) for x in rows]==list(range(n))
        old_counts=collections.Counter(x['primary_resolution'] for x in rows)
        old_struct={int(x['instruction']) for x in rows if x['primary_resolution']=='STRUCTURAL_ONLY'}
        attached=list(p.get('exact_straightline_expressions') or [])
        seen={(tuple(x['instruction_range']),x.get('status','EXACT')) for x in attached}
        promoted=[]
        for path in a.straightline_expr:
            d=json.load(open(path));status=d.get('status','')
            assert status.startswith('D1_GCN_STRAIGHTLINE_') and status.endswith('_EXPRESSION_EXACT'),(path,status)
            assert not d.get('violations'),(path,d.get('violations'))
            e=d['expression'];assert norm(e['shader'])==shader and norm(e['material'])==material
            ids=[int(i) for i in e['value_instruction_indices']];assert ids and len(ids)==len(set(ids))
            lo,hi=map(int,e['instruction_range']);assert all(lo<=i<=hi for i in ids)
            assert all(0<=i<n for i in ids)
            key=(tuple(e['instruction_range']),'EXACT')
            assert key not in seen,f'duplicate straight-line range {e["instruction_range"]}'
            for i in ids:
                row=rows[i];old=row['primary_resolution']
                assert old in ('STRUCTURAL_ONLY','EXPRESSION_EXACT'),(i,old)
                if old=='STRUCTURAL_ONLY':
                    row['primary_resolution']='EXPRESSION_EXACT';promoted.append(i)
                tag=f'STRAIGHTLINE_{lo}_{hi}_EXPRESSION_DAG'
                tags=set(row.get('evidence_tags') or []);tags.add(tag);row['evidence_tags']=sorted(tags)
            attached.append({'status':'EXACT','source_status':status,**e})
            seen.add(key)
        assert promoted,'no newly promoted instructions'
        new_counts=collections.Counter(x['primary_resolution'] for x in rows)
        assert new_counts['EXPRESSION_EXACT']==old_counts['EXPRESSION_EXACT']+len(set(promoted))
        assert new_counts['STRUCTURAL_ONLY']==old_counts['STRUCTURAL_ONLY']-len(set(promoted))
        structural={int(x['instruction']) for x in rows if x['primary_resolution']=='STRUCTURAL_ONLY'}
        # Preserve base span metadata only as opcode/control diagnostics; rebuild span
        # membership from the authoritative per-instruction rows.
        byidx={int(x['instruction']):x for x in rows}
        spans=[]
        for lo,hi in contiguous(structural):
            ops=collections.Counter(byidx[i]['opcode'] for i in range(lo,hi+1))
            spans.append({'start_instruction':lo,'end_instruction':hi,'instruction_count':hi-lo+1,
                          'opcode_histogram':dict(sorted(ops.items())),
                          'boundary':'STRUCTURAL_ONLY_NO_VALUE_EXPRESSION_PROMOTION'})
        p['exact_straightline_expressions']=attached
        p['coverage']['primary_resolution_counts']=dict(sorted(new_counts.items()))
        p['coverage']['exact_nonstructural_instruction_count']=n-new_counts['STRUCTURAL_ONLY']
        p['coverage']['exact_nonstructural_fraction']=(n-new_counts['STRUCTURAL_ONLY'])/n
        p['coverage']['structural_only_instruction_count']=new_counts['STRUCTURAL_ONLY']
        p['coverage']['structural_only_fraction']=new_counts['STRUCTURAL_ONLY']/n
        p['coverage']['structural_only_spans']=spans
        p['coverage']['straightline_promoted_instruction_count']=len(set(promoted))
        p['coverage']['straightline_promoted_instructions']=sorted(set(promoted))
        base['schema_version']=max(3,int(base.get('schema_version',1)))
        base['semantic_boundary']['exact_straightline_expression_blocks']='EXACT_WHERE_ATTACHED'
        base['semantic_boundary']['remaining_straight_line_value_dataflow']='NEXT_GATE'
        base['policy']+=' Exact straight-line blocks may be attached only from independently exact proof payloads; coverage is recomputed without semantic inference.'
        out=base
    except Exception as e:
        viol.append(repr(e));out={'schema_version':1,'status':'D1_GCN_RENDERER_PROGRAM_IR_FAILED','program':{},'violations':viol}
    if out.get('status')!='D1_GCN_RENDERER_PROGRAM_IR_FAILED':out['violations']=viol
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    p=out.get('program') or {};print(json.dumps({'status':out.get('status'),'coverage':p.get('coverage',{}).get('primary_resolution_counts'),'exact_nonstructural':p.get('coverage',{}).get('exact_nonstructural_instruction_count'),'structural_spans':len(p.get('coverage',{}).get('structural_only_spans',[])) if p else None,'violations':viol},indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
