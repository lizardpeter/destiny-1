#!/usr/bin/env python3
"""Close or bound animation ownership for D1 Tower articulated Family F.

Family F is source-owned and already closed structurally as:

    EntityModel 80C7AF4C
    skeleton    80C7AF3A (2 nodes)
    runtime rig 80C7AF40 (2 controls)
    SEntities   80C7ADE5, 80C7AE14, 80C7AE15, 80C7AE16, 80C7AE1B
    runtime placements 8

All five SEntities contain the same two EntityResource class pairs that act as the
animation-owner pair in the already-closed 67-bone Family E architecture:

    80C7AF3D  808020BF -> 808029D2
    80C7AF3F  80802B92 -> 808020BB

This probe does not infer that structural homology is sufficient.  It validates the
class pairs from retail bytes, reads the exact homologous FileHash slots (+0x110 and
+0x448), requires both owner halves to converge on one 80802C0E animation control,
decodes that control, and independently tests every referenced animation clip against
the exact 2-node skeleton/runtime-rig dimensions and component fingerprint.

A control with multiple selected clips/states is reported as such; this tool never
chooses a default state, loop behavior, or semantic animation name from appearance.
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
from d1_entity_resource_probe import parse_resource
from d1_animation_control_state_map import decode_control
from d1_animation_retarget_probe import component_rows

ENTITY_RESOURCE_REF = '80800861'
CONTROL_REF = '80802C0E'
CLIP_REF = '808005A1'

MODEL = '80C7AF4C'
SKELETON = '80C7AF3A'
RIG = '80C7AF40'
OWNER_HALVES = {
    '80C7AF3D': {
        'expected_pair': ('808020BF', '808029D2'),
        'control_offset': 0x110,
    },
    '80C7AF3F': {
        'expected_pair': ('80802B92', '808020BB'),
        'control_offset': 0x448,
    },
}
ENTITY_WORLD_IDS = {
    '80C7ADE5': ['064E5A7957373FA3'],
    '80C7AE14': ['29191E38D272B06B', '4FB47A0143A95F31', '747235765D9899D9', 'CFEA129378E00812'],
    '80C7AE15': ['0F6676AA91C2392A'],
    '80C7AE16': ['A7D4B393917E2436'],
    '80C7AE1B': ['6CB2EB24B545063B'],
}


def norm(x) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def u32(b: bytes, off: int) -> int:
    return struct.unpack_from('<I', b, off)[0]


def entry_map(r: EntryReader) -> dict[str, dict]:
    return {norm(e['tag_hash']): e for e in r.entries}


def exact_payload(r: EntryReader, by: dict[str, dict], tag: str,
                  expected_ref: str | None = None) -> tuple[dict, bytes]:
    tag = norm(tag)
    e = by.get(tag)
    if e is None:
        raise ValueError(f'{tag}: absent from package {int(r.h["pkg_id"]):04X}')
    if expected_ref is not None and norm(e['reference']) != norm(expected_ref):
        raise ValueError(f'{tag}: reference {norm(e["reference"])} != {norm(expected_ref)}')
    if not r.available(e['index']):
        raise ValueError(f'{tag}: payload unavailable; complete logical siblings must be staged')
    return e, r.entry(e['index'])


def dyn_resources(b: bytes) -> list[str]:
    # D1 SEntity dynamic EntityResource array, same validated layout used by the
    # Tower dependency census: +0x20 count/relative-array pointer, stride 0x0C.
    if len(b) < 0x2C:
        raise ValueError('SEntity payload too short')
    count = u32(b, 0x20)
    rel = u32(b, 0x28)
    hdr = 0x28 + rel
    if hdr < 0 or hdr + 0x10 > len(b):
        raise ValueError(f'SEntity resource array header OOB: 0x{hdr:X}')
    repeated = u32(b, hdr)
    if repeated != count:
        raise ValueError(f'SEntity resource count mismatch {count} != {repeated}')
    data = hdr + 0x10
    end = data + count * 0x0C
    if end > len(b):
        raise ValueError(f'SEntity resource array OOB: 0x{end:X} > 0x{len(b):X}')
    return [f'{u32(b, data + i * 0x0C):08X}' for i in range(count)]


def filebacked(read_animation, payload: bytes, version):
    with tempfile.NamedTemporaryFile() as f:
        f.write(payload)
        f.flush()
        f.seek(0)
        return read_animation(f, version)


def sig(rows: list[dict]) -> tuple[tuple[str, int], ...]:
    return tuple((norm(x['hash']), int(x['count'])) for x in rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--activity-pkg', type=Path, required=True,
                    help='023D_5 with all logical 023D siblings staged beside it')
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--parser-root', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    r = EntryReader(a.activity_pkg, a.runtime)
    by = entry_map(r)
    violations: list[str] = []

    # Re-prove all five SEntity owners contain the same Family-F identity and both
    # owner halves.  This makes the WorldID -> SEntity -> owner-pair chain durable
    # in one report instead of relying on an expiring earlier artifact.
    entity_rows = {}
    expected_shared = {SKELETON, '80C7AF39', RIG, *OWNER_HALVES.keys()}
    all_world_ids = []
    for entity, world_ids in ENTITY_WORLD_IDS.items():
        e, b = exact_payload(r, by, entity, '80800734')
        resources = dyn_resources(b)
        missing = sorted(expected_shared - set(resources))
        if missing:
            violations.append(f'{entity}: missing Family-F resources {missing}')
        all_world_ids.extend(world_ids)
        entity_rows[entity] = {
            'entry_index': int(e['index']),
            'size': int(e['file_size']),
            'resource_count': len(resources),
            'resource_hashes': resources,
            'runtime_placement_count': len(world_ids),
            'world_ids': world_ids,
            'family_resources_present': not missing,
        }
    if len(all_world_ids) != 8 or len(set(all_world_ids)) != 8:
        violations.append(f'Family-F WorldID domain expected 8 unique values, got {len(all_world_ids)}/{len(set(all_world_ids))}')

    # Validate both owner-resource classes and literal FileHash slots.
    owner_rows = {}
    observed_controls = []
    for owner, cfg in OWNER_HALVES.items():
        e, b = exact_payload(r, by, owner, ENTITY_RESOURCE_REF)
        parsed = parse_resource(b, r.h['platform'])
        observed_pair = (
            norm((parsed.get('unk10') or {}).get('class_hash', '0')),
            norm((parsed.get('unk18') or {}).get('class_hash', '0')),
        )
        expected_pair = tuple(norm(x) for x in cfg['expected_pair'])
        if observed_pair != expected_pair:
            violations.append(f'{owner}: class pair {observed_pair} != {expected_pair}')
        off = int(cfg['control_offset'])
        if off + 4 > len(b):
            violations.append(f'{owner}: control FileHash slot 0x{off:X} OOB')
            control = None
        else:
            control = f'{u32(b, off):08X}'
            observed_controls.append(control)
        owner_rows[owner] = {
            'entry_index': int(e['index']), 'size': int(e['file_size']),
            'expected_class_pair': list(expected_pair), 'observed_class_pair': list(observed_pair),
            'control_filehash_offset': off, 'observed_control': control,
            'class_pair_exact': observed_pair == expected_pair,
        }

    unique_controls = sorted(set(x for x in observed_controls if x is not None))
    control_tag = unique_controls[0] if len(unique_controls) == 1 else None
    if len(unique_controls) != 1:
        violations.append(f'Family-F owner halves do not converge on one control: {unique_controls}')

    control_row = None
    selected_unique: list[str] = []
    animation_list_unique: list[str] = []
    if control_tag is not None:
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

    # Parse exact Family-F skeleton and runtime rig, then test all animation-list clips.
    sys.path.insert(0, str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_animation import read_animation
    ver = Game_Version.D1_ROI

    _, sb = exact_payload(r, by, SKELETON, ENTITY_RESOURCE_REF)
    sk = read_skeleton(io.BytesIO(sb), ver)
    _, rb = exact_payload(r, by, RIG, ENTITY_RESOURCE_REF)
    rig = read_runtime_rig(io.BytesIO(rb), ver)
    node_count = len(sk.node_defs)
    control_count = len(rig.controls_relations)
    rig_components = component_rows(rig.rig_components)
    rig_signature = sig(rig_components)
    if node_count != 2:
        violations.append(f'{SKELETON}: skeleton node count {node_count} != 2')
    if control_count != 2:
        violations.append(f'{RIG}: runtime rig control count {control_count} != 2')

    clip_rows = {}
    for clip in animation_list_unique:
        row = {'tag_hash': clip, 'selected_by_any_state': clip in selected_unique}
        e = by.get(clip)
        if e is None:
            row['status'] = 'absent_from_023d_entry_table'
            row['exact_family_compatible'] = False
            if clip in selected_unique:
                violations.append(f'{clip}: selected clip absent from 023D entry table')
            clip_rows[clip] = row
            continue
        row['entry_index'] = int(e['index'])
        row['reference'] = norm(e['reference'])
        row['size'] = int(e['file_size'])
        if norm(e['reference']) != CLIP_REF:
            row['status'] = 'wrong_reference_class'
            row['exact_family_compatible'] = False
            if clip in selected_unique:
                violations.append(f'{clip}: selected FileHash ref {norm(e["reference"])} != {CLIP_REF}')
            clip_rows[clip] = row
            continue
        if not r.available(e['index']):
            row['status'] = 'payload_unavailable_in_staged_logical_family'
            row['exact_family_compatible'] = False
            if clip in selected_unique:
                violations.append(f'{clip}: selected clip payload unavailable')
            clip_rows[clip] = row
            continue
        try:
            anim = filebacked(read_animation, r.entry(e['index']), ver)
            h = anim.animation_header
            comps = component_rows(anim.runtime_rig_components)
            row.update({
                'status': 'parsed',
                'frame_count': int(h.frame_count),
                'node_count': int(h.node_count),
                'rig_control_count': int(h.rig_control_count),
                'runtime_rig_components': comps,
                'component_fingerprint_matches_runtime_rig': sig(comps) == rig_signature,
                'node_count_matches_skeleton': int(h.node_count) == node_count,
                'control_count_matches_runtime_rig': int(h.rig_control_count) == control_count,
            })
            row['exact_family_compatible'] = all((
                row['component_fingerprint_matches_runtime_rig'],
                row['node_count_matches_skeleton'],
                row['control_count_matches_runtime_rig'],
            ))
            if clip in selected_unique and not row['exact_family_compatible']:
                violations.append(f'{clip}: selected clip is not exact Family-F compatible')
        except Exception as ex:
            row['status'] = 'parse_failed'
            row['error'] = repr(ex)
            row['exact_family_compatible'] = False
            if clip in selected_unique:
                violations.append(f'{clip}: selected clip parse failed: {ex!r}')
        clip_rows[clip] = row

    selected_compatible = bool(selected_unique) and all(
        clip_rows.get(x, {}).get('exact_family_compatible') for x in selected_unique
    )
    owner_pair_exact = (
        len(unique_controls) == 1 and
        all(x['class_pair_exact'] and x['observed_control'] == control_tag for x in owner_rows.values())
    )
    selection_status = (
        'owner_control_selected_set_closed'
        if owner_pair_exact and control_row is not None and selected_compatible and not violations
        else 'partial'
    )

    out = {
        'schema_version': 1,
        'status': 'D1_TOWER_FAMILY_F_ANIMATION_OWNER_CONTROL_CLOSED' if selection_status != 'partial' else 'D1_TOWER_FAMILY_F_ANIMATION_OWNER_CONTROL_PARTIAL',
        'family': {
            'entity_model': MODEL, 'skeleton_resource': SKELETON,
            'skeleton_node_count': node_count, 'runtime_rig_resource': RIG,
            'runtime_rig_control_count': control_count, 'runtime_rig_components': rig_components,
            'sentity_count': len(ENTITY_WORLD_IDS), 'runtime_placement_count': len(all_world_ids),
            'unique_world_id_count': len(set(all_world_ids)),
        },
        'entities': entity_rows,
        'owner_halves': owner_rows,
        'owner_halves_converge': len(unique_controls) == 1,
        'animation_control': control_row,
        'unique_selected_clip_hashes': selected_unique,
        'clips': clip_rows,
        'selection_status': selection_status,
        'violations': violations,
        'policy': (
            'Owner/control closure requires exact SEntity membership, exact owner-resource class pairs, '
            'literal homologous FileHash slots converging on one 80802C0E control, decoded control selections, '
            'and exact selected-clip skeleton/runtime-rig compatibility. Multiple state-selected clips remain '
            'multiple actions; no default state, loop, synchronization, NPC/vendor role, or human-readable '
            'semantic is inferred.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'], 'family': out['family'],
        'owner_halves': out['owner_halves'],
        'control': control_tag,
        'animation_list': animation_list_unique,
        'selected_clips': selected_unique,
        'clip_summary': {k: {
            'status': v.get('status'), 'frame_count': v.get('frame_count'),
            'node_count': v.get('node_count'), 'rig_control_count': v.get('rig_control_count'),
            'selected': v.get('selected_by_any_state'),
            'exact_family_compatible': v.get('exact_family_compatible'),
        } for k, v in clip_rows.items()},
        'selection_status': selection_status,
        'violations': violations,
    }, indent=2))
    return 0 if selection_status != 'partial' else 2


if __name__ == '__main__':
    raise SystemExit(main())
