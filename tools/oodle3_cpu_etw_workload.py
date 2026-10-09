#!/usr/bin/env python3
"""Run one native DLL's verified LZH block workload for Windows ETW CPU sampling."""
from __future__ import annotations
import argparse
import ctypes
import hashlib
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from d1_pkg_probe import parse_header,parse_blocks,read_table

def load_decoder(path):
    dll=ctypes.WinDLL(str(Path(path).resolve()))
    fn=dll.OodleLZ_Decompress
    fn.restype=ctypes.c_int64
    fn.argtypes=[ctypes.c_void_p,ctypes.c_int64,ctypes.c_void_p,ctypes.c_int64,
                 ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32,
                 ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,
                 ctypes.c_void_p,ctypes.c_void_p,ctypes.c_uint32]
    return dll,fn

def cases(root):
    found=[]
    for member,patch,limit in (
        ("ps4_city_tower_destination_024c_5.pkg",5,8),
        ("ps4_globals_0157_6.pkg",6,3)):
        path=root/member
        with path.open('rb') as f:
            header=parse_header(f)
            table=read_table(f,header['block_table_offset'],header['block_table_count'],32)
        n=0
        for b in parse_blocks(table):
            if not b['compressed'] or int(b['patch_id'])!=patch: continue
            with path.open('rb') as f:
                f.seek(int(b['offset']))
                compressed=f.read(int(b['size']))
            if hashlib.sha1(compressed).hexdigest().lower()!=str(b['sha1']).lower():
                raise RuntimeError("Input data failed package SHA1: "+member)
            found.append((member+'/'+str(b['index']),
                          ctypes.create_string_buffer(compressed),
                          len(compressed),ctypes.create_string_buffer(0x40000)))
            n+=1
            if n==limit:break
        if n!=limit:raise RuntimeError(f'Expected {limit} blocks from {member}, got {n}')
    return found

def run(args):
    # Keep each native workload on one logical processor for easier single-core
    # sampling and to avoid attributing the benchmark process to several CPUs.
    if os.name=='nt':
        k=ctypes.WinDLL('kernel32.dll')
        k.GetCurrentProcess.restype=ctypes.c_void_p
        k.SetProcessAffinityMask.argtypes=[ctypes.c_void_p,ctypes.c_size_t]
        pinned=bool(k.SetProcessAffinityMask(k.GetCurrentProcess(),1))
    else:
        pinned=False
    ds=cases(args.packages)
    original,reference=load_decoder(args.reference)
    current,decode=load_decoder(args.dll)
    for name,src,n,dst in ds:
        expected=ctypes.create_string_buffer(0x40000)
        ret=reference(ctypes.cast(src,ctypes.c_void_p),n,
                      ctypes.cast(expected,ctypes.c_void_p),0x40000,
                      1,0,0,None,None,None,None,None,None,3)
        if ret!=0x40000:raise RuntimeError(f'Reference failure {name}: {ret}')
        result=decode(ctypes.cast(src,ctypes.c_void_p),n,
                      ctypes.cast(dst,ctypes.c_void_p),0x40000,
                      1,0,0,None,None,None,None,None,None,3)
        if result!=0x40000 or dst.raw!=expected.raw:
            raise RuntimeError('Decoder mismatch '+name)
    def one_pass():
        for _name,src,n,dst in ds:
            ret=decode(ctypes.cast(src,ctypes.c_void_p),n,ctypes.cast(dst,ctypes.c_void_p),
                       0x40000,1,0,0,None,None,None,None,None,None,3)
            if ret!=0x40000:raise RuntimeError('Decode runtime failure')
    for _ in range(20):one_pass()
    start=time.perf_counter()
    for i in range(args.iterations):one_pass()
    elapsed=time.perf_counter()-start
    mib=args.iterations*len(ds)*0x40000/(1024*1024)
    print('NATIVE_ETW_WORKLOAD_RESULT',json.dumps({
        'decoder':args.label,'iterations':args.iterations,'blocks':len(ds),
        'bytes_decoded':int(mib*1024*1024),'mib_s':round(mib/elapsed,2),
        'elapsed_s':round(elapsed,3),'single_cpu_affinity_requested':pinned,
        'checksum':'11/11 byte-for-byte original Oodle before sampling'},sort_keys=True),flush=True)
    return 0

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument('--dll',required=True)
    p.add_argument('--reference',required=True)
    p.add_argument('--packages',type=Path,default=Path('recovered'))
    p.add_argument('--label',required=True)
    p.add_argument('--iterations',type=int,default=2200)
    sys.exit(run(p.parse_args()))
