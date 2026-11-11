#!/usr/bin/env python3
"""Read only bounded HTTP ranges of a known publicly accessible Fortnite 5.41 PAK.
No R2 credentials, no executable payload download."""
from urllib.request import Request, urlopen
import re,struct,hashlib,sys
BASE="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/"
OBJECTS=[
"pakchunk0-WindowsClient.pak",
"pakchunk1-WindowsClient.pak",
"pakchunk2-WindowsClient.pak",
"pakchunk3-WindowsClient.pak",
"pakchunk4-WindowsClient.pak",
"pakchunk5-WindowsClient.pak",
"pakchunk6-WindowsClient.pak",
"pakchunk0-WindowsClient.sig",
"pakchunk0_s1-WindowsClient.pak",
"pakchunk0_s2-WindowsClient.pak",
"pakchunk0_s3-WindowsClient.pak",
"pakchunk0optional-WindowsClient.pak",
]
def grab(url, spec):
    req=Request(url,headers={"Range":f"bytes={spec}","User-Agent":"Fortnite541-index-audit/1.0"})
    with urlopen(req, timeout=60) as res:
        status=res.status
        data=res.read(1024*1024+256)
        length=res.headers.get("Content-Range","")
        return status, length, data
for name in OBJECTS:
    url=BASE+name
    try:
        status,cr,tail=grab(url,"-256")
        print(f"OBJECT {name} status={status} range={cr} length={len(tail)}",flush=True)
        if status!=206:continue
        match=re.search(r"bytes (\d+)-(\d+)/(\d+)",cr)
        if not match:continue
        file_size=int(match.group(3))
        # UE4 Pak magic 0x5A6F12E1 in LE
        magic=(0x5A6F12E1).to_bytes(4,"little")
        offsets=[m.start() for m in re.finditer(re.escape(magic),tail)]
        print(f"MAGIC_OFFSETS (within tail): {offsets}",flush=True)
        for off in offsets:
            if off+44>len(tail):continue
            version=struct.unpack_from("<I",tail,off+4)[0]
            index_offset,index_size=struct.unpack_from("<QQ",tail,off+8)
            sha1=tail[off+24:off+44].hex()
            encrypted=tail[off-1] if off else None
            # absolute tail offset for magic
            abs_magic=file_size-len(tail)+off
            print(f"FOOTER version={version} offset={index_offset} size={index_size} sha1={sha1} encrypted_flag={encrypted} abs_magic={abs_magic}",flush=True)
            if index_size>0 and index_size <= 1024*1024 and index_offset+index_size<=file_size:
                st,ic,body=grab(url,f"{index_offset}-{index_offset+index_size-1}")
                print(f"INDEX_FETCH status={st} range={ic} bytes={len(body)} sha1_matches={hashlib.sha1(body).hexdigest()==sha1} prefix_hex={body[:80].hex()}",flush=True)
    except Exception as exc:
        print(f"OBJECT {name} ERROR {str(exc)[:200]}",flush=True)
