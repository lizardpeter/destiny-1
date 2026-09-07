#!/usr/bin/env python3
"""Embed Crota's exact D1 texture resources and build an explicit Blender preview view.

The authoritative data preserved in this adapter is:

* material TagHash;
* native vertex/pixel shader TagHashes;
* exact PS t# -> texture TagHash array from the source-closed material stage state;
* exact native GCN image-usage proof for each pixel shader;
* exact decoded retail PNG bytes verified against the texture-export manifest;
* TFX bytecode, private constants, cbuffers and native material-state bytes.

Those native relationships live in glTF material/image extras and are the proof layer.
glTF PBR cannot reproduce arbitrary Destiny/GCN shaders, so portable material slots
are deliberately labelled preview adapters:

* PS 8108E956: t0/8108E951 is directly sampled as RGBA and contributes sampled RGB
  to MRT0, so the Crota 2048x2048 colour atlas is used as a strong portable base view.
* PS 8108E953: t0/8108E952 is directly sampled as RGB and contributes to MRT0; the
  source cbuffer tint [0.221830964,1,0.917799056] is retained as a portable factor.
* PS 8108E955: the native shader consumes five resources procedurally.  For Blender's
  simple material view only, t0/8108E7B6 is shown as a scalar pattern tinted by the
  source material vector [0.373239398,2,1.740176]/2.  This is explicitly PREVIEW_ONLY
  and does not claim t0 is a native base-colour map.
* PS 8108E7B7: the two sampled textures drive control/auxiliary output while MRT0 RGB
  comes from constants.  Conservative output leaves it at the exact black MRT0 colour;
  optional visible-preview mode uses the same t0 scalar resource with a dark neutral
  tint so geometry is inspectable, explicitly PREVIEW_ONLY.

No UV, mesh, skin, joint, inverse-bind, animation channel, animation time or scene
transform is rewritten here.  All exact native textures are embedded regardless of
whether they receive a portable PBR slot.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

from d1_gltf_bind_exact_shader_textures_v2 import append_blob, hbytes, read_glb, write_glb

MAT_RE = re.compile(r'(?:TigerMaterial_|D1_)([0-9A-Fa-f]{8})')
EXPECTED_MATERIALS = {
    '8108E667','8108E66B','8108E7A9','8108E7AA','8108E7B1','8108E7B2','8108E7B3'
}
EXPECTED_TEXTURES = {'8108E7B6','80AACF2A','80AAD0E1','8108E951','8108E952'}


def norm(x) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def hfile(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def texture_rows(manifest: dict) -> dict[str, dict]:
    if manifest.get('status') != 'D1_REMOTE_ACTIVITY_TEXTURE_EXPORT_COMPLETE' or manifest.get('violations'):
        raise ValueError('texture export manifest is not completely closed')
    out = {}
    for row in manifest.get('rows', []):
        h = norm(row.get('texture'))
        if h in out:
            raise ValueError(f'duplicate texture row {h}')
        pngs = [x for x in row.get('files', []) if x.get('kind') == 'png']
        if len(pngs) == 1:
            out[h] = {**row, 'png_file': pngs[0]}
    return out


def glb_materials(doc: dict) -> dict[int, str]:
    out = {}
    for i, m in enumerate(doc.get('materials', [])):
        mm = MAT_RE.search(str(m.get('name') or ''))
        if mm:
            out[i] = mm.group(1).upper()
    return out


def ps_usage_map(usage: dict) -> dict[str, dict]:
    if usage.get('status') != 'D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or usage.get('unmatched_image_instruction_count') != 0:
        raise ValueError('GCN image usage is not fully exact')
    return {norm(x['shader']): x for x in usage.get('shaders', [])}


def direct_preview(material: str, ps: str, stage: dict, mode: str) -> dict:
    """Return portable preview metadata only; native shader metadata remains authoritative."""
    if ps == '8108E956':
        return {
            'kind': 'DIRECT_NATIVE_COLOR_SAMPLE_PREVIEW',
            'texture': '8108E951',
            'base_factor': [1.0,1.0,1.0,1.0],
            'confidence': 'STRONG_NATIVE_DATAFLOW',
            'reason': 'GCN t0 dmask:xyzw sample feeds final MRT0 RGB multiplicatively.',
        }
    if ps == '8108E953':
        return {
            'kind': 'DIRECT_NATIVE_COLOR_SAMPLE_PREVIEW',
            'texture': '8108E952',
            'base_factor': [0.22183096408843994,1.0,0.9177990555763245,1.0],
            'confidence': 'STRONG_NATIVE_DATAFLOW_WITH_SOURCE_TINT',
            'reason': 'GCN t0 dmask:xyz sample feeds final MRT0 RGB; factor is exact material cbuffer vector.',
        }
    if ps == '8108E955':
        return {
            'kind': 'PROCEDURAL_SHADER_SCALAR_PREVIEW_ONLY',
            'texture': '8108E7B6',
            'base_factor': [0.18661969900131226,1.0,0.8700880408287048,1.0],
            'confidence': 'PREVIEW_ONLY',
            'reason': 'Native GCN consumes five textures; t0 scalar is visualized with normalized exact source cbuffer vector. Not a native base-colour semantic.',
        }
    if ps == '8108E7B7':
        if mode == 'visible':
            return {
                'kind': 'CONTROL_TEXTURE_VISIBILITY_PREVIEW_ONLY',
                'texture': '8108E7B6',
                'base_factor': [0.16,0.22,0.20,1.0],
                'confidence': 'PREVIEW_ONLY',
                'reason': 'Native MRT0 RGB is constant black; t0 is shown only to make the surface inspectable in Blender.',
            }
        return {
            'kind': 'EXACT_MRT0_CONSTANT_PREVIEW',
            'texture': None,
            'base_factor': [0.0,0.0,0.0,1.0],
            'confidence': 'EXACT_MRT0_CONSTANT',
            'reason': 'Native GCN MRT0 RGB comes from exact zero material constants; sampled resources are controls/auxiliary output.',
        }
    return {
        'kind': 'NO_PORTABLE_PREVIEW', 'texture': None, 'base_factor': [0.5,0.5,0.5,1.0],
        'confidence': 'NONE', 'reason': f'No bounded Crota portable policy for PS {ps}.'
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-glb', type=Path, required=True)
    ap.add_argument('--stage-state', type=Path, required=True)
    ap.add_argument('--texture-manifest', type=Path, required=True)
    ap.add_argument('--texture-dir', type=Path, required=True)
    ap.add_argument('--gcn-usage', type=Path, required=True)
    ap.add_argument('--preview-mode', choices=('conservative','visible'), default='visible')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    stage = json.loads(a.stage_state.read_text())
    if stage.get('status') != 'D1_MATERIAL_STAGE_STATE_EXACT' or stage.get('violations'):
        raise SystemExit('material stage state is not exact')
    smats = {norm(k): v for k, v in (stage.get('materials') or {}).items()}
    if set(smats) != EXPECTED_MATERIALS:
        raise SystemExit(f'stage-state material set drift: {sorted(set(smats)^EXPECTED_MATERIALS)}')
    texman = json.loads(a.texture_manifest.read_text())
    texrows = texture_rows(texman)
    if not EXPECTED_TEXTURES <= set(texrows):
        raise SystemExit('exact Crota texture rows missing: ' + ','.join(sorted(EXPECTED_TEXTURES-set(texrows))))
    usage = ps_usage_map(json.loads(a.gcn_usage.read_text()))

    src, srcbin = read_glb(a.input_glb)
    doc = copy.deepcopy(src)
    mids = glb_materials(doc)
    if set(mids.values()) != EXPECTED_MATERIALS:
        raise SystemExit(f'GLB material set drift: {sorted(set(mids.values())^EXPECTED_MATERIALS)}')
    # Every primitive must already carry the exact promoted source UV before a portable
    # texture view is allowed.
    for mi, mesh in enumerate(doc.get('meshes', [])):
        prims = mesh.get('primitives') or []
        if len(prims) != 1 or 'TEXCOORD_0' not in (prims[0].get('attributes') or {}):
            raise SystemExit(f'mesh {mi}: exact TEXCOORD_0 absent before material binding')

    bindata = srcbin
    tex_indices = {}
    source_rows = []
    for tag in sorted(EXPECTED_TEXTURES):
        row = texrows[tag]
        pf = row['png_file']
        rel = Path(pf['path'])
        # Manifests store paths relative to texture_export/, while --texture-dir is
        # the extracted texture_export root in the R4 workflow.
        p = a.texture_dir / rel
        if not p.exists():
            # Also accept --texture-dir pointing directly at textures/.
            p = a.texture_dir / rel.name
        if not p.exists():
            raise FileNotFoundError(str(p))
        raw = p.read_bytes()
        if hashlib.sha256(raw).hexdigest() != pf['sha256']:
            raise SystemExit(f'{tag}: retail PNG SHA drift')
        bvi, bindata = append_blob(doc, bindata, raw, f'D1_CROTA_TEXTURE_{tag}_PNG')
        ii = len(doc.setdefault('images', []))
        hi = row.get('header_info') or {}
        doc['images'].append({
            'name': f'D1_TEXTURE_{tag}', 'mimeType': 'image/png', 'bufferView': bvi,
            'extras': {
                'd1_taghash': tag, 'd1_exact_retail_texture': True,
                'd1_format': row.get('format_name'), 'd1_width': hi.get('width'), 'd1_height': hi.get('height'),
                'd1_png_sha256': pf['sha256'], 'd1_backing_hash': row.get('backing_hash'),
                'd1_backing_sha256': row.get('backing_sha256'),
            },
        })
        ti = len(doc.setdefault('textures', []))
        doc['textures'].append({'name': f'D1_TEXTURE_{tag}', 'source': ii, 'extras': {'d1_taghash': tag, 'd1_exact_retail_texture': True}})
        tex_indices[tag] = ti
        source_rows.append({'texture': tag, 'image_index': ii, 'gltf_texture_index': ti, 'png_bytes': len(raw), 'png_sha256': pf['sha256'], 'format': row.get('format_name'), 'width': hi.get('width'), 'height': hi.get('height')})

    material_rows = []
    for mi, mh in sorted(mids.items()):
        r = smats[mh]
        ps = norm((r.get('ps') or {}).get('shader'))
        vs = norm((r.get('vs') or {}).get('shader'))
        bindings = [{'stage':'ps','t':int(x['texture_index']),'texture':norm(x['texture'])} for x in (r['ps']['textures']['items'] or [])]
        # This exact shader must consume exactly the declared immediate texture index
        # domain for the selected material. Repeated texture TagHashes at different t#
        # remain separate native binding edges.
        ur = usage.get(ps)
        if ur is None:
            raise SystemExit(f'{mh}: pixel shader {ps} absent from exact GCN usage closure')
        declared = sorted({x['t'] for x in bindings})
        used = [int(x) for x in ur.get('used_texture_indices', [])]
        if declared != used:
            raise SystemExit(f'{mh}/{ps}: material t# {declared} != GCN-used {used}')
        if int(ur.get('unmatched_image_instruction_count', -1)) != 0:
            raise SystemExit(f'{mh}/{ps}: unmatched GCN image instruction')
        preview = direct_preview(mh, ps, r, a.preview_mode)
        m = doc['materials'][mi]
        ex = m.setdefault('extras', {})
        ex.update({
            'd1_material_taghash': mh,
            'd1_vertex_shader': vs,
            'd1_pixel_shader': ps,
            'd1_material_state4_hex': r.get('material_state4_hex'),
            'd1_native_texture_bindings': [{**b, 'gltf_texture_index': tex_indices[b['texture']]} for b in bindings],
            'd1_native_gcn_image_instruction_count': int(ur.get('image_instruction_count', 0)),
            'd1_native_gcn_used_texture_indices': used,
            'd1_tfx_bytecode_hex': (r['ps'].get('tfx_bytecode') or {}).get('bytes_hex'),
            'd1_tfx_program_sha256': r['ps'].get('tfx_program_sha256'),
            'd1_ps_private_constants': (r['ps'].get('tfx_private_constants') or {}).get('items'),
            'd1_ps_cbuffers': (r['ps'].get('cbuffers') or {}).get('items'),
            'd1_blender_preview': preview,
            'd1_native_shader_authoritative': True,
        })
        pbr = m.setdefault('pbrMetallicRoughness', {})
        pbr['metallicFactor'] = 0.0
        pbr['roughnessFactor'] = 1.0
        pbr['baseColorFactor'] = preview['base_factor']
        if preview['texture']:
            pbr['baseColorTexture'] = {'index': tex_indices[preview['texture']], 'texCoord': 0}
        else:
            pbr.pop('baseColorTexture', None)
        m['alphaMode'] = 'OPAQUE'
        material_rows.append({'material_index': mi, 'material': mh, 'vertex_shader': vs, 'pixel_shader': ps, 'native_bindings': bindings, 'preview': preview})

    doc.setdefault('asset', {}).setdefault('extras', {})['d1CrotaMaterialLayer'] = {
        'schema': 'd1_gltf_bind_crota_blender_materials/v1',
        'entity': '8108E484', 'entityName': 'Crota, Son of Oryx', 'model': '8108E5B7',
        'exactTextureCount': len(EXPECTED_TEXTURES),
        'materialCount': len(EXPECTED_MATERIALS),
        'previewMode': a.preview_mode,
        'nativeShaderMetadataAuthoritative': True,
        'portablePbrIsPreviewOnly': True,
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    write_glb(a.out, doc, bindata)
    chk, chkbin = read_glb(a.out)
    if chkbin[:len(srcbin)] != srcbin:
        raise SystemExit('input binary chunk is not exact output prefix')
    for key in ('accessors','meshes','nodes','skins','animations','scenes'):
        if chk.get(key, []) != src.get(key, []):
            raise SystemExit(f'{key} changed while binding Crota materials')
    if len(chk.get('images') or []) != len(src.get('images') or []) + 5:
        raise SystemExit('embedded image count drift')
    if len(chk.get('textures') or []) != len(src.get('textures') or []) + 5:
        raise SystemExit('embedded texture count drift')

    report = {
        'schema': 'd1_gltf_bind_crota_blender_materials/v1',
        'status': 'D1_CROTA_EXACT_TEXTURE_RESOURCES_AND_BLENDER_PREVIEW_COMPLETE',
        'preview_mode': a.preview_mode,
        'input_glb': str(a.input_glb), 'input_sha256': hfile(a.input_glb),
        'output_glb': str(a.out), 'output_sha256': hfile(a.out), 'output_bytes': a.out.stat().st_size,
        'material_count': len(material_rows), 'materials': material_rows,
        'exact_texture_count': len(source_rows), 'textures': source_rows,
        'geometry_skin_animation_scene_unchanged': True,
        'input_binary_prefix_exact': True,
        'policy': (
            'Native D1 material/shader/t# relationships and exact retail texture resources are authoritative and embedded. '
            'Portable glTF PBR assignments exist only so Blender shows a useful preview; each preview records its own '
            'evidence strength and any approximation explicitly.'
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('status','preview_mode','material_count','exact_texture_count','output_bytes','output_sha256')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
