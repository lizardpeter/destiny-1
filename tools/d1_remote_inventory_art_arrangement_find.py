#!/usr/bin/env python3
"""Reverse D1 ROI gearArtArrangementIndex -> inventory item hashes.

Input is a decoded 80A5FFBE inventory-item map.  Each map row supplies the API
InventoryItemHash and the FileHash of the corresponding D1 inventory item
definition.  For one investment-assets package family this tool opens the
logical patched package remotely, reads only referenced item definitions, and
parses the D1 equippingBlock ResourcePointer at item +0x60.

Charm's retail D1 schema establishes:
  InventoryItem (06188080, size 0x9c)
    +0x60 ResourcePointer -> equippingBlock (20108080, size 0x68)
  equippingBlock +0x00 DynamicArray<1A108080>
    row: int16 classHash, int16 gearArtArrangementIndex
  equippingBlock +0x60 int16 weaponSandboxPatternIndex

No item-name or weapon-type inference is performed here.
"""
from __future__ import annotations
import argparse, json, struct, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_investment_arrangement_probe import dyn_header, filehash_pkg_index
from d1_remote_investment_parent_probe import parse_member, RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar

D1_EQUIPPING_BLOCK=0x80801020


def i64(b,o): return struct.unpack_from('<q',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def i16(b,o): return struct.unpack_from('<h',b,o)[0]


def resource_ptr_target(b:bytes,field:int):
    if field+8>len(b): return None,None
    rel=i64(b,field)
    if rel==0: return None,None
    target=field+rel
    if target<4 or target>len(b): return None,None
    return target,u32(b,target-4)


def parse_item(b:bytes)->dict:
    if len(b)<0x68: raise ValueError(f'item shorter than equipping pointer: {len(b)}')
    target,cls=resource_ptr_target(b,0x60)
    out={'equipping_block_target':target,'equipping_block_class':f'{cls:08X}' if cls is not None else None}
    if target is None or cls!=D1_EQUIPPING_BLOCK:
        return out
    count,data=dyn_header(b,target+0x00)
    arrangements=[]
    for i in range(count):
        o=data+i*4
        if o+4>len(b): raise ValueError('arrangement row out of bounds')
        arrangements.append({'class_hash':i16(b,o),'art_arrangement_index':i16(b,o+2)})
    out['arrangements']=arrangements
    if target+0x62<=len(b): out['weapon_pattern_index']=i16(b,target+0x60)
    return out


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('inventory_map_json',type=Path)
    ap.add_argument('--package-id',type=lambda x:int(x,0),required=True)
    ap.add_argument('--target-arrangement',action='append',type=int,required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--member',action='append',type=parse_member,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    src=json.loads(a.inventory_map_json.read_text())
    rows=src['rows'] if isinstance(src,dict) else src
    candidates=[r for r in rows if int(r['item_package_id'])==a.package_id]
    targets=set(a.target_arrangement)

    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    siblings={m.patch_id:m for m in a.member}
    if any(m.pkg_id!=a.package_id for m in a.member): raise SystemExit('all members must match package id')
    rr=RemoteLogicalPackage(arc,siblings,a.runtime)

    matches=[]; errors=[]; parsed=0; equipping=0
    for n,r in enumerate(candidates,1):
        fh=int(r['item_file_hash'],16); pkg,idx=filehash_pkg_index(fh)
        try:
            if pkg!=a.package_id: raise ValueError('candidate package mismatch')
            if idx>=len(rr.entries): raise ValueError('file index beyond entry table')
            e=rr.entries[idx]
            if e['tag_hash'].upper()!=r['item_file_hash'].upper():
                raise ValueError(f"entry tag mismatch {e['tag_hash']}")
            b=rr.entry(idx); parsed+=1
            p=parse_item(b)
            if p.get('equipping_block_class')==f'{D1_EQUIPPING_BLOCK:08X}': equipping+=1
            arts=[x['art_arrangement_index'] for x in p.get('arrangements',[])]
            hit=sorted(targets.intersection(arts))
            if hit:
                row={**r,'entry_reference':e['reference'].upper(),'entry_size':len(b),**p,'matched_arrangements':hit}
                matches.append(row)
                print('INVENTORY_ARRANGEMENT_MATCH',json.dumps(row,separators=(',',':')),flush=True)
        except Exception as ex:
            errors.append({**r,'error':repr(ex)})
        if n%500==0:
            print(f'{a.package_id:04X}: {n}/{len(candidates)} candidate items parsed={parsed} matches={len(matches)} blocks={len(rr.block_cache)}',flush=True)

    rep={
      'package_id':a.package_id,'logical_view':rr.view.name,'target_arrangements':sorted(targets),
      'candidate_item_count':len(candidates),'parsed_item_count':parsed,'equipping_block_count':equipping,
      'match_count':len(matches),'matches':matches,'remote_blocks_read':len(rr.block_cache),
      'error_count':len(errors),'errors':errors[:200],
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:v for k,v in rep.items() if k not in ('matches','errors')},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
