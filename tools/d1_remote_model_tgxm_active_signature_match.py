#!/usr/bin/env python3
"""Search retail D1 PS4 models using a source-calibrated TGXM active-mesh signature.

The strict raw-index matcher is intentionally not used here.  Five independently
proven masculine Spektar item pairs establish the cross-platform invariant used by
this tool:

* discard render meshes with zero stage-0/highest-detail parts;
* preserve the remaining active mesh order;
* require the exact ordered highest-detail part-count sequence; and
* require each active mesh vertex count to be within a calibrated tolerance.

For the five calibration pairs the maximum observed mobile-TGXM -> retail-PS4
active vertex-count delta is 3 vertices, while raw index counts differ materially.
Therefore index counts are recorded as corroborating evidence only and never used
to accept/reject a candidate.

This remains a candidate finder.  A match is not promoted to identity until decoded
geometry/topology and exact retail ownership are independently closed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_model_probe import D1_ENTITY_MODEL_CLASS, parse_model
from d1_guardian_stage_part_material_resolve import HIGHEST_LODS
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_model_tgxm_signature_match import (
    LazyExactHashResolver,
    linked_buffer_signature,
    norm_hash,
    tgxm_target_signature,
)
from d1_split_tar_extract import SplitHttpTar


def active_target_signature(target: dict[str, Any]) -> dict[str, Any]:
    rows = [m for m in target['meshes'] if int(m['stage0_highest_part_count']) > 0]
    if not rows:
        raise ValueError('TGXM target has no stage-0/highest-detail active meshes')
    return {
        'active_mesh_count': len(rows),
        'mesh_indices': [int(m['mesh_index']) for m in rows],
        'stage0_highest_part_counts': [int(m['stage0_highest_part_count']) for m in rows],
        'vertex_counts': [int(m['vertex_count']) for m in rows],
        'index_counts': [int(m['index_count']) for m in rows],
        'stage0_highest_index_count_sequences': [list(m['stage0_highest_index_counts']) for m in rows],
        'stage0_highest_primitive_type_sequences': [list(m['stage0_highest_primitive_types']) for m in rows],
    }


def inline_ps4_active_structure(model: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for mi, mesh in enumerate(model['meshes']):
        offsets = [int(x) for x in (mesh.get('stage_part_offsets_source_derived') or [])]
        if len(offsets) < 2:
            raise ValueError(f'mesh {mi}: missing PS4 stage-0 boundaries')
        start, end = offsets[0], offsets[1]
        parts = mesh['parts']
        if start < 0 or end < start or end > len(parts):
            raise ValueError(f'mesh {mi}: invalid PS4 stage0 [{start},{end})/{len(parts)}')
        selected = []
        for pi in range(start, end):
            p = parts[pi]
            if int(p['lod']) not in HIGHEST_LODS:
                continue
            selected.append({
                'part_index': pi,
                'index_offset': int(p['index_offset']),
                'index_count': int(p['index_count']),
                'primitive_type': int(p['primitive_type']),
                'lod': int(p['lod']),
                'gear_dye_change_color_index': int(p['gear_dye_change_color_index']),
            })
        if selected:
            rows.append({
                'mesh_index': mi,
                'stage0_start': start,
                'stage0_end_exclusive': end,
                'stage0_highest_part_count': len(selected),
                'stage0_highest_index_counts': [x['index_count'] for x in selected],
                'stage0_highest_primitive_types': [x['primitive_type'] for x in selected],
                'stage0_highest_parts': selected,
                'vertices1': mesh['vertices1'],
                'vertices2': mesh['vertices2'],
                'indices': mesh['indices'],
            })
    return rows


def resolve_active_buffers(
    resolver: LazyExactHashResolver,
    model_hash: str,
    active_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    out = []
    for row in active_rows:
        mi = int(row['mesh_index'])
        v0 = linked_buffer_signature(resolver, row['vertices1'], 'vertex')
        v1 = linked_buffer_signature(resolver, row['vertices2'], 'vertex')
        if v0['value_count'] != v1['value_count']:
            raise ValueError(
                f'{model_hash} mesh {mi}: PS4 vertex streams disagree '
                f'{v0["value_count"]}/{v1["value_count"]}'
            )
        ib = linked_buffer_signature(resolver, row['indices'], 'index')
        out.append({
            'mesh_index': mi,
            'vertex_count': int(v0['value_count']),
            'vertex_strides': [int(v0['stride']), int(v1['stride'])],
            'vertex_buffers': [v0, v1],
            'index_count': int(ib['value_count']),
            'index_value_byte_size': int(ib['value_byte_size']),
            'index_buffer': ib,
            'stage0_start': row['stage0_start'],
            'stage0_end_exclusive': row['stage0_end_exclusive'],
            'stage0_highest_part_count': row['stage0_highest_part_count'],
            'stage0_highest_index_counts': row['stage0_highest_index_counts'],
            'stage0_highest_primitive_types': row['stage0_highest_primitive_types'],
            'stage0_highest_parts': row['stage0_highest_parts'],
        })
    return out


def compare_active(target: dict[str, Any], candidate: list[dict[str, Any]], tolerance: int) -> dict[str, Any]:
    cparts = [int(x['stage0_highest_part_count']) for x in candidate]
    cverts = [int(x['vertex_count']) for x in candidate]
    same_count = len(candidate) == int(target['active_mesh_count'])
    part_sequence = same_count and cparts == target['stage0_highest_part_counts']
    n = min(len(cverts), len(target['vertex_counts']))
    deltas = [cverts[i] - int(target['vertex_counts'][i]) for i in range(n)]
    vertex_within = same_count and len(deltas) == len(target['vertex_counts']) and all(abs(x) <= tolerance for x in deltas)
    exact_vertex = same_count and len(deltas) == len(target['vertex_counts']) and all(x == 0 for x in deltas)
    return {
        'active_mesh_count_match': same_count,
        'active_stage0_highest_part_count_sequence_match': bool(part_sequence),
        'target_active_stage0_highest_part_counts': target['stage0_highest_part_counts'],
        'candidate_active_stage0_highest_part_counts': cparts,
        'target_active_vertex_counts': target['vertex_counts'],
        'candidate_active_vertex_counts': cverts,
        'active_vertex_count_deltas_candidate_minus_target': deltas,
        'vertex_tolerance': tolerance,
        'active_vertex_counts_within_tolerance': bool(vertex_within),
        'active_vertex_counts_exact': bool(exact_vertex),
        'calibrated_active_structure_match': bool(part_sequence and vertex_within),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--scan-package-id', action='append', type=lambda x: int(x, 0), required=True)
    ap.add_argument('--target-tgxm', type=Path, required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--vertex-tolerance', type=int, default=3)
    ap.add_argument('--keep-top', type=int, default=50)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()
    if a.vertex_tolerance < 0:
        raise SystemExit('--vertex-tolerance must be nonnegative')

    full_target = tgxm_target_signature(a.target_tgxm)
    target = active_target_signature(full_target)
    catalogs = load_catalogs(a.member_catalog)
    scan_ids = list(dict.fromkeys(a.scan_package_id))
    missing = [x for x in scan_ids if x not in catalogs]
    if missing:
        raise SystemExit('missing verified scan package catalogs: ' + ', '.join(f'{x:04X}' for x in missing))

    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    resolver = LazyExactHashResolver(arc, catalogs, a.runtime)

    scanned_models = 0
    active_count_prefilter = 0
    part_sequence_prefilter = 0
    resolved_candidates = []
    errors = []

    for pkg in scan_ids:
        view = resolver.view(pkg)
        for e in view.entries:
            if e['type'] != 16 or e['subtype'] != 0 or e['reference'].upper() != D1_ENTITY_MODEL_CLASS:
                continue
            scanned_models += 1
            tag = e['tag_hash'].upper()
            try:
                raw = view.entry(e['index'])
                model = parse_model(raw, 'PS4')
                active = inline_ps4_active_structure(model)
                if len(active) != target['active_mesh_count']:
                    continue
                active_count_prefilter += 1
                cparts = [int(x['stage0_highest_part_count']) for x in active]
                if cparts != target['stage0_highest_part_counts']:
                    continue
                part_sequence_prefilter += 1
                resolved = resolve_active_buffers(resolver, tag, active)
                cmp = compare_active(target, resolved, a.vertex_tolerance)
                # Keep every exact part-sequence candidate so the report documents
                # how selective the calibrated vertex invariant is.
                resolved_candidates.append({
                    'package_id': f'{pkg:04X}',
                    'entry_index': int(e['index']),
                    'tag_hash': tag,
                    'model_file_size': int(e['file_size']),
                    'total_mesh_count': int(model['mesh_count']),
                    'active_mesh_indices': [int(x['mesh_index']) for x in resolved],
                    'comparison': cmp,
                    'active_meshes': resolved,
                })
                if cmp['calibrated_active_structure_match']:
                    print('CALIBRATED_ACTIVE_MATCH', f'{pkg:04X}', tag,
                          'active_meshes', [x['mesh_index'] for x in resolved],
                          'verts', cmp['candidate_active_vertex_counts'],
                          'delta', cmp['active_vertex_count_deltas_candidate_minus_target'])
            except Exception as ex:
                errors.append({
                    'package_id': f'{pkg:04X}',
                    'tag_hash': tag,
                    'entry_index': int(e['index']),
                    'error': repr(ex),
                })

    def rank(row: dict[str, Any]) -> tuple:
        cmp = row['comparison']
        deltas = cmp['active_vertex_count_deltas_candidate_minus_target']
        distance = sum(abs(int(x)) for x in deltas) if len(deltas) == len(target['vertex_counts']) else 10**9
        return (
            0 if cmp['calibrated_active_structure_match'] else 1,
            distance,
            row['package_id'],
            row['tag_hash'],
        )

    resolved_candidates.sort(key=rank)
    matches = [x for x in resolved_candidates if x['comparison']['calibrated_active_structure_match']]
    rep = {
        'schema': 'd1_remote_model_tgxm_active_signature_match/v1',
        'calibration_basis': {
            'workflow_run': 34041222260,
            'artifact_id': 9991725578,
            'proven_pair_count': 5,
            'max_observed_abs_active_vertex_delta': 3,
            'rule': (
                'Drop zero-highest-detail meshes; require exact ordered active highest-detail part-count sequence; '
                'require each active vertex count within configured tolerance. Raw index counts are non-invariant.'
            ),
        },
        'target': full_target,
        'target_active_signature': target,
        'vertex_tolerance': a.vertex_tolerance,
        'scan_package_ids': [f'{x:04X}' for x in scan_ids],
        'scanned_entity_model_count': scanned_models,
        'active_mesh_count_prefilter_count': active_count_prefilter,
        'active_part_sequence_prefilter_count': part_sequence_prefilter,
        'resolved_part_sequence_candidate_count': len(resolved_candidates),
        'calibrated_active_structure_match_count': len(matches),
        'matches': matches,
        'top_part_sequence_candidates': resolved_candidates[:max(0, a.keep_top)],
        'error_count': len(errors),
        'errors': errors,
        'policy': (
            'A calibrated active-structure match is candidate evidence only. Identity promotion requires decoded '
            'geometry/topology equivalence plus exact retail ownership/composition evidence. No filenames, visual '
            'similarity, neighboring FileHashes, bounds proximity or guessed bone semantics affect matching.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(rep, indent=2) + '\n')
    print('TARGET_ACTIVE_PARTS', target['stage0_highest_part_counts'], 'VERTS', target['vertex_counts'])
    print('SCAN', ','.join(rep['scan_package_ids']), 'MODELS', scanned_models,
          'ACTIVE_COUNT', active_count_prefilter, 'PART_SEQUENCE', part_sequence_prefilter,
          'RESOLVED', len(resolved_candidates), 'MATCHES', len(matches), 'ERRORS', len(errors))
    for x in resolved_candidates[:10]:
        c = x['comparison']
        print('TOP', x['package_id'], x['tag_hash'], 'meshes', x['active_mesh_indices'],
              'verts', c['candidate_active_vertex_counts'],
              'delta', c['active_vertex_count_deltas_candidate_minus_target'],
              'match', c['calibrated_active_structure_match'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
