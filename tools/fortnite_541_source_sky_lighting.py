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
def vecs(cat,data):
    if len(data)<4:return {"bytes":len(data)}
    count=struct.unpack_from("<I",data)[0]
    if count>128:raise ValueError("unbounded original sky material parameter count")
    cursor=4
    records=[]
    for i in range(count):
        fields,used=cat.props(data[cursor:])
        if not used:raise ValueError("sky material parameter struct did not advance")
        row=[]
        for name,kind,metadata,raw in fields:
            entry={"name":name,"kind":kind,"size":len(raw)}
            if kind=="FloatProperty" and len(raw)==4:
                entry["value"]=struct.unpack("<f",raw)[0]
            elif kind=="NameProperty" and len(raw)==8:
                entry["value"]=cat.fname(raw)
            elif kind=="StructProperty":
                if len(raw)==16:entry["values"]=list(struct.unpack("<ffff",raw))
                else:
                    try:
                        nested,nused=cat.props(raw)
                        entry["nested"]=[]
                        for n,k,meta,p in nested:
                            v={"name":n,"kind":k,"size":len(p)}
                            if k=="NameProperty" and len(p)==8:v["name_value"]=cat.fname(p)
                            elif k=="FloatProperty" and len(p)==4:v["float"]=struct.unpack("<f",p)[0]
                            elif k=="IntProperty" and len(p)==4:v["int"]=struct.unpack("<i",p)[0]
                            entry["nested"].append(v)
                        entry["nested_consumed"]=nused
                    except Exception:entry["raw_head"]=raw[:40].hex()
            elif kind=="IntProperty" and len(raw)==4:
                entry["value"]=struct.unpack("<i",raw)[0]
            row.append(entry)
        records.append(row)
        cursor+=used
    return {"count":count,"parsed":records,"consumed":cursor,"total":len(data),
            "remaining_bytes":data[cursor:cursor+32].hex()}

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
                    tag["entries"]=vecs(cat,raw)
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
