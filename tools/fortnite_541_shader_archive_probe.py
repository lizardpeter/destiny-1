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
    out={
        "path":path,"size":stored,"entry_sha1":digest.hex(),
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
