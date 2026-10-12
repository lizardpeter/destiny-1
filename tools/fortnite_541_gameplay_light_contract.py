#!/usr/bin/env python3
"""Audit the true source lighting activation contract of original Athena worlds.

A cooked PointLightComponent's presence is NOT evidence it is active during
normal gameplay. Record original visibility, actor ownership, light settings
and transform fields before passing anything to the neutral renderer.
"""
import json,struct,collections
from fortnite_541_material_expression_probe import Catalog
import fortnite_541_r2_material_probe as source
BASE="FortniteGame/Content/Athena/Maps/Streaming/Athena_GameplayActors"
FIELDS=("Intensity","LightColor","AttenuationRadius","SourceRadius",
        "RelativeLocation","RelativeRotation","RelativeScale3D",
        "bVisible","bHiddenInGame","bAffectsWorld","CastShadows",
        "bCastShadows","bUseInverseSquaredFalloff","Mobility","ComponentToWorld",
        "RootComponent","LightComponent","bEnabled","bAutoActivate",
        "bUseTemperature","Temperature","LightFalloffExponent")
def literal(cat,name,typ,meta,raw):
    item={"name":name,"type":typ,"meta":meta,"bytes":len(raw)}
    if typ=="FloatProperty" and len(raw)==4:
        item["value"]=struct.unpack("<f",raw)[0]
    elif typ=="BoolProperty":
        item["value"]=meta
    elif typ=="IntProperty" and len(raw)==4:
        item["value"]=struct.unpack("<i",raw)[0]
    elif typ in ("ObjectProperty","ClassProperty") and len(raw)==4:
        ref=struct.unpack("<i",raw)[0]
        item["ref"]=ref
        item["source"]=cat.path(ref) if ref else None
    elif typ=="StructProperty" and len(raw) in (3,4,12,16):
        item["data"]=raw.hex()
        if len(raw)==12:item["floats"]=list(struct.unpack("<3f",raw))
    return item
def run():
    ix=source.load_index()
    cat=Catalog(source.source_payload(ix[BASE+".umap"]),source.source_payload(ix[BASE+".uexp"]))
    groups=collections.Counter()
    examples=[]
    counts=collections.Counter()
    ownership=collections.Counter()
    allrows=[]
    for i,ex in enumerate(cat.exports,1):
        if cat.class_name(ex)!="PointLightComponent":continue
        fields,_=cat.props(cat.export_data(ex))
        row={"object":cat.path(i),"export":i,
             "authored_fields":[literal(cat,*entry) for entry in fields if entry[0] in FIELDS],
             "all_source_field_names":[entry[0] for entry in fields]}
        for field in row["authored_fields"]:counts[field["name"]]+=1
        owner=row["object"].split("::")
        subgroup=owner[-2] if len(owner)>2 else row["object"]
        family=subgroup.split("#")[0].rstrip("0123456789_")
        groups[family]+=1
        ownership[subgroup]+=1
        allrows.append(row)
    for row in allrows:
        if len(examples)<12 or any(
            f["name"] in ("Intensity","bVisible","bHiddenInGame") for f in row["authored_fields"]
        ) and len(examples)<35:
            examples.append(row)
    print("FORTNITE_541_AUTHENTIC_GAMEPLAY_LIGHT_CONTRACT "+json.dumps({
        "source_map":BASE,"point_light_count":len(allrows),
        "original_properties":counts.most_common(),
        "owner_families":groups.most_common(40),
        "source_examples":examples,
        "all_pointlight_objects":[r["object"] for r in allrows],
    },sort_keys=True),flush=True)
if __name__=="__main__":run()
