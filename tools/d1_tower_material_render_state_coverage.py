#!/usr/bin/env python3
"""Aggregate exact Tower material render-state closure across common, sky and light.

Inputs are exact d1_material_render_state_census outputs.  The light manifest is
optional but, when supplied, weights light material states by exact source light
instance frequency.

Safe source facts:
* +0x20 == 0: no material blend-state override selected by this field; opaque draw population.
* +0x20 != 0: D1 transparent draw population.
* low byte 0x88: exact blend-state index 8,
  Source + Destination*(1-SourceAlpha).

Other nonzero selectors remain unresolved.  This tool ranks them; it does not infer
their blend equations or depth/stencil/rasterizer semantics.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

EXPECTED={'common':99,'sky':74,'light':497}

def parse_pair(s):
    if '=' not in s: raise argparse.ArgumentTypeError('expected LABEL=PATH')
    k,p=s.split('=',1)
    if k not in EXPECTED: raise argparse.ArgumentTypeError(f'unknown label {k}')
    return k,Path(p)

def classify(r):
    if not r.get('transparent_draw_population'): return 'OPAQUE_NO_MATERIAL_BLEND_OVERRIDE'
    if r.get('exact_blend_state_known') and int(r.get('unk20_low_u8',-1))==0x88:
        return 'EXACT_BLEND_STATE_8_PREMULTIPLIED'
    return 'TRANSPARENT_BLEND_EQUATION_UNRESOLVED'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--state',action='append',type=parse_pair,required=True)
    ap.add_argument('--light-manifest',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    states=dict(a.state);v=[]
    if set(states)!=set(EXPECTED):v.append(f'domain set {sorted(states)} != {sorted(EXPECTED)}')

    light_freq={}
    if a.light_manifest:
        lm=json.loads(a.light_manifest.read_text())
        if lm.get('status')!='D1_WORLD_LIGHT_MATERIAL_MANIFEST_COMPLETE' or lm.get('material_decode_errors'):
            v.append('light manifest not exact')
        light_freq={str(k).upper():int(n) for k,n in (lm.get('material_instance_frequency') or {}).items()}
        if sum(light_freq.values())!=737:v.append(f'light instance frequency sum {sum(light_freq.values())} != 737')

    domains={};unknown_by_raw=collections.defaultdict(lambda:{'materials':collections.Counter(),'light_instances':0,'shaders':collections.Counter()})
    combined_class=collections.Counter()
    for label in ('common','sky','light'):
        if label not in states:continue
        d=json.loads(states[label].read_text())
        if d.get('status')!='D1_MATERIAL_RENDER_STATE_CENSUS_COMPLETE' or d.get('violations'):
            v.append(f'{label}: render state census not exact')
        if int(d.get('selected_material_count',-1))!=EXPECTED[label] or int(d.get('resolved_material_count',-1))!=EXPECTED[label]:
            v.append(f'{label}: material count drift {d.get("selected_material_count")}/{d.get("resolved_material_count")}')
        rows=d.get('materials') or []
        counts=collections.Counter();raw=collections.Counter();low=collections.Counter();state4=collections.Counter()
        lane_raw=[collections.Counter() for _ in range(4)]
        lane_selected=[collections.Counter() for _ in range(4)]
        unknown_rows=[]
        instance_counts=collections.Counter()
        for r in rows:
            cls=classify(r);counts[cls]+=1;combined_class[cls]+=1
            mh=str(r.get('material','')).upper()
            rawv=str(r.get('unk20_hex'));lowv=str(r.get('unk20_low_hex'))
            raw[rawv]+=1;low[lowv]+=1
            s4=str(r.get('state4_hex') or '')
            lanes=list(r.get('state4_lanes_u8') or [])
            if len(lanes)!=4:
                v.append(f'{label}:{mh}: state4 lanes missing/drift {lanes}')
            else:
                state4[s4]+=1
                for li,x in enumerate(lanes):
                    lane_raw[li][f'0x{int(x):02X}']+=1
                    idx=(int(x)&0x7F) if (int(x)&0x80) else None
                    lane_selected[li]['NONE' if idx is None else str(idx)]+=1
            weight=light_freq.get(mh,0) if label=='light' and light_freq else 0
            if label=='light' and light_freq:
                instance_counts[cls]+=weight
            if cls=='TRANSPARENT_BLEND_EQUATION_UNRESOLVED':
                rec={
                    'material':mh,'pixel_shader':str(r.get('pixel_shader','')).upper(),
                    'unk20_hex':rawv,'unk20_low_hex':lowv,'unk20_high_u8':int(r.get('unk20_high_u8',0)),
                    'light_instance_count':weight if label=='light' else None,
                }
                unknown_rows.append(rec)
                u=unknown_by_raw[rawv]
                u['materials'][label]+=1
                u['shaders'][(label,rec['pixel_shader'])]+=1
                if label=='light':u['light_instances']+=weight
        transparent=counts['EXACT_BLEND_STATE_8_PREMULTIPLIED']+counts['TRANSPARENT_BLEND_EQUATION_UNRESOLVED']
        domains[label]={
            'material_count':len(rows),
            'opaque_material_count':counts['OPAQUE_NO_MATERIAL_BLEND_OVERRIDE'],
            'transparent_material_count':transparent,
            'exact_state8_material_count':counts['EXACT_BLEND_STATE_8_PREMULTIPLIED'],
            'unresolved_transparent_material_count':counts['TRANSPARENT_BLEND_EQUATION_UNRESOLVED'],
            'transparent_exact_blend_fraction':(counts['EXACT_BLEND_STATE_8_PREMULTIPLIED']/transparent if transparent else 1.0),
            'all_material_blend_selector_resolution_fraction':((len(rows)-counts['TRANSPARENT_BLEND_EQUATION_UNRESOLVED'])/len(rows) if rows else None),
            'unk20_raw_counts':dict(sorted(raw.items())),
            'unk20_low_byte_counts':dict(sorted(low.items())),
            'state4_hex_counts':dict(sorted(state4.items())),
            'state4_lane_raw_counts':{str(i):dict(sorted(x.items())) for i,x in enumerate(lane_raw)},
            'state4_lane_selected_low7_counts':{str(i):dict(sorted(x.items())) for i,x in enumerate(lane_selected)},
            'unresolved_rows':sorted(unknown_rows,key=lambda x:(-(x.get('light_instance_count') or 0),x['unk20_hex'],x['material'])),
            'light_instance_class_counts':dict(instance_counts) if label=='light' and light_freq else None,
            'light_instance_blend_selector_resolution_fraction':(
                (737-instance_counts['TRANSPARENT_BLEND_EQUATION_UNRESOLVED'])/737
                if label=='light' and light_freq else None
            ),
        }

    unresolved=[]
    for rawv,u in unknown_by_raw.items():
        mats=dict(u['materials'])
        unresolved.append({
            'unk20_hex':rawv,
            'low_byte_hex':f"0x{int(rawv,16)&0xFF:02X}" if rawv.startswith('0x') else None,
            'material_counts_by_domain':mats,
            'total_material_count':sum(mats.values()),
            'light_instance_count':u['light_instances'],
            'shader_rows':[{'domain':d,'pixel_shader':sh,'material_count':n} for (d,sh),n in sorted(u['shaders'].items())],
        })
    unresolved.sort(key=lambda x:(-x['light_instance_count'],-x['total_material_count'],x['unk20_hex']))

    total=sum(EXPECTED.values())
    unresolved_total=combined_class['TRANSPARENT_BLEND_EQUATION_UNRESOLVED']
    out={
        'schema':'d1_tower_material_render_state_coverage/v1',
        'status':'D1_TOWER_MATERIAL_RENDER_STATE_COVERAGE_EXACT' if len(domains)==3 and not v else 'D1_TOWER_MATERIAL_RENDER_STATE_COVERAGE_PARTIAL',
        'domain_material_counts':EXPECTED,
        'domain_scoped_material_row_count':total,
        'domains':domains,
        'combined_material_class_counts':dict(combined_class),
        'combined_material_blend_selector_resolution_fraction':(total-unresolved_total)/total,
        'highest_priority_unresolved_render_states':unresolved,
        'violations':v,
        'semantic_boundary':{
            'transparent_population_from_unk20_nonzero':'SOURCE_CLOSED',
            'opaque_population_from_unk20_zero':'SOURCE_CLOSED',
            'low_byte_0x88_selector':'EXACT_BLEND_STATE_8',
            'blend_state_8_equation':'Source + Destination*(1-SourceAlpha)',
            'other_nonzero_blend_equations':'WITHHELD',
            'depth_stencil_state':'WITHHELD_BY_THIS_CENSUS',
            'state4_lane_1_3_names':'WITHHELD_BY_THIS_CENSUS',
            'state4_highbit_low7_selector_decomposition':'EXACT_MECHANICAL_SYNTAX_ONLY',
            'rasterizer_state':'WITHHELD_BY_THIS_CENSUS',
            'pass_order_and_framebuffer_ownership':'WITHHELD',
        },
        'policy':'Resolution fraction means only that material +0x20 is either zero/no blend override or the exact 0x88 blend selector. It is not a full pipeline-state or pass-order completeness metric.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],
        'domains':{k:{q:v0[q] for q in ('material_count','opaque_material_count','transparent_material_count','exact_state8_material_count','unresolved_transparent_material_count','all_material_blend_selector_resolution_fraction','light_instance_blend_selector_resolution_fraction')} for k,v0 in domains.items()},
        'combined_resolution':out['combined_material_blend_selector_resolution_fraction'],
        'top_unresolved':unresolved[:20],
        'violations':v,
    },indent=2))
    return 0 if out['status']=='D1_TOWER_MATERIAL_RENDER_STATE_COVERAGE_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
