#!/usr/bin/env python3
"""Decode exact D1 PS4 SMapDataTable rows through the verified remote catalog.

Pinned D1 ROI layout:
  SMapDataTable / 808009A2
    +0x08 DynamicArray<SMapDataEntry>, stride 0x90
  SMapDataEntry
    +0x00 EntitySK FileHash
    +0x20 Rotation Vector4
    +0x30 Translation Vector4
    +0x80 WorldID u64
    +0x88 ResourcePointer DataResource

The DynamicArray and ResourcePointer math is the same source-pinned layout already
used by the world pipeline. EntitySK FileHashes are resolved through the exact
universal Tiger catalog. Inline DataResource classes are preserved but not assigned
semantics unless an independent parser exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0,str(HERE))

from d1_crota_raid_candidate_probe import LazyExactHashResolver, meta_row, norm
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar

TABLE_CLASS='808009A2'
ENTITY_CLASS='80800734'
STRIDE=0x90
NULLS={'00000000','FFFFFFFF'}
PINNED_SOURCE=(
    'MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
    'Tiger/Schema/Static/StaticMapData.cs; mirrored by repository world-pipeline parsers'
)

def i32(b,o): return struct.unpack_from('<i',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u64(b,o): return struct.unpack_from('<Q',b,o)[0]
def i64(b,o): return struct.unpack_from('<q',b,o)[0]
def f4(b,o): return [float(x) for x in struct.unpack_from('<4f',b,o)]
def hx(v): return f'{v:08X}'

def dyn(b,off,stride):
    if off+0x10>len(b): return {'ok':False,'field_offset':off,'error':'descriptor_oob'}
    count=i32(b,off);unk=u32(b,off+4);rel=i64(b,off+8)
    absolute=off+8+rel+0x10
    end=absolute+max(count,0)*stride
    ok=count>=0 and (count==0 or (absolute>=0 and end<=len(b)))
    return {'ok':ok,'field_offset':off,'count':count,'unknown04':unk,'relative':rel,
            'absolute':absolute,'end':end,'stride':stride,
            **({} if ok else {'error':'array_bounds'})}

def resource_pointer(b,off):
    if off+8>len(b): return {'ok':False,'field_offset':off,'error':'pointer_oob'}
    rel=i64(b,off)
    row={'ok':True,'field_offset':off,'relative':rel,'is_null':rel==0,
         'absolute':None,'resource_class':None}
    if rel==0: return row
    absolute=off+rel;row['absolute']=absolute
    if absolute<4 or absolute>len(b):
        row['ok']=False;row['error']='target_oob';return row
    row['resource_class_offset']=absolute-4
    row['resource_class']=hx(u32(b,absolute-4))
    row['prefix_hex']=b[absolute:min(len(b),absolute+0x40)].hex()
    return row

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--tag-hash',action='append',required=True)
    ap.add_argument('--member-catalog',action='append',type=Path,required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    catalogs=load_catalogs(a.member_catalog)
    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    resolver=LazyExactHashResolver(arc,catalogs,a.runtime)

    tables=[];violations=[]
    for raw in a.tag_hash:
        h=norm(raw);t={'tag_hash':h,'violations':[],'entries':[]}
        try:
            view,e=resolver.locate(h)
            t['package_id']=f'{((int(h,16)-0x80800000)>>13)&0x7ff:04X}'
            t['logical_view']=view.view.name;t['entry']=meta_row(e)
            if e['reference'].upper()!=TABLE_CLASS:
                raise ValueError(f'{h}: expected {TABLE_CLASS}, got {e["reference"].upper()}')
            b=view.entry(e['index']);t['payload_size']=len(b);t['payload_sha256']=hashlib.sha256(b).hexdigest()
            if len(b)<0x18: raise ValueError(f'{h}: payload shorter than 0x18')
            arr=dyn(b,0x08,STRIDE);t['data_entries_array']=arr
            if not arr['ok']: raise ValueError(f'{h}: invalid SMapDataEntry array {arr}')
            for i in range(arr['count']):
                o=arr['absolute']+i*STRIDE
                ent=hx(u32(b,o));rot=f4(b,o+0x20);tr=f4(b,o+0x30);wid=u64(b,o+0x80);dr=resource_pointer(b,o+0x88)
                row={'index':i,'record_offset':o,'entity_hash':ent,'rotation':rot,'translation':tr,
                     'transform_finite':all(math.isfinite(x) for x in rot+tr),
                     'world_id':wid,'world_id_hex':f'{wid:016X}','data_resource':dr}
                if ent not in NULLS:
                    try:
                        _ev,ee=resolver.locate(ent);row['entity_entry']=meta_row(ee)
                        row['entity_class_matches']=ee['reference'].upper()==ENTITY_CLASS
                    except Exception as ex:
                        row['entity_resolution_error']=repr(ex);row['entity_class_matches']=False
                else:
                    row['entity_class_matches']=None
                if not row['transform_finite']:
                    t['violations'].append(f'entry[{i}]:nonfinite_transform')
                if not dr['ok']:
                    t['violations'].append(f'entry[{i}]:data_resource_pointer_invalid')
                if ent not in NULLS and not row.get('entity_class_matches'):
                    t['violations'].append(f'entry[{i}]:entity_not_s_entity:{ent}')
                t['entries'].append(row)
            t['entry_count']=len(t['entries'])
            t['unique_entity_hashes']=sorted({x['entity_hash'] for x in t['entries'] if x['entity_hash'] not in NULLS})
            t['unique_data_resource_classes']=sorted({x['data_resource']['resource_class'] for x in t['entries'] if x['data_resource'].get('resource_class')})
            if t['violations']:
                violations.extend({'tag_hash':h,'error':x} for x in t['violations'])
        except Exception as ex:
            msg=repr(ex);t['violations'].append(msg);violations.append({'tag_hash':h,'error':msg})
        tables.append(t)

    out={'schema':'d1_remote_exact_map_data_table_probe/v1','status':'D1_EXACT_MAP_DATA_TABLE_PROBE' if not violations else 'D1_EXACT_MAP_DATA_TABLE_PROBE_WITH_VIOLATIONS',
         'pinned_source':PINNED_SOURCE,'table_class':TABLE_CLASS,'entry_stride':STRIDE,'tables':tables,
         'violation_count':len(violations),'violations':violations,
         'policy':'Every placement row comes from the pinned SMapDataTable/SMapDataEntry serialization. Entity semantics are not inferred; only exact catalog class validation is performed. Inline DataResource classes are preserved without semantic promotion.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    for t in tables:
        print('TABLE',t['tag_hash'],'COUNT',t.get('entry_count'),'ENTITIES',t.get('unique_entity_hashes'),
              'DATA_CLASSES',t.get('unique_data_resource_classes'),'VIOLATIONS',t.get('violations'))
        for r in t.get('entries',[]):
            print(' ROW',r['index'],'OFF',hex(r['record_offset']),'ENTITY',r['entity_hash'],
                  'CLASS',(r.get('entity_entry') or {}).get('reference'),'WORLD',r['world_id_hex'],
                  'T',r['translation'],'DR',r['data_resource'].get('resource_class'),
                  'DR_OFF',r['data_resource'].get('absolute'))
    return 0 if not violations else 2

if __name__=='__main__': raise SystemExit(main())
