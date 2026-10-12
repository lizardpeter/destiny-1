#!/usr/bin/env python3
"""Retail-authenticated Athena 5.41 material/weight layout parity frontier.

Inspect original authored LandscapeLayerCoords, TextureCoordinate and
TextureSample bindings and original landscape paint layer allocations.
Source values, NOT a chosen replacement texture or arbitrary UV multiplier.
"""
import json,struct,collections
from fortnite_541_material_expression_probe import audit_one,audit_landscape_paint_layers,Catalog
import fortnite_541_r2_material_probe as retail

SOURCES=[
 "/Environments/Landscape/Material/M_Athena_Terrain_Master",
 "/Environments/Landscape/Material/M_Athena_Terrain_01",
 "/Environments/Landscape/MaterialFunctions/Standard/MF_Athena_Grass_01",
 "/Environments/Landscape/MaterialFunctions/Standard/MF_Athena_Rock_01",
 "/Environments/Landscape/MaterialFunctions/Standard/MF_Athena_Forest_01",
 "/Environments/Landscape/MaterialFunctions/Standard/MF_Athena_Gravel_01",
 "/Environments/Landscape/MaterialFunctions/Standard/MF_Athena_Mud_01",
 "/Environments/Landscape/MaterialFunctions/Standard/MF_Athena_Road_01",
 "/Environments/Landscape/MaterialFunctions/Arid/MF_Athena_Arid_Sand",
 "/Environments/Landscape/MaterialFunctions/MF_FarmGrass_Colors",
 "/Environments/Landscape/MaterialFunctions/MF_LawnGrassColoration",
]
def compact(node):
    attrs=node.get("authored_properties",[])
    interesting=("MappingScale","MappingRotation","MappingPanU","MappingPanV",
        "CoordinateIndex","UTiling","VTiling","ConstCoordinate","Texture",
        "ParameterName","LayerName","Layer","TextureObject",
        "BlendType","Layers","TextureCoordinate")
    return {"class":node["type"],"object":node["object"],
      "references":node.get("references",[]),
      "input_links":node.get("inputs",[]),
      "authored":[p for p in attrs if p["name"] in interesting]}
def main():
    idx=retail.load_index()
    layer_totals=collections.Counter()
    for section in range(6):
        data=audit_landscape_paint_layers(section,idx)
        layer_totals.update(data["layer_info_allocation_counts"])
        print("ATHENA_541_VERIFIED_PAINT_SECTION "+
              json.dumps(data,sort_keys=True),flush=True)
    print("ATHENA_541_VERIFIED_PAINT_LAYERS "+json.dumps(
         layer_totals,sort_keys=True),flush=True)
    original="FortniteGame/Content/Athena/Environments/Landscape/Material/M_Athena_Terrain_Master"
    c=Catalog(retail.source_payload(idx[original+".uasset"]),
              retail.source_payload(idx[original+".uexp"]))
    source_uv=[]
    for i,ex in enumerate(c.exports,1):
        cls=c.class_name(ex)
        if cls not in ("MaterialExpressionTextureSampleParameter2D","MaterialExpressionLandscapeLayerCoords","MaterialExpressionTextureCoordinate"):
            continue
        fields,_=c.props(c.export_data(ex))
        record=[]
        for name,kind,meta,payload in fields:
            if name not in ("ParameterName","Coordinates","Texture","MappingScale","MappingRotation","MappingPanU","MappingPanV","CoordinateIndex","UTiling","VTiling"):
                continue
            value=None
            if kind=="StructProperty" and meta==["ExpressionInput"] and len(payload)==40:
                ref=struct.unpack_from("<i",payload)[0]
                value={"ref":ref,"source":c.path(ref),"expr_fname":c.fname(payload[32:40]),"raw40":payload.hex()}
            elif kind=="NameProperty" and len(payload)==8:value=c.fname(payload)
            elif kind=="FloatProperty" and len(payload)==4:value=struct.unpack("<f",payload)[0]
            elif kind=="ObjectProperty" and len(payload)==4:value=c.path(struct.unpack("<i",payload)[0])
            elif kind=="IntProperty" and len(payload)==4:value=struct.unpack("<i",payload)[0]
            record.append({"field":name,"type":kind,"value":value})
        source_uv.append({"source":c.value(i),"class":cls,"tagged":record})
    print("ATHENA_541_AUTHENTIC_BIOME_SAMPLER_UV_CONNECTIONS "+
        json.dumps(source_uv,sort_keys=True),flush=True)
    for base in SOURCES:
        graph=audit_one(base,idx)
        nodes=graph["graph_links"]+graph["texture_samples"]
        found=[compact(n) for n in nodes if any(
            x in n["type"] for x in ("LandscapeLayer","TextureCoordinate",
                "TextureSample","MaterialFunctionCall"))]
        print("ATHENA_541_VERIFIED_TERRAIN_SOURCE_NODES "+json.dumps({
          "source":base,"source_expression_count":graph["expression_count"],
          "classes":graph["class_counts"],"nodes":found[:200],
          "unresolved":graph["unresolved"][:12]
        },sort_keys=True),flush=True)
    print("ATHENA_541_TERRAIN_SOURCE_PROOF_COMPLETE "+json.dumps({
        "material_sources":len(SOURCES),"paint_layers":dict(layer_totals)
    },sort_keys=True),flush=True)
if __name__=="__main__":main()
