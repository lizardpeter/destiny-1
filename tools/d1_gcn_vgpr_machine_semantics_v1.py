#!/usr/bin/env python3
"""Source-backed VGPR write behavior for the exact Destiny 1 GFX7 shader corpus.

This layer deliberately does not assign arithmetic, texture, interpolation, LDS, or
material meaning. It closes only register/lane state mutation semantics needed by a
register-granular SSA: ordinary vector destinations are EXEC-gated, V_WRITELANE_B32
is a proven single-lane EXEC-independent update, and V_MOVRELS_B32 is a proven
M0-indexed dynamic VGPR source.
"""
from __future__ import annotations
import json

SCHEMA='d1_gcn_vgpr_machine_semantics/v1'
STATUS='D1_GCN_VGPR_MACHINE_SEMANTICS_SOURCE_CLOSED'
AMD={
 'vendor':'Advanced Micro Devices, Inc.',
 'title':'AMD Sea Islands Series Instruction Set Architecture',
 'document_id':'70653','revision':'1.3','release_date':'2013-12-01',
 'architecture':'GCN 2 / GFX7 / Sea Islands',
 'official_url':'https://docs.amd.com/v/u/en-US/sea-islands-instruction-set-architecture_0',
}

# Exact 74-opcode destination surface observed in the frozen 26,464-program corpus.
VGPR_DEF_OPCODES={
 'buffer_load_dword','ds_read2_b32','ds_read_b32','ds_swizzle_b32',
 'image_gather4_lz','image_gather4_lz_o','image_get_lod','image_get_resinfo',
 'image_load_mip','image_sample','image_sample_d','image_sample_l','image_sample_lz','image_sample_lz_o',
 'tbuffer_load_format_xyz','tbuffer_load_format_xyzw',
 'v_add_f32','v_add_i32','v_and_b32','v_ceil_f32','v_cndmask_b32','v_cos_f32',
 'v_cubeid_f32','v_cubema_f32','v_cubesc_f32','v_cubetc_f32',
 'v_cvt_f32_i32','v_cvt_f32_u32','v_cvt_i32_f32','v_cvt_pknorm_u16_f32','v_cvt_pkrtz_f16_f32','v_cvt_u32_f32',
 'v_exp_f32','v_floor_f32','v_fract_f32','v_interp_mov_f32','v_interp_p1_f32','v_interp_p2_f32',
 'v_log_f32','v_lshl_b64','v_lshlrev_b32','v_lshrrev_b32','v_mac_f32','v_mac_legacy_f32',
 'v_mad_f32','v_mad_i32_i24','v_mad_legacy_f32','v_madak_f32','v_madmk_f32',
 'v_max_f32','v_max_i32','v_max_legacy_f32','v_min3_f32','v_min_f32','v_mov_b32','v_movrels_b32',
 'v_mul_f32','v_mul_hi_u32','v_mul_i32_i24','v_mul_legacy_f32','v_mul_lo_i32','v_mul_lo_u32',
 'v_or_b32','v_rcp_f32','v_rndne_f32','v_rsq_clamp_f32','v_rsq_f32','v_sin_f32','v_sqrt_f32',
 'v_sub_f32','v_sub_i32','v_subrev_f32','v_trunc_f32','v_writelane_b32',
}
SPECIAL_UNMASKED={'v_writelane_b32'}
DYNAMIC_SOURCE={'v_movrels_b32'}


def source(locator): return {**AMD,'locator':locator}

def behavior(op):
 if op not in VGPR_DEF_OPCODES: raise KeyError(op)
 if op=='v_writelane_b32':
  return {
   'write_behavior':'SINGLE_LANE_UNMASKED',
   'destination':'one structurally named VGPR, one lane selected by operand 2',
   'old_destination_dependency':'YES_PRESERVE_ALL_OTHER_LANES',
   'exec_dependency':'IGNORES_EXEC',
   'value_semantics':'WITHHELD',
   'source':source('Ch. 12 VOP2/VOP3b V_WRITELANE_B32; description states one VGPR lane and ignores EXEC mask'),
  }
 if op=='v_movrels_b32':
  return {
   'write_behavior':'EXEC_MASKED_WHOLE_LANE_DEST',
   'destination':'one structurally named VGPR for active lanes',
   'old_destination_dependency':'YES_FOR_INACTIVE_LANES',
   'exec_dependency':'EXEC_IN',
   'dynamic_source':'VGPR[encoded_source + M0]',
   'value_semantics':'DYNAMIC_SOURCE_IDENTITY_ONLY',
   'source':source('Ch. 6.2.4 GPR Indexing; V_MOVRELS performs VGPR[dst] = VGPR[src + M0]'),
  }
 return {
  'write_behavior':'EXEC_MASKED_WHOLE_LANE_DEST',
  'destination':'each structurally named VGPR destination for active lanes',
  'old_destination_dependency':'YES_FOR_INACTIVE_LANES',
  'exec_dependency':'EXEC_IN',
  'value_semantics':'WITHHELD',
  'source':source('Ch. 3.3 EXECute Mask: EXEC bit 1 executes vector thread, bit 0 does not execute; opcode-specific value semantics withheld'),
 }

def document():
 return {
  'schema':SCHEMA,'status':STATUS,'source':AMD,
  'general_vector_write_rule':{
   'rule':'For ordinary vector instructions, destination lane state changes only where the instruction EXEC-in bit is 1; inactive destination lanes preserve their old register value.',
   'source':source('Ch. 3.3 EXECute Mask'),
  },
  'opcode_behaviors':{op:behavior(op) for op in sorted(VGPR_DEF_OPCODES)},
  'special_unmasked_opcodes':sorted(SPECIAL_UNMASKED),
  'dynamic_vgpr_source_opcodes':sorted(DYNAMIC_SOURCE),
  'shader_expression_semantic_promotions':0,
  'policy':'This registry proves only which VGPR/lane state can be mutated and which prior state must be preserved. Arithmetic results, interpolation meaning, LDS/memory contents, image sampling results, branch feasibility, material semantics and shader expressions remain withheld.'
 }

def validate():
 bad=[]
 if len(VGPR_DEF_OPCODES)!=74:bad.append(f'opcode_count:{len(VGPR_DEF_OPCODES)}!=74')
 if SPECIAL_UNMASKED!={'v_writelane_b32'}:bad.append('special_unmasked_surface_changed')
 if DYNAMIC_SOURCE!={'v_movrels_b32'}:bad.append('dynamic_source_surface_changed')
 for op in VGPR_DEF_OPCODES:
  b=behavior(op)
  if b['write_behavior'] not in {'EXEC_MASKED_WHOLE_LANE_DEST','SINGLE_LANE_UNMASKED'}:bad.append(f'bad_behavior:{op}')
 return bad

if __name__=='__main__':
 bad=validate();print(json.dumps(document() if not bad else {'status':'INVALID','violations':bad},indent=2,sort_keys=True));raise SystemExit(0 if not bad else 2)
