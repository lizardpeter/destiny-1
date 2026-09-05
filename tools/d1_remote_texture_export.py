#!/usr/bin/env python3
"""Export exact D1 PS4 textures through verified remote package catalogs.

This adapts the validated d1_texture_export implementation to the same
MultiPackageReader used by Guardian geometry. Requested texture headers are
resolved by exact Tiger FileHash across verified logical package families, and
the existing texture exporter follows their serialized streamed/backing chain.

It can read texture hashes directly from a d1_remote_texture_plate_probe report.
No neighboring-package or filename inference is performed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader
from d1_split_tar_extract import SplitHttpTar
from d1_texture_export import export_reader


def norm(v:str)->str:
    v=v.upper().removeprefix('0X').zfill(8);int(v,16);return v


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--plate-report',type=Path)
    ap.add_argument('--tag-hash',action='append',default=[])
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    wanted=[]
    if a.plate_report:
        p=json.loads(a.plate_report.read_text())
        for h in p.get('source_texture_hashes',[]):
            h=norm(h)
            if h not in wanted:wanted.append(h)
    for h in a.tag_hash:
        h=norm(h)
        if h not in wanted:wanted.append(h)
    if not wanted:raise SystemExit('no texture hashes requested')

    catalogs=load_catalogs(a.member_catalog);base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    views={pkg:RemoteLogicalPackage(arc,fam,a.runtime) for pkg,fam in sorted(catalogs.items())}
    r=MultiPackageReader(views)
    by={e['tag_hash'].upper():e for e in r.entries}
    missing=[h for h in wanted if h not in by]
    if missing:raise SystemExit(f'requested texture headers absent from supplied catalogs: {missing}')

    a.out.mkdir(parents=True,exist_ok=True)
    rep=export_reader(r,a.out,tag_hashes=wanted,dependencies=[])
    manifest={
        'schema':'d1_remote_texture_export/v1',
        'requested_texture_hashes':wanted,
        'requested_count':len(wanted),
        'resolved_count':rep.get('texture_count'),
        'missing_requested':rep.get('missing_requested'),
        'textures':rep.get('textures',[]),
        'catalog_package_ids':[f'{x:04X}' for x in sorted(catalogs)],
        'policy':'Requested texture FileHashes and all serialized backing references are resolved only through exact hashes across verified logical package catalogs.',
    }
    (a.out/'remote_texture_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k!='textures'},indent=2))
    for x in manifest['textures']:
        print(x.get('header'),'->',x.get('png'),'owner',x.get('owner_package'),'backing',x.get('backing'))
    if manifest['missing_requested'] or manifest['resolved_count']!=len(wanted):
        raise SystemExit(f"texture export incomplete: {manifest['resolved_count']}/{len(wanted)}")
    bad=[x for x in manifest['textures'] if not x.get('png') or x.get('png_error')]
    if bad:raise SystemExit(f'{len(bad)} requested textures did not produce PNGs')
    return 0

if __name__=='__main__':raise SystemExit(main())
