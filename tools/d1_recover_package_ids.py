#!/usr/bin/env python3
"""Recover all current physical .pkg siblings for one or more D1 package IDs.

D1 v24 TagHash construction exposes package_id directly, so a world/material
pipeline can discover cross-package dependencies without guessing filenames:

    TagHash = 0x80800000 + (package_id << 13) + entry_index

Given `packages.txt`, this tool resolves each requested four-hex-digit package ID
to the exact current archive member names, walks the split TAR by validated TAR
headers, downloads only those members, and records their offsets/sizes/SHA-256.

This is intended as the generic dependency-expansion mechanism for the eventual
all-world exporter. A recovered package ID is dependency evidence, not semantic
world ownership.
"""
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_split_tar_extract import SplitHttpTar


def norm_id(x:str)->str:
    x=x.lower().removeprefix('0x').zfill(4)
    if not re.fullmatch(r'[0-9a-f]{4}',x):raise ValueError(x)
    return x


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--package-list',type=Path,required=True)
    ap.add_argument('--package-id',action='append',required=True)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('--base-url',default='https://crypt.cohae.dev/destiny/ps4/packages/latest')
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--start-offset',type=lambda x:int(x,0),default=0)
    a=ap.parse_args()

    ids=sorted({norm_id(x) for x in a.package_id})
    names={Path(x.strip()).name for x in a.package_list.read_text(errors='replace').splitlines() if x.strip()}
    selected={i:sorted(n for n in names if re.search(rf'_{i}_[0-9]+\.pkg$',n,re.I)) for i in ids}
    missing_ids=[i for i,v in selected.items() if not v]
    if missing_ids:raise SystemExit(f'package IDs absent from current packages.txt: {missing_ids}')
    wanted={n for rows in selected.values() for n in rows}

    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=120)
    found,headers=arc.find(wanted,start_offset=a.start_offset)
    missing=sorted(wanted-set(found))
    if missing:raise SystemExit(f'archive members not found: {missing}')

    a.out_dir.mkdir(parents=True,exist_ok=True)
    rows=[]
    for name in sorted(wanted):
        r=found[name];dst=a.out_dir/name
        sha=arc.copy_to(int(r['data_offset']),int(r['size']),dst)
        m=re.search(r'_([0-9a-fA-F]{4})_[0-9]+\.pkg$',name)
        rows.append({'package_id':m.group(1).lower() if m else None,'name':name,**r,'sha256':sha,'output':str(dst)})
        print('RECOVERED',name,r['size'],sha,flush=True)

    rep={
      'status':'D1_CURRENT_PACKAGE_ID_DEPENDENCIES_RECOVERED',
      'requested_package_ids':ids,'family_members':selected,
      'tar_headers_scanned':headers,'members':rows,
      'policy':'Package ID recovery follows exact TagHash namespace dependency only; it does not establish world ownership.'
    }
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({'package_ids':ids,'member_count':len(rows),'tar_headers_scanned':headers},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
