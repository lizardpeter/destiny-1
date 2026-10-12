#!/usr/bin/env python3
"""Authenticate source material instances used by actual Factory mesh slots.

Never search by a similarly named stock texture: follow exact MaterialInterface
UObject in StaticMaterials, find original MIC UTexture2D parameters, and
record their source identities for the universal renderer.
"""
import json,struct
from pathlib import Path
from fortnite_541_factory_native_mesh_batch import locate,read_source
from fortnite_541_all_poi_coverage import SPLITS,ROOT
import fortnite_541_r2_material_probe as main
import fortnite_541_skylight_cube_probe as split
from fortnite_541_material_expression_probe import Catalog
PACKAGES=[
    "Environments/Props/Industrial/Materials/MI_ShippingContainer_01",
    "Packages/DS_Fortnite_Terrain_NoLOD/Materials/M_Terrain_Cave",
    "Packages/DS_Fortnite_Terrain_NoLOD/Materials/M_Terrain_Cliff_White",
]
def run():
    indexes={"main":main.load_index()}
    for archive,sha in SPLITS:
        path="pakchunk1-WindowsClient.pak" if archive=="chunk1" else f"pakchunk0_{archive}-WindowsClient.pak"
        split.URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/"+path
        split.INDEX_SHA=sha
        indexes[archive]=split.source()
    # Verify actual source file spelling for a numbered material slot found
    # in the Toilet Factory mesh inventory, not an invented alternate name.
    numbered="Environments/Props/Boxes/Materials/WoodenCrates_2"
    places=[]
    for archive,items in indexes.items():
        candidates=(ROOT+numbered,numbered)
        for key in candidates:
            if key+".uasset" in items and key+".uexp" in items:
                places.append({"archive":archive,"source_file":key})
    print("FORTNITE_541_NUMBERED_MATERIAL_RETAIL_LOCATOR "+json.dumps({
        "original_material_identity":"/Game/Environments/Props/Boxes/Materials/WoodenCrates#3::WoodenCrates#3",
        "expected_numbered_package":numbered,"authenticated_source_locations":places
    },sort_keys=True),flush=True)
    for source in PACKAGES:
        full=ROOT+source
        found=locate("/Game/"+source+"::"+source.rsplit("/",1)[-1],indexes)
        if found is None:
            print("FORTNITE_SOURCE_MATERIAL_PROBE "+json.dumps({"material":source,"present":False}),flush=True)
            continue
        archive,base=found
        original_header=read_source(archive,base+".uasset",indexes)
        original_export=read_source(archive,base+".uexp",indexes)
        target=Path("/tmp/fortnite541_source_materials/FortniteGame/Content")/source
        target.parent.mkdir(parents=True,exist_ok=True)
        target.with_suffix(".uasset").write_bytes(original_header)
        target.with_suffix(".uexp").write_bytes(original_export)
        cat=Catalog(original_header,original_export)
        result=[]
        for i,ex in enumerate(cat.exports,1):
            typ=cat.class_name(ex)
            if typ not in ("MaterialInstanceConstant","Material","MaterialInstance"):
                continue
            props,_=cat.props(cat.export_data(ex))
            rows=[]
            for n,k,meta,v in props:
                item={"name":n,"kind":k,"meta":meta,"length":len(v)}
                if k=="ObjectProperty" and len(v)==4:
                    ref=struct.unpack("<i",v)[0]
                    item["source_object"]=cat.path(ref) if ref else None
                if k=="ArrayProperty" and len(v)>=4:
                    item["count"]=struct.unpack_from("<I",v)[0]
                    item["prefix"]=v[:125].hex()
                    if n=="TextureParameterValues":
                        none=struct.pack("<II",cat.names.index("None"),0)
                        wrapper,_=cat.props(v[4:]+none)
                        if len(wrapper)!=1 or wrapper[0][1]!="StructProperty":
                            raise ValueError("retail material texture parameter aggregate changed")
                        inner=wrapper[0][3]
                        cursor=0
                        decoded=[]
                        for j in range(item["count"]):
                            tagged,used=cat.props(inner[cursor:])
                            if used<=0:raise ValueError("original texture parameter struct failed to advance")
                            cursor+=used
                            param={}
                            for pn,pk,pmeta,praw in tagged:
                                if pn=="ParameterInfo" and pk=="StructProperty":
                                    info,_=cat.props(praw)
                                    param["info"]=[{"name":nn,"kind":nk,
                                        "value":cat.fname(nraw) if nk=="NameProperty" and len(nraw)==8 else None}
                                        for nn,nk,nmeta,nraw in info]
                                elif pn=="ParameterValue" and pk=="ObjectProperty" and len(praw)==4:
                                    ref=struct.unpack("<i",praw)[0]
                                    param["texture"]=cat.path(ref) if ref else None
                                else:param[pn]={"kind":pk,"size":len(praw)}
                            decoded.append(param)
                        item["original_texture_parameters"]=decoded
                        item["source_bytes_used"]=cursor
                        item["source_bytes_total"]=len(inner)
                rows.append(item)
            result.append({"name":cat.value(i),"class":typ,"fields":rows})
        print("FORTNITE_SOURCE_MATERIAL_PROBE "+json.dumps({
            "material":source,"archive":archive,"source_classes":[cat.class_name(e) for e in cat.exports],
            "exported_materials":result
        },sort_keys=True),flush=True)
        # Exactly the source parameter values selected by the native
        # material parser: no filename-based texture substitution.
        for entry in result:
            for param in entry["fields"]:
                if param["name"]!="TextureParameterValues":continue
                source_params=param.get("original_texture_parameters",[])
                for tex in source_params:
                    info=tex.get("info",[])
                    label=next((i["value"] for i in info if i["name"]=="Name"),None)
                    if label not in ("Diffuse","CliffTexture","Base Tiling Texture"):
                        continue
                    identity=tex.get("texture")
                    if not identity or not identity.startswith("/Game/"):
                        continue
                    original=identity.removeprefix("/Game/").split("::")[0]
                    base_path=ROOT+original
                    target_location=locate("/Game/"+original+"::"+original.rsplit("/",1)[-1],indexes)
                    if not target_location:
                        print("FORTNITE_SOURCE_MATERIAL_DIFFUSE_ABSENT "+json.dumps({
                            "param":label,"texture":identity}),flush=True)
                        continue
                    source_archive,source_base=target_location
                    out=Path("/tmp/fortnite541_source_materials/FortniteGame/Content")/original
                    out.parent.mkdir(parents=True,exist_ok=True)
                    saved=[]
                    for ext in (".uasset",".uexp",".ubulk"):
                        candidate=source_base+ext
                        potential=indexes[source_archive]
                        if candidate not in potential:continue
                        binary=read_source(source_archive,candidate,indexes)
                        out.with_suffix(ext).write_bytes(binary)
                        saved.append({"ext":ext,"bytes":len(binary)})
                    print("FORTNITE_SOURCE_MATERIAL_AUTHENTIC_DIFFUSE "+json.dumps({
                        "param":label,"texture":identity,"archive":source_archive,
                        "verified_files":saved
                    },sort_keys=True),flush=True)
if __name__=="__main__":run()
