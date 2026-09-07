#!/usr/bin/env python3
"""Enumerate every exact SMapDataEntry for the unresolved Tower actor model 80C88434.

The three known D912 owners each serialize the target EntitySK three times. This probe
preserves all records and reports their source-typed DataResource pointer/class plus
any S152 configuration. It also emits the exact visible variant-0 descriptor members
from parent EntityResource 80C883FD. It makes no material selection.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_remote_tower_placement_permutation_calibration import discover_smap_placements
from d1_remote_tower_descriptor_selection_calibration import parse_graph
from d1_split_tar_extract import SplitHttpTar

MODEL='80C88434';PARENT='80C883FD'
TARGETS={'80C7A5AD':'80C7A581','80C7ACC5':'80C7ACB4','80C883CA':'80C88477'}
def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--member-catalog',type=Path,action='append',required=True);ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
 cats=load_catalogs(a.member_catalog);arc=SplitHttpTar([f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90);c=RemoteCorpus(arc,cats,a.runtime)
 violations=[];placements=[]
 for entity,owner in TARGETS.items():
  try: rows=[x for x in discover_smap_placements(c,owner) if norm(x.get('entity_hash'))==entity]
  except Exception as ex: violations.append(f'{owner}:parse:{ex!r}');continue
  if not rows: violations.append(f'{owner}:{entity}:zero_smap_records');continue
  for ordinal,r in enumerate(rows):
   placements.append({'entity_hash':entity,'d912':owner,'ordinal':ordinal,'smap_offset':int(r['smap_offset']),'data_resource':r.get('data_resource'),'has_s152':bool(r.get('s152')),'s152':r.get('s152')})
 try:
  graph=parse_graph(c,PARENT);groups=[g for g in graph.get('groups',[]) if int(g.get('variant_shader_index',-1))==0]
  if len(groups)!=1: violations.append(f'{PARENT}:variant0_group_count:{len(groups)}');group=None
  else: group=groups[0]
 except Exception as ex: graph=None;group=None;violations.append(f'{PARENT}:graph:{ex!r}')
 counts={}
 for r in placements:
  dr=r.get('data_resource') or {};k=('NULL' if dr.get('null') else str(dr.get('class_hash')))
  counts[k]=counts.get(k,0)+1
 out={'schema_version':2,'status':'D1_TOWER_80C88434_SMAP_FRONTIER_EXACT' if not violations else 'D1_TOWER_80C88434_SMAP_FRONTIER_VIOLATIONS','model':MODEL,'model_parent_resource':PARENT,'target_count':len(TARGETS),'smap_record_count':len(placements),'data_resource_class_counts':counts,'placements':placements,'visible_variant0_group':group,'violations':violations,'gates':{'visible_variant0_material_selected':False,'D1_retail_descriptor_evaluator_source_closed':False},'policy':'All exact SMap records are retained. DataResource class/null state and S152 contents are source-typed evidence; descriptor members are exact parent data. No material winner is inferred.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'smap_record_count':len(placements),'data_resource_class_counts':counts,'placements':[{'entity':x['entity_hash'],'owner':x['d912'],'ordinal':x['ordinal'],'offset':hex(x['smap_offset']),'data_resource':x['data_resource'],'s152_records':None if not x.get('s152') else x['s152'].get('records')} for x in placements],'variant0_members':None if group is None else [{'member_index':m['member_index'],'material':m['material_tag_hash'],'list_a_pairs':m['list_a_pairs'],'list_b_pairs':m['list_b_pairs']} for m in group.get('members',[])],'violations':violations,'gates':out['gates']},indent=2))
 return 0 if not violations else 2
if __name__=='__main__': raise SystemExit(main())
