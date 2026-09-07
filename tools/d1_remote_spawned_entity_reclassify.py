#!/usr/bin/env python3
"""Reopen a source-pinned set of D1 spawned EntitySKs through the universal retail corpus.

The earlier Tower AI census intentionally used a bounded recovered dependency corpus.
That proved the nested NPC/enemy/AI carrier architecture, but some spawned SEntities
contained FileHashes whose encoded package families were not staged, which could
under-classify skeletons, rigs, children, or other composition resources.

This probe removes that boundary.  It routes every EntitySK and every dependency
FileHash through the verified universal member catalog and the split retail archive,
then calls the same source-pinned `parse_entity` implementation used by the local
world dependency census.  No missing dependency is interpreted as absence.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar
from d1_remote_activity_placements import RemoteCorpus
from d1_world_entity_dependency_census import parse_entity

NULLS={'00000000','FFFFFFFF'}


def norm(x): return str(x).upper().removeprefix('0X').zfill(8)


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--seed',type=Path,required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    seed=json.loads(a.seed.read_text())
    entities=sorted({norm(x) for x in seed.get('entity_hashes',[]) if norm(x) not in NULLS})
    if not entities: raise SystemExit('seed contains no entity_hashes')
    cats=load_catalogs(a.member_catalog)
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    c=RemoteCorpus(arc,cats,a.runtime)

    rows={};viol=[];class_counts=collections.Counter();role_counts=collections.Counter();bone_counts=collections.Counter()
    specific=collections.Counter();generic=collections.Counter();unresolved=[]
    for i,h in enumerate(entities,1):
        try: row=parse_entity(c,h)
        except Exception as ex:
            row={'entity':h,'violations':['parse_entity:'+repr(ex)]}
        rows[h]=row
        for v in row.get('violations',[]): viol.append(f'{h}:{v}')
        comp=row.get('composition') or {}
        class_counts[comp.get('classification','unparsed')]+=1
        for k,n in (comp.get('resource_role_counts') or {}).items(): role_counts[k]+=int(n)
        for n in comp.get('bone_counts',[]): bone_counts[str(int(n))]+=1
        for x in comp.get('specific_name_hashes',[]): specific[norm(x)]+=1
        for x in comp.get('generic_name_hashes',[]): generic[norm(x)]+=1
        for r in row.get('resources',[]):
            if not r.get('is_null_sentinel') and (r.get('meta') is None or r.get('entity_resource') is None):
                unresolved.append({'entity':h,'resource_hash':r.get('resource_hash'),'package_id':r.get('package_id'),'meta_present':r.get('meta') is not None})
        print(i,h,comp.get('classification'),comp.get('bone_counts'),comp.get('specific_name_hashes'),flush=True)

    model_skeleton=[h for h,r in rows.items() if (r.get('composition') or {}).get('has_visual_model') and (r.get('composition') or {}).get('has_skeleton')]
    runtime_rig=[h for h,r in rows.items() if (r.get('composition') or {}).get('has_runtime_rig')]
    children=[h for h,r in rows.items() if (r.get('composition') or {}).get('has_children')]
    named=[h for h,r in rows.items() if (r.get('composition') or {}).get('specific_name_hashes') or (r.get('composition') or {}).get('generic_name_hashes')]
    out={
      'schema_version':1,
      'status':'D1_REMOTE_SPAWNED_ENTITY_RECLASSIFY_COMPLETE' if not viol and not unresolved else 'D1_REMOTE_SPAWNED_ENTITY_RECLASSIFY_PARTIAL',
      'source_seed':str(a.seed),'seed_status':seed.get('status'),'entity_count':len(entities),
      'classification_counts':dict(class_counts),'resource_role_counts':dict(role_counts),
      'bone_count_frequency':dict(sorted(bone_counts.items(),key=lambda kv:int(kv[0]))),
      'model_and_skeleton_entity_count':len(model_skeleton),'model_and_skeleton_entities':model_skeleton,
      'runtime_rig_entity_count':len(runtime_rig),'runtime_rig_entities':runtime_rig,
      'entity_children_entity_count':len(children),'entity_children_entities':children,
      'named_entity_count':len(named),'named_entities':named,
      'specific_name_hash_counts':dict(specific),'generic_name_hash_counts':dict(generic),
      'unresolved_dependency_count':len(unresolved),'unresolved_dependencies':unresolved,
      'entities':rows,'violations':viol,
      'remote_logical_package_count':len(c.views),'remote_payload_cache_count':len(c.payload_cache),
      'policy':'Every source-seeded EntitySK and dependency is reopened through the universal exact retail package catalog. Classification comes only from serialized SEntity EntityResource membership and source-pinned class layouts. No visual, package-name, or proximity inference is used.'
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','entity_count','classification_counts','bone_count_frequency','model_and_skeleton_entity_count','runtime_rig_entity_count','entity_children_entity_count','named_entity_count','specific_name_hash_counts','generic_name_hash_counts','unresolved_dependency_count','violations')},indent=2))
    return 0 if out['status'].endswith('_COMPLETE') else 2

if __name__=='__main__': raise SystemExit(main())
