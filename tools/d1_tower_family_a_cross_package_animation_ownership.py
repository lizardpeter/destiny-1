#!/usr/bin/env python3
"""Close or bound Tower Family A animation ownership across 023D + 01E3.

Family A is intentionally cross-package. Its source SEntity and high owner half are
in Tower Activity 023D, while its low owner half, 4-node skeleton, and 4-control
runtime rig are in Globals Cinematic 01E3. This probe preserves that split exactly.
It never substitutes a same-shaped local resource.

Closure requires:
  * exact 023D SEntity membership and source-owned WorldID;
  * exact owner class pairs in their proven packages;
  * literal owner FileHash slots converging on one 80802C0E control;
  * exact control/state decoding from whichever staged source family owns it;
  * every selected clip resolving uniquely in the 023D+01E3 corpus and matching
    the exact 4-node skeleton, 4-control runtime rig, and component fingerprint.

Multiple selected states remain separate actions. No default/startup state, semantic
state name, loop behavior, synchronization, or actor role is inferred.
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


class Corpus:
    def __init__(self, readers: dict[str, EntryReader]):
        self.readers = readers
        self.maps = {k: entry_map(v) for k, v in readers.items()}

    def exact(self, package: str, tag: str, expected_ref: str | None = None):
        package = package.upper()
        if package not in self.readers:
            raise ValueError(f'unknown corpus package {package}')
        r = self.readers[package]
        e, b = exact_payload(r, self.maps[package], tag, expected_ref)
        return package, r, e, b

    def locate(self, tag: str, expected_ref: str | None = None):
        tag = norm(tag)
        out = []
        for package, r in self.readers.items():
            e = self.maps[package].get(tag)
            if e is None:
                continue
            if expected_ref is not None and norm(e['reference']) != norm(expected_ref):
                continue
            out.append({
                'package': package,
                'reader': r,
                'entry': e,
                'available': bool(r.available(e['index'])),
            })
        return out

    def unique(self, tag: str, expected_ref: str | None = None):
        locs = self.locate(tag, expected_ref)
        avail = [x for x in locs if x['available']]
        if len(avail) != 1:
            desc = [(x['package'], int(x['entry']['index']), norm(x['entry']['reference']), x['available']) for x in locs]
            raise ValueError(f'{norm(tag)}: expected one available corpus owner, got {desc}')
        x = avail[0]
        r = x['reader']; e = x['entry']
        return x['package'], r, e, r.entry(e['index'])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--activity-pkg', type=Path, required=True,
                    help='023D_5 with all logical 023D siblings staged beside it')
    ap.add_argument('--cinematic-pkg', type=Path, required=True,
                    help='01E3_2 with all logical 01E3 siblings staged beside it')
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--parser-root', type=Path, required=True)
    ap.add_argument('--spec', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    specs = json.loads(a.spec.read_text())
    spec = specs.get('families', {}).get('A')
    if spec is None:
        raise ValueError('Family A absent from spec')

    model = norm(spec['entity_model'])
    skeleton_tag = norm(spec['skeleton_resource'])
    rig_tag = norm(spec['runtime_rig_resource'])
    expected_nodes = int(spec['expected_node_count'])
    expected_controls = int(spec['expected_control_count'])
    entities_spec = {norm(k): [str(x).upper() for x in v] for k, v in spec['entities'].items()}
    owner_specs = {
        'low': {
            'package': '01E3',
            'resource_hash': norm(spec['owner_halves']['low']['resource_hash']),
            'class_pair': tuple(norm(x) for x in spec['owner_halves']['low']['class_pair']),
            'control_filehash_offset': int(spec['owner_halves']['low']['control_filehash_offset']),
        },
        'high': {
            'package': '023D',
            'resource_hash': norm(spec['owner_halves']['high']['resource_hash']),
            'class_pair': tuple(norm(x) for x in spec['owner_halves']['high']['class_pair']),
            'control_filehash_offset': int(spec['owner_halves']['high']['control_filehash_offset']),
        },
    }

    readers = {
        '023D': EntryReader(a.activity_pkg, a.runtime),
        '01E3': EntryReader(a.cinematic_pkg, a.runtime),
    }
    corpus = Corpus(readers)
    violations: list[str] = []

    # Re-prove the source SEntity in 023D and preserve its cross-package resource hashes.
    entity_rows = {}
    all_world_ids = []
    expected_shared = {skeleton_tag, rig_tag, *(x['resource_hash'] for x in owner_specs.values())}
    for entity, world_ids in entities_spec.items():
        _, r, e, b = corpus.exact('023D', entity, '80800734')
        resources = dyn_resources(b)
        missing = sorted(expected_shared - set(resources))
        if missing:
            violations.append(f'{entity}: missing required Family-A resources {missing}')
        all_world_ids.extend(world_ids)
        entity_rows[entity] = {
            'package': '023D', 'entry_index': int(e['index']), 'size': int(e['file_size']),
            'resource_count': len(resources), 'resource_hashes': resources,
            'runtime_placement_count': len(world_ids), 'world_ids': world_ids,
            'required_resources_present': not missing,
        }
    if len(set(all_world_ids)) != len(all_world_ids):
        violations.append('duplicate runtime WorldID in Family-A spec')

    # Validate both source-owned halves in their proven physical/logical families.
    owner_rows = {}
    observed_controls = []
    for half_name, cfg in owner_specs.items():
        package, r, e, b = corpus.exact(cfg['package'], cfg['resource_hash'], ENTITY_RESOURCE_REF)
        parsed = parse_resource(b, r.h['platform'])
        observed_pair = (
            norm((parsed.get('unk10') or {}).get('class_hash', '0')),
            norm((parsed.get('unk18') or {}).get('class_hash', '0')),
        )
        if observed_pair != cfg['class_pair']:
            violations.append(f'{cfg["resource_hash"]}: class pair {observed_pair} != {cfg["class_pair"]}')
        off = cfg['control_filehash_offset']
        if off + 4 > len(b):
            observed = None
            violations.append(f'{cfg["resource_hash"]}: FileHash slot 0x{off:X} OOB')
        else:
            observed = f'{u32(b, off):08X}'
            observed_controls.append(observed)
        owner_rows[half_name] = {
            'package': package, 'resource_hash': cfg['resource_hash'],
            'entry_index': int(e['index']), 'size': int(e['file_size']),
            'expected_class_pair': list(cfg['class_pair']), 'observed_class_pair': list(observed_pair),
            'control_filehash_offset': off, 'observed_control': observed,
            'class_pair_exact': observed_pair == cfg['class_pair'],
        }

    controls = sorted(set(x for x in observed_controls if x is not None))
    control_tag = controls[0] if len(controls) == 1 else None
    if len(controls) != 1:
        violations.append(f'Family-A owner halves do not converge on one control: {controls}')

    control_row = None
    animation_list_unique: list[str] = []
    selected_unique: list[str] = []
    if control_tag:
        try:
            package, r, ce, cb = corpus.unique(control_tag, CONTROL_REF)
            decoded = decode_control(cb, None)
            animation_list_unique = sorted({norm(x['tag_hash']) for x in decoded['animation_list']['items']})
            selected_unique = sorted({
                norm(x['tag_hash'])
                for state in decoded['state_table']['records']
                for x in state['selected_animations']
            })
            control_row = {
                'tag_hash': control_tag, 'package': package,
                'entry_index': int(ce['index']), 'size': int(ce['file_size']),
                **decoded,
                'unique_animation_list_hashes': animation_list_unique,
                'unique_selected_clip_hashes': selected_unique,
            }
        except Exception as ex:
            violations.append(f'{control_tag}: cross-package control decode failed: {ex!r}')

    # Parse exact 01E3 skeleton/rig and test every listed clip across the corpus.
    sys.path.insert(0, str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_animation import read_animation
    ver = Game_Version.D1_ROI

    _, _, se, sb = corpus.exact('01E3', skeleton_tag, ENTITY_RESOURCE_REF)
    sk = read_skeleton(io.BytesIO(sb), ver)
    _, _, re, rb = corpus.exact('01E3', rig_tag, ENTITY_RESOURCE_REF)
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
        locs = corpus.locate(clip, CLIP_REF)
        row['corpus_locations'] = [
            {'package': x['package'], 'entry_index': int(x['entry']['index']), 'available': x['available']}
            for x in locs
        ]
        try:
            package, r, e, payload = corpus.unique(clip, CLIP_REF)
            anim = filebacked(read_animation, payload, ver)
            h = anim.animation_header
            comps = component_rows(anim.runtime_rig_components)
            row.update(
                package=package, entry_index=int(e['index']), reference=norm(e['reference']), size=int(e['file_size']),
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
                violations.append(f'{clip}: selected clip not exact Family-A compatible')
        except Exception as ex:
            row.update(status='corpus_resolution_or_parse_failed', error=repr(ex), exact_family_compatible=False)
            if clip in selected_unique:
                violations.append(f'{clip}: selected clip failed cross-package resolution/parse: {ex!r}')
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
        'status': 'D1_TOWER_FAMILY_A_CROSS_PACKAGE_ANIMATION_OWNER_CONTROL_CLOSED' if closed else 'D1_TOWER_FAMILY_A_CROSS_PACKAGE_ANIMATION_OWNER_CONTROL_PARTIAL',
        'family_id': 'A',
        'corpus': {
            '023D': str(a.activity_pkg), '01E3': str(a.cinematic_pkg),
            'policy': 'Resources are resolved only from exact staged 023D and 01E3 logical families; ambiguous duplicate ownership fails closed.'
        },
        'family': {
            'entity_model': model,
            'skeleton_resource': skeleton_tag, 'skeleton_package': '01E3', 'skeleton_entry_index': int(se['index']),
            'skeleton_node_count': node_count,
            'runtime_rig_resource': rig_tag, 'runtime_rig_package': '01E3', 'runtime_rig_entry_index': int(re['index']),
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
        'policy': 'Closure requires exact cross-package SEntity membership, exact owner classes and literal FileHash slots, one uniquely resolved control, decoded selected clips, and exact selected-clip skeleton/runtime-rig compatibility. No same-shaped local substitution or default/semantic inference is permitted.',
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'], 'family': out['family'], 'owner_halves': owner_rows,
        'control': None if control_row is None else {'tag_hash': control_tag, 'package': control_row['package']},
        'animation_list': animation_list_unique, 'selected_clips': selected_unique,
        'states': [] if control_row is None else [{
            'state_hash': x['state_hash'], 'state_name': x.get('state_name'),
            'scalar_f32': x['scalar_f32'],
            'selected': [y['tag_hash'] for y in x['selected_animations']],
        } for x in control_row['state_table']['records']],
        'clip_summary': {k: {
            'package': v.get('package'), 'frame_count': v.get('frame_count'),
            'node_count': v.get('node_count'), 'rig_control_count': v.get('rig_control_count'),
            'selected': v.get('selected_by_any_state'),
            'exact_family_compatible': v.get('exact_family_compatible'), 'status': v.get('status'),
        } for k, v in clip_rows.items()},
        'violations': violations,
    }, indent=2))
    return 0 if closed else 2


if __name__ == '__main__':
    raise SystemExit(main())
