#!/usr/bin/env python3
"""Source-backed condition-mask and SCC machine semantics for exact D1 GFX7 corpus.

This is intentionally below shader semantics. It describes only architectural wave-mask
production/consumption, scalar condition-code writes and exact consumer roles needed by
path-aware condition SSA.
"""
from __future__ import annotations
import json

SCHEMA='d1_gcn_condition_machine_semantics/v1'
STATUS='D1_GCN_CONDITION_MACHINE_SEMANTICS_SOURCE_CLOSED'
AMD={
 'vendor':'Advanced Micro Devices, Inc.',
 'title':'AMD Sea Islands Series Instruction Set Architecture',
 'document_id':'70653','revision':'1.3','release_date':'2013-12-01',
 'architecture':'GCN 2 / GFX7 / Sea Islands',
 'official_url':'https://docs.amd.com/v/u/en-US/sea-islands-instruction-set-architecture_0',
}

COMPARES={
 'v_cmp_eq_i32':'signed integer equality',
 'v_cmp_gt_f32':'floating greater-than',
 'v_cmp_lt_f32':'floating less-than',
 'v_cmp_le_f32':'floating less-than-or-equal',
 'v_cmp_nlt_f32':'floating NLT condition',
 'v_cmp_ge_f32':'floating greater-than-or-equal',
 'v_cmp_lg_i32':'signed integer less-greater (not equal)',
 'v_cmp_neq_f32':'floating not-equal',
 'v_cmp_ngt_f32':'floating NGT condition',
 'v_cmp_gt_i32':'signed integer greater-than',
 'v_cmp_class_f32':'IEEE numeric-class test',
 'v_cmp_lt_i32':'signed integer less-than',
 'v_cmp_eq_f32':'floating equality',
 'v_cmpx_eq_i32':'signed integer equality with EXEC update',
 'v_cmpx_lt_u32':'unsigned integer less-than with EXEC update',
 'v_cmp_nle_f32':'floating NLE condition',
 'v_cmp_nge_f32':'floating NGE condition',
 'v_cmp_ge_u32':'unsigned integer greater-than-or-equal',
}
CMPX={'v_cmpx_eq_i32','v_cmpx_lt_u32'}
CARRY={
 'v_add_i32':'32-bit integer addition carry-out mask',
 'v_sub_i32':'32-bit integer subtraction carry/borrow mask',
}
SCALAR_MASK={
 's_mov_b64':'MASK_MOVE',
 's_and_b64':'MASK_AND',
 's_or_b64':'MASK_OR',
 's_andn2_b64':'MASK_AND_NOT_SECOND',
 's_xor_b64':'MASK_XOR',
 's_nand_b64':'MASK_NAND',
 's_wqm_b64':'MASK_WQM',
 's_and_saveexec_b64':'SAVE_OLD_EXEC_AND_UPDATE_EXEC',
}
SCC_PRODUCERS={
 's_addk_i32':{'kind':'SIGNED_OVERFLOW','locator':'Ch. 12 S_ADDK_I32'},
 's_and_b32':{'kind':'RESULT_NONZERO','locator':'Ch. 12 S_AND_B32'},
 's_and_b64':{'kind':'RESULT_NONZERO','locator':'Ch. 12 S_AND_B64'},
 's_and_saveexec_b64':{'kind':'NEW_EXEC_NONZERO','locator':'Ch. 12 S_AND_SAVEEXEC_B64'},
 's_andn2_b64':{'kind':'RESULT_NONZERO','locator':'Ch. 12 S_ANDN2_B64'},
 's_lshl_b32':{'kind':'RESULT_NONZERO','locator':'Ch. 12 S_LSHL_B32'},
 's_nand_b64':{'kind':'RESULT_NONZERO','locator':'Ch. 12 S_NAND_B64'},
 's_or_b64':{'kind':'RESULT_NONZERO','locator':'Ch. 12 S_OR_B64'},
 's_wqm_b64':{'kind':'RESULT_NONZERO','locator':'Ch. 12 S_WQM_B64'},
 's_xor_b64':{'kind':'RESULT_NONZERO','locator':'Ch. 12 S_XOR_B64'},
}
CONSUMERS={
 'v_cndmask_b32':{'kind':'VECTOR_SELECT_BY_MASK','mask_operand_index':3,'locator':'Ch. 12 V_CNDMASK_B32'},
 's_cbranch_vccz':{'kind':'MASK_EQ_ZERO_BRANCH','fixed_mask':'vcc','locator':'Ch. 12 S_CBRANCH_VCCZ'},
 's_cbranch_vccnz':{'kind':'MASK_NE_ZERO_BRANCH','fixed_mask':'vcc','locator':'Ch. 12 S_CBRANCH_VCCNZ'},
 's_cbranch_scc0':{'kind':'SCC_EQ_ZERO_BRANCH','fixed_condition':'scc','locator':'Ch. 12 S_CBRANCH_SCC0'},
}

# The exact corpus contains a B32 initialization of VCC_HI in every native program.
# This is an architectural partial write of the 64-bit VCC pair, not a high-level predicate semantic.
PARTIAL_MASK_WRITES={
 's_mov_b32':{'accepted_destinations':['vcc_lo','vcc_hi'],'kind':'MASK_HALF_WRITE','locator':'Ch. 6 scalar special registers; Ch. 12 S_MOV_B32'}
}


def source(locator): return {**AMD,'locator':locator}

def registry_document():
 return {
  'schema':SCHEMA,'status':STATUS,'source':AMD,
  'compare_opcodes':{op:{'operation':desc,'destination_operand_index':0,'execution':'EXEC_GATED_PER_LANE','inactive_lane_behavior':'DESTINATION_MASK_BIT_PRESERVED','cmpx_updates_exec':op in CMPX,'source':source('Ch. 6 vector compare behavior; Ch. 12 VOPC/VOP3 compare tables')} for op,desc in sorted(COMPARES.items())},
  'carry_mask_opcodes':{op:{'operation':desc,'destination_operand_index':1,'execution':'EXEC_GATED_PER_LANE','inactive_lane_behavior':'DESTINATION_MASK_BIT_PRESERVED','source':source('Ch. 6 integer arithmetic; Ch. 12 '+op.upper())} for op,desc in sorted(CARRY.items())},
  'scalar_mask_opcodes':{op:{'kind':kind,'execution':'SCALAR_UNMASKED','source':source('Ch. 12 '+op.upper())} for op,kind in sorted(SCALAR_MASK.items())},
  'scc_producers':{op:{**v,'source':source(v['locator'])} for op,v in sorted(SCC_PRODUCERS.items())},
  'consumers':{op:{**v,'source':source(v['locator'])} for op,v in sorted(CONSUMERS.items())},
  'partial_mask_writes':{op:{**v,'source':source(v['locator'])} for op,v in PARTIAL_MASK_WRITES.items()},
  'semantic_promotions':0,
  'policy':'Condition-mask and SCC machine effects are source-closed only. Predicate intent, branch feasibility, lane-value SSA, shader expressions, material roles and game semantics remain unproven.'
 }

def validate():
 p=[]
 if len(COMPARES)!=18:p.append(f'compare_count:{len(COMPARES)}!=18')
 if len(CARRY)!=2:p.append(f'carry_count:{len(CARRY)}!=2')
 if len(SCC_PRODUCERS)!=10:p.append(f'scc_producer_count:{len(SCC_PRODUCERS)}!=10')
 if set(CMPX)-set(COMPARES):p.append('cmpx_not_compare_subset')
 if SCC_PRODUCERS.get('s_mul_i32') is not None:p.append('s_mul_i32_must_not_define_scc')
 for op in COMPARES:
  if not op.startswith('v_cmp'):p.append(f'bad_compare_name:{op}')
 return p

if __name__=='__main__':
 bad=validate()
 print(json.dumps(registry_document() if not bad else {'status':'INVALID','problems':bad},indent=2,sort_keys=True))
 raise SystemExit(0 if not bad else 2)
