#!/usr/bin/env python3
"""Scan exact Xur SEntity + direct EntityResource payloads for material switch state.

The static model-parent graph already proves four switch keys and their exact
value domains.  This probe does not invent a runtime state representation.  It
checks only exact byte equality for:

* each 32-bit switch key;
* each known 32-bit value;
* exact adjacent little-endian (key,value) pairs;

Scope is source-owned and bounded: the two exact Xur SEntities and every direct
resource FileHash serialized in each SEntity.  If no exact adjacent pair occurs,
the result remains a frontier and a later recursive dependency probe is needed.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar
from d1_world_entity_dependency_census import parse_entity

NULLS={'00000000','FFFFFFFF'}
KEYS=['51E7A18D','4C58EF8F','26170C92','6EECD523']
VALUES={
 '51E7A18D':['6DFE676D'],
 '4C58EF8F':['237B2A6A','4AC210DE','562B37AD','5869948C','5EE47B3A','6093B6B7','676A29BB','693AC432','6C4E2617','7365B554','AE1880F4','C2D87ACF','D5A2FB2C','D93AF609','E32027FC'],
 '26170C92':['31BAEAC2','4AC210DE','562B37AD','5EE47B3A','6093B6B7','676A29BB','693AC432','6C4E2617','7365B554','742F9CDE','871AC0EA','9932E645','AE1880F4','D93AF609','E32027FC'],
 '6EECD523':['4B375162','6CC50CB8','871AC0EA'],
}
ALL_VALUES=sorted({v for vs in VALUES.values() for v in vs})


def norm(x)->str:return str(x).upper().removeprefix('0X').zfill(8)

def le(h:str)->bytes:return struct.pack('<I',int(h,16))

def offsets(blob:bytes,needle:bytes)->list[int]:
 out=[];start=0
 while True:
  i=blob.find(needle,start)
  if i<0:return out
  out.append(i);start=i+1

def context(blob:bytes,off:int,radius:int=16)->str:
 lo=max(0,off-radius);hi=min(len(blob),off+8+radius)
 return blob[lo:hi].hex()

def scan_blob(tag:str,reference:str|None,blob:bytes,source:str|None,kind:str)->dict:
 key_hits={};value_hits={};pairs=[]
 for k in KEYS:
  os=offsets(blob,le(k))
  if os:key_hits[k]=os
 for v in ALL_VALUES:
  os=offsets(blob,le(v))
  if os:value_hits[v]=os
 for k in KEYS:
  for v in VALUES[k]:
   needle=le(k)+le(v)
   for o in offsets(blob,needle):
    pairs.append({'key':k,'value':v,'offset':o,'aligned4':o%4==0,'context_hex':context(blob,o)})
 return {
  'tag_hash':norm(tag),'reference':None if reference is None else norm(reference),'kind':kind,
  'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'source':source,
  'key_hits':key_hits,'value_hits':value_hits,'adjacent_key_value_pairs':pairs,
 }

def main()->int:
 ap=argparse.ArgumentParser()
 ap.add_argument('--entity',action='append',required=True)
 ap.add_argument('--member-catalog',type=Path,action='append',required=True)
 ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
 ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
 a=ap.parse_args()
 cats=load_catalogs(a.member_catalog)
 arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
 c=RemoteCorpus(arc,cats,a.runtime)
 rows=[];viol=[];all_pair_hits=[];all_key_hits=[];all_value_hits=[]
 for ent_raw in a.entity:
  ent=norm(ent_raw)
  try:
   em=c.entry_meta(ent);eb,esrc=c.payload(ent)
   if em is None or eb is None:raise ValueError('exact SEntity payload unavailable')
   erow=parse_entity(c,ent)
   direct=[]
   entity_scan=scan_blob(ent,em.get('reference'),eb,esrc,'s_entity')
   seen=set()
   for rr in erow.get('resources',[]):
    h=norm(rr.get('resource_hash','FFFFFFFF'))
    if h in NULLS or h in seen:continue
    seen.add(h)
    try:
     m=c.entry_meta(h);b,src=c.payload(h)
     if m is None or b is None:raise ValueError('exact direct resource payload unavailable')
     direct.append(scan_blob(h,m.get('reference'),b,src,'direct_entity_resource'))
    except Exception as ex:
     direct.append({'tag_hash':h,'kind':'direct_entity_resource','error':repr(ex)})
     viol.append(f'{ent}:{h}:{ex!r}')
   row={'entity':ent,'entity_parse_violations':erow.get('violations',[]),'direct_resource_count':len(seen),'entity_payload':entity_scan,'direct_resources':direct}
   rows.append(row)
  except Exception as ex:
   rows.append({'entity':ent,'error':repr(ex)});viol.append(f'{ent}:{ex!r}');continue

 for row in rows:
  for rec in [row.get('entity_payload')]+row.get('direct_resources',[]):
   if not rec or rec.get('error'):continue
   for p in rec.get('adjacent_key_value_pairs',[]):all_pair_hits.append({'entity':row['entity'],'tag_hash':rec['tag_hash'],'reference':rec['reference'],**p})
   for k,os in rec.get('key_hits',{}).items():
    for o in os:all_key_hits.append({'entity':row['entity'],'tag_hash':rec['tag_hash'],'reference':rec['reference'],'key':k,'offset':o,'aligned4':o%4==0})
   for v,os in rec.get('value_hits',{}).items():
    for o in os:all_value_hits.append({'entity':row['entity'],'tag_hash':rec['tag_hash'],'reference':rec['reference'],'value':v,'offset':o,'aligned4':o%4==0})

 # Exact adjacent key/value pairs are evidence that a scoped source payload
 # serializes one of the static-graph pairs.  They are not automatically named
 # live state until the owning resource's semantic role is established.
 status='D1_XUR_DIRECT_MATERIAL_SWITCH_PAIR_EVIDENCE' if all_pair_hits and not viol else 'D1_XUR_DIRECT_MATERIAL_SWITCH_STATE_FRONTIER'
 rep={
  'schema_version':1,'status':status,'entities':[norm(x) for x in a.entity],
  'static_switch_keys':KEYS,'static_value_domain':VALUES,
  'rows':rows,'adjacent_pair_hits':all_pair_hits,'key_hits':all_key_hits,'value_hits':all_value_hits,
  'adjacent_pair_hit_count':len(all_pair_hits),'key_hit_count':len(all_key_hits),'value_hit_count':len(all_value_hits),
  'violations':viol,
  'policy':'Only exact bytes in source-owned SEntity/direct-resource payloads are reported. Pair presence is not promoted to live configuration semantics without owning-resource closure.',
  'live_configuration_state_complete':False,
  'retail_material_member_selection_complete':False,
 }
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
 print(json.dumps({'status':status,'pairs':all_pair_hits,'key_hits':all_key_hits,'value_hit_count':len(all_value_hits),'violations':viol},indent=2))
 return 0 if not viol else 2

if __name__=='__main__':raise SystemExit(main())
