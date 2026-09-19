#!/usr/bin/env python3
"""Join exact Crota skin joint indices to the exact 50-node skeleton hierarchy.

The skin census already proves every nonzero influence is inside the source-owned
skeleton. This adapter turns anonymous joint indices into exact node hashes and
hierarchy relationships and aggregates reference density per mesh and per bone.

No anatomical names are assigned.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--skin-census',type=Path,required=True)
 ap.add_argument('--s-entity',type=Path,required=True)
 ap.add_argument('--skeleton-resource',required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 sc=json.loads(a.skin_census.read_text());se=json.loads(a.s_entity.read_text());v=[]
 if sc.get('status')!='D1_CROTA_EXACT_SKIN_CENSUS_COMPLETE' or sc.get('violations') or sc.get('frontiers'):v.append('skin census not exact complete')
 if se.get('status')!='D1_EXACT_S_ENTITY_PROBE' or se.get('violation_count'):v.append('s_entity probe not exact')
 wanted=norm(a.skeleton_resource);hits=[]
 for e in se.get('entries',[]):
  for sk in e.get('skeletons',[]):
   if norm(sk.get('resource_hash'))==wanted:hits.append(sk)
 if len(hits)!=1:
  v.append(f'skeleton {wanted}: expected one row, got {len(hits)}');nodes=[]
 else:nodes=hits[0].get('nodes') or []
 if len(nodes)!=50:v.append(f'skeleton node count {len(nodes)} != 50')
 fams=sc.get('families') or []
 if len(fams)!=1:v.append(f'skin family count {len(fams)} != 1')
 meshes=(fams[0].get('meshes') or []) if fams else []
 global_refs=collections.Counter();mesh_rows=[]
 for m in meshes:
  skin=m.get('skin') or {}
  refs={int(k):int(n) for k,n in (skin.get('bone_reference_counts') or {}).items()}
  dom=sorted(int(x) for x in skin.get('bone_domain') or [])
  if dom!=sorted(refs):v.append(f"mesh {m.get('mesh_index')}: bone_domain/reference key mismatch")
  mapped=[]
  for i in dom:
   if i<0 or i>=len(nodes):
    v.append(f"mesh {m.get('mesh_index')}: joint {i} outside node list");continue
   n=nodes[i];count=refs[i];global_refs[i]+=count
   mapped.append({
    'joint_index':i,'node_hash':n['node_hash'],
    'parent_node_index':int(n['parent_node_index']),
    'first_child_node_index':int(n['first_child_node_index']),
    'next_sibling_node_index':int(n['next_sibling_node_index']),
    'nonzero_influence_reference_count':count,
   })
  mesh_rows.append({
   'mesh_index':int(m['mesh_index']),'storage':skin.get('storage'),'stride':skin.get('stride'),
   'vertex_count':int(skin.get('vertex_count',0)),'mode_counts':skin.get('mode_counts'),
   'weight_sum_min':skin.get('weight_sum_min'),'weight_sum_max':skin.get('weight_sum_max'),
   'referenced_joint_count':len(dom),'referenced_joints':mapped,
  })
 node_rows=[]
 for i,n in enumerate(nodes):
  node_rows.append({
   'joint_index':i,'node_hash':n['node_hash'],
   'parent_node_index':int(n['parent_node_index']),
   'first_child_node_index':int(n['first_child_node_index']),
   'next_sibling_node_index':int(n['next_sibling_node_index']),
   'skin_reference_count':global_refs[i],
   'referenced_by_skin':global_refs[i]>0,
   'mesh_indices':[x['mesh_index'] for x in mesh_rows if any(j['joint_index']==i for j in x['referenced_joints'])],
  })
 out={'schema':'d1_crota_skin_bone_map/v1',
      'status':'D1_CROTA_SKIN_BONE_MAP_EXACT' if len(mesh_rows)==3 and not v else 'D1_CROTA_SKIN_BONE_MAP_PARTIAL',
      'skeleton_resource':wanted,'skeleton_node_count':len(nodes),'mesh_count':len(mesh_rows),
      'skin_referenced_joint_count':sum(1 for x in node_rows if x['referenced_by_skin']),
      'unreferenced_skeleton_joint_count':sum(1 for x in node_rows if not x['referenced_by_skin']),
      'total_nonzero_influence_references':sum(global_refs.values()),
      'meshes':mesh_rows,'nodes':node_rows,'violations':v,
      'semantic_boundary':{'joint_index_to_node':'EXACT','node_hash':'EXACT','hierarchy':'EXACT','anatomical_names':'WITHHELD'},
      'policy':'Every mapping is a direct array-index join between source-closed skin indices and the source-owned EntitySkeleton node array. No anatomical naming or influence repair occurs.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 top=sorted(node_rows,key=lambda x:(-x['skin_reference_count'],x['joint_index']))[:15]
 print(json.dumps({'status':out['status'],'referenced_joint_count':out['skin_referenced_joint_count'],
                   'total_nonzero_influence_references':out['total_nonzero_influence_references'],
                   'mesh_joint_counts':[(x['mesh_index'],x['referenced_joint_count']) for x in mesh_rows],
                   'top_joints':[(x['joint_index'],x['node_hash'],x['skin_reference_count']) for x in top],
                   'violations':v},indent=2))
 return 0 if out['status']=='D1_CROTA_SKIN_BONE_MAP_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
