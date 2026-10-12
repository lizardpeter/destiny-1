#!/usr/bin/env python3
"""Authored Fortnite 5.41 SkyDome compiled DXBC shader frontier.

Resolve ten real ShaderCode hash IDs found within M_SkyDome.uexp against
the original authenticated UE4 PCD3D_SM5 shader library. Fetch only their
compressed records, validate zlib decompression, locate bounded DXBC
containers, and report shader stages/chunks/resource names. No compiled
shader source bytes are committed or printed.
"""
import collections
import hashlib
import json
import re
import struct
import zlib
import fortnite_541_r2_material_probe as r2
import fortnite_541_skylight_cube_probe as s4
from fortnite_541_material_shader_link_probe import ARCHIVE

MASTER="Packages/Fortress_Sky/SkyDome/Master/M_SkyDome.uexp"
S4_URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/pakchunk0_s4-WindowsClient.pak"
S4_HASH="96a67f9eae257051576e368fdb61a6fb78b2f56a"
def le32(b,o):
    return struct.unpack_from("<I",b,o)[0]
def ascii_at(blob,pos):
    if pos<0 or pos>=len(blob):return None
    m=re.match(rb"[\x20-\x7e]{1,127}\x00",blob[pos:pos+128])
    return m.group(0)[:-1].decode("ascii") if m else None
def shex_token_census(code):
    # SM4/SM5 tokenized instruction stream: two u32 header tokens,
    # instructions include their original encoded dword length in
    # opcode_token[24:30]. Never execute or disassemble guessed words.
    if len(code)<8 or len(code)%4:
        raise ValueError("original SHEX instruction payload not DWORD-aligned")
    version,total=struct.unpack_from("<II",code)
    if total!=len(code)//4:
        raise ValueError(f"original SHEX token count {total} vs {len(code)//4}")
    words=struct.unpack("<"+"I"*total,code)
    pos=2
    opcodes=collections.Counter()
    declarations=[]
    while pos<total:
        token=words[pos]
        op=token&0x7ff
        count=(token>>24)&0x7f
        if count==0 or pos+count>total:
            raise ValueError(f"invalid real DXBC token instruction length {count} at {pos}")
        opcodes[op]+=1
        if len(declarations)<45:
            declarations.append({"token_word":pos,"opcode":op,"dwords":count,
                "header":hex(token),
                "first_payload_words":[hex(w) for w in words[pos+1:min(pos+5,pos+count)]]})
        pos+=count
    if pos!=total:raise ValueError("original DXBC instruction stream not closed")
    return {"version_token":hex(version),"declared_dwords":total,
        "instruction_count":sum(opcodes.values()),
        "opcode_histogram":{str(k):v for k,v in sorted(opcodes.items())},
        "first_instructions":declarations}

def shader_container(blob):
    start=blob.find(b"DXBC")
    if start<0 or start+32>len(blob):return None
    length=le32(blob,start+24)
    count=le32(blob,start+28)
    if not 32<=length<=len(blob)-start or not 1<=count<=64:
        raise ValueError("original source compiled shader malformed DXBC envelope")
    contents=blob[start:start+length]
    chunks=[]
    for i in range(count):
        offset=le32(contents,32+i*4)
        if offset+8>length:raise ValueError("DXBC chunk offset past source")
        tag=contents[offset:offset+4].decode("ascii","replace")
        size=le32(contents,offset+4)
        if offset+8+size>length:raise ValueError("DXBC chunk size beyond source")
        chunk=contents[offset+8:offset+8+size]
        output={"fourcc":tag,"bytes":size}
        if tag=="RDEF" and len(chunk)>=32:
            cb_count=le32(chunk,0);cb_ofs=le32(chunk,4)
            resources=le32(chunk,8);rb_ofs=le32(chunk,12)
            if cb_count>4096 or resources>4096:
                raise ValueError("DXBC RDEF resource count exceeds validated bound")
            bindings=[]
            for n in range(resources):
                pos=rb_ofs+32*n
                if pos+32>len(chunk):
                    bindings.append({"index":n,"error":"source RDEF binding offset out of bounds"})
                    break
                name=ascii_at(chunk,le32(chunk,pos))
                word=struct.unpack_from("<8I",chunk,pos)
                bindings.append({"name":name,"type":word[1],
                    "bind_point":word[2],"bind_count":word[3],
                    "flags":word[4],"return_type":word[5],
                    "dimension":word[6],"samples":word[7]})
            output["resource_bindings"]=bindings
            output["source_constant_buffers"]=cb_count
            output["source_resource_binding_count"]=resources
        if tag=="SHEX":
            output["source_tokenized_code"]=shex_token_census(chunk)
        chunks.append(output)
    return {"dxbc_offset_in_original_code":start,"total_size":length,
            "original_UE4_parameter_prefix_bytes":start,"chunks":chunks}
def run():
    entries=r2.load_index()
    if ARCHIVE not in entries:raise ValueError("retail shader library unavailable")
    archive=entries[ARCHIVE]
    if archive[5] or archive[3] or archive[1]!=archive[2]:
        raise ValueError("unexpected original shader archive file entry")
    header=r2.ranged(archive[0],53)
    if header[28:48]!=archive[4]:
        raise ValueError("original shader archive local header index mismatch")
    start=archive[0]+53
    version,count=struct.unpack("<II",r2.ranged(start,8))
    if version!=1 or count!=96496:raise ValueError("original source shader library identity changed")
    table=r2.ranged(start+8,37*count)
    source_hashes={}
    for i in range(count):
        at=i*37
        h,offset,packed,unpacked,stage=struct.unpack_from("<20sQIIB",table,at)
        source_hashes[h]=(i,offset,packed,unpacked,stage)
    s4.URL=S4_URL;s4.INDEX_SHA=S4_HASH
    ix=s4.source()
    raw=s4.payload(ix[MASTER])
    hits=collections.defaultdict(list)
    for at in range(len(raw)-19):
        found=source_hashes.get(raw[at:at+20])
        if found:
            hits[found[0]].append(at)
    if sorted(hits)!=list(range(1314,1324)):
        raise ValueError("original M_SkyDome actual shader code reference set changed")
    decoded=[]
    archive_code_start=8+37*count
    for ordinal,locs in sorted(hits.items()):
        ident,ofs,csize,usize,stage=struct.unpack_from("<20sQIIB",table,ordinal*37)
        if not (0<csize<2*1024*1024 and 0<usize<4*1024*1024):
            raise ValueError("source SkyDome compiled shader byte limits violated")
        compressed=r2.ranged(start+archive_code_start+ofs,csize)
        shader=zlib.decompress(compressed)
        if len(shader)!=usize:
            raise ValueError("original sky compiled ShaderCode decompression disagrees with index")
        dxbc=shader_container(shader)
        row={
            "ordinal":ordinal,"source_shader_hash":ident.hex(),
            "frequency":stage,"source_compiled_bytes":len(shader),
            "compressed_bytes":len(compressed),
            "hash_references_in_M_SkyDome_uexp":len(locs),
            "original_byte_offsets":locs,"dxbc":dxbc,
            "decompressed_sha1":hashlib.sha1(shader).hexdigest(),
        }
        decoded.append(row)
        print("FORTNITE_ORIGINAL_SKY_COMPILED_SM5_SHADER "+json.dumps(row,sort_keys=True),flush=True)
    print("FORTNITE_ORIGINAL_SKY_COMPILED_SM5_SUMMARY "+json.dumps({
        "library_records":count,"source_references":sum(map(len,hits.values())),
        "distinct_shader_ids":len(decoded),
        "stages":dict(collections.Counter(str(x["frequency"]) for x in decoded)),
        "source_dxbc_validated":sum(x["dxbc"] is not None for x in decoded),
    },sort_keys=True),flush=True)
if __name__=="__main__":
    run()
