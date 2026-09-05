#!/usr/bin/env python3
"""Census every D1 s_animation_clip in a package against one concrete rig/skeleton.

This is a discovery companion to d1_animation_retarget_probe.py.  It parses all
resident clips, compares their ordered runtime-rig component fingerprints to the
supplied retail runtime rig, records the parser-native control limit, and can
fully decode/retarget a bounded number of exact full-control matches.

Compatibility is evidence about a runtime animation family only; it is not by
itself a gameplay-owner or player/enemy identity claim.
"""
from __future__ import annotations

import argparse
import collections
import io
import json
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entry_extract import EntryReader
from d1_animation_retarget_probe import component_rows, common_component_prefix

ANIMATION_CLIP_CLASS = '808005A1'


def get_entry(reader: EntryReader, tag: str):
    wanted = tag.upper().removeprefix('0X')
    for e in reader.entries:
        if e['tag_hash'].upper() == wanted:
            if not reader.available(e['index']):
                raise RuntimeError(f'{wanted} is not readable in {reader.pkg}')
            return e, reader.entry(e['index'])
    raise KeyError(wanted)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('pkg', type=Path)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--parser-root', type=Path, required=True)
    ap.add_argument('--skeleton', required=True)
    ap.add_argument('--rig', required=True)
    ap.add_argument('--retarget-limit', type=int, default=20)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    parser_root = a.parser_root.resolve()
    sys.path.insert(0, str(parser_root))
    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_animation import read_animation
    from animation_decoding.decode_animation import decode_animation
    from runtime_rig.rig_retarget import rig_retarget, calc_control_limit
    from animation_export.convert_animation_object_to_local import convert_obj_to_local

    r = EntryReader(a.pkg, a.runtime)
    ver = Game_Version.D1_ROI
    ske, skb = get_entry(r, a.skeleton)
    rie, rib = get_entry(r, a.rig)
    skeleton = read_skeleton(io.BytesIO(skb), ver)
    rig = read_runtime_rig(io.BytesIO(rib), ver)
    target_components = component_rows(rig.rig_components)
    target_controls = len(rig.controls_relations)
    target_nodes = len(skeleton.node_defs)

    rows = []
    signature_counts = collections.Counter()
    exact_matches = []
    parse_errors = []
    retargeted = 0

    for e in r.entries:
        if e['reference'].upper() != ANIMATION_CLIP_CLASS:
            continue
        row = {
            'tag_hash': e['tag_hash'].upper(), 'entry_index': e['index'],
            'size': e['file_size'], 'available': r.available(e['index']),
        }
        if not row['available']:
            rows.append(row)
            continue
        try:
            anim = read_animation(io.BytesIO(r.entry(e['index'])), ver)
            h = anim.animation_header
            comps = component_rows(anim.runtime_rig_components)
            sig = tuple((x['hash'], int(x['count'])) for x in comps)
            signature_counts[sig] += 1
            prefix = common_component_prefix(target_components, comps)
            native_limit = int(calc_control_limit(rig, anim.runtime_rig_components))
            exact = comps == target_components
            full = native_limit == target_controls
            row.update({
                'frame_count': int(h.frame_count),
                'node_count': int(h.node_count),
                'rig_control_count': int(h.rig_control_count),
                'runtime_rig_components': comps,
                'component_prefix': prefix,
                'native_control_limit': native_limit,
                'exact_component_match': exact,
                'full_target_control_coverage': full,
                'node_count_matches_skeleton': int(h.node_count) == target_nodes,
                'control_count_matches_rig': int(h.rig_control_count) == target_controls,
                'parse_success': True,
            })
            if exact and full:
                exact_matches.append(row['tag_hash'])
                if retargeted < max(0, a.retarget_limit):
                    try:
                        decoded = decode_animation(anim)
                        ret = rig_retarget(anim, decoded, skeleton, rig)
                        local = convert_obj_to_local(anim, ret, skeleton)
                        row.update({
                            'retarget_attempted': True,
                            'retarget_success': True,
                            'decoded_track_count': len(decoded),
                            'retargeted_track_count': len(ret),
                            'local_track_count': len(local),
                        })
                    except Exception as ex:
                        row.update({
                            'retarget_attempted': True,
                            'retarget_success': False,
                            'retarget_error': repr(ex),
                            'retarget_trace_tail': traceback.format_exc().splitlines()[-8:],
                        })
                    retargeted += 1
        except Exception as ex:
            row.update({'parse_success': False, 'parse_error': repr(ex)})
            parse_errors.append({'tag_hash': row['tag_hash'], 'error': repr(ex)})
        rows.append(row)

    sig_rows = [
        {'components': [{'hash': h, 'count': n} for h, n in sig], 'clip_count': count}
        for sig, count in signature_counts.most_common()
    ]
    exact_rows = [x for x in rows if x.get('exact_component_match') and x.get('full_target_control_coverage')]
    report = {
        'schema': 'd1_animation_rig_clip_census/v1',
        'package': str(r.pkg),
        'package_id': f"{int(r.h['pkg_id']):04X}",
        'target': {
            'skeleton': a.skeleton.upper(),
            'skeleton_node_count': target_nodes,
            'runtime_rig': a.rig.upper(),
            'runtime_rig_control_count': target_controls,
            'runtime_rig_components': target_components,
            'skeleton_entry_index': ske['index'],
            'rig_entry_index': rie['index'],
        },
        'summary': {
            'animation_clip_entries': sum(1 for e in r.entries if e['reference'].upper() == ANIMATION_CLIP_CLASS),
            'resident_clip_count': sum(bool(x.get('available')) for x in rows),
            'parsed_clip_count': sum(bool(x.get('parse_success')) for x in rows),
            'parse_error_count': len(parse_errors),
            'unique_runtime_component_signatures': len(signature_counts),
            'exact_full_control_match_count': len(exact_rows),
            'node_and_control_count_match_count': sum(bool(x.get('node_count_matches_skeleton') and x.get('control_count_matches_rig')) for x in rows),
            'retarget_attempt_count': sum(bool(x.get('retarget_attempted')) for x in rows),
            'retarget_success_count': sum(bool(x.get('retarget_success')) for x in rows),
        },
        'exact_full_control_matches': [
            {k: x.get(k) for k in ('tag_hash','entry_index','frame_count','node_count','rig_control_count','native_control_limit','retarget_attempted','retarget_success','decoded_track_count','retargeted_track_count','local_track_count')}
            for x in exact_rows
        ],
        'runtime_component_signatures': sig_rows,
        'clips': rows,
        'parse_errors': parse_errors,
        'policy': 'Exact component/full-control compatibility plus successful retarget proves runtime animation compatibility only; semantic ownership requires a separate serialized owner/assembly edge.',
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'target': report['target'], 'summary': report['summary'], 'first_exact_matches': report['exact_full_control_matches'][:20]}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
