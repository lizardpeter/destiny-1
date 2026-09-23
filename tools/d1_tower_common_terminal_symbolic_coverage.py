#!/usr/bin/env python3
"""Fail-closed coverage proof for all 65 Tower common-layer terminal equations.

The pinned aggregate digest is over a canonical sorted projection containing, for
every shader family:
- shader/native/GFX identities and byte count;
- visible-material frequency;
- terminal MRT0 address/compression mode;
- operation-preserving R/G/B/A expression hashes;
- whether an exact initial hardware VGPR leaf survives to MRT0.

This avoids embedding enormous symbolic expressions while still pinning the complete
65-family corpus. Human material meanings and live renderer input values remain
outside this proof.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

PINNED_FAMILY_COUNT=65
PINNED_VISIBLE_MATERIAL_COUNT=99
PINNED_PROJECTION_SHA256='8dd0014b2b95c50c89f301b7d59898bc1ebba590b7965d09a1d96e4a2c7abbb0'
PINNED_INITIAL_VGPR_SHADERS={'80AADBB4','80AAE1F5'}

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--shader-report',type=Path,required=True)
 ap.add_argument('--symbolic',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 sr=json.loads(a.shader_report.read_text());sy=json.loads(a.symbolic.read_text());v=[]
 if sr.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or sr.get('error_count'):v.append('shader report not exact')
 if sy.get('status')!='D1_GCN_TERMINAL_SYMBOLIC_REDUCER_EXACT' or sy.get('violations'):v.append('symbolic reducer not exact')
 srows={norm(x['shader']):x for x in sr.get('shaders',[]) if not x.get('error')}
 yrows={norm(x['shader']):x for x in sy.get('shaders',[])}
 if len(srows)!=PINNED_FAMILY_COUNT:v.append(f'shader family count {len(srows)} != {PINNED_FAMILY_COUNT}')
 if set(srows)!=set(yrows):v.append(f'shader set mismatch extract-only={sorted(set(srows)-set(yrows))} symbolic-only={sorted(set(yrows)-set(srows))}')

 projection=[];initial=set();visible=0
 for sh in sorted(set(srows)&set(yrows)):
  s=srows[sh];y=yrows[sh]
  if not y.get('exact_terminal_expression'):v.append(f'{sh}: terminal expression not exact')
  if any(y.get('terminal_unresolved_markers',{}).values()):v.append(f'{sh}: unresolved terminal markers {y["terminal_unresolved_markers"]}')
  weight=int(s.get('visible_material_count',0));visible+=weight
  uses_initial=any('INPUT_VGPR(' in str(e) for e in (y.get('terminal_expressions') or {}).values())
  if uses_initial:initial.add(sh)
  projection.append({
   'shader':sh,
   'visible_material_count':weight,
   'native_shader':norm(s.get('native_shader')),
   'native_sha256':s.get('native_sha256'),
   'gcn_sha256':s.get('gcn_sha256'),
   'gcn_bytes':int(s.get('gcn_bytes',0)),
   'terminal_mrt0_export_address':y.get('terminal_mrt0_export_address'),
   'terminal_mrt0_compressed':bool(y.get('terminal_mrt0_compressed')),
   'terminal_expression_sha256':y.get('terminal_expression_sha256'),
   'uses_initial_vgpr_leaf':uses_initial,
  })
 if visible!=PINNED_VISIBLE_MATERIAL_COUNT:v.append(f'visible material count {visible} != {PINNED_VISIBLE_MATERIAL_COUNT}')
 if initial!=PINNED_INITIAL_VGPR_SHADERS:v.append(f'initial VGPR shader set drift {sorted(initial)} != {sorted(PINNED_INITIAL_VGPR_SHADERS)}')
 canonical=json.dumps(projection,sort_keys=True,separators=(',',':')).encode()
 digest=hashlib.sha256(canonical).hexdigest()
 if digest!=PINNED_PROJECTION_SHA256:v.append(f'canonical projection sha {digest} != {PINNED_PROJECTION_SHA256}')
 out={
  'schema':'d1_tower_common_terminal_symbolic_coverage/v1',
  'status':'D1_TOWER_COMMON_TERMINAL_SYMBOLIC_COVERAGE_EXACT' if len(projection)==PINNED_FAMILY_COUNT and not v else 'D1_TOWER_COMMON_TERMINAL_SYMBOLIC_COVERAGE_PARTIAL',
  'shader_family_count':len(projection),'visible_material_count':visible,
  'shader_family_coverage_fraction':len(projection)/PINNED_FAMILY_COUNT,
  'visible_material_coverage_fraction':visible/PINNED_VISIBLE_MATERIAL_COUNT,
  'canonical_projection_sha256':digest,
  'initial_vgpr_leaf_shaders':sorted(initial),
  'violations':v,
  'semantic_boundary':{
   'terminal_expression':'EXACT_NATIVE_OPERATION_ORDER',
   'retail_shader_identity':'PINNED_BY_CANONICAL_PROJECTION_DIGEST',
   'initial_vgpr_leaf':'EXACT_HARDWARE_INPUT_REGISTER_IDENTITY_SEMANTIC_WITHHELD',
   'human_material_semantics':'WITHHELD',
   'live_renderer_values_and_producers':'WITHHELD',
   'portable_renderer_equivalence':'NOT_IMPLIED',
  },
  'policy':'This proves complete terminal-equation coverage, not full material meaning. The digest pins every family identity and expression hash. Initial VGPR leaves retain exact register identity only.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
 return 0 if out['status']=='D1_TOWER_COMMON_TERMINAL_SYMBOLIC_COVERAGE_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
