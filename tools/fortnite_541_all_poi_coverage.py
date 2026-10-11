#!/usr/bin/env python3
"""Authenticated Fortnite 5.41 40-POI source-coverage census.

Reads exact LF_Athena_POI AdditionalWorlds from the retail foundation map.
Parses the same direct StaticMeshComponent-root actor scope as the native
importer. Separates source package presence from successful native decoding;
a found source package is NOT counted as visible renderer geometry.
All PAK indexes and requested payloads are SHA1 checked by existing readers.
No original proprietary payloads are committed or uploaded.
"""
import collections
import json
import struct
from pathlib import Path
import fortnite_541_r2_material_probe as retail
import fortnite_541_skylight_cube_probe as split
from fortnite_541_material_expression_probe import Catalog

ROOT = "FortniteGame/Content/"
SPLITS = [
    ("s1", "a37147494190b90c420b852d69740402f93f6103"),
    ("s2", "42a45eee280ab70abbb5192b33a5945c119bd82c"),
    ("s3", "27376dab8f8a3488d0d2b5332a2a2da7d28fd73e"),
    ("s4", "96a67f9eae257051576e368fdb61a6fb78b2f56a"),
    ("s5", "9f9f8e76d614e080108d2c49d616e9b4bc9affd0"),
    ("chunk1", "b6b32c94f36c35a528d186bcb4a6b5f9bd89255f"),
]

def checked_package(source, suffix):
    # UE4 source FName #N is a numbered package, stored as _{N-1}.
    if not source.startswith("/Game/"):
        return None
    package = source.removeprefix("/Game/").split("::")[0]
    if "#" in package:
        head, _, number = package.rpartition("#")
        if not number.isdigit() or int(number) < 1:
            return None
        package = f"{head}_{int(number)-1}"
    pieces = package.split("/")
    if not pieces or any(not x or x in (".", "..") for x in pieces):
        return None
    if not all(ch.isascii() and (ch.isalnum() or ch in "_-/") for ch in package):
        return None
    return ROOT + package + suffix

def available_chunks(path, indexes):
    if path is None:
        return []
    suffix = Path(path).suffix
    if suffix not in (".uasset", ".umap"):
        raise ValueError("source path must be package header")
    base = path[:-len(suffix)]
    answer = []
    for label, ix in indexes.items():
        if label == "main":
            candidates = (base,)
        else:
            candidates = (base.removeprefix(ROOT), base)
        if any(p + suffix in ix and p + ".uexp" in ix for p in candidates):
            answer.append(label)
    return answer

def field_ref(fields, name):
    refs = [struct.unpack("<i", raw)[0] for n,k,_,raw in fields
            if n == name and k == "ObjectProperty" and len(raw) == 4]
    return refs[0] if len(refs) == 1 else None

def worlds_from_retail_foundations(main):
    key = ROOT + "Athena/Maps/Athena_POI_Foundations"
    c = Catalog(retail.source_payload(main[key+".umap"]),
                retail.source_payload(main[key+".uexp"]))
    worlds = []
    for ex in c.exports:
        if not c.class_name(ex).startswith("LF_Athena_POI_"):
            continue
        props,_ = c.props(c.export_data(ex))
        arrays=[raw for n,k,_,raw in props if n=="AdditionalWorlds"
                and k=="ArrayProperty"]
        # Many LF_Athena_POI_ actors have no AdditionalWorlds at all,
        # matching the native importer; only those with authored references
        # contribute streamed child levels.
        if not arrays:
            continue
        if len(arrays)!=1:
            raise ValueError("ambiguous authored LF AdditionalWorlds array")
        raw=arrays[0]
        if len(raw)<4: raise ValueError("truncated foundation worlds array")
        count=struct.unpack_from("<I",raw)[0]
        if count>16 or len(raw)!=4+12*count:
            raise ValueError("original source SoftObjectPath array layout changed")
        for i in range(count):
            index,number,subpath=struct.unpack_from("<IIi",raw,4+i*12)
            if number or subpath:
                raise ValueError("unsupported numbered AdditionalWorlds path")
            obj=c.name(index)
            if not obj.startswith("/Game/") or "." not in obj:
                raise ValueError(f"authored world path invalid: {obj}")
            src,export=obj.rsplit(".",1)
            if src.rsplit("/",1)[-1]!=export:
                raise ValueError(f"authored world export mismatch: {obj}")
            worlds.append(ROOT + src.removeprefix("/Game/"))
    if len(worlds)!=40 or len(set(worlds))!=40:
        raise ValueError(f"expected exactly 40 unique authored foundations, got {len(worlds)}")
    return worlds

def actor_inventory(cat):
    total=0
    direct=[]
    inherited=collections.Counter()
    errors=collections.Counter()
    for i,actor in enumerate(cat.exports,1):
        kind=cat.class_name(actor)
        if kind=="FortHLODSMActor" or kind.endswith("Component") or kind in ("World","Level"):
            continue
        try:
            fields,_=cat.props(cat.export_data(actor))
        except Exception:
            errors["actor_tagged_properties"]+=1
            continue
        root=field_ref(fields,"RootComponent")
        if root is None or root<=0 or root>len(cat.exports):
            continue
        component=cat.exports[root-1]
        if component["outer"]!=i or cat.class_name(component)!="StaticMeshComponent":
            continue
        total+=1
        try:
            cp,_=cat.props(cat.export_data(component))
        except Exception:
            errors["root_component_properties"]+=1
            continue
        mesh=field_ref(cp,"StaticMesh")
        if mesh:
            try:
                path=cat.path(mesh)
                package=checked_package(path,".uasset")
            except Exception:
                package=None
            if package:
                direct.append((path,package))
                continue
            errors["invalid_direct_mesh_identity"]+=1
        class_path=cat.path(actor["class"])
        inherited[class_path]+=1
    return total,direct,inherited,errors

def run():
    main=retail.load_index()
    worlds=worlds_from_retail_foundations(main)
    indexes={"main":main}
    for label,sha in SPLITS:
        name=("pakchunk1-WindowsClient.pak" if label=="chunk1"
              else f"pakchunk0_{label}-WindowsClient.pak")
        split.URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/"+name
        split.INDEX_SHA=sha
        indexes[label]=split.source()
    rows=[]
    all_classes=collections.Counter()
    all_direct=collections.Counter()
    per_class_archives={}
    for world in worlds:
        if world+".umap" not in main or world+".uexp" not in main:
            rows.append({"world":world,"error":"original POI world package absent from retail main PAK"})
            continue
        try:
            cat=Catalog(retail.source_payload(main[world+".umap"]),
                        retail.source_payload(main[world+".uexp"]))
            count,direct,inherited,errors=actor_inventory(cat)
        except Exception as exc:
            rows.append({"world":world,"error":str(exc)})
            continue
        by_package=collections.Counter(package for _,package in direct)
        available_direct=sum(n for package,n in by_package.items()
                             if available_chunks(package,indexes))
        only_split_classes=[]
        missing_classes=[]
        main_classes=0
        for cls,n in inherited.items():
            pkg=checked_package(cls,".uasset") if cls.endswith("_C") else None
            locations=available_chunks(pkg,indexes)
            per_class_archives[cls]=locations
            if "main" in locations: main_classes+=n
            elif locations: only_split_classes.append((n,cls,locations))
            else: missing_classes.append((n,cls))
        all_classes.update(inherited)
        all_direct.update(by_package)
        row={
            "world":world.split("/")[-1],
            "source_root_staticmesh_actors":count,
            "direct_staticmesh_actors":len(direct),
            "direct_mesh_package_present_actors":available_direct,
            "direct_unique_mesh_packages":len(by_package),
            "blueprint_inherited_actors":sum(inherited.values()),
            "inherited_blueprint_main_package_present_actors":main_classes,
            "inherited_blueprint_classes":len(inherited),
            "inherited_blueprint_only_split_actors":sum(n for n,_,_ in only_split_classes),
            "inherited_blueprint_missing_package_actors":sum(n for n,_ in missing_classes),
            "missing_direct_mesh_packages":[p for p in by_package
                                             if not available_chunks(p,indexes)][:12],
            "missing_blueprint_classes":sorted(missing_classes,reverse=True)[:12],
            "split_only_blueprint_classes":sorted(only_split_classes,reverse=True)[:12],
            "skipped_bad_actor_properties":dict(errors),
        }
        # This is an upper bound on potential geometry. A valid source
        # package can still fail the native CDO or LOD0 decoding contract.
        row["package_presence_upper_bound_percent"]=round(
            100*(available_direct+main_classes)/count,2) if count else 0.0
        rows.append(row)
        print("FORTNITE_AUTHENTIC_POI_PACKAGE_COVERAGE "+
              json.dumps(row,sort_keys=True),flush=True)
    summary={
        "authored_worlds":len(worlds),
        "scanned_worlds":sum("error" not in r for r in rows),
        "source_root_staticmesh_actors":sum(r.get("source_root_staticmesh_actors",0) for r in rows),
        "unique_blueprint_class_identities":len(all_classes),
        "unique_direct_mesh_packages":len(all_direct),
        "top_inherited_blueprint_classes":all_classes.most_common(30),
        "missing_worlds":[r for r in rows if "error" in r],
        "warning":"Package presence is not native LOD/CDO decode coverage and not visual parity",
    }
    print("FORTNITE_AUTHENTIC_40_POI_COVERAGE_SUMMARY "+
          json.dumps(summary,sort_keys=True),flush=True)
    if summary["scanned_worlds"]!=40:
        raise RuntimeError("Not all 40 exact source-authored POI levels were scanned")

if __name__=="__main__":
    run()
