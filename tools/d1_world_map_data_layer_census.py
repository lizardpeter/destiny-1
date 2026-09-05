#!/usr/bin/env python3
"""Loss-preserving D1 ROI SMapDataTable layer census.

This is the next world layer above baked statics.  It parses every shipped
SMapDataEntry (0x90 bytes in ROI), preserving its entity hash, outer transform,
WorldID and relative ResourcePointer.  Known resource classes are named only from
a pinned external schema and their immediate +0x0C TagHash is reported without
assuming that every unknown class has the same layout.

The tool is generic: repeat --map-data-table for every table owned by a world.
It does not require that an entry be a static map and it never discards unknown
resource classes.
"""
from __future__ import annotations
import argparse, json, math, struct, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5

MAP_DATA_TABLE_CLASS='808009A2'
PINNED_SOURCE='MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af Tiger/Schema/Static/StaticMapData.cs'
KNOWN_RESOURCE_CLASSES={
    '80801AEA': {'name':'SMapDataResource/static_map','target_offset':0x0C,'target_class':'80801AC6'},
    '80801BEA': {'name':'SMapLightResource','target_offset':0x0C,'target_class':None},
    '80801BDA': {'name':'SMapSkyEntResource','target_offset':0x0C,'target_class':None},
    '80801A70': {'name':'SMapDecalsResource','target_offset':0x0C,'target_class':None},
    '80801AF2': {'name':'D1_F21A8080/bytecode_buffer_resource','target_offset':None,'target_class':None},
}

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)
def hx(x): return f'{x:08X}'
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u64(b,o): return struct.unpack_from('<Q',b,o)[0]
def i64(b,o): return struct.unpack_from('<q',b,o)[0]
def f4(b,o): return [float(x) for x in struct.unpack_from('<4f',b,o)]

def dyn(b,off,stride):
    # D1 DynamicArray descriptor: u64 relative pointer at +0, u32 count at +8.
    if off+0x10>len(b): return {'ok':False,'error':'descriptor_oob'}
    rel=i64(b,off); count=u32(b,off+8); absolute=off+rel if rel else 0
    ok=(count==0 and rel==0) or (rel!=0 and absolute>=0 and absolute+count*stride<=len(b))
    return {'ok':ok,'relative':rel,'count':count,'absolute':absolute,'stride':stride,
            'end':absolute+count*stride if rel else absolute}

def target_meta(c,h):
    h=norm(h); m=c.entry_meta(h)
    return {'hash':h,'exists':m is not None,'meta':m}

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--map-data-table',action='append',required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())
    tables=[]; all_rows=[]; violations=[]
    for th0 in a.map_data_table:
        th=norm(th0); meta=c.entry_meta(th); b,src=c.payload(th)
        tr={'map_data_table':th,'meta':meta,'source':src,'entries':[]}
        if not meta or norm(meta.get('reference',''))!=MAP_DATA_TABLE_CLASS:
            tr['error']=f'not {MAP_DATA_TABLE_CLASS}'; violations.append(f'{th}: class mismatch'); tables.append(tr); continue
        if b is None:
            tr['error']='payload unavailable'; violations.append(f'{th}: payload unavailable'); tables.append(tr); continue
        arr=dyn(b,0x08,0x90); tr['payload_bytes']=len(b);tr['entries_array']=arr
        if not arr['ok']:
            tr['error']='entry array bounds failed'; violations.append(f'{th}: array bounds');tables.append(tr);continue
        for i in range(arr['count']):
            o=arr['absolute']+i*0x90; pf=o+0x88
            rot=f4(b,o+0x20); trans=f4(b,o+0x30); entity=hx(u32(b,o)); rel=i64(b,pf)
            row={'map_data_table':th,'index':i,'record_offset':o,'entity_hash':entity,
                 'entity':target_meta(c,entity) if entity!='FFFFFFFF' else None,
                 'rotation':rot,'translation':trans,'world_id':f'{u64(b,o+0x80):016X}',
                 'resource_pointer_field':pf,'resource_relative':rel,'resource_absolute':None,
                 'resource_class':None,'resource_class_name':None,'resource_target':None}
            if not all(math.isfinite(x) for x in rot+trans): row['transform_error']='nonfinite'
            if rel:
                absolute=pf+rel; row['resource_absolute']=absolute
                if absolute<4 or absolute>len(b):
                    row['resource_error']='pointer_oob'
                else:
                    cls=hx(u32(b,absolute-4));row['resource_class']=cls
                    ki=KNOWN_RESOURCE_CLASSES.get(cls);row['resource_class_name']=ki['name'] if ki else None
                    if ki and ki['target_offset'] is not None:
                        to=absolute+ki['target_offset']
                        if to+4<=len(b):
                            tag=hx(u32(b,to));row['resource_target']=target_meta(c,tag)
                            if ki.get('target_class') and row['resource_target']['meta']:
                                row['resource_target']['expected_class']=ki['target_class']
                                row['resource_target']['class_matches']=norm(row['resource_target']['meta'].get('reference',''))==ki['target_class']
                        else: row['resource_error']='known_target_field_oob'
            tr['entries'].append(row);all_rows.append(row)
        tables.append(tr)
    classes=Counter((r['resource_class'] or 'NULL') for r in all_rows)
    entities=[r for r in all_rows if r['entity_hash']!='FFFFFFFF']
    resource_rows=[r for r in all_rows if r['resource_class']]
    class_examples=defaultdict(list)
    for r in resource_rows:
        if len(class_examples[r['resource_class']])<8:
            class_examples[r['resource_class']].append({k:r.get(k) for k in ('map_data_table','index','entity_hash','translation','world_id','resource_target')})
    out={
        'schema_version':1,'status':'D1_WORLD_MAP_DATA_LAYER_CENSUS' if not violations else 'D1_WORLD_MAP_DATA_LAYER_CENSUS_PARTIAL',
        'pinned_source':PINNED_SOURCE,'map_data_table_count':len(tables),'entry_count':len(all_rows),
        'entity_hash_non_null_entries':len(entities),'resource_pointer_non_null_entries':len(resource_rows),
        'resource_class_counts':dict(classes),'known_resource_classes':KNOWN_RESOURCE_CLASSES,
        'resource_class_examples':dict(class_examples),'tables':tables,'violations':violations,
        'policy':'All SMapDataEntry rows are retained. Unknown resource classes remain exact class hashes; only pinned known class layouts receive names/target-field decoding.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','map_data_table_count','entry_count','entity_hash_non_null_entries','resource_pointer_non_null_entries','resource_class_counts','violations')},indent=2))
    return 0 if not violations else 2
if __name__=='__main__': raise SystemExit(main())
