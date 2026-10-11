#!/usr/bin/env python3
"""Read source-authentic sky dome parameter values and authored light/fog actors.
Retail SHA1 verified PAK payloads only. Emits metadata, not game assets.
"""
import json,struct
import fortnite_541_r2_material_probe as main
import fortnite_541_skylight_cube_probe as split
from fortnite_541_material_expression_probe import Catalog

PREFIX="Packages/Fortress_Sky/SkyDome/MaterialInstances/SkyDomeBasic01/"
ASSETS=["Morn_M_SkyDome_Inst_Basic01","Day_M_SkyDome_Inst_Basic01"]
KEYWORDS=("sun","sky","atmosphere","fog","cloud","light","day","dome")
def vecs(data):
    if len(data)<4:return {"bytes":len(data)}
    count=struct.unpack_from("<I",data)[0]
    for stride in (32,48):
        if count<256 and len(data)==4+stride*count:
            vals=[]
            for i in range(count):
                start=4+i*stride
                vals.append({"raw_first_16":data[start:start+16].hex(),
                   "f32":list(struct.unpack_from("<f"*(1 if stride==32 else 4),data,start+16)),
                   "guid":data[start+stride-16:start+stride].hex()})
            return {"count":count,"stride":stride,"values":vals}
    return {"count":count,"length":len(data),"head":data[:96].hex()}
def map_scene(index,root):
    header=main.source_payload(index[root+".umap"])
    exp=main.source_payload(index[root+".uexp"])
    cat=Catalog(header,exp)
    rows=[]
    for i,obj in enumerate(cat.exports,1):
        cls=cat.class_name(obj); name=cat.value(i)
        if not any(k in (cls+" "+name).lower() for k in KEYWORDS):continue
        fields,at=cat.props(cat.export_data(obj))
        properties=[]
        for n,k,meta,raw in fields:
            item={"name":n,"kind":k,"size":len(raw)}
            if k=="ObjectProperty" and len(raw)==4:
                ref=struct.unpack("<i",raw)[0]
                item["target"]=cat.path(ref) if ref else None
            elif k=="StructProperty" and len(raw)==12:
                item["xyz"]=list(struct.unpack("<fff",raw))
            elif k=="StructProperty" and len(raw)==16:
                item["values"]=list(struct.unpack("<ffff",raw))
            elif k=="FloatProperty" and len(raw)==4:
                item["value"]=struct.unpack("<f",raw)[0]
            elif k=="BoolProperty": item["flags"]=meta
            properties.append(item)
        rows.append({"export":i,"class":cls,"name":name,
            "source_path":cat.path(i),"properties":properties})
    print("FORTNITE_SOURCE_SKY_LIGHT_MAP "+json.dumps({
        "map":root,"rows":rows},sort_keys=True),flush=True)

def sky_materials(entries):
    for label in ASSETS:
        source=PREFIX+label
        hdr=next((rec for key,rec in entries.items() if key.endswith(source+".uasset")),None)
        exp=next((rec for key,rec in entries.items() if key.endswith(source+".uexp")),None)
        if hdr is None or exp is None:
            raise ValueError("source sky material instance absent "+source)
        cat=Catalog(split.payload(hdr),split.payload(exp))
        rows=[]
        for i,obj in enumerate(cat.exports,1):
            fields,at=cat.props(cat.export_data(obj))
            record={"source":cat.path(i),"class":cat.class_name(obj),
                "property_tags":[]}
            for name,kind,meta,raw in fields:
                tag={"name":name,"kind":kind,"size":len(raw)}
                if name in ("ScalarParameterValues","VectorParameterValues"):
                    tag["entries"]=vecs(raw)
                elif kind=="ObjectProperty" and len(raw)==4:
                    r=struct.unpack("<i",raw)[0]
                    tag["object"]=cat.path(r) if r else None
                record["property_tags"].append(tag)
            rows.append(record)
        print("FORTNITE_SOURCE_DAY_SKY_MATERIAL "+json.dumps({"asset":source,
            "records":rows},sort_keys=True),flush=True)

def main_run():
    main_idx=main.load_index()
    split.URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/pakchunk0_s4-WindowsClient.pak"
    split.INDEX_SHA="96a67f9eae257051576e368fdb61a6fb78b2f56a"
    s4=split.source()
    print("FORTNITE_SKY_SOURCE_ASSETS "+json.dumps([
        name for name in s4 if ("skydome" in name.lower() or "sun" in name.lower())
    ][:250]),flush=True)
    sky_materials(s4)
    for root in ("FortniteGame/Content/Athena/Maps/Athena_Terrain",
                 "FortniteGame/Content/Athena/Maps/Background/Athena_Background",
                 "FortniteGame/Content/Athena/Maps/Athena_GameplayActors"):
        if root+".umap" in main_idx and root+".uexp" in main_idx:
            map_scene(main_idx,root)
if __name__=="__main__":main_run()
