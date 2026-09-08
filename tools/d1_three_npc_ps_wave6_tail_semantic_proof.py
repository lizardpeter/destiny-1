#!/usr/bin/env python3
"""Fail-closed current-state/native semantic proof for D1 Tower three-NPC PS wave 6.

This closes seven small remaining shader programs against the exact pinned
three-NPC material-local state and native GCN. It does not promote generic PBR
equivalence, unresolved runtime-global buffers, or the Xur retail permutation.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

SAMPLER_2D='80AAE177'
SAMPLER_2D_SHA='2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb'
SAMPLER_CUBE='80AAE176'
SAMPLER_CUBE_SHA='0bcdaa82ea0d8588e313f29998f6c7b9166e7d28d40b13d422348d55ae5dc208'
K=4.594789981842041

F={
'809D8351':{
 'native':'809D8398','native_sha':'43cb1fdecbf778a40a45e4aa8e00d3be55cf7f6da224d60d1228fd1ba8070aa0','gcn':'0c2e796da1b0329faec6ae9e65ebb0f74202e39177f2e972a92d860d40bf67d0','bytes':720,
 'materials':['80C8864B'],'prims':2,'state':'00000000',
 'usage':[('PtrExtendedUserData',1,2),('ImmSampler',1,4),('ImmSampler',2,8),('PtrResourceTable',0,12),('ImmSampler',3,16),('ImmSampler',4,20),('ImmSampler',5,24),('ImmConstBuffer',0,28)],
 'image':[('image_sample',2,3,3),('image_sample',3,4,3),('image_sample',0,1,15),('image_sample',1,2,7),('image_sample',4,5,1)],
 'textures':{0:'80876559',1:'80AB0A49',2:'8087655A',3:'80AB0A4B',4:'80876555'},
 'samplers':[(SAMPLER_2D,SAMPLER_2D_SHA)]*5,
 'tfx_sha':'902e8371bb2fc00f416923ef17f25e5237507d3d7f2130e42a82fa10403aec99','tfx':'4900472149014722490247234903472449044725','priv':[],
 'cb':['0000e0400000e0400000000000000000','00000040000080bf000080bf000080bf','0000e0400000e0400000000000000000','00000040000080bf000080bf000080bf','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','8878113db6561a3d7e25253d0000803f','00000000000000000000000000000000','00000000dfdd5d3e00005c4200006042'],
 'anchors':['image_sample    v[8:9], v[6:9]','image_sample    v[4:5], v[4:7]','image_sample    v[12:15], v[6:9]','image_sample    v[16:18], v[2:5]','image_sample    v2, v[6:9]','v_mul_f32       v14, 0x40930885, v4','v_mul_f32       v16, 0x40930885, v8','v_mul_f32       v17, 0x40930885, v9','v_madmk_f32     v4, v4, 0xc0930885, v18','v_mac_f32       v14, v2, v4','exp             mrt0'],
 'equation':f'C=t0.rgb*t1.rgb; c=b0[28:31].rgb; B=saturate(c-0.25)+saturate(4*c)*({K}*C); mrt0.rgb=lerp({K}*C,B,t4.r)',
 'roles':{'t0':'surface RGB primary','t1':'surface RGB multiplier','t2':'primary normal XY','t3':'detail normal XY','t4':'RGB palette/mask selector scalar (r); not base color'},
},
'8087688E':{
 'native':'80876893','native_sha':'13ff22179f5e2cd6494686ab778cf630de1a8e7ba4b7c1b281252e02d13768ef','gcn':'baac1e745b26a50890eccb7549f1cba4f329c8bdcdd2825c2936c8666ec1686c','bytes':252,
 'materials':['80876865'],'prims':2,'state':'00000000',
 'usage':[('ImmConstBuffer',0,4)],'image':[],'textures':{},'samplers':[],
 'tfx_sha':'de39e4a77d2ac5c967dfa1b488259976c0f62177f3633a2ef142e770a173fda3','tfx':'4a043400034201','priv':['00000041000000410000004100000041'],
 'cb':['b4e7323c0000803f0000803f0000803f','00000000000000000000000000000000','00000000000000000000000000000000','0000803f3231713f0000704300007043'],
 'anchors':['s_buffer_load_dwordx4 s[8:11], s[4:7], 0x4','s_buffer_load_dwordx4 s[4:7], s[4:7], 0x0','v_mul_f32       v5, s4, v6','v_mul_f32       v6, s5, v7','v_mul_f32       v7, s6, v8','exp             mrt0'],
 'equation':'general mrt0.rgb=b0[0:3].rgb*b0[4:7].rgb; current b0[4:7].rgb=(0,0,0), therefore current mrt0.rgb=(0,0,0)',
 'roles':{},
},
'80876715':{
 'native':'80876764','native_sha':'45c3ed64ff4bbe58c03902bde875540f76d6de2f3377574bc86816e4a8a368cf','gcn':'cfc72eeba34802c8b8cfadd7986cf760464454e647b9a4d93781cbfdde0800b7','bytes':420,
 'materials':['808766B0'],'prims':1,'state':'00000000',
 'usage':[('PtrExtendedUserData',1,2),('ImmResource',0,4),('ImmSampler',1,12),('ImmResource',1,16),('ImmSampler',2,24),('ImmConstBuffer',0,28)],
 'image':[('image_sample',1,2,3),('image_sample',0,1,15)],'textures':{0:'80876709',1:'8087670A'},'samplers':[(SAMPLER_2D,SAMPLER_2D_SHA)]*2,
 'tfx_sha':'63e3caa08d671f3587190defea7e77363413343632d9feaae424d2de932b1b90','tfx':'4900472149014722','priv':[],
 'cb':['00000040000080bf000080bf000080bf','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000c8c7073f0000074300000843'],
 'anchors':['image_sample    v[4:5], v[2:5]','image_sample    v[6:9], v[2:5]','v_mad_f32       v3, v4, s4, v2','v_sqrt_f32      v4, v4','v_mac_f32       v3, s4, v9','exp             mrt0'],
 'equation':'mrt0.rgb=t0.rgb; t1.xy reconstructs nx=2*t1.r-1, ny=2*t1.g-1; normal packing k=0.375+0.125*t0.a',
 'roles':{'t0':'direct MRT0 RGB + normal-pack alpha','t1':'normal XY'},
},
'80876566':{
 'native':'808765B2','native_sha':'4aeb9c03f44fc76751a471feb1292cd03afd7a3ad4480c9fb85e92f3e58a6634','gcn':'7f4f43dad2fe85c636df47ce650d57c038e481f9dfd1347c51c6255a6591ace8','bytes':544,
 'materials':['80876508'],'prims':1,'state':'00000000',
 'usage':[('PtrExtendedUserData',1,2),('ImmResource',0,4),('ImmSampler',1,12),('ImmResource',1,16),('ImmSampler',2,24),('ImmConstBuffer',0,28)],
 'image':[('image_sample',1,2,3),('image_sample',0,1,7)],'textures':{0:'8087654F',1:'80876550'},'samplers':[(SAMPLER_2D,SAMPLER_2D_SHA)]*2,
 'tfx_sha':'63e3caa08d671f3587190defea7e77363413343632d9feaae424d2de932b1b90','tfx':'4900472149014722','priv':[],
 'cb':['0000404000000000000080bf000080bf','0000000000004040000080bf000080bf','20f8a63ce31cc73caa49ee3c0000803f','0000404000000000000080bf000080bf','0000000000004040000080bf000080bf','00000040000080bf000080bf000080bf'],
 'anchors':['image_sample    v[4:5], v[4:7]','image_sample    v[6:8], v[6:9]','v_max_f32       v3, s0, s0 mul:4','v_add_f32       v13, s0, v12 clamp','v_mac_f32       v13, v6, v3','exp             mrt0'],
 'equation':'c=b0[8:11].rgb; mrt0.rgb=saturate(c-0.25)+t0.rgb*saturate(4*c); current multiplier form=t0.rgb*(4*c) because current c<0.25 and 4*c<1',
 'roles':{'t0':'surface RGB entering constant tint equation','t1':'normal XY'},
},
'8087656E':{
 'native':'808765BA','native_sha':'ecc565e552b4b14e7c069ac1553f51e911b33e4dccfb66ee16559528da9ad2d5','gcn':'47f0af9375698ce8d7cf7b5545f00eb3bc946916db328dc42f70ad5210a29904','bytes':624,
 'materials':['80876510'],'prims':1,'state':'00008100',
 'usage':[('PtrExtendedUserData',1,2),('ImmResource',0,4),('ImmSampler',1,12),('ImmResource',1,16),('ImmResource',2,24),('ImmSampler',2,32),('ImmSampler',3,36),('ImmConstBuffer',0,40)],
 'image':[('image_sample',1,2,8),('image_sample',2,3,3),('image_sample',0,1,15)],'textures':{0:'8087655F',1:'80876560',2:'80876561'},'samplers':[(SAMPLER_2D,SAMPLER_2D_SHA)]*3,
 'tfx_sha':'cae4bd9028405caa08968e6f61635ccc1d31d1c01c687493e36c2a8b4629b8ee','tfx':'4900472149014722490247233c011c23220034000f23220035014206',
 'priv':['00000000000000000000803f00000000','0000003f0000803f0000803f0000803f','0000c03f0000803f0000803f0000803f'],
 'cb':['00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','a1cb3d3d5555623d906e873d0000803f','00000000000000000000000000000000','00000040000080bf000080bf000080bf','00000000000000000000000000000000','00000000dfdd5d3e00005c4200006042'],
 'anchors':['image_sample    v5, v[3:6]','s_buffer_load_dword s0, s[16:19], 0x18','v_cmp_gt_f32    vcc, 0, v5','image_sample    v[5:6], v[3:6]','image_sample    v[7:10], v[3:6]','v_max_f32       v11, s3, s3 mul:4','v_add_f32       v11, s3, v12 clamp','v_mac_f32       v13, v7, v6','exp             mrt0'],
 'equation':'coverage: discard when t1.w < b0[24] (current threshold 0); c=b0[20:23].rgb; surviving mrt0.rgb=saturate(c-0.25)+t0.rgb*saturate(4*c), reducing currently to t0.rgb*(4*c); t2.xy is normal source',
 'roles':{'t0':'surface RGB and pack-alpha','t1':'coverage/kill scalar W','t2':'normal XY'},
},
'80AA8E93':{
 'native':'80AA8E94','native_sha':'0b8b0ed287c4aef42c31b534cded1292d345429d58f77e3513e8dab797de50c1','gcn':'f2200200fba9acaf2b20fb0df75514166675d918c55cb8373c73158b51cedccf','bytes':844,
 'materials':['80876868'],'prims':3,'state':'00000000',
 'usage':[('PtrExtendedUserData',1,2),('ImmResource',0,4),('ImmSampler',1,12),('ImmResource',1,16),('ImmResource',2,24),('ImmSampler',2,32),('ImmSampler',3,36),('ImmConstBuffer',0,40),('ImmConstBuffer',12,44)],
 'image':[('image_sample',1,2,3),('image_sample',0,1,15),('image_get_lod',2,3,2),('image_sample_l',2,3,7)],
 'textures':{0:'80AAF8B2',1:'80AAF8B3',2:'80876957'},'samplers':[(SAMPLER_2D,SAMPLER_2D_SHA),(SAMPLER_2D,SAMPLER_2D_SHA),(SAMPLER_CUBE,SAMPLER_CUBE_SHA)],
 'tfx_sha':'c8c8592453040aa582d39a6872628846c44f8c68acdbaa5426b8a3d7f8b3b2e5','tfx':'490047214901472249024723','priv':[],
 'cb':['0000c03f000040bf000040bf000040bf','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','000080400000803f0000803f0000803f','000000000000803f0000803f0000803f','0000803f0000803f0000803f0000803f','0000803f0000803f0000803f0000803f','000000000000803f0000803f0000803f','0000803f0000803f0000803f0000803f','00000000000000000000000000000000','000000009b9a9a3d000098410000a041'],
 'anchors':['image_sample    v[4:5], v[2:5]','v_cubema_f32','image_sample    v[10:13], v[2:5]','image_get_lod','image_sample_l  v[14:16]','v_mad_f32       v5, v14, s0, -v2','v_mac_f32       v7, s9, v5','v_mac_f32       v10, s9, v6','v_mac_f32       v9, s9, v2','exp             mrt0'],
 'equation':'t1.xy reconstructs N; R=reflect(-V,N); cube=t2(R,L), L=max(native_lod, b0[16]+t0.a*(b0[20]-b0[16])); current b0 constants simplify final mrt0.rgb=t0.rgb+cube.rgb',
 'roles':{'t0':'direct surface RGB plus cube LOD alpha','t1':'normal XY','t2':'environment cubemap RGB'},
},
'80876537':{
 'native':'80876542','native_sha':'2a6f2862d8609c7633dd76c2febfcc638dd50153d8dd28e8ead3b43084bd4fa5','gcn':'600cb37b7fe79747fe1a0e4584e910d645e3130cf0ffd3f6c8a597abb4c49dab','bytes':580,
 'materials':['8087652A'],'prims':1,'state':'00000000',
 'usage':[('PtrExtendedUserData',1,2),('ImmSampler',1,4),('ImmSampler',2,8),('PtrResourceTable',0,12),('ImmSampler',3,16),('ImmSampler',4,20),('ImmSampler',5,24),('ImmConstBuffer',0,28)],
 'image':[('image_sample',2,3,3),('image_sample',3,4,3),('image_sample',4,5,1),('image_sample',0,1,7),('image_sample',1,2,7)],
 'textures':{0:'80876534',1:'80AB04BB',2:'80876535',3:'80AB04BC',4:'80876536'},'samplers':[(SAMPLER_2D,SAMPLER_2D_SHA)]*5,
 'tfx_sha':'902e8371bb2fc00f416923ef17f25e5237507d3d7f2130e42a82fa10403aec99','tfx':'4900472149014722490247234903472449044725','priv':[],
 'cb':['00008040000080400000000000000000','00000040000080bf000080bf000080bf','00008040000080400000000000000000','00000040000080bf000080bf000080bf','00000000000000000000000000000000','000000002625a53e0000a4420000a642'],
 'anchors':['image_sample    v[8:9], v[6:9]','image_sample    v[4:5], v[4:7]','image_sample    v2, v[6:9]','image_sample    v[12:14], v[6:9]','image_sample    v[15:17], v[15:18]','v_mul_f32       v6, v12, v15','v_mul_f32       v5, 0x40930885, v6','v_mul_f32       v6, 0x40930885, v7','v_mul_f32       v7, 0x40930885, v8','exp             mrt0'],
 'equation':f'C=t0.rgb*t1.rgb; mrt0.rgb={K}*C; t2/t3 reconstruct dual normal XY; t4.r controls only deferred normal packing k=0.375+0.125*t4.r',
 'roles':{'t0':'surface RGB primary','t1':'surface RGB multiplier','t2':'primary normal XY','t3':'detail normal XY','t4':'deferred normal-pack scalar only'},
},
}

def usage(row):
    return [(x.get('usage_name'),x.get('api_slot'),x.get('start_register')) for x in row.get('usage',{}).get('slots',[])]
def images(row):
    out=[]
    for x in row.get('instructions',[]):
        rr=x.get('resources') or [];ss=x.get('samplers') or []
        out.append((x.get('opcode'),rr[0].get('texture_index') if len(rr)==1 else None,ss[0].get('sampler_index') if len(ss)==1 else None,x.get('dmask')))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--extract-report',type=Path,required=True);ap.add_argument('--image-usage',type=Path,required=True)
    ap.add_argument('--material-state',type=Path,required=True);ap.add_argument('--disasm-dir',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    ext=json.loads(a.extract_report.read_text());iu=json.loads(a.image_usage.read_text());st=json.loads(a.material_state.read_text());viol=[]
    if ext.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT':viol.append('extract checkpoint not exact')
    if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':viol.append('image usage checkpoint not exact')
    if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):viol.append('material state checkpoint not exact')
    erby={x['shader']:x for x in ext.get('shaders',[])};irby={x['shader']:x for x in iu.get('shaders',[])}
    proofs=[]
    for sh,f in F.items():
        er=erby.get(sh);ir=irby.get(sh);asm=(a.disasm_dir/f'PS_{sh}.s').read_text()
        if not er:viol.append(f'{sh}: extraction row absent');continue
        for k,v in [('native_shader',f['native']),('native_sha256',f['native_sha']),('gcn_sha256',f['gcn']),('gcn_bytes',f['bytes'])]:
            if er.get(k)!=v:viol.append(f'{sh}: {k} mismatch {er.get(k)!r}')
        if usage(er)!=f['usage']:viol.append(f'{sh}: usage mismatch {usage(er)!r}')
        if not ir:viol.append(f'{sh}: image row absent')
        else:
            if images(ir)!=f['image']:viol.append(f'{sh}: image sequence mismatch {images(ir)!r}')
            if ir.get('unmatched_image_instruction_count')!=0:viol.append(f'{sh}: unmatched image instruction')
        for n in f['anchors']:
            if n not in asm:viol.append(f'{sh}: missing native anchor {n}')
        sm=sorted((st.get('shader_materials',{}).get('ps',{}) or {}).get(sh,[]))
        if sm!=sorted(f['materials']):viol.append(f'{sh}: exact material set mismatch {sm!r}')
        for mh in f['materials']:
            m=st.get('materials',{}).get(mh)
            if not m or m.get('error'):viol.append(f'{sh}/{mh}: missing/error material');continue
            ps=m['ps']
            if m.get('material_state4_hex')!=f['state']:viol.append(f'{sh}/{mh}: material state mismatch')
            if ps.get('shader')!=sh:viol.append(f'{sh}/{mh}: shader mismatch')
            if ps.get('tfx_program_sha256')!=f['tfx_sha'] or ps['tfx_bytecode'].get('bytes_hex')!=f['tfx'] or not ps.get('tfx_disassembly',{}).get('complete'):
                viol.append(f'{sh}/{mh}: TFX mismatch/incomplete')
            if [x['raw_hex'] for x in ps['tfx_private_constants']['items']]!=f['priv']:viol.append(f'{sh}/{mh}: TFX private constants mismatch')
            tex={int(x['texture_index']):x['texture'].upper() for x in ps['textures']['items']}
            if tex!=f['textures']:viol.append(f'{sh}/{mh}: texture map mismatch {tex!r}')
            if [x['raw_hex'] for x in ps['cbuffers']['items']]!=f['cb']:viol.append(f'{sh}/{mh}: full b0 mismatch')
            stag=[x['first_dword_hex'] for x in ps['samplers']['items']]
            ssha=[(r.get('native_sampler') or {}).get('payload_sha256') for r in ps.get('sampler_references',[])]
            if stag!=[x[0] for x in f['samplers']] or ssha!=[x[1] for x in f['samplers']]:viol.append(f'{sh}/{mh}: sampler state mismatch')
        proofs.append({'shader':sh,'native_shader':f['native'],'gcn_sha256':f['gcn'],'materials':f['materials'],'visible_primitive_count':f['prims'],'current_state_mrt0_rgb_equation':f['equation'],'promoted_texture_semantics':f['roles'],'current_material_native_color_dataflow_closed':True})
    if viol:
        out={'schema_version':1,'status':'D1_TOWER_THREE_NPC_PS_SEMANTICS_WAVE6_PARTIAL','violations':viol}
        rc=2
    else:
        total=sum(x['visible_primitive_count'] for x in proofs)
        assert total==11,total
        out={'schema_version':1,'status':'D1_TOWER_THREE_NPC_PS_SEMANTICS_WAVE6_EXACT','violations':[],'program_count':len(proofs),'visible_primitive_count':total,'proofs':proofs,
             'gates':{'current_material_native_color_dataflow_closed':True,'portable_blender_recreation_complete':False,'runtime_global_api15_closed':False},
             'policy':'Seven small shader programs / 11 visible primitives are instruction/current-state closed. This does not promote generic PBR equivalence, Xur retail permutation state, or the separate API15 runtime-global dependency used by PS 8087670E.'}
        rc=0
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in out if k not in ('proofs',)},indent=2));return rc
if __name__=='__main__':raise SystemExit(main())
