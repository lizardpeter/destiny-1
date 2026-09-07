#!/usr/bin/env python3
"""Materialize D1 ROI Activity-owned entity placements.

Two serialized paths are preserved independently because Charm's D1 activity
entity view consumes both:

1. ordinary SMapDataTable / 808009A2 -> SMapDataEntry[]
2. SF6038080 / 808003F6 -> EntityResource / 80800861 ->
   S2E098080 discriminator + SDD078080 -> SMapDataEntry[]

SMapDataEntry D1 layout used here is source-pinned:
  +0x00 EntitySK FileHash (Charm GetEntityHash())
  +0x20 Rotation Vector4
  +0x30 Translation Vector4
  +0x80 WorldID u64
  +0x88 DataResource ResourcePointer

A zero-count DynamicArray is valid without dereferencing its serialized pointer.
The raw relative/absolute pointer evidence is still preserved in the report, but
an out-of-payload target is not a framing violation when count == 0.

Parallel Activity/scenario carriers can serialize the same real WorldID more than
once. Serialized references are never silently discarded, but a second view is
emitted with one runtime record per real WorldID only when EntitySK, transform and
DataResource class agree exactly. WorldID FFFFFFFFFFFFFFFF is a sentinel/no-identity
value observed in retail activities; records carrying it remain independent runtime
placements and are never collapsed together by the sentinel value.

No entity/NPC semantic label is inferred by this layer.
"""
from __future__ import annotations

import argparse,json,math,struct,sys
from collections import Counter,defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5
import d1_world_activity_entity_table_census as act

F603='808003F6'; MAP_TABLE='808009A2'; ENTITY_RESOURCE='80800861'
S2E='8080092E'; SDD='808007DD'; SENTITY='80800734'; MAP_ENTRY_STRIDE=0x90
NULLS={'00000000','FFFFFFFF'}; WORLD_ID_SENTINELS={'FFFFFFFFFFFFFFFF'}
PINNED_SOURCE=(
 'MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
 'Charm/ActivityMapEntityView.xaml.cs + Tiger/Schema/Activity/ActivityStructsROI.cs + '
 'Tiger/Schema/Entity/EntityResource.cs + Tiger/Schema/Entity/EntityStructs.cs + '
 'Tiger/Schema/Static/StaticMapData.cs + Tiger/SchemaTypes.cs')

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def hx(v):return f'{v:08X}'
def u32(b,o):return struct.unpack_from('<I',b,o)[0]
def u64(b,o):return struct.unpack_from('<Q',b,o)[0]
def i64(b,o):return struct.unpack_from('<q',b,o)[0]
def f4(b,o):return list(struct.unpack_from('<4f',b,o))

def meta(c,h,expected=None):
 h=norm(h);m=c.entry_meta(h)
 return {'hash':h,'exists':m is not None,'meta':m,'expected_class':expected,
         'class_matches':bool(m and (expected is None or norm(m.get('reference'))==expected)),
         'is_null_sentinel':h in NULLS}

def resource_pointer(b,off):
 if off+8>len(b):return {'ok':False,'field_offset':off,'error':'pointer_oob'}
 rel=i64(b,off);r={'ok':True,'field_offset':off,'relative':rel,'absolute':None,'resource_class':None,'is_null':rel==0}
 if rel==0:return r
 absolute=off+rel;r['absolute']=absolute
 if absolute<4 or absolute>len(b):r['ok']=False;r['error']='target_oob';return r
 r['resource_class_offset']=absolute-4;r['resource_class']=hx(u32(b,absolute-4));return r

def string_pointer(b,off):
 if off+8>len(b):return {'ok':False,'field_offset':off,'error':'pointer_oob'}
 rel=i64(b,off);absolute=None if rel==0 else off+rel
 r={'ok':True,'field_offset':off,'relative':rel,'absolute':absolute,'value':None}
 if rel==0:return r
 if absolute<0 or absolute>=len(b):r['ok']=False;r['error']='target_oob';return r
 end=b.find(b'\0',absolute)
 if end<0:end=min(len(b),absolute+4096)
 r['value']=b[absolute:end].decode('utf-8','replace');return r

def placement_dyn(b,off,stride):
 """Use the shared D1 descriptor math but do not dereference empty arrays."""
 arr=act.dyn(b,off,stride)
 if arr.get('count')==0:
  arr=dict(arr);arr['serialized_pointer_bounds_ok']=bool(arr.get('ok'));arr['zero_count_no_dereference']=True;arr['ok']=True;arr.pop('error',None)
 return arr

def parse_map_entry(c,b,o,i,source_kind,source_hash):
 ent=hx(u32(b,o));rot=f4(b,o+0x20);tr=f4(b,o+0x30);wid=u64(b,o+0x80);dr=resource_pointer(b,o+0x88)
 return {'source_kind':source_kind,'source_hash':source_hash,'index':i,'record_offset':o,
         'entity_hash':ent,'entity':meta(c,ent,SENTITY),'rotation':rot,'translation':tr,
         'transform_finite':all(math.isfinite(x) for x in rot+tr),'world_id':wid,
         'world_id_hex':f'{wid:016X}','data_resource':dr}

def parse_direct_table(c,h):
 h=norm(h);tm=meta(c,h,MAP_TABLE);b,src=c.payload(h)
 out={'map_data_table':h,'target':tm,'payload_source':src,'entries':[],'violations':[]}
 if not tm['class_matches'] or b is None:out['violations'].append('map_table_missing_class_or_payload');return out
 if len(b)<0x18:out['violations'].append('map_table_shorter_than_0x18');return out
 arr=placement_dyn(b,0x08,MAP_ENTRY_STRIDE);out['data_entries_array']=arr
 if not arr['ok']:out['violations'].append('map_table_data_entries_bounds');return out
 for i in range(arr['count']):
  row=parse_map_entry(c,b,arr['absolute']+i*MAP_ENTRY_STRIDE,i,'direct_s_map_data_table',h);out['entries'].append(row)
  if not row['transform_finite']:out['violations'].append(f'entry[{i}]:nonfinite_transform')
  if not row['data_resource']['ok']:out['violations'].append(f'entry[{i}]:data_resource_pointer_invalid')
 out['entry_count']=len(out['entries']);return out

def parse_f603(c,h):
 h=norm(h);fm=meta(c,h,F603);fb,fsrc=c.payload(h)
 out={'f603':h,'target':fm,'payload_source':fsrc,'collapsed':False,'entries':[],'violations':[]}
 if not fm['class_matches'] or fb is None:out['violations'].append('f603_missing_class_or_payload');return out
 if len(fb)<0x10:out['violations'].append('f603_shorter_than_0x10');return out
 erh=hx(u32(fb,0x0C));out['entity_resource']=meta(c,erh,ENTITY_RESOURCE);eb,esrc=c.payload(erh);out['entity_resource_payload_source']=esrc
 if erh in NULLS:out['violations'].append('null_entity_resource');return out
 if not out['entity_resource']['class_matches'] or eb is None:out['violations'].append('entity_resource_missing_class_or_payload');return out
 if len(eb)<0x20:out['violations'].append('entity_resource_shorter_than_0x20');return out
 p10=resource_pointer(eb,0x10);p18=resource_pointer(eb,0x18);out['unk10_pointer']=p10;out['unk18_pointer']=p18
 if not p10['ok'] or p10.get('resource_class')!=S2E:out['collapse_reason']='unk10_not_S2E098080';return out
 if not p18['ok'] or p18.get('resource_class')!=SDD:out['violations'].append('unk18_not_SDD078080');return out
 dd=p18['absolute']
 if dd is None or dd+0x78>len(eb):out['violations'].append('sdd_header_oob');return out
 out['sdd_absolute']=dd;out['dev_name']=string_pointer(eb,dd+0x60);arr=placement_dyn(eb,dd+0x68,MAP_ENTRY_STRIDE);out['data_entries_array']=arr
 if not arr['ok']:out['violations'].append('sdd_data_entries_bounds');return out
 for i in range(arr['count']):
  row=parse_map_entry(c,eb,arr['absolute']+i*MAP_ENTRY_STRIDE,i,'f603_collapsed',h);out['entries'].append(row)
  if not row['transform_finite']:out['violations'].append(f'entry[{i}]:nonfinite_transform')
  if not row['data_resource']['ok']:out['violations'].append(f'entry[{i}]:data_resource_pointer_invalid')
 out['collapsed']=True;out['entry_count']=len(out['entries']);return out

def _runtime_row(first,wid,rows,consistent,identity_kind):
 return {'world_id':first['world_id'],'world_id_hex':wid,'world_id_identity_kind':identity_kind,
   'entity_hash':first['entity_hash'],'rotation':first['rotation'],'translation':first['translation'],
   'transform_finite':first['transform_finite'],'data_resource_class':(first.get('data_resource') or {}).get('resource_class'),
   'serialized_reference_count':len(rows),'duplicate_serialization_count':max(0,len(rows)-1),
   'serializations_consistent':consistent,
   'source_references':[{'source_kind':x['source_kind'],'source_hash':x['source_hash'],'index':x['index'],'record_offset':x['record_offset']} for x in rows]}

def runtime_placement_view(real_rows,violations):
 """Collapse real WorldIDs exactly; preserve sentinel/no-identity rows independently."""
 groups=defaultdict(list);sentinel=[]
 for r in real_rows:
  if r['world_id_hex'] in WORLD_ID_SENTINELS:sentinel.append(r)
  else:groups[r['world_id_hex']].append(r)
 unique=[];duplicate_refs=0
 for wid in sorted(groups):
  rows=groups[wid];first=rows[0]
  sig=lambda x:(x['entity_hash'],tuple(x['rotation']),tuple(x['translation']),
                (x.get('data_resource') or {}).get('resource_class'),bool((x.get('data_resource') or {}).get('is_null')))
  signatures={sig(x) for x in rows};consistent=len(signatures)==1
  if not consistent:violations.append(f'world_id_conflicting_serializations:{wid}')
  duplicate_refs+=max(0,len(rows)-1)
  unique.append(_runtime_row(first,wid,rows,consistent,'real_world_id'))
 for r in sentinel:
  unique.append(_runtime_row(r,r['world_id_hex'],[r],True,'sentinel_no_identity'))
 return unique,duplicate_refs

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--snapshot',type=Path,action='append',required=True);ap.add_argument('--runtime',type=Path,required=True)
 ap.add_argument('--entity-table-census',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 src=json.loads(a.entity_table_census.read_text());f603s=[norm(x) for x in src.get('unique_f603_entity_resources',[]) if norm(x) not in NULLS]
 direct_hashes=[norm(x) for x in src.get('unique_map_data_tables',[]) if norm(x) not in NULLS]
 if not f603s and not direct_hashes:raise SystemExit('entity-table census contains no entity data sources')
 c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve());viol=[]
 f603_tables=[parse_f603(c,h) for h in f603s];direct_tables=[parse_direct_table(c,h) for h in direct_hashes]
 for t in f603_tables:viol.extend(f"{t['f603']}:{x}" for x in t['violations'])
 for t in direct_tables:viol.extend(f"{t['map_data_table']}:{x}" for x in t['violations'])
 f603_rows=[e for t in f603_tables for e in t['entries']];direct_rows=[e for t in direct_tables for e in t['entries']];rows=f603_rows+direct_rows
 real=[e for e in rows if e['entity_hash'] not in NULLS];resolved=[e for e in real if e['entity']['exists']];class_ok=[e for e in real if e['entity']['class_matches']]
 unique_world,duplicate_refs=runtime_placement_view(real,viol);sentinel_runtime=sum(x.get('world_id_identity_kind')=='sentinel_no_identity' for x in unique_world)
 dr_classes=Counter((e['data_resource'].get('resource_class') or ('NULL' if e['data_resource'].get('is_null') else 'UNKNOWN')) for e in rows)
 entity_refs=Counter(e['entity_hash'] for e in real);world_ids=Counter(e['world_id_hex'] for e in real);source_kinds=Counter(e['source_kind'] for e in rows)
 runtime_entity_counts=Counter(e['entity_hash'] for e in unique_world);collapse_reasons=Counter(t.get('collapse_reason','collapsed' if t.get('collapsed') else 'failed') for t in f603_tables)
 er_hashes=Counter(t.get('entity_resource',{}).get('hash') for t in f603_tables if t.get('entity_resource',{}).get('hash') not in NULLS)
 out={'schema_version':5,'status':'D1_ACTIVITY_ENTITY_RESOURCE_CENSUS_COMPLETE' if not viol else 'D1_ACTIVITY_ENTITY_RESOURCE_CENSUS_PARTIAL',
  'pinned_source':PINNED_SOURCE,'input_entity_table_census':str(a.entity_table_census),
  'f603_count':len(f603_tables),'collapsed_f603_count':sum(t.get('collapsed',False) for t in f603_tables),'collapse_reason_counts':dict(collapse_reasons),
  'unique_entity_resource_tags':len(er_hashes),'direct_map_data_table_count':len(direct_tables),'direct_map_entry_count':len(direct_rows),
  'f603_collapsed_entry_count':len(f603_rows),'collapsed_entry_count':len(rows),'source_kind_counts':dict(source_kinds),
  'real_entity_entry_count':len(real),'serialized_entity_placement_reference_count':len(real),
  'unique_runtime_world_placement_count':len(unique_world),'sentinel_world_id_runtime_placement_count':sentinel_runtime,
  'duplicate_serialized_placement_reference_count':duplicate_refs,'unique_entity_hash_count':len(entity_refs),'resolved_entity_entry_count':len(resolved),
  'entity_class_match_entry_count':len(class_ok),'unique_world_id_count':len(world_ids),'data_resource_class_counts':dict(dr_classes),
  'entity_reference_counts':dict(entity_refs),'runtime_entity_placement_counts':dict(runtime_entity_counts),
  'world_id_reference_counts':dict(world_ids),'unique_entity_hashes':sorted(entity_refs),'unique_world_placements':unique_world,
  'direct_tables':direct_tables,'tables':f603_tables,'violations':viol,
  'policy':('Preserves both D1 activity entity paths used by Charm. Serialized references remain loss-preserved. Real WorldID values are used as runtime-placement identity only after repeated serializations agree exactly on EntitySK, transform and DataResource class. WorldID FFFFFFFFFFFFFFFF is treated as a sentinel/no-identity value and each such serialization remains an independent runtime placement. Zero-count arrays are never dereferenced. No NPC semantic is inferred.')}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 keys=('status','f603_count','collapsed_f603_count','collapse_reason_counts','unique_entity_resource_tags','direct_map_data_table_count','direct_map_entry_count','f603_collapsed_entry_count','collapsed_entry_count','source_kind_counts','real_entity_entry_count','serialized_entity_placement_reference_count','unique_runtime_world_placement_count','sentinel_world_id_runtime_placement_count','duplicate_serialized_placement_reference_count','unique_entity_hash_count','resolved_entity_entry_count','entity_class_match_entry_count','unique_world_id_count','data_resource_class_counts','violations')
 print(json.dumps({k:out[k] for k in keys},indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
