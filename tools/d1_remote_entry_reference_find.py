#!/usr/bin/env python3
"""Find exact Tiger entry-table reference backlinks in one logical D1 package.

Unlike payload backlink scans this does not decompress any asset blocks.  It
reads only the latest logical entry table, then reports entries whose serialized
entry-table reference hash exactly equals a requested FileHash/tag hash.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from d1_remote_investment_parent_probe import RemoteLogicalPackage, parse_member
from d1_split_tar_extract import SplitHttpTar


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--package-id',type=lambda x:int(x,0),required=True)
    ap.add_argument('--target',action='append',required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--member',action='append',type=parse_member,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    if any(m.pkg_id != a.package_id for m in a.member):
        raise SystemExit('all --member package ids must equal --package-id')
    wanted={x.upper().removeprefix('0X') for x in a.target}
    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    r=RemoteLogicalPackage(arc,{m.patch_id:m for m in a.member},a.runtime)
    hits=[]
    for e in r.entries:
        ref=e['reference'].upper()
        if ref in wanted:
            row={
                'tag_hash':e['tag_hash'].upper(),
                'entry_index':e['index'],
                'reference':ref,
                'type':e['type'],
                'subtype':e['subtype'],
                'size':e['file_size'],
                'entry_b':e.get('entry_b'),
                'starting_block':e.get('starting_block'),
                'starting_block_offset':e.get('starting_block_offset'),
            }
            hits.append(row); print('REFERENCE_BACKLINK',row,flush=True)
    rep={
        'package_id':a.package_id,
        'logical_view':r.view.name,
        'entry_count':len(r.entries),
        'targets':sorted(wanted),
        'hit_count':len(hits),
        'hits':hits,
        'remote_blocks_read':len(r.block_cache),
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:v for k,v in rep.items() if k!='hits'},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
