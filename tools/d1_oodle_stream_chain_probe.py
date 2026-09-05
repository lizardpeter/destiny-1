#!/usr/bin/env python3
"""Probe chained D1 Tiger Oodle blocks with a persistent decBufBase window.

Unlike the one-block history probe, this tool does not reset decBufBase between
successive compressed logical blocks. It allocates:

    [N verified preceding logical blocks][target block 0][target block 1]...

and keeps decBufBase fixed at the beginning while rawBuf advances one 0x40000-byte
logical block per Oodle call. This tests Oodle stream-history semantics directly.

Every stored compressed block is SHA-1 checked before decoding. History blocks are
read through the normal EntryReader and therefore must independently decode in this
probe; target blocks are the only blocks decoded with persistent history.
"""
from __future__ import annotations

import argparse, ctypes, hashlib, json, struct, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader
from d1_pkg_probe import BLOCK_SIZE, patch_path


def stored(reader: EntryReader, bi: int):
    b=reader.blocks[bi]; owner=patch_path(reader.pkg,b['patch_id'])
    if not owner.exists(): raise FileNotFoundError(str(owner))
    with owner.open('rb') as f:
        f.seek(b['offset']); raw=f.read(b['size'])
    got=hashlib.sha1(raw).hexdigest()
    if got.lower()!=b['sha1'].lower(): raise RuntimeError(f'block {bi} SHA mismatch')
    return b,owner,raw


def decode_chain(reader: EntryReader, first: int, count: int, history_depth: int):
    if history_depth < 1 or first < history_depth:
        raise ValueError('invalid history depth')
    hist_indices=list(range(first-history_depth,first))
    history=[]
    for bi in hist_indices:
        history.append(reader.block(bi))
    total_blocks=history_depth+count
    buf=ctypes.create_string_buffer(total_blocks*BLOCK_SIZE)
    base=ctypes.addressof(buf)
    for j,data in enumerate(history):
        ctypes.memmove(base+j*BLOCK_SIZE,data,BLOCK_SIZE)
    calls=[]
    for ti,bi in enumerate(range(first,first+count)):
        b,owner,raw=stored(reader,bi)
        out_index=history_depth+ti
        raw_addr=base+out_index*BLOCK_SIZE
        if not b['compressed']:
            ctypes.memmove(raw_addr,raw,min(len(raw),BLOCK_SIZE))
            ret=len(raw)
        else:
            src=ctypes.create_string_buffer(raw)
            # Keep the SAME base for every target block. decBufSize extends through
            # the current output block, not through unused future allocation.
            current_window=(out_index+1)*BLOCK_SIZE
            ret=reader.oodle.fn(
                ctypes.cast(src,ctypes.c_void_p),len(raw),
                ctypes.c_void_p(raw_addr),BLOCK_SIZE,
                1,0,1,
                ctypes.c_void_p(base),ctypes.c_void_p(current_window),
                None,None,None,None,3,
            )
        out=ctypes.string_at(raw_addr,BLOCK_SIZE)
        calls.append({
            'block_index':bi,'patch_id':int(b['patch_id']),'owner':owner.name,
            'compressed':bool(b['compressed']),'stored_size':len(raw),'stored_sha1':b['sha1'],
            'return':int(ret),'success':bool(ret>0),
            'output_sha256':hashlib.sha256(out).hexdigest() if ret>0 else None,
            'output_prefix':out[:32].hex() if ret>0 else None,
            'dec_buf_base_block':first-history_depth,
            'raw_buf_block_offset':out_index,
            'dec_buf_size':current_window,
        })
        if ret<=0:
            return {'success':False,'history_depth':history_depth,'history_indices':hist_indices,'calls':calls}
    target=ctypes.string_at(base+history_depth*BLOCK_SIZE,count*BLOCK_SIZE)
    return {'success':True,'history_depth':history_depth,'history_indices':hist_indices,'calls':calls,'target_logical_bytes_sha256':hashlib.sha256(target).hexdigest(),'target_bytes':target}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('pkg',type=Path)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--tag-hash',required=True)
    ap.add_argument('--history-depth',type=int,action='append',required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    r=EntryReader(a.pkg.resolve(),a.runtime.resolve())
    by={e['tag_hash'].upper():e for e in r.entries}; h=a.tag_hash.upper().removeprefix('0X')
    e=by.get(h)
    if not e: raise SystemExit(f'{h} not found')
    span=e['starting_block_offset']+e['file_size']; count=max(1,(span+BLOCK_SIZE-1)//BLOCK_SIZE)
    rep={'package':a.pkg.name,'tag_hash':h,'entry':{k:e[k] for k in ('index','reference','file_size','starting_block','starting_block_offset')},'target_block_count':count,'attempts':[]}
    for depth in a.history_depth:
        try:
            x=decode_chain(r,e['starting_block'],count,depth)
            target=x.pop('target_bytes',None)
            if target is not None:
                start=e['starting_block_offset']; payload=target[start:start+e['file_size']]
                x['entry_payload_bytes']=len(payload)
                x['entry_payload_sha256']=hashlib.sha256(payload).hexdigest()
                x['entry_payload_prefix']=payload[:64].hex()
            rep['attempts'].append(x)
        except Exception as ex:
            rep['attempts'].append({'success':False,'history_depth':depth,'error':repr(ex)})
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps(rep,indent=2))
    return 0 if any(x.get('success') for x in rep['attempts']) else 2

if __name__=='__main__': raise SystemExit(main())
