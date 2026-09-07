#!/usr/bin/env python3
"""Decode one exact D1 ROI S6E078080 activity resource and its F603 ownership edges.

Source layout is pinned by Charm ActivityStructsROI.cs:
  S6E078080 +0x30 DynamicArray<SE9058080> stride 0x28
  SE9058080 +0x10 Tag<SMapDataTable>
  SE9058080 +0x18 DynamicArray<S22428080> stride 0x04
  S22428080 +0x00 Tag<SF6038080>
  SF6038080 +0x0C EntityResource FileHash

A zero-count DynamicArray is valid without dereferencing its serialized relative
pointer. The calculated pointer evidence is retained, but an out-of-payload target
is not a bounds violation when count == 0.

Every F603 is additionally passed through the already source-validated D1 Activity
collapse parser. When its EntityResource pair is 8080092E -> 808007DD, the embedded
SDD078080.DataEntries are decoded as exact SMapDataEntry placements.
"""
from __future__ import annotations
import argparse,json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar
from d1_remote_activity_placements import RemoteCorpus
from d1_entity_resource_probe import parse_resource,ENTITY_RESOURCE_CLASS
import d1_world_activity_entity_resource_census as placements

S6E='8080076E';MAP='808009A2';F603='808003F6';NULLS={'00000000','FFFFFFFF'}
def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def u32(b,o):return struct.unpack_from('<I',b,o)[0]
def i32(b,o):return struct.unpack_from('<i',b,o)[0]
def i64(b,o):return struct.unpack_from('<q',b,o)[0]
def hx(v):return f'{v:08X}'
def dyn(b,o,stride):
 if o+0x10>len(b):return {'count':None,'relative':None,'absolute':None,'end':None,'stride':stride,'ok':False,'error':'descriptor_oob'}
 c=i32(b,o);rel=i64(b,o+8);a=o+8+rel+0x10;end=a+max(c,0)*stride
 pointer_ok=c>=0 and a>=0 and end<=len(b)
 return {'count':c,'relative':rel,'absolute':a,'end':end,'stride':stride,'ok':c==0 or pointer_ok,
         'serialized_pointer_bounds_ok':pointer_ok,'zero_count_no_dereference':c==0}

def meta(c,h):
 h=norm(h);m=c.entry_meta(h);return {'hash':h,'exists':m is not None,'reference':None if m is None else norm(m.get('reference')),'meta':m}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--s6e',required=True)
 ap.add_argument('--member-catalog',type=Path,action='append',required=True);ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
 cats=load_catalogs(a.member_catalog);arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90);c=RemoteCorpus(arc,cats,a.runtime)
 h=norm(a.s6e);m=meta(c,h);b,src=c.payload(h);viol=[];stages=[]
 if not m['exists'] or m['reference']!=S6E or b is None:raise SystemExit(f'{h} unavailable/wrong class {m}')
 arr=dyn(b,0x30,0x28)
 if not arr['ok']:raise SystemExit(f'{h} bad S6E +0x30 array {arr}')
 for i in range(arr['count']):
  o=arr['absolute']+i*0x28;table=hx(u32(b,o+0x10));sub=dyn(b,o+0x18,4);row={'stage_index':i,'record_offset':o,'map_data_table':meta(c,table),'f603_array':sub,'f603s':[]}
  if table not in NULLS and row['map_data_table']['reference']!=MAP:viol.append(f'stage[{i}] map {table} class {row["map_data_table"]["reference"]}')
  if not sub['ok']:viol.append(f'stage[{i}] f603 array bounds');stages.append(row);continue
  for j in range(sub['count']):
   fh=hx(u32(b,sub['absolute']+j*4));fm=meta(c,fh);fr={'index':j,'f603':fm}
   fb,fsrc=c.payload(fh);fr['payload_source']=fsrc
   if fh in NULLS:row['f603s'].append(fr);continue
   if not fm['exists'] or fm['reference']!=F603 or fb is None or len(fb)<0x10:
    fr['error']='F603 unavailable/wrong class';viol.append(f'stage[{i}] f603[{j}] {fh} invalid');row['f603s'].append(fr);continue
   erh=hx(u32(fb,0x0C));em=meta(c,erh);fr['entity_resource']=em;eb,esrc=c.payload(erh);fr['entity_resource_payload_source']=esrc
   if erh not in NULLS and em['exists'] and em['reference']==ENTITY_RESOURCE_CLASS and eb is not None:
    try:fr['entity_resource_parse']=parse_resource(eb,'PS4')
    except Exception as ex:fr['entity_resource_parse_error']=repr(ex)
   else:viol.append(f'stage[{i}] f603[{j}] entity resource {erh} invalid')
   try:
    cp=placements.parse_f603(c,fh);fr['activity_collapse']=cp
    if cp.get('violations'):viol.extend(f'stage[{i}] f603[{j}] collapse:{x}' for x in cp['violations'])
   except Exception as ex:
    fr['activity_collapse_error']=repr(ex);viol.append(f'stage[{i}] f603[{j}] collapse exception:{ex!r}')
   row['f603s'].append(fr)
  stages.append(row)
 exact_entries=[]
 for s in stages:
  for f in s['f603s']:
   cp=f.get('activity_collapse') or {}
   for e in cp.get('entries',[]):exact_entries.append({'stage_index':s['stage_index'],'f603':f['f603']['hash'],'entity_resource':(f.get('entity_resource') or {}).get('hash'),**e})
 out={'schema':'d1_remote_s6e_stage_probe/v2','status':'D1_REMOTE_S6E_STAGE_PROBE_COMPLETE' if not viol else 'D1_REMOTE_S6E_STAGE_PROBE_WITH_VIOLATIONS','s6e':h,'s6e_meta':m,'payload_source':src,'stage_array':arr,'stages':stages,'collapsed_placement_entry_count':len(exact_entries),'collapsed_placement_entries':exact_entries,'violations':viol,'policy':'All stage/map/F603/EntityResource edges are literal serialized FileHashes. Zero-count DynamicArrays are valid without dereferencing their serialized pointer; calculated pointer evidence is retained. 8080092E -> 808007DD resources are decoded only through the source-validated Activity collapse path. Entity identities and transforms in collapsed entries are exact SMapDataEntry fields; dev-name text is provenance, not identity inference.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
 print('STATUS',out['status'],'S6E',h,'STAGES',len(stages),'COLLAPSED_PLACEMENTS',len(exact_entries),'VIOLATIONS',len(viol))
 for s in stages:
  print('STAGE',s['stage_index'],'MAP',s['map_data_table']['hash'],'F603',len(s['f603s']))
  for f in s['f603s']:
   er=f.get('entity_resource') or {};p=f.get('entity_resource_parse') or {};cp=f.get('activity_collapse') or {}
   print(' F603',f['f603']['hash'],'ER',er.get('hash'),'ROLE',p.get('semantic_role'),'PAIR',((p.get('unk10') or {}).get('class_hash'),(p.get('unk18') or {}).get('class_hash')),'COLLAPSED',cp.get('collapsed'),'DEV',(cp.get('dev_name') or {}).get('value'),'ENTRIES',len(cp.get('entries',[])))
   for e in cp.get('entries',[]):print('   ENTRY',e.get('entity_hash'),'WORLD',e.get('world_id_hex'),'T',e.get('translation'),'R',e.get('rotation'),'DATA_CLASS',(e.get('data_resource') or {}).get('resource_class'))
 return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
