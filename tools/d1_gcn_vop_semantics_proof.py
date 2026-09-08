#!/usr/bin/env python3
"""Promote a pinned subset of AMDGPU value/export semantics used by D1 shader lifting.

Inputs are fetched from immutable source revisions by workflows. Only literal source
semantics are promoted; no Destiny material meaning or portable channel assignment is
inferred. Legacy floating-point operations remain distinct operators rather than being
silently collapsed to ordinary IEEE arithmetic.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--instr-info',type=Path,required=True)
    ap.add_argument('--modifier-syntax',type=Path,required=True)
    ap.add_argument('--instr-revision',required=True)
    ap.add_argument('--modifier-revision',required=True)
    ap.add_argument('--vop1-source',type=Path);ap.add_argument('--vop1-revision')
    ap.add_argument('--vop2-source',type=Path);ap.add_argument('--vop2-revision')
    ap.add_argument('--vop3-source',type=Path);ap.add_argument('--vop3-revision')
    ap.add_argument('--vinterp-source',type=Path);ap.add_argument('--vinterp-revision')
    ap.add_argument('--sop1-source',type=Path);ap.add_argument('--sop1-revision')
    ap.add_argument('--si-source',type=Path);ap.add_argument('--si-revision')
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args();viol=[];sem={}
    try:
        it=a.instr_info.read_text(errors='replace');mt=a.modifier_syntax.read_text(errors='replace')
        exp='// v_exp_f32, which is exp2, no denormal handling for f32.'
        rcp='// out = 1.0 / a'
        rsq='// out = 1.0 / sqrt(a) result clamped to +/- max_float.'
        assert exp in it,exp
        assert rcp in it,rcp
        assert rsq in it,rsq
        assert 'def AMDGPUrcp_impl : SDNode<"AMDGPUISD::RCP", SDTFPUnaryOp>;' in it
        assert 'def AMDGPUrsq_clamp_impl : SDNode<"AMDGPUISD::RSQ_CLAMP", SDTFPUnaryOp>;' in it
        assert 'For floating-point operations, clamp modifier indicates that the result must be clamped' in mt
        assert 'to the range [0.0, 1.0]. By default, there is no clamping.' in mt
        assert 'clamp modifier is applied after' in mt
        assert 'Indicates if the data is compressed (data is not compressed by default).' in mt
        assert 'compr                                    Data is compressed.' in mt
        assert 'done                                     Indicates the last export operation.' in mt
        assert 'vm                                       Set the flag indicating a valid' in mt
        sem={
          'v_exp_f32':{'operation':'EXP2','equation':'D = pow(2.0, S0)','denormal_note':'source states no denormal handling for f32','source_revision':a.instr_revision,'source_file_sha256':sha(a.instr_info),'source_literal':exp},
          'v_rcp_f32':{'operation':'RCP','equation':'D = 1.0 / S0','source_revision':a.instr_revision,'source_file_sha256':sha(a.instr_info),'source_literal':rcp},
          'v_rsq_clamp_f32':{'operation':'RSQ_CLAMP_MAXFLOAT','equation':'D = clamp_to_signed_max_float(1.0 / sqrt(S0))','source_revision':a.instr_revision,'source_file_sha256':sha(a.instr_info),'source_literal':rsq},
          'float_clamp':{'operation':'CLAMP_0_1','equation':'D = clamp(D, 0.0, 1.0)','application_order':'after output modifiers','source_revision':a.modifier_revision,'source_file_sha256':sha(a.modifier_syntax)},
          'exp_compr':{'operation':'COMPRESSED_EXPORT_FLAG','equation':'EXP.compr means exported data is compressed','channel_mapping':'WITHHELD_NOT_STATED_BY_THIS_SOURCE','source_revision':a.modifier_revision,'source_file_sha256':sha(a.modifier_syntax)},
          'exp_done':{'operation':'LAST_EXPORT_FLAG','equation':'EXP.done marks the last export operation','source_revision':a.modifier_revision,'source_file_sha256':sha(a.modifier_syntax)},
          'exp_vm':{'operation':'VALID_EXEC_MASK_FLAG','equation':'EXP.vm marks the EXEC mask valid for the export','source_revision':a.modifier_revision,'source_file_sha256':sha(a.modifier_syntax)},
        }
        if a.vop1_source is not None:
            if not a.vop1_revision:raise ValueError('--vop1-revision required with --vop1-source')
            vt=a.vop1_source.read_text(errors='replace')
            mov='// D.u = S0.u.';log='// D.f = log2(S0.f). Base 2 logarithm.'
            assert mov in vt and 'Inst_VOP1__V_MOV_B32::execute' in vt
            assert log in vt and 'Inst_VOP1__V_LOG_F32::execute' in vt
            assert 'Input and output modifiers not supported; this is an untyped operation.' in vt
            sem['v_mov_b32']={'operation':'BITWISE_MOV32','equation':'D.u = S0.u','typed_as':'UNTYPED_32_BIT','source_revision':a.vop1_revision,'source_file_sha256':sha(a.vop1_source),'source_literal':mov}
            sem['v_log_f32']={'operation':'LOG2','equation':'D = log2(S0)','source_revision':a.vop1_revision,'source_file_sha256':sha(a.vop1_source),'source_literal':log}
        if a.vop2_source is not None:
            if not a.vop2_revision:raise ValueError('--vop2-revision required with --vop2-source')
            vt=a.vop2_source.read_text(errors='replace')
            add='// D.f = S0.f + S1.f.'
            mul='// D.f = S0.f * S1.f.'
            legacy='// D.f = S0.f * S1.f (DX9 rules, 0.0*x = 0.0).'
            mac='// D.f = S0.f * S1.f + D.f.'
            vmax='// D.f = (S0.f >= S1.f ? S0.f : S1.f).'
            madak='// D.f = S0.f * S1.f + K; K is a 32-bit inline constant.'
            assert add in vt and 'Inst_VOP2__V_ADD_F32::execute' in vt
            assert mul in vt and 'Inst_VOP2__V_MUL_F32::execute' in vt
            assert legacy in vt and 'Inst_VOP2__V_MUL_LEGACY_F32::execute' in vt
            assert mac in vt and 'Inst_VOP2__V_MAC_F32::execute' in vt
            assert vmax in vt and 'Inst_VOP2__V_MAX_F32::execute' in vt
            assert madak in vt and 'Inst_VOP2__V_MADAK_F32::execute' in vt
            sem['v_add_f32']={'operation':'ADD','equation':'D = S0 + S1','source_revision':a.vop2_revision,'source_file_sha256':sha(a.vop2_source),'source_literal':add}
            sem['v_mul_f32']={'operation':'MUL','equation':'D = S0 * S1','source_revision':a.vop2_revision,'source_file_sha256':sha(a.vop2_source),'source_literal':mul}
            sem['v_mul_legacy_f32']={'operation':'LEGACY_MUL_DX9','equation':'D = legacy_mul_dx9(S0,S1)','zero_rule':'0.0*x = 0.0','source_revision':a.vop2_revision,'source_file_sha256':sha(a.vop2_source),'source_literal':legacy}
            sem['v_mac_f32']={'operation':'MAC','equation':'D_new = S0 * S1 + D_old','source_revision':a.vop2_revision,'source_file_sha256':sha(a.vop2_source),'source_literal':mac}
            sem['v_max_f32']={'operation':'MAX','equation':'D = (S0 >= S1 ? S0 : S1)','source_revision':a.vop2_revision,'source_file_sha256':sha(a.vop2_source),'source_literal':vmax}
            sem['v_madak_f32']={'operation':'MADAK','equation':'D = S0 * S1 + K','constant_kind':'32_BIT_INLINE_CONSTANT','source_revision':a.vop2_revision,'source_file_sha256':sha(a.vop2_source),'source_literal':madak}
        if a.vop3_source is not None:
            if not a.vop3_revision:raise ValueError('--vop3-revision required with --vop3-source')
            vt=a.vop3_source.read_text(errors='replace')
            mad='// D.f = S0.f * S1.f + S2.f.'
            pack='// D = {flt32_to_flt16(S1.f),flt32_to_flt16(S0.f)}, with round-toward-zero'
            intended='// This opcode is intended for use with 16-bit compressed exports.'
            assert mad in vt and 'Inst_VOP3__V_MAD_F32::execute' in vt
            assert pack in vt and intended in vt and 'Inst_VOP3__V_CVT_PKRTZ_F16_F32::execute' in vt
            sem['v_mad_f32']={'operation':'MAD','equation':'D = S0 * S1 + S2','source_revision':a.vop3_revision,'source_file_sha256':sha(a.vop3_source),'source_literal':mad}
            sem['v_cvt_pkrtz_f16_f32']={'operation':'PACK_F16_RTZ','equation':'D = {f16_rtz(S1), f16_rtz(S0)}','native_pair_order':['S1','S0'],'rounding':'TOWARD_ZERO','intended_use':'16-bit compressed exports','portable_channel_mapping':'WITHHELD','source_revision':a.vop3_revision,'source_file_sha256':sha(a.vop3_source),'source_literals':[pack,intended]}
        if a.vinterp_source is not None:
            if not a.vinterp_revision:raise ValueError('--vinterp-revision required with --vinterp-source')
            vt=a.vinterp_source.read_text(errors='replace')
            p1='// D.f = P10 * S.f + P0; parameter interpolation (SQ translates to'
            p2='// D.f = P20 * S.f + D.f; parameter interpolation (SQ translates to'
            note='// NOTE: In textual representations the I/J VGPR is the first source and'
            assert p1 in vt and 'Inst_VINTRP__V_INTERP_P1_F32::execute' in vt
            assert p2 in vt and 'Inst_VINTRP__V_INTERP_P2_F32::execute' in vt
            assert vt.count(note)>=2
            sem['v_interp_p1_f32']={'operation':'INTERP_P1','equation':'D = P10(attribute) * IJ + P0(attribute)','text_operand_order':'IJ_VGPR_FIRST_ATTRIBUTE_SECOND','coefficients':'RASTER_INTERPOLATION_CONTEXT','source_revision':a.vinterp_revision,'source_file_sha256':sha(a.vinterp_source),'source_literal':p1}
            sem['v_interp_p2_f32']={'operation':'INTERP_P2','equation':'D_new = P20(attribute) * IJ + D_old','text_operand_order':'IJ_VGPR_FIRST_ATTRIBUTE_SECOND','coefficients':'RASTER_INTERPOLATION_CONTEXT','source_revision':a.vinterp_revision,'source_file_sha256':sha(a.vinterp_source),'source_literal':p2}
        if a.sop1_source is not None:
            if not a.sop1_revision:raise ValueError('--sop1-revision required with --sop1-source')
            st=a.sop1_source.read_text(errors='replace');mov='// D.u = S0.u.'
            assert mov in st and 'Inst_SOP1__S_MOV_B32::execute' in st
            sem['s_mov_b32']={'operation':'BITWISE_MOV32','equation':'D.u = S0.u','typed_as':'UNTYPED_32_BIT','source_revision':a.sop1_revision,'source_file_sha256':sha(a.sop1_source),'source_literal':mov}
        if a.si_source is not None:
            if not a.si_revision:raise ValueError('--si-revision required with --si-source')
            st=a.si_source.read_text(errors='replace')
            # Require the LLVM selection pattern tying legacy MAC to fadd(fmul_legacy, src2).
            assert 'AMDGPUfmul_legacy (VOP3NoMods f32:$src0)' in st
            assert '(VOP3NoMods f32:$src1))' in st
            assert '(VOP3NoMods f32:$src2)))' in st
            assert 'V_MAC_LEGACY_F32_e64' in st
            sem['v_mac_legacy_f32']={'operation':'LEGACY_MAC_DX9','equation':'D_new = legacy_mul_dx9(S0,S1) + D_old','legacy_product':'AMDGPUfmul_legacy','source_revision':a.si_revision,'source_file_sha256':sha(a.si_source),'source_basis':'LLVM GCNPat selects fadd(AMDGPUfmul_legacy(src0,src1),src2) to V_MAC_LEGACY_F32'}
    except Exception as e:viol.append(repr(e))
    out={'schema_version':4,'status':'D1_GCN_VOP_SEMANTICS_SOURCE_PROVEN' if sem and not viol else 'D1_GCN_VOP_SEMANTICS_PARTIAL','semantics':sem,'violations':viol,'policy':'Only literal semantics present in immutable upstream AMDGPU source revisions are promoted. Legacy operators remain distinct; compressed f16 export values remain native ordered pairs; no Destiny visual role is inferred.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
