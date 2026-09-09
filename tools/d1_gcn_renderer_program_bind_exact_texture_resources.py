#!/usr/bin/env python3
"""Bind exact decoded D1 texture resources into a source-closed renderer program.

This adapter closes only the concrete resource facts proven by the exact texture exporter.
It does not assign visual texture roles, decode sampler state bits, or reinterpret BCn
channels beyond the format metadata already proven by the texture decoder.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

TARGET_SHADER = "808EE505"
EXPECTED = {
    "808EE4FE": {
        "texture_index": 0,
        "sampler_index": 1,
        "width": 1024,
        "height": 1024,
        "depth": 1,
        "array_size": 1,
        "format_name": "BC3",
        "stream": "808EE502",
        "backing": "808EE790",
        "backing_bytes": 1048576,
    },
    "808EE500": {
        "texture_index": 4,
        "sampler_index": 5,
        "width": 1024,
        "height": 1024,
        "depth": 1,
        "array_size": 1,
        "format_name": "BC5",
        "stream": "808EE504",
        "backing": "808EE792",
        "backing_bytes": 1048576,
    },
}


def load(path: Path):
    return json.loads(path.read_text())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--program", type=Path, required=True)
    ap.add_argument("--resources", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    violations: list[str] = []
    try:
        base = load(args.program)
        resources = load(args.resources)

        assert base["status"] == "D1_GCN_RENDERER_PROGRAM_IR_NATIVE_SEMANTICS_EXACT"
        assert not base.get("violations")
        program = base["program"]
        assert program["pixel_shader"] == TARGET_SHADER
        assert program["instruction_count"] == 456
        assert program["coverage"]["exact_nonstructural_instruction_count"] == 456
        assert program["coverage"]["structural_only_instruction_count"] == 0

        assert resources["status"] == "D1_CROTA_808EE505_FINAL_TEXTURE_RESOURCES_EXACT"
        assert resources["shader"] == TARGET_SHADER
        preflight = resources["preflight"]
        assert preflight["requested_count"] == 2
        assert preflight["success_count"] == 2
        assert preflight["failure_count"] == 0
        assert not preflight["failures"]

        rows = {row["header"]: row for row in resources["textures"]}
        assert set(rows) == set(EXPECTED), set(rows)

        contracts = {row["texture_taghash"]: row for row in program["final_native_image_sample_contracts"]}
        assert set(contracts) == set(EXPECTED), set(contracts)

        bound = []
        for tag, expected in EXPECTED.items():
            row = rows[tag]
            contract = contracts[tag]
            for key in ("width", "height", "depth", "array_size", "format_name", "stream", "backing", "backing_bytes"):
                assert row[key] == expected[key], (tag, key, row[key], expected[key])
            assert row["unswizzled"] is True
            assert row.get("png") and row.get("png_error") is None
            assert contract["texture_index"] == expected["texture_index"]
            assert contract["sampler_index"] == expected["sampler_index"]
            assert contract["resource_dimension"] == "CONSUMED_FROM_NATIVE_RESOURCE_DESCRIPTOR_NOT_GUESSED"

            bound.append({
                "texture_taghash": tag,
                "texture_index": expected["texture_index"],
                "sampler_index": expected["sampler_index"],
                "native_sample_instructions": [contract["instruction"]],
                "width": row["width"],
                "height": row["height"],
                "depth": row["depth"],
                "array_size": row["array_size"],
                "surface_format_raw": row["surface_format_raw"],
                "surface_format": row["surface_format"],
                "format_name": row["format_name"],
                "stream": row["stream"],
                "backing": row["backing"],
                "backing_bytes": row["backing_bytes"],
                "unswizzled": row["unswizzled"],
                "portable_decode": {
                    "dds": row["dds"],
                    "png": row["png"],
                    "png_error": row["png_error"],
                },
                "proof_tier": "EXACT_SERIALIZED_RESOURCE_CHAIN_AND_DECODE",
            })

        out = copy.deepcopy(base)
        out["schema_version"] = max(11, int(out.get("schema_version", 0)))
        out["status"] = "D1_GCN_RENDERER_PROGRAM_IR_NATIVE_AND_TEXTURE_RESOURCES_EXACT"
        out["program"]["exact_texture_resources"] = sorted(bound, key=lambda x: x["texture_index"])
        sb = out.setdefault("semantic_boundary", {})
        sb["portable_resource_dimension_for_808EE500_808EE4FE"] = "EXACT_2D_1024x1024"
        sb["portable_resource_format_for_808EE4FE"] = "EXACT_BC3"
        sb["portable_resource_format_for_808EE500"] = "EXACT_BC5"
        sb["texture_serialized_resource_chains"] = "EXACT_FOR_808EE4FE_808EE500"
        sb["visual_texture_role_names"] = "WITHHELD_UNLESS_SEPARATELY_SOURCE_PROVEN"
        sb["sampler_state_bit_decode"] = "NOT_DECODED_BY_THIS_LAYER"
        out["violations"] = []
        result = out
    except Exception as exc:
        violations = [repr(exc)]
        result = {
            "schema_version": 1,
            "status": "D1_GCN_RENDERER_TEXTURE_RESOURCE_BINDING_PARTIAL",
            "violations": violations,
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "status": result.get("status"),
        "bound_texture_count": len(result.get("program", {}).get("exact_texture_resources", [])),
        "violations": violations,
    }, indent=2))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
