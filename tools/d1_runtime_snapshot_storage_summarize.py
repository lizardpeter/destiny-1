#!/usr/bin/env python3
"""Summarize exact-build D1 runtime snapshot storage xrefs by block-relative offset.

This tool consumes d1_executable_rip_target_xrefs.py output and keeps semantics
withheld.  It groups resolved addresses relative to caller-supplied candidate
storage bases and classifies scalar-float-looking accesses only from instruction
form (for example vmovss/vmulss), never from a guessed Frame/DeferredLight name.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def parse_base(value: str) -> tuple[str, int]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("--base expects label=address")
    label, raw = value.split("=", 1)
    return label, int(raw, 0)


def scalar_floatish(mnemonic: str) -> bool:
    m = mnemonic.lower()
    return (
        m.endswith("ss")
        or m in {"vmovss", "movss"}
        or "ucomiss" in m
        or "comiss" in m
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xrefs", type=Path, required=True)
    ap.add_argument("--base", action="append", type=parse_base, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    doc = json.loads(a.xrefs.read_text())
    bases = dict(a.base)

    by_base: dict[str, Counter] = {k: Counter() for k in bases}
    float_by_base: dict[str, Counter] = {k: Counter() for k in bases}
    access_by_base: dict[str, Counter] = {k: Counter() for k in bases}
    hits_by_offset: dict[str, dict[int, list[dict]]] = {
        k: defaultdict(list) for k in bases
    }

    for hit in doc.get("hits", []):
        mnemonic = hit.get("mnemonic", "")
        for ref in hit.get("rip_refs", []):
            target = int(ref["resolved_target"])
            for label, base in bases.items():
                off = target - base
                # Keep a deliberately broad local snapshot window. Negative
                # offsets are retained only when still close enough to reveal
                # adjacent sibling blocks.
                if -0x200 <= off <= 0x2000:
                    by_base[label][off] += 1
                    access_by_base[label][ref.get("access", "unknown")] += 1
                    if scalar_floatish(mnemonic):
                        float_by_base[label][off] += 1
                    hits_by_offset[label][off].append({
                        "instruction_va": hit.get("address_hex"),
                        "mnemonic": mnemonic,
                        "op_str": hit.get("op_str"),
                        "access": ref.get("access"),
                        "resolved_target_hex": ref.get("resolved_target_hex"),
                    })

    blocks = {}
    for label, base in bases.items():
        rows = []
        offsets = set(by_base[label]) | set(float_by_base[label])
        for off in sorted(offsets):
            rows.append({
                "offset": off,
                "offset_hex": f"{off:+#x}",
                "absolute": base + off,
                "absolute_hex": hex(base + off),
                "xref_count": by_base[label][off],
                "scalar_floatish_xref_count": float_by_base[label][off],
                "hits": hits_by_offset[label][off],
            })
        hot = sorted(
            rows,
            key=lambda r: (
                -r["scalar_floatish_xref_count"],
                -r["xref_count"],
                abs(r["offset"]),
            ),
        )[:64]
        blocks[label] = {
            "base": base,
            "base_hex": hex(base),
            "access_counts": dict(access_by_base[label]),
            "offset_count": len(rows),
            "hot_offsets": hot,
            "all_offsets": rows,
        }

    out = {
        "schema": "d1_runtime_snapshot_storage_summary/v1",
        "status": "EXACT_BUILD_STORAGE_OFFSET_SUMMARY",
        "executable_sha256": doc.get("executable_sha256"),
        "blocks": blocks,
        "policy": (
            "Block-relative offsets and xref instruction forms are exact-build "
            "evidence. scalar_floatish_xref_count means only that the x86 opcode "
            "looks like scalar floating-point traffic. No block or field is named "
            "Frame, DeferredLight, exposure, time, or another renderer semantic "
            "without independent producer/consumer closure."
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({
        "status": out["status"],
        "blocks": {
            k: {
                "offset_count": v["offset_count"],
                "hot_offsets": [
                    {
                        "offset": x["offset_hex"],
                        "xrefs": x["xref_count"],
                        "floatish": x["scalar_floatish_xref_count"],
                    }
                    for x in v["hot_offsets"][:16]
                ],
            }
            for k, v in blocks.items()
        },
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
