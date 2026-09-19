#!/usr/bin/env python3
"""Annotate Crota's exact skeleton usage matrix with pinned lineage bone names.

The three-domain matrix (skin, selected-clip motion, runtime controls) remains exact
retail structural evidence. Name strings are joined separately by exact node hash
from d1_skeleton_lineage_name_map/v1 and retain their pinned-parser-lineage class.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--usage-matrix',type=Path,required=True)
 ap.add_argument('--lineage-names',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 u=json.loads(a.usage_matrix.read_text());n=json.loads(a.lineage_names.read_text());v=[]
 if u.get('status')!='D1_CROTA_SKELETON_USAGE_MATRIX_EXACT' or u.get('violations'):v.append('usage matrix not exact')
 if n.get('status')!='D1_SKELETON_LINEAGE_NAME_MAP_EXACT_HASH_JOIN' or n.get('violations'):v.append('lineage name join not exact')
 if u.get('skeleton_resource')!=n.get('skeleton_resource'):v.append('skeleton resource mismatch')
 ur=u.get('nodes') or [];nr=n.get('rows') or []
 if len(ur)!=len(nr):v.append(f'node count mismatch {len(ur)}/{len(nr)}')
 rows=[];named_patterns=collections.Counter()
 for i,(x,y) in enumerate(zip(ur,nr)):
  if int(x.get('index',-1))!=i or int(y.get('index',-1))!=i:v.append(f'node {i}: index drift')
  if x.get('node_hash')!=y.get('node_hash'):v.append(f'node {i}: hash mismatch {x.get("node_hash")}/{y.get("node_hash")}')
  name=y.get('bungie_name')
  r={**x,
     'bungie_name':name,
     'name_evidence':y.get('name_evidence'),
     'display_identity':name if name else x.get('node_hash')}
  rows.append(r)
  if name:named_patterns[(name,x.get('structural_pattern'))]+=1
 notable=[x for x in rows if x['has_target_only_suffix_control'] or
          (x['has_skin_influence'] and not x['has_runtime_control']) or
          (x['has_dynamic_motion'] and not x['has_runtime_control']) or
          (x['has_runtime_control'] and not x['has_skin_influence'])]
 out={
  'schema':'d1_crota_named_skeleton_usage/v1',
  'status':'D1_CROTA_NAMED_SKELETON_USAGE_EXACT_JOIN' if len(rows)==50 and not v else 'D1_CROTA_NAMED_SKELETON_USAGE_PARTIAL',
  'skeleton_resource':u.get('skeleton_resource'),'node_count':len(rows),
  'lineage_named_node_count':sum(bool(x['bungie_name']) for x in rows),
  'unresolved_name_node_count':sum(not x['bungie_name'] for x in rows),
  'nodes':rows,'notable_nodes':notable,'observations':u.get('observations'),
  'target_only_suffix_nodes':[x for x in rows if x['has_target_only_suffix_control']],
  'skin_nodes_without_direct_runtime_control':[x for x in rows if x['has_skin_influence'] and not x['has_runtime_control']],
  'dynamic_nodes_without_direct_runtime_control':[x for x in rows if x['has_dynamic_motion'] and not x['has_runtime_control']],
  'violations':v,
  'evidence_classes':{
   'skin_motion_control_membership':'EXACT_RETAIL_STRUCTURAL_OBSERVATION',
   'node_hash_hierarchy':'EXACT_RETAIL_ENTITYSKELETON',
   'bungie_name_string':'PINNED_COMMUNITY_PARSER_LINEAGE_TABLE',
   'semantic_interpretation_of_usage_patterns':'WITHHELD',
  },
  'policy':'Human-readable names improve inspection only. They do not change the evidence class of skin/motion/control membership and do not turn structural exceptions into inferred helper, IK, attachment, gameplay, or anatomical roles.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({
  'status':out['status'],'named':out['lineage_named_node_count'],
  'target_only_suffix':[(x['index'],x['display_identity'],x['runtime_controls']) for x in out['target_only_suffix_nodes']],
  'skin_without_control':[(x['index'],x['display_identity']) for x in out['skin_nodes_without_direct_runtime_control']],
  'dynamic_without_control':[(x['index'],x['display_identity']) for x in out['dynamic_nodes_without_direct_runtime_control']],
  'violations':v,
 },indent=2))
 return 0 if out['status']=='D1_CROTA_NAMED_SKELETON_USAGE_EXACT_JOIN' else 2

if __name__=='__main__':raise SystemExit(main())
