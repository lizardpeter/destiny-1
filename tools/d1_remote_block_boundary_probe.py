#!/usr/bin/env python3
"""Test D1 Tiger compressed block boundaries against physical package layout.

Given FileHashes, inspect the exact compressed block they occupy in each package
snapshot, locate the next stored block in the same physical owner package, and
test Oodle using only compressed-input lengths justified by recorded size and
physical alignment/gap boundaries.

This detects a specific failure mode: a block-table compressed size that might
exclude alignment/trailer bytes required by an older Oodle stream.  It does not
scan arbitrary prefixes and never crosses the next physical block boundary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_investment_arrangement_probe import filehash_pkg_index
from d1_oodle_probe import Oodle3
from d1_pkg_probe import BLOCK_SIZE
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_block_occupancy_probe import occupancy
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar


def norm(v: str) -> str:
    v=v.upper().removeprefix('0X').zfill(8); int(v,16); return v


def align_up(v:int,a:int)->int:
    return ((v+a-1)//a)*a


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--tag-hash',action='append',required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    wanted=[norm(x) for x in a.tag_hash];cats=load_catalogs(a.member_catalog)
    base=a.base_url.rstrip('/');arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    oodle=Oodle3(a.runtime);out=[]
    for tag in wanted:
        pkg,idx=filehash_pkg_index(int(tag,16));fam=cats[pkg];rec={'tag_hash':tag,'package_id':f'{pkg:04X}','file_index':idx,'snapshots':[]}
        for patch in sorted(fam):
            s={'snapshot_patch_id':patch,'snapshot_member':fam[patch].name}
            try:
                v=RemoteLogicalPackage(arc,{p:m for p,m in fam.items() if p<=patch},a.runtime)
                e=v.entries[idx];assert e['tag_hash'].upper()==tag
                bi=int(e['starting_block']);b=v.blocks[bi];owner_patch=int(b['patch_id']);owner=v.members[owner_patch]
                oc=occupancy(v.entries,bi)
                # Physical neighbors are selected by stored offset among all blocks
                # in this logical table that point into the same owner member.
                same=sorted((int(x['offset']),int(x['size']),int(x['index']),x) for x in v.blocks if int(x['patch_id'])==owner_patch)
                pos=next(i for i,x in enumerate(same) if x[2]==bi)
                prev=same[pos-1] if pos else None; nxt=same[pos+1] if pos+1<len(same) else None
                start=int(b['offset']);recorded=int(b['size']);recorded_end=start+recorded
                next_off=nxt[0] if nxt else min(owner.size,align_up(recorded_end,0x1000))
                gap=max(0,next_off-recorded_end)
                max_read=next_off-start
                physical=arc.read_at(owner.data_offset+start,max_read)
                assert hashlib.sha1(physical[:recorded]).hexdigest().lower()==b['sha1'].lower()
                comp_lengths={recorded}
                for al in (0x10,0x20,0x40,0x80,0x100,0x200,0x400,0x800,0x1000):
                    q=align_up(recorded,al)
                    if q<=max_read: comp_lengths.add(q)
                if gap>0: comp_lengths.add(max_read)
                raw_lengths=set(oc['derived_raw_length_candidates'])
                attempts=[]
                for clen in sorted(comp_lengths):
                    for rlen in sorted(raw_lengths):
                        x={'compressed_input_length':clen,'requested_raw_length':rlen}
                        try:
                            dec=oodle.decompress(physical[:clen],raw_capacity=rlen)
                            x.update({'success':True,'returned_length':len(dec),'sha256':hashlib.sha256(dec).hexdigest(),'prefix_hex':dec[:32].hex()})
                        except Exception as ex:
                            x.update({'success':False,'error':repr(ex)})
                        attempts.append(x)
                s.update({
                    'logical_block_index':bi,'physical_patch_id':owner_patch,'physical_owner_member':owner.name,
                    'recorded_offset':start,'recorded_size':recorded,'recorded_end':recorded_end,
                    'previous_physical_block':({'logical_index':prev[2],'offset':prev[0],'size':prev[1]} if prev else None),
                    'next_physical_block':({'logical_index':nxt[2],'offset':nxt[0],'size':nxt[1]} if nxt else None),
                    'gap_to_next_block':gap,'max_nonoverlap_input_length':max_read,
                    'gap_prefix_hex':physical[recorded:recorded+min(gap,64)].hex(),
                    'occupancy':oc,'compressed_input_candidates':sorted(comp_lengths),'raw_length_candidates':sorted(raw_lengths),
                    'decode_attempts':attempts,
                })
            except Exception as ex:s['error']=repr(ex)
            rec['snapshots'].append(s)
        out.append(rec)
    rep={'schema':'d1_remote_block_boundary_probe/v1','entries':out,
         'policy':'Compressed-input candidates are limited to block-table size, standard physical alignments within the following gap, and the exact next-block boundary. No arbitrary prefix scan is performed.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    for r in out:
        print('\nTAG',r['tag_hash'])
        for s in r['snapshots']:
            if 'error' in s: print(' SNAP',s['snapshot_patch_id'],'ERROR',s['error']);continue
            oks=[x for x in s['decode_attempts'] if x['success']]
            print(' SNAP',s['snapshot_patch_id'],'block',s['logical_block_index'],'owner',s['physical_owner_member'],
                  'size',s['recorded_size'],'gap',s['gap_to_next_block'],'next',s['next_physical_block'],
                  'comp_candidates',s['compressed_input_candidates'],'raw_candidates',s['raw_length_candidates'],'successes',len(oks))
            for x in oks: print('  SUCCESS',x)
    print('wrote',a.output);return 0

if __name__=='__main__':raise SystemExit(main())
