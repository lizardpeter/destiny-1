#!/usr/bin/env python3
"""Fail-closed Xur scripted-owner switch-state probe.

For source-pinned D1 SD912 scripted placement tables, decode the exact
SMapDataEntry -> DataResource(S152B8080) -> DynamicArray<S4E2A8080> path using
Tiger's serialized relative-pointer rules.  This establishes placement-owned
configuration records without assuming that those records are consumed by the
material-permutation evaluator.
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
SMAP_CLASS=0x80800406
S152_CLASS=0x80802B15
S4E2A_CLASS=0x80802A4E
EXPECTED_XUR_CONFIG=[('EAFBB478','2CA33BDB'),('26170C92','4AC210DE')]

def norm(s): return str(s).upper().removeprefix('0X').zfill(8)
def le(h): return struct.pack('<I',int(h,16))
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def i32(b,o): return struct.unpack_from('<i',b,o)[0]
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
 return [{'offset':p,'offset_hex':f'0x{p:X}','u32':f'{u32(b,p):08X}','target':p==o} for p in range(lo,hi,4)]

def resource_pointer(b,field):
 if field<0 or field+8>len(b): raise ValueError(f'ResourcePointer field out of bounds: 0x{field:X}')
 rel=q64(b,field)
 if rel==0:return {'field_offset':field,'relative':0,'null':True}
 target=field+rel
 if target<4 or target>len(b): raise ValueError(f'ResourcePointer target out of bounds: field=0x{field:X} rel={rel} target=0x{target:X}')
 return {'field_offset':field,'relative':rel,'target_offset':target,'class_offset':target-4,'class_hash':f'{u32(b,target-4):08X}','null':False}

def dynamic_array(b,field,stride):
 # Charm/Tiger SchemaTypes.cs DynamicArray<T>:
 #   count @ +0x00, RelativePointer @ +0x08, then AddExtraOffset(0x10).
 # RelativePointer.GetAbsoluteOffset() is pointer_field + signed relative offset.
 if field<0 or field+0x10>len(b):raise ValueError(f'DynamicArray header out of bounds: 0x{field:X}')
 count=i32(b,field); rel=q64(b,field+8)
 if count<0 or count>1_000_000:raise ValueError(f'implausible DynamicArray count {count} at 0x{field:X}')
 start=field+8+rel+0x10 if count else None
 if count and (start is None or start<4 or start+count*stride>len(b)):
  raise ValueError(f'DynamicArray payload out of bounds: field=0x{field:X} count={count} start={start}')
 return {'field_offset':field,'count':count,'relative':rel,'element_start':start,'stride':stride}

def decode_xur_placement(b,xoff):
 # Charm pins D1 SMapDataEntry to 0x90 bytes with EntitySK at +0x00 and
 # ResourcePointer DataResource at +0x88.  For these Xur placements the
 # DataResource pointer resolves directly to class 80802B15 / S152B8080.
 if xoff+0x90>len(b):raise ValueError(f'SMapDataEntry exceeds payload at Xur offset 0x{xoff:X}')
 data_ptr=resource_pointer(b,xoff+0x88)
 if data_ptr.get('class_hash')!=f'{S152_CLASS:08X}':
  raise ValueError(f'Xur DataResource is not S152B8080 at 0x{xoff:X}: {data_ptr}')
 s152=data_ptr['target_offset']
 arr=dynamic_array(b,s152+0x10,8)
 if arr['count'] and u32(b,arr['element_start']-4)!=S4E2A_CLASS:
  raise ValueError(f'S152 array element class marker is not S4E2A8080 at 0x{xoff:X}')
 records=[]
 for i in range(arr['count']):
  o=arr['element_start']+i*8
  records.append({'index':i,'offset':o,'offset_hex':f'0x{o:X}','unk00_tiger_hash':f'{u32(b,o):08X}','type_string_hash':f'{u32(b,o+4):08X}'})
 pairs=[(r['unk00_tiger_hash'],r['type_string_hash']) for r in records]
 return {
  'xur_offset':xoff,'xur_offset_hex':f'0x{xoff:X}',
  'smap_class_expected':f'{SMAP_CLASS:08X}',
  'data_resource_pointer':data_ptr,
  's152_payload_offset':s152,'s152_payload_offset_hex':f'0x{s152:X}',
  's152_array':arr,
  's4e2a_class_marker':f'{u32(b,arr["element_start"]-4):08X}' if arr['count'] else None,
  's4e2a_records':records,
  'exact_expected_xur_config':pairs==EXPECTED_XUR_CONFIG,
 }

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--owner',action='append',required=True);ap.add_argument('--member-catalog',type=Path,action='append',required=True);ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
 cats=load_catalogs(a.member_catalog);arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90);c=RemoteCorpus(arc,cats,a.runtime)
 rows=[];viol=[]
 for raw in a.owner:
  h=norm(raw)
  try:
   m=c.entry_meta(h);b,src=c.payload(h)
   if m is None or b is None:raise ValueError('payload unavailable')
   ref=norm(m.get('reference','0'));is_sd912=ref==SD912
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
    if oo:xh[x]=oo
    if is_sd912:
     for o in oo:placements.append({'entity':x,**decode_xur_placement(b,o)})
   rows.append({'tag_hash':h,'reference':ref,'is_source_pinned_SD912_scripted_entity_table':is_sd912,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'source':src,'xur_entity_hits':xh,'typed_xur_placements':placements,'key_hits':kh,'known_value_hits':vh,'adjacent_key_value_pairs':pairs,'placement_configuration_source_decoded':bool(placements) and all(p['exact_expected_xur_config'] for p in placements),'material_permutation_consumer_semantics_proven':False,'live_material_selection_proven':False})
  except Exception as ex:viol.append(f'{h}:{ex!r}');rows.append({'tag_hash':h,'error':repr(ex)})
 typed=[p for r in rows for p in r.get('typed_xur_placements',[])]
 exact=sum(bool(p.get('exact_expected_xur_config')) for p in typed)
 rep={'schema':'d1_remote_xur_scripted_owner_switch_probe/v3','status':'D1_XUR_PLACEMENT_CONFIGURATION_SOURCE_DECODED' if not viol and typed and exact==len(typed) else ('D1_XUR_SCRIPTED_OWNER_SWITCH_FRONTIER' if not viol else 'D1_XUR_SCRIPTED_OWNER_SWITCH_VIOLATIONS'),'source_schema_chain':{'SD9128080':'scripted entity table containing placement map-data records','SMapDataEntry_06048080':'D1 size 0x90; EntitySK + world metadata + ResourcePointer DataResource at +0x88','S152B8080':'DataResource target; DynamicArray<S4E2A8080> at +0x10','DynamicArray<T>':'count @ +0x00; RelativePointer @ +0x08; element absolute = pointer_field + relative + 0x10','S4E2A8080':'8 bytes: TigerHash Unk00 + StringHash Type'},'expected_xur_configuration_records':[list(x) for x in EXPECTED_XUR_CONFIG],'typed_xur_placement_count':len(typed),'exact_expected_configuration_count':exact,'rows':rows,'violations':viol,'proof':{'placement_configuration_source_decoded':bool(typed) and exact==len(typed) and not viol,'material_permutation_consumer_semantics_proven':False,'descriptor_A_B_evaluation_semantics_proven':False},'gates':{'E6_80C885E6_live_selection_proven':False,'E7_80C885E7_live_selection_proven':False,'E8_80C885E8_live_selection_proven':False},'policy':'The S152/S4E2A placement configuration is source-decoded. Its equality to model-parent switch keys/values is not by itself material-consumer proof. E6/E7/E8 remain fail-closed until the D1 consumer/evaluation path is independently established.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
 print(json.dumps({'status':rep['status'],'typed_xur_placement_count':len(typed),'exact_expected_configuration_count':exact,'proof':rep['proof'],'violations':viol,'gates':rep['gates']},indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
