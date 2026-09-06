#!/usr/bin/env python3
"""Classify the retail 809DCD66 tangent audit for Blender replay.

The native VS does *not* independently normalize its tangent. It transforms the
source normal and tangent by the same object 3x3, computes one reciprocal length
from transformed N, applies that reciprocal to both N and T, then constructs::

    B = cross(N, T) * source_tangent_w

That distinction matters for the measured Tower fixtures because their transforms
are slightly non-uniform. A generic glTF tangent path is therefore not the proof-
preserving adapter. Blender can still replay the shader exactly at semantic level
if the source normal, tangent XYZ, and tangent W are retained as custom attributes
and transformed explicitly as ordinary vectors.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--audit', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    d = json.loads(a.audit.read_text())
    g = d['promotion_gates']

    required = {
        'tangent_w_exact_signs': bool(g['tangent_w_is_glTF_sign_compatible']),
        'triangle_handedness_consistent': bool(g['every_triangle_has_uniform_tangent_w']),
        'instance_transforms_nonsingular': int(d['zero_determinant_placements']) == 0,
        'native_normal_semantic_unit': bool(g['native_normal_is_unit_within_1e_5']),
        'portable_uv_relation_closed': bool(g['portable_uv_v_flip_exact_within_2e_6']),
        'portable_parallax_relation_closed': bool(g['portable_parallax_y_sign_flip_exact_within_3e_6']),
    }
    failed = [k for k, v in required.items() if not v]

    # These are intentionally *not* required for the explicit native-basis path.
    # Their measured failure is why a standard tangent-space promotion is rejected.
    uniform_scale = bool(g['instance_scales_are_uniform_within_1e_5'])
    native_tangent_unit = bool(g['native_tangent_is_unit_within_1e_5'])
    standard_tangent_safe = uniform_scale and native_tangent_unit

    out = {
        'schema_version': 1,
        'status': 'D1_TOWER_809DCD66_BLENDER_EXPLICIT_BASIS_READY' if not failed else 'D1_TOWER_809DCD66_BLENDER_EXPLICIT_BASIS_BLOCKED',
        'source_audit_status': d.get('status'),
        'required_gates': required,
        'failed_required_gates': failed,
        'standard_gltf_tangent_promotion_safe': standard_tangent_safe,
        'standard_gltf_tangent_rejection_reasons': [
            x for x, cond in (
                ('retail instance transforms include measurable non-uniform scale', not uniform_scale),
                ('native VS tangent is not unit after its shared normal reciprocal-length scaling', not native_tangent_unit),
                ('portable TEXCOORD_0 flips V relative to native shader UV; native parallax Y must be sign-converted', True),
            ) if cond
        ],
        'required_custom_attributes': {
            '_D1_NORMAL': 'source packed normal xyz after SNORM decode, before instance transform',
            '_D1_TANGENT_XYZ': 'source packed tangent xyz after SNORM decode, before instance transform',
            '_D1_TANGENT_W': 'exact source handedness sign; measured only -1 or +1',
            '_D1_TANGENT': 'full forensic xyzw preservation; retained in addition to split Blender-facing fields',
        },
        'blender_native_basis_equation': [
            'Nraw = VectorTransform(Object->World, _D1_NORMAL, as ordinary VECTOR)',
            'Traw = VectorTransform(Object->World, _D1_TANGENT_XYZ, as ordinary VECTOR)',
            'invN = 1 / length(Nraw)',
            'N = Nraw * invN',
            'T = Traw * invN',
            'B = cross(N,T) * _D1_TANGENT_W',
        ],
        'portable_uv_equation': {
            'base': 'portable_uv = (native_u, 1-native_v)',
            'displaced': 'portable_uv2 = (portable_u + native_du, portable_v - native_dv)',
        },
        'measured': {
            'raw_tangent_w_counts': d['raw_tangent_w_counts'],
            'mixed_handedness_triangle_count': d['mixed_handedness_triangle_count'],
            'max_uniform_scale_spread': d['max_uniform_scale_spread'],
            'native_tangent_length': d['tangent_length_stats_after_native_vs'],
            'portable_uv_max_abs_error': d['portable_uv_max_abs_error'],
            'portable_parallax_max_abs_error': d['portable_parallax_max_abs_error'],
        },
        'policy': (
            'Do not map this D1 basis to standard glTF TANGENT for the faithful Blender adapter. '
            'Carry native source N/T/W explicitly and replay the vertex-shader basis arithmetic in nodes.'
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))
    return 0 if not failed else 2


if __name__ == '__main__':
    raise SystemExit(main())
