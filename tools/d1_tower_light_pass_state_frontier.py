#!/usr/bin/env python3
"""Source-correlate Tower light material state with renderer-owned light-pass state.

Exact D1 input:
- all 497 source-proven Tower light materials have state4 == 00000000.

Pinned independent Tiger lineage:
- LightRenderer selects depth/stencil state 0 when camera is inside the light volume;
- LightRenderer selects depth/stencil state 30 when camera is outside;
- Technique::bind merges current state with technique state;
- PipelineState::select retains the current lane when the incoming lane is unset.

This is not a D1 runtime pass-state promotion.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path

def depth_block(text:str, idx:int)->dict:
    start=text.find(f'{idx} DepthStencilDesc {{')
    if start<0:
        raise ValueError(f'depth state {idx} missing')
    nxt=re.search(rf'(?m)^{idx+1} DepthStencilDesc \{{', text[start+1:])
    end=(start+1+nxt.start()) if nxt else len(text)
    block=text[start:end]
    def one(name):
        q=re.search(rf'(?m)^    {re.escape(name)}: ([^,]+),',block)
        return q.group(1) if q else None
    return {
        'index':idx,
        'depth_enable':one('depth_enable'),
        'depth_write_mask':one('depth_write_mask'),
        'depth_func':one('depth_func'),
        'stencil_enable':one('stencil_enable'),
        'stencil_read_mask':one('stencil_read_mask'),
        'stencil_write_mask':one('stencil_write_mask'),
        'source_block':block.rstrip(),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--light-state',type=Path,required=True)
    ap.add_argument('--light-renderer-source',type=Path,required=True)
    ap.add_argument('--technique-bind-source',type=Path,required=True)
    ap.add_argument('--pipeline-state-source',type=Path,required=True)
    ap.add_argument('--depth-states-source',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    d=json.loads(a.light_state.read_text());v=[]
    if d.get('status')!='D1_MATERIAL_RENDER_STATE_CENSUS_COMPLETE' or d.get('violations'):
        v.append('light render-state census not exact')
    rows=d.get('materials') or []
    if len(rows)!=497:
        v.append(f'light material row count {len(rows)} != 497')
    bad=[x.get('material') for x in rows if x.get('state4_hex')!='00000000']
    if bad:
        v.append(f'nonzero D1 light material state4 rows {bad[:20]}')
    if d.get('opaque_material_count')!=497 or d.get('transparent_material_count')!=0:
        v.append('light material opaque/transparent population drift')

    lr=a.light_renderer_source.read_text()
    tb=a.technique_bind_source.read_text()
    ps=a.pipeline_state_source.read_text()
    ds=a.depth_states_source.read_text()

    if 'let is_camera_in_volume' not in lr:
        v.append('light renderer camera-volume anchor missing')
    if 'PipelineState::new(None, Some(0), None, None)' not in lr:
        v.append('inside depth-state anchor missing')
    if 'PipelineState::new(None, Some(30), None, None)' not in lr:
        v.append('outside depth-state anchor missing')
    if '.select(&self.tech.states)' not in tb or '.select(&cmd.state_override)' not in tb:
        v.append('technique state merge anchor missing')
    if 'Creates a new selection, filling unset states in' not in ps:
        v.append('PipelineState select contract comment missing')
    if 'let new_states = ((other >> 7 & 0x1010101) * 0xff) & (current ^ other) ^ current;' not in ps:
        v.append('PipelineState high-bit merge implementation missing')

    try:
        s0=depth_block(ds,0);s30=depth_block(ds,30)
    except Exception as ex:
        v.append(str(ex));s0={};s30={}

    expected0={
        'depth_enable':'BOOL(0)','depth_write_mask':'Zero','depth_func':'Always',
        'stencil_enable':'BOOL(0)','stencil_read_mask':'0','stencil_write_mask':'0',
    }
    expected30={
        'depth_enable':'BOOL(1)','depth_write_mask':'Zero','depth_func':'GreaterEqual',
        'stencil_enable':'BOOL(1)','stencil_read_mask':'16','stencil_write_mask':'16',
    }
    for k,val in expected0.items():
        if s0.get(k)!=val:
            v.append(f'depth state0 {k} {s0.get(k)!r} != {val!r}')
    for k,val in expected30.items():
        if s30.get(k)!=val:
            v.append(f'depth state30 {k} {s30.get(k)!r} != {val!r}')

    out={
        'schema':'d1_tower_light_pass_state_frontier/v1',
        'status':'D1_TOWER_LIGHT_PASS_STATE_SOURCE_CORRELATION_EXACT' if not v else 'D1_TOWER_LIGHT_PASS_STATE_SOURCE_CORRELATION_PARTIAL',
        'd1_material_state':{
            'material_count':len(rows),
            'state4_unique_values':sorted({x.get('state4_hex') for x in rows}),
            'all_four_selector_lanes_unset':not bad,
            'status':'EXACT_RETAIL_MATERIAL_BYTES',
        },
        'source_lineage':{
            'repository':'cohaereo/alkahest',
            'commit':'c632a562e88b5b805098152658b915d1c59f0f9a',
            'light_renderer':{
                'path':'crates/render/src/feature/light.rs',
                'sha256':hashlib.sha256(a.light_renderer_source.read_bytes()).hexdigest(),
                'camera_inside_depth_stencil_index':0,
                'camera_outside_depth_stencil_index':30,
            },
            'technique_bind':{
                'path':'crates/render/src/tfx/technique.rs',
                'sha256':hashlib.sha256(a.technique_bind_source.read_bytes()).hexdigest(),
                'merge_order':'current command state -> technique state -> state override',
            },
            'pipeline_state':{
                'path':'crates/data/tfx/technique.rs',
                'sha256':hashlib.sha256(a.pipeline_state_source.read_bytes()).hexdigest(),
                'unset_lane_behavior':'retain current lane',
            },
            'depth_state_0':s0,
            'depth_state_30':s30,
        },
        'frontier':{
            'source_correlated_model':'renderer-owned depth/stencil selection can survive an all-zero technique/material selection through high-bit merge semantics',
            'd1_runtime_selected_depth_stencil_state':'WITHHELD',
            'd1_camera_inside_outside_branch_identity':'WITHHELD',
            'd1_render_target_ownership':'WITHHELD',
            'd1_blend_state_for_light_pass':'WITHHELD',
            'required_primary_evidence':'D1 runtime draw/command state capture binding a source-owned Tower light draw to render targets plus blend/depth/raster/depth-bias state',
        },
        'violations':v,
        'policy':'All-zero D1 material state is exact. State 0/30 selection and merge behavior are pinned independent source-lineage facts only; D1 runtime pass state remains withheld.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],
        'd1_material_state':out['d1_material_state'],
        'source_inside':s0,
        'source_outside':s30,
        'frontier':out['frontier'],
        'violations':v,
    },indent=2))
    return 0 if out['status']=='D1_TOWER_LIGHT_PASS_STATE_SOURCE_CORRELATION_EXACT' else 2

if __name__=='__main__':
    raise SystemExit(main())
