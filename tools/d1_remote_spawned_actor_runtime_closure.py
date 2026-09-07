#!/usr/bin/env python3
"""Close D1 Tower spawned actor runtime assemblies through the universal retail corpus.

Input is the exact 57-EntitySK source seed recovered from the Tower scenario AI path.
For every spawned actor this probe reopens the complete SEntity resource list and
requires one exact skeleton, runtime rig, EntityChildren resource, and both halves of
the already source-proven D1 animation-owner architecture:

    low   808020BF -> 808029D2, control FileHash at +0x110
    high  80802B92 -> 808020BB, control FileHash at +0x448

Both halves must converge on one exact 80802C0E animation control.  The selector table
is decoded from retail bytes and every selected 808005A1 clip is independently parsed
and compared against the exact source-owned skeleton/runtime-rig dimensions and runtime
component fingerprint.

The four shared EntityChildren resources used by this population are decoded with the
Charm-pinned ROI layout, preserving child Entity FileHashes and all literal transforms.
One child level is then classified through the same SEntity dependency parser when the
child itself is an exact 80800734 SEntity.

No actor identity, default action, child socket, held-prop semantic, or location is
inferred from geometry or proximity.  Name hashes are merely carried forward from the
source-owned SEntity resources.
"""
from __future__ import annotations

import argparse
import collections
import io
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_animation_control_state_map import decode_control
from d1_animation_retarget_probe import component_rows
from d1_entity_resource_probe import parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_remote_entity_child_find import parse_children_resource
from d1_split_tar_extract import SplitHttpTar
from d1_world_entity_dependency_census import parse_entity

SENTITY = '80800734'
ENTITY_RESOURCE = '80800861'
CONTROL = '80802C0E'
CLIP = '808005A1'
LOW_PAIR = ('808020BF', '808029D2')
HIGH_PAIR = ('80802B92', '808020BB')
RIG_PAIR = ('808008B2', '8080099B')
SKELETON_PAIR = ('808006BD', '8080049A')
CHILDREN_PAIR = ('80802663', '80802708')
LOW_CONTROL_OFFSET = 0x110
HIGH_CONTROL_OFFSET = 0x448
NULLS = {'00000000', 'FFFFFFFF'}


def norm(x) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def u32(b: bytes, off: int) -> int:
    import struct
    if off < 0 or off + 4 > len(b):
        raise ValueError(f'u32 OOB at 0x{off:X}/0x{len(b):X}')
    return struct.unpack_from('<I', b, off)[0]


def pair_of_resource_row(row: dict) -> tuple[str, str] | None:
    er = row.get('entity_resource') or {}
    a = (er.get('unk10') or {}).get('class_hash')
    b = (er.get('unk18') or {}).get('class_hash')
    if not a or not b:
        return None
    return norm(a), norm(b)


def rows_for_pair(entity_row: dict, pair: tuple[str, str]) -> list[dict]:
    p = tuple(norm(x) for x in pair)
    return [r for r in entity_row.get('resources', []) if pair_of_resource_row(r) == p]


def rows_for_role(entity_row: dict, role: str) -> list[dict]:
    return [r for r in entity_row.get('resources', [])
            if (r.get('entity_resource') or {}).get('semantic_role') == role]


def exact_remote_payload(c: RemoteCorpus, tag: str, expected_ref: str | None = None) -> tuple[dict, bytes, str | None]:
    tag = norm(tag)
    m = c.entry_meta(tag)
    b, src = c.payload(tag)
    if m is None or b is None:
        raise ValueError(f'{tag}: exact payload unavailable')
    ref = norm(m.get('reference', 'FFFFFFFF'))
    if expected_ref is not None and ref != norm(expected_ref):
        raise ValueError(f'{tag}: reference {ref} != {norm(expected_ref)}')
    return m, b, src


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
    ap.add_argument('--seed', type=Path, required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--parser-root', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    seed = json.loads(a.seed.read_text())
    entities = sorted({norm(x) for x in seed.get('entity_hashes', []) if norm(x) not in NULLS})
    if not entities:
        raise SystemExit('seed contains no entity_hashes')

    cats = load_catalogs(a.member_catalog)
    arc = SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    c = RemoteCorpus(arc, cats, a.runtime)

    sys.path.insert(0, str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_animation import read_animation
    ver = Game_Version.D1_ROI

    violations: list[str] = []
    actor_rows: dict[str, dict] = {}
    unique_controls: dict[str, dict] = {}
    unique_skeletons: dict[str, dict] = {}
    unique_rigs: dict[str, dict] = {}
    unique_children: dict[str, dict] = {}
    unique_models = collections.Counter()

    # Reopen every spawned SEntity and identify the literal assembly resources.
    for idx, h in enumerate(entities, 1):
        try:
            erow = parse_entity(c, h)
        except Exception as ex:
            violations.append(f'{h}:parse_entity:{ex!r}')
            actor_rows[h] = {'entity': h, 'error': repr(ex)}
            continue
        for v in erow.get('violations', []):
            violations.append(f'{h}:{v}')
        comp = erow.get('composition') or {}

        lows = rows_for_pair(erow, LOW_PAIR)
        highs = rows_for_pair(erow, HIGH_PAIR)
        rigs = rows_for_pair(erow, RIG_PAIR)
        skels = rows_for_pair(erow, SKELETON_PAIR)
        children = rows_for_pair(erow, CHILDREN_PAIR)
        model_rows = rows_for_role(erow, 'entity_model')

        expected_one = {'low_owner': lows, 'high_owner': highs, 'runtime_rig': rigs,
                        'skeleton': skels, 'children': children, 'model': model_rows}
        for kind, rs in expected_one.items():
            if len(rs) != 1:
                violations.append(f'{h}:{kind}_count_{len(rs)}_not_1')

        model_tag = None
        if len(model_rows) == 1:
            model_tag = norm((model_rows[0].get('entity_resource') or {}).get('embedded_model_tag_hash', 'FFFFFFFF'))
            if model_tag not in NULLS:
                unique_models[model_tag] += 1

        low = norm(lows[0]['resource_hash']) if len(lows) == 1 else None
        high = norm(highs[0]['resource_hash']) if len(highs) == 1 else None
        rig = norm(rigs[0]['resource_hash']) if len(rigs) == 1 else None
        skel = norm(skels[0]['resource_hash']) if len(skels) == 1 else None
        child = norm(children[0]['resource_hash']) if len(children) == 1 else None

        low_control = None
        high_control = None
        for side, owner, off, expected_pair in (
            ('low', low, LOW_CONTROL_OFFSET, LOW_PAIR),
            ('high', high, HIGH_CONTROL_OFFSET, HIGH_PAIR),
        ):
            if owner is None:
                continue
            try:
                om, ob, osrc = exact_remote_payload(c, owner, ENTITY_RESOURCE)
                parsed = parse_resource(ob)
                observed_pair = (
                    norm((parsed.get('unk10') or {}).get('class_hash', '0')),
                    norm((parsed.get('unk18') or {}).get('class_hash', '0')),
                )
                if observed_pair != expected_pair:
                    violations.append(f'{h}:{owner}:{side}_pair_{observed_pair}_not_{expected_pair}')
                if off + 4 > len(ob):
                    raise ValueError(f'control slot 0x{off:X} OOB')
                ctl = f'{u32(ob, off):08X}'
                cm = c.entry_meta(ctl)
                cref = None if cm is None else norm(cm.get('reference', 'FFFFFFFF'))
                if cm is None or cref != CONTROL:
                    violations.append(f'{h}:{owner}:{side}_control_{ctl}_ref_{cref}_not_{CONTROL}')
                if side == 'low':
                    low_control = ctl
                else:
                    high_control = ctl
            except Exception as ex:
                violations.append(f'{h}:{owner}:{side}_owner_decode:{ex!r}')

        control = low_control if low_control and low_control == high_control else None
        if control is None:
            violations.append(f'{h}:owner_controls_do_not_converge:{low_control}/{high_control}')

        actor_rows[h] = {
            'entity': h,
            'classification': comp.get('classification'),
            'specific_name_hashes': comp.get('specific_name_hashes', []),
            'generic_name_hashes': comp.get('generic_name_hashes', []),
            'bone_counts_from_dependency_parser': comp.get('bone_counts', []),
            'model': model_tag,
            'skeleton_resource': skel,
            'runtime_rig_resource': rig,
            'children_resource': child,
            'animation_owner_low': low,
            'animation_owner_high': high,
            'low_control': low_control,
            'high_control': high_control,
            'animation_control': control,
            'resource_count': erow.get('resource_count'),
        }
        print('ACTOR', idx, h, 'bones', comp.get('bone_counts'), 'control', control, 'model', model_tag, flush=True)

    # Parse every unique skeleton and runtime rig exactly once.
    for h in sorted({x.get('skeleton_resource') for x in actor_rows.values() if x.get('skeleton_resource')}):
        row = {'tag_hash': h}
        try:
            m, b, src = exact_remote_payload(c, h, ENTITY_RESOURCE)
            sk = read_skeleton(io.BytesIO(b), ver)
            row.update(source=src, node_count=len(sk.node_defs))
        except Exception as ex:
            row['error'] = repr(ex)
            violations.append(f'{h}:skeleton_parse:{ex!r}')
        unique_skeletons[h] = row

    for h in sorted({x.get('runtime_rig_resource') for x in actor_rows.values() if x.get('runtime_rig_resource')}):
        row = {'tag_hash': h}
        try:
            m, b, src = exact_remote_payload(c, h, ENTITY_RESOURCE)
            rig = read_runtime_rig(io.BytesIO(b), ver)
            comps = component_rows(rig.rig_components)
            row.update(source=src, control_count=len(rig.controls_relations), runtime_rig_components=comps,
                       component_signature=[list(x) for x in sig(comps)])
        except Exception as ex:
            row['error'] = repr(ex)
            violations.append(f'{h}:runtime_rig_parse:{ex!r}')
        unique_rigs[h] = row

    # Decode each unique animation control and every selected clip.
    controls = sorted({x.get('animation_control') for x in actor_rows.values() if x.get('animation_control')})
    unique_clips: dict[str, dict] = {}
    for ch in controls:
        crow = {'tag_hash': ch}
        try:
            cm, cb, csrc = exact_remote_payload(c, ch, CONTROL)
            dec = decode_control(cb, None, [])
            animation_list = [norm(x['tag_hash']) for x in dec['animation_list']['items']]
            selected = sorted({norm(x['tag_hash']) for st in dec['state_table']['records'] for x in st['selected_animations']})
            crow.update(source=csrc, animation_list=animation_list, unique_selected_clips=selected,
                        state_table=dec['state_table'])
            for clip in selected:
                if clip in unique_clips:
                    continue
                x = {'tag_hash': clip}
                try:
                    mm, bb, src = exact_remote_payload(c, clip, CLIP)
                    an = filebacked(read_animation, bb, ver)
                    hdr = an.animation_header
                    comps = component_rows(an.runtime_rig_components)
                    x.update(source=src, frame_count=int(hdr.frame_count), node_count=int(hdr.node_count),
                             rig_control_count=int(hdr.rig_control_count), runtime_rig_components=comps,
                             component_signature=[list(z) for z in sig(comps)])
                except Exception as ex:
                    x['error'] = repr(ex)
                    violations.append(f'{clip}:animation_parse:{ex!r}')
                unique_clips[clip] = x
        except Exception as ex:
            crow['error'] = repr(ex)
            violations.append(f'{ch}:control_decode:{ex!r}')
        unique_controls[ch] = crow

    # Per-actor exact clip compatibility against the actor's own skeleton/runtime rig.
    for h, row in actor_rows.items():
        ch = row.get('animation_control')
        skh = row.get('skeleton_resource')
        rgh = row.get('runtime_rig_resource')
        selected = (unique_controls.get(ch) or {}).get('unique_selected_clips', []) if ch else []
        sn = (unique_skeletons.get(skh) or {}).get('node_count') if skh else None
        rc = (unique_rigs.get(rgh) or {}).get('control_count') if rgh else None
        rsig = (unique_rigs.get(rgh) or {}).get('component_signature') if rgh else None
        compat = []
        for clip in selected:
            cr = unique_clips.get(clip) or {}
            ok = (
                cr.get('node_count') == sn and
                cr.get('rig_control_count') == rc and
                cr.get('component_signature') == rsig
            )
            compat.append({'clip': clip, 'frame_count': cr.get('frame_count'), 'compatible': ok})
            if not ok:
                violations.append(f'{h}:{clip}:clip_not_exact_runtime_compatible')
        row['skeleton_node_count'] = sn
        row['runtime_rig_control_count'] = rc
        row['selected_clips'] = compat
        row['selected_clip_count'] = len(compat)
        row['all_selected_clips_exact_compatible'] = bool(compat) and all(x['compatible'] for x in compat)
        if not compat:
            violations.append(f'{h}:no_selected_clips')

    # Decode every unique source-owned children resource and classify one child level.
    child_entities = set()
    for rh in sorted({x.get('children_resource') for x in actor_rows.values() if x.get('children_resource')}):
        rr = {'resource_hash': rh}
        try:
            rm, rb, src = exact_remote_payload(c, rh, ENTITY_RESOURCE)
            parsed = parse_children_resource(rb)
            if parsed is None:
                raise ValueError('resource did not decode as D1 EntityChildren')
            rr.update(source=src, **parsed)
            for child in parsed.get('children', []):
                eh = norm(child.get('entity_hash', 'FFFFFFFF'))
                if eh not in NULLS:
                    child_entities.add(eh)
                    mm = c.entry_meta(eh)
                    child['resolved_reference'] = None if mm is None else norm(mm.get('reference', 'FFFFFFFF'))
        except Exception as ex:
            rr['error'] = repr(ex)
            violations.append(f'{rh}:children_parse:{ex!r}')
        unique_children[rh] = rr

    child_entity_rows = {}
    for eh in sorted(child_entities):
        mm = c.entry_meta(eh)
        ref = None if mm is None else norm(mm.get('reference', 'FFFFFFFF'))
        row = {'entity': eh, 'reference': ref}
        if ref == SENTITY:
            try:
                pr = parse_entity(c, eh)
                comp = pr.get('composition') or {}
                row.update(classification=comp.get('classification'), bone_counts=comp.get('bone_counts', []),
                           specific_name_hashes=comp.get('specific_name_hashes', []),
                           generic_name_hashes=comp.get('generic_name_hashes', []),
                           resource_count=pr.get('resource_count'), violations=pr.get('violations', []))
                for v in pr.get('violations', []):
                    violations.append(f'child:{eh}:{v}')
                mrows = rows_for_role(pr, 'entity_model')
                row['models'] = sorted({norm((x.get('entity_resource') or {}).get('embedded_model_tag_hash')) for x in mrows
                                        if (x.get('entity_resource') or {}).get('embedded_model_tag_hash')})
            except Exception as ex:
                row['error'] = repr(ex)
                violations.append(f'child:{eh}:parse_entity:{ex!r}')
        child_entity_rows[eh] = row

    # Collapse duplicate SEntities into exact reusable runtime architectures.
    architectures: dict[str, dict] = {}
    key_to_id = {}
    for h, row in actor_rows.items():
        key = (
            row.get('model'), row.get('skeleton_resource'), row.get('runtime_rig_resource'),
            row.get('children_resource'), row.get('animation_owner_low'), row.get('animation_owner_high'),
            row.get('animation_control'), row.get('skeleton_node_count'), row.get('runtime_rig_control_count'),
        )
        if key not in key_to_id:
            aid = f'ARCH_{len(key_to_id)+1:02d}'
            key_to_id[key] = aid
            architectures[aid] = {
                'model': key[0], 'skeleton_resource': key[1], 'runtime_rig_resource': key[2],
                'children_resource': key[3], 'animation_owner_low': key[4], 'animation_owner_high': key[5],
                'animation_control': key[6], 'skeleton_node_count': key[7], 'runtime_rig_control_count': key[8],
                'entities': [], 'specific_name_hashes': collections.Counter(), 'generic_name_hashes': collections.Counter(),
            }
        aid = key_to_id[key]
        architectures[aid]['entities'].append(h)
        architectures[aid]['specific_name_hashes'].update(row.get('specific_name_hashes', []))
        architectures[aid]['generic_name_hashes'].update(row.get('generic_name_hashes', []))
    for arow in architectures.values():
        arow['entity_count'] = len(arow['entities'])
        arow['specific_name_hashes'] = dict(arow['specific_name_hashes'])
        arow['generic_name_hashes'] = dict(arow['generic_name_hashes'])
        ctl = unique_controls.get(arow.get('animation_control')) or {}
        arow['unique_selected_clips'] = ctl.get('unique_selected_clips', [])
        arow['selected_clip_frames'] = {h: (unique_clips.get(h) or {}).get('frame_count') for h in arow['unique_selected_clips']}

    control_counts = collections.Counter(x.get('animation_control') for x in actor_rows.values() if x.get('animation_control'))
    bone_counts = collections.Counter(str(x.get('skeleton_node_count')) for x in actor_rows.values() if x.get('skeleton_node_count') is not None)
    child_resource_counts = collections.Counter(x.get('children_resource') for x in actor_rows.values() if x.get('children_resource'))

    closed_entities = [h for h, x in actor_rows.items()
                       if x.get('animation_control') and x.get('all_selected_clips_exact_compatible')]
    out = {
        'schema_version': 1,
        'status': 'D1_TOWER_SPAWNED_ACTOR_RUNTIME_CLOSURE_COMPLETE' if not violations and len(closed_entities) == len(entities)
                  else 'D1_TOWER_SPAWNED_ACTOR_RUNTIME_CLOSURE_PARTIAL',
        'seed_status': seed.get('status'),
        'entity_count': len(entities),
        'runtime_closed_entity_count': len(closed_entities),
        'runtime_closed_entities': closed_entities,
        'architecture_count': len(architectures),
        'architectures': architectures,
        'bone_count_frequency': dict(sorted(bone_counts.items(), key=lambda kv: int(kv[0]))),
        'animation_control_reference_counts': dict(control_counts),
        'children_resource_reference_counts': dict(child_resource_counts),
        'unique_model_count': len(unique_models),
        'model_reference_counts': dict(unique_models),
        'actors': actor_rows,
        'skeletons': unique_skeletons,
        'runtime_rigs': unique_rigs,
        'animation_controls': unique_controls,
        'animation_clips': unique_clips,
        'children_resources': unique_children,
        'child_entities': child_entity_rows,
        'child_entity_count': len(child_entity_rows),
        'violations': violations,
        'remote_logical_package_count': len(c.views),
        'remote_payload_cache_count': len(c.payload_cache),
        'policy': (
            'Actor assembly is source-owned SEntity data only. Animation closure requires both literal owner FileHash slots '
            'to converge on an exact 80802C0E control and every selector-selected clip to match the exact actor skeleton, '
            'runtime-rig control count, and runtime component fingerprint. EntityChildren FileHashes/transforms are literal '
            'retail data. No default action, actor identity meaning, child socket/prop meaning, or spawn location is inferred.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')

    print('STATUS', out['status'])
    print('ENTITIES', out['entity_count'], 'CLOSED', out['runtime_closed_entity_count'], 'ARCHITECTURES', out['architecture_count'])
    print('BONES', out['bone_count_frequency'])
    print('CONTROLS', out['animation_control_reference_counts'])
    print('CHILDREN_RESOURCES', out['children_resource_reference_counts'])
    print('CHILD_ENTITIES', out['child_entity_count'])
    for aid, ar in architectures.items():
        print('ARCH', aid, 'N', ar['entity_count'], 'BONES', ar['skeleton_node_count'], 'MODEL', ar['model'],
              'RIG', ar['runtime_rig_resource'], 'CONTROL', ar['animation_control'], 'CHILDREN', ar['children_resource'],
              'CLIPS', ar['selected_clip_frames'], 'SPECIFIC', ar['specific_name_hashes'])
    for rh, rr in unique_children.items():
        print('CHILD_RESOURCE', rh, 'COUNT', rr.get('child_count'))
        for ch in rr.get('children', []):
            print(' CHILD', ch.get('entity_hash'), 'REF', ch.get('resolved_reference'), 'TRANSFORMS', ch.get('transform_count'))
    print('VIOLATION_COUNT', len(violations))
    for v in violations[:100]:
        print('VIOLATION', v)
    return 0 if out['status'].endswith('_COMPLETE') else 2


if __name__ == '__main__':
    raise SystemExit(main())
