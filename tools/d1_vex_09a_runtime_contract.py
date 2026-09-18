#!/usr/bin/env python3
"""Emit a machine-readable native-runtime contract for D1 Vex 816CE09A.

The contract is intentionally partial-exact: it promotes only pipeline/binding
facts already closed by the exact 816CE240 blend proof and 816CE0A8 global-CB
proof. Missing API12/API13 producer identities/live bytes remain hard runtime
requirements, not invented defaults.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

OWNER='816CE12B';MODEL='816CE09A';MAT='816CE240';PS='816CE0A8';NATIVE='816CE0AE'
GCN='8e0e11cd37896f14873d86215ddec89dd5be34d457e33f6b734b7c3fd0e126fd'

def load(p:Path)->dict:return json.loads(p.read_text())

def main()->int:
 ap=argparse.ArgumentParser()
 ap.add_argument('--blend-proof',type=Path,required=True)
 ap.add_argument('--global-cb-proof',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 b=load(a.blend_proof);g=load(a.global_cb_proof);v=[]
 if b.get('status')!='D1_VEX_816CE240_NATIVE_ADDITIVE_RGB_EXACT' or b.get('violations'):v.append('blend_proof_not_exact')
 if b.get('material')!=MAT or b.get('pixel_shader')!=PS or b.get('gcn_sha256')!=GCN:v.append('blend_target_identity_drift')
 if g.get('status')!='D1_VEX_816CE0A8_GLOBAL_CB_DATAFLOW_EXACT' or g.get('violations'):v.append('global_cb_proof_not_exact')
 if g.get('shader')!=PS or g.get('native_shader')!=NATIVE or g.get('gcn_sha256')!=GCN:v.append('global_cb_target_identity_drift')
 comp=b.get('native_composition') or {}
 if comp.get('rgb')!='S.rgb + D.rgb' or comp.get('alpha')!='D.a':v.append('native_composition_drift')
 lane=b.get('promoted_state_lane') or {}
 if lane.get('raw')!='0x88' or lane.get('blend_state_index')!=8:v.append('blend_selector_drift')
 cb=(g.get('extended_user_data') or {}).get('constant_buffers')
 expected=[
  {'api_slot':0,'start_register':28,'extended_user_data_dword_offset':12},
  {'api_slot':12,'start_register':32,'extended_user_data_dword_offset':16},
  {'api_slot':13,'start_register':36,'extended_user_data_dword_offset':20},
 ]
 if cb!=expected:v.append(f'constant_buffer_binding_drift:{cb!r}')
 eq=g.get('proven_equations') or {}
 if eq.get('global_rgb_factor')!='api13[6] * api13[7]':v.append('api13_factor_drift')
 if eq.get('view_origin_delta')!='float3(api12[28]-attr4.x, api12[29]-attr4.y, api12[30]-attr4.z)':v.append('api12_view_delta_drift')
 gates=g.get('gates') or {}
 for k in ('api12_engine_producer_closed','api13_engine_producer_closed','api12_live_values_closed','api13_live_values_closed'):
  if gates.get(k) is not False:v.append('unexpected_semantic_promotion:'+k)
 exact=not v
 out={
  'schema':'d1_vex_09a_native_runtime_contract/v1',
  'status':'D1_VEX_09A_RUNTIME_CONTRACT_PARTIAL_EXACT' if exact else 'D1_VEX_09A_RUNTIME_CONTRACT_INVALID',
  'target':{'owner':OWNER,'model':MODEL,'material':MAT,'pixel_shader':PS,'native_shader':NATIVE,'gcn_sha256':GCN},
  'circuitry_pass':{
   'serialized_blend_selector':'0x88',
   'blend_state_index':8,
   'source_alpha':0,
   'native_composition':{'rgb':'S.rgb + D.rgb','alpha':'D.a'},
   'vulkan_color_blend_attachment':{
    'blendEnable':True,
    'srcColorBlendFactor':'VK_BLEND_FACTOR_ONE',
    'dstColorBlendFactor':'VK_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA',
    'colorBlendOp':'VK_BLEND_OP_ADD',
    'srcAlphaBlendFactor':'VK_BLEND_FACTOR_ONE',
    'dstAlphaBlendFactor':'VK_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA',
    'alphaBlendOp':'VK_BLEND_OP_ADD',
    'colorWriteMask':['R','G','B','A'],
    'derivation':'mechanical cross-API representation of proven state-8 factors/ops; not a Bungie-authored Vulkan state',
   },
   'zero_source_alpha_reduction':{
    'rgb':'Source.rgb + Destination.rgb',
    'alpha':'Destination.a',
   },
  } if exact else None,
  'ps_user_data':{
   'extended_user_data_pointer':'s[2:3]',
   'inline_user_sgpr_dword_count':16,
   'constant_buffer_descriptors':cb,
   'api0':{'proven_read':'dword 8','role':'(t0_scalar - 0.5) scale in UV displacement path'},
   'api12':{'proven_reads':[28,29,30],'role':'attr4-relative xyz vector before normalization','engine_producer':'WITHHELD','live_values':'WITHHELD'},
   'api13':{'proven_reads':[6,7],'role':'independent multiplicative ancestors of final RGB','factor':'api13[6] * api13[7]','engine_producer':'WITHHELD','live_values':'WITHHELD'},
  } if exact else None,
  'implementation_readiness':{
   'blend_state_exact':exact,
   'descriptor_layout_exact':exact,
   'api12_consumption_exact':exact,
   'api13_consumption_exact':exact,
   'exact_live_render_ready':False,
   'portable_preview_ready':exact,
   'hard_blockers':[
    'runtime producer/backing bytes for API12 values consumed at dwords 28..30',
    'runtime producer/backing bytes for API13 values consumed at dwords 6..7',
   ],
  },
  'rust_vulkan_requirements':[
   'preserve raw D1 material selector/state metadata alongside Vulkan pipeline state',
   'bind API0/API12/API13 descriptors at the proven user-data-derived locations or translate them losslessly into the runtime descriptor model',
   'do not substitute preview constants for unresolved API12/API13 live values in an exact mode',
   'apply the proven state-8 color/alpha blend factors and operations for circuitry material 816CE240',
   'retain native GCN SHA-256 and proof hashes in renderer diagnostics/provenance',
  ],
  'violations':v,
  'policy':'Vulkan names are implementation translations of an already-proven blend equation. They are not Bungie semantic names. Exact live rendering remains gated on primary runtime producer/backing evidence for API12/API13.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 0 if exact else 2
if __name__=='__main__':raise SystemExit(main())
