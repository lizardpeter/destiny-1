#!/usr/bin/env python3
"""Fail-closed native dataflow proof for Tower spawned-NPC PS 809D8362.

This proof closes the exact pixel-shader arithmetic for current retail material
80C88638 while keeping its two TFX-produced constant vectors (c0 and c17) as
explicit runtime inputs. The TFX program structurally writes those exact
targets, but the upstream Frame/curve producer semantics are not renamed or
frozen to the serialized zero defaults here.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

SHADER = '809D8362'
NATIVE = '809D83A9'
NATIVE_SHA = 'ec3a31cc2227e3193603a1d30c520880137c7e87b495186aa95a5eb23f7b0054'
GCN_SHA = '33317570362c7e85dd088259d1f274c215aa7e863070af722bdb1a754a0f35aa'
MATERIAL = '80C88638'
STATE = '00000000'
TFX_SHA = '66a31f0aadb49de0029eaa58d28ad838cc05c7a696f5393875f92c883fa193db'
TEXTURES = {
    0:'80AB04CD',
    1:'80C8866C',
    2:'80C8866D',
    3:'80AB04C1',
    4:'80AA820A',
    5:'80C8866E',
}
SAMPLERS = ['80AAE177','80AAE177','80AAE177','80AAE177','80AAE176','80AAE177']
SAMPLER_SHAS = [
    '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
    '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
    '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
    '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
    '0bcdaa82ea0d8588e313f29998f6c7b9166e7d28d40b13d422348d55ae5dc208',
    '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
]
EXPECTED_IMAGE = [
    ('image_sample',1,15,'xyzw'),
    ('image_sample',2,3,'xy'),
    ('image_sample',3,3,'xy'),
    ('image_sample',0,7,'xyz'),
    ('image_sample',5,1,'x'),
    ('image_get_lod',4,2,'y'),
    ('image_sample_l',4,15,'xyzw'),
]
EXPECTED_USAGE = [
    ('PtrExtendedUserData',1,2),
    ('ImmSampler',1,4),
    ('ImmSampler',2,8),
    ('PtrResourceTable',0,12),
    ('ImmSampler',3,16),
    ('ImmSampler',4,20),
    ('ImmSampler',5,24),
    ('ImmSampler',6,28),
    ('ImmConstBuffer',0,32),
    ('ImmConstBuffer',12,36),
]
CB = {
    4:4.0, 5:4.0,
    8:2.0, 9:-1.0,
    12:4.0, 13:4.0,
    16:2.0, 17:-1.0,
    32:0.0, 36:0.0,
    40:1.0, 41:1.0,
    44:0.0, 45:0.0, 46:0.0,
    48:-1.5649452209472656, 49:1.0,
    52:0.06020631641149521,
    53:0.082128144800663,
    54:0.09552287310361862,
    68:0.0, 69:0.0, 70:0.0, 71:0.0,
    81:0.028431374579668045,
    85:0.08725490421056747,
}
ANCHORS = [
    'image_sample    v[6:9], v[4:7]',
    'image_sample    v[10:11], v[4:7]',
    'v_cmp_gt_f32    s[8:9], v5, 1.0',
    's_buffer_load_dwordx4 s[20:23], s[16:19], 0x0',
    'v_mad_f32       v6, v6, v15, v20',
    'image_sample    v[12:13], v[12:15]',
    'image_sample    v[11:13], v[16:19]',
    'image_sample    v3, v[4:7]',
    's_buffer_load_dword s4, s[16:19], 0x55',
    's_buffer_load_dword s4, s[16:19], 0x51',
    's_buffer_load_dwordx4 s[4:7], s[4:7], 0x1c',
    'v_cubema_f32    v2, v21, v22, v14',
    'image_get_lod   v18, v[21:24]',
    'image_sample_l  v[20:23], v[21:24]',
    'v_mul_f32       v2, v6, v11',
    'v_mul_f32       v14, 0x40930885, v2',
    'v_madmk_f32     v2, v2, 0xc0930885, v24',
    'v_mad_f32       v11, -s6, v2, v11 clamp',
    'v_mac_f32       v14, v6, v5',
    'v_mac_f32       v14, s0, v11',
    'exp             mrt1',
    'exp             mrt0',
]

def flat_cb(m):
    return [float(v) for row in m['ps']['cbuffers']['items'] for v in row['value']]

def texmap(m):
    return {int(x['texture_index']):x['texture'].upper() for x in m['ps']['textures']['items']}

def close(a,b,eps=2e-7):
    return math.isclose(float(a),float(b),rel_tol=0.0,abs_tol=eps)

def main() -> int:
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

    er=next((x for x in ext.get('shaders',[]) if x.get('shader')==SHADER),None)
    if ext.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or not er:
        viol.append('exact shader extraction missing')
    else:
        for k,v in [('native_shader',NATIVE),('native_sha256',NATIVE_SHA),('gcn_sha256',GCN_SHA),('gcn_bytes',1328)]:
            if er.get(k)!=v: viol.append(f'{k} mismatch: {er.get(k)!r}')
        usage=[(x.get('usage_name'),x.get('api_slot'),x.get('start_register')) for x in er.get('usage',{}).get('slots',[])]
        if usage!=EXPECTED_USAGE: viol.append(f'user-data usage mismatch: {usage!r}')

    ir=next((x for x in iu.get('shaders',[]) if x.get('shader')==SHADER),None)
    if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or not ir:
        viol.append('exact image-resource map missing')
    else:
        seq=[]
        for x in ir.get('instructions',[]):
            rr=x.get('resources') or []
            seq.append((x.get('opcode'),rr[0].get('texture_index') if len(rr)==1 else None,x.get('dmask'),x.get('dmask_channels')))
        if seq!=EXPECTED_IMAGE: viol.append(f'image sequence mismatch: {seq!r}')
        if ir.get('unmatched_image_instruction_count')!=0:
            viol.append('unmatched native image instruction')

    if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):
        viol.append('material-state checkpoint not exact')
    m=(st.get('materials') or {}).get(MATERIAL)
    if not m or m.get('error'):
        viol.append('source material unresolved')
    else:
        ps=m['ps']
        if m.get('material_state4_hex')!=STATE: viol.append('material state mismatch')
        if ps.get('shader')!=SHADER: viol.append('pixel shader mismatch')
        if ps.get('tfx_program_sha256')!=TFX_SHA or not ps.get('tfx_disassembly',{}).get('complete'):
            viol.append('TFX program mismatch/incomplete')
        ops=ps.get('tfx_disassembly',{}).get('ops',[])
        targets=[x.get('d1_unk42_u8') for x in ops if x.get('name')=='Unk42']
        if targets!=[0,17]: viol.append(f'TFX output targets mismatch: {targets!r}')
        externs=[x for x in ops if 'extern_name' in x]
        if externs: viol.append(f'809D8362 TFX unexpectedly gained extern dependencies: {externs!r}')
        if texmap(m)!=TEXTURES: viol.append(f'texture map mismatch: {texmap(m)!r}')
        if [x['first_dword_hex'] for x in ps['samplers']['items']]!=SAMPLERS:
            viol.append('sampler-tag sequence mismatch')
        got_shas=[(x.get('native_sampler') or {}).get('payload_sha256') for x in ps.get('sampler_references',[])]
        if got_shas!=SAMPLER_SHAS: viol.append('native sampler descriptor sequence mismatch')
        vals=flat_cb(m)
        for i,v in CB.items():
            if i>=len(vals) or not close(vals[i],v):
                viol.append(f'b0[{i}] mismatch: {vals[i] if i<len(vals) else None!r} expected {v!r}')

    for needle in ANCHORS:
        if needle not in asm: viol.append('missing native anchor: '+needle)

    if viol:
        out={'schema_version':1,'status':'D1_TOWER_SPAWNED_PS_809D8362_NATIVE_DATAFLOW_PARTIAL','violations':viol}
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(out,indent=2)+'\n')
        print(json.dumps(out,indent=2))
        return 2

    out={
      'schema_version':1,
      'status':'D1_TOWER_SPAWNED_PS_809D8362_NATIVE_DATAFLOW_EXACT',
      'violations':[],
      'shader':SHADER,
      'native_shader':NATIVE,
      'native_sha256':NATIVE_SHA,
      'gcn_sha256':GCN_SHA,
      'source_material':MATERIAL,
      'spawned_triangle_impact_for_source_pair':21300,
      'aggregate_spawned_pixel_shader_triangle_impact':32028,
      'exact_inputs':{
        'texture_bindings':{str(k):v for k,v in TEXTURES.items()},
        'material_state4_hex':STATE,
        'tfx_program_sha256':TFX_SHA,
        'tfx_output_targets':[0,17],
        'tfx_producer_contract':{
          'bytecode_hex':m['ps']['tfx_bytecode'].get('bytes_hex',''),
          'private_constants':[x.get('value') for x in m['ps']['tfx_private_constants'].get('items',[])],
          'ops':m['ps']['tfx_disassembly'].get('ops',[]),
          'extern_histogram':{},
          'external_vector4_container':m['ps'].get('external_vector4_container'),
          'vector_storage_relation':m['ps'].get('vector_storage_relation'),
          'proof':'Exact retail material bytes and the D1 material-state decoder; no producer semantic names are added here.',
        },
        'tfx_output_semantics':{
          'c0':'runtime-produced vector consumed by the attr3.y<=1 surface-factor branch',
          'c17':'runtime-produced vector whose RGB drives the later palette branch',
        },
        'api12_dependency':'camera/view position loaded from API12 +0x1c',
        'current_material_b0_values':{str(k):v for k,v in CB.items()},
      },
      'instruction_level_equations':{
        'base_uv':'uv=attr3.xy',
        'surface_factor_pre_tfx':'S=sample(t1,uv)',
        'surface_factor_branch':'if uv.y<=1: S = saturate(c0-0.25) + S*saturate(4*c0), componentwise; if uv.y>1: S is unchanged',
        'normal_detail_uv':'uvN=(b0[14]+b0[12]*uv.x, b0[15]+b0[13]*uv.y); current uvN=4*uv',
        'normal_xy':'nx=b0[8]*t2.r+b0[16]*t3.r+b0[9]+b0[17]; ny=b0[8]*t2.g+b0[16]*t3.g+b0[9]+b0[17]; current nx=2*t2.r+2*t3.r-2 and ny=2*t2.g+2*t3.g-2',
        'normal_z':'nz=sqrt(saturate(1-nx*nx-ny*ny))',
        'world_normal':'N=normalize(nx*attr1.xyz+ny*attr2.xyz+nz*attr0.xyz)',
        'surface_uv':'uv0=(b0[6]+b0[4]*uv.x, b0[7]+b0[5]*uv.y); current uv0=4*uv',
        'surface_product':'C=S.rgb*sample(t0,uv0).rgb',
        'view_vector':'V=normalize(api12_camera_position-attr4.xyz)',
        'reflection_vector':'R=2*dot(N,V)*N-V',
        'cube_lod_floor':'Lfloor=b0[32]+S.a*(b0[36]-b0[32]); current Lfloor=0',
        'cube_sample':'cube=sample_l(t4,R,max(image_get_lod(t4,R).y,Lfloor))',
        'palette_from_c17':'P.rgb=saturate(c17.rgb-0.25)+saturate(4*c17.rgb)*(4.594789981842041*C.rgb)',
        'surface_palette_mix':'M.rgb=lerp(4.594789981842041*C.rgb,P.rgb,t5.r)',
        'view_response':'F2=(1-dot(N,V))^2; W=saturate((b0[48]+b0[49])-b0[48]*F2)',
        'cube_branch':'Q.rgb=b0[44:46]+M.rgb+cube.rgb*cube.a*(b0[41]+b0[40]*M.rgb)',
        'mrt0_rgb':'mrt0.rgb=Q.rgb+b0[52:54]*W',
        'mrt0_alpha':'mrt0.a=attr0.w',
        'mrt1_rgb':'k=0.375+b0[71]*S.a; mrt1.rgb=saturate(0.5+k*N)',
        'mrt1_alpha':'mrt1.a=b0[85] when uv.y>1, otherwise b0[81]',
      },
      'promoted_texture_semantics':{
        't0':{'tag':TEXTURES[0],'role':'surface_rgb_multiplier','proof':'RGB multiplies the post-c0 t1 surface factor before both palette and cube branches'},
        't1':{'tag':TEXTURES[1],'role':'surface_rgba_factor_with_runtime_c0_palette_branch','proof':'RGBA is directly transformed by c0 on uv.y<=1 and its alpha also controls cube LOD/normal packing'},
        't2':{'tag':TEXTURES[2],'role':'primary_normal_xy','proof':'XY enters exact normal reconstruction'},
        't3':{'tag':TEXTURES[3],'role':'detail_normal_xy','proof':'XY at transformed UV enters the same normal reconstruction'},
        't4':{'tag':TEXTURES[4],'role':'environment_cubemap_rgba','proof':'native cube coordinate ops, image_get_lod and image_sample_l feed MRT0'},
        't5':{'tag':TEXTURES[5],'role':'surface_palette_mix_scalar_r','proof':'native x sample is the exact lerp factor between scaled surface product and c17 palette branch'},
      },
      'runtime_frontiers':{
        'tfx_c0_producer_semantics_complete':False,
        'tfx_c17_producer_semantics_complete':False,
        'native_pixel_dataflow_complete_given_tfx_outputs':True,
        'portable_material_recreation_complete':False,
        'deferred_framebuffer_equivalence_closed':False,
      },
      'policy':'The native pixel-shader arithmetic is exact for current retail material 80C88638. c0 and c17 remain explicit runtime-produced TFX inputs; they are not replaced with serialized zero defaults or guessed high-level material labels.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
      'status':out['status'],
      'shader':SHADER,
      'source_material':MATERIAL,
      'runtime_frontiers':out['runtime_frontiers'],
      'violations':[],
    },indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
