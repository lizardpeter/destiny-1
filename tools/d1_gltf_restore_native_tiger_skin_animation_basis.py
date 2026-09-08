#!/usr/bin/env python3
"""Restore a skinned animated GLB from parser space to native D1/Tiger model space.

This is the generic production form of the source-proven Tower E/F/G r10 basis fix.
The pinned tiger-animation-parser maps raw Tiger [x,y,z] to [y,z,x] in skeleton and
retargeted animation data, while this repository's D1 model geometry stays in native
D1 model space. A standalone actor GLB built from parser-space skeletons/actions must
therefore basis-convert both domains together:

  * skin joint local TRS;
  * inverseBindMatrices;
  * all joint-targeted animation translation/rotation/scale output accessors.

Mesh data, exact JOINTS/WEIGHTS, animation times, channel targets, interpolation,
materials, textures, action hashes and selector evidence remain untouched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from d1_gltf_layer_merge import read_glb, write_glb
from d1_gltf_skin_bind_identity_probe import accessor, node_local
from d1_gltf_restore_native_tiger_skin_basis import (
    parser_to_native_matrix, decompose, set_float_accessor as set_ibm_accessor,
)
from d1_gltf_restore_native_tiger_animation_basis import (
    convert_values, set_float_accessor as set_animation_accessor,
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('input_glb', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    doc, binary = read_glb(a.input_glb)
    skins = doc.get('skins', [])
    animations = doc.get('animations', [])
    nodes = doc.get('nodes', [])
    if not skins:
        raise SystemExit('input has no skins')
    if not animations:
        raise SystemExit('input has no animations')

    blob = bytearray(binary)
    joint_nodes = set()
    ibm_accessors = set()
    skin_rows = []
    for si, skin in enumerate(skins):
        joints = [int(x) for x in skin.get('joints', [])]
        ibm = skin.get('inverseBindMatrices')
        if not joints or ibm is None:
            raise ValueError(f'skin {si}: missing joints or inverseBindMatrices')
        joint_nodes.update(joints)
        ibm_accessors.add(int(ibm))
        root = skin.get('skeleton')
        rex = nodes[int(root)].get('extras', {}) if root is not None else {}
        skin_rows.append({
            'skin_index': si, 'joint_count': len(joints), 'inverse_bind_accessor': int(ibm),
            'skeleton_root': root, 'model': str(rex.get('d1Model', '')).upper() or None,
            'skeleton': str(rex.get('d1Skeleton', '')).upper() or None,
            'runtime_rig': str(rex.get('d1RuntimeRig', '')).upper() or None,
        })

    for ji in sorted(joint_nodes):
        if not 0 <= ji < len(nodes):
            raise ValueError(f'joint node {ji} outside node array')
        native = parser_to_native_matrix(node_local(nodes[ji]))
        t, q, s = decompose(native)
        node = nodes[ji]
        node.pop('matrix', None)
        node['translation'] = [float(x) for x in t]
        node['rotation'] = [float(x) for x in q]
        node['scale'] = [float(x) for x in s]

    for ai in sorted(ibm_accessors):
        mats = accessor(doc, binary, ai).astype(np.float64)
        converted = np.stack([parser_to_native_matrix(m) for m in mats], axis=0)
        set_ibm_accessor(doc, blob, ai, converted)

    converted_outputs: dict[int, str] = {}
    channel_rows = []
    nonjoint = []
    animation_rows = []
    for ani, anim in enumerate(animations):
        joint_channel_count = 0
        for ci, ch in enumerate(anim.get('channels', [])):
            target = ch.get('target') or {}
            node = int(target['node'])
            path = str(target['path'])
            sampler = anim['samplers'][int(ch['sampler'])]
            output_ai = int(sampler['output'])
            if node not in joint_nodes:
                nonjoint.append({'animation_index': ani, 'channel_index': ci,
                                 'target_node': node, 'path': path, 'output_accessor': output_ai})
                continue
            previous = converted_outputs.get(output_ai)
            if previous is not None and previous != path:
                raise ValueError(f'output accessor {output_ai} shared by incompatible paths {previous}/{path}')
            if previous is None:
                # accessor() consumes any Python buffer-protocol object. Passing the
                # live bytearray avoids materializing a complete ~100 MB bytes copy
                # for each of tens of thousands of animation output accessors.
                vals = accessor(doc, blob, output_ai).astype(np.float64)
                set_animation_accessor(doc, blob, output_ai, convert_values(path, vals))
                converted_outputs[output_ai] = path
            joint_channel_count += 1
            channel_rows.append({'animation_index': ani, 'animation_name': anim.get('name'),
                                 'channel_index': ci, 'target_node': node, 'path': path,
                                 'output_accessor': output_ai})
        animation_rows.append({'animation_index': ani, 'name': anim.get('name'),
                               'channel_count': len(anim.get('channels', [])),
                               'joint_targeted_channel_count': joint_channel_count})

    if nonjoint:
        raise ValueError(f'found {len(nonjoint)} non-joint animation channels; refusing partial basis conversion')
    if not converted_outputs:
        raise ValueError('no joint-targeted animation outputs found')

    asset = doc.setdefault('asset', {'version': '2.0'})
    ex = asset.setdefault('extras', {})
    ex['d1NativeTigerSkinAnimationBasis'] = {
        'sourceParserBasis': '[x,y,z] -> [y,z,x]',
        'restoredBasis': 'native D1/Tiger [x,y,z]',
        'skinCount': len(skins),
        'jointNodeCount': len(joint_nodes),
        'inverseBindAccessorCount': len(ibm_accessors),
        'animationCount': len(animations),
        'jointTargetedChannelCount': len(channel_rows),
        'convertedAnimationOutputAccessorCount': len(converted_outputs),
        'meshVertexDataChanged': False,
        'jointIndicesChanged': False,
        'weightsChanged': False,
        'animationTimesChanged': False,
        'channelTargetsChanged': False,
        'materialsChanged': False,
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    write_glb(a.out, doc, bytes(blob))
    out_doc, out_binary = read_glb(a.out)
    if len(out_binary) != len(binary):
        raise ValueError(f'BIN byte length changed {len(binary)} -> {len(out_binary)}')
    for key in ('meshes', 'skins', 'animations', 'materials'):
        if len(out_doc.get(key, [])) != len(doc.get(key, [])):
            raise ValueError(f'{key} count changed')

    report = {
        'schema_version': 2,
        'status': 'D1_GLTF_NATIVE_TIGER_SKIN_ANIMATION_BASIS_RESTORED',
        'input': str(a.input_glb), 'input_sha256': sha256_file(a.input_glb),
        'output': str(a.out), 'output_sha256': sha256_file(a.out),
        'output_bytes': a.out.stat().st_size,
        'skin_count': len(skins), 'joint_node_count': len(joint_nodes),
        'inverse_bind_accessor_count': len(ibm_accessors),
        'animation_count': len(animations),
        'joint_targeted_channel_count': len(channel_rows),
        'converted_animation_output_accessor_count': len(converted_outputs),
        'binary_byte_length_unchanged': len(out_binary) == len(binary),
        'buffer_copy_policy': 'live bytearray buffer passed to accessor; no per-accessor full-buffer copy',
        'skins': skin_rows, 'animations': animation_rows,
        'parser_basis_unapplied': True,
        'restored_basis': 'native D1/Tiger [x,y,z]',
        'policy': (
            'Exact inverse of the pinned parser [x,y,z]->[y,z,x] basis is applied only '
            'to skin bind transforms and joint-targeted animation outputs. Source mesh, '
            'JOINTS/WEIGHTS, action selection, timing, interpolation and materials are unchanged. '
            'Animation output reads use the live buffer directly; this changes performance only.'
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in (
        'status','output_bytes','output_sha256','skin_count','joint_node_count',
        'animation_count','joint_targeted_channel_count',
        'converted_animation_output_accessor_count','binary_byte_length_unchanged',
        'buffer_copy_policy'
    )}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
