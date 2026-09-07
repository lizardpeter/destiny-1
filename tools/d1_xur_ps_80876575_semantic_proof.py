#!/usr/bin/env python3
"""Fail-closed native dataflow proof for Xur PS 80876575.

This closes the exact PS4 GCN arithmetic for the two scoped materials while
leaving higher-level PBR naming, TFX producer semantics, render state, and
portable recreation as independent gates.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

SHADER='80876575'
NATIVE_SHADER='808765C1'
NATIVE_SHA='a184db15565901e4525e47bbaadc415bba0b9feed6529da3a89f2e23472e7fa1'
GCN_SHA='a54830f1a28db733eaba59f8edd12612b41370e82fcbb03f1c8597566ccdf20a'
MEMBERS=['8087623B','80876410']
TFX_HEX='490047214901472249024723490347244904472549054726'
TEXTURES={0:'80876556',1:'80AAF8B6',2:'80876557',3:'80AB04D3',4:'80AACC28',5:'80876558'}
FORMATS={
 0:('BC3','sRGB',1024,512,1),
 1:('BC3','sRGB',512,512,1),
 2:('BC5','linear',1024,512,1),
 3:('BC5','linear',512,512,1),
 4:('RGBA8','linear',64,64,6),
 5:('BC4','linear',1024,512,1),
}
SAMPLERS=['80AAE177','80AAE177','80AAE177','80AAE177','80AAE176','80AAE177']
SAMPLER_SHAS=[
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '0bcdaa82ea0d8588e313f29998f6c7b9166e7d28d40b13d422348d55ae5dc208',
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
]
CB_RAW=[
 '00000040000080bf000080bf000080bf',
 '00002041000020410000000000000000',
 '0000803f000000bf000000bf000000bf',
 '00000000000000000000000000000000',
 '00000000000000000000000000000000',
 '00000000000000000000000000000000',
 '0000c0400000803f0000803f0000803f',
 '0000c0400000803f0000803f0000803f',
 'f931663ed9ce8f3f0000803f00000000',
 '295c4f3ee8fb893e0000000000000000',
 '3bdf8f3f000000000000000000000000',
 '7e25253d571dbf3ce817813c0000803f',
 '00000000000000000000000000000000',
 '00000000dfdd5d3e00005c4200006042',
]
EXPECTED_USAGE=[
 ('PtrExtendedUserData',1,2),('ImmSampler',1,4),('ImmSampler',2,8),('PtrResourceTable',0,12),
 ('ImmSampler',3,16),('ImmSampler',4,20),('ImmSampler',5,24),('ImmSampler',6,28),
 ('ImmConstBuffer',0,32),('ImmConstBuffer',12,36),
]
EXPECTED_IMAGE=[
 ('image_sample',2,3,3),('image_sample',3,4,3),('image_sample',0,1,15),
 ('image_get_lod',4,5,2),('image_sample',1,2,7),('image_sample',5,6,1),
 ('image_sample_l',4,5,15),
]
ANCHORS=[
 'image_sample    v[6:7], v[2:5], s[24:31], s[32:35] dmask:3',
 'image_sample    v[4:5], v[4:7], s[36:43], s[44:47] dmask:3',
 'v_add_f32       v4, -v4, 1.0 clamp','v_sqrt_f32      v4, v4',
 'v_rsq_clamp_f32 v4, v13','v_rsq_clamp_f32 v6, v6',
 'v_max_f32       v8, v11, v11 mul:2',
 'v_mad_legacy_f32 v13, -v9, v4, v13','v_cubema_f32    v4, v13, v14, v8',
 'image_get_lod   v10, v[20:23], s[28:35], s[36:39] dmask:2',
 'image_sample_l  v[19:22], v[20:23], s[28:35], s[36:39] dmask:15',
 'v_log_f32       v11, v11','v_exp_f32       v2, v11',
 'v_madak_f32     v2, v18, v2, 0x3f000000',
 'exp             mrt1, v1, v1, v2, v2 compr',
 'exp             mrt0, v1, v1, v0, v0 done compr vm',
]
K=4.594789981842041

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--material-state',type=Path,required=True)
    ap.add_argument('--shader-census',type=Path,required=True)
    ap.add_argument('--image-usage',type=Path,required=True)
    ap.add_argument('--texture-manifest',type=Path,required=True)
    ap.add_argument('--disassembly',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    st=json.loads(a.material_state.read_text()); ce=json.loads(a.shader_census.read_text())
    im=json.loads(a.image_usage.read_text()); ma=json.loads(a.texture_manifest.read_text())
    asm=a.disassembly.read_text(); viol=[]

    if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT': viol.append('material state checkpoint not exact')
    if ce.get('status')!='D1_XUR_ALL_NATIVE_SHADER_DISASSEMBLY_EXACT': viol.append('shader census checkpoint not exact')
    if im.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT': viol.append('image usage checkpoint not exact')
    if ma.get('visible_material_count')!=54 or ma.get('material_decode_errors') or ma.get('texture_errors'):
        viol.append('texture manifest checkpoint not exact/error-free')

    sr=next((x for x in ce.get('shaders',[]) if x.get('shader')==SHADER),None)
    if not sr: viol.append('shader absent')
    else:
        for k,v in [('native_shader',NATIVE_SHADER),('native_sha256',NATIVE_SHA),('gcn_sha256',GCN_SHA),('gcn_bytes',1108),('instruction_count_approx',217)]:
            if sr.get(k)!=v: viol.append(f'{k} mismatch: {sr.get(k)!r}')
        if sr.get('stages')!=['ps']: viol.append('not PS-only')
        slots=[(x.get('usage_name'),x.get('api_slot'),x.get('start_register')) for x in sr.get('usage',{}).get('slots',[])]
        if slots!=EXPECTED_USAGE: viol.append(f'user-data usage mismatch: {slots!r}')

    ir=next((x for x in im.get('shaders',[]) if x.get('shader')==SHADER),None)
    if not ir: viol.append('image usage absent')
    else:
        if ir.get('image_instruction_count')!=7: viol.append('expected 7 image instructions')
        if ir.get('used_texture_indices')!=list(range(6)): viol.append('used texture indices mismatch')
        if ir.get('texture_instruction_counts')!={'0':1,'1':1,'2':1,'3':1,'4':2,'5':1}: viol.append('texture instruction counts mismatch')
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
        if ps['tfx_bytecode'].get('bytes_hex')!=TFX_HEX or ps.get('tfx_disassembly',{}).get('complete') is not True:
            viol.append(f'{mh}: TFX mismatch/incomplete')
        if ps.get('tfx_private_constants',{}).get('items') not in ([],None): viol.append(f'{mh}: expected zero TFX private constants')
        if [x['raw_hex'] for x in ps['cbuffers']['items']]!=CB_RAW: viol.append(f'{mh}: full CBuffer payload mismatch')
        tex={int(x['texture_index']):x['texture'] for x in ps['textures']['items']}
        if tex!=TEXTURES: viol.append(f'{mh}: exact texture map mismatch')
        if [x['first_dword_hex'] for x in ps['samplers']['items']]!=SAMPLERS: viol.append(f'{mh}: sampler tags mismatch')
        shas=[(r.get('native_sampler') or {}).get('payload_sha256') for r in ps.get('sampler_references',[])]
        if shas!=SAMPLER_SHAS: viol.append(f'{mh}: native sampler descriptors mismatch')
        if len(ps['cbuffers']['items'])!=14: viol.append(f'{mh}: expected 14 Vec4 CBuffer records')

    for idx,tag in TEXTURES.items():
        tr=(ma.get('textures') or {}).get(tag)
        if not tr: viol.append('missing manifest texture '+tag); continue
        fmt,cs,w,h,array=FORMATS[idx]; hi=tr.get('header_info') or {}
        if (tr.get('format_name'),tr.get('native_colorspace_hint'))!=(fmt,cs): viol.append(f't{idx} format/colorspace mismatch')
        if (hi.get('width'),hi.get('height'),hi.get('array_size'))!=(w,h,array): viol.append(f't{idx} dimensions/array mismatch')
        if idx==4 and len(tr.get('faces') or [])!=6: viol.append('t4 is not a six-face cube')

    if viol:
        out={'schema_version':1,'status':'D1_XUR_PS_80876575_DATAFLOW_SEMANTICS_PARTIAL','violations':viol}
        a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2)); return 2

    out={
      'schema_version':1,
      'status':'D1_XUR_PS_80876575_DATAFLOW_SEMANTICS_EXACT',
      'shader':SHADER,'native_shader':NATIVE_SHADER,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,
      'scope_materials':MEMBERS,'scope_material_count':2,
      'exact_inputs':{
        'texture_bindings_t0_t5':{str(k):v for k,v in TEXTURES.items()},
        'texture_formats':{str(k):{'format':FORMATS[k][0],'colorspace':FORMATS[k][1],'width':FORMATS[k][2],'height':FORMATS[k][3],'array_size':FORMATS[k][4]} for k in FORMATS},
        'sampler_tags':SAMPLERS,'tfx_bytes_hex':TFX_HEX,
        'material_cbuffer_raw_hex':CB_RAW,
        'api12_camera_dependency':{'dwords':[28,29,30],'meaning':'camera/view position','evidence':'already retail-closed D1 api12 contract'},
        't4_cube':{'tag':'80AACC28','format':'RGBA8','colorspace':'linear','dimensions':[64,64],'faces':6},
      },
      'instruction_level_equations':{
        'uv':'uv = attr3.xy',
        'detail_normal_uv':'uvN = float2(b0[4]*uv.x+b0[6], b0[5]*uv.y+b0[7]); current uvN = 10*uv',
        'normal_xy':'nx = b0[0]*t2.r + b0[9] + b0[1] + b0[8]*t3.r; ny = b0[0]*t2.g + b0[9] + b0[1] + b0[8]*t3.g',
        'normal_xy_current_constants':'nx = 2*t2.r + t3.r - 1.5; ny = 2*t2.g + t3.g - 1.5',
        'normal_z':'nz = sqrt(saturate(1-nx*nx-ny*ny))',
        'world_normal':'N = normalize(nx*attr1.xyz + ny*attr2.xyz + nz*attr0.xyz)',
        'view_vector':'V = normalize(api12[28:30] - attr4.xyz)',
        'reflection_vector':'R = 2*dot(N,V)*N - V = reflect(-V,N)',
        'cube_lod':'lodFloor = b0[24] + t0.a*(b0[28]-b0[24]); current lodFloor=6; L=max(image_get_lod(t4,R).y,lodFloor); cube=sample_l(t4,R,L)',
        'surface_product':'C = t0.rgb * t1.rgb',
        'surface_scaled':f'Cs = {K} * C',
        'mask_branch':'B = saturate(Cs-0.25) + b0.c11.rgb*saturate(4*Cs)',
        'surface_mask_mix':'M = lerp(Cs,B,t5.r)',
        'fresnel':'F=exp2(b0[34]*log2(saturate(1-dot(N,V)))); current b0[34]=1 so F=saturate(1-dot(N,V))',
        'reflection_strength':'S=saturate(cube.a*(b0[36]+b0[37]*t0.a)*(b0[32]+b0[33]*F))',
        'reflection_strength_current_constants':'S=saturate(cube.a*(0.20250000059604645+0.2695000171661377*t0.a)*(0.2248000055551529+1.1234999895095825*F))',
        'cube_branch':'Q=saturate(b0[40]*cube.rgb-0.25)+M*saturate(4*b0[40]*cube.rgb); current b0[40]=1.1239999532699585',
        'mrt0_rgb':'mrt0.rgb=lerp(M,Q,S)',
        'mrt0_alpha':'mrt0.a=attr0.w',
        'normal_pack':'k=0.375+0.125*t0.a; mrt1.rgb=saturate(0.5+k*normalize(N)); mrt1.a=b0[53]',
        'normal_pack_current_alpha':'mrt1.a=0.21666668355464935',
      },
      'promoted_texture_semantics':{
        't0':'RGBA surface source is instruction-proven: RGB participates directly in visible surface color and alpha modulates cubemap LOD/reflection/normal packing',
        't1':'RGB multiplicative surface/detail source is instruction-proven by direct component-wise multiplication with t0.rgb before visible-color composition',
        't2_t3':'BC5 normal XY contributors are instruction-proven by signed combination, hemisphere-Z reconstruction, tangent-basis transform and normalization',
        't4':'six-face reflection cube is instruction-proven by camera-relative reflection-vector construction, cube coordinates, image_get_lod and explicit-LOD sampling',
        't5':'single-channel blend/control mask is instruction-proven by scalar interpolation between scaled surface RGB and the alternate branch; it is not a direct visible RGB source',
      },
      'pixel_shader_dataflow_complete_for_scoped_binary':True,
      'tfx_producer_semantics_complete':False,
      'render_state_semantics_complete':False,
      'portable_material_recreation_complete':False,
      'violations':[],
      'policy':'The native PS dataflow is closed. High-level PBR labels remain withheld; TFX producer semantics, exact render/blend/depth/raster state, and final portable renderer implementation remain separate gates.'
    }
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','scope_material_count','instruction_level_equations','promoted_texture_semantics','violations']},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
