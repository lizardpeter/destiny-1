#!/usr/bin/env python3
"""Locate authentic missing Fortnite 5.41 tree/foliage source packages across R2 PAKs.
Metadata only. Every discovered index is decrypted and authenticated using
the original archive footer's SHA1; no copyrighted asset bytes in output.
"""
import concurrent.futures,hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from urllib.parse import quote
import fortnite_541_r2_material_probe as original
BASE="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/"
TARGETS=[
 "Athena_Tree_Large","Shrub_05","Tree_Large","WavyGrass",
 "FortniteGame/Content/Environments/Props/Shrubs/",
 "FortniteGame/Content/Athena/Environments/Blueprints/",
 "FortniteGame/Content/Athena/Environments/Landscape/Foliage/",
]
PAKS=["pakchunk0-WindowsClient.pak"]+[
 f"pakchunk0_s{i}-WindowsClient.pak" for i in range(1,17)
]+[f"pakchunk{i}-WindowsClient.pak" for i in range(1,31)]
def head(name):
    url=BASE+name
    p=subprocess.run(["curl","--location","--silent","--show-error","--head",
        "--max-time","15",url],capture_output=True,text=True)
    if p.returncode!=0:return None
    lines=p.stdout.lower().splitlines()
    if not any(("http/" in l and "200" in l) for l in lines):return None
    lengths=[l.split(":",1)[1].strip() for l in lines if l.startswith("content-length:")]
    if not lengths:return None
    try:n=int(lengths[-1])
    except ValueError:return None
    return name,n if n>61 else None
def get_range(url,pos,n):
    if n<=0 or n>16*1024*1024:raise ValueError("source encrypted PAK index limit")
    with tempfile.TemporaryDirectory() as temp:
        out=Path(temp)/"bytes"
        subprocess.run(["curl","--fail","--location","--silent","--show-error",
            "--retry","2","--max-time","60","--range",f"{pos}-{pos+n-1}",
            "--output",str(out),url],check=True)
        data=out.read_bytes()
        if len(data)!=n:raise ValueError("original source R2 byte range length mismatch")
        return data
def source_index(name,length):
    url=BASE+name
    footer=get_range(url,length-61,61)
    if struct.unpack_from("<I",footer,17)[0]!=0x5a6f12e1 or struct.unpack_from("<I",footer,21)[0]!=7:
        raise ValueError("source PAK footer version/magic invalid")
    pos,n=struct.unpack_from("<QQ",footer,25)
    digest=footer[41:61]
    if pos+n>length-61 or n%16!=0:raise ValueError("source encrypted index bounds invalid")
    enc=get_range(url,pos,n)
    with tempfile.TemporaryDirectory() as temp:
        src=Path(temp)/"encrypted";dst=Path(temp)/"decrypted"
        src.write_bytes(enc)
        subprocess.run(["openssl","enc","-aes-256-ecb","-d","-nopad",
            "-K",original.KEY,"-in",str(src),"-out",str(dst)],check=True)
        plain=dst.read_bytes()
    if hashlib.sha1(plain).digest()!=digest:raise ValueError("original source index SHA1 mismatch")
    _,at=original.fstring(plain,0)
    nentries=struct.unpack_from("<I",plain,at)[0];at+=4
    if nentries>2_000_000:raise ValueError("source index entry bound exceeded")
    names=[]
    for i in range(nentries):
        path,at=original.fstring(plain,at)
        off,stored,raw,method=struct.unpack_from("<QQQI",plain,at);at+=28
        digest_item=plain[at:at+20];at+=20
        if method:
            chunks=struct.unpack_from("<I",plain,at)[0];at+=4+16*chunks
        encrypted=plain[at]&1;at+=5
        names.append(path)
    candidates=[k for k in names if any(t.lower() in k.lower() for t in TARGETS)]
    return {"pak":name,"length":length,"index_sha1":digest.hex(),
        "entries":len(names),"matched_source_paths":candidates[:150],
        "match_count":len(candidates)}
def run():
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        scanned=list(pool.map(head,PAKS))
    existing=[item for item in scanned if item and item[1]]
    print("FORTNITE_SOURCE_ARCHIVE_DISCOVERY "+json.dumps({
        "checked":len(PAKS),"archives":existing
    }),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        tasks={pool.submit(source_index,name,size):name for name,size in existing}
        for future in concurrent.futures.as_completed(tasks):
            name=tasks[future]
            try:
                result=future.result()
                print("FORTNITE_SOURCE_ARCHIVE_INDEX "+json.dumps(result),flush=True)
            except Exception as error:
                print("FORTNITE_SOURCE_ARCHIVE_INDEX_FAILED "+
                    json.dumps({"pak":name,"error":str(error)}),flush=True)
if __name__=="__main__":run()
