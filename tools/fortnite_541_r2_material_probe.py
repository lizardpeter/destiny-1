#!/usr/bin/env python3
"""SHA1-authenticated bounded Fortnite 5.41 retail-source metadata audit.

Uses original R2 encrypted PAK index and item digests. Emits metadata only;
never publishes the copyrighted source texture or material payloads.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import tempfile

URL = "https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/pakchunk0-WindowsClient.pak"
KEY = "81C42E03B21760A5C457C8DB7D52BA066F0633D0891FD9E37CF118F27687924A"
SIZE = 4_813_653_874
EXPECTED_INDEX_SHA1 = "fd1f4623c812f5fff47298f99cc3d0d8f2d0f11b"
TARGETS = [
    "/Environments/Landscape/Material/M_Athena_Terrain_Master",
    "/Environments/Landscape/Material/M_Athena_Terrain_01",
    "/Environments/Landscape/MaterialFunctions/Standard/MF_Athena_Grass_01",
    "/Environments/Landscape/MaterialFunctions/Standard/MF_Athena_Rock_01",
    "/Environments/Landscape/MaterialFunctions/Standard/MF_Athena_Forest_01",
    "/Environments/Landscape/Textures/T_Athena_Terrain_CombinedColors_01",
    "/Environments/Landscape/Textures/T_Athena_Terrain_Topo_Mask",
]
def ranged(start, count):
    if start < 0 or count < 1 or count > 24*1024*1024:
        raise ValueError("range request outside bounded source scope")
    with tempfile.TemporaryDirectory() as d:
        output = Path(d)/"range.bin"
        subprocess.run([
            "curl","--fail","--silent","--show-error","--location","--retry","4",
            "--max-time","110","--range",f"{start}-{start+count-1}",
            "--output",str(output),URL
        ],check=True)
        result=output.read_bytes()
        if len(result)!=count:
            raise ValueError(f"R2 range returned {len(result)} bytes rather than {count}")
        return result
def fstring(data, pos):
    n=struct.unpack_from("<i",data,pos)[0]
    pos+=4
    if n==0:
        return "",pos
    if not 0<abs(n)<=131072:
        raise ValueError("invalid original source FString size")
    raw=data[pos:pos+(n if n>0 else -2*n)]
    pos+=len(raw)
    if n>0:
        if not raw.endswith(b"\0"): raise ValueError("unterminated FString")
        return raw[:-1].decode("utf8"),pos
    if not raw.endswith(b"\0\0"): raise ValueError("unterminated UTF16 FString")
    return raw[:-2].decode("utf-16-le"),pos
def decrypt(raw):
    with tempfile.TemporaryDirectory() as d:
        encrypted=Path(d)/"index.enc"
        plain=Path(d)/"index.bin"
        encrypted.write_bytes(raw)
        subprocess.run([
            "openssl","enc","-aes-256-ecb","-d","-nopad",
            "-K",KEY,"-in",str(encrypted),"-out",str(plain)
        ],check=True)
        return plain.read_bytes()
def load_index():
    footer=ranged(SIZE-61,61)
    if struct.unpack_from("<I",footer,17)[0]!=0x5a6f12e1 or struct.unpack_from("<I",footer,21)[0]!=7:
        raise ValueError("unexpected original Fortnite 5.41 footer")
    index_offset,index_size=struct.unpack_from("<QQ",footer,25)
    digest=footer[41:61]
    if index_size>16*1024*1024 or index_size%16:
        raise ValueError("unbounded original source index")
    plain=decrypt(ranged(index_offset,index_size))
    if hashlib.sha1(plain).digest()!=digest or digest.hex()!=EXPECTED_INDEX_SHA1:
        raise ValueError("Fortnite 5.41 PAK original index SHA1 mismatch")
    _,pos=fstring(plain,0)
    count=struct.unpack_from("<I",plain,pos)[0]
    pos+=4
    if count>1000000: raise ValueError("invalid PAK source file count")
    records={}
    for _ in range(count):
        name,pos=fstring(plain,pos)
        offset,stored,unpacked,method=struct.unpack_from("<QQQI",plain,pos)
        pos+=28
        content_hash=plain[pos:pos+20]
        pos+=20
        if method:
            chunks=struct.unpack_from("<I",plain,pos)[0]
            pos+=4+16*chunks
        encrypted=plain[pos]&1
        pos+=5
        records[name]=(offset,stored,unpacked,method,content_hash,encrypted)
    return records
def source_payload(record):
    offset,stored,unpacked,method,digest,encrypted=record
    if stored>24*1024*1024 or stored!=unpacked or encrypted or method:
        raise ValueError(f"unsupported source entry flags method={method}, encrypted={encrypted}, stored={stored}")
    data=ranged(offset,stored+53)
    header,payload=data[:53],data[53:]
    if struct.unpack_from("<QQQI",header,0)[1:]!=(stored,unpacked,0):
        raise ValueError("source PAK internal header mismatch")
    if header[28:48]!=digest or hashlib.sha1(payload).digest()!=digest:
        raise ValueError("source original file SHA1 mismatch")
    return payload
def main():
    entries=load_index()
    print(f"FORTNITE_R2_VERIFIED_INDEX entries={len(entries)} sha1={EXPECTED_INDEX_SHA1}",flush=True)
    # Original archive-index names help identify the actual sampled texture
    # families without asserting unknown original shader/UV assignments.
    landscape_assets=sorted(k for k in entries
        if "/Athena/Environments/Landscape/" in k and k.endswith(".uasset"))
    texture_candidates=[k for k in landscape_assets
        if "/Textures/" in k or "/Texture/" in k]
    print("FORTNITE_R2_LANDSCAPE_INDEX "+json.dumps({
        "packages":len(landscape_assets),
        "texture_packages":len(texture_candidates),
        "texture_source_paths":texture_candidates[:128],
        "truncated":len(texture_candidates)>128
    }),flush=True)
    audit={"original_pak":URL,"verified_index_sha1":EXPECTED_INDEX_SHA1,"entries":len(entries),"source_packages":[]}
    for suffix in TARGETS:
        group={"path_suffix":suffix,"files":[]}
        for extension in [".uasset",".uexp",".ubulk"]:
            matches=[(path,record) for path,record in entries.items()
                     if path.endswith(suffix+extension)]
            if len(matches)!=1:
                group["files"].append({"extension":extension,"count":len(matches)})
                continue
            path,entry=matches[0]
            item={"extension":extension,"path":path,"bytes":entry[2],
                  "sha1":entry[4].hex(),"method":entry[3],"encrypted":bool(entry[5])}
            try:
                data=source_payload(entry)
                item["sha1_verified"]=True
                if extension==".uexp":
                    item["pixel_format_tokens"]=sorted(set(
                        token.decode("ascii").strip("\0")
                        for token in re.findall(rb"PF_[A-Za-z0-9_]+\x00",data)
                    ))
                    item["original_source_material_names"]=sorted(set(
                        token.decode("ascii")
                        for token in re.findall(rb"(?:Forest|Crater|Arid|Gravel|Grass|Rock|Road|Mud|Golf_[A-Za-z]+)",data)
                    ))
                print("FORTNITE_R2_VERIFIED_FILE "+json.dumps(item,sort_keys=True),flush=True)
            except Exception as error:
                item["source_error"]=str(error)
                print("FORTNITE_R2_UNREADABLE_FILE "+json.dumps(item,sort_keys=True),flush=True)
            group["files"].append(item)
        audit["source_packages"].append(group)
    output=Path("fortnite-541-r2-material-audit.json")
    output.write_text(json.dumps(audit,indent=2),encoding="utf8")
    print("FORTNITE_R2_AUDIT_COMPLETE "+json.dumps({"packages":len(audit["source_packages"]), "report":str(output)}),flush=True)
if __name__=="__main__":
    main()
