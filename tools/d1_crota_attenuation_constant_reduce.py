#!/usr/bin/env python3
"""Map exact Crota attenuation PS API0 cbuffer reads to serialized material values."""
from __future__ import annotations
import argparse,json
from pathlib import Path

FAMILIES={
 'proc_a':('8108E7A9','8108E7AB','8108E955','8108E958'),
 'proc_b':('8108E7B2','8108E7B4','8108E955','8108E958'),
 'atlas_a':('8108E7AA','8108E7AC','8108E956','8108E959'),
 'atlas_b':('8108E7B3','8108E7B5','8108E956','8108E959'),
}
# Exact API0 material-cbuffer dword reads frozen from the native GFX700 programs.
READS_958=[11,12,13,16,17,23,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48]
READS_959=[8,9,15,19]

def flat(stage):
 vals=[];raw=[]
 for r in stage['cbuffers']['items']:
  vals += [float(x) for x in r['value']]
  h=r['raw_hex'];raw += [h[i:i+8] for i in range(0,32,8)]
 return vals,raw

def selected(vals,raw,idxs):
 if max(idxs)>=len(vals):raise ValueError(f'cbuffer too short: need {max(idxs)+1}, got {len(vals)}')
 return [{'dword':i,'vec4_index':i//4,'lane':'xyzw'[i%4],'value':vals[i],'raw_le_hex':raw[i]} for i in idxs]

def diff(a,b):
 av,ar=flat(a);bv,br=flat(b);out=[]
 for i in range(max(len(av),len(bv))):
  aa=av[i] if i<len(av) else None;bb=bv[i] if i<len(bv) else None
  ah=ar[i] if i<len(ar) else None;bh=br[i] if i<len(br) else None
  if ah!=bh:out.append({'dword':i,'vec4_index':i//4,'lane':'xyzw'[i%4],
    'color':aa,'attenuation':bb,'color_raw_le_hex':ah,'attenuation_raw_le_hex':bh})
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--stage-state',type=Path,required=True);ap.add_argument('--cbuffer-usage',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 d=json.loads(a.stage_state.read_text());cu=json.loads(a.cbuffer_usage.read_text());v=[];rows=[]
 if cu.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or cu.get('missing_usage'):v.append('cbuffer usage not exact')
 usage={x['shader']:x for x in cu.get('shaders',[])}
 if d.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or d.get('violations'):v.append('stage state not exact')
 mats=d.get('materials') or {}
 for name,(ch,ah,cps,aps) in FAMILIES.items():
  try:
   c=mats[ch];q=mats[ah]
   if c.get('error') or q.get('error'):raise ValueError('material error')
   if c['ps']['shader']!=cps or q['ps']['shader']!=aps:raise ValueError('shader identity drift')
   cv,cr=flat(c['ps']);qv,qr=flat(q['ps']);expected=READS_958 if aps=='8108E958' else READS_959
   ur=usage.get(aps)
   if not ur:raise ValueError(f'{aps}: cbuffer provenance row missing')
   reads=[int(x) for x in (ur.get('api_slot_read_dwords') or {}).get('0',[])]
   if reads!=expected:raise ValueError(f'{aps}: derived API0 reads {reads} != frozen exact {expected}')
   sr=selected(qv,qr,reads);changes=diff(c['ps'],q['ps'])
   row={'family':name,'color_material':ch,'attenuation_material':ah,'color_shader':cps,'attenuation_shader':aps,
        'color_cbuffer_dword_count':len(cv),'attenuation_cbuffer_dword_count':len(qv),
        'attenuation_api0_reads':sr,'derived_api0_read_dwords':reads,'frozen_expected_api0_read_dwords':expected,
        'api0_read_set_revalidated_from_gcn':True,
        'color_vs_attenuation_changed_dwords':changes,'changed_dword_count':len(changes)}
   if aps=='8108E959':
    m={x['dword']:x['value'] for x in sr}
    row['exact_symbolic_coefficients']={'m8':m[8],'m9':m[9],'m15':m[15],'m19':m[19]}
    row['exact_formula']='A = m15 + m19 * clamp(clamp(m8*d^2 + m9)^2); t0.w is independently proven 1.0'
    row['coefficient_only_alpha_interval_before_render_target_clamp']=[min(m[15],m[15]+m[19]),max(m[15],m[15]+m[19])]
   rows.append(row)
  except Exception as e:v.append(f'{name}: {e}')
 out={'schema':'d1_crota_attenuation_constant_reduce/v1',
      'status':'D1_CROTA_ATTENUATION_CONSTANTS_EXACT' if len(rows)==4 and not v else 'D1_CROTA_ATTENUATION_CONSTANTS_PARTIAL',
      'rows':rows,'violations':v,
      'withheld':['semantic names of API0 cbuffer values','API12/global cbuffer semantic names','native pass order'],
      'policy':'Dword offsets are mechanically recovered from exact GCN scalar-buffer descriptor provenance on every run and checked against the frozen shader-family read set. Values come only from exact serialized PS cbuffers; no preview constants are used.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'rows':[{'family':r['family'],'changed':r['changed_dword_count'],'reads':r['attenuation_api0_reads'],'coefficients':r.get('exact_symbolic_coefficients'),'interval':r.get('coefficient_only_alpha_interval_before_render_target_clamp')} for r in rows],'violations':v},indent=2))
 return 0 if out['status']=='D1_CROTA_ATTENUATION_CONSTANTS_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
