#!/usr/bin/env python3
"""Source-prove the GCN v_madmk_f32 form used by D1 shader lifting."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap=argparse.ArgumentParser();ap.add_argument('--vop2-source',type=Path,required=True);ap.add_argument('--revision',required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
    viol=[];sem={}
    try:
        t=a.vop2_source.read_text(errors='replace')
        literal='// D.f = S0.f * K + S1.f; K is a 32-bit inline constant.'
        nomod='// This opcode cannot use the VOP3 encoding and cannot use input/output'
        assert 'Inst_VOP2__V_MADMK_F32::execute' in t
        assert literal in t
        assert nomod in t
        sem={
            'opcode':'v_madmk_f32',
            'operation':'MADMK',
            'equation':'D = S0 * K + S1',
            'constant_kind':'32_BIT_INLINE_CONSTANT',
            'input_output_modifiers':'NOT_SUPPORTED_BY_NATIVE_OPCODE',
            'source_revision':a.revision,
            'source_file_sha256':sha(a.vop2_source),
            'source_literals':[literal,nomod],
        }
    except Exception as exc:viol.append(repr(exc))
    out={'schema_version':1,'status':'D1_GCN_MADMK_SEMANTICS_SOURCE_PROVEN' if sem and not viol else 'D1_GCN_MADMK_SEMANTICS_PARTIAL','semantics':sem,'violations':viol,'policy':'Only literal v_madmk_f32 semantics from the immutable upstream AMDGPU implementation are promoted; no Destiny visual role is inferred.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 0 if not viol else 2

if __name__=='__main__':raise SystemExit(main())
