#!/usr/bin/env python3
"""Fail-closed current-state RGB proof for shared GCN program 8087630D/809D8370.

Two serialized PS headers/native shader tags contain the same exact GCN program.
The four scoped materials also share the exact current CB0 and t# state, although
they carry two exact TFX program hashes. This proof therefore closes the current
material-state pixel equation without claiming runtime TFX values are static.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

SHADERS={'8087630D':('80876388','8f8eac4c2f2c864f23ab1aebde78a86ec33ea92ef672b8593af143a62bcb5524'),'809D8370':('809D83B7','8f8eac4c2f2c864f23ab1aebde78a86ec33ea92ef672b8593af143a62bcb5524')}
GCN_SHA='9c9d2572ad03d01509fd8a1c1eb5c0cbb5f5b23754baef401331f3564aa3b05f';GCN_BYTES=1136
MATERIALS={'80876CB3':'8087630D','80C885E8':'809D8370','80C88609':'809D8370','80C88623':'809D8370'}
TEXTURES={0:'80AB04B3',1:'80AB04B4',2:'8087657B',3:'80AB04B5',4:'80AB04B5',5:'80AB04B5'}
TFX={'206761c3654c395e30fd9332256b06ea234d617f363c673bd05bd8aba0ddf0a9','781c38a507d8fae49c420139d2a72adeb622fdf6ab911a60e72a8fbede5675e1'}
STATE='00008100';EXPECTED=[('image_sample',1,1,'x'),('image_sample',4,1,'x'),('image_sample',0,7,'xyz'),('image_sample',5,1,'x'),('image_sample',2,1,'x'),('image_sample',3,1,'x')]
CB={40:.3400000035762787,44:.24455422163009644,45:.24455422163009644,46:.24455422163009644,48:-1.6592003107070923,49:1.1592832803726196,52:.7554457783699036,53:.7554457783699036,54:.7554457783699036,68:0.,69:0.,70:0.,77:.0049019609577953815,80:0.,81:0.,82:0.,84:0.,85:0.,86:0.,88:50.,92:25.,96:60.,104:.7103999853134155,108:1.0224000215530396,112:.8133000135421753,132:0.,136:.03200000151991844}
ANCHORS=['image_sample    v5, v[3:6]','v_cmp_gt_f32    vcc, 0, v5','s_andn2_b64     s[56:57], s[56:57], vcc','image_sample    v[6:8], v[3:6]','image_sample    v9, v[3:6]','image_sample    v10, v[3:6]','image_sample    v3, v[3:6]','v_sub_f32       v11, 1.0, v4','v_mad_f32       v11, -v4, v11, v11','v_mad_f32       v4, -s16, v11, v4 clamp','v_mac_f32       v6, v10, v14','v_mac_f32       v8, s12, v4','v_mul_f32       v6, v6, v8','exp             mrt1','exp             mrt0']

def flat(m):return [float(v) for r in m['ps']['cbuffers']['items'] for v in r['value']]
def tex(m):return {int(x['texture_index']):x['texture'].upper() for x in m['ps']['textures']['items']}
def eq(a,b):return math.isclose(float(a),float(b),rel_tol=0,abs_tol=2e-7)

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--extract-report',type=Path,required=True);ap.add_argument('--image-usage',type=Path,required=True);ap.add_argument('--material-state',type=Path,required=True);ap.add_argument('--disasm-8087630d',type=Path,required=True);ap.add_argument('--disasm-809d8370',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 ext=json.loads(a.extract_report.read_text());iu=json.loads(a.image_usage.read_text());st=json.loads(a.material_state.read_text());asms={'8087630D':a.disasm_8087630d.read_text(),'809D8370':a.disasm_809d8370.read_text()};viol=[]
 if ext.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT':viol.append('extract not exact')
 if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':viol.append('usage not exact')
 if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):viol.append('state not exact')
 for sh,(native,nsha) in SHADERS.items():
  er=next((x for x in ext.get('shaders',[]) if x.get('shader')==sh),None)
  if not er:viol.append(sh+': extract absent');continue
  for k,v in [('native_shader',native),('native_sha256',nsha),('gcn_sha256',GCN_SHA),('gcn_bytes',GCN_BYTES)]:
   if er.get(k)!=v:viol.append(f'{sh}:{k} mismatch')
  ir=next((x for x in iu.get('shaders',[]) if x.get('shader')==sh),None)
  if not ir:viol.append(sh+': usage absent')
  else:
   got=[]
   for x in ir.get('instructions',[]):
    rr=x.get('resources') or [];got.append((x.get('opcode'),rr[0].get('texture_index') if len(rr)==1 else None,x.get('dmask'),x.get('dmask_channels')))
   if got!=EXPECTED:viol.append(f'{sh}: image sequence mismatch {got!r}')
   if ir.get('unmatched_image_instruction_count')!=0:viol.append(sh+': unmatched image instruction')
  for q in ANCHORS:
   if q not in asms[sh]:viol.append(f'{sh}: missing anchor {q}')
 refcb=None
 for mh,sh in MATERIALS.items():
  m=(st.get('materials') or {}).get(mh)
  if not m or m.get('error'):viol.append(mh+': unresolved');continue
  if m.get('material_state4_hex')!=STATE or m['ps'].get('shader')!=sh:viol.append(mh+': state/shader mismatch')
  if m['ps'].get('tfx_program_sha256') not in TFX or not m['ps'].get('tfx_disassembly',{}).get('complete'):viol.append(mh+': TFX mismatch')
  if tex(m)!=TEXTURES:viol.append(mh+': texture map mismatch')
  vals=flat(m)
  for i,v in CB.items():
   if i>=len(vals) or not eq(vals[i],v):viol.append(f'{mh}:b0[{i}] mismatch')
  cbraw=tuple(x['raw_hex'] for x in m['ps']['cbuffers']['items'])
  if refcb is None:refcb=cbraw
  elif cbraw!=refcb:viol.append(mh+': current CB0 differs')
 if viol:
  out={'schema_version':1,'status':'D1_TOWER_PS_SHARED_8087630D_809D8370_CURRENT_STATE_PARTIAL','violations':viol};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 2
 out={'schema_version':1,'status':'D1_TOWER_PS_SHARED_8087630D_809D8370_CURRENT_STATE_RGB_EXACT','violations':[],'serialized_shaders':sorted(SHADERS),'gcn_sha256':GCN_SHA,'scope_materials':sorted(MATERIALS),'scope_material_count':4,'visible_primitive_count':15,
 'exact_inputs':{'texture_bindings':{str(k):v for k,v in TEXTURES.items()},'material_state4_hex':STATE,'tfx_program_sha256_set':sorted(TFX),'cb0_current_values':{str(k):v for k,v in CB.items()}},
 'current_state_equations':{
  'alpha_test':'t1.r is sampled first and compared with an extended-user-data scalar; failing pixel lanes are removed before the RGB path',
  'view_factor':'D=dot(normalize(extended_view_position-attr3.xyz),normalize(attr0.xyz)); R=saturate(1.6592003107070923*(1-D)^2-0.49991703033447266)',
  'surface':'C.rgb=t0.rgb*t2.r',
  'tint':'T.rgb=b0[44:46]+b0[52:54]*R = 0.2445542216 + 0.7554457784*R',
  'mrt0_rgb':'mrt0.rgb=C.rgb*T.rgb',
  'mrt0_alpha':'mrt0.a=attr0.w',
  'zero_weighted_current_branches':'t5.r highlight branch is multiplied by b0[84:86]=0; other additive current-state RGB branch b0[80:82]=0',
  'normal_pack':'t3.r controls the native deferred-normal packing magnitude; b0[77] is MRT1 auxiliary alpha',
 },
 'promoted_texture_semantics':{
  't0':{'tag':TEXTURES[0],'role':'surface_rgb','proof':'native RGB survives directly into C=t0.rgb*t2.r'},
  't1':{'tag':TEXTURES[1],'role':'alpha_test_scalar_r','proof':'first x sample feeds pixel-lane discard comparison'},
  't2':{'tag':TEXTURES[2],'role':'surface_scalar_multiplier_r','proof':'native x sample multiplies all three t0 RGB channels'},
  't3':{'tag':TEXTURES[3],'role':'deferred_normal_pack_scalar_r','proof':'native x sample feeds MRT1 packing factor, not MRT0 RGB'},
  't4':{'tag':TEXTURES[4],'role':'normal_or_view_perturbation_scalar_current_rgb_indirect_only','proof':'native x sample enters basis/normal path; no direct RGB sample'},
  't5':{'tag':TEXTURES[5],'role':'highlight_scalar_current_rgb_zero_weighted','proof':'native x sample reaches an additive RGB branch whose exact current b0[84:86] multipliers are zero'},
 },
 'critical_correction':'The shared program has one proven RGB texture (t0), but even it is not standalone baseColor: t2.r and an exact view-angle tint are part of MRT0. The remaining scalar textures are masks/control/normal-path inputs, not diffuse maps.',
 'gates':{'current_material_native_color_dataflow_closed':True,'runtime_tfx_evaluated_state_closed':False,'alpha_test_runtime_threshold_value_closed':False,'portable_blender_recreation_complete':False},
 'policy':'Exact current serialized material-state RGB semantics. Distinct exact TFX programs are retained and prevent a claim that these constants equal every retail runtime frame.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ('status','visible_primitive_count','critical_correction','gates')},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
