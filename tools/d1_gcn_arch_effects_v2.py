#!/usr/bin/env python3
"""Complete source-backed architectural-effect registry for the exact 67-opcode D1 frontier.

V2 extends the green v1 27-opcode tranche to every opcode that is structurally novel
relative to the 808EE505 baseline. This still does NOT promote shader-expression or
game/material semantics; it closes only GFX7 machine-instruction effects.
"""
from __future__ import annotations

from copy import deepcopy
import d1_gcn_arch_effects_v1 as v1

SCHEMA="d1_gcn_arch_effect_registry/v2"
STATUS="D1_GCN_ARCH_EFFECT_REGISTRY_ALL_67_FRONTIER_OPCODES_SOURCE_CLOSED"
SEMANTIC_STATUS="UNPROVEN"
AMD_SEA_ISLANDS=deepcopy(v1.AMD_SEA_ISLANDS)


def _e(*, family, execution_scope, exec_behavior, destination_write_scope="FULL_DESTINATION", implicit_reads=(), implicit_writes=(), memory_effect="NONE", control_flow="NONE", reads_old_destination=False, operation, source_locator, notes=()):
    return {
        "architectural_status":"SOURCE_CLOSED",
        "shader_expression_status":SEMANTIC_STATUS,
        "family":family,"execution_scope":execution_scope,"exec_behavior":exec_behavior,
        "destination_write_scope":destination_write_scope,"implicit_reads":list(implicit_reads),
        "implicit_writes":list(implicit_writes),"memory_effect":memory_effect,"control_flow":control_flow,
        "reads_old_destination":bool(reads_old_destination),"operation":operation,
        "source":{**AMD_SEA_ISLANDS,"locator":source_locator},"notes":list(notes),
    }


def _valu(operation, locator, *, family="VOP1_OR_VOP2_OR_VOP3", destination_write_scope="FULL_DESTINATION", implicit_reads=(), notes=()):
    return _e(family=family,execution_scope="VECTOR_PER_LANE",exec_behavior="EXEC_GATED",
              destination_write_scope=destination_write_scope,implicit_reads=("exec",*implicit_reads),
              operation=operation,source_locator=locator,notes=notes)


def _cmp(operation, locator):
    return _e(family="VOPC_OR_VOP3_COMPARE",execution_scope="VECTOR_PER_LANE",exec_behavior="EXEC_GATED",
              destination_write_scope="COMPARE_MASK",implicit_reads=("exec",),operation=operation,
              source_locator=locator,notes=("VOPC writes VCC; VOP3 writes its encoded SGPR-pair destination.",))


def _vmem(operation, locator, memory_effect, *, family="MIMG", destination_write_scope="FULL_DESTINATION"):
    return _e(family=family,execution_scope="VECTOR_MEMORY_PER_LANE",exec_behavior="EXEC_GATED",
              destination_write_scope=destination_write_scope,implicit_reads=("exec",),memory_effect=memory_effect,
              operation=operation,source_locator=locator)


EXTENSION={
    "v_cmp_nlt_f32":_cmp("floating NLT compare condition as defined by the ISA (NaN or normal comparison result)","Ch. 6 vector compare conditions; Ch. 12 VOPC F32 compare table"),
    "v_cvt_f32_u32":_valu("convert unsigned 32-bit integer to float32","Ch. 12 V_CVT_F32_U32",family="VOP1_OR_VOP3"),
    "v_cmp_ge_f32":_cmp("floating greater-than-or-equal compare","Ch. 6 vector compare conditions; Ch. 12 VOPC F32 compare table"),
    "v_cvt_u32_f32":_valu("convert float32 to unsigned 32-bit integer using ISA truncation/saturation rules","Ch. 12 V_CVT_U32_F32",family="VOP1_OR_VOP3"),
    "ds_read2_b32":_vmem("read two LDS dwords at independently offset addresses","Ch. 10 data share operations; Ch. 12 DS_READ2_B32","LDS_READ",family="DS",destination_write_scope="TWO_DWORDS"),
    "v_cmp_ngt_f32":_cmp("floating NGT compare condition as defined by the ISA (NaN or normal comparison result)","Ch. 6 vector compare conditions; Ch. 12 VOPC F32 compare table"),
    "s_lshl_b32":_e(family="SOP2",execution_scope="SCALAR_WAVE",exec_behavior="SCALAR_UNMASKED",implicit_writes=("scc",),operation="D.u = S0.u << S1.u[4:0]; SCC=1 iff result nonzero",source_locator="Ch. 12 S_LSHL_B32"),
    "s_movk_i32":_e(family="SOPK",execution_scope="SCALAR_WAVE",exec_behavior="SCALAR_UNMASKED",operation="D.i = signext(SIMM16)",source_locator="Ch. 12 S_MOVK_I32"),
    "s_addk_i32":_e(family="SOPK",execution_scope="SCALAR_WAVE",exec_behavior="SCALAR_UNMASKED",implicit_writes=("scc",),reads_old_destination=True,operation="D.i = D.i + signext(SIMM16); SCC=signed overflow",source_locator="Ch. 12 S_ADDK_I32"),
    "ds_read_b32":_vmem("read one LDS dword","Ch. 10 data share operations; Ch. 12 DS_READ_B32","LDS_READ",family="DS"),
    "v_max_i32":_valu("signed integer maximum","Ch. 12 V_MAX_I32",family="VOP2_OR_VOP3"),
    "v_cmp_class_f32":_cmp("IEEE numeric-class test selected by source class mask","Ch. 12 VOPC CLASS table: V_CMP_CLASS_F32"),
    "image_get_resinfo":_vmem("return mip-level resource information {mipLevels, depth, height, width}; no sampler","Ch. 8 image operations; Ch. 12 IMAGE_GET_RESINFO","IMAGE_RESOURCE_QUERY",destination_write_scope="UP_TO_FOUR_DWORDS"),
    "v_lshl_b64":_valu("64-bit logical left shift","Ch. 12 V_LSHL_B64",family="VOP3",destination_write_scope="TWO_DWORDS"),
    "v_mul_i32_i24":_valu("signed 24x24 multiply, low 32 bits","Ch. 12 V_MUL_I32_I24",family="VOP2_OR_VOP3"),
    "buffer_load_dword":_vmem("untyped buffer load of one dword","Ch. 8 buffer operations; Ch. 12 BUFFER_LOAD_DWORD","BUFFER_READ",family="MUBUF"),
    "v_mul_lo_i32":_valu("low 32 bits of signed 32x32 product","Ch. 12 V_MUL_LO_I32",family="VOP3"),
    "v_cmp_lt_i32":_cmp("signed integer less-than compare","Ch. 12 VOPC I32 compare table"),
    "buffer_store_dword":_vmem("untyped buffer store of one dword","Ch. 8 buffer operations; Ch. 12 BUFFER_STORE_DWORD","BUFFER_WRITE",family="MUBUF",destination_write_scope="NO_REGISTER_DESTINATION"),
    "v_cmp_eq_f32":_cmp("floating equality compare","Ch. 12 VOPC F32 compare table"),
    "v_ceil_f32":_valu("floating-point ceiling","Ch. 12 V_CEIL_F32",family="VOP1_OR_VOP3"),
    "v_max_legacy_f32":_valu("floating maximum using legacy DX9 NaN rules","Ch. 12 V_MAX_LEGACY_F32",family="VOP2_OR_VOP3"),
    "s_and_b32":_e(family="SOP2",execution_scope="SCALAR_WAVE",exec_behavior="SCALAR_UNMASKED",implicit_writes=("scc",),operation="32-bit bitwise AND; SCC=1 iff result nonzero",source_locator="Ch. 12 S_AND_B32"),
    "s_nand_b64":_e(family="SOP2",execution_scope="SCALAR_WAVE",exec_behavior="SCALAR_UNMASKED",implicit_writes=("scc",),operation="64-bit bitwise NAND; SCC=1 iff result nonzero",source_locator="Ch. 12 S_NAND_B64"),
    "v_lshrrev_b32":_valu("D.u = S1.u >> S0.u[4:0]","Ch. 12 V_LSHRREV_B32",family="VOP2_OR_VOP3"),
    "image_gather4_lz":_vmem("gather four single-component elements (2x2) at level zero","Ch. 8 image operations; Ch. 12 IMAGE_GATHER4_LZ","IMAGE_GATHER"),
    "v_interp_mov_f32":_e(family="VINTRP",execution_scope="VECTOR_PER_LANE",exec_behavior="EXEC_GATED",implicit_reads=("exec","m0"),operation="load P10, P20 or P0 parameter selected by VSRC",source_locator="Ch. 10 parameter reads / V_INTERP_MOV_F32",notes=("ISA states M0 use is automatic for parameter interpolation.",)),
    "v_movrels_b32":_valu("relative VGPR source move: VGPR[D] = VGPR[S0 + M0]","Ch. 6 GPR indexing; Ch. 13 V_MOVRELS_B32",family="VOP1_OR_VOP3",implicit_reads=("m0",)),
    "image_sample_lz_o":_vmem("sample with user-specified offsets from level zero","Ch. 8 image operations; Ch. 12 IMAGE_SAMPLE_LZ_O","IMAGE_SAMPLE"),
    "s_xor_b64":_e(family="SOP2",execution_scope="SCALAR_WAVE",exec_behavior="SCALAR_UNMASKED",implicit_writes=("scc",),operation="64-bit bitwise XOR; SCC=1 iff result nonzero",source_locator="Ch. 12 S_XOR_B64"),
    "tbuffer_load_format_xyz":_vmem("typed buffer load of XYZ components with format conversion","Ch. 8 buffer operations; Ch. 12 TBUFFER_LOAD_FORMAT_XYZ","TYPED_BUFFER_READ",family="MTBUF",destination_write_scope="THREE_DWORDS_FORMAT_CONVERTED"),
    "v_mad_i32_i24":_valu("24-bit signed integer multiply-add, low sign-extended 32-bit result","Ch. 12 V_MAD_I32_I24",family="VOP3"),
    "v_cmp_nle_f32":_cmp("floating NLE compare condition as defined by the ISA (NaN or normal comparison result)","Ch. 6 vector compare conditions; Ch. 12 VOPC F32 compare table"),
    "v_trunc_f32":_valu("floating truncation toward zero to integer-valued float","Ch. 12 V_TRUNC_F32",family="VOP1_OR_VOP3"),
    "image_gather4_lz_o":_vmem("gather four single-component elements (2x2) at level zero with user offsets","Ch. 8 image operations; Ch. 12 IMAGE_GATHER4_LZ_O","IMAGE_GATHER"),
    "v_cmp_ge_u32":_cmp("unsigned integer greater-than-or-equal compare","Ch. 12 VOPC U32 compare table"),
    "v_cmp_nge_f32":_cmp("floating NGE compare condition as defined by the ISA (NaN or normal comparison result)","Ch. 6 vector compare conditions; Ch. 12 VOPC F32 compare table"),
    "v_cvt_pknorm_u16_f32":_valu("pack two float32 values as two UNORM16 values","Ch. 12 V_CVT_PKNORM_U16_F32",family="VOP2_OR_VOP3",destination_write_scope="PACKED_TWO_U16"),
    "v_min3_f32":_valu("minimum of three float32 inputs with ISA DX10 NaN behavior","Ch. 12 V_MIN3_F32",family="VOP3"),
    "v_mul_hi_u32":_valu("high 32 bits of unsigned 32x32 product","Ch. 12 V_MUL_HI_U32",family="VOP3"),
}

REGISTRY={k:deepcopy(v) for k,v in v1.REGISTRY.items()}
for _op,_effect in EXTENSION.items():
    if _op in REGISTRY:
        raise RuntimeError(f"v2 extension duplicates v1 opcode {_op}")
    REGISTRY[_op]=_effect


def validate_registry():
    problems=[]
    if len(REGISTRY)!=67: problems.append(f"registry_count:{len(REGISTRY)}!=67")
    if len(EXTENSION)!=40: problems.append(f"extension_count:{len(EXTENSION)}!=40")
    required={"architectural_status","shader_expression_status","family","execution_scope","exec_behavior","destination_write_scope","implicit_reads","implicit_writes","memory_effect","control_flow","reads_old_destination","operation","source","notes"}
    for op,e in sorted(REGISTRY.items()):
        miss=required-set(e)
        if miss: problems.append(f"{op}:missing:{sorted(miss)}")
        if e.get('architectural_status')!='SOURCE_CLOSED': problems.append(f"{op}:architectural_status")
        if e.get('shader_expression_status')!='UNPROVEN': problems.append(f"{op}:shader_expression_status")
        src=e.get('source') or {}
        for k in ('document_id','revision','release_date','official_url','locator'):
            if not src.get(k): problems.append(f"{op}:source:{k}")
    return problems


def annotate_instruction(inst):
    op=str(inst.get('opcode','')); e=REGISTRY.get(op)
    defs=list(inst.get('defs') or []); uses=list(inst.get('uses') or [])
    if e is None:
        return {'opcode':op,'architectural_status':'UNPROVEN','shader_expression_status':'UNPROVEN','architectural_defs':defs,'architectural_uses':uses}
    if e['reads_old_destination']: uses.extend(defs)
    defs.extend(e['implicit_writes']); uses.extend(e['implicit_reads'])
    return {'opcode':op,'architectural_status':'SOURCE_CLOSED','shader_expression_status':'UNPROVEN','architectural_defs':list(dict.fromkeys(defs)),'architectural_uses':list(dict.fromkeys(uses)),'effects':deepcopy(e)}


def registry_document():
    return {'schema':SCHEMA,'status':STATUS,'source':AMD_SEA_ISLANDS,'source_closed_opcode_count':len(REGISTRY),'extension_opcode_count':len(EXTENSION),'semantic_promotions':0,'opcodes':{k:deepcopy(REGISTRY[k]) for k in sorted(REGISTRY)},'policy':'All 67 exact 808EE505-baseline-novel opcode architectural effects are source-closed against AMD Sea Islands ISA 70653 revision 1.3. Shader-expression, material and game semantics remain UNPROVEN.'}

if __name__=='__main__':
    import json
    bad=validate_registry()
    if bad:
        print(json.dumps({'status':'INVALID','problems':bad},indent=2)); raise SystemExit(2)
    print(json.dumps(registry_document(),indent=2,sort_keys=True))
