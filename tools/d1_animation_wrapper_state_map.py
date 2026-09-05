#!/usr/bin/env python3
"""Decode the reusable D1 ROI 0x8080222A action-wrapper state map.

Calibrated on the shared first-person weapon wrapper family around
80AA3CC4/80AA3CC7/80AA3CCB.  The parser intentionally keeps the semantics of
nested resource kinds/classes unnamed until they are independently closed.

Byte-proven layout used here:
  +0x08 DynamicArray-like count A
  +0x10 relative pointer -> A rows of (StringHash u32, local row index u32)
  +0x18 DynamicArray-like count B
  +0x20 relative pointer -> B rows, stride 0x10
         each row is a nested dynamic array header
  nested item stride 0x10:
         +0x00 uint64 kind/value
         +0x08 ResourceInTablePointer relative int64
         target resource class is the u32 immediately preceding target

The map can contain aliases: multiple hashes may select the same local row.
No action name is assigned unless an exact lowercase FNV1 preimage is supplied.
"""
from __future__ import annotations
import argparse,json,struct,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader
from d1_fnv1_action_probe import DEFAULTS,fnv1

WRAPPER_REF='8080222A'

def u32(b,o):
    if o<0 or o+4>len(b): raise ValueError(f'u32 OOB 0x{o:X}/0x{len(b):X}')
    return struct.unpack_from('<I',b,o)[0]
def u64(b,o):
    if o<0 or o+8>len(b): raise ValueError(f'u64 OOB 0x{o:X}/0x{len(b):X}')
    return struct.unpack_from('<Q',b,o)[0]
def i64(b,o):
    if o<0 or o+8>len(b): raise ValueError(f'i64 OOB 0x{o:X}/0x{len(b):X}')
    return struct.unpack_from('<q',b,o)[0]
def dyn(b,field):
    count=u32(b,field); rel=i64(b,field+8); data=field+rel+0x18
    if count and not (0<=data<len(b)): raise ValueError(f'dyn at 0x{field:X} -> 0x{data:X} OOB')
    return count,data,rel

def decode_wrapper(payload:bytes,names:list[str]|None=None)->dict:
    names=names or []
    pre={fnv1(x):x for x in names}
    map_count,map_data,map_rel=dyn(payload,0x08)
    row_count,row_data,row_rel=dyn(payload,0x18)
    hash_map=[]
    for i in range(map_count):
        o=map_data+i*8
        h=u32(payload,o); idx=u32(payload,o+4)
        if idx>=row_count: raise ValueError(f'hash map row {i}: local index {idx} >= row count {row_count}')
        hash_map.append({'map_index':i,'offset':o,'state_hash':f'{h:08X}','state_name':pre.get(h),'local_index':idx})
    rows=[]
    for i in range(row_count):
        o=row_data+i*0x10
        count,data,rel=dyn(payload,o)
        items=[]
        for j in range(count):
            q=data+j*0x10
            kind=u64(payload,q)
            ptr_field=q+8
            ptr_rel=i64(payload,ptr_field)
            target=ptr_field+ptr_rel
            if not (4<=target<len(payload)):
                raise ValueError(f'row {i} item {j}: resource target 0x{target:X} OOB')
            cls=u32(payload,target-4)
            prefix=payload[target:min(len(payload),target+64)]
            items.append({'item_index':j,'offset':q,'kind_u64':kind,'resource_pointer_field':ptr_field,
                          'resource_relative':ptr_rel,'resource_target':target,'resource_class':f'{cls:08X}',
                          'resource_prefix64_hex':prefix.hex()})
        rows.append({'local_index':i,'offset':o,'item_count':count,'items_data':data,'items_relative':rel,'items':items})
    aliases={}
    for x in hash_map: aliases.setdefault(x['local_index'],[]).append({'hash':x['state_hash'],'name':x['state_name']})
    for r in rows:r['state_aliases']=aliases.get(r['local_index'],[])
    return {'hash_map':{'count':map_count,'data_offset':map_data,'relative':map_rel,'records':hash_map},
            'state_rows':{'count':row_count,'data_offset':row_data,'relative':row_rel,'records':rows}}

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('pkg',type=Path)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--wrapper-tag',required=True)
    ap.add_argument('--name',action='append',default=[])
    ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args()
    names=[]
    for x in DEFAULTS+a.name:
        x=x.strip().lower()
        if x and x not in names:names.append(x)
    r=EntryReader(a.pkg,a.runtime);by={e['tag_hash'].upper():e for e in r.entries};t=a.wrapper_tag.upper()
    e=by.get(t)
    if not e: raise SystemExit(f'{t} absent')
    if e['reference'].upper()!=WRAPPER_REF: raise SystemExit(f'{t}: reference {e["reference"]} != {WRAPPER_REF}')
    b=r.entry(e['index']);d=decode_wrapper(b,names)
    report={'wrapper':{'tag_hash':t,'entry_index':e['index'],'reference':e['reference'].upper(),'size':len(b)},**d,
            'evidence_policy':'Hash/name pairs are exact FNV1 preimages. Nested kind values and resource classes are serialized exactly but left semantically unnamed.'}
    text=json.dumps(report,indent=2)
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text+'\n');print('wrote',a.output)
    else:print(text)
    known=[x for x in d['hash_map']['records'] if x['state_name']]
    print('known states',json.dumps(known,separators=(',',':')),file=sys.stderr)
    return 0
if __name__=='__main__':raise SystemExit(main())
