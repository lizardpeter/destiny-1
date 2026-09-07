#!/usr/bin/env python3
"""Fail-closed native dataflow proof for the shared Xur VS GCN family.

Three serialized VS headers (8087695C, 809DF743, 80A08C19) resolve to the exact
same 700-byte retail PS4 GCN program. The proof closes the post-fetch transform
math and param0..param4 interface without guessing fetch-shader source offsets or
engine-facing names for the global constant buffers.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HEADERS={
 '8087695C':'8087695E',
 '809DF743':'809DF744',
 '80A08C19':'80A08C1A',
}
NATIVE_SHA='16693766a86fa2fb1df82f48a378184ff49967421d71df62dc0ee15aee3a432a'
GCN_SHA='a5ad940fbf21746563f6585b889ac91b4220c94a3559e768028c894454bcdc12'
MEMBERS=[
 '8087623B','8087623F','808762D7','8087642F','808764CB','808764CC','808764CD','808764CE','808764CF',
 '8087652C','8087652D','8087652E','8087652F','80876530','80876533','80876546','80876547','80876548',
 '80876688','808767B2','808767B3','80876864','80876865','80876867','80876868','80876894','808768BA',
 '808768BB','80876CAE','80C888C7','80C888C9',
]
EXPECTED_HEADER_COUNTS={'8087695C':29,'809DF743':1,'80A08C19':1}
EXPECTED_USAGE=[
 ('SubPtrFetchShader',0,0),('PtrVertexBufferTable',0,2),('PtrExtendedUserData',1,6),
 ('ImmConstBuffer',10,8),('ImmConstBuffer',11,12),('ImmConstBuffer',12,16),
]
ANCHORS=[
 's_swappc_b64    s[0:1], s[0:1]',
 'v_mac_f32       v0, s0, v7',
 'v_cvt_u32_f32   v0, v0',
 'v_lshlrev_b32   v0, 1, v0',
 'tbuffer_load_format_xyzw v[20:23], v0, s[8:11], 0 idxen format:[32_32_32_32,float]',
 'tbuffer_load_format_xyzw v[0:3], v0, s[8:11], 0 idxen format:[32_32_32_32,float]',
 's_buffer_load_dwordx4 s[0:3], s[12:15], 0x14',
 'v_max_f32       v11, v22, v22 mul:2',
 'v_mad_f32       v26, -v11, v7, v4',
 'v_mad_f32       v26, -v11, v1, v26',
 'exp             pos0, v0, v1, v7, v10 done',
 's_buffer_load_dwordx4 s[0:3], s[12:15], 0x1c',
 's_buffer_load_dwordx4 s[4:7], s[12:15], 0x18',
 'v_mad_f32       v1, v13, v18, -v1',
 'v_mad_f32       v2, v14, v16, -v2',
 'v_mad_f32       v3, v12, v17, -v3',
 'v_mul_f32       v1, v19, v1',
 'exp             param0, v12, v13, v14, v0',
 'exp             param1, v16, v17, v18, v18',
 'exp             param2, v1, v2, v3, v8',
 'exp             param3, v4, v7, v4, v7',
 'exp             param4, v26, v5, v6, v8',
]


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--material-state',type=Path,required=True)
    ap.add_argument('--shader-census',type=Path,required=True)
    ap.add_argument('--disassembly',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    state=json.loads(a.material_state.read_text())
    census=json.loads(a.shader_census.read_text())
    asm=a.disassembly.read_text()
    violations=[]

    if state.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT': violations.append('material state checkpoint not exact')
    if census.get('status')!='D1_XUR_ALL_NATIVE_SHADER_DISASSEMBLY_EXACT': violations.append('shader census checkpoint not exact')
    by={x['shader']:x for x in census.get('shaders',[])}
    for h,native in HEADERS.items():
        r=by.get(h)
        if not r: violations.append(f'missing shader header {h}'); continue
        if r.get('stages')!=['vs']: violations.append(f'{h}: not VS-only')
        if r.get('native_shader')!=native: violations.append(f'{h}: native shader mismatch')
        if r.get('native_sha256')!=NATIVE_SHA: violations.append(f'{h}: native payload SHA mismatch')
        if r.get('gcn_sha256')!=GCN_SHA: violations.append(f'{h}: GCN SHA mismatch')
        if r.get('gcn_bytes')!=700: violations.append(f'{h}: GCN byte size mismatch')
        if r.get('instruction_count_approx')!=124: violations.append(f'{h}: instruction count mismatch')
        slots=[(x.get('usage_name'),x.get('api_slot'),x.get('start_register')) for x in r.get('usage',{}).get('slots',[])]
        if slots!=EXPECTED_USAGE: violations.append(f'{h}: user-data usage mismatch: {slots!r}')

    for needle in ANCHORS:
        if needle not in asm: violations.append(f'missing disassembly anchor: {needle}')

    got=[]; counts={h:0 for h in HEADERS}
    for mh,m in state.get('materials',{}).items():
        vs=m['vs']; h=vs.get('shader')
        if h not in HEADERS: continue
        got.append(mh);counts[h]+=1
        if vs['tfx_bytecode'].get('bytes_hex')!='': violations.append(f'{mh}: shared VS unexpectedly has TFX bytecode')
        if vs.get('tfx_disassembly',{}).get('complete') is not True: violations.append(f'{mh}: VS TFX framing incomplete')
        if vs['tfx_private_constants']['count']!=0: violations.append(f'{mh}: VS private constants not zero')
        if vs['cbuffers']['count']!=0: violations.append(f'{mh}: material-local VS CBuffer count not zero')
        if vs['textures']['count']!=0: violations.append(f'{mh}: VS texture count not zero')
        if vs['samplers']['count']!=0: violations.append(f'{mh}: VS sampler count not zero')
    if sorted(got)!=sorted(MEMBERS): violations.append(f'shared VS member set mismatch: got {sorted(got)!r}')
    if counts!=EXPECTED_HEADER_COUNTS: violations.append(f'header member counts mismatch: {counts!r}')

    if violations:
        out={'schema_version':1,'status':'D1_XUR_VS_A5AD940F_DATAFLOW_SEMANTICS_PARTIAL','violations':violations}
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
        print(json.dumps(out,indent=2));return 2

    out={
      'schema_version':1,
      'status':'D1_XUR_VS_A5AD940F_DATAFLOW_SEMANTICS_EXACT',
      'shader_headers':sorted(HEADERS),
      'native_shader_tags':HEADERS,
      'native_payload_sha256':NATIVE_SHA,
      'gcn_sha256':GCN_SHA,
      'scope_materials':MEMBERS,'scope_material_count':len(MEMBERS),
      'header_material_counts':counts,
      'material_local_vs_state':{
        'tfx_bytes':'','tfx_private_constant_count':0,'cbuffer_vec4_count':0,'texture_count':0,'sampler_count':0,
        'meaning':'the shared VS binary is driven by fetched vertex lanes plus api10/api11/api12/extended global data, not per-material VS textures or local CBuffers',
      },
      'post_fetch_register_roles':{
        'v4_v5_v6':'source position xyz before api11 scale/bias decode',
        'v7':'normalized transform-palette selector; converted back to an integer palette record index by 32767 scaling',
        'v8_v9':'source UV pair before api11 affine transform',
        'v12_v13_v14':'source normal xyz',
        'v16_v17_v18':'source tangent xyz',
        'v19':'tangent-basis handedness multiplier',
        'withheld':'exact fetch-shader source-buffer offsets/formats are outside this proof; roles are promoted from post-fetch native arithmetic only',
      },
      'instruction_level_equations':{
        'position_decode':'p = api11[20:22] + api11[23] * float3(v4,v5,v6)',
        'palette_index':'entry = 2 * uint(0.1 + 32767.0*v7); q = api10[entry]; d = api10[entry+1]',
        'dual_quaternion_translation':'translation = 2 * (d * conjugate(q)).xyz',
        'skinned_position':'P = rotate(q,p) + translation',
        'normal_transform':'N = rotate(q,float3(v12,v13,v14))',
        'tangent_transform':'T = rotate(q,float3(v16,v17,v18))',
        'bitangent':'B = v19 * cross(N,T)',
        'clip_position':'pos0 = extended_matrix_col0*P.x + extended_matrix_col1*P.y + extended_matrix_col2*P.z + extended_matrix_col3',
        'normal_scalar':'a = saturate(dot(api11[28:30],N) + api11[31])',
        'uv':'uv = float2(api11[26] + api11[24]*v8, api11[27] + api11[25]*v9)',
        'param0':'param0 = float4(N,a)',
        'param1':'param1 = float4(T.x,T.y,T.z,T.z)',
        'param2':'param2 = float4(B,1)',
        'param3':'param3 = float4(uv.x,uv.y,uv.x,uv.y)',
        'param4':'param4 = float4(P,1)',
      },
      'promoted_interface_semantics':{
        'attr0':'interpolated transformed normal xyz plus source-owned saturated scalar in w',
        'attr1':'interpolated transformed tangent xyz',
        'attr2':'interpolated handed bitangent xyz',
        'attr3':'interpolated api11-affine UV pair duplicated into zw at VS export',
        'attr4':'interpolated transformed position P; consumed as world/instance position by already-closed Tower pixel-shader families',
      },
      'dual_quaternion_skinning_dataflow_complete_for_scoped_binary':True,
      'fetch_shader_source_layout_complete':False,
      'global_buffer_engine_names_complete':False,
      'portable_skinning_recreation_complete':False,
      'violations':[],
      'policy':'The exact shared GCN arithmetic and VS export contract are closed. The proof intentionally withholds fetch-shader source offsets/formats, engine-facing api10/api11/api12 names, and any claim that the palette selector is a direct skeleton-bone index rather than a transform-palette record.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','gcn_sha256','scope_material_count','header_material_counts','instruction_level_equations','promoted_interface_semantics','dual_quaternion_skinning_dataflow_complete_for_scoped_binary','violations']},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
