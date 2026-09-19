#!/usr/bin/env python3
"""Join Crota skin usage and retargeted animation motion on the exact skeleton nodes.

Both inputs independently map into skeleton resource 8108E4BB. This tool requires
index/hash/hierarchy agreement and classifies each exact node by two observed uses:
nonzero retail skin influence references and dynamic local-space animation tracks.

The classes are structural only; they are not anatomical labels.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--skin-bone-map',type=Path,required=True)
 ap.add_argument('--motion-bone-map',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 s=json.loads(a.skin_bone_map.read_text());m=json.loads(a.motion_bone_map.read_text());v=[]
 if s.get('status')!='D1_CROTA_SKIN_BONE_MAP_EXACT' or s.get('violations'):v.append('skin bone map not exact')
 if m.get('status')!='D1_ANIMATION_MOTION_BONE_MAP_EXACT' or m.get('violations'):v.append('motion bone map not exact')
 if s.get('skeleton_resource')!=m.get('skeleton_resource'):v.append('skeleton resource mismatch')
 sn=s.get('nodes') or [];mn=m.get('node_activity_rows') or []
 if len(sn)!=len(mn):v.append(f'node count mismatch {len(sn)}/{len(mn)}')
 rows=[];classes=collections.Counter()
 for i,(a0,b0) in enumerate(zip(sn,mn)):
  for k in ('node_hash','parent_node_index','first_child_node_index','next_sibling_node_index'):
   if a0.get(k)!=b0.get(k):v.append(f'node {i}: {k} mismatch {a0.get(k)!r}/{b0.get(k)!r}')
  if int(a0.get('joint_index',-1))!=i or int(b0.get('index',-1))!=i:v.append(f'node {i}: index drift')
  skin=int(a0.get('skin_reference_count',0))
  anim=int(b0.get('dynamic_any_clip_instances',0))
  if skin>0 and anim>0:cl='SKIN_AND_DYNAMIC_MOTION'
  elif skin>0:cl='SKIN_ONLY_IN_CENSUS'
  elif anim>0:cl='DYNAMIC_MOTION_ONLY_IN_CENSUS'
  else:cl='NEITHER_SKIN_NOR_DYNAMIC_MOTION_IN_CENSUS'
  classes[cl]+=1
  rows.append({
   'index':i,'node_hash':a0.get('node_hash'),'parent_node_index':a0.get('parent_node_index'),
   'first_child_node_index':a0.get('first_child_node_index'),'next_sibling_node_index':a0.get('next_sibling_node_index'),
   'usage_class':cl,'skin_reference_count':skin,
   'skin_mesh_indices':a0.get('mesh_indices') or [],
   'dynamic_any_clip_instances':anim,
   'dynamic_scale_clip_instances':int(b0.get('dynamic_scale_clip_instances',0)),
   'dynamic_rotation_clip_instances':int(b0.get('dynamic_rotation_clip_instances',0)),
   'dynamic_translation_clip_instances':int(b0.get('dynamic_translation_clip_instances',0)),
  })
 out={'schema':'d1_crota_skeleton_usage_union/v1',
      'status':'D1_CROTA_SKELETON_USAGE_UNION_EXACT' if len(rows)==50 and not v else 'D1_CROTA_SKELETON_USAGE_UNION_PARTIAL',
      'skeleton_resource':s.get('skeleton_resource'),'node_count':len(rows),
      'usage_class_counts':dict(sorted(classes.items())),'nodes':rows,'violations':v,
      'structural_observations':{
       'skin_referenced_node_count':sum(x['skin_reference_count']>0 for x in rows),
       'dynamic_motion_node_count':sum(x['dynamic_any_clip_instances']>0 for x in rows),
       'skin_and_dynamic_node_count':sum(x['usage_class']=='SKIN_AND_DYNAMIC_MOTION' for x in rows),
       'skin_only_node_count':sum(x['usage_class']=='SKIN_ONLY_IN_CENSUS' for x in rows),
       'dynamic_only_node_count':sum(x['usage_class']=='DYNAMIC_MOTION_ONLY_IN_CENSUS' for x in rows),
       'neither_node_count':sum(x['usage_class']=='NEITHER_SKIN_NOR_DYNAMIC_MOTION_IN_CENSUS' for x in rows),
      },
      'semantic_boundary':{'usage_classes':'OBSERVED_DATASET_MEMBERSHIP_ONLY','helper_bone_label':'WITHHELD','anatomical_names':'WITHHELD','control_bone_label':'WITHHELD'},
      'policy':'A node can be called skin-referenced or dynamically varying only from the two exact input censuses. Dynamic-only nodes are not automatically helper/control bones, and neither nodes are not automatically unused by the engine.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'usage_class_counts':out['usage_class_counts'],
                   'observations':out['structural_observations'],
                   'dynamic_only':[(x['index'],x['node_hash'],x['parent_node_index'],x['dynamic_any_clip_instances']) for x in rows if x['usage_class']=='DYNAMIC_MOTION_ONLY_IN_CENSUS'],
                   'skin_only':[(x['index'],x['node_hash'],x['parent_node_index'],x['skin_reference_count']) for x in rows if x['usage_class']=='SKIN_ONLY_IN_CENSUS'],
                   'violations':v},indent=2))
 return 0 if out['status']=='D1_CROTA_SKELETON_USAGE_UNION_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
