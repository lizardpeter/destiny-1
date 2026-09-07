#!/usr/bin/env python3
"""Loss-preserving exact D1 texture binder driven by the material manifest itself.

v2 used the semantic-role inventory as both the preview-policy source and the exact
texture usage source.  That inventory intentionally contains only pixel-shader
bindings, so a VS-only native texture could be omitted from the GLB resource set.

This version separates those concerns:

* exact material -> VS/PS -> t# -> Texture TagHash edges come only from the exact
  material_texture_manifest.json;
* preview base/normal choices come only from the evidence-scoped role inventory;
* every native texture referenced by a material actually present in the input GLB
  is embedded, including VS-only textures and cubemaps;
* every material extra records stage, t#, TagHash and exact glTF texture index;
* the original BIN chunk remains an exact prefix and accessors/meshes/nodes are
  byte-for-byte JSON equivalent after save/reload.

Portable PBR slots remain a preview adapter only.  Native shader bindings retained
in extras are authoritative.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from collections import defaultdict
from pathlib import Path

from d1_gltf_bind_exact_shader_textures_v2 import (
    MAT_RE,
    append_blob,
    bc5_normal,
    hbytes,
    hfile,
    load_native_image,
    read_glb,
    write_glb,
)
from d1_world_texture_role_inventory import resource_class


def norm(x: str) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def glb_material_hashes(doc: dict) -> dict[int, str]:
    out = {}
    for i, m in enumerate(doc.get('materials', [])):
        mm = MAT_RE.search(str(m.get('name') or ''))
        if mm:
            out[i] = mm.group(1).upper()
    return out


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
    a = ap.parse_args()

    man = json.loads(a.manifest.read_text())
    inv = json.loads(a.roles.read_text())
    tex = man.get('textures') or {}
    manifest_materials = man.get('materials') or {}
    semantic_materials = inv.get('materials') or {}

    src, srcbin = read_glb(a.input_glb)
    doc = copy.deepcopy(src)
    bindata = srcbin
    material_indices = glb_material_hashes(doc)
    glb_hashes = sorted(set(material_indices.values()))
    if not glb_hashes:
        raise SystemExit('input GLB contains no D1 material hashes in recognized material names')

    missing_manifest = sorted(set(glb_hashes) - set(manifest_materials))
    if missing_manifest:
        raise SystemExit('GLB materials absent from exact manifest: ' + ','.join(missing_manifest))
    missing_roles = sorted(set(glb_hashes) - set(semantic_materials))
    if missing_roles:
        raise SystemExit('GLB materials absent from role inventory: ' + ','.join(missing_roles))

    exact_usage = defaultdict(list)
    for mh in glb_hashes:
        m = manifest_materials[mh]
        for b in m.get('bindings', []):
            tag = norm(b.get('texture'))
            if tag in ('00000000', 'FFFFFFFF'):
                continue
            exact_usage[tag].append({
                'material': mh,
                'stage': str(b.get('stage') or '').lower(),
                'texture_index': int(b.get('texture_index', -1)),
                'vertex_shader': m.get('vertex_shader'),
                'pixel_shader': m.get('pixel_shader'),
                'semantic_role': b.get('semantic_role'),
                'semantic_status': b.get('semantic_status'),
            })

    tags = sorted(exact_usage)
    absent_textures = sorted(set(tags) - set(tex))
    if absent_textures:
        raise SystemExit('exact bound texture tags absent from manifest: ' + ','.join(absent_textures))

    base_counts = {k: len(src.get(k, [])) for k in ('bufferViews', 'images', 'textures', 'materials', 'meshes', 'nodes', 'accessors')}

    indices = {}
    source_rows = []
    representation_counts = defaultdict(int)
    for tag in tags:
        rec = tex[tag]
        png, rep = load_native_image(tag, rec, a.texture_dir)
        representation_counts[rep['representation']] += 1
        uses = exact_usage[tag]
        bvi, bindata = append_blob(doc, bindata, png, f'D1_TEXTURE_{tag}_PNG')
        image_idx = len(doc.setdefault('images', []))
        rc = resource_class(rec)
        extra = {
            'd1_taghash': tag,
            'd1_native_texture_resource': True,
            'd1_format_name': rec.get('format_name'),
            'd1_header_info': rec.get('header_info'),
            'd1_resource_class': rc,
            'd1_shader_bindings': uses,
            'd1_glb_representation': rep,
            'd1_embedded_png_sha256': hbytes(png),
        }
        doc['images'].append({
            'name': f'D1_TEXTURE_{tag}', 'mimeType': 'image/png', 'bufferView': bvi, 'extras': extra,
        })
        texture_idx = len(doc.setdefault('textures', []))
        doc['textures'].append({
            'name': f'D1_TEXTURE_{tag}', 'source': image_idx,
            'extras': {
                'd1_taghash': tag,
                'd1_native_texture_resource': True,
                'd1_resource_class': rc,
                'd1_representation': rep['representation'],
            },
        })
        indices[tag] = texture_idx
        source_rows.append({
            'tag': tag, 'texture_index': texture_idx, 'image_index': image_idx,
            'buffer_view': bvi, 'png_bytes': len(png), 'png_sha256': hbytes(png),
            'representation': rep, 'resource_class': rc, 'shader_bindings': uses,
        })

    allowed_base = {'PROVEN', 'STRONG_FORMAT_CANDIDATE'}
    if a.include_medium_base:
        allowed_base.add('MEDIUM_PREVIEW_CANDIDATE')
    allowed_normal = {'PROVEN'}
    if a.bind_normal_candidates:
        allowed_normal.add('STRONG_FORMAT_CANDIDATE')

    needed_normals = sorted({
        norm(s.get('preview_normal'))
        for mh, s in semantic_materials.items()
        if mh in glb_hashes
        and s.get('preview_normal')
        and s.get('preview_normal_confidence') in allowed_normal
        and s.get('preview_base_color')
        and s.get('preview_base_confidence') in allowed_base
    })
    normal_indices = {}
    normal_rows = []
    for tag in needed_normals:
        rec = tex[tag]
        if not rec.get('png'):
            raise SystemExit(f'{tag}: selected portable normal is not a 2D PNG resource')
        raw = (a.texture_dir / rec['png']).read_bytes()
        derived = bc5_normal(raw)
        bvi, bindata = append_blob(doc, bindata, derived, f'D1_DERIVED_NORMAL_{tag}_PNG')
        image_idx = len(doc.setdefault('images', []))
        doc['images'].append({
            'name': f'D1_DERIVED_NORMAL_{tag}', 'mimeType': 'image/png', 'bufferView': bvi,
            'extras': {
                'd1_source_taghash': tag,
                'd1_derived_portable_normal': True,
                'd1_derivation': 'BC5/RG XY -> signed XY -> reconstruct +Z -> RGB',
                'd1_png_sha256': hbytes(derived),
            },
        })
        texture_idx = len(doc.setdefault('textures', []))
        doc['textures'].append({
            'name': f'D1_DERIVED_NORMAL_{tag}', 'source': image_idx,
            'extras': {'d1_source_taghash': tag, 'd1_derived_portable_normal': True},
        })
        normal_indices[tag] = texture_idx
        normal_rows.append({
            'source_tag': tag, 'texture_index': texture_idx, 'image_index': image_idx,
            'buffer_view': bvi, 'png_bytes': len(derived), 'png_sha256': hbytes(derived),
        })

    material_rows = []
    portable_base_count = 0
    portable_normal_count = 0
    for mi, mh in material_indices.items():
        m = doc['materials'][mi]
        exact = manifest_materials[mh]
        sem = semantic_materials[mh]
        native = []
        for b in exact.get('bindings', []):
            tag = norm(b.get('texture'))
            if tag in ('00000000', 'FFFFFFFF'):
                continue
            native.append({
                'stage': str(b.get('stage') or '').lower(),
                't': int(b.get('texture_index', -1)),
                'taghash': tag,
                'exact_texture_index': indices[tag],
                'semantic_role': b.get('semantic_role'),
                'semantic_status': b.get('semantic_status'),
            })
        conf = sem.get('preview_base_confidence', 'NONE')
        bt = norm(sem.get('preview_base_color')) if sem.get('preview_base_color') and conf in allowed_base else ''
        nc = sem.get('preview_normal_confidence', 'NONE')
        nt = norm(sem.get('preview_normal')) if sem.get('preview_normal') and nc in allowed_normal and bt else ''
        ex = m.setdefault('extras', {})
        ex.update({
            'd1_material_taghash': mh,
            'd1_vertex_shader': exact.get('vertex_shader'),
            'd1_pixel_shader': exact.get('pixel_shader'),
            'd1_native_texture_bindings': native,
            'd1_preview_base_confidence': conf,
            'd1_preview_normal_confidence': nc,
            'd1_exact_binding_source': 'material_texture_manifest.json',
        })
        if bt:
            pbr = m.setdefault('pbrMetallicRoughness', {})
            pbr['baseColorTexture'] = {'index': indices[bt]}
            pbr['metallicFactor'] = 0.0
            pbr['roughnessFactor'] = 1.0
            m['alphaMode'] = 'OPAQUE'
            portable_base_count += 1
            if nt:
                m['normalTexture'] = {'index': normal_indices[nt]}
                portable_normal_count += 1
        material_rows.append({
            'material_index': mi, 'material': mh,
            'vertex_shader': exact.get('vertex_shader'), 'pixel_shader': exact.get('pixel_shader'),
            'native_binding_count': len(native),
            'vs_binding_count': sum(1 for x in native if x['stage'] == 'vs'),
            'ps_binding_count': sum(1 for x in native if x['stage'] == 'ps'),
            'base_texture': bt or None, 'base_confidence': conf,
            'normal_texture': nt or None, 'normal_confidence': nc,
        })

    doc.setdefault('asset', {'version': '2.0'}).setdefault('extras', {})['d1_exact_shader_texture_corpus'] = {
        'schema': 'd1_gltf_bind_exact_shader_textures/v3',
        'material_count': len(glb_hashes),
        'native_texture_tag_count': len(source_rows),
        'derived_portable_normal_count': len(normal_rows),
        'representation_counts': dict(representation_counts),
        'exact_binding_source': 'material_texture_manifest.json including VS and PS stages',
        'preview_policy_source': 'evidence-scoped texture role inventory',
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    write_glb(a.out, doc, bindata)
    chk, chkbin = read_glb(a.out)
    if chkbin[:len(srcbin)] != srcbin:
        raise SystemExit('input BIN is not exact output prefix')
    for k in ('accessors', 'meshes', 'nodes'):
        if chk.get(k, []) != src.get(k, []):
            raise SystemExit(f'input {k} changed')

    final_counts = {k: len(chk.get(k, [])) for k in ('bufferViews', 'images', 'textures', 'materials', 'meshes', 'nodes', 'accessors')}
    expected_images = base_counts['images'] + len(source_rows) + len(normal_rows)
    expected_textures = base_counts['textures'] + len(source_rows) + len(normal_rows)
    if final_counts['images'] != expected_images or final_counts['textures'] != expected_textures:
        raise SystemExit(f'resource count mismatch {final_counts}')

    vs_edges = sum(len([x for x in uses if x['stage'] == 'vs']) for uses in exact_usage.values())
    ps_edges = sum(len([x for x in uses if x['stage'] == 'ps']) for uses in exact_usage.values())
    report = {
        'schema_version': 3,
        'status': 'D1_GLTF_EXACT_SHADER_TEXTURE_RESOURCES_BOUND_ALL_STAGES',
        'input_glb': str(a.input_glb), 'input_sha256': hfile(a.input_glb),
        'output_glb': str(a.out), 'output_sha256': hfile(a.out), 'output_bytes': a.out.stat().st_size,
        'material_count': len(glb_hashes), 'materials': material_rows,
        'base_counts': base_counts, 'final_counts': final_counts,
        'exact_source_texture_count': len(source_rows),
        'exact_vs_binding_edge_count': vs_edges,
        'exact_ps_binding_edge_count': ps_edges,
        'derived_portable_normal_count': len(normal_rows),
        'representation_counts': dict(representation_counts),
        'portable_base_bound_material_count': portable_base_count,
        'portable_normal_bound_material_count': portable_normal_count,
        'source_textures': source_rows, 'derived_normals': normal_rows,
        'policy': (
            'Exact native texture resources and VS/PS t# edges come only from the exact material manifest. '
            'Preview base/normal bindings are evidence-scoped adapters and never replace native shader metadata. '
            'Input BIN remains an exact prefix and geometry/skin/animation accessors and nodes are unchanged.'
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({
        k: report[k] for k in (
            'status', 'material_count', 'exact_source_texture_count',
            'exact_vs_binding_edge_count', 'exact_ps_binding_edge_count',
            'derived_portable_normal_count', 'portable_base_bound_material_count',
            'portable_normal_bound_material_count', 'representation_counts', 'output_bytes', 'output_sha256'
        )
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
