#!/usr/bin/env python3
"""Source-correlate D1 ROI Material +0x20 lane2 with Tiger rasterizer state.

This tool is intentionally one proof level below a global semantic promotion. It
requires an exact D1 material-stage dump plus pinned independent Tiger PipelineState
source and the corresponding built-in rasterizer-state table. It decodes the
selected descriptor numerically and records the source interpretation without
claiming that every D1 ROI lane2 byte has been behaviorally proven yet.
"""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path

REC=struct.Struct('<IIiiffiiiiI')  # D3D11_RASTERIZER_DESC (40) + source padding u32
FILL={2:'WIREFRAME',3:'SOLID'}
CULL={1:'NONE',2:'FRONT',3:'BACK'}

def descriptor(raw:bytes,i:int)->dict:
    vals=REC.unpack_from(raw,i*REC.size)
    fill,cull,front,db,dbc,slope,depthclip,scissor,msaa,aaline,pad=vals
    return {
      'index':i,'fill_mode_raw':fill,'fill_mode':FILL.get(fill,f'UNKNOWN_{fill}'),
      'cull_mode_raw':cull,'cull_mode':CULL.get(cull,f'UNKNOWN_{cull}'),
      'front_counter_clockwise':bool(front),'depth_bias':db,
      'depth_bias_clamp':dbc,'slope_scaled_depth_bias':slope,
      'depth_clip_enable':bool(depthclip),'scissor_enable':bool(scissor),
      'multisample_enable_table_value':bool(msaa),'antialiased_line_enable':bool(aaline),
      'source_padding_u32':pad,
    }

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--material-stage',type=Path,required=True)
    ap.add_argument('--technique-source',type=Path,required=True);ap.add_argument('--global-state-source',type=Path,required=True)
    ap.add_argument('--rasterizer-table',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
    violations=[];out=None
    try:
        d=json.loads(a.material_stage.read_text());assert d['status']=='D1_CORPUS_MATERIAL_STAGE_EXACT' and len(d['materials'])==1
        row=d['materials'][0];assert not row['violations'];state=row['stage']['material_state4_hex'];b=bytes.fromhex(state);assert len(b)==4
        tech=a.technique_source.read_text();glob=a.global_state_source.read_text();raw=a.rasterizer_table.read_bytes()
        needed=['blend_state: u8','depth_stencil_state: u8','rasterizer_state: u8','depth_bias_state: u8','if self.rasterizer_state & 0x80 != 0','Some((self.rasterizer_state & 0x7f) as usize)']
        for x in needed:assert x in tech,x
        assert 'pub struct PaddedRasterizerState' in glob and 'pub desc: d3d11::RasterizerDesc' in glob
        assert 'assert_eq!(rasterizer_states.len(), 9)' in glob
        assert 'desc.multisample_enable = false.into()' in glob
        assert len(raw)==9*REC.size,(len(raw),REC.size)
        lane=int(b[2]);idx=(lane&0x7f) if lane&0x80 else None
        assert idx is not None and idx<9,(lane,idx)
        descs=[descriptor(raw,i) for i in range(9)];sel=descs[idx]
        effective=dict(sel);effective['multisample_enable_effective_in_pinned_source']=False
        out={
          'schema_version':1,'status':'D1_ROI_RASTERIZER_STATE_SOURCE_CORRELATED',
          'material':row['material'],'material_state4_hex':state,'material_state_lanes_u8':list(b),
          'pipeline_state_lane_order':['blend_state','depth_stencil_state','rasterizer_state','depth_bias_state'],
          'rasterizer_lane_raw':f'0x{lane:02X}','selector_encoding':'high_bit_active_low7_index','selected_rasterizer_index':idx,
          'selected_table_descriptor':sel,'pinned_source_effective_descriptor':effective,'all_table_descriptors':descs,
          'evidence':{
            'technique_source_sha256':hashlib.sha256(a.technique_source.read_bytes()).hexdigest(),
            'global_state_source_sha256':hashlib.sha256(a.global_state_source.read_bytes()).hexdigest(),
            'rasterizer_table_sha256':hashlib.sha256(raw).hexdigest(),'rasterizer_table_bytes':len(raw),'record_bytes':REC.size},
          'promotion':'SOURCE_CORRELATED_ONLY',
          'remaining_gate':'Independent D1 rasterization/culling fixture must agree before lane2/rasterizer semantics are promoted globally.',
          'policy':'The D1 bytes are exact and the selected source descriptor is exact. The semantic identity of D1 Material +0x20 lane2 with this independent Tiger PipelineState field remains source-correlated until a D1 behavioral fixture closes it.'}
    except Exception as ex:violations.append(repr(ex))
    rep=out or {'schema_version':1,'status':'D1_ROI_RASTERIZER_STATE_SOURCE_CORRELATION_FAILED'};rep['violations']=violations
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2));return 0 if not violations else 2
if __name__=='__main__':raise SystemExit(main())
