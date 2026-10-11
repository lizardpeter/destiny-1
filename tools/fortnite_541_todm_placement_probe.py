#!/usr/bin/env python3
"""Find the authored Athena TODM_BR actor/root placement, fog height and sun source.

The original time-of-day class CDO provides HeightFogZOffset but not a
verified world-space anchor. Only source scene actor/root transforms can
justify applying that height to a universal exponential fog renderer.
"""
import json,struct
import fortnite_541_r2_material_probe as original
from fortnite_541_material_expression_probe import Catalog
import fortnite_541_skylight_cube_probe as split
from fortnite_541_all_poi_coverage import SPLITS

WORLD_PATHS=(
    "Athena/Maps/Athena_Terrain",
    "Athena/Maps/Athena_GameplayActors",
    "Athena/Maps/Athena_Streaming_Grid",
    "Athena/Maps/Athena_POI_Foundations",
    "Athena/Maps/Background/Athena_Background",
)
def typed_fields(c,ex):
    props,end=c.props(c.export_data(ex))
    result=[]
    for name,kind,meta,raw in props:
        row={"name":name,"kind":kind,"meta":meta,"len":len(raw)}
        if kind in ("ObjectProperty","ClassProperty") and len(raw)==4:
            ref=struct.unpack("<i",raw)[0]
            row["ref"]=ref
            row["target"]=c.path(ref) if ref else None
        elif kind=="StructProperty" and len(raw)==12:
            row["xyz"]=list(struct.unpack("<fff",raw))
        elif kind=="FloatProperty" and len(raw)==4:
            row["value"]=struct.unpack("<f",raw)[0]
        elif kind=="BoolProperty":
            row["value"]=meta
        result.append(row)
    return result,end
def inspect(ix,base,reader=original.source_payload,prefix="FortniteGame/Content/"):
    source=prefix+base
    if source+".umap" not in ix or source+".uexp" not in ix:
        return {"map":base,"error":"original world not in selected authenticated archive"}
    c=Catalog(reader(ix[source+".umap"]),reader(ix[source+".uexp"]))
    identified=[]
    for i,e in enumerate(c.exports,1):
        typ=c.class_name(e)
        name=c.value(i)
        if not any(x in (typ+" "+name).lower() for x in
                   ("todm","timeofday","daynight","exponentialheightfog","directionallight",
                    "skyatmosphere")):
            continue
        data={"class":typ,"name":name,"object":c.path(i),"export":i}
        try:
            props,used=typed_fields(c,e)
            data["properties"]=props
            # Follow source actor root pointers into its ORIGINAL exported
            # scene component rather than inventing a class CDO transform.
            refs=[x for x in props if x["name"] in
                  ("RootComponent","DirectionalLightComponent",
                   "ActiveHeightFogComponent","SkyLightComp")]
            components=[]
            for ref in refs:
                number=ref.get("ref")
                if isinstance(number,int) and 0<number<=len(c.exports):
                    attached=c.exports[number-1]
                    try:
                        cp,cu=typed_fields(c,attached)
                        components.append({"object":c.path(number),
                            "class":c.class_name(attached),
                            "fields":cp})
                    except Exception as err:
                        components.append({"object":c.path(number),"error":str(err)})
            data["root_components"]=components
        except Exception as err:data["error"]=str(err)
        identified.append(data)
    return {"map":base,"exports":len(c.exports),"references":identified}
def run():
    ix=original.load_index()
    incomplete=[]
    for name in WORLD_PATHS:
        out=inspect(ix,name)
        if "error" in out:incomplete.append(name)
        out["source_archive"]="main"
        print("FORTNITE_541_AUTHORED_TODM_SUN_FOG_PLACEMENT "+
              json.dumps(out,sort_keys=True),flush=True)
    for archive,sha in SPLITS:
        if not incomplete:break
        filename=("pakchunk1-WindowsClient.pak" if archive=="chunk1"
                  else f"pakchunk0_{archive}-WindowsClient.pak")
        split.URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/"+filename
        split.INDEX_SHA=sha
        entries=split.source()
        remaining=[]
        for name in incomplete:
            selected=None
            for prefix in ("","FortniteGame/Content/"):
                path=prefix+name
                if path+".umap" in entries and path+".uexp" in entries:
                    selected=inspect(entries,name,reader=split.payload,prefix=prefix)
                    break
            if selected is None:remaining.append(name)
            else:
                selected["source_archive"]=archive
                print("FORTNITE_541_AUTHORED_TODM_SUN_FOG_PLACEMENT "+
                      json.dumps(selected,sort_keys=True),flush=True)
        incomplete=remaining
    print("FORTNITE_541_UNAVAILABLE_ROOT_STREAMS "+json.dumps(incomplete),flush=True)
if __name__=="__main__":run()
