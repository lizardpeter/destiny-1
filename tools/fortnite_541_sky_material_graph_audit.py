#!/usr/bin/env python3
"""Source-authentic M_SkyDome master expression, texture, and cloud dependency audit.

All bytes originate from SHA1-verified Fortnite 5.41 s4 retail PAK records.
No generated approximations, static screenshots or guessed cloud UVs.
"""
import collections
import json
import struct
import fortnite_541_skylight_cube_probe as s4
from fortnite_541_material_expression_probe import Catalog

S4="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/pakchunk0_s4-WindowsClient.pak"
HASH="96a67f9eae257051576e368fdb61a6fb78b2f56a"
ROOT="Packages/Fortress_Sky/SkyDome/Master/"
MASTER=ROOT+"M_SkyDome"
TEXTURES=[
    ROOT+"T_SkyDome_Cloud_Voroni",
    ROOT+"T_SkyDome_Stars_Sharp",
]
MESHES=[ROOT+"S_SkyDome01","Packages/Fortress_Sky/Mesh_NoLOD/SunHalfSphere"]
def source(index,path):
    matches=[(key,value) for key,value in index.items() if key.endswith(path)]
    if len(matches)!=1:
        raise ValueError(f"expected one original asset {path}, got {len(matches)}")
    return s4.payload(matches[0][1])
def package(index,name):
    header=source(index,name+".uasset")
    return Catalog(header,source(index,name+".uexp"))
def fields_of(cat,ex):
    raw=cat.export_data(ex)
    fields,end=cat.props(raw)
    result=[]
    for name,kind,meta,data in fields:
        row={"name":name,"kind":kind,"meta":meta,"size":len(data)}
        if kind in ("ObjectProperty","ClassProperty") and len(data)==4:
            ref=struct.unpack("<i",data)[0]
            row["source"]=cat.path(ref) if ref else None
        elif kind=="NameProperty" and len(data)==8:
            row["source_name"]=cat.fname(data)
        elif kind=="FloatProperty" and len(data)==4:
            row["value"]=struct.unpack("<f",data)[0]
        elif kind=="IntProperty" and len(data)==4:
            row["value"]=struct.unpack("<i",data)[0]
        elif kind=="StructProperty" and len(data) in (16,40):
            row["head"]=data[:40].hex()
            if len(data)==40:
                ref=struct.unpack_from("<i",data)[0]
                row["input_node"]=cat.path(ref) if ref else None
        elif kind=="ArrayProperty" and len(data)>=4:
            row["length"]=struct.unpack_from("<I",data)[0]
        result.append(row)
    return result,end
def main():
    s4.URL=S4
    s4.INDEX_SHA=HASH
    index=s4.source()
    cat=package(index,MASTER)
    types=collections.Counter()
    expressions=[]
    root=[]
    texture_uses=[]
    for i,ex in enumerate(cat.exports,1):
        typ=cat.class_name(ex)
        types[typ]+=1
        try:
            prop,end=fields_of(cat,ex)
        except Exception as err:
            root.append({"object":cat.path(i),"class":typ,"parse_error":str(err)})
            continue
        if typ.startswith("MaterialExpression"):
            refs=[p for p in prop if "source" in p or "input_node" in p]
            params=[p for p in prop if "source_name" in p or "value" in p]
            if "Texture" in typ or any(p["name"]=="Texture" for p in prop):
                texture_uses.append({"node":cat.path(i),"class":typ,
                                     "texture_refs":refs,"params":params})
            expressions.append({
                "node":cat.path(i),"class":typ,"refs":refs,
                "params":params,"properties_count":len(prop)
            })
        elif typ in ("Material","MaterialFunction","MaterialInstanceConstant"):
            root.append({"object":cat.path(i),"class":typ,"properties":prop})
    print("FORTNITE_SKY_MASTER_EXPRESSION_GRAPH "+json.dumps({
        "source":MASTER,"total_exports":len(cat.exports),
        "expression_count":len(expressions),
        "class_census":types.most_common(),
        "material_roots":root,
        "texture_nodes":texture_uses,
        "expression_edges":expressions
    },sort_keys=True),flush=True)
    # Inspect the actual source package inventory, including texture
    # UBulk. No assumption that .uexp exists for cooked textures.
    for name in TEXTURES+MESHES:
        inventory={}
        for ext in (".uasset",".uexp",".ubulk"):
            matches=[(k,v) for k,v in index.items() if k.endswith(name+ext)]
            if len(matches)>1:raise ValueError("duplicate original sky package record")
            if matches:
                b=s4.payload(matches[0][1])
                inventory[ext]=len(b)
                if ext==".uasset":
                    try:
                        c=Catalog(b,b"")
                        inventory["name_count"]=len(c.names)
                        inventory["export_types"]=collections.Counter(
                            c.class_name(e) for e in c.exports
                        ).most_common()
                        inventory["name_candidates"]=[
                            n for n in c.names if any(z in n.lower()
                                for z in ("cloud","star","pixel","format","texture","rgb","grayscale"))][:25]
                    except Exception as exc:inventory["header_error"]=str(exc)
                if ext==".ubulk":
                    inventory["first64"]=b[:64].hex()
        print("FORTNITE_SKY_SOURCE_RESOURCE "+json.dumps({
            "package":name,"retail_files":inventory},sort_keys=True),flush=True)
if __name__=="__main__":
    main()
