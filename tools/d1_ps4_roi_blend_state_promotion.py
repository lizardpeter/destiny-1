#!/usr/bin/env python3
"""Promote the D1 PS4 ROI Material +0x20 lane-0 blend selector narrowly.

Inputs are independently closed artifacts:
  * exact D1 four-byte Material +0x20 windows;
  * pinned Tiger/Alkahest PipelineState lane/selector and blend table source;
  * exact 80CA0B97 card pixel-shader output dataflow;
  * exact 816CE0A8 circuitry pixel-shader alpha-zero output.

The promotion is intentionally fixture-scoped.  It proves that, for the tested
D1 ROI materials whose byte0 is 0x88, byte0 uses the Tiger PipelineState blend
selector encoding: high bit active, low seven bits index 8, whose render-target
0 equation is Source*One + Destination*InvSrcAlpha.  It does not rename the
remaining three state bytes globally.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CARDS = {'80B9E8C2': '80B9E8CF', '80B9E8C3': '80B9E8D0'}
CIRCUIT = '816CE240'
OPAQUE = '809C475F'


def load(p: Path) -> dict:
    return json.loads(p.read_text())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--state4', type=Path, required=True)
    ap.add_argument('--correlation', type=Path, required=True)
    ap.add_argument('--card-gcn', type=Path, required=True)
    ap.add_argument('--circuit-gcn', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    state = load(a.state4); corr = load(a.correlation); card = load(a.card_gcn); circ = load(a.circuit_gcn)
    violations = []
    if state.get('status') != 'D1_REMOTE_PS4_ROI_MATERIAL_STATE4_COMPLETE' or state.get('violations'):
        violations.append('state4_not_closed')
    if corr.get('status') != 'D1_PS4_ROI_STATE4_CROSS_SOURCE_CORRELATION_COMPLETE':
        violations.append('cross_source_correlation_not_closed')
    if card.get('status') != 'D1_80CA0B97_CARD_GCN_OUTPUT_DEPENDENCY_PROVEN' or card.get('violations'):
        violations.append('card_gcn_not_closed')
    if circ.get('status') != 'D1_816CE0A8_GCN_OUTPUT_ALPHA_ZERO_REPRODUCED':
        violations.append('circuit_gcn_not_closed')

    rows = {str(r['material']).upper(): r for r in state.get('rows', [])}
    expected = {OPAQUE, CIRCUIT, *CARDS.keys()}
    if set(rows) != expected:
        violations.append(f'state_material_set_drift:{sorted(rows)}')

    for h in CARDS:
        if rows.get(h, {}).get('lanes_u8') != [0x88, 0x00, 0x81, 0x00]:
            violations.append(f'{h}:state_bytes_drift:{rows.get(h,{}).get("lanes_u8")}')
    if rows.get(CIRCUIT, {}).get('lanes_u8') != [0x88, 0, 0, 0]:
        violations.append(f'{CIRCUIT}:state_bytes_drift:{rows.get(CIRCUIT,{}).get("lanes_u8")}')
    if rows.get(OPAQUE, {}).get('lanes_u8') != [0, 0, 0, 0]:
        violations.append(f'{OPAQUE}:state_bytes_drift:{rows.get(OPAQUE,{}).get("lanes_u8")}')

    lane_order = corr.get('source_pipeline_state_lane_order')
    if lane_order != ['blend_state','depth_stencil_state','rasterizer_state','depth_bias_state']:
        violations.append(f'pipeline_state_lane_order_drift:{lane_order}')
    desc8 = (corr.get('source_blend_descriptors') or {}).get('8', '')
    required_desc = ['blend_enable: BOOL(1)', 'src_blend: One', 'dest_blend: InvSrcAlpha', 'blend_op: Add',
                     'src_blend_alpha: One', 'dest_blend_alpha: InvSrcAlpha', 'blend_op_alpha: Add']
    for x in required_desc:
        if x not in desc8: violations.append(f'blend8_descriptor_missing:{x}')
    selected = corr.get('lane0_selected_indices') or {}
    for h in (*CARDS.keys(), CIRCUIT):
        if selected.get(h) != 8: violations.append(f'{h}:lane0_index_not_8:{selected.get(h)}')
    if selected.get(OPAQUE) is not None: violations.append(f'{OPAQUE}:unexpected_lane0_override:{selected.get(OPAQUE)}')

    card_rows = {x['shader']: x for x in card.get('shaders', [])}
    if set(card_rows) != set(CARDS.values()): violations.append(f'card_shader_set_drift:{sorted(card_rows)}')
    cf = card_rows.get('80B9E8CF', {})
    d0 = card_rows.get('80B9E8D0', {})
    if cf.get('output_structure', {}).get('rgb_structure') != 'PREMULTIPLIED_BY_FINAL_ALPHA_SCALAR':
        violations.append('80B9E8CF_not_premultiplied')
    if d0.get('output_structure', {}).get('rgb_structure') != 'EXPLICIT_ZERO':
        violations.append('80B9E8D0_rgb_not_zero')
    if cf.get('output_structure', {}).get('mrt0_a') != 'FINAL_ALPHA_SCALAR' or d0.get('output_structure', {}).get('mrt0_a') != 'FINAL_ALPHA_SCALAR':
        violations.append('card_alpha_contract_drift')
    if circ.get('output_alpha') != 'EXACT_ZERO_SOURCE_REPRODUCED':
        violations.append('circuit_alpha_not_zero')

    promoted = not violations
    out = {
        'schema': 'd1_ps4_roi_blend_state_promotion/v1',
        'status': 'D1_PS4_ROI_BLEND_SELECTOR_INDEX8_PROMOTED_CROSS_FIXTURE' if promoted else 'D1_PS4_ROI_BLEND_SELECTOR_PROMOTION_FAILED',
        'promotion_scope': {
            'field': 'D1 PS4 ROI Material +0x20 byte0',
            'tested_active_raw_value': '0x88',
            'selector_encoding': 'high_bit_active_low7_index',
            'selected_blend_state_index': 8,
            'tested_materials': sorted([*CARDS.keys(), CIRCUIT]),
            'opaque_no_override_fixture': OPAQUE,
            'remaining_state_bytes_semantics': 'NOT_PROMOTED_GLOBALLY',
        },
        'blend_state_8': {
            'render_target_0_descriptor': desc8,
            'rgb_equation': 'Source.rgb + Destination.rgb * (1 - Source.a)',
            'alpha_equation': 'Source.a + Destination.a * (1 - Source.a)',
            'portable_name': 'PREMULTIPLIED_ALPHA_COMPOSITION',
        } if promoted else None,
        'cross_fixture_predictions': {
            '80B9E8C2_80B9E8CF': {
                'shader_output': 'rgb = authored_rgb * A; alpha = A',
                'state8_result': 'authored_rgb*A + destination*(1-A)',
                'interpretation': 'premultiplied-alpha color composition',
            },
            '80B9E8C3_80B9E8D0': {
                'shader_output': 'rgb = 0; alpha = A',
                'state8_result': 'destination*(1-A)',
                'interpretation': 'alpha-only destination attenuation; beauty-pass role still requires pass ownership proof',
            },
            '816CE240_816CE0A8': {
                'shader_output': 'rgb = circuitry HDR color; alpha = 0',
                'state8_result': 'source_rgb + destination_rgb',
                'interpretation': 'exact additive RGB consequence of the same premultiplied blend state when source alpha is zero',
            },
            '809C475F': {
                'material_byte0': '0x00',
                'state_result': 'no material blend-state override selected by this field',
                'interpretation': 'independent opaque/deferred control fixture',
            },
        } if promoted else None,
        'evidence': {
            'alkahest_commit': corr.get('alkahest_commit'),
            'alkahest_technique_sha256': corr.get('alkahest_technique_sha256'),
            'alkahest_blend_states_sha256': corr.get('alkahest_blend_states_sha256'),
            'circuit_gcn_sha256': circ.get('gcn_sha256'),
            'card_shader_count': card.get('shader_count'),
        },
        'violations': violations,
        'policy': (
            'Promotion requires agreement between exact D1 material bytes, independently pinned Tiger PipelineState source, '
            'the exact blend-state table, and three distinct exact shader-output contracts. The promotion is intentionally '
            'limited to byte0/0x88 and state index 8 for the tested materials. Other byte values and lanes remain unresolved.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))
    return 0 if promoted else 2


if __name__ == '__main__':
    raise SystemExit(main())
