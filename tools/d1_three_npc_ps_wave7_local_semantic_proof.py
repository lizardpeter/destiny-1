#!/usr/bin/env python3
"""Fail-closed native/current-state proof for three-NPC PS wave 7.

Closes the four remaining local-only color programs. Material fingerprints cover
state, TFX, private constants, all b0 vectors, exact t# bindings, sampler tags,
and native sampler payloads. Native shader/GCN hashes, OrbShdr usage, image
instructions, and instruction anchors are checked independently. API15-dependent
PS 8087670E is intentionally excluded.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
K=4.594789981842041
F={
'8087645C':{
'native':'80876469','native_sha':'a5332139c498dace61fe93b0673c6606c210a350fc389556d89ed860c1cdee9c','gcn':'b4e0a596f4b3fcb8d910768b009613905c12754d81a83ab97949894fb6d7e5b9','bytes':956,'prims':1,
'usage':[('PtrExtendedUserData',1,2),('ImmSampler',1,4),('ImmSampler',2,8),('PtrResourceTable',0,12),('ImmSampler',3,16),('ImmSampler',4,20),('ImmSampler',5,24),('ImmSampler',6,28),('ImmConstBuffer',0,32),('ImmConstBuffer',12,36)],
'image':[('image_sample',1,2,3),('image_sample',2,3,3),('image_sample',0,1,15),('image_get_lod',3,4,2),('image_sample_l',3,4,15),('image_sample',4,5,4),('image_sample',5,6,1)],
'materials':{'8087642C':'52cb70f63fafd3319d542f2b955b7d4db5fe74bac4723b71b8b7f760f9a1d1f5'},
'anchors':['image_sample    v[8:9], v[6:9]','image_sample    v[4:5], v[4:7]','v_cubema_f32','image_get_lod','image_sample_l','image_sample    v2, v[6:9]','image_sample    v3, v[3:6]','v_log_f32','v_exp_f32','exp             mrt0'],
'eq':{'normal_xy':'nx=2*t1.r+2*t2.r-2; ny=2*t1.g+2*t2.g-2; t2 current UV=(2*u-0.5,2*v-0.5)','view':'V=normalize(api12[28:30]-attr4.xyz); R=reflect(-V,N)','lod':'A=saturate(-1.3+2.3*t0.a); lodFloor=1-A; cube=sample_l(t3,R,max(image_get_lod(t3,R).y,lodFloor))','fresnel':'F=(saturate(1-dot(N,V)))^5','reflection_strength':'S=cube.a*(2-t0.a)*0.4*F','detail_scalar':'M=t4.b*t5.r','mrt0_rgb':'mrt0.rgb=t0.rgb+(0.39+0.91*t0.rgb)*cube.rgb*M*S','mrt0_alpha':'mrt0.a=attr0.w','normal_pack':'k=0.375+0.125*t0.a; mrt1.rgb=saturate(0.5+k*N); mrt1.a=0.051960788667201996'},
'roles':{'t0':'surface RGB + alpha control','t1':'primary normal XY','t2':'detail normal XY','t3':'environment cube','t4':'blue detail/reflection scalar','t5':'red detail/reflection scalar'}},
'8087656A':{
'native':'808765B6','native_sha':'32e754efc9ac6b2333d2eeb18751081b24ecafca2208ba59e8c92e9061cd8057','gcn':'48ed81ed1cfef67930cb813e45304b4f786b49bf45d44d33fc1cbba535320135','bytes':1048,'prims':2,
'usage':[('PtrExtendedUserData',1,2),('ImmSampler',1,4),('ImmSampler',2,8),('PtrResourceTable',0,12),('ImmSampler',3,16),('ImmSampler',4,20),('ImmSampler',5,24),('ImmConstBuffer',0,28),('ImmConstBuffer',12,32)],
'image':[('image_sample',0,1,15),('image_sample',2,3,3),('image_sample',3,4,3),('image_get_lod',4,5,2),('image_sample',1,2,7),('image_sample_l',4,5,15)],
'materials':{'8087650C':'9150fbc0a552f4c4998e1a5f967c8bf4aaec246568009c070e7be3912fb2b8fb','80876645':'9150fbc0a552f4c4998e1a5f967c8bf4aaec246568009c070e7be3912fb2b8fb'},
'anchors':['image_sample    v[7:10], v[3:6]','v_cmp_gt_f32    vcc, 0, v11','image_sample    v[5:6], v[3:6]','image_sample    v[11:12], v[11:14]','v_cubema_f32','image_get_lod','image_sample    v[17:19]','image_sample_l','v_log_f32','v_exp_f32','v_madmk_f32','exp             mrt0'],
'eq':{'coverage':'kill when t0.a < b0[24]; current threshold=0','normal_xy':'nx=2*t2.r+1.6*t3.r-1.8; ny=2*t2.g+1.6*t3.g-1.8; t3 current UV=7*uv','view':'V=normalize(api12[28:30]-attr4.xyz); R=reflect(-V,N)','lod':'current cube LOD floor=6','surface':f'C=t0.rgb*t1.rgb; Cs={K}*C','fresnel':'F=saturate(1-dot(N,V))','reflection_strength':'S=saturate(cube.a*(0.20250000059604645+0.2695000171661377*t0.a)*(0.2248000055551529+1.1234999895095825*F))','cube_branch':'Q=saturate(1.1239999532699585*cube.rgb-0.25)+Cs*saturate(4*1.1239999532699585*cube.rgb)','mrt0_rgb':'mrt0.rgb=lerp(Cs,Q,S)','mrt0_alpha':'mrt0.a=attr0.w','normal_pack':'k=0.375+0.125*t0.a; mrt1.a=0.21666668355464935'},
'roles':{'t0':'surface RGB primary + coverage/reflection/pack alpha','t1':'surface RGB multiplier','t2':'primary normal XY','t3':'detail normal XY','t4':'environment cube'}},
'8087670C':{
'native':'8087675B','native_sha':'cf89e633113024cbc40b932086b9aadd9604b99286d54531d6761dbbd2ed819f','gcn':'4621f4b7d19c09deadbb92b56654a5609f426c9bf59cd3f41c892db26dbbac4c','bytes':1128,'prims':2,
'usage':[('PtrExtendedUserData',1,2),('ImmSampler',1,4),('ImmSampler',2,8),('PtrResourceTable',0,12),('ImmSampler',3,16),('ImmSampler',4,20),('ImmSampler',5,24),('ImmSampler',6,28),('ImmConstBuffer',0,32),('ImmConstBuffer',12,36)],
'image':[('image_sample',2,3,3),('image_sample',3,4,3),('image_sample',5,6,8),('image_get_lod',4,5,2),('image_sample',0,1,7),('image_sample',1,2,7),('image_sample_l',4,5,15)],
'materials':{'808766AF':'79ff01198f73caa655c00f77762b12fd47d0459d78de98f1039db7b65ad6c9b9','808766B4':'79ff01198f73caa655c00f77762b12fd47d0459d78de98f1039db7b65ad6c9b9'},
'anchors':['image_sample    v[8:9], v[6:9]','image_sample    v[4:5], v[4:7]','v_cubema_f32','image_sample    v12, v[6:9]','image_get_lod','image_sample    v[17:19]','image_sample    v[20:22]','image_sample_l','v_log_f32','v_exp_f32','v_madmk_f32','exp             mrt0'],
'eq':{'normal_xy':'nx=2*t2.r+1.2*t3.r-1.6; ny=2*t2.g+1.2*t3.g-1.6; t3 current UV=7*uv','view':'D=saturate(1-dot(N,normalize(api12[28:30]-attr4.xyz))); R=reflect(-V,N)','lod':'current cube LOD floor=6','surface':f'C=t0.rgb*t1.rgb; Cs={K}*C','fresnel':'F=exp2(3.944000005722046*log2(D))','reflection_strength':'S=saturate(cube.a*(-0.5+2.5*t5.a)*(1.3300000429153442*F))','alternate_branch':'B=saturate(Cs-0.25)+(7*cube.rgb)*saturate(4*Cs)','pre_color':'P=lerp(Cs,B,S)','view_scalar':'G=(-0.9568462371826172+1.343794822692871)-(-0.9568462371826172)*(D*D)','channel_scale':'H=(1,0.5674839615821838,0.4098677933216095)+(-0.8509050607681274,-0.094829261302948,0.24156227707862854)*G','mrt0_rgb':'mrt0.rgb=P*H','mrt0_alpha':'mrt0.a=attr0.w','normal_pack':'k=0.375+0.125*t5.a; mrt1.a=0.028431374579668045'},
'roles':{'t0':'surface RGB primary','t1':'surface RGB detail multiplier','t2':'primary normal XY','t3':'detail normal XY','t4':'environment cube','t5':'alpha scalar controlling cube/reflection/normal-pack'}},
'808762E1':{
'native':'8087635C','native_sha':'72f4492cdd48ff32dc17211324e0fcf52673948737606d1f1857deb7302cb140','gcn':'564ece90d384ef625046b6f374aa5ecbb310e09301aa0308a3926f93bbe82c24','bytes':1036,'prims':2,
'usage':[('PtrExtendedUserData',1,2),('ImmSampler',1,4),('ImmSampler',2,8),('PtrResourceTable',0,12),('ImmSampler',3,16),('ImmSampler',4,20),('ImmSampler',5,24),('ImmSampler',6,28),('ImmSampler',7,32),('ImmSampler',8,36),('ImmConstBuffer',0,40)],
'image':[('image_sample',6,7,3),('image_sample',7,8,3),('image_sample',0,1,3),('image_sample',2,3,7),('image_sample',3,4,7),('image_sample',5,6,4),('image_sample',4,5,7),('image_sample',1,2,15)],
'materials':{'808761C9':'8f6e66aa5ef45aaaac0af9521490e45dfc31617c31327418a98410e4b700d758'},
'anchors':['image_sample    v[8:9], v[6:9]','image_sample    v[4:5], v[4:7]','image_sample    v[2:3], v[6:9]','image_sample    v[12:14]','image_sample    v[15:17]','image_sample    v18','image_sample    v[19:21]','image_sample    v[22:25]','v_subrev_f32    v29, s7, v2','v_mac_f32       v11, v12, v4','v_mac_f32       v11, v3, v15','v_mac_f32       v11, v18, v3','v_mul_f32       v4, v25, v4','exp             mrt0'],
'eq':{'control':'q0=0.23750001192092896+t0.r*(t0.r-0.23750001192092896); q1=q0+t0.g*(t0.g-q0); q2=q1+t5.b*(t5.b-q1); coverage=t1.a*q2','palette_a':'A=saturate((0.03551533818244934,0.03768035024404526,0.04031895846128464)-0.25)+t2.rgb*saturate(4*(0.03551533818244934,0.03768035024404526,0.04031895846128464))','palette_b':'B=saturate((0.03551533818244934,0.03768035024404526,0.04031895846128464)-0.25)+t3.rgb*saturate(4*(0.03551533818244934,0.03768035024404526,0.04031895846128464))','palette_c':'C=saturate((0.020570652559399605,0.021824637427926064,0.023352932184934616)-0.25)+t4.rgb*saturate(4*(0.020570652559399605,0.021824637427926064,0.023352932184934616))','palette_mix':'P1=lerp((1,1,1),A,t0.r); P2=lerp(P1,B,t0.g); P3=lerp(P2,C,t5.b)','normal_xy':'nx=2*t6.r+1.6*t7.r-1.8; ny=2*t6.g+1.6*t7.g-1.8; t7 current UV=17*uv','mrt0_rgb':f'mrt0.rgb={K}*(t1.rgb*P3)','mrt0_alpha':'mrt0.a=attr0.w','normal_pack':'k=0.375+0.125*coverage; mrt1.a=0.21666668355464935'},
'roles':{'t0':'palette selector RG + control','t1':'surface RGB multiplier + coverage alpha','t2':'palette branch A RGB','t3':'palette branch B RGB','t4':'palette branch C RGB','t5':'palette selector blue + control','t6':'primary normal XY','t7':'detail normal XY'}}}

def semantic_obj(m):
 p=m['ps'];return {'state':m.get('material_state4_hex'),'tfx_sha':p.get('tfx_program_sha256'),'tfx_hex':p['tfx_bytecode'].get('bytes_hex'),'priv':[x['raw_hex'] for x in p['tfx_private_constants']['items']],'cb':[x['raw_hex'] for x in p['cbuffers']['items']],'textures':[(int(x['texture_index']),x['texture'].upper()) for x in p['textures']['items']],'sampler_tags':[x['first_dword_hex'] for x in p['samplers']['items']],'sampler_shas':[(x.get('native_sampler') or {}).get('payload_sha256') for x in p.get('sampler_references',[])]}
def fp(m):return hashlib.sha256(json.dumps(semantic_obj(m),sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('--extract-report',type=Path,required=True);a.add_argument('--image-usage',type=Path,required=True);a.add_argument('--material-state',type=Path,required=True);a.add_argument('--disasm-dir',type=Path,required=True);a.add_argument('--out',type=Path,required=True);q=a.parse_args();e=json.loads(q.extract_report.read_text());i=json.loads(q.image_usage.read_text());s=json.loads(q.material_state.read_text());v=[];proof=[]
 if e.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT':v.append('extract not exact')
 if i.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':v.append('image usage not exact')
 if s.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or s.get('violations'):v.append('material state not exact')
 eb={x['shader']:x for x in e['shaders']};ib={x['shader']:x for x in i['shaders']}
 for sh,f in F.items():
  er=eb.get(sh);ir=ib.get(sh);asm=(q.disasm_dir/f'PS_{sh}.s').read_text()
  if not er:v.append(sh+': no extract');continue
  for k,w in [('native_shader',f['native']),('native_sha256',f['native_sha']),('gcn_sha256',f['gcn']),('gcn_bytes',f['bytes'])]:
   if er.get(k)!=w:v.append(f'{sh}: {k} mismatch')
  if [(x.get('usage_name'),x.get('api_slot'),x.get('start_register')) for x in er.get('usage',{}).get('slots',[])]!=f['usage']:v.append(sh+': usage mismatch')
  seq=[]
  if not ir:v.append(sh+': no image row');continue
  for x in ir.get('instructions',[]):
   r=x.get('resources') or [];z=x.get('samplers') or [];seq.append((x.get('opcode'),r[0].get('texture_index') if len(r)==1 else None,z[0].get('sampler_index') if len(z)==1 else None,x.get('dmask')))
  if seq!=f['image'] or ir.get('unmatched_image_instruction_count')!=0:v.append(sh+': image sequence mismatch')
  for n in f['anchors']:
   if n not in asm:v.append(sh+': missing anchor '+n)
  if sorted((s.get('shader_materials',{}).get('ps',{}) or {}).get(sh,[]))!=sorted(f['materials']):v.append(sh+': material set mismatch')
  for mh,w in f['materials'].items():
   m=s.get('materials',{}).get(mh)
   if not m or m.get('error') or fp(m)!=w:v.append(f'{sh}/{mh}: semantic fingerprint mismatch')
  proof.append({'shader':sh,'native_shader':f['native'],'gcn_sha256':f['gcn'],'materials':sorted(f['materials']),'visible_primitive_count':f['prims'],'instruction_level_equations':f['eq'],'promoted_texture_semantics':f['roles'],'current_material_native_color_dataflow_closed':True,'portable_blender_recreation_complete':False})
 if v:o={'schema_version':1,'status':'D1_TOWER_THREE_NPC_PS_SEMANTICS_WAVE7_PARTIAL','violations':v};rc=2
 else:
  total=sum(x['visible_primitive_count'] for x in proof);assert total==7
  o={'schema_version':1,'status':'D1_TOWER_THREE_NPC_PS_SEMANTICS_WAVE7_EXACT','violations':[],'program_count':4,'visible_primitive_count':total,'proofs':proof,'gates':{'current_material_native_color_dataflow_closed':True,'portable_blender_recreation_complete':False,'runtime_global_api15_closed':False},'policy':'Four local-only programs / 7 visible primitives are native/current-state closed. PS 8087670E remains blocked on API15 plus its runtime t4 resource.'};rc=0
 q.out.parent.mkdir(parents=True,exist_ok=True);q.out.write_text(json.dumps(o,indent=2)+'\n');print(json.dumps({k:o[k] for k in o if k!='proofs'},indent=2));return rc
if __name__=='__main__':raise SystemExit(main())
