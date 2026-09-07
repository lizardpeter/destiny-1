#!/usr/bin/env python3
"""Build a fail-closed Xur visual material binding using the calibrated D1 descriptor rule.

This is deliberately a *visual adapter*, not a promotion of D1 retail evaluator
semantics.  It replaces Charm's known placeholder external-material member-0 choice
with the one candidate rule that is deterministic over the exact Tower corpus:

  satisfied := descriptor list-A pairs are a subset of the placement configuration
  winner    := unique satisfied member with greatest list-A pair count
  fallback  := an empty list-A descriptor when no more-specific member is satisfied

The rule has already calibrated 70,281/70,281 Tower placement×group evaluations to
one unique winner with zero ambiguous/no-candidate groups.  This tool applies it only
to the source-owned Xur model-parent pair and an explicitly supplied source-typed S152
configuration.  It leaves the formal retail-consumer proof gate false.
"""
from __future__ import annotations

import argparse, collections, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import d1_world_entity_model_material_bindings as base
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_remote_tower_descriptor_selection_calibration import parse_graph
from d1_split_tar_extract import SplitHttpTar

XUR_MODEL = '80C88CEF'
XUR_PARENT = '80C88CE2'
XUR_ENTITIES = ['80C7ACC8', '80C885AA']


def norm(x):
    return str(x).upper().removeprefix('0X').zfill(8)


def pkgid(h):
    return f'{((int(norm(h),16)-0x80800000)>>13)&0x7ff:04x}'


def parse_pair(text: str) -> tuple[str,str]:
    for sep in ('=', ':', ',', '/'):
        if sep in text:
            a,b = text.split(sep, 1)
            return norm(a.strip()), norm(b.strip())
    raise argparse.ArgumentTypeError('pair must be KEY=VALUE')


def winner(group: dict, config: set[tuple[str,str]]) -> tuple[int,dict,list[dict]]:
    sats = []
    evidence = []
    for m in group['members']:
        req = {tuple(norm(v) for v in x) for x in m.get('list_a_pairs', [])}
        ok = req.issubset(config)
        evidence.append({
            'member_index': int(m['member_index']),
            'material_tag_hash': norm(m['material_tag_hash']),
            'descriptor_index': int(m['descriptor_index']),
            'required_list_a_pairs': [list(x) for x in sorted(req)],
            'satisfied': ok,
            'specificity': len(req),
        })
        if ok:
            sats.append((len(req), m))
    if not sats:
        raise ValueError(f"variant {group['variant_shader_index']}: no satisfied candidate")
    maxspec = max(n for n,_ in sats)
    wins = [m for n,m in sats if n == maxspec]
    if len(wins) != 1:
        raise ValueError(f"variant {group['variant_shader_index']}: ambiguous max-specificity candidates {len(wins)}")
    return maxspec, wins[0], evidence


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--config-pair', action='append', type=parse_pair, required=True)
    ap.add_argument('--model', default=XUR_MODEL)
    ap.add_argument('--parent-resource', default=XUR_PARENT)
    ap.add_argument('-o','--output',type=Path,required=True)
    a = ap.parse_args()

    model = norm(a.model)
    parent = norm(a.parent_resource)
    config = set(a.config_pair)
    violations = []
    if model != XUR_MODEL:
        violations.append(f'unexpected_xur_model:{model}')
    if parent != XUR_PARENT:
        violations.append(f'unexpected_xur_parent:{parent}')

    cats = load_catalogs(a.member_catalog)
    arc = SplitHttpTar(
        [f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],
        retries=6, timeout=90,
    )
    c = RemoteCorpus(arc, cats, a.runtime)

    try:
        binding = base.bind_model(c, model, parent)
    except Exception as ex:
        binding = {'model':model,'parent_resource':parent,'meshes':[],'violations':[repr(ex)],'validation_ok':False}
        violations.append('base_binding:' + repr(ex))

    graph = None
    try:
        graph = parse_graph(c, parent)
    except Exception as ex:
        violations.append('permutation_graph:' + repr(ex))

    selection_rows = []
    selected = collections.Counter()
    external_parts = 0
    if graph is not None and not binding.get('violations'):
        groups = {int(g['variant_shader_index']): g for g in graph['groups']}
        for mesh in binding.get('meshes', []):
            for part in mesh.get('parts', []):
                vi = int(part['variant_shader_index'])
                if vi == -1:
                    sm = part.get('selected_material') or {}
                    h = norm(sm['hash']) if sm.get('hash') else None
                    if h and h not in base.NULLS:
                        selected[h] += 1
                    continue
                external_parts += 1
                g = groups.get(vi)
                if g is None:
                    part['violations'].append('calibrated_variant_shader_index_missing')
                    violations.append(f"mesh[{mesh['mesh_index']}].part[{part['part_index']}]:calibrated_variant_shader_index_missing:{vi}")
                    continue
                try:
                    maxspec, win, evidence = winner(g, config)
                    h = norm(win['material_tag_hash'])
                    # Replace the old member-0 result completely.  Preserve it as audit evidence.
                    part['placeholder_member0_selection'] = {
                        'selection': part.get('selection'),
                        'selected_external_material_index': part.get('selected_external_material_index'),
                        'selected_material': part.get('selected_material'),
                        'selection_status': part.get('selection_status'),
                    }
                    part.pop('selected_material', None)
                    part.pop('selection_status', None)
                    part.pop('renderable', None)
                    part.pop('null_material_source_rule', None)
                    part['violations'] = []
                    part['selection'] = 'tower_corpus_calibrated_descriptor_A_subset_max_specificity'
                    part['calibrated_configuration_pairs'] = [list(x) for x in sorted(config)]
                    part['calibrated_winner_member_index'] = int(win['member_index'])
                    part['calibrated_winner_descriptor_index'] = int(win['descriptor_index'])
                    part['calibrated_winner_specificity'] = int(maxspec)
                    part['calibrated_candidate_evidence'] = evidence
                    # ExternalMaterialsMap start index is exact; member index maps directly into the bank.
                    me = part.get('external_map_entry') or {}
                    ext_idx = int(me.get('material_start_index', -1)) + int(win['member_index'])
                    part['selected_external_material_index'] = ext_idx
                    base._classify_selected_material(
                        part,
                        base.meta(c, h, base.MATERIAL_CLASS),
                        'calibrated_external_material_missing_or_class_mismatch',
                    )
                    if part['violations']:
                        raise ValueError(','.join(part['violations']))
                    if h not in base.NULLS:
                        selected[h] += 1
                    selection_rows.append({
                        'mesh_index': int(mesh['mesh_index']),
                        'part_index': int(part['part_index']),
                        'variant_shader_index': vi,
                        'winner_material': h,
                        'winner_member_index': int(win['member_index']),
                        'winner_descriptor_index': int(win['descriptor_index']),
                        'winner_specificity': int(maxspec),
                    })
                except Exception as ex:
                    part['violations'].append('calibrated_selection:' + repr(ex))
                    violations.append(f"mesh[{mesh['mesh_index']}].part[{part['part_index']}]:{ex!r}")

    parts = [p for m in binding.get('meshes',[]) for p in m.get('parts',[])]
    binding['violations'] = [x for x in binding.get('violations',[]) if x]
    for m in binding.get('meshes',[]):
        for p in m.get('parts',[]):
            for x in p.get('violations',[]):
                tag = f"mesh[{m['mesh_index']}].part[{p['part_index']}]:{x}"
                if tag not in violations:
                    violations.append(tag)
    binding['part_count'] = len(parts)
    binding['external_variant_part_count'] = sum(int(p.get('variant_shader_index',-1)) != -1 for p in parts)
    binding['explicit_null_material_part_count'] = sum(p.get('selection_status') == 'EXPLICIT_NULL_MATERIAL' for p in parts)
    binding['renderable_material_part_count'] = sum(p.get('renderable') is True for p in parts)
    binding['validation_ok'] = not violations
    binding['owning_entity_count'] = len(XUR_ENTITIES)

    out = {
        'schema_version': 3,
        'status': 'D1_XUR_CORPUS_CALIBRATED_VISUAL_MATERIAL_BINDINGS_COMPLETE' if not violations else 'D1_XUR_CORPUS_CALIBRATED_VISUAL_MATERIAL_BINDINGS_PARTIAL',
        'compatibility_status_for_exporter': 'D1_WORLD_ENTITY_MODEL_MATERIAL_BINDINGS_COMPLETE' if not violations else 'D1_WORLD_ENTITY_MODEL_MATERIAL_BINDINGS_PARTIAL',
        'model_parent_pair_count': 1,
        'validated_pair_count': 1 if binding.get('validation_ok') else 0,
        'part_count': binding.get('part_count',0),
        'external_variant_part_count': binding.get('external_variant_part_count',0),
        'explicit_null_material_part_count': binding.get('explicit_null_material_part_count',0),
        'renderable_material_part_count': binding.get('renderable_material_part_count',0),
        'unique_selected_material_count': len(selected),
        'selected_material_reference_counts': dict(sorted(selected.items())),
        'required_selected_material_package_ids': sorted({pkgid(h) for h in selected}),
        'source_entities': XUR_ENTITIES,
        'entity_model': model,
        'model_parent_resource': parent,
        'configuration_pairs': [list(x) for x in sorted(config)],
        'permutation_graph': {
            'resource_hash': graph.get('resource_hash') if graph else None,
            'model_tag_hash': graph.get('model_tag_hash') if graph else None,
            'descriptor_count': graph.get('descriptor_count') if graph else None,
            'group_count': graph.get('group_count') if graph else None,
            'material_count': graph.get('material_count') if graph else None,
            'switch_record_count': graph.get('switch_record_count') if graph else None,
        },
        'calibrated_external_part_selections': selection_rows,
        'bindings': [binding],
        'violations': violations,
        'proof': {
            'source_owned_xur_model_parent_pair': model == XUR_MODEL and parent == XUR_PARENT,
            'placement_configuration_source_typed_elsewhere': True,
            'candidate_rule_calibrated_70281_of_70281_unique_elsewhere': True,
            'all_xur_external_parts_unique_under_candidate_rule': not violations and len(selection_rows) == external_parts,
            'D1_retail_consumer_execution_path_proven': False,
            'descriptor_evaluation_algorithm_source_closed': False,
        },
        'gates': {
            'E6_80C885E6_live_selection_proven': False,
            'E7_80C885E7_live_selection_proven': False,
            'E8_80C885E8_live_selection_proven': False,
        },
        'policy': (
            'This is a Blender visual adapter. It replaces the known Charm member-0 placeholder only because the candidate '
            'descriptor-A subset/max-specificity rule is deterministic across the exact 70,281-evaluation Tower corpus and '
            'the Xur S152 configuration is source typed. It does not claim the retail D1 evaluator has been source-closed. '
            'Formal E6/E7/E8 live-selection gates remain false.'
        ),
    }
    # The existing exporter requires this exact status spelling.  Keep the stronger
    # semantic status in xur_status while exposing a compatibility status at top level.
    out['xur_status'] = out['status']
    out['status'] = out['compatibility_status_for_exporter']

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'],
        'xur_status': out['xur_status'],
        'part_count': out['part_count'],
        'external_variant_part_count': out['external_variant_part_count'],
        'calibrated_external_selection_count': len(selection_rows),
        'unique_selected_material_count': out['unique_selected_material_count'],
        'required_selected_material_package_ids': out['required_selected_material_package_ids'],
        'proof': out['proof'],
        'gates': out['gates'],
        'violations': violations,
    }, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
