#!/usr/bin/env python3
"""Source-exact UE4.21 SkyDome material graph topology and function inventory.

Resolves the actual cooked material's root emissive link, material expression
FExpressionInput link positions, and SkyTwist source function. All references
are inspected as raw source before choosing a native decoder layout.
No guessed cloud UVs or derivative color math.
"""
import collections
import json
import struct
from pathlib import Path
import fortnite_541_skylight_cube_probe as source
from fortnite_541_material_expression_probe import Catalog

S4_URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/pakchunk0_s4-WindowsClient.pak"
S4_HASH="96a67f9eae257051576e368fdb61a6fb78b2f56a"
PACKAGES=(
    "Packages/Fortress_Sky/SkyDome/Master/M_SkyDome",
    "Packages/Fortress_Sky/Fortnite_SkyTwistFunction",
    "Packages/Fortress_SharedMaterials/GlobalMaterialParameters/FortniteMaterialParameters",
)

def lookup(ix,key):
    hits=[v for k,v in ix.items() if k==key or k.endswith("/"+key)]
    if len(hits)!=1:
        return None
    return source.payload(hits[0])

def read(ix,name):
    h=lookup(ix,name+".uasset")
    x=lookup(ix,name+".uexp")
    if h is None or x is None:
        return None
    root=Path("/tmp/fortnite541_source_sky/FortniteGame/Content")
    p=root/name
    p.parent.mkdir(parents=True,exist_ok=True)
    p.with_suffix(".uasset").write_bytes(h)
    p.with_suffix(".uexp").write_bytes(x)
    return Catalog(h,x)

def ref(cat,raw,offset=0):
    if len(raw)<offset+4:return None
    index=struct.unpack_from("<i",raw,offset)[0]
    if index==0:return None
    try:
        resolved=cat.path(index)
    except Exception:
        return None
    return {"index":index,"object":resolved}

def u32words(raw,limit=48):
    return [struct.unpack_from("<I",raw,i)[0]
        for i in range(0,min(len(raw),limit)//4*4,4)]
def main():
    source.URL=S4_URL
    source.INDEX_SHA=S4_HASH
    ix=source.source()
    print("FORTNITE_UE4_SKY_INPUT_LINK_CANDIDATES begin",flush=True)
    for package in PACKAGES:
        cat=read(ix,package)
        if cat is None:
            print("FORTNITE_SKY_GRAPH_PACKAGE_MISSING "+json.dumps(package),flush=True)
            continue
        by_class=collections.Counter(cat.class_name(ex) for ex in cat.exports)
        graph=[]
        roots=[]
        for i,ex in enumerate(cat.exports,1):
            typ=cat.class_name(ex)
            if not (typ.startswith("MaterialExpression") or typ in
                ("Material","MaterialFunction","MaterialParameterCollection")):
                continue
            fields,end=cat.props(cat.export_data(ex))
            links=[]
            parameters=[]
            for name,kind,meta,raw in fields:
                if kind=="StructProperty" and meta and meta[0] in (
                    "ExpressionInput","ColorMaterialInput","ScalarMaterialInput",
                    "MaterialAttributesInput","VectorMaterialInput"):
                    offsets=[{"offset":pos,**target}
                      for pos in range(0,min(len(raw),48),4)
                      if (target:=ref(cat,raw,pos)) is not None]
                    # Cooked UE4 shader inputs commonly have a null
                    # Expression pointer. Original ExpressionName FName,
                    # however, survives serialization at offset 32.
                    # Decode it, but validate later against actual exports.
                    logical=None
                    if len(raw)>=40:
                        fi,number=struct.unpack_from("<II",raw,32)
                        if fi < len(cat.names):
                            base=cat.names[fi]
                            target=base if number==0 else f"{base}#{number}"
                            logical={"name_index":fi,"number":number,
                                     "expression_name":target}
                    links.append({"name":name,"type":meta[0],"size":len(raw),
                                  "u32":u32words(raw,48),"references":offsets,
                                  "cooked_expression_name":logical})
                elif kind in ("ObjectProperty","ClassProperty") and len(raw)==4:
                    target=ref(cat,raw)
                    if target and name not in ("Material",):
                        parameters.append({"name":name,"target":target})
                elif kind=="NameProperty" and len(raw)==8:
                    parameters.append({"name":name,"value":cat.fname(raw)})
                elif kind=="FloatProperty" and len(raw)==4:
                    parameters.append({"name":name,"float":struct.unpack("<f",raw)[0]})
            entry={"object":cat.path(i),"class":typ,
                   "expression_inputs":links,"other_inputs":parameters}
            if typ.startswith("MaterialExpression"):
                graph.append(entry)
            else:
                roots.append(entry)
        known={o["object"].split("::")[-1]:o["object"] for o in graph}
        src_edges=[]
        unmatched=[]
        for node in graph+roots:
            for link in node["expression_inputs"]:
                item=link["cooked_expression_name"]
                if not item:continue
                identifier=item["expression_name"]
                if identifier in known:
                    src_edges.append({"consumer":node["object"],"port":link["name"],
                                      "producer":known[identifier]})
                elif identifier and not identifier.startswith("None"):
                    unmatched.append({"consumer":node["object"],"port":link["name"],
                                      "target":identifier})
        print("FORTNITE_SKY_AUTHORED_NAMED_EDGES "+json.dumps({
            "package":package,"matched":len(src_edges),"unresolved":len(unmatched),
            "edges":src_edges,"missing":unmatched[:80]},sort_keys=True),flush=True)
        print("FORTNITE_SKY_GRAPH_TOPOLOGY "+json.dumps({
            "package":package,"exports":len(cat.exports),
            "expression_count":len(graph),
            "class_census":by_class.most_common(),
            "roots":roots,
            "input_nodes":[n for n in graph if n["expression_inputs"]],
            "function_calls":[n for n in graph if
                n["class"]=="MaterialExpressionMaterialFunctionCall"],
            "parameter_collections":[n for n in graph if
                n["class"]=="MaterialExpressionCollectionParameter"],
        },sort_keys=True),flush=True)
if __name__=="__main__":
    main()
