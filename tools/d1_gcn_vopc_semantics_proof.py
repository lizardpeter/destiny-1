#!/usr/bin/env python3
"""Pin the VOPC compare semantics needed by D1 GCN control reconstruction.

This proof is intentionally tiny. It promotes only an upstream .arch-derived
equation from an immutable gem5 revision and does not infer shader intent.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def need(text: str, *parts: str) -> None:
    for part in parts:
        if part not in text:
            raise ValueError(f"missing immutable source literal: {part!r}")

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--gem5-vopc", type=Path, required=True)
    ap.add_argument("--gem5-revision", required=True)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args()
    violations=[]; semantics={}
    try:
        t=a.gem5_vopc.read_text()
        need(
            t,
            "Inst_VOPC__V_CMP_GT_F32::execute",
            "// D.u64[threadID] = (S0 > S1); D = VCC in VOPC encoding.",
            "ConstVecOperandF32 src0(gpuDynInst, instData.SRC0);",
            "ConstVecOperandF32 src1(gpuDynInst, instData.VSRC1);",
        )
        semantics["v_cmp_gt_f32"]={
            "equation":"D = (S0 > S1)",
            "destination":"VCC in VOPC encoding",
            "operand_order":["S0","S1"],
            "basis":"gem5 immutable .arch-derived VOPC description",
        }
    except Exception as exc:
        violations.append(repr(exc))
    out={
        "schema_version":1,
        "status":"D1_GCN_VOPC_SEMANTICS_SOURCE_PROVEN" if semantics and not violations else "D1_GCN_VOPC_SEMANTICS_PARTIAL",
        "semantics":semantics,
        "violations":violations,
        "source":{"revision":a.gem5_revision,"file_sha256":sha(a.gem5_vopc)},
        "policy":"Only literal VOPC operand-order semantics present in the immutable upstream source are promoted. Shader intent is not inferred.",
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
    return 0 if not violations else 2

if __name__=="__main__":
    raise SystemExit(main())
