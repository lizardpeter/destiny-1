#!/usr/bin/env python3
"""Build a three-domain structural usage matrix for Crota's exact 50-node skeleton.

Domains:
1. retail skin influence references;
2. dynamic local-space motion across selector-selected clips;
3. target runtime-rig control ownership, including the exact 37/7 retarget boundary.

All joins require exact skeleton index/hash/hierarchy agreement.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--usage-union',type=Path,required=True)
 ap.add_argument('--control-map',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 u=json.loads(a.usage_union.read_text());c=json.loads(a.control_map.read_text());v=[]
 if u.get('status')!='D1_CROTA_SKELETON_USAGE_UNION_EXACT' or u.get('violations'):v.append('skin/motion union not exact')
 if c.get('status')!='D1_CROTA_RUNTIME_CONTROL_SKELETON_MAP_EXACT' or c.get('violations'):v.append('runtime control map not exact')
 if u.get('skeleton_resource')!=c.get('skeleton_resource'):v.append('skeleton resource mismatch')
 nodes=u.get('nodes') or [];controls=c.get('controls') or []
 bybone=collections.defaultdict(list)
 for x in controls:bybone[int(x['bone_index'])].append(x)
 rows=[];patterns=collections.Counter()
 for i,n in enumerate(nodes):
  cc=sorted(bybone.get(i,[]),key=lambda x:x['control_index'])
  for q in cc:
   for k in ('node_hash','parent_node_index','first_child_node_index','next_sibling_node_index'):
    if q.get(k)!=n.get(k):v.append(f'node {i}: control {q.get("control_index")} {k} mismatch')
  skin=int(n['skin_reference_count'])>0
  motion=int(n['dynamic_any_clip_instances'])>0
  ctrl=bool(cc)
  shared=any(x['retarget_boundary_class']=='SHARED_RETARGETABLE_PREFIX' for x in cc)
  suffix=any(x['retarget_boundary_class']=='TARGET_ONLY_SUFFIX' for x in cc)
  pattern=f"skin={int(skin)};motion={int(motion)};control={int(ctrl)};shared={int(shared)};suffix={int(suffix)}"
  patterns[pattern]+=1
  rows.append({
   **n,
   'has_skin_influence':skin,'has_dynamic_motion':motion,'has_runtime_control':ctrl,
   'has_shared_prefix_control':shared,'has_target_only_suffix_control':suffix,
   'runtime_controls':[{'control_index':int(x['control_index']),'retarget_boundary_class':x['retarget_boundary_class']} for x in cc],
   'structural_pattern':pattern,
  })
 # Every runtime control must map into one of these exact node rows.
 if sum(len(x['runtime_controls']) for x in rows)!=int(c.get('control_count',-1)):
  v.append('runtime control accounting mismatch')
 observations={
  'nodes_with_skin_and_motion_and_control':sum(x['has_skin_influence'] and x['has_dynamic_motion'] and x['has_runtime_control'] for x in rows),
  'nodes_with_target_only_suffix_control':sum(x['has_target_only_suffix_control'] for x in rows),
  'target_only_control_nodes_without_skin':sum(x['has_target_only_suffix_control'] and not x['has_skin_influence'] for x in rows),
  'target_only_control_nodes_without_dynamic_motion':sum(x['has_target_only_suffix_control'] and not x['has_dynamic_motion'] for x in rows),
  'skin_nodes_without_direct_runtime_control':sum(x['has_skin_influence'] and not x['has_runtime_control'] for x in rows),
  'dynamic_nodes_without_direct_runtime_control':sum(x['has_dynamic_motion'] and not x['has_runtime_control'] for x in rows),
  'controlled_nodes_without_skin':sum(x['has_runtime_control'] and not x['has_skin_influence'] for x in rows),
  'controlled_nodes_without_dynamic_motion':sum(x['has_runtime_control'] and not x['has_dynamic_motion'] for x in rows),
 }
 out={'schema':'d1_crota_skeleton_usage_matrix/v1',
      'status':'D1_CROTA_SKELETON_USAGE_MATRIX_EXACT' if len(rows)==50 and not v else 'D1_CROTA_SKELETON_USAGE_MATRIX_PARTIAL',
      'skeleton_resource':u.get('skeleton_resource'),'node_count':len(rows),
      'runtime_control_count':sum(len(x['runtime_controls']) for x in rows),
      'pattern_histogram':dict(sorted(patterns.items())),'observations':observations,
      'nodes':rows,'violations':v,
      'semantic_boundary':{'all_three_domains':'EXACT_STRUCTURAL_OBSERVATION','helper_bone_interpretation':'WITHHELD','anatomical_names':'WITHHELD','target_only_control_behavior':'WITHHELD'},
      'policy':'The matrix reports only observed membership in exact retail skin, selected-clip dynamic motion, and runtime-rig mappings. Structural exceptions are not promoted to semantic bone categories.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 notable=[x for x in rows if x['has_target_only_suffix_control'] or (x['has_skin_influence'] and not x['has_runtime_control']) or (x['has_dynamic_motion'] and not x['has_runtime_control'])]
 print(json.dumps({'status':out['status'],'pattern_histogram':out['pattern_histogram'],'observations':observations,
                   'notable_nodes':[(x['index'],x['node_hash'],x['parent_node_index'],x['structural_pattern'],x['runtime_controls']) for x in notable],
                   'violations':v},indent=2))
 return 0 if out['status']=='D1_CROTA_SKELETON_USAGE_MATRIX_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
