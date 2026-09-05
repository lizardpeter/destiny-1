#!/usr/bin/env python3
"""Probe evidence-driven Oodle raw lengths for one remote D1 logical block.

OodleLZ_Decompress requires the expected raw length, not merely a destination
capacity. Most Tiger blocks expand to 0x40000, but a partially covered logical
block can require a shorter serialized length. This probe derives candidate raw
lengths only from FileEntry coverage in the same current logical package table,
verifies the stored block SHA-1, and tries those exact/rounded coverage lengths.

No decoded bytes are accepted if the stored SHA-1 is wrong and no arbitrary raw
length search is performed.
"""
from __future__ import annotations

import argparse,ctypes,hashlib,json,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_pkg_probe import BLOCK_SIZE
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar


def auto_int(s:str)->int:return int(s,0)
def align(v,a):return ((v+a-1)//a)*a

def usage(entries,bi):
    rows=[]
    for e in entries:
        remain=int(e['file_size']);cur=int(e['starting_block']);off=int(e['starting_block_offset'])
        while remain>0:
            n=min(remain,BLOCK_SIZE-off)
            if cur==bi:
                rows.append({'entry_index':int(e['index']),'tag_hash':e['tag_hash'].upper(),'reference':e['reference'].upper(),'local_start':off,'local_end':off+n,'bytes':n})
            remain-=n;cur+=1;off=0
            if cur>bi and remain>0 and not rows:
                # Entries are ordered by starting block often enough that this is
                # not used as a correctness shortcut; preserve full scan.
                pass
    return rows

def call(oodle,comp,raw_len):
    src=ctypes.create_string_buffer(comp);dst=ctypes.create_string_buffer(raw_len)
    ret=oodle.fn(ctypes.cast(src,ctypes.c_void_p),len(comp),ctypes.cast(dst,ctypes.c_void_p),raw_len,1,0,1,None,None,None,None,None,None,3)
    out=dst.raw[:raw_len] if ret>0 else b''
    return {'raw_len':raw_len,'return':int(ret),'success':bool(ret>0),'output_sha256':hashlib.sha256(out).hexdigest() if out else None,'output_prefix':out[:64].hex() if out else None}

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--package-id',type=auto_int,required=True);ap.add_argument('--block',type=int,action='append',required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True);ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
    cats=load_catalogs(a.member_catalog);fam=cats.get(a.package_id)
    if fam is None:raise SystemExit(f'package {a.package_id:04X} absent from catalogs')
    base=a.base_url.rstrip('/');arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    r=RemoteLogicalPackage(arc,fam,a.runtime);reps=[]
    for bi in a.block:
        b=r.blocks[bi];owner=r.members.get(int(b['patch_id']))
        if owner is None:raise RuntimeError(f'block {bi} needs missing patch {b["patch_id"]}')
        comp=arc.read_at(owner.data_offset+int(b['offset']),int(b['size']));got=hashlib.sha1(comp).hexdigest()
        if got.lower()!=b['sha1'].lower():raise RuntimeError(f'block {bi} SHA mismatch {got} != {b["sha1"]}')
        u=usage(r.entries,bi);ends=sorted({x['local_end'] for x in u if x['local_end']>0});max_end=max(ends,default=0)
        candidates={BLOCK_SIZE}
        for x in ends:
            candidates.add(x)
        if max_end:
            for q in (0x10,0x100,0x1000,0x4000):candidates.add(align(max_end,q))
        candidates=sorted(x for x in candidates if 0<x<=BLOCK_SIZE)
        attempts=[]
        if b['compressed']:
            for n in candidates:
                try:attempts.append(call(r.oodle,comp,n))
                except Exception as ex:attempts.append({'raw_len':n,'success':False,'error':repr(ex)})
        else:
            attempts=[{'raw_len':len(comp),'return':len(comp),'success':True,'output_sha256':hashlib.sha256(comp).hexdigest(),'output_prefix':comp[:64].hex()}]
        rep={'block_index':bi,'patch_id':int(b['patch_id']),'owner_member':owner.name,'stored_offset':int(b['offset']),'stored_size':int(b['size']),
             'flags':int(b['flags']),'compressed':bool(b['compressed']),'encrypted':bool(b['encrypted']),'key1_flag':bool(b.get('key1_flag')),'unknown_0x8':bool(b.get('unknown_0x8')),
             'stored_sha1':got,'stored_prefix':comp[:64].hex(),'usage_count':len(u),'max_used_end':max_end,'distinct_used_ends':ends,'usage':u,'candidate_raw_lengths':candidates,
             'attempts':attempts,'successful_attempts':[x for x in attempts if x.get('success')]}
        reps.append(rep)
        print('BLOCK',bi,'patch',b['patch_id'],'flags',hex(int(b['flags'])),'stored',len(comp),'coverage',hex(max_end),'candidates',[hex(x) for x in candidates])
        for x in attempts:print(' ',hex(x['raw_len']),'->',x.get('return'),x.get('success'))
    out={'schema':'d1_remote_block_rawlen_probe/v1','package_id':f'{a.package_id:04X}','logical_view':r.view.name,'blocks':reps,
         'policy':'Stored SHA-1 is mandatory; candidate Oodle raw lengths come only from serialized FileEntry coverage and standard alignments of the maximum covered byte.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');return 0
if __name__=='__main__':raise SystemExit(main())
