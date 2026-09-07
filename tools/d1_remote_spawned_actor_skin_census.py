#!/usr/bin/env python3
"""Census exact D1 skin storage for the 57 Tower spawned-actor visual families.

Input is d1_remote_spawned_actor_visual_plan output.  The visual plan already proves
one exact EntityModel parent, model, skeleton resource and runtime rig per spawned
actor.  This adapter reuses the source-validated D1 PS4 skin decoder from
``d1_world_articulated_skin_census`` but resolves payloads lazily through the exact
universal package-member catalog instead of requiring a local multi-GB corpus.

No weight stream is repaired or guessed.  Unsupported layouts remain frontiers.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar
from d1_remote_activity_placements import RemoteCorpus
import d1_world_articulated_skin_census as skin


def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--visual-plan',type=Path,required=True);ap.add_argument('--member-catalog',type=Path,action='append',required=True);ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
 p=json.loads(a.visual_plan.read_text())
 if p.get('status')!='D1_WORLD_ARTICULATED_ENTITY_PLAN_COMPLETE' or p.get('semantic_scope')!='D1_TOWER_SPAWNED_AI_ACTOR_VISUAL_PLAN' or p.get('violations'):
  raise SystemExit(f'visual plan not closed spawned plan: {p.get("status")} {p.get("semantic_scope")} {p.get("violations")}')
 cats=load_catalogs(a.member_catalog);arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90);c=RemoteCorpus(arc,cats,a.runtime)
 families=[];viol=[];front=[]
 for f in p.get('families',[]):
  row={
   'family_key':f.get('family_id'),'entities':[norm(x) for x in f.get('entities',[])],
   'models':[norm(f.get('model'))],'skeleton_resources':[norm(x) for x in f.get('skeleton_resources',[])],
   'bone_counts':[int(x) for x in f.get('bone_counts',[])],
   'runtime_rig_resources':[norm(x) for x in f.get('runtime_rig_resources',[])],
   'runtime_placement_count':0,'serialized_placement_reference_count':0,
   'source_entity_count':int(f.get('entity_count',len(f.get('entities',[]))))
  }
  r=skin.inspect_family(c,row);families.append(r)
  viol.extend(f"{row['family_key']}:{x}" for x in r.get('violations',[]));front.extend(f"{row['family_key']}:{x}" for x in r.get('frontiers',[]))
 out={
  'schema':'d1_remote_spawned_actor_skin_census/v1',
  'status':'D1_TOWER_SPAWNED_ACTOR_SKIN_CENSUS_COMPLETE' if not viol and not front else ('D1_TOWER_SPAWNED_ACTOR_SKIN_CENSUS_FRONTIER' if not viol else 'D1_TOWER_SPAWNED_ACTOR_SKIN_CENSUS_PARTIAL'),
  'source_visual_plan':str(a.visual_plan),'source_entity_count':int(p.get('candidate_count',-1)),'family_count':len(families),
  'mesh_count':sum(int(x.get('mesh_count',0)) for x in families),
  'inline_mesh_count':sum(int(x.get('inline_mesh_count',0)) for x in families),
  'separate_old_weights_mesh_count':sum(int(x.get('separate_old_weights_mesh_count',0)) for x in families),
  'unsupported_inline_mesh_count':sum(int(x.get('unsupported_inline_mesh_count',0)) for x in families),
  'unsupported_separate_old_weights_mesh_count':sum(int(x.get('unsupported_separate_old_weights_mesh_count',0)) for x in families),
  'families':families,'frontiers':front,'violations':viol,
  'remote_logical_package_count':len(c.views),'remote_payload_cache_count':len(c.payload_cache),
  'policy':'Family/model/skeleton/rig ownership is inherited only from the exact spawned-actor visual plan. Skin bytes use the source-validated D1 PS4 decoder; unsupported layouts fail closed and no weights are normalized, repaired, or guessed.'
 }
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
 print('STATUS',out['status'],'ENTITIES',out['source_entity_count'],'FAMILIES',out['family_count'],'MESHES',out['mesh_count'],'INLINE',out['inline_mesh_count'],'SEPARATE',out['separate_old_weights_mesh_count'],'FRONTIERS',len(front),'VIOLATIONS',len(viol))
 for f in families:print('FAMILY',f.get('family_key'),'MODEL',f.get('model'),'BONES',f.get('bone_counts'),'RIGS',f.get('runtime_rig_resources'),'MESHES',f.get('mesh_count'),'INLINE',f.get('inline_mesh_count'),'SEPARATE',f.get('separate_old_weights_mesh_count'),'FRONT',len(f.get('frontiers',[])),'VIOL',len(f.get('violations',[])))
 for x in front:print('FRONTIER',x)
 for x in viol:print('VIOLATION',x)
 return 0 if not viol and not front else 2
if __name__=='__main__':raise SystemExit(main())
