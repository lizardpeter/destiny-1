#!/usr/bin/env python3
"""Find original Fortnite 5.41 detailed building Blueprint CDO mesh inheritance.
All source asset bytes SHA1-verified from real PAK indexes; reports references,
not guesses. Target the most common opaque Factory / floor / roof actors.
"""
import collections,json,struct
import fortnite_541_r2_material_probe as m
import fortnite_541_skylight_cube_probe as s
from fortnite_541_material_expression_probe import Catalog
POI="FortniteGame/Content/Athena/Maps/POI/Athena_POI_ToiletFactory_001"
def props(cat,ex):
    raw=cat.export_data(ex)
    try:fields,end=cat.props(raw)
    except Exception as e:return {"error":str(e)}
    out=[]
    for name,kind,extra,bytes in fields:
        f={"name":name,"kind":kind,"len":len(bytes)}
        if kind in ("ObjectProperty","ClassProperty") and len(bytes)==4:
            ref=struct.unpack("<i",bytes)[0]
            f["ref"]=ref
            f["target"]=cat.path(ref) if ref else None
        if kind=="ArrayProperty" and len(bytes)>=4:
            f["count"]=struct.unpack_from("<I",bytes)[0]
        if kind=="StructProperty" and len(bytes)==12:
            f["xyz"]=struct.unpack("<fff",bytes)
        out.append(f)
    return {"fields":out,"native":len(raw)-end}
def run():
    ix=m.load_index()
    cat=Catalog(m.source_payload(ix[POI+".umap"]),m.source_payload(ix[POI+".uexp"]))
    classes=collections.Counter(cat.class_name(ex) for ex in cat.exports)
    selected=[]
    for cls,count in classes.most_common():
        if count<10 or not cls.endswith("_C"):continue
        if any(w in cls.lower() for w in ("chest","loot","ammo","particle","audio","tiered")):continue
        matches=[ex for ex in cat.exports if cat.class_name(ex)==cls]
        example=cat.path(matches[0]["class"]) if matches else None
        selected.append({"class":cls,"count":count,"source_class":example})
        if len(selected)>=24:break
    print("FORTNITE_REAL_BUILDING_BLUEPRINT_CLASSES "+json.dumps(selected),flush=True)
    inventory={"main":ix}
    s.URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/pakchunk0_s3-WindowsClient.pak"
    s.INDEX_SHA="27376dab8f8a3488d0d2b5332a2a2da7d28fd73e"
    inventory["s3"]=s.source()
    resolved=[]
    for entry in selected:
        classpath=entry["source_class"]
        package=classpath.split("::")[0].split("#")[0].removeprefix("/Game/")
        # CDO class import may carry a numbered FName suffix denoting package
        # name e.g. Athena_Tree_Large#2 -> Athena_Tree_Large_1.
        options=[package]
        if "#" in classpath.split("::")[0]:
            n=int(classpath.split("::")[0].rsplit("#",1)[-1])
            options.append(package+"_"+str(n-1))
        choice=None
        for variant in options:
            for arch,index in inventory.items():
                roots=[variant, "FortniteGame/Content/"+variant]
                for root in roots:
                    if root+".uasset" in index and root+".uexp" in index:
                        choice=(arch,root)
                        break
                if choice:break
            if choice:break
        record=dict(entry,source_package=package,archive=choice)
        if choice:
            arch,root=choice
            source=inventory[arch]
            s.URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/pakchunk0_s3-WindowsClient.pak"
            reader=m.source_payload if arch=="main" else s.payload
            try:
                cc=Catalog(reader(source[root+".uasset"]),reader(source[root+".uexp"]))
                record["exports"]=len(cc.exports)
                record["objects"]=[]
                for j,ex in enumerate(cc.exports,1):
                    cls=cc.class_name(ex)
                    name=cc.value(j)
                    if any(z in (name+" "+cls).lower() for z in
                           ("default__","meshcomponent","staticmesh","scs_node","construction")):
                        record["objects"].append({"object":cc.path(j),"class":cls,
                            "source":props(cc,ex)})
            except Exception as err:record["error"]=str(err)
        resolved.append(record)
        print("FORTNITE_REAL_BUILDING_BLUEPRINT_CDO "+json.dumps(record),flush=True)
    print("FORTNITE_REAL_BUILDING_BLUEPRINT_COVERAGE "+json.dumps({
        "classes":len(resolved),"found":sum(bool(x["archive"]) for x in resolved),
        "actor_count":sum(x["count"] for x in resolved),
        "resolved_actors":sum(x["count"] for x in resolved if x["archive"])
    }),flush=True)
if __name__=="__main__":run()
