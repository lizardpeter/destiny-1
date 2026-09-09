#!/usr/bin/env python3
"""Fail-closed corpus census for Destiny 1 native GCN shader programs.

This adapter intentionally sits *above* the generic structural parser.  It does
not infer material intent or shader-stage meaning.  Its job is accounting:

* preserve every input reference and its package/tag/stage provenance;
* deduplicate only exact native program binaries (SHA-256);
* run every unique program through ``d1_gcn_cfg_ir_v2.py``;
* require one structural parse result per unique program;
* stop on any parser error, malformed record, or accounting mismatch; and
* emit a deterministic corpus ledger suitable for later opcode/feature census.

The input is newline-delimited JSON (JSONL).  Each non-empty line must contain:

    {
      "package": "...",
      "tag": "808EE505",
      "stage": "PixelShader",
      "code_path": "/path/to/native.bin"
    }

Additional keys are preserved under ``source_metadata``.  ``code_path`` may be
relative to the JSONL file.  The structural parser must accept ``--code`` and
``--out``; this script treats any non-zero parser exit or missing/invalid JSON
output as a hard failure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REQUIRED_SOURCE_KEYS = ("package", "tag", "stage", "code_path")
STATUS = "D1_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE"


def _die(message: str) -> "NoReturn":
    raise SystemExit(f"ERROR: {message}")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _load_sources(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    base = path.parent
    with path.open("r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                _die(f"{path}:{lineno}: invalid JSON: {exc}")
            if not isinstance(row, dict):
                _die(f"{path}:{lineno}: row is not a JSON object")
            missing = [k for k in REQUIRED_SOURCE_KEYS if k not in row]
            if missing:
                _die(f"{path}:{lineno}: missing required keys {missing}")
            for key in ("package", "tag", "stage", "code_path"):
                if not isinstance(row[key], str) or not row[key]:
                    _die(f"{path}:{lineno}: {key} must be a non-empty string")
            code_path = Path(row["code_path"])
            if not code_path.is_absolute():
                code_path = (base / code_path).resolve()
            if not code_path.is_file():
                _die(f"{path}:{lineno}: code_path does not exist: {code_path}")
            code = code_path.read_bytes()
            if not code:
                _die(f"{path}:{lineno}: native program is empty: {code_path}")
            source_metadata = {k: v for k, v in row.items() if k not in REQUIRED_SOURCE_KEYS}
            rows.append(
                {
                    "source_index": len(rows),
                    "package": row["package"],
                    "tag": row["tag"],
                    "stage": row["stage"],
                    "code_path": str(code_path),
                    "code_size": len(code),
                    "code_sha256": _sha256(code),
                    "source_metadata": source_metadata,
                }
            )
    if not rows:
        _die(f"{path}: no source rows")
    return rows


def _run_parser(parser: Path, code_path: Path, out_path: Path) -> dict[str, Any]:
    cmd = [sys.executable, str(parser), "--code", str(code_path), "--out", str(out_path)]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        _die(f"structural parser failed for {code_path} with exit {proc.returncode}")
    if not out_path.is_file():
        _die(f"structural parser produced no output for {code_path}")
    try:
        ir = json.loads(out_path.read_text(encoding="utf-8"))
    except Exception as exc:
        _die(f"invalid structural parser JSON for {code_path}: {exc}")
    if not isinstance(ir, dict):
        _die(f"structural parser output is not an object for {code_path}")
    return ir


def _instruction_rows(ir: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("instructions", "program", "ops"):
        value = ir.get(key)
        if isinstance(value, list) and all(isinstance(x, dict) for x in value):
            return value
    _die("structural IR has no recognized instruction array (instructions/program/ops)")


def _opcode_of(inst: dict[str, Any]) -> str:
    for key in ("opcode", "op", "mnemonic"):
        value = inst.get(key)
        if isinstance(value, str) and value:
            return value
    _die(f"structural instruction lacks opcode/mnemonic: {inst!r}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True, type=Path, help="JSONL source manifest")
    ap.add_argument("--parser", default=Path(__file__).with_name("d1_gcn_cfg_ir_v2.py"), type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    sources_path = args.sources.resolve()
    parser = args.parser.resolve()
    if not sources_path.is_file():
        _die(f"source manifest not found: {sources_path}")
    if not parser.is_file():
        _die(f"structural parser not found: {parser}")

    sources = _load_sources(sources_path)
    by_sha: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in sources:
        by_sha[row["code_sha256"]].append(row)

    unique_programs: list[dict[str, Any]] = []
    global_opcodes: Counter[str] = Counter()
    global_stages: Counter[str] = Counter(row["stage"] for row in sources)

    with tempfile.TemporaryDirectory(prefix="d1_shader_census_") as tmp:
        tmpdir = Path(tmp)
        for ordinal, sha in enumerate(sorted(by_sha)):
            refs = by_sha[sha]
            representative = refs[0]
            code_path = Path(representative["code_path"])
            for ref in refs[1:]:
                other = Path(ref["code_path"]).read_bytes()
                if _sha256(other) != sha:
                    _die(f"source changed during census: {ref['code_path']}")
            ir_path = tmpdir / f"{ordinal:06d}_{sha}.json"
            ir = _run_parser(parser, code_path, ir_path)
            instructions = _instruction_rows(ir)
            opcodes = Counter(_opcode_of(inst) for inst in instructions)
            global_opcodes.update(opcodes)

            unique_programs.append(
                {
                    "code_sha256": sha,
                    "code_size": representative["code_size"],
                    "reference_count": len(refs),
                    "references": [
                        {
                            "source_index": r["source_index"],
                            "package": r["package"],
                            "tag": r["tag"],
                            "stage": r["stage"],
                            "code_path": r["code_path"],
                            "source_metadata": r["source_metadata"],
                        }
                        for r in refs
                    ],
                    "instruction_count": len(instructions),
                    "opcode_counts": dict(sorted(opcodes.items())),
                    "structural_ir_sha256": _sha256(_canonical_json_bytes(ir)),
                }
            )

    if sum(p["reference_count"] for p in unique_programs) != len(sources):
        _die("deduplication accounting mismatch")
    if len({p["code_sha256"] for p in unique_programs}) != len(unique_programs):
        _die("duplicate exact code SHA survived unique-program accounting")

    output = {
        "status": STATUS,
        "source_manifest": str(sources_path),
        "source_manifest_sha256": _sha256(sources_path.read_bytes()),
        "parser": str(parser),
        "parser_sha256": _sha256(parser.read_bytes()),
        "source_reference_count": len(sources),
        "unique_program_count": len(unique_programs),
        "duplicate_reference_count": len(sources) - len(unique_programs),
        "stage_reference_counts": dict(sorted(global_stages.items())),
        "opcode_instruction_counts": dict(sorted(global_opcodes.items())),
        "unique_programs": unique_programs,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(_canonical_json_bytes(output))
    print(json.dumps({k: output[k] for k in ("status", "source_reference_count", "unique_program_count", "duplicate_reference_count")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
