#!/usr/bin/env python3
"""GCN (gfx7 / PS4 Liverpool) instruction census of D1 shader binaries vs. shadPS4.

Input is a directory of native shader payloads (the FileEntry resources that end
in an `OrbShdr` ShaderBinaryInfo footer, e.g. as written by
`tools/d1_remote_ps4_shader_extract.py`). For each payload the code is bounded by
the footer's code length and decoded linearly. Every opcode is named with the
section enums in shadPS4's `src/shader_recompiler/frontend/opcodes.h`, so names
match the emulator exactly.

Coverage is read from the same checkout:

  * translated  — the opcode is a `case Opcode::X:` label in
                  `frontend/translate/*.cpp`, or S_SWAPPC_B64 (fetch-shader call),
                  or its format category is DebugProfile (ignored by design);
  * missing     — anything else. shadPS4 logs "Unknown opcode" and marks the
                  shader's translation as failed.

Decoding is self-checking: a shader is `clean` when decoding consumes exactly the
code length, hits no unknown encoding and ends in S_ENDPGM.

    python tools/eboot/d1_gcn_isa_census.py --shaders DIR --shadps4 /path/shadPS4 \
        --out evidence/generated/d1_gcn_isa_census.json

No shader bytes are written to the output, only opcode statistics and hashes.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from d1_ps4_shader_binary_probe import find_footer, parse_binary_info  # noqa: E402

SECTIONS = ["SOP2", "SOPK", "SOP1", "SOPC", "SOPP", "SMRD", "VOP2", "VOP3", "VOP1", "VOPC",
            "VINTRP", "DS", "MUBUF", "MTBUF", "MIMG", "EXP"]


def load_enums(opcodes_h: str) -> dict[str, dict[int, str]]:
    out = {}
    for sec in SECTIONS:
        m = re.search(r"enum class Opcode" + sec + r"\s*:\s*u32\s*\{(.*?)\};", opcodes_h, re.S)
        names = {}
        for name, val in re.findall(r"^\s*([A-Z0-9_]+)\s*=\s*(0x[0-9A-Fa-f]+|\d+)\s*,", m.group(1), re.M):
            if name.startswith("OP_RANGE"):
                continue
            names.setdefault(int(val, 0), []).append(name)  # keep aliases (e.g. V_CMP_LG_I32 / V_CMP_NE_I32)
        out[sec] = names
    return out


def load_translated(shad: Path) -> set[str]:
    done = {"S_SWAPPC_B64", "EXP"}  # EXP is handled by EmitExport for the whole category
    for p in (shad / "src/shader_recompiler/frontend/translate").glob("*.cpp"):
        done |= set(re.findall(r"case\s+Opcode::([A-Z0-9_]+)\s*:", p.read_text(errors="ignore")))
    fmt = (shad / "src/shader_recompiler/frontend/format.cpp").read_text(errors="ignore")
    # table rows are preceded by a "// N = NAME" comment; DebugProfile rows are ignored by design
    done |= set(re.findall(r"//\s*\d+\s*=\s*([A-Z0-9_]+)\s*\n\s*\{[^}]*InstCategory::DebugProfile", fmt))
    return done


def decode(code: bytes, enums) -> tuple[list[tuple[str, str]], list[str]]:
    """Return [(section, name)] and problems."""
    out, problems, i, n = [], [], 0, len(code)
    u32 = lambda o: struct.unpack_from("<I", code, o)[0]
    while i + 4 <= n:
        w = u32(i)
        size, sec, op, lit = 4, None, None, False
        if (w >> 23) == 0x17D:
            sec, op = "SOP1", (w >> 8) & 0xFF; lit = (w & 0xFF) == 0xFF
        elif (w >> 23) == 0x17F:
            sec, op = "SOPP", (w >> 16) & 0x7F
        elif (w >> 23) == 0x17E:
            sec, op = "SOPC", (w >> 16) & 0x7F; lit = (w & 0xFF) == 0xFF or ((w >> 8) & 0xFF) == 0xFF
        elif (w >> 25) == 0x3F:
            sec, op = "VOP1", (w >> 9) & 0xFF; lit = (w & 0x1FF) == 0xFF
        elif (w >> 25) == 0x3E:
            sec, op = "VOPC", (w >> 17) & 0xFF; lit = (w & 0x1FF) == 0xFF
        elif (w >> 26) == 0x34:
            sec, op, size = "VOP3", (w >> 17) & 0x1FF, 8
        elif (w >> 26) == 0x3E:
            sec, op, size = "EXP", 0, 8
        elif (w >> 26) == 0x32:
            sec, op = "VINTRP", (w >> 16) & 0x3
        elif (w >> 26) == 0x36:
            sec, op, size = "DS", (w >> 18) & 0xFF, 8
        elif (w >> 26) == 0x38:
            sec, op, size = "MUBUF", (w >> 18) & 0x7F, 8
        elif (w >> 26) == 0x3A:
            sec, op, size = "MTBUF", (w >> 16) & 0x7, 8
        elif (w >> 26) == 0x3C:
            sec, op, size = "MIMG", (w >> 18) & 0x7F, 8
        elif (w >> 27) == 0x18:
            sec, op = "SMRD", (w >> 22) & 0x1F; lit = not (w >> 8) & 1 and (w & 0xFF) == 0xFF
        elif (w >> 28) == 0xB:
            sec, op = "SOPK", (w >> 23) & 0x1F; lit = op == 21  # S_SETREG_IMM32_B32
        elif (w >> 30) == 0x2:
            sec, op = "SOP2", (w >> 23) & 0x7F; lit = (w & 0xFF) == 0xFF or ((w >> 8) & 0xFF) == 0xFF
        elif (w >> 31) == 0:
            sec, op = "VOP2", (w >> 25) & 0x3F; lit = (w & 0x1FF) == 0xFF or op in (32, 33)  # V_MADMK/MADAK
        else:
            problems.append(f"unknown encoding {w:08X} @ {i:#x}")
            break
        size += 4 if lit else 0
        aliases = ["EXP"] if sec == "EXP" else enums[sec].get(op)
        name = "/".join(aliases) if aliases else None
        if name is None:
            problems.append(f"unnamed {sec} op {op} @ {i:#x}")
            name = f"{sec}_OP_{op}"
        out.append((sec, name))
        i += size
    if i != n:
        problems.append(f"decode ended at {i:#x} of {n:#x}")
    if not out or out[-1][1] != "S_ENDPGM":
        # trailing padding after S_ENDPGM is tolerated if S_ENDPGM was seen
        if not any(x[1] == "S_ENDPGM" for x in out):
            problems.append("no S_ENDPGM")
    return out, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shaders", type=Path, required=True)
    ap.add_argument("--shadps4", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    opcodes_h = (a.shadps4 / "src/shader_recompiler/frontend/opcodes.h").read_text(errors="ignore")
    enums = load_enums(opcodes_h)
    translated = load_translated(a.shadps4)

    is_translated = lambda n: any(x in translated for x in n.split("/"))
    uses = collections.Counter()           # opcode -> instruction count
    encodings = collections.defaultdict(collections.Counter)  # opcode -> encoding -> count
    shaders_using = collections.Counter()  # opcode -> shader count
    stage_counts = collections.Counter()
    per_shader, problems, seen = [], {}, set()
    for p in sorted(a.shaders.iterdir()):
        payload = p.read_bytes()
        h = hashlib.sha256(payload).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        footer, _ = find_footer(payload)
        if footer is None:
            continue
        info = parse_binary_info(payload, footer)
        code = payload[:info["code_length_bytes"]]
        insts, probs = decode(code, enums)
        stage_counts[info["stage"]] += 1
        names = [n for _, n in insts]
        for s_, n in insts:
            encodings[n][s_] += 1
        for n in names:
            uses[n] += 1
        for n in set(names):
            shaders_using[n] += 1
        miss = sorted({n for n in names if not is_translated(n)})
        per_shader.append({"file": p.name, "sha256": h, "stage": info["stage"], "instructions": len(names),
                           "clean": not probs, "missing_opcodes": miss})
        if probs:
            problems[p.name] = probs[:5]

    opcodes = [{"opcode": n, "encodings": dict(encodings[n]), "instructions": uses[n], "shaders": shaders_using[n],
                "shadps4": "translated" if is_translated(n) else "missing"} for n in uses]
    opcodes.sort(key=lambda r: (-r["instructions"], r["opcode"]))
    missing = [r for r in opcodes if r["shadps4"] == "missing"]
    blocked = [s for s in per_shader if s["missing_opcodes"]]
    result = {
        "schema": "d1_gcn_isa_census/v1",
        "unique_shaders": len(per_shader),
        "clean_decodes": sum(s["clean"] for s in per_shader),
        "stages": dict(stage_counts),
        "instructions_total": sum(uses.values()),
        "distinct_opcodes": len(uses),
        "missing_in_shadps4": {"distinct_opcodes": len(missing), "instructions": sum(r["instructions"] for r in missing),
                               "shaders_affected": len(blocked)},
        "opcodes": opcodes,
        "shaders_with_missing_opcodes": blocked,
        "decode_problems": problems,
        "notes": [
            "Opcode names and translation coverage come from the shadPS4 checkout given on the command line.",
            "A shader with a missing opcode fails translation in shadPS4 (info.translation_failed).",
            "Operand-level gaps (unsupported image formats, SDWA/DPP, export formats) are not counted here.",
        ],
    }
    a.out.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: result[k] for k in ("unique_shaders", "clean_decodes", "stages", "instructions_total",
                                             "distinct_opcodes", "missing_in_shadps4")}))


if __name__ == "__main__":
    main()
