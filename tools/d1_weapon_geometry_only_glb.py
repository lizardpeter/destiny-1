#!/usr/bin/env python3
"""Export a skeleton-free proof/check GLB for one D1 ROI s_entity_model.

This is intentionally a geometry diagnostic rather than a renderer claim.  It
exports every deduplicated LOD1 index range once, uses neutral portable
materials, and preserves the complete set of native inline material candidates
in glTF extras.  No armature, animation, skin, or attachment transform is
created, so Blender can be used to judge the model geometry independently from
weapon-pedestal semantics.
"""
from __future__ import annotations

import argparse
import base64
import json
import struct
import sys
from pathlib import Path

import numpy as np
from pygltflib import (
    GLTF2, Asset, Scene, Node, Mesh, Primitive, Attributes,
    Buffer, BufferView, Accessor, Material, PbrMetallicRoughness,
)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_entry_extract import EntryReader
from d1_entity_model_probe import parse_model

FLOAT = 5126
UNSIGNED_SHORT = 5123
UNSIGNED_INT = 5125
ARRAY_BUFFER = 34962
ELEMENT_ARRAY_BUFFER = 34963


def snorm16(a: np.ndarray) -> np.ndarray:
    x = np.asarray(a, dtype=np.float32) / 32767.0
    return np.maximum(x, -1.0)


def tiger_to_gltf_xyz(a: np.ndarray) -> np.ndarray:
    return np.ascontiguousarray(a[:, [1, 2, 0]])


def append_buffer(gltf: GLTF2, payload: bytes) -> int:
    i = len(gltf.buffers)
    gltf.buffers.append(Buffer(
        byteLength=len(payload),
        uri="data:application/octet-stream;base64," + base64.b64encode(payload).decode("ascii"),
    ))
    return i


def append_accessor(gltf: GLTF2, a: np.ndarray, component_type: int, typ: str,
                    target: int | None = None, minmax: bool = False) -> int:
    a = np.ascontiguousarray(a)
    payload = a.tobytes()
    bi = append_buffer(gltf, payload)
    bvi = len(gltf.bufferViews)
    gltf.bufferViews.append(BufferView(buffer=bi, byteOffset=0, byteLength=len(payload), target=target))
    ai = len(gltf.accessors)
    acc = Accessor(bufferView=bvi, byteOffset=0, componentType=component_type,
                   count=int(a.shape[0]), type=typ)
    if minmax:
        x = a.reshape((a.shape[0], -1))
        acc.min = [float(v) for v in np.min(x, axis=0)]
        acc.max = [float(v) for v in np.max(x, axis=0)]
    gltf.accessors.append(acc)
    return ai


def linked_payload(r: EntryReader, by: dict[str, dict], h: str) -> tuple[bytes, bytes, dict, dict]:
    e = by[h.upper()]
    if not r.available(e["index"]):
        raise RuntimeError(f"header {h} is not resident")
    hb = r.entry(e["index"])
    pe = by.get(e["reference"].upper())
    if pe is None:
        raise KeyError(f"{h} -> missing payload entry {e['reference']}")
    if not r.available(pe["index"]):
        raise RuntimeError(f"payload {pe['tag_hash']} is not resident")
    return hb, r.entry(pe["index"]), e, pe


def strip16(values: np.ndarray) -> np.ndarray:
    out = []
    strip = []
    for raw in values.tolist():
        v = int(raw)
        if v == 0xFFFF:
            strip.clear()
            continue
        strip.append(v)
        if len(strip) < 3:
            continue
        a, b, c = strip[-3:]
        if (len(strip) - 3) & 1:
            a, b = b, a
        if a != b and b != c and a != c:
            out.append((a, b, c))
    return np.asarray(out, dtype=np.uint16).reshape((-1, 3))


def triangles(values: np.ndarray, primitive: int, is32: bool) -> np.ndarray:
    if primitive == 5:
        if is32:
            restart = 0xFFFFFFFF
            out = []
            strip = []
            for raw in values.tolist():
                v = int(raw)
                if v == restart:
                    strip.clear(); continue
                strip.append(v)
                if len(strip) >= 3:
                    a,b,c=strip[-3:]
                    if (len(strip)-3)&1: a,b=b,a
                    if a!=b and b!=c and a!=c: out.append((a,b,c))
            return np.asarray(out,dtype=np.uint32).reshape((-1,3))
        return strip16(values)
    if primitive == 3:
        n = (len(values)//3)*3
        return values[:n].reshape((-1,3)).copy()
    raise RuntimeError(f"unsupported D1 primitive type {primitive}")


def decode_mesh(r: EntryReader, by: dict[str, dict], mesh: dict, mi: int) -> tuple[dict, dict]:
    h0,p0,e0,p0e = linked_payload(r,by,mesh["vertices1"])
    h1,p1,e1,p1e = linked_payload(r,by,mesh["vertices2"])
    hi,pi,ei,pie = linked_payload(r,by,mesh["indices"])
    stride0=struct.unpack_from('<h',h0,4)[0]
    stride1=struct.unpack_from('<h',h1,4)[0]
    type0=struct.unpack_from('<h',h0,6)[0]
    type1=struct.unpack_from('<h',h1,6)[0]
    if stride0 != 8:
        raise RuntimeError(f"mesh {mi}: this diagnostic currently requires D1 position stride 8, got {stride0}")
    if stride1 not in (20,24):
        raise RuntimeError(f"mesh {mi}: unsupported secondary stride {stride1}")
    r0=np.frombuffer(p0,dtype='<i2').reshape((-1,stride0//2))
    r1=np.frombuffer(p1,dtype='<i2').reshape((-1,stride1//2))
    if len(r0)!=len(r1): raise RuntimeError(f"mesh {mi}: stream count mismatch")

    scale=np.asarray(mesh["model_scale"][:3],dtype=np.float32)
    trans=np.asarray(mesh["model_translation"][:3],dtype=np.float32)
    pos_tiger=snorm16(r0[:,:3])*scale+trans
    pos=tiger_to_gltf_xyz(pos_tiger).astype(np.float32)

    uvscale=np.asarray(mesh["texcoord_scale"],dtype=np.float32)
    uvtrans=np.asarray(mesh["texcoord_translation"],dtype=np.float32)
    uv=(snorm16(r1[:,:2])*uvscale+uvtrans).astype(np.float32)
    n_tiger=snorm16(r1[:,2:5])
    lengths=np.linalg.norm(n_tiger,axis=1,keepdims=True)
    n_tiger=np.divide(n_tiger,np.maximum(lengths,1e-8))
    normals=tiger_to_gltf_xyz(n_tiger).astype(np.float32)

    is32=bool(hi[1]) if len(hi)>=2 else False
    idx=np.frombuffer(pi,dtype='<u4' if is32 else '<u2')
    groups={}
    for part in mesh["parts"]:
        if int(part["lod"]) != 1: continue
        key=(int(part["index_offset"]),int(part["index_count"]),int(part["primitive_type"]))
        groups.setdefault(key,[]).append(part)
    ranges=[]
    for (off,count,primitive),parts in sorted(groups.items()):
        tri=triangles(idx[off:off+count],primitive,is32)
        ranges.append({
            "index_offset":off,"index_count":count,"primitive_type":primitive,
            "materials":sorted({p["material"] for p in parts}),
            "variant_shader_indices":sorted({int(p["variant_shader_index"]) for p in parts}),
            "triangles":tri,
        })
    report={
        "mesh_index":mi,"vertex_count":int(len(r0)),"stride0":stride0,"type0":type0,
        "stride1":stride1,"type1":type1,
        "position_header":e0["tag_hash"],"position_payload":p0e["tag_hash"],
        "secondary_header":e1["tag_hash"],"secondary_payload":p1e["tag_hash"],
        "index_header":ei["tag_hash"],"index_payload":pie["tag_hash"],
        "fourth_i16_unique":sorted({int(x) for x in r0[:,3].tolist()}),
        "bbox_gltf":{"min":pos.min(axis=0).astype(float).tolist(),"max":pos.max(axis=0).astype(float).tolist()},
        "lod1_ranges":[{k:v for k,v in q.items() if k!='triangles'}|{"triangle_count":int(len(q['triangles']))} for q in ranges],
        "lod1_triangle_count":int(sum(len(q['triangles']) for q in ranges)),
    }
    return {"positions":pos,"normals":normals,"uv":uv,"ranges":ranges,"is32":is32},report


def build(a) -> dict:
    r=EntryReader(a.pkg,a.runtime)
    by={e["tag_hash"].upper():e for e in r.entries}
    tag=a.model.upper().removeprefix('0X')
    me=by[tag]
    model=parse_model(r.entry(me["index"]),r.h["platform"])
    decoded=[]; reports=[]
    for mi,m in enumerate(model["meshes"]):
        d,rep=decode_mesh(r,by,m,mi); decoded.append(d); reports.append(rep)

    gltf=GLTF2(asset=Asset(version='2.0',generator='destiny-1 d1_weapon_geometry_only_glb.py'),
               scene=0,scenes=[Scene(nodes=[])],nodes=[],meshes=[],materials=[],buffers=[],bufferViews=[],accessors=[])
    gltf.materials.append(Material(name='GeometryCheck_Neutral',pbrMetallicRoughness=PbrMetallicRoughness(
        baseColorFactor=[0.55,0.55,0.55,1.0],metallicFactor=0.0,roughnessFactor=0.7),
        extras={"portableDiagnostic":True,"nativeMaterialSemantics":"preserved per primitive in extras"}))
    nodes=[]
    for mi,d in enumerate(decoded):
        pa=append_accessor(gltf,d['positions'].astype('<f4'),FLOAT,'VEC3',ARRAY_BUFFER,True)
        na=append_accessor(gltf,d['normals'].astype('<f4'),FLOAT,'VEC3',ARRAY_BUFFER)
        ua=append_accessor(gltf,d['uv'].astype('<f4'),FLOAT,'VEC2',ARRAY_BUFFER)
        prims=[]
        for q in d['ranges']:
            flat=q['triangles'].reshape(-1)
            if d['is32']:
                ia=append_accessor(gltf,flat.astype('<u4'),UNSIGNED_INT,'SCALAR',ELEMENT_ARRAY_BUFFER)
            else:
                ia=append_accessor(gltf,flat.astype('<u2'),UNSIGNED_SHORT,'SCALAR',ELEMENT_ARRAY_BUFFER)
            prims.append(Primitive(attributes=Attributes(POSITION=pa,NORMAL=na,TEXCOORD_0=ua),indices=ia,material=0,mode=4,
                                   extras={"d1IndexOffset":q['index_offset'],"d1IndexCount":q['index_count'],
                                           "d1PrimitiveType":q['primitive_type'],"d1MaterialCandidates":q['materials'],
                                           "d1VariantShaderIndices":q['variant_shader_indices']}))
        meshi=len(gltf.meshes)
        gltf.meshes.append(Mesh(name=f'{tag}_mesh{mi}_LOD1_GEOMETRY_CHECK',primitives=prims,
                                extras={"d1Model":tag,"d1MeshIndex":mi,"noSkeleton":True,"noAttachmentTransform":True}))
        ni=len(gltf.nodes)
        gltf.nodes.append(Node(name=f'{tag}_mesh{mi}',mesh=meshi))
        nodes.append(ni)
    gltf.scenes[0].nodes=nodes
    gltf.extras={"d1Model":tag,"packageSnapshot":str(a.pkg),"purpose":"Skeleton-free geometry check",
                 "coordinateConversion":"Tiger [x,y,z] -> glTF [y,z,x]",
                 "warning":"No skeleton, animation, attachment transform, texture, or native renderer claim is present."}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    gltf.save_binary(str(a.out))
    rep={"output":str(a.out),"bytes":a.out.stat().st_size,"model":tag,"entry_index":me['index'],
         "model_size":me['file_size'],"mesh_count":len(decoded),"total_lod1_triangles":sum(x['lod1_triangle_count'] for x in reports),
         "meshes":reports}
    a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps(rep,indent=2))
    return rep


def main():
    ap=argparse.ArgumentParser();ap.add_argument('pkg',type=Path);ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--model',default='80A39E12');ap.add_argument('--out',type=Path,required=True);ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args();build(a)

if __name__=='__main__': main()
