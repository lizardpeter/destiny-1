#!/usr/bin/env python3
"""Decode one exact D1 ROI S6E078080 activity resource and its F603 ownership edges.

Source layout is pinned by Charm ActivityStructsROI.cs:
  S6E078080 +0x30 DynamicArray<SE9058080> stride 0x28
  SE9058080 +0x10 Tag<SMapDataTable>
  SE9058080 +0x18 DynamicArray<S22428080> stride 0x04
  S22428080 +0x00 Tag<SF6038080>
  SF6038080 +0x0C EntityResource FileHash

The tool reports those literal edges and parses each EntityResource with the existing
D1 resource parser. It is intentionally semantic-conservative beyond parser-proven
roles.
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

S6E='8080076E';MAP='808009A2';F603='808003F6';NULLS={'00000000','FFFFFFFF'}
def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def u32(b,o):return struct.unpack_from('<I',b,o)[0]
def i32(b,o):return struct.unpack_from('<i',b,o)[0]
def i64(b,o):return struct.unpack_from('<q',b,o)[0]
def hx(v):return f'{v:08X}'
def dyn(b,o,stride):
 c=i32(b,o);rel=i64(b,o+8);a=o+8+rel+0x10;end=a+max(c,0)*stride
 return {'count':c,'relative':rel,'absolute':a,'end':end,'stride':stride,'ok':c>=0 and a>=0 and end<=len(b)}

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
   row['f603s'].append(fr)
  stages.append(row)
 out={'schema':'d1_remote_s6e_stage_probe/v1','status':'D1_REMOTE_S6E_STAGE_PROBE_COMPLETE' if not viol else 'D1_REMOTE_S6E_STAGE_PROBE_WITH_VIOLATIONS','s6e':h,'s6e_meta':m,'payload_source':src,'stage_array':arr,'stages':stages,'violations':viol,'policy':'All stage/map/F603/EntityResource edges are literal serialized FileHashes. EntityResource semantics are only those returned by the existing source-crosschecked parser.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
 print('STATUS',out['status'],'S6E',h,'STAGES',len(stages),'VIOLATIONS',len(viol))
 for s in stages:
  print('STAGE',s['stage_index'],'MAP',s['map_data_table']['hash'],'F603',len(s['f603s']))
  for f in s['f603s']:
   er=f.get('entity_resource') or {};p=f.get('entity_resource_parse') or {}
   print(' F603',f['f603']['hash'],'ER',er.get('hash'),'ROLE',p.get('semantic_role'),'D912',p.get('scripted_entity_table_tag_hash'),'DEV',p.get('dev_name'))
 return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
