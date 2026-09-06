#!/usr/bin/env python3
"""Turn D1_CURRENT_EVERYTHING.sqlite into deterministic export/resolution shards.

Every current Tiger entry appears exactly once in one of three readiness buckets:
  * standalone_ready: an exact decoder can export the resource in isolation;
  * context_required: the class is known but ownership/rig/placement/etc. is needed;
  * unknown: class/type semantics are not yet registered.

This is scheduling metadata only. It never changes evidence confidence or claims a
standalone decode is a complete semantic asset.
"""
from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

FIELDS=('package_name','package_id','entry_index','tag_hash','reference','type','subtype','file_size',
        'class_label','export_route','standalone_export','semantic_status','route_tool')


def rowdict(r):
    return dict(zip(FIELDS,r))


def safe(s:str)->str:
    return ''.join(c if c.isalnum() or c in '-_.' else '_' for c in s)


def write_tsv(path:Path,rows:list[dict]):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS,delimiter='\t');w.writeheader();w.writerows(rows)


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('sqlite',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--shard-size',type=int,default=1000)
    a=ap.parse_args()
    if a.shard_size<=0:raise ValueError('shard-size must be positive')
    a.out.mkdir(parents=True,exist_ok=True)

    db=sqlite3.connect(a.sqlite)
    try:
        cols=','.join(FIELDS)
        rows=[rowdict(r) for r in db.execute(f'SELECT {cols} FROM current_entries ORDER BY package_id,entry_index')]
        if not rows:raise ValueError('current_entries is empty')
        buckets={'standalone_ready':[],'context_required':[],'unknown':[]}
        by_route=defaultdict(list);unknown_refs=Counter();unknown_types=Counter()
        for r in rows:
            route=r['export_route']
            if route=='unknown':
                bucket='unknown';unknown_refs[r['reference']]+=1;unknown_types[f"{r['type']}:{r['subtype']}"]+=1
            elif int(r['standalone_export']):bucket='standalone_ready'
            else:bucket='context_required'
            r['standalone_export']=int(r['standalone_export'])
            buckets[bucket].append(r);by_route[route].append(r)

        manifest=[]
        for bucket,xs in buckets.items():
            write_tsv(a.out/f'{bucket}.tsv',xs)
        for route,xs in sorted(by_route.items()):
            rd=a.out/'routes'/safe(route);rd.mkdir(parents=True,exist_ok=True)
            for n,start in enumerate(range(0,len(xs),a.shard_size)):
                shard=xs[start:start+a.shard_size];p=rd/f'{route}_{n:04d}.tsv';write_tsv(p,shard)
                manifest.append({'route':route,'shard':n,'row_count':len(shard),'first_tag':shard[0]['tag_hash'],
                                 'last_tag':shard[-1]['tag_hash'],'path':str(p.relative_to(a.out))})

        summary={
          'schema':'d1_everything_export_plan/v1','current_entry_count':len(rows),
          'bucket_counts':{k:len(v) for k,v in buckets.items()},
          'route_counts':{k:len(v) for k,v in sorted(by_route.items())},
          'shard_size':a.shard_size,'shard_count':len(manifest),'shards':manifest,
          'unknown_reference_frequency':[{'reference':h,'count':n} for h,n in unknown_refs.most_common()],
          'unknown_type_subtype_frequency':[{'type_subtype':h,'count':n} for h,n in unknown_types.most_common()],
          'policy':'Every current indexed entry is scheduled exactly once. Standalone-ready means only that a resource decoder exists; semantic composition remains a separate graph-resolution stage.'}
        assert sum(summary['bucket_counts'].values())==len(rows)
        assert sum(summary['route_counts'].values())==len(rows)
        (a.out/'PLAN.json').write_text(json.dumps(summary,indent=2)+'\n')
        print(json.dumps({'current_entry_count':len(rows),'bucket_counts':summary['bucket_counts'],
                          'route_counts':summary['route_counts'],'shard_count':len(manifest),
                          'top_unknown_references':summary['unknown_reference_frequency'][:20]},indent=2))
        return 0
    finally:db.close()

if __name__=='__main__':raise SystemExit(main())
