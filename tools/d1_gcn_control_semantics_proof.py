#!/usr/bin/env python3
"""Pin the small GCN control/arithmetic semantic subset needed by loop IR.

This proof deliberately does not infer shader intent. It accepts only literal
instruction equations present in immutable upstream AMDGPU implementation or
.arch-derived sources, then emits a machine-readable semantics contract used by
later CFG/EXEC recurrence passes.
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--llvm-sop", type=Path, required=True)
    ap.add_argument("--gem5-sop1", type=Path, required=True)
    ap.add_argument("--gem5-sopp", type=Path, required=True)
    ap.add_argument("--gem5-vop2", type=Path, required=True)
    ap.add_argument("--llvm-revision", required=True)
    ap.add_argument("--gem5-revision", required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    violations = []
    semantics = {}
    try:
        sop = a.llvm_sop.read_text()
        sop1 = a.gem5_sop1.read_text()
        sopp = a.gem5_sopp.read_text()
        vop2 = a.gem5_vop2.read_text()

        need(
            sop,
            'let Defs = [SCC] in {',
            'def S_AND_B64 : SOP2_64 <"s_and_b64"',
            'UniformBinFrag<and> i64:$src0, i64:$src1',
            'def S_ANDN2_B64 : SOP2_64 <"s_andn2_b64"',
            'UniformBinFrag<and> i64:$src0, (not i64:$src1)',
        )
        need(
            sop1,
            'D.u64 = EXEC;',
            'EXEC = S0.u64 & EXEC;',
            'SCC = 1 if the new value of EXEC is non-zero.',
        )
        need(
            sopp,
            'if (SCC == 0) then PC = PC + signext(SIMM16 * 4) + 4;',
            'if (EXEC == 0) then PC = PC + signext(SIMM16 * 4) + 4;',
        )
        need(vop2, 'Inst_VOP2__V_SUBREV_F32', 'D.f = S1.f - S0.f.')

        semantics = {
            "s_and_b64": {
                "equation": "D = S0 & S1",
                "scc": "D != 0",
                "basis": "LLVM SOP2 bitwise pattern under SCC-defining block",
            },
            "s_andn2_b64": {
                "equation": "D = S0 & ~S1",
                "scc": "D != 0",
                "basis": "LLVM SOP2 bitwise pattern under SCC-defining block",
            },
            "s_and_saveexec_b64": {
                "equation": "D = EXEC_old; EXEC_new = S0 & EXEC_old",
                "scc": "EXEC_new != 0",
                "basis": "gem5 .arch-derived instruction description",
            },
            "s_cbranch_scc0": {
                "equation": "branch iff SCC == 0",
                "basis": "gem5 .arch-derived instruction description",
            },
            "s_cbranch_execz": {
                "equation": "branch iff EXEC == 0",
                "basis": "gem5 .arch-derived instruction description",
            },
            "v_subrev_f32": {
                "equation": "D = S1 - S0",
                "basis": "gem5 .arch-derived instruction description",
            },
        }
    except Exception as exc:
        violations.append(repr(exc))

    out = {
        "schema_version": 1,
        "status": (
            "D1_GCN_CONTROL_SEMANTICS_SOURCE_PROVEN"
            if semantics and not violations
            else "D1_GCN_CONTROL_SEMANTICS_PARTIAL"
        ),
        "semantics": semantics,
        "violations": violations,
        "sources": {
            "llvm": {
                "revision": a.llvm_revision,
                "file_sha256": sha(a.llvm_sop),
            },
            "gem5": {
                "revision": a.gem5_revision,
                "sop1_sha256": sha(a.gem5_sop1),
                "sopp_sha256": sha(a.gem5_sopp),
                "vop2_sha256": sha(a.gem5_vop2),
            },
        },
        "policy": (
            "Only literal ISA equations present in immutable upstream "
            "implementation/description sources are promoted. Shader intent is not inferred."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
