#!/usr/bin/env python3
"""Compare OodleLZ_Decompress call modes on exact remote D1 Tiger blocks.

The project's historical bridge used tiger-pkg-style arguments
fuzzSafe=1/checkCRC=0/verbosity=1.  Charm's explicit Destiny 1 Rise of Iron
Package implementation instead uses fuzzSafe=0/checkCRC=0/verbosity=0, with
threadPhase=3.  Oodle users handling package blocks with unknown real size also
search destination sizes in 0x4000-byte steps.

This probe crosses those two independently source-backed facts on exact,
checksum-validated D1 blocks.  A known-good control must remain byte-identical.
No global decoder behavior is changed by this diagnostic.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_investment_arrangement_probe import filehash_pkg_index
from d1_oodle_probe import Oodle3
from d1_pkg_probe import BLOCK_SIZE
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_block_occupancy_probe import occupancy
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar

STEP=0x4000
MODES={
    'project_historical':(1,0,1),
    'charm_d1_roi':(0,0,0),
    'fuzz_off_verbose_minimal':(0,0,1),
    'fuzz_on_verbose_none':(1,0,0),
}


def norm(v:str)->str:
    v=v.upper().removeprefix('0X').zfill(8);int(v,16);return v


def align_up(v:int,a:int)->int:return ((v+a-1)//a)*a


def call(oodle:Oodle3,comp:bytes,raw_len:int,mode:tuple[int,int,int])->dict:
    src=ctypes.create_string_buffer(comp);dst=ctypes.create_string_buffer(raw_len)
    fuzz,crc,verb=mode
    n=oodle.fn(ctypes.cast(src,ctypes.c_void_p),len(comp),ctypes.cast(dst,ctypes.c_void_p),raw_len,
               fuzz,crc,verb,None,None,None,None,None,None,3)
    row={'return_value':int(n),'success':int(n)>0,'requested_raw_length':raw_len,
         'fuzz_safe':fuzz,'check_crc':crc,'verbosity':verb,'thread_phase':3}
    if n>0:
        data=dst.raw[:int(n)]
        row.update({'returned_length':len(data),'sha256':hashlib.sha256(data).hexdigest(),'prefix_hex':data[:32].hex()})
    return row


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--tag-hash',action='append',required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args();wanted=[norm(x) for x in a.tag_hash];cats=load_catalogs(a.member_catalog)
    base=a.base_url.rstrip('/');arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    oodle=Oodle3(a.runtime);rows=[]
    for tag in wanted:
        pkg,idx=filehash_pkg_index(int(tag,16));fam=cats[pkg]
        # Use the physical producer snapshot of the target block: oldest snapshot
        # in which the exact FileHash exists. Later logical tables may remap its
        # block index while retaining the same patch-1 physical bytes.
        found=None
        for patch in sorted(fam):
            v=RemoteLogicalPackage(arc,{p:m for p,m in fam.items() if p<=patch},a.runtime)
            if idx<len(v.entries) and v.entries[idx]['tag_hash'].upper()==tag:
                found=(patch,v,v.entries[idx]);break
        if found is None:raise RuntimeError(f'{tag}: no snapshot')
        patch,v,e=found;bi=int(e['starting_block']);b=v.blocks[bi];owner=v.members[int(b['patch_id'])]
        raw=arc.read_at(owner.data_offset+int(b['offset']),int(b['size']))
        got=hashlib.sha1(raw).hexdigest();assert got.lower()==b['sha1'].lower()
        oc=occupancy(v.entries,bi);min_oodle=align_up(int(oc['max_referenced_end']),STEP)
        sizes=sorted({min_oodle,BLOCK_SIZE})
        attempts=[]
        for size in sizes:
            for name,mode in MODES.items():
                x=call(oodle,raw,size,mode);x['mode']=name;attempts.append(x)
        row={'tag_hash':tag,'package_id':f'{pkg:04X}','file_index':idx,'producer_snapshot_patch':patch,
             'logical_block_index':bi,'physical_patch_id':int(b['patch_id']),'physical_owner_member':owner.name,
             'stored_offset':int(b['offset']),'stored_size':int(b['size']),'stored_sha1':got,
             'max_referenced_end':oc['max_referenced_end'],'first_legal_0x4000_size':min_oodle,
             'tested_raw_lengths':sizes,'attempts':attempts}
        rows.append(row)
        print('\nTAG',tag,'block',bi,'owner',owner.name,'stored',b['size'],'max_end',hex(oc['max_referenced_end']),'first_0x4000',hex(min_oodle))
        for x in attempts:print(' ',x['mode'],hex(x['requested_raw_length']),'->',x['return_value'],x.get('sha256',''))
    rep={'schema':'d1_remote_oodle_call_matrix_probe/v1','step':STEP,'modes':{k:{'fuzz_safe':v[0],'check_crc':v[1],'verbosity':v[2],'thread_phase':3} for k,v in MODES.items()},
         'entries':rows,'policy':'Exact checksum-validated blocks only; raw sizes are canonical 0x40000 and the first 0x4000 multiple covering serialized occupancy. Charm D1 ROI mode is tested without changing production decoder behavior.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n');print('wrote',a.output);return 0

if __name__=='__main__':raise SystemExit(main())
