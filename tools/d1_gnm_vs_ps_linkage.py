#!/usr/bin/env python3
"""Join exact PS4 GNM VS export semantics to PS input semantics.

The matching key is the raw 8-bit semantic ID.  Pixel table record order is
preserved as attr_index; VS export records provide out_index (param#).  This tool
does not assign human semantic names such as TEXCOORD/NORMAL.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

ATTR_RE=re.compile(r'\battr(\d+)\.[xyzw]\b')
PARAM_RE=re.compile(r'\bexp\s+param(\d+)\b')

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def attrs(path:Path)->list[int]:
    out=set()
    for line in path.read_text(errors='replace').splitlines():
        out.update(int(x) for x in ATTR_RE.findall(line))
    return sorted(out)

def params(path:Path)->list[int]:
    out=set()
    for line in path.read_text(errors='replace').splitlines():
        out.update(int(x) for x in PARAM_RE.findall(line))
    return sorted(out)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--extract-report',type=Path,required=True)
    ap.add_argument('--disasm-dir',type=Path,required=True)
    ap.add_argument('--link',action='append',required=True,help='VS:PS')
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    d=json.loads(a.extract_report.read_text());by={norm(x['shader']):x for x in d.get('shaders',[])}
    violations=[];rows=[]
    for spec in a.link:
        try:
            vs,ps=(norm(x) for x in spec.split(':',1))
            vr=by[vs];pr=by[ps]
            vg=vr.get('gnm_header') or {};pg=pr.get('gnm_header') or {}
            if vg.get('status')!='D1_PS4_GNM_SHADER_HEADER_EXACT' or vg.get('stage')!='VertexShader':
                raise ValueError(f'{vs}: exact VS GNM header absent')
            if pg.get('status')!='D1_PS4_GNM_SHADER_HEADER_EXACT' or pg.get('stage')!='PixelShader':
                raise ValueError(f'{ps}: exact PS GNM header absent')
            vex=vg.get('vertex_export_semantics') or []
            pin=pg.get('pixel_input_semantics') or []
            sem_to_export={}
            for x in vex:
                sem=int(x['semantic'])
                if sem in sem_to_export: raise ValueError(f'{vs}: duplicate export semantic {sem}')
                sem_to_export[sem]=x
            mapping=[];unmatched=[]
            for x in pin:
                sem=int(x['semantic']);ve=sem_to_export.get(sem)
                q={
                    'attr_index':int(x['attr_index']),'semantic':sem,
                    'vs_param_index':None if ve is None else int(ve['out_index']),
                    'vs_export_f16':None if ve is None else int(ve['export_f16']),
                    'ps_default_value':int(x['default_value']),
                    'ps_flat':bool(x['is_flat_shaded']),'ps_linear':bool(x['is_linear']),
                    'ps_custom':bool(x['is_custom']),
                }
                mapping.append(q)
                if ve is None and q['ps_default_value']==0: unmatched.append(q)
            vp=a.disasm_dir/f'PS_{vs}_GFX700.s';pp=a.disasm_dir/f'PS_{ps}_GFX700.s'
            if not vp.exists(): vp=a.disasm_dir/f'PS_{vs}.s'
            if not pp.exists(): pp=a.disasm_dir/f'PS_{ps}.s'
            if not vp.exists() or not pp.exists(): raise ValueError(f'{vs}:{ps}: disassembly absent')
            used_attrs=attrs(pp);emitted=params(vp)
            mapped_by_attr={x['attr_index']:x for x in mapping}
            used_rows=[]
            for i in used_attrs:
                q=mapped_by_attr.get(i)
                if q is None: raise ValueError(f'{ps}: consumed attr{i} absent from PS semantic table')
                if q['vs_param_index'] is None and q['ps_default_value']==0:
                    raise ValueError(f'{ps}: consumed attr{i} has no VS export/default')
                if q['vs_param_index'] is not None and q['vs_param_index'] not in emitted:
                    raise ValueError(f'{vs}:{ps}: attr{i} links param{q["vs_param_index"]}, not emitted')
                used_rows.append(q)
            rows.append({
                'vertex_shader':vs,'pixel_shader':ps,
                'vs_export_semantic_count':len(vex),'ps_input_semantic_count':len(pin),
                'vs_emitted_param_indices':emitted,'ps_consumed_attr_indices':used_attrs,
                'linkage':mapping,'consumed_linkage':used_rows,
                'unmatched_nondefault_inputs':unmatched,
                'semantic_boundary':'RAW_GNM_SEMANTIC_ID_LINKAGE_ONLY',
            })
        except Exception as ex:
            violations.append(f'{spec}:{ex}')
    out={'schema':'d1_gnm_vs_ps_linkage/v1',
         'status':'D1_GNM_VS_PS_LINKAGE_EXACT' if rows and not violations else 'D1_GNM_VS_PS_LINKAGE_PARTIAL',
         'link_count':len(rows),'links':rows,'violations':violations,
         'policy':'Raw GNM semantic IDs prove VS-export to PS-input linkage. Semantic names and geometric roles remain withheld.'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'links':[{'vs':x['vertex_shader'],'ps':x['pixel_shader'],'used':x['consumed_linkage']} for x in rows],'violations':violations},indent=2))
    return 0 if out['status']=='D1_GNM_VS_PS_LINKAGE_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
