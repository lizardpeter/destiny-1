import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "d1_code_hash_literal_candidates",
    ROOT / "tools" / "d1_code_hash_literal_candidates.py",
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules["d1_code_hash_literal_candidates"] = mod
SPEC.loader.exec_module(mod)


def write_graph(root: Path):
    root.mkdir()
    exe = "executable:CUSA00219:01.29:aaaaaaaaaaaaaaaa"
    fn = "function:aaaaaaaaaaaaaaaa:0000000000001000"
    lit = "d1hash:aaaaaaaaaaaaaaaa:80801ad7"
    manifest = {
        "schema": "d1_normalized_code_graph/v1",
        "executable_id": exe,
        "executable_sha256": "a" * 64,
        "title_id": "CUSA00219",
        "app_version": "01.29",
        "counts": {},
    }
    nodes = [
        {
            "id": exe,
            "kind": "executable_build",
            "attrs": {"sha256": "a" * 64},
        },
        {
            "id": fn,
            "kind": "function",
            "attrs": {
                "name": "FUN_1000",
                "entry": "0080001000",
                "image_offset": 0x1000,
                "instruction_count": 12,
                "instruction_bytes_sha256": "b" * 64,
                "mnemonic_sequence_sha256": "c" * 64,
            },
        },
        {
            "id": lit,
            "kind": "d1_hash_literal",
            "attrs": {
                "executable_sha256": "a" * 64,
                "value_u32": 0x80801AD7,
                "value_hex": "0x80801AD7",
            },
        },
    ]
    edges = [
        {
            "subject": fn,
            "predicate": "REFERENCES_D1_HASH_LITERAL",
            "object": lit,
            "attrs": {
                "instruction": "0080001010",
                "instruction_image_offset": 0x1010,
                "operand_index": 1,
                "bit_length": 32,
            },
        }
    ]
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (root / "nodes.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in nodes), encoding="utf-8"
    )
    (root / "edges.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in edges), encoding="utf-8"
    )


def test_registry_literal_match_reports_exact_function_xref(tmp_path):
    graph = tmp_path / "graph"
    write_graph(graph)
    registry = {
        0x80801AD7: {
            "label": "SMaterial_ROI_PS4",
            "semantic_status": "global_byte_validated",
            "export_route": "material_manifest",
        },
        0x808005A1: {
            "label": "s_animation_clip",
            "semantic_status": "global_byte_validated",
            "export_route": "animation_clip",
        },
    }
    result = mod.analyze(graph, registry, [])
    assert result["observed_value_count"] == 1
    assert result["observed_occurrence_count"] == 1
    assert result["observed_function_count"] == 1

    material = next(
        row for row in result["rows"] if row["value_u32"] == 0x80801AD7
    )
    assert material["registry_label"] == "SMaterial_ROI_PS4"
    assert material["status"] == "LITERAL_MATCH_ONLY"
    assert material["functions"][0]["function_id"].endswith("0000000000001000")
    assert (
        material["functions"][0]["occurrences"][0]["instruction_image_offset"]
        == 0x1010
    )

    animation = next(
        row for row in result["rows"] if row["value_u32"] == 0x808005A1
    )
    assert animation["literal_present"] is False
    assert animation["status"] == "NOT_OBSERVED"


def test_parse_u32_accepts_prefixed_and_plain_hex():
    assert mod.parse_u32("0x80801AD7") == 0x80801AD7
    assert mod.parse_u32("80801AD7") == 0x80801AD7
