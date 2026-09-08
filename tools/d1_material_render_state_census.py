#!/usr/bin/env python3
"""Resolve exact D1 render state for a selected material population.

The selector is destination-agnostic JSON with a top-level ``materials`` object
or list of material TagHashes.  Source payloads are read from recovered retail
package snapshots.  Output is intended to be consumed by Blender/glTF adapters
and by future Rust renderer import code.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_tower_map_schema_validate_v5 as v5
from d1_material_render_state import MATERIAL_CLASS, decode_material_render_state, norm_hash


def selector_materials(src: dict) -> list[str]:
    m = src.get('materials') or {}
    if isinstance(m, dict):
        vals = m.keys()
    elif isinstance(m, list):
        vals = m
    else:
        raise ValueError('selector materials must be object or list')
    return sorted({norm_hash(x) for x in vals})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--visual-json', type=Path, required=True)
    ap.add_argument('-o', '--out', type=Path, required=True)
    a = ap.parse_args()

    selected = selector_materials(json.loads(a.visual_json.read_text()))
    if not selected:
        raise SystemExit('selector contains no material hashes')

    corpus = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    rows = []
    violations = []
    raw_counts = Counter()
    low_counts = Counter()
    ps_by_class = defaultdict(Counter)

    for h in selected:
        meta = corpus.entry_meta(h)
        payload, source = corpus.payload(h)
        if meta is None or payload is None:
            violations.append(f'{h}: material payload unavailable')
            continue
        ref = norm_hash(meta.get('reference', ''))
        if ref != MATERIAL_CLASS:
            violations.append(f'{h}: class {ref} != {MATERIAL_CLASS}')
            continue
        try:
            state = decode_material_render_state(payload)
        except Exception as ex:
            violations.append(f'{h}: render-state decode failed: {ex!r}')
            continue
        state.update({'material': h, 'source': source, 'resource_class': ref})
        rows.append(state)
        raw_counts[state['unk20_hex']] += 1
        low_counts[state['unk20_low_hex']] += 1
        cls = 'transparent' if state['transparent_draw_population'] else 'opaque'
        ps_by_class[cls][state['pixel_shader']] += 1

    if len(rows) != len(selected):
        violations.append(f'resolved {len(rows)} of {len(selected)} selected materials')

    out = {
        'schema_version': 1,
        'status': 'D1_MATERIAL_RENDER_STATE_CENSUS_COMPLETE' if not violations else 'D1_MATERIAL_RENDER_STATE_CENSUS_PARTIAL',
        'selected_material_count': len(selected),
        'resolved_material_count': len(rows),
        'transparent_material_count': sum(x['transparent_draw_population'] for x in rows),
        'opaque_material_count': sum(not x['transparent_draw_population'] for x in rows),
        'known_0x88_blend_material_count': sum(x['exact_blend_state_known'] for x in rows),
        'unk20_raw_counts': dict(sorted(raw_counts.items())),
        'unk20_low_byte_counts': dict(sorted(low_counts.items())),
        'transparent_pixel_shader_counts': dict(sorted(ps_by_class['transparent'].items())),
        'opaque_pixel_shader_counts': dict(sorted(ps_by_class['opaque'].items())),
        'materials': rows,
        'violations': violations,
        'decoder_contract': {
            'material_class': MATERIAL_CLASS,
            'source_payload_is_authoritative': True,
            'destination_neutral': True,
            'unknown_nonzero_blend_equations_are_not_guessed': True,
        },
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in (
        'status', 'selected_material_count', 'resolved_material_count',
        'transparent_material_count', 'opaque_material_count',
        'known_0x88_blend_material_count', 'unk20_raw_counts', 'violations')}, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
