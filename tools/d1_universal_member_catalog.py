#!/usr/bin/env python3
"""Convert the archive-wide Activity location index into one resolver catalog.

The published Activity index covers the ordinary PS4 Tiger member namespace whose
filenames end ``_<package-id>_<generation>.pkg``. ``packages.txt`` also contains
localized cinematic variants such as ``_0204_jpn_0.pkg``; those are intentionally
reported as excluded here because package id alone cannot safely collapse language
variants into one logical family.

Within the base namespace this tool removes the old hand-curated-catalog bottleneck:
every indexed physical member becomes available through one standard
``d1_remote_package_member_catalog/v1`` file. The exact full packages.txt SHA is
still required, and no semantic ownership is inferred from filenames or locality.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

BASE_RX=re.compile(r'_([0-9A-Fa-f]{4})_([0-9]+)\.pkg$',re.I)


def pkg_identity(name:str)->tuple[str,int]:
    m=BASE_RX.search(Path(name).name)
    if not m:raise ValueError(f'not an ordinary package member name: {name!r}')
    return m.group(1).upper(),int(m.group(2))


def listed_names(path:Path)->tuple[set[str],set[str]]:
    base=set();excluded=set()
    for raw in path.read_text(errors='replace').splitlines():
        name=Path(raw.strip()).name
        if not name or not name.lower().endswith('.pkg'):continue
        if BASE_RX.search(name):base.add(name)
        else:excluded.add(name)
    return base,excluded


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

    wanted,excluded=listed_names(a.package_list);families={};seen=set();violations=[]
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
            outrows.append({'name':name,'data_offset':do,'size':size,'tar_header_offset':ho,
                            'filename_generation':gen,'header_patch_id':int(row['header_patch_id'])})
        families[pkg]=outrows
    missing=sorted(wanted-seen);extra=sorted(seen-wanted)
    if missing:violations.append(f'missing base package-list members: {missing[:30]}')
    if extra:violations.append(f'extra indexed base members: {extra[:30]}')
    if len(seen)!=int(src.get('physical_member_count',-1)):
        violations.append(f'flattened member count {len(seen)} != source {src.get("physical_member_count")}')
    if violations:raise ValueError('; '.join(violations[:20]))

    out={
        'schema':'d1_remote_package_member_catalog/v1',
        'scope':'ordinary_base_package_namespace',
        'source':'D1_CURRENT_ACTIVITY_INDEX.json physical package_families',
        'source_activity_index_sha256':hashlib.sha256(a.activity_index.read_bytes()).hexdigest(),
        'packages_txt_sha256':list_sha,
        'physical_member_count':len(seen),'package_family_count':len(families),
        'excluded_package_list_member_count':len(excluded),
        'excluded_package_list_members':sorted(excluded),
        'families':families,
        'policy':'Exact physical byte-location catalog for the ordinary _XXXX_generation.pkg namespace. Localized/alternate-language filename variants are explicitly excluded pending a language-aware family key. Every FileHash still resolves through its encoded Tiger package id; filename/proximity does not establish semantic ownership.'
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':'D1_UNIVERSAL_BASE_MEMBER_CATALOG_EXACT','physical_member_count':len(seen),
                      'package_family_count':len(families),'excluded_locale_or_variant_members':len(excluded),
                      'packages_txt_sha256':list_sha},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
