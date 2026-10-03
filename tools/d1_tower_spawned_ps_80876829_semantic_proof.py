#!/usr/bin/env python3
"""Fail-closed native dataflow proof for Tower spawned-NPC PS 80876829.

The native pixel arithmetic is closed with TFX c15 kept as an explicit runtime
input. The material's TFX program contains raw D1 opcode 0x4B operand 0x56 and
writes c15 through 0x42; that producer is intentionally not guessed here.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

SHADER='80876829';NATIVE='8087684D'
NATIVE_SHA='fe341576ad022a097e5f8b44560ac56ad4905eebe5b058ee8f1f898b2c5682bb'
GCN_SHA='30c3c7a33c6a786073a21b35c15deceb822462ff22372dba4214fdb720225e29'
MATERIAL='808767DB';STATE='00000000'
TFX_SHA='918b11a566367827930bf5db0378f32d390ccf0de3250d7af255850925d35099'
TEXTURES={0:'8087689D',1:'80876981',2:'8087689E',3:'80AACC28'}
SAMPLERS=['80AAE177','80AAE177','80AAE177','80AAE176']
SAMPLER_SHAS=[
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '0bcdaa82ea0d8588e313f29998f6c7b9166e7d28d40b13d422348d55ae5dc208']
EXPECTED_IMAGE=[
 ('image_sample',2,3,'xy'),('image_sample',0,15,'xyzw'),
 ('image_get_lod',3,2,'y'),('image_sample_l',3,15,'xyzw'),
 ('image_sample',1,7,'xyz')]
CB={0:10.,1:10.,4:2.,5:-1.,20:6.,24:0.,28:-.20000000298023224,29:1.548799991607666,
32:.25,36:.9300000071525574,37:.8999999761581421,38:.7699999809265137,39:1.,
40:2.,44:.5,45:.5,56:.5494505763053894,57:-.09890110790729523,
58:.095238097012043,59:-.1428571492433548,69:.22843138873577118}
ANCHORS=[
 'image_sample    v[6:7], v[2:5]','v_mad_f32       v6, v6, s0, v8',
 'v_cubema_f32    v7, v8, v21, v18','image_sample    v[21:24], v[2:5]',
 'image_get_lod   v4, v[25:28]','image_sample_l  v[25:28], v[25:28]',
 'v_mad_f32       v2, v2, s4, v4','image_sample    v[2:4], v[2:5]',
 'v_madmk_f32     v13, v16, 0x3f170000, v13','v_madmk_f32     v13, v18, 0x3e99a000, v13',
 'v_mac_f32       v21, v2, v11','v_mul_f32       v2, s7, v17',
 'v_mac_f32       v21, v3, v12','v_mul_f32       v2, s20, v7',
 'v_mac_f32       v21, v2, v21','exp             mrt1','exp             mrt0']

def flat(m):return [float(v) for r in m['ps']['cbuffers']['items'] for v in r['value']]
def tex(m):return {int(x['texture_index']):x['texture'].upper() for x in m['ps']['textures']['items']}
def eq(a,b):return math.isclose(float(a),float(b),rel_tol=0,abs_tol=2e-7)

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--extract-report',type=Path,required=True);ap.add_argument('--image-usage',type=Path,required=True);ap.add_argument('--material-state',type=Path,required=True);ap.add_argument('--disassembly',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 ext=json.loads(a.extract_report.read_text());iu=json.loads(a.image_usage.read_text());st=json.loads(a.material_state.read_text());asm=a.disassembly.read_text();v=[]
 er=next((x for x in ext.get('shaders',[]) if x.get('shader')==SHADER),None)
 if ext.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or not er:v.append('extract not exact/present')
 else:
  for k,z in [('native_shader',NATIVE),('native_sha256',NATIVE_SHA),('gcn_sha256',GCN_SHA),('gcn_bytes',1112)]:
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
  ops=ps.get('tfx_disassembly',{}).get('ops',[])
  raw4b=[x.get('raw_hex') for x in ops if x.get('name')=='Unk4b']
  targets=[x.get('d1_unk42_u8') for x in ops if x.get('name')=='Unk42']
  if raw4b!=['4B56']:v.append(f'0x4B operand drift {raw4b!r}')
  if targets!=[15]:v.append(f'TFX output target drift {targets!r}')
  if tex(m)!=TEXTURES:v.append(f'texture map mismatch {tex(m)!r}')
  if [x['first_dword_hex'] for x in ps['samplers']['items']]!=SAMPLERS:v.append('sampler tags mismatch')
  if [(x.get('native_sampler') or {}).get('payload_sha256') for x in ps.get('sampler_references',[])]!=SAMPLER_SHAS:v.append('sampler SHA mismatch')
  vals=flat(m)
  for i,z in CB.items():
   if i>=len(vals) or not eq(vals[i],z):v.append(f'b0[{i}] mismatch')
 for q in ANCHORS:
  if q not in asm:v.append('missing native anchor '+q)
 if v:
  out={'schema_version':1,'status':'D1_TOWER_SPAWNED_PS_80876829_NATIVE_DATAFLOW_PARTIAL','violations':v};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 2
 out={
 'schema_version':1,'status':'D1_TOWER_SPAWNED_PS_80876829_NATIVE_DATAFLOW_EXACT','violations':[],
 'shader':SHADER,'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'source_material':MATERIAL,
 'aggregate_spawned_pixel_shader_triangle_impact':12390,
 'exact_inputs':{'texture_bindings':{str(k):z for k,z in TEXTURES.items()},'tfx_program_sha256':TFX_SHA,'tfx_raw_0x4b':'4B56','tfx_output_target':15,'api12_dependency':'camera/view position','current_material_b0_values':{str(k):z for k,z in CB.items()}},
 'instruction_level_equations':{
  'base_uv':'uv=attr3.xy',
  'normal':'nx=b0[4]*t2.r+b0[5]; ny=b0[4]*t2.g+b0[5]; nz=sqrt(saturate(1-nx^2-ny^2)); N=normalize(nx*attr1+ny*attr2+nz*attr0)',
  'view_and_reflection':'V=normalize(api12_camera_position-attr4.xyz); R=2*dot(N,V)*N-V',
  'cube_lod_floor':'Lfloor=b0[20]+t0.a*(b0[24]-b0[20]); current Lfloor=6*(1-t0.a)',
  'cube':'cube=sample_l(t3,R,max(image_get_lod(t3,R).y,Lfloor))',
  'detail_uv':'uv1=(b0[2]+b0[0]*uv.x,b0[3]+b0[1]*uv.y); current uv1=10*uv',
  'palette_surface':'P=saturate(t0.rgb-0.25)+sample(t1,uv1).rgb*saturate(4*t0.rgb)',
  'cube_tint':'T=2*cube.rgb*b0[36:38]',
  'cube_luminance':'Y=0.300048828125*T.r+0.58984375*T.g+0.1099853515625*T.b',
  'cube_saturation':'D=Y+b0[32]*(T-Y); current b0[32]=0.25',
  'cube_alpha_weight':'A=b0[39]*cube.a*(b0[28]+b0[29]*t0.a)',
  'cube_surface_factor':'H=b0[45]+b0[44]*P',
  'base_reflected_color':'O=P+A*D*H',
  'view_falloff':'F2=(1-dot(N,V))^2',
  'distance_gate':'Gd=saturate(b0[59]+b0[58]*length(api12_camera_position-attr4.xyz))',
  'runtime_c15_add':'mrt0.rgb=O+c15.rgb*(F2*Gd)',
  'mrt0_alpha':'mrt0.a=attr0.w',
  'mrt1_rgb':'k=0.375+0.125*t0.a; mrt1.rgb=saturate(0.5+k*N)',
  'mrt1_alpha':'mrt1.a=b0[69]'},
 'promoted_texture_semantics':{
  't0':{'tag':TEXTURES[0],'role':'surface_rgba_primary','proof':'RGB drives palette surface; alpha drives cube LOD and reflection strength/normal pack'},
  't1':{'tag':TEXTURES[1],'role':'palette_surface_rgb_multiplier','proof':'RGB at 10x UV multiplies saturate(4*t0.rgb) in the exact surface equation'},
  't2':{'tag':TEXTURES[2],'role':'primary_normal_xy','proof':'XY reconstructs tangent-space normal'},
  't3':{'tag':TEXTURES[3],'role':'environment_cubemap_rgba','proof':'cube RGB/alpha enter reflected color path'}},
 'runtime_frontiers':{'tfx_raw_0x4b_0x56_semantics_complete':False,'tfx_c15_producer_semantics_complete':False,'native_pixel_dataflow_complete_given_c15':True,'portable_material_recreation_complete':False,'deferred_framebuffer_equivalence_closed':False},
 'policy':'Exact native pixel arithmetic with c15 preserved as an unresolved runtime TFX product. 0x4B/0x56 is not assigned a guessed semantic.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ('status','shader','aggregate_spawned_pixel_shader_triangle_impact','runtime_frontiers')},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
