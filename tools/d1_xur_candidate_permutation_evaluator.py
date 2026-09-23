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
import argparse,json,math,itertools,collections
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

 # Prove the exact serialized descriptor table is a complete ordered decision table.
 # This is a structural theorem over the retail bytes, not yet an xref to the client
 # consumer.  Configuration values are drawn from the exact switch bank; the invalid
 # sentinel is treated as absent/unset because no list-A descriptor ever requires it
 # and every list-B descriptor uses it as the companion value for the same keys.
 list_a_contains_invalid=[]
 for di,d in descriptors.items():
  aa=flatten_switch_records(d['list_a'])
  if any(v==INVALID for k,v in aa):
   list_a_contains_invalid.append(di)

 group_structure=[]
 ordered_structure_ok=True
 for vi,members in sorted(by_vi.items()):
  ordered=sorted(members,key=lambda x:int(x['member_index']))
  reqs=[flatten_switch_records(descriptors[int(m['descriptor_index'])]['list_a']) for m in ordered]
  empty=[i for i,r in enumerate(reqs) if not r]
  specificity=[len(r) for r in reqs]
  row={
   'variant_shader_index':vi,
   'member_count':len(ordered),
   'empty_descriptor_member_indices':empty,
   'single_final_empty_fallback':empty==[len(ordered)-1],
   'specificity_pair_counts':specificity,
   'specificity_nonincreasing':all(specificity[i]>=specificity[i+1] for i in range(len(specificity)-1)),
  }
  group_structure.append(row)
  if not row['single_final_empty_fallback'] or not row['specificity_nonincreasing']:
   ordered_structure_ok=False

 switch_domains=collections.defaultdict(set)
 for r in g.get('switch_records',[]):
  for k,v in r.get('pairs',[]):
   switch_domains[norm(k)].add(norm(v))
 config_keys=sorted(switch_domains)
 config_choices={
  k:[None]+sorted(v for v in switch_domains[k] if v!=INVALID)
  for k in config_keys
 }
 exhaustive_config_count=0
 exhaustive_case_count=0
 exhaustive_gap_count=0
 exhaustive_ambiguity_count=0
 first_match_vs_max_specificity_mismatch_count=0
 mismatch_examples=[]
 gap_examples=[]
 ambiguity_examples=[]
 for values in itertools.product(*(config_choices[k] for k in config_keys)):
  config={k:v for k,v in zip(config_keys,values) if v is not None}
  exhaustive_config_count+=1
  for vi,members in sorted(by_vi.items()):
   exhaustive_case_count+=1
   ordered=sorted(members,key=lambda x:int(x['member_index']))
   satisfied=[]
   for m in ordered:
    req=flatten_switch_records(descriptors[int(m['descriptor_index'])]['list_a'])
    if all(config.get(k)==v for k,v in req):
     satisfied.append((len(req),m))
   if not satisfied:
    exhaustive_gap_count+=1
    if len(gap_examples)<8:gap_examples.append({'variant_shader_index':vi,'configuration':config})
    continue
   maxspec=max(s for s,m in satisfied)
   winners=[m for s,m in satisfied if s==maxspec]
   if len(winners)!=1:
    exhaustive_ambiguity_count+=1
    if len(ambiguity_examples)<8:
     ambiguity_examples.append({'variant_shader_index':vi,'configuration':config,'winner_member_indices':[int(x['member_index']) for x in winners]})
    continue
   first=satisfied[0][1]
   if int(first['member_index'])!=int(winners[0]['member_index']):
    first_match_vs_max_specificity_mismatch_count+=1
    if len(mismatch_examples)<8:
     mismatch_examples.append({'variant_shader_index':vi,'configuration':config,'first_match':int(first['member_index']),'max_specificity':int(winners[0]['member_index'])})

 decision_table_analysis={
  'configuration_domain_policy':'For each exact switch key: absent/unset or one exact non-871AC0EA value from the model switch bank.',
  'switch_domains':{k:sorted(v) for k,v in sorted(switch_domains.items())},
  'configuration_key_count':len(config_keys),
  'exhaustive_configuration_count':exhaustive_config_count,
  'variant_group_count':len(by_vi),
  'exhaustive_group_configuration_case_count':exhaustive_case_count,
  'list_A_descriptor_count_containing_invalid_sentinel':len(list_a_contains_invalid),
  'list_A_descriptor_indices_containing_invalid_sentinel':list_a_contains_invalid,
  'every_group_has_single_final_empty_fallback':all(x['single_final_empty_fallback'] for x in group_structure),
  'every_group_specificity_nonincreasing_in_serialized_order':all(x['specificity_nonincreasing'] for x in group_structure),
  'gap_count':exhaustive_gap_count,
  'ambiguity_count':exhaustive_ambiguity_count,
  'first_match_vs_max_specificity_mismatch_count':first_match_vs_max_specificity_mismatch_count,
  'complete_unique_decision_table':exhaustive_gap_count==0 and exhaustive_ambiguity_count==0,
  'serialized_first_match_equivalent_to_unique_max_specificity':first_match_vs_max_specificity_mismatch_count==0 and exhaustive_gap_count==0 and exhaustive_ambiguity_count==0,
  'group_structure':group_structure,
  'gap_examples':gap_examples,
  'ambiguity_examples':ambiguity_examples,
  'mismatch_examples':mismatch_examples,
  'D1_retail_consumer_execution_path_proven':False,
 }
 if list_a_contains_invalid:violations.append('list_A_contains_invalid_sentinel')
 if not ordered_structure_ok:violations.append('serialized_group_priority_structure_failed')
 if exhaustive_gap_count or exhaustive_ambiguity_count or first_match_vs_max_specificity_mismatch_count:
  violations.append(f'descriptor_decision_table_failed:gaps={exhaustive_gap_count}:amb={exhaustive_ambiguity_count}:mismatch={first_match_vs_max_specificity_mismatch_count}')

 # Test a stronger retail-style invariant independently of the per-group rule:
 # does one global permutation index reproduce every unique local winner via
 #     local_member = global_index % MaterialCount
 # as used by the later MIDA/Charm-family consumer?
 residue_sets={}
 for ev in evaluations:
  if not ev['unique_candidate']:
   continue
  n=int(ev['member_count']); w=int(ev['candidate_members'][0]['member_index'])
  residue_sets.setdefault(n,set()).add(w)
 residue_rows={str(n):sorted(v) for n,v in sorted(residue_sets.items())}
 residue_consistent=all(len(v)==1 for v in residue_sets.values())
 period=1
 for n in residue_sets: period=math.lcm(period,n)
 compatible_mod=[]
 if residue_consistent:
  wanted={n:next(iter(v)) for n,v in residue_sets.items()}
  compatible_mod=[i for i in range(period) if all(i % n == r for n,r in wanted.items())]
 descriptor_bound=len(descriptors)
 compatible_descriptor_range=[i for i in compatible_mod if i < descriptor_bound]
 global_index_analysis={
  'rule':'local_member_index == global_permutation_index % material_count',
  'material_count_to_candidate_local_index_set':residue_rows,
  'material_count_residue_consistent':residue_consistent,
  'modulus_lcm':period,
  'compatible_global_indices_mod_lcm':compatible_mod,
  'compatible_global_indices_below_descriptor_count':compatible_descriptor_range,
  'descriptor_count_bound':descriptor_bound,
  'unique_global_residue_mod_lcm':len(compatible_mod)==1,
  'unique_global_index_below_descriptor_count':len(compatible_descriptor_range)==1,
  'later_strategy_structural_analogy_only':True,
  'D1_retail_consumer_execution_path_proven':False,
 }
 consequences={}
 for label,target in TARGETS.items():
  occurrences=[]
  for ev in evaluations:
   trows=[x for x in ev['members'] if x['material_tag_hash']==target]
   for tr in trows:
    occurrences.append({'variant_shader_index':ev['variant_shader_index'],'target_member':tr,'candidate_members':ev['candidate_members'],'target_is_candidate':any(x['material_tag_hash']==target for x in ev['candidate_members'])})
  consequences[label]={'target_material':target,'occurrences':occurrences}

 out={'schema':'d1_xur_candidate_permutation_evaluator/v1','status':'D1_XUR_CANDIDATE_PERMUTATION_EVALUATION_UNIQUE' if not violations else 'D1_XUR_CANDIDATE_PERMUTATION_EVALUATION_VIOLATIONS','raw_source_decoded_placement_pairs':[list(x) for x in sorted(raw_config)],'model_switch_configuration_pairs':[list(x) for x in sorted(model_config)],'placement_pairs_not_in_model_switch_bank':[list(x) for x in sorted(non_model_placement_pairs)],'descriptor_B_companion_invariant':{'descriptor_count':len(b_invariant),'same_keys_all_B_invalid_count':sum(x['same_keys_and_all_B_invalid'] for x in b_invariant),'invalid_value':INVALID,'rows':b_invariant},'variant_group_count':len(evaluations),'unique_candidate_group_count':unique,'evaluations':evaluations,'descriptor_order_decision_table_analysis':decision_table_analysis,'global_permutation_index_analysis':global_index_analysis,'E6_E7_E8_candidate_consequences':consequences,'proof':{'placement_configuration_source_decoded':True,'placement_pair_to_own_model_switch_bank_correspondence_proven':True,'descriptor_B_same_keys_invalid_companion_structural_invariant':all(x['same_keys_and_all_B_invalid'] for x in b_invariant),'candidate_list_A_max_specificity_evaluator_unique_across_all_groups':unique==len(evaluations),'descriptor_order_complete_unique_decision_table':decision_table_analysis['complete_unique_decision_table'],'serialized_first_match_equivalent_to_unique_max_specificity':decision_table_analysis['serialized_first_match_equivalent_to_unique_max_specificity'],'single_global_modulo_index_consistent':global_index_analysis['unique_global_residue_mod_lcm'],'D1_retail_consumer_execution_path_proven':False,'descriptor_evaluation_algorithm_source_closed':False},'gates':{'E6_80C885E6_live_selection_proven':False,'E7_80C885E7_live_selection_proven':False,'E8_80C885E8_live_selection_proven':False},'violations':violations,'policy':'Candidate uniqueness is not promoted to D1 retail execution semantics. E6/E7/E8 remain fail-closed until the D1 consumer/evaluator path itself is independently closed.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'raw_config':out['raw_source_decoded_placement_pairs'],'model_config':out['model_switch_configuration_pairs'],'descriptor_B_invariant':out['descriptor_B_companion_invariant']['same_keys_all_B_invalid_count'],'variant_groups':out['variant_group_count'],'unique_candidates':out['unique_candidate_group_count'],'E6_E7_E8':out['E6_E7_E8_candidate_consequences'],'descriptor_order_decision_table_analysis':{k:v for k,v in out['descriptor_order_decision_table_analysis'].items() if k!='group_structure'},'global_permutation_index_analysis':out['global_permutation_index_analysis'],'proof':out['proof'],'gates':out['gates'],'violations':violations},indent=2));return 0 if not violations else 2
if __name__=='__main__':raise SystemExit(main())
