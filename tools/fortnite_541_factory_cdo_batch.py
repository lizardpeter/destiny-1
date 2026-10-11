#!/usr/bin/env python3
"""Prepare native CDO resolution inputs from SHA1-verified retail Fortnite 5.41.

Use only the exact distinct Blueprint-generated classes actually inherited by
source actor roots in Athena_POI_ToiletFactory_001. Download original CDO
UAsset/UExp from the authenticated main PAK temporarily during a proof run.
No retail assets enter Git.
"""
import collections
import json
from pathlib import Path
import fortnite_541_r2_material_probe as retail
from fortnite_541_material_expression_probe import Catalog
from fortnite_541_all_poi_coverage import actor_inventory,checked_package

WORLD="FortniteGame/Content/Athena/Maps/POI/Athena_POI_ToiletFactory_001"
DEST=Path("/tmp/fortnite541_factory_cdos")
MANIFEST=Path("/tmp/fortnite541_factory_cdos.tsv")

def run():
    ix=retail.load_index()
    c=Catalog(retail.source_payload(ix[WORLD+".umap"]),
              retail.source_payload(ix[WORLD+".uexp"]))
    total,direct,classes,errors=actor_inventory(c)
    if total!=1335 or len(direct)!=186 or sum(classes.values())!=1149:
        raise ValueError(f"Production-scope factory actor census unexpectedly changed: {total} {len(direct)} {sum(classes.values())}")
    DEST.mkdir(parents=True,exist_ok=True)
    lines=[]
    source_files=0
    unavailable=0
    for i,(class_path,n) in enumerate(sorted(classes.items())):
        pkg=checked_package(class_path,".uasset") if class_path.endswith("_C") else None
        base=DEST/str(i)
        if pkg is not None and pkg in ix and pkg[:-7]+".uexp" in ix:
            for extension in (".uasset",".uexp"):
                key=pkg[:-7]+extension
                raw=retail.source_payload(ix[key])
                (DEST/(str(i)+extension)).write_bytes(raw)
                source_files+=1
            lines.append(f"{class_path}\t{n}\t{base}")
        else:
            lines.append(f"{class_path}\t{n}\t")
            unavailable+=1
    MANIFEST.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("FORTNITE_FACTORY_CDO_AUTHENTIC_SOURCE_PREP "+json.dumps({
        "retail_source_actors":total,"direct_mesh_actors":len(direct),
        "inherited_actors":sum(classes.values()),"unique_classes":len(classes),
        "retail_verified_cdo_files":source_files,
        "unavailable_source_classes":unavailable,
        "manifest":str(MANIFEST)
    }),flush=True)
if __name__=="__main__":
    run()
