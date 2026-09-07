#!/usr/bin/env python3
"""Resolve source-proven D1 PS4 EntityResource render-parent contexts remotely.

This is the generic counterpart to the Guardian-specific context probe.  Given one
or more exact outer EntityResource FileHashes it follows only the standard D1
model-parent path already source-closed in d1_render_owner_probe:

  outer class 0x80800861
    +0x10 ResourcePointer -> class 0x80801A80
    +0x18 ResourcePointer -> class 0x80801A9C
      -> embedded model at +0x15C
      -> TexturePlatesROI at +0x1A8
      -> ExternalMaterialsMap at +0x230
      -> ExternalMaterials at +0x270

The tool is deliberately content-agnostic: NPCs, Guardians, enemies, weapons, or
other entity families may reuse it whenever they use this proven parent layout.
No material choice is inferred beyond the exact serialized map/bank contents.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_render_owner_probe import ENTITY_RESOURCE_CLASS,parse_parent_resource
from d1_split_tar_extract import SplitHttpTar


def norm(x:str)->str:
    h=str(x).upper().removeprefix('0X').zfill(8)
    if len(h)!=8: raise ValueError(x)
    int(h,16);return h


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--entity-resource',action='append',required=True)
    ap.add_argument('--expected-model')
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    tags=list(dict.fromkeys(norm(x) for x in a.entity_resource)); expected=norm(a.expected_model) if a.expected_model else None
    catalogs=load_catalogs(a.member_catalog)
    needed=sorted({filehash_pkg_index(int(h,16))[0] for h in tags})
    missing=[p for p in needed if p not in catalogs]
    if missing: raise SystemExit('missing verified catalogs: '+','.join(f'{p:04X}' for p in missing))
    base=a.base_url.rstrip('/');arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    views={p:RemoteLogicalPackage(arc,catalogs[p],a.runtime) for p in needed}
    rows=[];errors=[]
    for h in tags:
        pkg,idx=filehash_pkg_index(int(h,16));v=views[pkg]
        rec={'entity_resource_hash':h,'package_id':f'{pkg:04X}','entry_index':idx}
        try:
            if not 0<=idx<len(v.entries): raise IndexError(f'index {idx} outside {pkg:04X}')
            e=v.entries[idx]; rec['entry']={'tag_hash':e['tag_hash'].upper(),'reference':e['reference'].upper(),'type':e['type'],'subtype':e['subtype'],'file_size':e['file_size']}
            if e['tag_hash'].upper()!=h: raise ValueError(f'tag mismatch {e["tag_hash"]}')
            if e['reference'].upper()!=ENTITY_RESOURCE_CLASS: raise ValueError(f'expected {ENTITY_RESOURCE_CLASS}, got {e["reference"]}')
            parent=parse_parent_resource(v.entry(idx))
            if parent is None: raise ValueError('standard D1 model parent absent')
            if parent.get('error'): raise ValueError(parent['error'])
            if expected and parent.get('embedded_model_tag_hash')!=expected:
                raise ValueError(f'embedded model {parent.get("embedded_model_tag_hash")} != expected {expected}')
            rec['render_parent']=parent
        except Exception as ex:
            rec['error']=repr(ex);errors.append({'entity_resource_hash':h,'error':repr(ex)})
        rows.append(rec)
    rep={'schema':'d1_remote_render_parent_context_probe/v1','entity_resource_count':len(rows),'expected_model':expected,
         'needed_package_ids':[f'{p:04X}' for p in needed],'rows':rows,'error_count':len(errors),'errors':errors,
         'policy':'Only the source-proven D1 80800861 -> 80801A80/80801A9C model-parent path is decoded. Complete external material map/bank serialization is preserved; no identity, variant, or first-material choice is promoted without separate evidence.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print('RENDER_PARENTS',len(rows),'ERRORS',len(errors))
    for r in rows:
        p=r.get('render_parent') or {}
        print('RESOURCE',r['entity_resource_hash'],'MODEL',p.get('embedded_model_tag_hash'),'PLATES',len(p.get('texture_plates_roi_entries') or []),'MAP',len(p.get('external_materials_map_entries') or []),'MATERIALS',len(p.get('external_material_tag_hashes') or []))
        print(' MAP_ROWS',p.get('external_materials_map_entries'))
        print(' MATERIAL_BANK',p.get('external_material_tag_hashes'))
    return 0 if not errors else 2

if __name__=='__main__':raise SystemExit(main())
