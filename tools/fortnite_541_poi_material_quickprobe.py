#!/usr/bin/env python3
"""Source authentic fast material-slot sample on first five direct Factory meshes."""
import collections,json,struct
import fortnite_541_r2_material_probe as main
import fortnite_541_skylight_cube_probe as split
from fortnite_541_material_expression_probe import Catalog
from fortnite_541_all_poi_coverage import ROOT,SPLITS,actor_inventory,checked_package
WORLD=ROOT+"Athena/Maps/POI/Athena_POI_ToiletFactory_001"
def run():
    ix=main.load_index()
    c=Catalog(main.source_payload(ix[WORLD+".umap"]),
              main.source_payload(ix[WORLD+".uexp"]))
    total,direct,inherited,errors=actor_inventory(c)
    paths=list(dict.fromkeys(obj for obj,_ in direct))
    split.URL=("https://r2.houseofkublai.com/Fortnite/5.41/"
               "FortniteGame/Content/Paks/pakchunk0_s3-WindowsClient.pak")
    split.INDEX_SHA=dict(SPLITS)["s3"]
    s3=split.source()
    found=[]
    for identity in paths:
        package=checked_package(identity.split("::")[0],".uasset")
        if package is None:continue
        base=package[:-7].removeprefix(ROOT)
        if base+".uasset" not in s3 or base+".uexp" not in s3:continue
        c=Catalog(split.payload(s3[base+".uasset"]),split.payload(s3[base+".uexp"]))
        obj=identity.split("::")[-1]
        exports=[e for i,e in enumerate(c.exports,1) if
                 c.class_name(e)=="StaticMesh" and c.value(i)==obj]
        if not exports:continue
        ex=exports[0]
        fields,off=c.props(c.export_data(ex))
        tags=[]
        for name,kind,meta,raw in fields:
            if name in ("StaticMaterials","Materials","MaterialSlotName","SectionInfoMap"):
                tags.append({"name":name,"kind":kind,"meta":meta,"bytes":len(raw),
                    "head":raw[:110].hex()})
        found.append({"mesh":identity,"tags":tags,
            "all_tags":[f[0] for f in fields],
            "imports":[c.path(-i) for i in range(1,min(len(c.imports),60)+1)
                if "Material" in c.path(-i)][:35],
            "native_bytes":len(c.export_data(ex))-off})
        if len(found)>=8:break
    print("FORTNITE_DIRECT_DETAIL_MATERIAL_SAMPLE "+json.dumps(
        {"source_world_count":total,"direct":len(direct),"sample":found},
         sort_keys=True),flush=True)
if __name__=="__main__":run()
