#!/usr/bin/env python3
"""Decode authentic original Fortnite 5.41 tree Blueprint and Shrub_05 source.
Resolves Unreal serialized FName Foo#2 -> cooked package Foo_1, and PAK
mount-root differences. All source reads exact SHA1-verified retail entries.
"""
import json,collections,struct
import fortnite_541_r2_material_probe as r2
import fortnite_541_skylight_cube_probe as split
from fortnite_541_material_expression_probe import Catalog
ROOTS=[
 ("main","FortniteGame/Content/Athena/Environments/Blueprints/Athena_Tree_Large_1"),
 ("s3","Environments/Props/Shrubs/Meshes/Shrub_05"),
 ("s2","Environments/Foliage/Meshes/S_WavyGrass_01"),
 ("main","FortniteGame/Content/Athena/Environments/Landscape/Foliage/Athena_SM_WavyGrass_TopologyColor")
]
def prop_dump(cat,data,cap=70):
    props,n=cat.props(data)
    rows=[]
    for name,kind,meta,value in props[:cap]:
        p={"name":name,"kind":kind,"size":len(value),"meta":meta}
        if kind in ("ObjectProperty","ClassProperty") and len(value)==4:
            idx=struct.unpack("<i",value)[0]
            p["value"]=cat.path(idx) if idx else None
            p["package_index"]=idx
        elif kind=="NameProperty" and len(value)==8:
            p["value"]=cat.fname(value)
        elif kind=="ArrayProperty" and len(value)>=4:
            p["count"]=struct.unpack_from("<I",value)[0]
        elif kind=="StructProperty" and len(value)==12:
            p["xyz"]=struct.unpack("<fff",value)
        rows.append(p)
    return rows
def run():
    main=r2.load_index()
    archives={"main":main}
    for n,sha in [("s2","42a45eee280ab70abbb5192b33a5945c119bd82c"),
                  ("s3","27376dab8f8a3488d0d2b5332a2a2da7d28fd73e")]:
        split.URL=f"https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/pakchunk0_{n}-WindowsClient.pak"
        split.INDEX_SHA=sha
        archives[n]=split.source()
    for name,path in ROOTS:
        index=archives[name]
        source={}
        for ext in (".uasset",".uexp",".ubulk"):
            if path+ext not in index:continue
            read=r2.source_payload if name=="main" else split.payload
            if name!="main":
                split.URL=f"https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/pakchunk0_{name}-WindowsClient.pak"
            raw=read(index[path+ext])
            source[ext]=raw
        doc={"package":path,"archive":name,"source_bytes":{k:len(v) for k,v in source.items()}}
        if ".uasset" in source and ".uexp" in source:
            cat=Catalog(source[".uasset"],source[".uexp"])
            doc["exports"]=[]
            for i,ex in enumerate(cat.exports,1):
                item={"index":i,"name":cat.value(i),"class":cat.class_name(ex),"bytes":ex["size"]}
                try:
                    data=cat.export_data(ex)
                    props,end=cat.props(data)
                    item["props"]=prop_dump(cat,data)
                    item["native_bytes"]=len(data)-end
                    item["native_head"]=data[end:end+80].hex()
                except Exception as e:item["error"]=str(e)
                doc["exports"].append(item)
        print("FORTNITE_AUTHENTIC_TREES_AND_SHRUBS "+json.dumps(doc),flush=True)
if __name__=="__main__":run()
