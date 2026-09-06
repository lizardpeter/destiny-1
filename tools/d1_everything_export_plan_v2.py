#!/usr/bin/env python3
"""Build deterministic namespace-safe export shards from D1 everything-index v2.

D1 localized packages reuse FileHash values across language namespaces. A FileHash by
itself is therefore not a globally unique export identity in the complete 2,105-package
physical corpus. This planner makes the namespace part of every scheduled identity:

    resource_key = <namespace_key>:<tag_hash>

Every current entry appears exactly once in one readiness bucket and exactly once in
one route shard. Shards are split by route *and namespace kind* so a downstream worker
cannot accidentally treat localized entries as base resources merely because their
FileHash matches.

This is scheduling metadata only. It does not increase evidence confidence and it does
not claim that a standalone decoder produces a complete semantic asset.
"""
from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

DB_FIELDS=(
    'package_name','namespace_kind','namespace_key','locale','package_id',
    'package_generation','package_patch_id','entry_index','tag_hash','reference',
    'type','subtype','file_size','class_label','export_route','standalone_export',
    'classification_source','semantic_status','route_tool'
)
OUT_FIELDS=(
    'resource_key',*DB_FIELDS
)


def safe(s: str) -> str:
    return ''.join(c if c.isalnum() or c in '-_.' else '_' for c in str(s))


def rowdict(row) -> dict:
    d=dict(zip(DB_FIELDS,row))
    d['standalone_export']=int(d['standalone_export'])
    d['resource_key']=f"{d['namespace_key']}:{d['tag_hash']}"
    return d


def write_tsv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=OUT_FIELDS,delimiter='\t',extrasaction='ignore')
        w.writeheader(); w.writerows(rows)


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('sqlite',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--shard-size',type=int,default=1000)
    a=ap.parse_args()
    if a.shard_size<=0: raise ValueError('shard-size must be positive')
    a.out.mkdir(parents=True,exist_ok=True)

    db=sqlite3.connect(a.sqlite)
    try:
        cols=','.join(DB_FIELDS)
        rows=[rowdict(r) for r in db.execute(
            f'''SELECT {cols} FROM current_entries
                ORDER BY namespace_kind,namespace_key,package_id,entry_index''')]
        if not rows: raise ValueError('current_entries is empty')

        buckets={'standalone_ready':[],'context_required':[],'unknown':[]}
        by_route_kind=defaultdict(list)
        by_route=Counter(); by_namespace_kind=Counter(); by_namespace=Counter()
        unknown_refs=Counter(); unknown_types=Counter(); unknown_by_kind=Counter()
        resource_occurrences=Counter()

        for r in rows:
            route=r['export_route']
            kind=r['namespace_kind']
            resource_occurrences[r['resource_key']]+=1
            by_namespace_kind[kind]+=1
            by_namespace[r['namespace_key']]+=1
            by_route[route]+=1
            by_route_kind[(route,kind)].append(r)
            if route=='unknown':
                bucket='unknown'
                unknown_refs[r['reference']]+=1
                unknown_types[f"{r['type']}:{r['subtype']}"]+=1
                unknown_by_kind[kind]+=1
            elif r['standalone_export']:
                bucket='standalone_ready'
            else:
                bucket='context_required'
            buckets[bucket].append(r)

        for bucket,xs in buckets.items():
            write_tsv(a.out/f'{bucket}.tsv',xs)

        manifest=[]
        scheduled_keys=[]
        for (route,kind),xs in sorted(by_route_kind.items()):
            rd=a.out/'routes'/safe(route)/safe(kind)
            rd.mkdir(parents=True,exist_ok=True)
            for n,start in enumerate(range(0,len(xs),a.shard_size)):
                shard=xs[start:start+a.shard_size]
                p=rd/f'{safe(route)}_{safe(kind)}_{n:04d}.tsv'
                write_tsv(p,shard)
                scheduled_keys.extend((x['namespace_key'],x['package_name'],x['entry_index']) for x in shard)
                manifest.append({
                    'route':route,'namespace_kind':kind,'shard':n,'row_count':len(shard),
                    'first_resource_key':shard[0]['resource_key'],
                    'last_resource_key':shard[-1]['resource_key'],
                    'namespace_key_count':len({x['namespace_key'] for x in shard}),
                    'path':str(p.relative_to(a.out)),
                })

        identity_collisions=[
            {'resource_key':k,'current_entry_occurrence_count':n}
            for k,n in resource_occurrences.most_common() if n>1
        ]
        tag_namespaces=defaultdict(set)
        for r in rows: tag_namespaces[r['tag_hash']].add(r['namespace_key'])
        cross_namespace_hashes=sorted(
            ((h,len(ns)) for h,ns in tag_namespaces.items() if len(ns)>1),
            key=lambda x:(-x[1],x[0])
        )

        summary={
            'schema':'d1_everything_export_plan_v2/v1',
            'identity_rule':'resource_key = namespace_key + ":" + tag_hash',
            'current_entry_count':len(rows),
            'current_namespace_count':len(by_namespace),
            'namespace_kind_entry_counts':dict(sorted(by_namespace_kind.items())),
            'bucket_counts':{k:len(v) for k,v in buckets.items()},
            'route_counts':dict(sorted(by_route.items())),
            'route_namespace_kind_counts':{
                f'{route}|{kind}':len(xs) for (route,kind),xs in sorted(by_route_kind.items())
            },
            'shard_size':a.shard_size,
            'shard_count':len(manifest),
            'shards':manifest,
            'same_resource_key_multiple_current_entries':identity_collisions,
            'cross_namespace_filehash_count':len(cross_namespace_hashes),
            'top_cross_namespace_filehashes':[
                {'tag_hash':h,'namespace_count':n} for h,n in cross_namespace_hashes[:100]
            ],
            'unknown_reference_frequency':[
                {'reference':h,'count':n} for h,n in unknown_refs.most_common()
            ],
            'unknown_type_subtype_frequency':[
                {'type_subtype':h,'count':n} for h,n in unknown_types.most_common()
            ],
            'unknown_by_namespace_kind':dict(sorted(unknown_by_kind.items())),
            'policy':(
                'Every current indexed entry is scheduled exactly once. FileHash is never treated as '
                'globally unique across base/localized/special namespaces. Standalone-ready means only '
                'that a resource decoder exists; semantic composition remains a separate graph-resolution stage.'
            ),
        }
        assert sum(summary['bucket_counts'].values())==len(rows)
        assert sum(summary['route_counts'].values())==len(rows)
        assert len(scheduled_keys)==len(rows)
        assert len(set(scheduled_keys))==len(rows), 'a current physical entry was scheduled more than once'
        (a.out/'PLAN.json').write_text(json.dumps(summary,indent=2)+'\n')
        print(json.dumps({
            'current_entry_count':len(rows),
            'current_namespace_count':summary['current_namespace_count'],
            'namespace_kind_entry_counts':summary['namespace_kind_entry_counts'],
            'bucket_counts':summary['bucket_counts'],
            'route_counts':summary['route_counts'],
            'shard_count':len(manifest),
            'cross_namespace_filehash_count':summary['cross_namespace_filehash_count'],
            'top_unknown_references':summary['unknown_reference_frequency'][:20],
        },indent=2))
        return 0
    finally:
        db.close()


if __name__=='__main__':
    raise SystemExit(main())
