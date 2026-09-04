#!/usr/bin/env python3
"""Find which D1 Investment EntityParent resolves to a requested EntityDataROI.

Uses the 013f EntityArrangementMap only to obtain the exact set of parent
FileHashes for one Investment asset package, then reads those parents directly
from the split TAR with RemoteLogicalPackage. This is intended for parallel
package-family searches and avoids downloading giant Investment asset PKGs.
"""
from __future__ import annotations

import argparse
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
    ap.add_argument('--package-id',type=lambda x:int(x,0),required=True)
    ap.add_argument('--find-entity',required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--member',action='append',type=parse_member,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    mr=EntryReader(a.assignment_map_pkg,a.runtime)
    _,mb=entry_payload(mr,ENTITY_ASSIGNMENTS_MAP)
    amap=parse_assignment_map(mb)
    parent_hashes=sorted({p for p in amap.values() if filehash_pkg_index(p)[0]==a.package_id})

    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    siblings={m.patch_id:m for m in a.member}
    if any(m.pkg_id!=a.package_id for m in a.member):
        raise SystemExit('all --member package ids must equal --package-id')
    r=RemoteLogicalPackage(arc,siblings,a.runtime)
    target=int(a.find_entity,16)
    hits=[]; errors=[]; blocks_before=0
    for n,pv in enumerate(parent_hashes,1):
        pkg,index=filehash_pkg_index(pv)
        ph=f'{pv:08X}'
        try:
            if index>=len(r.entries):
                raise RuntimeError('parent index outside entry table')
            e=r.entries[index]
            if e['tag_hash'].upper()!=ph:
                raise RuntimeError(f"tag mismatch {e['tag_hash']}")
            b=r.entry(index)
            if len(b)<0x14:
                raise RuntimeError(f'payload too short: {len(b)}')
            entity=struct.unpack_from('<I',b,0x10)[0]
            if entity==target:
                hits.append({'parent_hash':ph,'entry_index':index,'reference':e['reference'].upper(),'size':e['file_size'],'entity_data_hash':f'{entity:08X}'})
                print('TARGET',hits[-1],flush=True)
        except Exception as ex:
            errors.append({'parent_hash':ph,'entry_index':index,'error':repr(ex)})
        if n%500==0:
            print(f'{a.package_id:04X}: {n}/{len(parent_hashes)} parents; remote blocks cached={len(r.block_cache)}',flush=True)

    rep={'package_id':a.package_id,'logical_view':r.view.name,'candidate_parent_count':len(parent_hashes),
         'resolved_or_attempted':len(parent_hashes),'remote_blocks_read':len(r.block_cache),
         'target_entity':f'{target:08X}','hits':hits,'error_count':len(errors),'errors':errors[:100]}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:v for k,v in rep.items() if k not in ('errors',)},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
