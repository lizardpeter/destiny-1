#!/usr/bin/env python3
"""Inventory non-material Xbox D1 DXBC constant-buffer usage.

Consumes an existing ``d1_dxbc_probe.py`` regression/report. Material-owned b0 is
excluded; the purpose is to enumerate global shader cbuffers such as b12/b13 by
register, declared vec4 count, pixel shader and material.

This does not assign engine names to the buffers. It produces a bounded search
index for cross-platform producer tracing.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path


def rows_from_doc(d: dict) -> list[dict]:
    # Historical d1_dxbc_probe regression fixtures use ``compared``; newer
    # reports may use one of the generic names below. Preserve all accepted
    # shapes explicitly so the inventory does not depend on one report vintage.
    for key in ('compared','comparisons','materials','rows','bindings'):
        v=d.get(key)
        if isinstance(v,list): return v
        if isinstance(v,dict):
            out=[]
            for h,r in v.items():
                if isinstance(r,dict): out.append({'material':h,**r})
            return out
    raise ValueError('could not locate DXBC comparison rows')


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    d=json.loads(a.input.read_text())
    rows=rows_from_doc(d)

    by_reg=defaultdict(list); shape=Counter(); shader_regs=defaultdict(set)
    for r in rows:
        mh=str(r.get('material') or '').upper()
        ps=str(r.get('pixel_shader') or '').upper()
        for cb in r.get('non_b0_cbuffers') or []:
            reg=int(cb['register']); count=int(cb['vec4_count'])
            rec={'material':mh,'pixel_shader':ps,'register':reg,'vec4_count':count}
            by_reg[reg].append(rec);shape[(reg,count)]+=1;shader_regs[ps].add((reg,count))

    registers={}
    for reg, rr in sorted(by_reg.items()):
        registers[str(reg)]={
            'row_count':len(rr),
            'unique_pixel_shaders':sorted({x['pixel_shader'] for x in rr}),
            'unique_materials':sorted({x['material'] for x in rr}),
            'vec4_count_frequency':dict(sorted(Counter(x['vec4_count'] for x in rr).items())),
            'rows':rr,
        }
    shaders=[]
    for ps,ss in sorted(shader_regs.items()):
        shaders.append({'pixel_shader':ps,'global_cbuffers':[{'register':r,'vec4_count':n} for r,n in sorted(ss)]})
    out={
      'schema_version':2,
      'status':'D1_XBOX_DXBC_GLOBAL_CBUFFER_INVENTORY',
      'source':str(a.input),
      'input_row_count':len(rows),
      'global_cbuffer_row_count':sum(len(x) for x in by_reg.values()),
      'register_frequency':{str(k):len(v) for k,v in sorted(by_reg.items())},
      'register_vec4_shape_frequency':{f'b{r}:{n}':c for (r,n),c in sorted(shape.items())},
      'registers':registers,
      'pixel_shaders_with_global_cbuffers':shaders,
      'b13':registers.get('13'),
      'policy':'DXBC declarations only. b12/b13 are classified as non-material/global relative to proven material b0; no engine producer/name is inferred.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','input_row_count','global_cbuffer_row_count','register_frequency','register_vec4_shape_frequency')},indent=2))
    print('B13',json.dumps(out['b13'],indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
