#!/usr/bin/env python3
"""Enumerate a package family inside a calibrated Destiny split TAR interval.

Unlike d1_split_tar_extract, this tool is for discovering all physical patch
members of one logical family when the exact member suffixes are not yet known.
The caller supplies a validated TAR-header start offset and optionally an exact
stop-header offset. Every visited header is checksum validated before its name
or size is trusted.

No package ordering beyond the caller-provided calibrated interval is inferred.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from d1_split_tar_extract import BLOCK, SplitHttpTar, parse_tar_number, tar_header_checksum_ok, tar_name


def auto_int(s:str)->int:return int(s,0)


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,required=True)
    ap.add_argument('--start-offset',type=auto_int,required=True,help='validated TAR header offset')
    ap.add_argument('--stop-offset',type=auto_int,help='exclusive validated TAR header boundary')
    ap.add_argument('--prefix',required=True,help='archive basename prefix to retain')
    ap.add_argument('--retries',type=int,default=6);ap.add_argument('--timeout',type=int,default=90)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args();base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=a.retries,timeout=a.timeout)
    if a.start_offset%BLOCK:raise ValueError('start offset is not a TAR block boundary')
    if a.stop_offset is not None and a.stop_offset%BLOCK:raise ValueError('stop offset is not a TAR block boundary')
    off=a.start_offset;rows=[];visited=0
    while off+BLOCK<=arc.logical_size and (a.stop_offset is None or off<a.stop_offset):
        h=arc.read_at(off,BLOCK)
        if h==b'\0'*BLOCK:break
        if h[257:262]!=b'ustar':raise RuntimeError(f'invalid TAR magic at 0x{off:X}')
        if not tar_header_checksum_ok(h):raise RuntimeError(f'TAR checksum mismatch at 0x{off:X}')
        name=tar_name(h);size=parse_tar_number(h[124:136]);base_name=name.rsplit('/',1)[-1];visited+=1
        if base_name.startswith(a.prefix):
            row={'archive_name':name,'name':base_name,'header_offset':f'0x{off:X}','data_offset':f'0x{off+BLOCK:X}','size':size}
            rows.append(row);print('MATCH',base_name,row['header_offset'],row['data_offset'],size,flush=True)
        off += BLOCK + ((size+BLOCK-1)//BLOCK)*BLOCK
    rep={'schema':'d1_split_tar_family_discover/v1','prefix':a.prefix,'start_offset':f'0x{a.start_offset:X}',
         'stop_offset':f'0x{a.stop_offset:X}' if a.stop_offset is not None else None,'headers_visited':visited,
         'end_offset':f'0x{off:X}','member_count':len(rows),'members':rows,
         'policy':'Every member is accepted only after validating the ustar magic and checksum while walking from the caller-supplied calibrated TAR boundary.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2))
    if not rows:raise SystemExit(f'no members matched prefix {a.prefix!r}')
    return 0
if __name__=='__main__':raise SystemExit(main())
