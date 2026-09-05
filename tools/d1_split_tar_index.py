#!/usr/bin/env python3
"""Build a complete validated member index for the remote Destiny split TAR.

This performs the same sparse TAR-header walk as `d1_split_tar_extract.py` but
records every member instead of downloading payloads.  Because TAR headers carry
member sizes, the walker jumps over package bodies and only range-reads 512-byte
headers.  A supplied `packages.txt` can be required to match the resulting .pkg
basename set exactly.

The resulting catalog removes one of the last Tower-specific scaling hacks: any
future D1 TagHash package namespace can be resolved to exact physical TAR member
offsets without another bounded archive scan.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_split_tar_extract import BLOCK, SplitHttpTar, parse_tar_number, tar_header_checksum_ok, tar_name


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--package-list',type=Path)
    ap.add_argument('-o','--output',type=Path,required=True)
    ap.add_argument('--retries',type=int,default=6)
    ap.add_argument('--timeout',type=int,default=90)
    a=ap.parse_args()
    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=a.retries,timeout=a.timeout)

    off=0;headers=0;zero=0;members=[]
    while off+BLOCK<=arc.logical_size:
        h=arc.read_at(off,BLOCK)
        if h==b'\0'*BLOCK:
            zero+=1
            if zero>=2:break
            off+=BLOCK;continue
        zero=0
        if h[257:262]!=b'ustar':
            raise SystemExit(f'invalid TAR magic at 0x{off:X}: {h[257:263]!r}')
        if not tar_header_checksum_ok(h):
            raise SystemExit(f'TAR checksum mismatch at 0x{off:X}')
        name=tar_name(h);size=parse_tar_number(h[124:136]);base_name=name.rsplit('/',1)[-1]
        members.append({'archive_name':name,'basename':base_name,'header_offset':off,'data_offset':off+BLOCK,'size':size})
        headers+=1
        if headers%100==0:print(f'headers={headers} off=0x{off:X} member={base_name}',flush=True)
        off += BLOCK + ((size+BLOCK-1)//BLOCK)*BLOCK

    pkg_members=[r for r in members if r['basename'].lower().endswith('.pkg')]
    verification=None
    if a.package_list:
        expected={Path(x.strip()).name for x in a.package_list.read_text(errors='replace').splitlines() if x.strip()}
        found={r['basename'] for r in pkg_members}
        verification={
            'expected_count':len(expected),'found_count':len(found),
            'missing':sorted(expected-found),'extra':sorted(found-expected),'exact':expected==found,
        }
        if not verification['exact']:
            raise SystemExit('packages.txt does not exactly match TAR package members: '+json.dumps(verification))

    out={
      'schema_version':1,'status':'D1_REMOTE_SPLIT_TAR_COMPLETE_MEMBER_INDEX',
      'base_url':base,'part_count':a.part_count,'part_sizes':arc.sizes,'logical_size':arc.logical_size,
      'tar_headers_scanned':headers,'member_count':len(members),'package_member_count':len(pkg_members),
      'packages_txt_verification':verification,'members':members,
      'policy':'Physical archive member index only. Semantic D1 ownership/dependencies remain FileHash/resource-graph evidence.',
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('logical_size','tar_headers_scanned','member_count','package_member_count','packages_txt_verification')},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
