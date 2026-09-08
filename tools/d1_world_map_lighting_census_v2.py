#!/usr/bin/env python3
"""Evidence-bounded D1 map-lighting census wrapper.

This keeps ``d1_world_map_lighting_census.py`` as the canonical source-pinned parser and
adds one independently retail-proven D1 serialization payload shape:

    class 80801C1F / payload 0x60
    SHA-256 ab5aed627609f799666d2308d344cb045a45aa16cc365b38312ad4f17c06755c

The dedicated exact-byte probe (workflow run 34012180939) first proved this payload on
TagHash 80CA0CAF. It established that the bytes:
- serialize FileSize == 0x60;
- contain a structurally valid +0x08 DynamicArray<SkyRecord> with count == 0;
- contain every source-defined field through +0x60;
- store +FLT_MAX xyz,1 and -FLT_MAX xyz,1 sentinel bounds at +0x40/+0x50.

Crota TagHash 80D77525 independently resolves as the same class and serializes the
*identical 96-byte payload digest*. TagHash is therefore not part of the compatibility
condition: the evidence is the exact retail byte sequence itself. Every accepted copy
must still class-match 80801C1F and pass the full structural recheck below. Any other
short payload digest fails closed through the canonical parser.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_world_map_lighting_census as base

PROVEN_ORIGIN_TAG = '80CA0CAF'
PROVEN_SHA256 = 'ab5aed627609f799666d2308d344cb045a45aa16cc365b38312ad4f17c06755c'
PROVEN_PROBE_WORKFLOW_RUN = 34012180939
FLT_MAX = 3.4028234663852886e38
_original_parse_sky_collection = base.parse_sky_collection


def _sentinel(v, sign: int) -> bool:
    target = FLT_MAX if sign > 0 else -FLT_MAX
    return len(v) == 4 and v[0] == target and v[1] == target and v[2] == target and v[3] == 1.0


def parse_sky_collection(c, h, missing, missing_evidence, sky_models, violations):
    h = base.norm(h)
    b, src = c.payload(h)
    if b is None or len(b) != 0x60:
        return _original_parse_sky_collection(c, h, missing, missing_evidence, sky_models, violations)

    digest = base.sha(b)
    if digest != PROVEN_SHA256:
        out = {
            'hash': h,
            'target': base.meta(c, h, base.D1_SKY_COLLECTION),
            'source': src,
            'payload_bytes': len(b),
            'payload_sha256': digest,
            'status': 'UNPROVEN_SHORT_0X60_VARIANT',
        }
        violations.append(f'sky_collection:{h}:unproven_short_0x60:{digest}')
        return out

    target = base.meta(c, h, base.D1_SKY_COLLECTION)
    if not target['class_matches']:
        violations.append(f'sky_collection:{h}:class_mismatch')
        return {'hash': h, 'target': target, 'source': src, 'status': 'CLASS_MISMATCH'}

    file_size = base.i64(b, 0x00)
    arr = base.layer.dyn(b, 0x08, 0x80)
    v40 = base.vec4(b, 0x40)
    v50 = base.vec4(b, 0x50)
    ok = (
        file_size == 0x60 and arr.get('ok') and arr.get('count') == 0
        and arr.get('end') <= 0x60 and _sentinel(v40, +1) and _sentinel(v50, -1)
        and all(math.isfinite(x) for x in v40 + v50)
    )
    if not ok:
        violations.append(f'sky_collection:{h}:proven_payload_failed_structural_recheck')
        return {
            'hash': h, 'target': target, 'source': src,
            'payload_bytes': len(b), 'payload_sha256': digest,
            'file_size_i64': file_size, 'sky_records_array': arr,
            'vector40': v40, 'vector50': v50,
            'status': 'PROVEN_PAYLOAD_STRUCTURAL_RECHECK_FAILED',
        }

    return {
        'hash': h,
        'target': target,
        'source': src,
        'payload_bytes': len(b),
        'payload_sha256': digest,
        'file_size_i64': file_size,
        'sky_records_array': arr,
        'vector40': v40,
        'vector50': v50,
        'sky_records': [],
        'sky_record_count': 0,
        'retail_serialization_variant': 'D1_EMPTY_SKY_COLLECTION_0X60_SENTINEL_BOUNDS',
        'pinned_schema_declared_size': 0x68,
        'decoded_fields_end_offset': 0x60,
        'exact_payload_evidence': {
            'sha256': PROVEN_SHA256,
            'origin_tag_hash': PROVEN_ORIGIN_TAG,
            'probe_workflow_run': PROVEN_PROBE_WORKFLOW_RUN,
            'acceptance_basis': 'exact_payload_digest_plus_class_plus_structural_recheck',
        },
        'status': 'D1_SKY_COLLECTION_EMPTY_0X60_RETAIL_VARIANT_PRESERVED',
    }


base.parse_sky_collection = parse_sky_collection

if __name__ == '__main__':
    raise SystemExit(base.main())
