#!/usr/bin/env python3
"""Classify exact D1 Tower sky terminal MRT0 output modes.

A channel is ZERO_ONLY only when the exact terminal value slice contains literal
0 and no texture/cbuffer/interpolant/unknown-register leaves.  Families are then
classified as RGB_ONLY, ALPHA_ONLY, RGBA, ZERO, or OTHER_<lanes>.

This is numerical output-shape classification only.  RGB_ONLY does not mean
"color pass" and ALPHA_ONLY does not mean "attenuation/mask" without separate
evidence.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

def zero_only(q):
    return q.get('literals')==['0'] and not q.get('texture_sample_channels') and not q.get('cbuffer_dwords') and not q.get('interpolants') and not q.get('unknown_registers')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--shader-report',type=Path,required=True)
    ap.add_argument('--terminal-mrt0',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    sr=json.loads(a.shader_report.read_text());tm=json.loads(a.terminal_mrt0.read_text());v=[]
    if sr.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or sr.get('error_count'):v.append('shader report not exact')
    if tm.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT':v.append('terminal MRT0 report not exact')
    freq={x['shader']:int(x.get('visible_material_count',0)) for x in sr.get('shaders',[]) if not x.get('error')}
    rows=[];fam=collections.Counter();mat=collections.Counter()
    for r in tm.get('shaders',[]):
        sh=r['shader'];nonzero=[];zero=[]
        for ch in ('R','G','B','A'):
            q=((r.get('channels') or {}).get(ch) or {}).get('value_slice') or {}
            if zero_only(q):zero.append(ch)
            else:nonzero.append(ch)
        if nonzero==['A']:mode='ALPHA_ONLY'
        elif nonzero==['R','G','B']:mode='RGB_ONLY'
        elif nonzero==['R','G','B','A']:mode='RGBA'
        elif not nonzero:mode='ZERO'
        else:mode='OTHER_'+''.join(nonzero)
        w=freq.get(sh)
        if w is None:v.append(f'{sh}: visible material frequency missing');w=0
        fam[mode]+=1;mat[mode]+=w
        rows.append({
            'shader':sh,'visible_material_count':w,'mode':mode,
            'zero_only_channels':zero,'nonzero_channels':nonzero,
            'terminal_export_address':r.get('terminal_mrt0_export_address'),
            'compressed':bool(r.get('terminal_mrt0_compressed')),
        })
    if len(rows)!=43:v.append(f'row count {len(rows)} != 43')
    if sum(x['visible_material_count'] for x in rows)!=74:v.append('visible material weight sum != 74')
    modes={k:{'shader_family_count':fam[k],'visible_material_count':mat[k],
              'visible_material_fraction':mat[k]/74} for k in sorted(fam)}
    out={
        'schema':'d1_tower_sky_terminal_output_modes/v1',
        'status':'D1_TOWER_SKY_TERMINAL_OUTPUT_MODES_EXACT' if len(rows)==43 and not v else 'D1_TOWER_SKY_TERMINAL_OUTPUT_MODES_PARTIAL',
        'shader_family_count':len(rows),'visible_material_count':sum(x['visible_material_count'] for x in rows),
        'modes':modes,
        'rows':sorted(rows,key=lambda x:(x['mode'],-x['visible_material_count'],x['shader'])),
        'violations':v,
        'semantic_boundary':{
            'zero_channel_identity':'EXACT_TERMINAL_DATAFLOW',
            'output_mode':'EXACT_NUMERICAL_LANE_SHAPE',
            'pass_or_material_role':'WITHHELD',
        },
        'policy':'Output modes classify only which MRT0 lanes are provably zero versus data-dependent. They do not name a render pass or sky semantic.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'modes':modes,'violations':v},indent=2))
    return 0 if out['status']=='D1_TOWER_SKY_TERMINAL_OUTPUT_MODES_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
