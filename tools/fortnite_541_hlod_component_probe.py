#!/usr/bin/env python3
"""Inventory original Fortnite 5.41 Athena static-mesh/HLOD actor references.

No names inferred, no mesh invented. Validate SHA1 of original root source
before extracting export class, source UObject reference, and actor placement
property metadata. This discovers exactly which retail mesh assets matter.
"""
import json,struct,collections
from pathlib import Path
import fortnite_541_r2_material_probe as r2
from fortnite_541_material_expression_probe import Catalog

SUFFIX="/Maps/Athena_Terrain"
def payload(entries,ext):
    hits=[(name,rec) for name,rec in entries.items() if name.endswith(SUFFIX+ext)]
    if len(hits)!=1:raise ValueError(f"original Athena root {ext}: {len(hits)} matches")
    return r2.source_payload(hits[0][1])
def parse_location(cat,kind,meta,raw):
    if kind=="StructProperty" and len(raw) in (12,16):
        if len(raw)==12:
            return {"f32":list(struct.unpack("<fff",raw)),"struct":meta}
        return {"f32":list(struct.unpack("<ffff",raw)),"struct":meta}
    if kind=="ObjectProperty" and len(raw)==4:
        ref=struct.unpack("<i",raw)[0]
        return {"object_ref":ref,"source_object":cat.path(ref) if ref else None}
    if kind=="ArrayProperty":
        return {"count":struct.unpack_from("<I",raw,0)[0],"bytes":len(raw)}
    if kind=="BoolProperty":return {"source_bool":meta}
    if kind=="FloatProperty" and len(raw)==4:return struct.unpack("<f",raw)[0]
    if kind=="IntProperty" and len(raw)==4:return struct.unpack("<i",raw)[0]
    return {"bytes":len(raw)}
def run():
    entries=r2.load_index()
    head,comp=payload(entries,".umap"),payload(entries,".uexp")
    cat=Catalog(head,comp)
    counts=collections.Counter()
    refs=collections.Counter()
    meshes=[]
    actors=[]
    propcounts=collections.Counter()
    failures=[]
    for number,exp in enumerate(cat.exports,1):
        kind=cat.class_name(exp)
        counts[kind]+=1
        if kind not in ("StaticMeshComponent","FortHLODSMActor","FortStaticMeshActor","SceneComponent"):continue
        item={"index":number,"class":kind,"object":cat.path(number)}
        try:
            props,end=cat.props(cat.export_data(exp))
            item["properties"]={}
            for prop,tag_type,meta,raw in props:
                propcounts[(kind,prop,tag_type)]+=1
                if prop in ("StaticMesh","RootComponent","AttachParent","RelativeLocation",
                    "RelativeRotation","RelativeScale3D","ComponentToWorld",
                    "StaticMeshComponent","StaticMeshComponents","HLODStaticMesh",
                    "ActorLabel","LODIndex","bVisible","bHiddenInGame","Mobility","UniqueWorldLocation",
                    "OverrideMaterials","Tags","StaticMesh"):
                    item["properties"][prop]=parse_location(cat,tag_type,meta,raw)
                    if prop=="StaticMesh" and len(raw)==4:
                        ref=struct.unpack("<i",raw)[0]
                        refs[cat.path(ref) if ref else "null"]+=1
            if kind=="StaticMeshComponent":
                meshes.append(item)
            else:actors.append(item)
        except Exception as e:
            failures.append({"object":item["object"],"error":str(e)})
    asset_names=[]
    for name,count in refs.most_common():
        if not name.startswith("/Game/"):continue
        pkg=name.split("::",1)[0].replace("/Game/","FortniteGame/Content/",1)
        asset_names.append({"source_package":pkg,"used_by":count,
            "in_main_pak_uasset":pkg+".uasset" in entries,
            "in_main_pak_uexp":pkg+".uexp" in entries,
            "in_main_pak_ubulk":pkg+".ubulk" in entries})
    mesh_asset=None
    for obj in asset_names:
        if not obj["in_main_pak_uasset"] or not obj["in_main_pak_uexp"]:continue
        pkg=obj["source_package"]
        ah=r2.source_payload(entries[pkg+".uasset"])
        ae=r2.source_payload(entries[pkg+".uexp"])
        ac=Catalog(ah,ae)
        mesh_asset={"source_package":pkg,"header_bytes":len(ah),"export_bytes":len(ae),
            "export_classes":[{"index":i,"class":ac.class_name(exp),"name":ac.value(i),
                "serialized_bytes":exp["size"]} for i,exp in enumerate(ac.exports,1)][:12]}
        for ex in ac.exports:
            if ac.class_name(ex)=="StaticMesh":
                mesh_bytes=ac.export_data(ex)
                props,end=ac.props(mesh_bytes)
                mesh_asset["static_mesh_properties"]=[
                    {"name":n,"type":kind,"byte_count":len(raw)}
                    for n,kind,extra,raw in props]
                mesh_asset["native_render_payload_bytes"]=len(mesh_bytes)-end
                mesh_asset["native_first_256"]=mesh_bytes[end:end+256].hex()
                mesh_asset["native_last_64"]=mesh_bytes[-64:].hex()
                break
        break
    out={"original_map":SUFFIX,"exports":len(cat.exports),
         "referenced_hlod_packages":len(asset_names),
         "referenced_mesh_packages_in_original_main_pak":sum(
            1 for a in asset_names if a["in_main_pak_uasset"] and a["in_main_pak_uexp"]),
         "sample_mesh_package_presence":asset_names[:16],
         "verified_sample_mesh_package":mesh_asset,
         "classes":dict(counts),"static_mesh_components":len(meshes),
         "hlod_actors":sum(x["class"]=="FortHLODSMActor" for x in actors),
         "unique_static_mesh_refs":len(refs),
         "most_common_source_meshes":refs.most_common(40),
         "property_census":[{"class":a,"name":b,"tag":c,"count":num}
              for (a,b,c),num in propcounts.most_common(45)],
         "component_examples":meshes[:20],"actor_examples":actors[:10],
         "errors":failures[:20]}
    print("FORTNITE_ORIGINAL_HLOD_COMPONENT_AUDIT "+json.dumps(out,sort_keys=True),flush=True)
    Path("fortnite541_hlod_component_audit.json").write_text(json.dumps(out,indent=2))
if __name__=="__main__":run()
