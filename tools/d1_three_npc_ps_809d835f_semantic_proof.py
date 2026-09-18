#!/usr/bin/env python3
"""Fail-closed native semantic proof for D1 PS4 pixel shader 809D835F.

The generic straight-line lifter rejected this program because it contains
per-lane EXEC control flow. Manual instruction-level closure shows that the two
control-flow regions do not create alternate surviving-pixel RGB equations:

* one chooses the MRT1 auxiliary scalar from CB0[93] or CB0[97] according to
  UV.y > 1;
* one removes lanes through an alpha-test/discard comparison using t3.r and an
  extended-user-data constant.

All lanes that survive that discard execute one deterministic surface RGB,
palette/mask and cubemap/Fresnel path. This proof closes that path while keeping
the runtime alpha-test threshold semantically unnamed.
"""
from __future__ import annotations

import argparse,json,math
from pathlib import Path

SHADER='809D835F'
NATIVE='809D83A6'
NATIVE_SHA='8f3c678a6e31ee836054f59741024a0a3e0a103faed05b04db71876c54d4ae8c'
GCN_SHA='83abda92b1d12f584a8560ac12137de925ca359b0b26a563559a487a85078caf'
MATERIALS=['80C880E3','80C880E6','80C880E8','80C88113','80C888DA','80C888F1']
TEXTURES={
    0:'80C88667',1:'80C88668',2:'80C88669',3:'80C8866A',4:'80C8866B',
    5:'80AB04BC',6:'80AACC28',7:'80C88669',8:'80C88667',
}
TFX_SHA='53878434a818342246fa480f06c2c0becdf20083a93f0ed60a43f23bdbf54909'
STATE='00008100'
EXPECTED_IMAGE=[
    ('image_sample',4,3,'xy'),('image_sample',5,3,'xy'),('image_sample',1,15,'xyzw'),
    ('image_sample',0,7,'xyz'),('image_sample',2,7,'xyz'),('image_sample',7,1,'x'),
    ('image_sample',8,8,'w'),('image_sample',3,1,'x'),
    ('image_get_lod',6,2,'y'),('image_sample_l',6,15,'xyzw'),
]
CB={
    24:0.0,
    28:20.0,29:20.0,
    36:2.0,37:-1.0,
    40:9.0,41:9.0,
    44:2.0,45:-1.0,
    60:6.0,64:6.0,
    68:0.2248000055551529,69:1.1234999895095825,70:1.0,
    72:0.20250000059604645,73:0.2695000171661377,
    76:1.1239999532699585,
    80:0.6660000085830688,81:0.6660000085830688,82:0.6660000085830688,
    93:0.02450980618596077,97:0.04803922027349472,
}
ANCHORS=[
    'image_sample    v[11:12], v[9:12]',
    'image_sample    v[5:6], v[5:8]',
    'image_sample    v[13:16], v[7:10]',
    'v_cmp_lg_i32    s[0:1], v2, 0',
    'v_cmp_lt_f32    vcc, 1.0, v10',
    's_and_saveexec_b64 s[0:1], vcc',
    's_buffer_load_dword s4, s[16:19], 0x61',
    's_buffer_load_dword s4, s[16:19], 0x5d',
    'image_sample    v4, v[9:12]',
    'v_cmp_gt_f32    vcc, 0, v4',
    's_andn2_b64     s[64:65], s[64:65], vcc',
    'image_get_lod   v13, v[21:24]',
    'image_sample_l  v[20:23], v[21:24]',
    'v_log_f32       v12, v12',
    'v_exp_f32       v8, v12',
    'exp             mrt1',
    'exp             mrt0',
]


def flat_cb(m):
    return [float(v) for row in m['ps']['cbuffers']['items'] for v in row['value']]


def texmap(m):
    return {int(x['texture_index']):x['texture'].upper() for x in m['ps']['textures']['items']}


def close(a,b,eps=2e-7):
    return math.isclose(float(a),float(b),rel_tol=0.0,abs_tol=eps)


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--extract-report',type=Path,required=True)
    ap.add_argument('--image-usage',type=Path,required=True)
    ap.add_argument('--material-state',type=Path,required=True)
    ap.add_argument('--disassembly',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    ext=json.loads(a.extract_report.read_text());iu=json.loads(a.image_usage.read_text());st=json.loads(a.material_state.read_text());asm=a.disassembly.read_text();viol=[]
    if ext.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT':viol.append('extract checkpoint not exact')
    if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':viol.append('image usage checkpoint not exact')
    if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):viol.append('material state checkpoint not exact')
    er=next((x for x in ext.get('shaders',[]) if x.get('shader')==SHADER),None)
    if not er:viol.append('shader extraction row absent')
    else:
        for k,v in [('native_shader',NATIVE),('native_sha256',NATIVE_SHA),('gcn_sha256',GCN_SHA),('gcn_bytes',1448)]:
            if er.get(k)!=v:viol.append(f'{k} mismatch: {er.get(k)!r}')
        slots={(x.get('usage_name'),x.get('api_slot'),x.get('start_register')) for x in er.get('usage',{}).get('slots',[])}
        for q in [('PtrResourceTable',0,12),('ImmConstBuffer',0,44),('ImmConstBuffer',12,48),('ImmConstBuffer',13,52)]:
            if q not in slots:viol.append(f'required user-data descriptor absent: {q!r}')
    ir=next((x for x in iu.get('shaders',[]) if x.get('shader')==SHADER),None)
    if not ir:viol.append('image usage row absent')
    else:
        got=[]
        for x in ir.get('instructions',[]):
            rr=x.get('resources') or []
            got.append((x.get('opcode'),rr[0].get('texture_index') if len(rr)==1 else None,x.get('dmask'),x.get('dmask_channels')))
        if got!=EXPECTED_IMAGE:viol.append(f'image instruction sequence mismatch: {got!r}')
        if ir.get('unmatched_image_instruction_count')!=0:viol.append('unmatched native image instruction')
    for needle in ANCHORS:
        if needle not in asm:viol.append('missing native anchor: '+needle)
    shader_mats=sorted((st.get('shader_materials',{}).get('ps',{}) or {}).get(SHADER,[]))
    if shader_mats!=sorted(MATERIALS):viol.append(f'scoped material set mismatch: {shader_mats!r}')
    reference=None
    for mh in MATERIALS:
        m=(st.get('materials') or {}).get(mh)
        if not m or m.get('error'):viol.append(f'{mh}: material unresolved');continue
        if m.get('material_state4_hex')!=STATE:viol.append(f'{mh}: state mismatch')
        if m['ps'].get('shader')!=SHADER:viol.append(f'{mh}: PS mismatch')
        if m['ps'].get('tfx_program_sha256')!=TFX_SHA or not m['ps'].get('tfx_disassembly',{}).get('complete'):viol.append(f'{mh}: TFX mismatch/incomplete')
        if texmap(m)!=TEXTURES:viol.append(f'{mh}: t# texture map mismatch: {texmap(m)!r}')
        vals=flat_cb(m)
        if len(vals)<98:viol.append(f'{mh}: short CB0 {len(vals)}');continue
        for idx,val in CB.items():
            if not close(vals[idx],val):viol.append(f'{mh}: b0[{idx}]={vals[idx]!r} expected {val!r}')
        semantic=(m['ps']['tfx_bytecode']['bytes_hex'],tuple(x['raw_hex'] for x in m['ps']['tfx_private_constants']['items']),tuple(x['raw_hex'] for x in m['ps']['cbuffers']['items']),tuple(sorted(texmap(m).items())),tuple(x['first_dword_hex'] for x in m['ps']['samplers']['items']))
        if reference is None:reference=semantic
        elif semantic!=reference:viol.append(f'{mh}: PS semantic payload differs from family reference')
    if viol:
        out={'schema_version':1,'status':'D1_TOWER_PS_809D835F_DATAFLOW_SEMANTICS_PARTIAL','violations':viol}
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 2
    out={
      'schema_version':1,'status':'D1_TOWER_PS_809D835F_SURVIVING_PIXEL_COLOR_SEMANTICS_EXACT','violations':[],
      'shader':SHADER,'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,
      'scope_materials':MATERIALS,'scope_material_count':6,'visible_primitive_count':39,
      'exact_inputs':{'texture_bindings_t0_t8':{str(k):v for k,v in TEXTURES.items()},'material_state4_hex':STATE,'tfx_program_sha256':TFX_SHA,'cb0_current_values':{str(k):v for k,v in CB.items()}},
      'control_flow':{
        'mrt1_aux_selector':'per lane: CB0[97] when attr3.y > 1, else CB0[93]',
        'alpha_discard':'t3.r is compared against a scalar loaded through PtrExtendedUserData; failing lanes are removed from the saved pixel EXEC mask before the lighting/color block',
        'alpha_test_runtime_threshold_semantic_name_closed':False,
        'alternate_surviving_pixel_rgb_branch_exists':False,
      },
      'instruction_level_equations':{
        'uv':'uv=attr3.xy; normalDetailUV=9*uv; controlUV=20*uv',
        'normal_xy':'nx=2*t4.r+2*t5.r-2; ny=2*t4.g+2*t5.g-2',
        'normal_z':'nz=sqrt(saturate(1-nx*nx-ny*ny))',
        'control_scalar':'W=t1.r+t1.g for the exact current CB0 selector constants',
        'color_gate':'G.rgb=saturate(1+W-t2.rgb)',
        'surface_rgb':'C.rgb=t0.rgb*G.rgb',
        'palette_branch':'Q0.rgb=saturate(C.rgb-0.25)+b0[80:82]*saturate(4*C.rgb); current b0[80:82]=0.666',
        'surface_mask_mix':'M.rgb=lerp(C.rgb,Q0.rgb,t7.r)',
        'world_normal':'N=normalize(nx*attr1.xyz+ny*attr2.xyz+nz*attr0.xyz) with the native per-lane basis sign retained by the shader',
        'reflection_vector':'R=2*dot(N,V)*N-V',
        'cube_lod':'L=max(image_get_lod(t6,R).y, b0[60]+t8.a*(b0[64]-b0[60])); current b0[60]=b0[64]=6',
        'fresnel':'F=exp2(b0[70]*log2(saturate(1-dot(N,V)))); current b0[70]=1',
        'reflection_strength':'S=saturate(cube.a*(b0[72]+b0[73]*t8.a)*(b0[68]+b0[69]*F))',
        'cube_branch':'Q.rgb=saturate(b0[76]*cube.rgb-0.25)+M.rgb*saturate(4*b0[76]*cube.rgb); current b0[76]=1.124',
        'mrt0_rgb':'mrt0.rgb=lerp(M.rgb,Q.rgb,S)',
        'mrt0_alpha':'mrt0.a=attr0.w',
        'normal_pack':'k=0.375+0.125*t8.a; mrt1.rgb=saturate(0.5+k*N); mrt1.a is the UV-selected CB0[93]/CB0[97] value',
      },
      'promoted_texture_semantics':{
        't0':{'tag':TEXTURES[0],'role':'surface_rgb_and_alpha_duplicate','proof':'native RGB is the direct multiplicand in C; same resource is rebound as t8 alpha'},
        't1':{'tag':TEXTURES[1],'role':'two_channel_surface_control','proof':'native RGBA sample but exact current selector math reduces visible color contribution to t1.r+t1.g; not a base-color map'},
        't2':{'tag':TEXTURES[2],'role':'surface_rgb_color_gate_source_and_mask_duplicate','proof':'native RGB appears in saturate(1+W-t2); same resource is rebound as t7.r mask'},
        't3':{'tag':TEXTURES[3],'role':'alpha_test_scalar_r','proof':'native x sample feeds comparison that removes pixel lanes before lighting block'},
        't4':{'tag':TEXTURES[4],'role':'primary_normal_xy','proof':'native xy enters normal reconstruction'},
        't5':{'tag':TEXTURES[5],'role':'detail_normal_xy','proof':'native xy at 9x UV enters same normal reconstruction'},
        't6':{'tag':TEXTURES[6],'role':'environment_cubemap','proof':'native cube coordinate ops + image_get_lod + image_sample_l'},
        't7':{'tag':TEXTURES[7],'role':'surface_palette_mask_r','proof':'duplicate of t2 sampled x only and used as color lerp mask'},
        't8':{'tag':TEXTURES[8],'role':'surface_alpha_duplicate_reflection_and_normal_pack_control','proof':'duplicate of t0 sampled w only'},
      },
      'critical_correction':'The largest broken family also has no valid single heuristic baseColor choice. t1 is control data; t2 participates in a subtractive gate; t7 is a scalar palette mask. Surviving-pixel RGB must replay the native multi-texture equation.',
      'gates':{'surviving_pixel_native_color_dataflow_closed':True,'alpha_test_runtime_threshold_value_closed':False,'portable_blender_recreation_complete':False,'deferred_framebuffer_equivalence_closed':False,'runtime_external_material_permutation_selected':False},
      'policy':'Exact current-material surviving-pixel RGB/dataflow only. The alpha-test compare source is structurally proven but its runtime scalar semantic/value is deliberately not guessed.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','scope_material_count','visible_primitive_count','critical_correction','gates')},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
