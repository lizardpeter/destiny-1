#!/usr/bin/env python3
"""Exact glTF skin-influence census for primitives using one D1 material.

Reads only carrier-owned glTF/GLB data:
- material tag -> exact primitive set;
- JOINTS_0/WEIGHTS_0 accessors;
- skin joint-index -> node-index mapping;
- joint node names/extras;
- aggregate referenced vertex counts and total normalized weights.

No anatomical label is inferred from joint position or name.
"""
from __future__ import annotations
import argparse,hashlib,json,math,struct
from pathlib import Path
from collections import Counter,defaultdict

JSON_CHUNK=0x4E4F534A
BIN_CHUNK=0x004E4942
CT_FMT={5120:"b",5121:"B",5122:"h",5123:"H",5125:"I",5126:"f"}
CT_SIZE={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}
NCOMP={"SCALAR":1,"VEC2":2,"VEC3":3,"VEC4":4,"MAT2":4,"MAT3":9,"MAT4":16}

def read_glb(path:Path):
    raw=path.read_bytes()
    if raw[:4]!=b"glTF" or struct.unpack_from("<I",raw,4)[0]!=2:
        raise ValueError("not GLB2")
    total=struct.unpack_from("<I",raw,8)[0]
    if total!=len(raw): raise ValueError("GLB length mismatch")
    p=12;doc=None;bin_blob=b""
    while p+8<=len(raw):
        n,t=struct.unpack_from("<II",raw,p);p+=8
        chunk=raw[p:p+n];p+=n
        if t==JSON_CHUNK: doc=json.loads(chunk.decode("utf-8").rstrip(" \t\r\n\0"))
        elif t==BIN_CHUNK: bin_blob=chunk
    if doc is None: raise ValueError("JSON chunk absent")
    return doc,bin_blob,raw

def mat_tag(m):
    return str((m.get("extras") or {}).get("d1_material_taghash") or "").upper()

def accessor_rows(doc,blob,ai):
    a=doc["accessors"][int(ai)]
    if "sparse" in a: raise ValueError(f"accessor {ai}: sparse unsupported")
    if "bufferView" not in a: raise ValueError(f"accessor {ai}: no bufferView")
    bv=doc["bufferViews"][int(a["bufferView"])]
    if int(bv.get("buffer",0))!=0: raise ValueError(f"accessor {ai}: nonzero buffer")
    ct=int(a["componentType"]);typ=str(a["type"]);count=int(a["count"])
    ncomp=NCOMP[typ];cs=CT_SIZE[ct];elem=cs*ncomp
    stride=int(bv.get("byteStride",elem));base=int(bv.get("byteOffset",0))+int(a.get("byteOffset",0))
    if stride<elem: raise ValueError(f"accessor {ai}: stride {stride}<elem {elem}")
    fmt="<"+CT_FMT[ct]*ncomp
    normalized=bool(a.get("normalized",False))
    out=[]
    for i in range(count):
        off=base+i*stride
        vals=list(struct.unpack_from(fmt,blob,off))
        if normalized and ct!=5126:
            if ct in (5121,5123,5125):
                den={5121:255.0,5123:65535.0,5125:4294967295.0}[ct]
                vals=[v/den for v in vals]
            elif ct in (5120,5122):
                den={5120:127.0,5122:32767.0}[ct]
                vals=[max(-1.0,v/den) for v in vals]
        out.append(vals)
    return out,a

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("glb",type=Path)
    ap.add_argument("--material",required=True)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args();target=a.material.upper().removeprefix("0X");viol=[]
    doc,blob,raw=read_glb(a.glb)
    mats=[i for i,m in enumerate(doc.get("materials") or []) if mat_tag(m)==target]
    if len(mats)!=1: viol.append(f"material cardinality {mats!r}")
    mi=mats[0] if len(mats)==1 else -1

    mesh_nodes=defaultdict(list)
    for ni,n in enumerate(doc.get("nodes") or []):
        if "mesh" in n: mesh_nodes[int(n["mesh"])].append(ni)

    rows=[];global_weight=defaultdict(float);global_vertex_refs=Counter();global_nonzero_refs=Counter()
    for mesh_i,m in enumerate(doc.get("meshes") or []):
        for pi,p in enumerate(m.get("primitives") or []):
            if int(p.get("material",-1))!=mi: continue
            attrs=p.get("attributes") or {}
            if "JOINTS_0" not in attrs or "WEIGHTS_0" not in attrs:
                viol.append(f"mesh {mesh_i} prim {pi}: skin attrs absent");continue
            js,ja=accessor_rows(doc,blob,attrs["JOINTS_0"]);ws,wa=accessor_rows(doc,blob,attrs["WEIGHTS_0"])
            if len(js)!=len(ws): viol.append(f"mesh {mesh_i}: joint/weight count mismatch");continue
            nodes=mesh_nodes.get(mesh_i,[])
            skins=sorted({int(doc["nodes"][ni].get("skin",-1)) for ni in nodes if doc["nodes"][ni].get("skin") is not None})
            if len(skins)!=1: viol.append(f"mesh {mesh_i}: skin cardinality {skins!r}");continue
            skin_i=skins[0];skin=doc["skins"][skin_i];joint_nodes=list(skin.get("joints") or [])
            totals=defaultdict(float);vrefs=Counter();nzrefs=Counter();sum_err=0.0;max_sum_err=0.0
            for vi,(jj,ww) in enumerate(zip(js,ws)):
                s=float(sum(float(x) for x in ww));err=abs(s-1.0);sum_err+=err;max_sum_err=max(max_sum_err,err)
                for jv,wv in zip(jj,ww):
                    j=int(jv);w=float(wv)
                    if j<0 or j>=len(joint_nodes):
                        if w>1e-7: viol.append(f"mesh {mesh_i} vertex {vi}: joint {j} OOB")
                        continue
                    vrefs[j]+=1;global_vertex_refs[j]+=1
                    if w>1e-7:
                        nzrefs[j]+=1;global_nonzero_refs[j]+=1;totals[j]+=w;global_weight[j]+=w
            jr=[]
            for j in sorted(set(vrefs)|set(totals)):
                node_i=int(joint_nodes[j]);node=doc["nodes"][node_i]
                jr.append({
                    "skin_joint_index":j,"node_index":node_i,"node_name":node.get("name"),"node_extras":node.get("extras"),
                    "referenced_vertex_count":int(vrefs[j]),"nonzero_weight_vertex_count":int(nzrefs[j]),
                    "total_weight":totals[j],
                })
            jr.sort(key=lambda x:(-x["total_weight"],-x["nonzero_weight_vertex_count"],x["skin_joint_index"]))
            rows.append({
                "mesh_index":mesh_i,"mesh_name":m.get("name"),"mesh_extras":m.get("extras"),"primitive_index":pi,
                "skin_index":skin_i,"vertex_count":len(js),
                "weight_sum_mean_abs_error":sum_err/max(1,len(js)),"weight_sum_max_abs_error":max_sum_err,
                "joint_influence_count":sum(1 for x in jr if x["total_weight"]>1e-7),
                "joint_influences":jr,
            })

    global_rows=[]
    if rows:
        # all scoped rows are expected to use the same skin, but map each index from the first row's skin
        skin_i=rows[0]["skin_index"];joint_nodes=list(doc["skins"][skin_i].get("joints") or [])
        for j in sorted(set(global_vertex_refs)|set(global_weight)):
            node_i=int(joint_nodes[j]);node=doc["nodes"][node_i]
            global_rows.append({
                "skin_joint_index":j,"node_index":node_i,"node_name":node.get("name"),"node_extras":node.get("extras"),
                "referenced_vertex_count":int(global_vertex_refs[j]),"nonzero_weight_vertex_count":int(global_nonzero_refs[j]),
                "total_weight":global_weight[j],
            })
        global_rows.sort(key=lambda x:(-x["total_weight"],-x["nonzero_weight_vertex_count"],x["skin_joint_index"]))
    if not rows: viol.append("no scoped primitives")
    out={
        "schema_version":1,
        "status":"D1_GLTF_MATERIAL_SKIN_INFLUENCE_EXACT" if not viol else "D1_GLTF_MATERIAL_SKIN_INFLUENCE_VIOLATIONS",
        "glb_sha256":hashlib.sha256(raw).hexdigest(),"material_taghash":target,"material_index":mi,
        "primitive_count":len(rows),"skin_indices":sorted({r["skin_index"] for r in rows}),
        "global_joint_influences":global_rows,"primitives":rows,"violations":viol,
        "policy":"Exact glTF skin influence census only. Joint/node names are carrier provenance; no anatomical role is inferred unless separately source-closed."
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({
        "status":out["status"],"primitive_count":len(rows),
        "top_global_joint_influences":global_rows[:12],"violations":viol
    },indent=2))
    return 0 if not viol else 2
if __name__=="__main__":raise SystemExit(main())
