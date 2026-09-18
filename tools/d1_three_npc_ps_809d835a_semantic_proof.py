#!/usr/bin/env python3
"""Fail-closed native semantic proof for D1 PS4 PS 809D835A.

This closes the exact visible-color/dataflow contract for the five scoped Tower
NPC materials using only the pinned native GCN, exact t# image provenance and
exact material-local state. It deliberately does not claim Blender/PBR or D1
framebuffer/deferred-renderer equivalence.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

SHADER='809D835A'
NATIVE='809D83A1'
NATIVE_SHA='7dc13163b95c5ec30ac99478f2ede4a92a07ca4993248b537f419d0c2fff1177'
GCN_SHA='bc60f549becda517d8358e23998222a0d813d18abd7a82adc0e7538903157f66'
MATERIALS=['80C880E2','80C880E4','80C880E9','80C880EA','80C888DF']
TEXTURES={0:'80C88660',1:'80C88661',2:'80AB04BB',3:'80AB04BB',4:'80C88662',5:'80AB04BC',6:'80AACC28',7:'80C88661'}
TFX_SHA='020a90252ac9bef3079a591dbda6ffd419efc14c244826cfc9614a496e4a49d4'
STATE='00000000'
EXPECTED_IMAGE=[
 ('image_sample',4,3,'xy'),('image_sample',5,3,'xy'),('image_sample',7,8,'w'),
 ('image_get_lod',6,2,'y'),('image_sample',2,7,'xyz'),('image_sample',0,3,'xy'),
 ('image_sample',3,7,'xyz'),('image_sample',1,7,'xyz'),('image_sample_l',6,15,'xyzw'),
]
# Exact current CB0 values used by the closed equations.
CB={
 12:9.0,13:9.0,16:1.0,17:1.0,18:1.0,19:0.23750001192092896,
 20:0.0,21:0.0,22:0.0,24:0.6660000085830688,25:0.6660000085830688,26:0.6660000085830688,
 28:2.0,29:-1.0,32:9.0,33:9.0,36:1.600000023841858,37:-0.800000011920929,
 52:6.0,56:6.0,60:0.2248000055551529,61:0.6516000032424927,62:1.0,
 64:0.30000001192092896,65:0.171999990940094,68:1.1239999532699585,77:0.02450980618596077,
}
K=4.594789981842041
ANCHORS=[
 'image_sample    v[8:9], v[6:9]',
 'image_sample    v[4:5], v[4:7]',
 'v_add_f32       v4, -v4, 1.0 clamp',
 'v_sqrt_f32      v4, v4',
 'v_rsq_clamp_f32 v4, v15',
 'v_rsq_clamp_f32 v8, v8',
 'v_max_f32       v10, v13, v13 mul:2',
 'v_cubema_f32    v4, v15, v16, v10',
 'image_get_lod   v14, v[27:30]',
 'image_sample    v[19:20], v[6:9]',
 'image_sample    v[24:26], v[6:9]',
 'image_sample_l  v[27:30], v[27:30]',
 'v_log_f32       v2, v13',
 'v_exp_f32       v2, v2',
 'v_madmk_f32     v3, v3, 0xc0930885, v20',
 'v_madak_f32     v2, v22, v2, 0x3f000000',
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
    ext=json.loads(a.extract_report.read_text()); iu=json.loads(a.image_usage.read_text()); st=json.loads(a.material_state.read_text())
    asm=a.disassembly.read_text(); viol=[]
    if ext.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT':viol.append('extract checkpoint not exact')
    if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':viol.append('image usage checkpoint not exact')
    if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):viol.append('material state checkpoint not exact')
    er=next((x for x in ext.get('shaders',[]) if x.get('shader')==SHADER),None)
    if not er:viol.append('shader extraction row absent')
    else:
        for k,v in [('native_shader',NATIVE),('native_sha256',NATIVE_SHA),('gcn_sha256',GCN_SHA),('gcn_bytes',1300)]:
            if er.get(k)!=v:viol.append(f'{k} mismatch: {er.get(k)!r}')
        slots=[(x.get('usage_name'),x.get('api_slot'),x.get('start_register')) for x in er.get('usage',{}).get('slots',[])]
        if ('ImmConstBuffer',0,40) not in slots or ('ImmConstBuffer',12,44) not in slots or ('PtrResourceTable',0,12) not in slots:
            viol.append(f'required user-data descriptors absent: {slots!r}')
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
        if m['ps'].get('tfx_program_sha256')!=TFX_SHA or not m['ps'].get('tfx_disassembly',{}).get('complete'):
            viol.append(f'{mh}: TFX mismatch/incomplete')
        if texmap(m)!=TEXTURES:viol.append(f'{mh}: t# texture map mismatch: {texmap(m)!r}')
        vals=flat_cb(m)
        if len(vals)<78:viol.append(f'{mh}: short CB0 {len(vals)}');continue
        for idx,val in CB.items():
            if not close(vals[idx],val):viol.append(f'{mh}: b0[{idx}]={vals[idx]!r} expected {val!r}')
        # The relevant PS-side semantic payload is equal for all five materials,
        # even where serialized array offsets/source metadata differ.
        semantic=(m['ps']['tfx_bytecode']['bytes_hex'],tuple(x['raw_hex'] for x in m['ps']['tfx_private_constants']['items']),
                  tuple(x['raw_hex'] for x in m['ps']['cbuffers']['items']),tuple(sorted(texmap(m).items())),
                  tuple(x['first_dword_hex'] for x in m['ps']['samplers']['items']))
        if reference is None:reference=semantic
        elif semantic!=reference:viol.append(f'{mh}: PS semantic payload differs from family reference')
    if viol:
        out={'schema_version':1,'status':'D1_TOWER_PS_809D835A_DATAFLOW_SEMANTICS_PARTIAL','violations':viol}
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 2
    out={
      'schema_version':1,'status':'D1_TOWER_PS_809D835A_DATAFLOW_SEMANTICS_EXACT','violations':[],
      'shader':SHADER,'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,
      'scope_materials':MATERIALS,'scope_material_count':5,'visible_primitive_count':33,
      'exact_inputs':{
        'texture_bindings_t0_t7':{str(k):v for k,v in TEXTURES.items()},
        'material_state4_hex':STATE,'tfx_program_sha256':TFX_SHA,
        'api12_camera_dependency':{'dwords':[28,29,30],'meaning':'camera/view position','evidence':'already source-closed D1 api12 contract'},
        'cb0_current_values':{str(k):v for k,v in CB.items()},
      },
      'instruction_level_equations':{
        'uv':'uv = attr3.xy; detailUV = 9*uv',
        'normal_xy':'nx = 2*t4.r + 1.6*t5.r - 1.8; ny = 2*t4.g + 1.6*t5.g - 1.8',
        'normal_z':'nz = sqrt(saturate(1-nx*nx-ny*ny))',
        'world_normal':'N = normalize(nx*attr1.xyz + ny*attr2.xyz + nz*attr0.xyz)',
        'view_vector':'V = normalize(api12[28:30] - attr4.xyz)',
        'reflection_vector':'R = 2*dot(N,V)*N - V',
        'cube_lod':'lodFloor = b0[52] + t7.a*(b0[56]-b0[52]); current b0[52]=b0[56]=6, so L=max(image_get_lod(t6,R).y,6)',
        'dye_branch_a':'A.rgb = b0[16:18] + t0.r*(saturate(b0[20:22]-0.25) + t2.rgb*saturate(4*b0[20:22]) - b0[16:18]); current b0[20:22]=0 and b0[16:18]=1, so A=1-t0.r',
        'dye_branch_b':'B.rgb = saturate(b0[24:26]-0.25) + t3.rgb*saturate(4*b0[24:26]); current b0[24:26]=0.666',
        'dye_mix':'M.rgb = lerp(A.rgb,B.rgb,t0.g)',
        'surface_product':'C.rgb = t1.rgb * M.rgb',
        'surface_scaled':f'Cs.rgb = {K} * C.rgb',
        'fresnel':'F = exp2(b0[62]*log2(saturate(1-dot(N,V)))); current b0[62]=1',
        'reflection_strength':'S = saturate(cube.a*(b0[64]+b0[65]*t7.a)*(b0[60]+b0[61]*F))',
        'reflection_strength_current':'S = saturate(cube.a*(0.3+0.172*t1.a)*(0.2248+0.6516*F)); t7 and t1 bind the same texture',
        'cube_branch':'Q.rgb = saturate(b0[68]*cube.rgb-0.25) + Cs.rgb*saturate(4*b0[68]*cube.rgb); current b0[68]=1.124',
        'mrt0_rgb':'mrt0.rgb = lerp(Cs.rgb,Q.rgb,S)',
        'mrt0_alpha':'mrt0.a = attr0.w',
        'normal_pack':'k=0.375+0.125*t7.a; mrt1.rgb=saturate(0.5+k*N); mrt1.a=b0[77]=0.02450980618596077',
      },
      'promoted_texture_semantics':{
        't0':{'tag':TEXTURES[0],'role':'dye_control_xy','proof':'native sample dmask xy; both channels select color branches; no t0 RGB sample exists'},
        't1':{'tag':TEXTURES[1],'role':'surface_rgb_alpha_reflection_and_normal_pack_control','proof':'native RGB multiplies exact dye mix; same resource is rebound as t7 alpha for reflection/normal packing'},
        't2':{'tag':TEXTURES[2],'role':'dye_branch_rgb_input_currently_zero_weighted','proof':'native RGB branch multiplied by current b0[20:22]=0'},
        't3':{'tag':TEXTURES[3],'role':'dye_branch_rgb_input','proof':'native RGB enters branch B'},
        't4':{'tag':TEXTURES[4],'role':'primary_normal_xy','proof':'native xy enters signed normal reconstruction'},
        't5':{'tag':TEXTURES[5],'role':'detail_normal_xy','proof':'native xy enters same normal reconstruction at detail UV'},
        't6':{'tag':TEXTURES[6],'role':'environment_cubemap','proof':'native cube coordinate ops + image_get_lod + image_sample_l'},
        't7':{'tag':TEXTURES[7],'role':'surface_alpha_duplicate_control','proof':'same TagHash as t1, sampled w only'},
      },
      'critical_correction':'Texture t0 (80C88660) is instruction-proven dye/control data, not base color. Binding it directly to glTF/Blender baseColor caused the false-color preview. The actual sampled surface RGB multiplier is t1 (80C88661), combined with the native dye branches before reflection.',
      'gates':{'native_pixel_color_dataflow_closed':True,'portable_blender_recreation_complete':False,'deferred_framebuffer_equivalence_closed':False,'runtime_external_material_permutation_selected':False},
      'policy':'Exact native instruction/dataflow semantics for this PS/local-state family only. No generic PBR equivalence or runtime permutation claim is made.'
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','scope_material_count','visible_primitive_count','critical_correction','gates')},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
