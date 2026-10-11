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
