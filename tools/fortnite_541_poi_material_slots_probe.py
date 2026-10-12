#!/usr/bin/env python3
"""Audit native full-detail Fortnite POI StaticMesh material-slot identities.

Consumes the original SHA1 verified Factory 248 mesh packages already staged
by the independent native LOD0 proof. Never guess material identities by
filename, and never create generic game-specific shader branches.
"""
from pathlib import Path
import collections,json,struct
from fortnite_541_material_expression_probe import Catalog

SOURCE=Path("/tmp/fortnite541_factory_lod0.tsv")
def main():
    parsed=SOURCE.read_text().splitlines()
    assets={}
    samples=[]
    missing=collections.Counter()
    tagged=collections.Counter()
    slots=collections.Counter()
    found=0
    for index,line in enumerate(parsed):
        path,n,stem=line.split("\t")
        if not stem:continue
        if stem in assets:continue
        p=Path(stem)
        c=Catalog(p.with_suffix(".uasset").read_bytes(),p.with_suffix(".uexp").read_bytes())
        rec=[]
        for i,ex in enumerate(c.exports,1):
            if c.class_name(ex)!="StaticMesh":continue
            raw=c.export_data(ex)
            fields,offset=c.props(raw)
            tags=[{"name":name,"kind":kind,"meta":meta,"size":len(body),
                "head":body[:128].hex() if name=="StaticMaterials" else None}
                for name,kind,meta,body in fields]
            found+=1
            for t in tags:tagged[t["name"]]+=1
            slot=[t for t in tags if t["name"] in
                  ("StaticMaterials","Materials","SectionInfoMap","MaterialSlotName")]
            if slot:
                slots[tuple(t["name"] for t in slot)]+=1
            elif len(missing)<8:
                missing[c.value(i)]+=1
            if len(samples)<12 or any(t["name"]=="StaticMaterials" for t in slot) and len(samples)<22:
                samples.append({"source":path,"file":p.name,"object":c.value(i),
                    "slots":slot,"fields":tags[:36],"native_bytes":len(raw)-offset,
                    "source_imports":[c.path(-j) for j in range(1,min(len(c.imports),18)+1)]})
            rec.append((c.value(i),slot))
        assets[stem]=rec
    print("FORTNITE_541_NATIVE_STATICMESH_MATERIAL_SLOTS "+json.dumps({
        "unique_packages":len(assets),"source_staticmesh_exports":found,
        "source_property_tags":tagged.most_common(30),
        "material_slot_tag_combinations":[{"tags":list(k),"count":v} for k,v in slots.most_common()],
        "missing_material_slot_tags":missing.most_common(),
        "samples":samples,
    },sort_keys=True),flush=True)
if __name__=="__main__":main()
