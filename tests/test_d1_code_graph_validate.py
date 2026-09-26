import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "d1_code_graph_validate", ROOT / "tools" / "d1_code_graph_validate.py"
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules["d1_code_graph_validate"] = mod
SPEC.loader.exec_module(mod)

SHA = "a" * 64


def graph():
    executable = "executable:CUSA00219:01.29:aaaaaaaaaaaaaaaa"
    function = "function:aaaaaaaaaaaaaaaa:00000000000fa000"
    string = "string:aaaaaaaaaaaaaaaa:0000000000100000"
    manifest = {
        "schema": "d1_normalized_code_graph/v1",
        "executable_id": executable,
        "executable_sha256": SHA,
        "title_id": "CUSA00219",
        "app_version": "01.29",
        "source_schema": "d1_ghidra_code_graph/v1",
        "counts": {
            "nodes": 3,
            "edges": 4,
            "functions": 1,
            "external_functions": 0,
            "external_libraries": 0,
            "defined_strings": 1,
            "call_edges": 0,
            "string_xref_edges": 1,
        },
    }
    nodes = [
        {
            "id": executable,
            "kind": "executable_build",
            "attrs": {
                "sha256": SHA,
                "title_id": "CUSA00219",
                "app_version": "01.29",
                "image_base": "0080000000",
                "language_id": "x86:LE:64:default",
                "compiler_spec": "gcc",
                "executable_format": "ELF",
            },
        },
        {
            "id": function,
            "kind": "function",
            "attrs": {
                "executable_sha256": SHA,
                "entry": "00800FA000",
                "image_offset": 0xFA000,
                "body_ranges": [
                    {
                        "min": "00800FA000",
                        "max": "00800FABFF",
                        "min_image_offset": 0xFA000,
                        "max_image_offset": 0xFABFF,
                    }
                ],
                "instruction_count": 100,
                "instruction_byte_count": 400,
                "instruction_bytes_sha256": "b" * 64,
                "mnemonic_sequence_sha256": "c" * 64,
                "name": "FUN_00800FA000",
                "source": "ANALYSIS",
            },
        },
        {
            "id": string,
            "kind": "defined_string",
            "attrs": {
                "executable_sha256": SHA,
                "address": "0080100000",
                "image_offset": 0x100000,
                "text": "Graphics Heartbeat",
                "data_type": "string",
            },
        },
    ]
    edges = [
        {
            "subject": executable,
            "predicate": "HAS_FUNCTION",
            "object": function,
            "attrs": {},
        },
        {
            "subject": executable,
            "predicate": "HAS_DEFINED_STRING",
            "object": string,
            "attrs": {},
        },
        {
            "subject": function,
            "predicate": "REFERENCES_STRING",
            "object": string,
            "attrs": {"from_image_offset": 0xFAA20},
        },
        {
            "subject": executable,
            "predicate": "HAS_DEFINED_STRING",
            "object": string,
            "attrs": {"secondary_registration": True},
        },
    ]
    return manifest, nodes, edges


def test_valid_graph_passes_and_counts():
    manifest, nodes, edges = graph()
    result = mod.validate_graph(manifest, nodes, edges)
    assert result["status"] == "D1_CODE_GRAPH_VALID"
    assert result["counts"]["functions"] == 1
    assert result["counts"]["string_xref_edges"] == 1


def test_dangling_edge_fails():
    manifest, nodes, edges = graph()
    edges[0]["object"] = "function:missing"
    try:
        mod.validate_graph(manifest, nodes, edges)
    except ValueError as exc:
        assert "unknown object" in str(exc)
    else:
        raise AssertionError("dangling edge must fail")


def test_mixed_executable_sha_fails():
    manifest, nodes, edges = graph()
    nodes[1]["attrs"]["executable_sha256"] = "d" * 64
    try:
        mod.validate_graph(manifest, nodes, edges)
    except ValueError as exc:
        assert "does not match manifest exact build" in str(exc)
    else:
        raise AssertionError("mixed executable namespace must fail")


def test_wrong_edge_kind_fails():
    manifest, nodes, edges = graph()
    edges[0] = {
        "subject": nodes[2]["id"],
        "predicate": "HAS_FUNCTION",
        "object": nodes[1]["id"],
        "attrs": {},
    }
    try:
        mod.validate_graph(manifest, nodes, edges)
    except ValueError as exc:
        assert "subject kind" in str(exc)
    else:
        raise AssertionError("wrong edge kind must fail")
