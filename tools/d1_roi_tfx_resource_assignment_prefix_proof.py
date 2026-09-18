#!/usr/bin/env python3
"""Fail-closed structural proof for D1 ROI material TFX texture assignments.

The generic TFX opcode labels historically used by this repository were inherited
from a later/community table.  Bungie's own GDC 2017 D1-era bytecode example proves
that those labels cannot be applied blindly to the retail D1 streams: the official
example has decimal 67 (0x43)=pop_output, 69 (0x45)=push_temp and
70 (0x46)=pop_temp.

Rather than invent names for 0x49/0x47, this proof extracts the repeated four-byte
prefix seen in exact ROI pixel-material streams:

    49 <texture_index> 47 <destination_code>

and proves its relationship to the independently serialized PS texture table across
both the Xur and three-NPC material checkpoints.  It promotes only the structural
resource-assignment contract needed by a decoder.  Missing serialized indices are
kept as explicit runtime/default-resource holes.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

BUNGIE_GDC_SOURCE = 'https://advances.realtimerendering.com/destiny/gdc_2017/Destiny_shader_system_GDC_2017_v.4.0.pdf'
OFFICIAL_D1_BYTECODE_IDENTITIES = {
    '0x43': 'pop_output',
    '0x45': 'push_temp',
    '0x46': 'pop_temp',
}


def norm(x) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def prefix(raw: bytes) -> tuple[list[dict], int]:
    out = []
    p = 0
    while p + 3 < len(raw) and raw[p] == 0x49 and raw[p + 2] == 0x47:
        idx = raw[p + 1]
        dst = raw[p + 3]
        out.append({
            'byte_offset': p,
            'opcode_a': '49',
            'texture_index': idx,
            'opcode_b': '47',
            'destination_code': dst,
            'expected_destination_code': 0x21 + idx,
        })
        p += 4
    return out, p


def texture_map(ps: dict) -> dict[int, str]:
    return {int(x['texture_index']): norm(x['texture']) for x in ps['textures']['items']}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--state', action='append', required=True, help='NAME=material_state.json')
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    violations = []
    rows = []
    hole_rows = []
    total_materials = 0
    total_pairs = 0
    serialized_texture_entries = 0
    covered_serialized_entries = 0
    no_prefix = []

    for spec in a.state:
        if '=' not in spec:
            raise SystemExit('--state expects NAME=PATH')
        corpus, path = spec.split('=', 1)
        d = json.loads(Path(path).read_text())
        if d.get('status') != 'D1_MATERIAL_STAGE_STATE_EXACT' or d.get('violations'):
            violations.append(f'{corpus}: state checkpoint not exact')
        mats = d.get('materials', {})
        total_materials += len(mats)
        for mh, m in sorted(mats.items()):
            if m.get('error'):
                violations.append(f'{corpus}:{mh}: material error')
                continue
            ps = m.get('ps') or {}
            raw = bytes.fromhex((ps.get('tfx_bytecode') or {}).get('bytes_hex', ''))
            pairs, used = prefix(raw)
            tex = texture_map(ps)
            serialized_texture_entries += len(tex)
            if not pairs:
                no_prefix.append({'corpus': corpus, 'material': norm(mh), 'shader': norm(ps.get('shader', '0')), 'serialized_texture_indices': sorted(tex)})
                if tex:
                    violations.append(f'{corpus}:{mh}: serialized PS textures but no 49/47 assignment prefix')
                continue
            total_pairs += len(pairs)
            bound = {x['texture_index'] for x in pairs}
            bad_dst = [x for x in pairs if x['destination_code'] != x['expected_destination_code']]
            if bad_dst:
                violations.append(f'{corpus}:{mh}: destination-code rule violated')
            missing_bind = sorted(set(tex) - bound)
            if missing_bind:
                violations.append(f'{corpus}:{mh}: serialized texture indices absent from prefix {missing_bind}')
            covered_serialized_entries += len(set(tex) & bound)
            holes = sorted(bound - set(tex))
            for idx in holes:
                hole_rows.append({
                    'corpus': corpus,
                    'material': norm(mh),
                    'pixel_shader': norm(ps.get('shader', '0')),
                    'texture_index': idx,
                    'destination_code': 0x21 + idx,
                })
            rows.append({
                'corpus': corpus,
                'material': norm(mh),
                'pixel_shader': norm(ps.get('shader', '0')),
                'tfx_bytes_hex': raw.hex().upper(),
                'assignment_prefix_bytes': used,
                'assignment_count': len(pairs),
                'assignments': pairs,
                'serialized_textures': {str(k): v for k, v in sorted(tex.items())},
                'runtime_default_hole_indices': holes,
                'tail_hex': raw[used:].hex().upper(),
            })

    # These are the only holes in the two exact current checkpoints.  Xur and the
    # three-NPC state overlap on 80876688/808768BB, so those appear once per corpus.
    got_holes = sorted((x['corpus'], x['material'], x['pixel_shader'], x['texture_index']) for x in hole_rows)
    expected_holes = sorted([
        ('xur', '80876688', '808768C0', 2),
        ('xur', '808768BB', '808768C0', 2),
        ('three_npc', '80876688', '808768C0', 2),
        ('three_npc', '808768BB', '808768C0', 2),
        ('three_npc', '808766B2', '8087670E', 4),
        ('three_npc', '808766B6', '8087670E', 4),
    ])
    if got_holes != expected_holes:
        violations.append(f'runtime/default hole set changed: {got_holes!r}')

    shader_holes = collections.Counter(f"{x['pixel_shader']}:t{x['texture_index']}" for x in hole_rows)
    assign_hist = collections.Counter(str(x['assignment_count']) for x in rows)
    dst_hist = collections.Counter(f"0x{x['destination_code']:02X}" for r in rows for x in r['assignments'])

    out = {
        'schema_version': 1,
        'status': 'D1_ROI_TFX_RESOURCE_ASSIGNMENT_PREFIX_EXACT' if not violations else 'D1_ROI_TFX_RESOURCE_ASSIGNMENT_PREFIX_PARTIAL',
        'bungie_gdc_source': BUNGIE_GDC_SOURCE,
        'official_d1_bytecode_identities': OFFICIAL_D1_BYTECODE_IDENTITIES,
        'critical_correction': 'The later/community generic TFX opcode labels cannot be used as D1 retail semantics in this region. D1 resource binding is therefore decoded here from exact retail structural correlation, while 0x49/0x47 low-level stack names remain withheld.',
        'material_count': total_materials,
        'material_ps_streams_with_assignment_prefix': len(rows),
        'assignment_pair_count': total_pairs,
        'serialized_ps_texture_entry_count': serialized_texture_entries,
        'serialized_ps_texture_entries_covered_by_prefix': covered_serialized_entries,
        'all_serialized_ps_texture_entries_covered': serialized_texture_entries == covered_serialized_entries,
        'destination_rule': 'for every observed prefix pair: destination_code == 0x21 + texture_index',
        'assignment_count_histogram': dict(sorted(assign_hist.items(), key=lambda x: int(x[0]))),
        'destination_code_histogram': dict(sorted(dst_hist.items())),
        'runtime_default_hole_count': len(hole_rows),
        'runtime_default_holes': hole_rows,
        'runtime_default_hole_shader_slot_histogram': dict(sorted(shader_holes.items())),
        'streams_without_assignment_prefix': no_prefix,
        'rows': rows,
        'violations': violations,
        'gates': {
            'd1_generic_opcode_table_correction_closed': True,
            'roi_ps_texture_assignment_prefix_structure_closed': not violations,
            'all_serialized_texture_entries_correlated': serialized_texture_entries == covered_serialized_entries,
            'runtime_default_holes_isolated': got_holes == expected_holes,
            'runtime_default_resource_values_closed': False,
        },
        'policy': 'The 49/index/47/destination sequence is promoted as a D1 ROI PS resource-assignment structure because it exactly covers independently serialized texture indices across both pinned retail corpora with zero destination-rule violations. The two missing-slot families remain runtime/default-resource holes; no fallback texture is guessed.',
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'],
        'material_count': total_materials,
        'streams': len(rows),
        'assignment_pairs': total_pairs,
        'serialized_texture_entries': serialized_texture_entries,
        'covered': covered_serialized_entries,
        'runtime_default_holes': hole_rows,
        'violations': violations,
    }, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
