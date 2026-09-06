#!/usr/bin/env python3
"""Bind portable D1 preview textures without discarding native shader resources.

The old world preview adapter round-tripped through trimesh.  That was convenient
for PBR preview material creation, but the resulting GLB only contained images
that happened to fit a portable base-color/normal slot.  Exact D1 material
resources with mask, scalar, cubemap, reflection, palette, or other native roles
were therefore absent from the GLB even though extraction had recovered them.

This adapter edits the GLB JSON/BIN directly:

* every exact texture referenced by the supplied material manifest/inventory is
  embedded exactly once as a PNG image + glTF texture resource;
* each image/texture is named by its D1 Texture TagHash and carries source-format,
  resource-class, shader/register, and proven-role metadata in ``extras``;
* safe preview base-color bindings reuse those exact source texture resources;
* BC5 normals selected for portable preview get one additional derived +Z RGB
  normal image while the exact decoded source texture remains preserved;
* materials retain the complete native pixel-shader/t# binding table in extras;
* geometry, accessors, meshes, nodes, and all existing BIN bytes remain exact
  prefixes.  No texture is fabricated from appearance and no unknown role is
  promoted to canonical semantics.

For the closed Tower common-layer corpus this intentionally produces 50 exact
source texture resources plus one derived portable normal, reproducing the
resource topology of the 588-texture combined Tower checkpoint when merged onto
the 537-texture baked base.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

from d1_gltf_layer_merge import read_glb, write_glb

MAT_RE = re.compile(r'(?:TigerMaterial_|D1_)([0-9A-Fa-f]{8})')


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def append_blob(doc: dict, bin_data: bytes, payload: bytes, *, name: str | None = None) -> tuple[int, bytes]:
    aligned = (len(bin_data) + 3) & ~3
    if aligned != len(bin_data):
        bin_data += b'\x00' * (aligned - len(bin_data))
    off = len(bin_data)
    idx = len(doc.setdefault('bufferViews', []))
    row = {'buffer': 0, 'byteOffset': off, 'byteLength': len(payload)}
    if name:
        row['name'] = name
    doc['bufferViews'].append(row)
    return idx, bin_data + payload


def load_png_for_texture(texrec: dict, texture_dir: Path) -> tuple[Path, bytes]:
    rel = texrec.get('png')
    if not rel:
        raise FileNotFoundError('texture manifest has no PNG output')
    p = texture_dir / rel
    if not p.exists():
        raise FileNotFoundError(str(p))
    data = p.read_bytes()
    with Image.open(io.BytesIO(data)) as im:
        im.verify()
    return p, data


def bc5_to_rgb_normal_png(data: bytes) -> bytes:
    with Image.open(io.BytesIO(data)) as im:
        a = np.asarray(im.convert('RGB'), dtype=np.float32) / 255.0
    x = a[..., 0] * 2.0 - 1.0
    y = a[..., 1] * 2.0 - 1.0
    z = np.sqrt(np.maximum(0.0, 1.0 - x * x - y * y))
    out = np.stack((x * 0.5 + 0.5, y * 0.5 + 0.5, z * 0.5 + 0.5), axis=-1)
    nim = Image.fromarray(np.clip(out * 255.0 + 0.5, 0, 255).astype(np.uint8), 'RGB')
    bio = io.BytesIO()
    # Fixed encoder settings make the derived resource deterministic.
    nim.save(bio, format='PNG', optimize=False, compress_level=9)
    return bio.getvalue()


def texture_usage(inventory: dict) -> dict[str, list[dict]]:
    uses: dict[str, list[dict]] = defaultdict(list)
    for mh, m in sorted((inventory.get('materials') or {}).items()):
        ps = m.get('pixel_shader')
        for b in m.get('bindings', []):
            tag = str(b.get('texture', '')).upper()
            if not tag:
                continue
            uses[tag].append({
                'material': mh.upper(),
                'pixel_shader': ps,
                'texture_index': int(b.get('texture_index', -1)),
                'resource_class': b.get('resource_class'),
                'proven_role': b.get('proven_role'),
                'evidence_status': b.get('evidence_status'),
                'preview_role': b.get('preview_role'),
            })
    return dict(uses)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-glb', type=Path, required=True)
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--roles', type=Path, required=True)
    ap.add_argument('--texture-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--include-medium-base', action='store_true')
    ap.add_argument('--bind-normal-candidates', action='store_true')
    ap.add_argument('--expect-exact-textures', type=int)
    ap.add_argument('--expect-derived-normals', type=int)
    a = ap.parse_args()

    manifest = json.loads(a.manifest.read_text())
    inventory = json.loads(a.roles.read_text())
    texrecs = manifest.get('textures') or {}
    semantics = inventory.get('materials') or {}
    uses = texture_usage(inventory)
    exact_tags = sorted(uses)

    if set(exact_tags) - set(texrecs):
        raise SystemExit('role inventory references texture tags absent from manifest: ' + ','.join(sorted(set(exact_tags)-set(texrecs))))
    if a.expect_exact_textures is not None and len(exact_tags) != a.expect_exact_textures:
        raise SystemExit(f'exact texture count changed: {len(exact_tags)} != {a.expect_exact_textures}')

    src_doc, src_bin = read_glb(a.input_glb)
    doc = copy.deepcopy(src_doc)
    bin_data = src_bin
    base_counts = {k: len(src_doc.get(k, [])) for k in ('bufferViews','images','textures','materials','meshes','nodes','accessors')}

    # Embed every exact source texture once, independent of portable PBR support.
    source_texture_index: dict[str, int] = {}
    source_rows = []
    for tag in exact_tags:
        rec = texrecs[tag]
        p, png = load_png_for_texture(rec, a.texture_dir)
        uv = uses[tag]
        classes = sorted({str(x.get('resource_class')) for x in uv if x.get('resource_class')})
        proven = sorted({str(x.get('proven_role')) for x in uv if x.get('proven_role')})
        bvi, bin_data = append_blob(doc, bin_data, png, name=f'D1_TEXTURE_{tag}_PNG')
        ii = len(doc.setdefault('images', []))
        img_extras = {
            'd1_taghash': tag,
            'd1_exact_source_texture': True,
            'd1_format_name': rec.get('format_name'),
            'd1_header_info': rec.get('header_info'),
            'd1_resource_classes': classes,
            'd1_proven_roles': proven,
            'd1_shader_bindings': uv,
            'd1_png_sha256': sha256_bytes(png),
            'd1_manifest_png': rec.get('png'),
        }
        doc['images'].append({'name': f'D1_TEXTURE_{tag}', 'mimeType': 'image/png', 'bufferView': bvi, 'extras': img_extras})
        ti = len(doc.setdefault('textures', []))
        doc['textures'].append({'name': f'D1_TEXTURE_{tag}', 'source': ii, 'extras': {
            'd1_taghash': tag,
            'd1_exact_source_texture': True,
            'd1_resource_classes': classes,
            'd1_proven_roles': proven,
        }})
        source_texture_index[tag] = ti
        source_rows.append({'tag': tag, 'texture_index': ti, 'image_index': ii, 'buffer_view': bvi,
                            'png': str(p), 'png_bytes': len(png), 'png_sha256': sha256_bytes(png),
                            'resource_classes': classes, 'proven_roles': proven, 'usage_count': len(uv)})

    allowed_base = {'PROVEN', 'STRONG_FORMAT_CANDIDATE'}
    if a.include_medium_base:
        allowed_base.add('MEDIUM_PREVIEW_CANDIDATE')
    allowed_normals = {'PROVEN'}
    if a.bind_normal_candidates:
        allowed_normals.add('STRONG_FORMAT_CANDIDATE')

    # Portable normal images are intentionally derived resources.  They are
    # additional to, not replacements for, the exact source BC5 texture.
    derived_normal_index: dict[str, int] = {}
    derived_rows = []
    needed_normals = sorted({
        str(m.get('preview_normal')).upper()
        for m in semantics.values()
        if m.get('preview_normal') and m.get('preview_normal_confidence') in allowed_normals
           and m.get('preview_base_color') and m.get('preview_base_confidence') in allowed_base
    })
    for tag in needed_normals:
        rec = texrecs.get(tag)
        if rec is None:
            raise SystemExit(f'normal preview texture {tag} absent from manifest')
        p, source_png = load_png_for_texture(rec, a.texture_dir)
        derived_png = bc5_to_rgb_normal_png(source_png)
        bvi, bin_data = append_blob(doc, bin_data, derived_png, name=f'D1_DERIVED_NORMAL_{tag}_PNG')
        ii = len(doc.setdefault('images', []))
        doc['images'].append({'name': f'D1_DERIVED_NORMAL_{tag}', 'mimeType': 'image/png', 'bufferView': bvi, 'extras': {
            'd1_source_taghash': tag,
            'd1_derived_portable_normal': True,
            'd1_derivation': 'BC5/RG XY -> [-1,+1], reconstruct +Z, encode RGB tangent normal',
            'd1_source_png_sha256': sha256_bytes(source_png),
            'd1_png_sha256': sha256_bytes(derived_png),
        }})
        ti = len(doc.setdefault('textures', []))
        doc['textures'].append({'name': f'D1_DERIVED_NORMAL_{tag}', 'source': ii, 'extras': {
            'd1_source_taghash': tag, 'd1_derived_portable_normal': True,
        }})
        derived_normal_index[tag] = ti
        derived_rows.append({'source_tag': tag, 'texture_index': ti, 'image_index': ii,
                             'buffer_view': bvi, 'png_bytes': len(derived_png),
                             'png_sha256': sha256_bytes(derived_png), 'source_png': str(p)})

    if a.expect_derived_normals is not None and len(derived_rows) != a.expect_derived_normals:
        raise SystemExit(f'derived normal count changed: {len(derived_rows)} != {a.expect_derived_normals}')

    material_rows = []
    bound_materials = 0
    normal_bound_materials = 0
    material_hashes_seen = set()
    for mi, mat in enumerate(doc.get('materials', [])):
        name = str(mat.get('name') or '')
        mm = MAT_RE.search(name)
        if not mm:
            continue
        mh = mm.group(1).upper()
        material_hashes_seen.add(mh)
        sem = semantics.get(mh)
        if sem is None:
            continue
        conf = sem.get('preview_base_confidence', 'NONE')
        base = str(sem.get('preview_base_color') or '').upper() if conf in allowed_base else ''
        nconf = sem.get('preview_normal_confidence', 'NONE')
        normal = str(sem.get('preview_normal') or '').upper() if nconf in allowed_normals and base else ''
        native_bindings = []
        for b in sem.get('bindings', []):
            tag = str(b.get('texture') or '').upper()
            native_bindings.append({
                't': int(b.get('texture_index', -1)),
                'taghash': tag,
                'exact_texture_index': source_texture_index.get(tag),
                'resource_class': b.get('resource_class'),
                'proven_role': b.get('proven_role'),
                'evidence_status': b.get('evidence_status'),
                'preview_role': b.get('preview_role'),
            })
        ex = mat.setdefault('extras', {})
        ex['d1_material_taghash'] = mh
        ex['d1_pixel_shader'] = sem.get('pixel_shader')
        ex['d1_native_texture_bindings'] = native_bindings
        ex['d1_preview_base_confidence'] = conf
        ex['d1_preview_normal_confidence'] = nconf
        if base:
            if base not in source_texture_index:
                raise SystemExit(f'{mh}: selected base {base} is not an exact embedded texture')
            pbr = mat.setdefault('pbrMetallicRoughness', {})
            pbr['baseColorTexture'] = {'index': source_texture_index[base]}
            pbr['metallicFactor'] = 0.0
            pbr['roughnessFactor'] = 1.0
            mat['alphaMode'] = 'OPAQUE'
            bound_materials += 1
            if normal:
                if normal not in derived_normal_index:
                    raise SystemExit(f'{mh}: selected normal {normal} has no derived portable resource')
                mat['normalTexture'] = {'index': derived_normal_index[normal]}
                normal_bound_materials += 1
        material_rows.append({'material_index': mi, 'material': mh, 'pixel_shader': sem.get('pixel_shader'),
                              'base_texture': base or None, 'base_confidence': conf,
                              'normal_texture': normal or None, 'normal_confidence': nconf,
                              'native_binding_count': len(native_bindings)})

    missing_materials = sorted(set(semantics) - material_hashes_seen)
    if missing_materials:
        raise SystemExit('role-inventory materials not represented in input GLB: ' + ','.join(missing_materials))

    # Record corpus-level provenance in the asset itself.
    asset = doc.setdefault('asset', {'version': '2.0'})
    ax = asset.setdefault('extras', {})
    ax['d1_exact_shader_texture_corpus'] = {
        'exact_texture_count': len(source_rows),
        'derived_portable_normal_count': len(derived_rows),
        'source_manifest_status': manifest.get('status'),
        'role_inventory_status': inventory.get('status'),
        'policy': 'All exact D1 shader texture resources are embedded once; portable PBR bindings are a view over the preserved native t# table.',
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    write_glb(a.out, doc, bin_data)
    chk, chk_bin = read_glb(a.out)
    if chk_bin[:len(src_bin)] != src_bin:
        raise SystemExit('input BIN payload is not an exact output prefix')
    for key in ('accessors','meshes','nodes'):
        if chk.get(key, []) != src_doc.get(key, []):
            raise SystemExit(f'input {key} changed while binding textures')

    final_counts = {k: len(chk.get(k, [])) for k in ('bufferViews','images','textures','materials','meshes','nodes','accessors')}
    expected_images = base_counts['images'] + len(source_rows) + len(derived_rows)
    expected_textures = base_counts['textures'] + len(source_rows) + len(derived_rows)
    if final_counts['images'] != expected_images or final_counts['textures'] != expected_textures:
        raise SystemExit(f'resource count mismatch images/textures {final_counts} expected {expected_images}/{expected_textures}')

    report = {
        'schema_version': 1,
        'status': 'D1_GLTF_EXACT_SHADER_TEXTURE_RESOURCES_BOUND',
        'input_glb': str(a.input_glb),
        'input_sha256': sha256_file(a.input_glb),
        'output_glb': str(a.out),
        'output_sha256': sha256_file(a.out),
        'output_bytes': a.out.stat().st_size,
        'base_counts': base_counts,
        'final_counts': final_counts,
        'exact_source_texture_count': len(source_rows),
        'derived_portable_normal_count': len(derived_rows),
        'portable_base_bound_material_count': bound_materials,
        'portable_normal_bound_material_count': normal_bound_materials,
        'include_medium_base': a.include_medium_base,
        'bind_normal_candidates': a.bind_normal_candidates,
        'source_textures': source_rows,
        'derived_normals': derived_rows,
        'materials': material_rows,
        'policy': (
            'All exact manifest texture tags referenced by the native material shader bindings are embedded once and retained even when glTF has no native PBR slot. '
            'Portable base/normal mappings never replace the native pixel-shader/t# metadata. Derived +Z normals are explicitly additional preview resources.'
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in (
        'status','exact_source_texture_count','derived_portable_normal_count',
        'portable_base_bound_material_count','portable_normal_bound_material_count',
        'base_counts','final_counts','output_bytes','output_sha256')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
