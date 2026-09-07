#!/usr/bin/env python3
"""Build a Blender-facing Crota ethereal preview from the source-closed R8 GLB.

This adapter corrects two portable-view mistakes without changing source identity:

1. Crota's active D1 materials all use state byte 0x88. The already source-closed
   D1 blend selector maps 0x88 -> state 8:
       Source + Destination * (1 - SourceAlpha)
   Native GCN closes the paired Crota color/attenuation contract:
       PS 8108E953/955/956 : RGB contribution, MRT0 alpha = 0
       PS 80AAE1CD         : RGB = 0, alpha = 1
       PS 8108E958/959     : RGB = 0, nonzero attenuation alpha
   Therefore the group-3 ranges R7/R8 called "auxiliary" are not a redundant LOD;
   they are the destination-attenuation half of Crota's ethereal composition.
   Core glTF cannot express this custom two-pass equation, so this file creates an
   explicitly marked translucent/emissive proxy on the already correct group-2
   geometry. Exact group-3 material/shader identities remain documented in extras.

2. The visible mesh2 range 45583/4904 carries source NORMAL values that disagree
   badly with its actual exported triangle winding. For Blender only, this adapter
   recomputes area-weighted normals for that one range. The original exact NORMAL
   accessor is retained losslessly as _D1_NORMAL_RAW.

Mode ``bind-no-armature`` also removes the skin/armature from the active scene only;
this prevents Blender's bone display from appearing as long rods through Crota during
static visual inspection. Source skin/joint objects remain serialized but unreachable.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import struct
from pathlib import Path

import numpy as np

PROC = {'8108E7A9', '8108E7B2'}
ATLAS = {'8108E7AA', '8108E7B3'}
DETAIL = {'8108E7B1'}
ACTIVE = PROC | ATLAS | DETAIL

# Exact serialized partner materials for the same high-detail ranges.
ATTENUATION_PARTNER = {
    '8108E7A9': '8108E7AB',
    '8108E7AA': '8108E7AC',
    '8108E7B1': '809DD1DC',
    '8108E7B2': '8108E7B4',
    '8108E7B3': '8108E7B5',
}
COLOR_PS = {
    '8108E7A9': '8108E955',
    '8108E7AA': '8108E956',
    '8108E7B1': '8108E953',
    '8108E7B2': '8108E955',
    '8108E7B3': '8108E956',
}
ATTEN_PS = {
    '8108E7A9': '8108E958',
    '8108E7AA': '8108E959',
    '8108E7B1': '80AAE1CD',
    '8108E7B2': '8108E958',
    '8108E7B3': '8108E959',
}
PROC_FACTOR = [0.18661969900131226, 1.0, 0.8700880408287048]
DETAIL_FACTOR = [0.22183096408843994, 1.0, 0.9177990555763245]
TARGET_NORMAL_NODE = '8108E5B7_mesh2_range45583_4904'

CTYPES = {
    5120: np.int8,
    5121: np.uint8,
    5122: np.int16,
    5123: np.uint16,
    5125: np.uint32,
    5126: np.float32,
}
NCOMP = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_glb(p: Path):
    raw = p.read_bytes()
    if raw[:4] != b'glTF':
        raise ValueError('not a GLB')
    jl, jt = struct.unpack_from('<II', raw, 12)
    if jt != 0x4E4F534A:
        raise ValueError('missing JSON chunk')
    doc = json.loads(raw[20:20 + jl].decode().rstrip(' \x00'))
    bo = 20 + jl
    bl, bt = struct.unpack_from('<II', raw, bo)
    if bt != 0x004E4942:
        raise ValueError('missing BIN chunk')
    return doc, raw[bo + 8:bo + 8 + bl]


def write_glb(p: Path, doc: dict, blob: bytes):
    j = json.dumps(doc, separators=(',', ':'), ensure_ascii=False).encode()
    j += b' ' * ((4 - len(j) % 4) % 4)
    bb = blob + b'\x00' * ((4 - len(blob) % 4) % 4)
    out = bytearray(struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(j) + 8 + len(bb)))
    out += struct.pack('<II', len(j), 0x4E4F534A) + j
    out += struct.pack('<II', len(bb), 0x004E4942) + bb
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(out)


def mat_tag(m: dict) -> str:
    return str((m.get('extras') or {}).get('d1_material_taghash') or '').upper()


def accessor_array(doc: dict, blob: bytes, ai: int) -> np.ndarray:
    a = doc['accessors'][ai]
    if 'sparse' in a:
        raise ValueError('sparse accessor unsupported in bounded Crota adapter')
    bv = doc['bufferViews'][a['bufferView']]
    dt = np.dtype(CTYPES[int(a['componentType'])]).newbyteorder('<')
    nc = NCOMP[a['type']]
    count = int(a['count'])
    off = int(bv.get('byteOffset', 0)) + int(a.get('byteOffset', 0))
    packed = dt.itemsize * nc
    stride = int(bv.get('byteStride', packed))
    if stride == packed:
        arr = np.frombuffer(blob, dtype=dt, count=count * nc, offset=off).copy()
        return arr.reshape((count, nc)) if nc > 1 else arr
    out = np.empty((count, nc), dtype=dt)
    for i in range(count):
        out[i] = np.frombuffer(blob, dtype=dt, count=nc, offset=off + i * stride)
    return out if nc > 1 else out[:, 0]


def geometric_vertex_normals(pos: np.ndarray, indices: np.ndarray) -> np.ndarray:
    tri = np.asarray(indices, dtype=np.int64).reshape((-1, 3))
    if tri.size == 0 or tri.min() < 0 or tri.max() >= len(pos):
        raise ValueError('invalid target triangle indices')
    p0, p1, p2 = pos[tri[:, 0]], pos[tri[:, 1]], pos[tri[:, 2]]
    fn = np.cross(p1 - p0, p2 - p0)
    out = np.zeros((len(pos), 3), dtype=np.float64)
    for k in range(3):
        np.add.at(out, tri[:, k], fn)
    n = np.linalg.norm(out, axis=1)
    bad = n <= 1e-20
    if np.any(bad):
        # Isolated/degenerate vertices are not used to invent orientation.
        out[bad] = [0.0, 0.0, 1.0]
        n[bad] = 1.0
    return (out / n[:, None]).astype(np.float32)


def face_corner_dot_stats(pos: np.ndarray, indices: np.ndarray, normals: np.ndarray) -> dict:
    tri = np.asarray(indices, dtype=np.int64).reshape((-1, 3))
    p0, p1, p2 = pos[tri[:, 0]], pos[tri[:, 1]], pos[tri[:, 2]]
    fn = np.cross(p1 - p0, p2 - p0)
    ln = np.linalg.norm(fn, axis=1)
    good = ln > 1e-20
    fn = fn[good] / ln[good, None]
    tri = tri[good]
    dots = np.concatenate([np.einsum('ij,ij->i', normals[tri[:, k]], fn) for k in range(3)])
    return {
        'corner_count': int(len(dots)),
        'mean_dot': float(np.mean(dots)),
        'median_dot': float(np.median(dots)),
        'negative_fraction': float(np.count_nonzero(dots < 0.0) / len(dots)),
    }


def repair_target_normal(doc: dict, blob: bytes) -> tuple[bytes, dict]:
    matches = [(i, n) for i, n in enumerate(doc.get('nodes', [])) if n.get('name') == TARGET_NORMAL_NODE]
    if len(matches) != 1:
        raise ValueError(f'expected one {TARGET_NORMAL_NODE}, got {len(matches)}')
    ni, node = matches[0]
    mi = int(node['mesh'])
    prim = doc['meshes'][mi]['primitives'][0]
    if int(prim.get('mode', 4)) != 4:
        raise ValueError('target normal repair expects triangle-list primitive')
    attrs = prim['attributes']
    old_normal = int(attrs['NORMAL'])
    pos = accessor_array(doc, blob, int(attrs['POSITION'])).astype(np.float64)
    idx = accessor_array(doc, blob, int(prim['indices'])).astype(np.int64).reshape(-1)
    old = accessor_array(doc, blob, old_normal).astype(np.float32)
    if old.shape != (len(pos), 3):
        raise ValueError(f'target NORMAL shape drift {old.shape}/{len(pos)}')
    new = geometric_vertex_normals(pos, idx)
    before = face_corner_dot_stats(pos, idx, old)
    after = face_corner_dot_stats(pos, idx, new)

    pad = (-len(blob)) & 3
    if pad:
        blob += b'\x00' * pad
    off = len(blob)
    payload = np.asarray(new, dtype='<f4').tobytes(order='C')
    blob += payload
    bvi = len(doc.setdefault('bufferViews', []))
    doc['bufferViews'].append({
        'buffer': 0,
        'byteOffset': off,
        'byteLength': len(payload),
        'target': 34962,
        'name': 'CROTA_R9_RECOMPUTED_NORMAL_mesh2_range45583_4904',
    })
    ai = len(doc.setdefault('accessors', []))
    doc['accessors'].append({
        'bufferView': bvi,
        'byteOffset': 0,
        'componentType': 5126,
        'count': len(new),
        'type': 'VEC3',
        'name': 'CROTA_R9_RECOMPUTED_NORMAL_mesh2_range45583_4904',
    })
    attrs['_D1_NORMAL_RAW'] = old_normal
    attrs['NORMAL'] = ai
    prim.setdefault('extras', {})['d1CrotaR9NormalRepair'] = {
        'sourceNormalAccessor': old_normal,
        'portableNormalAccessor': ai,
        'sourcePreservedAs': '_D1_NORMAL_RAW',
        'reason': 'source NORMAL disagrees with exported triangle winding on this one visible range',
    }
    doc['buffers'][0]['byteLength'] = len(blob)
    return blob, {
        'node': TARGET_NORMAL_NODE,
        'node_index': ni,
        'mesh_index': mi,
        'source_normal_accessor': old_normal,
        'portable_normal_accessor': ai,
        'vertex_count': int(len(new)),
        'before': before,
        'after': after,
    }


def make_ethereal_materials(doc: dict) -> list[dict]:
    used = set(doc.get('extensionsUsed') or [])
    used.add('KHR_materials_emissive_strength')
    doc['extensionsUsed'] = sorted(used)
    rows = []
    for mi, m in enumerate(doc.get('materials', [])):
        tag = mat_tag(m)
        if tag not in ACTIVE:
            continue
        pbr = m.setdefault('pbrMetallicRoughness', {})
        pbr['metallicFactor'] = 0.0
        pbr['roughnessFactor'] = 1.0
        if tag in PROC:
            alpha = 0.28
            rgb = PROC_FACTOR
            pbr.pop('baseColorTexture', None)
            pbr['baseColorFactor'] = [*rgb, alpha]
            m.pop('emissiveTexture', None)
            m['emissiveFactor'] = rgb
            strength = 2.8
            proxy = 'source cbuffer RGB + translucent/emissive proxy; procedural attenuation is view/runtime dependent'
        elif tag in ATLAS:
            alpha = 0.36
            tex = pbr.get('baseColorTexture')
            if not tex:
                raise ValueError(f'{tag}: exact 8108E951 texture missing')
            pbr['baseColorFactor'] = [1.0, 1.0, 1.0, alpha]
            m['emissiveTexture'] = copy.deepcopy(tex)
            m['emissiveFactor'] = [0.55, 1.0, 0.82]
            strength = 2.2
            proxy = 'exact 8108E951 RGB + translucent/emissive proxy; paired PS8108E959 attenuation remains native contract'
        else:
            alpha = 0.30
            tex = pbr.get('baseColorTexture')
            if not tex:
                raise ValueError(f'{tag}: exact 8108E952 texture missing')
            pbr['baseColorFactor'] = [*DETAIL_FACTOR, alpha]
            m['emissiveTexture'] = copy.deepcopy(tex)
            m['emissiveFactor'] = DETAIL_FACTOR
            strength = 2.4
            proxy = 'exact 8108E952 RGB + translucent/emissive proxy; paired 80AAE1CD is black alpha=1'
        m['alphaMode'] = 'BLEND'
        m['doubleSided'] = True
        ext = dict(m.get('extensions') or {})
        ext['KHR_materials_emissive_strength'] = {'emissiveStrength': strength}
        m['extensions'] = ext
        ex = m.setdefault('extras', {})
        ex['d1CrotaR9EtherealProxy'] = {
            'status': 'SOURCE_CONSTRAINED_PORTABLE_APPROXIMATION',
            'nativeBlendSelector': '0x88',
            'nativeBlendStateIndex': 8,
            'nativeBlendEquation': 'Source + Destination*(1-SourceAlpha)',
            'colorPixelShader': COLOR_PS[tag],
            'attenuationMaterial': ATTENUATION_PARTNER[tag],
            'attenuationPixelShader': ATTEN_PS[tag],
            'portableProxy': proxy,
        }
        rows.append({
            'material_index': mi,
            'material': tag,
            'color_ps': COLOR_PS[tag],
            'attenuation_material': ATTENUATION_PARTNER[tag],
            'attenuation_ps': ATTEN_PS[tag],
            'alpha_proxy': alpha,
            'emissive_strength': strength,
        })
    if {x['material'] for x in rows} != ACTIVE:
        raise ValueError(f'active material set drift: {sorted(x["material"] for x in rows)}')
    return rows


def active_scene_mesh_nodes(doc: dict) -> tuple[int, int, list[int]]:
    si = int(doc.get('scene', 0))
    roots = doc['scenes'][si].get('nodes', [])
    if len(roots) != 1:
        raise ValueError(f'expected one portable root, got {roots}')
    root = int(roots[0])
    rn = doc['nodes'][root]
    mesh_nodes = [int(x) for x in rn.get('children', []) if doc['nodes'][int(x)].get('mesh') is not None]
    return si, root, mesh_nodes


def remove_armature_from_static_view(doc: dict) -> dict:
    _, root, meshes = active_scene_mesh_nodes(doc)
    if len(meshes) != 6:
        raise ValueError(f'expected six active color meshes, got {len(meshes)}')
    rn = doc['nodes'][root]
    children = list(rn.get('children', []))
    skeleton = [int(x) for x in children if 'SKELETON_ROOT' in str(doc['nodes'][int(x)].get('name', '')).upper()]
    if len(skeleton) != 1:
        raise ValueError(f'expected one active skeleton root, got {skeleton}')
    rn['children'] = [int(x) for x in children if int(x) not in skeleton]
    skins_removed = 0
    for ni in meshes:
        if 'skin' in doc['nodes'][ni]:
            doc['nodes'][ni].pop('skin')
            skins_removed += 1
    return {
        'removed_skeleton_root_node': skeleton[0],
        'active_mesh_skin_links_removed': skins_removed,
        'serialized_skin_count_preserved': len(doc.get('skins', [])),
        'serialized_joint_nodes_preserved': len(doc.get('nodes', [])),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('input', type=Path)
    ap.add_argument('--mode', choices=('bind-no-armature', 'animated'), required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    src, chunk = read_glb(a.input)
    d = copy.deepcopy(src)
    source_buffer_len = int(d['buffers'][0]['byteLength'])
    if source_buffer_len > len(chunk):
        raise ValueError('declared source buffer exceeds BIN chunk')
    source_prefix = bytes(chunk[:source_buffer_len])
    blob = source_prefix

    _, _, active_meshes = active_scene_mesh_nodes(d)
    if len(active_meshes) != 6:
        raise ValueError(f'R9 requires six R7/R8 color-stage meshes, got {len(active_meshes)}')
    active_tags = []
    for ni in active_meshes:
        prim = d['meshes'][int(d['nodes'][ni]['mesh'])]['primitives'][0]
        active_tags.append(mat_tag(d['materials'][int(prim['material'])]))
    if set(active_tags) != ACTIVE:
        raise ValueError(f'active tag drift {active_tags}')

    blob, normal_report = repair_target_normal(d, blob)
    material_rows = make_ethereal_materials(d)
    armature_report = None
    if a.mode == 'bind-no-armature':
        if len(d.get('animations', [])) != 0:
            raise ValueError('bind-no-armature input unexpectedly has animations')
        armature_report = remove_armature_from_static_view(d)
    else:
        if len(d.get('animations', [])) < 1:
            raise ValueError('animated mode requires at least one exact animation')

    d.setdefault('asset', {}).setdefault('extras', {})['d1CrotaR9EtherealPreview'] = {
        'schema': 'd1_crota_r9_ethereal_preview/v1',
        'status': 'SOURCE_CONSTRAINED_PORTABLE_APPROXIMATION',
        'nativeBlendSelector': '0x88',
        'nativeBlendStateIndex': 8,
        'nativeBlendEquation': 'Source + Destination*(1-SourceAlpha)',
        'nativeColorPass': 'PS 8108E953/955/956 export RGB with alpha=0',
        'nativeAttenuationPass': 'PS 80AAE1CD exports black alpha=1; PS 8108E958/959 export black with attenuation alpha',
        'portablePolicy': 'Core glTF cannot encode the native two-pass custom blend; active group-2 surfaces use a translucent emissive proxy while exact partner identities remain in extras.',
        'normalRepair': TARGET_NORMAL_NODE,
        'staticArmaturePolicy': 'bind-no-armature removes only active scene skin/armature links so Blender cannot display bones as geometry-like rods',
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    write_glb(a.out, d, blob)
    chk, outchunk = read_glb(a.out)
    out_buffer_len = int(chk['buffers'][0]['byteLength'])
    if bytes(outchunk[:source_buffer_len]) != source_prefix:
        raise ValueError('source BIN is not an exact output prefix')
    if out_buffer_len <= source_buffer_len:
        raise ValueError('normal repair did not append portable data')
    if len(chk.get('meshes', [])) != len(src.get('meshes', [])):
        raise ValueError('source mesh count changed')
    if len(chk.get('animations', [])) != len(src.get('animations', [])):
        raise ValueError('animation count changed')

    rep = {
        'schema': 'd1_crota_r9_ethereal_preview/v1',
        'status': 'D1_CROTA_R9_ETHEREAL_PREVIEW_COMPLETE',
        'mode': a.mode,
        'input': str(a.input),
        'input_sha256': sha256_file(a.input),
        'output': str(a.out),
        'output_sha256': sha256_file(a.out),
        'output_bytes': a.out.stat().st_size,
        'source_bin_exact_prefix': True,
        'source_buffer_bytes': source_buffer_len,
        'output_buffer_bytes': out_buffer_len,
        'active_color_surface_count': 6,
        'material_rows': material_rows,
        'normal_repair': normal_report,
        'armature_static_view': armature_report,
        'animation_count': len(chk.get('animations', [])),
        'native_contract': {
            'blend_selector_raw': '0x88',
            'blend_state_index': 8,
            'blend_equation': 'Source + Destination*(1-SourceAlpha)',
            'color_pass_ps': ['8108E953', '8108E955', '8108E956'],
            'attenuation_pass_ps': ['80AAE1CD', '8108E958', '8108E959'],
        },
        'withheld': [
            'native-equivalent custom two-pass blend in core glTF',
            'runtime/view-dependent exact attenuation scalar for PS 8108E958/959',
        ],
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(rep, indent=2) + '\n')
    print(json.dumps(rep, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
