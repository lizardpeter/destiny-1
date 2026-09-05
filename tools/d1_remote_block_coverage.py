#!/usr/bin/env python3
"""Report exact serialized FileEntry coverage for remote D1 logical blocks.

This tool deliberately never initializes or calls Oodle. It exists so raw-length
candidates can be derived safely before any decompression experiment. Stored
block bytes are SHA-1 checked against the current logical block table and the
report includes every FileEntry interval that occupies the selected block.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_pkg_probe import BLOCK_SIZE
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar


def auto_int(v:str)->int:return int(v,0)

def align(v:int,a:int)->int:return ((v+a-1)//a)*a

def entry_intervals(entries:list[dict], block_index:int)->list[dict]:
    rows=[]
    for e in entries:
        remain=int(e['file_size']);cur=int(e['starting_block']);off=int(e['starting_block_offset'])
        while remain>0:
            take=min(remain,BLOCK_SIZE-off)
            if cur==block_index:
                rows.append({
                    'entry_index':int(e['index']),'tag_hash':e['tag_hash'].upper(),'reference':e['reference'].upper(),
                    'entry_size':int(e['file_size']),'local_start':off,'local_end':off+take,'bytes_in_block':take,
                })
            remain-=take;cur+=1;off=0
    return rows

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--package-id',type=auto_int,required=True);ap.add_argument('--block',type=int,action='append',required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True);ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
    cats=load_catalogs(a.member_catalog);fam=cats.get(a.package_id)
    if fam is None:raise SystemExit(f'package {a.package_id:04X} absent from catalogs')
    base=a.base_url.rstrip('/');arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    # Runtime is intentionally omitted: RemoteLogicalPackage accepts a runtime
    # path only for payload reads; this census uses tables + raw archive bytes.
    # Supply a dummy nonexistent path because no block() / entry() call occurs.
    r=RemoteLogicalPackage(arc,fam,Path('/nonexistent/no-oodle-runtime'))
    reps=[]
    for bi in a.block:
        b=r.blocks[bi];patch=int(b['patch_id']);owner=r.members.get(patch)
        if owner is None:raise RuntimeError(f'block {bi}: missing patch member {patch}')
        stored=arc.read_at(owner.data_offset+int(b['offset']),int(b['size']))
        got=hashlib.sha1(stored).hexdigest()
        if got.lower()!=b['sha1'].lower():raise RuntimeError(f'block {bi}: stored SHA1 {got} != table {b["sha1"]}')
        rows=entry_intervals(r.entries,bi);ends=sorted({x['local_end'] for x in rows});starts=sorted({x['local_start'] for x in rows})
        max_end=max(ends,default=0);min_start=min(starts,default=None)
        cands=[]
        if max_end:
            for n in [max_end,align(max_end,0x10),align(max_end,0x100),align(max_end,0x1000),align(max_end,0x4000),BLOCK_SIZE]:
                if 0<n<=BLOCK_SIZE and n not in cands:cands.append(n)
        elif BLOCK_SIZE not in cands:cands.append(BLOCK_SIZE)
        rep={
            'block_index':bi,'patch_id':patch,'owner_member':owner.name,'owner_data_offset':owner.data_offset,
            'stored_offset':int(b['offset']),'stored_size':int(b['size']),'stored_sha1':got,'stored_prefix_hex':stored[:64].hex(),
            'flags':int(b['flags']),'flags_hex':f"0x{int(b['flags']):X}",'compressed':bool(b['compressed']),'encrypted':bool(b['encrypted']),
            'key1_flag':bool(b.get('key1_flag')),'unknown_0x8':bool(b.get('unknown_0x8')),
            'usage_count':len(rows),'min_used_start':min_start,'max_used_end':max_end,'distinct_used_starts':starts,'distinct_used_ends':ends,
            'coverage_candidate_raw_lengths':cands,'usage':rows,
        }
        reps.append(rep)
        print('BLOCK',bi,'patch',patch,'flags',rep['flags_hex'],'stored',rep['stored_size'],'coverage',hex(max_end),'candidates',[hex(x) for x in cands])
        for x in rows:print(' ',x['entry_index'],x['tag_hash'],x['reference'],hex(x['local_start']),hex(x['local_end']),x['bytes_in_block'])
    out={'schema':'d1_remote_block_coverage/v1','package_id':f'{a.package_id:04X}','logical_view':r.view.name,'blocks':reps,
         'policy':'No decompressor is initialized. Coverage derives only from current logical FileEntry block/start/size fields; stored bytes must pass current block-table SHA-1.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');return 0
if __name__=='__main__':raise SystemExit(main())
