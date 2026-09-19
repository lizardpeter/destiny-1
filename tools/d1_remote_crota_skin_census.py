#!/usr/bin/env python3
"""Run the exact Crota skin census directly from verified remote D1 package catalogs.

This is the reusable form of the original Crota skin-census workflow inline driver.
All decoding remains delegated to d1_world_articulated_skin_census.py.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar
from d1_remote_activity_placements import RemoteCorpus
from d1_world_articulated_skin_census import inspect_family,PINNED_PROJECT_PROOF

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--member-catalog',type=Path,action='append',required=True)
 ap.add_argument('--base-url',required=True)
 ap.add_argument('--part-count',type=int,default=10)
 ap.add_argument('--runtime',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 cats=load_catalogs(a.member_catalog)
 base=a.base_url.rstrip('/')
 arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
 c=RemoteCorpus(arc,cats,a.runtime)
 seed={
  'family_key':'CROTA_SON_OF_ORYX_8108E484',
  'entities':['8108E484'],'models':['8108E5B7'],
  'skeleton_resources':['8108E4BB'],'bone_counts':[50],
  'runtime_rig_resources':['8108E4CB'],
  'runtime_placement_count':1,'serialized_placement_reference_count':1,'source_entity_count':1,
 }
 f=inspect_family(c,seed)
 viol=list(f.get('violations',[]));front=list(f.get('frontiers',[]))
 out={
  'schema':'d1_crota_exact_skin_census/v2',
  'status':'D1_CROTA_EXACT_SKIN_CENSUS_COMPLETE' if not viol and not front else ('D1_CROTA_EXACT_SKIN_CENSUS_FRONTIER' if not viol else 'D1_CROTA_EXACT_SKIN_CENSUS_PARTIAL'),
  'semantic_identity':{'entity':'8108E484','entity_name_hash':'64C53DB9','entity_name':'Crota, Son of Oryx'},
  'physical':{'model':'8108E5B7','skeleton_resource':'8108E4BB','skeleton_node_count':50,'runtime_rig':'8108E4CB'},
  'project_proof_basis':PINNED_PROJECT_PROOF,'family_count':1,'families':[f],
  'mesh_count':int(f.get('mesh_count',0)),'inline_mesh_count':int(f.get('inline_mesh_count',0)),
  'separate_old_weights_mesh_count':int(f.get('separate_old_weights_mesh_count',0)),
  'unsupported_inline_mesh_count':int(f.get('unsupported_inline_mesh_count',0)),
  'unsupported_separate_old_weights_mesh_count':int(f.get('unsupported_separate_old_weights_mesh_count',0)),
  'frontiers':front,'violations':viol,
  'policy':'Identity/model/skeleton/runtime-rig are the exact source-closed Crota chain. Skin storage is decoded only through source-closed D1 PS4 formats; no influence is fabricated, normalized, repaired or guessed.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print('STATUS',out['status'],'MESHES',out['mesh_count'],'INLINE',out['inline_mesh_count'],'SEPARATE',out['separate_old_weights_mesh_count'],'FRONTIERS',len(front),'VIOLATIONS',len(viol))
 for m in f.get('meshes',[]):
  s=m.get('skin') or {}
  print('MESH',m['mesh_index'],'V1',m['vertices1'],'PRIMARY_STRIDE',m.get('primary_stride'),'OLD_WEIGHTS',m['old_weights'],
        'STORAGE',s.get('storage'),'WEIGHT_STRIDE',s.get('stride'),'VERTICES',s.get('vertex_count'),
        'MODES',s.get('mode_counts'),'BONE_DOMAIN',s.get('bone_domain'),'SUMS',s.get('weight_sum_min'),s.get('weight_sum_max'))
 return 0 if out['status']=='D1_CROTA_EXACT_SKIN_CENSUS_COMPLETE' else 2
if __name__=='__main__':raise SystemExit(main())
