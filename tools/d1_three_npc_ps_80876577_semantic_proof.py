#!/usr/bin/env python3
"""Fail-closed native/current-state color semantic proof for D1 PS4 PS 80876577.

The proof is deliberately scoped to the four exact Tower-Xur materials in the
three-NPC checkpoint.  It closes native GCN texture/resource dataflow and the
current serialized b0 state without claiming generic PBR equivalence, TFX
producer semantics, or a runtime permutation beyond those exact records.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

SHADER = '80876577'
NATIVE = '808765C3'
NATIVE_SHA = 'de76f5fa87c2e16e027c2554c501f6ad0a7528f1000535e9926ba8bfb3821242'
GCN_SHA = '2541b6332610fd4649afc0292389acaba734834f08e04a53021f0e3ac5d3987b'
MATERIALS = ['8087650A', '80876511', '8087651F', '80876526']
TEXTURES = {
    0: '80876551',
    1: '80876552',
    2: '80AB04BB',
    3: '80AAF8B8',
    4: '80AB0A52',
    5: '80876555',
    6: '80876554',
    7: '80AB0A50',
    8: '80AACC28',
}
TFX_SHA = 'd20b748ea6778af3fdb6586274dc89f12b67be8934ea7985d2460d4e2ec69f75'
TFX_HEX = '4900472149014722490247234903472449044725490547264906472749074728490847293c011c23220034000f2322003501420a'
PRIVATE_RAW = [
    '00000000000000000000803f00000000',
    '8fc2753c0000803f0000803f0000803f',
    '0000803f0000803f0000803f0000803f',
]
STATE = '00008100'
EXPECTED_USAGE = [
    ('PtrExtendedUserData', 1, 2),
    ('ImmSampler', 1, 4),
    ('ImmSampler', 2, 8),
    ('PtrResourceTable', 0, 12),
    ('ImmSampler', 3, 16),
    ('ImmSampler', 4, 20),
    ('ImmSampler', 5, 24),
    ('ImmSampler', 6, 28),
    ('ImmSampler', 7, 32),
    ('ImmSampler', 8, 36),
    ('ImmSampler', 9, 40),
    ('ImmConstBuffer', 0, 44),
    ('ImmConstBuffer', 12, 48),
]
EXPECTED_IMAGE = [
    ('image_sample', 0, 1, 3),
    ('image_sample', 5, 6, 4),
    ('image_sample', 1, 2, 15),
    ('image_sample', 6, 7, 3),
    ('image_sample', 7, 8, 3),
    ('image_get_lod', 8, 9, 2),
    ('image_sample', 2, 3, 7),
    ('image_sample', 3, 4, 7),
    ('image_sample', 4, 5, 7),
    ('image_sample_l', 8, 9, 15),
]
# The values below are addressed by the native s_buffer offsets (dword units).
CB = {
    40: 0.0,
    44: 17.0, 45: 17.0,
    48: 1.0, 49: 1.0, 50: 1.0, 51: 0.23750001192092896,
    52: 0.03551533818244934, 53: 0.03768035024404526, 54: 0.04031895846128464, 55: 1.0,
    56: 0.03551533818244934, 57: 0.03768035024404526, 58: 0.04031895846128464, 59: 1.0,
    60: 0.020570652559399605, 61: 0.021824637427926064, 62: 0.023352932184934616, 63: 1.0,
    64: 2.0, 65: -1.0,
    68: 17.0, 69: 17.0,
    72: 1.600000023841858, 73: -0.800000011920929,
    88: 6.0, 92: 6.0,
    96: 0.2248000055551529, 97: 1.1234999895095825, 98: 1.0,
    100: 0.20250000059604645, 101: 0.2695000171661377,
    104: 1.1239999532699585,
    113: 0.21666668355464935,
}
K = 4.594789981842041
ANCHORS = [
    'image_sample    v[7:8], v[3:6], s[16:23], s[4:7] dmask:3',
    'image_sample    v9, v[3:6], s[24:31], s[32:35] dmask:4',
    'image_sample    v[10:13], v[3:6], s[16:23], s[8:11] dmask:15',
    'v_cmp_gt_f32    vcc, 0, v15',
    's_andn2_b64     s[64:65], s[64:65], vcc',
    'image_sample    v[5:6], v[3:6], s[20:27], s[28:31] dmask:3',
    'image_sample    v[15:16], v[15:18], s[32:39], s[40:43] dmask:3',
    'v_add_f32       v6, -v6, 1.0 clamp',
    'v_sqrt_f32      v6, v6',
    'v_rsq_clamp_f32 v6, v22',
    'v_rsq_clamp_f32 v5, v5',
    'v_max_f32       v17, v20, v20 mul:2',
    'v_cubema_f32    v2, v21, v22, v17',
    'image_get_lod   v18, v[30:33], s[16:23], s[24:27] dmask:2',
    'image_sample    v[21:23], v[3:6], s[32:39], s[40:43] dmask:7',
    'image_sample    v[24:26], v[3:6], s[44:51], s[52:55] dmask:7',
    'image_sample    v[27:29], v[3:6], s[56:63], s[12:15] dmask:7',
    'image_sample_l  v[30:33], v[30:33], s[16:23], s[24:27] dmask:15',
    'v_mad_f32       v14, v7, v14, s8',
    'v_mac_f32       v14, v8, v18',
    'v_mac_f32       v14, v9, v2',
    'v_mul_f32       v4, v10, v14',
    'v_log_f32       v2, v8',
    'v_exp_f32       v2, v2',
    'v_madmk_f32     v4, v4, 0xc0930885, v20',
    'v_madak_f32     v2, v22, v2, 0x3f000000',
    'exp             mrt1, v1, v1, v2, v2 compr',
    'exp             mrt0, v1, v1, v0, v0 done compr vm',
]


def flat_cb(m: dict) -> list[float]:
    return [float(v) for row in m['ps']['cbuffers']['items'] for v in row['value']]


def texmap(m: dict) -> dict[int, str]:
    return {int(x['texture_index']): x['texture'].upper() for x in m['ps']['textures']['items']}


def close(a: float, b: float, eps: float = 2e-7) -> bool:
    return math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=eps)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--extract-report', type=Path, required=True)
    ap.add_argument('--image-usage', type=Path, required=True)
    ap.add_argument('--material-state', type=Path, required=True)
    ap.add_argument('--disassembly', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    ext = json.loads(a.extract_report.read_text())
    iu = json.loads(a.image_usage.read_text())
    st = json.loads(a.material_state.read_text())
    asm = a.disassembly.read_text()
    viol: list[str] = []

    if ext.get('status') != 'D1_WORLD_PIXEL_SHADER_GCN_EXACT':
        viol.append('extract checkpoint not exact')
    if iu.get('status') != 'D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':
        viol.append('image usage checkpoint not exact')
    if st.get('status') != 'D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):
        viol.append('material state checkpoint not exact')

    er = next((x for x in ext.get('shaders', []) if x.get('shader') == SHADER), None)
    if not er:
        viol.append('shader extraction row absent')
    else:
        for k, v in [('native_shader', NATIVE), ('native_sha256', NATIVE_SHA), ('gcn_sha256', GCN_SHA), ('gcn_bytes', 1532)]:
            if er.get(k) != v:
                viol.append(f'{k} mismatch: {er.get(k)!r}')
        slots = [(x.get('usage_name'), x.get('api_slot'), x.get('start_register')) for x in er.get('usage', {}).get('slots', [])]
        if slots != EXPECTED_USAGE:
            viol.append(f'user-data usage mismatch: {slots!r}')

    ir = next((x for x in iu.get('shaders', []) if x.get('shader') == SHADER), None)
    if not ir:
        viol.append('image usage row absent')
    else:
        got = []
        for x in ir.get('instructions', []):
            rr = x.get('resources') or []
            ss = x.get('samplers') or []
            got.append((x.get('opcode'), rr[0].get('texture_index') if len(rr) == 1 else None,
                        ss[0].get('sampler_index') if len(ss) == 1 else None, x.get('dmask')))
        if got != EXPECTED_IMAGE:
            viol.append(f'image instruction sequence mismatch: {got!r}')
        if ir.get('unmatched_image_instruction_count') != 0:
            viol.append('unmatched native image instruction')

    for needle in ANCHORS:
        if needle not in asm:
            viol.append('missing native anchor: ' + needle)

    shader_mats = sorted((st.get('shader_materials', {}).get('ps', {}) or {}).get(SHADER, []))
    if shader_mats != sorted(MATERIALS):
        viol.append(f'scoped material set mismatch: {shader_mats!r}')

    reference = None
    for mh in MATERIALS:
        m = (st.get('materials') or {}).get(mh)
        if not m or m.get('error'):
            viol.append(f'{mh}: material unresolved')
            continue
        ps = m['ps']
        if m.get('material_state4_hex') != STATE:
            viol.append(f'{mh}: state mismatch')
        if ps.get('shader') != SHADER:
            viol.append(f'{mh}: PS mismatch')
        if ps.get('tfx_program_sha256') != TFX_SHA or ps['tfx_bytecode'].get('bytes_hex') != TFX_HEX or not ps.get('tfx_disassembly', {}).get('complete'):
            viol.append(f'{mh}: TFX mismatch/incomplete')
        if [x['raw_hex'] for x in ps['tfx_private_constants']['items']] != PRIVATE_RAW:
            viol.append(f'{mh}: private TFX constants mismatch')
        if texmap(m) != TEXTURES:
            viol.append(f'{mh}: t# texture map mismatch: {texmap(m)!r}')
        vals = flat_cb(m)
        if len(vals) != 116:
            viol.append(f'{mh}: expected 116 b0 dwords, got {len(vals)}')
            continue
        for idx, val in CB.items():
            if not close(vals[idx], val):
                viol.append(f'{mh}: b0[{idx}]={vals[idx]!r} expected {val!r}')
        semantic = (
            ps['tfx_bytecode']['bytes_hex'],
            tuple(x['raw_hex'] for x in ps['tfx_private_constants']['items']),
            tuple(x['raw_hex'] for x in ps['cbuffers']['items']),
            tuple(sorted(texmap(m).items())),
            tuple(x['first_dword_hex'] for x in ps['samplers']['items']),
            tuple((r.get('native_sampler') or {}).get('payload_sha256') for r in ps.get('sampler_references', [])),
        )
        if reference is None:
            reference = semantic
        elif semantic != reference:
            viol.append(f'{mh}: PS semantic payload differs from family reference')

    if viol:
        out = {'schema_version': 1, 'status': 'D1_TOWER_PS_80876577_CURRENT_STATE_COLOR_SEMANTICS_PARTIAL', 'violations': viol}
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(out, indent=2) + '\n')
        print(json.dumps(out, indent=2))
        return 2

    out = {
        'schema_version': 1,
        'status': 'D1_TOWER_PS_80876577_CURRENT_STATE_COLOR_SEMANTICS_EXACT',
        'violations': [],
        'shader': SHADER,
        'native_shader': NATIVE,
        'native_sha256': NATIVE_SHA,
        'gcn_sha256': GCN_SHA,
        'scope_materials': MATERIALS,
        'scope_material_count': 4,
        'visible_primitive_count': 27,
        'exact_inputs': {
            'texture_bindings_t0_t8': {str(k): v for k, v in TEXTURES.items()},
            'material_state4_hex': STATE,
            'tfx_program_sha256': TFX_SHA,
            'tfx_bytes_hex': TFX_HEX,
            'tfx_private_constants_raw_hex': PRIVATE_RAW,
            'api12_camera_dependency': {'dwords': [28, 29, 30], 'meaning': 'camera/view position', 'evidence': 'already source-closed D1 api12 contract'},
            'current_b0_values': {str(k): v for k, v in CB.items()},
        },
        'instruction_level_equations': {
            'uv': 'uv = attr3.xy',
            'coverage_q0': 'q0 = b0[51] + t0.r*(t0.r-b0[51])',
            'coverage_q1': 'q1 = q0 + t0.g*(t0.g-q0)',
            'coverage_q2': 'q2 = q1 + t5.b*(t5.b-q1)',
            'coverage_test': 'coverage = t1.a*q2; native lanes with coverage < b0[40] are killed; current b0[40]=0',
            'normal_detail_uv': 'uvN = float2(b0[68]*uv.x, b0[69]*uv.y); current uvN=17*uv',
            'normal_xy': 'nx=b0[64]*t6.r+b0[65]+b0[73]+b0[72]*t7.r; ny=b0[64]*t6.g+b0[65]+b0[73]+b0[72]*t7.g',
            'normal_xy_current': 'nx=2*t6.r+1.6*t7.r-1.8; ny=2*t6.g+1.6*t7.g-1.8',
            'normal_z': 'nz=sqrt(saturate(1-nx*nx-ny*ny))',
            'native_basis_sign': 'h = +1 when the native incoming v2 lane is nonzero, otherwise -1; no higher-level semantic name is promoted here',
            'world_normal': 'N=normalize(nx*attr1.xyz + ny*attr2.xyz + h*nz*attr0.xyz)',
            'view_vector': 'V=normalize(api12[28:30]-attr4.xyz)',
            'reflection_vector': 'R=2*dot(N,V)*N-V',
            'cube_lod': 'lodFloor=lerp(b0[88],b0[92],coverage); current endpoints are both 6, so L=max(image_get_lod(t8,R).y,6)',
            'palette_a': 'A=saturate(b0[52:54]-0.25)+t2.rgb*saturate(4*b0[52:54])',
            'palette_b': 'B=saturate(b0[56:58]-0.25)+t3.rgb*saturate(4*b0[56:58])',
            'palette_c': 'C=saturate(b0[60:62]-0.25)+t4.rgb*saturate(4*b0[60:62])',
            'palette_mix_1': 'P1=lerp(b0[48:50],A,t0.r); current b0[48:50]=(1,1,1)',
            'palette_mix_2': 'P2=lerp(P1,B,t0.g)',
            'palette_mix_3': 'P3=lerp(P2,C,t5.b)',
            'surface_product': 'Csurf=t1.rgb*P3',
            'surface_scaled': f'Cs={K}*Csurf',
            'fresnel': 'F=exp2(b0[98]*log2(saturate(1-dot(N,V)))); current b0[98]=1',
            'reflection_strength': 'S=saturate(cube.a*(b0[100]+b0[101]*coverage)*(b0[96]+b0[97]*F))',
            'reflection_strength_current': 'S=saturate(cube.a*(0.2025+0.2695000171661377*coverage)*(0.2248000055551529+1.1234999895095825*F))',
            'cube_branch': 'Q=saturate(b0[104]*cube.rgb-0.25)+Cs*saturate(4*b0[104]*cube.rgb); current b0[104]=1.1239999532699585',
            'mrt0_rgb': 'mrt0.rgb=lerp(Cs,Q,S)',
            'mrt0_alpha': 'mrt0.a=attr0.w',
            'normal_pack': 'k=0.375+0.125*coverage; mrt1.rgb=saturate(0.5+k*normalize(N)); mrt1.a=b0[113]',
            'normal_pack_current_alpha': 'mrt1.a=0.21666668355464935',
        },
        'promoted_texture_semantics': {
            't0': {'tag': TEXTURES[0], 'role': 'palette_selector_rg_and_coverage_control', 'proof': 'native xy sample drives first two palette lerps and coverage polynomial'},
            't1': {'tag': TEXTURES[1], 'role': 'surface_rgb_multiplier_and_coverage_alpha', 'proof': 'native RGB multiplies reconstructed palette; alpha multiplies coverage'},
            't2': {'tag': TEXTURES[2], 'role': 'palette_branch_a_rgb', 'proof': 'native RGB enters first color branch at 17x UV'},
            't3': {'tag': TEXTURES[3], 'role': 'palette_branch_b_rgb', 'proof': 'native RGB enters second color branch at 17x UV'},
            't4': {'tag': TEXTURES[4], 'role': 'palette_branch_c_rgb', 'proof': 'native RGB enters third color branch at 17x UV'},
            't5': {'tag': TEXTURES[5], 'role': 'palette_selector_b_and_coverage_control', 'proof': 'native z sample drives third palette lerp and coverage polynomial'},
            't6': {'tag': TEXTURES[6], 'role': 'primary_normal_xy', 'proof': 'native xy enters signed normal reconstruction'},
            't7': {'tag': TEXTURES[7], 'role': 'detail_normal_xy', 'proof': 'native xy at 17x UV enters the same normal reconstruction'},
            't8': {'tag': TEXTURES[8], 'role': 'environment_cubemap', 'proof': 'native cube coordinate ops + image_get_lod + image_sample_l'},
        },
        'critical_correction': '80876577 has no single base-color texture. Its native surface RGB is t1.rgb multiplied by a three-branch palette reconstructed from t2/t3/t4 and selected by t0.r, t0.g, and t5.b before reflection.',
        'gates': {
            'current_material_native_color_dataflow_closed': True,
            'coverage_kill_path_closed': True,
            'portable_blender_recreation_complete': False,
            'deferred_framebuffer_equivalence_closed': False,
            'runtime_external_material_permutation_selected': False,
        },
        'policy': 'Exact current serialized material state and native instruction dataflow for this family only. No generic PBR or unresolved runtime-permutation claim is made.',
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in ('status', 'scope_material_count', 'visible_primitive_count', 'critical_correction', 'gates')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
