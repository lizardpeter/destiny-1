#!/usr/bin/env python3
"""Build a compact exact-input manifest for the Tower 809DCD66 Blender adapter.

Consumes the already closed material-vector report and exact world texture
manifest. No source semantic is inferred here: the manifest merely serializes the
native inputs needed to construct a Blender node graph for VS 80CA0DDA / PS
809DCD66.

Dynamic TFX materials are evaluated at abstract native ``Frame[0] = 0``. That
sample is exact for zero regardless of the still-unresolved Frame[0] time unit;
future animation must keep the frame unit/phase explicit rather than mapping it
to Blender seconds by guesswork.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_tower_809dcd66_tfx_eval import (
    PREFIX,
    bytecode_hex,
    cbuffer_vectors,
    constant_vectors,
    eval_program,
    symbolic_x,
)

VS = '80CA0DDA'
PS = '809DCD66'
T0 = '8093E9A3'
T1 = '8093E9A2'


def norm(h) -> str:
    return str(h).upper().removeprefix('0X').zfill(8)


def material_rows(doc: dict) -> dict[str, dict]:
    m = doc.get('materials') or {}
    if isinstance(m, dict):
        return {norm(k): v for k, v in m.items()}
    return {norm(r['material']): r for r in m}


def vec(v):
    return [float(x) for x in v]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--constants', type=Path, required=True)
    ap.add_argument('--texture-manifest', type=Path, required=True)
    ap.add_argument('--roles', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    const_doc = json.loads(a.constants.read_text())
    tex_doc = json.loads(a.texture_manifest.read_text())
    role_doc = json.loads(a.roles.read_text())
    rows = material_rows(const_doc)
    roles = {norm(k): v for k, v in (role_doc.get('materials') or {}).items()}
    tex = {norm(k): v for k, v in (tex_doc.get('textures') or {}).items()}
    world_mats = {norm(k): v for k, v in (tex_doc.get('materials') or {}).items()}

    selected = {
        h: r for h, r in rows.items()
        if norm(r.get('vertex_shader')) == VS and norm(r.get('pixel_shader')) == PS
    }
    if len(selected) != 24:
        raise SystemExit(f'expected 24 exact target materials, got {len(selected)}')
    if T0 not in tex or T1 not in tex:
        raise SystemExit('exact target textures missing from texture manifest')

    materials = {}
    static_count = dynamic_count = 0
    for h, r in sorted(selected.items()):
        cbuf = cbuffer_vectors(r)
        if len(cbuf) != 7:
            raise ValueError(f'{h}: expected 7 cbuffer vectors, got {len(cbuf)}')
        consts = constant_vectors(r)
        raw = bytes.fromhex(bytecode_hex(r))
        c6_frame0 = float(eval_program(raw, consts, cbuf, 0.0)[0])
        if raw == PREFIX:
            mode = 'static_serialized'
            expr = 'serialized_c6.x'
            static_count += 1
        else:
            mode = 'dynamic_tfx_frame0_abstract'
            expr = symbolic_x(raw, consts)
            dynamic_count += 1

        bindings = sorted(
            ((int(x['texture_index']), norm(x['texture'])) for x in r.get('ps_texture_tags', [])),
            key=lambda x: x[0]
        )
        if bindings != [(0, T0), (1, T1)]:
            raise ValueError(f'{h}: target texture binding changed: {bindings}')

        wm = world_mats.get(h) or {}
        ps_samp = ((wm.get('samplers') or {}).get('ps') or {}).get('items') or []
        sampler_by_index = {int(x['index']): norm(x['first_dword_hex']) for x in ps_samp}
        if sampler_by_index.get(0) != '80AAE177' or sampler_by_index.get(1) != '80AAE176':
            raise ValueError(f'{h}: sampler binding changed: {sampler_by_index}')

        rr = roles.get(h) or {}
        rb = {int(x['texture_index']): x for x in rr.get('bindings', [])}
        if norm(rb.get(0, {}).get('texture')) != T0 or norm(rb.get(1, {}).get('texture')) != T1:
            raise ValueError(f'{h}: shader-role inventory missing exact t0/t1')

        materials[h] = {
            'material': h,
            'vertex_shader': VS,
            'pixel_shader': PS,
            'c2_palette_base': vec(cbuf[2]),
            'c3_palette_delta': vec(cbuf[3]),
            'c4': vec(cbuf[4]),
            'c4_x_parallax': float(cbuf[4][0]),
            'c5_rgb_multiplier': vec(cbuf[5]),
            'serialized_c6': vec(cbuf[6]),
            'c6_mode': mode,
            'c6_x_at_abstract_frame0_zero': c6_frame0,
            'tfx_expression_x': expr,
            'tfx_private_constants': [vec(x) for x in consts],
            'tfx_bytecode_hex': raw.hex(),
            'texture_bindings': {
                't0': {
                    'taghash': T0,
                    'sampler': '80AAE177',
                    'portable_png': tex[T0].get('png'),
                    'format': tex[T0].get('format_name'),
                    'native_colorspace_hint': tex[T0].get('native_colorspace_hint'),
                    'proven_channel': 'R',
                    'proven_role': rb[0].get('proven_role'),
                },
                't1': {
                    'taghash': T1,
                    'sampler': '80AAE176',
                    'portable_png': tex[T1].get('png'),
                    'format': tex[T1].get('format_name'),
                    'native_colorspace_hint': tex[T1].get('native_colorspace_hint'),
                    'proven_channel': 'R',
                    'proven_role': rb[1].get('proven_role'),
                },
            },
        }

    out = {
        'schema_version': 1,
        'status': 'D1_TOWER_809DCD66_BLENDER_ADAPTER_INPUTS_CLOSED',
        'material_count': len(materials),
        'static_material_count': static_count,
        'dynamic_material_count': dynamic_count,
        'vertex_shader': VS,
        'pixel_shader': PS,
        'required_mesh_attributes': ['_D1_NORMAL', '_D1_TANGENT_XYZ', '_D1_TANGENT_W'],
        'forensic_mesh_attribute_retained': '_D1_TANGENT',
        'native_basis': {
            'Nraw': 'ObjectToWorldVector(_D1_NORMAL)',
            'Traw': 'ObjectToWorldVector(_D1_TANGENT_XYZ)',
            'invN': '1/length(Nraw)',
            'N': 'Nraw*invN',
            'T': 'Traw*invN',
            'B': 'cross(N,T)*_D1_TANGENT_W',
        },
        'portable_uv': {
            'relation': 'portable=(native_u,1-native_v)',
            'base_sample_t0': 'sample portable TEXCOORD_0',
            'native_displacement': 'du=-c4.x*dot(V,T)/dot(V,N); dv=-c4.x*dot(V,B)/dot(V,N)',
            'portable_displaced_t1': 'portable_uv2=(portable_u+du, portable_v-dv)',
        },
        'pixel_rgb': 'rgb=(c2.rgb+c3.rgb*saturate(t0.r))*t1.r*c5.rgb*c6.x*api13[6]*api13[7]',
        'global_inputs': {
            'api13_dword6': {'engine_name': None, 'runtime_source': None, 'preview_fallback': 1.0},
            'api13_dword7': {'engine_name': None, 'runtime_source': None, 'preview_fallback': 1.0},
        },
        'render_state': {
            'native_alpha_output': 0.0,
            'native_blend_composition_state': None,
            'blender_preview_output': 'Emission RGB; not promoted as native blend semantics',
        },
        'dynamic_time': {
            'extern': 'Frame[0]',
            'unit': None,
            'phase': None,
            'initial_sample_rule': 'Frame[0]=0 only; exact zero sample does not require a time-unit guess',
        },
        'textures': {
            T0: {k: tex[T0].get(k) for k in ('png', 'format_name', 'header_info', 'native_colorspace_hint')},
            T1: {k: tex[T1].get(k) for k in ('png', 'format_name', 'header_info', 'native_colorspace_hint')},
        },
        'materials': materials,
        'policy': (
            'This manifest contains exact closed native equations and material inputs plus explicitly labeled preview fallbacks. '
            'api13 runtime values, render/blend state, and Frame[0] unit/phase remain unresolved and are never renamed or inferred.'
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'],
        'material_count': out['material_count'],
        'static_material_count': out['static_material_count'],
        'dynamic_material_count': out['dynamic_material_count'],
        't0': out['textures'][T0],
        't1': out['textures'][T1],
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
