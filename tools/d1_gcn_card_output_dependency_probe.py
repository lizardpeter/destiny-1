#!/usr/bin/env python3
"""Prove the exact output dependency shape of the Tower 80CA0B97 card shaders.

This probe is deliberately narrow and instruction-derived. It consumes the already
source-closed CLRX disassemblies and exact Sony resource-usage report for PS
80B9E8CF/80B9E8D0. It does not assign a game-facing blend mode. It proves only the
native shader facts needed to reject an opaque/base-color portable interpretation:

* material t0.x and t1.x are sampled as scalar channels and multiplied together;
* that product multiplicatively feeds the scalar packed into MRT0 alpha;
* 80B9E8CF's RGB lanes are all multiplied by that same final alpha scalar before
  fp16 packing (premultiplied-output structure);
* 80B9E8D0 explicitly zeros RGB and exports only the scalar in alpha.

No texture semantic name (opacity, cloud, noise, etc.) is inferred here.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TARGETS = ('80B9E8CF', '80B9E8D0')


def normalized_lines(path: Path) -> list[str]:
    return [re.sub(r'\s+', ' ', x.strip()) for x in path.read_text(errors='replace').splitlines() if x.strip()]


def finds(lines: list[str], needle: str) -> list[int]:
    return [i for i, x in enumerate(lines) if needle in x]


def find(lines: list[str], needle: str) -> int:
    hits = finds(lines, needle)
    if len(hits) != 1:
        raise ValueError(f'{needle!r}: expected one exact instruction hit, got {len(hits)}')
    return hits[0]


def find_first_after(lines: list[str], needle: str, after: int) -> int:
    hits = [i for i in finds(lines, needle) if i > after]
    if not hits:
        raise ValueError(f'{needle!r}: no instruction after line-index {after}')
    return hits[0]


def find_last_after(lines: list[str], needle: str, after: int) -> int:
    hits = [i for i in finds(lines, needle) if i > after]
    if not hits:
        raise ValueError(f'{needle!r}: no instruction after line-index {after}')
    return hits[-1]


def assert_order(indices: list[int], label: str) -> None:
    if indices != sorted(indices) or len(set(indices)) != len(indices):
        raise ValueError(f'{label}: instruction order drift {indices}')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--image-usage', type=Path, required=True)
    ap.add_argument('--disasm-dir', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    usage = json.loads(a.image_usage.read_text())
    if usage.get('status') != 'D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':
        raise SystemExit('image usage is not exact')
    by = {str(x['shader']).upper(): x for x in usage.get('shaders', [])}
    violations = []
    rows = []

    for shader in TARGETS:
        try:
            u = by[shader]
            if u.get('unmatched_image_instruction_count') != 0:
                raise ValueError('unmatched image instructions')
            inst = u.get('instructions', [])
            samples = {}
            load_t10 = None
            for x in inst:
                tex = [int(r['texture_index']) for r in x.get('resources', [])]
                if x['opcode'] == 'image_sample' and len(tex) == 1:
                    samples[tex[0]] = x
                if x['opcode'] == 'image_load_mip' and tex == [10]:
                    load_t10 = x
            if sorted(samples) != [0, 1] or load_t10 is None:
                raise ValueError(f'image resource shape drift samples={sorted(samples)} t10={load_t10 is not None}')
            if samples[0].get('dmask_channels') != 'x' or samples[1].get('dmask_channels') != 'x':
                raise ValueError('t0/t1 are no longer scalar x samples')

            lines = normalized_lines(a.disasm_dir / f'PS_{shader}.s')
            # Exact register destinations are source-proven by the image usage report.
            s0 = find(lines, 'image_sample v3, v[4:7], s[4:11], s[12:15]')
            s1 = find(lines, 'image_sample v4, v[7:10], s[44:51], s[32:35]')
            # 80B9E8CF reuses the same textual v3=v3*v4 form later for final B*alpha.
            # The t0*t1 product is the first occurrence after both image samples.
            mul_tex = find_first_after(lines, 'v_mul_f32 v3, v3, v4', max(s0, s1))
            mul_alpha = find_first_after(lines, 'v_mul_f32 v0, v3, v0', mul_tex)
            if not (s0 < mul_tex and s1 < mul_tex < mul_alpha):
                raise ValueError('t0/t1 product no longer feeds final scalar chain')

            if shader == '80B9E8CF':
                # v0 is the final scalar after both post-texture clamp/mask stages and scalar cbuffer multipliers.
                a0 = find_first_after(lines, 'v_mul_f32 v0, s0, v0', mul_alpha)
                a1 = find_first_after(lines, 'v_mul_f32 v0, s1, v0', a0)
                rgb_alpha0 = find_first_after(lines, 'v_mul_f32 v4, s5, v0', a1)
                rgb_alpha1 = find_first_after(lines, 'v_mul_f32 v4, s4, v4', rgb_alpha0)
                r = find_first_after(lines, 'v_mul_f32 v1, v1, v4', rgb_alpha1)
                g = find_first_after(lines, 'v_mul_f32 v2, v2, v4', r)
                b = find_last_after(lines, 'v_mul_f32 v3, v3, v4', g)
                pack_rg = find_first_after(lines, 'v_cvt_pkrtz_f16_f32 v1, v1, v2', b)
                pack_ba = find_first_after(lines, 'v_cvt_pkrtz_f16_f32 v0, v3, v0', pack_rg)
                exp = find_first_after(lines, 'exp mrt0, v1, v1, v0, v0 done compr vm', pack_ba)
                assert_order([mul_tex, mul_alpha, a0, a1, rgb_alpha0, rgb_alpha1, r, g, b, pack_rg, pack_ba, exp], '80B9E8CF output chain')
                structure = {
                    'mrt0_r': 'SOURCE_RGB_COEFFICIENT_R * FINAL_ALPHA_SCALAR',
                    'mrt0_g': 'SOURCE_RGB_COEFFICIENT_G * FINAL_ALPHA_SCALAR',
                    'mrt0_b': 'SOURCE_RGB_COEFFICIENT_B * FINAL_ALPHA_SCALAR',
                    'mrt0_a': 'FINAL_ALPHA_SCALAR',
                    'rgb_structure': 'PREMULTIPLIED_BY_FINAL_ALPHA_SCALAR',
                }
            else:
                a0 = find_first_after(lines, 'v_mul_f32 v0, s0, v0', mul_alpha)
                a1 = find_first_after(lines, 'v_mul_f32 v0, s1, v0', a0)
                zero = find_first_after(lines, 'v_mov_b32 v1, 0', a1)
                pack_rg = find_first_after(lines, 'v_cvt_pkrtz_f16_f32 v2, v1, v1', zero)
                pack_ba = find_first_after(lines, 'v_cvt_pkrtz_f16_f32 v0, v1, v0', pack_rg)
                exp = find_first_after(lines, 'exp mrt0, v2, v2, v0, v0 done compr vm', pack_ba)
                assert_order([mul_tex, mul_alpha, a0, a1, zero, pack_rg, pack_ba, exp], '80B9E8D0 output chain')
                structure = {
                    'mrt0_r': '0', 'mrt0_g': '0', 'mrt0_b': '0',
                    'mrt0_a': 'FINAL_ALPHA_SCALAR',
                    'rgb_structure': 'EXPLICIT_ZERO',
                }

            rows.append({
                'shader': shader,
                'material_texture_sample_roles': {
                    't0': 'SCALAR_X_SAMPLE_FEEDS_T0_TIMES_T1_PRODUCT',
                    't1': 'SCALAR_X_SAMPLE_FEEDS_T0_TIMES_T1_PRODUCT',
                },
                't0_times_t1_product_feeds_final_alpha_scalar': True,
                'output_structure': structure,
                'blend_mode_semantic': 'WITHHELD',
                'texture_role_semantics': {'t0': 'WITHHELD', 't1': 'WITHHELD'},
            })
        except Exception as ex:
            violations.append(f'{shader}:{ex!r}')

    out = {
        'schema_version': 1,
        'status': 'D1_80CA0B97_CARD_GCN_OUTPUT_DEPENDENCY_PROVEN' if len(rows) == 2 and not violations else 'D1_80CA0B97_CARD_GCN_OUTPUT_DEPENDENCY_PARTIAL',
        'model': '80CA0B97',
        'materials': {'80B9E8C2': '80B9E8CF', '80B9E8C3': '80B9E8D0'},
        'shader_count': len(rows),
        'shaders': rows,
        'portable_rendering_consequence': (
            'These shaders cannot be represented faithfully as ordinary opaque base-color card materials. '
            'The exact native PS path computes a scalar from both material texture samples and exports it in MRT0 alpha; '
            'one shader premultiplies RGB by the same scalar and the other exports zero RGB.'
        ) if not violations else 'WITHHELD',
        'blend_mode_semantic': 'WITHHELD',
        'violations': violations,
        'policy': (
            'Only exact GCN instruction dataflow and Sony resource provenance are promoted. '
            'No game-facing blend/cutout/additive semantic and no human texture-role name is assigned.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in ('status','shader_count','portable_rendering_consequence','blend_mode_semantic','violations')}, indent=2))
    return 0 if not violations and len(rows) == 2 else 2


if __name__ == '__main__':
    raise SystemExit(main())
