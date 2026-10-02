#!/usr/bin/env python3
"""Assemble exact D1 Tower light global-channel runtime evidence.

Inputs:
  * exact GlobalChannelDefaults decode
  * exact local-sequencer-ID -> global-index StringHash join
  * symbolic sequencer reduction

Output is intentionally compact and runtime-oriented. It does not assign
human-facing channel names. A channel may be:
  DEFAULT_ONLY
  TOWER_SEQUENCER_OVERRIDE
  TOWER_SEQUENCER_PARTIAL
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUESTED = (0x11, 0x28, 0x30, 0x60)


def key(i: int) -> str:
    return f"0x{i:02X}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--defaults", type=Path, required=True)
    ap.add_argument("--join", type=Path, required=True)
    ap.add_argument("--symbolic", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    defaults = json.loads(a.defaults.read_text())
    join = json.loads(a.join.read_text())
    symbolic = json.loads(a.symbolic.read_text())

    by_index = {int(row["index"]): row for row in defaults.get("channels", [])}
    joined = {
        i: [row for row in join.get("joins", []) if int(row["global_index"]) == i]
        for i in REQUESTED
    }
    symbolic_by = symbolic.get("programs_by_index", {})

    rows = []
    violations = []

    for i in REQUESTED:
        k = key(i)
        default = by_index.get(i)
        if default is None:
            violations.append(f"{k}:missing_exact_default")
            continue

        programs = joined[i]
        sym = symbolic_by.get(k, [])
        if programs and not sym:
            state = "TOWER_SEQUENCER_PARTIAL"
        elif programs:
            state = "TOWER_SEQUENCER_OVERRIDE"
        else:
            state = "DEFAULT_ONLY"

        # Every exact joined program for one global row must share the same
        # StringHash identity by construction.
        string_hashes = sorted({
            str(row.get("channel_id_string_hash") or "").upper()
            for row in programs
            if row.get("channel_id_string_hash")
        })
        if len(string_hashes) > 1:
            violations.append(f"{k}:multiple_string_hashes:{string_hashes}")

        symbolic_rows = []
        for row in sym:
            s = row.get("symbolic") or {}
            symbolic_rows.append({
                "resource_hash": row.get("resource_hash"),
                "local_channel_index": row.get("local_channel_index"),
                "local_channel_index_hex": row.get("local_channel_index_hex"),
                "channel_id_string_hash": row.get("channel_id_string_hash"),
                "bytecode_sha256": row.get("bytecode_sha256"),
                "fully_symbolically_closed": bool(s.get("fully_symbolically_closed")),
                "outputs": s.get("outputs", {}),
                "unresolved": s.get("unresolved", []),
            })

        rows.append({
            "global_index": i,
            "global_index_hex": k,
            "state": state,
            "string_hash": string_hashes[0] if len(string_hashes) == 1 else None,
            "default_vec4": default.get("default_vec4"),
            "tower_override_program_count": len(programs),
            "tower_override_programs": symbolic_rows,
        })

    out = {
        "schema": "d1_tower_light_runtime_global_channels/v1",
        "status": (
            "D1_TOWER_LIGHT_RUNTIME_GLOBAL_CHANNELS_EXACT"
            if not violations
            else "D1_TOWER_LIGHT_RUNTIME_GLOBAL_CHANNELS_PARTIAL"
        ),
        "global_defaults_tag_hash": defaults.get("tag_hash"),
        "global_channel_count": defaults.get("layout", {}).get("channel_count"),
        "requested_indices": [key(i) for i in REQUESTED],
        "channels": rows,
        "violations": violations,
        "runtime_policy": (
            "Start each requested channel from its exact GlobalChannelDefaults Vec4. "
            "Apply only exact Tower sequencer overrides whose local ID was joined to "
            "the global row by StringHash and whose bytecode symbolic reduction is "
            "closed. Do not infer a human-facing semantic name from index, value, "
            "lane usage, or later-engine terminology."
        ),
        "proof_boundary": (
            "This report closes exact default values and Tower-owned sequencer update "
            "program identity/formulas when present. It does not prove update cadence, "
            "sequencer activation conditions outside the exact owner chain, or names "
            "such as exposure/sun/intensity/direction."
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n")

    print(json.dumps({
        "status": out["status"],
        "global_channel_count": out["global_channel_count"],
        "channels": [
            {
                "index": row["global_index_hex"],
                "state": row["state"],
                "default_vec4": row["default_vec4"],
                "override_programs": row["tower_override_program_count"],
                "closed_formulas": sum(
                    int(x["fully_symbolically_closed"])
                    for x in row["tower_override_programs"]
                ),
            }
            for row in rows
        ],
        "violations": violations,
    }, indent=2))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
