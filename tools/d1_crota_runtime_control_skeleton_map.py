#!/usr/bin/env python3
"""Map Crota runtime-rig controls onto exact skeleton nodes and retarget boundary.

Inputs are exact runtime-rig mapping arrays, the exact EntitySkeleton hierarchy,
and the selected-clip runtime-component boundary.  Controls are classified only by
whether their index lies inside the proven 37-control shared retargetable prefix.

No control or bone behavior/name is inferred.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--runtime-rig',type=Path,required=True)
 ap.add_argument('--s-entity',type=Path,required=True)
 ap.add_argument('--component-boundary',type=Path,required=True)
 ap.add_argument('--skeleton-resource',required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 rg=json.loads(a.runtime_rig.read_text());se=json.loads(a.s_entity.read_text());bd=json.loads(a.component_boundary.read_text());v=[]
 if rg.get('schema')!='d1_remote_runtime_rig_probe/v1' or rg.get('rig_resource_tag_hash')!='8108E4CB':v.append('runtime rig identity/schema drift')
 if int(rg.get('control_count',-1))!=44:v.append(f"runtime rig control count {rg.get('control_count')} != 44")
 if bd.get('status')!='D1_CROTA_RUNTIME_COMPONENT_BOUNDARY_EXACT' or bd.get('violations'):v.append('component boundary not exact')
 prefix=int(bd.get('shared_retargetable_control_prefix_count',-1))
 if prefix!=37:v.append(f'shared prefix {prefix} != 37')
 wanted=norm(a.skeleton_resource);hits=[]
 for e in se.get('entries',[]):
  for sk in e.get('skeletons',[]):
   if norm(sk.get('resource_hash'))==wanted:hits.append(sk)
 if len(hits)!=1:v.append(f'skeleton {wanted}: expected one row, got {len(hits)}');nodes=[]
 else:nodes=hits[0].get('nodes') or []
 if len(nodes)!=50:v.append(f'skeleton node count {len(nodes)} != 50')
 fields=rg.get('decoded_fields') or {}
 ctb=[int(x) for x in fields.get('control_to_bone') or []]
 btc=[int(x) for x in fields.get('bone_to_control') or []]
 if len(ctb)!=44:v.append(f'control_to_bone length {len(ctb)} != 44')
 if len(btc)!=50:v.append(f'bone_to_control length {len(btc)} != 50')
 rows=[];bone_controls=collections.defaultdict(list)
 for ci,bi in enumerate(ctb):
  if not (0<=bi<len(nodes)):
   v.append(f'control {ci}: bone index {bi} outside skeleton');continue
  n=nodes[bi]
  cls='SHARED_RETARGETABLE_PREFIX' if ci<prefix else 'TARGET_ONLY_SUFFIX'
  row={'control_index':ci,'bone_index':bi,'node_hash':n['node_hash'],
       'parent_node_index':int(n['parent_node_index']),
       'first_child_node_index':int(n['first_child_node_index']),
       'next_sibling_node_index':int(n['next_sibling_node_index']),
       'retarget_boundary_class':cls}
  rows.append(row);bone_controls[bi].append(ci)
 # Cross-check inverse map where the parser supplies a concrete control.
 inverse_mismatch=[]
 for bi,ci in enumerate(btc):
  if ci<0:continue
  if ci>=len(ctb) or ctb[ci]!=bi:inverse_mismatch.append({'bone_index':bi,'bone_to_control':ci,'control_to_bone':None if ci>=len(ctb) else ctb[ci]})
 if inverse_mismatch:v.append(f'bone/control inverse mismatch count {len(inverse_mismatch)}')
 suffix=[x for x in rows if x['retarget_boundary_class']=='TARGET_ONLY_SUFFIX']
 out={'schema':'d1_crota_runtime_control_skeleton_map/v1',
      'status':'D1_CROTA_RUNTIME_CONTROL_SKELETON_MAP_EXACT' if len(rows)==44 and not v else 'D1_CROTA_RUNTIME_CONTROL_SKELETON_MAP_PARTIAL',
      'runtime_rig':'8108E4CB','skeleton_resource':wanted,'skeleton_node_count':len(nodes),
      'control_count':len(rows),'shared_prefix_control_count':prefix,'target_only_suffix_control_count':len(suffix),
      'controls':rows,'target_only_suffix_controls':suffix,
      'controlled_skeleton_node_count':len(bone_controls),
      'skeleton_nodes_without_direct_control_count':len(nodes)-len(bone_controls),
      'inverse_mapping_mismatches':inverse_mismatch,'violations':v,
      'semantic_boundary':{'control_to_bone':'EXACT_PARSER_MAPPING','retarget_boundary':'EXACT_SELECTED_CLIP_COMPONENT_PREFIX','control_names':'WITHHELD','bone_names':'WITHHELD','target_only_suffix_behavior':'WITHHELD'},
      'policy':'The 37/7 classification is purely the exact component-prefix boundary observed across selected clips. A target-only suffix control is not assigned any gameplay or anatomical role.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'controlled_nodes':out['controlled_skeleton_node_count'],
                   'suffix_controls':[(x['control_index'],x['bone_index'],x['node_hash'],x['parent_node_index']) for x in suffix],
                   'violations':v},indent=2))
 return 0 if out['status']=='D1_CROTA_RUNTIME_CONTROL_SKELETON_MAP_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
