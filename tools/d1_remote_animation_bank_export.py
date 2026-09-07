#!/usr/bin/env python3
"""Losslessly export every retail D1 animation-list bank clip plus decode metadata.

Input is the source-closed activity animation-options report. Unlike the GLB action
appenders, this tool intentionally includes selector-unused animation-list entries.
Every exact s_animation_clip payload is written verbatim, SHA-256 pinned, parsed by
the pinned D1 ROI parser, and passed through decode_animation. No gameplay state or
semantic ownership is invented for clips that are present in a bank but not selected.

An exact source-closed animation population may contain zero animation-list bank
clips. That is represented as a complete empty export, not as an error and never by
fabricating a placeholder clip.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_animation_retarget_probe import component_rows
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_model_tgxm_signature_match import LazyExactHashResolver
from d1_split_tar_extract import SplitHttpTar

ANIMATION_CLIP_CLASS = '808005A1'


def norm(v: str) -> str:
    return str(v).upper().removeprefix('0X').zfill(8)


def read_animation_filebacked(read_animation, payload: bytes, version):
    with tempfile.NamedTemporaryFile() as f:
        f.write(payload); f.flush(); f.seek(0)
        return read_animation(f, version)


def write_empty(a, src: dict, selected: set[str]) -> int:
    a.out_dir.mkdir(parents=True, exist_ok=True)
    out = {
        'schema': 'd1_remote_animation_bank_export/v1',
        'status': 'D1_REMOTE_ANIMATION_BANK_EXPORT_COMPLETE',
        'source_closed_empty_bank': True,
        'animation_list_unique_clip_count': 0,
        'selector_selected_unique_clip_count': len(selected),
        'animation_list_only_unique_clip_count': 0,
        'exported_raw_clip_count': 0,
        'parsed_clip_count': 0,
        'decoded_clip_count': 0,
        'clips': [],
        'violations': [],
        'policy': (
            'The source-closed animation options serialize zero unique animation-list bank clips. The exact export is '
            'therefore empty. No placeholder clip, default state, or inferred animation is created.'
        ),
    }
    if selected:
        raise ValueError(f'zero animation-list bank but selector-selected clips exist: {sorted(selected)}')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('clips','violations')}, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--animation-options', type=Path, required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--parser-root', type=Path, required=True)
    ap.add_argument('--out-dir', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    src = json.loads(a.animation_options.read_text())
    if src.get('status') != 'D1_ACTIVITY_ACTOR_ANIMATION_OPTIONS_COMPLETE':
        raise SystemExit(f'animation options not complete: {src.get("status")}')
    bank = [norm(x) for x in src.get('unique_animation_list_clip_hashes', [])]
    selected = {norm(x) for x in src.get('unique_selector_selected_clip_hashes', [])}
    clips = list(dict.fromkeys(bank))
    if not clips:
        return write_empty(a, src, selected)

    cats = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    resolver = LazyExactHashResolver(arc, cats, a.runtime)

    sys.path.insert(0, str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_animation import read_animation
    from animation_decoding.decode_animation import decode_animation
    ver = Game_Version.D1_ROI

    raw_dir = a.out_dir / 'raw_clips'
    raw_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    violations = []
    for i, h in enumerate(clips, 1):
        try:
            _view, e, b = resolver.bytes(h)
            ref = norm(e.get('reference', ''))
            if ref != ANIMATION_CLIP_CLASS:
                raise ValueError(f'class {ref} != {ANIMATION_CLIP_CLASS}')
            fn = raw_dir / f'{h}.s_animation_clip.bin'
            fn.write_bytes(b)
            sha = hashlib.sha256(b).hexdigest()
            anim = read_animation_filebacked(read_animation, b, ver)
            hdr = anim.animation_header
            comps = component_rows(anim.runtime_rig_components)
            decoded = decode_animation(anim)
            row = {
                'tag_hash': h,
                'selector_selected': h in selected,
                'animation_list_only': h not in selected,
                'entry_index': int(e['index']),
                'package_id': f"{int(e.get('package_id', 0)):04X}" if e.get('package_id') is not None else None,
                'reference': ref,
                'bytes': len(b),
                'sha256': sha,
                'raw_file': str(fn),
                'frame_count': int(hdr.frame_count),
                'node_count': int(hdr.node_count),
                'rig_control_count': int(hdr.rig_control_count),
                'runtime_rig_components': comps,
                'decoded_track_count': len(decoded),
                'parse_success': True,
                'decode_success': True,
            }
            rows.append(row)
            print('CLIP', i, '/', len(clips), h, 'FRAMES', row['frame_count'], 'TRACKS', row['decoded_track_count'], 'SELECTED', row['selector_selected'], flush=True)
        except Exception as ex:
            violations.append({'tag_hash': h, 'error': repr(ex)})
            print('ERROR', h, repr(ex), flush=True)

    out = {
        'schema': 'd1_remote_animation_bank_export/v1',
        'status': 'D1_REMOTE_ANIMATION_BANK_EXPORT_COMPLETE' if len(rows) == len(clips) and not violations else 'D1_REMOTE_ANIMATION_BANK_EXPORT_INCOMPLETE',
        'source_closed_empty_bank': False,
        'animation_list_unique_clip_count': len(clips),
        'selector_selected_unique_clip_count': len(selected),
        'animation_list_only_unique_clip_count': len(set(clips) - selected),
        'exported_raw_clip_count': len(rows),
        'parsed_clip_count': sum(bool(x.get('parse_success')) for x in rows),
        'decoded_clip_count': sum(bool(x.get('decode_success')) for x in rows),
        'clips': rows,
        'violations': violations,
        'policy': (
            'Every unique FileHash serialized in a source-closed animation-list bank is retained, including clips not '
            'selected by any decoded control state. Raw files are exact retail payloads; parser/decode success does not '
            'promote an unused bank clip to a gameplay state or actor identity. A source-closed zero-bank population is '
            'represented by a complete empty export rather than a fabricated clip.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('clips','violations')}, indent=2))
    if violations or len(rows) != len(clips):
        for v in violations[:50]: print('VIOLATION', v)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
