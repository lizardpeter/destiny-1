#!/usr/bin/env python3
"""Source-backed base formula semantics for the 50 exact D1 GFX7 VALU-result opcodes.

This registry closes opcode identity/formula semantics only. It does not infer shader intent,
material roles, resource contents, interpolation meaning, or numerically emulate floating-point
instructions with host arithmetic. Floating-point MODE state and VOP3 modifiers remain explicit
architectural inputs/boundaries. AMD Sea Islands ISA revision 1.3 contains an internal CLAMP-range
conflict, so CLAMP numeric evaluation is deliberately withheld.
"""
from __future__ import annotations
import json

SCHEMA = "d1_gcn_vector_formula_semantics/v1"
STATUS = "D1_GCN_VECTOR_BASE_FORMULAS_SOURCE_CLOSED"
AMD = {
    "vendor": "Advanced Micro Devices, Inc.",
    "title": "AMD Sea Islands Series Instruction Set Architecture",
    "document_id": "70653",
    "revision": "1.3",
    "release_date": "2013-12-01",
    "architecture": "GCN 2 / GFX7 / Sea Islands",
    "official_url": "https://docs.amd.com/v/u/en-US/sea-islands-instruction-set-architecture_0",
}

PENDING = {
    'v_add_f32','v_and_b32','v_ceil_f32','v_cos_f32','v_cubeid_f32','v_cubema_f32',
    'v_cubesc_f32','v_cubetc_f32','v_cvt_f32_i32','v_cvt_f32_u32','v_cvt_i32_f32',
    'v_cvt_pknorm_u16_f32','v_cvt_pkrtz_f16_f32','v_cvt_u32_f32','v_exp_f32',
    'v_floor_f32','v_fract_f32','v_log_f32','v_lshl_b64','v_lshlrev_b32','v_lshrrev_b32',
    'v_mac_f32','v_mac_legacy_f32','v_mad_f32','v_mad_i32_i24','v_mad_legacy_f32',
    'v_madak_f32','v_madmk_f32','v_max_f32','v_max_i32','v_max_legacy_f32','v_min3_f32',
    'v_min_f32','v_mov_b32','v_mul_f32','v_mul_hi_u32','v_mul_i32_i24','v_mul_legacy_f32',
    'v_mul_lo_i32','v_mul_lo_u32','v_or_b32','v_rcp_f32','v_rndne_f32','v_rsq_clamp_f32',
    'v_rsq_f32','v_sin_f32','v_sqrt_f32','v_sub_f32','v_subrev_f32','v_trunc_f32',
}

BIT_EXACT_REPLAY_READY = {
    'v_and_b32','v_lshl_b64','v_lshlrev_b32','v_lshrrev_b32','v_mad_i32_i24','v_max_i32',
    'v_mov_b32','v_mul_hi_u32','v_mul_i32_i24','v_mul_lo_i32','v_mul_lo_u32','v_or_b32',
}


def src(locator: str, pdf_pages: str) -> dict:
    return {**AMD, "locator": locator, "pdf_pages": pdf_pages}


def E(explicit_sources: int, result_components: int, result_kind: str, formula: str,
      semantic_kind: str, locator: str, pages: str, *, old_dest: bool=False,
      special_rules: list[str] | None=None, numeric_replay: str | None=None,
      fp_state: str | None=None) -> dict:
    if numeric_replay is None:
        numeric_replay = "SYMBOLIC_SOURCE_CLOSED_NUMERIC_REPLAY_WITHHELD"
    if fp_state is None:
        fp_state = "NOT_APPLICABLE" if result_kind in {"B32","I32","U32","B64"} and 'f32' not in formula.lower() else "BIND_MODE_SNAPSHOT_BEFORE_NUMERIC_EVALUATION"
    return {
        "explicit_source_count": explicit_sources,
        "result_components": result_components,
        "result_kind": result_kind,
        "formula": formula,
        "semantic_kind": semantic_kind,
        "old_destination_is_input": old_dest,
        "special_rules": special_rules or [],
        "numeric_replay_status": numeric_replay,
        "fp_state_policy": fp_state,
        "source": src(locator, pages),
    }


FORMULAS = {
    'v_add_f32': E(2,1,'F32','D.f = S0.f + S1.f','FP_BASIC','Ch. 12 V_ADD_F32 / Ch. 13 VOP2 summary','146, 276'),
    'v_and_b32': E(2,1,'B32','D.u = S0.u & S1.u','BITWISE','Ch. 12 V_AND_B32 / Ch. 13 VOP2 summary','147, 276',numeric_replay='BIT_EXACT_REPLAY_READY'),
    'v_ceil_f32': E(1,1,'F32','D.f = ceil(S0.f)','FP_ROUNDING_PRIMITIVE','Ch. 12 V_CEIL_F32 / Ch. 13 VOP1 summary','171, 279',special_rules=['implemented as truncation plus positive non-integral correction']),
    'v_cos_f32': E(1,1,'F32','D.f = hardware_cos_normalized(S0.f)','FP_SPECIAL_FUNCTION','Ch. 12 V_COS_F32 / Ch. 13 VOP1 summary','173, 280',special_rules=['input is normalized by 2*PI','documented valid normalized domain [-256,+256]','out-of-range input returns 1.0']),
    'v_cubeid_f32': E(3,1,'F32','D.f = cube_face_id(S0.f,S1.f,S2.f)','CUBEMAP_COORDINATE','Ch. 12 V_CUBEID_F32','213',special_rules=['piecewise major-axis face ID 0..5 exactly as source pseudocode']),
    'v_cubema_f32': E(3,1,'F32','D.f = 2.0 * signed_major_axis(S0.f,S1.f,S2.f)','CUBEMAP_COORDINATE','Ch. 12 V_CUBEMA_F32','213',special_rules=['major-axis tie ordering Z then Y then X exactly as source pseudocode']),
    'v_cubesc_f32': E(3,1,'F32','D.f = cube_s_coordinate_numerator(S0.f,S1.f,S2.f)','CUBEMAP_COORDINATE','Ch. 12 V_CUBESC_F32','214',special_rules=['piecewise sign/axis rule exactly as source pseudocode']),
    'v_cubetc_f32': E(3,1,'F32','D.f = cube_t_coordinate_numerator(S0.f,S1.f,S2.f)','CUBEMAP_COORDINATE','Ch. 12 V_CUBETC_F32','214',special_rules=['piecewise sign/axis rule exactly as source pseudocode']),
    'v_cvt_f32_i32': E(1,1,'F32','D.f = float32_from_signed_i32(S0.i)','CONVERSION','Ch. 12 V_CVT_F32_I32 / Ch. 13 VOP1 summary','175, 279'),
    'v_cvt_f32_u32': E(1,1,'F32','D.f = float32_from_unsigned_u32(S0.u)','CONVERSION','Ch. 12 V_CVT_F32_U32 / Ch. 13 VOP1 summary','175, 279'),
    'v_cvt_i32_f32': E(1,1,'I32','D.i = truncating_saturating_i32_from_f32(S0.f)','CONVERSION','Ch. 12 V_CVT_I32_F32','180',special_rules=['truncate toward zero','overflow saturates to max_int/-max_int','+inf->max_int','-inf->-max_int','NaN and +/-0 -> 0']),
    'v_cvt_pknorm_u16_f32': E(2,1,'B32','D = pack_u16(DX_UNORM16(S1.f), DX_UNORM16(S0.f))','PACK_CONVERSION','Ch. 12 V_CVT_PKNORM_U16_F32 / Ch. 13 VOP2 summary','152, 277',special_rules=['source defines DX Float32 to UNORM16 conversion; keep conversion as architectural helper rather than host cast']),
    'v_cvt_pkrtz_f16_f32': E(2,1,'B32','D = pack_f16(f32_to_f16_rtz(S1.f), f32_to_f16_rtz(S0.f))','PACK_CONVERSION','Ch. 12 V_CVT_PKRTZ_F16_F32 / Ch. 13 VOP2 summary','153, 277',special_rules=['round toward zero is instruction-defined']),
    'v_cvt_u32_f32': E(1,1,'U32','D.u = truncating_saturating_u32_from_f32(S0.f)','CONVERSION','Ch. 12 V_CVT_U32_F32','183',special_rules=['truncate toward zero','positive overflow saturates to max_uint','-inf, NaN, +/-0 -> 0','+inf -> max_uint']),
    'v_exp_f32': E(1,1,'F32','D.f = hardware_pow2(S0.f)','FP_SPECIAL_FUNCTION','Ch. 12 V_EXP_F32 / Ch. 13 VOP1 summary','185-186, 279'),
    'v_floor_f32': E(1,1,'F32','D.f = floor(S0.f)','FP_ROUNDING_PRIMITIVE','Ch. 12 V_FLOOR_F32 / Ch. 13 VOP1 summary','187, 279',special_rules=['source implements truncation plus negative non-integral correction']),
    'v_fract_f32': E(1,1,'F32','D.f = S0.f - floor(S0.f)','FP_ROUNDING_PRIMITIVE','Ch. 12 V_FRACT_F32 / Ch. 13 VOP1 summary','188, 279'),
    'v_log_f32': E(1,1,'F32','D.f = hardware_log2(S0.f)','FP_SPECIAL_FUNCTION','Ch. 12 V_LOG_F32 / Ch. 13 VOP1 summary','190-191, 279'),
    'v_lshl_b64': E(2,2,'B64','D.u64 = S0.u64 << (S1.u & 0x3f)','INTEGER_SHIFT','Ch. 12 V_LSHL_B64 / Ch. 13 VOP3a summary','221, 286',numeric_replay='BIT_EXACT_REPLAY_READY'),
    'v_lshlrev_b32': E(2,1,'B32','D.u = S1.u << (S0.u & 0x1f)','INTEGER_SHIFT','Ch. 12 V_LSHLREV_B32 / Ch. 13 VOP2 summary','154, 276',numeric_replay='BIT_EXACT_REPLAY_READY'),
    'v_lshrrev_b32': E(2,1,'B32','D.u = S1.u >> (S0.u & 0x1f)','INTEGER_SHIFT','Ch. 12 V_LSHRREV_B32 / Ch. 13 VOP2 summary','155, 276',numeric_replay='BIT_EXACT_REPLAY_READY'),
    'v_mac_f32': E(2,1,'F32','D.f = S0.f * S1.f + OLD_D.f','FP_ACCUMULATE','Ch. 12 V_MAC_F32 / Ch. 13 VOP2 summary','156, 276',old_dest=True,special_rules=['preserve as one architectural MAC opcode; do not lower to host mul+add']),
    'v_mac_legacy_f32': E(2,1,'F32','D.f = legacy_muladd(S0.f,S1.f,OLD_D.f)','FP_LEGACY_ACCUMULATE','Ch. 12 V_MAC_LEGACY_F32 / Ch. 13 VOP2 summary','156, 276',old_dest=True,special_rules=['DX9 legacy multiply rule: 0.0 * anything = 0.0']),
    'v_mad_f32': E(3,1,'F32','D.f = gfx7_mad_f32(S0.f,S1.f,S2.f)','FP_MAD','Ch. 12/13 V_MAD_F32','222-223, 285',special_rules=['preserve opcode atomicity; V_FMA_F32 is a distinct opcode in the ISA']),
    'v_mad_i32_i24': E(3,1,'I32','D.i = low32(signext24(S0) * signext24(S1) + S2.i)','INTEGER_MAD_I24','Ch. 12/13 V_MAD_I32_I24','222-223, 285',numeric_replay='BIT_EXACT_REPLAY_READY'),
    'v_mad_legacy_f32': E(3,1,'F32','D.f = legacy_muladd(S0.f,S1.f,S2.f)','FP_LEGACY_MAD','Ch. 12/13 V_MAD_LEGACY_F32','222, 285',special_rules=['DX9 legacy multiply rule: 0.0 * anything = 0.0']),
    'v_madak_f32': E(3,1,'F32','D.f = gfx7_madak_f32(S0.f,S1.f,K32)','FP_LITERAL_MAD','Ch. 12 V_MADAK_F32 / Ch. 13 VOP2 summary','156, 276',special_rules=['K is the literal 32-bit constant encoded with the instruction']),
    'v_madmk_f32': E(3,1,'F32','D.f = gfx7_madmk_f32(S0.f,K32,S1.f)','FP_LITERAL_MAD','Ch. 12 V_MADMK_F32 / Ch. 13 VOP2 summary','157, 276',special_rules=['K is the literal 32-bit constant encoded with the instruction']),
    'v_max_f32': E(2,1,'F32','D.f = gfx7_max_f32_mode_aware(S0.f,S1.f)','FP_MINMAX_MODE_AWARE','Ch. 12 V_MAX_F32; MODE register IEEE/DX10_CLAMP','157-159, 27',special_rules=['NaN behavior depends on IEEE/DX10-related architectural mode; do not map to host max']),
    'v_max_i32': E(2,1,'I32','D.i = max_signed_i32(S0.i,S1.i)','INTEGER_MINMAX','Ch. 12/13 V_MAX_I32','159, 276',numeric_replay='BIT_EXACT_REPLAY_READY'),
    'v_max_legacy_f32': E(2,1,'F32','D.f = legacy_max_f32(S0.f,S1.f)','FP_LEGACY_MINMAX','Ch. 12/13 V_MAX_LEGACY_F32','160, 276',special_rules=['DX9 legacy NaN handling']),
    'v_min3_f32': E(3,1,'F32','D.f = min3_dx10_f32(S0.f,S1.f,S2.f)','FP_MINMAX_MODE_AWARE','Ch. 12 V_MIN3_F32 / Ch. 13 VOP3a summary','227, 285',special_rules=['DX10 NaN handling and flag creation']),
    'v_min_f32': E(2,1,'F32','D.f = gfx7_min_f32_mode_aware(S0.f,S1.f)','FP_MINMAX_MODE_AWARE','Ch. 12 V_MIN_F32; MODE register IEEE/DX10_CLAMP','160-162, 27',special_rules=['NaN and signed-zero rules are architectural; do not map to host min']),
    'v_mov_b32': E(1,1,'B32','D.u = S0.u','BIT_MOVE','Ch. 12/13 V_MOV_B32','194, 279',numeric_replay='BIT_EXACT_REPLAY_READY'),
    'v_mul_f32': E(2,1,'F32','D.f = S0.f * S1.f','FP_BASIC','Ch. 12/13 V_MUL_F32','163, 276'),
    'v_mul_hi_u32': E(2,1,'U32','D.u = high32(S0.u * S1.u)','INTEGER_MULTIPLY','Ch. 12/13 V_MUL_HI_U32','231, 286',numeric_replay='BIT_EXACT_REPLAY_READY'),
    'v_mul_i32_i24': E(2,1,'I32','D.i = low32(signext24(S0) * signext24(S1))','INTEGER_MULTIPLY_I24','Ch. 12/13 V_MUL_I32_I24','164, 276',numeric_replay='BIT_EXACT_REPLAY_READY'),
    'v_mul_legacy_f32': E(2,1,'F32','D.f = legacy_mul_f32(S0.f,S1.f)','FP_LEGACY_MULTIPLY','Ch. 12/13 V_MUL_LEGACY_F32','164, 276',special_rules=['DX9 rule: 0.0 * anything = 0.0']),
    'v_mul_lo_i32': E(2,1,'I32','D.i = low32(S0.i * S1.i)','INTEGER_MULTIPLY','Ch. 12/13 V_MUL_LO_I32','231, 286',numeric_replay='BIT_EXACT_REPLAY_READY'),
    'v_mul_lo_u32': E(2,1,'U32','D.u = low32(S0.u * S1.u)','INTEGER_MULTIPLY','Ch. 12/13 V_MUL_LO_U32','232, 286',numeric_replay='BIT_EXACT_REPLAY_READY'),
    'v_or_b32': E(2,1,'B32','D.u = S0.u | S1.u','BITWISE','Ch. 12/13 V_OR_B32','165, 276',numeric_replay='BIT_EXACT_REPLAY_READY'),
    'v_rcp_f32': E(1,1,'F32','D.f = hardware_reciprocal_f32(S0.f)','FP_SPECIAL_FUNCTION','Ch. 12/13 V_RCP_F32','195-196, 287',special_rules=['architectural reciprocal approximation; do not replace with host 1/x for bit-exact replay']),
    'v_rndne_f32': E(1,1,'F32','D.f = round_nearest_even(S0.f)','FP_ROUNDING_PRIMITIVE','Ch. 12/13 V_RNDNE_F32','199, 279',special_rules=['rounding direction is instruction-defined nearest-even']),
    'v_rsq_clamp_f32': E(1,1,'F32','D.f = clamp_finite(hardware_rsqrt_f32(S0.f))','FP_SPECIAL_FUNCTION','Ch. 12/13 V_RSQ_CLAMP_F32','200-201, 287',special_rules=['result infinity is clamped to signed max_float']),
    'v_rsq_f32': E(1,1,'F32','D.f = hardware_rsqrt_f32(S0.f)','FP_SPECIAL_FUNCTION','Ch. 12/13 V_RSQ_F32','201-202, 287'),
    'v_sin_f32': E(1,1,'F32','D.f = hardware_sin_normalized(S0.f)','FP_SPECIAL_FUNCTION','Ch. 12/13 V_SIN_F32','202, 280',special_rules=['input is normalized by 2*PI','documented valid normalized domain [-256,+256]']),
    'v_sqrt_f32': E(1,1,'F32','D.f = sqrt_f32(S0.f)','FP_SPECIAL_FUNCTION','Ch. 12/13 V_SQRT_F32','203, 280'),
    'v_sub_f32': E(2,1,'F32','D.f = S0.f - S1.f','FP_BASIC','Ch. 12/13 V_SUB_F32','166, 276'),
    'v_subrev_f32': E(2,1,'F32','D.f = S1.f - S0.f','FP_BASIC','Ch. 12/13 V_SUBREV_F32','168, 276'),
    'v_trunc_f32': E(1,1,'F32','D.f = trunc(S0.f)','FP_ROUNDING_PRIMITIVE','Ch. 12/13 V_TRUNC_F32','204, 279'),
}

VOP3_MODIFIERS = {
    "input_abs_then_neg": {"status":"SOURCE_CLOSED","rule":"ABS on an input is applied before NEG; NEG is applied after ABS.","source":src("Ch. 13 VOP3a/VOP3b field descriptions","284, 289, 293")},
    "output_modifier": {"status":"SOURCE_CLOSED","rule":"OMOD applies before CLAMP: 0=no change, 1=*2, 2=*4, 3=/2.","source":src("Ch. 13 VOP3a/VOP3b OMOD field","289, 293")},
    "clamp": {
        "status":"WITHHELD_AMD_REV1_3_INTERNAL_SOURCE_CONFLICT",
        "chapter_6_claim":"clamp floating result to [-1.0,+1.0]",
        "chapter_13_claim":"clamp output to [0.0,1.0] after OMOD",
        "source_chapter_6":src("Ch. 6.2.2 vector outputs","50"),
        "source_chapter_13":src("Ch. 13 VOP3 field description","284"),
        "policy":"Do not numerically evaluate CLAMP until the conflict is resolved by stronger architecture-specific evidence."
    },
}

FP_MODE = {
    "status":"SOURCE_CLOSED_AS_ARCHITECTURAL_STATE",
    "fields": {
        "FP_ROUND_F32":"nearest-even / +infinity / -infinity / toward-zero",
        "FP_DENORM_F32":"flush/allow input and output denorm combinations",
        "DX10_CLAMP":"MODE bit affecting NaN treatment",
        "IEEE":"MODE bit affecting IEEE signaling-NaN behavior for supported operations",
    },
    "source":src("Ch. 3.5 MODE register; Ch. 6.4 Denormals and Rounding Modes","27, 54"),
    "policy":"Attach the MODE snapshot to floating-point symbolic operations before any numeric replay; opcode-specific relevance remains explicit in the node/registry rather than being replaced by host FP defaults."
}


def document() -> dict:
    return {
        "schema":SCHEMA,"status":STATUS,"source":AMD,
        "base_formula_opcode_count":len(FORMULAS),
        "formulas":{k:FORMULAS[k] for k in sorted(FORMULAS)},
        "bit_exact_replay_ready_opcodes":sorted(BIT_EXACT_REPLAY_READY),
        "vop3_modifier_semantics":VOP3_MODIFIERS,
        "fp_mode_state":FP_MODE,
        "shader_expression_semantic_promotions":0,
        "policy":"All 50 exact retail VALU formula-pending opcodes now have a source-backed architectural base operation. Opcode atomicity is preserved: MAD/MAC/transcendental/legacy/conversion helpers are not rewritten as host-language expressions. Integer/bit operations without observed modifiers may proceed to bit-exact symbolic replay. Floating-point numeric replay remains gated on MODE and opcode-specific hardware behavior. VOP3 CLAMP remains unresolved because AMD revision 1.3 contains conflicting clamp ranges."
    }


def validate() -> list[str]:
    bad=[]
    if set(FORMULAS)!=PENDING: bad.append(f"formula_surface_missing={sorted(PENDING-set(FORMULAS))};extra={sorted(set(FORMULAS)-PENDING)}")
    if len(FORMULAS)!=50: bad.append(f"formula_count:{len(FORMULAS)}!=50")
    if len(BIT_EXACT_REPLAY_READY)!=12: bad.append(f"bit_exact_count:{len(BIT_EXACT_REPLAY_READY)}!=12")
    if not BIT_EXACT_REPLAY_READY<=PENDING: bad.append("bit_exact_not_subset")
    for op,e in FORMULAS.items():
        if e['explicit_source_count'] not in {1,2,3}: bad.append(f"source_count:{op}:{e['explicit_source_count']}")
        if e['result_components'] not in {1,2}: bad.append(f"result_components:{op}:{e['result_components']}")
        if not e['formula']: bad.append(f"missing_formula:{op}")
        if not e['source'].get('locator') or not e['source'].get('pdf_pages'): bad.append(f"missing_source:{op}")
        if op in BIT_EXACT_REPLAY_READY and e['numeric_replay_status']!='BIT_EXACT_REPLAY_READY': bad.append(f"bit_exact_status:{op}")
    if FORMULAS['v_mac_f32']['old_destination_is_input'] is not True: bad.append('mac_old_dest_missing')
    if FORMULAS['v_mac_legacy_f32']['old_destination_is_input'] is not True: bad.append('legacy_mac_old_dest_missing')
    if FORMULAS['v_lshl_b64']['result_components']!=2: bad.append('lshl_b64_width')
    if VOP3_MODIFIERS['clamp']['status']!='WITHHELD_AMD_REV1_3_INTERNAL_SOURCE_CONFLICT': bad.append('clamp_conflict_must_remain_withheld')
    return bad

if __name__=='__main__':
    bad=validate();print(json.dumps(document() if not bad else {'status':'INVALID','violations':bad},indent=2,sort_keys=True));raise SystemExit(0 if not bad else 2)
