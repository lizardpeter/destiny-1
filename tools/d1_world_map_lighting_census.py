#!/usr/bin/env python3
"""Loss-preserving Destiny 1 ROI map lighting/sky census.

This consumes the *full* Activity-owned SMapDataTable layer census and decodes only
D1 structures pinned in Charm source. It deliberately does not infer light type,
colour, intensity, range, cone angles, shadowing, exposure, or probe semantics.

Pinned D1 path (MontagueM/Charm@50d36ee...):

  SMapLightResource     canonical 80801BEA
    +0x0C Tag<D1Class_5B1A8080>              canonical 80801A5B
      +0x10 Vector4
      +0x20 Vector4
      +0x30 DynamicArray<LightData>           stride 0x90
      +0x40 DynamicArray<Transform>           stride 0x20
      +0x54 Tag<SOcclusionBounds>             canonical 80800583

  LightData D1 +0x84 Tag<D2Class_F21A8080>   canonical 80801AF2
    +0x00 i64 FileSize
    +0x10 i64 unknown
    +0x20 DynamicArray<byte> TFX bytecode

  Transform D1 (0x20)
    +0x00 Vector4 Rotation
    +0x10 Vector4 Translation

  SMapSkyEntResource    canonical 80801BDA
    +0x0C Tag<D1Class_1F1C8080>              canonical 80801C1F
      +0x10 DynamicArray<D1Class_1E1C8080>    stride 0x10
        +0x00 Tag<Entity>
        +0x08 float
        +0x0C float

Every raw light/sky record is hashed and retained as hex so future semantic decoding can
be checked against the exact retail bytes. Missing dependencies are reported only by
serialized FileHash package id; package filenames are never used as semantic evidence.
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

MAP_LIGHT_RESOURCE = '80801BEA'
MAP_SKY_RESOURCE = '80801BDA'
D1_LIGHT_COLLECTION = '80801A5B'
D1_SKY_COLLECTION = '80801C1F'
D1_LIGHT_BUFFER = '80801AF2'
OCCLUSION_BOUNDS = '80800583'
ENTITY = '80800734'
NULLS = {'00000000', 'FFFFFFFF'}
PINNED_SOURCE = (
    'MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
    'Tiger/Schema/Static/StaticMapData.cs + Tiger/Schema/Entity/EntityStructs.cs + '
    'Tiger/Schema/Shaders/TFX Bytecode/OpCodes.cs'
)


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def hx(v: int) -> str:
    return f'{v:08X}'


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from('<I', b, o)[0]


def i64(b: bytes, o: int) -> int:
    return struct.unpack_from('<q', b, o)[0]


def f32(b: bytes, o: int) -> float:
    return float(struct.unpack_from('<f', b, o)[0])


def vec4(b: bytes, o: int) -> list[float]:
    return [float(x) for x in struct.unpack_from('<4f', b, o)]


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def pkgid(h: str) -> str | None:
    h = norm(h)
    if h in NULLS:
        return None
    try:
        return f'{filehash_package_id(h):04x}'
    except Exception:
        return None


def snapshots(paths: list[Path]):
    return [p.resolve() for p in paths]


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


def add_missing(c, h: str, missing: Counter, reason: str, evidence: list[dict]):
    h = norm(h)
    if h in NULLS:
        return
    if c.entry_meta(h) is None:
        p = pkgid(h)
        if p:
            missing[p] += 1
        evidence.append({'hash': h, 'package_id': p, 'reason': reason})


def parse_buffer(c, h: str, missing: Counter, missing_evidence: list[dict], violations: list[str]) -> dict:
    h = norm(h)
    out = {'hash': h, 'target': meta(c, h, D1_LIGHT_BUFFER)}
    add_missing(c, h, missing, 'light_buffer', missing_evidence)
    b, src = c.payload(h)
    out['source'] = src
    if b is None:
        out['status'] = 'UNAVAILABLE'
        return out
    out['payload_bytes'] = len(b)
    out['payload_sha256'] = sha(b)
    if not out['target']['class_matches']:
        out['status'] = 'CLASS_MISMATCH'
        violations.append(f'light_buffer:{h}:class_mismatch')
        return out
    if len(b) < 0x30:
        out['status'] = 'SHORT'
        violations.append(f'light_buffer:{h}:short:{len(b)}')
        return out
    bc = layer.dyn(b, 0x20, 1)
    out['file_size_i64'] = i64(b, 0x00)
    out['unknown10_i64'] = i64(b, 0x10)
    out['bytecode_array'] = bc
    if not bc['ok']:
        out['status'] = 'BYTECODE_ARRAY_BOUNDS'
        violations.append(f'light_buffer:{h}:bytecode_bounds')
        return out
    raw = b[bc['absolute']:bc['end']]
    out['bytecode_bytes'] = len(raw)
    out['bytecode_sha256'] = sha(raw)
    out['bytecode_hex'] = raw.hex().upper()
    out['opcode_first_bytes'] = [f'{x:02X}' for x in raw[:32]]
    out['status'] = 'D1_LIGHT_BUFFER_BYTECODE_PRESERVED'
    return out


def parse_light_collection(c, h: str, missing: Counter, missing_evidence: list[dict],
                           buffers: dict[str, dict], violations: list[str]) -> dict:
    h = norm(h)
    out = {'hash': h, 'target': meta(c, h, D1_LIGHT_COLLECTION)}
    add_missing(c, h, missing, 'light_collection', missing_evidence)
    b, src = c.payload(h)
    out['source'] = src
    if b is None:
        out['status'] = 'UNAVAILABLE'
        return out
    out['payload_bytes'] = len(b)
    out['payload_sha256'] = sha(b)
    if not out['target']['class_matches']:
        out['status'] = 'CLASS_MISMATCH'
        violations.append(f'light_collection:{h}:class_mismatch')
        return out
    if len(b) < 0x60:
        out['status'] = 'SHORT'
        violations.append(f'light_collection:{h}:short:{len(b)}')
        return out

    lights = layer.dyn(b, 0x30, 0x90)
    transforms = layer.dyn(b, 0x40, 0x20)
    bounds = hx(u32(b, 0x54))
    out['vector10'] = vec4(b, 0x10)
    out['vector20'] = vec4(b, 0x20)
    out['light_data_array'] = lights
    out['transform_array'] = transforms
    out['occlusion_bounds'] = meta(c, bounds, OCCLUSION_BOUNDS)
    add_missing(c, bounds, missing, 'light_collection_occlusion_bounds', missing_evidence)
    if not lights['ok']:
        violations.append(f'light_collection:{h}:light_array_bounds')
    if not transforms['ok']:
        violations.append(f'light_collection:{h}:transform_array_bounds')

    out_lights = []
    if lights['ok']:
        for i in range(lights['count']):
            o = lights['absolute'] + i * 0x90
            raw = b[o:o + 0x90]
            bh = hx(u32(b, o + 0x84))
            row = {
                'index': i,
                'record_offset': o,
                'record_sha256': sha(raw),
                'record_hex': raw.hex().upper(),
                'buffer_data': meta(c, bh, D1_LIGHT_BUFFER),
            }
            add_missing(c, bh, missing, 'light_record_buffer_data', missing_evidence)
            if bh not in NULLS and bh not in buffers and c.entry_meta(bh) is not None:
                buffers[bh] = parse_buffer(c, bh, missing, missing_evidence, violations)
            out_lights.append(row)

    out_transforms = []
    if transforms['ok']:
        for i in range(transforms['count']):
            o = transforms['absolute'] + i * 0x20
            raw = b[o:o + 0x20]
            r = vec4(b, o)
            t = vec4(b, o + 0x10)
            finite = all(math.isfinite(x) for x in r + t)
            if not finite:
                violations.append(f'light_collection:{h}:transform_{i}:nonfinite')
            out_transforms.append({
                'index': i,
                'record_offset': o,
                'record_sha256': sha(raw),
                'record_hex': raw.hex().upper(),
                'rotation': r,
                'translation': t,
                'finite': finite,
            })

    out['lights'] = out_lights
    out['transforms'] = out_transforms
    out['light_count'] = len(out_lights)
    out['transform_count'] = len(out_transforms)
    out['parallel_count_equal'] = len(out_lights) == len(out_transforms)
    # Pair only when the retail arrays themselves prove a one-to-one cardinality.
    out['paired_light_transforms'] = []
    if out['parallel_count_equal']:
        out['paired_light_transforms'] = [
            {
                'index': i,
                'buffer_data': out_lights[i]['buffer_data']['hash'],
                'rotation': out_transforms[i]['rotation'],
                'translation': out_transforms[i]['translation'],
            }
            for i in range(len(out_lights))
        ]
    out['status'] = 'D1_LIGHT_COLLECTION_PRESERVED'
    return out


def parse_sky_collection(c, h: str, missing: Counter, missing_evidence: list[dict],
                         violations: list[str]) -> dict:
    h = norm(h)
    out = {'hash': h, 'target': meta(c, h, D1_SKY_COLLECTION)}
    add_missing(c, h, missing, 'sky_collection', missing_evidence)
    b, src = c.payload(h)
    out['source'] = src
    if b is None:
        out['status'] = 'UNAVAILABLE'
        return out
    out['payload_bytes'] = len(b)
    out['payload_sha256'] = sha(b)
    if not out['target']['class_matches']:
        out['status'] = 'CLASS_MISMATCH'
        violations.append(f'sky_collection:{h}:class_mismatch')
        return out
    if len(b) < 0x20:
        out['status'] = 'SHORT'
        violations.append(f'sky_collection:{h}:short:{len(b)}')
        return out
    arr = layer.dyn(b, 0x10, 0x10)
    out['sky_entities_array'] = arr
    if not arr['ok']:
        out['status'] = 'SKY_ARRAY_BOUNDS'
        violations.append(f'sky_collection:{h}:array_bounds')
        return out
    rows = []
    for i in range(arr['count']):
        o = arr['absolute'] + i * 0x10
        raw = b[o:o + 0x10]
        eh = hx(u32(b, o))
        add_missing(c, eh, missing, 'sky_entity', missing_evidence)
        f0 = f32(b, o + 0x08)
        f1 = f32(b, o + 0x0C)
        if not (math.isfinite(f0) and math.isfinite(f1)):
            violations.append(f'sky_collection:{h}:entry_{i}:nonfinite')
        rows.append({
            'index': i,
            'record_offset': o,
            'record_sha256': sha(raw),
            'record_hex': raw.hex().upper(),
            'entity': meta(c, eh, ENTITY),
            'unknown08': f0,
            'unknown0C': f1,
        })
    out['sky_entities'] = rows
    out['sky_entity_count'] = len(rows)
    out['status'] = 'D1_SKY_COLLECTION_PRESERVED'
    return out


def layer_rows(d: dict):
    for table in d.get('tables', []):
        for row in table.get('entries', []):
            yield row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--layer-census', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    layer_doc = json.loads(a.layer_census.read_text())
    if layer_doc.get('status') not in {'D1_WORLD_MAP_DATA_LAYER_CENSUS', 'D1_WORLD_MAP_DATA_LAYER_CENSUS_PARTIAL'}:
        raise SystemExit(f'unexpected map-data layer status: {layer_doc.get("status")}')
    c = v5.v3.base.Corpus(snapshots(a.snapshot), a.runtime.resolve())
    violations: list[str] = []
    missing: Counter = Counter()
    missing_evidence: list[dict] = []
    buffers: dict[str, dict] = {}
    light_collections: dict[str, dict] = {}
    sky_collections: dict[str, dict] = {}
    occurrences = []

    for row in layer_rows(layer_doc):
        cls = norm(row.get('resource_class') or '00000000')
        if cls not in {MAP_LIGHT_RESOURCE, MAP_SKY_RESOURCE}:
            continue
        rt = row.get('resource_target') or {}
        th = norm(rt.get('hash') or 'FFFFFFFF')
        occ = {
            'map_data_table': row.get('map_data_table'),
            'entry_index': row.get('index'),
            'world_id': row.get('world_id'),
            'outer_rotation': row.get('rotation'),
            'outer_translation': row.get('translation'),
            'resource_class': cls,
            'resource_target': th,
        }
        occurrences.append(occ)
        if th in NULLS:
            violations.append(f'{cls}:{row.get("map_data_table")}:{row.get("index")}:null_target')
            continue
        if cls == MAP_LIGHT_RESOURCE and th not in light_collections:
            light_collections[th] = parse_light_collection(c, th, missing, missing_evidence, buffers, violations)
        elif cls == MAP_SKY_RESOURCE and th not in sky_collections:
            sky_collections[th] = parse_sky_collection(c, th, missing, missing_evidence, violations)

    # A buffer can be missing on the first pass; preserve the exact wanted hashes here.
    all_buffer_hashes = sorted({
        x['buffer_data']['hash']
        for lc in light_collections.values()
        for x in lc.get('lights', [])
        if x.get('buffer_data', {}).get('hash') not in NULLS
    })
    for h in all_buffer_hashes:
        if h not in buffers and c.entry_meta(h) is not None:
            buffers[h] = parse_buffer(c, h, missing, missing_evidence, violations)

    light_records = sum(x.get('light_count', 0) for x in light_collections.values())
    transform_records = sum(x.get('transform_count', 0) for x in light_collections.values())
    sky_records = sum(x.get('sky_entity_count', 0) for x in sky_collections.values())
    unresolved_buffers = [h for h in all_buffer_hashes if c.entry_meta(h) is None]
    missing_ids = dict(sorted(missing.items()))

    out = {
        'schema_version': 1,
        'status': 'D1_WORLD_MAP_LIGHTING_CENSUS_COMPLETE' if not violations and not missing_ids else 'D1_WORLD_MAP_LIGHTING_CENSUS_PARTIAL',
        'pinned_source': PINNED_SOURCE,
        'source_layer_census': str(a.layer_census),
        'source_layer_status': layer_doc.get('status'),
        'source_map_data_table_count': layer_doc.get('map_data_table_count'),
        'source_entry_count': layer_doc.get('entry_count'),
        'light_resource_occurrences': sum(x['resource_class'] == MAP_LIGHT_RESOURCE for x in occurrences),
        'sky_resource_occurrences': sum(x['resource_class'] == MAP_SKY_RESOURCE for x in occurrences),
        'unique_light_collection_count': len(light_collections),
        'unique_sky_collection_count': len(sky_collections),
        'light_record_count': light_records,
        'transform_record_count': transform_records,
        'parallel_collection_count': sum(x.get('parallel_count_equal', False) for x in light_collections.values()),
        'sky_entity_record_count': sky_records,
        'light_buffer_hash_count': len(all_buffer_hashes),
        'decoded_light_buffer_count': len(buffers),
        'unresolved_light_buffer_hashes': unresolved_buffers,
        'missing_dependency_package_ids': missing_ids,
        'missing_dependency_evidence': missing_evidence,
        'occurrences': occurrences,
        'light_collections': [light_collections[k] for k in sorted(light_collections)],
        'light_buffers': [buffers[k] for k in sorted(buffers)],
        'sky_collections': [sky_collections[k] for k in sorted(sky_collections)],
        'violations': violations,
        'semantic_withholding': [
            'light_type', 'light_colour', 'light_intensity', 'light_range', 'spot_cone',
            'shadow_parameters', 'exposure', 'indirect_irradiance', 'probe_semantics'
        ],
        'policy': (
            'Only source-pinned D1 structure offsets are decoded. Direct-light transforms, sky Entity tags, and raw light TFX bytecode are preserved exactly. '
            'No Blender light type or photometric parameter is assigned until the light BufferData bytecode/constants path is independently decoded.'
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in (
        'status','source_map_data_table_count','source_entry_count','light_resource_occurrences',
        'sky_resource_occurrences','unique_light_collection_count','unique_sky_collection_count',
        'light_record_count','transform_record_count','sky_entity_record_count','light_buffer_hash_count',
        'decoded_light_buffer_count','missing_dependency_package_ids','violations'
    )}, indent=2))
    return 0 if out['status'] == 'D1_WORLD_MAP_LIGHTING_CENSUS_COMPLETE' else 2


if __name__ == '__main__':
    raise SystemExit(main())
