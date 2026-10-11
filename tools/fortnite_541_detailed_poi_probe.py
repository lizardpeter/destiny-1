#!/usr/bin/env python3
"""Audit source-authentic detailed building actors and native mesh refs inside
retail Fortnite 5.41 streamed POI levels. All PAK bytes SHA1 verified.
Never treat HLOD proxies as full-detail mesh source.
"""
import collections,json,struct
from pathlib import Path
import fortnite_541_r2_material_probe as retail
from fortnite_541_material_expression_probe import Catalog

def trace(cat,exp,index):
    src=cat.export_data(exp)
    props,at=cat.props(src)
    fields=[]
    for name,kind,meta,raw in props:
        if name not in ("StaticMesh","RootComponent","StaticMeshComponent","RelativeLocation",
                        "RelativeRotation","RelativeScale3D","UniqueWorldLocation","ComponentToWorld","InstanceComponents"):
            continue
        p={"name":name,"kind":kind,"size":len(raw)}
        if kind=="ObjectProperty" and len(raw)==4:
            n=struct.unpack("<i",raw)[0]
            p["ref"]=n
            p["target"]=cat.path(n) if n else None
        if kind=="StructProperty" and len(raw)==12:
            p["floats"]=list(struct.unpack("<fff",raw))
        fields.append(p)
    return {"path":cat.path(index),"class":cat.class_name(exp),"properties":fields,"native":len(src)-at}

def run():
    ix=retail.load_index()
    maps=sorted(k for k in ix if k.endswith(".umap") and
        ("Athena/Maps/POI/" in k or "Athena/Maps/Athena_POI" in k))
    eligible=[p for p in maps if p[:-5]+".uexp" in ix]
    print("FORTNITE_REAL_DETAIL_POI_SOURCE_CENSUS "+json.dumps({
        "complete_original_poi_maps":len(eligible),
        "name_samples":eligible[:80],
        "largest":sorted([{"map":p,"umap":ix[p][2],"uexp":ix[p[:-5]+".uexp"][2]}
            for p in eligible],key=lambda x:-x["uexp"])[:14]
    }),flush=True)
    samples=[]
    hm=next((p for p in eligible if "HedgeMaze" in p),None)
    if hm:samples.append(hm)
    foundation=next((p for p in eligible if "POI_Foundations" in p),None)
    if foundation:samples.append(foundation)
    # Sample full-detail retail POIs with many UObject exports.
    for p in sorted(eligible,key=lambda k:-ix[k][2]):
        if p not in samples and len(samples)<8 and ix[p][2]<11_000_000:
            samples.append(p)
    # Foundation actors own true POI selection/position and streaming state.
    # Discover the *authored* references before inventing per-level offsets.
    for foundation_map in [
        "FortniteGame/Content/Athena/Maps/Athena_POI_Foundations",
        "FortniteGame/Content/Athena/Maps/Athena_Streaming_Grid"
    ]:
        if foundation_map+".umap" not in ix:continue
        c=Catalog(retail.source_payload(ix[foundation_map+".umap"]),
                  retail.source_payload(ix[foundation_map+".uexp"]))
        candidates=[]
        for ordinal,export in enumerate(c.exports,1):
            cl=c.class_name(export)
            if not ("LF_Athena_POI_" in cl or "LevelStreaming" in cl
                    or cl in ("World","Level","WorldComposition")):
                continue
            raw=c.export_data(export)
            try:props,end=c.props(raw)
            except Exception as e:
                candidates.append({"class":cl,"object":c.path(ordinal),"error":str(e)})
                continue
            fields=[]
            for key,kind,meta,val in props:
                item={"name":key,"type":kind,"size":len(val)}
                if kind in ("ObjectProperty","ClassProperty") and len(val)==4:
                    ref=struct.unpack("<i",val)[0]
                    item["ref"]=c.path(ref) if ref else None
                elif kind=="NameProperty" and len(val)==8:
                    item["name_value"]=c.fname(val)
                elif kind=="SoftObjectProperty" and len(val)>=12:
                    item["soft_path"]=c.fname(val[:8])
                elif kind=="StructProperty" and len(val)==12:
                    item["floats"]=struct.unpack("<fff",val)
                elif kind=="ArrayProperty" and len(val)>=4:
                    item["array_count"]=struct.unpack_from("<I",val)[0]
                    if key=="AdditionalWorlds" and len(val)==16:
                        item["first_world"]=c.fname(val[4:12])
                        item["array_hex"]=val.hex()
                fields.append(item)
            root=next((v.get("ref") for v in fields if v["name"]=="RootComponent"),None)
            root_fields=[]
            root_index=next((struct.unpack("<i",vv)[0] for nm,tp,md,vv in props
                if nm=="RootComponent" and tp=="ObjectProperty" and len(vv)==4),0)
            if root_index>0:
                component=c.exports[root_index-1]
                buf=c.export_data(component)
                try:
                    cp,ce=c.props(buf)
                    for pn,pk,meta,datum in cp:
                        if pn in ("RelativeLocation","RelativeRotation","RelativeScale3D") and len(datum)==12:
                            root_fields.append({"name":pn,"floats":struct.unpack("<fff",datum)})
                except Exception as e:root_fields.append({"error":str(e)})
            candidates.append({"class":cl,"object":c.path(ordinal),
                "fields":fields,"root_transform":root_fields,"native_bytes":len(raw)-end})
        print("FORTNITE_POI_AUTHORED_FOUNDATION_REFERENCES "+json.dumps({
            "map":foundation_map,"num":len(candidates),
            "candidates":candidates[:52]
        }),flush=True)
    for path in samples:
        try:
            cat=Catalog(retail.source_payload(ix[path]),
                retail.source_payload(ix[path[:-5]+".uexp"]))
            classes=collections.Counter(cat.class_name(e) for e in cat.exports)
            kinds={"StaticMeshComponent","InstancedStaticMeshComponent",
                   "HierarchicalInstancedStaticMeshComponent"}
            meshs=[];actors=[]
            for i,ex in enumerate(cat.exports,1):
                cls=cat.class_name(ex)
                if cls in kinds:
                    try:meshs.append(trace(cat,ex,i))
                    except Exception as err:meshs.append({"source":cat.path(i),"error":str(err)})
                if cls in ("FortStaticMeshActor","StaticMeshActor","FortHLODSMActor",
                           "FortBuildingActor","Athena_Tree_Large_1_C"):
                    try:actors.append(trace(cat,ex,i))
                    except Exception as err:actors.append({"source":cat.path(i),"error":str(err)})
            refs=[f["target"] for e in meshs for f in e.get("properties",[])
                if f["name"]=="StaticMesh" and f.get("target")]
            original_detail=[r for r in refs if "/HLOD/" not in r]
            item={"map":path,"total_exports":len(cat.exports),
                "classes":classes.most_common(30),
                "mesh_components":len(meshs),
                "static_mesh_references":len(refs),
                "full_detail_mesh_references":len(original_detail),
                "unique_detailed_source_meshes":len(set(original_detail)),
                "source_mesh_samples":list(dict.fromkeys(original_detail))[:35],
                "source_mesh_components":meshs[:10],
                "source_actors":actors[:7]}
            print("FORTNITE_REAL_DETAIL_POI_SAMPLE "+json.dumps(item),flush=True)
        except Exception as e:
            print("FORTNITE_REAL_DETAIL_POI_ERROR "+json.dumps({
                "map":path,"error":str(e)}),flush=True)
if __name__=="__main__":run()
