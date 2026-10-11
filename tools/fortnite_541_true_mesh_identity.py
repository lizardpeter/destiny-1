#!/usr/bin/env python3
import fortnite_541_skylight_cube_probe as s
from fortnite_541_material_expression_probe import Catalog
s.URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/pakchunk0_s3-WindowsClient.pak"
s.INDEX_SHA="27376dab8f8a3488d0d2b5332a2a2da7d28fd73e"
ix=s.source()
for package in ["Environments/Sets/Factory/Meshes/Factory_Wall_1",
"Packages/DS_Fortnite_Terrain_NoLOD/Elevation/S_Cave_Outer_Middle",
"Packages/Fortress_Floors_Generic/SM/Mesh/SM_Fort_Floors_Generic_TileBasic"]:
    if not all(package+ext in ix for ext in (".uasset",".uexp")):
        print("FORTNITE_TRUE_MESH_IDENTITY MISSING",package,flush=True);continue
    head=s.payload(ix[package+".uasset"]);exp=s.payload(ix[package+".uexp"])
    cat=Catalog(head,exp)
    classes=[(cat.path(i),cat.class_name(e)) for i,e in enumerate(cat.exports,1)
        if cat.class_name(e)=="StaticMesh"]
    print("FORTNITE_TRUE_MESH_IDENTITY",package,classes,flush=True)

print("FORTNITE_VERIFIED_INHERITED_FLOOR_SOURCE_ARCHIVES",flush=True)
target="Packages/Fortress_Floors_Generic/SM/Mesh/SM_Fort_Floors_Generic_TileBasic"
for name,sha in [
    ("s1","a37147494190b90c420b852d69740402f93f6103"),
    ("s2","42a45eee280ab70abbb5192b33a5945c119bd82c"),
    ("s3","27376dab8f8a3488d0d2b5332a2a2da7d28fd73e"),
    ("s4","96a67f9eae257051576e368fdb61a6fb78b2f56a"),
    ("s5","9f9f8e76d614e080108d2c49d616e9b4bc9affd0"),
]:
    s.URL=f"https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/pakchunk0_{name}-WindowsClient.pak"
    s.INDEX_SHA=sha
    try:
        entries=s.source()
        found=[key for key in entries if key.endswith(target+".uasset") or key.endswith(target+".uexp")]
        print("FORTNITE_INHERITED_FLOOR_PACKAGE",name,found,flush=True)
    except Exception as exc:
        print("FORTNITE_INHERITED_FLOOR_SOURCE_INDEX_ERROR",name,str(exc)[:100],flush=True)
