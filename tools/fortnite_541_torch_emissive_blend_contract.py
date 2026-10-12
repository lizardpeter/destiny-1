#!/usr/bin/env python3
"""Authenticate cooked Fortnite 5.41 campfire/torch emissive blend contracts.

No shader guessing: report exact UMaterial BlendMode, ShadingModel,
TwoSided, EmissiveColor expression FName, surviving material parameters
and cooked expression-node counts from the original SHA1 source bytes.
"""
import json,struct
from fortnite_541_material_expression_probe import Catalog
import fortnite_541_r2_material_probe as main
import fortnite_541_skylight_cube_probe as s4
from fortnite_541_all_poi_coverage import ROOT,SPLITS
SOURCES=[
  ("/Game/Athena/Items/Traps/Campfire/Effects/MI_Fire_Campfire_Mesh_Torch::MI_Fire_Campfire_Mesh_Torch","main"),
  ("/Game/Athena/Items/Traps/Campfire/Effects/M_Fire_Campfire_Mesh::M_Fire_Campfire_Mesh","main"),
  ("/Game/Packages/Fortress_Transylvania/Test_Assets/Materials/M_FakeVolumeGlow::M_FakeVolumeGlow","s4"),
]
def parse_important(c,ex):
    raw=c.export_data(ex)
    fields,_=c.props(raw)
    result=[]
    for name,kind,meta,payload in fields:
        if name not in ("BlendMode","ShadingModel","TwoSided","EmissiveColor",
                "Opacity","OpacityMask","WorldPositionOffset",
                "bUseEmissiveForDynamicAreaLighting","ScalarParameterValues",
                "VectorParameterValues","TextureParameterValues","BasePropertyOverrides",
                "Parent","DefaultValue","ParameterName","SubsurfaceColor","bUsedWithParticleSprites"):
            continue
        item={"name":name,"kind":kind,"meta":meta,"length":len(payload)}
        if kind in ("ByteProperty","NameProperty") and len(payload)==8:
            try:item["fname"]=c.fname(payload)
            except Exception as e:item["decode_error"]=str(e)
        if kind=="BoolProperty":item["encoded_boolean"]=meta
        if kind=="FloatProperty" and len(payload)==4:
            item["float"]=struct.unpack("<f",payload)[0]
        if kind=="StructProperty":
            if meta and meta[0]=="LinearColor" and len(payload)==16:
                item["linear_rgba"]=struct.unpack("<4f",payload)
            elif meta and meta[0]=="Color" and len(payload)==4:
                item["bgra"]=payload.hex()
            elif meta and meta[0] in ("ColorMaterialInput","ScalarMaterialInput",
                                    "VectorMaterialInput","ExpressionInput"):
                item["bytes0_48"]=payload[:48].hex()
                if len(payload)>=40:
                    id,n=struct.unpack_from("<II",payload,32)
                    if id<len(c.names):
                        item["expression_source"]=c.names[id]+("#"+str(n) if n else "")
            elif meta and meta[0]=="MaterialInstanceBasePropertyOverrides":
                try:
                    sub,_=c.props(payload)
                    item["overrides"]=[{"name":n,"kind":k,"meta":md,"value":c.fname(v) if k=="ByteProperty" and len(v)==8 else v.hex() if len(v)<=16 else str(len(v))+" bytes"} for n,k,md,v in sub]
                except Exception as e:item["override_error"]=str(e)
        if kind=="ObjectProperty" and len(payload)==4:
            ref=struct.unpack("<i",payload)[0]
            item["source_object"]=c.path(ref) if ref else None
        if kind=="ArrayProperty":
            if len(payload)>=4:item["original_count"]=struct.unpack_from("<I",payload)[0]
            item["source_bytes_prefix"]=payload[:64].hex()
        result.append(item)
    return result
def run():
    archives={"main":main.load_index()}
    sha=dict(SPLITS)["s4"]
    s4.URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/pakchunk0_s4-WindowsClient.pak"
    s4.INDEX_SHA=sha
    archives["s4"]=s4.source()
    for source,archive in SOURCES:
        path=source.removeprefix("/Game/").split("::")[0]
        base=(ROOT+path) if archive=="main" else path
        index=archives[archive]
        if base+".uasset" not in index or base+".uexp" not in index:
            raise ValueError(f"required retail material package absent: {source} archive {archive}")
        if archive=="main":
            header=main.source_payload(index[base+".uasset"])
            payload=main.source_payload(index[base+".uexp"])
        else:
            header=s4.payload(index[base+".uasset"])
            payload=s4.payload(index[base+".uexp"])
        c=Catalog(header,payload)
        exports=[]
        for i,ex in enumerate(c.exports,1):
            cls=c.class_name(ex)
            if cls in ("Material","MaterialInstanceConstant") or cls.startswith("MaterialExpression"):
                exports.append({"identity":c.path(i),"class":cls,
                    "fields":parse_important(c,ex)})
        print("FORTNITE_541_SOURCE_FLAME_EMISSIVE_CONTRACT "+json.dumps({
            "source":source,"archive":archive,"exports":exports,
            "source_names":[name for name in c.names if name.startswith("BLEND_") or
                            name.startswith("MSM_")][:45]
        },sort_keys=True),flush=True)
if __name__=="__main__":run()
