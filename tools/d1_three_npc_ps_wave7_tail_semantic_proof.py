#!/usr/bin/env python3
"""Fail-closed current-state/native semantic proof for D1 Tower three-NPC PS wave 7.

Closes the final four non-API15 shader programs in the original three-NPC
heuristic-forbidden material frontier. GCN V_SUBREV_F32 is interpreted per AMD
GCN ISA as D = S1 - S0; this matters for the palette lerps in 808762E1 and the
reflection/LOD arithmetic in 8087645C/8087670C.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

K=4.594789981842041
S2='80AAE177'; S2SHA='2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb'
SC='80AAE176'; SCSHA='0bcdaa82ea0d8588e313f29998f6c7b9166e7d28d40b13d422348d55ae5dc208'

F={
 '8087656A':{
  'native':'808765B6','native_sha':'32e754efc9ac6b2333d2eeb18751081b24ecafca2208ba59e8c92e9061cd8057',
  'gcn':'48ed81ed1cfef67930cb813e45304b4f786b49bf45d44d33fc1cbba535320135','bytes':1048,
  'materials':['8087650C','80876645'],'prims':2,'state':'00008100',
  'usage':[('PtrExtendedUserData',1,2),('ImmSampler',1,4),('ImmSampler',2,8),('PtrResourceTable',0,12),('ImmSampler',3,16),('ImmSampler',4,20),('ImmSampler',5,24),('ImmConstBuffer',0,28),('ImmConstBuffer',12,32)],
  'image':[('image_sample',0,1,15),('image_sample',2,3,3),('image_sample',3,4,3),('image_get_lod',4,5,2),('image_sample',1,2,7),('image_sample_l',4,5,15)],
  'textures':{0:'8087655D',1:'80AB04BB',2:'8087655E',3:'80AB04BC',4:'80AACC28'},
  'samplers':[(S2,S2SHA)]*4+[(SC,SCSHA)],
  'tfx_sha':'fb53cc8c0825227794144bb49c931c72a887a6ec7e5bad889129aa37cfcadc31',
  'tfx':'49004721490147224902472349034724490447253c011c23220034000f2322004206',
  'priv':['00000000000000000000803f00000000'],
  'cb':['00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','0000e0400000e0400000000000000000','00000000000000000000000000000000','00000040000080bf000080bf000080bf','0000e0400000e0400000000000000000','cdcccc3fcdcc4cbfcdcc4cbfcdcc4cbf','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','0000c0400000803f0000803f0000803f','0000c0400000803f0000803f0000803f','f931663ed9ce8f3f0000803f00000000','295c4f3ee8fb893e0000000000000000','3bdf8f3f000000000000000000000000','00000000000000000000000000000000','00000000dfdd5d3e00005c4200006042'],
  'anchors':['v_cmp_gt_f32    vcc, 0, v11','v_subrev_f32    v11, s0, v10','image_sample    v[17:19]','image_sample_l  v[20:23]','v_mul_f32       v6, v7, v17','v_mul_f32       v14, 0x40930885, v6','v_madmk_f32     v6, v6, 0xc0930885, v20','v_mac_f32       v14, v4, v6','exp             mrt0'],
  'equations':{
   'coverage':'discard when t0.a < b0[24]; current threshold b0[24]=0',
   'normal':'nx=2*t2.r+1.6*t3.r-1.8; ny=2*t2.g+1.6*t3.g-1.8; N=normalize(TBN*(nx,ny,sqrt(saturate(1-nx^2-ny^2))))',
   'surface':'C=t0.rgb*t1.rgb; Cs=K*C',
   'view':'V=normalize(api12.camera_position-attr4.xyz); R=reflect(-V,N); F=saturate(1-dot(N,V))',
   'cube_lod':'L=max(native_lod(t4,R), 6 + t0.a*(6-6)); current L=max(native_lod(t4,R),6)',
   'reflection_strength':'S=saturate(t4.a*(0.20250000059604645+0.2695000171661377*t0.a)*(0.2248000055551529+1.1234999895095825*F))',
   'cube_branch':'Q=saturate(1.1239999532699585*t4.rgb-0.25)+Cs*saturate(4*1.1239999532699585*t4.rgb)',
   'mrt0_rgb':'mrt0.rgb=lerp(Cs,Q,S)',
  },
  'roles':{'t0':'surface RGB primary + coverage/LOD/pack alpha','t1':'surface RGB multiplier','t2':'primary normal XY','t3':'detail normal XY','t4':'environment cubemap RGBA'}
 },
 '8087645C':{
  'native':'80876469','native_sha':'a5332139c498dace61fe93b0673c6606c210a350fc389556d89ed860c1cdee9c',
  'gcn':'b4e0a596f4b3fcb8d910768b009613905c12754d81a83ab97949894fb6d7e5b9','bytes':956,
  'materials':['8087642C'],'prims':1,'state':'00000000',
  'usage':[('PtrExtendedUserData',1,2),('ImmSampler',1,4),('ImmSampler',2,8),('PtrResourceTable',0,12),('ImmSampler',3,16),('ImmSampler',4,20),('ImmSampler',5,24),('ImmSampler',6,28),('ImmConstBuffer',0,32),('ImmConstBuffer',12,36)],
  'image':[('image_sample',1,2,3),('image_sample',2,3,3),('image_sample',0,1,15),('image_get_lod',3,4,2),('image_sample_l',3,4,15),('image_sample',4,5,4),('image_sample',5,6,1)],
  'textures':{0:'80876456',1:'80876457',2:'80AB04C1',3:'80AB04CF',4:'808768AD',5:'80876987'},
  'samplers':[(S2,S2SHA)]*3+[(SC,SCSHA)]+[(S2,S2SHA)]*2,
  'tfx_sha':'bf2e53212baa812a8702f59c61453adfc501870c863f74e6f1f42a8fc4b695c0','tfx':'490047214901472249024723490347244904472549054726','priv':[],
  'cb':['00000040000080bf000080bf000080bf','0000004000000000000000bf000000bf','0000000000000040000000bf000000bf','00000040000080bf000080bf000080bf','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','0000803f0000803f0000803f0000803f','000000000000803f0000803f0000803f','6666a6bf333313400000803f0000803f','00000041000000410000000000000000','00000000cdcccc3e0000a04000000000','00000040000080bf0000000000000000','c2f5683f15aec73e6666a63f6666a63f','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000d6d4543d0000504100006041'],
  'anchors':['v_subrev_f32    v15, s5, v15','image_sample    v[17:20]','image_get_lod','image_sample_l  v[21:24]','image_sample    v2, v[6:9]','image_sample    v3, v[3:6]','v_log_f32','v_exp_f32','v_mul_f32       v2, v2, v3','v_mac_f32       v17, v5, v7','exp             mrt0'],
  'equations':{
   'normal':'nx=2*t1.r+2*t2.r-2; ny=2*t1.g+2*t2.g-2; t2 is sampled at transformed UV (2*u-0.5,2*v-0.5)',
   'view':'V=normalize(api12.camera_position-attr4.xyz); R=reflect(-V,N); F=saturate(1-dot(N,V))^5',
   'cube_lod':'g=saturate(2.3*t0.a-1.3); SUBREV gives (b0[40]-b0[36])=0-1=-1, therefore Lfloor=1-g; L=max(native_lod(t3,R),1-g)',
   'detail':'M=t4.b*t5.r',
   'reflection_strength':'S=M*(2-t0.a)*0.4*F',
   'mrt0_rgb':'mrt0.rgb=t0.rgb+(0.39+0.91*t0.rgb)*t3.rgb*S',
  },
  'roles':{'t0':'direct surface RGB + LOD/pack alpha','t1':'primary normal XY','t2':'detail normal XY','t3':'environment cubemap RGB','t4':'detail-mask blue channel','t5':'detail-mask red channel'}
 },
 '8087670C':{
  'native':'8087675B','native_sha':'cf89e633113024cbc40b932086b9aadd9604b99286d54531d6761dbbd2ed819f',
  'gcn':'4621f4b7d19c09deadbb92b56654a5609f426c9bf59cd3f41c892db26dbbac4c','bytes':1128,
  'materials':['808766AF','808766B4'],'prims':2,'state':'00000000',
  'usage':[('PtrExtendedUserData',1,2),('ImmSampler',1,4),('ImmSampler',2,8),('PtrResourceTable',0,12),('ImmSampler',3,16),('ImmSampler',4,20),('ImmSampler',5,24),('ImmSampler',6,28),('ImmConstBuffer',0,32),('ImmConstBuffer',12,36)],
  'image':[('image_sample',2,3,3),('image_sample',3,4,3),('image_sample',5,6,8),('image_get_lod',4,5,2),('image_sample',0,1,7),('image_sample',1,2,7),('image_sample_l',4,5,15)],
  'textures':{0:'80876706',1:'80AB0A49',2:'80876707',3:'80AB0A4B',4:'80AACC28',5:'80876708'},
  'samplers':[(S2,S2SHA)]*4+[(SC,SCSHA),(S2,S2SHA)],
  'tfx_sha':'bf2e53212baa812a8702f59c61453adfc501870c863f74e6f1f42a8fc4b695c0','tfx':'490047214901472249024723490347244904472549054726','priv':[],
  'cb':['0000e0400000e0400000000000000000','00000040000080bf000080bf000080bf','0000e0400000e0400000000000000000','9a99993f9a9919bf9a9919bf9a9919bf','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','0000c0400000803f0000803f0000803f','0000c0400000803f0000803f0000803f','00000000713daa3f7f6a7c4000000000','000000bf000020400000000000000000','0000e040000000000000000000000000','0000803fa146113f31dad13e0000803f','e0f374bf7801ac3fe0f3743fe0f3743f','ead459bfd835c2bd1a5c773e00000000','00000000000000000000000000000000','00000000eae8e83c0000e04000000041'],
  'anchors':['image_sample    v12, v[6:9]','image_get_lod','image_sample    v[17:19]','image_sample    v[20:22]','image_sample_l  v[23:26]','v_sub_f32       v2, 1.0, v13','v_log_f32','v_exp_f32','v_subrev_f32    v2, s15, v2','v_mac_f32       v10, v16, v3','v_mul_f32       v2, v10, v2','exp             mrt0'],
  'equations':{
   'normal':'nx=2*t2.r+1.2*t3.r-1.6; ny=2*t2.g+1.2*t3.g-1.6; t3 is sampled at 7x UV',
   'view':'V=normalize(api12.camera_position-attr4.xyz); d=dot(N,V); R=reflect(-V,N)',
   'cube_lod':'current b0[28]=b0[32]=6, so the t5.a interpolation collapses and L=max(native_lod(t4,R),6)',
   'surface':'C=t0.rgb*t1.rgb; Cs=K*C; t1 sampled at 7x UV',
   'fresnel':'F=saturate(1-d)^3.944000005722046',
   'reflection_strength':'S=saturate(t4.a*(-0.5+2.5*t5.a)*(1.3300000429153442*F))',
   'cube_branch':'Q=saturate(Cs-0.25)+7*t4.rgb*saturate(4*Cs)',
   'view_tint_weight':'W=saturate((-0.9568462371826172+1.343794822692871)+(0.9568462371826172*(1-d)^2))',
   'view_tint':'T=(1,0.5674839615821838,0.4098677933216095)+(-0.8509050607681274,-0.094829261302948,0.24156227707862854)*W',
   'mrt0_rgb':'mrt0.rgb=lerp(Cs,Q,S)*T',
  },
  'roles':{'t0':'surface RGB primary','t1':'surface RGB detail multiplier','t2':'primary normal XY','t3':'detail normal XY','t4':'environment cubemap RGBA','t5':'alpha/W reflection-strength control'}
 },
 '808762E1':{
  'native':'8087635C','native_sha':'72f4492cdd48ff32dc17211324e0fcf52673948737606d1f1857deb7302cb140',
  'gcn':'564ece90d384ef625046b6f374aa5ecbb310e09301aa0308a3926f93bbe82c24','bytes':1036,
  'materials':['808761C9'],'prims':2,'state':'00000000',
  'usage':[('PtrExtendedUserData',1,2),('ImmSampler',1,4),('ImmSampler',2,8),('PtrResourceTable',0,12),('ImmSampler',3,16),('ImmSampler',4,20),('ImmSampler',5,24),('ImmSampler',6,28),('ImmSampler',7,32),('ImmSampler',8,36),('ImmConstBuffer',0,40)],
  'image':[('image_sample',6,7,3),('image_sample',7,8,3),('image_sample',0,1,3),('image_sample',2,3,7),('image_sample',3,4,7),('image_sample',5,6,4),('image_sample',4,5,7),('image_sample',1,2,15)],
  'textures':{0:'80876551',1:'80876552',2:'80AB04BB',3:'80AAF8B8',4:'80AB0A52',5:'80876555',6:'80876554',7:'80AB0A50'},
  'samplers':[(S2,S2SHA)]*8,
  'tfx_sha':'b4271f54f37c62c675e1cde807efd9eec2ce7e6a49363391915d0d27dcd7bf2c','tfx':'4900472149014722490247234903472449044725490547264906472749074728','priv':[],
  'cb':['00008841000088410000000000000000','0000803f0000803f0000803f3433733e','8878113db6561a3d7e25253d0000803f','8878113db6561a3d7e25253d0000803f','c983a83c95c9b23ca64ebf3c0000803f','00000040000080bf000080bf000080bf','00008841000088410000000000000000','cdcccc3fcdcc4cbfcdcc4cbfcdcc4cbf','00000000000000000000000000000000','00000000dfdd5d3e00005c4200006042'],
  'anchors':['image_sample    v[2:3]','image_sample    v[12:14]','image_sample    v[15:17]','image_sample    v18','image_sample    v[19:21]','image_sample    v[22:25]','v_subrev_f32    v11, s4, v11','v_subrev_f32    v15, v11, v26','v_mac_f32       v11, v18, v3','v_mul_f32       v6, v22, v11','v_mul_f32       v6, 0x40930885, v6','exp             mrt0'],
  'equations':{
   'normal':'nx=2*t6.r+1.6*t7.r-1.8; ny=2*t6.g+1.6*t7.g-1.8',
   'palette_A':'A=(0.03551533818244934,0.03768035024404526,0.04031895846128464); P2=saturate(A-0.25)+t2.rgb*saturate(4*A); P3=saturate(A-0.25)+t3.rgb*saturate(4*A)',
   'palette_B':'B=(0.020570652559399605,0.021824637427926064,0.023352932184934616); P4=saturate(B-0.25)+t4.rgb*saturate(4*B)',
   'selector_chain':'C0=lerp((1,1,1),P2,t0.r); C1=lerp(C0,P3,t0.g); C2=lerp(C1,P4,t5.b)',
   'mrt0_rgb':'mrt0.rgb=K*t1.rgb*C2',
   'packing_only':'nonlinear t0.r/t0.g/t5.b/t1.a chain also drives deferred normal packing; it does not alter the closed MRT0 RGB equation',
  },
  'roles':{'t0':'two-channel palette/control selector; NOT base color','t1':'final RGB multiplier plus packing alpha','t2':'palette RGB branch A','t3':'palette RGB branch B','t4':'palette RGB branch C','t5':'blue-channel palette selector','t6':'primary normal XY','t7':'detail normal XY'}
 },
}

def usage(row):
    return [(x.get('usage_name'),x.get('api_slot'),x.get('start_register')) for x in row.get('usage',{}).get('slots',[])]
def images(row):
    out=[]
    for x in row.get('instructions',[]):
        rr=x.get('resources') or []; ss=x.get('samplers') or []
        out.append((x.get('opcode'),rr[0].get('texture_index') if len(rr)==1 else None,ss[0].get('sampler_index') if len(ss)==1 else None,x.get('dmask')))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--extract-report',type=Path,required=True);ap.add_argument('--image-usage',type=Path,required=True)
    ap.add_argument('--material-state',type=Path,required=True);ap.add_argument('--disasm-dir',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    ext=json.loads(a.extract_report.read_text()); iu=json.loads(a.image_usage.read_text()); st=json.loads(a.material_state.read_text()); viol=[]
    if ext.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT':viol.append('extract checkpoint not exact')
    if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':viol.append('image usage checkpoint not exact')
    if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):viol.append('material state checkpoint not exact')
    erby={x['shader']:x for x in ext.get('shaders',[])}; irby={x['shader']:x for x in iu.get('shaders',[])}
    proofs=[]
    for sh,f in F.items():
        er=erby.get(sh); ir=irby.get(sh); asm=(a.disasm_dir/f'PS_{sh}.s').read_text()
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
            if m.get('material_state4_hex')!=f['state']:viol.append(f'{sh}/{mh}: state mismatch')
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
        proofs.append({'shader':sh,'native_shader':f['native'],'gcn_sha256':f['gcn'],'materials':f['materials'],'visible_primitive_count':f['prims'],
                       'instruction_level_equations':f['equations'],'promoted_texture_semantics':f['roles'],'current_material_native_color_dataflow_closed':True})
    if viol:
        out={'schema_version':1,'status':'D1_TOWER_THREE_NPC_PS_SEMANTICS_WAVE7_PARTIAL','violations':viol};rc=2
    else:
        total=sum(x['visible_primitive_count'] for x in proofs); assert total==7,total
        out={'schema_version':1,'status':'D1_TOWER_THREE_NPC_PS_SEMANTICS_WAVE7_EXACT','violations':[],'program_count':4,'visible_primitive_count':total,'proofs':proofs,
             'gcn_subrev_f32_semantics':'D = S1 - S0 (AMD GCN ISA); equations above use this direction',
             'gates':{'current_material_native_color_dataflow_closed':True,'portable_blender_recreation_complete':False,'runtime_global_api15_closed':False},
             'policy':'Final four non-API15 programs / seven visible primitives are native/current-state closed. PS 8087670E remains fail-closed on runtime-global ImmConstBuffer API15. No generic PBR equivalence or Xur retail-permutation claim is made.'};rc=0
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in out if k!='proofs'},indent=2));return rc
if __name__=='__main__':raise SystemExit(main())
