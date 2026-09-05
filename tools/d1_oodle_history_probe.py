#!/usr/bin/env python3
"""Test D1 Tiger Oodle blocks with explicit preceding decode history.

Some Tiger blocks decode independently while immediately following blocks return
OODLELZ_FAILED. Oodle's decBufBase API allows compressed chunks to reference
contiguous preceding decompressed data used as a dictionary. This tool tests that
mechanism without changing package semantics.

For each --pair PREV:NEXT:
1. verify/read PREV from its block-table-selected patch sibling;
2. decode PREV independently;
3. verify/read NEXT from its own patch sibling;
4. allocate PREV||NEXT output contiguously;
5. pass the allocation base as decBufBase and the NEXT region as rawBuf;
6. record Oodle's return value and the recovered NEXT bytes/hashes.

No result is promoted unless the stored block SHA-1 checks first.
"""
from __future__ import annotations
import argparse, ctypes, hashlib, json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_pkg_probe import BLOCK_SIZE
from d1_oodle_probe import Oodle3, read_pkg_blocks, stored_block, sha1_hex, sha256_hex


def chained_decode(oodle: Oodle3, prev_raw: bytes, comp: bytes) -> tuple[int, bytes]:
    if len(prev_raw) != BLOCK_SIZE:
        raise ValueError(f'preceding block must be exactly {BLOCK_SIZE} bytes, got {len(prev_raw)}')
    total=BLOCK_SIZE*2
    buf=ctypes.create_string_buffer(total)
    ctypes.memmove(ctypes.addressof(buf), prev_raw, BLOCK_SIZE)
    src=ctypes.create_string_buffer(comp)
    base_addr=ctypes.addressof(buf)
    raw_addr=base_addr+BLOCK_SIZE
    n=oodle.fn(
        ctypes.cast(src,ctypes.c_void_p),len(comp),
        ctypes.c_void_p(raw_addr),BLOCK_SIZE,
        1,0,1,
        ctypes.c_void_p(base_addr),total,
        None,None,None,0,
        3,
    )
    if n <= 0:
        return int(n), b''
    # Oodle documents that with rawBuf > decBufBase the return includes the inset.
    produced=int(n)-BLOCK_SIZE if int(n)>BLOCK_SIZE else int(n)
    if produced < 0 or produced > BLOCK_SIZE:
        raise RuntimeError(f'impossible history decode return {n}, derived current bytes {produced}')
    return int(n), ctypes.string_at(raw_addr,produced)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('pkg',type=Path)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--pair',action='append',required=True,help='PREV:NEXT block indices, repeatable')
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    pkg=a.pkg.resolve(); h,blocks=read_pkg_blocks(pkg); oodle=Oodle3(a.runtime)
    rows=[]
    for rawpair in a.pair:
        ps,ns=rawpair.split(':',1); pi,ni=int(ps),int(ns)
        pb=blocks[pi]; nb=blocks[ni]
        po,pstored=stored_block(pkg,pb); no,nstored=stored_block(pkg,nb)
        if sha1_hex(pstored).lower()!=pb['sha1'].lower(): raise RuntimeError(f'prev block {pi} SHA mismatch')
        if sha1_hex(nstored).lower()!=nb['sha1'].lower(): raise RuntimeError(f'next block {ni} SHA mismatch')
        prev_raw=oodle.decompress(pstored) if pb['compressed'] else pstored
        if len(prev_raw)<BLOCK_SIZE: prev_raw=prev_raw+b'\0'*(BLOCK_SIZE-len(prev_raw))
        if len(prev_raw)!=BLOCK_SIZE: raise RuntimeError(f'prev block {pi} decoded to {len(prev_raw)}')
        ret,current=chained_decode(oodle,prev_raw,nstored) if nb['compressed'] else (BLOCK_SIZE*2,nstored)
        row={
          'prev_block':pi,'next_block':ni,
          'prev_owner':str(po),'next_owner':str(no),
          'prev_patch_id':pb['patch_id'],'next_patch_id':nb['patch_id'],
          'prev_stored_size':len(pstored),'next_stored_size':len(nstored),
          'prev_decompressed_sha256':sha256_hex(prev_raw),
          'history_bytes':BLOCK_SIZE,'dec_buf_size':BLOCK_SIZE*2,
          'oodle_return':ret,'success':bool(current),
          'current_decompressed_size':len(current),
          'current_decompressed_sha256':sha256_hex(current) if current else None,
          'current_prefix_hex':current[:64].hex() if current else None,
        }
        rows.append(row); print(json.dumps(row,indent=2),flush=True)
    rep={'package':str(pkg),'package_id':h['pkg_id'],'runtime':str(a.runtime.resolve()),'history_policy':'one complete immediately preceding 0x40000-byte Tiger logical block passed contiguously via decBufBase','pairs':rows}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(rep,indent=2)+'\n')
    return 0 if all(r['success'] for r in rows) else 2

if __name__=='__main__': raise SystemExit(main())
