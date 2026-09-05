#!/usr/bin/env python3
"""Probe D1 ROI texture plates through verified remote logical package views.

This is the cross-package form of d1_texture_plate_probe.py. Texture-plate
headers, plate records, and their source textures are FileHashes and therefore
may belong to different package families. Every lookup is routed by the encoded
Tiger package/index through caller-supplied verified member catalogs.

No plate or texture ownership is inferred from package locality.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader
from d1_split_tar_extract import SplitHttpTar
from d1_texture_plate_probe import HEADER_CLASS, PLATE_CLASS, TRANSFORM_SIZE, dynamic_array, ceil_pow2, filehash_package_id, filehash_entry_index


def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def i32(b,o): return struct.unpack_from('<i',b,o)[0]


def parse_plate_remote(r, by_hash:dict[str,dict], tag_hash:str)->dict:
    tag_hash=tag_hash.upper()
    row={'tag_hash':tag_hash,'filehash_package_id':filehash_package_id(tag_hash),'filehash_entry_index':filehash_entry_index(tag_hash)}
    e=by_hash.get(tag_hash)
    if e is None:
        return {**row,'present_in_catalog_views':False}
    row.update({'present_in_catalog_views':True,'synthetic_entry_index':e['index'],'source_package_id':e.get('_source_package_id'),
                'source_file_index':e.get('_source_file_index'),'entry_type':e['type'],'entry_subtype':e['subtype'],
                'class_hash':e['reference'].upper(),'declared_file_size':e['file_size'],'available':r.available(e['index'])})
    if not row['available']: return row
    b=r.entry(e['index']);row['actual_file_size']=len(b)
    if e['reference'].upper()!=PLATE_CLASS: row['warning']=f'expected texture plate class {PLATE_CLASS}'
    arr=dynamic_array(b,0x10,TRANSFORM_SIZE);row['plate_transforms']=arr
    transforms=[];max_dim=0
    if not arr.get('error'):
        for i in range(arr['count']):
            o=arr['data_offset']+i*TRANSFORM_SIZE
            texture=f'{u32(b,o):08X}';tx,ty=i32(b,o+4),i32(b,o+8);sx,sy=i32(b,o+0xC),i32(b,o+0x10)
            max_dim=max(max_dim,tx+sx,ty+sy)
            te=by_hash.get(texture)
            transforms.append({'index':i,'offset':o,'texture':texture,
                'texture_filehash_package_id':filehash_package_id(texture),'texture_filehash_entry_index':filehash_entry_index(texture),
                'translation':[tx,ty],'scale':[sx,sy],
                'texture_present_in_catalog_views':te is not None,
                'texture_entry_type':te.get('type') if te else None,'texture_entry_subtype':te.get('subtype') if te else None,
                'texture_entry_reference':te.get('reference') if te else None,
                'texture_source_package_id':te.get('_source_package_id') if te else None})
    row['transforms']=transforms;row['plate_dimension_source_max']=max_dim;row['plate_dimension_pow2']=ceil_pow2(max_dim)
    return row


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--header-tag',action='append',required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    catalogs=load_catalogs(a.member_catalog);base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    views={pkg:RemoteLogicalPackage(arc,fam,a.runtime) for pkg,fam in sorted(catalogs.items())}
    r=MultiPackageReader(views);by={e['tag_hash'].upper():e for e in r.entries}

    headers=[];all_textures=[];errors=[]
    for raw in a.header_tag:
        h=raw.upper().removeprefix('0X').zfill(8);e=by.get(h)
        rec={'tag_hash':h,'filehash_package_id':filehash_package_id(h),'filehash_entry_index':filehash_entry_index(h)}
        try:
            if e is None: raise KeyError(f'{h}: header absent from supplied catalog views')
            if not r.available(e['index']): raise RuntimeError(f'{h}: header unavailable')
            b=r.entry(e['index'])
            if len(b)<0x30: raise ValueError(f'{h}: short header {len(b)}')
            rec.update({'synthetic_entry_index':e['index'],'source_package_id':e.get('_source_package_id'),
                        'source_file_index':e.get('_source_file_index'),'class_hash':e['reference'].upper(),
                        'declared_file_size':e['file_size'],'actual_file_size':len(b),'file_size_field':struct.unpack_from('<Q',b,0)[0],
                        'albedo_plate':f'{u32(b,0x24):08X}','normal_plate':f'{u32(b,0x28):08X}','gstack_plate':f'{u32(b,0x2C):08X}'})
            if e['reference'].upper()!=HEADER_CLASS: rec['warning']=f'expected texture-plate header class {HEADER_CLASS}'
            plates={role:parse_plate_remote(r,by,tag) for role,tag in (
                ('albedo',rec['albedo_plate']),('normal',rec['normal_plate']),('gstack',rec['gstack_plate']))}
            rec['plates']=plates
            tex=[]
            for p in plates.values():
                for t in p.get('transforms',[]):
                    if t['texture'] not in tex: tex.append(t['texture'])
                    if t['texture'] not in all_textures: all_textures.append(t['texture'])
            rec['source_texture_hashes']=tex
        except Exception as ex:
            rec['error']=repr(ex);errors.append({'header_tag':h,'error':repr(ex)})
        headers.append(rec)

    report={'schema':'d1_remote_texture_plate_probe/v1','header_count':len(headers),'headers':headers,
            'unique_source_texture_count':len(all_textures),'source_texture_hashes':all_textures,'errors':errors,
            'catalog_package_ids':[f'{x:04X}' for x in sorted(catalogs)],
            'policy':'Header, plate and source-texture FileHashes are routed only through their encoded Tiger package/index across verified logical package catalogs.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('headers','errors')},indent=2))
    for h in headers:
        print('\nHEADER',h['tag_hash'],'pkg',f"{h.get('source_package_id',-1):04X}" if h.get('source_package_id') is not None else None,
              'plates',h.get('albedo_plate'),h.get('normal_plate'),h.get('gstack_plate'),'textures',len(h.get('source_texture_hashes',[])))
        for role,p in (h.get('plates') or {}).items():
            print(' ',role,p.get('tag_hash'),'dim',p.get('plate_dimension_pow2'),'placements',len(p.get('transforms',[])))
    if errors: raise SystemExit(f'{len(errors)} texture-plate header(s) failed')
    missing=[t for h in headers for p in (h.get('plates') or {}).values() for t in p.get('transforms',[]) if not t.get('texture_present_in_catalog_views')]
    if missing: raise SystemExit(f'{len(missing)} source texture reference(s) are outside supplied catalog views')
    return 0

if __name__=='__main__': raise SystemExit(main())
