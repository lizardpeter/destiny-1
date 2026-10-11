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
        "/Maps/Athena_Streaming_Grid",
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
                if not any(x in kind.lower() for x in FOLIAGE_WORDS) and not kind.startswith("LevelStreaming"):
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
    # Deep source check: the *cooked native tails* are critical. Unreal's
    # serialized FoliageInstancedStaticMeshComponent may omit its placement
    # arrays from ordinary tagged properties.
    for suffix in ["/Maps/Athena_Terrain","/Maps/Landscape/Athena_Terrain_LS_01",
                   "/Maps/POI/Athena_POI_HedgeMaze",
                   "/Maps/Athena_Streaming_Grid"]:
        paths={}
        for ext in (".umap",".uexp"):
            candidates=[v for k,v in ix.items() if k.endswith(suffix+ext)]
            if len(candidates)!=1:continue
            paths[ext]=candidates[0]
        if len(paths)!=2:continue
        cat=Catalog(r2.source_payload(paths[".umap"]),r2.source_payload(paths[".uexp"]))
        rows=[]
        for i,ex in enumerate(cat.exports,1):
            cls=cat.class_name(ex)
            if cls not in ("FoliageInstancedStaticMeshComponent","InstancedStaticMeshComponent",
                "InstancedFoliageActor","LevelStreamingAlwaysLoaded","LevelStreamingDynamic",
                "LF_Athena_POI_80x80_C",
                "StaticMeshComponent",
                "Athena_Tree_Large_1_C","Athena_Prop_Plant_Shrub_01_C"):
                continue
            owner=cat.path(i)
            if cls=="StaticMeshComponent" and not any(k in owner for k in
                ("Tree_Large","Plant_Shrub","Foliage")):
                continue
            raw=cat.export_data(ex)
            try:fields,used=cat.props(raw)
            except Exception as e:
                rows.append({"class":cls,"object":owner,"error":str(e)});continue
            props=[]
            for name,kind,meta,blob in fields:
                if (cls=="InstancedFoliageActor" or kind=="ObjectProperty" or
                    name in ("PerInstanceSMData","InstanceReorderTable",
                             "PerInstanceSMCustomData","InstancingRandomSeed",
                             "StaticMesh","RelativeLocation","RelativeRotation",
                             "RelativeScale3D","BodyInstance")):
                    field={"name":name,"kind":kind,"bytes":len(blob)}
                    if kind=="ObjectProperty" and len(blob)==4:
                        ref=struct.unpack("<i",blob)[0]
                        field["value"]=cat.path(ref) if ref else None
                    if kind=="StructProperty" and len(blob)==12:
                        field["xyz"]=struct.unpack("<fff",blob)
                    if kind=="ArrayProperty":
                        field["head"]=blob[:128].hex()
                    props.append(field)
            if cls in ("FoliageInstancedStaticMeshComponent","InstancedStaticMeshComponent"):
                tail=raw[used:]
                if len(tail)>=20:
                    count=struct.unpack_from("<I",tail,16)[0]
                    stride=struct.unpack_from("<I",tail,12)[0]
                    if stride in (16,32,48,64,80) and count<200000:
                        matrices=[]
                        for off in (20,20+stride,20+(count//2)*stride,20+(count-1)*stride,20+count*stride):
                            if off>=0 and off+64<=len(tail):
                                matrices.append({"relative_byte":off,"16f":struct.unpack_from("<16f",tail,off),
                                "16u32":struct.unpack_from("<16I",tail,off)})
                        rows.append({"kind":"verified_native_instance_buffer_candidate",
                            "class":cls,"object":owner,"header_u32":struct.unpack_from("<5I",tail),
                            "instance_count":count,"stride":stride,
                            "estimated_data_end":20+count*stride,
                            "native_tail_bytes":len(tail),"sample":matrices})
            rows.append({"class":cls,"object":owner,
                "total_bytes":len(raw),"native_tail_bytes":len(raw)-used,
                "native_head":raw[used:used+160].hex(),
                "native_last":raw[-96:].hex(),
                "props":props})
        o={"map":suffix,"candidates":len(rows),"objects":rows[:40]}
        print("FORTNITE_AUTHENTIC_FOLIAGE_NATIVE_SERIAL "+json.dumps(o),flush=True)
    roots=["Athena/Environments/Landscape/Foliage/Athena_SM_WavyGrass_TopologyColor",
           "Environments/Foliage/Meshes/S_WavyGrass_01"]
    for root in roots:
        pref="FortniteGame/Content/"+root
        print("FORTNITE_AUTHENTIC_FOLIAGE_ASSET "+json.dumps({
            "path":pref,"source_entries":[{"ext":e,"bytes":ix[pref+e][2]}
                for e in (".uasset",".uexp",".ubulk") if pref+e in ix]
        }),flush=True)
    Path("fortnite541_authored_foliage_audit.json").write_text(json.dumps({"index":report,"maps":output},indent=2))
if __name__=="__main__":run()
