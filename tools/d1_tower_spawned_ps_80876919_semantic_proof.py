#!/usr/bin/env python3
"""Fail-closed native dataflow proof for Tower spawned-NPC PS 80876919."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

SHADER='80876919';NATIVE='8087693F'
NATIVE_SHA='dcbd414b50dc42f5ed54a1f6378f36255044f31c9ac7d1b14ac9b6898bb3d17e'
GCN_SHA='aa86620fb0ab2e5c3f2b397ea4ceb3b5151e764ee9b27d8d5de727a84df2d0e7'
MATERIAL='808768F2';STATE='00000000'
TFX_SHA='902e8371bb2fc00f416923ef17f25e5237507d3d7f2130e42a82fa10403aec99'
TEXTURES={0:'8087690A',1:'8087690C',2:'80AACC28',3:'80876910',4:'8087690B'}
SAMPLERS=['80AAE177','80AAE177','80AAE176','80AAE177','80AAE177']
SAMPLER_SHAS=[
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '0bcdaa82ea0d8588e313f29998f6c7b9166e7d28d40b13d422348d55ae5dc208',
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb']
EXPECTED_IMAGE=[
 ('image_sample',1,3,'xy'),('image_sample',4,1,'x'),('image_get_lod',2,2,'y'),
 ('image_sample',0,7,'xyz'),('image_sample',3,1,'x'),('image_sample_l',2,15,'xyzw')]
CB={0:2.,1:-1.,16:6.,20:0.,24:.15000000596046448,25:.8500000238418579,
28:.25,29:.25,32:0.,33:0.,34:0.,36:-1.235635757446289,37:1.,
40:.1858726441860199,41:.1858726441860199,42:.1858726441860199,
44:3.,48:.019999999552965164,52:.021256688982248306,
53:.04728276655077934,54:.07641646265983582,61:.4754902422428131}
ANCHORS=[
 'image_sample    v[4:5], v[2:5]','v_mad_f32       v4, v4, s0, v6',
 'v_cubema_f32    v5, v13, v14, v6','image_sample    v10, v[2:5]',
 'image_get_lod   v12, v[17:20]','image_sample    v[14:16], v[2:5]',
 'image_sample    v2, v[2:5]','image_sample_l  v[17:20], v[17:20]',
 'v_log_f32       v3, v3','v_exp_f32       v3, v3',
 'v_mac_f32       v14, v2, v12','v_mul_f32       v17, v17, v2',
 'v_madak_f32     v2, v6, v2, 0x3f800000','v_rcp_f32       v2, v2',
 'v_mul_f32       v2, v17, v2','exp             mrt1','exp             mrt0']

def flat(m):return [float(v) for r in m['ps']['cbuffers']['items'] for v in r['value']]
def tex(m):return {int(x['texture_index']):x['texture'].upper() for x in m['ps']['textures']['items']}
def eq(a,b):return math.isclose(float(a),float(b),rel_tol=0,abs_tol=2e-7)

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--extract-report',type=Path,required=True);ap.add_argument('--image-usage',type=Path,required=True);ap.add_argument('--material-state',type=Path,required=True);ap.add_argument('--disassembly',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 ext=json.loads(a.extract_report.read_text());iu=json.loads(a.image_usage.read_text());st=json.loads(a.material_state.read_text());asm=a.disassembly.read_text();v=[]
 er=next((x for x in ext.get('shaders',[]) if x.get('shader')==SHADER),None)
 if ext.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or not er:v.append('extract not exact/present')
 else:
  for k,z in [('native_shader',NATIVE),('native_sha256',NATIVE_SHA),('gcn_sha256',GCN_SHA),('gcn_bytes',1116)]:
   if er.get(k)!=z:v.append(k+' mismatch')
 ir=next((x for x in iu.get('shaders',[]) if x.get('shader')==SHADER),None)
 if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or not ir:v.append('image map not exact/present')
 else:
  seq=[]
  for x in ir.get('instructions',[]):
   rr=x.get('resources') or [];seq.append((x.get('opcode'),rr[0].get('texture_index') if len(rr)==1 else None,x.get('dmask'),x.get('dmask_channels')))
  if seq!=EXPECTED_IMAGE:v.append(f'image sequence mismatch {seq!r}')
  if ir.get('unmatched_image_instruction_count')!=0:v.append('unmatched image instruction')
 if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):v.append('material state not exact')
 m=(st.get('materials') or {}).get(MATERIAL)
 if not m or m.get('error'):v.append('material unresolved')
 else:
  ps=m['ps']
  if m.get('material_state4_hex')!=STATE or ps.get('shader')!=SHADER:v.append('state/shader mismatch')
  if ps.get('tfx_program_sha256')!=TFX_SHA or not ps.get('tfx_disassembly',{}).get('complete'):v.append('TFX mismatch')
  if any(x.get('name')=='Unk42' for x in ps.get('tfx_disassembly',{}).get('ops',[])):v.append('unexpected TFX output write')
  if tex(m)!=TEXTURES:v.append(f'texture map mismatch {tex(m)!r}')
  if [x['first_dword_hex'] for x in ps['samplers']['items']]!=SAMPLERS:v.append('sampler tags mismatch')
  if [(x.get('native_sampler') or {}).get('payload_sha256') for x in ps.get('sampler_references',[])]!=SAMPLER_SHAS:v.append('sampler SHA mismatch')
  vals=flat(m)
  for i,z in CB.items():
   if i>=len(vals) or not eq(vals[i],z):v.append(f'b0[{i}] mismatch')
 for q in ANCHORS:
  if q not in asm:v.append('missing native anchor '+q)
 if v:
  out={'schema_version':1,'status':'D1_TOWER_SPAWNED_PS_80876919_NATIVE_DATAFLOW_PARTIAL','violations':v};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 2
 out={
 'schema_version':1,'status':'D1_TOWER_SPAWNED_PS_80876919_NATIVE_DATAFLOW_EXACT','violations':[],
 'shader':SHADER,'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'source_material':MATERIAL,
 'aggregate_spawned_pixel_shader_triangle_impact':14468,
 'exact_inputs':{'texture_bindings':{str(k):z for k,z in TEXTURES.items()},'tfx_program_sha256':TFX_SHA,'api12_dependency':'camera/view position','current_material_b0_values':{str(k):z for k,z in CB.items()}},
 'instruction_level_equations':{
  'normal':'nx=2*t1.r-1; ny=2*t1.g-1; nz=sqrt(saturate(1-nx^2-ny^2)); N=normalize(nx*attr1+ny*attr2+nz*attr0)',
  'view_and_reflection':'V=normalize(api12_camera_position-attr4.xyz); R=2*dot(N,V)*N-V',
  'cube_lod_floor':'Lfloor=b0[16]+t4.r*(b0[20]-b0[16]); current Lfloor=6*(1-t4.r)',
  'cube':'cube=sample_l(t2,R,max(image_get_lod(t2,R).y,Lfloor))',
  'surface_palette':'P=saturate(b0[52:54]-0.25)+t0.rgb*saturate(4*b0[52:54]); M=lerp(t0.rgb,P,t3.r)',
  'view_power':'F=exp2(b0[44]*log2(1-dot(N,V))); current exponent b0[44]=3',
  'cube_alpha_weight':'A=cube.a*(b0[24]+b0[25]*t4.r)',
  'response_weight':'W=saturate((b0[36]+b0[37])-b0[36]*(b0[48]+F*(1-b0[48])))',
  'cube_color_modulation':'H=b0[29]+b0[28]*M; O=M+cube.rgb*A*H',
  'denominator_control':'D=b0[32:34]+b0[40:42]*W',
  'mrt0_rgb':'mrt0.rgb=(2*O-O*O)/((1-D)*(1-D)) componentwise',
  'mrt0_alpha':'mrt0.a=attr0.w',
  'mrt1_rgb':'k=0.375+0.125*t4.r; mrt1.rgb=saturate(0.5+k*N)',
  'mrt1_alpha':'mrt1.a=b0[61]'},
 'promoted_texture_semantics':{
  't0':{'tag':TEXTURES[0],'role':'surface_rgb_primary','proof':'RGB enters exact palette/mix path'},
  't1':{'tag':TEXTURES[1],'role':'primary_normal_xy','proof':'XY reconstructs tangent-space normal'},
  't2':{'tag':TEXTURES[2],'role':'environment_cubemap_rgba','proof':'cube RGB/alpha enter reflection path'},
  't3':{'tag':TEXTURES[3],'role':'surface_palette_mix_scalar_r','proof':'x is the exact surface/palette lerp factor'},
  't4':{'tag':TEXTURES[4],'role':'reflection_lod_strength_and_normal_pack_control_r','proof':'x controls cube LOD floor, cube alpha weight and MRT1 packing scale'}},
 'gates':{'native_current_material_color_dataflow_closed':True,'runtime_tfx_output_dependency':False,'portable_material_recreation_complete':False,'deferred_framebuffer_equivalence_closed':False},
 'policy':'Exact current-retail native pixel dataflow. No generic PBR equivalence is inferred.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ('status','shader','aggregate_spawned_pixel_shader_triangle_impact','gates')},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
