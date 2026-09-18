#!/usr/bin/env python3
"""Fail-closed current-state/native semantic proofs for seven remaining three-NPC PS families.

The families in this wave are intentionally grouped because each exact GCN binary
has a compact, independently readable MRT0 RGB path. Every proof is pinned to the
exact native payload SHA, GCN SHA, user-data layout, image-resource sequence,
material membership, TFX bytes, material state, texture map, sampler descriptors,
and full local b0 payload. No PBR/base-color naming is inferred beyond the exact
native equations recorded below.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

SAMPLER='80AAE177'
SAMPLER_SHA='2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb'
CUBE_SAMPLER='80AAE176'
CUBE_SAMPLER_SHA='0bcdaa82ea0d8588e313f29998f6c7b9166e7d28d40b13d422348d55ae5dc208'
K=4.594789981842041

F={
'809D8351':{
 'native':'809D8398','native_sha':'43cb1fdecbf778a40a45e4aa8e00d3be55cf7f6da224d60d1228fd1ba8070aa0','gcn':'0c2e796da1b0329faec6ae9e65ebb0f74202e39177f2e972a92d860d40bf67d0','bytes':720,'prim':2,
 'usage':[('PtrExtendedUserData',1,2),('ImmSampler',1,4),('ImmSampler',2,8),('PtrResourceTable',0,12),('ImmSampler',3,16),('ImmSampler',4,20),('ImmSampler',5,24),('ImmConstBuffer',0,28)],
 'image':[('image_sample',2,3,3),('image_sample',3,4,3),('image_sample',0,1,15),('image_sample',1,2,7),('image_sample',4,5,1)],
 'materials':['80C8864B'],'state':'00000000','tfx':'4900472149014722490247234903472449044725','tfx_sha':'902e8371bb2fc00f416923ef17f25e5237507d3d7f2130e42a82fa10403aec99',
 'textures':{0:'80876559',1:'80AB0A49',2:'8087655A',3:'80AB0A4B',4:'80876555'},
 'cb':['0000e0400000e0400000000000000000','00000040000080bf000080bf000080bf','0000e0400000e0400000000000000000','00000040000080bf000080bf000080bf','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','8878113db6561a3d7e25253d0000803f','00000000000000000000000000000000','00000000dfdd5d3e00005c4200006042'],
 'samplers':[SAMPLER]*5,'sampler_shas':[SAMPLER_SHA]*5,
 'anchors':['v_mul_f32       v4, v12, v16','v_mul_f32       v8, v13, v17','v_mul_f32       v9, v14, v18','v_mul_f32       v14, 0x40930885, v4','v_madmk_f32     v4, v4, 0xc0930885, v18','v_mac_f32       v14, v2, v4','exp             mrt0, v1, v1, v0, v0 done compr vm'],
 'equations':{'normal_xy':'nx=2*t2.r+2*t3.r-2; ny=2*t2.g+2*t3.g-2','surface':'C=t0.rgb*t1.rgb; Cs=4.594789981842041*C','palette':'P=b0[28:30]; B=saturate(P-0.25)+saturate(4*P)*Cs','mrt0_rgb':'mrt0.rgb=lerp(Cs,B,t4.r)','mrt0_alpha':'mrt0.a=attr0.w','normal_pack':'k=0.375+0.125*t0.a; mrt1.rgb=saturate(0.5+k*N); mrt1.a=b0[37]'},
 'roles':{'t0':'surface_rgb_primary_and_pack_alpha','t1':'surface_rgb_detail_multiplier','t2':'primary_normal_xy','t3':'detail_normal_xy','t4':'palette_mix_scalar'}},
'8087688E':{
 'native':'80876893','native_sha':'13ff22179f5e2cd6494686ab778cf630de1a8e7ba4b7c1b281252e02d13768ef','gcn':'baac1e745b26a50890eccb7549f1cba4f329c8bdcdd2825c2936c8666ec1686c','bytes':252,'prim':2,
 'usage':[('ImmConstBuffer',0,4)],'image':[],'materials':['80876865'],'state':'00000000','tfx':'4a043400034201','tfx_sha':'de39e4a77d2ac5c967dfa1b488259976c0f62177f3633a2ef142e770a173fda3','textures':{},
 'cb':['b4e7323c0000803f0000803f0000803f','00000000000000000000000000000000','00000000000000000000000000000000','0000803f3231713f0000704300007043'],'samplers':[],'sampler_shas':[],
 'anchors':['v_mul_f32       v5, s4, v6','v_mul_f32       v6, s5, v7','v_mul_f32       v7, s6, v8','exp             mrt0, v1, v1, v0, v0 done compr vm'],
 'equations':{'current_mrt0_rgb':'mrt0.rgb=b0[0:2]*b0[4:6]=(0,0,0)','mrt0_alpha':'mrt0.a=attr0.w','normal':'N=normalize(attr0.xyz)','normal_pack':'k=0.375+0.125*b0[12]=0.5; mrt1.rgb=saturate(0.5+k*N); mrt1.a=b0[13]'},'roles':{}},
'80AA8E93':{
 'native':'80AA8E94','native_sha':'0b8b0ed287c4aef42c31b534cded1292d345429d58f77e3513e8dab797de50c1','gcn':'f2200200fba9acaf2b20fb0df75514166675d918c55cb8373c73158b51cedccf','bytes':844,'prim':3,
 'usage':[('PtrExtendedUserData',1,2),('ImmResource',0,4),('ImmSampler',1,12),('ImmResource',1,16),('ImmResource',2,24),('ImmSampler',2,32),('ImmSampler',3,36),('ImmConstBuffer',0,40),('ImmConstBuffer',12,44)],
 'image':[('image_sample',1,2,3),('image_sample',0,1,15),('image_get_lod',2,3,2),('image_sample_l',2,3,7)],
 'materials':['80876868'],'state':'00000000','tfx':'490047214901472249024723','tfx_sha':'c8c8592453040aa582d39a6872628846c44f8c68acdbaa5426b8a3d7f8b3b2e5','textures':{0:'80AAF8B2',1:'80AAF8B3',2:'80876957'},
 'cb':['0000c03f000040bf000040bf000040bf','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','000080400000803f0000803f0000803f','000000000000803f0000803f0000803f','0000803f0000803f0000803f0000803f','0000803f0000803f0000803f0000803f','000000000000803f0000803f0000803f','0000803f0000803f0000803f0000803f','00000000000000000000000000000000','000000009b9a9a3d000098410000a041'],
 'samplers':[SAMPLER,SAMPLER,CUBE_SAMPLER],'sampler_shas':[SAMPLER_SHA,SAMPLER_SHA,CUBE_SAMPLER_SHA],
 'anchors':['v_cubema_f32    v5, v6, v13, v11','image_get_lod   v2, v[14:17]','image_sample_l  v[14:16], v[14:17]','v_mul_f32       v7, v10, v15','v_mac_f32       v7, s9, v5','exp             mrt0, v1, v1, v0, v0 done compr vm'],
 'equations':{'normal_xy':'nx=1.5*t1.r-0.75; ny=1.5*t1.g-0.75','view_reflection':'R=reflect(-normalize(api12[28:30]-attr4.xyz),N)','cube_lod_current':'L=max(image_get_lod(t2,R).y,4*(1-t0.a)); cube=sample_l(t2,R,L).rgb','mrt0_rgb_current':'mrt0.rgb=t0.rgb*(1+cube)+cube','mrt0_alpha':'mrt0.a=attr0.w'},'roles':{'t0':'surface_rgb_alpha_cube_lod_control','t1':'primary_normal_xy','t2':'environment_cube_rgb'}},
'80876566':{
 'native':'808765B2','native_sha':'4aeb9c03f44fc76751a471feb1292cd03afd7a3ad4480c9fb85e92f3e58a6634','gcn':'7f4f43dad2fe85c636df47ce650d57c038e481f9dfd1347c51c6255a6591ace8','bytes':544,'prim':1,
 'usage':[('PtrExtendedUserData',1,2),('ImmResource',0,4),('ImmSampler',1,12),('ImmResource',1,16),('ImmSampler',2,24),('ImmConstBuffer',0,28)],'image':[('image_sample',1,2,3),('image_sample',0,1,7)],
 'materials':['80876508'],'state':'00000000','tfx':'4900472149014722','tfx_sha':'63e3caa08d671f3587190defea7e77363413343632d9feaae424d2de932b1b90','textures':{0:'8087654F',1:'80876550'},
 'cb':['0000404000000000000080bf000080bf','0000000000004040000080bf000080bf','20f8a63ce31cc73caa49ee3c0000803f','0000404000000000000080bf000080bf','0000000000004040000080bf000080bf','00000040000080bf000080bf000080bf'],
 'samplers':[SAMPLER,SAMPLER],'sampler_shas':[SAMPLER_SHA,SAMPLER_SHA],
 'anchors':['v_max_f32       v3, s0, s0 mul:4','v_add_f32       v13, s0, v12 clamp','v_mac_f32       v13, v6, v3','exp             mrt0, v1, v1, v0, v0 done compr vm'],
 'equations':{'normal':'t1.xy is transformed by the exact two affine UV rows and b0[20:21] signed-normal remap before basis normalization','palette':'P=b0[8:10]; mrt0.rgb=saturate(P-0.25)+t0.rgb*saturate(4*P)','current_palette':'P=(0.02038198709487915,0.024305766448378563,0.029087860137224197)','mrt0_alpha':'mrt0.a=attr0.w','mrt1_alpha':'0'},'roles':{'t0':'palette_scaled_surface_rgb','t1':'primary_normal_xy'}},
'80876715':{
 'native':'80876764','native_sha':'45c3ed64ff4bbe58c03902bde875540f76d6de2f3377574bc86816e4a8a368cf','gcn':'cfc72eeba34802c8b8cfadd7986cf760464454e647b9a4d93781cbfdde0800b7','bytes':420,'prim':1,
 'usage':[('PtrExtendedUserData',1,2),('ImmResource',0,4),('ImmSampler',1,12),('ImmResource',1,16),('ImmSampler',2,24),('ImmConstBuffer',0,28)],'image':[('image_sample',1,2,3),('image_sample',0,1,15)],
 'materials':['808766B0'],'state':'00000000','tfx':'4900472149014722','tfx_sha':'63e3caa08d671f3587190defea7e77363413343632d9feaae424d2de932b1b90','textures':{0:'80876709',1:'8087670A'},
 'cb':['00000040000080bf000080bf000080bf','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000c8c7073f0000074300000843'],
 'samplers':[SAMPLER,SAMPLER],'sampler_shas':[SAMPLER_SHA,SAMPLER_SHA],
 'anchors':['image_sample    v[4:5], v[2:5]','image_sample    v[6:9], v[2:5]','v_mac_f32       v3, s4, v9','v_cvt_pkrtz_f16_f32 v1, v6, v7','v_cvt_pkrtz_f16_f32 v0, v8, v0','exp             mrt0, v1, v1, v0, v0 done compr vm'],
 'equations':{'normal_xy':'nx=2*t1.r-1; ny=2*t1.g-1','mrt0_rgb':'mrt0.rgb=t0.rgb','mrt0_alpha':'mrt0.a=attr0.w','normal_pack':'k=0.375+0.125*t0.a; mrt1.rgb=saturate(0.5+k*N); mrt1.a=b0[17]'},'roles':{'t0':'direct_surface_rgb_and_pack_alpha','t1':'primary_normal_xy'}},
'8087656E':{
 'native':'808765BA','native_sha':'ecc565e552b4b14e7c069ac1553f51e911b33e4dccfb66ee16559528da9ad2d5','gcn':'47f0af9375698ce8d7cf7b5545f00eb3bc946916db328dc42f70ad5210a29904','bytes':624,'prim':1,
 'usage':[('PtrExtendedUserData',1,2),('ImmResource',0,4),('ImmSampler',1,12),('ImmResource',1,16),('ImmResource',2,24),('ImmSampler',2,32),('ImmSampler',3,36),('ImmConstBuffer',0,40)],'image':[('image_sample',1,2,8),('image_sample',2,3,3),('image_sample',0,1,15)],
 'materials':['80876510'],'state':'00008100','tfx':'4900472149014722490247233c011c23220034000f23220035014206','tfx_sha':'cae4bd9028405caa08968e6f61635ccc1d31d1c01c687493e36c2a8b4629b8ee','textures':{0:'8087655F',1:'80876560',2:'80876561'},
 'cb':['00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','a1cb3d3d5555623d906e873d0000803f','00000000000000000000000000000000','00000040000080bf000080bf000080bf','00000000000000000000000000000000','00000000dfdd5d3e00005c4200006042'],
 'samplers':[SAMPLER]*3,'sampler_shas':[SAMPLER_SHA]*3,
 'anchors':['image_sample    v5, v[3:6]','v_cmp_gt_f32    vcc, 0, v5','image_sample    v[5:6], v[3:6]','image_sample    v[7:10], v[3:6]','v_max_f32       v10, s0, s0 mul:4','v_mac_f32       v13, v7, v6','exp             mrt0, v1, v1, v0, v0 done compr vm'],
 'equations':{'coverage':'t1.a is sampled before the main path and compared against current b0[24]=0; rejected lanes do not execute the surface path','normal_xy':'nx=2*t2.r-1; ny=2*t2.g-1','palette':'P=b0[20:22]; mrt0.rgb=saturate(P-0.25)+t0.rgb*saturate(4*P)','current_palette':'P=(0.04633677378296852,0.0552571602165699,0.06612884998321533)','mrt0_alpha':'mrt0.a=attr0.w','normal_pack':'t0.a contributes to the current deferred-normal packing scale through the exact native scalar branch; mrt1.a=b0[37]'},'roles':{'t0':'palette_scaled_surface_rgb_and_pack_alpha','t1':'coverage_mask_alpha','t2':'primary_normal_xy'}},
'80876537':{
 'native':'80876542','native_sha':'2a6f2862d8609c7633dd76c2febfcc638dd50153d8dd28e8ead3b43084bd4fa5','gcn':'600cb37b7fe79747fe1a0e4584e910d645e3130cf0ffd3f6c8a597abb4c49dab','bytes':580,'prim':1,
 'usage':[('PtrExtendedUserData',1,2),('ImmSampler',1,4),('ImmSampler',2,8),('PtrResourceTable',0,12),('ImmSampler',3,16),('ImmSampler',4,20),('ImmSampler',5,24),('ImmConstBuffer',0,28)],'image':[('image_sample',2,3,3),('image_sample',3,4,3),('image_sample',4,5,1),('image_sample',0,1,7),('image_sample',1,2,7)],
 'materials':['8087652A'],'state':'00000000','tfx':'4900472149014722490247234903472449044725','tfx_sha':'902e8371bb2fc00f416923ef17f25e5237507d3d7f2130e42a82fa10403aec99','textures':{0:'80876534',1:'80AB04BB',2:'80876535',3:'80AB04BC',4:'80876536'},
 'cb':['00008040000080400000000000000000','00000040000080bf000080bf000080bf','00008040000080400000000000000000','00000040000080bf000080bf000080bf','00000000000000000000000000000000','000000002625a53e0000a4420000a642'],
 'samplers':[SAMPLER]*5,'sampler_shas':[SAMPLER_SHA]*5,
 'anchors':['v_mul_f32       v6, v12, v15','v_mul_f32       v7, v13, v16','v_mul_f32       v8, v14, v17','v_mul_f32       v5, 0x40930885, v6','v_mul_f32       v6, 0x40930885, v7','v_mul_f32       v7, 0x40930885, v8','exp             mrt0, v1, v1, v0, v0 done compr vm'],
 'equations':{'normal_xy':'nx=2*t2.r+2*t3.r-2; ny=2*t2.g+2*t3.g-2','mrt0_rgb':'mrt0.rgb=4.594789981842041*(t0.rgb*t1.rgb)','mrt0_alpha':'mrt0.a=attr0.w','normal_pack':'k=0.375+0.125*t4.r; mrt1.rgb=saturate(0.5+k*N); mrt1.a=b0[21]'},'roles':{'t0':'surface_rgb_primary','t1':'surface_rgb_detail_multiplier','t2':'primary_normal_xy','t3':'detail_normal_xy','t4':'normal_pack_scalar'}}
}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--extract-report',type=Path,required=True);ap.add_argument('--image-usage',type=Path,required=True);ap.add_argument('--material-state',type=Path,required=True);ap.add_argument('--disasm-dir',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 ext=json.loads(a.extract_report.read_text()); iu=json.loads(a.image_usage.read_text()); st=json.loads(a.material_state.read_text());viol=[];proofs=[]
 if ext.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT':viol.append('extract checkpoint not exact')
 if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':viol.append('image-usage checkpoint not exact')
 if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):viol.append('material-state checkpoint not exact')
 eby={x['shader']:x for x in ext.get('shaders',[])}; iby={x['shader']:x for x in iu.get('shaders',[])}
 for sh,f in F.items():
  er=eby.get(sh); ir=iby.get(sh); asm=(a.disasm_dir/f'PS_{sh}.s').read_text()
  if not er:viol.append(f'{sh}: extract row absent');continue
  for k,v in [('native_shader',f['native']),('native_sha256',f['native_sha']),('gcn_sha256',f['gcn']),('gcn_bytes',f['bytes'])]:
   if er.get(k)!=v:viol.append(f'{sh}: {k} mismatch {er.get(k)!r}')
  usage=[(x.get('usage_name'),x.get('api_slot'),x.get('start_register')) for x in er.get('usage',{}).get('slots',[])]
  if usage!=f['usage']:viol.append(f'{sh}: usage mismatch {usage!r}')
  if not ir:viol.append(f'{sh}: image row absent');continue
  seq=[]
  for x in ir.get('instructions',[]):
   rr=x.get('resources') or [];ss=x.get('samplers') or []
   seq.append((x.get('opcode'),rr[0].get('texture_index') if len(rr)==1 else None,ss[0].get('sampler_index') if len(ss)==1 else None,x.get('dmask')))
  if seq!=f['image'] or ir.get('unmatched_image_instruction_count')!=0:viol.append(f'{sh}: image sequence mismatch {seq!r}')
  for needle in f['anchors']:
   if needle not in asm:viol.append(f'{sh}: missing anchor {needle}')
  got=sorted((st.get('shader_materials',{}).get('ps',{}) or {}).get(sh,[]))
  if got!=sorted(f['materials']):viol.append(f'{sh}: material set mismatch {got!r}')
  for mh in f['materials']:
   m=st.get('materials',{}).get(mh)
   if not m or m.get('error'):viol.append(f'{sh}/{mh}: unresolved material');continue
   ps=m['ps']
   if m.get('material_state4_hex')!=f['state']:viol.append(f'{sh}/{mh}: material state mismatch')
   if ps.get('shader')!=sh:viol.append(f'{sh}/{mh}: shader mismatch')
   if ps.get('tfx_program_sha256')!=f['tfx_sha'] or ps['tfx_bytecode'].get('bytes_hex')!=f['tfx'] or ps.get('tfx_disassembly',{}).get('complete') is not True:viol.append(f'{sh}/{mh}: TFX mismatch/incomplete')
   tex={int(x['texture_index']):x['texture'].upper() for x in ps['textures']['items']}
   if tex!=f['textures']:viol.append(f'{sh}/{mh}: texture map mismatch {tex!r}')
   if [x['raw_hex'] for x in ps['cbuffers']['items']]!=f['cb']:viol.append(f'{sh}/{mh}: full b0 mismatch')
   if [x['first_dword_hex'] for x in ps['samplers']['items']]!=f['samplers']:viol.append(f'{sh}/{mh}: sampler tag sequence mismatch')
   shas=[(x.get('native_sampler') or {}).get('payload_sha256') for x in ps.get('sampler_references',[])]
   if shas!=f['sampler_shas']:viol.append(f'{sh}/{mh}: native sampler payload sequence mismatch')
  proofs.append({'shader':sh,'native_shader':f['native'],'gcn_sha256':f['gcn'],'materials':f['materials'],'visible_primitive_count':f['prim'],'texture_bindings':{str(k):v for k,v in f['textures'].items()},'instruction_level_equations':f['equations'],'promoted_texture_semantics':f['roles'],'current_material_native_color_dataflow_closed':True,'portable_blender_recreation_complete':False})
 if viol: out={'schema_version':1,'status':'D1_TOWER_THREE_NPC_PS_TAIL_WAVE6_PARTIAL','violations':viol}
 else:
  n=sum(x['visible_primitive_count'] for x in proofs); assert n==11,n
  out={'schema_version':1,'status':'D1_TOWER_THREE_NPC_PS_TAIL_WAVE6_EXACT','program_count':len(proofs),'visible_primitive_count':n,'proofs':proofs,'current_material_native_color_dataflow_closed':True,'portable_blender_recreation_complete':False,'violations':[],'policy':'Exact native/current serialized-state RGB semantics only. No generic glTF/Principled/PBR equivalence is promoted.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out if viol else {k:out[k] for k in ['status','program_count','visible_primitive_count','violations']},indent=2));return 2 if viol else 0
if __name__=='__main__': raise SystemExit(main())
