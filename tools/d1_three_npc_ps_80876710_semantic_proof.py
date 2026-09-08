#!/usr/bin/env python3
"""Fail-closed native/current-state semantic proof for D1 PS4 PS 80876710.

This family looked similar to reflection-bearing surface shaders by opcode shape,
but its exact native dataflow has no cubemap/reflection path. Color is the
componentwise product of two RGB samples times the native scale constant.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

SHADER='80876710'
NATIVE='8087675F'
NATIVE_SHA='996022ed7a7a886b0433813527330b072c3d4dd343d5afe170377184c47b0e1f'
GCN_SHA='18718a2e21438926187f14bf3aaf82507cf747f1f95c4ea8036ca762cdc0faf2'
MATERIALS=['808766AE','808766B7']
TEXTURES={0:'80876703',1:'80AAF743',2:'80876704',3:'80AAF8BC',4:'80876705'}
TFX_SHA='902e8371bb2fc00f416923ef17f25e5237507d3d7f2130e42a82fa10403aec99'
TFX_HEX='4900472149014722490247234903472449044725'
CB_RAW=[
 '00000041000000410000000000000000',
 '00000040000080bf000080bf000080bf',
 '00000041000000410000000000000000',
 '00000040000080bf000080bf000080bf',
 '00000000000000000000000000000000',
 '00000000ebea2a3f00002a4300002b43',
]
SAMPLER='80AAE177'
SAMPLER_SHA='2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb'
STATE='00000000'
EXPECTED_USAGE=[
 ('PtrExtendedUserData',1,2),('ImmSampler',1,4),('ImmSampler',2,8),
 ('PtrResourceTable',0,12),('ImmSampler',3,16),('ImmSampler',4,20),
 ('ImmSampler',5,24),('ImmConstBuffer',0,28),
]
EXPECTED_IMAGE=[
 ('image_sample',2,3,3),('image_sample',3,4,3),('image_sample',4,5,8),
 ('image_sample',0,1,7),('image_sample',1,2,7),
]
ANCHORS=[
 'v_mac_f32       v4, s20, v6','v_mac_f32       v5, s21, v7',
 'image_sample    v[8:9], v[6:9], s[24:31], s[32:35] dmask:3',
 'image_sample    v[4:5], v[4:7], s[36:43], s[44:47] dmask:3',
 'image_sample    v2, v[6:9], s[24:31], s[0:3] dmask:8',
 'image_sample    v[12:14], v[6:9], s[32:39], s[4:7] dmask:7',
 'image_sample    v[15:17], v[15:18], s[40:47], s[8:11] dmask:7',
 'v_add_f32       v4, -v4, 1.0 clamp','v_sqrt_f32      v4, v4',
 'v_rsq_clamp_f32 v4, v6','v_rsq_clamp_f32 v7, v7',
 'v_mul_f32       v6, v12, v15','v_mul_f32       v7, v13, v16','v_mul_f32       v8, v14, v17',
 'v_mul_f32       v5, 0x40930885, v6','v_mul_f32       v6, 0x40930885, v7','v_mul_f32       v7, 0x40930885, v8',
 's_buffer_load_dword s0, s[16:19], 0x15',
 'exp             mrt1, v1, v1, v2, v2 compr','exp             mrt0, v1, v1, v0, v0 done compr vm',
]
K=4.594789981842041

def close(a,b,eps=2e-7): return math.isclose(float(a),float(b),rel_tol=0.0,abs_tol=eps)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--extract-report',type=Path,required=True);ap.add_argument('--image-usage',type=Path,required=True)
 ap.add_argument('--material-state',type=Path,required=True);ap.add_argument('--disassembly',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args();ext=json.loads(a.extract_report.read_text());iu=json.loads(a.image_usage.read_text());st=json.loads(a.material_state.read_text());asm=a.disassembly.read_text();viol=[]
 if ext.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT':viol.append('extract checkpoint not exact')
 if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':viol.append('image usage checkpoint not exact')
 if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):viol.append('material state checkpoint not exact')
 er=next((x for x in ext.get('shaders',[]) if x.get('shader')==SHADER),None)
 if not er:viol.append('shader extraction row absent')
 else:
  for k,v in [('native_shader',NATIVE),('native_sha256',NATIVE_SHA),('gcn_sha256',GCN_SHA),('gcn_bytes',580)]:
   if er.get(k)!=v:viol.append(f'{k} mismatch {er.get(k)!r}')
  slots=[(x.get('usage_name'),x.get('api_slot'),x.get('start_register')) for x in er.get('usage',{}).get('slots',[])]
  if slots!=EXPECTED_USAGE:viol.append(f'user-data usage mismatch {slots!r}')
 ir=next((x for x in iu.get('shaders',[]) if x.get('shader')==SHADER),None)
 if not ir:viol.append('image usage row absent')
 else:
  got=[]
  for x in ir.get('instructions',[]):
   rr=x.get('resources') or [];ss=x.get('samplers') or []
   got.append((x.get('opcode'),rr[0].get('texture_index') if len(rr)==1 else None,ss[0].get('sampler_index') if len(ss)==1 else None,x.get('dmask')))
  if got!=EXPECTED_IMAGE:viol.append(f'image sequence mismatch {got!r}')
  if ir.get('unmatched_image_instruction_count')!=0:viol.append('unmatched image instruction')
 for needle in ANCHORS:
  if needle not in asm:viol.append('missing native anchor '+needle)
 sm=sorted((st.get('shader_materials',{}).get('ps',{}) or {}).get(SHADER,[]))
 if sm!=sorted(MATERIALS):viol.append(f'material set mismatch {sm!r}')
 ref=None
 for mh in MATERIALS:
  m=st.get('materials',{}).get(mh)
  if not m or m.get('error'):viol.append(f'{mh}: unresolved');continue
  ps=m['ps']
  if m.get('material_state4_hex')!=STATE:viol.append(f'{mh}: state mismatch')
  if ps.get('shader')!=SHADER:viol.append(f'{mh}: shader mismatch')
  if ps.get('tfx_program_sha256')!=TFX_SHA or ps['tfx_bytecode'].get('bytes_hex')!=TFX_HEX or not ps.get('tfx_disassembly',{}).get('complete'):viol.append(f'{mh}: TFX mismatch/incomplete')
  if ps['tfx_private_constants']['items']:viol.append(f'{mh}: expected no private TFX constants')
  tex={int(x['texture_index']):x['texture'].upper() for x in ps['textures']['items']}
  if tex!=TEXTURES:viol.append(f'{mh}: texture map mismatch {tex!r}')
  if [x['raw_hex'] for x in ps['cbuffers']['items']]!=CB_RAW:viol.append(f'{mh}: full b0 payload mismatch')
  if [x['first_dword_hex'] for x in ps['samplers']['items']]!=[SAMPLER]*5:viol.append(f'{mh}: sampler tags mismatch')
  shas=[(r.get('native_sampler') or {}).get('payload_sha256') for r in ps.get('sampler_references',[])]
  if shas!=[SAMPLER_SHA]*5:viol.append(f'{mh}: native sampler descriptors mismatch')
  vals=[float(v) for row in ps['cbuffers']['items'] for v in row['value']]
  expected={0:8,1:8,4:2,5:-1,8:8,9:8,12:2,13:-1,21:0.6676470637321472}
  if len(vals)!=24:viol.append(f'{mh}: expected 24 b0 dwords')
  else:
   for i,v in expected.items():
    if not close(vals[i],v):viol.append(f'{mh}: b0[{i}] mismatch {vals[i]!r}')
  semantic=(ps['tfx_bytecode']['bytes_hex'],tuple(x['raw_hex'] for x in ps['cbuffers']['items']),tuple(sorted(tex.items())),tuple(x['first_dword_hex'] for x in ps['samplers']['items']))
  if ref is None:ref=semantic
  elif semantic!=ref:viol.append(f'{mh}: semantic payload differs')
 if viol:
  out={'schema_version':1,'status':'D1_TOWER_PS_80876710_CURRENT_STATE_COLOR_SEMANTICS_PARTIAL','violations':viol};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 2
 out={
  'schema_version':1,'status':'D1_TOWER_PS_80876710_CURRENT_STATE_COLOR_SEMANTICS_EXACT','violations':[],
  'shader':SHADER,'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'scope_materials':MATERIALS,'scope_material_count':2,'visible_primitive_count':6,
  'exact_inputs':{'texture_bindings_t0_t4':{str(k):v for k,v in TEXTURES.items()},'material_state4_hex':STATE,'tfx_program_sha256':TFX_SHA,'material_cbuffer_raw_hex':CB_RAW},
  'instruction_level_equations':{
   'uv':'uv=attr3.xy','color_detail_uv':'uvC=float2(b0[0]*uv.x+b0[2],b0[1]*uv.y+b0[3]); current uvC=8*uv','normal_detail_uv':'uvN=float2(b0[8]*uv.x+b0[10],b0[9]*uv.y+b0[11]); current uvN=8*uv',
   'normal_xy':'nx=b0[4]*t2.r+b0[5]+b0[13]+b0[12]*t3.r; ny=b0[4]*t2.g+b0[5]+b0[13]+b0[12]*t3.g','normal_xy_current':'nx=2*t2.r+2*t3.r-2; ny=2*t2.g+2*t3.g-2','normal_z':'nz=sqrt(saturate(1-nx*nx-ny*ny))','world_normal':'N=normalize(nx*attr1.xyz+ny*attr2.xyz+nz*attr0.xyz)',
   'surface_product':'C=t0.rgb*t1.rgb','mrt0_rgb':f'mrt0.rgb={K}*C','mrt0_alpha':'mrt0.a=attr0.w','normal_pack':'k=0.375+0.125*t4.a; mrt1.rgb=saturate(0.5+k*N); mrt1.a=b0[21]','normal_pack_current_alpha':'mrt1.a=0.6676470637321472'},
  'promoted_texture_semantics':{
   't0':{'tag':TEXTURES[0],'role':'surface_rgb_primary','proof':'native RGB is multiplied componentwise into MRT0 color'},'t1':{'tag':TEXTURES[1],'role':'surface_rgb_detail_multiplier','proof':'native RGB sampled at 8x UV is multiplied componentwise into MRT0 color'},
   't2':{'tag':TEXTURES[2],'role':'primary_normal_xy','proof':'native xy enters signed normal reconstruction'},'t3':{'tag':TEXTURES[3],'role':'detail_normal_xy','proof':'native xy at 8x UV enters same normal reconstruction'},'t4':{'tag':TEXTURES[4],'role':'normal_pack_scalar_alpha','proof':'native w only changes deferred normal packing scale and never enters MRT0 RGB'}},
  'critical_correction':'80876710 is not a reflection-bearing material despite opcode-shape similarity. It has no cubemap sample. Its exact RGB is the scaled product of t0.rgb and t1.rgb.',
  'gates':{'current_material_native_color_dataflow_closed':True,'portable_color_source_closed':True,'portable_blender_recreation_complete':False,'deferred_framebuffer_equivalence_closed':False},
  'policy':'Exact current-state/native color semantics only; no generic PBR equivalence is promoted.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ('status','visible_primitive_count','critical_correction','gates')},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
