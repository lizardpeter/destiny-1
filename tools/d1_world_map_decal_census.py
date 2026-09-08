#!/usr/bin/env python3
"""Loss-preserving Destiny 1 ROI map decal census.

Pinned source:
  MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af
  Tiger/Schema/Static/StaticMapData.cs
  Tiger/Exporters/MetadataExporter.cs

D1 map path:
  SMapDecalsResource                     canonical 80801A70
    +0x0C Tag<SMapDecals>                canonical 80801B40

  SMapDecals (0x68)
    +0x00 u64 FileSize
    +0x08 DynamicArray<DecalResource>     stride 0x08, canonical element 80801A83
    +0x18 DynamicArray<DecalLocation>     stride 0x10, canonical element 80801A53
    +0x28 Tag unknown
    +0x2C Tag unknown
    +0x38 Tag<SOcclusionBounds>           canonical 80800583
    +0x40/+0x50 Vector4 bounds-like values
    +0x60 TigerHash

  DecalResource (0x08)
    +0x00 Material FileHash               canonical 80801AD7
    +0x04 i16 StartIndex
    +0x06 i16 Count

  DecalLocation (0x10)
    +0x00 Vector4 Location

  SOcclusionBounds (0x18)
    +0x08 DynamicArray<InstanceBounds>    stride 0x30
  InstanceBounds
    +0x00 Vector4 Corner1
    +0x10 Vector4 Corner2
    +0x20 TigerHash
    +0x24 TigerHash (MetadataExporter box hash)

Charm's MetadataExporter maps each DecalResource.StartIndex/Count onto Locations and
matching InstanceBounds. Location.xyz is the decal origin and Location.w is scale;
Corner1/Corner2 are the projection box. Materials are exported as transparent.

This tool preserves those exact retail values and validates only source-defined
relationships. It does not invent projection geometry, orientation, shader semantics,
or meanings for SMapDecals +0x28/+0x2C/+0x60.
"""
from __future__ import annotations

import argparse
import hashlib
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

MAP_DECALS_RESOURCE = '80801A70'
D1_MAP_DECALS = '80801B40'
MATERIAL = '80801AD7'
OCCLUSION_BOUNDS = '80800583'
NULLS = {'00000000', 'FFFFFFFF'}
PINNED_SOURCE = (
    'MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
    'Tiger/Schema/Static/StaticMapData.cs + Tiger/Exporters/MetadataExporter.cs'
)


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def hx(v: int) -> str:
    return f'{v:08X}'


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from('<I', b, o)[0]


def u64(b: bytes, o: int) -> int:
    return struct.unpack_from('<Q', b, o)[0]


def i16(b: bytes, o: int) -> int:
    return struct.unpack_from('<h', b, o)[0]


def vec4(b: bytes, o: int) -> list[float]:
    return [float(x) for x in struct.unpack_from('<4f', b, o)]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def pkgid(h: str) -> str | None:
    h = norm(h)
    if h in NULLS:
        return None
    try:
        return f'{filehash_package_id(h):04x}'
    except Exception:
        return None


def meta(c, h: str, expected: str | None = None) -> dict:
    h = norm(h)
    m = c.entry_meta(h)
    return {
        'hash': h,
        'package_id': pkgid(h),
        'exists': m is not None,
        'expected_class': expected,
        'class_matches': bool(m and (expected is None or norm(m.get('reference', '')) == expected)),
        'meta': m,
    }


def add_missing(c, h: str, missing: Counter, evidence: list[dict], reason: str) -> None:
    h = norm(h)
    if h in NULLS or c.entry_meta(h) is not None:
        return
    p = pkgid(h)
    if p:
        missing[p] += 1
    evidence.append({'hash': h, 'package_id': p, 'reason': reason})


def parse_bounds(c, h: str, missing: Counter, missing_evidence: list[dict], violations: list[str]) -> dict:
    h = norm(h)
    out = {'hash': h, 'target': meta(c, h, OCCLUSION_BOUNDS)}
    if h in NULLS:
        out['status'] = 'EXPLICIT_NULL_BOUNDS'
        return out
    add_missing(c, h, missing, missing_evidence, 'decal_projection_bounds')
    b, src = c.payload(h)
    out['source'] = src
    if b is None:
        out['status'] = 'UNAVAILABLE'
        return out
    out['payload_bytes'] = len(b)
    out['payload_sha256'] = sha(b)
    if not out['target']['class_matches']:
        violations.append(f'decal_bounds:{h}:class_mismatch')
        out['status'] = 'CLASS_MISMATCH'
        return out
    if len(b) < 0x18:
        violations.append(f'decal_bounds:{h}:short:{len(b)}')
        out['status'] = 'SHORT'
        return out
    arr = layer.dyn(b, 0x08, 0x30)
    out['file_size_u64'] = u64(b, 0x00)
    out['instance_bounds_array'] = arr
    if not arr.get('ok'):
        violations.append(f'decal_bounds:{h}:array_bounds')
        out['status'] = 'ARRAY_BOUNDS'
        return out
    rows = []
    for i in range(arr['count']):
        o = arr['absolute'] + i * 0x30
        raw = b[o:o + 0x30]
        c1 = vec4(b, o)
        c2 = vec4(b, o + 0x10)
        finite = all(math.isfinite(x) for x in c1 + c2)
        if not finite:
            violations.append(f'decal_bounds:{h}:instance_{i}:nonfinite')
        rows.append({
            'index': i,
            'record_offset': o,
            'record_sha256': sha(raw),
            'record_hex': raw.hex().upper(),
            'corner1': c1,
            'corner2': c2,
            'unknown20': hx(u32(b, o + 0x20)),
            'box_hash_24': hx(u32(b, o + 0x24)),
            'finite': finite,
        })
    out['instance_bounds'] = rows
    out['instance_bounds_count'] = len(rows)
    out['status'] = 'D1_DECAL_PROJECTION_BOUNDS_PRESERVED'
    return out


def parse_collection(c, h: str, missing: Counter, missing_evidence: list[dict], violations: list[str]) -> dict:
    h = norm(h)
    out = {'hash': h, 'target': meta(c, h, D1_MAP_DECALS)}
    add_missing(c, h, missing, missing_evidence, 'map_decals_collection')
    b, src = c.payload(h)
    out['source'] = src
    if b is None:
        out['status'] = 'UNAVAILABLE'
        return out
    out['payload_bytes'] = len(b)
    out['payload_sha256'] = sha(b)
    if not out['target']['class_matches']:
        violations.append(f'map_decals:{h}:class_mismatch')
        out['status'] = 'CLASS_MISMATCH'
        return out
    if len(b) < 0x68:
        violations.append(f'map_decals:{h}:short:{len(b)}')
        out['status'] = 'SHORT'
        return out

    resources = layer.dyn(b, 0x08, 0x08)
    locations = layer.dyn(b, 0x18, 0x10)
    bounds_h = hx(u32(b, 0x38))
    out.update({
        'file_size_u64': u64(b, 0x00),
        'decal_resources_array': resources,
        'locations_array': locations,
        'unknown_tag_28': hx(u32(b, 0x28)),
        'unknown_tag_2c': hx(u32(b, 0x2C)),
        'decal_projection_bounds_hash': bounds_h,
        'vector40': vec4(b, 0x40),
        'vector50': vec4(b, 0x50),
        'unknown_hash_60': hx(u32(b, 0x60)),
    })
    if not resources.get('ok'):
        violations.append(f'map_decals:{h}:resource_array_bounds')
    if not locations.get('ok'):
        violations.append(f'map_decals:{h}:location_array_bounds')
    if not (resources.get('ok') and locations.get('ok')):
        out['status'] = 'ARRAY_BOUNDS'
        return out

    locs = []
    for i in range(locations['count']):
        o = locations['absolute'] + i * 0x10
        raw = b[o:o + 0x10]
        v = vec4(b, o)
        finite = all(math.isfinite(x) for x in v)
        if not finite:
            violations.append(f'map_decals:{h}:location_{i}:nonfinite')
        locs.append({
            'index': i,
            'record_offset': o,
            'record_sha256': sha(raw),
            'record_hex': raw.hex().upper(),
            'origin_xyz': v[:3],
            'scale_w': v[3],
            'location_vec4': v,
            'finite': finite,
        })

    bounds = parse_bounds(c, bounds_h, missing, missing_evidence, violations)
    bound_rows = bounds.get('instance_bounds', [])
    resources_out = []
    projected = []
    material_hist = Counter()
    for i in range(resources['count']):
        o = resources['absolute'] + i * 0x08
        raw = b[o:o + 0x08]
        mh = hx(u32(b, o))
        start = i16(b, o + 0x04)
        count = i16(b, o + 0x06)
        mt = meta(c, mh, MATERIAL)
        add_missing(c, mh, missing, missing_evidence, 'decal_material')
        if mh not in NULLS and mt['exists'] and not mt['class_matches']:
            violations.append(f'map_decals:{h}:resource_{i}:material_class_mismatch:{mh}')
        if start < 0 or count < 0 or start > len(locs) or start + count > len(locs):
            violations.append(f'map_decals:{h}:resource_{i}:location_range:{start}+{count}/{len(locs)}')
            range_ok = False
        else:
            range_ok = True
        row = {
            'index': i,
            'record_offset': o,
            'record_sha256': sha(raw),
            'record_hex': raw.hex().upper(),
            'material': mt,
            'start_index': start,
            'count': count,
            'location_range_ok': range_ok,
        }
        resources_out.append(row)
        if mh not in NULLS:
            material_hist[mh] += max(0, count)
        if range_ok:
            for j in range(start, start + count):
                br = bound_rows[j] if j < len(bound_rows) else None
                if br is None:
                    violations.append(f'map_decals:{h}:projection_{j}:missing_matching_bound')
                projected.append({
                    'decal_resource_index': i,
                    'location_index': j,
                    'material': mh,
                    'origin_xyz': locs[j]['origin_xyz'],
                    'scale_w': locs[j]['scale_w'],
                    'corner1': None if br is None else br['corner1'],
                    'corner2': None if br is None else br['corner2'],
                    'box_hash_24': None if br is None else br['box_hash_24'],
                })

    if bound_rows and len(bound_rows) != len(locs):
        violations.append(f'map_decals:{h}:bounds_location_count:{len(bound_rows)}!={len(locs)}')

    out['decal_resources'] = resources_out
    out['locations'] = locs
    out['projection_bounds'] = bounds
    out['decal_resource_count'] = len(resources_out)
    out['location_count'] = len(locs)
    out['projected_decal_count'] = len(projected)
    out['projected_decals'] = projected
    out['material_reference_counts'] = dict(material_hist)
    out['unique_material_count'] = len(material_hist)
    out['status'] = 'D1_MAP_DECALS_COLLECTION_PRESERVED'
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--layer-census', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    layer_doc = json.loads(a.layer_census.read_text())
    if layer_doc.get('status') != 'D1_WORLD_MAP_DATA_LAYER_CENSUS':
        raise SystemExit(f'layer census status not accepted: {layer_doc.get("status")!r}')
    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    missing = Counter()
    missing_evidence = []
    violations = []
    occurrences = []
    collections: dict[str, dict] = {}

    for t in layer_doc.get('tables', []):
        table = norm(t.get('map_data_table'))
        for e in t.get('entries', []):
            if norm(e.get('resource_class')) != MAP_DECALS_RESOURCE:
                continue
            target = norm((e.get('resource_target') or {}).get('hash', 'FFFFFFFF'))
            row = {
                'map_data_table': table,
                'entry_index': e.get('index'),
                'record_offset': e.get('record_offset'),
                'entity_hash': norm(e.get('entity_hash')),
                'world_id': e.get('world_id'),
                'rotation': e.get('rotation'),
                'translation': e.get('translation'),
                'collection_hash': target,
                'explicit_null_collection': target in NULLS,
            }
            occurrences.append(row)
            if target in NULLS:
                continue
            if target not in collections:
                collections[target] = parse_collection(c, target, missing, missing_evidence, violations)

    material_hist = Counter()
    projected = 0
    location_count = 0
    resource_count = 0
    for col in collections.values():
        projected += int(col.get('projected_decal_count', 0))
        location_count += int(col.get('location_count', 0))
        resource_count += int(col.get('decal_resource_count', 0))
        material_hist.update(col.get('material_reference_counts', {}))

    expected_occ = int((layer_doc.get('resource_class_counts') or {}).get(MAP_DECALS_RESOURCE, 0))
    if len(occurrences) != expected_occ:
        violations.append(f'decal_occurrence_count:{len(occurrences)}!={expected_occ}')
    nonnull = sum(not x['explicit_null_collection'] for x in occurrences)
    closed = not missing and not violations and all(
        x.get('status') == 'D1_MAP_DECALS_COLLECTION_PRESERVED' for x in collections.values()
    )
    out = {
        'schema_version': 1,
        'status': 'D1_WORLD_MAP_DECAL_CENSUS_COMPLETE' if closed else 'D1_WORLD_MAP_DECAL_CENSUS_PARTIAL',
        'pinned_source': PINNED_SOURCE,
        'source_layer_census': str(a.layer_census),
        'source_map_data_table_count': layer_doc.get('map_data_table_count'),
        'source_entry_count': layer_doc.get('entry_count'),
        'decal_resource_occurrences': len(occurrences),
        'nonnull_decal_collection_occurrences': nonnull,
        'explicit_null_decal_collection_occurrences': len(occurrences) - nonnull,
        'unique_decal_collection_count': len(collections),
        'decal_resource_record_count': resource_count,
        'decal_location_count': location_count,
        'projected_decal_count': projected,
        'unique_material_count': len(material_hist),
        'material_reference_counts': dict(material_hist),
        'occurrences': occurrences,
        'collections': [collections[k] for k in sorted(collections)],
        'missing_dependency_package_ids': dict(missing),
        'missing_dependency_evidence': missing_evidence,
        'violations': violations,
        'policy': (
            'Only source-defined D1 SMapDecalsResource -> SMapDecals fields are decoded. Explicit null collection '
            'TagHashes are preserved as empty source rows. StartIndex/Count, Location.xyz/w and SOcclusionBounds '
            'Corner1/Corner2/Unk24 are joined exactly as pinned Charm MetadataExporter does. No decal mesh, orientation, '
            'shader semantic, or meaning for unknown SMapDecals tags/hashes is inferred.'
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in (
        'status','decal_resource_occurrences','nonnull_decal_collection_occurrences',
        'explicit_null_decal_collection_occurrences','unique_decal_collection_count',
        'decal_resource_record_count','decal_location_count','projected_decal_count',
        'unique_material_count','missing_dependency_package_ids','violations'
    )}, indent=2))
    return 0 if closed else 2


if __name__ == '__main__':
    raise SystemExit(main())
