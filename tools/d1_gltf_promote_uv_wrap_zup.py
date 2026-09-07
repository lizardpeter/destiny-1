#!/usr/bin/env python3
"""Make one native-D1 articulated GLB portable for Blender/glTF without touching skin math.

The D1 model/skin/animation closure deliberately keeps all articulated data in native
Tiger model space, which is Z-up.  glTF is Y-up.  World-scene exporters already apply
the source-closed adapter

    gltf = D1_ZUP_TO_GLTF_YUP @ native

at a placement/root boundary.  A standalone actor GLB must do the same thing exactly
once.  This tool therefore wraps every existing active-scene root beneath one new root
node carrying the exact -90 degree X rotation.  Mesh positions, joint local TRS,
inverse bind matrices and animation outputs remain byte-for-byte unchanged.

The Crota Blender visual-union exporter also preserves exact retail UV0 in custom
attribute ``_D1_UV0`` because Trimesh drops TEXCOORD_0 when the initial material has no
portable image.  This adapter promotes that same accessor index to TEXCOORD_0 without
copying or rewriting any vertex bytes.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path

from d1_gltf_layer_merge import read_glb, write_glb


def hfile(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('input_glb', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--expect-meshes', type=int)
    ap.add_argument('--expect-skins', type=int)
    ap.add_argument('--expect-animations', type=int)
    ap.add_argument('--expect-joints', type=int)
    ap.add_argument('--root-name', default='D1_ZUP_TO_GLTF_YUP')
    a = ap.parse_args()

    src, srcbin = read_glb(a.input_glb)
    doc = copy.deepcopy(src)
    if str((doc.get('asset') or {}).get('version')) != '2.0':
        raise SystemExit('input is not glTF 2.0')
    meshes = doc.get('meshes') or []
    skins = doc.get('skins') or []
    animations = doc.get('animations') or []
    if a.expect_meshes is not None and len(meshes) != a.expect_meshes:
        raise SystemExit(f'mesh count {len(meshes)} != {a.expect_meshes}')
    if a.expect_skins is not None and len(skins) != a.expect_skins:
        raise SystemExit(f'skin count {len(skins)} != {a.expect_skins}')
    if a.expect_animations is not None and len(animations) != a.expect_animations:
        raise SystemExit(f'animation count {len(animations)} != {a.expect_animations}')
    if a.expect_joints is not None:
        if len(skins) != 1 or len(skins[0].get('joints') or []) != a.expect_joints:
            raise SystemExit(f'joint count is not exact singleton {a.expect_joints}')

    # Promote the exact source UV accessor; no buffer or accessor changes occur.
    uv_rows = []
    for mi, mesh in enumerate(meshes):
        prims = mesh.get('primitives') or []
        if len(prims) != 1:
            raise SystemExit(f'mesh {mi}: expected one exact range primitive, got {len(prims)}')
        attrs = prims[0].setdefault('attributes', {})
        if 'TEXCOORD_0' in attrs:
            raise SystemExit(f'mesh {mi}: TEXCOORD_0 already present; refusing double UV conversion')
        if '_D1_UV0' not in attrs:
            raise SystemExit(f'mesh {mi}: exact _D1_UV0 accessor missing')
        acc = int(attrs['_D1_UV0'])
        if acc < 0 or acc >= len(doc.get('accessors') or []):
            raise SystemExit(f'mesh {mi}: _D1_UV0 accessor {acc} out of range')
        ar = doc['accessors'][acc]
        if ar.get('type') != 'VEC2' or int(ar.get('componentType', -1)) != 5126:
            raise SystemExit(f'mesh {mi}: UV accessor is not float32 VEC2: {ar}')
        pos_acc = int(attrs.get('POSITION', -1))
        if pos_acc < 0 or int(doc['accessors'][pos_acc].get('count', -1)) != int(ar.get('count', -2)):
            raise SystemExit(f'mesh {mi}: UV/POSITION vertex count drift')
        attrs['TEXCOORD_0'] = acc
        del attrs['_D1_UV0']
        uv_rows.append({'mesh_index': mi, 'accessor': acc, 'count': int(ar['count'])})

    scene_index = int(doc.get('scene', 0))
    scenes = doc.get('scenes') or []
    if scene_index < 0 or scene_index >= len(scenes):
        raise SystemExit(f'active scene index {scene_index} invalid')
    old_roots = [int(x) for x in (scenes[scene_index].get('nodes') or [])]
    if not old_roots:
        raise SystemExit('active scene has no roots')
    node_count_before = len(doc.get('nodes') or [])
    if any(x < 0 or x >= node_count_before for x in old_roots):
        raise SystemExit('active scene root index out of range')
    if any(str((doc['nodes'][x] or {}).get('name') or '') == a.root_name for x in old_roots):
        raise SystemExit('portable D1 root already present')

    s = math.sqrt(0.5)
    portable_root = {
        'name': a.root_name,
        'rotation': [-s, 0.0, 0.0, s],
        'children': old_roots,
        'extras': {
            'd1CoordinateAdapter': 'D1_ZUP_TO_GLTF_YUP',
            'd1NativeToGltfMatrix3x3': [[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, -1.0, 0.0]],
            'd1Policy': 'Single root conversion only; mesh, skin bind data and animation tracks remain native D1 underneath.'
        },
    }
    root_index = node_count_before
    doc.setdefault('nodes', []).append(portable_root)
    scenes[scene_index]['nodes'] = [root_index]
    doc.setdefault('asset', {}).setdefault('extras', {})['d1StandalonePortableBasis'] = {
        'source': 'native D1/Tiger Z-up',
        'target': 'glTF Y-up',
        'adapter': 'D1_ZUP_TO_GLTF_YUP',
        'rootNode': root_index,
        'rootName': a.root_name,
    }

    # Everything except primitive attribute aliases, the one appended root, active
    # scene roots and asset metadata must remain structurally identical.
    if len(doc.get('accessors') or []) != len(src.get('accessors') or []):
        raise SystemExit('accessor count changed')
    if len(doc.get('bufferViews') or []) != len(src.get('bufferViews') or []):
        raise SystemExit('bufferView count changed')
    if len(doc.get('skins') or []) != len(src.get('skins') or []):
        raise SystemExit('skin count changed')
    if len(doc.get('animations') or []) != len(src.get('animations') or []):
        raise SystemExit('animation count changed')

    a.out.parent.mkdir(parents=True, exist_ok=True)
    write_glb(a.out, doc, srcbin)
    chk, chkbin = read_glb(a.out)
    if chkbin != srcbin:
        raise SystemExit('binary chunk changed during UV/root adapter')
    if len(chk.get('nodes') or []) != node_count_before + 1:
        raise SystemExit('portable root node count drift after save')
    if (chk.get('scenes') or [])[scene_index].get('nodes') != [root_index]:
        raise SystemExit('portable active-scene root drift after save')
    for mi, mesh in enumerate(chk.get('meshes') or []):
        attrs = mesh['primitives'][0]['attributes']
        if 'TEXCOORD_0' not in attrs or '_D1_UV0' in attrs:
            raise SystemExit(f'mesh {mi}: saved UV promotion drift')

    report = {
        'schema': 'd1_gltf_promote_uv_wrap_zup/v1',
        'status': 'D1_GLTF_UV_AND_ZUP_TO_YUP_ROOT_COMPLETE',
        'input_glb': str(a.input_glb),
        'input_sha256': hfile(a.input_glb),
        'output_glb': str(a.out),
        'output_sha256': hfile(a.out),
        'output_bytes': a.out.stat().st_size,
        'mesh_count': len(meshes),
        'skin_count': len(skins),
        'joint_count': len(skins[0].get('joints') or []) if len(skins) == 1 else None,
        'animation_count': len(animations),
        'uv_promoted_mesh_count': len(uv_rows),
        'uv_rows': uv_rows,
        'active_scene_index': scene_index,
        'old_scene_roots': old_roots,
        'portable_root_index': root_index,
        'portable_root_rotation_xyzw': portable_root['rotation'],
        'binary_identical': True,
        'accessor_count_unchanged': True,
        'buffer_view_count_unchanged': True,
        'policy': (
            'Exact decoded source UV accessors are only aliased into standard TEXCOORD_0. '
            'The native D1 articulated domain remains unchanged and is wrapped once by the same '
            'D1_ZUP_TO_GLTF_YUP root adapter used by the source-closed world scene pipeline.'
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('status','mesh_count','joint_count','animation_count','uv_promoted_mesh_count','portable_root_index','output_bytes','output_sha256')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
