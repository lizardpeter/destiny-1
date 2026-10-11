#!/usr/bin/env python3
"""Read original 5.41 world managers, named POI placement and level streams.
Original retail SHA1-authenticated source UObject properties only; no world
positions or tile origins are inferred from place names.
"""
import json,collections,struct
from pathlib import Path
import fortnite_541_r2_material_probe as r2
from fortnite_541_material_expression_probe import Catalog
MAPS=[
 "Athena/Maps/Athena_Terrain",
 "Athena/Maps/Athena_Streaming_Grid",
 "Athena/Maps/Athena_POI_Foundations",
 "Athena/Maps/Athena_LocationVolumes",
 "Athena/Maps/Athena_ForagedItems",
 "Athena/Maps/Athena_Playground",
 "Athena/Maps/POI/Athena_POI_HedgeMaze",
]
def detail(cat,ex,i):
    obj=cat.export_data(ex)
    props,consumed=cat.props(obj)
    fields=[]
    for key,kind,extra,raw in props:
        row={"name":key,"kind":kind,"bytes":len(raw)}
        if kind in ("ObjectProperty","ClassProperty") and len(raw)==4:
            n=struct.unpack("<i",raw)[0]
            row["target"]=cat.path(n) if n else None
        elif kind=="StructProperty" and len(raw)==12:
            row["xyz"]=list(struct.unpack("<fff",raw))
            row["struct_kind"]=extra[:1]
        elif kind=="ArrayProperty" and len(raw)>=4:
            row["count"]=struct.unpack_from("<I",raw)[0]
            row["first40"]=raw[:40].hex()
        elif kind in ("NameProperty","SoftObjectProperty","StrProperty"):
            row["first40"]=raw[:40].hex()
        elif kind=="IntProperty" and len(raw)==4:
            row["value"]=struct.unpack("<i",raw)[0]
        fields.append(row)
    return {"index":i,"class":cat.class_name(ex),"path":cat.path(i),"fields":fields,
        "source_native_bytes":len(obj)-consumed,
        "native_head":obj[consumed:consumed+160].hex()}
def run():
    index=r2.load_index()
    for mapname in MAPS:
        prefix="FortniteGame/Content/"+mapname
        if prefix+".umap" not in index or prefix+".uexp" not in index:
            print("FORTNITE_AUTHORED_POI_MAP_ABSENT "+json.dumps({"map":mapname}),flush=True)
            continue
        catalog=Catalog(r2.source_payload(index[prefix+".umap"]),
                        r2.source_payload(index[prefix+".uexp"]))
        classes=collections.Counter(catalog.class_name(e) for e in catalog.exports)
        mentions=[n for n in catalog.names if any(q in n.lower() for q in
            ("hedge","wailing","stream","tile","pois","worldcomposition","poi_"))]
        rows=[]
        for i,e in enumerate(catalog.exports,1):
            cls=catalog.class_name(e)
            if cls in ("FortWorldManager","WorldTileManager","FortWorldSettings",
                "World","Level","LevelStreamingAlwaysLoaded","LevelStreamingDynamic",
                "FortWorldComposition","LandscapeStreamingProxy","FortLevelStreamingDynamic",
                "FortLevelStreamingAlwaysLoaded") or any(
                q in cls.lower() for q in ("foundation","locationvolume","foraged")
            ):
                try:rows.append(detail(catalog,e,i))
                except Exception as err:rows.append({"class":cls,"index":i,"error":str(err)})
        info={"source":mapname,"exports":len(catalog.exports),
            "classes":classes.most_common(60),
            "matched_source_names":mentions[:150],
            "matched_names_total":len(mentions),
            "world_actors":rows[:36]}
        print("FORTNITE_ORIGINAL_POI_WORLD_MAP "+json.dumps(info),flush=True)
if __name__=="__main__":run()
