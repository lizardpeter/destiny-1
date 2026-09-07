#!/usr/bin/env python3
"""Close visible material signatures for the 13 source-owned Tower actor models.

Inputs are two already-green proof artifacts:
- exact 918-placement S152/model-switch-bank calibration corpus;
- exact 13-model articulated actor visual export/plan.

For each actor model this tool reconstructs the exact model-parent permutation graph
from retail bytes and restricts evaluation to the *visible* stage-0/highest-detail
variant_shader_index values emitted by the articulated model exporter.

For models represented in the 918-placement corpus, the already-calibrated candidate
rule is evaluated for every source-typed placement configuration:

  satisfied := descriptor list-A pairs are a subset of the placement configuration
  winner    := unique satisfied member with greatest list-A pair count

The tool then counts distinct visible external-material signatures. A model with one
signature can be exported once. A model with multiple signatures requires explicit
placement/configuration variants; they are preserved rather than collapsed.

Models absent from the placement corpus are considered configuration-independent only
when every visible external group is render-equivalent without evaluating a selector
(i.e. all serialized members in that group name the same Material). Any other case
remains fail-closed.

This is a Blender/export adapter closure. It does not promote the descriptor rule to
source-closed retail execution semantics and does not select runtime-active Tower
scenario/group/animation state.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_remote_tower_descriptor_selection_calibration import parse_graph
from d1_split_tar_extract import SplitHttpTar

NULLS = {'00000000', 'FFFFFFFF'}


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def visible_external_groups(model_export: dict) -> dict[str, list[int]]:
    out: dict[str, set[int]] = collections.defaultdict(set)
    for m in model_export.get('models', []):
        model = norm(m.get('model'))
        for r in m.get('ranges', []):
            for p in r.get('parts', []):
                vi = int(p.get('variant_shader_index', -1))
                if vi >= 0:
                    out[model].add(vi)
    return {k: sorted(v) for k, v in out.items()}


def pair_config(row: dict) -> set[tuple[str, str]]:
    # Mirror the exact candidate-rule calibration: only source-typed placement pairs
    # that also occur in the placement's own exact model switch bank participate.
    return {
        (norm(x['pair'][0]), norm(x['pair'][1]))
        for x in row.get('record_matches', [])
        if x.get('exact_pair_in_own_model_switch_bank')
    }


def choose(group: dict, config: set[tuple[str, str]]) -> dict:
    sat = []
    candidates = []
    for m in group.get('members', []):
        req = {tuple(norm(v) for v in p) for p in m.get('list_a_pairs', [])}
        ok = req.issubset(config)
        c = {
            'member_index': int(m['member_index']),
            'material_tag_hash': norm(m['material_tag_hash']),
            'descriptor_index': int(m['descriptor_index']),
            'required_list_a_pairs': [list(x) for x in sorted(req)],
            'specificity': len(req),
            'satisfied': ok,
        }
        candidates.append(c)
        if ok:
            sat.append(c)
    if not sat:
        raise ValueError(f"variant {group['variant_shader_index']}: no satisfied member")
    maxspec = max(x['specificity'] for x in sat)
    wins = [x for x in sat if x['specificity'] == maxspec]
    if len(wins) != 1:
        raise ValueError(
            f"variant {group['variant_shader_index']}: ambiguous max-specificity winners "
            f"{[(x['member_index'], x['material_tag_hash']) for x in wins]}"
        )
    return {'winner': wins[0], 'candidates': candidates}


def sig_key(rows: list[dict]) -> tuple:
    return tuple(
        (int(x['variant_shader_index']), norm(x['material_tag_hash']))
        for x in sorted(rows, key=lambda y: int(y['variant_shader_index']))
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--placement-calibration', type=Path, required=True)
    ap.add_argument('--visual-plan', type=Path, required=True)
    ap.add_argument('--model-export', type=Path, required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    corpus = json.loads(a.placement_calibration.read_text())
    plan = json.loads(a.visual_plan.read_text())
    export = json.loads(a.model_export.read_text())
    violations: list[str] = []

    if corpus.get('status') != 'D1_TOWER_PLACEMENT_PERMUTATION_CROSS_ENTITY_CALIBRATION' or corpus.get('violations'):
        violations.append('placement_calibration_not_green')
    if plan.get('status') != 'D1_WORLD_ARTICULATED_ENTITY_PLAN_COMPLETE' or plan.get('violations'):
        violations.append('visual_plan_not_green')
    if export.get('status') != 'D1_WORLD_ARTICULATED_MODEL_SET_COMPLETE' or export.get('errors'):
        violations.append('model_export_not_green')

    families = {norm(x['model']): x for x in plan.get('families', [])}
    exported_models = {norm(x['model']) for x in export.get('models', [])}
    if len(families) != 13:
        violations.append(f'expected_13_actor_models_got_{len(families)}')
    if set(families) != exported_models:
        violations.append(f'plan_export_model_set_mismatch:{sorted(set(families)^exported_models)}')

    visible_groups = visible_external_groups(export)
    cats = load_catalogs(a.member_catalog)
    arc = SplitHttpTar(
        [f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)],
        retries=6, timeout=90,
    )
    c = RemoteCorpus(arc, cats, a.runtime)

    placement_rows_by_model: dict[str, list[dict]] = collections.defaultdict(list)
    for row in corpus.get('calibration_rows', []):
        model = norm(row.get('model_tag_hash', 'FFFFFFFF'))
        if model not in NULLS:
            placement_rows_by_model[model].append(row)

    model_rows = []
    total_evaluations = 0
    total_unique_signatures = 0
    production_closed = 0
    placement_variant_models = 0
    static_models = 0
    unresolved_models = 0

    for model in sorted(families):
        fam = families[model]
        parent = norm(fam['model_parent_resource'])
        active_vis = visible_groups.get(model, [])
        try:
            graph = parse_graph(c, parent)
        except Exception as ex:
            violations.append(f'{model}:{parent}:parse_graph:{ex!r}')
            model_rows.append({
                'model': model, 'model_parent_resource': parent,
                'status': 'graph_unavailable', 'error': repr(ex),
            })
            unresolved_models += 1
            continue

        groups = {int(g['variant_shader_index']): g for g in graph.get('groups', [])}
        missing = [vi for vi in active_vis if vi not in groups]
        if missing:
            violations.append(f'{model}:visible_variant_groups_missing:{missing}')

        placements = placement_rows_by_model.get(model, [])
        signatures: dict[tuple, dict] = {}
        placement_details = []

        if placements:
            for row in placements:
                config = pair_config(row)
                selected = []
                try:
                    for vi in active_vis:
                        ev = choose(groups[vi], config)
                        w = ev['winner']
                        selected.append({
                            'variant_shader_index': vi,
                            'material_tag_hash': norm(w['material_tag_hash']),
                            'member_index': int(w['member_index']),
                            'descriptor_index': int(w['descriptor_index']),
                            'specificity': int(w['specificity']),
                        })
                        total_evaluations += 1
                except Exception as ex:
                    violations.append(f"{model}:{row.get('owner')}:{row.get('smap_offset')}:{ex!r}")
                    continue
                key = sig_key(selected)
                rec = signatures.setdefault(key, {
                    'signature_index': -1,
                    'visible_external_materials': [
                        {'variant_shader_index': vi, 'material_tag_hash': mat}
                        for vi, mat in key
                    ],
                    'placement_count': 0,
                    'entity_hashes': set(),
                    'scripted_owners': set(),
                    'configurations': set(),
                })
                rec['placement_count'] += 1
                rec['entity_hashes'].add(norm(row['entity_hash']))
                rec['scripted_owners'].add(norm(row['owner']))
                rec['configurations'].add(tuple(sorted(config)))
                placement_details.append({
                    'entity_hash': norm(row['entity_hash']),
                    'scripted_owner': norm(row['owner']),
                    'smap_offset': int(row['smap_offset']),
                    'configuration_pairs': [list(x) for x in sorted(config)],
                    'signature_key': [list(x) for x in key],
                })

            sig_list = []
            for i, key in enumerate(sorted(signatures)):
                rec = signatures[key]
                rec['signature_index'] = i
                rec['entity_hashes'] = sorted(rec['entity_hashes'])
                rec['scripted_owners'] = sorted(rec['scripted_owners'])
                rec['configurations'] = [
                    [list(x) for x in cfg] for cfg in sorted(rec['configurations'])
                ]
                sig_list.append(rec)
            total_unique_signatures += len(sig_list)
            status = 'calibrated_single_visible_signature' if len(sig_list) == 1 else 'calibrated_placement_specific_visible_signatures'
            if len(sig_list) == 1:
                production_closed += 1
            else:
                placement_variant_models += 1
                production_closed += 1
            model_rows.append({
                'model': model,
                'model_parent_resource': parent,
                'entity_count': int(fam.get('entity_count', 0)),
                'entities': [norm(x) for x in fam.get('entities', [])],
                'visible_external_variant_shader_indices': active_vis,
                'visible_external_group_count': len(active_vis),
                'placement_calibration_row_count': len(placements),
                'unique_source_configuration_count': len({tuple(sorted(pair_config(x))) for x in placements}),
                'unique_visible_external_signature_count': len(sig_list),
                'status': status,
                'signatures': sig_list,
                'placement_rows': placement_details,
                'graph_summary': {
                    'group_count': graph.get('group_count'),
                    'descriptor_count': graph.get('descriptor_count'),
                    'material_count': graph.get('material_count'),
                    'switch_record_count': graph.get('switch_record_count'),
                },
            })
        else:
            rows = []
            unresolved = []
            for vi in active_vis:
                g = groups.get(vi)
                if g is None:
                    unresolved.append({'variant_shader_index': vi, 'reason': 'group_missing'})
                    continue
                mats = sorted({norm(m['material_tag_hash']) for m in g.get('members', [])})
                row = {
                    'variant_shader_index': vi,
                    'serialized_member_count': len(g.get('members', [])),
                    'unique_material_count': len(mats),
                    'material_tag_hashes': mats,
                }
                rows.append(row)
                if len(mats) != 1:
                    unresolved.append(row)
            if not unresolved:
                static_models += 1
                production_closed += 1
                key = tuple((x['variant_shader_index'], x['material_tag_hashes'][0]) for x in rows)
                if key:
                    total_unique_signatures += 1
                model_rows.append({
                    'model': model,
                    'model_parent_resource': parent,
                    'entity_count': int(fam.get('entity_count', 0)),
                    'entities': [norm(x) for x in fam.get('entities', [])],
                    'visible_external_variant_shader_indices': active_vis,
                    'visible_external_group_count': len(active_vis),
                    'placement_calibration_row_count': 0,
                    'unique_source_configuration_count': 0,
                    'unique_visible_external_signature_count': 1,
                    'status': 'configuration_independent_visible_signature',
                    'configuration_independent_groups': rows,
                    'signatures': [{
                        'signature_index': 0,
                        'visible_external_materials': [
                            {'variant_shader_index': vi, 'material_tag_hash': mat}
                            for vi, mat in key
                        ],
                        'placement_count': None,
                    }],
                    'graph_summary': {
                        'group_count': graph.get('group_count'),
                        'descriptor_count': graph.get('descriptor_count'),
                        'material_count': graph.get('material_count'),
                        'switch_record_count': graph.get('switch_record_count'),
                    },
                })
            else:
                unresolved_models += 1
                model_rows.append({
                    'model': model,
                    'model_parent_resource': parent,
                    'entity_count': int(fam.get('entity_count', 0)),
                    'entities': [norm(x) for x in fam.get('entities', [])],
                    'visible_external_variant_shader_indices': active_vis,
                    'visible_external_group_count': len(active_vis),
                    'placement_calibration_row_count': 0,
                    'unique_source_configuration_count': 0,
                    'unique_visible_external_signature_count': None,
                    'status': 'fail_closed_missing_configuration_for_non_equivalent_visible_group',
                    'configuration_independent_groups': rows,
                    'unresolved_visible_groups': unresolved,
                    'graph_summary': {
                        'group_count': graph.get('group_count'),
                        'descriptor_count': graph.get('descriptor_count'),
                        'material_count': graph.get('material_count'),
                        'switch_record_count': graph.get('switch_record_count'),
                    },
                })

    actor_models = len(families)
    all_visual_material_signatures_closed = (
        not violations and production_closed == actor_models and unresolved_models == 0
    )
    out = {
        'schema_version': 1,
        'status': 'D1_TOWER_ACTOR_VISIBLE_MATERIAL_SIGNATURES_COMPLETE'
                  if all_visual_material_signatures_closed
                  else ('D1_TOWER_ACTOR_VISIBLE_MATERIAL_SIGNATURES_FRONTIER' if not violations
                        else 'D1_TOWER_ACTOR_VISIBLE_MATERIAL_SIGNATURES_VIOLATIONS'),
        'actor_model_count': actor_models,
        'production_closed_model_count': production_closed,
        'placement_variant_model_count': placement_variant_models,
        'configuration_independent_model_count': static_models,
        'unresolved_model_count': unresolved_models,
        'candidate_rule_visible_group_evaluation_count': total_evaluations,
        'total_unique_visible_external_signature_count': total_unique_signatures,
        'models': model_rows,
        'violations': violations,
        'proof': {
            'stage0_highest_detail_visible_group_set_from_green_actor_export': True,
            'placement_configuration_from_green_918_placement_corpus': True,
            'candidate_rule_previously_calibrated_70281_of_70281_unique': True,
            'all_13_actor_visible_material_signatures_production_closed': all_visual_material_signatures_closed,
            'D1_retail_descriptor_evaluator_source_closed': False,
            'runtime_active_scenario_selected': False,
            'runtime_active_D912_group_selected': False,
            'runtime_actor_animation_state_selected': False,
        },
        'policy': (
            'Visible material signatures are an export adapter result. Source-typed S152 placement configurations are '
            'evaluated only with the previously corpus-deterministic descriptor-A subset/max-specificity candidate rule. '
            'Models without S152 calibration are closed only when every visible external group serializes one unique '
            'Material hash independent of member choice. Multiple exact signatures are preserved as placement-specific '
            'variants. No runtime scenario/group/animation activation is inferred and retail evaluator semantics remain unpromoted.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        k: out[k] for k in (
            'status','actor_model_count','production_closed_model_count',
            'placement_variant_model_count','configuration_independent_model_count',
            'unresolved_model_count','candidate_rule_visible_group_evaluation_count',
            'total_unique_visible_external_signature_count','violations','proof'
        )
    }, indent=2))
    for r in model_rows:
        print('MODEL', r['model'], r['status'], 'visible_groups', r.get('visible_external_group_count'),
              'placements', r.get('placement_calibration_row_count'),
              'signatures', r.get('unique_visible_external_signature_count'))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
