#!/usr/bin/env python3
"""Source-backed semantic probe for Destiny 1 map-light records.

This stage intentionally sits after the loss-preserving map-light census and TFX
inventory. It promotes only semantics that the D1 retail corpus itself proves:

* Buffer1 is the TFX bytecode constant bank: every PushConstantVec4/LerpConstant
  reference must fit Buffer1, and the Buffer1 length must end exactly at the highest
  referenced constant for every light BufferData object.
* SOcclusionBounds is decoded from its pinned D1 schema and paired by array index only
  when its record count equals the light and transform arrays.
* LightData +0x80 is treated as a *candidate serialized reference* until its actual
  package entry/class is resolved. No semantic name is assigned by numeric appearance.

Buffer2 is preserved and characterized, but its D1 semantic role is not promoted here.
Later Tiger implementations use the corresponding array as initial constant-buffer
values; that is useful lineage evidence, not by itself D1 proof.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_tower_map_schema_validate_v5 as v5
import d1_world_map_data_layer_census as layer
from d1_world_activity_manifest_dependency_plan import filehash_package_id

OCCLUSION_BOUNDS = '80800583'
NULLS = {'00000000', 'FFFFFFFF'}
PINNED_D1_SOURCE = (
    'MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
    'Tiger/Schema/Static/StaticMapData.cs + Tiger/Schema/Shaders/TFX Bytecode/OpCodes.cs'
)
LINEAGE_SOURCE = (
    'cohaereo/alkahest current SDynamicConstants/DynamicConstants architecture: '
    'bytecode_constants plus initial_constants; used only as non-authoritative lineage evidence'
)


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def hx(v: int) -> str:
    return f'{v:08X}'


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from('<I', b, o)[0]


def i64(b: bytes, o: int) -> int:
    return struct.unpack_from('<q', b, o)[0]


def vec4(b: bytes, o: int) -> list[float]:
    return [float(x) for x in struct.unpack_from('<4f', b, o)]


def pid(h: str) -> str | None:
    h = norm(h)
    if h in NULLS:
        return None
    try:
        return f'{filehash_package_id(h):04x}'
    except Exception:
        return None


def entry(c, h: str) -> dict:
    h = norm(h)
    m = c.entry_meta(h)
    return {
        'hash': h,
        'package_id': pid(h),
        'exists': m is not None,
        'reference': norm(m.get('reference')) if m and m.get('reference') is not None else None,
        'meta': m,
    }


def refs_from_ops(ops: list[dict]) -> list[int]:
    refs: list[int] = []
    for op in ops:
        if 'constant_index' in op:
            refs.append(int(op['constant_index']))
        if 'constant_start' in op:
            i = int(op['constant_start'])
            refs.extend((i, i + 1))
    return refs


def parse_bounds(c, h: str, violations: list[str]) -> dict:
    h = norm(h)
    out = {'hash': h, 'target': entry(c, h)}
    b, src = c.payload(h)
    out['source'] = src
    if b is None:
        out['status'] = 'UNAVAILABLE'
        violations.append(f'occlusion_bounds:{h}:unavailable')
        return out
    out['payload_bytes'] = len(b)
    if out['target']['reference'] != OCCLUSION_BOUNDS:
        out['status'] = 'CLASS_MISMATCH'
        violations.append(f'occlusion_bounds:{h}:class:{out["target"]["reference"]}')
        return out
    if len(b) < 0x18:
        out['status'] = 'SHORT'
        violations.append(f'occlusion_bounds:{h}:short:{len(b)}')
        return out
    arr = layer.dyn(b, 0x08, 0x30)
    out['file_size_i64'] = i64(b, 0)
    out['instance_bounds_array'] = arr
    if not arr.get('ok'):
        out['status'] = 'ARRAY_BOUNDS'
        violations.append(f'occlusion_bounds:{h}:array_bounds')
        return out
    rows = []
    for i in range(arr['count']):
        o = arr['absolute'] + i * 0x30
        c1 = vec4(b, o)
        c2 = vec4(b, o + 0x10)
        finite = all(math.isfinite(x) for x in c1 + c2)
        if not finite:
            violations.append(f'occlusion_bounds:{h}:{i}:nonfinite')
        lo = [min(c1[j], c2[j]) for j in range(3)]
        hi = [max(c1[j], c2[j]) for j in range(3)]
        rows.append({
            'index': i,
            'corner1': c1,
            'corner2': c2,
            'min_xyz': lo,
            'max_xyz': hi,
            'center_xyz': [(lo[j] + hi[j]) * 0.5 for j in range(3)],
            'extent_xyz': [hi[j] - lo[j] for j in range(3)],
            'unk20_u32': u32(b, o + 0x20),
            'unk24_u32': u32(b, o + 0x24),
            'finite': finite,
        })
    out['records'] = rows
    out['record_count'] = len(rows)
    out['status'] = 'D1_OCCLUSION_BOUNDS_DECODED'
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--lighting-census', type=Path, required=True)
    ap.add_argument('--tfx-inventory', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    lighting = json.loads(a.lighting_census.read_text())
    tfx = json.loads(a.tfx_inventory.read_text())
    if lighting.get('status') != 'D1_WORLD_MAP_LIGHTING_CENSUS_COMPLETE':
        raise SystemExit(f'incomplete lighting census: {lighting.get("status")}')
    if tfx.get('status') != 'D1_TFX_PROGRAM_INVENTORY_COMPLETE':
        raise SystemExit(f'incomplete TFX inventory: {tfx.get("status")}')

    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    violations: list[str] = []

    light_buffers = {norm(x['hash']): x for x in lighting.get('light_buffers', [])}
    tfx_buffers = {norm(x['buffer_hash']): x for x in tfx.get('buffers', [])}
    constant_rows = []
    b1_exact = 0
    b1_fit = 0
    b2_fit = 0
    b1_only = 0
    b2_counts = Counter()
    for h, b in sorted(light_buffers.items()):
        ti = tfx_buffers.get(h)
        if ti is None:
            violations.append(f'tfx_missing_buffer:{h}')
            continue
        refs = refs_from_ops(ti.get('ops', []))
        max_ref = max(refs) if refs else -1
        b1n = int(b.get('buffer1_count', len(b.get('buffer1', []))))
        b2n = int(b.get('buffer2_count', len(b.get('buffer2', []))))
        fit1 = max_ref < b1n
        fit2 = max_ref < b2n
        exact1 = b1n == max_ref + 1
        b1_fit += int(fit1)
        b2_fit += int(fit2)
        b1_exact += int(exact1)
        b1_only += int(fit1 and not fit2)
        b2_counts[b2n] += 1
        if not fit1 or not exact1:
            violations.append(f'constant_span:{h}:max={max_ref}:b1={b1n}')
        constant_rows.append({
            'buffer_hash': h,
            'max_referenced_constant': max_ref,
            'referenced_constant_count': len(set(refs)),
            'buffer1_count': b1n,
            'buffer2_count': b2n,
            'all_references_fit_buffer1': fit1,
            'all_references_fit_buffer2': fit2,
            'buffer1_exactly_ends_after_highest_reference': exact1,
        })

    nbuf = len(light_buffers)
    buffer1_proven = (
        len(constant_rows) == nbuf
        and b1_fit == nbuf
        and b1_exact == nbuf
        and b1_only > 0
    )
    if not buffer1_proven:
        violations.append('buffer1_constant_bank_not_proven')

    bounds_docs: dict[str, dict] = {}
    ref80_reference_hist = Counter()
    ref80_package_hist = Counter()
    ref80_missing_package_hist = Counter()
    ref80_resolved = 0
    ref80_total = 0
    flags88_hist = Counter()
    flags8c_hist = Counter()
    instances = []
    parallel_bounds_collections = 0

    for col in lighting.get('light_collections', []):
        ch = norm(col['hash'])
        bh = norm(col['occlusion_bounds']['hash'])
        bd = bounds_docs.get(bh)
        if bd is None:
            bd = parse_bounds(c, bh, violations)
            bounds_docs[bh] = bd
        bounds = bd.get('records', [])
        lights = col.get('lights', [])
        transforms = col.get('transforms', [])
        parallel = len(bounds) == len(lights) == len(transforms)
        parallel_bounds_collections += int(parallel)
        if not parallel:
            violations.append(
                f'parallel_bounds:{ch}:lights={len(lights)}:transforms={len(transforms)}:bounds={len(bounds)}'
            )
        for i, light in enumerate(lights):
            raw = bytes.fromhex(light['record_hex'])
            if len(raw) != 0x90:
                violations.append(f'light_record:{ch}:{i}:size={len(raw)}')
                continue
            r80 = hx(u32(raw, 0x80))
            r80m = entry(c, r80)
            ref80_total += 1
            if r80m['exists']:
                ref80_resolved += 1
                ref80_reference_hist[r80m['reference'] or 'NONE'] += 1
            else:
                p = r80m['package_id'] or 'INVALID'
                ref80_missing_package_hist[p] += 1
            ref80_package_hist[r80m['package_id'] or 'INVALID'] += 1
            f88 = u32(raw, 0x88)
            f8c = u32(raw, 0x8C)
            flags88_hist[f'{f88:08X}'] += 1
            flags8c_hist[f'{f8c:08X}'] += 1
            row = {
                'collection_hash': ch,
                'index': i,
                'buffer_data': norm(light['buffer_data']['hash']),
                'candidate_ref80': r80m,
                'flags88_u32': f88,
                'flags88_hex': f'{f88:08X}',
                'flags8c_u32': f8c,
                'flags8c_hex': f'{f8c:08X}',
            }
            if i < len(transforms):
                row['rotation'] = transforms[i]['rotation']
                row['translation'] = transforms[i]['translation']
            if i < len(bounds):
                row['occlusion_bounds'] = bounds[i]
            instances.append(row)

    if parallel_bounds_collections != len(lighting.get('light_collections', [])):
        violations.append('not_all_light_collections_have_parallel_bounds')

    out = {
        'schema_version': 1,
        'status': 'D1_WORLD_MAP_LIGHT_SEMANTIC_PROBE_COMPLETE' if not violations else 'D1_WORLD_MAP_LIGHT_SEMANTIC_PROBE_PARTIAL',
        'pinned_d1_source': PINNED_D1_SOURCE,
        'lineage_source_non_authoritative': LINEAGE_SOURCE,
        'source_lighting_status': lighting.get('status'),
        'source_tfx_status': tfx.get('status'),
        'light_buffer_count': nbuf,
        'buffer1_constant_bank_proof': {
            'proven': buffer1_proven,
            'semantic_role': 'D1_TFX_BYTECODE_CONSTANTS' if buffer1_proven else 'WITHHELD',
            'all_reference_fit_count': b1_fit,
            'exact_highest_reference_span_count': b1_exact,
            'buffer1_only_fit_count': b1_only,
            'buffer2_reference_fit_count': b2_fit,
            'evidence': (
                'D1 opcode identities PushConstantVec4/LerpConstant are source-pinned. '
                'Across the retail Tower corpus Buffer1 ends exactly after the highest referenced constant for every BufferData; '
                'some references exceed Buffer2, so Buffer2 cannot be the bytecode constant bank.'
            ),
            'buffers': constant_rows,
        },
        'buffer2_characterization': {
            'semantic_role': 'WITHHELD',
            'count_histogram': dict(sorted(b2_counts.items())),
            'all_same_length': len(b2_counts) == 1,
            'lineage_note': (
                'Later Tiger SDynamicConstants has a separate initial-constants array corresponding architecturally to this position, '
                'but D1 promotion requires D1 shader/VM dataflow evidence.'
            ),
        },
        'occlusion_bounds': {
            'collection_count': len(bounds_docs),
            'decoded_collection_count': sum(x.get('status') == 'D1_OCCLUSION_BOUNDS_DECODED' for x in bounds_docs.values()),
            'record_count': sum(int(x.get('record_count', 0)) for x in bounds_docs.values()),
            'parallel_light_transform_bounds_collection_count': parallel_bounds_collections,
            'collections': list(bounds_docs.values()),
        },
        'record_plus_0x80_candidate_reference': {
            'total_occurrences': ref80_total,
            'resolved_occurrences': ref80_resolved,
            'unresolved_occurrences': ref80_total - ref80_resolved,
            'reference_class_histogram': dict(ref80_reference_hist),
            'package_id_histogram': dict(ref80_package_hist),
            'missing_package_id_histogram': dict(ref80_missing_package_hist),
            'semantic_name': 'WITHHELD',
        },
        'flags88_histogram': dict(flags88_hist),
        'flags8c_histogram': dict(flags8c_hist),
        'light_instances': instances,
        'violations': violations,
        'policy': (
            'Bounds are paired only by exact parallel D1 arrays. LightData +0x80 remains unnamed until class/dataflow resolution proves its role. '
            'No light type, colour, intensity, range, cone, or shadow semantic is assigned from visual appearance.'
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'],
        'buffer1_constant_bank_proof': {k: out['buffer1_constant_bank_proof'][k] for k in (
            'proven','semantic_role','all_reference_fit_count','exact_highest_reference_span_count','buffer1_only_fit_count','buffer2_reference_fit_count')},
        'buffer2_characterization': out['buffer2_characterization'],
        'occlusion_bounds_summary': {k: out['occlusion_bounds'][k] for k in (
            'collection_count','decoded_collection_count','record_count','parallel_light_transform_bounds_collection_count')},
        'record_plus_0x80_candidate_reference': out['record_plus_0x80_candidate_reference'],
        'flags88_histogram': out['flags88_histogram'],
        'flags8c_histogram': out['flags8c_histogram'],
        'violations': violations,
    }, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
