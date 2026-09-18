#!/usr/bin/env python3
"""Fail-closed current-state surviving-pixel RGB proof for D1 PS4 PS 809D836C."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
SHADER='809D836C';NATIVE='809D83B3';NATIVE_SHA='c92a58a3a3b92a44ad5b9ae71203edf5789bb3b2b3fcdef89dd1495164bde6d8';GCN_SHA='ffab799bc6ff6ec3fe2021a58bb39aeea6cf6b9bb5d85af783daa8896622a1e3'
MATERIALS=['80C882C8','80C88459','80C88605','80C88610'];TEXTURES={0:'80AB04B3',1:'8087657B',2:'80AB04B5',3:'80AB04B5',4:'80AB04B5'};STATE='00008100'
TFX={'27878544805b23ba133e16286723f658d96317835c27aa27ee38be14096a17f7','762058c7a83b0c1291057ff652d4f2ff7b4aafd4c58cf92c47a64712679b3347'}
EXPECTED=[('image_sample',0,15,'xyzw'),('image_sample',3,1,'x'),('image_sample',4,1,'x'),('image_sample',1,1,'x'),('image_sample',2,1,'x')]
CB={40:.23000000417232513,44:.24455422163009644,45:.24455422163009644,46:.24455422163009644,48:-1.6592003107070923,49:1.1592832803726196,52:.7554457783699036,53:.7554457783699036,54:.7554457783699036,68:0.,69:0.,70:0.,77:.0049019609577953815,80:0.,81:0.,82:0.,84:0.,85:0.,86:0.,88:50.,92:25.,96:60.,104:.7103999853134155,108:1.0224000215530396,112:.8133000135421753,132:0.,136:.03200000151991844}
ANCHORS=['image_sample    v[5:8], v[3:6]','v_mad_f32       v8, v8, v18, -s14','v_cmp_gt_f32    vcc, 0, v8','s_andn2_b64     s[52:53], s[52:53], vcc','image_sample    v8, v[3:6]','image_sample    v18, v[3:6]','image_sample    v20, v[3:6]','image_sample    v3, v[3:6]','v_subrev_f32    v9, v5, v14','v_mac_f32       v5, v20, v9','v_mac_f32       v7, s20, v16','v_mul_f32       v5, v5, v7','v_mac_f32       v11, s0, v3','exp             mrt1','exp             mrt0']
def flat(m):return [float(v) for r in m['ps']['cbuffers']['items'] for v in r['value']]
def tex(m):return {int(x['texture_index']):x['texture'].upper() for x in m['ps']['textures']['items']}
def eq(a,b):return math.isclose(float(a),float(b),rel_tol=0,abs_tol=2e-7)
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--extract-report',type=Path,required=True);ap.add_argument('--image-usage',type=Path,required=True);ap.add_argument('--material-state',type=Path,required=True);ap.add_argument('--disassembly',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();ext=json.loads(a.extract_report.read_text());iu=json.loads(a.image_usage.read_text());st=json.loads(a.material_state.read_text());asm=a.disassembly.read_text();viol=[]
 er=next((x for x in ext.get('shaders',[]) if x.get('shader')==SHADER),None)
 if ext.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or not er:viol.append('extract not exact/present')
 else:
  for k,v in [('native_shader',NATIVE),('native_sha256',NATIVE_SHA),('gcn_sha256',GCN_SHA),('gcn_bytes',1136)]:
   if er.get(k)!=v:viol.append(k+' mismatch')
 ir=next((x for x in iu.get('shaders',[]) if x.get('shader')==SHADER),None)
 if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or not ir:viol.append('usage not exact/present')
 else:
  got=[]
  for x in ir.get('instructions',[]):
   rr=x.get('resources') or [];got.append((x.get('opcode'),rr[0].get('texture_index') if len(rr)==1 else None,x.get('dmask'),x.get('dmask_channels')))
  if got!=EXPECTED:viol.append(f'image sequence mismatch {got!r}')
  if ir.get('unmatched_image_instruction_count')!=0:viol.append('unmatched image instruction')
 if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):viol.append('state not exact')
 for q in ANCHORS:
  if q not in asm:viol.append('missing anchor '+q)
 if sorted((st.get('shader_materials',{}).get('ps',{}) or {}).get(SHADER,[]))!=MATERIALS:viol.append('material scope mismatch')
 ref=None
 for mh in MATERIALS:
  m=(st.get('materials') or {}).get(mh)
  if not m or m.get('error'):viol.append(mh+': unresolved');continue
  if m.get('material_state4_hex')!=STATE or m['ps'].get('shader')!=SHADER:viol.append(mh+': state/shader mismatch')
  if m['ps'].get('tfx_program_sha256') not in TFX or not m['ps'].get('tfx_disassembly',{}).get('complete'):viol.append(mh+': TFX mismatch')
  if tex(m)!=TEXTURES:viol.append(mh+': texture map mismatch')
  vals=flat(m)
  for i,v in CB.items():
   if i>=len(vals) or not eq(vals[i],v):viol.append(f'{mh}:b0[{i}] mismatch')
  raw=tuple(x['raw_hex'] for x in m['ps']['cbuffers']['items'])
  if ref is None:ref=raw
  elif raw!=ref:viol.append(mh+': current CB0 differs')
 if viol:
  out={'schema_version':1,'status':'D1_TOWER_PS_809D836C_CURRENT_STATE_PARTIAL','violations':viol};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 2
 out={'schema_version':1,'status':'D1_TOWER_PS_809D836C_CURRENT_STATE_SURVIVING_RGB_EXACT','violations':[],'shader':SHADER,'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'scope_materials':MATERIALS,'scope_material_count':4,'visible_primitive_count':14,
 'exact_inputs':{'texture_bindings':{str(k):v for k,v in TEXTURES.items()},'material_state4_hex':STATE,'tfx_program_sha256_set':sorted(TFX),'cb0_current_values':{str(k):v for k,v in CB.items()}},
 'current_state_equations':{'alpha_rejection':'t0.a is multiplied by a native view/normal response and compared against b0[40]=0.23; failing lanes are removed before color','surface':'C.rgb=t0.rgb*(1-t1.r)','view_factor':'R=saturate(1.6592003107070923*(1-D)^2-0.49991703033447266), with D the exact normalized view/geometric-normal dot path','tint':'T.rgb=b0[44:46]+b0[52:54]*R = 0.2445542216+0.7554457784*R','zero_weighted_current_branches':'the sampled t3/t4 additive highlight branches are multiplied by exact b0[80:86]=0 and do not reach current MRT0 RGB','mrt0_rgb':'mrt0.rgb=C.rgb*T.rgb','mrt0_alpha':'mrt0.a=attr0.w','normal_pack':'t2.r controls the MRT1 packing scalar; b0[77] is MRT1 auxiliary alpha'},
 'promoted_texture_semantics':{'t0':{'tag':TEXTURES[0],'role':'surface_rgb_alpha_rejection_source','proof':'RGB survives into C; alpha feeds pre-color pixel rejection'},'t1':{'tag':TEXTURES[1],'role':'surface_subtractive_mask_r','proof':'native x sample forms t0.rgb*(1-t1.r)'},'t2':{'tag':TEXTURES[2],'role':'deferred_normal_pack_scalar_r','proof':'native x sample reaches MRT1 packing, not current MRT0 RGB'},'t3':{'tag':TEXTURES[3],'role':'normal_or_highlight_control_current_rgb_zero_weighted','proof':'native scalar branch has exact zero current RGB multiplier'},'t4':{'tag':TEXTURES[4],'role':'highlight_control_current_rgb_zero_weighted','proof':'native scalar branch has exact zero current RGB multiplier'}},
 'critical_correction':'Current MRT0 is not t0 alone: it is t0.rgb*(1-t1.r) times the exact view tint. t2/t3/t4 are control paths, and the alpha cut is view-dependent rather than a guessed fixed Blender threshold.',
 'gates':{'current_material_surviving_rgb_dataflow_closed':True,'runtime_tfx_evaluated_state_closed':False,'portable_alpha_rejection_recreation_complete':False,'portable_blender_recreation_complete':False},'policy':'Exact current serialized material-state surviving RGB. Dynamic TFX and portable alpha-threshold reproduction remain explicit gates.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ('status','visible_primitive_count','critical_correction','gates')},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
