#!/usr/bin/env python3
"""Inspect original Fortnite 5.41 PCD3D_SM5 cooked shader archives from R2.

Reads the authenticated UE4 PAK index and validates each selected file's
on-disk FPakEntry header against the index. Fetches bounded byte windows,
never commits original shader code, and emits archive metadata only.
"""
import json
import hashlib
import re
import struct
from pathlib import Path
import fortnite_541_r2_material_probe as r2

TARGETS=[
    "FortniteGame/Content/ShaderArchive-FortniteGame-PCD3D_SM5.ushaderbytecode",
    "FortniteGame/Content/ShaderArchive-Global-PCD3D_SM5.ushaderbytecode",
    "Engine/GlobalShaderCache-PCD3D_SM5.bin",
]
def inspect_one(path,meta):
    offset,stored,unpacked,method,digest,encrypted=meta
    if encrypted or method or stored!=unpacked:
        raise ValueError("source shader archive compressed/encrypted: "+path)
    source_header=r2.ranged(offset,53)
    if struct.unpack_from("<QQQI",source_header,0)[1:]!=(stored,unpacked,0):
        raise ValueError("source shader PAK header differs from authenticated index: "+path)
    if source_header[28:48]!=digest:
        raise ValueError("source shader archive PAK entry hash differs from authenticated index: "+path)
    count=min(stored,8*1024*1024)
    prefix=r2.ranged(offset+53,count)
    magic=prefix[:96].hex()
    ascii_strings=[x.decode("ascii",errors="replace") for x in
        re.findall(rb"[ -~]{8,96}",prefix[:4096])[:12]]
    dxbc=[m.start() for m in re.finditer(rb"DXBC",prefix)]
    d3d11=[m.start() for m in re.finditer(rb"RDEF",prefix)]
    # UE4.21 retail uses the older shader archive version 1. Parse only a
    # candidate table until its entry stride, extents, uniqueness and archive
    # bounds are proven by the authenticated source bytes.
    parsed={}
    version,num=struct.unpack_from("<II",prefix,0)
    if version==1 and 0<num<=200000:
        rec_size=37
        table_end=8+num*rec_size
        if table_end<=len(prefix):
            shaders=[]
            hashes=set()
            for i in range(num):
                h,loc,csize,usize,frequency=struct.unpack_from("<20sQIIB",prefix,8+i*rec_size)
                shaders.append((loc,csize,usize,frequency))
                hashes.add(h)
            first_offsets=sorted(shaders,key=lambda x:x[0])
            max_end=max(loc+csize for loc,csize,_ in shaders)
            contiguous=sum(
                1 for a,b in zip(first_offsets,first_offsets[1:])
                if a[0]+a[1]==b[0]
            )
            parsed={
                "version":version,"index_count":num,"entry_stride":rec_size,
                "table_end":table_end,"unique_hashes":len(hashes),
                "zero_offsets":sum(1 for loc,_,_,_ in shaders if loc==0),
                "zero_sizes":sum(1 for _,c,_,_ in shaders if c==0),
                "compressed_larger_than_original":sum(1 for _,c,u,_ in shaders if c>u),
                "max_code_stream_end":max_end,
                "inferred_code_start":stored-max_end,
                "contiguous_adjacent_codes":contiguous,
                "frequency_counts":{str(k):sum(1 for _,_,_,f in shaders if f==k) for k in sorted(set(f for _,_,_,f in shaders))},
                "lowest_offset":min(loc for loc,_,_,_ in shaders),
                "max_compressed_shader":max(c for _,c,_,_ in shaders),
                "max_uncompressed_shader":max(u for _,_,u,_ in shaders),
                "first_sorted_entries":first_offsets[:5],
                "table_tail_hex":prefix[table_end:table_end+64].hex(),
                "plausible_strides":len(hashes)==num and max_end<=stored and all(f<=6 for _,_,_,f in shaders) and
                    sum(1 for loc,c,u,_ in shaders if c>0 and u>0 and loc+c<=stored)==num,
            }
    out={
        "path":path,"size":stored,"entry_sha1":digest.hex(),
        "candidate_v1_index":parsed,
        "first_96_bytes_hex":magic,
        "first_4k_ascii_strings":ascii_strings,
        "first_8mb_dxbc_offsets":dxbc[:30],
        "first_8mb_rdef_offsets":d3d11[:30],
        "dxbc_count_first_8mb":len(dxbc),"rdef_count_first_8mb":len(d3d11),
        "parsed_little_endian_first_12_u32":list(struct.unpack_from("<12I",prefix,0)),
    }
    return out
def run():
    entries=r2.load_index()
    output=[]
    for path in TARGETS:
        if path not in entries:raise ValueError("original shader archive path not found: "+path)
        result=inspect_one(path,entries[path])
        print("FORTNITE_RETAIL_SHADER_ARCHIVE "+json.dumps(result,sort_keys=True),flush=True)
        output.append(result)
    Path("fortnite-541-retail-shader-archive-audit.json").write_text(
        json.dumps(output,indent=2),encoding="utf8")
if __name__=="__main__":
    run()
