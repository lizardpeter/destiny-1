#!/usr/bin/env python3
"""Fail-closed current-state semantic proof for D1 PS4 pixel shader 809D8363.

For the two scoped materials the exact CB0 state collapses the shader's sampled
surface-color branches to zero. Neither sampled texture contributes to MRT0 RGB
under this exact state. The surviving RGB is the authored CB0[40:42] tint scaled
by a view/normal response factor. This is an exact current-state statement, not
a global claim that other hypothetical constant states of this native program
would ignore the textures.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

SHADER='809D8363';NATIVE='809D83AA'
NATIVE_SHA='bc6afe9c70f0c25cf24d75f469eac2c7876b9e129d48f152b9365c301af61538'
GCN_SHA='91dc3ecf67913f2b29e641b39e2b63f4d350106d8a92e1ff759569dddcfb4e45'
MATERIALS=['80C885F5','80C88603'];TEXTURES={0:'80AB04CD',1:'80C8866E'}
TFX_SHA='112c5733eda8b769a048ce74a352be05d982d8a4887dd35056ce9db5c86f55d1';STATE='00000000'
EXPECTED_IMAGE=[('image_sample',0,7,'xyz'),('image_sample',1,1,'x')]
CB={
  0:0.0,1:0.0,2:0.0,3:0.0,4:4.0,5:4.0,
  32:0.0,33:0.0,34:0.0,35:1.0,
  36:-1.5649452209472656,37:1.0,
  40:0.06020631641149521,41:0.082128144800663,42:0.09552287310361862,
  56:0.0,57:0.0,58:0.0,
  69:0.028431374579668045,73:0.08725490421056747,
}
ANCHORS=[
 'v_cmp_gt_f32    s[0:1], v12, 1.0','s_and_saveexec_b64 s[20:21], s[0:1]',
 's_buffer_load_dwordx4 s[24:27], s[16:19], 0x0','image_sample    v[8:10], v[8:11]',
 'image_sample    v2, v[11:14]','s_buffer_load_dword s4, s[16:19], 0x49',
 's_buffer_load_dword s4, s[16:19], 0x45','v_mul_f32       v8, 0x40930885, v3',
 'v_mac_f32       v8, v2, v3','v_sub_f32       v11, 1.0, v5',
 'v_mad_f32       v11, -v5, v11, v11','v_mad_f32       v5, -s8, v11, v5 clamp',
 'v_mac_f32       v8, s12, v5','exp             mrt1','exp             mrt0'
]

def flat(m):return [float(v) for r in m['ps']['cbuffers']['items'] for v in r['value']]
def tex(m):return {int(x['texture_index']):x['texture'].upper() for x in m['ps']['textures']['items']}
def eq(a,b):return math.isclose(float(a),float(b),rel_tol=0,abs_tol=2e-7)

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--extract-report',type=Path,required=True);ap.add_argument('--image-usage',type=Path,required=True);ap.add_argument('--material-state',type=Path,required=True);ap.add_argument('--disassembly',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 ext=json.loads(a.extract_report.read_text());iu=json.loads(a.image_usage.read_text());st=json.loads(a.material_state.read_text());asm=a.disassembly.read_text();viol=[]
 if ext.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT':viol.append('extract not exact')
 if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':viol.append('image usage not exact')
 if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):viol.append('material state not exact')
 er=next((x for x in ext.get('shaders',[]) if x.get('shader')==SHADER),None)
 if not er:viol.append('extract row absent')
 else:
  for k,v in [('native_shader',NATIVE),('native_sha256',NATIVE_SHA),('gcn_sha256',GCN_SHA),('gcn_bytes',764)]:
   if er.get(k)!=v:viol.append(f'{k} mismatch {er.get(k)!r}')
 ir=next((x for x in iu.get('shaders',[]) if x.get('shader')==SHADER),None)
 if not ir:viol.append('usage row absent')
 else:
  got=[]
  for x in ir.get('instructions',[]):
   rr=x.get('resources') or [];got.append((x.get('opcode'),rr[0].get('texture_index') if len(rr)==1 else None,x.get('dmask'),x.get('dmask_channels')))
  if got!=EXPECTED_IMAGE:viol.append(f'image sequence mismatch {got!r}')
  if ir.get('unmatched_image_instruction_count')!=0:viol.append('unmatched image instruction')
 for q in ANCHORS:
  if q not in asm:viol.append('missing anchor '+q)
 if sorted((st.get('shader_materials',{}).get('ps',{}) or {}).get(SHADER,[]))!=MATERIALS:viol.append('material scope mismatch')
 ref=None
 for mh in MATERIALS:
  m=(st.get('materials') or {}).get(mh)
  if not m or m.get('error'):viol.append(mh+': unresolved');continue
  if m.get('material_state4_hex')!=STATE:viol.append(mh+': state mismatch')
  if m['ps'].get('shader')!=SHADER:viol.append(mh+': PS mismatch')
  if m['ps'].get('tfx_program_sha256')!=TFX_SHA or not m['ps'].get('tfx_disassembly',{}).get('complete'):viol.append(mh+': TFX mismatch')
  if tex(m)!=TEXTURES:viol.append(mh+': texture map mismatch')
  vals=flat(m)
  for i,v in CB.items():
   if i>=len(vals) or not eq(vals[i],v):viol.append(f'{mh}:b0[{i}] mismatch')
  sem=(m['ps']['tfx_bytecode']['bytes_hex'],tuple(x['raw_hex'] for x in m['ps']['cbuffers']['items']),tuple(sorted(tex(m).items())))
  if ref is None:ref=sem
  elif sem!=ref:viol.append(mh+': semantic payload differs')
 if viol:
  out={'schema_version':1,'status':'D1_TOWER_PS_809D8363_CURRENT_STATE_SEMANTICS_PARTIAL','violations':viol};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 2
 out={
  'schema_version':1,'status':'D1_TOWER_PS_809D8363_CURRENT_STATE_COLOR_SEMANTICS_EXACT','violations':[],
  'shader':SHADER,'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'scope_materials':MATERIALS,'scope_material_count':2,'visible_primitive_count':15,
  'exact_inputs':{'texture_bindings':{str(k):v for k,v in TEXTURES.items()},'tfx_program_sha256':TFX_SHA,'material_state4_hex':STATE,'cb0_current_values':{str(k):v for k,v in CB.items()}},
  'current_state_reduction':{
    'attr1_y_branch':'if attr1.y>1 the palette seed is explicitly zero; otherwise seed=saturate(b0[0:3]-0.25)',
    'palette_seed_current':'b0[0:3]=0, therefore the false-branch palette seed is also zero',
    'sampled_surface_branch':'t0.rgb multiplies the zero palette seed; the t1.r blend/delta branch is also zero because b0[56:58]=0 and the sampled branch begins at zero',
    'view_factor':'R=saturate((-b0[36])*(1-dot(N,V))^2 + (b0[36]+b0[37])); current R=saturate(1.5649452209472656*(1-dot(N,V))^2-0.5649452209472656)',
    'mrt0_rgb':'mrt0.rgb=b0[32:34]+b0[40:42]*R; current b0[32:34]=0, so RGB=(0.0602063164,0.0821281448,0.0955228731)*R',
    'mrt0_alpha':'mrt0.a=attr0.w',
    'mrt1_aux':'mrt1.a=b0[73] when attr1.y>1, else b0[69]',
  },
  'promoted_texture_semantics':{
    't0':{'tag':TEXTURES[0],'role':'surface_rgb_branch_currently_zero_weighted','proof':'sampled RGB enters the surface branch but exact current palette constants reduce its MRT0 contribution to zero'},
    't1':{'tag':TEXTURES[1],'role':'surface_scalar_branch_currently_zero_delta','proof':'sampled x blends a delta that is exactly zero under current b0[56:58] and zero surface seed'},
  },
  'critical_correction':'For these exact two materials, neither texture is a valid baseColor source. MRT0 RGB is constant-tint/view-response output; using t0 or t1 as diffuse invents color absent from the native current-state equation.',
  'gates':{'current_material_native_color_dataflow_closed':True,'hypothetical_other_constant_states_globally_named':False,'portable_blender_recreation_complete':False},
  'policy':'Exact current-state semantics only. Branches are retained and proven; no extrapolation to different material constants is made.'
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ('status','visible_primitive_count','critical_correction','gates')},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
