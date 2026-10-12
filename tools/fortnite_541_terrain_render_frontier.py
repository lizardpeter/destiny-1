#!/usr/bin/env python3
"""Retail-authenticated Athena 5.41 material/weight layout parity frontier.

Inspect original authored LandscapeLayerCoords, TextureCoordinate and
TextureSample bindings and original landscape paint layer allocations.
Source values, NOT a chosen replacement texture or arbitrary UV multiplier.
"""
import json,struct,collections
from fortnite_541_material_expression_probe import audit_one,audit_landscape_paint_layers
import fortnite_541_r2_material_probe as retail

SOURCES=[
 "/Environments/Landscape/Material/M_Athena_Terrain_Master",
 "/Environments/Landscape/Material/M_Athena_Terrain_01",
 "/Environments/Landscape/MaterialFunctions/Standard/MF_Athena_Grass_01",
 "/Environments/Landscape/MaterialFunctions/Standard/MF_Athena_Rock_01",
 "/Environments/Landscape/MaterialFunctions/Standard/MF_Athena_Forest_01",
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
