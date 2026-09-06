#!/usr/bin/env python3
"""Disable non-stage0 mesh nodes in an existing D1 Guardian GLB.

The fully rigged Spektar proof GLB intentionally preserved every deduplicated
serialized range.  Bungie's archived D1 gear renderer instead draws stage 0 only
and highest LOD.  Given the exact `d1_guardian_stage0_material_resolve/v1`
report, this tool keeps only those byte-proven ranges while preserving the
existing skin, joints, inverse bind matrices, and animation untouched.

To minimize risk, this pass does not rewrite binary buffers/accessors.  It clears
the `mesh` reference on excluded geometry nodes, making them non-rendering while
leaving all unrelated glTF indices stable.  A later compaction pass can remove
unused mesh/buffer data after visual validation.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from pygltflib import GLTF2

NAME_RE=re.compile(r'(?P<tag>[0-9A-Fa-f]{8})_mesh(?P<mesh>\d+)_range(?P<off>\d+)_(?P<count>\d+)')


def key_from_name(name:str|None):
    if not name: return None
    m=NAME_RE.search(name)
    if not m: return None
    return (m.group('tag').upper(),int(m.group('mesh')),int(m.group('off')),int(m.group('count')))


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('input_glb',type=Path)
    ap.add_argument('--stage0-report',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    ap.add_argument('--json',type=Path)
    a=ap.parse_args()

    d=json.loads(a.stage0_report.read_text())
    if d.get('schema')!='d1_guardian_stage0_material_resolve/v1':
        raise ValueError('unexpected stage0 report schema')
    if d.get('errors') or d.get('multi_part_selected_range_count') or d.get('multi_material_selected_range_count'):
        raise ValueError('stage0 report is not uniquely resolved')
    keep={(r['model_tag'].upper(),int(r['mesh_index']),int(r['index_offset']),int(r['index_count'])) for r in d['ranges']}
    if len(keep)!=d['selected_range_count']:
        raise ValueError('duplicate stage0 range keys')

    g=GLTF2().load(str(a.input_glb))
    matched={}; kept=[]; removed=[]; unrecognized_mesh_nodes=[]
    for ni,n in enumerate(g.nodes or []):
        if n.mesh is None: continue
        names=[]
        if n.name: names.append(n.name)
        if 0 <= n.mesh < len(g.meshes or []) and g.meshes[n.mesh].name:
            names.append(g.meshes[n.mesh].name)
        keys=[key_from_name(x) for x in names]
        keys=[x for x in keys if x is not None]
        keys=list(dict.fromkeys(keys))
        if not keys:
            unrecognized_mesh_nodes.append({'node_index':ni,'node_name':n.name,'mesh_index':n.mesh,'mesh_name':g.meshes[n.mesh].name if 0<=n.mesh<len(g.meshes or []) else None})
            continue
        if len(keys)!=1:
            raise ValueError(f'node {ni}: conflicting geometry keys {keys}')
        k=keys[0]
        if k in matched:
            raise ValueError(f'duplicate GLB node for geometry key {k}: {matched[k]} and {ni}')
        matched[k]=ni
        if k in keep:
            kept.append({'node_index':ni,'mesh_index':n.mesh,'key':list(k),'node_name':n.name})
        else:
            old=n.mesh
            n.mesh=None
            removed.append({'node_index':ni,'mesh_index':old,'key':list(k),'node_name':n.name})

    missing=sorted(keep-set(matched))
    if missing:
        raise ValueError(f'{len(missing)} stage0 ranges absent from GLB: {missing[:8]}')
    if len(kept)!=len(keep):
        raise ValueError((len(kept),len(keep)))
    # Any mesh-bearing node that is not a recognized D1 range is dangerous: it
    # could be an accidental geometry attachment. Bone nodes are mesh-less.
    if unrecognized_mesh_nodes:
        raise ValueError(f'unrecognized mesh-bearing nodes: {unrecognized_mesh_nodes[:8]}')

    a.output.parent.mkdir(parents=True,exist_ok=True)
    g.save_binary(str(a.output))
    out=GLTF2().load(str(a.output))
    active_nodes=[(i,n) for i,n in enumerate(out.nodes or []) if n.mesh is not None]
    if len(active_nodes)!=len(keep):
        raise ValueError(f'roundtrip active mesh nodes {len(active_nodes)} != {len(keep)}')

    rep={
        'schema':'d1_gltf_stage0_prune/v1','input_glb':str(a.input_glb),'output_glb':str(a.output),
        'stage0_range_count':len(keep),'recognized_input_range_node_count':len(matched),
        'kept_mesh_node_count':len(kept),'disabled_mesh_node_count':len(removed),
        'skin_count':len(out.skins or []),'animation_count':len(out.animations or []),
        'node_count':len(out.nodes or []),'mesh_object_count_preserved':len(out.meshes or []),
        'active_mesh_node_count':len(active_nodes),'kept':kept,'disabled':removed,
        'policy':'Excluded serialized ranges have only their node.mesh reference cleared. Skin, animation, node indices and binary accessor layout remain untouched.',
    }
    jp=a.json or a.output.with_suffix('.stage0.json')
    jp.write_text(json.dumps(rep,indent=2)+'\n')
    print('STAGE0 GLB',len(kept),'active,',len(removed),'disabled, skins',rep['skin_count'],'animations',rep['animation_count'])
    return 0


if __name__=='__main__':
    raise SystemExit(main())
