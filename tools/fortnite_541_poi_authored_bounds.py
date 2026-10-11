#!/usr/bin/env python3
"""Verify original Fortnite 5.41 POI foundation authored FBox bounds and
source HLOD intersections. Exact original SHA1 PAK, no inferred bounds."""
import struct,json,math
import fortnite_541_r2_material_probe as r2
from fortnite_541_material_expression_probe import Catalog
def fields(cat,export):
    return {name:(kind,data) for name,kind,_,data in cat.props(cat.export_data(export))[0]}
def xyz(blob):
    return tuple(round(x,3) for x in struct.unpack("<fff",blob))
def main():
    ix=r2.load_index()
    foundation="FortniteGame/Content/Athena/Maps/Athena_POI_Foundations"
    terrain="FortniteGame/Content/Athena/Maps/Athena_Terrain"
    f=Catalog(r2.source_payload(ix[foundation+".umap"]),r2.source_payload(ix[foundation+".uexp"]))
    t=Catalog(r2.source_payload(ix[terrain+".umap"]),r2.source_payload(ix[terrain+".uexp"]))
    rows=[]
    for i,e in enumerate(f.exports,1):
        cl=f.class_name(e)
        if not cl.startswith("LF_Athena_POI_"):continue
        p=fields(f,e)
        b=p.get("StreamingBoundingBox")
        if b and len(b[1])==25:
            raw=b[1]
            mins=xyz(raw[:12]);maxs=xyz(raw[12:24]);valid=raw[24]
        else:mins=maxs=None;valid=None
        ref=struct.unpack("<i",p["RootComponent"][1])[0]
        q=fields(f,f.exports[ref-1])
        loc=xyz(q["RelativeLocation"][1]) if "RelativeLocation" in q else (0,0,0)
        rot=xyz(q["RelativeRotation"][1]) if "RelativeRotation" in q else (0,0,0)
        wp=p.get("AdditionalWorlds")
        world=f.fname(wp[1][4:12]) if wp else None
        if world:
            rows.append({"asset":world,"loc":loc,"yaw":rot[1],"min":mins,"max":maxs,"valid":valid})
    a=[x for x in rows if "ToiletFactory" in x["asset"] or "HedgeMaze" in x["asset"] or "Diner" in x["asset"]]
    print("FORTNITE_SOURCE_AUTHORED_POI_BOUNDING_BOXES "+json.dumps({"samples":a,"all_count":len(rows),"valid_count":sum(x["valid"]==1 for x in rows),"all":rows[:15]}),flush=True)
    chosen=next(x for x in a if "ToiletFactory" in x["asset"])
    candidates=[]
    for i,e in enumerate(t.exports,1):
        if t.class_name(e)!="FortHLODSMActor":continue
        p=fields(t,e)
        k=p.get("UniqueWorldLocation")
        if not k or len(k[1])!=12:continue
        v=xyz(k[1])
        if abs(v[0]-chosen["loc"][0])<20000 and abs(v[1]-chosen["loc"][1])<20000:
            candidates.append({"obj":t.path(i),"loc":v})
    print("FORTNITE_AUTHORED_HLOD_NEAR_TOILET_FACTORY "+json.dumps({"count":len(candidates),"samples":candidates[:35]}),flush=True)
if __name__=="__main__":main()
