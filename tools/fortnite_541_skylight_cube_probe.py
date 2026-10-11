#!/usr/bin/env python3
"""Verify split-s4 PAK and inspect original Fortnite 5.41 cubemap source.

Metadata only: original source bytes never uploaded or committed.
"""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
import fortnite_541_r2_material_probe as main
from fortnite_541_material_expression_probe import Catalog
URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/pakchunk0_s4-WindowsClient.pak"
INDEX_SHA="96a67f9eae257051576e368fdb61a6fb78b2f56a"
SUFFIX="Packages/Fortress_Sky/TexturesHDR/T_AthenaSkylight"
KEY=main.KEY
def size():
    out=subprocess.run(["curl","--fail","--silent","--show-error","--location","--head","--max-time","40",URL],capture_output=True,text=True,check=True).stdout
    for line in reversed(out.splitlines()):
        if line.lower().startswith("content-length:"):
            return int(line.split(":",1)[1].strip())
    raise ValueError("source s4 response has no Content-Length")
def ranged(start,length):
    with tempfile.TemporaryDirectory() as d:
        f=Path(d)/"original.bin"
        subprocess.run(["curl","--fail","--silent","--show-error","--location","--retry","3","--range",
            f"{start}-{start+length-1}","--output",str(f),URL],check=True)
        b=f.read_bytes()
        if len(b)!=length:raise ValueError("R2 did not honor s4 source bytes request")
        return b
def source():
    length=size()
    footer=ranged(length-61,61)
    if struct.unpack_from("<II",footer,17)!=(0x5a6f12e1,7):
        raise ValueError("wrong source s4 PAK footer")
    idx,sizeidx=struct.unpack_from("<QQ",footer,25)
    original_hash=footer[41:61]
    if sizeidx>100*1024*1024 or sizeidx%16!=0 or idx+sizeidx>length-61:
        raise ValueError("source s4 PAK index invalid")
    encrypted=ranged(idx,sizeidx)
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"encrypted.bin";p.write_bytes(encrypted)
        q=Path(d)/"index.bin"
        subprocess.run(["openssl","enc","-aes-256-ecb","-d","-nopad","-K",KEY,
                        "-in",str(p),"-out",str(q)],check=True)
        plain=q.read_bytes()
    if hashlib.sha1(plain).digest()!=original_hash or original_hash.hex()!=INDEX_SHA:
        raise ValueError("original split-s4 index SHA1 mismatch")
    _,pos=main.fstring(plain,0)
    count=struct.unpack_from("<I",plain,pos)[0];pos+=4
    if count>1000000:raise ValueError("invalid number of original files")
    records={}
    for _ in range(count):
        name,pos=main.fstring(plain,pos)
        off,stored,raw,comp=struct.unpack_from("<QQQI",plain,pos);pos+=28
        digest=plain[pos:pos+20];pos+=20
        if comp:
            chunks=struct.unpack_from("<I",plain,pos)[0];pos+=4+16*chunks
        encrypted=plain[pos]&1;pos+=5
        records[name]=(off,stored,raw,comp,digest,encrypted)
    print("FORTNITE_S4_VERIFIED_INDEX "+json.dumps({
        "bytes":length,"index_sha1":original_hash.hex(),"source_files":len(records)
    }),flush=True)
    return records
def payload(entry):
    off,stored,raw,comp,digest,encrypted=entry
    if comp or encrypted or raw!=stored or raw>48*1024*1024:
        raise ValueError("source texture is not plain bounded bytes")
    b=ranged(off,stored+53)
    if b[28:48]!=digest or hashlib.sha1(b[53:]).digest()!=digest:
        raise ValueError("source texture SHA1 invalid")
    return b[53:]
def main_fn():
    records=source()
    packages={}
    for ext in [".uasset",".uexp",".ubulk"]:
        matches=[(key,v) for key,v in records.items() if key.endswith(SUFFIX+ext)]
        packages[ext]=matches
    report={"source":SUFFIX}
    for ext,matches in packages.items():
        report[ext]=[{"path":k,"bytes":v[2],"sha1":v[4].hex()} for k,v in matches]
    if len(packages[".uasset"])!=1 or len(packages[".uexp"])!=1:
        candidates=sorted([key for key in records if
            any(q in key.lower() for q in ("athenaskylight","skydome","fortress_sky","textureshdr"))])
        print("FORTNITE_S4_SKY_SOURCE_CANDIDATES "+json.dumps({
            "matched":len(candidates),"paths":candidates[:100]
        }),flush=True)
        matched=sorted(k for k in records if any(term in k.lower()
            for term in ("athenaskylight","textureshdr","skydomebasic01","todm_br","m_sky_basic")))
        print("FORTNITE_S4_FOCUSED_SOURCE_CANDIDATES "+json.dumps({
            "count":len(matched),"paths":matched[:160]
        }),flush=True)
        print("FORTNITE_S4_SOURCE_LOOKUP_FAILED "+json.dumps(report),flush=True)
        return
    header=payload(packages[".uasset"][0][1])
    export=payload(packages[".uexp"][0][1])
    cat=Catalog(header,export)
    report["names"]=[n for n in cat.names if any(w in n for w in
        ["TextureCube","Texture2D","PixelFormat","PF_","SizeX","SizeY","NumSlices","Mip","Compressed","SRGB","Lightmap","Cube"])]
    report["exports"]=[]
    for i,ex in enumerate(cat.exports,1):
        item={"object":cat.value(i),"class":cat.class_name(ex),"length":ex["size"]}
        try:
            props,end=cat.props(cat.export_data(ex))
            item["properties"]=[{"name":n,"kind":k,"size":len(v),"meta":extra}
                for n,k,extra,v in props]
            item["native_tail_len"]=ex["size"]-end
            native=cat.export_data(ex)[end:]
            # Temporary original cooked texture ONLY on this ephemeral runner.
            # Never commit or upload original source texture bytes.
            source_cube=Path("/tmp/fortnite541_verified_s4_skylight_cooked.bin")
            source_cube.write_bytes(native)
            item["original_cooked_source_sha1"]=hashlib.sha1(native).hexdigest()
            if len(native)>=92+393216:
                face_bytes=native[92:92+393216]
                item["source_cube_face_sha1"]=[
                    hashlib.sha1(face_bytes[i*65536:(i+1)*65536]).hexdigest()
                    for i in range(6)
                ]
            item["tail_first256"]=native[:256].hex()
            item["tail_last48"]=native[-48:].hex()
            item["source_lengths"]=[len(native),len(native)%16, len(native)-524288]
            item["source_pf_dxt5_offset"]=native.find(b"PF_DXT5")
            item["native_top_mip_size_0x60000_offsets"]=[
                p for p in range(0,min(200,len(native)-4))
                if native[p:p+4]==(393216).to_bytes(4,"little")
            ]
            item["recorded_u32_at_0_to_160"]=[
                {"pos":p,"value":struct.unpack_from("<I",native,p)[0]}
                for p in range(0,min(160,len(native)-4),4)
            ]
        except Exception as error:
            item["error"]=str(error)
        report["exports"].append(item)
    print("FORTNITE_S4_SKYLIGHT_SOURCE "+json.dumps(report,sort_keys=True),flush=True)
    Path("fortnite541_skylight_s4_source_audit.json").write_text(json.dumps(report,indent=2))
if __name__=="__main__":main_fn()
