#!/usr/bin/env python3
"""Apply conservative D1 source semantics to a GLB without touching BIN data.

Two corrections are made:

1. Standard glTF ``COLOR_0`` is demoted to application-specific ``_D1_COLOR``.
   The accessor and binary bytes are unchanged.  D1's serialized RGBA field is a
   shader input whose role can be color, blend weight, mask/control data, or other
   per-vertex state depending on the native shader.  It must not be allowed to
   silently multiply generic glTF PBR base color before that shader-specific role
   is proven.

2. Material alpha class is populated from the exact D1 +0x20 render-state census.
   ``Unk20 == 0`` maps to portable OPAQUE; ``Unk20 != 0`` maps to portable BLEND.
   The exact native equation is retained only when independently closed (currently
   low selector 0x88 -> state 8).  No missing alpha texture or shader composition
   is invented.

This is a portable adapter, not the authoritative renderer.  The source metadata
stored in extras is intended to be consumed by Blender tooling and the Rust engine.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

from d1_gltf_layer_merge import read_glb, write_glb

MAT_RE = re.compile(r'(?:TigerMaterial_|D1_)([0-9A-Fa-f]{8})')


def hfile(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(8 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-glb', type=Path, required=True)
    ap.add_argument('--render-state', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    census = json.loads(a.render_state.read_text())
    if census.get('status') != 'D1_MATERIAL_RENDER_STATE_CENSUS_COMPLETE' or census.get('violations'):
        raise SystemExit('render-state census is not fully closed')
    states = {str(x['material']).upper(): x for x in census.get('materials') or []}
    if len(states) != int(census.get('resolved_material_count', -1)):
        raise SystemExit('render-state material identity/count drift')

    src, srcbin = read_glb(a.input_glb)
    doc = copy.deepcopy(src)

    # Lossless semantic demotion: accessor identity and BIN bytes remain unchanged.
    renamed = []
    color0_remaining = []
    for mi, mesh in enumerate(doc.get('meshes') or []):
        for pi, prim in enumerate(mesh.get('primitives') or []):
            attrs = prim.setdefault('attributes', {})
            if 'COLOR_0' not in attrs:
                continue
            if '_D1_COLOR' in attrs:
                raise SystemExit(f'mesh {mi} primitive {pi} already contains _D1_COLOR')
            accessor = attrs.pop('COLOR_0')
            attrs['_D1_COLOR'] = accessor
            renamed.append({'mesh': mi, 'primitive': pi, 'accessor': accessor, 'material_index': prim.get('material')})

    for mi, mesh in enumerate(doc.get('meshes') or []):
        for pi, prim in enumerate(mesh.get('primitives') or []):
            if 'COLOR_0' in (prim.get('attributes') or {}):
                color0_remaining.append([mi, pi])
    if color0_remaining:
        raise SystemExit(f'COLOR_0 remains after demotion: {color0_remaining[:8]}')

    material_rows = []
    seen = set()
    unresolved_named = []
    for i, mat in enumerate(doc.get('materials') or []):
        name = str(mat.get('name') or '')
        mm = MAT_RE.search(name)
        if not mm:
            continue
        h = mm.group(1).upper()
        state = states.get(h)
        if state is None:
            unresolved_named.append({'material_index': i, 'material': h, 'name': name})
            continue
        seen.add(h)
        alpha = state['portable_alpha_class']
        if alpha not in ('OPAQUE', 'BLEND'):
            raise SystemExit(f'{h}: invalid portable alpha class {alpha!r}')
        mat['alphaMode'] = alpha
        ex = mat.setdefault('extras', {})
        ex.update({
            'd1_material_taghash': h,
            'd1_source_render_state': {
                'unk20_raw_u16': state['unk20_raw_u16'],
                'unk20_hex': state['unk20_hex'],
                'unk20_low_u8': state['unk20_low_u8'],
                'unk20_low_hex': state['unk20_low_hex'],
                'unk20_high_u8': state['unk20_high_u8'],
                'transparent_draw_population': state['transparent_draw_population'],
                'exact_blend_state_known': state['exact_blend_state_known'],
                'exact_blend_state_index': state['exact_blend_state_index'],
                'exact_blend_equation': state['exact_blend_equation'],
            },
            'd1_portable_alpha_adapter': {
                'alphaMode': alpha,
                'classification_source': 'D1 Material +0x20 native draw population',
                'native_equation_not_implied_when_unknown': True,
            },
        })
        material_rows.append({
            'material_index': i,
            'material': h,
            'alpha_mode': alpha,
            'unk20_hex': state['unk20_hex'],
            'exact_blend_state_known': state['exact_blend_state_known'],
        })

    if unresolved_named:
        raise SystemExit(f'D1-named GLB materials absent from render-state census: {unresolved_named[:8]}')
    missing = sorted(set(states) - seen)
    if missing:
        raise SystemExit(f'render-state materials absent from GLB: {missing[:8]}')

    doc.setdefault('asset', {}).setdefault('extras', {})['d1SourceSemanticsAdapter'] = {
        'schema': 'd1_gltf_source_semantics_adapter/v1',
        'sourceColorAttribute': '_D1_COLOR',
        'demotedStandardColor0PrimitiveCount': len(renamed),
        'materialRenderStateCount': len(material_rows),
        'policy': 'D1 source shader inputs remain canonical. Generic glTF color/alpha semantics are exposed only where source-backed; shader-specific composition remains separate.',
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    write_glb(a.out, doc, srcbin)
    chk, chkbin = read_glb(a.out)
    if chkbin != srcbin:
        raise SystemExit('GLB BIN payload changed')
    for key in ('accessors','bufferViews','images','textures','nodes','skins','animations','scenes'):
        if chk.get(key, []) != src.get(key, []):
            raise SystemExit(f'{key} changed unexpectedly')

    opaque = sum(x['alpha_mode'] == 'OPAQUE' for x in material_rows)
    blend = sum(x['alpha_mode'] == 'BLEND' for x in material_rows)
    rep = {
        'schema_version': 1,
        'status': 'D1_GLTF_SOURCE_SEMANTICS_ADAPTER_COMPLETE',
        'input_glb': str(a.input_glb),
        'input_bytes': a.input_glb.stat().st_size,
        'input_sha256': hfile(a.input_glb),
        'output_glb': str(a.out),
        'output_bytes': a.out.stat().st_size,
        'output_sha256': hfile(a.out),
        'bin_byte_identical': True,
        'demoted_color0_primitive_count': len(renamed),
        'remaining_color0_primitive_count': 0,
        'd1_material_count': len(material_rows),
        'opaque_material_count': opaque,
        'blend_material_count': blend,
        'known_exact_blend_material_count': sum(x['exact_blend_state_known'] for x in material_rows),
        'color_changes': renamed,
        'materials': material_rows,
        'proof_boundary': 'Vertex RGBA source data and material +0x20 state are preserved/classified exactly. Native shader evaluation, alpha-source composition, sampler behavior, terrain dyemap equations, sky shader behavior, and unknown blend equations are not invented by this adapter.',
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(rep, indent=2) + '\n')
    print(json.dumps({k: rep[k] for k in (
        'status','input_bytes','output_bytes','bin_byte_identical',
        'demoted_color0_primitive_count','d1_material_count','opaque_material_count',
        'blend_material_count','known_exact_blend_material_count','output_sha256')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
