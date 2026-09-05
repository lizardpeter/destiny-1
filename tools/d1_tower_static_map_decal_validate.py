#!/usr/bin/env python3
"""Binary-validate Destiny 1 ROI SStaticMapData decal arrays.

The candidate layout is pinned to MontagueM/Charm commit
50d36ee1f9ecadad7522504c20b1f3f9c97e30af, then checked against shipped Tiger bytes.

D1 SStaticMapData / canonical class 808008B4:
  +0x08 DynamicArray<D1Class_BA048080> Decals, elem 0x80
  +0x18 Tag<SOcclusionBounds>                  canonical 80800583
  +0x30 Tag<SStaticMapData_D1>                 canonical 80801B75 or null/FFFFFFFF

D1 decal record BA048080 / 0x80:
  +0x08 DynamicArray<75018080> Transforms      elem 0x40 Matrix4x4
  +0x18 DynamicArray<C1018080> Unknown vectors elem 0x10 Vector4
  +0x28 DynamicArray<A5438080> Models          elem 0x04 EntityModel TagHash

Charm's exporter asserts each decal has one transform and one model. We report that
singleton invariant separately from structural validity so a non-singleton retail row
is preserved as evidence instead of being silently rejected or normalized.

No map ownership is inferred here. This validates only the internals of an explicitly
selected 808008B4 resource.
"""
from __future__ import annotations

import argparse, json, math, struct, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_tower_map_schema_validate import Corpus, dyn

STATIC_MAP_DATA = '808008B4'
OCCLUSION_BOUNDS = '80800583'
STATIC_MAP_D1 = '80801B75'
ENTITY_MODEL = '80801AB5'
PINNED_SOURCE = (
    'MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
    'Tiger/Schema/Static/StaticMapData.cs'
)


def norm(s: str) -> str:
    return str(s).upper().removeprefix('0X').zfill(8)


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from('<I', b, o)[0]


def u64(b: bytes, o: int) -> int:
    return struct.unpack_from('<Q', b, o)[0]


def hx(v: int) -> str:
    return f'{v:08X}'


def finite_floats(raw: bytes) -> bool:
    if len(raw) % 4:
        return False
    return all(math.isfinite(x[0]) for x in struct.iter_unpack('<f', raw))


def target(c: Corpus, h: str, expected: str | None = None) -> dict:
    h = norm(h)
    m = c.entry_meta(h)
    return {
        'hash': h,
        'exists': m is not None,
        'expected_reference': expected,
        'reference_matches': bool(m and (expected is None or m['reference'] == expected)),
        'meta': m,
    }


def parse_decal(c: Corpus, b: bytes, record_offset: int, index: int) -> dict:
    end = record_offset + 0x80
    row = {
        'index': index,
        'record_offset': record_offset,
        'record_end': end,
        'declared_size': None,
        'arrays': {},
        'models': [],
        'violations': [],
    }
    if record_offset < 0 or end > len(b):
        row['violations'].append('decal record out of bounds')
        row['ok'] = False
        return row

    row['declared_size'] = u64(b, record_offset)
    transforms = dyn(b, record_offset + 0x08, 0x40)
    unk18 = dyn(b, record_offset + 0x18, 0x10)
    models = dyn(b, record_offset + 0x28, 0x04)
    row['arrays'] = {'transforms': transforms, 'unk18': unk18, 'models': models}
    if not transforms['ok']:
        row['violations'].append('Transforms dynamic array bounds')
    if not unk18['ok']:
        row['violations'].append('Unk18 dynamic array bounds')
    if not models['ok']:
        row['violations'].append('Models dynamic array bounds')

    if transforms['ok']:
        mats = []
        all_finite = True
        for i in range(transforms['count']):
            o = transforms['absolute'] + i * 0x40
            raw = b[o:o + 0x40]
            vals = list(struct.unpack_from('<16f', raw, 0))
            finite = all(math.isfinite(x) for x in vals)
            all_finite &= finite
            mats.append({
                'index': i,
                'offset': o,
                'finite': finite,
                'rows': [vals[j:j + 4] for j in range(0, 16, 4)],
            })
        row['transforms'] = mats
        row['transforms_all_finite'] = all_finite
        if not all_finite:
            row['violations'].append('non-finite transform matrix')

    if unk18['ok']:
        vectors = []
        all_finite = True
        for i in range(unk18['count']):
            o = unk18['absolute'] + i * 0x10
            vals = list(struct.unpack_from('<4f', b, o))
            finite = all(math.isfinite(x) for x in vals)
            all_finite &= finite
            vectors.append({'index': i, 'offset': o, 'finite': finite, 'value': vals})
        row['unk18_vectors'] = vectors
        row['unk18_all_finite'] = all_finite
        if not all_finite:
            row['violations'].append('non-finite Unk18 vector')

    if models['ok']:
        for i in range(models['count']):
            o = models['absolute'] + i * 4
            h = hx(u32(b, o))
            tm = target(c, h, ENTITY_MODEL)
            row['models'].append({'index': i, 'offset': o, **tm})
            if not tm['reference_matches']:
                row['violations'].append(
                    f'model[{i}] {h} missing or class != {ENTITY_MODEL}'
                )

    row['singleton_transform_model'] = bool(
        transforms.get('ok') and models.get('ok') and
        transforms.get('count') == 1 and models.get('count') == 1
    )
    row['ok'] = not row['violations']
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--static-map-data', required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    h = norm(a.static_map_data)
    c = Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    meta = c.entry_meta(h)
    rep = {
        'schema_version': 1,
        'evidence_status': 'SOURCE_DERIVED_DECAL_LAYOUT_UNDER_BINARY_VALIDATION',
        'pinned_source': PINNED_SOURCE,
        'static_map_data': h,
        'meta': meta,
        'violations': [],
        'decals': [],
    }
    if not meta or meta['reference'] != STATIC_MAP_DATA:
        rep['violations'].append(f'{h} is not class {STATIC_MAP_DATA}')
        b = None
    else:
        b, src = c.payload(h)
        rep['payload_source'] = src
        if b is None:
            rep['violations'].append('payload unavailable')
        else:
            rep['payload_size'] = len(b)
            if len(b) < 0x38:
                rep['violations'].append('payload shorter than D1 SStaticMapData 0x38 frontier')

    if b is not None and len(b) >= 0x38:
        decals = dyn(b, 0x08, 0x80)
        rep['decals_array'] = decals
        if not decals['ok']:
            rep['violations'].append('Decals dynamic array bounds')

        occ_hash = hx(u32(b, 0x18))
        rep['occlusion_bounds'] = target(c, occ_hash, OCCLUSION_BOUNDS)
        if not rep['occlusion_bounds']['reference_matches']:
            rep['violations'].append(
                f'occlusion +0x18 {occ_hash} missing or class != {OCCLUSION_BOUNDS}'
            )

        d1_hash = hx(u32(b, 0x30))
        rep['d1_static_map_raw'] = d1_hash
        rep['d1_static_map_is_null_sentinel'] = d1_hash in ('00000000', 'FFFFFFFF')
        if not rep['d1_static_map_is_null_sentinel']:
            rep['d1_static_map'] = target(c, d1_hash, STATIC_MAP_D1)
            if not rep['d1_static_map']['reference_matches']:
                rep['violations'].append(
                    f'D1 static +0x30 {d1_hash} missing or class != {STATIC_MAP_D1}'
                )
        else:
            rep['d1_static_map'] = None

        if decals['ok']:
            for i in range(decals['count']):
                rep['decals'].append(parse_decal(c, b, decals['absolute'] + i * 0x80, i))
            if any(not x['ok'] for x in rep['decals']):
                rep['violations'].append('one or more decal records failed structural validation')

    model_hashes = [
        m['hash'] for d in rep['decals'] for m in d.get('models', [])
        if m.get('reference_matches')
    ]
    singleton_count = sum(bool(d.get('singleton_transform_model')) for d in rep['decals'])
    rep['summary'] = {
        'decal_count': rep.get('decals_array', {}).get('count'),
        'decal_records_parsed': len(rep['decals']),
        'decal_records_structurally_valid': sum(bool(d.get('ok')) for d in rep['decals']),
        'singleton_transform_model_records': singleton_count,
        'all_decal_records_singleton_transform_model': bool(
            rep['decals'] and singleton_count == len(rep['decals'])
        ),
        'model_reference_occurrences': len(model_hashes),
        'unique_entity_models': len(set(model_hashes)),
        'entity_model_histogram': dict(Counter(model_hashes)),
        'has_direct_d1_static_child': bool(
            rep.get('d1_static_map') and rep['d1_static_map'].get('reference_matches')
        ),
        'd1_static_child': None if not rep.get('d1_static_map') else rep['d1_static_map']['hash'],
        'occlusion_bounds': None if not rep.get('occlusion_bounds') else rep['occlusion_bounds']['hash'],
    }
    rep['ok'] = not rep['violations']
    if rep['ok']:
        rep['evidence_status'] = 'CONFIRMED_BINARY_D1_STATIC_MAP_DECAL_LAYOUT'

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(rep, indent=2) + '\n')
    print(json.dumps({
        'static_map_data': h,
        'evidence_status': rep['evidence_status'],
        'summary': rep['summary'],
        'violations': rep['violations'],
        'ok': rep['ok'],
    }, indent=2))
    return 0 if rep['ok'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
