#!/usr/bin/env python3
"""Aggregate exact Tower sky terminal-equation proof coverage.

Accepts any number of fail-closed proof JSONs that expose exact rows with
shader and visible_material_count. Duplicate coverage is rejected unless the
duplicated row is byte-identical in its exact terminal equation.

Coverage is measured against the source-closed 43-family / 74-material sky
manifest. This tool only makes the remaining equation queue explicit.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--proof',type=Path,action='append',required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    m=json.loads(a.manifest.read_text());v=[];covered={};sources={}
    if m.get('status')!='D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT' or m.get('material_decode_errors') or m.get('texture_errors'):
        v.append('manifest not exact')
    freq={norm(k):int(x) for k,x in (m.get('pixel_shader_frequency') or {}).items()}
    if len(freq)!=43 or sum(freq.values())!=74:v.append(f'manifest corpus drift families={len(freq)} weight={sum(freq.values())}')
    for p in a.proof:
        d=json.loads(p.read_text())
        status=str(d.get('status',''))
        if not status.endswith('_EXACT'):v.append(f'{p}: proof status not exact: {status}')
        if d.get('violations'):v.append(f'{p}: proof violations present')
        for r in d.get('rows',[]):
            sh=norm(r.get('shader'))
            if sh not in freq:v.append(f'{p}: shader {sh} outside sky corpus');continue
            w=int(r.get('visible_material_count',-1))
            if w!=freq[sh]:v.append(f'{p}: {sh} weight {w} != manifest {freq[sh]}')
            eq=r.get('exact_terminal_equation')
            if sh in covered:
                if covered[sh]!=eq:v.append(f'{sh}: conflicting terminal equation proofs')
                continue
            covered[sh]=eq;sources[sh]=str(p)
    missing=sorted(set(freq)-set(covered),key=lambda x:(-freq[x],x))
    rows=[{'shader':sh,'visible_material_count':freq[sh],'proof':sources[sh],'exact_terminal_equation':covered[sh]} for sh in sorted(covered,key=lambda x:(-freq[x],x))]
    cw=sum(freq[x] for x in covered)
    out={
        'schema':'d1_tower_sky_factorization_coverage/v1',
        'status':'D1_TOWER_SKY_FACTORIZATION_COVERAGE_EXACT' if not v else 'D1_TOWER_SKY_FACTORIZATION_COVERAGE_PARTIAL',
        'total_shader_family_count':43,'total_visible_material_count':74,
        'covered_shader_family_count':len(covered),'covered_visible_material_count':cw,
        'shader_family_coverage_fraction':len(covered)/43,
        'visible_material_coverage_fraction':cw/74,
        'missing_shader_family_count':len(missing),
        'missing_visible_material_count':sum(freq[x] for x in missing),
        'highest_priority_missing_shaders':[{'shader':x,'visible_material_count':freq[x]} for x in missing],
        'covered_rows':rows,'violations':v,
        'semantic_boundary':{
            'coverage':'EXACT_PROOF_SET_ACCOUNTING',
            'terminal_equations':'INHERITED_FROM_EXACT_INPUT_PROOFS',
            'sky_human_semantics':'WITHHELD',
            'portable_renderer_equivalence':'NOT_IMPLIED',
        },
        'policy':'Coverage means a pinned exact terminal MRT0 equation exists for that native family. It does not mean active sky selection, live renderer values, blending/order, or complete portable renderer equivalence is solved.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'covered_families':len(covered),'covered_materials':cw,
                      'family_fraction':out['shader_family_coverage_fraction'],'material_fraction':out['visible_material_coverage_fraction'],
                      'missing':out['highest_priority_missing_shaders'],'violations':v},indent=2))
    return 0 if out['status']=='D1_TOWER_SKY_FACTORIZATION_COVERAGE_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
