#!/usr/bin/env python3
"""Fail-closed native semantic proof for D1 PS4 pixel shader 809D835C.

This closes the exact visible-color/dataflow contract for the two scoped Tower
NPC materials.  It uses only the pinned native GCN extraction, exact Sony
resource-table provenance, and exact material-local state.  It deliberately does
not flatten the result into generic PBR or claim D1 deferred/framebuffer
composition equivalence.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

SHADER='809D835C'
NATIVE='809D83A3'
NATIVE_SHA='432f2de48385467e977759a407fa14e3d7f04281273a67b85b90332bdc74fb5b'
GCN_SHA='d7a09451c42dcf84d7a3a2032cdd13428d506c2430fe9fe2b616af5620d3036e'
MATERIALS=['80C880E5','80C880E7']
TEXTURES={
    0:'80C88663', 1:'80C88664', 2:'80AB04BB', 3:'80C88665',
    4:'80AB04BC', 5:'80AACC28', 6:'80C88664', 7:'80C88663',
}
TFX_SHA='b4271f54f37c62c675e1cde807efd9eec2ce7e6a49363391915d0d27dcd7bf2c'
STATE='00000000'
K=4.594789981842041

# Exact native image order after Sony InputUsageSlot/resource-table resolution.
EXPECTED_IMAGE=[
    ('image_sample',3,3,'xy'),
    ('image_sample',4,3,'xy'),
    ('image_sample',7,8,'w'),
    ('image_get_lod',5,2,'y'),
    ('image_sample',1,7,'xyz'),
    ('image_sample',0,7,'xyz'),
    ('image_sample',2,7,'xyz'),
    ('image_sample',6,1,'x'),
    ('image_sample_l',5,15,'xyzw'),
]

# Material CB0 lanes actually consumed by the closed equations.
CB={
    0:0.9840545654296875, 1:0.9840545654296875, 2:0.9840545654296875,
    4:9.0, 5:9.0, 8:2.0, 9:-1.0, 12:9.0, 13:9.0,
    16:2.0, 17:-1.0,
    32:6.0, 36:6.0,
    40:0.2248000055551529, 41:1.1234999895095825, 42:1.0,
    44:0.20250000059604645, 45:0.2695000171661377,
    48:1.1239999532699585,
    52:0.3277781009674072, 53:0.0423114113509655, 54:0.0423114113509655,
    61:0.02450980618596077,
}

ANCHORS=[
    'image_sample    v[8:9], v[6:9]',
    'image_sample    v[4:5], v[4:7]',
    'v_add_f32       v4, -v4, 1.0 clamp',
    'v_sqrt_f32      v4, v4',
    'v_rsq_clamp_f32 v4, v15',
    'v_rsq_clamp_f32 v8, v8',
    'v_cubema_f32    v4, v15, v16, v10',
    'image_sample    v12, v[6:9]',
    'image_get_lod   v14, v[26:29]',
    'image_sample    v[15:17], v[6:9]',
    'image_sample    v[20:22], v[6:9]',
    'image_sample    v[23:25], v[2:5]',
    'image_sample    v3, v[6:9]',
    'image_sample_l  v[26:29], v[26:29]',
    'v_log_f32       v13, v13',
    'v_exp_f32       v2, v13',
    'exp             mrt1',
    'exp             mrt0',
]


def flat_cb(m:dict)->list[float]:
    return [float(v) for row in m['ps']['cbuffers']['items'] for v in row['value']]


def texmap(m:dict)->dict[int,str]:
    return {int(x['texture_index']):x['texture'].upper() for x in m['ps']['textures']['items']}


def close(a:float,b:float,eps:float=2e-7)->bool:
    return math.isclose(float(a),float(b),rel_tol=0.0,abs_tol=eps)


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--extract-report',type=Path,required=True)
    ap.add_argument('--image-usage',type=Path,required=True)
    ap.add_argument('--material-state',type=Path,required=True)
    ap.add_argument('--disassembly',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    ext=json.loads(a.extract_report.read_text())
    iu=json.loads(a.image_usage.read_text())
    st=json.loads(a.material_state.read_text())
    asm=a.disassembly.read_text()
    viol=[]

    if ext.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT':
        viol.append('extract checkpoint not exact')
    if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':
        viol.append('image usage checkpoint not exact')
    if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):
        viol.append('material state checkpoint not exact')

    er=next((x for x in ext.get('shaders',[]) if x.get('shader')==SHADER),None)
    if not er:
        viol.append('shader extraction row absent')
    else:
        for k,v in [('native_shader',NATIVE),('native_sha256',NATIVE_SHA),('gcn_sha256',GCN_SHA),('gcn_bytes',1228)]:
            if er.get(k)!=v:
                viol.append(f'{k} mismatch: {er.get(k)!r}')
        slots=[(x.get('usage_name'),x.get('api_slot'),x.get('start_register')) for x in er.get('usage',{}).get('slots',[])]
        required={('PtrResourceTable',0,12),('ImmConstBuffer',0,40),('ImmConstBuffer',12,44)}
        if not required <= set(slots):
            viol.append(f'required user-data descriptors absent: {slots!r}')

    ir=next((x for x in iu.get('shaders',[]) if x.get('shader')==SHADER),None)
    if not ir:
        viol.append('image usage row absent')
    else:
        got=[]
        for x in ir.get('instructions',[]):
            rr=x.get('resources') or []
            got.append((x.get('opcode'),rr[0].get('texture_index') if len(rr)==1 else None,x.get('dmask'),x.get('dmask_channels')))
        if got!=EXPECTED_IMAGE:
            viol.append(f'image instruction sequence mismatch: {got!r}')
        if ir.get('unmatched_image_instruction_count')!=0:
            viol.append('unmatched native image instruction')

    for needle in ANCHORS:
        if needle not in asm:
            viol.append('missing native anchor: '+needle)

    shader_mats=sorted((st.get('shader_materials',{}).get('ps',{}) or {}).get(SHADER,[]))
    if shader_mats!=sorted(MATERIALS):
        viol.append(f'scoped material set mismatch: {shader_mats!r}')

    reference=None
    for mh in MATERIALS:
        m=(st.get('materials') or {}).get(mh)
        if not m or m.get('error'):
            viol.append(f'{mh}: material unresolved')
            continue
        if m.get('material_state4_hex')!=STATE:
            viol.append(f'{mh}: state mismatch')
        if m['ps'].get('shader')!=SHADER:
            viol.append(f'{mh}: PS mismatch')
        if m['ps'].get('tfx_program_sha256')!=TFX_SHA or not m['ps'].get('tfx_disassembly',{}).get('complete'):
            viol.append(f'{mh}: TFX mismatch/incomplete')
        if texmap(m)!=TEXTURES:
            viol.append(f'{mh}: t# texture map mismatch: {texmap(m)!r}')
        vals=flat_cb(m)
        if len(vals)<62:
            viol.append(f'{mh}: short CB0 {len(vals)}')
            continue
        for idx,val in CB.items():
            if not close(vals[idx],val):
                viol.append(f'{mh}: b0[{idx}]={vals[idx]!r} expected {val!r}')
        semantic=(
            m['ps']['tfx_bytecode']['bytes_hex'],
            tuple(x['raw_hex'] for x in m['ps']['tfx_private_constants']['items']),
            tuple(x['raw_hex'] for x in m['ps']['cbuffers']['items']),
            tuple(sorted(texmap(m).items())),
            tuple(x['first_dword_hex'] for x in m['ps']['samplers']['items']),
        )
        if reference is None:
            reference=semantic
        elif semantic!=reference:
            viol.append(f'{mh}: PS semantic payload differs from family reference')

    if viol:
        out={'schema_version':1,'status':'D1_TOWER_PS_809D835C_DATAFLOW_SEMANTICS_PARTIAL','violations':viol}
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(out,indent=2)+'\n')
        print(json.dumps(out,indent=2))
        return 2

    out={
        'schema_version':1,
        'status':'D1_TOWER_PS_809D835C_DATAFLOW_SEMANTICS_EXACT',
        'violations':[],
        'shader':SHADER,
        'native_shader':NATIVE,
        'native_sha256':NATIVE_SHA,
        'gcn_sha256':GCN_SHA,
        'scope_materials':MATERIALS,
        'scope_material_count':2,
        'visible_primitive_count':24,
        'exact_inputs':{
            'texture_bindings_t0_t7':{str(k):v for k,v in TEXTURES.items()},
            'material_state4_hex':STATE,
            'tfx_program_sha256':TFX_SHA,
            'api12_camera_dependency':{'dwords':[20,21,22],'meaning':'camera/view position','evidence':'already source-closed D1 api12 contract'},
            'cb0_current_values':{str(k):v for k,v in CB.items()},
        },
        'instruction_level_equations':{
            'uv':'uv = attr3.xy; detailUV = 9*uv',
            'normal_xy':'nx = 2*t3.r + 2*t4.r - 2; ny = 2*t3.g + 2*t4.g - 2',
            'normal_z':'nz = sqrt(saturate(1-nx*nx-ny*ny))',
            'world_normal':'N = normalize(nx*attr1.xyz + ny*attr2.xyz + nz*attr0.xyz)',
            'view_vector':'V = normalize(api12[20:22] - attr4.xyz)',
            'reflection_vector':'R = 2*dot(N,V)*N - V',
            'cube_lod':'lodFloor = b0[32] + t7.a*(b0[36]-b0[32]); current b0[32]=b0[36]=6, so L=max(image_get_lod(t5,R).y,6)',
            'color_gate':'G.rgb = saturate(1 + b0[0:2] - t1.rgb)',
            'surface_product':'P.rgb = t0.rgb * G.rgb * t2.rgb',
            'surface_scaled':f'C.rgb = {K} * P.rgb',
            'palette_branch':'Q0.rgb = saturate(C.rgb-0.25) + b0[52:54]*saturate(4*C.rgb)',
            'surface_mask_mix':'M.rgb = lerp(C.rgb,Q0.rgb,t6.r)',
            'fresnel':'F = exp2(b0[42]*log2(saturate(1-dot(N,V)))); current b0[42]=1',
            'reflection_strength':'S = saturate(cube.a*(b0[44]+b0[45]*t7.a)*(b0[40]+b0[41]*F))',
            'reflection_strength_current':'S = saturate(cube.a*(0.2025+0.2695*t0.a)*(0.2248+1.1235*F)); t7 and t0 bind the same texture',
            'cube_branch':'Q.rgb = saturate(b0[48]*cube.rgb-0.25) + M.rgb*saturate(4*b0[48]*cube.rgb); current b0[48]=1.124',
            'mrt0_rgb':'mrt0.rgb = lerp(M.rgb,Q.rgb,S)',
            'mrt0_alpha':'mrt0.a = attr0.w',
            'normal_pack':'k=0.375+0.125*t7.a; mrt1.rgb=saturate(0.5+k*N); mrt1.a=b0[61]=0.02450980618596077',
        },
        'promoted_texture_semantics':{
            't0':{'tag':TEXTURES[0],'role':'surface_rgb_multiplier_alpha_reflection_and_normal_pack_control','proof':'native RGB multiplies gated color path; same resource is rebound as t7 alpha'},
            't1':{'tag':TEXTURES[1],'role':'surface_rgb_color_gate_source_and_mask_duplicate','proof':'native RGB appears inside saturate(1+b0-t1); same resource is rebound as t6.r mask'},
            't2':{'tag':TEXTURES[2],'role':'detail_uv_surface_rgb_multiplier','proof':'native RGB sampled at detailUV and multiplies t0*gate'},
            't3':{'tag':TEXTURES[3],'role':'primary_normal_xy','proof':'native xy enters signed normal reconstruction'},
            't4':{'tag':TEXTURES[4],'role':'detail_normal_xy','proof':'native xy enters same normal reconstruction at detail UV'},
            't5':{'tag':TEXTURES[5],'role':'environment_cubemap','proof':'native cube coordinate ops + image_get_lod + image_sample_l'},
            't6':{'tag':TEXTURES[6],'role':'surface_palette_mask_r','proof':'same TagHash as t1, sampled x only and used as lerp mask'},
            't7':{'tag':TEXTURES[7],'role':'surface_alpha_duplicate_control','proof':'same TagHash as t0, sampled w only for LOD/reflection/normal packing'},
        },
        'critical_correction':(
            '809D835C has no single portable base-color texture. Visible pre-reflection RGB is '
            'K * t0.rgb * t2.rgb * saturate(1+b0[0:2]-t1.rgb), then a t6.r palette branch. '
            'Binding t0 or t1 alone as Blender/glTF baseColor is semantically wrong.'
        ),
        'gates':{
            'native_pixel_color_dataflow_closed':True,
            'portable_blender_recreation_complete':False,
            'deferred_framebuffer_equivalence_closed':False,
            'runtime_external_material_permutation_selected':False,
        },
        'policy':'Exact native instruction/dataflow semantics for this PS/local-state family only. No generic PBR equivalence or runtime permutation claim is made.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','scope_material_count','visible_primitive_count','critical_correction','gates')},indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
