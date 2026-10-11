#!/usr/bin/env python3
"""Authenticate and inspect original 5.41 Athena sky, atmosphere, fog actor properties."""
import json,sys,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import fortnite_541_r2_material_probe as r2
from fortnite_541_material_expression_probe import Catalog

SOURCE=[
    "/Maps/Athena_Terrain", "/Maps/Background/Athena_Background",
    "/Maps/Streaming/Sublevel_X0Y0"
]
WORDS=("fog","sky","sun","atmosphere","cloud","directional","light","weather")
def report_scene(source,entries):
    parts=[]
    for ext in [".umap",".uexp"]:
        hits=[x for name,x in entries.items() if name.endswith(source+ext)]
        if len(hits)!=1:raise ValueError("not one verified Athena map: "+source+ext)
        parts.append(r2.source_payload(hits[0]))
    cat=Catalog(*parts)
    rows=[]
    for index,ex in enumerate(cat.exports,1):
        cl=cat.class_name(ex)
        name=cat.value(index)
        if not any(w in (cl+" "+name).lower() for w in WORDS):continue
        row={"index":index,"class":cl,"object":name,"byte_length":ex["size"]}
        try:
            fields,end=cat.props(cat.export_data(ex))
            selected=[]
            for prop,kind,extra,raw in fields[:70]:
                v={"name":prop,"type":kind,"bytes":len(raw)}
                if kind=="FloatProperty" and len(raw)==4:
                    v["value"]=struct.unpack("<f",raw)[0]
                elif kind in ["ObjectProperty","ClassProperty"] and len(raw)==4:
                    ref=struct.unpack("<i",raw)[0]
                    v["ref"]=ref
                    v["path"]=cat.path(ref)
                elif kind=="StructProperty" and len(raw)==12:
                    v["raw_floats"]=struct.unpack("<fff",raw)
                elif kind=="StructProperty" and len(raw)==16:
                    v["raw_floats"]=struct.unpack("<ffff",raw)
                elif kind=="BoolProperty":v["value"]=extra
                elif kind=="ArrayProperty":v["count"]=struct.unpack_from("<I",raw,0)[0] if len(raw)>3 else None
                selected.append(v)
            row["fields"]=selected
        except Exception as e:row["error"]=str(e)
        rows.append(row)
    return {"scene":source,"matched_objects":len(rows),"objects":rows[:200]}
def main():
    entries=r2.load_index()
    findings=[report_scene(s,entries) for s in SOURCE]
    for scene in findings:
        print("FORTNITE_ORIGINAL_SKY_FOG_ACTORS "+json.dumps(scene,sort_keys=True),flush=True)
    Path("fortnite541_sky_fog_actor_audit.json").write_text(json.dumps(findings,indent=2))
if __name__=="__main__":main()
