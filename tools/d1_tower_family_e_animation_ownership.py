#!/usr/bin/env python3
"""Close source-owned animation selection for the Tower 67-bone articulated family.

This is intentionally narrow.  It joins four independently decoded layers:

* the source-owned Tower Family-E WorldID -> SEntity evidence;
* each SEntity's serialized EntityResource list;
* literal animation-owner -> control -> selected-clip edges; and
* exact skeleton/runtime-rig/clip component and dimension compatibility.

No clip is named idle/vendor/ambient from appearance or duration.
"""
from __future__ import annotations

import argparse
import io
import json
import struct
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_entry_extract import EntryReader
from d1_world_activity_entity_table_census import dyn
from d1_animation_control_state_map import decode_control
from d1_animation_retarget_probe import component_rows

SENTITY_REF = '80800734'
ENTITY_RESOURCE_REF = '80800861'
CONTROL_REF = '80802C0E'
CLIP_REF = '808005A1'

FAMILY_SHARED = {'809D8613', '80CA0CD8', '809D8566', '809D856E'}
OWNER_TO_CONTROL = {
    '80C7AE48': (0x110, '80C7AE68'),
    '80C7AE49': (0x448, '80C7AE68'),
    '809DF581': (0x110, '809D856F'),
    '809DF582': (0x448, '809D856F'),
}
CONTROL_TO_CLIP = {
    '80C7AE68': '80C7AE98',
    '809D856F': '809D8572',
}


def norm(x: str) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def u32(b: bytes, off: int) -> int:
    return struct.unpack_from('<I', b, off)[0]


def find_entry(reader: EntryReader, tag: str, expected_ref: str | None = None):
    tag = norm(tag)
    rows = [e for e in reader.entries if norm(e['tag_hash']) == tag]
    if len(rows) != 1:
        raise ValueError(f'{tag}: expected one entry in package {reader.h["pkg_id"]:04X}, got {len(rows)}')
    e = rows[0]
    if expected_ref is not None and norm(e['reference']) != norm(expected_ref):
        raise ValueError(f'{tag}: reference {e["reference"]}, expected {expected_ref}')
    if not reader.available(e['index']):
        raise ValueError(f'{tag}: payload unavailable')
    return e


def payload(reader: EntryReader, tag: str, expected_ref: str | None = None) -> tuple[dict, bytes]:
    e = find_entry(reader, tag, expected_ref)
    return e, reader.entry(e['index'])


def parse_sentity_resources(reader: EntryReader, tag: str) -> dict:
    e, b = payload(reader, tag, SENTITY_REF)
    a = dyn(b, 0x20, 0x0C)
    if not a['ok']:
        raise ValueError(f'{tag}: SEntity resource array invalid: {a}')
    rows = []
    for i in range(a['count']):
        off = a['absolute'] + i * 0x0C
        h = f'{u32(b, off):08X}'
        rows.append({'index': i, 'record_offset': off, 'resource_hash': h})
    return {
        'tag_hash': norm(tag), 'entry_index': e['index'], 'resource_count': len(rows),
        'resource_hashes': [x['resource_hash'] for x in rows], 'resources': rows,
    }


def filebacked(read_animation, b: bytes, version):
    with tempfile.NamedTemporaryFile() as f:
        f.write(b); f.flush(); f.seek(0)
        return read_animation(f, version)


def clip_row(reader: EntryReader, tag: str, read_animation, version) -> dict:
    e, b = payload(reader, tag, CLIP_REF)
    anim = filebacked(read_animation, b, version)
    h = anim.animation_header
    comps = component_rows(anim.runtime_rig_components)
    return {
        'tag_hash': norm(tag), 'entry_index': e['index'], 'size': e['file_size'],
        'frame_count': int(h.frame_count), 'node_count': int(h.node_count),
        'rig_control_count': int(h.rig_control_count), 'runtime_rig_components': comps,
    }


def sig(rows: list[dict]) -> tuple[tuple[str, int], ...]:
    return tuple((norm(x['hash']), int(x['count'])) for x in rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--tower-activity-pkg', type=Path, required=True)
    ap.add_argument('--tower-destination-pkg', type=Path, required=True)
    ap.add_argument('--generic-owner-pkg', type=Path, required=True)
    ap.add_argument('--generic-animation-pkg', type=Path, required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--parser-root', type=Path, required=True)
    ap.add_argument('--evidence', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    sys.path.insert(0, str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_animation import read_animation
    ver = Game_Version.D1_ROI

    tower = EntryReader(a.tower_activity_pkg, a.runtime)
    dest = EntryReader(a.tower_destination_pkg, a.runtime)
    owner = EntryReader(a.generic_owner_pkg, a.runtime)
    anim_reader = EntryReader(a.generic_animation_pkg, a.runtime)
    evidence = json.loads(a.evidence.read_text())

    readers_by_entity = {'80C7AD82': tower, '80C7AE3E': tower, '80CA0CD6': dest}
    owner_readers = {'80C7AE48': tower, '80C7AE49': tower, '809DF581': owner, '809DF582': owner}
    control_readers = {'80C7AE68': tower, '809D856F': anim_reader}
    clip_readers = {'80C7AE98': tower, '809D8572': anim_reader}

    entities = {}
    violations = []
    all_world_ids = []
    for entity, expected in evidence['entities'].items():
        entity = norm(entity)
        parsed = parse_sentity_resources(readers_by_entity[entity], entity)
        resources = set(parsed['resource_hashes'])
        missing_shared = sorted(FAMILY_SHARED - resources)
        expected_pair = [norm(x) for x in expected['animation_owner_pair']]
        missing_owner = [x for x in expected_pair if x not in resources]
        other_pair = ['80C7AE48', '80C7AE49'] if expected_pair[0].startswith('809D') else ['809DF581', '809DF582']
        unexpected_other = [x for x in other_pair if x in resources]
        world_ids = [str(x).upper() for x in expected['world_ids']]
        all_world_ids.extend(world_ids)
        if len(world_ids) != int(expected['runtime_placement_count']):
            violations.append(f'{entity}: evidence placement count mismatch')
        if missing_shared:
            violations.append(f'{entity}: missing shared Family-E resources {missing_shared}')
        if missing_owner:
            violations.append(f'{entity}: missing expected animation owner resources {missing_owner}')
        if unexpected_other:
            violations.append(f'{entity}: unexpectedly contains alternate animation owner resources {unexpected_other}')
        entities[entity] = {
            **parsed,
            'runtime_placement_count': int(expected['runtime_placement_count']),
            'world_ids': world_ids,
            'ownership_scope': expected['ownership_scope'],
            'expected_animation_owner_pair': expected_pair,
            'expected_animation_control': norm(expected['animation_control']),
            'expected_animation_clip': norm(expected['animation_clip']),
            'shared_family_resources_present': not missing_shared,
            'owner_pair_present': not missing_owner,
            'alternate_owner_pair_absent': not unexpected_other,
        }

    if len(all_world_ids) != evidence['family']['runtime_placement_count'] or len(set(all_world_ids)) != len(all_world_ids):
        violations.append('Family-E WorldID evidence is not six unique runtime placements')

    owner_edges = []
    for owner_tag, (off, control_tag) in OWNER_TO_CONTROL.items():
        r = owner_readers[owner_tag]
        e, b = payload(r, owner_tag, ENTITY_RESOURCE_REF)
        if off + 4 > len(b):
            violations.append(f'{owner_tag}: control edge offset 0x{off:X} OOB')
            observed = None
        else:
            observed = f'{u32(b, off):08X}'
            if observed != control_tag:
                violations.append(f'{owner_tag}: control edge {observed} != {control_tag}')
        ce = find_entry(control_readers[control_tag], control_tag, CONTROL_REF)
        owner_edges.append({
            'owner': owner_tag, 'owner_entry_index': e['index'], 'edge_offset': off,
            'observed_control': observed, 'expected_control': control_tag,
            'control_entry_index': ce['index'], 'exact': observed == control_tag,
        })

    controls = {}
    for control_tag, expected_clip in CONTROL_TO_CLIP.items():
        r = control_readers[control_tag]
        e, b = payload(r, control_tag, CONTROL_REF)
        decoded = decode_control(b, r)
        selected = []
        for st in decoded['state_table']['records']:
            selected.extend(x['tag_hash'] for x in st['selected_animations'])
        selected_unique = sorted(set(selected))
        if decoded['animation_list']['count'] != 1 or selected_unique != [expected_clip]:
            violations.append(f'{control_tag}: selected clips {selected_unique}, expected [{expected_clip}]')
        controls[control_tag] = {
            'entry_index': e['index'],
            'animation_list': decoded['animation_list'],
            'state_table': decoded['state_table'],
            'expected_clip': expected_clip,
            'exact_single_clip_selection': decoded['animation_list']['count'] == 1 and selected_unique == [expected_clip],
        }

    se, sb = payload(anim_reader, '809D8613', ENTITY_RESOURCE_REF)
    skeleton = read_skeleton(io.BytesIO(sb), ver)
    skeleton_node_count = len(skeleton.node_defs)
    re, rb = payload(anim_reader, '809D856E', ENTITY_RESOURCE_REF)
    rig = read_runtime_rig(io.BytesIO(rb), ver)
    rig_components = component_rows(rig.rig_components)
    rig_control_count = len(rig.controls_relations)
    rig_sig = sig(rig_components)

    clips = {}
    for clip_tag, r in clip_readers.items():
        row = clip_row(r, clip_tag, read_animation, ver)
        row['component_fingerprint_matches_runtime_rig'] = sig(row['runtime_rig_components']) == rig_sig
        row['node_count_matches_skeleton'] = row['node_count'] == skeleton_node_count
        row['control_count_matches_runtime_rig'] = row['rig_control_count'] == rig_control_count
        row['exact_family_compatible'] = all((
            row['component_fingerprint_matches_runtime_rig'],
            row['node_count_matches_skeleton'],
            row['control_count_matches_runtime_rig'],
        ))
        if not row['exact_family_compatible']:
            violations.append(f'{clip_tag}: clip does not exactly match 67-bone Family-E skeleton/runtime rig')
        clips[clip_tag] = row

    if skeleton_node_count != 67:
        violations.append(f'809D8613 node count {skeleton_node_count} != 67')
    if rig_control_count != 67:
        violations.append(f'809D856E control count {rig_control_count} != 67')

    for entity, row in entities.items():
        control = row['expected_animation_control']
        clip = row['expected_animation_clip']
        row['selection_status'] = 'owner_selected' if (
            row['owner_pair_present'] and row['alternate_owner_pair_absent'] and
            controls[control]['exact_single_clip_selection'] and clips[clip]['exact_family_compatible']
        ) else 'unresolved'
        if row['selection_status'] != 'owner_selected':
            violations.append(f'{entity}: animation selection did not close')

    out = {
        'schema_version': 1,
        'status': 'D1_TOWER_FAMILY_E_ANIMATION_OWNERSHIP_CLOSED' if not violations else 'D1_TOWER_FAMILY_E_ANIMATION_OWNERSHIP_PARTIAL',
        'family': {
            'model_parent_resource': '80CA0CD8', 'entity_model': '80CA0CFC',
            'skeleton_resource': '809D8613', 'skeleton_node_count': skeleton_node_count,
            'runtime_rig_resource': '809D856E', 'runtime_rig_control_count': rig_control_count,
            'runtime_rig_components': rig_components,
            'runtime_placement_count': len(all_world_ids), 'unique_world_id_count': len(set(all_world_ids)),
        },
        'entities': entities,
        'owner_control_edges': owner_edges,
        'controls': controls,
        'clips': clips,
        'violations': violations,
        'policy': 'Owner-selected means the source-owned WorldID->SEntity evidence, literal SEntity owner-resource membership, literal owner->control edge, decoded control-selected clip, and exact skeleton/runtime-rig clip compatibility all agree. Clip semantic names remain unresolved.',
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'], 'family': out['family'],
        'entity_selection_status': {k: v['selection_status'] for k, v in entities.items()},
        'clip_summary': {k: {x: v[x] for x in ('frame_count','node_count','rig_control_count','exact_family_compatible')} for k, v in clips.items()},
        'violations': violations,
    }, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
