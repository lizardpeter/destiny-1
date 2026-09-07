#!/usr/bin/env python3
"""Scan exact D1 EntityResource bytes for aligned uint32 values that resolve to retail tags.

This is a conservative structure-discovery aid for still-unknown D1 resource classes.
For each requested EntityResource it validates class 80800861, parses the known outer
ResourcePointer pair, and then tests every aligned uint32 in the payload against the
verified universal retail package catalog. Only values that resolve to an actual exact
entry are reported, together with byte offset and resolved class/type/size.

A resolved value proves a literal retail FileHash occurrence at that byte offset. It
does not by itself assign field semantics. Nulls, self references, and obvious outer
pointer class words may be retained as context but are labelled separately.
"""
from __future__ import annotations
import argparse,collections,json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_crota_raid_candidate_probe import LazyExactHashResolver,meta_row,norm
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS,parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar

NULLS={'00000000','FFFFFFFF'}
def u32(b,o):return struct.unpack_from('<I',b,o)[0]
def hx(v):return f'{v:08X}'

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--tag-hash',action='append',required=True);ap.add_argument('--member-catalog',type=Path,action='append',required=True);ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
 cats=load_catalogs(a.member_catalog);arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90);r=LazyExactHashResolver(arc,cats,a.runtime)
 rows=[];viol=[];global_classes=collections.Counter()
 for raw in a.tag_hash:
  h=norm(raw);row={'tag_hash':h,'hits':[],'violations':[]}
  try:
   v,e=r.locate(h);row['entry']=meta_row(e)
   if e['reference'].upper()!=ENTITY_RESOURCE_CLASS:raise ValueError(f'{h}: ref {e["reference"]} != {ENTITY_RESOURCE_CLASS}')
   b=v.entry(e['index']);row['payload_size']=len(b);row['outer_parse']=parse_resource(b,'PS4')
   pair=((row['outer_parse'].get('unk10') or {}).get('class_hash'),(row['outer_parse'].get('unk18') or {}).get('class_hash'));row['outer_pair']=pair
   cache={}
   for off in range(0,len(b)-3,4):
    val=hx(u32(b,off))
    if val in NULLS:continue
    if val==h:continue
    if val not in cache:
     try:
      vv,ee=r.locate(val);cache[val]={'ok':True,'entry':meta_row(ee)}
     except Exception as ex:cache[val]={'ok':False}
    c=cache[val]
    if not c['ok']:continue
    hit={'offset':off,'offset_hex':f'0x{off:X}','value':val,'entry':c['entry']}
    # Mark outer ResourcePointer class words when they happen to resolve as tags;
    # they are schema identifiers rather than evidence of a FileHash field.
    hit['context']='resolved_aligned_u32_candidate_filehash'
    row['hits'].append(hit);global_classes[c['entry']['reference']]+=1
   row['resolved_aligned_u32_count']=len(row['hits']);row['resolved_unique_hash_count']=len({x['value'] for x in row['hits']})
  except Exception as ex:
   row['violations'].append(repr(ex));viol.append({'tag_hash':h,'error':repr(ex)})
  rows.append(row)
 out={'schema':'d1_remote_entity_resource_filehash_scan/v1','status':'D1_REMOTE_ENTITY_RESOURCE_FILEHASH_SCAN_COMPLETE' if not viol else 'D1_REMOTE_ENTITY_RESOURCE_FILEHASH_SCAN_WITH_VIOLATIONS','resources':rows,'resolved_reference_class_frequency':dict(global_classes),'violations':viol,'policy':'Each hit is only an aligned uint32 whose exact value resolves through the verified retail catalog. This proves literal occurrence, not field meaning or ownership; semantics require independent schema/consumer evidence.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
 for x in rows:
  print('RESOURCE',x['tag_hash'],'PAIR',x.get('outer_pair'),'HITS',len(x.get('hits',[])))
  for q in x.get('hits',[]):print(' ',q['offset_hex'],q['value'],'REF',q['entry']['reference'],'TYPE',q['entry']['type'],'SUB',q['entry']['subtype'],'SIZE',q['entry']['file_size'])
 print('STATUS',out['status'],'VIOLATIONS',viol);return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
