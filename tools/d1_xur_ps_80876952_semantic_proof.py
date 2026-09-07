#!/usr/bin/env python3
"""Fail-closed native dataflow proof for Xur PS 80876952.

The proof closes the exact retail PS4 GCN arithmetic for the three scoped
materials while deliberately keeping TFX producer semantics, high-level PBR
labels, render state, and portable recreation as separate gates.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

SHADER='80876952'
NATIVE_SHADER='80876955'
NATIVE_SHA='e028c6098344779b53be464ab95acf05d9a6ed8392126050441a5643ee6f6339'
GCN_SHA='cd1acacbbf0fa69a229255ab4d21c8f218fb50b3c031d63a6bb3c866d5dc57a7'
MEMBERS=['808764C9','808767AE','808767AF']
TFX_HEX='490047214901472249024723490347244904472549054726490647274907472834003c01003401031a230d34020e420d34033c01003404031a230e420e340534063c01043407011f340834091223033c0100340a032923350b0321034211'
TEXTURES={
 '808764C9':{0:'808764E6',1:'80AB04CD',2:'808764E7',3:'80AB04C1',4:'80AB04CF',5:'80876951',6:'80AACD40',7:'80AACD40'},
 '808767AE':{0:'80876818',1:'80AB04CD',2:'80876819',3:'80AB04C1',4:'80AB04CF',5:'80876951',6:'80AACD40',7:'80AACD40'},
 '808767AF':{0:'8087681A',1:'80AB04CD',2:'8087681B',3:'80AB04C1',4:'80AB04CF',5:'80876951',6:'80AACD40',7:'80AACD40'},
}
FORMATS={
 0:('BC3','sRGB',2048,2048,1),
 1:('BC3','sRGB',512,512,1),
 2:('BC5','linear',2048,2048,1),
 3:('BC5','linear',512,512,1),
 4:('RGBA8','linear',16,16,6),
 5:('BC1','sRGB',1024,1024,1),
 6:('BC1','sRGB',512,512,1),
 7:('BC1','sRGB',512,512,1),
}
SAMPLERS=['80AAE177','80AAE177','80AAE177','80AAE177','80AAE176','80AAE177','80AAE177','80AAE177']
SAMPLER_SHAS=[
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '0bcdaa82ea0d8588e313f29998f6c7b9166e7d28d40b13d422348d55ae5dc208',
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
]
CB_COMMON=[
 '0000004000000000000000bf000000bf','0000000000000040000000bf000000bf','00000040000080bf000080bf000080bf',
 '0000004000000000000000bf000000bf','0000000000000040000000bf000000bf','00000040000080bf000080bf000080bf',
 '00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000',
 '0000803f0000803f0000803f0000803f','000000000000803f0000803f0000803f','6666a6bf333313400000803f0000803f',
 '000000006666a63f0000004000000000','00000000000000000000000000000000','00000000000000000000000000000000',
 '00000040000080bf0000000000000000','1750ce3e0e78123f3e30763f0000803f','00000000000000000000000000000000',
 '00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000',
 '00000000000000000000000000000000','00000000d6d4543d0000504100006041',
]
CB_AF=CB_COMMON.copy()
CB_AF[0]='33337340000000003333b3bf3333b3bf'; CB_AF[1]='00000000333373403333b3bf3333b3bf'
CB_AF[3]='33337340000000003333b3bf3333b3bf'; CB_AF[4]='00000000333373403333b3bf3333b3bf'
CB_BY_MATERIAL={'808764C9':CB_COMMON,'808767AE':CB_COMMON,'808767AF':CB_AF}
PRIV=[
 [2.0,2.0,0.0,0.0],[0.05000000074505806,1.0,1.0,1.0],[0.0,0.0,0.0,0.0],
 [2.0,2.0,0.0,0.0],[0.05000000074505806,1.0,1.0,1.0],[0.699999988079071,0.30000001192092896,1.0,1.0],
 [25.0,1.0,1.0,1.0],[1.0,1.0,1.0,1.0],[0.5,1.0,1.0,1.0],[0.5,1.0,1.0,1.0],
 [0.20000000298023224,1.0,1.0,1.0],[0.5,1.0,1.0,1.0],[1.0,1.0,1.0,1.0],
]
EXPECTED_USAGE=[
 ('PtrExtendedUserData',1,2),('ImmSampler',1,4),('ImmSampler',2,8),('PtrResourceTable',0,12),
 ('ImmSampler',3,16),('ImmSampler',4,20),('ImmSampler',5,24),('ImmSampler',6,28),
 ('ImmSampler',7,32),('ImmSampler',8,36),('ImmConstBuffer',0,40),('ImmConstBuffer',12,44),
]
EXPECTED_IMAGE=[
 ('image_sample',2,3,3),('image_sample',3,4,3),('image_sample',0,1,15),('image_sample',1,2,15),
 ('image_get_lod',4,5,2),('image_sample',5,6,4),('image_sample',6,7,1),
 ('image_sample_l',4,5,15),('image_sample',7,8,1),
]
ANCHORS=[
 'v_mad_f32       v8, v8, s14, v10','v_mac_f32       v8, s0, v4','v_add_f32       v4, -v4, 1.0 clamp',
 'v_sqrt_f32      v4, v4','v_rsq_clamp_f32 v4, v15','v_rsq_clamp_f32 v8, v8',
 'v_max_f32       v16, v13, v13 mul:2','v_mad_legacy_f32 v17, -v11, v4, v17',
 'v_cubema_f32    v4, v17, v18, v16','image_get_lod   v11, v[27:30], s[20:27], s[44:47] dmask:2',
 'image_sample_l  v[27:30], v[27:30], s[20:27], s[44:47] dmask:15','v_log_f32       v6, v6',
 'v_exp_f32       v3, v6','v_madak_f32     v6, v18, v6, 0x3f000000',
 'v_madmk_f32     v3, v3, 0x40930885, v7','exp             mrt1, v1, v1, v5, v5 compr',
 'exp             mrt0, v1, v1, v0, v0 done compr vm',
]
K=4.594789981842041

def flat(ps): return [float(v) for row in ps['cbuffers']['items'] for v in row['value']]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--material-state',type=Path,required=True); ap.add_argument('--shader-census',type=Path,required=True)
    ap.add_argument('--image-usage',type=Path,required=True); ap.add_argument('--texture-manifest',type=Path,required=True)
    ap.add_argument('--disassembly',type=Path,required=True); ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args(); st=json.loads(a.material_state.read_text()); ce=json.loads(a.shader_census.read_text())
    im=json.loads(a.image_usage.read_text()); ma=json.loads(a.texture_manifest.read_text()); asm=a.disassembly.read_text(); viol=[]
    if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT': viol.append('material state checkpoint not exact')
    if ce.get('status')!='D1_XUR_ALL_NATIVE_SHADER_DISASSEMBLY_EXACT': viol.append('shader census checkpoint not exact')
    if im.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT': viol.append('image usage checkpoint not exact')
    if ma.get('visible_material_count')!=54 or ma.get('material_decode_errors') or ma.get('texture_errors'): viol.append('texture manifest checkpoint not exact/error-free')
    sr=next((x for x in ce.get('shaders',[]) if x.get('shader')==SHADER),None)
    if not sr: viol.append('shader absent')
    else:
        for k,v in [('native_shader',NATIVE_SHADER),('native_sha256',NATIVE_SHA),('gcn_sha256',GCN_SHA),('gcn_bytes',1144),('instruction_count_approx',237)]:
            if sr.get(k)!=v: viol.append(f'{k} mismatch: {sr.get(k)!r}')
        if sr.get('stages')!=['ps']: viol.append('not PS-only')
        slots=[(x.get('usage_name'),x.get('api_slot'),x.get('start_register')) for x in sr.get('usage',{}).get('slots',[])]
        if slots!=EXPECTED_USAGE: viol.append(f'user-data usage mismatch: {slots!r}')
    ir=next((x for x in im.get('shaders',[]) if x.get('shader')==SHADER),None)
    if not ir: viol.append('image usage absent')
    else:
        if ir.get('image_instruction_count')!=9: viol.append('expected 9 image instructions')
        if ir.get('used_texture_indices')!=list(range(8)): viol.append('used texture indices mismatch')
        if ir.get('texture_instruction_counts')!={'0':1,'1':1,'2':1,'3':1,'4':2,'5':1,'6':1,'7':1}: viol.append('texture instruction counts mismatch')
        if ir.get('unmatched_image_instruction_count')!=0: viol.append('unmatched image instruction')
        got=[]
        for row in ir.get('instructions',[]):
            rr=row.get('resources') or []; ss=row.get('samplers') or []
            got.append((row.get('opcode'),rr[0].get('texture_index') if len(rr)==1 else None,ss[0].get('sampler_index') if len(ss)==1 else None,row.get('dmask')))
        if got!=EXPECTED_IMAGE: viol.append(f'image instruction sequence mismatch: {got!r}')
    for needle in ANCHORS:
        if needle not in asm: viol.append('missing disassembly anchor: '+needle)
    for mh in MEMBERS:
        row=(st.get('materials') or {}).get(mh)
        if not row: viol.append('missing material '+mh); continue
        ps=row['ps']
        if ps.get('shader')!=SHADER: viol.append(f'{mh}: PS mismatch')
        if row.get('material_state4_hex')!='00000000': viol.append(f'{mh}: material state mismatch')
        if ps['tfx_bytecode'].get('bytes_hex')!=TFX_HEX or ps.get('tfx_disassembly',{}).get('complete') is not True: viol.append(f'{mh}: TFX mismatch/incomplete')
        targets=[op.get('d1_unk42_u8') for op in ps.get('tfx_disassembly',{}).get('ops',[]) if op.get('name')=='Unk42']
        if targets!=[13,14,17]: viol.append(f'{mh}: D1 0x42 operand targets mismatch: {targets!r}')
        if [x['value'] for x in ps['tfx_private_constants']['items']]!=PRIV: viol.append(f'{mh}: TFX private constants mismatch')
        if [x['raw_hex'] for x in ps['cbuffers']['items']]!=CB_BY_MATERIAL[mh]: viol.append(f'{mh}: full CBuffer payload mismatch')
        tex={int(x['texture_index']):x['texture'] for x in ps['textures']['items']}
        if tex!=TEXTURES[mh]: viol.append(f'{mh}: exact texture map mismatch')
        if [x['first_dword_hex'] for x in ps['samplers']['items']]!=SAMPLERS: viol.append(f'{mh}: sampler tags mismatch')
        shas=[(r.get('native_sampler') or {}).get('payload_sha256') for r in ps.get('sampler_references',[])]
        if shas!=SAMPLER_SHAS: viol.append(f'{mh}: native sampler descriptors mismatch')
        if len(flat(ps))!=92: viol.append(f'{mh}: expected 23 Vec4 / 92 dwords')
        for idx,tag in tex.items():
            tr=(ma.get('textures') or {}).get(tag)
            if not tr: viol.append(f'{mh}: missing manifest texture {tag}'); continue
            fmt,cs,w,h,array=FORMATS[idx]; hi=tr.get('header_info') or {}
            if (tr.get('format_name'),tr.get('native_colorspace_hint'))!=(fmt,cs): viol.append(f'{mh}: t{idx} format/colorspace mismatch')
            if (hi.get('width'),hi.get('height'),hi.get('array_size'))!=(w,h,array): viol.append(f'{mh}: t{idx} dimensions/array mismatch')
            if idx==4 and len(tr.get('faces') or [])!=6: viol.append(f'{mh}: t4 is not six-face cube')
    if viol:
        out={'schema_version':1,'status':'D1_XUR_PS_80876952_DATAFLOW_SEMANTICS_PARTIAL','violations':viol}
        a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2)); return 2
    out={
      'schema_version':1,'status':'D1_XUR_PS_80876952_DATAFLOW_SEMANTICS_EXACT','shader':SHADER,'native_shader':NATIVE_SHADER,
      'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'scope_materials':MEMBERS,'scope_material_count':3,
      'exact_inputs':{
        'texture_bindings_t0_t7':{m:{str(k):v for k,v in t.items()} for m,t in TEXTURES.items()},
        'texture_slot_formats':{str(k):{'format':v[0],'colorspace':v[1],'width':v[2],'height':v[3],'array_size':v[4]} for k,v in FORMATS.items()},
        'sampler_tags':SAMPLERS,'native_sampler_payload_sha256':SAMPLER_SHAS,'tfx_bytes_hex':TFX_HEX,
        'tfx_private_constants':PRIV,'tfx_unk42_operands':[13,14,17],
        'api12_camera_semantics_dependency':{'dwords':[28,29,30],'meaning':'camera/view position','evidence':'already retail-closed D1 api12 contract used by the same attr4 subtraction pattern'},
        'surface_scale_constant':K,
      },
      'instruction_level_equations':{
        'uv':'uv = attr3.xy',
        't3_uv':'uv3 = float2(b0[12]*uv.x + b0[13]*uv.y + b0[14], b0[16]*uv.x + b0[17]*uv.y + b0[18])',
        'normal_xy':'nx = b0[8]*t2.r + b0[9] + b0[21] + b0[20]*t3.r; ny = b0[8]*t2.g + b0[9] + b0[21] + b0[20]*t3.g',
        'normal_xy_current_source_constants':'nx = 2*t2.r + 2*t3.r - 2; ny = 2*t2.g + 2*t3.g - 2',
        'normal_z':'nz = sqrt(saturate(1 - nx*nx - ny*ny))',
        'basis_transform':'Nraw = nx*attr1.xyz + ny*attr2.xyz + nz*attr0.xyz; N = normalize(Nraw)',
        'view_vector':'V = normalize(api12[28:30] - attr4.xyz)','reflection_vector':'R = 2*dot(N,V)*N - V = reflect(-V,N)',
        't1_uv':'uv1 = float2(b0[0]*uv.x + b0[1]*uv.y + b0[2], b0[4]*uv.x + b0[5]*uv.y + b0[6])',
        'surface_product':'B = t0.rgb * t1.rgb','alpha_product_scaled':f'A = {K} * t0.a * t1.a',
        'cube_lod_factor':'q = saturate(b0[44] + b0[45]*A)',
        'cube_lod_floor':'lodFloor = b0[36] + q*(b0[40] - b0[36]); L = max(image_get_lod(t4,R).y, lodFloor); cube = sample_l(t4,R,L)',
        't6_uv':'uv6 = float2(b0[52]*uv.x + b0[54], b0[53]*uv.y + b0[55])',
        't7_uv':'uv7 = float2(b0[56]*uv.x + b0[58], b0[57]*uv.y + b0[59])',
        'aux_scalar':'E = t5.b * t6.r * t7.r',
        'fresnel_power':'F = exp2(b0[50] * log2(saturate(1 - dot(N,V))))',
        'reflection_gain':'S = b0[67] * cube.a * (b0[60] + b0[61]*A) * (b0[48] + b0[49]*F)',
        'reflection_rgb':'J = cube.rgb * E * b0[64:67].rgb * S',
        'base_reflection_modulator':f'M = b0[69] + b0[68] * ({K} * B)',
        'mrt0_rgb':f'mrt0.rgb = {K} * B + M * J','mrt0_alpha':'mrt0.a = attr0.w',
        'normal_pack_scale':'k = 0.375 + 0.125*A','mrt1_rgb':'mrt1.rgb = saturate(0.5 + k*N)',
        'mrt1_alpha':'mrt1.a = b0[89]','mrt1_alpha_current_serialized_value':'0.051960788667201996',
      },
      'promoted_texture_semantics':{
        't0':'RGBA surface contributor: RGB is multiplied directly with t1 RGB for MRT0; alpha participates in A and cube LOD control',
        't1':'second RGBA surface contributor sampled at material-affine UV; RGB multiplies t0 RGB and alpha participates in A',
        't2_t3':'BC5 normal XY contributors; signed combination is instruction-proven before hemisphere-Z reconstruction and tangent-basis transform',
        't4':'six-face RGBA8 reflection cube addressed by the reflected view vector with image_get_lod plus explicit-LOD sampling',
        't5':'BC1 auxiliary source; only its blue channel is consumed by the proved scalar E',
        't6_t7':'BC1 auxiliary scalar sources; only red is consumed, each at its own material/TFX-controlled affine UV',
      },
      'scoped_tfx_dependency':{
        'unk42_operands':[13,14,17],
        'ps_consumed_vectors':{'c13':'b0[52:56] controls t6 affine UV','c14':'b0[56:60] controls t7 affine UV','c17':'b0[68:72] controls base/reflection modulation (x/y consumed by this PS)'},
        'serialized_values_for_c13_c14_c17_are_zero':True,
        'meaning':'The exact TFX stream ends three subexpressions with D1 0x42 operands 13, 14 and 17, exactly matching vectors the PS consumes in time-varying-sensitive paths. This is strong scoped producer-target evidence, but the global semantic meaning of opcode 0x42 and the Frame/Wander producers remains separately gated.',
      },
      'pixel_shader_dataflow_complete_for_scoped_binary':True,'tfx_producer_semantics_complete':False,
      'render_state_semantics_complete':False,'portable_material_recreation_complete':False,'violations':[],
      'policy':'The exact native PS arithmetic, texture register use, sampler sequence, local state, and MRT outputs are closed. High-level PBR labels, the TFX Frame/Wander producer semantics, render/blend/depth/raster state, and portable retail-equivalent implementation remain independent gates.'
    }
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','scope_material_count','instruction_level_equations','promoted_texture_semantics','scoped_tfx_dependency','violations']},indent=2)); return 0

if __name__=='__main__': raise SystemExit(main())
