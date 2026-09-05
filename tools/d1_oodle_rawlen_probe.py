#!/usr/bin/env python3
"""Probe exact Oodle raw lengths for problematic D1 Tiger logical blocks.

Tiger readers commonly assume every decompressed block is 0x40000 bytes. Oodle's
API, however, requires the caller to provide the expected raw length. Patch blocks
that contain only a partial logical tail can therefore fail if 0x40000 is supplied.

This tool derives byte coverage of a selected logical block from every serialized
FileEntry in the same package table, then tries a small evidence-driven set of raw
lengths. It can test independent decoding and immediate-previous-block history.
No guessed payload bytes are accepted; stored SHA-1 is always verified first.
"""
from __future__ import annotations

import argparse, ctypes, hashlib, json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader
from d1_pkg_probe import BLOCK_SIZE, patch_path


def block_usage(reader: EntryReader, bi: int):
    rows=[]
    for e in reader.entries:
        remaining=int(e['file_size']); cur=int(e['starting_block']); off=int(e['starting_block_offset'])
        while remaining>0:
            n=min(remaining,BLOCK_SIZE-off)
            if cur==bi:
                rows.append({'entry_index':int(e['index']),'tag_hash':e['tag_hash'],'reference':e['reference'],'local_start':off,'local_end':off+n,'bytes':n})
            remaining-=n; cur+=1; off=0
            if cur>bi and not rows and cur>bi: # harmless early opportunity only
                pass
    return rows


def stored(reader,bi):
    b=reader.blocks[bi]; owner=patch_path(reader.pkg,b['patch_id'])
    if not owner.exists(): raise FileNotFoundError(str(owner))
    with owner.open('rb') as f:
        f.seek(b['offset']); raw=f.read(b['size'])
    got=hashlib.sha1(raw).hexdigest()
    if got.lower()!=b['sha1'].lower(): raise RuntimeError(f'block {bi} SHA mismatch')
    return b,owner,raw


def align(v,a): return ((v+a-1)//a)*a


def call(reader,bi,raw_len,history=False):
    b,owner,comp=stored(reader,bi)
    if not b['compressed']:
        return {'success':len(comp)<=raw_len,'return':len(comp),'owner':owner.name,'compressed':False}
    if history:
        if bi<=0: return {'success':False,'error':'no previous block'}
        prev=reader.block(bi-1)
        total=BLOCK_SIZE+raw_len
        buf=ctypes.create_string_buffer(total)
        base=ctypes.addressof(buf); ctypes.memmove(base,prev,BLOCK_SIZE)
        raw_addr=base+BLOCK_SIZE
        src=ctypes.create_string_buffer(comp)
        ret=reader.oodle.fn(ctypes.cast(src,ctypes.c_void_p),len(comp),ctypes.c_void_p(raw_addr),raw_len,1,0,1,ctypes.c_void_p(base),ctypes.c_void_p(total),None,None,None,None,3)
        out=ctypes.string_at(raw_addr,raw_len) if ret>0 else b''
    else:
        dst=ctypes.create_string_buffer(raw_len); src=ctypes.create_string_buffer(comp)
        ret=reader.oodle.fn(ctypes.cast(src,ctypes.c_void_p),len(comp),ctypes.cast(dst,ctypes.c_void_p),raw_len,1,0,1,None,None,None,None,None,None,3)
        out=dst.raw[:raw_len] if ret>0 else b''
    return {'success':bool(ret>0),'return':int(ret),'owner':owner.name,'compressed':True,'raw_len':raw_len,'history':history,'output_sha256':hashlib.sha256(out).hexdigest() if out else None,'output_prefix':out[:32].hex() if out else None}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('pkg',type=Path); ap.add_argument('--runtime',type=Path,required=True); ap.add_argument('--block',type=int,action='append',required=True); ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args(); r=EntryReader(a.pkg.resolve(),a.runtime.resolve()); reps=[]
    for bi in a.block:
        usage=block_usage(r,bi); max_end=max((x['local_end'] for x in usage),default=0); min_start=min((x['local_start'] for x in usage),default=None)
        candidates={BLOCK_SIZE}
        if max_end>0:
            candidates.update({max_end,align(max_end,0x10),align(max_end,0x100),align(max_end,0x1000),align(max_end,0x4000)})
        # Include each distinct serialized end point; these are not arbitrary sizes.
        candidates.update(x['local_end'] for x in usage if x['local_end']>0)
        candidates=sorted(x for x in candidates if 0<x<=BLOCK_SIZE)
        attempts=[]
        for n in candidates:
            for hist in (False,True):
                try: attempts.append(call(r,bi,n,hist))
                except Exception as ex: attempts.append({'success':False,'raw_len':n,'history':hist,'error':repr(ex)})
        reps.append({'block_index':bi,'block_table_count':len(r.blocks),'usage_count':len(usage),'min_used_start':min_start,'max_used_end':max_end,'usage':usage,'candidate_raw_lengths':candidates,'attempts':attempts,'successful_attempts':[x for x in attempts if x.get('success')]})
    rep={'package':a.pkg.name,'blocks':reps}; a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(rep,indent=2)+'\n'); print(json.dumps(rep,indent=2)); return 0

if __name__=='__main__': raise SystemExit(main())
