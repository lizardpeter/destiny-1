#!/usr/bin/env python3
"""Fail-closed Xur scripted-owner switch-state probe.

Targets exact Tower owners already discovered as literal backlinks to the two Xur
SEntities. SD9128080 owners are source-pinned scripted-entity tables; EB058080
remains an unresolved wrapper class. This probe records exact nested placement
context but does not promote key/value adjacency to live state without a schema-
typed field path.
"""
from __future__ import annotations
import argparse, hashlib, json, struct, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar

KEYS=['51E7A18D','4C58EF8F','26170C92','6EECD523']
VALUES={
'51E7A18D':['6DFE676D'],
'4C58EF8F':['237B2A6A','4AC210DE','562B37AD','5869948C','5EE47B3A','6093B6B7','676A29BB','693AC432','6C4E2617','7365B554','AE1880F4','C2D87ACF','D5A2FB2C','D93AF609','E32027FC'],
'26170C92':['31BAEAC2','4AC210DE','562B37AD','5EE47B3A','6093B6B7','676A29BB','693AC432','6C4E2617','7365B554','742F9CDE','871AC0EA','9932E645','AE1880F4','D93AF609','E32027FC'],
'6EECD523':['4B375162','6CC50CB8','871AC0EA']}
XURS=['80C7ACC8','80C885AA']
SD912='808012D9'
KNOWN_CLASSES={
'80800406':'SMapDataEntry_06048080',
'80801333':'S33138080',
'80802B15':'S152B8080',
'80802A4E':'S4E2A8080',
'80801348':'S48138080',
'808014D6':'SD6148080',
'80800184':'DynamicArray_serialized_header_observed',
}

def norm(s): return str(s).upper().removeprefix('0X').zfill(8)
def le(h): return struct.pack('<I',int(h,16))
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def q64(b,o): return struct.unpack_from('<q',b,o)[0]
def offs(b,n):
 out=[];p=0
 while True:
  p=b.find(n,p)
  if p<0:return out
  out.append(p);p+=1

def win(b,o,r=32):
 lo=max(0,o-r);hi=min(len(b),o+8+r);return b[lo:hi].hex()
def u32win(b,o,n=12):
 lo=max(0,(o//4-n)*4);hi=min(len(b)-(len(b)%4),(o//4+n+2)*4)
 return [{'offset':p,'offset_hex':f'0x{p:X}','u32':f'{u32(b,p):08X}','target':p==o,'class_name':KNOWN_CLASSES.get(f'{u32(b,p):08X}')} for p in range(lo,hi,4)]
def class_markers(b,lo,hi):
 out=[];hi=min(hi,len(b)-(len(b)%4))
 for p in range(max(0,lo),hi,4):
  h=f'{u32(b,p):08X}'
  if h in KNOWN_CLASSES: out.append({'offset':p,'offset_hex':f'0x{p:X}','class_hash':h,'class_name':KNOWN_CLASSES[h]})
 return out

def placement_record(b,xoff):
 # The ten SD912 tables have six placements exactly 0x130 apart. Capture the
 # complete interval around each Xur ref while preserving raw bytes. This is
 # discovery evidence; record boundaries are not promoted merely from stride.
 start=max(0,xoff-0x20); end=min(len(b),start+0x130)
 return {
  'xur_offset':xoff,'xur_offset_hex':f'0x{xoff:X}',
  'candidate_interval_start':start,'candidate_interval_end':end,
  'candidate_interval_hex':b[start:end].hex(),
  'xur_u32_window':u32win(b,xoff,16),
  'class_markers':class_markers(b,start,end),
 }

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--owner',action='append',required=True);ap.add_argument('--member-catalog',type=Path,action='append',required=True);ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
 cats=load_catalogs(a.member_catalog);arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90);c=RemoteCorpus(arc,cats,a.runtime)
 rows=[];viol=[]
 for raw in a.owner:
  h=norm(raw)
  try:
   m=c.entry_meta(h);b,src=c.payload(h)
   if m is None or b is None: raise ValueError('payload unavailable')
   ref=norm(m.get('reference','0'))
   kh={};vh={};pairs=[];xh={};placements=[]
   for k in KEYS:
    q=[]
    for o in offs(b,le(k)):q.append({'offset':o,'offset_hex':f'0x{o:X}','context_hex':win(b,o),'u32_window':u32win(b,o)})
    if q:kh[k]=q
    for v in VALUES[k]:
     oo=offs(b,le(v))
     if oo:vh.setdefault(v,[]).extend(oo)
     for o in offs(b,le(k)+le(v)):pairs.append({'key':k,'value':v,'offset':o,'offset_hex':f'0x{o:X}','context_hex':win(b,o)})
   for x in XURS:
    oo=offs(b,le(x))
    if oo:
     xh[x]=oo
     placements.extend({'entity':x,**placement_record(b,o)} for o in oo)
   rows.append({'tag_hash':h,'reference':ref,'is_source_pinned_SD912_scripted_entity_table':ref==SD912,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'source':src,'header_hex':b[:0x100].hex(),'xur_entity_hits':xh,'placement_contexts':placements,'key_hits':kh,'known_value_hits':vh,'adjacent_key_value_pairs':pairs,'live_switch_assignment_proven':False})
  except Exception as ex: viol.append(f'{h}:{ex!r}');rows.append({'tag_hash':h,'error':repr(ex)})
 rep={'schema':'d1_remote_xur_scripted_owner_switch_probe/v2','status':'D1_XUR_SCRIPTED_OWNER_SWITCH_FRONTIER' if not viol else 'D1_XUR_SCRIPTED_OWNER_SWITCH_VIOLATIONS','source_schema_chain':{'SD9128080':'FileSize + metadata + DynamicArray<SD6148080> + locations','SD6148080':'StringHash Type + DynamicArray<S48138080>','S48138080':'ResourcePointer -> SMapDataEntry(06048080)','SMapDataEntry':'D1 size 0x90; entity + world metadata; ResourcePointer DataResource at +0x88','S33138080':'ResourcePointer -> S152B8080; EntityName at +0x20','S152B8080':'DynamicArray<S4E2A8080> at +0x10','S4E2A8080':'TigerHash Unk00 + StringHash Type'},'rows':rows,'violations':viol,'gates':{'E6_80C885E6_live_selection_proven':False,'E7_80C885E7_live_selection_proven':False,'E8_80C885E8_live_selection_proven':False},'policy':'Typed SD912/SMapDataEntry/S331/S152B ownership is accepted only where source schema closes the pointer chain. Raw post-array words remain untyped until their owning schema field is established. No E6/E7/E8 gate is advanced from adjacency.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
 print(json.dumps({'status':rep['status'],'owners':len(rows),'sd912':sum(r.get('is_source_pinned_SD912_scripted_entity_table',False) for r in rows),'key_owner_count':sum(bool(r.get('key_hits')) for r in rows),'pair_owner_count':sum(bool(r.get('adjacent_key_value_pairs')) for r in rows),'placement_context_count':sum(len(r.get('placement_contexts',[])) for r in rows),'violations':viol,'gates':rep['gates']},indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
