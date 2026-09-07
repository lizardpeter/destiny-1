#!/usr/bin/env python3
"""Source-close animation-control options for arbitrary D1 spawned actor SEntities.

This generalizes the exact Tower Family-E ownership proof without assigning a
semantic default action. For each requested SEntity it reopens the retail Resource[]
array, identifies only source-typed resources, and follows the two calibrated D1
animation-owner pairs:

    808020BF -> 808029D2  owner edge at +0x110
    80802B92 -> 808020BB  owner edge at +0x448

Each literal edge must resolve to class 80802C0E. The control payload is then decoded
with the validated selector parser; every state hash, known FNV1 preimage, packed
selection and selected animation FileHash is preserved. Every referenced clip is
reopened as class 808005A1 and checked against the exact entity skeleton/runtime rig:
node count, runtime-rig control count and ordered runtime-component fingerprint.

No state is promoted to "idle", "default" or "startup" unless the control table
itself has a known exact FNV1 preimage. All compatible state/clip choices survive in
the output so historical/conditional actor variants can be exported later.
"""
from __future__ import annotations

import argparse
import io
import json
import struct
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_animation_control_state_map import decode_control
from d1_animation_retarget_probe import component_rows
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS, parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_remote_s_entity_resource_package_find import S_ENTITY_REF, parse_entity_resources
from d1_skeleton_probe import parse_skeleton_resource
from d1_split_tar_extract import SplitHttpTar

NULLS = {'00000000', 'FFFFFFFF'}
CONTROL_REF = '80802C0E'
CLIP_REF = '808005A1'
RUNTIME_RIG_PAIR = ('808008B2', '8080099B')
OWNER_EDGES = {
    ('808020BF', '808029D2'): 0x110,
    ('80802B92', '808020BB'): 0x448,
}


def norm(x):
    return str(x).upper().removeprefix('0X').zfill(8)


def u32(b: bytes, o: int) -> int:
    if o < 0 or o + 4 > len(b):
        raise ValueError(f'u32 OOB at 0x{o:X}/0x{len(b):X}')
    return struct.unpack_from('<I', b, o)[0]


def exact(c: RemoteCorpus, h: str, expected_ref: str | None = None) -> tuple[dict, bytes, str]:
    h = norm(h)
    m = c.entry_meta(h)
    b, src = c.payload(h)
    if m is None or b is None:
        raise KeyError(f'{h}: exact payload unavailable')
    if expected_ref is not None and norm(m.get('reference')) != norm(expected_ref):
        raise ValueError(f'{h}: reference {norm(m.get("reference"))} != {norm(expected_ref)}')
    return m, b, str(src)


def filebacked(read_animation, b: bytes, version):
    with tempfile.NamedTemporaryFile() as f:
        f.write(b)
        f.flush()
        f.seek(0)
        return read_animation(f, version)


def sig(rows: list[dict]) -> tuple[tuple[str, int], ...]:
    return tuple((norm(x['hash']), int(x['count'])) for x in rows)


def entity_resources(c: RemoteCorpus, entity: str) -> list[dict]:
    _, b, _ = exact(c, entity, S_ENTITY_REF)
    out = []
    for rr in parse_entity_resources(b):
        rh = norm(rr['resource_hash'])
        if rh in NULLS:
            continue
        rm, rb, rsrc = exact(c, rh)
        row = {
            'resource_index': int(rr['resource_index']),
            'resource_hash': rh,
            'reference': norm(rm.get('reference')),
            'source': rsrc,
        }
        if row['reference'] == ENTITY_RESOURCE_CLASS:
            pr = parse_resource(rb, 'PS4')
            row['semantic_role'] = pr.get('semantic_role')
            row['pair'] = [
                norm((pr.get('unk10') or {}).get('class_hash', 'FFFFFFFF')),
                norm((pr.get('unk18') or {}).get('class_hash', 'FFFFFFFF')),
            ]
            row['embedded_model'] = pr.get('embedded_model_tag_hash')
        out.append(row)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--entity', action='append', default=[])
    ap.add_argument('--seed', type=Path)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--parser-root', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    entities = [norm(x) for x in a.entity]
    if a.seed:
        seed = json.loads(a.seed.read_text())
        entities.extend(norm(x) for x in seed.get('entity_hashes', []))
    entities = list(dict.fromkeys(entities))
    if not entities:
        raise SystemExit('no entities supplied')

    cats = load_catalogs(a.member_catalog)
    arc = SplitHttpTar(
        [f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)],
        retries=6, timeout=90,
    )
    c = RemoteCorpus(arc, cats, a.runtime)

    sys.path.insert(0, str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_animation import read_animation
    ver = Game_Version.D1_ROI

    controls_cache: dict[str, dict] = {}
    clips_cache: dict[str, dict] = {}
    rig_cache: dict[str, dict] = {}
    skeleton_cache: dict[str, dict] = {}
    rows = []
    violations = []
    frontiers = []

    def skeleton_info(h: str) -> dict:
        h = norm(h)
        if h not in skeleton_cache:
            _, b, src = exact(c, h, ENTITY_RESOURCE_CLASS)
            parsed = parse_skeleton_resource(b)
            info = parsed['skeleton_info']
            skeleton_cache[h] = {
                'resource_hash': h,
                'node_count': int(info['node_hierarchy']['count']),
                'source': src,
            }
        return skeleton_cache[h]

    def rig_info(h: str) -> dict:
        h = norm(h)
        if h not in rig_cache:
            _, b, src = exact(c, h, ENTITY_RESOURCE_CLASS)
            rig = read_runtime_rig(io.BytesIO(b), ver)
            comps = component_rows(rig.rig_components)
            rig_cache[h] = {
                'resource_hash': h,
                'control_count': len(rig.controls_relations),
                'runtime_components': comps,
                'runtime_component_signature': list(sig(comps)),
                'source': src,
            }
        return rig_cache[h]

    def control_info(h: str) -> dict:
        h = norm(h)
        if h not in controls_cache:
            m, b, src = exact(c, h, CONTROL_REF)
            dec = decode_control(b, None)
            clips = [norm(x['tag_hash']) for x in dec['animation_list']['items']]
            controls_cache[h] = {
                'tag_hash': h,
                'entry_index': int(m['index']),
                'size': int(m['file_size']),
                'source': src,
                'animation_list': dec['animation_list'],
                'state_table': dec['state_table'],
                'clip_hashes': clips,
            }
        return controls_cache[h]

    def clip_info(h: str) -> dict:
        h = norm(h)
        if h not in clips_cache:
            m, b, src = exact(c, h, CLIP_REF)
            anim = filebacked(read_animation, b, ver)
            hd = anim.animation_header
            comps = component_rows(anim.runtime_rig_components)
            clips_cache[h] = {
                'tag_hash': h,
                'entry_index': int(m['index']),
                'size': int(m['file_size']),
                'source': src,
                'frame_count': int(hd.frame_count),
                'node_count': int(hd.node_count),
                'rig_control_count': int(hd.rig_control_count),
                'runtime_components': comps,
                'runtime_component_signature': list(sig(comps)),
            }
        return clips_cache[h]

    for entity in entities:
        row = {'entity': entity, 'violations': [], 'frontiers': []}
        try:
            resources = entity_resources(c, entity)
            row['resources'] = resources
            sks = [r['resource_hash'] for r in resources if r.get('semantic_role') == 'entity_skeleton']
            rigs = [r['resource_hash'] for r in resources if tuple(r.get('pair') or []) == RUNTIME_RIG_PAIR]
            owners = []
            for r in resources:
                p = tuple(r.get('pair') or [])
                if p in OWNER_EDGES:
                    off = OWNER_EDGES[p]
                    _, ob, osrc = exact(c, r['resource_hash'], ENTITY_RESOURCE_CLASS)
                    control = f'{u32(ob, off):08X}'
                    cm = c.entry_meta(control)
                    exact_control = cm is not None and norm(cm.get('reference')) == CONTROL_REF
                    owners.append({
                        'resource_hash': r['resource_hash'], 'pair': list(p),
                        'edge_offset': off, 'edge_offset_hex': f'0x{off:X}',
                        'observed_control': control,
                        'control_reference': None if cm is None else norm(cm.get('reference')),
                        'exact_control_class': exact_control, 'source': osrc,
                    })
            row['skeleton_resources'] = sks
            row['runtime_rig_resources'] = rigs
            row['animation_owner_edges'] = owners
            if len(sks) != 1:
                row['frontiers'].append(f'expected one source skeleton, got {sks}')
            if len(rigs) != 1:
                row['frontiers'].append(f'expected one runtime rig pair {RUNTIME_RIG_PAIR}, got {rigs}')
            if len(owners) != 2:
                row['frontiers'].append(f'expected two calibrated animation owner resources, got {len(owners)}')
            bad_owner = [x for x in owners if not x['exact_control_class']]
            if bad_owner:
                row['violations'].append(f'owner edge(s) do not resolve to {CONTROL_REF}: {bad_owner}')
            controls = sorted({x['observed_control'] for x in owners if x['exact_control_class']})
            row['control_hashes'] = controls
            row['owner_pair_controls_agree'] = len(controls) == 1 and len(owners) == 2
            if len(controls) > 1:
                row['frontiers'].append(f'animation owner resources select multiple controls {controls}; preserving all')

            sk = skeleton_info(sks[0]) if len(sks) == 1 else None
            rig = rig_info(rigs[0]) if len(rigs) == 1 else None
            row['skeleton'] = sk
            row['runtime_rig'] = rig
            control_rows = []
            all_clips = set()
            for ch in controls:
                ci = control_info(ch)
                control_rows.append(ci)
                all_clips.update(ci['clip_hashes'])
            row['controls'] = control_rows
            row['clip_hashes'] = sorted(all_clips)
            comp_rows = []
            for clip_h in sorted(all_clips):
                cp = clip_info(clip_h)
                compat = {
                    'tag_hash': clip_h,
                    'frame_count': cp['frame_count'],
                    'node_count': cp['node_count'],
                    'rig_control_count': cp['rig_control_count'],
                    'skeleton_node_count': None if sk is None else sk['node_count'],
                    'runtime_rig_control_count': None if rig is None else rig['control_count'],
                    'node_count_matches_skeleton': sk is not None and cp['node_count'] == sk['node_count'],
                    'control_count_matches_runtime_rig': rig is not None and cp['rig_control_count'] == rig['control_count'],
                    'runtime_component_fingerprint_matches': rig is not None and sig(cp['runtime_components']) == sig(rig['runtime_components']),
                }
                compat['exact_family_compatible'] = all((
                    compat['node_count_matches_skeleton'],
                    compat['control_count_matches_runtime_rig'],
                    compat['runtime_component_fingerprint_matches'],
                ))
                comp_rows.append(compat)
                if sk is not None and rig is not None and not compat['exact_family_compatible']:
                    row['violations'].append(f'{clip_h}: control-selected clip is not exact skeleton/rig compatible')
            row['clips'] = comp_rows
            row['all_control_selected_clips_compatible'] = bool(comp_rows) and all(x['exact_family_compatible'] for x in comp_rows)
            row['state_option_count'] = sum(int(x['state_table']['count']) for x in control_rows)
            row['nonempty_state_option_count'] = sum(
                1 for x in control_rows for st in x['state_table']['records'] if st['selected_animations']
            )
            row['status'] = (
                'source_closed' if not row['violations'] and not row['frontiers'] and controls and row['all_control_selected_clips_compatible']
                else 'preserved_with_frontier' if not row['violations']
                else 'violation'
            )
        except Exception as ex:
            row['status'] = 'violation'
            row['violations'].append(repr(ex))
        for x in row['violations']:
            violations.append({'entity': entity, 'error': x})
        for x in row['frontiers']:
            frontiers.append({'entity': entity, 'frontier': x})
        rows.append(row)
        print('ENTITY', entity, 'STATUS', row['status'], 'SKEL', row.get('skeleton_resources'),
              'RIG', row.get('runtime_rig_resources'), 'CONTROLS', row.get('control_hashes'),
              'CLIPS', row.get('clip_hashes'), 'STATES', row.get('state_option_count'),
              'VIOL', len(row['violations']), 'FRONT', len(row['frontiers']), flush=True)

    control_to_entities = defaultdict(list)
    for r in rows:
        for ch in r.get('control_hashes', []):
            control_to_entities[ch].append(r['entity'])
    family_keys = defaultdict(list)
    for r in rows:
        sk = ((r.get('skeleton') or {}).get('resource_hash'))
        rig = ((r.get('runtime_rig') or {}).get('resource_hash'))
        controls = tuple(r.get('control_hashes') or [])
        family_keys[(sk, rig, controls)].append(r['entity'])
    families = []
    for i, ((sk, rig, controls), ents) in enumerate(sorted(family_keys.items(), key=lambda x: str(x[0])), 1):
        families.append({
            'family_id': f'ANIM_FAMILY_{i:02d}', 'skeleton': sk, 'runtime_rig': rig,
            'controls': list(controls), 'entity_count': len(ents), 'entities': sorted(ents),
        })

    status_counts = Counter(r['status'] for r in rows)
    out = {
        'schema': 'd1_remote_spawned_actor_animation_census/v1',
        'status': 'D1_TOWER_SPAWNED_ACTOR_ANIMATION_CENSUS_COMPLETE' if not violations else 'D1_TOWER_SPAWNED_ACTOR_ANIMATION_CENSUS_WITH_VIOLATIONS',
        'entity_count': len(rows),
        'source_closed_entity_count': status_counts['source_closed'],
        'preserved_with_frontier_entity_count': status_counts['preserved_with_frontier'],
        'violation_entity_count': status_counts['violation'],
        'unique_control_count': len(controls_cache),
        'unique_clip_count': len(clips_cache),
        'animation_family_count': len(families),
        'families': families,
        'control_to_entities': {k: sorted(v) for k, v in sorted(control_to_entities.items())},
        'controls': controls_cache,
        'clips': clips_cache,
        'entities': rows,
        'frontier_count': len(frontiers),
        'frontiers': frontiers,
        'violation_count': len(violations),
        'violations': violations,
        'policy': (
            'Animation owner resources are selected only by exact EntityResource class-pairs already calibrated on D1 retail. '
            'Owner->control edges are literal u32 FileHashes at the calibrated per-pair offsets. Controls and selected clips are '
            'binary decoded; clips are reopened and checked against source skeleton/runtime-rig dimensions and runtime-component '
            'fingerprints. All state/clip options are preserved. No visual, duration, naming, location or default-state guess is used.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print('STATUS', out['status'], 'ENTITIES', out['entity_count'], 'SOURCE_CLOSED', out['source_closed_entity_count'],
          'FRONTIER_ENTITIES', out['preserved_with_frontier_entity_count'], 'VIOLATION_ENTITIES', out['violation_entity_count'],
          'CONTROLS', out['unique_control_count'], 'CLIPS', out['unique_clip_count'], 'FAMILIES', out['animation_family_count'],
          'FRONTIERS', out['frontier_count'], 'VIOLATIONS', out['violation_count'])
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
