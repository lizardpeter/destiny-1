#!/usr/bin/env python3
"""Instruction-anchored symbolic reduction of Crota PS 8108E958/8108E959 MRT0 alpha.

This tool freezes the exact native instruction sequence for the two known GCN
programs, validates the terminal-alpha dependency slice, then substitutes exact
serialized API0 material cbuffer values into a source-faithful symbolic equation.

The normalized dot-product input is deliberately named d only. Texture sample
lanes retain t# syntax. API12 values remain symbolic because their engine
semantic/runtime producer is not promoted here.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

SHA={'8108E958':'f91de6415f535e7012c705db9ed8206ad6775e8fae5188938cc6970254ee8a3e',
     '8108E959':'4e35c2ff53dfa9eb29850edbe838b674bfd73838d67c2f9820c1086bb463aba1'}
MATS={'8108E958':['8108E7AB','8108E7B4'],'8108E959':['8108E7AC','8108E7B5']}
READ958=[11,12,13,16,17,23,27,48]
READ959=[8,9,15,19]
ANCHORS={
 '8108E958':[
  'v_mad_f32       v1, v0, s0, v1 clamp',
  'v_mac_f32       v0, s3, v1',
  'v_sub_f32       v3, 1.0, v4',
  'v_mul_f32       v5, v5, v6 clamp',
  'v_mad_f32       v5, v5, s0, v1',
  'v_mac_f32       v1, s0, v0',
  'v_subrev_f32    v3, s4, v3',
  'v_mul_f32       v4, s4, v4',
  'v_mad_f32       v3, v4, v6, s4',
  'v_mad_f32       v4, -v2, s6, v4 clamp',
  'v_mad_f32       v5, v1, s0, v5 clamp',
  'v_madmk_f32     v0, v0, 0x3ecccccd, v3',
  'v_add_f32       v0, 0x3da3d70a, v0',
  'v_mul_f32       v1, v4, v5 clamp',
  'v_max_f32       v2, v0, v0 clamp',
  'v_mac_f32       v1, v2, v0',
  'v_mul_f32       v0, s1, v1',
 ],
 '8108E959':[
  'v_mul_f32       v0, v3, v3',
  'v_mad_f32       v1, v0, s4, v1 clamp',
  'v_mul_f32       v0, v1, v1 clamp',
  'v_mac_f32       v1, s0, v0',
  'v_mul_f32       v0, v2, v1',
 ],
}
def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def flat(stage):
 out=[]
 for r in stage['cbuffers']['items']:out.extend(float(x) for x in r['value'])
 return out
def val(v,i):
 if i>=len(v):raise ValueError(f'cbuffer lacks dword {i}; count={len(v)}')
 return v[i]

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--stage-state',type=Path,required=True)
 ap.add_argument('--extract-report',type=Path,required=True)
 ap.add_argument('--alpha-slice',type=Path,required=True)
 ap.add_argument('--disasm-dir',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 st=json.loads(a.stage_state.read_text());ex=json.loads(a.extract_report.read_text());sl=json.loads(a.alpha_slice.read_text());v=[];rows=[]
 if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):v.append('stage state not exact')
 if ex.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT':v.append('shader extract not exact')
 if sl.get('status')!='D1_GCN_TERMINAL_ALPHA_SLICE_EXACT' or sl.get('violations'):v.append('alpha slice not exact')
 mats={norm(k):x for k,x in (st.get('materials') or {}).items()}
 er={norm(x['shader']):x for x in ex.get('shaders',[])}
 sr={norm(x['shader']):x for x in sl.get('shaders',[])}
 for sh in ('8108E958','8108E959'):
  e=er.get(sh)
  if not e or e.get('gcn_sha256')!=SHA[sh]:v.append(f'{sh}: exact GCN SHA drift')
  text=(a.disasm_dir/f'PS_{sh}_GFX700.s').read_text(errors='replace')
  missing=[x for x in ANCHORS[sh] if x not in text]
  if missing:v.append(f'{sh}: missing native anchors {missing}')
  direct=(sr.get(sh,{}).get('value_slice') or {}).get('cbuffer_dwords',{}).get('0',[])
  expected=READ958 if sh=='8108E958' else READ959
  if [int(x) for x in direct]!=expected:v.append(f'{sh}: terminal alpha direct API0 drift {direct}')
  for mh in MATS[sh]:
   m=mats.get(mh)
   if not m or m.get('error'):v.append(f'{mh}: material missing/error');continue
   if norm(m['ps']['shader'])!=sh:v.append(f'{mh}: PS identity drift');continue
   q=flat(m['ps'])
   coeff={str(i):val(q,i) for i in expected}
   if sh=='8108E958':
    formula={
     'definitions':[
      'd = dot(normalize(API12[28:30] - attr2.xyz), attr0.xyz), with native component ordering preserved',
      'U = clamp(m16*d*d + m17)',
      'V = m23 + m27*U',
      'F = clamp(0.010300000198185444 * (0.6000000238418579 + 9.399999618530273*clamp(t1.w*t2.w)) * (0.6000000238418579 + 9.399999618530273*V) - 0.05999999865889549)',
      'G = clamp(m13 + m12*(1 - t0.x))',
      'H = 0.07999999821186066 + m48*(1 + 2.4000000953674316*t4.w) - 0.4000000059604645*(1 - t4.w - m48)^2',
      'A = m11 * (clamp(G*F) + clamp(H)*H)',
     ],
     'api0_coefficients':{'m11':coeff['11'],'m12':coeff['12'],'m13':coeff['13'],'m16':coeff['16'],'m17':coeff['17'],'m23':coeff['23'],'m27':coeff['27'],'m48':coeff['48']},
     'direct_texture_lanes':['t0.x','t1.w','t2.w','t4.w'],
     'api12_direct_dwords':[28,29,30],
    }
   else:
    formula={
     'definitions':[
      'd = dot(normalize(API12[28:30] - attr2.xyz), attr0.xyz), with native component ordering preserved',
      'U = clamp(m8*d*d + m9)',
      'V = clamp(U*U)',
      'A = t0.w * (m15 + m19*V)',
     ],
     'api0_coefficients':{'m8':coeff['8'],'m9':coeff['9'],'m15':coeff['15'],'m19':coeff['19']},
     'direct_texture_lanes':['t0.w'],
     'api12_direct_dwords':[28,29,30],
    }
   rows.append({'material':mh,'pixel_shader':sh,'gcn_sha256':SHA[sh],**formula})
 out={'schema':'d1_crota_attenuation_symbolic_reduce/v1',
      'status':'D1_CROTA_ATTENUATION_SYMBOLIC_REDUCTION_EXACT' if len(rows)==4 and not v else 'D1_CROTA_ATTENUATION_SYMBOLIC_REDUCTION_PARTIAL',
      'rows':rows,'violations':v,
      'literal_constants':{'0.6':0.6000000238418579,'9.4':9.399999618530273,'2.4':2.4000000953674316,'-0.06':-0.05999999865889549,'0.0103':0.010300000198185444,'0.4':0.4000000059604645,'0.08':0.07999999821186066},
      'semantic_boundary':{'A':'TERMINAL_MRT0_ALPHA_NUMERICAL_VALUE','d':'UNNAMED_NORMALIZED_DOT_INPUT','API0':'SERIALIZED_MATERIAL_CBUFFER_VALUES','API12':'RUNTIME_OR_GLOBAL_CBUFFER_SEMANTIC_WITHHELD','native_pass_order':'WITHHELD'},
      'policy':'Equations are transcription/reduction of exact pinned GCN instructions and exact serialized API0 values. clamp denotes the native clamp modifier. API12 and interpolant meanings are deliberately unnamed.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'rows':[{'material':x['material'],'shader':x['pixel_shader'],'coefficients':x['api0_coefficients'],'definitions':x['definitions']} for x in rows],'violations':v},indent=2))
 return 0 if out['status']=='D1_CROTA_ATTENUATION_SYMBOLIC_REDUCTION_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
