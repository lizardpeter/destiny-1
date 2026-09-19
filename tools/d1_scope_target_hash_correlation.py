#!/usr/bin/env python3
"""Correlate exact D1 s_scope payload edges with a bounded target FileHash family.

Input is the output of d1_remote_reference_class_census.py for s_scope class
80801C47. That census already emits an aligned u32 edge only when the value resolves
as a current FileHash in the pinned package catalog.

This tool therefore promotes only exact structural co-occurrence:
  scope TagHash -> aligned offset -> target FileHash.

It does not assign a field name, API slot, descriptor, draw ownership, or runtime
producer role to a hit.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

SCOPE_CLASS='80801C47'

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--census',type=Path,required=True)
    ap.add_argument('--target',action='append',required=True,help='LABEL=FILEHASH or FILEHASH')
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    src=json.loads(a.census.read_text())
    violations=[]
    if src.get('status')!='D1_REMOTE_REFERENCE_CLASS_CENSUS_EXACT' or src.get('violations'):
        violations.append('source class census not exact')
    refs={norm(x) for x in src.get('requested_references',[])}
    if SCOPE_CLASS not in refs:
        violations.append(f'source census does not include s_scope class {SCOPE_CLASS}')

    labels={}
    for raw in a.target:
        if '=' in raw:
            label,h=raw.split('=',1)
        else:
            label,h=raw,raw
        h=norm(h)
        if h in labels:
            violations.append(f'duplicate target hash {h}')
        labels[h]=label

    target_hits=collections.defaultdict(list)
    scope_rows=[]
    for row in src.get('rows',[]):
        if norm(row.get('reference'))!=SCOPE_CLASS:
            continue
        sh=norm(row['tag_hash'])
        hits=[]
        for edge in row.get('resolved_aligned_filehash_edges',[]) or []:
            h=norm(edge.get('target'))
            if h not in labels:
                continue
            rec={
                'scope':sh,
                'offset':int(edge['offset']),
                'target':h,
                'target_label':labels[h],
                'target_reference':norm(edge.get('target_reference')),
                'target_package_id':edge.get('target_package_id'),
                'target_type':edge.get('target_type'),
                'target_subtype':edge.get('target_subtype'),
                'target_size':edge.get('target_size'),
            }
            hits.append(rec); target_hits[h].append(rec)
        if hits:
            scope_rows.append({
                'scope':sh,
                'package_id':row.get('package_id'),
                'entry_index':row.get('entry_index'),
                'payload_bytes':row.get('payload_bytes'),
                'payload_sha256':row.get('payload_sha256'),
                'hits':sorted(hits,key=lambda x:(x['offset'],x['target'])),
                'target_hashes':sorted({x['target'] for x in hits}),
            })

    target_summary=[]
    for h,label in sorted(labels.items()):
        hs=target_hits.get(h,[])
        target_summary.append({
            'target':h,'label':label,
            'hit_count':len(hs),
            'scope_count':len({x['scope'] for x in hs}),
            'scopes':sorted({x['scope'] for x in hs}),
            'offset_histogram':dict(sorted(collections.Counter(str(x['offset']) for x in hs).items(),key=lambda x:int(x[0]))),
        })

    co=collections.Counter()
    for r in scope_rows:
        hs=r['target_hashes']
        for i,a0 in enumerate(hs):
            for b0 in hs[i+1:]:
                co[(a0,b0)]+=1
    co_rows=[{'a':x[0],'a_label':labels[x[0]],'b':x[1],'b_label':labels[x[1]],'scope_count':n}
             for x,n in sorted(co.items(),key=lambda x:(-x[1],x[0]))]

    out={
        'schema':'d1_scope_target_hash_correlation/v1',
        'status':'D1_SCOPE_TARGET_HASH_CORRELATION_EXACT' if not violations else 'D1_SCOPE_TARGET_HASH_CORRELATION_PARTIAL',
        'scope_class':SCOPE_CLASS,
        'source_scope_entry_count':sum(norm(x.get('reference'))==SCOPE_CLASS for x in src.get('rows',[])),
        'target_count':len(labels),
        'targets':target_summary,
        'scope_with_target_hit_count':len(scope_rows),
        'scope_rows':sorted(scope_rows,key=lambda x:x['scope']),
        'cooccurrence':co_rows,
        'violations':violations,
        'gates':{
            'exact_aligned_filehash_correlation_closed':not violations,
            'scope_field_semantics_closed':False,
            'api15_producer_closed':False,
            'runtime_t4_binding_closed':False,
        },
        'policy':'A hit proves only that an aligned u32 in an exact current s_scope payload resolves to the target current FileHash. No field meaning, API slot, descriptor ownership, draw association, or runtime producer role is inferred.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],
        'source_scope_entry_count':out['source_scope_entry_count'],
        'scope_with_target_hit_count':len(scope_rows),
        'targets':[(x['target'],x['label'],x['hit_count'],x['scope_count']) for x in target_summary],
        'cooccurrence':co_rows[:30],
        'violations':violations,
    },indent=2))
    return 0 if out['status']=='D1_SCOPE_TARGET_HASH_CORRELATION_EXACT' else 2

if __name__=='__main__':
    raise SystemExit(main())
