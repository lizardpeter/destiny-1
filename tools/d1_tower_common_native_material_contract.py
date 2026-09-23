#!/usr/bin/env python3
"""Build an exact native-render contract for all 99 Tower common materials.

Inputs must already satisfy the complete common terminal-behavior closure:
- 64 shader families have exact flattened terminal equations;
- 8093E501 is preserved as an exact native CFG program plus terminal reduction.

The contract joins those proofs back to each exact serialized SMaterial_ROI row:
texture t# bindings, sampler records, TFX bytes, PS constant-container identity,
native shader identity, exact cbuffer dword reads, and unresolved runtime inputs.

This is a renderer handoff, not a portable-render equivalence claim.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

VGPR_RE=re.compile(r'INPUT_VGPR\((v\d+)\)')

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def load(p):return json.loads(p.read_text())

def main():
 ap=argparse.ArgumentParser()
 for n in (
  'manifest','shader-report','cbuffer-usage','terminal-closure','symbolic-coverage',
  'alpha-cfg','be9-bea-cfg','ps-80c997a7','ps-80ca0bfa','ps-80ca1427',
  'ps-8093e501','out'
 ): ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args()

 m=load(a.manifest);sr=load(a.shader_report);cb=load(a.cbuffer_usage)
 tc=load(a.terminal_closure);sy=load(a.symbolic_coverage)
 alpha=load(a.alpha_cfg);pair=load(a.be9_bea_cfg);p997=load(a.ps_80c997a7)
 pbfa=load(a.ps_80ca0bfa);p1427=load(a.ps_80ca1427);p501=load(a.ps_8093e501)
 violations=[]

 if m.get('status')!='D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT' or m.get('material_decode_errors') or m.get('texture_errors'):
  violations.append('material manifest not exact')
 if sr.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or sr.get('error_count'):
  violations.append('shader report not exact')
 if cb.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or cb.get('missing_usage'):
  violations.append('cbuffer usage not exact')
 if tc.get('status')!='D1_TOWER_COMMON_TERMINAL_BEHAVIOR_CLOSED' or tc.get('violations'):
  violations.append('terminal closure not exact')
 if sy.get('status')!='D1_TOWER_COMMON_SYMBOLIC_COVERAGE_EXACT' or sy.get('violations'):
  violations.append('symbolic coverage not exact')

 sby={norm(x['shader']):x for x in sr.get('shaders',[]) if not x.get('error')}
 cby={norm(x['shader']):x for x in cb.get('shaders',[])}
 syby={norm(x['shader']):x for x in sy.get('exact_rows',[])}
 flat={norm(x['shader']):x for x in tc.get('flattened_rows',[])}
 prog={norm(x['shader']):x for x in tc.get('program_rows',[])}

 alpha_by={norm(x['shader']):x for x in alpha.get('rows',[])}
 pair_by={norm(x['shader']):x for x in pair.get('rows',[])}

 def equation_contract(sh):
  if sh in prog:
   if sh!=norm(p501.get('shader')):
    raise ValueError(f'{sh}: unknown program closure source')
   return {
    'closure_level':'EXACT_NATIVE_CFG_PROGRAM_PLUS_TERMINAL_REDUCTION',
    'source_proof':'8093E501_CFG_PROGRAM_PROOF',
    'program_phases':p501.get('program_phases'),
    'terminal_reduction':p501.get('exact_terminal_reduction'),
    'cfg_summary':p501.get('cfg_summary'),
   }
  row=flat.get(sh)
  if not row: raise ValueError(f'{sh}: terminal closure row missing')
  src=row.get('source')
  if src=='TOWER_COMMON65_SYMBOLIC_COVERAGE':
   q=syby.get(sh)
   if not q:raise ValueError(f'{sh}: symbolic exact row missing')
   return {
    'closure_level':'EXACT_FLATTENED_TERMINAL_EQUATION',
    'source_proof':src,
    'terminal_expressions':q.get('terminal_expressions'),
    'terminal_expression_sha256':q.get('terminal_expression_sha256'),
    'terminal_mrt0_export_address':q.get('terminal_mrt0_export_address'),
    'terminal_mrt0_compressed':q.get('terminal_mrt0_compressed'),
   }
  if src=='ALPHA_BRANCH_CFG_PROOF':
   q=alpha_by.get(sh)
   return {'closure_level':'EXACT_FLATTENED_TERMINAL_EQUATION','source_proof':src,
           'terminal_equations':q.get('exact_cfg_equation'),'export_lane_gate':q.get('exact_export_lane_gate'),
           'terminal_mrt0_export_address':q.get('terminal_mrt0_export_address')}
  if src=='80CA0BE9_80CA0BEA_CFG_PROOF':
   q=pair_by.get(sh)
   return {'closure_level':'EXACT_FLATTENED_TERMINAL_EQUATION','source_proof':src,
           'common_cfg_equation':q.get('common_cfg_equation'),'terminal_equations':q.get('terminal_equation'),
           'terminal_mrt0_export_address':q.get('terminal_mrt0_export_address')}
  if src=='80C997A7_CFG_PROOF':
   return {'closure_level':'EXACT_FLATTENED_TERMINAL_EQUATION','source_proof':src,
           'terminal_equations':p997.get('exact_cfg_equation'),
           'terminal_mrt0_export_address':p997.get('terminal_mrt0_export_address')}
  if src=='80CA0BFA_CFG_PROOF':
   return {'closure_level':'EXACT_FLATTENED_TERMINAL_EQUATION','source_proof':src,
           'cfg_selector':pbfa.get('exact_cfg_selector'),'terminal_equations':pbfa.get('exact_terminal_equation')}
  if src=='80CA1427_CFG_PROOF':
   return {'closure_level':'EXACT_FLATTENED_TERMINAL_EQUATION','source_proof':src,
           'cfg_matrix_selector':p1427.get('exact_cfg_matrix_selector'),'terminal_equations':p1427.get('exact_terminal_equation')}
  raise ValueError(f'{sh}: unsupported flattened proof source {src!r}')

 families={}
 for sh in sorted(set(flat)|set(prog)):
  s=sby.get(sh);c=cby.get(sh)
  if not s or not c:
   violations.append(f'{sh}: shader/cbuffer row missing');continue
  try: eq=equation_contract(sh)
  except Exception as ex:
   violations.append(str(ex));continue
  txt=json.dumps(eq,sort_keys=True)
  vgprs=sorted(set(VGPR_RE.findall(txt)),key=lambda x:int(x[1:]))
  slots={str(k):[int(z) for z in v] for k,v in (c.get('api_slot_read_dwords') or {}).items()}
  families[sh]={
   'shader':sh,
   'visible_material_count':int(s.get('visible_material_count',0)),
   'native_shader':s.get('native_shader'),
   'native_sha256':s.get('native_sha256'),
   'gcn_sha256':s.get('gcn_sha256'),
   'gcn_bytes':int(s.get('gcn_bytes',0)),
   'cbuffer_dword_reads':slots,
   'material_api0_dwords':slots.get('0',[]),
   'nonmaterial_api_dword_reads':{k:v for k,v in slots.items() if k!='0'},
   'initial_vgpr_inputs':vgprs,
   'terminal_contract':eq,
  }

 materials={}
 for mh,mr in sorted((m.get('materials') or {}).items()):
  mh=norm(mh);sh=norm(mr.get('pixel_shader'))
  fam=families.get(sh)
  if not fam:
   violations.append(f'{mh}: shader {sh} lacks terminal contract');continue
  binds=[{
    'stage':x['stage'],'texture_index':int(x['texture_index']),'texture':norm(x['texture'])
  } for x in mr.get('bindings',[])]
  ps_sam=(mr.get('samplers') or {}).get('ps') or {}
  materials[mh]={
   'material':mh,
   'source_package_id':(mr.get('source') or {}).get('package_id'),
   'vertex_shader':norm(mr.get('vertex_shader')),
   'pixel_shader':sh,
   'native_pixel_shader':fam['native_shader'],
   'gcn_sha256':fam['gcn_sha256'],
   'texture_bindings':binds,
   'ps_sampler_records':ps_sam.get('items') or [],
   'ps_tfx_bytes_hex':((mr.get('tfx') or {}).get('ps') or {}).get('bytes_hex',''),
   'ps_vector4_container':norm(((mr.get('constants') or {}).get('ps_vector4_container'))),
   'material_api0_dwords_used':fam['material_api0_dwords'],
   'nonmaterial_runtime_inputs':fam['nonmaterial_api_dword_reads'],
   'initial_vgpr_inputs':fam['initial_vgpr_inputs'],
   'terminal_contract':fam['terminal_contract'],
   'replay_boundary':{
    'serialized_material_state':'EXACT',
    'native_terminal_behavior':'EXACT',
    'nonmaterial_runtime_values':'WITHHELD_UNLESS_SEPARATELY_CAPTURED',
    'initial_vgpr_values_and_semantics':'WITHHELD_UNLESS_VERTEX_OR_RUNTIME_PROVEN',
    'blend_framebuffer_order':'SEPARATE_RENDER_STATE_PROOF_REQUIRED',
    'portable_filter_derivative_rounding':'NOT_BIT_IDENTICAL_UNLESS_SEPARATELY_PROVEN',
   },
  }

 if len(families)!=65:violations.append(f'family contract count {len(families)} != 65')
 if len(materials)!=99:violations.append(f'material contract count {len(materials)} != 99')
 if sum(x['visible_material_count'] for x in families.values())!=99:
  violations.append('family visible-material weights do not sum to 99')
 program_count=sum(x['terminal_contract']['closure_level'].endswith('TERMINAL_REDUCTION') for x in families.values())
 flattened_count=sum(x['terminal_contract']['closure_level']=='EXACT_FLATTENED_TERMINAL_EQUATION' for x in families.values())
 runtime_materials=sum(bool(x['nonmaterial_runtime_inputs']) for x in materials.values())
 vgpr_materials=sum(bool(x['initial_vgpr_inputs']) for x in materials.values())

 out={
  'schema':'d1_tower_common_native_material_contract/v1',
  'status':'D1_TOWER_COMMON_NATIVE_MATERIAL_CONTRACT_EXACT' if len(families)==65 and len(materials)==99 and not violations else 'D1_TOWER_COMMON_NATIVE_MATERIAL_CONTRACT_PARTIAL',
  'shader_family_count':len(families),'material_count':len(materials),
  'flattened_equation_family_count':flattened_count,
  'cfg_program_family_count':program_count,
  'materials_with_nonmaterial_runtime_inputs':runtime_materials,
  'materials_with_initial_vgpr_inputs':vgpr_materials,
  'shader_families':families,'materials':materials,'violations':violations,
  'semantic_boundary':{
   'material_shader_texture_sampler_tfx_identity':'EXACT',
   'terminal_behavior':'EXACT_64_EQUATIONS_PLUS_1_CFG_PROGRAM',
   'API0_dword_identity':'EXACT_MATERIAL_CBUFFER_SLOT_OFFSETS',
   'nonmaterial_api_dword_identity':'EXACT_SHADER_INPUT_SLOT_OFFSETS_LIVE_VALUES_MAY_BE_WITHHELD',
   'human_pass_names':'NOT_REQUIRED_FOR_CONTRACT',
   'portable_renderer_equivalence':'NOT_CLAIMED',
  },
  'policy':'This is the exact machine-readable handoff from recovered Tower common material state to native terminal shader behavior. Consumers must preserve every replay boundary rather than substitute generic PBR defaults silently.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'families':len(families),'materials':len(materials),
  'flattened_equations':flattened_count,'cfg_programs':program_count,
  'materials_with_nonmaterial_runtime_inputs':runtime_materials,
  'materials_with_initial_vgpr_inputs':vgpr_materials,'violations':violations},indent=2))
 return 0 if out['status']=='D1_TOWER_COMMON_NATIVE_MATERIAL_CONTRACT_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
