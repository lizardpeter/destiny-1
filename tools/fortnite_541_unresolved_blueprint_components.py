#!/usr/bin/env python3
"""Investigate real missing source component inheritance behind 100 shrubs.

The original Athena_POI CDO parser only follows directly owned root
StaticMeshComponent pointers. Audit exact original Blueprint source classes
and all exported child StaticMeshComponent/ChildActorComponent templates
before changing the canonical importer.
"""
import json,collections,struct
import fortnite_541_r2_material_probe as src
from fortnite_541_material_expression_probe import Catalog
PATHS=(
    "Athena/BuildingActors/Props/Building/ActorBlueprints/Containers/Athena_Prop_Plant_Shrub_01",
    "Building/ActorBlueprints/Containers/Plant_Shrub_01",
    "Packages/Fortress_Transylvania/Test_Assets/Blueprints/ArtificialLights/BP_TRV_ALight_Torch_02",
    "Athena/Environments/Blueprints/LF_7x12_GenericPlot",
)
def props(cat,ex):
    try:
        fields,end=cat.props(cat.export_data(ex))
        tags=[]
        for n,k,meta,raw in fields:
            row={"name":n,"kind":k,"meta":meta,"len":len(raw)}
            if k in ("ObjectProperty","ClassProperty") and len(raw)==4:
                ref=struct.unpack_from("<i",raw)[0]
                row["object"]=cat.path(ref) if ref else None
                row["raw_ref"]=ref
            elif k=="NameProperty" and len(raw)==8:
                row["name_value"]=cat.fname(raw)
            elif k=="ArrayProperty" and len(raw)>=4:
                row["count"]=struct.unpack_from("<I",raw)[0]
            tags.append(row)
        return tags
    except Exception as e:return [{"error":str(e)}]
def run():
    ix=src.load_index()
    for base in PATHS:
        prefix="FortniteGame/Content/"+base
        if prefix+".uasset" not in ix or prefix+".uexp" not in ix:
            print("FORTNITE_AUTHORED_MISSING_CDO "+json.dumps({"source":base,"not_in_main":True}),flush=True)
            continue
        cat=Catalog(src.source_payload(ix[prefix+".uasset"]),
                    src.source_payload(ix[prefix+".uexp"]))
        classes=collections.Counter(cat.class_name(e) for e in cat.exports)
        objects=[]
        for i,e in enumerate(cat.exports,1):
            kind=cat.class_name(e)
            full=cat.path(i)
            if not (
                "StaticMeshComponent" in kind or "ChildActorComponent" in kind
                or "SimpleConstructionScript" in kind or "SceneComponent" in kind
                or "InheritableComponentHandler" in kind
                or "Default__" in full or "ActorComponent" in kind
                or kind.endswith("_C")
            ):continue
            objects.append({"index":i,"class":kind,"name":cat.value(i),
                "outer":cat.path(e["outer"]) if e["outer"] else None,
                "path":full,"properties":props(cat,e)})
        print("FORTNITE_AUTHORED_MISSING_CDO "+json.dumps({
            "source":base,"export_count":len(cat.exports),
            "export_class_census":classes.most_common(25),
            "candidate_objects":objects[:120],
            "candidate_count":len(objects),
        },sort_keys=True),flush=True)
if __name__=="__main__":run()
