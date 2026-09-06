#!/usr/bin/env python3
"""Search retail D1 PS4 s_entity_model meshes for independently calibrated TGXM components.

This matcher is the split-component counterpart to
``d1_remote_model_tgxm_active_signature_match.py``.  It is used only after a
whole-model calibrated search has been exhausted.  Each stage-0/highest-detail
TGXM mesh is treated as an independent structural component and matched against
every active PS4 model mesh using the same cross-platform calibration already
proved on five exact Spektar TGXM -> PS4 pairs:

* exact stage-0/highest-detail part count for the component; and
* PS4 vertex count within the calibrated +/-3-vertex tolerance.

Raw index counts remain non-invariant and are recorded only as corroborating
evidence.  Mesh order, model names, neighboring FileHashes, visual similarity,
bounds proximity and guessed bone semantics never participate.

A component match is candidate evidence only.  It does not prove that multiple
matched components compose the same retail item; that requires an exact serialized
ownership/composition edge plus decoded geometry/topology confirmation.
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
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_model_tgxm_active_signature_match import (
    active_target_signature,
    inline_ps4_active_structure,
    resolve_active_buffers,
)
from d1_remote_model_tgxm_signature_match import LazyExactHashResolver, tgxm_target_signature
from d1_split_tar_extract import SplitHttpTar


def target_components(full_target: dict[str, Any]) -> list[dict[str, Any]]:
    active = active_target_signature(full_target)
    out = []
    for slot, mi in enumerate(active['mesh_indices']):
        m = full_target['meshes'][mi]
        out.append({
            'component_slot': slot,
            'source_mesh_index': int(mi),
            'stage0_highest_part_count': int(m['stage0_highest_part_count']),
            'vertex_count': int(m['vertex_count']),
            'index_count': int(m['index_count']),
            'stage0_highest_index_counts': list(m['stage0_highest_index_counts']),
            'stage0_highest_primitive_types': list(m['stage0_highest_primitive_types']),
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--scan-package-id', action='append', type=lambda x: int(x, 0), required=True)
    ap.add_argument('--target-tgxm', type=Path, required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--vertex-tolerance', type=int, default=3)
    ap.add_argument('--keep-top-per-component', type=int, default=100)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()
    if a.vertex_tolerance < 0:
        raise SystemExit('--vertex-tolerance must be nonnegative')

    full_target = tgxm_target_signature(a.target_tgxm)
    comps = target_components(full_target)
    if len(comps) < 2:
        raise SystemExit('split-component search requires at least two active target meshes')

    catalogs = load_catalogs(a.member_catalog)
    scan_ids = list(dict.fromkeys(a.scan_package_id))
    missing = [x for x in scan_ids if x not in catalogs]
    if missing:
        raise SystemExit('missing verified scan package catalogs: ' + ', '.join(f'{x:04X}' for x in missing))

    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    resolver = LazyExactHashResolver(arc, catalogs, a.runtime)

    scanned_models = 0
    scanned_active_meshes = 0
    part_count_prefilters = [0 for _ in comps]
    resolved_by_component: list[list[dict[str, Any]]] = [[] for _ in comps]
    errors: list[dict[str, Any]] = []

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
            except Exception as ex:
                errors.append({
                    'package_id': f'{pkg:04X}',
                    'tag_hash': tag,
                    'entry_index': int(e['index']),
                    'phase': 'parse_model_active_structure',
                    'error': repr(ex),
                })
                continue

            scanned_active_meshes += len(active)
            for row in active:
                pc = int(row['stage0_highest_part_count'])
                for ci, target in enumerate(comps):
                    if pc != int(target['stage0_highest_part_count']):
                        continue
                    part_count_prefilters[ci] += 1
                    try:
                        resolved = resolve_active_buffers(resolver, tag, [row])[0]
                    except Exception as ex:
                        errors.append({
                            'package_id': f'{pkg:04X}',
                            'tag_hash': tag,
                            'entry_index': int(e['index']),
                            'model_mesh_index': int(row['mesh_index']),
                            'target_component_slot': ci,
                            'phase': 'resolve_active_buffers',
                            'error': repr(ex),
                        })
                        continue
                    delta = int(resolved['vertex_count']) - int(target['vertex_count'])
                    match = abs(delta) <= a.vertex_tolerance
                    rec = {
                        'package_id': f'{pkg:04X}',
                        'entry_index': int(e['index']),
                        'tag_hash': tag,
                        'model_file_size': int(e['file_size']),
                        'total_mesh_count': int(model['mesh_count']),
                        'model_active_mesh_count': len(active),
                        'model_mesh_index': int(row['mesh_index']),
                        'target_component_slot': ci,
                        'target_source_mesh_index': int(target['source_mesh_index']),
                        'target_stage0_highest_part_count': int(target['stage0_highest_part_count']),
                        'candidate_stage0_highest_part_count': int(resolved['stage0_highest_part_count']),
                        'target_vertex_count': int(target['vertex_count']),
                        'candidate_vertex_count': int(resolved['vertex_count']),
                        'vertex_delta_candidate_minus_target': delta,
                        'vertex_tolerance': a.vertex_tolerance,
                        'calibrated_component_structure_match': match,
                        'active_mesh': resolved,
                    }
                    resolved_by_component[ci].append(rec)
                    if match:
                        print('CALIBRATED_COMPONENT_MATCH', f'{pkg:04X}', tag,
                              'model_mesh', row['mesh_index'], 'component', ci,
                              'parts', pc, 'verts', resolved['vertex_count'], 'delta', delta)

    def rank(x: dict[str, Any]) -> tuple:
        return (
            0 if x['calibrated_component_structure_match'] else 1,
            abs(int(x['vertex_delta_candidate_minus_target'])),
            x['package_id'], x['tag_hash'], int(x['model_mesh_index']),
        )

    component_reports = []
    total_matches = 0
    for ci, target in enumerate(comps):
        rows = sorted(resolved_by_component[ci], key=rank)
        matches = [x for x in rows if x['calibrated_component_structure_match']]
        total_matches += len(matches)
        component_reports.append({
            'target': target,
            'part_count_prefilter_count': part_count_prefilters[ci],
            'resolved_candidate_count': len(rows),
            'calibrated_component_structure_match_count': len(matches),
            'matches': matches,
            'top_candidates': rows[:max(0, a.keep_top_per_component)],
        })

    rep = {
        'schema': 'd1_remote_model_tgxm_component_signature_match/v1',
        'calibration_basis': {
            'workflow_run': 34041222260,
            'artifact_id': 9991725578,
            'proven_pair_count': 5,
            'max_observed_abs_active_vertex_delta': 3,
            'rule': (
                'For each active target mesh independently, require exact stage-0/highest-detail part count and '
                'vertex count within configured tolerance. Raw index counts are non-invariant.'
            ),
        },
        'target': full_target,
        'target_components': comps,
        'vertex_tolerance': a.vertex_tolerance,
        'scan_package_ids': [f'{x:04X}' for x in scan_ids],
        'scanned_entity_model_count': scanned_models,
        'scanned_active_mesh_count': scanned_active_meshes,
        'component_reports': component_reports,
        'total_calibrated_component_structure_match_count': total_matches,
        'error_count': len(errors),
        'errors': errors,
        'policy': (
            'A component signature hit is candidate evidence only. It does not establish that multiple components '
            'belong to one retail composition, nor does it establish asset identity. Promotion requires decoded '
            'geometry/topology equivalence and exact serialized ownership/composition evidence.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(rep, indent=2) + '\n')
    print('TARGET_COMPONENTS', [(x['stage0_highest_part_count'], x['vertex_count']) for x in comps])
    print('SCAN', ','.join(rep['scan_package_ids']), 'MODELS', scanned_models, 'ACTIVE_MESHES', scanned_active_meshes,
          'PREFILTERS', part_count_prefilters, 'MATCHES', total_matches, 'ERRORS', len(errors))
    for ci, cr in enumerate(component_reports):
        for x in cr['top_candidates'][:10]:
            print('TOP', ci, x['package_id'], x['tag_hash'], 'mesh', x['model_mesh_index'],
                  'verts', x['candidate_vertex_count'], 'delta', x['vertex_delta_candidate_minus_target'],
                  'match', x['calibrated_component_structure_match'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
