#!/usr/bin/env python3
"""Fail-closed native dataflow proof for Tower spawned-NPC PS 809DF769."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

SHADER='809DF769'
NATIVE='809DF76A'
NATIVE_SHA='65fc9449d292700983fc635587f4daf7b31417ff98f48da7bedfe5d8ba72f9e7'
GCN_SHA='be3b16685c5615c0bcf7f480b38db9f92ed762aeaafe0c5435031d2e9a4bfcc9'
MATERIAL='80C9923D'
STATE='00000000'
TFX_SHA='c2da8a898b249e495fc5a77e38b0a1d399eb6f8c4df96c5912fe86b732623092'
TEXTURES={0:'8087696F',1:'80876970',2:'80AACC28',3:'80876971'}
SAMPLERS=['80AAE177','80AAE177','80AAE176','80AAE177']
SAMPLER_SHAS=[
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '0bcdaa82ea0d8588e313f29998f6c7b9166e7d28d40b13d422348d55ae5dc208',
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
]
EXPECTED_USAGE=[
 ('PtrExtendedUserData',1,2),('ImmResource',0,4),('ImmSampler',1,12),
 ('ImmResource',1,16),('ImmResource',2,24),('ImmResource',3,32),
 ('ImmSampler',2,40),('ImmSampler',3,44),('ImmSampler',4,48),
 ('ImmConstBuffer',0,52),('ImmConstBuffer',12,56),
]
EXPECTED_IMAGE=[
 ('image_sample',1,3,'xy'),('image_sample',0,15,'xyzw'),
 ('image_get_lod',2,2,'y'),('image_sample_l',2,7,'xyz'),
 ('image_sample',3,1,'x'),
]
CB={
 0:2.0,1:-1.0,
 16:3.0,20:0.0,
 24:0.5842411518096924,25:0.6680784225463867,26:0.6680784225463867,
 28:1.0,
 32:0.0,33:1.0,34:1.0,
 36:0.15000000596046448,
 40:0.1171594113111496,41:0.07694324105978012,42:0.07219332456588745,
 49:0.3813726007938385,
}
ANCHORS=[
 'image_sample    v[4:5], v[2:5]',
 'v_mad_f32       v4, v4, s0, v6',
 'v_sqrt_f32      v5, v5',
 'v_cubema_f32    v5, v6, v13, v11',
 'image_sample    v[10:13], v[2:5]',
 'image_get_lod   v14, v[16:19]',
 'image_sample_l  v[14:16], v[16:19]',
 'image_sample    v2, v[2:5]',
 'v_madmk_f32     v3, v5, 0x3f170a3d, v3',
 'v_madmk_f32     v3, v6, 0x3e99999a, v3',
 'v_mad_f32       v14, v14, s0, -v3',
 'v_mac_f32       v18, s4, v5',
 'v_subrev_f32    v14, v10, v18',
 'v_mac_f32       v10, v2, v16',
 'v_mac_f32       v2, s9, v5',
 'exp             mrt1',
 'exp             mrt0',
]

def flat(m): return [float(v) for r in m['ps']['cbuffers']['items'] for v in r['value']]
def tex(m): return {int(x['texture_index']):x['texture'].upper() for x in m['ps']['textures']['items']}
def close(a,b): return math.isclose(float(a),float(b),rel_tol=0,abs_tol=2e-7)

def main()->int:
 ap=argparse.ArgumentParser()
 ap.add_argument('--extract-report',type=Path,required=True)
 ap.add_argument('--image-usage',type=Path,required=True)
 ap.add_argument('--material-state',type=Path,required=True)
 ap.add_argument('--disassembly',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 ext=json.loads(a.extract_report.read_text()); iu=json.loads(a.image_usage.read_text())
 st=json.loads(a.material_state.read_text()); asm=a.disassembly.read_text(); viol=[]
 er=next((x for x in ext.get('shaders',[]) if x.get('shader')==SHADER),None)
 if ext.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or not er: viol.append('shader extract not exact/present')
 else:
  for k,v in [('native_shader',NATIVE),('native_sha256',NATIVE_SHA),('gcn_sha256',GCN_SHA),('gcn_bytes',988)]:
   if er.get(k)!=v: viol.append(f'{k} mismatch')
  usage=[(x.get('usage_name'),x.get('api_slot'),x.get('start_register')) for x in er.get('usage',{}).get('slots',[])]
  if usage!=EXPECTED_USAGE: viol.append(f'usage mismatch {usage!r}')
 ir=next((x for x in iu.get('shaders',[]) if x.get('shader')==SHADER),None)
 if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or not ir: viol.append('image usage not exact/present')
 else:
  seq=[]
  for x in ir.get('instructions',[]):
   rr=x.get('resources') or []
   seq.append((x.get('opcode'),rr[0].get('texture_index') if len(rr)==1 else None,x.get('dmask'),x.get('dmask_channels')))
  if seq!=EXPECTED_IMAGE: viol.append(f'image sequence mismatch {seq!r}')
  if ir.get('unmatched_image_instruction_count')!=0: viol.append('unmatched image instruction')
 if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'): viol.append('material state not exact')
 m=(st.get('materials') or {}).get(MATERIAL)
 if not m or m.get('error'): viol.append('material unresolved')
 else:
  ps=m['ps']
  if m.get('material_state4_hex')!=STATE or ps.get('shader')!=SHADER: viol.append('state/shader mismatch')
  if ps.get('tfx_program_sha256')!=TFX_SHA or not ps.get('tfx_disassembly',{}).get('complete'): viol.append('TFX mismatch/incomplete')
  if any(x.get('name')=='Unk42' for x in ps.get('tfx_disassembly',{}).get('ops',[])): viol.append('unexpected TFX output write')
  if tex(m)!=TEXTURES: viol.append(f'texture map mismatch {tex(m)!r}')
  if [x['first_dword_hex'] for x in ps['samplers']['items']]!=SAMPLERS: viol.append('sampler tags mismatch')
  shas=[(x.get('native_sampler') or {}).get('payload_sha256') for x in ps.get('sampler_references',[])]
  if shas!=SAMPLER_SHAS: viol.append('sampler payload SHA sequence mismatch')
  vals=flat(m)
  for i,v in CB.items():
   if i>=len(vals) or not close(vals[i],v): viol.append(f'b0[{i}] mismatch')
 for q in ANCHORS:
  if q not in asm: viol.append('missing native anchor '+q)
 if viol:
  out={'schema_version':1,'status':'D1_TOWER_SPAWNED_PS_809DF769_NATIVE_DATAFLOW_PARTIAL','violations':viol}
  a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2)); return 2
 out={
  'schema_version':1,'status':'D1_TOWER_SPAWNED_PS_809DF769_NATIVE_DATAFLOW_EXACT','violations':[],
  'shader':SHADER,'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,
  'source_material':MATERIAL,'aggregate_spawned_pixel_shader_triangle_impact':17279,
  'exact_inputs':{'texture_bindings':{str(k):v for k,v in TEXTURES.items()},'material_state4_hex':STATE,'tfx_program_sha256':TFX_SHA,'api12_dependency':'camera/view position','current_material_b0_values':{str(k):v for k,v in CB.items()}},
  'instruction_level_equations':{
   'normal_xy':'nx=b0[0]*t1.r+b0[1]; ny=b0[0]*t1.g+b0[1]; current nx=2*t1.r-1 and ny=2*t1.g-1',
   'normal_z':'nz=sqrt(saturate(1-nx*nx-ny*ny))',
   'world_normal':'N=normalize(nx*attr1.xyz+ny*attr2.xyz+nz*attr0.xyz)',
   'view_vector':'V=normalize(api12_camera_position-attr4.xyz)',
   'reflection_vector':'R=2*dot(N,V)*N-V',
   'cube_lod_floor':'Lfloor=b0[16]+t0.a*(b0[20]-b0[16]); current Lfloor=3*(1-t0.a)',
   'cube_sample':'cube=sample_l(t2,R,max(image_get_lod(t2,R).y,Lfloor)).rgb',
   'cube_tint':'T=b0[24:26]*cube',
   'cube_luminance':'Y=0.30*T.r+0.59*T.g+0.11*T.b',
   'cube_saturation':'D=Y+b0[28]*(T-Y); current b0[28]=1 so D=T',
   'surface_palette':'P=saturate(t0.rgb-0.25)+b0[40:42]*saturate(4*t0.rgb)',
   'surface_mix':'M=lerp(t0.rgb,P,t3.r)',
   'mrt0_rgb':'mrt0.rgb=M*(b0[34]+b0[32]*D)+b0[33]*b0[36]*D; current mrt0.rgb=M+0.15*D',
   'mrt0_alpha':'mrt0.a=attr0.w',
   'mrt1_rgb':'k=0.375+0.125*t0.a; mrt1.rgb=saturate(0.5+k*N)',
   'mrt1_alpha':'mrt1.a=b0[49]',
  },
  'promoted_texture_semantics':{
   't0':{'tag':TEXTURES[0],'role':'surface_rgba_primary','proof':'RGB drives surface/palette mix; alpha drives cube LOD and normal packing'},
   't1':{'tag':TEXTURES[1],'role':'primary_normal_xy','proof':'XY enters exact tangent-space normal reconstruction'},
   't2':{'tag':TEXTURES[2],'role':'environment_cubemap_rgb','proof':'native cube coordinate ops plus get_lod/sample_l feed final RGB'},
   't3':{'tag':TEXTURES[3],'role':'surface_palette_mix_scalar_r','proof':'native x sample is the exact lerp factor between t0 and its palette transform'},
  },
  'gates':{'native_current_material_color_dataflow_closed':True,'runtime_tfx_output_dependency':False,'portable_material_recreation_complete':False,'deferred_framebuffer_equivalence_closed':False},
  'policy':'Exact current-retail native pixel dataflow. High-level PBR equivalence is not inferred.'
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ('status','shader','aggregate_spawned_pixel_shader_triangle_impact','gates')},indent=2));return 0
if __name__=='__main__': raise SystemExit(main())
