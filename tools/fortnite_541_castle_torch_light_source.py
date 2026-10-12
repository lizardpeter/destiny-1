#!/usr/bin/env python3
"""Source-exact Fortnite 5.41 castle torch Blueprint light template census.

18 authentic BP_TRV_ALight_Torch_02_C actor instances were just recovered
by loading their original split-s4 cooked Blueprint. Inspect its actual
light/component template exports before any shared renderer admission.
"""
from pathlib import Path
import json,struct,collections
from fortnite_541_material_expression_probe import Catalog
MANIFEST=Path("/tmp/fortnite541_split_only_cdos.tsv")
def fields(c,ex):
    try:
        props,offset=c.props(c.export_data(ex))
    except Exception as e:
        return [{"error":str(e)}]
    out=[]
    for name,kind,meta,raw in props:
        elem={"name":name,"kind":kind,"meta":meta,"bytes":len(raw)}
        if kind in ("ObjectProperty","ClassProperty") and len(raw)==4:
            ref=struct.unpack("<i",raw)[0]
            elem["source_object"]=c.path(ref) if ref else None
        elif kind=="FloatProperty" and len(raw)==4:
            elem["value"]=struct.unpack("<f",raw)[0]
        elif kind=="StructProperty" and len(raw)==12:
            elem["source_xyz"]=struct.unpack("<fff",raw)
        elif kind=="StructProperty" and len(raw) in (4,16):
            elem["source_rgba"]=raw.hex()
        elif kind=="BoolProperty":
            elem["original_flag"]=meta
        out.append(elem)
    return out
def run():
    lines=MANIFEST.read_text().splitlines()
    matches=[line.split("\t") for line in lines if "BP_TRV_ALight_Torch_02" in line]
    if len(matches)!=1:raise ValueError("retail castle torch source class manifest identity missing")
    identity,n,stem=matches[0]
    if int(n)!=18:raise ValueError("source temple torch actor count differs")
    root=Path(stem)
    cat=Catalog(root.with_suffix(".uasset").read_bytes(),
                root.with_suffix(".uexp").read_bytes())
    classes=collections.Counter(cat.class_name(e) for e in cat.exports)
    objs=[]
    for i,ex in enumerate(cat.exports,1):
        cls=cat.class_name(ex)
        path=cat.path(i)
        if (cls.endswith("Component") or cls.endswith("_C")
            or cls in ("SCS_Node","SimpleConstructionScript",
                       "InheritableComponentHandler")
            or "Default__" in path):
            objs.append({"idx":i,"class":cls,"path":path,
                 "source_outer":cat.path(ex["outer"]) if ex["outer"] else None,
                 "props":fields(cat,ex)})
    report={"identity":identity,"placed_actors":n,
       "source_export_count":len(cat.exports),
       "source_component_class_counts":classes.most_common(50),
       "templates":objs,"lights":[x for x in objs if "Light" in x["class"]]}
    print("FORTNITE_ORIGINAL_CASTLE_TORCH_LIGHT_SOURCE "+json.dumps(report,sort_keys=True),flush=True)
if __name__=="__main__":run()
