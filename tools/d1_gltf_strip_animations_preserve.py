#!/usr/bin/env python3
"""Create a bind-pose inspection GLB by removing only glTF Animation objects.

This is intentionally a viewer/diagnostic adapter.  It does not rewrite mesh bytes,
accessors, nodes, skins, inverse binds, materials, textures, images, scene transforms,
or any D1 provenance metadata.  The binary chunk is preserved byte-for-byte, so the
unused animation accessors remain as inert evidence data.  Removing the JSON animation
objects prevents Blender/importers from choosing an arbitrary action when there is no
source-proven default/startup animation semantic.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

from d1_gltf_layer_merge import read_glb, write_glb


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('input_glb', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--expect-animations', type=int)
    a = ap.parse_args()

    src, binary = read_glb(a.input_glb)
    animations = src.get('animations') or []
    if a.expect_animations is not None and len(animations) != a.expect_animations:
        raise SystemExit(f'animation count {len(animations)} != {a.expect_animations}')
    if not animations:
        raise SystemExit('input GLB already has no animations')

    doc = copy.deepcopy(src)
    removed = []
    for i, anim in enumerate(animations):
        removed.append({
            'index': i,
            'name': anim.get('name'),
            'sampler_count': len(anim.get('samplers') or []),
            'channel_count': len(anim.get('channels') or []),
            'extras': anim.get('extras'),
        })
    doc['animations'] = []
    doc.setdefault('asset', {}).setdefault('extras', {})['d1BindPoseInspectionView'] = {
        'sourceAnimationCount': len(animations),
        'animationObjectsRemoved': True,
        'binaryAnimationEvidenceRetained': True,
        'reason': 'No source-proven default/startup action; prevent viewer auto-selection during bind-pose inspection.',
    }

    # Guard every structural domain that must remain unchanged.
    for key in ('accessors','bufferViews','buffers','images','materials','meshes','nodes','samplers','scenes','skins','textures'):
        if doc.get(key, []) != src.get(key, []):
            raise SystemExit(f'{key} changed before save')

    a.out.parent.mkdir(parents=True, exist_ok=True)
    write_glb(a.out, doc, binary)
    chk, chkbin = read_glb(a.out)
    if chkbin != binary:
        raise SystemExit('binary chunk changed')
    if chk.get('animations'):
        raise SystemExit('saved bind-pose GLB still contains animations')
    for key in ('accessors','bufferViews','buffers','images','materials','meshes','nodes','samplers','scenes','skins','textures'):
        if chk.get(key, []) != src.get(key, []):
            raise SystemExit(f'{key} changed after save')

    report = {
        'schema': 'd1_gltf_strip_animations_preserve/v1',
        'status': 'D1_GLTF_BIND_POSE_INSPECTION_VIEW_COMPLETE',
        'input': str(a.input_glb),
        'input_sha256': sha256(a.input_glb),
        'output': str(a.out),
        'output_sha256': sha256(a.out),
        'output_bytes': a.out.stat().st_size,
        'removed_animation_count': len(removed),
        'removed_animations': removed,
        'binary_identical': True,
        'skin_count': len(chk.get('skins') or []),
        'mesh_count': len(chk.get('meshes') or []),
        'material_count': len(chk.get('materials') or []),
        'image_count': len(chk.get('images') or []),
        'policy': 'Only JSON Animation objects are removed. All source mesh/skin/material/texture data and the complete binary payload are retained exactly.',
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('status','removed_animation_count','mesh_count','skin_count','material_count','image_count','output_bytes','output_sha256')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
