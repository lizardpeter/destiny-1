#!/usr/bin/env python3
"""Convert a D1 source-space GLB to a standards-compliant glTF Y-up basis.

Destiny/Tiger world placement is Z-up. glTF 2.0 viewers conventionally interpret
+Y as up; Blender then converts glTF Y-up to Blender Z-up on import. A raw D1
Z-up scene written directly as glTF therefore appears laid onto the wrong axis in
Blender. This tool left-multiplies every source-space node transform by the single
D1 Z-up -> glTF Y-up basis matrix while preserving all local geometry bytes.

It is an adapter only: source-space matrices remain the canonical evidence.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import trimesh

from d1_world_static_common import d1_world_to_gltf_matrix


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--json',type=Path)
    a=ap.parse_args()

    src=trimesh.load(a.input,force='scene',process=False)
    out=trimesh.Scene()
    # Copy geometry once. Geometry names are preserved where possible.
    for name,g in src.geometry.items():
        out.geometry[name]=g.copy()
    for node in src.graph.nodes_geometry:
        tf,gname=src.graph.get(node)
        out.graph.update(frame_to=str(node),frame_from=out.graph.base_frame,
                         matrix=d1_world_to_gltf_matrix(tf),geometry=gname)

    a.out.parent.mkdir(parents=True,exist_ok=True)
    out.export(a.out,file_type='glb')
    check=trimesh.load(a.out,force='scene',process=False)
    if len(check.graph.nodes_geometry)!=len(src.graph.nodes_geometry):
        raise SystemExit('node count changed during basis conversion')
    if len(check.geometry)!=len(src.geometry):
        raise SystemExit('geometry count changed during basis conversion')

    rep={
      'status':'D1_SOURCE_Z_UP_TO_GLTF_Y_UP_ADAPTER',
      'input':str(a.input),'output':str(a.out),
      'nodes':len(check.graph.nodes_geometry),'geometry':len(check.geometry),
      'source_bounds':src.bounds.tolist() if src.bounds is not None else None,
      'gltf_bounds':check.bounds.tolist() if check.bounds is not None else None,
      'output_bytes':a.out.stat().st_size,
      'output_sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),
      'basis_matrix':[[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]],
      'policy':'local geometry unchanged; basis conversion applied only to node world transforms'
    }
    jp=a.json or a.out.with_suffix('.json')
    jp.parent.mkdir(parents=True,exist_ok=True);jp.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps(rep,indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
