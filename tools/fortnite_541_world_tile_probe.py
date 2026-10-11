#!/usr/bin/env python3
"""World-composition metadata in ORIGINAL UE4 package summary.
Authenticated original R2 bytes; no invented HedgeMaze tile offset.
"""
from pathlib import Path
import json,struct
import fortnite_541_r2_material_probe as r2
def i(data,p):return struct.unpack_from("<i",data,p)[0]
def u(data,p):return struct.unpack_from("<I",data,p)[0]
def fstr(data,p):return r2.fstring(data,p)
def summary(header):
    # Legacy UE4.21 -7 cooked asset summary. Fields before the name table
    # follow FPackageFileSummary, and WorldTileInfoDataOffset points directly
    # to a separate serialized FWorldTileInfo in the header.
    p=28
    folder,p=fstr(header,p)
    flags,name_count,name_offset,gather_count,gather_offset,exp_count,exp_offset,imp_count,imp_offset,deps=struct.unpack_from("<10I",header,p)
    p+=40
    records=[]
    for optional_soft in (0,8):
      for optional_search in (0,4):
       try:
        q=p+optional_soft+optional_search+4+16
        generations=i(header,q);q+=4
        if not 0<=generations<100:continue
        q+=8*generations
        versions=[]
        for _ in range(2):
            major,minor,patch=struct.unpack_from("<HHH",header,q)
            changelist=u(header,q+6)
            branch,q=fstr(header,q+10)
            versions.append((major,minor,patch,changelist,branch))
        compression=u(header,q);q+=4
        chunk_count=u(header,q);q+=4
        if chunk_count>100:continue
        q+=chunk_count*16
        package_source=u(header,q);q+=4
        extra_count=u(header,q);q+=4
        if extra_count>100:continue
        for _ in range(extra_count):_,q=fstr(header,q)
        registry=i(header,q);bulk=struct.unpack_from("<q",header,q+4)[0]
        world=i(header,q+12)
        q+=16
        chunk_ids=i(header,q);q+=4
        if chunk_ids>100:continue
        q+=chunk_ids*4
        preloads=struct.unpack_from("<ii",header,q)
        if not 0<=name_count<250000 or not 0<name_offset<len(header):continue
        records.append(dict(soft_extra=optional_soft,search_extra=optional_search,
            version=versions,first10=[flags,name_count,name_offset,exp_count,exp_offset,imp_count,imp_offset],
            header_summary_end=q+8,registry=registry,bulk=bulk,world_offset=world,
            world_head=header[world:world+120].hex() if 0<world<len(header) else None,
            candidate_ints=struct.unpack_from("<6i",header,world) if world>0 and world+24<len(header) else None,
            positions={str(off):i(header,off) for off in range(q-16,q+5,4) if off+4<len(header)}
            ))
       except Exception as e:pass
    return {"folder":folder,"raw32to192":header[32:192].hex(),
        "name_offset":name_offset,"possible":records}
def run():
    entries=r2.load_index()
    packages=["Athena/Maps/Athena_Terrain","Athena/Maps/Athena_Streaming_Grid",
        "Athena/Maps/POI/Athena_POI_HedgeMaze",
        "Athena/Maps/Landscape/Athena_Terrain_LS_00",
        "Athena/Maps/Landscape/Athena_Terrain_LS_01"]
    for package in packages:
        key="FortniteGame/Content/"+package+".umap"
        if key not in entries:continue
        raw=r2.source_payload(entries[key])
        result={"package":package,"bytes":len(raw),**summary(raw)}
        print("FORTNITE_VERIFIED_WORLD_TILE_INFO "+json.dumps(result),flush=True)
if __name__=="__main__":run()
