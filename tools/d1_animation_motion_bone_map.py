#!/usr/bin/env python3
"""Map exact retargeted animation-motion track indices onto an exact D1 skeleton.

The motion census stores anonymous target-track indices. This adapter joins those
indices to the source-closed EntitySkeleton hierarchy preserved by the remote exact
s_entity probe.

No anatomical or behavioral names are invented. Bone identity remains the exact
32-bit node hash plus hierarchy indices.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--motion-census',type=Path,required=True)
 ap.add_argument('--s-entity',type=Path,required=True)
 ap.add_argument('--skeleton-resource',required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 m=json.loads(a.motion_census.read_text());s=json.loads(a.s_entity.read_text());violations=[]
 if m.get('status')!='D1_ANIMATION_MOTION_CENSUS_EXACT':violations.append('motion census not exact')
 if s.get('status')!='D1_EXACT_S_ENTITY_PROBE' or s.get('violation_count'):violations.append('s_entity probe not exact')
 wanted=norm(a.skeleton_resource);hits=[]
 for e in s.get('entries',[]):
  for sk in e.get('skeletons',[]):
   if norm(sk.get('resource_hash'))==wanted:hits.append(sk)
 if len(hits)!=1:
  violations.append(f'skeleton {wanted}: expected one exact row, got {len(hits)}')
  sk={'nodes':[],'node_count':0}
 else:sk=hits[0]
 nodes=sk.get('nodes') or []
 if int(sk.get('node_count',-1))!=len(nodes):violations.append('skeleton node_count/nodes length mismatch')
 for i,n in enumerate(nodes):
  if int(n.get('index',-1))!=i:violations.append(f'skeleton node index drift at {i}')
 counts={k:collections.Counter() for k in ('any','scale','rotation','translation')}
 rows=[]
 for r in m.get('rows',[]):
  if int(r.get('target_node_count',-1))!=len(nodes):
   violations.append(f"{r.get('clip')}: target node count {r.get('target_node_count')} != skeleton {len(nodes)}")
   continue
  ms=r.get('local_motion_summary') or {}
  mapped={}
  for kind,key in (
      ('any','dynamic_any_track_indices'),
      ('scale','dynamic_scale_track_indices'),
      ('rotation','dynamic_rotation_track_indices'),
      ('translation','dynamic_translation_track_indices'),
  ):
   out=[]
   for raw in ms.get(key,[]) or []:
    i=int(raw)
    if i<0 or i>=len(nodes):
     violations.append(f"{r.get('clip')}:{key}: index {i} out of range")
     continue
    n=nodes[i]
    out.append({
      'index':i,'node_hash':n['node_hash'],
      'parent_node_index':int(n['parent_node_index']),
      'first_child_node_index':int(n['first_child_node_index']),
      'next_sibling_node_index':int(n['next_sibling_node_index']),
    })
    counts[kind][i]+=1
   mapped[kind]=out
  rows.append({
   'target_id':r.get('target_id'),'control':r.get('control'),'clip':r.get('clip'),
   'frame_count':r.get('frame_count'),'source_dimensions_exact':r.get('source_dimensions_exact'),
   'dynamic_track_nodes':mapped,
   'bone0_translation_syntax':ms.get('bone0_translation_syntax'),
  })
 node_activity=[]
 for i,n in enumerate(nodes):
  node_activity.append({
   'index':i,'node_hash':n['node_hash'],
   'parent_node_index':int(n['parent_node_index']),
   'first_child_node_index':int(n['first_child_node_index']),
   'next_sibling_node_index':int(n['next_sibling_node_index']),
   'dynamic_any_clip_instances':counts['any'][i],
   'dynamic_scale_clip_instances':counts['scale'][i],
   'dynamic_rotation_clip_instances':counts['rotation'][i],
   'dynamic_translation_clip_instances':counts['translation'][i],
  })
 out={
  'schema':'d1_animation_motion_bone_map/v1',
  'status':'D1_ANIMATION_MOTION_BONE_MAP_EXACT' if rows and not violations else 'D1_ANIMATION_MOTION_BONE_MAP_PARTIAL',
  'skeleton_resource':wanted,'skeleton_node_count':len(nodes),
  'clip_instance_count':len(rows),'rows':rows,
  'node_activity_rows':node_activity,
  'nodes_dynamic_in_any_clip_instance':sum(1 for x in node_activity if x['dynamic_any_clip_instances']>0),
  'nodes_dynamic_translation_in_any_clip_instance':sum(1 for x in node_activity if x['dynamic_translation_clip_instances']>0),
  'nodes_dynamic_rotation_in_any_clip_instance':sum(1 for x in node_activity if x['dynamic_rotation_clip_instances']>0),
  'nodes_dynamic_scale_in_any_clip_instance':sum(1 for x in node_activity if x['dynamic_scale_clip_instances']>0),
  'violations':violations,
  'semantic_boundary':{
    'node_identity':'EXACT_HASH_AND_HIERARCHY',
    'track_to_node_index':'EXACT_TARGET_TRACK_ORDER',
    'anatomical_names':'WITHHELD',
    'behavioral_clip_names':'WITHHELD',
    'bone0_root_motion_semantic':'WITHHELD',
  },
  'policy':'Track indices are joined only to the exact target EntitySkeleton node array. Hashes and hierarchy are source data; no anatomical names or behavioral meanings are inferred.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 top=sorted(node_activity,key=lambda x:(-x['dynamic_any_clip_instances'],x['index']))[:15]
 print(json.dumps({'status':out['status'],'skeleton_node_count':len(nodes),'clip_instances':len(rows),
                   'nodes_dynamic_any':out['nodes_dynamic_in_any_clip_instance'],'top_dynamic_nodes':top,'violations':violations},indent=2))
 return 0 if out['status']=='D1_ANIMATION_MOTION_BONE_MAP_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
