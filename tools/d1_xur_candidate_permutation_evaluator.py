#!/usr/bin/env python3
"""Evaluate the source-decoded Xur placement configuration against the exact D1 static graph.

This is deliberately a candidate evaluator, not retail-consumer closure.
It combines only already-closed serialized facts:
  * exact Xur S152/S4E2A placement records;
  * exact model-parent switch-record/descriptors/material groups;
  * structural invariant that descriptor list-B uses the same keys as list-A and
    every list-B value is the invalid/default sentinel 871AC0EA.

Candidate rule tested (not promoted to retail semantics here):
  1. retain placement pairs that occur exactly in the owning model switch bank;
  2. a descriptor list-A is satisfied when all its exact key/value pairs occur in
     that configuration;
  3. within a material group, choose the satisfied descriptor with the greatest
     number of required pairs; empty list-A is therefore fallback only when no
     more-specific member matches.

The tool requires uniqueness across every VariantShaderIndex group and reports the
E6/E7/E8 consequences, while leaving all three live-selection gates false.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

INVALID='871AC0EA'
TARGETS={'E6':'80C885E6','E7':'80C885E7','E8':'80C885E8'}

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def flatten_switch_records(desc_list):
 out=[]
 for r in desc_list.get('switch_records',[]):
  for p in r.get('pairs',[]):out.append((norm(p[0]),norm(p[1])))
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--static-graph',type=Path,required=True);ap.add_argument('--placement-config',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
 g=json.loads(a.static_graph.read_text());p=json.loads(a.placement_config.read_text())
 violations=[]
 if g.get('status')!='D1_XUR_MODEL_PARENT_PERMUTATION_STATIC_REFERENCE_GRAPH_EXACT':violations.append('static_graph_not_exact')
 if p.get('status')!='D1_XUR_PLACEMENT_CONFIGURATION_SOURCE_DECODED':violations.append('placement_configuration_not_source_decoded')
 if g.get('violations'):violations.append('static_graph_has_violations')
 if p.get('violations'):violations.append('placement_config_has_violations')

 switch_pairs=set()
 for r in g.get('switch_records',[]):
  for x in r.get('pairs',[]):switch_pairs.add((norm(x[0]),norm(x[1])))

 placement_pair_sets=[]
 for row in p.get('rows',[]):
  for pl in row.get('typed_xur_placements',[]):
   q={(norm(r['unk00_tiger_hash']),norm(r['type_string_hash'])) for r in pl.get('s4e2a_records',[])}
   placement_pair_sets.append(q)
 if not placement_pair_sets:violations.append('no_typed_xur_placements')
 elif any(q!=placement_pair_sets[0] for q in placement_pair_sets):violations.append('xur_placement_configuration_not_invariant')
 raw_config=placement_pair_sets[0] if placement_pair_sets else set()
 model_config=raw_config & switch_pairs
 non_model_placement_pairs=raw_config-switch_pairs

 descriptors={int(d['descriptor_index']):d for d in g.get('descriptors',[])}
 b_invariant=[]
 for di,d in descriptors.items():
  aa=flatten_switch_records(d['list_a']);bb=flatten_switch_records(d['list_b'])
  akeys=[k for k,v in aa];bkeys=[k for k,v in bb]
  ok=akeys==bkeys and all(v==INVALID for k,v in bb)
  b_invariant.append({'descriptor_index':di,'list_a_pairs':[list(x) for x in aa],'list_b_pairs':[list(x) for x in bb],'same_keys_and_all_B_invalid':ok})
 if not all(x['same_keys_and_all_B_invalid'] for x in b_invariant):violations.append('descriptor_B_companion_invariant_failed')

 by_vi={}
 for m in g.get('variant_members',[]):by_vi.setdefault(int(m['variant_shader_index']),[]).append(m)
 evaluations=[];unique=0
 for vi,members in sorted(by_vi.items()):
  rows=[]
  for m in sorted(members,key=lambda x:int(x['member_index'])):
   d=descriptors[int(m['descriptor_index'])];req=flatten_switch_records(d['list_a'])
   satisfied=all(x in model_config for x in req)
   rows.append({'member_index':int(m['member_index']),'material_tag_hash':norm(m['material_tag_hash']),'descriptor_index':int(m['descriptor_index']),'required_list_A_pairs':[list(x) for x in req],'specificity_pair_count':len(req),'satisfied_by_source_decoded_model_config':satisfied})
  sats=[x for x in rows if x['satisfied_by_source_decoded_model_config']]
  maxspec=max((x['specificity_pair_count'] for x in sats),default=None)
  winners=[x for x in sats if x['specificity_pair_count']==maxspec]
  if len(winners)==1:unique+=1
  evaluations.append({'variant_shader_index':vi,'member_count':len(rows),'satisfied_member_count':len(sats),'max_specificity':maxspec,'unique_candidate':len(winners)==1,'candidate_members':winners,'members':rows})
 if unique!=len(evaluations):violations.append(f'candidate_not_unique_for_all_groups:{unique}/{len(evaluations)}')

 consequences={}
 for label,target in TARGETS.items():
  occurrences=[]
  for ev in evaluations:
   trows=[x for x in ev['members'] if x['material_tag_hash']==target]
   for tr in trows:
    occurrences.append({'variant_shader_index':ev['variant_shader_index'],'target_member':tr,'candidate_members':ev['candidate_members'],'target_is_candidate':any(x['material_tag_hash']==target for x in ev['candidate_members'])})
  consequences[label]={'target_material':target,'occurrences':occurrences}

 out={'schema':'d1_xur_candidate_permutation_evaluator/v1','status':'D1_XUR_CANDIDATE_PERMUTATION_EVALUATION_UNIQUE' if not violations else 'D1_XUR_CANDIDATE_PERMUTATION_EVALUATION_VIOLATIONS','raw_source_decoded_placement_pairs':[list(x) for x in sorted(raw_config)],'model_switch_configuration_pairs':[list(x) for x in sorted(model_config)],'placement_pairs_not_in_model_switch_bank':[list(x) for x in sorted(non_model_placement_pairs)],'descriptor_B_companion_invariant':{'descriptor_count':len(b_invariant),'same_keys_all_B_invalid_count':sum(x['same_keys_and_all_B_invalid'] for x in b_invariant),'invalid_value':INVALID,'rows':b_invariant},'variant_group_count':len(evaluations),'unique_candidate_group_count':unique,'evaluations':evaluations,'E6_E7_E8_candidate_consequences':consequences,'proof':{'placement_configuration_source_decoded':True,'placement_pair_to_own_model_switch_bank_correspondence_proven':True,'descriptor_B_same_keys_invalid_companion_structural_invariant':all(x['same_keys_and_all_B_invalid'] for x in b_invariant),'candidate_list_A_max_specificity_evaluator_unique_across_all_groups':unique==len(evaluations),'D1_retail_consumer_execution_path_proven':False,'descriptor_evaluation_algorithm_source_closed':False},'gates':{'E6_80C885E6_live_selection_proven':False,'E7_80C885E7_live_selection_proven':False,'E8_80C885E8_live_selection_proven':False},'violations':violations,'policy':'Candidate uniqueness is not promoted to D1 retail execution semantics. E6/E7/E8 remain fail-closed until the D1 consumer/evaluator path itself is independently closed.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'raw_config':out['raw_source_decoded_placement_pairs'],'model_config':out['model_switch_configuration_pairs'],'descriptor_B_invariant':out['descriptor_B_companion_invariant']['same_keys_all_B_invalid_count'],'variant_groups':out['variant_group_count'],'unique_candidates':out['unique_candidate_group_count'],'E6_E7_E8':out['E6_E7_E8_candidate_consequences'],'proof':out['proof'],'gates':out['gates'],'violations':violations},indent=2));return 0 if not violations else 2
if __name__=='__main__':raise SystemExit(main())
