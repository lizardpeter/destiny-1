#!/usr/bin/env python3
"""Locate every primitive using one exact D1 material inside a GLB carrier.

This is a geometry/ownership diagnostic only.  It does not infer a semantic role
from shape or location.  It records the exact glTF node/mesh/primitive ownership,
POSITION accessor bounds, index/vertex counts and source extras for later reasoning.
"""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path

JSON_CHUNK=0x4E4F534A

def read_glb_json(path:Path)->dict:
    raw=path.read_bytes()
    if raw[:4]!=b"glTF" or struct.unpack_from("<I",raw,4)[0]!=2:
        raise ValueError("not glTF 2 GLB")
    n,t=struct.unpack_from("<II",raw,12)
    if t!=JSON_CHUNK: raise ValueError("first GLB chunk is not JSON")
    return json.loads(raw[20:20+n].decode("utf-8").rstrip(" \t\r\n\0"))

def tag(m:dict)->str:
    return str((m.get("extras") or {}).get("d1_material_taghash") or "").upper()

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("glb",type=Path)
    ap.add_argument("--material",required=True)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args(); target=a.material.upper().removeprefix("0X")
    d=read_glb_json(a.glb); viol=[]
    mats=[i for i,m in enumerate(d.get("materials") or []) if tag(m)==target]
    if len(mats)!=1: viol.append(f"material index cardinality {mats!r}")
    mi=mats[0] if len(mats)==1 else -1

    mesh_nodes={}
    for ni,n in enumerate(d.get("nodes") or []):
        if "mesh" in n: mesh_nodes.setdefault(int(n["mesh"]),[]).append(ni)

    rows=[]
    for mesh_i,m in enumerate(d.get("meshes") or []):
        for pi,p in enumerate(m.get("primitives") or []):
            if int(p.get("material",-1))!=mi: continue
            attrs=p.get("attributes") or {}
            pos_i=attrs.get("POSITION")
            if pos_i is None:
                viol.append(f"mesh {mesh_i} prim {pi}: POSITION absent");continue
            acc=(d.get("accessors") or [])[int(pos_i)]
            idx_i=p.get("indices")
            idx_acc=None if idx_i is None else (d.get("accessors") or [])[int(idx_i)]
            node_rows=[]
            for ni in mesh_nodes.get(mesh_i,[]):
                n=d["nodes"][ni]
                node_rows.append({
                    "node_index":ni,"node_name":n.get("name"),
                    "skin":n.get("skin"),
                    "matrix":n.get("matrix"),"translation":n.get("translation"),
                    "rotation":n.get("rotation"),"scale":n.get("scale"),
                    "extras":n.get("extras"),
                })
            mn=acc.get("min");mx=acc.get("max")
            extent=None;center=None
            if isinstance(mn,list) and isinstance(mx,list) and len(mn)>=3 and len(mx)>=3:
                extent=[float(mx[i])-float(mn[i]) for i in range(3)]
                center=[(float(mx[i])+float(mn[i]))*.5 for i in range(3)]
            mode=int(p.get("mode",4))
            index_count=None if idx_acc is None else int(idx_acc.get("count",0))
            triangles=(index_count//3 if mode==4 and index_count is not None else None)
            rows.append({
                "mesh_index":mesh_i,"mesh_name":m.get("name"),"mesh_extras":m.get("extras"),
                "primitive_index":pi,"primitive_mode":mode,
                "position_accessor":int(pos_i),"vertex_count":int(acc.get("count",0)),
                "position_min":mn,"position_max":mx,"position_center":center,"position_extent":extent,
                "indices_accessor":idx_i,"index_count":index_count,"triangle_count_if_triangles":triangles,
                "primitive_extras":p.get("extras"),"nodes":node_rows,
            })
    if not rows: viol.append("no primitive uses target material")
    out={
        "schema_version":1,
        "status":"D1_GLTF_MATERIAL_PRIMITIVE_GEOMETRY_EXACT" if not viol else "D1_GLTF_MATERIAL_PRIMITIVE_GEOMETRY_VIOLATIONS",
        "glb":str(a.glb),"glb_sha256":hashlib.sha256(a.glb.read_bytes()).hexdigest(),
        "material_taghash":target,"material_index":mi,
        "primitive_count":len(rows),
        "total_vertex_reference_count":sum(x["vertex_count"] for x in rows),
        "total_triangle_count_if_triangles":sum(x["triangle_count_if_triangles"] or 0 for x in rows),
        "primitives":rows,"violations":viol,
        "policy":"Exact glTF carrier ownership/bounds only. Geometry shape/location is not promoted to a gameplay, visibility, emissive, UI, or effect semantic without independent source evidence."
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({
        "status":out["status"],"material":target,"primitive_count":len(rows),
        "total_vertices":out["total_vertex_reference_count"],"total_triangles":out["total_triangle_count_if_triangles"],
        "rows":[{k:r[k] for k in ("mesh_index","mesh_name","primitive_index","vertex_count","triangle_count_if_triangles","position_center","position_extent")} for r in rows],
        "violations":viol,
    },indent=2))
    return 0 if not viol else 2
if __name__=="__main__":raise SystemExit(main())
