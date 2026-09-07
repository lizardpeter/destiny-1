#!/usr/bin/env python3
"""Corpus-calibrate a candidate D1 descriptor selection rule across Tower placements.

Inputs:
- the exact green Tower placement/model-switch-bank calibration report;
- exact retail model-owner EntityResource payloads fetched by proven hashes.

For each independently resolved model parent this tool reconstructs the D1 static
permutation graph generically (switch bank, +0x250 indirect index list, +0x260
FE1A descriptors, ExternalMaterialsMap, material bank).  It then tests ONE candidate
rule without promoting it to retail semantics:

  descriptor list-A must be a subset of the placement's exact own-model switch
  configuration; among satisfied members choose greatest list-A pair count; an
  empty list-A can therefore act as fallback.

The test is useful only if it is deterministic across many independent models and
placements.  List-B is separately checked for the observed same-key/871AC0EA
companion invariant.  No E6/E7/E8 gate is opened here.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))

from d1_entity_resource_probe import parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_remote_model_parent_permutation_layout_probe import (
    parse_map,parse_materials,parse_candidate_indices,parse_descriptors,
    early_dynamic_headers,test_switch_container_candidate,
)
from d1_model_parent_permutation_static_graph_close import resolve_descriptor_list
from d1_split_tar_extract import SplitHttpTar

ENTITY_RESOURCE='80800861';MODEL_PARENT='80801A9C';INVALID='871AC0EA'
XUR_ENTITIES={'80C7ACC8','80C885AA'}
TARGETS={'E6':'80C885E6','E7':'80C885E7','E8':'80C885E8'}

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def flatten(records,indices):
 out=[]
 for i in indices:
  for p in records[i]:out.append((norm(p[0]),norm(p[1])))
 return out

def parse_graph(c,resource_hash):
 h=norm(resource_hash);m=c.entry_meta(h);b,src=c.payload(h)
 if m is None or b is None:raise ValueError(f'{h}: payload unavailable')
 if norm(m.get('reference',''))!=ENTITY_RESOURCE:raise ValueError(f'{h}: not EntityResource')
 p=parse_resource(b,'PS4');parent=p.get('unk18') or {};base=parent.get('target_offset')
 if parent.get('class_hash')!=MODEL_PARENT or not isinstance(base,int):raise ValueError(f'{h}: model parent mismatch {parent}')
 maps=parse_map(b,base);mats=parse_materials(b,base);idx=parse_candidate_indices(b,base);desc=parse_descriptors(b,base,idx['count'] if idx.get('bounds_valid') else None)
 for name,o in [('map',maps),('materials',mats),('index',idx),('descriptors',desc)]:
  if not o.get('bounds_valid'):raise ValueError(f'{h}: {name} bounds invalid')
 tests=[test_switch_container_candidate(b,x) for x in early_dynamic_headers(b,base)]
 exact=[x for x in tests if x.get('all_outer_elements_have_valid_nested_pair_array') and x.get('inner_pair_total',0)>0 and x.get('parent_relative_offset')==0x50]
 if len(exact)!=1:raise ValueError(f'{h}: exact +0x50 switch candidate count {len(exact)}')
 sw=exact[0];switch_count=int(sw['outer_count']);records={int(x['outer_index']):x['pairs'] for x in sw.get('inner_pair_rows',[])}
 if set(records)!=set(range(switch_count)):raise ValueError(f'{h}: incomplete switch record coverage')
 indirect=[int(x) for x in idx['u16_values']]
 if any(x<0 or x>=switch_count for x in indirect):raise ValueError(f'{h}: indirect switch index OOB')
 drows=[];used=set()
 for d in desc['rows']:
  vals=[int(x) for x in d['u16']];a=resolve_descriptor_list(vals[0],vals[1],indirect,switch_count);bb=resolve_descriptor_list(vals[2],vals[3],indirect,switch_count)
  for z in (a,bb):
   if z['mode']=='indirect_list':used.update(range(z['start'],z['start']+z['count']))
  ap=flatten(records,a['switch_record_indices']);bp=flatten(records,bb['switch_record_indices'])
  drows.append({'descriptor_index':int(d['index']),'raw_u16':vals,'list_a_indices':a['switch_record_indices'],'list_b_indices':bb['switch_record_indices'],'list_a_pairs':[list(x) for x in ap],'list_b_pairs':[list(x) for x in bp],'B_same_keys_all_invalid':([k for k,v in ap]==[k for k,v in bp] and all(v==INVALID for k,v in bp))})
 if used and used!=set(range(len(indirect))):raise ValueError(f'{h}: indirect list not exactly consumed')
 tags=[norm(x) for x in mats['tag_hashes']];groups=[]
 descriptor_coverage=set()
 for r in maps['rows']:
  vi=int(r['index']);count=int(r['material_count']);ms=int(r['material_start_index']);ds=int(r['unk08'])
  if count<=0 or ms<0 or ms+count>len(tags) or ds<0 or ds+count>len(drows):raise ValueError(f'{h}: group {vi} range invalid')
  members=[]
  for local in range(count):
   di=ds+local;descriptor_coverage.add(di);dr=drows[di]
   members.append({'member_index':local,'material_tag_hash':tags[ms+local],'descriptor_index':di,'list_a_pairs':dr['list_a_pairs'],'list_b_pairs':dr['list_b_pairs'],'B_same_keys_all_invalid':dr['B_same_keys_all_invalid']})
  groups.append({'variant_shader_index':vi,'material_count':count,'material_start_index':ms,'descriptor_start_index':ds,'members':members})
 if descriptor_coverage!=set(range(len(drows))):raise ValueError(f'{h}: descriptor coverage incomplete')
 return {'resource_hash':h,'model_tag_hash':norm(p.get('embedded_model_tag_hash','FFFFFFFF')),'sha256':hashlib.sha256(b).hexdigest(),'source':src,'switch_record_count':switch_count,'switch_records':records,'descriptor_count':len(drows),'descriptor_rows':drows,'group_count':len(groups),'groups':groups,'material_count':len(tags),'B_invariant_count':sum(x['B_same_keys_all_invalid'] for x in drows)}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--placement-calibration',type=Path,required=True);ap.add_argument('--member-catalog',type=Path,action='append',required=True);ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
 src=json.loads(a.placement_calibration.read_text());viol=[]
 if src.get('status')!='D1_TOWER_PLACEMENT_PERMUTATION_CROSS_ENTITY_CALIBRATION':viol.append('upstream_calibration_not_green')
 if src.get('violations'):viol.append('upstream_calibration_has_violations')
 cats=load_catalogs(a.member_catalog);arc=SplitHttpTar([f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90);c=RemoteCorpus(arc,cats,a.runtime)
 resource_hashes=sorted({norm(r['model_resource_hash']) for r in src.get('calibration_rows',[]) if r.get('exact_switch_bank_model_count')==1 and r.get('model_resource_hash')})
 graphs={}
 for h in resource_hashes:
  try:graphs[h]=parse_graph(c,h)
  except Exception as ex:viol.append(f'{h}:{ex!r}')

 total_groups=unique_groups=ambiguous_groups=no_candidate_groups=0;placements=0
 specificity=collections.Counter();fallback=0;nonfallback=0
 per_model=collections.defaultdict(lambda:{'placements':0,'groups':0,'unique':0,'ambiguous':0,'no_candidate':0})
 xur_results=[]
 for row in src.get('calibration_rows',[]):
  if row.get('exact_switch_bank_model_count')!=1 or not row.get('model_resource_hash'):continue
  h=norm(row['model_resource_hash']);g=graphs.get(h)
  if not g:continue
  config={(norm(x['pair'][0]),norm(x['pair'][1])) for x in row.get('record_matches',[]) if x.get('exact_pair_in_own_model_switch_bank')}
  placements+=1;pm=per_model[h];pm['placements']+=1
  for group in g['groups']:
   total_groups+=1;pm['groups']+=1;sats=[]
   for m in group['members']:
    req={tuple(x) for x in m['list_a_pairs']}
    if req.issubset(config):sats.append((len(req),m))
   if not sats:
    no_candidate_groups+=1;pm['no_candidate']+=1;continue
   maxspec=max(n for n,m in sats);wins=[m for n,m in sats if n==maxspec]
   if len(wins)==1:
    unique_groups+=1;pm['unique']+=1;specificity[maxspec]+=1
    if maxspec==0:fallback+=1
    else:nonfallback+=1
   else:
    ambiguous_groups+=1;pm['ambiguous']+=1
   if norm(row['entity_hash']) in XUR_ENTITIES:
    target_hits=[]
    for label,t in TARGETS.items():
     if any(norm(m['material_tag_hash'])==t for m in group['members']):target_hits.append(label)
    if target_hits:
     xur_results.append({'entity_hash':norm(row['entity_hash']),'owner':row['owner'],'smap_offset':row['smap_offset'],'variant_shader_index':group['variant_shader_index'],'targets_in_group':target_hits,'config_pairs':[list(x) for x in sorted(config)],'max_specificity':maxspec,'candidate_members':[{'member_index':m['member_index'],'material_tag_hash':m['material_tag_hash'],'descriptor_index':m['descriptor_index'],'list_a_pairs':m['list_a_pairs']} for m in wins]})

 b_total=sum(g['descriptor_count'] for g in graphs.values());b_ok=sum(g['B_invariant_count'] for g in graphs.values())
 out={'schema':'d1_remote_tower_descriptor_selection_calibration/v1','status':'D1_TOWER_DESCRIPTOR_CANDIDATE_RULE_CORPUS_UNIQUE' if not viol and total_groups and unique_groups==total_groups else ('D1_TOWER_DESCRIPTOR_CANDIDATE_RULE_CORPUS_FRONTIER' if not viol else 'D1_TOWER_DESCRIPTOR_CANDIDATE_RULE_VIOLATIONS'),'upstream_placement_count':src.get('s152_placement_count'),'comparable_placement_count':placements,'unique_model_resource_count':len(graphs),'model_resources':[{k:v for k,v in g.items() if k not in ('switch_records','descriptor_rows','groups')} for g in graphs.values()],'descriptor_B_invariant':{'descriptor_count':b_total,'same_keys_all_B_invalid_count':b_ok,'invalid_value':INVALID},'candidate_rule_results':{'placement_group_evaluations':total_groups,'unique_candidate_groups':unique_groups,'ambiguous_groups':ambiguous_groups,'no_candidate_groups':no_candidate_groups,'unique_fraction':unique_groups/total_groups if total_groups else None,'fallback_unique_groups':fallback,'nonfallback_unique_groups':nonfallback,'winner_specificity_histogram':dict(sorted(specificity.items()))},'per_model':dict(per_model),'xur_target_group_results':xur_results,'proof':{'multi_model_candidate_rule_calibrated':bool(total_groups),'candidate_rule_unique_across_all_comparable_groups':unique_groups==total_groups and total_groups>0,'descriptor_B_same_keys_invalid_companion_corpus_invariant':b_ok==b_total and b_total>0,'D1_retail_consumer_execution_path_proven':False,'descriptor_evaluation_algorithm_source_closed':False},'gates':{'E6_80C885E6_live_selection_proven':False,'E7_80C885E7_live_selection_proven':False,'E8_80C885E8_live_selection_proven':False},'violations':viol,'policy':'Corpus determinism is structural calibration, not executable retail semantics. The D1 runtime consumer/evaluator must still be independently closed before live material gates advance.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'comparable_placements':placements,'model_resources':len(graphs),'B_invariant':out['descriptor_B_invariant'],'candidate_rule_results':out['candidate_rule_results'],'xur_target_group_sample':xur_results[:8],'proof':out['proof'],'gates':out['gates'],'violations':viol},indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
