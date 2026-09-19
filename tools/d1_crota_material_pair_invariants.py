#!/usr/bin/env python3
"""Promote exact structural invariants across Crota's five paired high-detail materials.

Inputs:
* exact ten-material ROI stage state;
* exact paired GCN resource/instruction differential;
* exact terminal MRT0 channel-class proof;
* exact attenuation constant reduction.

The output groups repeated material pairs by their *serialized/native structure*.
Names remain deliberately neutral: this proves shared inputs, shader differences,
terminal channel classes and cbuffer-prefix relationships, not engine pass order or
appearance semantics.
"""
from __future__ import annotations
import argparse,collections,hashlib,json
from pathlib import Path

PAIRS=[
 ('8108E7A9','8108E7AB','8108E955','8108E958'),
 ('8108E7B2','8108E7B4','8108E955','8108E958'),
 ('8108E7AA','8108E7AC','8108E956','8108E959'),
 ('8108E7B3','8108E7B5','8108E956','8108E959'),
 ('8108E7B1','809DD1DC','8108E953','80AAE1CD'),
]
def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def tex(s):return [(int(x['texture_index']),norm(x['texture'])) for x in (s.get('textures') or {}).get('items',[])]
def samp(s):return [(int(x['inline_index']),norm(x['sampler_taghash']),str(x.get('inline_raw_hex') or '').lower()) for x in s.get('sampler_references',[])]
def vec(s,k):return [str(x.get('raw_hex') or '').lower() for x in (s.get(k) or {}).get('items',[])]
def stable(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--stage-state',type=Path,required=True)
 ap.add_argument('--paired-gcn',type=Path,required=True)
 ap.add_argument('--mrt0-proof',type=Path,required=True)
 ap.add_argument('--attenuation',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 st=json.loads(a.stage_state.read_text());gd=json.loads(a.paired_gcn.read_text())
 mr=json.loads(a.mrt0_proof.read_text());at=json.loads(a.attenuation.read_text())
 v=[];rows=[]
 if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):v.append('stage state not exact')
 if gd.get('status')!='D1_GCN_PAIRED_SHADER_DIFFERENTIAL_EXACT' or gd.get('violations'):v.append('paired GCN not exact')
 if mr.get('status')!='D1_GCN_TERMINAL_MRT0_EXPORT_EXACT' or mr.get('violations'):v.append('MRT0 proof not exact')
 if at.get('status')!='D1_CROTA_ATTENUATION_CONSTANTS_EXACT' or at.get('violations'):v.append('attenuation reduction not exact')
 mats={norm(k):x for k,x in (st.get('materials') or {}).items()}
 gp={(norm(x['a']),norm(x['b'])):x for x in gd.get('pairs',[])}
 mrt={norm(x['shader']):x for x in mr.get('shaders',[])}
 ar={x['attenuation_shader']:x for x in at.get('rows',[])}

 for cm,pm,cps,pps in PAIRS:
  c=mats.get(cm);p=mats.get(pm)
  if not c or not p:v.append(f'{cm}/{pm}: material missing');continue
  if c.get('error') or p.get('error'):v.append(f'{cm}/{pm}: material error');continue
  if norm(c['ps']['shader'])!=cps or norm(p['ps']['shader'])!=pps:v.append(f'{cm}/{pm}: shader identity drift')
  if list(c.get('material_state4_u8') or [None])[0]!=0x88 or list(p.get('material_state4_u8') or [None])[0]!=0x88:
   v.append(f'{cm}/{pm}: byte0 is not exact 0x88')
  diff=gp.get((cps,pps))
  if diff is None:v.append(f'{cps}/{pps}: paired GCN row missing')
  ct,pt=tex(c['ps']),tex(p['ps']);cs,ps=samp(c['ps']),samp(p['ps'])
  ctf,ptf=(c['ps'].get('tfx_program_sha256'),p['ps'].get('tfx_program_sha256'))
  cp,pp=vec(c['ps'],'tfx_private_constants'),vec(p['ps'],'tfx_private_constants')
  cb,pb=vec(c['ps'],'cbuffers'),vec(p['ps'],'cbuffers')
  prefix=cb[:len(pb)]==pb
  if pps in ('8108E958','8108E959'):
   structural='SHARED_SERIALIZED_RESOURCE_PROGRAM_DIFFERENT_PIXEL_SHADER'
   if not (ct==pt and cs==ps and ctf==ptf and cp==pp and prefix):
    v.append(f'{cm}/{pm}: expected shared serialized family invariant failed')
  elif pps=='80AAE1CD':
   structural='RESOURCE_BEARING_COLOR_PARTNER_RESOURCE_EMPTY_CONSTANT_OUTPUT'
   if pt or ps or (p['ps'].get('tfx_bytecode') or {}).get('count',0):
    v.append(f'{pm}: constant-output partner unexpectedly has serialized PS resources/program')
  else:structural='UNCLASSIFIED';v.append(f'{cm}/{pm}: unknown partner family')
  cr=mrt.get(cps);pr=mrt.get(pps)
  if not cr or not pr:v.append(f'{cps}/{pps}: terminal MRT row missing')
  term=None if not cr or not pr else {'color':cr['channel_classes'],'partner':pr['channel_classes']}
  if term:
   if term['color']!={'R':'COMPUTED','G':'COMPUTED','B':'COMPUTED','A':'ZERO'}:v.append(f'{cps}: terminal class drift')
   want={'R':'ZERO','G':'ZERO','B':'ZERO','A':'ONE' if pps=='80AAE1CD' else 'COMPUTED'}
   if term['partner']!=want:v.append(f'{pps}: terminal class drift {term["partner"]}')
  row={
   'color_material':cm,'partner_material':pm,'color_pixel_shader':cps,'partner_pixel_shader':pps,
   'structural_family':structural,
   'material_state4_equal':c.get('material_state4_hex')==p.get('material_state4_hex'),
   'color_material_state4_hex':c.get('material_state4_hex'),'partner_material_state4_hex':p.get('material_state4_hex'),
   'same_vertex_shader':norm(c['vs']['shader'])==norm(p['vs']['shader']),
   'serialized_ps_inputs':{
     'textures_equal':ct==pt,'samplers_equal':cs==ps,'tfx_program_equal':ctf==ptf,
     'private_constants_equal':cp==pp,'cbuffers_equal':cb==pb,
     'partner_cbuffers_exact_prefix_of_color':prefix,
     'color_only_cbuffer_suffix_count':len(cb)-len(pb) if prefix else None,
     'color_texture_map':ct,'partner_texture_map':pt,
   },
   'terminal_mrt0':term,
   'paired_gcn_resource':None if diff is None else {
      'shared_texture_indices':diff['resource_usage']['shared_texture_indices'],
      'color_only_texture_indices':diff['resource_usage']['a_only_texture_indices'],
      'partner_only_texture_indices':diff['resource_usage']['b_only_texture_indices'],
   },
   'attenuation_direct_alpha':None if pps=='80AAE1CD' else ({
      'direct_api0_dwords':ar[pps]['terminal_alpha_direct_api0_dwords'],
      'value_slice':ar[pps]['terminal_alpha_value_slice'],
   } if pps in ar else None),
  }
  row['invariant_sha256']=stable({k:x for k,x in row.items() if k not in ('color_material','partner_material')})
  rows.append(row)

 fam=collections.defaultdict(list)
 for r in rows:fam[(r['color_pixel_shader'],r['partner_pixel_shader'],r['structural_family'])].append(r)
 families=[]
 for (cps,pps,k),rr in sorted(fam.items()):
  families.append({
   'color_pixel_shader':cps,'partner_pixel_shader':pps,'structural_family':k,
   'material_pair_count':len(rr),'material_pairs':[[x['color_material'],x['partner_material']] for x in rr],
   'all_same_vertex_shader':all(x['same_vertex_shader'] for x in rr),
   'all_state4_equal':all(x['material_state4_equal'] for x in rr),
   'all_textures_equal':all(x['serialized_ps_inputs']['textures_equal'] for x in rr),
   'all_samplers_equal':all(x['serialized_ps_inputs']['samplers_equal'] for x in rr),
   'all_tfx_equal':all(x['serialized_ps_inputs']['tfx_program_equal'] for x in rr),
   'all_partner_cbuffers_prefix':all(x['serialized_ps_inputs']['partner_cbuffers_exact_prefix_of_color'] for x in rr),
  })
 out={'schema':'d1_crota_material_pair_invariants/v1',
      'status':'D1_CROTA_MATERIAL_PAIR_INVARIANTS_EXACT' if len(rows)==5 and len(families)==3 and not v else 'D1_CROTA_MATERIAL_PAIR_INVARIANTS_PARTIAL',
      'pair_count':len(rows),'structural_family_count':len(families),'families':families,'pairs':rows,'violations':v,
      'semantic_boundary':{'pair_structure':'EXACT','resource_program_equality':'EXACT','terminal_channel_classes':'EXACT','native_pass_order':'WITHHELD','runtime_scalar_semantics':'WITHHELD','portable_material_semantics':'WITHHELD'},
      'policy':'Structural family labels describe only exact serialized/native similarities. They are not engine pass names. The constant-output family is identified only from its exact resource-empty material plus MRT0=(0,0,0,1).'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'families':families,'violations':v},indent=2))
 return 0 if out['status']=='D1_CROTA_MATERIAL_PAIR_INVARIANTS_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
