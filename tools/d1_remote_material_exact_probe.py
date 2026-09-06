#!/usr/bin/env python3
"""Decode exact D1 PS4 SMaterial_ROI resources from verified remote package catalogs.

This is an identity-preserving remote counterpart to d1_material_decode.py.  The
requested material FileHash itself selects its package/index.  No neighboring
material, texture-name inference, visual similarity, or package-local fallback is
allowed.  Shader identities, texture/sampler arrays, TFX bytecode and constant
container references are emitted exactly as serialized.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_investment_arrangement_probe import filehash_pkg_index
from d1_material_decode import PS4_MATERIAL_CLASS, parse_material
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar


def norm(x: str) -> str:
    x=x.upper().removeprefix('0X').zfill(8); int(x,16); return x


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--tag-hash',action='append',required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    wanted=[]
    for raw in a.tag_hash:
        h=norm(raw)
        if h not in wanted: wanted.append(h)
    catalogs=load_catalogs(a.member_catalog)
    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    views={}
    rows=[];errors=[]
    for h in wanted:
        pkg,idx=filehash_pkg_index(int(h,16))
        row={'tag_hash':h,'package_id':f'{pkg:04X}','file_index':idx}
        try:
            if pkg not in catalogs: raise KeyError(f'package {pkg:04X} absent from verified catalogs')
            if pkg not in views: views[pkg]=RemoteLogicalPackage(arc,catalogs[pkg],a.runtime)
            v=views[pkg]
            if idx>=len(v.entries): raise IndexError(f'index {idx} outside {len(v.entries)} entries')
            e=v.entries[idx]
            if e['tag_hash'].upper()!=h: raise ValueError(f'logical tag mismatch {e["tag_hash"]}')
            row['entry']={k:e[k] for k in ('index','reference','type','subtype','file_size','tag_hash')}
            if e['reference'].upper()!=PS4_MATERIAL_CLASS:
                raise ValueError(f'{h}: class {e["reference"]}, expected {PS4_MATERIAL_CLASS}')
            b=v.entry(idx)
            d=parse_material(b,'PS4')
            row.update(d)
            row['ps_texture_tags']=[x['texture'].upper() for x in d['ps_textures']['items']]
            row['vs_texture_tags']=[x['texture'].upper() for x in d['vs_textures']['items']]
            row['resolved']=True
            print('MATERIAL',h,'VS',d['vertex_shader'],'PS',d['pixel_shader'],'VS_TEX',row['vs_texture_tags'],'PS_TEX',row['ps_texture_tags'],flush=True)
        except Exception as ex:
            row['resolved']=False;row['error']=repr(ex);errors.append(h)
            print('ERROR',h,repr(ex),flush=True)
        rows.append(row)

    alltex=[]
    for r in rows:
        if not r.get('resolved'): continue
        for h in r['vs_texture_tags']+r['ps_texture_tags']:
            if h not in ('00000000','FFFFFFFF') and h not in alltex: alltex.append(h)
    rep={
        'schema':'d1_remote_material_exact_probe/v1',
        'requested_materials':wanted,
        'resolved_count':sum(bool(x.get('resolved')) for x in rows),
        'error_count':len(errors),
        'errors':errors,
        'materials':rows,
        'referenced_texture_tags':alltex,
        'catalog_package_ids':[f'{x:04X}' for x in sorted(catalogs)],
        'policy':'Requested FileHash selects exact PS4 SMaterial_ROI. Serialized shader/texture/sampler/TFX/constant references only; no visual or neighboring-material substitution.'
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    if errors: raise SystemExit(f'{len(errors)} requested materials failed exact decode')
    return 0


if __name__=='__main__': raise SystemExit(main())
