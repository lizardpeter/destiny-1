#!/usr/bin/env python3
"""Inspect exact D1 EntityResource records through verified package catalogs.

For each requested 80800861 resource this records the source-closed ResourcePointer
triple and every 4-byte-aligned dword that resolves to an actual Tiger FileHash in
the supplied exact package catalogs. Resolvable aligned values are link candidates,
not automatically semantic fields; their byte offsets and target classes are
preserved so a concrete structure parser can later promote them.
"""
from __future__ import annotations

import argparse,json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS,parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_model_tgxm_signature_match import LazyExactHashResolver
from d1_split_tar_extract import SplitHttpTar


def norm(s:str)->str:return s.upper().removeprefix('0X').zfill(8)


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--tag',action='append',required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args();tags=list(dict.fromkeys(norm(x) for x in a.tag))
    cats=load_catalogs(a.member_catalog)
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    resolver=LazyExactHashResolver(arc,cats,a.runtime)
    rows=[]
    for h in tags:
        view,e,b=resolver.bytes(h)
        if e['reference'].upper()!=ENTITY_RESOURCE_CLASS:raise ValueError(f'{h}: ref {e["reference"]} != {ENTITY_RESOURCE_CLASS}')
        parsed=parse_resource(b,view.h['platform'])
        links=[]
        seen=set()
        for off in range(0,len(b)-(len(b)%4),4):
            v=struct.unpack_from('<I',b,off)[0];th=f'{v:08X}'
            if th in ('00000000','FFFFFFFF') or (off,th) in seen:continue
            try:
                tv,te=resolver.locate(th)
            except Exception:
                continue
            seen.add((off,th))
            links.append({'offset':off,'tag_hash':th,'package_id':f'{int(tv.h["pkg_id"]):04X}','entry_index':int(te['index']),
                          'reference':te['reference'].upper(),'type':int(te['type']),'subtype':int(te['subtype']),'file_size':int(te['file_size'])})
        rows.append({'tag_hash':h,'package_id':f'{int(view.h["pkg_id"]):04X}','entry_index':int(e['index']),'file_size':int(e['file_size']),
                     'resource':parsed,'aligned_resolvable_links':links,'aligned_resolvable_link_count':len(links)})
    rep={'schema':'d1_remote_entity_resource_links/v1','resources':rows,'catalog_package_ids':[f'{x:04X}' for x in sorted(cats)],
         'policy':'ResourcePointer class/targets are structurally decoded. Aligned resolvable dwords are exact byte occurrences that point to real catalog entries but remain candidate fields until their enclosing schema offset is source-closed.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps([{'tag_hash':r['tag_hash'],'semantic_role':r['resource']['semantic_role'],'unk10':r['resource']['unk10'],'unk18':r['resource']['unk18'],
                       'links':r['aligned_resolvable_links']} for r in rows],indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
