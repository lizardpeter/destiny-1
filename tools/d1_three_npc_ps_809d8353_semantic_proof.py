#!/usr/bin/env python3
"""Fail-closed current-state native color proof for D1 PS4 PS 809D8353."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
SHADER='809D8353';NATIVE='809D839A'
NATIVE_SHA='664c19ed92eaace11f8e85e34444b2c07e0564471ac6c0f9b961e30e6735e12b'
GCN_SHA='8ce20ec83df2f657b344251ac6c1d6509c73dc95adfedeeb6d533e52c5016f70'
MATERIALS=['80C885F3','80C88632']
TEXTURES={0:'8087655B',1:'80AB04CD',2:'8087655C',3:'80AB04CF',4:'808768AD',5:'80876987',6:'80876555'}
TFX_SHA='e7498b2cc00ab7229f7474490d6d630cbd5fe7ca23f8d83ab7f20a87753c6429'
TFX_HEX='490047214901472249024723490347244904472549054726490647274a0022002322003700214a0022002322003905214a002200232200390f2322003b194210'
CB_RAW=['0000004000000000000000bf000000bf','0000000000000040000000bf000000bf','00000040000080bf000080bf000080bf','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','0000803f0000803f0000803f0000803f','000000000000803f0000803f0000803f','6666a6bf333313400000803f0000803f','00000041000000410000000000000000','00000000cdcccc3e0000a04000000000','00000040000080bf0000000000000000','c2f5683f15aec73e6666a63f6666a63f','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000d6d4543d0000504100006041']
SAMPLERS=['80AAE177','80AAE177','80AAE177','80AAE176','80AAE177','80AAE177','80AAE177']
SAMPLER_SHAS=['2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb']*3+['0bcdaa82ea0d8588e313f29998f6c7b9166e7d28d40b13d422348d55ae5dc208']+['2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb']*3
EXPECTED_USAGE=[('PtrExtendedUserData',1,2),('ImmSampler',1,4),('ImmSampler',2,8),('PtrResourceTable',0,12),('ImmSampler',3,16),('ImmSampler',4,20),('ImmSampler',5,24),('ImmSampler',6,28),('ImmSampler',7,32),('ImmConstBuffer',0,36),('ImmConstBuffer',12,40)]
EXPECTED_IMAGE=[('image_sample',2,3,3),('image_sample',0,1,15),('image_sample',1,2,15),('image_get_lod',3,4,2),('image_sample_l',3,4,15),('image_sample',4,5,4),('image_sample',5,6,1),('image_sample',6,7,1)]
ANCHORS=['image_sample    v[6:7], v[4:7], s[16:23], s[24:27] dmask:3','v_mad_f32       v6, v6, s0, v8','v_sqrt_f32      v7, v7','v_rsq_clamp_f32 v7, v15','v_rsq_clamp_f32 v6, v6','image_sample    v[19:22], v[4:7], s[28:35], s[4:7] dmask:15','image_sample    v[23:26], v[2:5], s[36:43], s[8:11] dmask:15','v_cubema_f32    v7, v17, v18, v16','image_get_lod   v11, v[27:30], s[20:27], s[44:47] dmask:2','image_sample_l  v[26:29], v[26:29], s[20:27], s[44:47] dmask:15','image_sample    v2, v[4:7], s[28:35], s[36:39] dmask:4','image_sample    v3, v[7:10], s[48:55], s[40:43]','image_sample    v4, v[4:7], s[56:63], s[12:15]','v_mul_f32       v14, v22, v26','v_mul_f32       v14, v14, v15','v_mul_f32       v7, v19, v23','v_mul_f32       v8, v20, v24','v_mul_f32       v11, v21, v25','v_mul_f32       v2, v2, v3','v_log_f32       v5, v5','v_exp_f32       v5, v5','v_mac_f32       v19, v4, v7','v_mac_f32       v20, v4, v8','v_mac_f32       v15, v4, v11','exp             mrt1, v1, v1, v2, v2 compr','exp             mrt0, v1, v1, v0, v0 done compr vm']
K=4.594789981842041
def close(a,b,eps=2e-7):return math.isclose(float(a),float(b),rel_tol=0,abs_tol=eps)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--extract-report',type=Path,required=True);ap.add_argument('--image-usage',type=Path,required=True);ap.add_argument('--material-state',type=Path,required=True);ap.add_argument('--disassembly',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 ext=json.loads(a.extract_report.read_text());iu=json.loads(a.image_usage.read_text());st=json.loads(a.material_state.read_text());asm=a.disassembly.read_text();viol=[]
 if ext.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT':viol.append('extract not exact')
 if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':viol.append('image usage not exact')
 if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):viol.append('material state not exact')
 er=next((x for x in ext.get('shaders',[]) if x.get('shader')==SHADER),None)
 if not er:viol.append('shader row absent')
 else:
  for k,v in [('native_shader',NATIVE),('native_sha256',NATIVE_SHA),('gcn_sha256',GCN_SHA),('gcn_bytes',1152)]:
   if er.get(k)!=v:viol.append(f'{k} mismatch {er.get(k)!r}')
  slots=[(x.get('usage_name'),x.get('api_slot'),x.get('start_register')) for x in er.get('usage',{}).get('slots',[])]
  if slots!=EXPECTED_USAGE:viol.append(f'usage mismatch {slots!r}')
 ir=next((x for x in iu.get('shaders',[]) if x.get('shader')==SHADER),None)
 if not ir:viol.append('image row absent')
 else:
  got=[]
  for x in ir.get('instructions',[]):
   rr=x.get('resources') or [];ss=x.get('samplers') or []
   got.append((x.get('opcode'),rr[0].get('texture_index') if len(rr)==1 else None,ss[0].get('sampler_index') if len(ss)==1 else None,x.get('dmask')))
  if got!=EXPECTED_IMAGE:viol.append(f'image mismatch {got!r}')
  if ir.get('unmatched_image_instruction_count')!=0:viol.append('unmatched image instruction')
 for n in ANCHORS:
  if n not in asm:viol.append('missing anchor '+n)
 sm=sorted((st.get('shader_materials',{}).get('ps',{}) or {}).get(SHADER,[]))
 if sm!=sorted(MATERIALS):viol.append(f'material set mismatch {sm!r}')
 ref=None
 for mh in MATERIALS:
  m=st.get('materials',{}).get(mh)
  if not m or m.get('error'):viol.append(f'{mh}: unresolved');continue
  ps=m['ps']
  if m.get('material_state4_hex')!='00000000':viol.append(f'{mh}: state mismatch')
  if ps.get('shader')!=SHADER:viol.append(f'{mh}: shader mismatch')
  if ps.get('tfx_program_sha256')!=TFX_SHA or ps['tfx_bytecode'].get('bytes_hex')!=TFX_HEX or not ps.get('tfx_disassembly',{}).get('complete'):viol.append(f'{mh}: TFX mismatch')
  tex={int(x['texture_index']):x['texture'].upper() for x in ps['textures']['items']}
  if tex!=TEXTURES:viol.append(f'{mh}: texture mismatch {tex!r}')
  if [x['raw_hex'] for x in ps['cbuffers']['items']]!=CB_RAW:viol.append(f'{mh}: b0 raw mismatch')
  if [x['first_dword_hex'] for x in ps['samplers']['items']]!=SAMPLERS:viol.append(f'{mh}: sampler mismatch')
  shas=[(r.get('native_sampler') or {}).get('payload_sha256') for r in ps.get('sampler_references',[])]
  if shas!=SAMPLER_SHAS:viol.append(f'{mh}: native sampler mismatch')
  vals=[float(v) for row in ps['cbuffers']['items'] for v in row['value']]
  expected={0:2,2:-.5,4:0,5:2,6:-.5,8:2,9:-1,24:1,28:0,32:-1.2999999523162842,33:2.299999952316284,36:8,37:8,40:0,41:.4000000059604645,42:5,44:2,45:-1,48:.9099999666213989,49:.39000001549720764,64:0,65:0,66:0,73:.051960788667201996}
  if len(vals)!=76:viol.append(f'{mh}: b0 length {len(vals)}')
  else:
   for i,v in expected.items():
    if not close(vals[i],v):viol.append(f'{mh}: b0[{i}] {vals[i]!r} != {v!r}')
  sem=(ps['tfx_bytecode']['bytes_hex'],tuple(x['raw_hex'] for x in ps['tfx_private_constants']['items']),tuple(x['raw_hex'] for x in ps['cbuffers']['items']),tuple(sorted(tex.items())),tuple(x['first_dword_hex'] for x in ps['samplers']['items']))
  if ref is None:ref=sem
  elif sem!=ref:viol.append(f'{mh}: semantic payload differs')
 if viol:
  out={'schema_version':1,'status':'D1_TOWER_PS_809D8353_CURRENT_STATE_COLOR_SEMANTICS_PARTIAL','violations':viol};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 2
 out={'schema_version':1,'status':'D1_TOWER_PS_809D8353_CURRENT_STATE_COLOR_SEMANTICS_EXACT','violations':[],'shader':SHADER,'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'scope_materials':MATERIALS,'scope_material_count':2,'visible_primitive_count':6,
 'exact_inputs':{'texture_bindings_t0_t6':{str(k):v for k,v in TEXTURES.items()},'material_state4_hex':'00000000','tfx_program_sha256':TFX_SHA,'material_cbuffer_raw_hex':CB_RAW,'api12_camera_dependency':{'dwords':[28,29,30],'meaning':'camera/view position','evidence':'already source-closed D1 api12 contract'}},
 'instruction_level_equations':{'uv':'uv=attr3.xy','surface_detail_uv':'uvC=float2(b0[0]*uv.x+b0[1]*uv.y+b0[2],b0[4]*uv.x+b0[5]*uv.y+b0[6]); current uvC=2*uv-0.5','detail_control_uv':'uvD=float2(b0[36]*uv.x+b0[38],b0[37]*uv.y+b0[39]); current uvD=8*uv','normal_xy':'nx=b0[8]*t2.r+b0[9]; ny=b0[8]*t2.g+b0[9]; current nx=2*t2.r-1, ny=2*t2.g-1','normal_z':'nz=sqrt(saturate(1-nx*nx-ny*ny))','world_normal':'N=normalize(nx*attr1.xyz+ny*attr2.xyz+nz*attr0.xyz)','view_vector':'V=normalize(api12[28:30]-attr4.xyz)','reflection_vector':'R=2*dot(N,V)*N-V','surface_product':'C=t0.rgb*t1.rgb','surface_scaled':f'Cs={K}*C','alpha_product_scaled':f'A={K}*t0.a*t1.a','cube_lod_factor':'q=saturate(b0[32]+b0[33]*A); current q=saturate(-1.3+2.3*A)','cube_lod_floor':'Lfloor=b0[24]+q*(b0[28]-b0[24]); current Lfloor=1-q','cube_lod':'L=max(image_get_lod(t3,R).y,Lfloor); cube=sample_l(t3,R,L)','fresnel':'F=exp2(b0[42]*log2(saturate(1-dot(N,V)))); current F=saturate(1-dot(N,V))^5','base_attenuated_current':'Base=Cs*(1-t6.r); this simplification is exact for current b0[64:66]=0','detail_scalar':'D=t4.b*t5.r','normal_length_correction':'Nc=2-dot(N,N); native code retains this correction rather than assuming ideal unit length','reflection_strength':'S=cube.a*Nc*(b0[40]+b0[41]*F); current S=cube.a*Nc*0.4*F','reflection_color_factor':'Rf=b0[49]+b0[48]*Base; current Rf=0.39+0.91*Base','mrt0_rgb':'mrt0.rgb=Base + cube.rgb*D*S*Rf','mrt0_alpha':'mrt0.a=attr0.w','normal_pack':'k=0.375+0.125*A; mrt1.rgb=saturate(0.5+k*N); mrt1.a=b0[73]','normal_pack_current_alpha':'mrt1.a=0.051960788667201996'},
 'promoted_texture_semantics':{'t0':{'tag':TEXTURES[0],'role':'surface_rgb_alpha_primary','proof':'native RGBA participates in surface RGB and A'},'t1':{'tag':TEXTURES[1],'role':'surface_rgb_alpha_detail','proof':'native RGBA at transformed UV multiplies t0'},'t2':{'tag':TEXTURES[2],'role':'normal_xy','proof':'native xy reconstructs signed normal'},'t3':{'tag':TEXTURES[3],'role':'environment_cubemap','proof':'cube coordinate ops + get_lod + sample_l'},'t4':{'tag':TEXTURES[4],'role':'reflection_detail_blue_control','proof':'native z only multiplies reflection detail'},'t5':{'tag':TEXTURES[5],'role':'reflection_detail_red_control','proof':'native r at 8x UV multiplies t4.b'},'t6':{'tag':TEXTURES[6],'role':'surface_attenuation_red_control','proof':'current native branch reduces Base to Cs*(1-t6.r)'}},
 'critical_correction':'809D8353 is not a single-base-texture material. Current surface color is the product t0.rgb*t1.rgb, attenuated by t6.r, with a separate cubemap detail term controlled by t4.b*t5.r.',
 'gates':{'current_material_native_color_dataflow_closed':True,'portable_color_source_closed':True,'portable_blender_recreation_complete':False,'deferred_framebuffer_equivalence_closed':False,'runtime_tfx_semantics_complete':False},'policy':'Exact current serialized state and native GCN dataflow only; TFX producer meaning and generic PBR equivalence remain separate.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ('status','visible_primitive_count','critical_correction','gates')},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
