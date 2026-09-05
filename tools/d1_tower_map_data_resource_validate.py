#!/usr/bin/env python3
"""Validate the outer D1 ROI map-data-entry -> static-map resource chain.

Candidate layout is source-derived from pinned Charm commit 50d36ee..., then checked
against shipped bytes. D1 SMapDataTable has 0x90 SMapDataEntry records; each entry has
Rotation +0x20, Translation +0x30, WorldID +0x80 and ResourcePointer +0x88. Charm's
ResourcePointer is a signed 64-bit relative pointer based at the pointer field; the
resource class hash is four bytes immediately before the target. For the static-map
resource candidate we require:
  resource class 80801AEA (Charm EA1A8080 / SMapDataResource)
  +0x0C -> 80801AC6 SStaticMapParent TagHash
  parent +0x08 -> 808008B4 SStaticMapData TagHash
No ownership is promoted merely from class/name affinity; every hop is checked.
"""
from __future__ import annotations
import argparse,json,math,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_tower_map_schema_validate import Corpus,dyn

MAP_DATA_TABLE='808009A2'
MAP_DATA_RESOURCE='80801AEA'
STATIC_MAP_PARENT='80801AC6'
STATIC_MAP_DATA='808008B4'
PINNED_SOURCE='MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af Tiger/Schema/Static/StaticMapData.cs + Tiger/SchemaTypes.cs'

def hx(v): return f'{v:08X}'
def norm(s): return str(s).upper().removeprefix('0X').zfill(8)
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u64(b,o): return struct.unpack_from('<Q',b,o)[0]
def i64(b,o): return struct.unpack_from('<q',b,o)[0]
def f4(b,o): return [float(x) for x in struct.unpack_from('<4f',b,o)]

def target_meta(c,h,expected=None):
    m=c.entry_meta(h)
    return {'hash':norm(h),'exists':m is not None,'meta':m,'expected_reference':expected,
            'reference_matches':bool(m and (expected is None or m['reference']==expected))}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--map-data-table',required=True)
    ap.add_argument('--target-static-map',default=None)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args(); tableh=norm(a.map_data_table); target=norm(a.target_static_map) if a.target_static_map else None
    c=Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())
    meta=c.entry_meta(tableh)
    if not meta or meta['reference']!=MAP_DATA_TABLE:
        raise SystemExit(f'{tableh} is not a corpus SMapDataTable/{MAP_DATA_TABLE}: {meta}')
    b,src=c.payload(tableh)
    if b is None: raise SystemExit(f'{tableh} payload unavailable')
    arr=dyn(b,0x08,0x90)
    rep={'evidence_status':'SOURCE_DERIVED_OUTER_MAP_CHAIN_UNDER_BINARY_VALIDATION','pinned_source':PINNED_SOURCE,
         'map_data_table':tableh,'map_data_table_source':src,'payload_size':len(b),'entries_array':arr,
         'target_static_map':target,'entries':[],'violations':[]}
    if not arr['ok']:
        rep['violations'].append('SMapDataEntry dynamic array bounds failed')
    else:
        for i in range(arr['count']):
            o=arr['absolute']+i*0x90
            rot=f4(b,o+0x20); tr=f4(b,o+0x30); rel=i64(b,o+0x88); ptr_field=o+0x88
            row={'index':i,'record_offset':o,'entity_hash':hx(u32(b,o)),'rotation':rot,'translation':tr,
                 'world_id':f'{u64(b,o+0x80):016X}','resource_pointer_field_offset':ptr_field,
                 'resource_relative_offset':rel,'resource_absolute_offset':None,'resource_class':None,
                 'resource_chain_ok':False}
            if not all(math.isfinite(x) for x in rot+tr):
                row['error']='non-finite outer transform'; rep['entries'].append(row); continue
            if rel==0:
                row['resource_pointer_null']=True; rep['entries'].append(row); continue
            absolute=ptr_field+rel; row['resource_absolute_offset']=absolute
            if absolute<4 or absolute>len(b):
                row['error']='resource pointer target out of bounds'; rep['entries'].append(row); continue
            cls=hx(u32(b,absolute-4)); row['resource_class']=cls; row['resource_class_offset']=absolute-4
            if cls!=MAP_DATA_RESOURCE:
                row['error']=f'resource class {cls} != {MAP_DATA_RESOURCE}'; rep['entries'].append(row); continue
            if absolute+0x10>len(b):
                row['error']='SMapDataResource field frontier out of bounds'; rep['entries'].append(row); continue
            parent=hx(u32(b,absolute+0x0C)); row['static_map_parent']=target_meta(c,parent,STATIC_MAP_PARENT)
            if not row['static_map_parent']['reference_matches']:
                row['error']='StaticMapParent target missing/class mismatch'; rep['entries'].append(row); continue
            pb,psrc=c.payload(parent); row['static_map_parent_payload_source']=psrc
            if pb is None or len(pb)<0x0C:
                row['error']='StaticMapParent payload unavailable/short'; rep['entries'].append(row); continue
            sm=hx(u32(pb,0x08)); row['static_map']=target_meta(c,sm,STATIC_MAP_DATA)
            if not row['static_map']['reference_matches']:
                row['error']='StaticMap target missing/class mismatch'; rep['entries'].append(row); continue
            row['resource_chain_ok']=True
            row['matches_requested_static_map']=target is not None and sm==target
            rep['entries'].append(row)
    good=[x for x in rep['entries'] if x.get('resource_chain_ok')]
    requested=[x for x in good if x.get('matches_requested_static_map')]
    from collections import Counter
    rep['summary']={'entry_count':arr.get('count') if arr['ok'] else None,'resource_chain_ok':len(good),
                    'resource_classes':dict(Counter(x.get('resource_class') or 'NULL' for x in rep['entries'])),
                    'static_maps':dict(Counter(x.get('static_map',{}).get('hash') for x in good)),
                    'requested_static_map_matches':len(requested)}
    if target:
        if len(requested)!=1: rep['violations'].append(f'requested static map {target} matched {len(requested)} entries, expected exactly one')
        else:
            x=requested[0]
            rep['validated_target_entry']={k:x[k] for k in ('index','record_offset','rotation','translation','world_id','resource_pointer_field_offset','resource_relative_offset','resource_absolute_offset','resource_class','static_map_parent')}
            rep['validated_target_entry']['static_map']=x['static_map']
    rep['ok']=arr['ok'] and not rep['violations']
    if rep['ok'] and target: rep['evidence_status']='CONFIRMED_BINARY_OUTER_MAP_CHAIN'
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({'evidence_status':rep['evidence_status'],'map_data_table':tableh,'target_static_map':target,
                      'summary':rep['summary'],'validated_target_entry':rep.get('validated_target_entry'),
                      'violations':rep['violations'],'ok':rep['ok']},indent=2))
    return 0 if rep['ok'] else 2
if __name__=='__main__': raise SystemExit(main())
