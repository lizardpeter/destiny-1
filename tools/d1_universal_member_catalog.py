#!/usr/bin/env python3
"""Convert the archive-wide Activity location index into one universal D1 member catalog.

Most remote D1 tools accept one or more ``d1_remote_package_member_catalog/v1``
files. Historically those catalogs were accumulated per investigation, which makes
archive-wide export unnecessarily dependent on hand-curated package lists.

The published Activity index already preserves every physical current-archive Tiger
package member and exact split-TAR offset. This tool converts that physical catalog
to the standard resolver schema only after validating the exact ``packages.txt``
SHA-256 and complete member-name set. It adds no semantic ownership claims.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def pkg_identity(name:str)->tuple[str,int]:
    stem=Path(name).name
    try:
        tail=stem[:-4] if stem.lower().endswith('.pkg') else stem
        pkg,generation=tail.rsplit('_',2)[-2:]
        return pkg.upper(),int(generation)
    except Exception as ex:
        raise ValueError(f'cannot decode package id/generation from {name!r}') from ex


def package_names(path:Path)->set[str]:
    out=set()
    for raw in path.read_text(errors='replace').splitlines():
        name=Path(raw.strip()).name
        if not name or not name.lower().endswith('.pkg'):continue
        try:pkg_identity(name)
        except ValueError:continue
        out.add(name)
    return out


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--activity-index',type=Path,required=True)
    ap.add_argument('--package-list',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    src=json.loads(a.activity_index.read_text())
    if int(src.get('schema_version',0))!=2 or src.get('status')!='D1_REMOTE_ACTIVITY_INDEX_COMPLETE':
        raise ValueError('source is not a complete D1 remote Activity index v2')
    list_sha=hashlib.sha256(a.package_list.read_bytes()).hexdigest()
    source_sha=str((src.get('source') or {}).get('package_list_sha256') or '').lower()
    if source_sha!=list_sha:raise ValueError(f'packages.txt SHA mismatch {source_sha} != {list_sha}')

    wanted=package_names(a.package_list);families={};seen=set();violations=[]
    for pkg,rows in sorted((src.get('package_families') or {}).items()):
        pkg=pkg.upper().zfill(4);outrows=[]
        for row in rows:
            name=Path(str(row['name'])).name
            fp,gen=pkg_identity(name)
            if fp!=pkg:violations.append(f'{name}: filename package {fp} != family {pkg}')
            ho=int(row['tar_header_offset']);do=int(row['data_offset']);size=int(row['size'])
            if do!=ho+512:violations.append(f'{name}: TAR data/header delta {do-ho} != 512')
            if name in seen:violations.append(f'{name}: duplicate physical member')
            seen.add(name)
            outrows.append({
                'name':name,'data_offset':do,'size':size,
                'tar_header_offset':ho,'filename_generation':gen,
                'header_patch_id':int(row['header_patch_id']),
            })
        families[pkg]=outrows
    missing=sorted(wanted-seen);extra=sorted(seen-wanted)
    if missing:violations.append(f'missing package-list members: {missing[:30]}')
    if extra:violations.append(f'extra indexed members: {extra[:30]}')
    if len(seen)!=int(src.get('physical_member_count',-1)):
        violations.append(f'flattened member count {len(seen)} != source {src.get("physical_member_count")}')
    if violations:raise ValueError('; '.join(violations[:20]))

    out={
        'schema':'d1_remote_package_member_catalog/v1',
        'source':'D1_CURRENT_ACTIVITY_INDEX.json physical package_families',
        'source_activity_index_sha256':hashlib.sha256(a.activity_index.read_bytes()).hexdigest(),
        'packages_txt_sha256':list_sha,
        'physical_member_count':len(seen),'package_family_count':len(families),
        'families':families,
        'policy':'Universal physical byte-location catalog only. Every FileHash must still resolve through its encoded Tiger package id; package filenames/proximity do not establish semantic ownership.'
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':'D1_UNIVERSAL_MEMBER_CATALOG_EXACT','physical_member_count':len(seen),
                      'package_family_count':len(families),'packages_txt_sha256':list_sha},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
