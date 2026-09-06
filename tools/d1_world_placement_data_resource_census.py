#!/usr/bin/env python3
"""Census optional D1 SMapDataEntry DataResource payloads.

This layer is intentionally separate from SEntity ownership. A world placement can
carry instance-specific data at SMapDataEntry +0x88 even when many placements share
the same reusable SEntity owner.

Known source-backed class:
  80802B15 / raw 152B8080 / S152B8080
    +0x10 DynamicArray<S4E2A8080>, stride 0x08
  S4E2A8080
    +0x00 TigerHash
    +0x04 StringHash Type

Charm's source comment describes Type as faction/type-like data (examples include a
faction and a weapon/type label), so this tool deliberately reports the raw Type
StringHash without assigning stronger semantics.

Unknown classes are still loss-preserved with exact source host, target offset,
prefix bytes, placement WorldID and entity owner. No size is invented for an unknown
inline resource.
"""
from __future__ import annotations

import argparse,json,struct,sys
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5

S152='80802B15'
NULLS={'00000000','FFFFFFFF'}
PINNED_SOURCE=('MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
 'Tiger/Schema/Activity/ActivityStructsROI.cs + Tiger/SchemaTypes.cs')

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def hx(v):return f'{v:08X}'
def i32(b,o):return struct.unpack_from('<i',b,o)[0]
def u32(b,o):return struct.unpack_from('<I',b,o)[0]
def i64(b,o):return struct.unpack_from('<q',b,o)[0]

def dyn(b,off,stride):
 if off+0x10>len(b):return {'ok':False,'field_offset':off,'error':'descriptor_oob'}
 count=i32(b,off);unk=u32(b,off+4);rel=i64(b,off+8);absolute=off+8+rel+0x10;end=absolute+max(count,0)*stride
 pointer_ok=absolute>=0 and end<=len(b);ok=count>=0 and (count==0 or pointer_ok)
 return {'ok':ok,'field_offset':off,'count':count,'unknown04':unk,'relative':rel,'absolute':absolute,'end':end,
         'stride':stride,'serialized_pointer_bounds_ok':pointer_ok,'zero_count_no_dereference':count==0,'payload_size':len(b)}

def decode_s152(b,base):
 out={'class_hash':S152,'base_offset':base,'violations':[],'records':[]}
 if base<0 or base+0x28>len(b):out['violations'].append('S152_header_oob');return out
 arr=dyn(b,base+0x10,0x08);out['records_array']=arr
 if not arr['ok']:out['violations'].append('S152_records_bounds');return out
 for i in range(arr['count']):
  o=arr['absolute']+i*8
  out['records'].append({'index':i,'record_offset':o,'tiger_hash':hx(u32(b,o)),'type_string_hash':hx(u32(b,o+4))})
 out['record_count']=len(out['records']);return out

def host_for_direct(c,table):
 h=norm(table['map_data_table']);b,src=c.payload(h);return h,b,src

def host_for_f603(c,table):
 h=norm((table.get('entity_resource') or {}).get('hash','FFFFFFFF'));b,src=c.payload(h);return h,b,src

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--snapshot',type=Path,action='append',required=True);ap.add_argument('--runtime',type=Path,required=True)
 ap.add_argument('--placements',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 p=json.loads(a.placements.read_text());c=v5.v3.base.Corpus([x.resolve() for x in a.snapshot],a.runtime.resolve())
 rows=[];viol=[];type_hashes=Counter();class_counts=Counter();worldids=Counter()
 for collection,hostfn in ((p.get('direct_tables',[]),host_for_direct),(p.get('tables',[]),host_for_f603)):
  for table in collection:
   host_hash,b,src=hostfn(c,table)
   for e in table.get('entries',[]):
    dr=e.get('data_resource') or {};cls=dr.get('resource_class')
    if dr.get('is_null') or not cls:continue
    cls=norm(cls);base=dr.get('absolute')
    row={'source_kind':e.get('source_kind'),'source_hash':e.get('source_hash'),'source_index':e.get('index'),
         'record_offset':e.get('record_offset'),'host_hash':host_hash,'host_payload_source':src,
         'entity_hash':norm(e.get('entity_hash','FFFFFFFF')),'world_id':e.get('world_id'),'world_id_hex':e.get('world_id_hex'),
         'data_resource_class':cls,'data_resource_absolute':base,'pointer':dr,'decoded':None,'violations':[]}
    class_counts[cls]+=1;worldids[e.get('world_id_hex')]+=1
    if b is None:row['violations'].append('host_payload_unavailable')
    elif not isinstance(base,int) or base<0 or base>len(b):row['violations'].append('data_resource_target_oob')
    else:
     row['raw_prefix_hex']=b[base:min(len(b),base+0x100)].hex()
     row['raw_prefix_length']=min(0x100,max(0,len(b)-base))
     if cls==S152:
      dec=decode_s152(b,base);row['decoded']=dec;row['violations'].extend(dec['violations'])
      for r in dec.get('records',[]):type_hashes[r['type_string_hash']]+=1
    if row['violations']:viol.extend(f"{row['world_id_hex']}/{cls}:{x}" for x in row['violations'])
    rows.append(row)
 out={'schema_version':1,'status':'D1_WORLD_PLACEMENT_DATA_RESOURCE_CENSUS_COMPLETE' if not viol else 'D1_WORLD_PLACEMENT_DATA_RESOURCE_CENSUS_PARTIAL',
      'pinned_source':PINNED_SOURCE,'serialized_nonnull_data_resource_reference_count':len(rows),
      'unique_world_id_count':len(worldids),'data_resource_class_counts':dict(class_counts),
      'known_S152_reference_count':class_counts.get(S152,0),'unique_type_string_hash_count':len(type_hashes),
      'type_string_hash_reference_counts':dict(type_hashes),'unique_type_string_hashes':sorted(type_hashes),
      'resources':rows,'violations':viol,
      'policy':'Per-placement DataResource payloads remain separate from reusable SEntity ownership. Only source-defined S152B8080 is semantically decoded; unknown classes retain exact inline bytes and source provenance without invented size or meaning.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:out[k] for k in ('status','serialized_nonnull_data_resource_reference_count','unique_world_id_count','data_resource_class_counts','known_S152_reference_count','unique_type_string_hash_count','unique_type_string_hashes','violations')},indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
