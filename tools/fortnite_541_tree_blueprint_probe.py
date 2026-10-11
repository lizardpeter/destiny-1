#!/usr/bin/env python3
"""Trace original Fortnite 5.41 tree/shrub actors through Blueprint defaults
and original source mesh references. No fabricated tree identity or placement.
"""
from pathlib import Path
import json,struct,collections
import fortnite_541_r2_material_probe as r2
from fortnite_541_material_expression_probe import Catalog
SUFFIX="/Maps/POI/Athena_POI_HedgeMaze"
CLASSES=("Athena_Tree_Large_1_C","Athena_Prop_Plant_Shrub_01_C","Athena_Prop_Plant_Shrub_09_C")
def prop_desc(cat,raw,limit=50):
    props,end=cat.props(raw)
    data=[]
    for name,typ,extra,value in props[:limit]:
        field={"name":name,"type":typ,"size":len(value)}
        if typ in ("ObjectProperty","ClassProperty") and len(value)==4:
            ref=struct.unpack("<i",value)[0]
            field["ref"]=ref
            field["path"]=cat.path(ref) if ref else None
        elif typ=="StructProperty" and len(value)==12:
            field["vector"]=struct.unpack("<fff",value)
        elif typ=="NameProperty" and len(value)==8:
            field["value"]=cat.fname(value)
        elif typ in ("ArrayProperty","MapProperty"):
            field["head"]=value[:48].hex()
        data.append(field)
    return {"fields":data,"native_tail_bytes":len(raw)-end}
def run():
    index=r2.load_index()
    pair=[v for key,v in index.items() if key.endswith(SUFFIX+".umap")]
    exps=[v for key,v in index.items() if key.endswith(SUFFIX+".uexp")]
    if len(pair)!=1 or len(exps)!=1:raise ValueError("original source HedgeMaze map not unique")
    cat=Catalog(r2.source_payload(pair[0]),r2.source_payload(exps[0]))
    byclass=collections.defaultdict(list)
    packages={}
    for idx,export in enumerate(cat.exports,1):
        cls=cat.class_name(export)
        if cls not in CLASSES:continue
        clspath=cat.path(export["class"])
        byclass[cls].append({
            "name":cat.path(idx),
            "class_source":clspath,
            "actor_fields":prop_desc(cat,cat.export_data(export)),
        })
        package=clspath.split("::")[0]
        packages[cls]=package
    for cls in CLASSES:
        print("FORTNITE_TREE_ACTOR_SOURCE "+json.dumps({
            "class":cls,"count":len(byclass[cls]),"examples":byclass[cls][:2],
            "blueprint_class_source":packages.get(cls)
        }),flush=True)
    for cls,path in packages.items():
        prefix="FortniteGame/Content/"+path.removeprefix("/Game/")
        candidates=[{"ext":ext,"source_bytes":index[prefix+ext][2]}
            for ext in (".uasset",".uexp",".ubulk") if prefix+ext in index]
        doc={"class":cls,"source_package":path,"pak_files":candidates}
        if prefix+".uasset" in index and prefix+".uexp" in index:
            head=r2.source_payload(index[prefix+".uasset"])
            payload=r2.source_payload(index[prefix+".uexp"])
            a=Catalog(head,payload)
            doc["exports"]=len(a.exports)
            doc["class_census"]=collections.Counter(a.class_name(e) for e in a.exports).most_common(35)
            doc["objects"]=[]
            for j,ex in enumerate(a.exports,1):
                name=a.value(j)
                kind=a.class_name(ex)
                if any(w in (name+" "+kind).lower() for w in ("default__","mesh","component","scs","tree","shrub")):
                    row={"class":kind,"name":name,"source_path":a.path(j),"export_bytes":ex["size"]}
                    try:row["source"]=prop_desc(a,a.export_data(ex),30)
                    except Exception as error:row["source_error"]=str(error)
                    doc["objects"].append(row)
        print("FORTNITE_TREE_BLUEPRINT_SOURCE "+json.dumps(doc,sort_keys=True,default=str),flush=True)
    Path("fortnite541_tree_blueprint_source.json").write_text(json.dumps(
        {"actor_classes":{k:v[:5] for k,v in byclass.items()},"blueprints":packages},indent=2))
if __name__=="__main__":run()
