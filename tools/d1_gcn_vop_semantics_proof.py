#!/usr/bin/env python3
"""Promote a tiny pinned subset of AMDGPU VOP semantics used by D1 shader lifting.

The input files must be fetched from immutable source revisions by the workflow.
This probe deliberately promotes only semantics whose exact source text is present:
  * V_EXP_F32 is base-2 exponentiation (exp2);
  * floating-point `clamp` limits the result to [0,1].

This is an ISA semantics source proof, not a Destiny material interpretation.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--instr-info',type=Path,required=True);ap.add_argument('--modifier-syntax',type=Path,required=True);ap.add_argument('--instr-revision',required=True);ap.add_argument('--modifier-revision',required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args();viol=[];sem={}
    try:
        it=a.instr_info.read_text(errors='replace');mt=a.modifier_syntax.read_text(errors='replace')
        needle='// v_exp_f32, which is exp2, no denormal handling for f32.'
        assert needle in it,needle
        assert 'For floating-point operations, clamp modifier indicates that the result must be clamped' in mt
        assert 'to the range [0.0, 1.0]. By default, there is no clamping.' in mt
        assert 'clamp modifier is applied after' in mt
        sem={
          'v_exp_f32':{'operation':'EXP2','equation':'D = pow(2.0, S0)','denormal_note':'source states no denormal handling for f32',
                       'source_revision':a.instr_revision,'source_file_sha256':sha(a.instr_info),'source_literal':needle},
          'float_clamp':{'operation':'CLAMP_0_1','equation':'D = clamp(D, 0.0, 1.0)','application_order':'after output modifiers',
                         'source_revision':a.modifier_revision,'source_file_sha256':sha(a.modifier_syntax)}
        }
    except Exception as e:viol.append(repr(e))
    out={'schema_version':1,'status':'D1_GCN_VOP_SEMANTICS_SOURCE_PROVEN' if sem and not viol else 'D1_GCN_VOP_SEMANTICS_PARTIAL','semantics':sem,'violations':viol,
         'policy':'Only literal semantics present in immutable upstream AMDGPU source revisions are promoted. No Destiny shader role is inferred.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
