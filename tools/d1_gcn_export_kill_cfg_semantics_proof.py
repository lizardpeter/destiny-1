#!/usr/bin/env python3
"""Pin the GCN semantics needed by CFG-aware persistent export-kill decoding.

This is a supplemental source contract. The existing control-semantics proof already
closes s_andn2_b64, s_and_b64, s_cbranch_scc0 and v_subrev_f32. This file pins the
remaining comparison, whole-quad and scalar-move behavior from one immutable gem5
revision so later shader-specific CFG analysis does not infer those operations from
mnemonics or visual behavior.
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
    ap.add_argument("--gem5-vopc", type=Path, required=True)
    ap.add_argument("--gem5-sop1", type=Path, required=True)
    ap.add_argument("--gem5-revision", required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    violations = []
    semantics = {}
    try:
        vopc = a.gem5_vopc.read_text()
        sop1 = a.gem5_sop1.read_text()

        need(
            vopc,
            "Inst_VOPC__V_CMP_GT_F32",
            "D.u64[threadID] = (S0 > S1); D = VCC in VOPC encoding.",
        )
        need(
            sop1,
            "Inst_SOP1__S_MOV_B64",
            "D.u64 = S0.u64.",
            "Inst_SOP1__S_WQM_B64",
            "D[i] = (S0[(i & ~3):(i | 3)] != 0);",
            "Computes whole quad mode for an active/valid mask.",
            "SCC = 1 if result is non-zero.",
        )

        semantics = {
            "v_cmp_gt_f32": {
                "equation": "VCC[lane] = (S0 > S1) for active lanes",
                "basis": "gem5 .arch-derived VOPC implementation/description",
            },
            "s_mov_b64": {
                "equation": "D = S0",
                "basis": "gem5 .arch-derived SOP1 implementation/description",
            },
            "s_wqm_b64": {
                "equation": "D = wholeQuadMode(S0)",
                "lane_equation": "D[i] = (S0[(i & ~3):(i | 3)] != 0)",
                "scc": "D != 0",
                "basis": "gem5 .arch-derived SOP1 implementation/description",
            },
        }
    except Exception as exc:
        violations.append(repr(exc))

    out = {
        "schema_version": 1,
        "status": (
            "D1_GCN_EXPORT_KILL_CFG_SEMANTICS_SOURCE_PROVEN"
            if semantics and not violations
            else "D1_GCN_EXPORT_KILL_CFG_SEMANTICS_PARTIAL"
        ),
        "semantics": semantics,
        "violations": violations,
        "sources": {
            "gem5": {
                "revision": a.gem5_revision,
                "vopc_sha256": sha(a.gem5_vopc),
                "sop1_sha256": sha(a.gem5_sop1),
            }
        },
        "policy": (
            "Only literal ISA behavior present in immutable upstream gem5 AMDGPU "
            "implementation/description sources is promoted. Shader intent and "
            "render-target meaning remain outside this contract."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
