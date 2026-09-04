#!/usr/bin/env python3
"""Find D1 Investment EntityParents whose EntityDataROI belongs to a target package.

This is the package-wide companion to d1_remote_investment_target_find.py.  It
uses the 013f EntityArrangementMap only to obtain the exact parent FileHash set,
then resolves parent +0x10 and reports every final EntityDataROI whose decoded
FileHash package id equals --target-package-id.  No assumption is made about
which 011c entity/permutation is the final weapon selection.
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader
from d1_investment_arrangement_probe import entry_payload, parse_assignment_map, filehash_pkg_index, ENTITY_ASSIGNMENTS_MAP
from d1_remote_investment_parent_probe import parse_member, RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('assignment_map_pkg',type=Path,help='013f logical snapshot containing 80A7E1DD')
    ap.add_argument('--package-id',type=lambda x:int(x,0),required=True,help='Investment asset family being scanned')
    ap.add_argument('--target-package-id',type=lambda x:int(x,0),required=True,help='final EntityDataROI package id to match')
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--member',action='append',type=parse_member,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    mr=EntryReader(a.assignment_map_pkg,a.runtime)
    _,mb=entry_payload(mr,ENTITY_ASSIGNMENTS_MAP)
    amap=parse_assignment_map(mb)
    # preserve assignment hashes so every parent hit can be traced back to all selectors
    parent_to_assignments=collections.defaultdict(list)
    for assignment,parent in amap.items():
        if filehash_pkg_index(parent)[0]==a.package_id:
            parent_to_assignments[parent].append(assignment)
    parent_hashes=sorted(parent_to_assignments)

    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    siblings={m.patch_id:m for m in a.member}
    if any(m.pkg_id!=a.package_id for m in a.member):
        raise SystemExit('all --member package ids must equal --package-id')
    r=RemoteLogicalPackage(arc,siblings,a.runtime)

    hits=[]; errors=[]; final_pkg_counts=collections.Counter()
    for n,pv in enumerate(parent_hashes,1):
        _,index=filehash_pkg_index(pv); ph=f'{pv:08X}'
        try:
            if index>=len(r.entries): raise RuntimeError('parent index outside entry table')
            e=r.entries[index]
            if e['tag_hash'].upper()!=ph: raise RuntimeError(f"tag mismatch {e['tag_hash']}")
            b=r.entry(index)
            if len(b)<0x14: raise RuntimeError(f'payload too short: {len(b)}')
            entity=struct.unpack_from('<I',b,0x10)[0]
            if entity not in (0,0xFFFFFFFF):
                epkg,eidx=filehash_pkg_index(entity); final_pkg_counts[epkg]+=1
                if epkg==a.target_package_id:
                    row={
                        'parent_hash':ph,'parent_entry_index':index,'parent_reference':e['reference'].upper(),
                        'parent_size':e['file_size'],'entity_data_hash':f'{entity:08X}',
                        'entity_data_package_id':epkg,'entity_data_file_index':eidx,
                        'assignment_hashes':[f'{x:08X}' for x in sorted(parent_to_assignments[pv])],
                    }
                    hits.append(row); print('TARGET_PACKAGE_HIT',json.dumps(row,separators=(',',':')),flush=True)
        except Exception as ex:
            errors.append({'parent_hash':ph,'entry_index':index,'error':repr(ex)})
        if n%500==0:
            print(f'{a.package_id:04X}: {n}/{len(parent_hashes)} parents; hits={len(hits)} blocks={len(r.block_cache)}',flush=True)

    rep={
        'investment_package_id':a.package_id,'logical_view':r.view.name,
        'target_package_id':a.target_package_id,'candidate_parent_count':len(parent_hashes),
        'remote_blocks_read':len(r.block_cache),'hit_count':len(hits),'hits':hits,
        'final_entity_package_counts':{f'{k:04X}':v for k,v in sorted(final_pkg_counts.items())},
        'error_count':len(errors),'errors':errors[:200],
    }
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:v for k,v in rep.items() if k not in ('hits','errors','final_entity_package_counts')},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
