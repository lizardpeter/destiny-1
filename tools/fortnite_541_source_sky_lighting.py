#!/usr/bin/env python3
"""Read source-authentic sky dome parameter values and authored light/fog actors.
Retail SHA1 verified PAK payloads only. Emits metadata, not game assets.
"""
import json,struct
from pathlib import Path
import fortnite_541_r2_material_probe as main
import fortnite_541_skylight_cube_probe as split
from fortnite_541_material_expression_probe import Catalog

PREFIX="Packages/Fortress_Sky/SkyDome/MaterialInstances/SkyDomeBasic01/"
ASSETS=["Morn_M_SkyDome_Inst_Basic01","Day_M_SkyDome_Inst_Basic01"]
KEYWORDS=("sun","sky","atmosphere","fog","cloud","light","day","dome")
def vecs(cat,data):
    if len(data)<4:raise ValueError("truncated source SkyDome parameter array")
    count=struct.unpack_from("<I",data)[0]
    if count>128:raise ValueError("unbounded source SkyDome parameters")
    marker=struct.pack("<II",cat.names.index("None"),0)
    fields,used=cat.props(data[4:]+marker)
    if len(fields)!=1 or fields[0][1]!="StructProperty":
        raise ValueError("source SkyDome array lacks UE4 StructProperty aggregate")
    inner=fields[0][3]
    cursor=0
    parameters=[]
    for i in range(count):
        if cursor>=len(inner):
            raise ValueError("source SkyDome parameter struct stream prematurely ended")
        record,nbytes=cat.props(inner[cursor:]+marker)
        if nbytes<=0:raise ValueError("source SkyDome parameter did not advance")
        cursor+=nbytes
        props={name:(kind,raw) for name,kind,metadata,raw in record}
        pi=props.get("ParameterInfo")
        if not pi or pi[0]!="StructProperty":
            raise ValueError("SkyDome parameter missing typed ParameterInfo")
        inner_fields,nread=cat.props(pi[1]+marker)
        name_fields=[cat.fname(raw) for name,kind,meta,raw in inner_fields
                     if name=="Name" and kind=="NameProperty" and len(raw)==8]
        if len(name_fields)!=1:raise ValueError("source SkyDome parameter FName ambiguous")
        v=props.get("ParameterValue")
        if v is None:raise ValueError("original SkyDome parameter Value absent")
        if v[0]=="FloatProperty" and len(v[1])==4:
            value=struct.unpack("<f",v[1])[0]
        elif v[0]=="StructProperty" and len(v[1])==16:
            value=list(struct.unpack("<ffff",v[1]))
        else:raise ValueError("source sky parameter contains unsupported typed value")
        parameters.append({"name":name_fields[0],"value":value})
    return {"count":count,"parameters":parameters,"source_bytes":len(inner),
            "used_source_bytes":cursor,"outer_consumed":used}

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
        hbytes=split.payload(hdr)
        ebytes=split.payload(exp)
        # Reuse the exact SHA1-verified retail input for the identical
        # production Rust reader. The original files live only in CI /tmp.
        target=Path("/tmp/fortnite541_source_sky/FortniteGame/Content")/source
        target.parent.mkdir(parents=True,exist_ok=True)
        target.with_suffix(".uasset").write_bytes(hbytes)
        target.with_suffix(".uexp").write_bytes(ebytes)
        cat=Catalog(hbytes,ebytes)
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
