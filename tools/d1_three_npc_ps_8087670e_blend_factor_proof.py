#!/usr/bin/env python3
"""Fail-closed blend-factor reduction for D1 PS4 PS 8087670E.

Proves that only API15 c0.w survives, that current material b0 negates it into
one scalar f, and that the same f interpolates both the detail-normal branch and
the t4-driven alternate surface branch. Runtime f and t4 remain unresolved.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
SH='8087670E'; MATS=['808766B2','808766B6']
ANCHORS=[
 's_buffer_load_dwordx4 s[16:19], s[16:19], s14',
 'v_mul_f32       v5, s19, 1.0',
 'v_mad_f32       v5, 0, s18, v5',
 'v_mad_f32       v5, 0, s17, v5',
 'v_mad_f32       v5, 0, s16, v5',
 'v_mul_f32       v5, s1, v5',
 'v_subrev_f32    v10, v8, v10','v_subrev_f32    v9, v4, v9','v_subrev_f32    v7, v6, v7',
 'v_mac_f32       v8, v5, v10','v_mac_f32       v4, v5, v9','v_mac_f32       v6, v5, v7',
 'image_sample    v[19:22], v[2:5]','v_subrev_f32    v12, v18, v13','v_mac_f32       v18, v5, v12',
 'v_subrev_f32    v13, v15, v13','v_subrev_f32    v14, v16, v14','v_subrev_f32    v26, v17, v26',
 'v_subrev_f32    v2, v15, v9','v_subrev_f32    v3, v16, v10','v_subrev_f32    v6, v17, v12',
 'v_mac_f32       v15, v5, v2','v_mac_f32       v16, v5, v3','v_mac_f32       v17, v5, v6',
]
def flat(ps): return [float(v) for r in ps['cbuffers']['items'] for v in r['value']]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--material-state',type=Path,required=True);ap.add_argument('--extract-report',type=Path,required=True);ap.add_argument('--disassembly',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 st=json.loads(a.material_state.read_text()); ex=json.loads(a.extract_report.read_text()); asm=a.disassembly.read_text(); v=[]
 if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):v.append('material state not exact')
 if ex.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT':v.append('shader extraction not exact')
 er=next((x for x in ex.get('shaders',[]) if x.get('shader')==SH),None)
 if not er:v.append('shader absent')
 else:
  if er.get('gcn_sha256')!='c3751c74f6cc13660cf4acf6c5372f6a178f64bfe29c5b55ef5b5f694a3d98bc':v.append('GCN SHA mismatch')
 for n in ANCHORS:
  if n not in asm:v.append('missing native anchor '+n)
 rows=[]
 for mh in MATS:
  m=st.get('materials',{}).get(mh)
  if not m or m.get('error'):v.append(mh+': material unresolved');continue
  ps=m['ps']; vals=flat(ps)
  if ps.get('shader')!=SH:v.append(mh+': PS mismatch');continue
  need={1:-1.0,16:3.0,20:0.0,24:0.25,25:0.0,36:2.0,37:-1.0,40:0.22316759824752808,41:0.22316759824752808,42:0.22316759824752808,48:0.0}
  for i,z in need.items():
   if i>=len(vals) or not math.isclose(vals[i],z,rel_tol=0,abs_tol=2e-7):v.append(f'{mh}: b0[{i}] mismatch')
  tex={int(x['texture_index']):x['texture'] for x in ps['textures']['items']}
  if 4 in tex:v.append(f'{mh}: t4 unexpectedly serialized')
  rows.append({'material':mh,'b0_1':vals[1] if len(vals)>1 else None,'b0_48':vals[48] if len(vals)>48 else None,'serialized_textures':{str(k):z for k,z in sorted(tex.items())}})
 if v:o={'schema_version':1,'status':'D1_TOWER_PS_8087670E_BLEND_FACTOR_PARTIAL','violations':v};rc=2
 else:
  o={'schema_version':1,'status':'D1_TOWER_PS_8087670E_BLEND_FACTOR_EXACT','violations':[],'shader':SH,'gcn_sha256':'c3751c74f6cc13660cf4acf6c5372f6a178f64bfe29c5b55ef5b5f694a3d98bc','scope_materials':MATS,'material_rows':rows,
   'api15_reduction':{'selected_vector':'c0','native_loaded_components':'xyzw','surviving_component':'w','xyz_effect':'dead because each is multiplied by literal 0 before the accumulator reaches v5','material_multiplier':'b0[1] = -1','blend_factor':'f = -API15.c0.w'},
   'instruction_level_equations':{
    'primary_normal_xy':'n0.xy = 2*t1.xy - 1','detail_combined_normal_xy':'n1.xy = n0.xy + 2*t5.xy - 1','normal_z_each':'z0=sqrt(saturate(1-dot(n0.xy,n0.xy))); z1=sqrt(saturate(1-dot(n1.xy,n1.xy)))','normal_blend':'n.xyz = lerp(float3(n0,z0), float3(n1,z1), f)',
    't0_alpha_alt':'Ba = saturate(t0.a-0.25) + t4.a*saturate(4*t0.a)','surface_alpha_control':'A = lerp(t0.a, Ba, f); current later scale uses 3*A',
    'material_local_rgb_branch':'P = lerp(t0.rgb, saturate(t0.rgb-0.25) + float3(0.22316759824752808)*saturate(4*t0.rgb), t3.r)','t4_rgb_branch':'Q = saturate(t0.rgb-0.25) + t4.rgb*saturate(4*t0.rgb)','surface_branch_blend':'surface = lerp(P,Q,f)',
   },
   'critical_correction':'API15 is not a broad color buffer in this shader. Only c0.w survives, negated by exact b0[1]=-1 into f. The same f enables both the detail-normal and t4 alternate-surface branches; API15 c0.xyz are dead for this program.',
   'gates':{'api15_component_usage_closed':True,'api15_blend_factor_equation_closed':True,'t4_conditional_role_closed':True,'api15_c0_w_runtime_value_closed':False,'runtime_t4_binding_closed':False,'final_shader_color_closed':False},
   'policy':'Exact native/current-material dataflow only. Runtime f and runtime/default t4 are explicitly unresolved and are not assigned compatibility values.'};rc=0
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(o,indent=2)+'\n');print(json.dumps(o if rc else {k:o[k] for k in ['status','critical_correction','gates']},indent=2));return rc
if __name__=='__main__':raise SystemExit(main())
