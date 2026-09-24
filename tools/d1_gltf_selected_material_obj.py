#!/usr/bin/env python3
"""Extract selected D1 glTF material primitives to a compact OBJ diagnostic.

The input GLB is already the exact carrier. This tool does not alter coordinates
or infer semantics; it simply writes POSITION + triangle indices for named material
TagHashes, preserving source mesh/node names in OBJ group comments.
"""
from __future__ import annotations
import argparse,json,struct,hashlib
from pathlib import Path

JSON_CHUNK=0x4E4F534A; BIN_CHUNK=0x004E4942
FMT={5120:"b",5121:"B",5122:"h",5123:"H",5125:"I",5126:"f"}
SZ={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}
NC={"SCALAR":1,"VEC2":2,"VEC3":3,"VEC4":4}

def read_glb(p):
    raw=p.read_bytes()
    if raw[:4]!=b"glTF":raise ValueError("not GLB")
    q=12;doc=None;blob=b""
    while q+8<=len(raw):
        n,t=struct.unpack_from("<II",raw,q);q+=8;c=raw[q:q+n];q+=n
        if t==JSON_CHUNK:doc=json.loads(c.decode("utf-8").rstrip(" \t\r\n\0"))
        elif t==BIN_CHUNK:blob=c
    if doc is None:raise ValueError("JSON absent")
    return doc,blob,raw

def rows(doc,blob,ai):
    a=doc["accessors"][int(ai)];bv=doc["bufferViews"][int(a["bufferView"])]
    ct=int(a["componentType"]);n=NC[a["type"]];stride=int(bv.get("byteStride",SZ[ct]*n))
    base=int(bv.get("byteOffset",0))+int(a.get("byteOffset",0))
    fmt="<"+FMT[ct]*n
    return [struct.unpack_from(fmt,blob,base+i*stride) for i in range(int(a["count"]))]

def tag(m):return str((m.get("extras") or {}).get("d1_material_taghash") or "").upper()

def main():
    ap=argparse.ArgumentParser();ap.add_argument("glb",type=Path)
    ap.add_argument("--material",action="append",required=True)
    ap.add_argument("--obj",type=Path,required=True);ap.add_argument("--report",type=Path,required=True)
    a=ap.parse_args();targets={x.upper().removeprefix("0X") for x in a.material}
    doc,blob,raw=read_glb(a.glb);mat_by_i={i:tag(m) for i,m in enumerate(doc.get("materials") or [])}
    mesh_nodes={}
    for ni,n in enumerate(doc.get("nodes") or []):
        if "mesh" in n:mesh_nodes.setdefault(int(n["mesh"]),[]).append(ni)
    out=["# exact D1 carrier diagnostic extraction"];base=1;rr=[];viol=[]
    for mi,m in enumerate(doc.get("meshes") or []):
        for pi,p in enumerate(m.get("primitives") or []):
            mh=mat_by_i.get(int(p.get("material",-1)),"")
            if mh not in targets:continue
            if int(p.get("mode",4))!=4:viol.append(f"mesh{mi}:prim{pi}:mode{p.get('mode')}");continue
            at=p.get("attributes") or {}
            if "POSITION" not in at or "indices" not in p:viol.append(f"mesh{mi}:prim{pi}:missing data");continue
            vv=rows(doc,blob,at["POSITION"]);ii=rows(doc,blob,p["indices"])
            name=(m.get("name") or f"mesh{mi}").replace(" ","_")
            out += [f"\n# material {mh}",f"g {mh}_{name}_p{pi}"]
            for v in vv:out.append(f"v {float(v[0]):.9g} {float(v[1]):.9g} {float(v[2]):.9g}")
            flat=[int(x[0]) for x in ii]
            if len(flat)%3:viol.append(f"mesh{mi}:prim{pi}:index count not /3")
            for j in range(0,len(flat)-2,3):
                out.append(f"f {base+flat[j]} {base+flat[j+1]} {base+flat[j+2]}")
            rr.append({"material":mh,"mesh_index":mi,"mesh_name":m.get("name"),"primitive_index":pi,
                       "vertex_count":len(vv),"triangle_count":len(flat)//3,
                       "nodes":[{"node_index":n,"node_name":doc["nodes"][n].get("name"),
                                 "extras":doc["nodes"][n].get("extras")} for n in mesh_nodes.get(mi,[])]})
            base+=len(vv)
    missing=targets-{x["material"] for x in rr}
    if missing:viol.append("missing materials:"+",".join(sorted(missing)))
    a.obj.parent.mkdir(parents=True,exist_ok=True);a.obj.write_text("\n".join(out)+"\n")
    rep={"schema_version":1,"status":"D1_GLTF_SELECTED_MATERIAL_OBJ_EXACT" if not viol else "D1_GLTF_SELECTED_MATERIAL_OBJ_VIOLATIONS",
         "glb_sha256":hashlib.sha256(raw).hexdigest(),"materials":sorted(targets),"rows":rr,
         "obj_sha256":hashlib.sha256(a.obj.read_bytes()).hexdigest(),"violations":viol,
         "policy":"Coordinate-preserving diagnostic extraction only; no anatomical/material semantic is inferred."}
    a.report.write_text(json.dumps(rep,indent=2)+"\n");print(json.dumps(rep,indent=2))
    return 0 if not viol else 2
if __name__=="__main__":raise SystemExit(main())
