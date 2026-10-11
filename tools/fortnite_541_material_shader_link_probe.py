#!/usr/bin/env python3
"""Find exact original compiled ShaderCodeId hashes in cooked material packages.

SHA-1 verify all original source .uasset/.uexp data before scanning. No
source shader/material bytes are published. An absent match is meaningful:
it means we must recover shader map serialization from another source, not
guess a compiled shader by biome/function names.
"""
import json
import struct
from pathlib import Path
import fortnite_541_r2_material_probe as r2

ARCHIVE="FortniteGame/Content/ShaderArchive-FortniteGame-PCD3D_SM5.ushaderbytecode"
ORIGINAL_MATERIALS=[
    "FortniteGame/Content/Athena/Environments/Landscape/Material/M_Athena_Terrain_Master",
    "FortniteGame/Content/Athena/Environments/Landscape/Material/M_Athena_Terrain_01",
    "FortniteGame/Content/Athena/Environments/Landscape/Material/M_Athena_Terrain_01_Masked",
    "FortniteGame/Content/Athena/Environments/Landscape/Material/M_Athena_Terrain_01_NoAridRock",
    "FortniteGame/Content/Athena/Maps/Landscape/Athena_Terrain_LS_00",
]
def original_library_ids(entries):
    record=entries[ARCHIVE]
    header=r2.ranged(record[0]+53,8)
    version,count=struct.unpack("<II",header)
    if version!=1 or count!=96496:
        raise ValueError(f"unexpected original compiled shader archive header {version} {count}")
    packed=r2.ranged(record[0]+53+8,count*37)
    hashes={}
    for i in range(count):
        pos=i*37
        ident=packed[pos:pos+20]
        if ident in hashes:raise ValueError("duplicate original UE4 library hash")
        hashes[ident]=i
    return hashes
def hit_scan(data,shader_ids):
    # Scan source bytes linearly with a four-byte prefix map, rather than
    # 96k regexes or O(96k * file_size) substring searches.
    prefixes=set(key[:4] for key in shader_ids)
    result=set()
    for at in range(len(data)-19):
        if data[at:at+4] not in prefixes:continue
        shader=shader_ids.get(data[at:at+20])
        if shader is not None:result.add((shader,at))
    return [{"library_ordinal":i,"source_offset":at} for i,at in sorted(result)]
def main():
    entries=r2.load_index()
    shaders=original_library_ids(entries)
    census=[]
    for base in ORIGINAL_MATERIALS:
        record={"source_package":base,"files":[]}
        extensions=(".umap",".uexp") if "/Maps/" in base else (".uasset",".uexp")
        for ext in extensions:
            path=base+ext
            if path not in entries:
                record["files"].append({"path":path,"available":False})
                continue
            bytes_data=r2.source_payload(entries[path])
            matched=hit_scan(bytes_data,shaders)
            file={"path":path,"source_bytes":len(bytes_data),
                  "source_sha1":entries[path][4].hex(),
                  "compiler_shader_hash_matches":matched[:40],
                  "total_matches":len(matched)}
            record["files"].append(file)
            print("FORTNITE_RETAIL_MATERIAL_SHADER_LINK "+json.dumps(file,sort_keys=True),flush=True)
        census.append(record)
    report={"verified_library_shader_ids":len(shaders),"material_sources":census}
    Path("fortnite-541-material-shader-link-audit.json").write_text(
        json.dumps(report,indent=2),encoding="utf8")
    print("FORTNITE_RETAIL_MATERIAL_SHADER_LINK_COMPLETE "+
          json.dumps({"library_ids":len(shaders),"matches":sum(f.get("total_matches",0) for m in census for f in m["files"])}),flush=True)
if __name__=="__main__":main()
