#!/usr/bin/env python3
"""Prove D1 animation-control compatibility by executing the native retarget path remotely.

A source-owned SEntity may reference an animation control whose clips do not have the
same node/control dimensions as the target skeleton/runtime rig.  D1's runtime-rig
component architecture deliberately supports this: tiger-animation-parser computes a
common control prefix and retargets the decoded clip into the target rig.

This tool therefore tests compatibility by the production decode/retarget/localize
sequence, not by requiring exact clip/target dimensions:

    read_animation -> decode_animation -> calc_control_limit -> rig_retarget
                   -> convert_obj_to_local

The caller supplies exact TARGET:SKELETON:RIG:CONTROL tuples.  Every selector-selected
808005A1 clip from each exact 80802C0E control is fetched through the verified universal
retail package catalog and executed against that concrete target.  A target is closed
only when every selected clip succeeds.  Semantic state names/default states are not
inferred.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import tempfile
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_animation_control_state_map import decode_control
from d1_animation_retarget_probe import component_rows, common_component_prefix
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar

ENTITY_RESOURCE = '80800861'
CONTROL = '80802C0E'
CLIP = '808005A1'


def norm(x):
    return str(x).upper().removeprefix('0X').zfill(8)


def exact_payload(c, h, ref=None):
    h = norm(h)
    m = c.entry_meta(h)
    b, src = c.payload(h)
    if m is None or b is None:
        raise ValueError(f'{h}: payload unavailable')
    got = norm(m.get('reference', 'FFFFFFFF'))
    if ref is not None and got != norm(ref):
        raise ValueError(f'{h}: reference {got} != {norm(ref)}')
    return m, b, src


def read_animation_filebacked(read_animation, payload, version):
    with tempfile.NamedTemporaryFile() as f:
        f.write(payload); f.flush(); f.seek(0)
        return read_animation(f, version)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--parser-root', type=Path, required=True)
    ap.add_argument('--target', action='append', required=True,
                    help='ID:SKELETON:RIG:CONTROL')
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    cats = load_catalogs(a.member_catalog)
    arc = SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    c = RemoteCorpus(arc, cats, a.runtime)

    sys.path.insert(0, str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_animation import read_animation
    from animation_decoding.decode_animation import decode_animation
    from runtime_rig.rig_retarget import rig_retarget, calc_control_limit
    from animation_export.convert_animation_object_to_local import convert_obj_to_local
    ver = Game_Version.D1_ROI

    violations = []
    targets = []
    clip_cache = {}
    control_cache = {}

    for spec in a.target:
        tid, skh, rgh, cth = spec.split(':', 3)
        skh, rgh, cth = map(norm, (skh, rgh, cth))
        row = {'id': tid, 'skeleton': skh, 'runtime_rig': rgh, 'animation_control': cth}
        try:
            _, skb, sksrc = exact_payload(c, skh, ENTITY_RESOURCE)
            _, rgb, rgsrc = exact_payload(c, rgh, ENTITY_RESOURCE)
            skeleton = read_skeleton(io.BytesIO(skb), ver)
            rig = read_runtime_rig(io.BytesIO(rgb), ver)
            target_components = component_rows(rig.rig_components)
            row.update({
                'skeleton_source': sksrc,
                'runtime_rig_source': rgsrc,
                'skeleton_node_count': len(skeleton.node_defs),
                'runtime_rig_control_count': len(rig.controls_relations),
                'runtime_rig_components': target_components,
            })

            if cth not in control_cache:
                _, cb, csrc = exact_payload(c, cth, CONTROL)
                dec = decode_control(cb, None, [])
                selected = sorted({norm(a0['tag_hash']) for st in dec['state_table']['records'] for a0 in st['selected_animations']})
                control_cache[cth] = {'source': csrc, 'decoded': dec, 'selected': selected}
            cc = control_cache[cth]
            selected = cc['selected']
            row['control_source'] = cc['source']
            row['selector_record_count'] = cc['decoded']['state_table']['count']
            row['selected_clip_count'] = len(selected)

            results = []
            for n, cliph in enumerate(selected, 1):
                if cliph not in clip_cache:
                    _, bb, src = exact_payload(c, cliph, CLIP)
                    animation = read_animation_filebacked(read_animation, bb, ver)
                    clip_cache[cliph] = (animation, src)
                animation, src = clip_cache[cliph]
                hdr = animation.animation_header
                clip_components = component_rows(animation.runtime_rig_components)
                rr = {
                    'clip': cliph,
                    'source': src,
                    'frame_count': int(hdr.frame_count),
                    'source_node_count': int(hdr.node_count),
                    'source_rig_control_count': int(hdr.rig_control_count),
                    'source_runtime_rig_components': clip_components,
                    'component_prefix': common_component_prefix(target_components, clip_components),
                }
                try:
                    limit = int(calc_control_limit(rig, animation.runtime_rig_components))
                    rr['native_control_limit'] = limit
                    if limit != rr['component_prefix']['control_limit']:
                        raise RuntimeError(f'control-limit disagreement {limit} != {rr["component_prefix"]["control_limit"]}')
                    decoded = decode_animation(animation)
                    retargeted = rig_retarget(animation, decoded, skeleton, rig)
                    local = convert_obj_to_local(animation, retargeted, skeleton)
                    rr.update({
                        'decoded_track_count': len(decoded),
                        'retargeted_track_count': len(retargeted),
                        'local_track_count': len(local),
                        'success': True,
                    })
                except Exception as ex:
                    rr.update({'success': False, 'error_type': type(ex).__name__, 'error': str(ex),
                               'trace_tail': traceback.format_exc().splitlines()[-8:]})
                    violations.append(f'{tid}:{cliph}:{type(ex).__name__}:{ex}')
                results.append(rr)
                if n % 50 == 0 or n == len(selected):
                    print('TARGET', tid, n, '/', len(selected), 'success', sum(1 for x in results if x.get('success')), flush=True)

            row['clips'] = results
            row['success_count'] = sum(1 for x in results if x.get('success'))
            row['failure_count'] = len(results) - row['success_count']
            row['all_selected_clips_retarget_success'] = bool(results) and row['failure_count'] == 0
            row['native_control_limit_histogram'] = dict(__import__('collections').Counter(str(x.get('native_control_limit')) for x in results if x.get('native_control_limit') is not None))
            if not row['all_selected_clips_retarget_success']:
                violations.append(f'{tid}:target_not_closed:{row["success_count"]}/{len(results)}')
        except Exception as ex:
            row['error'] = repr(ex)
            violations.append(f'{tid}:target_setup:{ex!r}')
        targets.append(row)

    out = {
        'schema_version': 1,
        'status': 'D1_REMOTE_ANIMATION_RETARGET_MATRIX_COMPLETE' if not violations else 'D1_REMOTE_ANIMATION_RETARGET_MATRIX_PARTIAL',
        'target_count': len(targets),
        'closed_target_count': sum(1 for x in targets if x.get('all_selected_clips_retarget_success')),
        'unique_control_count': len(control_cache),
        'unique_clip_count': len(clip_cache),
        'targets': targets,
        'violations': violations,
        'remote_logical_package_count': len(c.views),
        'remote_payload_cache_count': len(c.payload_cache),
        'policy': (
            'Compatibility is established only by executing the pinned D1 decode/rig_retarget/convert-to-local path for each '
            'concrete clip/target pair. Dimension equality is not required. A successful retarget does not assign a default '
            'selector state or gameplay semantic; ownership comes from the separately source-proven animation-control edge.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print('STATUS', out['status'], 'TARGETS', len(targets), 'CLOSED', out['closed_target_count'], 'UNIQUE_CLIPS', out['unique_clip_count'])
    for x in targets:
        print(x['id'], 'nodes', x.get('skeleton_node_count'), 'controls', x.get('runtime_rig_control_count'),
              'clips', x.get('selected_clip_count'), 'success', x.get('success_count'), 'fail', x.get('failure_count'),
              'limits', x.get('native_control_limit_histogram'))
    print('VIOLATIONS', len(violations))
    for v in violations[:100]: print(v)
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
