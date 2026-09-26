import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


bridge_mod = load("d1_code_semantic_bridge", "tools/d1_code_semantic_bridge.py")
db_mod = load("d1_knowledge_db_bridge_test", "tools/d1_knowledge_db.py")


def write_graph(graph_dir: Path):
    graph_dir.mkdir()
    manifest = {
        "schema": "d1_normalized_code_graph/v1",
        "executable_id": "executable:CUSA00219:01.29:aaaaaaaaaaaaaaaa",
        "executable_sha256": "a" * 64,
        "title_id": "CUSA00219",
        "app_version": "01.29",
        "source_schema": "d1_ghidra_code_graph/v1",
        "counts": {
            "nodes": 2,
            "edges": 1,
            "functions": 1,
            "external_functions": 0,
            "external_libraries": 0,
            "defined_strings": 0,
            "call_edges": 0,
            "string_xref_edges": 0,
        },
    }
    fn = {
        "id": "function:aaaaaaaaaaaaaaaa:00000000000fa000",
        "kind": "function",
        "attrs": {
            "executable_sha256": "a" * 64,
            "title_id": "CUSA00219",
            "app_version": "01.29",
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
            "namespace": "Global",
            "source": "ANALYSIS",
            "calling_convention": "unknown",
            "prototype": "void FUN_00800FA000(void)",
            "is_thunk": False,
            "is_external": False,
        },
    }
    exe = {
        "id": manifest["executable_id"],
        "kind": "executable_build",
        "attrs": {
            "sha256": "a" * 64,
            "title_id": "CUSA00219",
            "app_version": "01.29",
            "image_base": "0080000000",
            "language_id": "x86:LE:64:default",
            "compiler_spec": "gcc",
            "executable_format": "ELF",
        },
    }
    (graph_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (graph_dir / "nodes.jsonl").write_text(
        json.dumps(exe) + "\n" + json.dumps(fn) + "\n",
        encoding="utf-8",
    )
    (graph_dir / "edges.jsonl").write_text(
        json.dumps(
            {
                "subject": exe["id"],
                "predicate": "HAS_FUNCTION",
                "object": fn["id"],
                "attrs": {},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return fn["id"]


def asset_record():
    return {
        "schema": "d1_knowledge_record/v1",
        "record_id": "material_record",
        "title": "material record",
        "updated_utc": "2026-09-26T13:00:00Z",
        "nodes": [
            {
                "id": "material:80AAE14B",
                "kind": "material",
                "status": "PROVEN",
                "attrs": {},
            }
        ],
        "edges": [],
        "assertions": [],
        "sources": [],
        "rejections": [],
        "frontiers": [],
    }


def test_bridge_promotes_function_and_cross_record_edge(tmp_path):
    graph_dir = tmp_path / "graph"
    function_id = write_graph(graph_dir)
    spec_path = tmp_path / "bridge.json"
    spec = {
        "schema": "d1_code_semantic_bridge/v1",
        "record_id": "code_material_bridge",
        "title": "code to material bridge",
        "updated_utc": "2026-09-26T13:00:00Z",
        "bridges": [
            {
                "function_id": function_id,
                "predicate": "SELECTS_MATERIAL",
                "target_node_id": "material:80AAE14B",
                "target_record_id": "material_record",
                "status": "STRONGLY_SUPPORTED",
                "claim": "The analyzed function selects the proven material.",
                "evidence": {"fixture": True},
            }
        ],
    }
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    record = bridge_mod.build_record(graph_dir, spec_path, spec)

    fn = record["nodes"][0]
    assert fn["id"] == function_id
    assert fn["status"] == "PROVEN"
    assert record["external_nodes"] == [
        {
            "id": "material:80AAE14B",
            "record_id": "material_record",
            "note": None,
        }
    ]
    assert record["edges"][0]["status"] == "STRONGLY_SUPPORTED"
    assert record["edges"][0]["predicate"] == "SELECTS_MATERIAL"

    asset_path = tmp_path / "asset.json"
    bridge_path = tmp_path / "promoted.json"
    asset_path.write_text(json.dumps(asset_record()), encoding="utf-8")
    bridge_path.write_text(json.dumps(record), encoding="utf-8")
    db_mod.validate_all(
        [(asset_path, asset_record()), (bridge_path, record)]
    )


def test_bridge_rejects_unknown_function(tmp_path):
    graph_dir = tmp_path / "graph"
    write_graph(graph_dir)
    spec_path = tmp_path / "bridge.json"
    spec = {
        "schema": "d1_code_semantic_bridge/v1",
        "record_id": "bad",
        "title": "bad",
        "updated_utc": "2026-09-26T13:00:00Z",
        "bridges": [
            {
                "function_id": "function:missing",
                "predicate": "SELECTS_MATERIAL",
                "target_node_id": "material:80AAE14B",
                "target_record_id": "material_record",
                "status": "CANDIDATE",
                "claim": "bad",
            }
        ],
    }
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    try:
        bridge_mod.build_record(graph_dir, spec_path, spec)
    except ValueError as exc:
        assert "unknown function_id" in str(exc)
    else:
        raise AssertionError("unknown function must fail")


def test_bridge_rejects_conflicting_target_ownership(tmp_path):
    graph_dir = tmp_path / "graph"
    function_id = write_graph(graph_dir)
    spec_path = tmp_path / "bridge.json"
    spec = {
        "schema": "d1_code_semantic_bridge/v1",
        "record_id": "conflict",
        "title": "conflict",
        "updated_utc": "2026-09-26T13:00:00Z",
        "bridges": [
            {
                "function_id": function_id,
                "predicate": "SELECTS_MATERIAL",
                "target_node_id": "material:80AAE14B",
                "target_record_id": "material_record_a",
                "status": "CANDIDATE",
                "claim": "first",
            },
            {
                "function_id": function_id,
                "predicate": "BINDS_SHADER_RESOURCE",
                "target_node_id": "material:80AAE14B",
                "target_record_id": "material_record_b",
                "status": "CANDIDATE",
                "claim": "second",
            },
        ],
    }
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    try:
        bridge_mod.build_record(graph_dir, spec_path, spec)
    except ValueError as exc:
        assert "conflicting target_record_id" in str(exc)
    else:
        raise AssertionError("conflicting target ownership must fail")
