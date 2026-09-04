#!/usr/bin/env python3
"""Attach the exact D1 ROI Gjallarhorn pattern-39 rig/animations to arrangement-1229 geometry.

Binary-grounded inputs already established elsewhere in this repository:
  * Year-3 Gjallarhorn art arrangement 1229 -> six selected visual models / eight meshes.
  * weapon pattern 39 -> skeleton EntityResource 80AA3C97 and runtime rig 80AA2D6D.
  * direct animation control 80AA2DCD -> clips 80AA2E4A and 80AA2E4B.
  * for every selected mesh, primary vertex stream int16 lane 3 contains only 0..6,
    exactly the seven pattern-39 joint indices; old_weights == FFFFFFFF.

This tool does not infer skin weights.  It copies the native rigid joint index for
EVERY vertex and emits WEIGHTS_0=[1,0,0,0].  The exact inverse-bind matrices,
skeleton hierarchy and animation tracks are copied from the independently decoded
pattern-39 rig proof GLB.

The two input GLBs are merged at the GLB JSON/BIN level so embedded textures and
animation data survive byte-for-byte in their respective binary spans.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import struct
from collections import Counter
from pathlib import Path

import numpy as np

from d1_entry_extract import EntryReader
from d1_entity_model_probe import parse_model
from d1_investment_arrangement_probe import filehash_pkg_index

JSON_CHUNK = 0x4E4F534A
BIN_CHUNK = 0x004E4942
ARRAY_BUFFER = 34962
UNSIGNED_BYTE = 5121
FLOAT = 5126

EXPECTED_DISTRIBUTIONS = {
    ('80A743A6', 0): {0: 340, 6: 223},
    ('80A73BAB', 0): {0: 2040, 2: 144},
    ('80A72202', 0): {5: 86},
    ('80A7317B', 0): {1: 1423},
    ('80A73256', 0): {1: 188},
    ('80A73256', 1): {0: 3064, 1: 2168},
    ('80A73D13', 0): {0: 8},
    ('80A73D13', 1): {1: 117},
}
EXPECTED_BONE_NAMES = [
    'C410084A', 'AD2A05CD', '3308E6CC', '752D6334',
    'FC1090F4', '0AB6C582', 'B79A6009',
]
EXPECTED_CLIPS = ['80AA2E4A', '80AA2E4B']


def parse_glb(path: Path) -> tuple[dict, bytes]:
    b = path.read_bytes()
    if b[:4] != b'glTF' or struct.unpack_from('<I', b, 4)[0] != 2:
        raise ValueError(f'{path}: not a glTF 2 GLB')
    if struct.unpack_from('<I', b, 8)[0] != len(b):
        raise ValueError(f'{path}: GLB length mismatch')
    off = 12
    js = None
    binary = None
    while off < len(b):
        n, typ = struct.unpack_from('<II', b, off)
        off += 8
        payload = b[off:off+n]
        off += n
        if typ == JSON_CHUNK:
            js = json.loads(payload.decode('utf-8').rstrip('\x00 '))
        elif typ == BIN_CHUNK:
            binary = payload
    if js is None or binary is None:
        raise ValueError(f'{path}: expected JSON and BIN chunks')
    return js, binary


def write_glb(path: Path, g: dict, binary: bytes) -> None:
    jb = json.dumps(g, separators=(',', ':')).encode('utf-8')
    jb += b' ' * ((4 - len(jb) % 4) % 4)
    bb = bytes(binary)
    bb += b'\x00' * ((4 - len(bb) % 4) % 4)
    total = 12 + 8 + len(jb) + 8 + len(bb)
    out = bytearray(b'glTF')
    out += struct.pack('<II', 2, total)
    out += struct.pack('<II', len(jb), JSON_CHUNK) + jb
    out += struct.pack('<II', len(bb), BIN_CHUNK) + bb
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(out)


def patch_number(path: Path) -> int:
    m = re.search(r'_(\d+)\.pkg$', path.name)
    return int(m.group(1)) if m else -1


def reader_family(seed: Path, runtime: Path):
    m = re.match(r'^(.*)_\d+\.pkg$', seed.name)
    paths = [seed] if not m else sorted(seed.parent.glob(m.group(1) + '_*.pkg'), key=patch_number, reverse=True)
    out = []
    for p in paths:
        try:
            r = EntryReader(p, runtime)
            out.append((r, {e['tag_hash'].upper(): e for e in r.entries}))
        except Exception:
            pass
    if not out:
        raise RuntimeError(f'no readable snapshots for {seed}')
    return out


def linked_vertex_payload(reader_sets, tag: str):
    pkg, _ = filehash_pkg_index(int(tag, 16))
    errors = []
    for r, table in reader_sets.get(pkg, []):
        e = table.get(tag.upper())
        if not e:
            continue
        linked = table.get(e['reference'].upper())
        if not linked:
            continue
        try:
            h = r.entry(e['index'])
            p = r.entry(linked['index'])
            if len(h) < 6:
                raise RuntimeError('short vertex header')
            stride = struct.unpack_from('<h', h, 4)[0]
            if stride < 8 or stride > 128 or stride % 2:
                raise RuntimeError(f'invalid stride {stride}')
            if len(p) % stride:
                raise RuntimeError(f'payload {len(p)} not divisible by {stride}')
            return h, p, {'snapshot': r.pkg.name, 'header': tag.upper(), 'payload': e['reference'].upper(), 'stride': stride}
        except Exception as ex:
            errors.append({'snapshot': r.pkg.name, 'error': repr(ex)})
    raise RuntimeError(f'could not recover vertex stream {tag}: {errors}')


def load_models(model_dir: Path) -> dict[str, dict]:
    out = {}
    for p in sorted(model_dir.glob('*.bin')):
        tag = p.stem.upper()
        if (tag, 0) in EXPECTED_DISTRIBUTIONS or any(k[0] == tag for k in EXPECTED_DISTRIBUTIONS):
            out[tag] = parse_model(p.read_bytes(), 'PS4')
    expected = {k[0] for k in EXPECTED_DISTRIBUTIONS}
    if set(out) != expected:
        raise RuntimeError(f'model headers differ: have {sorted(out)}, expected {sorted(expected)}')
    return out


def align4(buf: bytearray) -> int:
    while len(buf) % 4:
        buf.append(0)
    return len(buf)


def append_accessor(g: dict, blob: bytearray, array: np.ndarray, component_type: int, atype: str, target=ARRAY_BUFFER) -> int:
    align4(blob)
    off = len(blob)
    payload = np.ascontiguousarray(array).tobytes()
    blob.extend(payload)
    bv = len(g.setdefault('bufferViews', []))
    g['bufferViews'].append({'buffer': 0, 'byteOffset': off, 'byteLength': len(payload), 'target': target})
    ai = len(g.setdefault('accessors', []))
    g['accessors'].append({
        'bufferView': bv, 'byteOffset': 0, 'componentType': component_type,
        'count': int(array.shape[0]), 'type': atype,
    })
    return ai


def accessor_count(g: dict, ai: int) -> int:
    return int(g['accessors'][ai]['count'])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('textured_glb', type=Path)
    ap.add_argument('rig_glb', type=Path)
    ap.add_argument('--pkg-011c', type=Path, required=True)
    ap.add_argument('--pkg-0139', type=Path, required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--model-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    geo, geo_bin = parse_glb(a.textured_glb)
    rig, rig_bin = parse_glb(a.rig_glb)

    if [x.get('name') for x in rig.get('nodes', [])[:7]] != EXPECTED_BONE_NAMES:
        raise RuntimeError('rig bone order does not match the proven seven-bone Gjallarhorn skeleton')
    if [x.get('name') for x in rig.get('animations', [])] != EXPECTED_CLIPS:
        raise RuntimeError('rig clip set differs from exact directly-linked Gjallarhorn clips')
    if len(rig.get('skins', [])) != 1 or len(rig['skins'][0].get('joints', [])) != 7:
        raise RuntimeError('expected one seven-joint source skin')
    if len(geo.get('meshes', [])) != 8:
        raise RuntimeError('expected eight Gjallarhorn visual meshes')
    if len(geo.get('buffers', [])) != 1 or len(rig.get('buffers', [])) != 1:
        raise RuntimeError('merger currently expects one embedded BIN buffer per source GLB')
    if any(int(v.get('buffer', 0)) != 0 for v in geo.get('bufferViews', [])):
        raise RuntimeError('textured GLB has unexpected nonzero bufferView buffer')
    if any(int(v.get('buffer', 0)) != 0 for v in rig.get('bufferViews', [])):
        raise RuntimeError('rig GLB has unexpected nonzero bufferView buffer')

    models = load_models(a.model_dir)
    readers = {
        0x011C: reader_family(a.pkg_011c, a.runtime),
        0x0139: reader_family(a.pkg_0139, a.runtime),
    }

    # Merge the two existing binary chunks first.  Existing geometry bufferViews
    # keep their offsets; rig bufferViews are shifted by rig_base.
    blob = bytearray(geo_bin)
    rig_base = align4(blob)
    blob.extend(rig_bin)
    bv_base = len(geo.get('bufferViews', []))
    acc_base = len(geo.get('accessors', []))
    node_base = len(geo.get('nodes', []))

    for bv in rig.get('bufferViews', []):
        x = copy.deepcopy(bv)
        x['buffer'] = 0
        x['byteOffset'] = rig_base + int(x.get('byteOffset', 0))
        geo.setdefault('bufferViews', []).append(x)
    for acc in rig.get('accessors', []):
        x = copy.deepcopy(acc)
        if x.get('bufferView') is not None:
            x['bufferView'] = bv_base + int(x['bufferView'])
        geo.setdefault('accessors', []).append(x)

    # Clone exact skeleton hierarchy under the existing presentation root.
    for n in rig.get('nodes', []):
        x = copy.deepcopy(n)
        if x.get('children') is not None:
            x['children'] = [node_base + int(c) for c in x['children']]
        geo.setdefault('nodes', []).append(x)
    if not geo.get('scenes') or geo.get('scene') is None:
        raise RuntimeError('textured GLB has no active scene')
    scene_roots = geo['scenes'][int(geo['scene'])].get('nodes', [])
    if scene_roots != [0]:
        raise RuntimeError(f'expected Gjallarhorn presentation root node 0, got {scene_roots}')
    root_children = geo['nodes'][0].setdefault('children', [])
    root_children.append(node_base + int(rig['skins'][0]['skeleton']))

    # Clone the source skin and exact inverse bind matrices.
    src_skin = copy.deepcopy(rig['skins'][0])
    skin = {
        **src_skin,
        'inverseBindMatrices': acc_base + int(src_skin['inverseBindMatrices']),
        'skeleton': node_base + int(src_skin['skeleton']),
        'joints': [node_base + int(j) for j in src_skin['joints']],
        'name': 'D1_Gjallarhorn_pattern39_exact_rigid_skin',
        'extras': {
            'd1SkeletonResource': '80AA3C97',
            'd1RuntimeRigResource': '80AA2D6D',
            'jointBindingSource': 'primary vertex stream int16 lane 3',
            'weightPolicy': 'rigid 1.0; s_entity_model old_weights == FFFFFFFF for all eight meshes',
        },
    }
    geo['skins'] = [skin]

    # Map each glTF mesh to its exact model+mesh record and attach native joint index arrays.
    mesh_nodes = {}
    for ni, node in enumerate(geo['nodes'][:node_base]):
        if node.get('mesh') is None:
            continue
        mi = int(node['mesh'])
        mex = geo['meshes'][mi].get('extras') or {}
        model = (mex.get('d1Model') or (node.get('extras') or {}).get('d1Model'))
        mesh_index = mex.get('d1MeshIndex')
        if model is None or mesh_index is None:
            raise RuntimeError(f'geometry mesh {mi} lacks d1Model/d1MeshIndex provenance')
        key = (str(model).upper(), int(mesh_index))
        if key in mesh_nodes:
            raise RuntimeError(f'duplicate mesh provenance {key}')
        mesh_nodes[key] = (mi, ni)
    if set(mesh_nodes) != set(EXPECTED_DISTRIBUTIONS):
        raise RuntimeError(f'mesh provenance differs: {sorted(mesh_nodes)}')

    joint_rows = []
    for key in sorted(EXPECTED_DISTRIBUTIONS):
        model_tag, mesh_index = key
        mesh_record = models[model_tag]['meshes'][mesh_index]
        if mesh_record['old_weights'].upper() != 'FFFFFFFF':
            raise RuntimeError(f'{key}: old_weights unexpectedly present: {mesh_record["old_weights"]}')
        _, payload, source = linked_vertex_payload(readers, mesh_record['vertices1'])
        stride = int(source['stride'])
        words = np.frombuffer(payload, dtype='<i2').reshape((-1, stride // 2))
        if words.shape[1] < 4:
            raise RuntimeError(f'{key}: primary stream has fewer than four int16 lanes')
        joint = words[:, 3].astype(np.int64)
        if np.any(joint < 0) or np.any(joint > 6):
            raise RuntimeError(f'{key}: joint lane outside 0..6: {sorted(set(joint.tolist()))}')
        dist = dict(sorted(Counter(int(x) for x in joint.tolist()).items()))
        if dist != EXPECTED_DISTRIBUTIONS[key]:
            raise RuntimeError(f'{key}: joint distribution {dist} != expected {EXPECTED_DISTRIBUTIONS[key]}')

        mesh_i, node_i = mesh_nodes[key]
        prims = geo['meshes'][mesh_i]['primitives']
        if not prims:
            raise RuntimeError(f'{key}: no primitives')
        pos_ai = int(prims[0]['attributes']['POSITION'])
        if accessor_count(geo, pos_ai) != len(joint):
            raise RuntimeError(f'{key}: source joint count {len(joint)} != POSITION count {accessor_count(geo, pos_ai)}')
        for p in prims:
            if int(p['attributes']['POSITION']) != pos_ai:
                raise RuntimeError(f'{key}: primitives do not share one vertex stream')

        joints4 = np.zeros((len(joint), 4), dtype=np.uint8)
        joints4[:, 0] = joint.astype(np.uint8)
        weights4 = np.zeros((len(joint), 4), dtype=np.float32)
        weights4[:, 0] = 1.0
        jai = append_accessor(geo, blob, joints4, UNSIGNED_BYTE, 'VEC4')
        wai = append_accessor(geo, blob, weights4, FLOAT, 'VEC4')
        for p in prims:
            p['attributes']['JOINTS_0'] = jai
            p['attributes']['WEIGHTS_0'] = wai
        geo['nodes'][node_i]['skin'] = 0
        geo['meshes'][mesh_i].setdefault('extras', {})['d1RigidJointDistribution'] = {str(k): v for k, v in dist.items()}
        geo['meshes'][mesh_i]['extras']['d1JointIndexVertexLane'] = 3
        joint_rows.append({
            'model_tag': model_tag, 'mesh_index': mesh_index, 'mesh': mesh_i, 'node': node_i,
            'vertex_count': len(joint), 'distribution': dist, 'source': source,
            'joints_accessor': jai, 'weights_accessor': wai,
        })

    # Clone exact animation samplers/channels, remapping accessors and target nodes.
    geo['animations'] = []
    for anim in rig.get('animations', []):
        x = copy.deepcopy(anim)
        for s in x.get('samplers', []):
            s['input'] = acc_base + int(s['input'])
            s['output'] = acc_base + int(s['output'])
        for c in x.get('channels', []):
            c['target']['node'] = node_base + int(c['target']['node'])
        geo['animations'].append(x)

    geo['buffers'] = [{'byteLength': len(blob)}]
    extras = geo.setdefault('extras', {})
    extras['d1GjallarhornExactPattern39Rig'] = {
        'inventoryItemHashYear3': 'D471D331',
        'artArrangementIndex': 1229,
        'weaponPatternIndex': 39,
        'patternEntity': '80A6A017',
        'skeletonResource': '80AA3C97',
        'runtimeRigResource': '80AA2D6D',
        'directAnimationControl': '80AA2DCD',
        'directClipOffsets': {'176': '80AA2E4A', '180': '80AA2E4B'},
        'jointCount': 7,
        'jointHashes': EXPECTED_BONE_NAMES,
        'binding': 'exact rigid per-vertex joint index from primary vertex int16 lane 3; WEIGHTS_0=1.0',
        'oldWeightsAbsent': True,
        'geometryChanged': False,
    }
    geo.setdefault('asset', {})['generator'] = 'destiny-1 exact Gjallarhorn 1229 texture + pattern39 rigid skin + direct animations'

    write_glb(a.out, geo, blob)
    check, check_bin = parse_glb(a.out)
    if len(check.get('meshes', [])) != 8 or len(check.get('skins', [])) != 1 or len(check.get('animations', [])) != 2:
        raise RuntimeError('combined GLB structural validation failed')
    if [x.get('name') for x in check['animations']] != EXPECTED_CLIPS:
        raise RuntimeError('combined animation names changed')
    skinned_nodes = [n for n in check['nodes'] if n.get('mesh') is not None and n.get('skin') == 0]
    if len(skinned_nodes) != 8:
        raise RuntimeError(f'expected 8 skinned mesh nodes, got {len(skinned_nodes)}')
    for mesh in check['meshes']:
        for p in mesh['primitives']:
            if 'JOINTS_0' not in p['attributes'] or 'WEIGHTS_0' not in p['attributes']:
                raise RuntimeError('primitive missing native rigid binding attributes')

    report = {
        'output': str(a.out), 'output_bytes': a.out.stat().st_size,
        'geometry': {'models': 6, 'meshes': 8, 'triangles_lod1': 10738},
        'textures': {'images': len(check.get('images', [])), 'core_gltf_textures': len(check.get('textures', []))},
        'rig': {'joints': 7, 'skin_count': 1, 'skeleton_resource': '80AA3C97', 'runtime_rig': '80AA2D6D'},
        'animations': [x.get('name') for x in check.get('animations', [])],
        'binding_rows': joint_rows,
        'binary_spans': {'textured_bytes': len(geo_bin), 'rig_bytes': len(rig_bin), 'rig_base': rig_base, 'combined_bin_bytes': len(check_bin)},
        'policy': 'No guessed geometry, joint indices, weights, skeleton, or clips. Every vertex uses retail primary-stream lane3 joint index and rigid weight 1.0.',
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'binding_rows'}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
