#!/usr/bin/env python3
"""Prove D1 map-light volume/Buffer2 invariants from exact retail records.

This is deliberately a mathematical proof layer, not a Blender light classifier.
It uses the exact 0x90 LightData bytes, source-paired BufferData, and source-proven
SMaterial_ROI manifest to establish:

* LightData +0x20..+0x5F forms a four-Vec4 volume transform block.
* Two structural populations exist in the Tower corpus:
  - affine-volume records whose fourth stored vector is [0,0,0,1];
  - projective-volume records with a distinct projective form.
* For every affine-volume record, the spatial norms of stored rows +0x30 and +0x40
  equal Buffer2[1].y exactly within float tolerance.
* For every projective-volume record, abs(+0x20.y) and abs(+0x30.z) equal
  tan(Buffer2[1].w), while +0x40.w/+0x50.w encode Buffer2[1].y through the exact
  reciprocal identities documented below.
* Pixel-shader families do not cross the affine/projective structural split.

The semantic labels "point", "spot", "intensity" and "inner cone" remain withheld.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
from collections import Counter, defaultdict
from pathlib import Path

TOL = 1e-5


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def vec4s8(raw: bytes) -> list[list[float]]:
    return [list(struct.unpack_from('<4f', raw, i * 0x10)) for i in range(8)]


def row_norm3(v: list[float]) -> float:
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])


def close(a: float, b: float, tol: float = TOL) -> bool:
    return math.isfinite(a) and math.isfinite(b) and abs(a - b) <= tol


def kind(v: list[list[float]]) -> str:
    last = v[5]  # LightData +0x50, fourth Vec4 in +0x20..+0x5F block
    if max(abs(last[i]) for i in range(3)) <= TOL and close(last[3], 1.0):
        return 'AFFINE_VOLUME'
    return 'PROJECTIVE_VOLUME'


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--lighting-census', type=Path, required=True)
    ap.add_argument('--semantic-probe', type=Path, required=True)
    ap.add_argument('--material-manifest', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    lighting = json.loads(a.lighting_census.read_text())
    sem = json.loads(a.semantic_probe.read_text())
    mats = json.loads(a.material_manifest.read_text())
    if lighting.get('status') != 'D1_WORLD_MAP_LIGHTING_CENSUS_COMPLETE':
        raise SystemExit('lighting census incomplete')
    if sem.get('status') != 'D1_WORLD_MAP_LIGHT_SEMANTIC_PROBE_COMPLETE':
        raise SystemExit('semantic probe incomplete')
    if mats.get('status') != 'D1_WORLD_LIGHT_MATERIAL_MANIFEST_COMPLETE':
        raise SystemExit('light material manifest incomplete')

    buffers = {norm(x['hash']): x for x in lighting['light_buffers']}
    raw_by = {}
    for col in lighting['light_collections']:
        for r in col['lights']:
            raw_by[(norm(col['hash']), int(r['index']))] = bytes.fromhex(r['record_hex'])

    counts = Counter()
    violations = []
    records = []
    ps_kinds: dict[str, Counter] = defaultdict(Counter)
    affine_exact_y = affine_exact_z = 0
    projective_tan_y = projective_tan_z = 0
    projective_recip_sum = projective_recip_diff = 0

    for inst in sem['light_instances']:
        key = (norm(inst['collection_hash']), int(inst['index']))
        raw = raw_by[key]
        if len(raw) != 0x90:
            violations.append(f'{key}:record_size:{len(raw)}')
            continue
        v = vec4s8(raw)
        k = kind(v)
        counts[k] += 1
        bh = norm(inst['buffer_data'])
        b2 = buffers[bh]['buffer2']
        if len(b2) != 8:
            violations.append(f'{key}:buffer2_count:{len(b2)}')
            continue
        p = b2[1]
        material = norm(inst['candidate_ref80']['hash'])
        ps = norm(mats['materials'][material]['pixel_shader'])
        ps_kinds[ps][k] += 1

        proof = {}
        if k == 'AFFINE_VOLUME':
            y_ok = close(row_norm3(v[3]), p[1])
            z_ok = close(row_norm3(v[4]), p[1])
            affine_exact_y += int(y_ok)
            affine_exact_z += int(z_ok)
            if not (y_ok and z_ok):
                violations.append(f'{key}:affine_range_invariant')
            proof = {
                'buffer2_1_y': p[1],
                'row_0x30_spatial_norm': row_norm3(v[3]),
                'row_0x40_spatial_norm': row_norm3(v[4]),
                'range_invariant_y': y_ok,
                'range_invariant_z': z_ok,
                'row_0x20_spatial_norm': row_norm3(v[2]),
            }
        else:
            if p[1] == 0:
                violations.append(f'{key}:projective_zero_range_parameter')
                continue
            target_tan = math.tan(p[3])
            ty = close(abs(v[2][1]), target_tan)
            tz = close(abs(v[3][2]), target_tan)
            rs = close(v[5][3] + v[4][3], 1.0 / p[1])
            rd = close(v[5][3] - v[4][3], 100.0 / p[1])
            projective_tan_y += int(ty)
            projective_tan_z += int(tz)
            projective_recip_sum += int(rs)
            projective_recip_diff += int(rd)
            if not (ty and tz and rs and rd):
                violations.append(f'{key}:projective_volume_invariant')
            proof = {
                'buffer2_1_y': p[1],
                'buffer2_1_w': p[3],
                'tan_buffer2_1_w': target_tan,
                'abs_row_0x20_y': abs(v[2][1]),
                'abs_row_0x30_z': abs(v[3][2]),
                'row_0x50_w_plus_row_0x40_w': v[5][3] + v[4][3],
                'reciprocal_buffer2_1_y': 1.0 / p[1],
                'row_0x50_w_minus_row_0x40_w': v[5][3] - v[4][3],
                'hundred_over_buffer2_1_y': 100.0 / p[1],
                'tan_invariant_y': ty,
                'tan_invariant_z': tz,
                'reciprocal_sum_invariant': rs,
                'reciprocal_difference_invariant': rd,
            }
        records.append({
            'collection_hash': key[0], 'index': key[1], 'kind': k,
            'material': material, 'pixel_shader': ps, 'buffer_data': bh,
            'volume_transform_vec4s': v[2:6],
            'buffer2_1': p,
            'proof': proof,
        })

    crossing = {ps: dict(c) for ps, c in ps_kinds.items() if len(c) != 1}
    if crossing:
        violations.append(f'pixel_shader_crosses_volume_kind:{crossing}')

    aff = counts['AFFINE_VOLUME']
    proj = counts['PROJECTIVE_VOLUME']
    summary = {
        'affine_volume_count': aff,
        'projective_volume_count': proj,
        'affine_buffer2_1_y_matches_0x30_norm': affine_exact_y,
        'affine_buffer2_1_y_matches_0x40_norm': affine_exact_z,
        'projective_tan_w_matches_0x20_y': projective_tan_y,
        'projective_tan_w_matches_0x30_z': projective_tan_z,
        'projective_reciprocal_sum_matches': projective_recip_sum,
        'projective_hundred_over_range_difference_matches': projective_recip_diff,
        'pixel_shader_count': len(ps_kinds),
        'pixel_shader_cross_kind_count': len(crossing),
    }
    expected = (
        len(records) == 737 and aff == 512 and proj == 225
        and affine_exact_y == aff and affine_exact_z == aff
        and projective_tan_y == proj and projective_tan_z == proj
        and projective_recip_sum == proj and projective_recip_diff == proj
        and not crossing
    )
    if not expected:
        violations.append('tower_exact_population_or_equation_assertion_failed')

    out = {
        'schema_version': 1,
        'status': 'D1_WORLD_LIGHT_VOLUME_INVARIANTS_PROVEN' if not violations else 'D1_WORLD_LIGHT_VOLUME_INVARIANTS_PARTIAL',
        'summary': summary,
        'buffer2_promotions': {
            'buffer2_1_y': {
                'role': 'AUTHORED_LIGHT_VOLUME_RANGE_PARAMETER',
                'evidence': '512/512 affine volume transverse spatial norms and 225/225 projective reciprocal transform identities.',
            },
            'buffer2_1_w': {
                'role': 'PROJECTIVE_LIGHT_VOLUME_BOUNDARY_ANGLE_RADIANS',
                'scope': 'PROJECTIVE_VOLUME only',
                'evidence': 'tan(value) equals both projective transverse transform coefficients for 225/225 projective records.',
            },
            'buffer2_1_x': {'role': 'WITHHELD'},
            'buffer2_1_z': {'role': 'WITHHELD'},
        },
        'volume_kinds': {
            'AFFINE_VOLUME': {'count': aff, 'semantic_light_type': 'WITHHELD'},
            'PROJECTIVE_VOLUME': {'count': proj, 'semantic_light_type': 'WITHHELD'},
        },
        'pixel_shader_volume_kinds': {ps: dict(c) for ps, c in sorted(ps_kinds.items())},
        'records': records,
        'violations': violations,
        'policy': 'Mathematical/storage semantics only. Point/spot/area/type, colour, intensity and inner-cone labels remain withheld until D1 shader dataflow closes them.',
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'status': out['status'], 'summary': summary, 'buffer2_promotions': out['buffer2_promotions'], 'violations': violations}, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
