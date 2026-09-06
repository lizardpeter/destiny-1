#!/usr/bin/env python3
"""Validate the common D1 Tower runtime-rig animation-owner architecture.

The family identity and expected homologous owner slots come from a source-owned
family spec.  Nothing in that spec is promoted by itself.  This tool reopens the
retail SEntities and EntityResources, validates both owner class pairs, reads the
literal FileHash slots, requires convergence on one 80802C0E control, decodes the
selector table, and checks every selected clip against the exact skeleton/runtime
rig dimensions and runtime-component fingerprint.

Multiple selected clips remain multiple source-owned actions.  No startup/default
state, state name, loop behavior, synchronization, or actor semantics are inferred.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entry_extract import EntryReader
from d1_entity_resource_probe import parse_resource
from d1_animation_control_state_map import decode_control
from d1_animation_retarget_probe import component_rows
from d1_tower_family_f_animation_ownership import (
    norm, u32, entry_map, exact_payload, dyn_resources, filebacked, sig,
    ENTITY_RESOURCE_REF, CONTROL_REF, CLIP_REF,
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--activity-pkg', type=Path, required=True,
                    help='023D_5 with all logical 023D siblings staged beside it')
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--parser-root', type=Path, required=True)
    ap.add_argument('--spec', type=Path, required=True)
    ap.add_argument('--family', required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    specs = json.loads(a.spec.read_text())
    fam_id = str(a.family).upper()
    spec = specs.get('families', {}).get(fam_id)
    if spec is None:
        raise ValueError(f'family {fam_id} absent from {a.spec}')

    model = norm(spec['entity_model'])
    skeleton_tag = norm(spec['skeleton_resource'])
    rig_tag = norm(spec['runtime_rig_resource'])
    expected_nodes = int(spec['expected_node_count'])
    expected_controls = int(spec['expected_control_count'])
    entities_spec = {norm(k): [str(x).upper() for x in v] for k, v in spec['entities'].items()}
    owner_specs = {
        str(k): {
            'resource_hash': norm(v['resource_hash']),
            'class_pair': tuple(norm(x) for x in v['class_pair']),
            'control_filehash_offset': int(v['control_filehash_offset']),
        }
        for k, v in spec['owner_halves'].items()
    }
    expected_owner_hashes = {v['resource_hash'] for v in owner_specs.values()}

    r = EntryReader(a.activity_pkg, a.runtime)
    by = entry_map(r)
    violations: list[str] = []

    all_world_ids = []
    entity_rows = {}
    expected_shared = {skeleton_tag, rig_tag, *expected_owner_hashes}
    for entity, world_ids in entities_spec.items():
        e, b = exact_payload(r, by, entity, '80800734')
        resources = dyn_resources(b)
        missing = sorted(expected_shared - set(resources))
        if missing:
            violations.append(f'{entity}: missing required family resources {missing}')
        all_world_ids.extend(world_ids)
        entity_rows[entity] = {
            'entry_index': int(e['index']), 'size': int(e['file_size']),
            'resource_count': len(resources), 'resource_hashes': resources,
            'runtime_placement_count': len(world_ids), 'world_ids': world_ids,
            'required_resources_present': not missing,
        }
    if len(set(all_world_ids)) != len(all_world_ids):
        violations.append('duplicate runtime WorldID in family spec')

    owner_rows = {}
    observed_controls = []
    for half_name, cfg in owner_specs.items():
        owner = cfg['resource_hash']
        e, b = exact_payload(r, by, owner, ENTITY_RESOURCE_REF)
        parsed = parse_resource(b, r.h['platform'])
        observed_pair = (
            norm((parsed.get('unk10') or {}).get('class_hash', '0')),
            norm((parsed.get('unk18') or {}).get('class_hash', '0')),
        )
        expected_pair = cfg['class_pair']
        if observed_pair != expected_pair:
            violations.append(f'{owner}: class pair {observed_pair} != {expected_pair}')
        off = cfg['control_filehash_offset']
        if off + 4 > len(b):
            violations.append(f'{owner}: FileHash slot 0x{off:X} OOB')
            observed = None
        else:
            observed = f'{u32(b, off):08X}'
            observed_controls.append(observed)
        owner_rows[half_name] = {
            'resource_hash': owner, 'entry_index': int(e['index']), 'size': int(e['file_size']),
            'expected_class_pair': list(expected_pair), 'observed_class_pair': list(observed_pair),
            'control_filehash_offset': off, 'observed_control': observed,
            'class_pair_exact': observed_pair == expected_pair,
        }

    controls = sorted(set(x for x in observed_controls if x is not None))
    control_tag = controls[0] if len(controls) == 1 else None
    if len(controls) != 1:
        violations.append(f'owner halves do not converge on one control: {controls}')

    control_row = None
    animation_list_unique: list[str] = []
    selected_unique: list[str] = []
    if control_tag:
        try:
            ce, cb = exact_payload(r, by, control_tag, CONTROL_REF)
            decoded = decode_control(cb, r)
            animation_list_unique = sorted({norm(x['tag_hash']) for x in decoded['animation_list']['items']})
            selected_unique = sorted({
                norm(x['tag_hash'])
                for state in decoded['state_table']['records']
                for x in state['selected_animations']
            })
            control_row = {
                'tag_hash': control_tag, 'entry_index': int(ce['index']), 'size': int(ce['file_size']),
                **decoded,
                'unique_animation_list_hashes': animation_list_unique,
                'unique_selected_clip_hashes': selected_unique,
            }
        except Exception as ex:
            violations.append(f'{control_tag}: control decode failed: {ex!r}')

    sys.path.insert(0, str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_animation import read_animation
    ver = Game_Version.D1_ROI

    _, sb = exact_payload(r, by, skeleton_tag, ENTITY_RESOURCE_REF)
    sk = read_skeleton(io.BytesIO(sb), ver)
    _, rb = exact_payload(r, by, rig_tag, ENTITY_RESOURCE_REF)
    rig = read_runtime_rig(io.BytesIO(rb), ver)
    node_count = len(sk.node_defs)
    control_count = len(rig.controls_relations)
    rig_components = component_rows(rig.rig_components)
    rig_signature = sig(rig_components)
    if node_count != expected_nodes:
        violations.append(f'{skeleton_tag}: nodes {node_count} != expected {expected_nodes}')
    if control_count != expected_controls:
        violations.append(f'{rig_tag}: controls {control_count} != expected {expected_controls}')

    clip_rows = {}
    for clip in animation_list_unique:
        row = {'tag_hash': clip, 'selected_by_any_state': clip in selected_unique}
        e = by.get(clip)
        if e is None:
            row.update(status='absent_from_023d_entry_table', exact_family_compatible=False)
            if clip in selected_unique:
                violations.append(f'{clip}: selected clip absent from 023D entry table')
            clip_rows[clip] = row
            continue
        row.update(entry_index=int(e['index']), reference=norm(e['reference']), size=int(e['file_size']))
        if norm(e['reference']) != CLIP_REF:
            row.update(status='wrong_reference_class', exact_family_compatible=False)
            if clip in selected_unique:
                violations.append(f'{clip}: selected ref {norm(e["reference"])} != {CLIP_REF}')
            clip_rows[clip] = row
            continue
        if not r.available(e['index']):
            row.update(status='payload_unavailable', exact_family_compatible=False)
            if clip in selected_unique:
                violations.append(f'{clip}: selected payload unavailable')
            clip_rows[clip] = row
            continue
        try:
            anim = filebacked(read_animation, r.entry(e['index']), ver)
            h = anim.animation_header
            comps = component_rows(anim.runtime_rig_components)
            row.update(
                status='parsed', frame_count=int(h.frame_count), node_count=int(h.node_count),
                rig_control_count=int(h.rig_control_count), runtime_rig_components=comps,
                component_fingerprint_matches_runtime_rig=sig(comps) == rig_signature,
                node_count_matches_skeleton=int(h.node_count) == node_count,
                control_count_matches_runtime_rig=int(h.rig_control_count) == control_count,
            )
            row['exact_family_compatible'] = all((
                row['component_fingerprint_matches_runtime_rig'],
                row['node_count_matches_skeleton'], row['control_count_matches_runtime_rig'],
            ))
            if clip in selected_unique and not row['exact_family_compatible']:
                violations.append(f'{clip}: selected clip not exact family compatible')
        except Exception as ex:
            row.update(status='parse_failed', error=repr(ex), exact_family_compatible=False)
            if clip in selected_unique:
                violations.append(f'{clip}: selected clip parse failed: {ex!r}')
        clip_rows[clip] = row

    owner_exact = (
        control_tag is not None and
        all(x['class_pair_exact'] and x['observed_control'] == control_tag for x in owner_rows.values())
    )
    selected_compatible = bool(selected_unique) and all(
        clip_rows.get(x, {}).get('exact_family_compatible') for x in selected_unique
    )
    closed = owner_exact and control_row is not None and selected_compatible and not violations

    out = {
        'schema_version': 1,
        'status': f'D1_TOWER_FAMILY_{fam_id}_ANIMATION_OWNER_CONTROL_CLOSED' if closed else f'D1_TOWER_FAMILY_{fam_id}_ANIMATION_OWNER_CONTROL_PARTIAL',
        'family_id': fam_id,
        'family': {
            'entity_model': model, 'skeleton_resource': skeleton_tag,
            'skeleton_node_count': node_count, 'runtime_rig_resource': rig_tag,
            'runtime_rig_control_count': control_count, 'runtime_rig_components': rig_components,
            'sentity_count': len(entities_spec), 'runtime_placement_count': len(all_world_ids),
            'unique_world_id_count': len(set(all_world_ids)),
        },
        'entities': entity_rows,
        'owner_halves': owner_rows,
        'owner_halves_converge': len(controls) == 1,
        'animation_control': control_row,
        'unique_selected_clip_hashes': selected_unique,
        'clips': clip_rows,
        'selection_status': 'owner_control_selected_set_closed' if closed else 'partial',
        'violations': violations,
        'policy': 'Closed means exact SEntity membership, exact owner class pairs, literal owner FileHash slots converging on one 80802C0E control, decoded selector-selected clips, and exact selected-clip skeleton/runtime-rig compatibility. Multiple selected states remain separate actions; no default/state-name/loop/synchronization/actor semantic is inferred.',
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'], 'family': out['family'], 'owner_halves': owner_rows,
        'control': control_tag, 'animation_list': animation_list_unique,
        'selected_clips': selected_unique,
        'states': [] if control_row is None else [{
            'state_hash': x['state_hash'], 'state_name': x.get('state_name'),
            'scalar_f32': x['scalar_f32'],
            'selected': [y['tag_hash'] for y in x['selected_animations']],
        } for x in control_row['state_table']['records']],
        'clip_summary': {k: {
            'frame_count': v.get('frame_count'), 'node_count': v.get('node_count'),
            'rig_control_count': v.get('rig_control_count'), 'selected': v.get('selected_by_any_state'),
            'exact_family_compatible': v.get('exact_family_compatible'), 'status': v.get('status'),
        } for k, v in clip_rows.items()},
        'violations': violations,
    }, indent=2))
    return 0 if closed else 2


if __name__ == '__main__':
    raise SystemExit(main())
