#!/usr/bin/env python3
"""Rebuild the compact retail Tower 809DCD66 scene from a proven world sidecar.

This intentionally consumes the already validated ``TOWER_80C98254_WORLD.json``
sidecar rather than reinterpreting map tables. The sidecar fixes source geometry,
index slices, per-instance UV triples and affine transforms; current retail package
backings supply the exact vertex/index bytes.

Only materials present in the supplied 809DCD66 adapter manifest are emitted.
For the pinned Tower cell this is exactly 12 geometry variants / 64 placements /
5 materials. Source D1 tangent xyzw is retained as ``_D1_TANGENT``; a later
loss-preserving postprocessor exposes split Blender-facing attributes without
promoting standard glTF TANGENT semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import sys

import numpy as np
import trimesh

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

import d1_tower_map_schema_validate_v5 as v5
import d1_tower_static_chunk_export as base
from d1_world_static_common import apply_d1_instance_uv, d1_world_to_gltf_matrix
from d1_tower_80ca0dda_vs_replay import decode_static_inputs


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--world',type=Path,required=True)
    ap.add_argument('--adapter-manifest',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args()

    world=json.loads(a.world.read_text())
    adapter=json.loads(a.adapter_manifest.read_text())
    targets={str(h).upper() for h in adapter['materials']}
    c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())

    geoms=[g for g in world['geometry'] if str(g.get('source_key',{}).get('material_hash','')).upper() in targets]
    nodes=[n for n in world['nodes'] if str(n.get('material_hash','')).upper() in targets]
    if len(geoms)!=12 or len(nodes)!=64:
        raise SystemExit(f'pinned retail target fixture changed: geometry={len(geoms)} nodes={len(nodes)}')
    cell_mats=sorted({str(n['material_hash']).upper() for n in nodes})
    if len(cell_mats)!=5:
        raise SystemExit(f'pinned retail target material count changed: {cell_mats}')

    by_geom=defaultdict(list)
    for n in nodes: by_geom[n['geometry']].append(n)
    refs={}
    def ref(h):
        h=str(h).upper()
        if h not in refs: refs[h]=base.read_reference_file(c,h)
        return refs[h]

    scene=trimesh.Scene(); grows=[]; nrows=[]; total_triangles=0; total_unique_vertices=0
    for g in geoms:
        k=g['source_key']; mh=str(k['material_hash']).upper()
        v0=ref(k['vertices0']);v1=ref(k['vertices1']);ib=ref(k['indices'])
        s0=base.hdr_stride(v0['header']);s1=base.hdr_stride(v1['header'])
        if (s0,s1)!=(8,20): raise AssertionError((g['geometry'],s0,s1))
        inp=decode_static_inputs(v0['backing'],v1['backing'])
        inds=base.decode_indices(ib['backing'],base.index_is32(ib['header']))
        off=int(k['index_offset']);cnt=int(k['index_count']);prim=int(k['primitive_type'])
        faces_source=base.primitive_faces(inds[off:off+cnt],prim,base.index_is32(ib['header']))
        if len(faces_source)==0: raise AssertionError(f"{g['geometry']}: no faces")
        used,inv=np.unique(faces_source.reshape(-1),return_inverse=True); faces=inv.reshape((-1,3))
        if used.tolist()!=g['source_vertex_indices']:
            raise AssertionError(f"{g['geometry']}: source vertex identity changed")

        placements=by_geom[g['geometry']]
        if len(placements)!=int(g['placement_count']): raise AssertionError(g['geometry'])
        uvtr=np.asarray(g['uv_transform'],dtype=np.float32)
        uv=apply_d1_instance_uv(inp.v8_v9_uv[used],float(uvtr[0]),float(uvtr[1]),float(uvtr[2]))
        verts=inp.v4_v6_position[used]
        norms=inp.v12_v14_normal[used]
        tang=inp.v16_v19_tangent[used]

        visual=trimesh.visual.TextureVisuals(uv=uv,material=trimesh.visual.material.PBRMaterial(name=f'TigerMaterial_{mh}'))
        tm=trimesh.Trimesh(vertices=verts,faces=faces,visual=visual,process=False,validate=False)
        tm.vertex_normals=norms
        tm.vertex_attributes['D1_TANGENT']=tang.astype(np.float32)
        scene.geometry[g['geometry']]=tm

        total_triangles+=len(faces); total_unique_vertices+=len(used)
        grows.append({'geometry':g['geometry'],'material':mh,'vertices':len(used),'triangles':len(faces),
                      'placements':len(placements),'vertices0':k['vertices0'],'vertices1':k['vertices1'],'indices':k['indices'],
                      'index_offset':off,'index_count':cnt,'primitive_type':prim,'stride0':s0,'stride1':s1,
                      'source_vertex_indices':used.tolist(),'uv_transform':[float(x) for x in uvtr],
                      'raw_tangent_w_counts':{str(int(x)):int(np.sum(inp.raw_tangent[used,3]==x)) for x in np.unique(inp.raw_tangent[used,3])}})

        for n in placements:
            m=np.asarray(n['source_affine'],dtype=np.float64)
            export_m=d1_world_to_gltf_matrix(m)
            scene.graph.update(frame_to=n['node'],frame_from=scene.graph.base_frame,matrix=export_m,geometry=g['geometry'])
            nrows.append({'node':n['node'],'geometry':g['geometry'],'material':mh,'transform_index':n['transform_index'],
                          'source_affine':n['source_affine'],'uv_transform':n['uv_transform'],'tail_0x3c':n['tail_0x3c']})

    a.out.parent.mkdir(parents=True,exist_ok=True)
    scene.export(a.out,file_type='glb')
    chk=trimesh.load(a.out,force='scene',process=False)
    if len(chk.graph.nodes_geometry)!=64: raise SystemExit(f'GLB reload node mismatch {len(chk.graph.nodes_geometry)}')
    if len(chk.geometry)!=12: raise SystemExit(f'GLB reload geometry mismatch {len(chk.geometry)}')

    rep={'schema_version':1,'status':'D1_TOWER_809DCD66_RETAIL_COMPACT_SCENE_EXPORTED',
         'source_world':str(a.world),'source_static_map_data':world.get('static_map_data'),'target_vs':'80CA0DDA','target_ps':'809DCD66',
         'material_count':len(cell_mats),'materials':cell_mats,'geometry_count':len(grows),'placement_count':len(nrows),
         'triangle_count_per_geometry_sum':total_triangles,'unique_vertex_count_per_geometry_sum':total_unique_vertices,
         'geometry':grows,'nodes':nrows,'bounds':chk.bounds.tolist() if chk.bounds is not None else None,
         'output_glb':str(a.out),'output_bytes':a.out.stat().st_size,'output_sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),
         'policy':'Sidecar selection/placement remains canonical; current retail source buffers are replayed exactly. _D1_TANGENT is forensic source xyzw and is not promoted to standard glTF TANGENT.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in ('status','material_count','geometry_count','placement_count','triangle_count_per_geometry_sum','unique_vertex_count_per_geometry_sum','bounds','output_bytes','output_sha256')},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
