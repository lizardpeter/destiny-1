#!/usr/bin/env python3
"""Bake evaluated rigid-weapon joint motion onto a directly animated GLB node.

Destiny weapon geometry in the current D1 fixture is rigid and has no native
per-vertex skin weights.  The proof exporter parents that rigid object under the
recovered weapon Pedestal joint C410084A.  Some interchange importers preserve
joint animation but do not preserve ordinary object children of joint nodes in
a way that visibly follows the imported armature.

This tool does NOT invent internal articulation.  It evaluates the source
joint's exact glTF world transform through every animated ancestor and writes
that same T/R/S onto a normal scene-root WeaponRoot node.  Static source clips
can be omitted by measured world-motion thresholds.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
from pathlib import Path

import numpy as np

JSON_CHUNK = 0x4E4F534A
BIN_CHUNK = 0x004E4942
FLOAT = 5126


def read_glb(path: Path):
    b = path.read_bytes()
    if b[:4] != b"glTF" or struct.unpack_from("<I", b, 4)[0] != 2:
        raise ValueError("not a glTF 2.0 GLB")
    if struct.unpack_from("<I", b, 8)[0] != len(b):
        raise ValueError("GLB declared length mismatch")
    o = 12
    chunks = []
    while o < len(b):
        n, typ = struct.unpack_from("<II", b, o)
        o += 8
        chunks.append((typ, b[o:o+n]))
        o += n
    if not chunks or chunks[0][0] != JSON_CHUNK:
        raise ValueError("GLB missing JSON chunk")
    j = json.loads(chunks[0][1].decode("utf-8").rstrip("\x00 "))
    bins = [x for typ, x in chunks if typ == BIN_CHUNK]
    if len(bins) != 1:
        raise ValueError(f"expected exactly one BIN chunk, got {len(bins)}")
    if len(j.get("buffers", [])) != 1:
        raise ValueError("direct baker currently requires one GLB buffer")
    return j, bytearray(bins[0])


def write_glb(path: Path, j: dict, binary: bytearray):
    while len(binary) & 3:
        binary.append(0)
    j["buffers"][0]["byteLength"] = len(binary)
    jb = json.dumps(j, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    jb += b" " * ((-len(jb)) & 3)
    total = 12 + 8 + len(jb) + 8 + len(binary)
    out = bytearray(struct.pack("<4sII", b"glTF", 2, total))
    out += struct.pack("<II", len(jb), JSON_CHUNK) + jb
    out += struct.pack("<II", len(binary), BIN_CHUNK) + binary
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(out)


def accessor_f32(j: dict, binary: bytearray, index: int) -> np.ndarray:
    a = j["accessors"][index]
    if a.get("componentType") != FLOAT:
        raise ValueError(f"accessor {index}: expected FLOAT, got {a.get('componentType')}")
    ncomp = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}[a["type"]]
    bv = j["bufferViews"][a["bufferView"]]
    if bv.get("buffer", 0) != 0:
        raise ValueError("accessor references nonzero buffer")
    base = int(bv.get("byteOffset", 0)) + int(a.get("byteOffset", 0))
    count = int(a["count"])
    stride = int(bv.get("byteStride", ncomp * 4))
    if stride == ncomp * 4:
        return np.frombuffer(binary, dtype="<f4", count=count*ncomp, offset=base).reshape(count, ncomp).copy()
    out = np.empty((count, ncomp), dtype=np.float32)
    for i in range(count):
        out[i] = np.frombuffer(binary, dtype="<f4", count=ncomp, offset=base + i*stride)
    return out


def append_f32_accessor(j: dict, binary: bytearray, values: np.ndarray, typ: str, *, minmax=False) -> int:
    a = np.ascontiguousarray(values, dtype="<f4")
    while len(binary) & 3:
        binary.append(0)
    off = len(binary)
    payload = a.tobytes()
    binary.extend(payload)
    bvi = len(j.setdefault("bufferViews", []))
    j["bufferViews"].append({"buffer": 0, "byteOffset": off, "byteLength": len(payload)})
    acc = {"bufferView": bvi, "byteOffset": 0, "componentType": FLOAT, "count": int(a.shape[0]), "type": typ}
    if minmax:
        flat = a.reshape(a.shape[0], -1)
        acc["min"] = [float(x) for x in flat.min(axis=0)]
        acc["max"] = [float(x) for x in flat.max(axis=0)]
    ai = len(j.setdefault("accessors", []))
    j["accessors"].append(acc)
    return ai


def qnorm(q):
    q = np.asarray(q, dtype=np.float64)
    n = float(np.linalg.norm(q))
    return q / n if n > 1e-15 else np.array([0.0, 0.0, 0.0, 1.0])


def qslerp(a, b, t):
    a = qnorm(a); b = qnorm(b)
    dot = float(np.dot(a, b))
    if dot < 0.0:
        b = -b; dot = -dot
    dot = max(-1.0, min(1.0, dot))
    if dot > 0.9995:
        return qnorm(a + t*(b-a))
    th = math.acos(dot)
    s = math.sin(th)
    return qnorm(math.sin((1-t)*th)/s*a + math.sin(t*th)/s*b)


def qmat(q):
    x,y,z,w = qnorm(q)
    return np.array([
        [1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
        [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
        [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)],
    ], dtype=np.float64)


def matq(m):
    # Stable matrix -> xyzw quaternion conversion.
    m = np.asarray(m, dtype=np.float64)
    tr = float(np.trace(m))
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2; w = 0.25*s
        x = (m[2,1]-m[1,2])/s; y = (m[0,2]-m[2,0])/s; z = (m[1,0]-m[0,1])/s
    elif m[0,0] > m[1,1] and m[0,0] > m[2,2]:
        s = math.sqrt(max(0.0, 1+m[0,0]-m[1,1]-m[2,2]))*2
        w=(m[2,1]-m[1,2])/s; x=.25*s; y=(m[0,1]+m[1,0])/s; z=(m[0,2]+m[2,0])/s
    elif m[1,1] > m[2,2]:
        s = math.sqrt(max(0.0, 1+m[1,1]-m[0,0]-m[2,2]))*2
        w=(m[0,2]-m[2,0])/s; x=(m[0,1]+m[1,0])/s; y=.25*s; z=(m[1,2]+m[2,1])/s
    else:
        s = math.sqrt(max(0.0, 1+m[2,2]-m[0,0]-m[1,1]))*2
        w=(m[1,0]-m[0,1])/s; x=(m[0,2]+m[2,0])/s; y=(m[1,2]+m[2,1])/s; z=.25*s
    return qnorm([x,y,z,w])


def trs_matrix(t, q, s):
    out = np.eye(4, dtype=np.float64)
    out[:3,:3] = qmat(q) @ np.diag(np.asarray(s, dtype=np.float64))
    out[:3,3] = np.asarray(t, dtype=np.float64)
    return out


def decompose(m):
    t = np.asarray(m[:3,3], dtype=np.float64)
    a = np.asarray(m[:3,:3], dtype=np.float64)
    s = np.linalg.norm(a, axis=0)
    s = np.where(s < 1e-12, 1.0, s)
    r = a / s
    if np.linalg.det(r) < 0:
        s[0] *= -1; r[:,0] *= -1
    return t, matq(r), s


def node_base_trs(node: dict):
    if "matrix" in node and node["matrix"] is not None:
        # glTF matrices are column-major.
        m = np.asarray(node["matrix"], dtype=np.float64).reshape((4,4), order="F")
        return decompose(m)
    return (
        np.asarray(node.get("translation", [0,0,0]), dtype=np.float64),
        qnorm(node.get("rotation", [0,0,0,1])),
        np.asarray(node.get("scale", [1,1,1]), dtype=np.float64),
    )


def parents_of(j: dict):
    p = {}
    for i,n in enumerate(j.get("nodes", [])):
        for c in n.get("children", []) or []:
            if c in p: raise ValueError(f"node {c} has multiple parents")
            p[c] = i
    return p


def source_chain(j: dict, source: int):
    p = parents_of(j); chain=[source]
    while chain[-1] in p: chain.append(p[chain[-1]])
    chain.reverse(); return chain


def sample_track(times, values, t, path, interpolation):
    if len(times) == 1 or t <= times[0]: return values[0]
    if t >= times[-1]: return values[-1]
    hi = int(np.searchsorted(times, t, side="right")); lo = hi-1
    if interpolation == "STEP": return values[lo]
    if interpolation == "CUBICSPLINE": raise ValueError("CUBICSPLINE source channel not supported by rigid baker")
    den = float(times[hi]-times[lo]); u = 0.0 if abs(den)<1e-15 else float((t-times[lo])/den)
    if path == "rotation": return qslerp(values[lo], values[hi], u)
    return values[lo]*(1-u) + values[hi]*u


def animation_tracks(j, binary, anim):
    tracks = {}
    all_times=[]
    for ch in anim.get("channels", []):
        target=ch["target"]; node=int(target["node"]); path=target["path"]
        if path not in ("translation","rotation","scale"): continue
        smp=anim["samplers"][int(ch["sampler"])]
        times=accessor_f32(j,binary,int(smp["input"]))[:,0].astype(np.float64)
        vals=accessor_f32(j,binary,int(smp["output"])).astype(np.float64)
        tracks[(node,path)] = (times, vals, smp.get("interpolation","LINEAR"))
        all_times.extend(float(x) for x in times)
    return tracks, np.asarray(sorted(set(all_times)),dtype=np.float64)


def eval_world(j, chain, tracks, t):
    world=np.eye(4,dtype=np.float64)
    for ni in chain:
        bt,bq,bs=node_base_trs(j["nodes"][ni])
        vals={"translation":bt,"rotation":bq,"scale":bs}
        for path in ("translation","rotation","scale"):
            tr=tracks.get((ni,path))
            if tr is not None: vals[path]=sample_track(*tr[:2],t,path,tr[2])
        world = world @ trs_matrix(vals["translation"], vals["rotation"], vals["scale"])
    return decompose(world)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input",type=Path)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--source-node",type=int,default=72)
    ap.add_argument("--report",type=Path,required=True)
    ap.add_argument("--translation-threshold",type=float,default=1e-3)
    ap.add_argument("--rotation-threshold-deg",type=float,default=0.25)
    ap.add_argument("--scale-threshold",type=float,default=1e-3)
    ap.add_argument("--keep-static",action="store_true")
    args=ap.parse_args()

    j,binary=read_glb(args.input)
    src=args.source_node
    if src<0 or src>=len(j.get("nodes",[])): raise ValueError("source node out of range")
    mesh_children=[x for x in (j["nodes"][src].get("children",[]) or []) if j["nodes"][x].get("mesh") is not None]
    if not mesh_children: raise RuntimeError(f"source node {src} has no rigid mesh children")
    j["nodes"][src]["children"]=[x for x in (j["nodes"][src].get("children",[]) or []) if x not in mesh_children]

    chain=source_chain(j,src)
    rest_world=np.eye(4,dtype=np.float64)
    for ni in chain:
        rest_world=rest_world@trs_matrix(*node_base_trs(j["nodes"][ni]))
    rt,rq,rs=decompose(rest_world)
    direct_idx=len(j["nodes"])
    j["nodes"].append({
        "name":"WeaponRoot_DIRECT_BAKED",
        "children":mesh_children,
        "translation":[float(x) for x in rt],
        "rotation":[float(x) for x in rq],
        "scale":[float(x) for x in rs],
        "extras":{
            "sourceJointNode":src,
            "sourceJointName":j["nodes"][src].get("name"),
            "sourceJointChain":chain,
            "method":"evaluated source-joint world TRS; no invented internal articulation",
        },
    })
    scene_idx=int(j.get("scene",0)); roots=j["scenes"][scene_idx].setdefault("nodes",[])
    if direct_idx not in roots: roots.append(direct_idx)

    source_anims=list(j.get("animations",[])); new_anims=[]; rows=[]
    for anim in source_anims:
        tracks,times=animation_tracks(j,binary,anim)
        if len(times)==0: continue
        T=[];Q=[];S=[]
        for t in times:
            tt,qq,ss=eval_world(j,chain,tracks,float(t));T.append(tt);Q.append(qq);S.append(ss)
        T=np.asarray(T,dtype=np.float32);Q=np.asarray(Q,dtype=np.float32);S=np.asarray(S,dtype=np.float32)
        td=float(np.max(np.linalg.norm(T-T[0],axis=1)))
        qn=Q/np.maximum(np.linalg.norm(Q,axis=1,keepdims=True),1e-12); dots=np.clip(np.abs(qn@qn[0]),0,1)
        rd=float(np.degrees(np.max(2*np.arccos(dots))))
        sd=float(np.max(np.linalg.norm(S-S[0],axis=1)))
        moving=td>args.translation_threshold or rd>args.rotation_threshold_deg or sd>args.scale_threshold
        source_name=anim.get("name",f"animation_{len(rows)}")
        row={"source_animation":source_name,"sample_count":len(times),"translation_delta":td,"rotation_delta_deg":rd,"scale_delta":sd,"moving":moving}
        rows.append(row)
        if not moving and not args.keep_static: continue
        ti=append_f32_accessor(j,binary,times.astype(np.float32).reshape(-1,1),"SCALAR",minmax=True)
        ta=append_f32_accessor(j,binary,T,"VEC3")
        qa=append_f32_accessor(j,binary,Q,"VEC4")
        sa=append_f32_accessor(j,binary,S,"VEC3")
        new_anims.append({
            "name":source_name+"_VISIBLE_WEAPON",
            "extras":{"sourceAnimation":source_name,"sourceJointNode":src,"worldMotion":{"translationDelta":td,"rotationDeltaDeg":rd,"scaleDelta":sd}},
            "samplers":[
                {"input":ti,"output":ta,"interpolation":"LINEAR"},
                {"input":ti,"output":qa,"interpolation":"LINEAR"},
                {"input":ti,"output":sa,"interpolation":"LINEAR"},
            ],
            "channels":[
                {"sampler":0,"target":{"node":direct_idx,"path":"translation"}},
                {"sampler":1,"target":{"node":direct_idx,"path":"rotation"}},
                {"sampler":2,"target":{"node":direct_idx,"path":"scale"}},
            ],
        })
    j["animations"]=new_anims
    j.setdefault("extras",{}).setdefault("d1RigidWeaponMotionBake",{}).update({
        "sourceNode":src,"directNode":direct_idx,"meshChildren":mesh_children,"sourceChain":chain,
        "staticClipsOmitted":not args.keep_static,"sourceAnimationCount":len(source_anims),"outputAnimationCount":len(new_anims),
    })
    write_glb(args.out,j,binary)
    report={
        "input":str(args.input),"output":str(args.out),"output_bytes":args.out.stat().st_size,
        "source_node":src,"source_node_name":j["nodes"][src].get("name"),"source_chain":chain,
        "direct_node":direct_idx,"mesh_children":mesh_children,
        "source_animation_count":len(source_anims),"output_animation_count":len(new_anims),
        "output_animation_names":[x["name"] for x in new_anims],"clips":rows,
        "thresholds":{"translation":args.translation_threshold,"rotation_deg":args.rotation_threshold_deg,"scale":args.scale_threshold},
        "semantic_boundary":"Rigid world-pose compatibility bake only; no internal weapon animation or skin weights are invented.",
    }
    args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__": main()
