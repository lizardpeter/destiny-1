#!/usr/bin/env python3
"""Regenerate scalar/M0 SSA from structural IR before resource/LDS provenance.

This intentionally removes the historical per-program scalar artifact as a trust input.
The checked-in SGPR/M0 analyzer is run directly over the exact IR corpus, then the
existing fail-closed provenance join consumes those regenerated reports together with
the independently-produced exact vector-binding corpus.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from d1_gcn_sgpr_ssa_v1 import OUTPUT_STATUS as SCALAR_EXACT, analyze as analyze_scalar
from d1_gcn_resource_lds_provenance_v1 import STATUS_EXACT, GateError, analyze_corpus, parse_expect

SCHEMA = "d1_gcn_resource_lds_rebuild/v1"


def json_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.json") if p.is_file())


def regenerate_scalar(ir_dir: Path, scalar_dir: Path) -> dict:
    files = json_files(ir_dir)
    if not files:
        raise GateError(f"no structural IR JSON files under {ir_dir}")
    scalar_dir.mkdir(parents=True, exist_ok=True)
    seen_sha: set[str] = set()
    instruction_count = 0
    for src in files:
        ir = json.loads(src.read_text(encoding="utf-8"))
        if not isinstance(ir, dict):
            raise GateError(f"{src}: structural IR top level is not an object")
        out = analyze_scalar(ir)
        if out.get("status") != SCALAR_EXACT or out.get("violations"):
            raise GateError(f"{src}: regenerated scalar SSA is not exact")
        sha = out.get("program_sha256")
        if not isinstance(sha, str) or len(sha) != 64:
            raise GateError(f"{src}: regenerated scalar report lacks exact program_sha256")
        if sha in seen_sha:
            raise GateError(f"duplicate structural program identity {sha}")
        seen_sha.add(sha)
        instruction_count += int(out.get("instruction_count", 0))
        (scalar_dir / f"{sha}.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"program_count": len(seen_sha), "instruction_count": instruction_count, "program_sha256": sorted(seen_sha)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir-dir", type=Path, required=True)
    ap.add_argument("--binding-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--scalar-output-dir", type=Path)
    ap.add_argument("--expect-opcode", action="append", default=[])
    ns = ap.parse_args()
    try:
        expected = parse_expect(ns.expect_opcode)
        if ns.scalar_output_dir:
            scalar_dir = ns.scalar_output_dir
            regen = regenerate_scalar(ns.ir_dir, scalar_dir)
            report = analyze_corpus(ns.ir_dir, ns.binding_dir, scalar_dir, expected)
        else:
            with tempfile.TemporaryDirectory(prefix="d1-scalar-rebuild-") as td:
                scalar_dir = Path(td)
                regen = regenerate_scalar(ns.ir_dir, scalar_dir)
                report = analyze_corpus(ns.ir_dir, ns.binding_dir, scalar_dir, expected)
        if report.get("status") != STATUS_EXACT:
            raise GateError(f"resource/LDS provenance did not close: {report.get('status')!r}")
        wrapped = {
            "schema": SCHEMA,
            "status": "D1_GCN_RESOURCE_LDS_REBUILD_EXACT",
            "scalar_regeneration": regen,
            "resource_lds_provenance": report,
            "policy": "Scalar/M0 SSA is regenerated from structural IR with the checked-in exact analyzer; no historical scalar artifact is trusted or admitted.",
        }
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(json.dumps(wrapped, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": wrapped["status"], "scalar_regeneration": regen, "coverage": report.get("coverage")}, indent=2, sort_keys=True))
        return 0
    except (GateError, OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
