#!/usr/bin/env python3
"""Account exact symbolic terminal-equation coverage for all Tower common shaders.

The input symbolic reducer may be PARTIAL: rows with exact_terminal_expression=True
are accepted only when their native shader identity is present in the exact common
shader report and their visible-material frequency matches the exact common material
manifest. Rows with unresolved terminal markers remain an explicit work queue.

This is coverage accounting, not a human material-role classifier.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--shader-report',type=Path,required=True)
    ap.add_argument('--symbolic',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    m=json.loads(a.manifest.read_text())
    sr=json.loads(a.shader_report.read_text())
    sy=json.loads(a.symbolic.read_text())
    violations=[]

    if m.get('status')!='D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT' or m.get('material_decode_errors') or m.get('texture_errors'):
        violations.append('common material manifest not exact')
    if sr.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or sr.get('error_count'):
        violations.append('common shader report not exact')
    if sy.get('schema')!='d1_gcn_terminal_symbolic_reducer/v1':
        violations.append(f"unexpected symbolic schema {sy.get('schema')!r}")

    freq={norm(k):int(v) for k,v in (m.get('pixel_shader_frequency') or {}).items()}
    sby={norm(x['shader']):x for x in sr.get('shaders',[]) if not x.get('error')}
    yby={norm(x['shader']):x for x in sy.get('shaders',[])}

    if len(freq)!=65:
        violations.append(f'common manifest family count {len(freq)} != 65')
    if len(sby)!=65:
        violations.append(f'common exact shader count {len(sby)} != 65')

    missing_symbolic=sorted(set(freq)-set(yby))
    if missing_symbolic:
        violations.append(f'symbolic rows missing {missing_symbolic}')

    exact=[];unresolved=[]
    for sh in sorted(freq,key=lambda x:(-freq[x],x)):
        s=sby.get(sh);y=yby.get(sh)
        if not s or not y:
            continue
        row={
            'shader':sh,
            'visible_material_count':freq[sh],
            'native_shader':s.get('native_shader'),
            'native_sha256':s.get('native_sha256'),
            'gcn_sha256':s.get('gcn_sha256'),
            'gcn_bytes':int(s.get('gcn_bytes',0)),
            'terminal_mrt0_export_address':y.get('terminal_mrt0_export_address'),
            'terminal_mrt0_compressed':bool(y.get('terminal_mrt0_compressed')),
            'terminal_expression_sha256':y.get('terminal_expression_sha256'),
            'terminal_expressions':y.get('terminal_expressions'),
            'terminal_unresolved_markers':y.get('terminal_unresolved_markers'),
            'terminal_bad_channels':y.get('terminal_bad_channels') or [],
            'unsupported_operations':y.get('unsupported_operations') or [],
            'off_path_unsupported_operation_count':y.get('off_path_unsupported_operation_count'),
            'exact_terminal_expression':bool(y.get('exact_terminal_expression')),
        }
        if row['exact_terminal_expression'] and not any((row['terminal_unresolved_markers'] or {}).values()):
            exact.append(row)
        else:
            unresolved.append(row)

    ew=sum(x['visible_material_count'] for x in exact)
    uw=sum(x['visible_material_count'] for x in unresolved)
    total=sum(freq.values())
    out={
        'schema':'d1_tower_common_symbolic_coverage/v1',
        'status':'D1_TOWER_COMMON_SYMBOLIC_COVERAGE_EXACT' if len(exact)+len(unresolved)==65 and not violations else 'D1_TOWER_COMMON_SYMBOLIC_COVERAGE_PARTIAL',
        'total_shader_family_count':65,
        'total_visible_material_count':total,
        'exact_terminal_equation_family_count':len(exact),
        'exact_terminal_equation_visible_material_count':ew,
        'unresolved_terminal_equation_family_count':len(unresolved),
        'unresolved_terminal_equation_visible_material_count':uw,
        'family_coverage_fraction':len(exact)/65,
        'visible_material_coverage_fraction':ew/total if total else None,
        'exact_rows':exact,
        'highest_priority_unresolved_rows':sorted(
            unresolved,
            key=lambda x:(-x['visible_material_count'],-x['gcn_bytes'],x['shader'])
        ),
        'violations':violations,
        'semantic_boundary':{
            'terminal_equation_exactness':'INHERITED_FROM_OPERATION_PRESERVING_NATIVE_GCN_REDUCER',
            'shader_identity':'EXACT_RETAIL_GCN_IDENTITY',
            'coverage_weight':'EXACT_VISIBLE_MATERIAL_FREQUENCY',
            'human_material_roles':'WITHHELD',
            'runtime_global_producers':'WITHHELD',
            'portable_renderer_equivalence':'NOT_IMPLIED',
        },
        'policy':'An exact row means every terminal MRT0 channel is expressible using the audited native GCN subset with exact texture/cbuffer/interpolant provenance. It does not name the pass or imply Blender/runtime equivalence.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],
        'exact_families':len(exact),
        'exact_material_weight':ew,
        'family_fraction':out['family_coverage_fraction'],
        'material_fraction':out['visible_material_coverage_fraction'],
        'unresolved':[{
            'shader':x['shader'],
            'visible_material_count':x['visible_material_count'],
            'gcn_bytes':x['gcn_bytes'],
            'bad_channels':x['terminal_bad_channels'],
            'unresolved':x['terminal_unresolved_markers'],
            'unsupported':x['unsupported_operations'][:8],
        } for x in out['highest_priority_unresolved_rows'][:30]],
        'violations':violations,
    },indent=2))
    return 0 if out['status']=='D1_TOWER_COMMON_SYMBOLIC_COVERAGE_EXACT' else 2

if __name__=='__main__':
    raise SystemExit(main())
