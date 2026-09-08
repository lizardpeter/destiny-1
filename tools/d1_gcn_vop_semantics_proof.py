#!/usr/bin/env python3
"""Promote a pinned subset of AMDGPU value/export semantics used by D1 shader lifting.

Inputs are fetched from immutable source revisions by workflows. Only literal source
semantics are promoted; no Destiny material meaning or portable channel assignment is
inferred. The terminal-export additions deliberately preserve compressed f16 values as
native ordered pairs until an independent source closes the EXP channel unpacking.
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
    ap.add_argument('--vop2-source',type=Path)
    ap.add_argument('--vop2-revision')
    ap.add_argument('--vop3-source',type=Path)
    ap.add_argument('--vop3-revision')
    ap.add_argument('--vinterp-source',type=Path)
    ap.add_argument('--vinterp-revision')
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args();viol=[];sem={}
    try:
        it=a.instr_info.read_text(errors='replace');mt=a.modifier_syntax.read_text(errors='replace')
        exp='// v_exp_f32, which is exp2, no denormal handling for f32.'
        rcp='// out = 1.0 / a'
        assert exp in it,exp
        assert rcp in it,rcp
        assert 'def AMDGPUrcp_impl : SDNode<"AMDGPUISD::RCP", SDTFPUnaryOp>;' in it
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
          'float_clamp':{'operation':'CLAMP_0_1','equation':'D = clamp(D, 0.0, 1.0)','application_order':'after output modifiers','source_revision':a.modifier_revision,'source_file_sha256':sha(a.modifier_syntax)},
          'exp_compr':{'operation':'COMPRESSED_EXPORT_FLAG','equation':'EXP.compr means exported data is compressed','channel_mapping':'WITHHELD_NOT_STATED_BY_THIS_SOURCE','source_revision':a.modifier_revision,'source_file_sha256':sha(a.modifier_syntax)},
          'exp_done':{'operation':'LAST_EXPORT_FLAG','equation':'EXP.done marks the last export operation','source_revision':a.modifier_revision,'source_file_sha256':sha(a.modifier_syntax)},
          'exp_vm':{'operation':'VALID_EXEC_MASK_FLAG','equation':'EXP.vm marks the EXEC mask valid for the export','source_revision':a.modifier_revision,'source_file_sha256':sha(a.modifier_syntax)},
        }
        if a.vop2_source is not None:
            if not a.vop2_revision:raise ValueError('--vop2-revision required with --vop2-source')
            vt=a.vop2_source.read_text(errors='replace')
            mac='// D.f = S0.f * S1.f + D.f.'
            vmax='// D.f = (S0.f >= S1.f ? S0.f : S1.f).'
            assert mac in vt and 'Inst_VOP2__V_MAC_F32::execute' in vt
            assert vmax in vt and 'Inst_VOP2__V_MAX_F32::execute' in vt
            sem['v_mac_f32']={'operation':'MAC','equation':'D_new = S0 * S1 + D_old','source_revision':a.vop2_revision,'source_file_sha256':sha(a.vop2_source),'source_literal':mac}
            sem['v_max_f32']={'operation':'MAX','equation':'D = (S0 >= S1 ? S0 : S1)','source_revision':a.vop2_revision,'source_file_sha256':sha(a.vop2_source),'source_literal':vmax}
        if a.vop3_source is not None:
            if not a.vop3_revision:raise ValueError('--vop3-revision required with --vop3-source')
            vt=a.vop3_source.read_text(errors='replace')
            mad='// D.f = S0.f * S1.f + S2.f.'
            pack='// D = {flt32_to_flt16(S1.f),flt32_to_flt16(S0.f)}, with round-toward-zero'
            intended='// This opcode is intended for use with 16-bit compressed exports.'
            assert mad in vt and 'Inst_VOP3__V_MAD_F32::execute' in vt
            assert pack in vt and intended in vt and 'Inst_VOP3__V_CVT_PKRTZ_F16_F32::execute' in vt
            sem['v_mad_f32']={'operation':'MAD','equation':'D = S0 * S1 + S2','source_revision':a.vop3_revision,'source_file_sha256':sha(a.vop3_source),'source_literal':mad}
            sem['v_cvt_pkrtz_f16_f32']={
                'operation':'PACK_F16_RTZ','equation':'D = {f16_rtz(S1), f16_rtz(S0)}',
                'native_pair_order':['S1','S0'],'rounding':'TOWARD_ZERO',
                'intended_use':'16-bit compressed exports','portable_channel_mapping':'WITHHELD',
                'source_revision':a.vop3_revision,'source_file_sha256':sha(a.vop3_source),
                'source_literals':[pack,intended]
            }
        if a.vinterp_source is not None:
            if not a.vinterp_revision:raise ValueError('--vinterp-revision required with --vinterp-source')
            vt=a.vinterp_source.read_text(errors='replace')
            p1='// D.f = P10 * S.f + P0; parameter interpolation (SQ translates to'
            p2='// D.f = P20 * S.f + D.f; parameter interpolation (SQ translates to'
            note='// NOTE: In textual representations the I/J VGPR is the first source and'
            assert p1 in vt and 'Inst_VINTRP__V_INTERP_P1_F32::execute' in vt
            assert p2 in vt and 'Inst_VINTRP__V_INTERP_P2_F32::execute' in vt
            assert vt.count(note)>=2
            sem['v_interp_p1_f32']={
                'operation':'INTERP_P1','equation':'D = P10(attribute) * IJ + P0(attribute)',
                'text_operand_order':'IJ_VGPR_FIRST_ATTRIBUTE_SECOND','coefficients':'RASTER_INTERPOLATION_CONTEXT',
                'source_revision':a.vinterp_revision,'source_file_sha256':sha(a.vinterp_source),'source_literal':p1
            }
            sem['v_interp_p2_f32']={
                'operation':'INTERP_P2','equation':'D_new = P20(attribute) * IJ + D_old',
                'text_operand_order':'IJ_VGPR_FIRST_ATTRIBUTE_SECOND','coefficients':'RASTER_INTERPOLATION_CONTEXT',
                'source_revision':a.vinterp_revision,'source_file_sha256':sha(a.vinterp_source),'source_literal':p2
            }
    except Exception as e:viol.append(repr(e))
    out={'schema_version':3,'status':'D1_GCN_VOP_SEMANTICS_SOURCE_PROVEN' if sem and not viol else 'D1_GCN_VOP_SEMANTICS_PARTIAL','semantics':sem,'violations':viol,
         'policy':'Only literal semantics present in immutable upstream AMDGPU source revisions are promoted. Compressed f16 export values remain native ordered pairs; RGBA/channel unpacking is withheld unless independently source-proven.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
