#!/usr/bin/env python3
"""Decode D1 ROI inventory equipping blocks remotely.

Input is a decoded 80A5FFBE inventory-item map. Each map row supplies the API
InventoryItemHash and the FileHash of the corresponding D1 inventory item
definition. For one investment-assets package family this tool opens the
logical patched package remotely, reads only referenced item definitions, and
parses the D1 equippingBlock ResourcePointer at item +0x60.

Charm's retail D1 schema establishes:
  InventoryItem (06188080, size 0x9c)
    +0x60 ResourcePointer -> equippingBlock (20108080, size 0x68)
    +0x78 InventoryItemHash
  equippingBlock +0x00 DynamicArray<1A108080>
    row: int16 classHash, int16 gearArtArrangementIndex
  equippingBlock +0x20 DynamicArray<1C108080> LockedDyes
  equippingBlock +0x30 DynamicArray<1C108080> DefaultDyes
  equippingBlock +0x50 DynamicArray<1C108080> CustomDyes
    dye row: int16 ChannelIndex, int16 DyeIndex
  equippingBlock +0x60 int16 weaponSandboxPatternIndex

With one or more --target-arrangement values this retains the historical
reverse-search behavior. With no target-arrangement arguments it performs a
full census and emits every successfully decoded inventory item in the package
family, which is the bulk-ripper mode.

No item-name, dye-channel, or weapon-type inference is performed here. Dye
indices remain serialized indices until separately resolved through the retail
D1 dye-channel / ArtDyeReference Investment tables.
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


def parse_dye_array(b:bytes,field:int)->list[dict]:
    count,data=dyn_header(b,field)
    rows=[]
    for i in range(count):
        o=data+i*4
        if o+4>len(b): raise ValueError(f'dye row {i} out of bounds for array at 0x{field:X}')
        rows.append({'channel_index':i16(b,o),'dye_index':i16(b,o+2)})
    return rows


def parse_item(b:bytes)->dict:
    if len(b)<0x7c: raise ValueError(f'item shorter than D1 inventory hash field: {len(b)}')
    target,cls=resource_ptr_target(b,0x60)
    out={
      'serialized_inventory_item_hash':f'{u32(b,0x78):08X}',
      'equipping_block_target':target,
      'equipping_block_class':f'{cls:08X}' if cls is not None else None,
    }
    if target is None or cls!=D1_EQUIPPING_BLOCK:
        return out
    count,data=dyn_header(b,target+0x00)
    arrangements=[]
    for i in range(count):
        o=data+i*4
        if o+4>len(b): raise ValueError('arrangement row out of bounds')
        arrangements.append({'class_hash':i16(b,o),'art_arrangement_index':i16(b,o+2)})
    out['arrangements']=arrangements
    out['locked_dyes']=parse_dye_array(b,target+0x20)
    out['default_dyes']=parse_dye_array(b,target+0x30)
    out['custom_dyes']=parse_dye_array(b,target+0x50)
    if target+0x62<=len(b): out['weapon_pattern_index']=i16(b,target+0x60)
    return out


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('inventory_map_json',type=Path)
    ap.add_argument('--package-id',type=lambda x:int(x,0),required=True)
    ap.add_argument('--target-arrangement',action='append',type=int,default=[],
                    help='optional art arrangement filter; repeatable. Omit for full package-family census.')
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
    full_census=not targets

    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    siblings={m.patch_id:m for m in a.member}
    if any(m.pkg_id!=a.package_id for m in a.member): raise SystemExit('all members must match package id')
    rr=RemoteLogicalPackage(arc,siblings,a.runtime)

    matches=[]; errors=[]; parsed=0; equipping=0
    arrangement_item_count=0; weapon_pattern_item_count=0; dye_item_count=0
    arrangement_counts={}; pattern_counts={}; dye_row_counts={'locked':0,'default':0,'custom':0}
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
            if p['serialized_inventory_item_hash']!=r['inventory_item_hash'].upper():
                raise ValueError(
                    f"serialized InventoryItemHash {p['serialized_inventory_item_hash']} != map {r['inventory_item_hash']}"
                )
            if p.get('equipping_block_class')==f'{D1_EQUIPPING_BLOCK:08X}': equipping+=1
            arts=[x['art_arrangement_index'] for x in p.get('arrangements',[]) if x['art_arrangement_index']>=0]
            if arts:
                arrangement_item_count+=1
                for art in arts: arrangement_counts[str(art)]=arrangement_counts.get(str(art),0)+1
            dye_rows=sum((p.get(f'{kind}_dyes',[]) for kind in ('locked','default','custom')),[])
            if dye_rows: dye_item_count+=1
            for kind in ('locked','default','custom'):
                dye_row_counts[kind]+=len(p.get(f'{kind}_dyes',[]))
            pat=p.get('weapon_pattern_index')
            if isinstance(pat,int) and pat>=0:
                weapon_pattern_item_count+=1
                pattern_counts[str(pat)]=pattern_counts.get(str(pat),0)+1
            hit=sorted(targets.intersection(arts)) if targets else arts
            if full_census or hit:
                row={**r,'entry_reference':e['reference'].upper(),'entry_size':len(b),**p,'matched_arrangements':hit}
                matches.append(row)
                if not full_census:
                    print('INVENTORY_ARRANGEMENT_MATCH',json.dumps(row,separators=(',',':')),flush=True)
        except Exception as ex:
            errors.append({**r,'error':repr(ex)})
        if n%500==0:
            print(f'{a.package_id:04X}: {n}/{len(candidates)} candidate items parsed={parsed} emitted={len(matches)} blocks={len(rr.block_cache)}',flush=True)

    rep={
      'schema':'d1_remote_inventory_art_arrangement_find/v2',
      'package_id':a.package_id,'logical_view':rr.view.name,'full_census':full_census,
      'target_arrangements':sorted(targets),'candidate_item_count':len(candidates),'parsed_item_count':parsed,
      'equipping_block_count':equipping,'arrangement_item_count':arrangement_item_count,
      'dye_item_count':dye_item_count,'dye_row_counts':dye_row_counts,
      'weapon_pattern_item_count':weapon_pattern_item_count,'emitted_item_count':len(matches),
      'match_count':len(matches),'matches':matches,'arrangement_counts':arrangement_counts,
      'weapon_pattern_counts':pattern_counts,'remote_blocks_read':len(rr.block_cache),
      'error_count':len(errors),'errors':errors[:200],
      'evidence_policy':'Equipping block, art arrangement indices, serialized dye ChannelIndex/DyeIndex pairs, and weapon pattern index are parsed directly from each retail inventory definition. Dye indices are not semantically inferred.',
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:v for k,v in rep.items() if k not in ('matches','errors','arrangement_counts','weapon_pattern_counts')},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
