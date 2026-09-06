#!/usr/bin/env python3
"""Calibrate cross-platform D1 geometry invariants on already-proven gear pairs.

The historical Bungie TGXM and retail PS4 ``s_entity_model`` encodings do not keep
raw index-buffer counts identical.  Before using a relaxed matcher for the shared
Spektar glove/collar component, this tool measures which structural properties do
survive on exact item->geometry pairs whose PS4 ownership is independently proven.

A pair is accepted only when:
* its explicitly named PS4 FileHash is an ``s_entity_model``;
* both sides have the same ordered count of stage-0/highest-detail ACTIVE meshes;
* the active meshes have exactly the same ordered highest-detail part counts; and
* each paired active mesh vertex count differs by no more than ``--vertex-tolerance``.

Zero-active-LOD meshes and raw index counts are recorded but are deliberately not
used as the relaxed invariant.  No visual similarity, filenames, nearby hashes or
bone guesses participate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from d1_remote_model_tgxm_signature_match import (
    D1_ENTITY_MODEL_CLASS,
    LazyExactHashResolver,
    norm_hash,
    ps4_model_signature,
    tgxm_target_signature,
)
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar


def active(meshes: list[dict]) -> list[dict]:
    return [m for m in meshes if int(m['stage0_highest_part_count']) > 0]


def compare_pair(target: dict, candidate: dict, tolerance: int) -> dict:
    ta = active(target['meshes'])
    ca = active(candidate['meshes'])
    same_count = len(ta) == len(ca)
    n = min(len(ta), len(ca))
    target_parts = [int(m['stage0_highest_part_count']) for m in ta]
    candidate_parts = [int(m['stage0_highest_part_count']) for m in ca]
    stage_sequence_match = same_count and target_parts == candidate_parts
    deltas = [int(ca[i]['vertex_count']) - int(ta[i]['vertex_count']) for i in range(n)]
    vertex_within = same_count and all(abs(x) <= tolerance for x in deltas)
    return {
        'target_mesh_count': len(target['meshes']),
        'candidate_mesh_count': len(candidate['meshes']),
        'target_active_mesh_indices': [int(m['mesh_index']) for m in ta],
        'candidate_active_mesh_indices': [int(m['mesh_index']) for m in ca],
        'active_mesh_count_match': same_count,
        'target_active_stage0_highest_part_counts': target_parts,
        'candidate_active_stage0_highest_part_counts': candidate_parts,
        'active_stage0_highest_part_count_sequence_match': stage_sequence_match,
        'target_active_vertex_counts': [int(m['vertex_count']) for m in ta],
        'candidate_active_vertex_counts': [int(m['vertex_count']) for m in ca],
        'active_vertex_count_deltas_candidate_minus_target': deltas,
        'vertex_tolerance': tolerance,
        'active_vertex_counts_within_tolerance': vertex_within,
        'calibrated_active_structure_match': bool(stage_sequence_match and vertex_within),
        'target_full_index_counts': [int(m['index_count']) for m in target['meshes']],
        'candidate_full_index_counts': [int(m['index_count']) for m in candidate['meshes']],
        'target_active_stage0_index_count_sequences': [m['stage0_highest_index_counts'] for m in ta],
        'candidate_active_stage0_index_count_sequences': [m['stage0_highest_index_counts'] for m in ca],
    }


def parse_pair(raw: str) -> tuple[Path, str]:
    if '=' not in raw:
        raise argparse.ArgumentTypeError('--pair must be TGXM_PATH=PS4_MODEL_HASH')
    left, right = raw.rsplit('=', 1)
    return Path(left), norm_hash(right)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--pair', action='append', type=parse_pair, required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--vertex-tolerance', type=int, default=3)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()
    if a.vertex_tolerance < 0:
        raise SystemExit('--vertex-tolerance must be nonnegative')

    catalogs = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    resolver = LazyExactHashResolver(arc, catalogs, a.runtime)

    rows = []
    failures = []
    for tgxm_path, model_hash in a.pair:
        target = tgxm_target_signature(tgxm_path)
        view, e, raw = resolver.bytes(model_hash)
        if e['reference'].upper() != D1_ENTITY_MODEL_CLASS or e['type'] != 16 or e['subtype'] != 0:
            raise ValueError(f'{model_hash}: exact FileHash is not a PS4 s_entity_model')
        candidate = ps4_model_signature(resolver, model_hash, raw)
        cmp = compare_pair(target, candidate, a.vertex_tolerance)
        row = {
            'tgxm_path': str(tgxm_path),
            'tgxm_sha256': target['tgxm_sha256'],
            'tgxm_file_identifier': target['tgxm_file_identifier'],
            'ps4_model_hash': model_hash,
            'ps4_package_id': f'{int(view.h["pkg_id"]):04X}',
            'ps4_entry_index': int(e['index']),
            'comparison': cmp,
        }
        rows.append(row)
        if not cmp['calibrated_active_structure_match']:
            failures.append(model_hash)
        print(model_hash, target['tgxm_file_identifier'], 'active parts', cmp['target_active_stage0_highest_part_counts'],
              'verts', cmp['target_active_vertex_counts'], '->', cmp['candidate_active_vertex_counts'],
              'delta', cmp['active_vertex_count_deltas_candidate_minus_target'],
              'match', cmp['calibrated_active_structure_match'])

    max_abs_delta = max((abs(x) for r in rows for x in r['comparison']['active_vertex_count_deltas_candidate_minus_target']), default=0)
    rep = {
        'schema': 'd1_tgxm_ps4_active_signature_calibration/v1',
        'vertex_tolerance': a.vertex_tolerance,
        'pair_count': len(rows),
        'matched_pair_count': sum(r['comparison']['calibrated_active_structure_match'] for r in rows),
        'max_observed_active_vertex_count_delta': max_abs_delta,
        'pairs': rows,
        'failure_model_hashes': failures,
        'derived_search_rule': (
            'For source-proven D1 gear pairs, compare only stage-0/highest-detail active meshes in order. '
            'Require the exact active highest-detail part-count sequence and active per-mesh vertex-count delta '
            f'<= {a.vertex_tolerance}. Raw index counts are not cross-platform invariants.'
        ),
        'promotion_policy': (
            'This calibration can justify a candidate search rule only if every independently proven pair passes. '
            'A future shared-hand candidate still requires decoded geometry equivalence and exact retail ownership '
            'before inclusion in a Guardian export.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(rep, indent=2) + '\n')
    if failures:
        raise SystemExit('calibration failed for: ' + ', '.join(failures))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
