#!/usr/bin/env python3
"""Fail-closed native blend contract for Vex circuitry material 816CE240.

This is deliberately narrower than the generic ROI blend-state promotion. It
requires all four independently closed inputs used by that promotion and emits a
target-specific contract suitable for exporters/runtime adapters.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

MAT='816CE240'; SH='816CE0A8'; GCN='8e0e11cd37896f14873d86215ddec89dd5be34d457e33f6b734b7c3fd0e126fd'
CARDS={'80B9E8C2':'80B9E8CF','80B9E8C3':'80B9E8D0'}
OPAQUE='809C475F'
REQ_DESC=['blend_enable: BOOL(1)','src_blend: One','dest_blend: InvSrcAlpha','blend_op: Add',
          'src_blend_alpha: One','dest_blend_alpha: InvSrcAlpha','blend_op_alpha: Add','render_target_write_mask: 15']

def load(p):return json.loads(Path(p).read_text())

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--state4',type=Path,required=True);ap.add_argument('--correlation',type=Path,required=True);ap.add_argument('--card-gcn',type=Path,required=True);ap.add_argument('--circuit-gcn',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 state,corr,card,circ=map(load,(a.state4,a.correlation,a.card_gcn,a.circuit_gcn));v=[]
 if state.get('status')!='D1_REMOTE_PS4_ROI_MATERIAL_STATE4_COMPLETE' or state.get('violations'):v.append('state4_not_exact')
 rows={str(r.get('material')).upper():r for r in state.get('rows',[])}
 if set(rows)!={OPAQUE,MAT,*CARDS}:v.append(f'state_material_set_drift:{sorted(rows)}')
 if rows.get(MAT,{}).get('lanes_u8')!=[0x88,0,0,0]:v.append(f'{MAT}:state_bytes_drift')
 if rows.get(OPAQUE,{}).get('lanes_u8')!=[0,0,0,0]:v.append(f'{OPAQUE}:opaque_control_drift')
 for h in CARDS:
  if rows.get(h,{}).get('lanes_u8')!=[0x88,0,0x81,0]:v.append(f'{h}:card_state_drift')
 if corr.get('status')!='D1_PS4_ROI_STATE4_CROSS_SOURCE_CORRELATION_COMPLETE':v.append('correlation_not_exact')
 if corr.get('source_pipeline_state_lane_order')!=['blend_state','depth_stencil_state','rasterizer_state','depth_bias_state']:v.append('lane_order_drift')
 selected=corr.get('lane0_selected_indices') or {}
 for h in [MAT,*CARDS]:
  if selected.get(h)!=8:v.append(f'{h}:blend_index:{selected.get(h)}')
 if selected.get(OPAQUE) is not None:v.append('opaque_control_unexpected_override')
 desc=(corr.get('source_blend_descriptors') or {}).get('8','')
 for x in REQ_DESC:
  if x not in desc:v.append(f'blend8_descriptor_missing:{x}')
 if card.get('status')!='D1_80CA0B97_CARD_GCN_OUTPUT_DEPENDENCY_PROVEN' or card.get('violations'):v.append('card_gcn_not_exact')
 cr={str(x.get('shader')).upper():x for x in card.get('shaders',[])}
 if set(cr)!=set(CARDS.values()):v.append(f'card_shader_set_drift:{sorted(cr)}')
 if cr.get('80B9E8CF',{}).get('output_structure',{}).get('rgb_structure')!='PREMULTIPLIED_BY_FINAL_ALPHA_SCALAR':v.append('premultiplied_card_fixture_drift')
 if cr.get('80B9E8D0',{}).get('output_structure',{}).get('rgb_structure')!='EXPLICIT_ZERO':v.append('attenuation_card_fixture_drift')
 for q in ('80B9E8CF','80B9E8D0'):
  if cr.get(q,{}).get('output_structure',{}).get('mrt0_a')!='FINAL_ALPHA_SCALAR':v.append(q+':alpha_contract_drift')
 if circ.get('status')!='D1_816CE0A8_GCN_OUTPUT_ALPHA_ZERO_REPRODUCED':v.append('circuit_gcn_not_exact')
 if circ.get('shader')!=SH:v.append(f'circuit_shader:{circ.get("shader")}')
 if circ.get('gcn_sha256')!=GCN:v.append(f'circuit_gcn_sha:{circ.get("gcn_sha256")}')
 if circ.get('output_alpha')!='EXACT_ZERO_SOURCE_REPRODUCED':v.append('circuit_alpha_not_zero')
 exact=not v
 out={
  'schema':'d1_vex_816ce240_native_blend_contract/v1',
  'status':'D1_VEX_816CE240_NATIVE_ADDITIVE_RGB_EXACT' if exact else 'D1_VEX_816CE240_NATIVE_BLEND_PARTIAL',
  'material':MAT,'pixel_shader':SH,'gcn_sha256':GCN,
  'serialized_state_bytes':rows.get(MAT,{}).get('lanes_u8'),
  'promoted_state_lane':{'material_offset':'0x20','lane':0,'raw':'0x88','encoding':'high_bit_active_low7_index','blend_state_index':8} if exact else None,
  'blend_state_8':{'descriptor':desc,'rgb_equation':'S.rgb + D.rgb * (1 - S.a)','alpha_equation':'S.a + D.a * (1 - S.a)'} if exact else None,
  'shader_output':{'source_alpha':'0','source_rgb':'circuitry HDR/palette RGB from exact shader dataflow'} if exact else None,
  'native_composition':{
    'rgb':'S.rgb + D.rgb',
    'alpha':'D.a',
    'classification':'EXACT_ADDITIVE_RGB_CONSEQUENCE_OF_STATE8_WITH_ZERO_SOURCE_ALPHA',
  } if exact else None,
  'portable_boundary':{
    'core_gltf_equivalent':False,
    'emissive_proxy_allowed':True,
    'emissive_proxy_is_native_equivalent':False,
  },
  'unpromoted':[
    'material +0x21/+0x22/+0x23 semantics for 816CE240',
    'engine-facing name of blend state 8',
    'API12/API13 producer names or live values',
  ],
  'evidence':{
    'state_payload_source':rows.get(MAT,{}).get('payload_source'),
    'state_entry_index':(rows.get(MAT,{}).get('meta') or {}).get('index'),
    'alkahest_commit':corr.get('alkahest_commit'),
    'alkahest_technique_sha256':corr.get('alkahest_technique_sha256'),
    'alkahest_blend_states_sha256':corr.get('alkahest_blend_states_sha256'),
    'card_fixture_count':card.get('shader_count'),
  },
  'violations':v,
  'policy':'The additive result is promoted only for material 816CE240 / PS 816CE0A8 from exact D1 state bytes, pinned Tiger PipelineState source, independent card shader cross-fixtures, and exact retail circuitry GCN alpha=0. Other state bytes and engine names remain withheld.'
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 0 if exact else 2
if __name__=='__main__':raise SystemExit(main())
