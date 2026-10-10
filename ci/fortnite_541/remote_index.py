#!/usr/bin/env python3
"""Bounded real Fortnite 5.41 encrypted PAK index inspection over HTTP Range.
Read-only; does not store extracted assets in a public repository."""
from urllib.request import Request, urlopen
import re, struct, hashlib, subprocess, sys, collections

BASE="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/"
KEY="81C42E03B21760A5C457C8DB7D52BA066F0633D0891FD9E37CF118F27687924A"
PAKS=[
"pakchunk0-WindowsClient.pak",
"pakchunk1-WindowsClient.pak",
"pakchunk0_s1-WindowsClient.pak",
"pakchunk0_s2-WindowsClient.pak",
"pakchunk0_s3-WindowsClient.pak",
]
def get(url, spec, limit):
    with urlopen(Request(url,headers={"Range":f"bytes={spec}"}),timeout=90) as f:
        if f.status!=206:raise RuntimeError(f"range required, got HTTP {f.status}")
        b=f.read(limit+1)
        if len(b)>limit:raise RuntimeError(f"range exceeded {limit}")
        return b, f.headers.get("Content-Range","")

def fstr(buf, pos):
    if pos+4>len(buf):raise ValueError("truncated fstring length")
    count=struct.unpack_from("<i",buf,pos)[0];pos+=4
    if count==0:return "",pos
    if abs(count)>131072:raise ValueError(f"string length {count} oversized")
    countbytes=count if count>0 else -count*2
    if pos+countbytes>len(buf):raise ValueError("truncated fstring bytes")
    payload=buf[pos:pos+countbytes];pos+=countbytes
    if count>0:
        if not payload.endswith(b"\0"): raise ValueError("unclosed utf8 string")
        return payload[:-1].decode("utf8"),pos
    else:
        if not payload.endswith(b"\0\0"):raise ValueError("unclosed utf16 string")
        return payload[:-2].decode("utf-16-le"),pos

def index_entries(buf):
    pos=0
    mount,pos=fstr(buf,pos)
    if pos+4>len(buf):raise ValueError("truncated entry count")
    count=struct.unpack_from("<I",buf,pos)[0];pos+=4
    if count>1_000_000:raise ValueError(f"bad count {count}")
    maps=[]
    methods=collections.Counter()
    encrypted_entries=0
    for i in range(count):
        path,pos=fstr(buf,pos)
        if pos+48>len(buf):raise ValueError(f"truncated record {i}")
        offset,size,raw,method=struct.unpack_from("<QQQI",buf,pos);pos+=28
        pos+=20 # pak entry hash
        if method:
            if pos+4>len(buf):raise ValueError("truncated compression block count")
            blocks=struct.unpack_from("<I",buf,pos)[0];pos+=4
            if blocks>2_000_000:raise ValueError("invalid compression blocks")
            pos+=blocks*16
        if pos+5>len(buf):raise ValueError("truncated block flags")
        encrypted=buf[pos] & 1;pos+=1
        blocksz=struct.unpack_from("<I",buf,pos)[0];pos+=4
        if pos>len(buf):raise ValueError("overrun")
        encrypted_entries+=encrypted
        methods[method]+=1
        if path.casefold().endswith(".umap"):maps.append(path)
    return mount,count,maps,methods,encrypted_entries,pos,len(buf)

for name in PAKS:
    url=BASE+name
    print("ARCHIVE",name,flush=True)
    try:
        tail,header=get(url,"-256",256)
        match=re.search(r"bytes (\d+)-(\d+)/(\d+)",header)
        length=int(match.group(3))
        sig=(0x5A6F12E1).to_bytes(4,"little")
        found=tail.rfind(sig)
        if found<0:raise RuntimeError("missing PakInfo")
        version=struct.unpack_from("<I",tail,found+4)[0]
        if version!=7:raise RuntimeError(f"unknown version {version}")
        offset,size=struct.unpack_from("<QQ",tail,found+8)
        digest=tail[found+24:found+44]
        encflag=tail[found-1]
        print(f"PAK_INFO length={length} version={version} idx={offset}+{size} encrypted={encflag} sha={digest.hex()}",flush=True)
        if size>12*1024*1024:raise RuntimeError("index too large")
        raw,rr=get(url,f"{offset}-{offset+size-1}",size)
        print(f"INDEX_DOWNLOADED bytes={len(raw)} range={rr}",flush=True)
        if len(raw)!=size:raise RuntimeError("range length mismatch")
        print(f"SHA_ENCRYPTED verified={hashlib.sha1(raw).digest()==digest} prefix={raw[:16].hex()}",flush=True)
        if size%16!=0:raise RuntimeError("encrypted size unaligned")
        p=subprocess.run(["openssl","enc","-aes-256-ecb","-d","-nopad","-K",KEY],
                         input=raw,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
        decrypted=p.stdout
        print(f"SHA_DECRYPTED verified={hashlib.sha1(decrypted).digest()==digest} prefix={decrypted[:32].hex()}",flush=True)
        if hashlib.sha1(decrypted).digest()!=digest:
            print("INDEX_KEY_HASH_MISMATCH",flush=True)
            continue
        mount,count,maps,methods,enc,counted,total=index_entries(decrypted)
        print(f"INDEX_PARSED mount={mount!r} entries={count} encrypted_payloads={enc} compression_methods={dict(methods)} consumed={counted}/{total}",flush=True)
        print(f"UMAP_COUNT {len(maps)}",flush=True)
        print("UMAP_EXAMPLES",repr(maps[:45]),flush=True)
        print("ATHENA_MAP_PATHS",repr([m for m in maps if "athena" in m.lower()][:45]),flush=True)
    except Exception as err:
        print("ERROR",type(err).__name__,str(err)[:400],flush=True)
