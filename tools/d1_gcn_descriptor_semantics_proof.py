#!/usr/bin/env python3
"""Source-pin the GFX7 descriptor/load semantics used by the D1 PS4 shader decoder.

This deliberately separates GFX7/Sea-Islands SMRD behavior from later SMEM/Vega
behavior.  D1 PS4 shaders in this pipeline are disassembled as GFX700.  The proof
accepts only literal LLVM source contracts for:

* dword-scaled SMRD immediate offsets;
* the pre-GFX12.5 16-user-SGPR limit;
* scalar x4/x8 load widths;
* MIMG 256-bit resource and 128-bit sampler descriptor widths.

No D1 texture role or shader intent is inferred here.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def need(text: str, *parts: str) -> None:
    for part in parts:
        if part not in text:
            raise ValueError(f"missing pinned source literal: {part!r}")


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--base-info-h',type=Path,required=True)
    ap.add_argument('--base-info-cpp',type=Path,required=True)
    ap.add_argument('--sm-instructions',type=Path,required=True)
    ap.add_argument('--mimg-instructions',type=Path,required=True)
    ap.add_argument('--llvm-revision',required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    violations=[]; proof={}
    try:
        h=a.base_info_h.read_text(); cpp=a.base_info_cpp.read_text()
        sm=a.sm_instructions.read_text(); mimg=a.mimg_instructions.read_text()

        # LLVM names the conversion explicitly and implements it as >>2 after
        # dword-alignment validation for generations using dword SMRD offsets.
        need(h,
             'Convert \\p ByteOffset to dwords if the subtarget uses dword SMRD immediate',
             'getSMRDEncodedOffset')
        need(cpp,
             'assert(isDwordAligned(ByteOffset));',
             'return ByteOffset >> 2;',
             'std::optional<int64_t> getSMRDEncodedOffset')

        # GFX7 is well below GFX12.5, so this closes the resident user-data
        # register count used to interpret PtrExtendedUserData spill offsets.
        m=re.search(r'unsigned getMaxNumUserSGPRs\(const MCSubtargetInfo &STI\) \{\s*'
                    r'if \(isGFX1250Plus\(STI\)\)\s*return 32;\s*return 16;\s*\}',cpp)
        if not m:
            raise ValueError('pinned getMaxNumUserSGPRs 32/16 contract not found')

        need(sm,
             'def smrd_offset_8 : ImmOperand<i32, "SMRDOffset8", 1>;',
             'defm S_LOAD_DWORDX4  : SM_Pseudo_Loads <SReg_64, SReg_128>;',
             'defm S_LOAD_DWORDX8  : SM_Pseudo_Loads <SReg_64, SReg_256>;')
        need(mimg,
             '(ins SReg_256_XNULL:$srsrc, SReg_128_XNULL:$ssamp,')

        proof={
          'architecture':'GFX7_GFX700',
          'smrd_immediate_offset_unit':'DWORD',
          'smrd_immediate_byte_scale':4,
          'resident_user_sgpr_count':16,
          'extended_user_data_logical_base_dword':16,
          'scalar_load_widths_dwords':{
             's_load_dwordx4':4,
             's_load_dwordx8':8,
          },
          'mimg_descriptor_widths_dwords':{
             'resource':8,
             'sampler':4,
          },
          'equations':{
             'smrd_encoded_immediate':'encoded_dword_offset = byte_offset >> 2',
             'extended_user_data':'logical_user_dword = 16 + immediate_dword_offset',
          },
          'semantic_boundary':{
             'resource_table_entry_stride':'8 DWORDS WHEN USED AS MIMG RESOURCE DESCRIPTOR',
             'extended_user_data_role':'LOGICAL_USER_DATA_SPILL_RECONSTRUCTION',
             'texture_or_sampler_visual_role':'WITHHELD',
          }
        }
    except Exception as exc:
        violations.append(repr(exc))

    out={
      'schema_version':1,
      'status':'D1_GFX7_DESCRIPTOR_SEMANTICS_SOURCE_PROVEN' if proof and not violations else 'D1_GFX7_DESCRIPTOR_SEMANTICS_PARTIAL',
      'proof':proof,
      'violations':violations,
      'sources':{
        'llvm_revision':a.llvm_revision,
        'base_info_h_sha256':sha(a.base_info_h),
        'base_info_cpp_sha256':sha(a.base_info_cpp),
        'sm_instructions_sha256':sha(a.sm_instructions),
        'mimg_instructions_sha256':sha(a.mimg_instructions),
      },
      'policy':'Only pinned GFX7-compatible scalar-memory/user-SGPR and MIMG descriptor-width semantics are promoted. Later-generation SMEM byte-offset rules are not substituted for GFX7 SMRD.'
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'proof':proof,'violations':violations},indent=2))
    return 0 if not violations else 2


if __name__=='__main__':
    raise SystemExit(main())
