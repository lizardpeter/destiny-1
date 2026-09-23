#!/usr/bin/env python3
"""Source-correlate the four D1 material +0x20 state lanes with Tiger PipelineState.

This proof consumes exact D1 state4 census coverage plus pinned independent Tiger
source.  It validates:
  lane0 -> blend_state
  lane1 -> depth_stencil_state
  lane2 -> rasterizer_state
  lane3 -> depth_bias_state
and the high-bit-active / low-seven-index selector syntax in source.

The result is SOURCE_CORRELATED_ONLY for lanes 1..3.  Existing independent D1
behavioral promotion of lane0/0x88 remains separate.  No table descriptor or D1
behavior is inferred from a selected index here.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path

ALKAHest_COMMIT='c632a562e88b5b805098152658b915d1c59f0f9a'
ALKAHest_BLOB='008cacbd3db09b66f903943e1fd1b7a6ce9140a9'
LANES=['blend_state','depth_stencil_state','rasterizer_state','depth_bias_state']

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--coverage',type=Path,required=True)
    ap.add_argument('--technique-source',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    d=json.loads(a.coverage.read_text());src=a.technique_source.read_text();v=[]
    if d.get('status')!='D1_TOWER_MATERIAL_RENDER_STATE_COVERAGE_EXACT' or d.get('violations'):
        v.append('render-state coverage not exact')

    required=[
        'pub struct PipelineState {',
        'blend_state: u8',
        'depth_stencil_state: u8',
        'rasterizer_state: u8',
        'depth_bias_state: u8',
        'blend_state: (raw & 0xff) as u8',
        'depth_stencil_state: ((raw >> 8) & 0xff) as u8',
        'rasterizer_state: ((raw >> 16) & 0xff) as u8',
        'depth_bias_state: ((raw >> 24) & 0xff) as u8',
    ]
    for s in required:
        if s not in src:v.append(f'source anchor missing: {s}')
    for name in LANES:
        pat=rf'pub fn {name}\(&self\) -> Option<usize> \{{.*?self\.{name} & 0x80 != 0.*?Some\(\(self\.{name} & 0x7f\) as usize\)'
        if not re.search(pat,src,re.S):v.append(f'{name}: selector accessor drift')

    domains={}
    for label,row in (d.get('domains') or {}).items():
        raw=row.get('state4_lane_raw_counts') or {}
        sel=row.get('state4_lane_selected_low7_counts') or {}
        if set(raw)!={'0','1','2','3'} or set(sel)!={'0','1','2','3'}:
            v.append(f'{label}: lane histograms incomplete')
            continue
        lanes=[]
        for i,name in enumerate(LANES):
            lanes.append({
                'lane_index':i,
                'source_field_name':name,
                'source_field_name_status':'SOURCE_CORRELATED_ONLY' if i else 'SOURCE_CORRELATED_PLUS_EXISTING_D1_BLEND_FIXTURE',
                'raw_u8_counts':raw[str(i)],
                'selected_low7_index_counts':sel[str(i)],
                'd1_behavioral_semantics':(
                    '0x88_INDEX8_BLEND_EQUATION_INDEPENDENTLY_PROMOTED'
                    if i==0 else 'WITHHELD_PENDING_INDEPENDENT_D1_BEHAVIORAL_FIXTURE'
                ),
            })
        domains[label]={'material_count':row['material_count'],'lanes':lanes}

    out={
        'schema':'d1_tower_material_state4_source_correlation/v1',
        'status':'D1_TOWER_MATERIAL_STATE4_SOURCE_CORRELATION_EXACT' if domains and not v else 'D1_TOWER_MATERIAL_STATE4_SOURCE_CORRELATION_PARTIAL',
        'source':{
            'repository':'cohaereo/alkahest',
            'commit':ALKAHest_COMMIT,
            'blob_sha1':ALKAHest_BLOB,
            'path':'crates/data/tfx/technique.rs',
            'pipeline_state_size_bytes':4,
            'lane_order':LANES,
            'selector_syntax':'high_bit_active_low7_index',
            'sha256':hashlib.sha256(a.technique_source.read_bytes()).hexdigest(),
        },
        'domains':domains,
        'violations':v,
        'semantic_boundary':{
            'four_byte_d1_windows':'EXACT_RETAIL_BYTES',
            'lane_order_and_selector_syntax':'PINNED_INDEPENDENT_TIGER_SOURCE',
            'lane0_0x88_blend_behavior':'INDEPENDENT_D1_CROSS_FIXTURE_PROMOTED',
            'lane1_depth_stencil_d1_behavior':'WITHHELD',
            'lane2_rasterizer_d1_behavior':'WITHHELD',
            'lane3_depth_bias_d1_behavior':'WITHHELD',
        },
        'policy':'Names for lanes 1..3 are source correlations, not global D1 behavioral promotions. Selected indices may prioritize future fixtures but receive no D1 effect semantics from this report alone.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],
        'domains':{k:[(x['source_field_name'],x['selected_low7_index_counts']) for x in q['lanes']] for k,q in domains.items()},
        'violations':v,
    },indent=2))
    return 0 if out['status']=='D1_TOWER_MATERIAL_STATE4_SOURCE_CORRELATION_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
