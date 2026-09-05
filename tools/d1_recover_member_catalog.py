#!/usr/bin/env python3
"""Recover exact package members from a lightweight physical-member catalog.

This is intentionally semantic-agnostic. A catalog tells us where validated TAR
members physically live; higher-level D1 dependency logic decides *why* those
members are needed.  The tool supports the `families` shape used by the Tower
texture dependency catalog and optionally verifies current `packages.txt` family
membership before reading any bytes.

Recovered bytes are SHA-256 recorded. If a row already carries a `sha256`, the
hash is treated as a required pin and recovery fails closed on mismatch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_split_tar_extract import SplitHttpTar


def package_id(name: str) -> str | None:
    m = re.search(r'_([0-9a-fA-F]{4})_[0-9]+\.pkg$', name)
    return m.group(1).lower() if m else None


def load_rows(doc: dict, families: set[str] | None) -> list[tuple[str, dict]]:
    if 'families' not in doc or not isinstance(doc['families'], dict):
        raise SystemExit('catalog must contain a families object')
    out=[]
    for fid, rows in doc['families'].items():
        fid=fid.lower()
        if families is not None and fid not in families:
            continue
        if not isinstance(rows,list):
            raise SystemExit(f'catalog family {fid} is not a list')
        for r in rows:
            if not isinstance(r,dict) or not {'name','data_offset','size'} <= set(r):
                raise SystemExit(f'catalog family {fid} has malformed member row: {r!r}')
            if package_id(str(r['name'])) != fid:
                raise SystemExit(f'catalog family/name mismatch: {fid} / {r["name"]}')
            out.append((fid,r))
    if families is not None:
        present={fid for fid,_ in out}
        missing=sorted(families-present)
        if missing:
            raise SystemExit(f'requested catalog families absent: {missing}')
    return out


def sha256_file(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--catalog',type=Path,required=True)
    ap.add_argument('--family',action='append',default=[],help='four-hex package id; repeatable; default all')
    ap.add_argument('--package-list',type=Path,help='current packages.txt; verifies exact selected-family membership')
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('--base-url',default='https://crypt.cohae.dev/destiny/ps4/packages/latest')
    ap.add_argument('--part-count',type=int,default=10)
    a=ap.parse_args()

    fams={x.lower().removeprefix('0x').zfill(4) for x in a.family} if a.family else None
    doc=json.loads(a.catalog.read_text())
    rows=load_rows(doc,fams)
    selected_families=sorted({fid for fid,_ in rows})

    if a.package_list:
        listed={Path(x.strip()).name for x in a.package_list.read_text(errors='replace').splitlines() if x.strip()}
        for fid in selected_families:
            expected=sorted(str(r['name']) for f,r in rows if f==fid)
            current=sorted(n for n in listed if package_id(n)==fid)
            if current != expected:
                raise SystemExit(f'current archive family {fid} differs from catalog: expected={expected} current={current}')

    a.out_dir.mkdir(parents=True,exist_ok=True)
    arc=SplitHttpTar([f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=120)
    recovered=[]
    for fid,r in rows:
        name=str(r['name']);off=int(r['data_offset']);size=int(r['size'])
        dst=a.out_dir/name
        got=arc.copy_to(off,size,dst)
        # copy_to already returns SHA-256, but re-check the local file so the
        # report certifies the exact bytes that later tools open.
        local=sha256_file(dst)
        if got.lower()!=local.lower():
            raise SystemExit(f'{name}: streamed/local SHA disagreement {got} != {local}')
        pin=r.get('sha256')
        if pin is not None and local.lower()!=str(pin).lower():
            raise SystemExit(f'{name}: SHA mismatch {local} != pinned {pin}')
        recovered.append({'family':fid,'name':name,'data_offset':off,'size':size,'sha256':local,'sha_pinned':pin is not None})
        print('RECOVERED',fid,name,size,local,flush=True)

    rep={
        'schema_version':1,
        'status':'EXACT_SPLIT_TAR_MEMBER_CATALOG_RECOVERY',
        'catalog':str(a.catalog),
        'selected_families':selected_families,
        'member_count':len(recovered),
        'members':recovered,
        'policy':'Physical member catalog recovery only; semantic ownership is established by higher-level serialized D1 dependency evidence.',
    }
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(rep,indent=2)+'\n')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
