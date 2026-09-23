#!/usr/bin/env python3
"""Fail-closed coverage gate for exact Tower light terminal-MRT0 factorizations."""
from __future__ import annotations
import argparse,glob,json
from pathlib import Path

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--material-manifest',type=Path,required=True)
 ap.add_argument('--reports-dir',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 m=json.loads(a.material_manifest.read_text());v=[]
 if m.get('status')!='D1_WORLD_LIGHT_MATERIAL_MANIFEST_COMPLETE':v.append('material manifest not exact')
 freq={norm(k):int(x) for k,x in (m.get('pixel_shader_frequency') or {}).items()}
 if len(freq)!=32:v.append(f'pixel shader family count {len(freq)} != 32')
 if sum(freq.values())!=737:v.append(f'light frequency sum {sum(freq.values())} != 737')
 paths=sorted(a.reports_dir.glob('TOWER_LIGHT_*_FACTORIZATION.json'))
 rows=[];seen={}
 for p in paths:
  try:d=json.loads(p.read_text())
  except Exception as ex:
   v.append(f'{p.name}: JSON read failed {ex}');continue
  sh=norm(d.get('shader'))
  if sh in seen:
   v.append(f'{sh}: duplicate factorization reports {seen[sh]} and {p.name}');continue
  seen[sh]=p.name
  status=str(d.get('status') or '')
  exact=status.endswith('_EXACT')
  violations=d.get('violations') or []
  instances=int(d.get('instance_count',-1))
  expected=freq.get(sh)
  if expected is None:v.append(f'{sh}: factorization shader absent from source manifest')
  elif instances!=expected:v.append(f'{sh}: instance count {instances} != manifest {expected}')
  if not exact:v.append(f'{sh}: status not exact: {status}')
  if violations:v.append(f'{sh}: factorization violations {violations}')
  eq=d.get('exact_terminal_equation') or {}
  if not eq or 'mrt0_a' not in eq:v.append(f'{sh}: terminal equation missing')
  rows.append({
   'shader':sh,'report':p.name,'status':status,'instance_count':instances,
   'manifest_instance_count':expected,'mrt0_alpha':eq.get('mrt0_a'),
   'gate':eq.get('gate'),'vector_form':eq.get('vector_form') or eq.get('mrt0_rgb'),
  })
 missing=sorted(set(freq)-set(seen))
 extra=sorted(set(seen)-set(freq))
 if missing:v.append(f'missing factorization families {missing}')
 if extra:v.append(f'extra factorization families {extra}')
 if len(seen)!=32:v.append(f'unique factorization count {len(seen)} != 32')
 covered=sum(freq.get(sh,0) for sh in seen if sh in freq)
 if covered!=737:v.append(f'covered light instances {covered} != 737')
 rows.sort(key=lambda x:(-int(x['instance_count']),x['shader']))
 out={
  'schema':'d1_tower_light_factorization_coverage/v1',
  'status':'D1_TOWER_LIGHT_TERMINAL_MRT0_FACTORIZATION_COVERAGE_EXACT' if not v else 'D1_TOWER_LIGHT_TERMINAL_MRT0_FACTORIZATION_COVERAGE_PARTIAL',
  'source_shader_family_count':len(freq),
  'factorized_shader_family_count':len(seen),
  'source_light_instance_count':sum(freq.values()),
  'factorized_light_instance_count':covered,
  'family_coverage_fraction':(len(seen)/len(freq) if freq else None),
  'instance_coverage_fraction':(covered/sum(freq.values()) if freq and sum(freq.values()) else None),
  'missing_shader_families':missing,'extra_shader_families':extra,
  'rows':rows,'violations':v,
  'semantic_boundary':{
   'terminal_mrt0_factorization_coverage':'EXACT_SOURCE_MANIFEST_JOIN',
   'all_renderer_resource_human_semantics':'NOT_IMPLIED',
   'full_light_pass_equivalence':'NOT_IMPLIED',
   'MRT1_and_framebuffer_composition':'NOT_IMPLIED_BY_MRT0_COVERAGE',
  },
  'policy':'32/32 terminal-MRT0 factorization coverage closes native terminal arithmetic for the source light-family census. It does not by itself identify renderer input meanings, MRT1 meanings, blend/framebuffer ordering, or prove a complete portable light renderer.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({
  'status':out['status'],'families':f"{len(seen)}/{len(freq)}",
  'instances':f"{covered}/{sum(freq.values())}",'missing':missing,'violations':v,
 },indent=2))
 return 0 if not v else 2

if __name__=='__main__':raise SystemExit(main())
