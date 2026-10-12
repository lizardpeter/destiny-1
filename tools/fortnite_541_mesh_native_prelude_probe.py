#!/usr/bin/env python3
"""Inspect exact 5.41 original native StaticMesh preludes and socket variants.

Inputs are the SHA1-verified 248 source Factory mesh pairs staged in the
existing native LOD proof. Only names, bounded numeric fields and short
headers are emitted; do not assume that a gigantic socket count is valid.
"""
from pathlib import Path
import json,struct,collections
from fortnite_541_material_expression_probe import Catalog

def read_native(identity,stem):
    p=Path(stem)
    cat=Catalog(p.with_suffix(".uasset").read_bytes(),
                p.with_suffix(".uexp").read_bytes())
    name=identity.rsplit("::",1)[-1]
    for i,ex in enumerate(cat.exports,1):
        if cat.class_name(ex)=="StaticMesh" and cat.value(i)==name:
            data=cat.export_data(ex)
            _,used=cat.props(data)
            return data[used:],cat
    raise ValueError(f"original source mesh {identity} absent")
def u32(s,p):
    return struct.unpack_from("<I",s,p)[0] if p+4<=len(s) else None
def run():
    rows=[]
    target=Path("/tmp/fortnite541_factory_lod0.tsv")
    for line in target.read_text().splitlines():
        identity,n,stem=line.split("\t")
        if not stem:continue
        native,cat=read_native(identity,stem)
        count=u32(native,34)
        if count is not None and 64<count<=512 and len(native)>=38+4*count+5:
            references=list(struct.unpack_from("<"+"i"*count,native,38))
            obj_sockets={
                "read":len(references),
                "min":min(references),"max":max(references),
                "unique":len(set(references)),
                "non_positive":[r for r in references if r<=0][:10],
                "lod_count_after_sockets":u32(native,38+4*count),
                "next_strip_bytes":native[42+4*count:44+4*count].hex(),
                "socket_export_class_samples":[
                    cat.class_name(cat.exports[j-1]) if 0<j<=len(cat.exports)
                    else "<invalid ref>" for j in references[:10]
                ],
                "socket_references_last":references[-10:],
                "source_export_count":len(cat.exports),
            }
        else:
            obj_sockets=None
        obj={"name":identity,"actors":int(n),
             "native_bytes":len(native),"first64":native[:64].hex(),
             "at_offsets":{str(p):u32(native,p) for p in (6,10,14,18,26,30,34,38,42,46,50,54)},
             "socket_count":count,"source_flags":[native[0],native[1],list(native[2:6])],
             "source_names":[name for name in cat.names if "Socket" in name][:12],
             "authored_large_socket_list":obj_sockets}
        rows.append(obj)
    unusual=[o for o in rows if o["socket_count"] is None or o["socket_count"]>64]
    normal=[o for o in rows if o["socket_count"] is not None and o["socket_count"]<=64]
    print("FORTNITE_NATIVE_PRELUDE_VARIANT_SUMMARY "+json.dumps({
        "meshes":len(rows),"normal":len(normal),"unusual":len(unusual),
        "normal_first":normal[:10],"unusual_all":unusual,
        "socket_histogram":collections.Counter(str(o["socket_count"]) for o in rows).most_common(18)
    },sort_keys=True),flush=True)
if __name__=="__main__":run()
