#!/usr/bin/env python3
"""Resolve exact FileHash edges serialized inside the archived 80C88434 EntityResources.

This is deliberately a *direct-edge* census.  The source payloads are the exact 42
EntityResource payloads already archived by the 80C88434 resource-class census.
Every aligned u32 is treated only as a candidate FileHash; it is promoted to an edge
only when the banked D1 FileHash decoder routes it to a verified package family and
an entry with that exact TagHash exists in the current retail package metadata.

For small direct targets we additionally inspect one payload hop and record exact
Texture2DHeader / SDye_D1 children.  This is discovery evidence only: no runtime
binding, default-resource value, or dye ownership is inferred from proximity.
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar

NULLS = {'00000000', 'FFFFFFFF'}
DYE_CLASS = '80801AF4'
MATERIAL_CLASS = '80801AD7'
ENTITY_CLASS = '80800734'


def norm(x) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def package_of(h: str) -> int:
    return filehash_pkg_index(int(norm(h), 16))[0]


def classify(meta: dict) -> str:
    ref = norm(meta.get('reference', 'FFFFFFFF'))
    typ = int(meta.get('type', -1))
    sub = int(meta.get('subtype', -1))
    if ref == DYE_CLASS:
        return 'd1_dye'
    if ref == MATERIAL_CLASS:
        return 'roi_material'
    if ref == ENTITY_CLASS:
        return 'entity'
    if typ == 32 and sub in (1, 2):
        return 'texture_header'
    if typ == 1:
        return 'raw_or_texture_backing'
    if typ == 16:
        return 'structured_tag'
    return 'other'


def scan_exact_edges(c: RemoteCorpus, payload: bytes, source: str) -> tuple[list[dict], int]:
    rows = []
    candidate_count = 0
    for off in range(0, len(payload) - 3, 4):
        value = struct.unpack_from('<I', payload, off)[0]
        h = f'{value:08X}'
        if h in NULLS:
            continue
        # Cheap reject before touching remote metadata.  A valid D1 FileHash must
        # route to one of the verified current package families.
        try:
            pkg = package_of(h)
        except Exception:
            continue
        if pkg not in c.catalogs:
            continue
        candidate_count += 1
        meta = c.entry_meta(h)
        if meta is None or norm(meta.get('tag_hash', '')) != h:
            continue
        rows.append({
            'source': source,
            'offset': off,
            'target': h,
            'package_id': f'{pkg:04X}',
            'entry_index': int(meta['index']),
            'type': int(meta['type']),
            'subtype': int(meta['subtype']),
            'reference': norm(meta.get('reference', 'FFFFFFFF')),
            'file_size': int(meta.get('file_size', 0)),
            'classification': classify(meta),
        })
    return rows, candidate_count


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--payload-dir', type=Path, required=True)
    ap.add_argument('--resource-census', type=Path, required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--small-target-max-bytes', type=int, default=16384)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    violations = []
    census = json.loads(a.resource_census.read_text())
    if census.get('status') != 'D1_TOWER_80C88434_RESOURCE_CLASS_CENSUS_EXACT':
        violations.append('source resource census is not exact')
    expected = sorted(norm(x['resource_hash']) for x in census.get('unique_resources', []))
    payload_paths = sorted(a.payload_dir.glob('*.bin'))
    actual = sorted(p.stem.upper() for p in payload_paths)
    if expected != actual:
        violations.append(f'payload set mismatch expected={len(expected)} actual={len(actual)}')

    catalogs = load_catalogs(a.member_catalog)
    arc = SplitHttpTar(
        [f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=90,
    )
    c = RemoteCorpus(arc, catalogs, a.runtime)

    direct = []
    candidate_count = 0
    for p in payload_paths:
        rows, n = scan_exact_edges(c, p.read_bytes(), p.stem.upper())
        candidate_count += n
        direct.extend(rows)

    # Deduplicate target identities while retaining every physical source/offset edge.
    target_hashes = sorted({x['target'] for x in direct})
    target_rows = []
    by_target = collections.defaultdict(list)
    for x in direct:
        by_target[x['target']].append(x)
    for h in target_hashes:
        first = by_target[h][0]
        target_rows.append({
            'target': h,
            'package_id': first['package_id'],
            'entry_index': first['entry_index'],
            'type': first['type'],
            'subtype': first['subtype'],
            'reference': first['reference'],
            'file_size': first['file_size'],
            'classification': first['classification'],
            'physical_edge_count': len(by_target[h]),
            'sources': sorted({x['source'] for x in by_target[h]}),
        })

    # One bounded payload hop.  This is useful for wrappers/containers while staying
    # far away from an unconstrained dependency-graph traversal.
    second_hop = []
    second_candidate_count = 0
    inspected = []
    for t in target_rows:
        if t['classification'] not in ('structured_tag', 'd1_dye', 'roi_material', 'entity'):
            continue
        if t['file_size'] <= 0 or t['file_size'] > a.small_target_max_bytes:
            continue
        payload, owner = c.payload(t['target'])
        if payload is None:
            violations.append(f"{t['target']}: direct target payload unavailable")
            continue
        inspected.append({'target': t['target'], 'bytes': len(payload), 'owner': owner})
        rr, n = scan_exact_edges(c, payload, t['target'])
        second_candidate_count += n
        # Keep only semantically high-value second-hop endpoints plus self-describing
        # structured children; ordinary graph noise stays outside this checkpoint.
        for x in rr:
            if x['classification'] in ('texture_header', 'd1_dye', 'roi_material'):
                second_hop.append(x)

    direct_class_hist = collections.Counter(x['classification'] for x in direct)
    target_class_hist = collections.Counter(x['classification'] for x in target_rows)
    ref_hist = collections.Counter(x['reference'] for x in target_rows)
    type_hist = collections.Counter(f"{x['type']}:{x['subtype']}" for x in target_rows)
    package_hist = collections.Counter(x['package_id'] for x in target_rows)

    direct_textures = sorted({x['target'] for x in direct if x['classification'] == 'texture_header'})
    direct_dyes = sorted({x['target'] for x in direct if x['classification'] == 'd1_dye'})
    direct_materials = sorted({x['target'] for x in direct if x['classification'] == 'roi_material'})
    second_textures = sorted({x['target'] for x in second_hop if x['classification'] == 'texture_header'})
    second_dyes = sorted({x['target'] for x in second_hop if x['classification'] == 'd1_dye'})

    out = {
        'schema_version': 1,
        'status': 'D1_TOWER_80C88434_RESOURCE_EDGE_METADATA_EXACT' if not violations else 'D1_TOWER_80C88434_RESOURCE_EDGE_METADATA_PARTIAL',
        'source_resource_count': len(payload_paths),
        'aligned_words_routed_to_known_package_count': candidate_count,
        'exact_direct_edge_count': len(direct),
        'unique_direct_target_count': len(target_rows),
        'direct_classification_histogram': dict(sorted(direct_class_hist.items())),
        'unique_target_classification_histogram': dict(sorted(target_class_hist.items())),
        'unique_target_type_subtype_histogram': dict(sorted(type_hist.items())),
        'unique_target_reference_histogram': dict(sorted(ref_hist.items())),
        'unique_target_package_histogram': dict(sorted(package_hist.items())),
        'direct_texture_headers': direct_textures,
        'direct_d1_dyes': direct_dyes,
        'direct_roi_materials': direct_materials,
        'small_direct_targets_inspected': inspected,
        'second_hop_high_value_edges': second_hop,
        'second_hop_texture_headers': second_textures,
        'second_hop_d1_dyes': second_dyes,
        'second_hop_candidate_count': second_candidate_count,
        'direct_edges': direct,
        'unique_direct_targets': target_rows,
        'violations': violations,
        'policy': 'Only exact TagHash matches in verified current package metadata are edges. Second-hop inspection is bounded to small direct structured targets. No runtime t4/API15 binding or dye ownership is inferred from an edge, adjacency, class proximity, or texture format.',
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'],
        'source_resource_count': out['source_resource_count'],
        'exact_direct_edge_count': out['exact_direct_edge_count'],
        'unique_direct_target_count': out['unique_direct_target_count'],
        'direct_texture_headers': direct_textures,
        'direct_d1_dyes': direct_dyes,
        'direct_roi_materials': direct_materials,
        'second_hop_texture_headers': second_textures,
        'second_hop_d1_dyes': second_dyes,
        'violations': violations,
    }, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
