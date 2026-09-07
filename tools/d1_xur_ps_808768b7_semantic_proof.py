#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
SHADERS={'808768B7':('808768BE','a87bbdfa26d8ccaf5fba62638297665e190ce7af05b93904a8032770f77951c1'),'80A08C16':('80A08C18','a87bbdfa26d8ccaf5fba62638297665e190ce7af05b93904a8032770f77951c1')}
GCN_SHA='749b857954de10c984a7b75dceadd9df5dcb1d4a84546750e650bfc3ecd323b9'
MEMBERS={'80876894':'808768B7','80C888C7':'80A08C16'}
TFX='4900472149014722490247234903472449044725'
TEXTURES={0:'80AAF8B2',1:'80AAF8B3',2:'80AA820A',3:'80AAA11C',4:'80AAC12A'}
FORMATS={0:('BC1','sRGB',256,256,1),1:('BC5','linear',256,256,1),2:('BC1','sRGB',512,512,6),3:('RGBA8','linear',256,256,1),4:('RGBA8','linear',256,256,1)}
SAMPLERS=['80AAE177','80AAE177','80AAE176','80AAE177','80AAE177']
SAMPLER_SHAS=['2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb','2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb','0bcdaa82ea0d8588e313f29998f6c7b9166e7d28d40b13d422348d55ae5dc208','2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb','2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb']
CB_RAW=['0000c03f000040bf000040bf000040bf','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','000000000000803f0000803f0000803f','000000000000803f0000000000000000','0000803f0000803f0000000000000000','153a963ccb15283c9e02003c0000803f','00000000000000000000000000000000','00000000a3a2a23d0000a0410000a841']
EXPECTED_USAGE=[('PtrExtendedUserData',1,2),('ImmSampler',1,4),('ImmSampler',2,8),('PtrResourceTable',0,12),('ImmSampler',3,16),('ImmSampler',4,20),('ImmSampler',5,24),('ImmConstBuffer',0,28),('ImmConstBuffer',12,32)]
EXPECTED_IMAGE=[('image_sample',1,2,3),('image_get_lod',2,3,2),('image_sample',0,1,7),('image_sample',4,5,1),('image_sample',3,4,1),('image_sample_l',2,3,15)]
ANCHORS=['v_mad_f32       v4, v4, s0, v6','v_mac_f32       v6, s0, v5','v_sqrt_f32      v5, v5','v_rsq_clamp_f32 v5, v13','v_rsq_clamp_f32 v4, v4','v_mad_legacy_f32 v6, -v9, v5, v6','v_cubema_f32    v5, v6, v13, v11','image_get_lod   v10, v[15:18], s[16:23], s[24:27] dmask:2','image_sample    v[11:13], v[2:5], s[28:35], s[4:7] dmask:7','image_sample    v14, v[2:5], s[36:43], s[44:47]','image_sample    v2, v[2:5], s[48:55], s[12:15]','image_sample_l  v[15:18], v[15:18], s[16:23], s[24:27] dmask:15','v_madak_f32     v4, v19, v4, 0x3f000000','exp             mrt1, v1, v1, v2, v2 compr','exp             mrt0, v1, v1, v0, v0 done compr vm']

def main():
 ap=argparse.ArgumentParser()
 for n in ['material-state','shader-census','image-usage','texture-manifest','disassembly','out']: ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();st=json.loads(a.material_state.read_text());ce=json.loads(a.shader_census.read_text());im=json.loads(a.image_usage.read_text());ma=json.loads(a.texture_manifest.read_text());asm=a.disassembly.read_text();viol=[]
 if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT':viol.append('material state not exact')
 if ce.get('status')!='D1_XUR_ALL_NATIVE_SHADER_DISASSEMBLY_EXACT':viol.append('shader census not exact')
 if im.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':viol.append('image usage not exact')
 if ma.get('visible_material_count')!=54 or ma.get('material_decode_errors') or ma.get('texture_errors'):viol.append('texture manifest not exact/error-free')
 for sh,(native,nsha) in SHADERS.items():
  sr=next((x for x in ce.get('shaders',[]) if x.get('shader')==sh),None)
  if not sr:viol.append('missing shader '+sh);continue
  for k,v in [('native_shader',native),('native_sha256',nsha),('gcn_sha256',GCN_SHA),('gcn_bytes',892),('instruction_count_approx',178)]:
   if sr.get(k)!=v:viol.append(f'{sh} {k} mismatch {sr.get(k)!r}')
  slots=[(x.get('usage_name'),x.get('api_slot'),x.get('start_register')) for x in sr.get('usage',{}).get('slots',[])]
  if slots!=EXPECTED_USAGE:viol.append(f'{sh} usage mismatch')
  ir=next((x for x in im.get('shaders',[]) if x.get('shader')==sh),None)
  if not ir:viol.append('missing image usage '+sh);continue
  if ir.get('image_instruction_count')!=6 or ir.get('used_texture_indices')!=list(range(5)) or ir.get('texture_instruction_counts')!={'0':1,'1':1,'2':2,'3':1,'4':1} or ir.get('unmatched_image_instruction_count')!=0:viol.append(f'{sh} image summary mismatch')
  got=[]
  for row in ir.get('instructions',[]):
   rr=row.get('resources') or [];ss=row.get('samplers') or []
   got.append((row.get('opcode'),rr[0].get('texture_index') if len(rr)==1 else None,ss[0].get('sampler_index') if len(ss)==1 else None,row.get('dmask')))
  if got!=EXPECTED_IMAGE:viol.append(f'{sh} image sequence mismatch: {got!r}')
 for needle in ANCHORS:
  if needle not in asm:viol.append('missing asm anchor '+needle)
 for mh,sh in MEMBERS.items():
  row=(st.get('materials') or {}).get(mh)
  if not row:viol.append('missing material '+mh);continue
  ps=row['ps']
  if ps.get('shader')!=sh:viol.append(f'{mh} PS mismatch')
  if row.get('material_state4_hex')!='00000000':viol.append(f'{mh} state mismatch')
  if ps['tfx_bytecode'].get('bytes_hex')!=TFX or ps.get('tfx_disassembly',{}).get('complete') is not True:viol.append(f'{mh} TFX mismatch')
  if ps.get('tfx_private_constants',{}).get('items') not in ([],None):viol.append(f'{mh} private constants nonempty')
  if [x['raw_hex'] for x in ps['cbuffers']['items']]!=CB_RAW:viol.append(f'{mh} cbuffer mismatch')
  tex={int(x['texture_index']):x['texture'] for x in ps['textures']['items']}
  if tex!=TEXTURES:viol.append(f'{mh} texture map mismatch')
  if [x['first_dword_hex'] for x in ps['samplers']['items']]!=SAMPLERS:viol.append(f'{mh} samplers mismatch')
  if [(r.get('native_sampler') or {}).get('payload_sha256') for r in ps.get('sampler_references',[])]!=SAMPLER_SHAS:viol.append(f'{mh} sampler descriptors mismatch')
 for idx,tag in TEXTURES.items():
  tr=(ma.get('textures') or {}).get(tag)
  if not tr:viol.append('missing texture '+tag);continue
  fmt,cs,w,h,arr=FORMATS[idx];hi=tr.get('header_info') or {}
  if (tr.get('format_name'),tr.get('native_colorspace_hint'),hi.get('width'),hi.get('height'),hi.get('array_size'))!=(fmt,cs,w,h,arr):viol.append(f't{idx} metadata mismatch')
  if idx==2 and len(tr.get('faces') or [])!=6:viol.append('t2 cube topology mismatch')
 if viol:
  out={'schema_version':1,'status':'D1_XUR_PS_808768B7_DATAFLOW_SEMANTICS_PARTIAL','violations':viol};a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 2
 out={'schema_version':1,'status':'D1_XUR_PS_808768B7_DATAFLOW_SEMANTICS_EXACT','shader_headers':sorted(SHADERS),'gcn_sha256':GCN_SHA,'scope_materials':sorted(MEMBERS),'scope_material_count':2,
 'instruction_level_equations':{
 'uv':'uv=attr3.xy','normal_xy':'nx=1.5*t1.r-0.75; ny=1.5*t1.g-0.75','normal_z':'nz=sqrt(saturate(1-nx*nx-ny*ny))','world_normal':'N=normalize(nx*attr1.xyz+ny*attr2.xyz+nz*attr0.xyz)','view_vector':'V=normalize(api12[28:30]-attr4.xyz)','reflection_vector':'R=2*dot(N,V)*N-V=reflect(-V,N)','cube_lod':'L=max(b0[20], image_get_lod(t2,R).y); current b0[20]=0','surface':'C=t0.rgb','alternate_branch':'B=saturate(C-0.25)+b0.c8.rgb*saturate(4*C)','mask_mix':'M=lerp(C,B,t3.r)','reflection_gate':'G=t4.r','reflection':'mrt0.rgb=M + t2.rgb*(t2.a*G)*(M+b0[29]); current b0[29]=1','mrt0_alpha':'mrt0.a=attr0.w','normal_pack':'k=0.375+0.125*G; mrt1.rgb=saturate(0.5+k*N); mrt1.a=b0[41]','normal_pack_current_alpha':'mrt1.a=0.07941176742315292'},
 'promoted_texture_semantics':{'t0':'RGB visible surface source','t1':'BC5 normal XY source','t2':'six-face reflection cube','t3':'single-channel surface branch blend/control input','t4':'single-channel reflection and normal-packing control input'},
 'pixel_shader_dataflow_complete_for_scoped_binary':True,'tfx_producer_semantics_complete':False,'render_state_semantics_complete':False,'portable_material_recreation_complete':False,'violations':[]}
 a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
