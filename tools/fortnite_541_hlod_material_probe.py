#!/usr/bin/env python3
"""Decode exact source HLOD material/texture FPropertyTag references.
All original asset bytes stay on public runner, never in git artifacts.
"""
import json,struct,collections
from pathlib import Path
import fortnite_541_r2_material_probe as r2
from fortnite_541_material_expression_probe import Catalog
ASSETS=[
"FortniteGame/Content/Athena/Maps/Buildings/1x1/HLOD/Athena_REM_1x1_Shack_a_0_HLOD",
"FortniteGame/Content/Athena/Maps/Buildings/3x3/HLOD/Athena_RUR_3x3_House_c_1_HLOD",
"FortniteGame/Content/Athena/Maps/Buildings/5x5/HLOD/Athena_SUB_5x5_House2_a_1_HLOD"
]
def nested(cat,raw,prefix):
    if len(raw)>65536:return {"size":len(raw),"truncated":True}
    samples=[]
    for start in range(0,len(raw)-8,4):
        v=struct.unpack_from("<i",raw,start)[0]
        if v==0 or abs(v)>len(cat.imports)+len(cat.exports):continue
        try:
            name=cat.path(v)
            if any(x in name.lower() for x in ["texture","diffuse","material","normal","rough","metal","albedo","athena","color"]):
                samples.append({"byte_offset":start,"ref":v,"path":name})
        except Exception:pass
    return {"source_bytes":len(raw),"ref_candidates":samples[:48],"hex_head":raw[:240].hex()}
def run():
    entries=r2.load_index()
    outcomes=[]
    for name in ASSETS:
        pkg={x:r2.source_payload(entries[name+x]) for x in [".uasset",".uexp"]}
        cat=Catalog(pkg[".uasset"],pkg[".uexp"])
        obj={"package":name,"exports":len(cat.exports),"textures":[],"materials":[],"meshes":[]}
        for i,ex in enumerate(cat.exports,1):
            cls=cat.class_name(ex)
            if cls not in ("MaterialInstanceConstant","Texture2D","StaticMesh"):continue
            raw=cat.export_data(ex)
            props,at=cat.props(raw)
            item={"object":cat.value(i),"class":cls,"native_bytes":len(raw)-at,
                "properties":[]}
            for field,kind,extra,value in props:
                info={"name":field,"type":kind,"byte_count":len(value)}
                if kind in ["ObjectProperty","ClassProperty"] and len(value)==4:
                    v=struct.unpack("<i",value)[0]
                    info["ref"]=v;info["path"]=cat.path(v) if v else "null"
                elif kind=="StructProperty":
                    info["struct"]=extra
                elif kind=="ArrayProperty":
                    info["array"]=nested(cat,value,field)
                elif kind in ("BoolProperty","NameProperty","FloatProperty"):
                    info["value"]=extra if kind=="BoolProperty" else (
                        cat.fname(value) if kind=="NameProperty" else (
                            struct.unpack("<f",value)[0] if len(value)==4 else None))
                item["properties"].append(info)
            if cls=="MaterialInstanceConstant":obj["materials"].append(item)
            elif cls=="Texture2D":
                native=raw[at:]
                item["platform_header"]=native[:144].hex()
                item["external_bulk_source_bytes"]=entries.get(name+".ubulk",[0,0,0])[2] if name+".ubulk" in entries else 0
                obj["textures"].append(item)
            else:obj["meshes"].append(item)
        outcomes.append(obj)
    for o in outcomes:
        print("FORTNITE_AUTHORED_HLOD_MATERIAL_SOURCE "+json.dumps(o,sort_keys=True),flush=True)
    Path("fortnite541_hlod_material_metadata.json").write_text(json.dumps(outcomes,indent=2))
if __name__=="__main__":run()
