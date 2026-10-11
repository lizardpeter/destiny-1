#!/usr/bin/env python3
"""Inventory original Fortnite 5.41 foliage sources, actor classes and exports.

All file contents are SHA1 checked via the original R2 PAK. Metadata only.
"""
import collections,json,struct
from pathlib import Path
import fortnite_541_r2_material_probe as r2
from fortnite_541_material_expression_probe import Catalog
FOLIAGE_WORDS=("foliage","grass","tree","bush","shrub","hedge","fern","pine","leaf","plant","vegetation","forest","instanced")
def run():
    ix=r2.load_index()
    umaps=[key for key in ix if key.endswith(".umap") and
        ("Athena" in key or "Maps/Background" in key)]
    foliage_files=[k for k in ix if any(w in k.lower() for w in FOLIAGE_WORDS)
        and k.endswith((".uasset",".umap"))]
    report={"all_athena_umaps":len(umaps),
        "athena_umap_paths":sorted(umaps)[:135],
        "foliage_source_packages":len(foliage_files),
        "foliage_source_samples":sorted(foliage_files)[:100],
        "foliage_related_umaps":[k for k in umaps if any(w in k.lower() for w in FOLIAGE_WORDS)][:60]}
    print("FORTNITE_SOURCE_FOLIAGE_PAK_INDEX "+json.dumps(report),flush=True)
    candidates=[
        "/Maps/Athena_Terrain",
        "/Maps/Background/Athena_Background",
        "/Maps/Landscape/Athena_Terrain_LS_00",
        "/Maps/Landscape/Athena_Terrain_LS_01",
    ]
    for suffix in report["foliage_related_umaps"][:7]:
        name=suffix.removesuffix(".umap")
        if name not in candidates:candidates.append(name)
    output=[]
    for suffix in candidates:
        pair={}
        for ext in (".umap",".uexp"):
            matches=[(key,v) for key,v in ix.items() if key.endswith(suffix+ext)]
            if len(matches)!=1:break
            pair[ext]=matches[0]
        if len(pair)!=2:continue
        try:
            cat=Catalog(r2.source_payload(pair[".umap"][1]),
                        r2.source_payload(pair[".uexp"][1]))
            counts=collections.Counter(cat.class_name(ex) for ex in cat.exports)
            objects=[]
            for i,ex in enumerate(cat.exports,1):
                kind=cat.class_name(ex)
                if not any(x in kind.lower() for x in FOLIAGE_WORDS):
                    continue
                row={"class":kind,"object":cat.path(i),"bytes":ex["size"]}
                try:
                    fields,pos=cat.props(cat.export_data(ex))
                    row["fields"]=[]
                    for key,typ,meta,raw in fields:
                        val={"name":key,"type":typ,"nbytes":len(raw)}
                        if typ=="ObjectProperty" and len(raw)==4:
                            ref=struct.unpack("<i",raw)[0]
                            val["ref"]=cat.path(ref) if ref else None
                        elif typ in ("MapProperty","ArrayProperty","StructProperty","SetProperty"):
                            val["header_first_60"]=raw[:60].hex()
                        elif typ=="IntProperty" and len(raw)==4:
                            val["val"]=struct.unpack("<i",raw)[0]
                        row["fields"].append(val)
                except Exception as e:row["error"]=str(e)
                objects.append(row)
            x={"source_map":suffix,"exports":len(cat.exports),
                "class_counts":counts.most_common(30),
                "foliage_objects":objects[:15]}
            output.append(x)
            print("FORTNITE_SOURCE_FOLIAGE_MAP "+json.dumps(x),flush=True)
        except Exception as e:
            print("FORTNITE_SOURCE_FOLIAGE_MAP_FAILED "+json.dumps({"source_map":suffix,"error":str(e)}),flush=True)
    Path("fortnite541_authored_foliage_audit.json").write_text(json.dumps({"index":report,"maps":output},indent=2))
if __name__=="__main__":run()
