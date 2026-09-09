#!/usr/bin/env python3
"""Regression fixture for the strict V2 -> PS/VS/DS V3 corpus reclassifier."""
from __future__ import annotations

import copy
import hashlib
import json
import struct
import tempfile
from pathlib import Path

import d1_shader_corpus_v2_format_reclassify as r


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        hd = root / "headers"
        pd = root / "programs"
        hd.mkdir(); pd.mkdir()

        hb = struct.pack("<I", (2 << 24) | 0x40) + b"\x00" * 12
        hsha = sha(hb)
        (hd / "PS_80000001.bin").write_bytes(hb)
        code = b"\x00" * 16
        csha = sha(code)
        (pd / f"{csha}.bin").write_bytes(code)

        native = {
            "native_program_reference": "80000002",
            "header_count": 1,
            "headers": [{"stage": "PS", "header": "80000001"}],
            "stages": ["PS"],
            "violations": ["80000001:ps_embedded_size:64!=128"],
            "retail_native_meta": {"type": 1, "subtype": 8},
            "native_payload": {"bytes": 128, "sha256": "0" * 64},
            "orbshdr_locator": {
                "formula_footer_offset": 36,
                "formula_magic_matches": True,
            },
            "binary_info": {
                "offset": 36,
                "stage": "PixelShader",
                "num_input_usage_slots": 2,
            },
            "gcn_code": {"bytes": 16, "sha256": csha},
        }
        header = {
            "stage": "PS",
            "header": "80000001",
            "planned_native_program_reference": "80000002",
            "retail_native_program_reference": "80000002",
            "violations": [],
            "retail_header_meta": {"type": 32, "subtype": 8},
            "header_payload": {"bytes": len(hb), "sha256": hsha},
        }
        program = {
            "gcn_sha256": csha,
            "gcn_bytes": 16,
            "native_program_references": ["80000002"],
            "headers": [{"stage": "PS", "header": "80000001"}],
            "stages": ["PS"],
            "native_reference_count": 1,
            "header_count": 1,
        }
        topv = ["80000002:80000001:ps_embedded_size:64!=128"]
        src = {
            "schema": r.RAW_SCHEMA,
            "status": "D1_REMOTE_PS4_SHADER_CORPUS_WITH_VIOLATIONS",
            "source_plan": "plan.json",
            "violations": topv,
            "header_population": {
                "total": 1,
                "payload_recovered_count": 1,
                "payload_unrecovered_count": 0,
            },
            "native_reference_population": {
                "planned_unique": 1,
                "recovered_rows": 1,
                "payload_recovered_count": 1,
                "gcn_code_recovered_count": 1,
                "unrecovered_native_references": [],
            },
            "gcn_program_population": {"unique_exact_code_sha256_count": 1},
            "headers": [header],
            "native_programs": [native],
            "unique_gcn_programs": [program],
        }

        out = r.reclassify(src, hd, pd)
        assert out["status"] == r.OUT_STATUS, out["violations"]
        assert out["header_population"]["stage_counts"] == {"PS": 1}
        assert out["native_reference_population"]["stage_counts"] == {"PS": 1}
        assert out["gcn_program_population"]["stage_unique_counts"] == {"PS": 1}
        assert out["reclassification"]["legacy_v2_violations_exactly_explained"] == 1
        assert out["proof"]["all_original_violations_accounted"] is True

        bad = copy.deepcopy(src)
        bad["native_programs"][0]["violations"].append("mystery_violation")
        bad["violations"].append("80000002:mystery_violation")
        rejected = r.reclassify(bad, hd, pd)
        assert rejected["status"] != r.OUT_STATUS
        assert any("unexplained_legacy_violation" in x for x in rejected["violations"])

    print("D1_SHADER_CORPUS_V2_FORMAT_RECLASSIFY_REGRESSION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
