#!/usr/bin/env python3
"""Join an exact D1 EntitySkeleton to the pinned parser's bone-name lineage map.

Retail evidence proves the ordered node hashes and hierarchy. Human-readable
Bungie-style strings in this report are a separate evidence class: they come
from the explicitly pinned tiger-animation-parser hash_to_bungie_name table.

Unmapped hashes stay numeric. This tool never invents anatomical names.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--s-entity',type=Path,required=True)
 ap.add_argument('--skeleton-resource',required=True)
 ap.add_argument('--parser-root',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 d=json.loads(a.s_entity.read_text());violations=[]
 if d.get('status')!='D1_EXACT_S_ENTITY_PROBE' or d.get('violation_count'):
  violations.append('s_entity probe not exact')
 wanted=norm(a.skeleton_resource);hits=[]
 for e in d.get('entries',[]):
  for sk in e.get('skeletons',[]):
   if norm(sk.get('resource_hash'))==wanted:hits.append(sk)
 if len(hits)!=1:
  violations.append(f'{wanted}: expected one skeleton row, got {len(hits)}')
  sk={'bone_hashes':[],'nodes':[],'node_count':0}
 else:sk=hits[0]
 hashes=[norm(x) for x in sk.get('bone_hashes',[])]
 nodes=sk.get('nodes') or []
 if int(sk.get('node_count',-1))!=len(hashes):
  violations.append('node_count/bone_hashes length mismatch')
 if nodes and len(nodes)!=len(hashes):
  violations.append('nodes/bone_hashes length mismatch')
 parser_root=a.parser_root.resolve()
 if str(parser_root) not in sys.path:sys.path.insert(0,str(parser_root))
 try:
  from fnv_hashes.bones_names import hash_to_bungie_name
 except Exception as ex:
  violations.append(f'pinned parser name map import failed: {ex!r}')
  hash_to_bungie_name={}
 rows=[];resolved=[];unresolved=[]
 for i,h in enumerate(hashes):
  hv=int(h,16);name=hash_to_bungie_name.get(hv)
  n=nodes[i] if i<len(nodes) else {}
  row={
   'index':i,'node_hash':h,
   'bungie_name':name,
   'name_evidence':'PINNED_TIGER_ANIMATION_PARSER_LINEAGE' if name else 'UNRESOLVED',
   'parent_node_index':n.get('parent_node_index'),
   'first_child_node_index':n.get('first_child_node_index'),
   'next_sibling_node_index':n.get('next_sibling_node_index'),
  }
  rows.append(row)
  (resolved if name else unresolved).append(row)
 out={
  'schema':'d1_skeleton_lineage_name_map/v1',
  'status':'D1_SKELETON_LINEAGE_NAME_MAP_EXACT_HASH_JOIN' if len(rows)==len(hashes) and hashes and not violations else 'D1_SKELETON_LINEAGE_NAME_MAP_PARTIAL',
  'skeleton_resource':wanted,'node_count':len(rows),
  'lineage_named_node_count':len(resolved),'unresolved_node_count':len(unresolved),
  'rows':rows,
  'unresolved_nodes':unresolved,
  'violations':violations,
  'evidence_classes':{
   'node_hash_and_order':'EXACT_RETAIL_ENTITYSKELETON',
   'hierarchy':'EXACT_RETAIL_ENTITYSKELETON' if nodes else 'UNAVAILABLE_IN_INPUT',
   'bungie_name_string':'PINNED_COMMUNITY_PARSER_LINEAGE_TABLE',
   'unmapped_anatomical_identity':'WITHHELD',
  },
  'parser_lineage':'SolUnshadowed/tiger-animation-parser pinned by calling workflow',
  'policy':'Names are joined only by exact uint32 node hash. The report does not upgrade parser-lineage strings into independently source-proven retail semantics, and unmatched hashes remain unnamed.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'named':len(resolved),'unresolved':[(x['index'],x['node_hash']) for x in unresolved],
                   'preview':[(x['index'],x['node_hash'],x['bungie_name']) for x in resolved[:20]],'violations':violations},indent=2))
 return 0 if out['status']=='D1_SKELETON_LINEAGE_NAME_MAP_EXACT_HASH_JOIN' else 2

if __name__=='__main__':raise SystemExit(main())
