#!/usr/bin/env python3
"""Build a PS4-only census of native GCN constant-buffer API 13 usage.

Inputs are reports produced by ``d1_gcn_constant_buffer_usage_analyze.py`` plus,
optionally, the corresponding CLRX disassembly directories.  The census is
mechanical: it records exact OrbShdr ImmConstBuffer API slots and exact
``s_buffer_load_*`` immediate offsets.  It does not assign an engine semantic
name to API 13 or its dwords.

This tool exists specifically to keep cross-platform evidence secondary.  A D1
PS4 semantic is promoted only from PS4-native evidence unless another platform
is used as independent corroboration.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path


def parse_named_path(raw: str) -> tuple[str, Path]:
    if "=" not in raw:
        raise argparse.ArgumentTypeError("expected NAME=PATH")
    name, path = raw.split("=", 1)
    name = name.strip()
    if not name:
        raise argparse.ArgumentTypeError("empty corpus name")
    return name, Path(path)


def covered_offsets(load: dict) -> list[int]:
    off = load.get("static_offset")
    if off is None:
        return []
    width = int(load.get("width_dwords") or 1)
    return list(range(int(off), int(off) + width))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", action="append", required=True, type=parse_named_path,
                    help="NAME=constant-buffer-usage.json; repeatable")
    ap.add_argument("--disasm", action="append", default=[], type=parse_named_path,
                    help="NAME=disassembly-directory; repeatable")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    disasm_dirs = dict(a.disasm)
    rows = []
    slot_hist = Counter()
    api13_offset_hist = Counter()
    api13_shader_hist = Counter()
    target_hits = {6: [], 7: []}
    violations = []
    unique_shaders = set()

    for corpus, path in a.input:
        doc = json.loads(path.read_text())
        if doc.get("status") != "D1_GCN_CONSTANT_BUFFER_USAGE_ANALYZED":
            violations.append(f"{corpus}:usage_status={doc.get('status')}")
        for sh in doc.get("shaders", []):
            shader = str(sh.get("shader") or "").upper()
            if not shader:
                violations.append(f"{corpus}:row_without_shader")
                continue
            unique_shaders.add(shader)
            mapped = []
            api13 = []
            text_lines = None
            ddir = disasm_dirs.get(corpus)
            if ddir is not None:
                p = ddir / f"PS_{shader}.s"
                if p.exists():
                    text_lines = p.read_text(errors="replace").splitlines()
            for load in sh.get("loads", []):
                cb = load.get("constant_buffer")
                if not cb:
                    continue
                api = int(cb["api_slot"])
                slot_hist[str(api)] += 1
                rec = {
                    "api_slot": api,
                    "line_number": load.get("line_number"),
                    "line": load.get("line"),
                    "descriptor_start_register": load.get("descriptor_start_register"),
                    "width_dwords": int(load.get("width_dwords") or 1),
                    "static_offset": load.get("static_offset"),
                    "covered_dword_offsets": covered_offsets(load),
                }
                if text_lines is not None and load.get("line_number"):
                    ln = int(load["line_number"])
                    lo = max(0, ln - 6)
                    hi = min(len(text_lines), ln + 5)
                    rec["context"] = text_lines[lo:hi]
                mapped.append(rec)
                if api == 13:
                    api13.append(rec)
                    api13_shader_hist[shader] += 1
                    for off in rec["covered_dword_offsets"]:
                        api13_offset_hist[str(off)] += 1
                        if off in target_hits:
                            target_hits[off].append({
                                "corpus": corpus,
                                "shader": shader,
                                "load": rec,
                            })
            rows.append({
                "corpus": corpus,
                "shader": shader,
                "imm_constant_buffers": sh.get("imm_constant_buffers", []),
                "mapped_load_count": len(mapped),
                "api13_load_count": len(api13),
                "api13_loads": api13,
            })

    api13_rows = [r for r in rows if r["api13_load_count"]]
    api13_shaders = sorted({r["shader"] for r in api13_rows})
    exact_67_shaders = sorted({
        hit["shader"]
        for off in (6, 7)
        for hit in target_hits[off]
        if any(x["shader"] == hit["shader"] for x in target_hits[6])
        and any(x["shader"] == hit["shader"] for x in target_hits[7])
    })

    out = {
        "schema_version": 1,
        "status": "D1_PS4_API13_CENSUS_COMPLETE" if not violations else "D1_PS4_API13_CENSUS_PARTIAL",
        "corpora": [name for name, _ in a.input],
        "corpus_shader_row_count": len(rows),
        "unique_shader_count": len(unique_shaders),
        "constant_buffer_api_slot_load_histogram": dict(sorted(slot_hist.items(), key=lambda x: int(x[0]))),
        "api13_shader_count": len(api13_shaders),
        "api13_shaders": api13_shaders,
        "api13_dword_load_histogram": dict(sorted(api13_offset_hist.items(), key=lambda x: int(x[0]))),
        "api13_dword6_hit_count": len(target_hits[6]),
        "api13_dword7_hit_count": len(target_hits[7]),
        "api13_dword6_hits": target_hits[6],
        "api13_dword7_hits": target_hits[7],
        "api13_shaders_covering_both_6_and_7": exact_67_shaders,
        "api13_rows": api13_rows,
        "violations": violations,
        "policy": (
            "PS4-native OrbShdr InputUsageSlot plus exact CLRX scalar-buffer loads only. "
            "API13 and dwords 6/7 remain source names; no engine semantic is inferred by this census."
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in (
        "status", "corpora", "corpus_shader_row_count", "unique_shader_count",
        "api13_shader_count", "api13_dword_load_histogram", "api13_dword6_hit_count",
        "api13_dword7_hit_count", "api13_shaders_covering_both_6_and_7", "violations"
    )}, indent=2))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
