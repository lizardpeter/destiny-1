#!/usr/bin/env python3
"""Trace 80C88434 selector evidence through the three exact EntitySK resource graphs.

All nine SMapDataEntry DataResource pointers for this actor family are proven null.
This probe therefore opens only the three source-owned EntitySKs and every resource
explicitly serialized in each SEntity resource array. It records resource-set deltas
and exact aligned occurrences of the visible-material selector key/value domain:

  26170C92 -> {E32027FC, AE1880F4, 6093B6B7}

Raw occurrences remain discovery evidence. No material is selected by this tool.
"""
from __future__ import annotations
import argparse,collections,json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_remote_s_entity_resource_package_find import S_ENTITY_REF,parse_entity_resources
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS,parse_resource
from d1_split_tar_extract import SplitHttpTar

ENTITIES=['80C7A5AD','80C7ACC5','80C883CA']
TARGETS=['26170C92','E32027FC','AE1880F4','6093B6B7','871AC0EA']
def norm(x): return str(x).upper().removeprefix('0X').zfill(8)
def aligned_hits(b:bytes,h:str):
 needle=struct.pack('<I',int(h,16));out=[];p=0
 while True:
  i=b.find(needle,p)
  if i<0: break
  p=i+1
  if i%4==0: out.append(i)
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--member-catalog',type=Path,action='append',required=True);ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
 cats=load_catalogs(a.member_catalog);arc=SplitHttpTar([f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90);c=RemoteCorpus(arc,cats,a.runtime)
 violations=[];rows=[];sets={}
 for entity in ENTITIES:
  meta=c.entry_meta(entity);eb,esrc=c.payload(entity)
  if meta is None or eb is None or norm(meta.get('reference',''))!=S_ENTITY_REF:
   violations.append(f'{entity}:entity_unavailable_or_class_mismatch');continue
  try: rr=parse_entity_resources(eb)
  except Exception as ex: violations.append(f'{entity}:resource_array:{ex!r}');continue
  resources=[];sets[entity]=[norm(x['resource_hash']) for x in rr]
  entity_hits={h:aligned_hits(eb,h) for h in TARGETS}
  for x in rr:
   rh=norm(x['resource_hash']);rm=c.entry_meta(rh);rb,rsrc=c.payload(rh)
   rec={'resource_index':int(x.get('resource_index',-1)),'resource_hash':rh,'reference':norm(rm.get('reference','FFFFFFFF')) if rm else None,'source':str(rsrc) if rsrc else None,'byte_count':len(rb) if rb is not None else None,'aligned_selector_hits':{}}
   if rb is not None:
    rec['aligned_selector_hits']={h:aligned_hits(rb,h) for h in TARGETS if aligned_hits(rb,h)}
    if rec['reference']==ENTITY_RESOURCE_CLASS:
     try:
      p=parse_resource(rb,'PS4');rec['entity_resource']={'semantic_role':p.get('semantic_role'),'embedded_model_tag_hash':norm(p.get('embedded_model_tag_hash','FFFFFFFF')),'unk08':p.get('unk08'),'unk10':p.get('unk10'),'unk18':p.get('unk18')}
     except Exception as ex: rec['entity_resource_error']=repr(ex)
   resources.append(rec)
  rows.append({'entity_hash':entity,'source':str(esrc),'resource_count':len(rr),'entity_payload_aligned_selector_hits':{h:v for h,v in entity_hits.items() if v},'resources':resources})
 allsets={e:set(v) for e,v in sets.items()};common=sorted(set.intersection(*allsets.values())) if len(allsets)==len(ENTITIES) else []
 deltas={e:sorted(allsets[e]-set(common)) for e in allsets}
 hit_summary=[]
 for r in rows:
  for h,offs in r['entity_payload_aligned_selector_hits'].items(): hit_summary.append({'entity':r['entity_hash'],'scope':'entity','hash':h,'offsets':offs})
  for q in r['resources']:
   for h,offs in q.get('aligned_selector_hits',{}).items(): hit_summary.append({'entity':r['entity_hash'],'scope':'resource','resource_hash':q['resource_hash'],'reference':q['reference'],'hash':h,'offsets':offs})
 out={'schema_version':1,'status':'D1_TOWER_80C88434_ENTITY_SELECTOR_PROBE_COMPLETE' if not violations else 'D1_TOWER_80C88434_ENTITY_SELECTOR_PROBE_VIOLATIONS','entities':rows,'common_resource_hashes':common,'entity_specific_resource_hashes':deltas,'selector_hit_summary':hit_summary,'violations':violations,'gates':{'selector_value_owned_by_entity_resource_graph':False,'visible_variant0_material_selected':False,'D1_retail_descriptor_evaluator_source_closed':False},'policy':'Only direct SEntity resource-array members are opened. Exact aligned key/value hits and resource-set deltas are discovery evidence, not evaluator semantics or live material selection.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'resource_counts':{r['entity_hash']:r['resource_count'] for r in rows},'common_resource_count':len(common),'entity_specific_resource_hashes':deltas,'selector_hit_summary':hit_summary,'violations':violations,'gates':out['gates']},indent=2))
 return 0 if not violations else 2
if __name__=='__main__': raise SystemExit(main())
