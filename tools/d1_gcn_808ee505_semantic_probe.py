#!/usr/bin/env python3
"""Promote exact instruction-level semantics for D1 PS 808EE505 / material 80D777B6.

This is deliberately shader-specific and fail-closed. It converts already exact
GCN disassembly/resource provenance into a destination-neutral renderer contract.
It does not infer roles from image appearance or texture file names.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

PS='808EE505'; VS='80D77543'; MATERIAL='80D777B6'
EXPECTED_BINDINGS={0:'808EE4FE',1:'808EE4FF',2:'808EE4FD',3:'808EE4FF',4:'808EE500',5:'80AAFB08'}


def lines(p:Path):
    return [re.sub(r'\s+',' ',x.strip()) for x in p.read_text(errors='replace').splitlines() if x.strip()]

def hits(ls,needle): return [i for i,x in enumerate(ls) if needle in x]
def one(ls,needle):
    h=hits(ls,needle)
    if len(h)!=1: raise ValueError(f'{needle!r}: expected one hit, got {len(h)}')
    return h[0]
def ordered(*xs):
    if list(xs)!=sorted(xs) or len(set(xs))!=len(xs): raise ValueError(f'instruction order drift: {xs}')

def flatten_cb(stage):
    vals=[]
    for r in stage['stage']['ps_cbuffers']['items']: vals.extend(float(x) for x in r['value'])
    return vals

def near(a,b,t=1e-6): return abs(float(a)-float(b))<=t


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--stage',type=Path,required=True); ap.add_argument('--usage',type=Path,required=True)
    ap.add_argument('--ps-disasm',type=Path,required=True); ap.add_argument('--vs-disasm',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args(); violations=[]
    try:
        sd=json.loads(a.stage.read_text()); assert sd['status']=='D1_CORPUS_MATERIAL_STAGE_EXACT'
        row=sd['materials'][0]; assert row['material']==MATERIAL and not row['violations']; s=row['stage']
        assert s['vertex_shader']==VS and s['pixel_shader']==PS
        binds={int(x['texture_index']):x['texture'] for x in s['ps_textures']['items']}; assert binds==EXPECTED_BINDINGS,(binds,EXPECTED_BINDINGS)
        assert s['material_state4_hex']=='00008100'
        cb=flatten_cb(row)
        checks={28:0.5,64:2.0,65:-1.0,80:5.0,84:0.0,88:0.4249999523162842,89:1.5750000476837158,
                92:0.75,93:0.25,94:3.0,96:0.75,100:1.0,101:1.0,109:0.5147058963775635}
        for i,v in checks.items(): assert near(cb[i],v,2e-6),(i,cb[i],v)
        ud=json.loads(a.usage.read_text()); assert ud['status']=='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' and ud['unmatched_image_instruction_count']==0
        u={x['shader']:x for x in ud['shaders']}[PS]
        assert u['used_texture_indices']==[0,1,2,3,4,5] and u['image_instruction_count']==14
        count={i:0 for i in range(6)}
        for x in u['instructions']:
            for r in x.get('resources',[]): count[int(r['texture_index'])]+=1
        assert count=={0:1,1:8,2:1,3:1,4:1,5:2},count

        ps=lines(a.ps_disasm); vs=lines(a.vs_disasm)
        p0=one(vs,'exp param0, v10, v3, v11, v20'); p1=one(vs,'exp param1, v5, v6, v4, v4')
        p2=one(vs,'exp param2, v7, v12, v13, v8'); p3=one(vs,'exp param3, v14, v15, v9, v8'); p4=one(vs,'exp param4, v0, v1, v2, v8'); ordered(p0,p1,p2,p3,p4)
        uvx=one(vs,'v_mac_f32 v14, s8, v8'); uvy=one(vs,'v_mac_f32 v15, s8, v9'); assert uvx<p3 and uvy<p3
        cross0=one(vs,'v_mad_f32 v7, v3, v4, -v7'); cross1=one(vs,'v_mad_f32 v12, v11, v5, -v12'); cross2=one(vs,'v_mad_f32 v13, v10, v6, -v13')
        handed=one(vs,'v_mul_f32 v7, v19, v7'); assert cross0<handed<p2 and cross1<handed and cross2<handed
        av4=one(ps,'v_interp_p2_f32 v3, v1, attr4.z'); view_sub=one(ps,'v_sub_f32 v3, s18, v3'); view_rsq=one(ps,'v_rsq_clamp_f32 v6, v6'); assert av4<view_sub<view_rsq

        t3=one(ps,'image_sample_d v34, v[35:38], s[24:31], s[32:35]'); loop_back=one(ps,'s_branch .L648_0')
        t4=one(ps,'image_sample v[18:19], v[16:19], s[24:31], s[32:35] dmask:3'); t0=one(ps,'image_sample v[20:23], v[16:19], s[36:43], s[4:7] dmask:15'); assert t3<loop_back<t4<t0

        c2=one(ps,'s_buffer_load_dwordx2 s[0:1], s[20:23], 0x40'); nx=one(ps,'v_mad_f32 v17, v18, s0, v16'); ny=one(ps,'v_mac_f32 v16, s0, v19')
        nz2=one(ps,'v_add_f32 v18, -v18, 1.0 clamp'); nz=one(ps,'v_sqrt_f32 v18, v18')
        basis0=one(ps,'v_mac_f32 v19, v18, v2'); basis1=one(ps,'v_mac_f32 v21, v18, v9'); basis2=one(ps,'v_mac_f32 v16, v18, v12'); ordered(t4,c2,nx,ny,nz2,nz,basis0,basis1,basis2)

        t1_samples=[i for i,x in enumerate(ps) if 'image_sample ' in x and 's[24:31], s[8:11]' in x and any(f'v{d}' in x for d in (15,26,7,13,36,34,32,30))]
        assert len(t1_samples)==8,t1_samples
        exp_att=one(ps,'v_exp_f32 v7, -v13 clamp'); mulr=one(ps,'v_mul_f32 v26, v20, v7'); mulg=one(ps,'v_mul_f32 v13, v21, v7'); mulb=one(ps,'v_mul_f32 v15, v22, v7'); mula=one(ps,'v_mul_f32 v20, v23, v7')
        assert max(t1_samples)<exp_att<mulr<mulg<mulb<mula

        t2=one(ps,'image_sample v16, v[16:19], s[4:11], s[16:19]'); th=one(ps,'s_buffer_load_dword s0, s[20:23], 0x1c')
        sub=one(ps,'v_subrev_f32 v16, s0, v16'); cmpi=one(ps,'v_cmp_gt_f32 vcc, 0, v16'); kill=one(ps,'s_andn2_b64 s[48:49], s[48:49], vcc')
        restore=one(ps,'s_mov_b64 exec, s[48:49]'); mrt0=one(ps,'exp mrt0, v1, v1, v0, v0 done compr vm'); ordered(t2,th,sub,cmpi,kill,restore,mrt0)

        cube_ma=one(ps,'v_cubema_f32 v3, v12, v14, v10'); getlod=one(ps,'image_get_lod v5, v[16:19], s[4:11], s[0:3] dmask:2')
        lod_a=one(ps,'v_mad_f32 v10, v20, s13, v10 clamp'); lodmax=one(ps,'v_max_f32 v19, v10, v5'); samplel=one(ps,'image_sample_l v[3:6], v[16:19], s[4:11], s[0:3] dmask:15'); ordered(cube_ma,getlod,lod_a,lodmax,samplel)

        dot0=one(ps,'v_mul_f32 v8, v8, v9'); dot1=one(ps,'v_mac_f32 v8, v10, v11'); dot2=one(ps,'v_mac_f32 v8, v14, v2')
        reflect_scale=one(ps,'v_max_f32 v10, v8, v8 mul:2'); one_minus=one(ps,'v_add_f32 v8, -v8, 1.0 clamp'); logi=one(ps,'v_log_f32 v8, v8')
        powmul=one(ps,'v_mul_f32 v8, s2, v8'); expi=one(ps,'v_exp_f32 v8, v8'); fmac=one(ps,'v_mac_f32 v12, s1, v8'); ordered(dot0,dot1,dot2,reflect_scale,cube_ma,one_minus,logi,powmul,expi,fmac)

        envr=one(ps,'v_mul_f32 v3, s3, v3'); envg=one(ps,'v_mul_f32 v4, s3, v4'); envb=one(ps,'v_mul_f32 v5, s3, v5'); enva=one(ps,'v_mul_f32 v6, v6, v12')
        cr=one(ps,'v_mad_f32 v10, v26, s4, v12'); cg=one(ps,'v_mad_f32 v14, v13, s4, v12'); cbv=one(ps,'v_mac_f32 v12, s4, v15')
        er=one(ps,'v_mul_f32 v3, v6, v3'); eg=one(ps,'v_mul_f32 v4, v6, v4'); eb=one(ps,'v_mul_f32 v5, v6, v5')
        outr=one(ps,'v_mad_f32 v7, v10, v3, v26'); outg=one(ps,'v_mac_f32 v13, v14, v4'); outb=one(ps,'v_mac_f32 v15, v12, v5'); ordered(samplel,enva,envr,envg,envb,cr,cg,cbv,er,eg,eb,outr,outg,outb,mrt0)

        a0=one(ps,'v_interp_p1_f32 v0, v0, attr0.w'); a1=one(ps,'v_interp_p2_f32 v0, v1, attr0.w'); packa=one(ps,'v_cvt_pkrtz_f16_f32 v0, v15, v0'); ordered(a0,a1,packa,mrt0)
        encx=one(ps,'v_madak_f32 v2, v8, v2, 0x3f000000'); ency=one(ps,'v_madak_f32 v6, v8, v11, 0x3f000000'); encz=one(ps,'v_madak_f32 v8, v8, v9, 0x3f000000')
        load109=one(ps,'s_buffer_load_dword s0, s[20:23], 0x6d'); mrt1=one(ps,'exp mrt1, v1, v1, v2, v2 compr'); ordered(encx,ency,encz,load109,mrt1)

        contract={
          'shader':PS,'vertex_shader':VS,'material':MATERIAL,
          'material_state4':{'raw':'00008100','blend_override':None,'rasterizer_selector_raw':'0x81','rasterizer_index_candidate':1},
          'bindings':{f't{i}':h for i,h in EXPECTED_BINDINGS.items()},
          'vertex_to_pixel':{
            'attr0_xyz':'normalized primary surface-basis vector','attr0_w':'source vertex scalar passed unchanged to MRT0 alpha',
            'attr1_xyz':'second surface-basis vector','attr2_xyz':'cross-product basis vector multiplied by source handedness scalar',
            'attr3_xy':'affine-transformed source 2D texture coordinates','attr4_xyz':'position-like vector subtracted from a shader constant and normalized into view direction'},
          'texture_semantics':{
            't0':{'role':'PRIMARY_RGBA_COEFFICIENT_SOURCE','proof':'RGBA sample becomes P; all P.rgb enter MRT0 RGB and P.a controls cubemap LOD / MRT1 normal encoding scale.'},
            't1':{'role':'MULTITAP_SCALAR_ATTENUATION_FIELD','proof':'Eight scalar samples around the post-parallax coordinates are reduced through max/exp and multiply all four P channels.'},
            't2':{'role':'HARD_DISCARD_SCALAR_FIELD','threshold':cb[28],'discard_when':'sample > threshold','survive_when':'sample <= threshold','proof':'comparison removes matching lanes from saved export exec mask.'},
            't3':{'role':'ITERATIVE_VIEW_DEPENDENT_COORDINATE_DISPLACEMENT_FIELD','same_texture_as_t1':True,'proof':'scalar image_sample_d occurs inside a back-edge loop and changes coordinates later used by t4/t0.'},
            't4':{'role':'TANGENT_SPACE_NORMAL_XY','decode':'x=2*sample.x-1; y=2*sample.y-1; z=sqrt(saturate(1-x*x-y*y)); transform by attr1/attr2/attr0 basis'},
            't5':{'role':'REFLECTION_CUBEMAP','proof':'reflection-vector cube coordinate generation + image_get_lod + image_sample_l; sampled RGBA contributes to final MRT0 RGB.'}},
          'main_color_equation':{
            'P':'sample(t0, displaced_uv), conditionally multiplied by t1-derived attenuation on the native branch',
            'D':'dot(view_direction, reconstructed_normal)','F':f'{cb[92]:.9g} + {cb[93]:.9g} * pow(saturate(1-D), {cb[94]:.9g})',
            'reflection_vector':'max(D,2*D)*reconstructed_normal - view_direction',
            'cubemap_lod_control':f'max(hardware_lod, lerp({cb[84]:.9g}, {cb[80]:.9g}, saturate(P.a*{cb[89]:.9g}+{cb[88]:.9g})))',
            'mrt0_rgb':f'P.rgb + (P.rgb*{cb[100]:.9g}+{cb[101]:.9g}) * (cube.rgb*{cb[96]:.9g}) * (cube.a*F)','mrt0_alpha':'attr0.w'},
          'mrt1':{'rgb':'saturate(0.5 + reconstructed_normal * (0.375 + 0.125*P.a))','alpha':cb[109]},
          'portable_consequence':{'ordinary_opaque_basecolor_is_invalid':True,'native_hard_discard_required':True,
            'portable_mask_proxy':'alpha = 1 when t2 <= 0.5 else 0; direct t2-as-alpha is inverted relative to native lane rejection',
            'native_parallax_required_for_exact_uv':True,'native_tangent_normal_required':True,'native_reflection_cubemap_required':True}}
    except Exception as ex:
        violations.append(repr(ex)); contract=None
    out={'schema_version':1,'status':'D1_808EE505_SEMANTIC_CONTRACT_EXACT' if contract and not violations else 'D1_808EE505_SEMANTIC_CONTRACT_PARTIAL','contract':contract,'violations':violations,
         'policy':'Every promoted role is tied to exact instruction order, exact t# resource provenance and exact material cbuffer values. Human appearance and filename heuristics are excluded. The contract is shader-specific; a generic GCN SSA/CFG lifter remains a separate next step.'}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2)); return 0 if not violations else 2
if __name__=='__main__': raise SystemExit(main())
