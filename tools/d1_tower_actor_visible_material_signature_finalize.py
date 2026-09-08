#!/usr/bin/env python3
"""Finalize production-visible material signatures for all 13 Tower actor models.

This combines four already-bounded proof products:
1. the 918-placement actor material-signature census;
2. the green stage-0/highest-detail actor model export;
3. the exact 80C88434 nine-SMap census;
4. the exact 80C88434 direct EntitySK resource selector probe.

Two v1 frontier cases are resolved without weakening the retail proof boundary:

* 80C7B00E: the green visible model export contains zero parts with a nonnegative
  variant_shader_index, so there is no visible external selector to evaluate.

* 80C88434: all 9/9 source-owned SMapDataEntry DataResource pointers are null and
  there is no S152 placement configuration. The three direct EntitySK resource graphs
  contain no selector key/value occurrence outside the shared model-parent definition
  bank 80C883FD. Therefore the portable visual adapter evaluates the already-corpus-
  calibrated descriptor rule with the empty source-owned configuration. Exactly one
  member has empty list-A, yielding fallback Material 808765F3.

This is an export/Blender adapter closure only. It explicitly does NOT claim that the
D1 retail descriptor evaluator execution path is source-closed, and it does not select
runtime-active scenario, D912 group, Xur location, or animation state.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

MODEL_NO_VISIBLE_SELECTOR = '80C7B00E'
MODEL_EMPTY_CONFIG = '80C88434'
EMPTY_CONFIG_PARENT = '80C883FD'
EMPTY_CONFIG_FALLBACK = '808765F3'
EXPECTED_VARIANT_COUNTS = {'809D8104': 5, '80C885E3': 8, '80C88CEF': 7}
SELECTOR_DOMAIN = {'26170C92', 'E32027FC', 'AE1880F4', '6093B6B7', '871AC0EA'}


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def visible_external_indices(export: dict, model: str) -> list[int]:
    out = set()
    for m in export.get('models', []):
        if norm(m.get('model')) != model:
            continue
        for r in m.get('ranges', []):
            for p in r.get('parts', []):
                vi = int(p.get('variant_shader_index', -1))
                if vi >= 0:
                    out.add(vi)
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--signature-frontier', type=Path, required=True)
    ap.add_argument('--model-export', type=Path, required=True)
    ap.add_argument('--smap-frontier', type=Path, required=True)
    ap.add_argument('--entity-selector-probe', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    src = json.loads(a.signature_frontier.read_text())
    export = json.loads(a.model_export.read_text())
    smap = json.loads(a.smap_frontier.read_text())
    selector = json.loads(a.entity_selector_probe.read_text())
    violations: list[str] = []

    if src.get('schema_version') != 1 or int(src.get('actor_model_count', 0)) != 13:
        violations.append('signature_frontier_shape_mismatch')
    expected_old_violation = (
        "80C7B00E:80C7B005:parse_graph:ValueError('80C7B005: exact +0x50 switch candidate count 0')"
    )
    old_viol = list(src.get('violations') or [])
    if old_viol != [expected_old_violation]:
        violations.append(f'unexpected_signature_frontier_violations:{old_viol}')
    if export.get('status') != 'D1_WORLD_ARTICULATED_MODEL_SET_COMPLETE' or export.get('errors'):
        violations.append('model_export_not_green')
    if smap.get('status') != 'D1_TOWER_80C88434_SMAP_FRONTIER_EXACT' or smap.get('violations'):
        violations.append('80C88434_smap_frontier_not_green')
    if selector.get('status') != 'D1_TOWER_80C88434_ENTITY_SELECTOR_PROBE_COMPLETE' or selector.get('violations'):
        violations.append('80C88434_entity_selector_probe_not_green')

    rows = {norm(x.get('model')): copy.deepcopy(x) for x in src.get('models', [])}
    if set(rows) != {norm(m.get('model')) for m in export.get('models', [])}:
        violations.append('signature_export_model_set_mismatch')

    # Close 80C7B00E from the actual visible export, not from a missing permutation graph.
    no_sel_vis = visible_external_indices(export, MODEL_NO_VISIBLE_SELECTOR)
    if no_sel_vis:
        violations.append(f'{MODEL_NO_VISIBLE_SELECTOR}:unexpected_visible_external_groups:{no_sel_vis}')
    r = rows.get(MODEL_NO_VISIBLE_SELECTOR)
    if r is None:
        violations.append(f'{MODEL_NO_VISIBLE_SELECTOR}:missing_frontier_row')
    else:
        r.update({
            'visible_external_variant_shader_indices': [],
            'visible_external_group_count': 0,
            'placement_calibration_row_count': 0,
            'unique_source_configuration_count': 0,
            'unique_visible_external_signature_count': 1,
            'status': 'no_visible_external_selector_groups',
            'signatures': [{
                'signature_index': 0,
                'visible_external_materials': [],
                'placement_count': None,
            }],
            'closure_evidence': {
                'green_model_export_has_zero_nonnegative_variant_shader_indices': True,
                'permutation_graph_required_for_visible_export': False,
            },
        })
        r.pop('error', None)

    # Close 80C88434 as an empty-source-config fallback visual adapter.
    smap_rows = list(smap.get('placements') or [])
    if len(smap_rows) != 9:
        violations.append(f'{MODEL_EMPTY_CONFIG}:expected_9_smap_rows_got_{len(smap_rows)}')
    for x in smap_rows:
        dr = x.get('data_resource') or {}
        if dr.get('null') is not True or x.get('has_s152'):
            violations.append(f'{MODEL_EMPTY_CONFIG}:nonempty_placement_config:{x}')

    sel_rows = list(selector.get('entities') or [])
    if len(sel_rows) != 3 or any(int(x.get('resource_count', -1)) != 40 for x in sel_rows):
        violations.append(f'{MODEL_EMPTY_CONFIG}:entity_resource_shape_mismatch')
    for hit in selector.get('selector_hit_summary') or []:
        if norm(hit.get('hash')) not in SELECTOR_DOMAIN:
            continue
        if hit.get('scope') != 'resource' or norm(hit.get('resource_hash')) != EMPTY_CONFIG_PARENT:
            violations.append(f'{MODEL_EMPTY_CONFIG}:selector_literal_outside_shared_parent:{hit}')

    group = smap.get('visible_variant0_group') or {}
    if int(group.get('variant_shader_index', -1)) != 0:
        violations.append(f'{MODEL_EMPTY_CONFIG}:variant0_group_missing')
    members = list(group.get('members') or [])
    empty = [m for m in members if not m.get('list_a_pairs')]
    if len(empty) != 1:
        violations.append(f'{MODEL_EMPTY_CONFIG}:empty_list_A_member_count:{len(empty)}')
        fallback = None
    else:
        fallback = norm(empty[0].get('material_tag_hash'))
        if fallback != EMPTY_CONFIG_FALLBACK:
            violations.append(f'{MODEL_EMPTY_CONFIG}:fallback_material:{fallback}')
    nonempty = [m for m in members if m.get('list_a_pairs')]
    if len(members) != 4 or len(nonempty) != 3:
        violations.append(f'{MODEL_EMPTY_CONFIG}:unexpected_variant0_member_shape')

    r = rows.get(MODEL_EMPTY_CONFIG)
    if r is None:
        violations.append(f'{MODEL_EMPTY_CONFIG}:missing_frontier_row')
    elif fallback is not None:
        r.update({
            'visible_external_variant_shader_indices': [0],
            'visible_external_group_count': 1,
            'placement_calibration_row_count': 0,
            'unique_source_configuration_count': 1,
            'unique_visible_external_signature_count': 1,
            'status': 'empty_source_configuration_fallback_visual_signature',
            'signatures': [{
                'signature_index': 0,
                'visible_external_materials': [{
                    'variant_shader_index': 0,
                    'material_tag_hash': fallback,
                }],
                'placement_count': 9,
                'source_configuration_pairs': [],
            }],
            'closure_evidence': {
                'smap_record_count': 9,
                'all_smap_data_resources_null': True,
                's152_configuration_present': False,
                'direct_entity_selector_literals_outside_shared_parent': False,
                'shared_parent_resource': EMPTY_CONFIG_PARENT,
                'candidate_rule_input_configuration': [],
                'unique_empty_list_A_fallback_material': fallback,
            },
        })
        r.pop('unresolved_visible_groups', None)
        r.pop('configuration_independent_groups', None)

    # Validate the three genuinely placement-varying actor model families.
    for model, count in EXPECTED_VARIANT_COUNTS.items():
        r = rows.get(model)
        if r is None:
            violations.append(f'{model}:missing_model_row')
            continue
        if r.get('status') != 'calibrated_placement_specific_visible_signatures':
            violations.append(f'{model}:unexpected_status:{r.get("status")}')
        if int(r.get('unique_visible_external_signature_count', -1)) != count:
            violations.append(f'{model}:expected_{count}_signatures_got_{r.get("unique_visible_external_signature_count")}')
        if len(r.get('signatures') or []) != count:
            violations.append(f'{model}:signature_row_count_mismatch')

    ordered = [rows[k] for k in sorted(rows)]
    unresolved = [x['model'] for x in ordered if x.get('status') in {
        'graph_unavailable', 'fail_closed_missing_configuration_for_non_equivalent_visible_group'
    }]
    total_signatures = sum(int(x.get('unique_visible_external_signature_count') or 0) for x in ordered)
    placement_variant_models = [x['model'] for x in ordered if int(x.get('unique_visible_external_signature_count') or 0) > 1]
    single_signature_models = [x['model'] for x in ordered if int(x.get('unique_visible_external_signature_count') or 0) == 1]

    if unresolved:
        violations.append(f'unresolved_models_after_finalize:{unresolved}')
    if len(ordered) != 13:
        violations.append(f'expected_13_final_rows_got_{len(ordered)}')
    if set(placement_variant_models) != set(EXPECTED_VARIANT_COUNTS):
        violations.append(f'placement_variant_model_set:{placement_variant_models}')

    complete = not violations and len(ordered) == 13 and not unresolved
    out = {
        'schema_version': 2,
        'status': 'D1_TOWER_ACTOR_VISIBLE_MATERIAL_SIGNATURES_COMPLETE' if complete else 'D1_TOWER_ACTOR_VISIBLE_MATERIAL_SIGNATURES_FINALIZE_VIOLATIONS',
        'actor_model_count': len(ordered),
        'production_closed_model_count': len(ordered) - len(unresolved),
        'placement_variant_model_count': len(placement_variant_models),
        'placement_variant_models': placement_variant_models,
        'single_signature_model_count': len(single_signature_models),
        'single_signature_models': single_signature_models,
        'total_unique_visible_external_signature_count': total_signatures,
        'candidate_rule_visible_group_evaluation_count_from_corpus': int(src.get('candidate_rule_visible_group_evaluation_count', 0)),
        'models': ordered,
        'violations': violations,
        'proof': {
            'all_13_actor_visible_material_signatures_production_closed': complete,
            '80C7B00E_has_no_visible_external_selector_groups': not no_sel_vis,
            '80C88434_all_9_smap_data_resources_null': len(smap_rows) == 9 and all((x.get('data_resource') or {}).get('null') is True for x in smap_rows),
            '80C88434_direct_entity_selector_literals_absent_outside_shared_parent': not any(
                norm(h.get('hash')) in SELECTOR_DOMAIN and (h.get('scope') != 'resource' or norm(h.get('resource_hash')) != EMPTY_CONFIG_PARENT)
                for h in selector.get('selector_hit_summary') or []
            ),
            '80C88434_empty_config_unique_fallback_material': fallback,
            'candidate_rule_previously_calibrated_70281_of_70281_unique': True,
            'D1_retail_descriptor_evaluator_source_closed': False,
            'runtime_active_scenario_selected': False,
            'runtime_active_D912_group_selected': False,
            'runtime_active_xur_location_selected': False,
            'runtime_actor_animation_state_selected': False,
        },
        'gates': {
            'D1_retail_descriptor_evaluator_source_closed': False,
            'runtime_active_scenario_selected': False,
            'runtime_active_D912_group_selected': False,
            'runtime_active_xur_location_selected': False,
            'runtime_actor_animation_state_selected': False,
            'E6_80C885E6_live_selection_proven': False,
            'E7_80C885E7_live_selection_proven': False,
            'E8_80C885E8_live_selection_proven': False,
        },
        'policy': (
            'This report closes only portable visible-material signatures for the 13 Tower actor models. '
            'The three multi-signature families preserve every source-typed placement-specific signature. '
            '80C7B00E requires no external material evaluation because its visible export has no external-selector part. '
            '80C88434 is adapted with the empty source-owned configuration because all nine placement DataResources are null '
            'and its direct EntitySK graphs contain no discriminating selector value; the corpus-calibrated rule therefore '
            'selects the unique empty-list-A fallback 808765F3. This does not promote the D1 retail evaluator semantics or any runtime activation gate.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'],
        'actor_model_count': out['actor_model_count'],
        'production_closed_model_count': out['production_closed_model_count'],
        'placement_variant_models': out['placement_variant_models'],
        'single_signature_model_count': out['single_signature_model_count'],
        'total_unique_visible_external_signature_count': out['total_unique_visible_external_signature_count'],
        '80C88434_fallback': fallback,
        'violations': violations,
        'gates': out['gates'],
    }, indent=2))
    return 0 if complete else 2


if __name__ == '__main__':
    raise SystemExit(main())
