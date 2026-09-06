#!/usr/bin/env python3
"""Census D1 Havok collision resources and static-map occlusion bounds.

This deliberately keeps two concepts separate:

* gameplay/physics candidates: Tiger file metadata Type=27, SubType=0, which pinned
  Charm labels `Havok` and passes to DestinyHavok.ReadShapeCollection();
* visibility bounds: D1 SStaticMapData +0x18 -> SOcclusionBounds (80800583), whose
  0x30-byte records contain two Vector4 corners. These are exported as occlusion AABBs,
  never silently promoted to gameplay collision.

The census does not infer that every Havok resource belongs to the selected world merely
because it is present in the dependency corpus. It inventories current resources and
records package/hash evidence so later ownership tracing can connect them explicitly.
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

STATIC_MAP_DATA = '808008B4'
OCCLUSION_BOUNDS = '80800583'
HAVOK_TYPE = 27
HAVOK_SUBTYPE = 0
PINNED_SOURCE = (
    'MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
    'Charm/DevView.xaml.cs (Type 27/SubType 0 = Havok; DestinyHavok.ReadShapeCollection) + '
    'Tiger/Schema/Model/Havok/HavokMesh.cs + Tiger/Schema/Static/StaticMapData.cs'
)


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def hx(v: int) -> str:
    return f'{v:08X}'


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from('<I', b, o)[0]


def f4(b: bytes, o: int) -> list[float]:
    return list(struct.unpack_from('<4f', b, o))


def finite(v: list[float]) -> bool:
    return all(math.isfinite(x) for x in v)


def parse_occlusion(c, h: str) -> dict:
    h = norm(h)
    meta = c.entry_meta(h)
    rep = {
        'hash': h,
        'meta': meta,
        'ok': False,
        'bounds': [],
        'violations': [],
    }
    if not meta:
        rep['violations'].append('tag_missing')
        return rep
    if norm(meta.get('reference', '')) != OCCLUSION_BOUNDS:
        rep['violations'].append(
            f'entry_reference_mismatch:{norm(meta.get("reference",""))}!={OCCLUSION_BOUNDS}'
        )
        return rep
    b, src = c.payload(h)
    rep['payload_source'] = src
    if b is None:
        rep['violations'].append('payload_unavailable')
        return rep
    rep['payload_bytes'] = len(b)
    arr = layer.dyn(b, 0x08, 0x30)
    rep['instance_bounds_array'] = arr
    if not arr['ok']:
        rep['violations'].append('instance_bounds_array_bounds')
        return rep
    for i in range(arr['count']):
        o = arr['absolute'] + i * 0x30
        c1 = f4(b, o)
        c2 = f4(b, o + 0x10)
        row = {
            'index': i,
            'offset': o,
            'corner1': c1,
            'corner2': c2,
            'unk20': hx(u32(b, o + 0x20)),
            'unk24': hx(u32(b, o + 0x24)),
            'finite': finite(c1) and finite(c2),
            'ordered_xyz': all(c1[j] <= c2[j] for j in range(3)),
        }
        rep['bounds'].append(row)
        if not row['finite']:
            rep['violations'].append(f'bound[{i}]:non_finite_corner')
    rep['bound_count'] = len(rep['bounds'])
    rep['finite_bound_count'] = sum(x['finite'] for x in rep['bounds'])
    rep['ordered_xyz_count'] = sum(x['ordered_xyz'] for x in rep['bounds'])
    rep['ok'] = not rep['violations']
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())

    current = []
    for h in sorted(c.occ):
        m = c.entry_meta(h)
        if m:
            current.append(m)

    havok = []
    for m in current:
        if int(m.get('type', -1)) != HAVOK_TYPE or int(m.get('subtype', -1)) != HAVOK_SUBTYPE:
            continue
        h = norm(m['hash'])
        b, src = c.payload(h)
        havok.append({
            'hash': h,
            'meta': m,
            'payload_available': b is not None,
            'payload_source': src,
            'payload_bytes': None if b is None else len(b),
            'prefix_hex_32': None if b is None else b[:32].hex(),
        })

    static_maps = []
    occ_hashes = []
    for m in current:
        if norm(m.get('reference', '')) != STATIC_MAP_DATA:
            continue
        h = norm(m['hash'])
        b, src = c.payload(h)
        row = {'hash': h, 'meta': m, 'payload_source': src, 'occlusion_bounds': None, 'violations': []}
        if b is None or len(b) < 0x1C:
            row['violations'].append('payload_unavailable_or_short_for_occlusion_field')
        else:
            oh = hx(u32(b, 0x18))
            row['occlusion_bounds'] = oh
            if oh not in {'00000000', 'FFFFFFFF'}:
                occ_hashes.append(oh)
        static_maps.append(row)

    unique_occ = sorted(set(occ_hashes))
    occ = [parse_occlusion(c, h) for h in unique_occ]

    pkg_havok = Counter(x['meta']['package_id'] for x in havok)
    pkg_static = Counter(x['meta']['package_id'] for x in static_maps)
    violations = []
    if any(x['violations'] for x in static_maps):
        violations.append('one_or_more_static_map_occlusion_fields_unavailable')
    if any(not x['ok'] for x in occ):
        violations.append('one_or_more_occlusion_resources_failed_validation')

    out = {
        'schema_version': 1,
        'status': 'D1_WORLD_COLLISION_RESOURCE_CENSUS_COMPLETE' if not violations else 'D1_WORLD_COLLISION_RESOURCE_CENSUS_PARTIAL',
        'pinned_source': PINNED_SOURCE,
        'current_entry_count': len(current),
        'havok_file_metadata': {'type': HAVOK_TYPE, 'subtype': HAVOK_SUBTYPE},
        'havok_resource_count': len(havok),
        'havok_payload_available_count': sum(x['payload_available'] for x in havok),
        'havok_package_histogram': dict(sorted(pkg_havok.items())),
        'havok_resources': havok,
        'static_map_data_count': len(static_maps),
        'static_map_package_histogram': dict(sorted(pkg_static.items())),
        'static_maps': static_maps,
        'unique_occlusion_bounds_count': len(unique_occ),
        'occlusion_bounds_resources': occ,
        'occlusion_bound_record_count': sum(x.get('bound_count', 0) for x in occ),
        'finite_occlusion_bound_record_count': sum(x.get('finite_bound_count', 0) for x in occ),
        'ordered_xyz_occlusion_bound_record_count': sum(x.get('ordered_xyz_count', 0) for x in occ),
        'violations': violations,
        'policy': (
            'Type27/SubType0 resources are Havok/physics candidates by pinned Charm file-metadata behavior. '
            'Presence in this dependency corpus is not yet world ownership. SOcclusionBounds are separately '
            'validated visibility bounds and are never relabeled as gameplay collision without independent proof.'
        ),
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in (
        'status', 'current_entry_count', 'havok_resource_count', 'havok_payload_available_count',
        'havok_package_histogram', 'static_map_data_count', 'unique_occlusion_bounds_count',
        'occlusion_bound_record_count', 'finite_occlusion_bound_record_count', 'violations'
    )}, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
