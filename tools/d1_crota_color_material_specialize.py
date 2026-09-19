#!/usr/bin/env python3
"""Material-specialize Crota's three exact terminal-RGB shader families.

This proof combines exact serialized material stage state, exact terminal-RGB
dependency slices, exact native shader identities, and exact texture-channel
facts. It performs only algebraic eliminations justified by the selected retail
material payloads.

The resulting equations are numerical native-dataflow descriptions. API12/API13
and interpolant engine meanings remain unnamed; no lighting, albedo, emissive, or
render-pass semantic is inferred.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHAS={
 '8108E953':'a5fe9ef18b14e9f204aedd5f0d8cf34021bf5812f445521cd9b9fec18dfd9552',
 '8108E955':'2bb9b4e27b0aa204e5d0b47ce8d85746853da1187d8b0ce2700b94009810795f',
 '8108E956':'b2b8147deb1b5ed70ee9306784d8760eb82b7aef6cb07cf308e3ed64645d9e69',
}
MATERIALS={
 '8108E7B1':{'shader':'8108E953','textures':{0:'8108E952'}},
 '8108E7AA':{'shader':'8108E956','textures':{0:'8108E951'}},
 '8108E7B3':{'shader':'8108E956','textures':{0:'8108E951'}},
 '8108E7A9':{'shader':'8108E955','textures':{0:'8108E7B6',1:'80AACF2A',2:'80AACF2A',3:'80AAD0E1',4:'80AACF2A'}},
 '8108E7B2':{'shader':'8108E955','textures':{0:'8108E7B6',1:'80AACF2A',2:'80AACF2A',3:'80AAD0E1',4:'80AACF2A'}},
}
REQ={
 '8108E953':{
  'R':({'0':[8,9,12,16,20,24],'12':[28,29,30],'13':[6,7]},[('0','x')]),
  'G':({'0':[8,9,13,17,21,24],'12':[28,29,30],'13':[6,7]},[('0','y')]),
  'B':({'0':[8,9,14,18,22,24],'12':[28,29,30],'13':[6,7]},[('0','z')]),
 },
 '8108E956':{
  'R':({'0':[8,9,12,15,16,19,20,24],'12':[28,29,30],'13':[6,7]},[('0','w'),('0','x')]),
  'G':({'0':[8,9,13,15,17,19,21,24],'12':[28,29,30],'13':[6,7]},[('0','w'),('0','y')]),
  'B':({'0':[8,9,14,15,18,19,22,24],'12':[28,29,30],'13':[6,7]},[('0','w'),('0','z')]),
 },
 '8108E955':{
  'R':({'0':[8,11,12,13,16,17,20,23,24,27,48,52,56],'12':[28,29,30],'13':[6,7]},[('0','x'),('1','w'),('1','x'),('2','w'),('2','x'),('4','w'),('4','x')]),
  'G':({'0':[9,11,12,13,16,17,21,23,25,27,48,53,56],'12':[28,29,30],'13':[6,7]},[('0','x'),('1','w'),('1','y'),('2','w'),('2','y'),('4','w'),('4','y')]),
  'B':({'0':[10,11,12,13,16,17,22,23,26,27,48,54,56],'12':[28,29,30],'13':[6,7]},[('0','x'),('1','w'),('1','z'),('2','w'),('2','z'),('4','w'),('4','z')]),
 },
}

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def flat(stage):
 vals=[]
 for r in (stage.get('cbuffers') or {}).get('items',[]): vals.extend(float(x) for x in r['value'])
 return vals

def texmap(stage):
 return {int(x['texture_index']):norm(x['texture']) for x in (stage.get('textures') or {}).get('items',[])}

def exact(v,i):
 if i>=len(v):raise ValueError(f'cbuffer lacks dword {i}; count={len(v)}')
 return float(v[i])

def check_slice(row,shader):
 for ch,(cb,tx) in REQ[shader].items():
  s=(row.get('channels') or {}).get(ch,{}).get('value_slice') or {}
  gotcb={str(k):[int(x) for x in v] for k,v in (s.get('cbuffer_dwords') or {}).items()}
  gottx=[(str(x['texture_index']),str(x['channel'])) for x in s.get('texture_sample_channels',[])]
  if gotcb!=cb:raise ValueError(f'{shader}:{ch}: cbuffer slice drift {gotcb} != {cb}')
  if gottx!=tx:raise ValueError(f'{shader}:{ch}: texture slice drift {gottx} != {tx}')
  if s.get('unknown_registers'):raise ValueError(f"{shader}:{ch}: unknown register leaves {s['unknown_registers']}")

def specialize_953(mh,v):
 # Native:
 # U=clamp(m8*d^2+m9)
 # RGB_j=t0.j*m20..22*m24*API13[7]*API13[6]*(m12..14+m16..18*U)
 if not (exact(v,8)==1.0 and exact(v,9)==0.0):raise ValueError(f'{mh}: 953 angular constants drift')
 if any(exact(v,i)!=0.0 for i in (12,13,14)):raise ValueError(f'{mh}: 953 additive RGB constants nonzero')
 if any(exact(v,i)!=1.0 for i in (20,21,22)):raise ValueError(f'{mh}: 953 texture channel multipliers drift')
 return {
  'angular':{
   'definition':'d = dot(normalize(API12[28:30] - attr2.xyz), attr0.xyz), native component ordering preserved',
   'specialized':'U = clamp(d*d)',
   'runtime_or_global_dependency':['API12[28]','API12[29]','API12[30]'],
  },
  'texture_rgb':'t0.rgb = texture 8108E952 RGB',
  'exact_material_rgb_vector':[exact(v,16),exact(v,17),exact(v,18)],
  'exact_material_scalar':exact(v,24),
  'runtime_scale':'API13[6] * API13[7]',
  'specialized_equation':'RGB = t0.rgb * [m16,m17,m18] * U * m24 * API13[6] * API13[7]',
  'dead_serialized_terms':['m9','m12','m13','m14'],
  'remaining_runtime_dwords':{'12':[28,29,30],'13':[6,7]},
 }

def specialize_956(mh,v,tc):
 # Native:
 # U=clamp(m8*d^2+m9); V=clamp(U^2)
 # W=t0.w*(m15+m19*V)
 # RGB=t0.rgb*(m12..14+m16..18*V)*(m20..22*m24)*API13[6]*API13[7]*W
 if not (exact(v,8)==1.0 and exact(v,9)==0.0):raise ValueError(f'{mh}: 956 angular constants drift')
 if not (exact(v,15)==1.0 and exact(v,19)==0.0):raise ValueError(f'{mh}: 956 alpha branch constants drift')
 pr=(tc.get('textures') or {}).get('8108E951') or {}
 if not pr.get('sample_alpha_constant_one'):raise ValueError(f'{mh}: 8108E951 alpha not exact one')
 return {
  'angular':{
   'definition':'d = dot(normalize(API12[28:30] - attr2.xyz), attr0.xyz), native component ordering preserved',
   'specialized':['U = clamp(d*d)','V = clamp(U*U)'],
   'runtime_or_global_dependency':['API12[28]','API12[29]','API12[30]'],
  },
  'texture_rgb':'t0.rgb = texture 8108E951 RGB',
  'texture_alpha_substitution':'t0.w = 1.0 exact from DXT1 blocks',
  'angular_rgb_bias':[exact(v,12),exact(v,13),exact(v,14)],
  'angular_rgb_slope':[exact(v,16),exact(v,17),exact(v,18)],
  'exact_static_rgb_vector':[exact(v,20),exact(v,21),exact(v,22)],
  'exact_material_scalar':exact(v,24),
  'runtime_scale':'API13[6] * API13[7]',
  'specialized_equation':'RGB = t0.rgb * ([m12,m13,m14] + [m16,m17,m18]*V) * [m20,m21,m22] * m24 * API13[6] * API13[7]',
  'dead_serialized_terms':['m9','m19'],
  'remaining_runtime_dwords':{'12':[28,29,30],'13':[6,7]},
 }

def specialize_955(mh,v,tc):
 # Current Crota constants remove the V angular branch from F_alpha and all m48 terms,
 # but U remains in each RGB F_j through m24..26 == 1.
 expect={11:1.0,12:6.0,16:-1.25,17:1.25,23:1.0,27:0.0,48:0.0,
         24:1.0,25:1.0,26:1.0,52:1.0,53:1.0,54:1.0,56:55.0}
 for i,x in expect.items():
  if exact(v,i)!=x:raise ValueError(f'{mh}: 955 m{i} {exact(v,i)} != {x}')
 for tag in ('80AACF2A',):
  pr=(tc.get('textures') or {}).get(tag) or {}
  if not pr.get('sample_alpha_constant_one'):raise ValueError(f'{mh}: {tag} alpha not exact one')
 return {
  'angular':{
   'definition':'d = dot(normalize(API12[28:30] - attr2.xyz), attr0.xyz), native component ordering preserved',
   'specialized':'U = clamp(-1.25*d*d + 1.25)',
   'runtime_or_global_dependency':['API12[28]','API12[29]','API12[30]'],
  },
  'exact_texture_map':{
   't0':'8108E7B6 BC4 scalar x',
   't1':'80AACF2A BC1 rgba',
   't2':'80AACF2A BC1 rgba',
   't3':'80AAD0E1 BC5 coordinate-side only; absent terminal-RGB value slice',
   't4':'80AACF2A BC1 rgba',
  },
  'exact_alpha_substitutions':['t1.w = 1.0','t2.w = 1.0','t4.w = 1.0'],
  'channel_gain_vector':[exact(v,8),exact(v,9),exact(v,10)],
  'normalized_channel_gain_by_green':[exact(v,8)/exact(v,9),1.0,exact(v,10)/exact(v,9)],
  'exact_material_scalar':exact(v,56),
  'runtime_scale':'API13[6] * API13[7]',
  'common_control':[
    'G = clamp(m13 + m12*(1 - t0.x))',
    'F_alpha = clamp(0.010300000198185444 * 10 * 10 - 0.05999999865889549)',
    'H_alpha = 0.07999999821186066',
    'A_base = clamp(G*F_alpha) + clamp(H_alpha)*H_alpha',
  ],
  'per_channel_definition':[
    'P_j = clamp(t1.j * t2.j)',
    'Q_j = 0.6000000238418579 + 9.399999618530273 * P_j',
    'R = 0.6000000238418579 + 9.399999618530273 * U',
    'F_j = clamp(0.010300000198185444 * Q_j * R - 0.05999999865889549)',
    'H_j = 0.07999999821186066 - 0.4000000059604645 * (1 - t4.j)^2',
    'C_j = clamp(G*F_j) + clamp(H_j)*H_j',
    'RGB_j = m(8+j) * C_j * A_base * m(52+j) * m56 * API13[6] * API13[7]',
  ],
  'specialized_constants':{
    'm8_m9_m10':[exact(v,8),exact(v,9),exact(v,10)],
    'm11':exact(v,11),'m12':exact(v,12),'m13':exact(v,13),
    'm16':exact(v,16),'m17':exact(v,17),'m23':exact(v,23),'m27':exact(v,27),
    'm48':exact(v,48),'m52_m53_m54':[exact(v,52),exact(v,53),exact(v,54)],'m56':exact(v,56),
  },
  'dead_or_constant_dependencies':{
    'm27_view_branch_in_common_alpha':True,
    'm48_terms':True,
    'BC1_alpha_variation':True,
  },
  'remaining_runtime_dwords':{'12':[28,29,30],'13':[6,7]},
 }

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--stage-state',type=Path,required=True)
 ap.add_argument('--rgb-slice',type=Path,required=True)
 ap.add_argument('--extract-report',type=Path,required=True)
 ap.add_argument('--texture-channels',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 st=json.loads(a.stage_state.read_text());sl=json.loads(a.rgb_slice.read_text())
 ex=json.loads(a.extract_report.read_text());tc=json.loads(a.texture_channels.read_text())
 violations=[];rows=[]
 if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):violations.append('stage state not exact')
 if sl.get('status')!='D1_GCN_TERMINAL_RGB_SLICE_EXACT' or sl.get('violations'):violations.append('RGB slice not exact')
 if ex.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or ex.get('error_count'):violations.append('shader extract not exact')
 if tc.get('status')!='D1_CROTA_TEXTURE_CHANNEL_PROOF_EXACT' or tc.get('violations'):violations.append('texture channel proof not exact')
 mats={norm(k):v for k,v in (st.get('materials') or {}).items()}
 slices={norm(x['shader']):x for x in sl.get('shaders',[])}
 extract={norm(x['shader']):x for x in ex.get('shaders',[])}
 for sh in ('8108E953','8108E955','8108E956'):
  try:
   e=extract.get(sh)
   if not e or str(e.get('gcn_sha256','')).lower()!=SHAS[sh]:raise ValueError(f'{sh}: GCN SHA drift {None if not e else e.get("gcn_sha256")}')
   sr=slices.get(sh)
   if not sr:raise ValueError(f'{sh}: RGB slice missing')
   check_slice(sr,sh)
  except Exception as err:violations.append(str(err))
 for mh,spec in MATERIALS.items():
  try:
   m=mats.get(mh)
   if not m or m.get('error'):raise ValueError(f'{mh}: material missing/error')
   sh=spec['shader']
   if norm(m['ps']['shader'])!=sh:raise ValueError(f'{mh}: shader drift {m["ps"]["shader"]}')
   if texmap(m['ps'])!=spec['textures']:raise ValueError(f'{mh}: texture map drift {texmap(m["ps"])}')
   v=flat(m['ps'])
   if sh=='8108E953':sp=specialize_953(mh,v)
   elif sh=='8108E956':sp=specialize_956(mh,v,tc)
   else:sp=specialize_955(mh,v,tc)
   rows.append({'material':mh,'pixel_shader':sh,'gcn_sha256':SHAS[sh],**sp})
  except Exception as err:violations.append(str(err))
 out={
  'schema':'d1_crota_color_material_specialization/v1',
  'status':'D1_CROTA_COLOR_MATERIAL_SPECIALIZATION_EXACT' if len(rows)==5 and not violations else 'D1_CROTA_COLOR_MATERIAL_SPECIALIZATION_PARTIAL',
  'row_count':len(rows),'rows':rows,'violations':violations,
  'family_counts':{sh:sum(x['pixel_shader']==sh for x in rows) for sh in ('8108E953','8108E955','8108E956')},
  'semantic_boundary':{
   'terminal_rgb_numerical_dependencies':'EXACT_FOR_SELECTED_RETAIL_MATERIALS',
   'API12_API13_engine_names':'WITHHELD',
   'interpolant_semantics':'WITHHELD',
   'lighting_albedo_emissive_labels':'WITHHELD',
   'native_pass_order':'WITHHELD',
  },
  'policy':'Every reduction is restricted to exact selected Crota material payloads and exact pinned GCN identities. Serialized zeros/ones and exact BC1 alpha-one facts may eliminate branches; API12/API13 and interpolant roles remain unnamed. Equations describe terminal MRT0 RGB values only.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'families':out['family_counts'],
                   'rows':[{'material':x['material'],'shader':x['pixel_shader'],
                            'equation':x.get('specialized_equation'),
                            'static_rgb':x.get('exact_static_rgb_vector'),
                            'gain':x.get('channel_gain_vector')} for x in rows],
                   'violations':violations},indent=2))
 return 0 if out['status']=='D1_CROTA_COLOR_MATERIAL_SPECIALIZATION_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
