import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SPEC = importlib.util.spec_from_file_location(
    "d1_executable_renderer_frontier",
    TOOLS / "d1_executable_renderer_frontier.py",
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules["d1_executable_renderer_frontier"] = mod
SPEC.loader.exec_module(mod)


def write_graph(root: Path):
    root.mkdir()
    exe = "executable:CUSA00219:01.33:aaaaaaaaaaaaaaaa"
    a = "function:aaaaaaaaaaaaaaaa:0000000000001000"
    b = "function:aaaaaaaaaaaaaaaa:0000000000002000"
    ext = "external:aaaaaaaaaaaaaaaa:gpu"
    string = "string:aaaaaaaaaaaaaaaa:0000000000009000"
    manifest = {
        "schema": "d1_normalized_code_graph/v1",
        "executable_id": exe,
        "executable_sha256": "a" * 64,
        "title_id": "CUSA00219",
        "app_version": "01.33",
        "counts": {},
    }
    nodes = [
        {"id": exe, "kind": "executable_build", "attrs": {"sha256": "a" * 64}},
        {
            "id": a,
            "kind": "function",
            "attrs": {
                "entry": "0080001000",
                "image_offset": 0x1000,
                "name": "FUN_1000",
                "prototype": "void FUN_1000(void)",
                "instruction_count": 40,
                "body_ranges": [{
                    "min_image_offset": 0x1000,
                    "max_image_offset": 0x10FF,
                }],
            },
        },
        {
            "id": b,
            "kind": "function",
            "attrs": {
                "entry": "0080002000",
                "image_offset": 0x2000,
                "name": "FUN_2000",
                "prototype": "void FUN_2000(void)",
                "instruction_count": 20,
                "body_ranges": [{
                    "min_image_offset": 0x2000,
                    "max_image_offset": 0x20FF,
                }],
            },
        },
        {
            "id": ext,
            "kind": "external_function",
            "attrs": {
                "name": "sceGnmSubmitCommandBuffers",
                "library": "libSceGnmDriver",
                "prototype": "int sceGnmSubmitCommandBuffers(...)",
            },
        },
        {
            "id": string,
            "kind": "defined_string",
            "attrs": {
                "text": "deferred lighting render target",
                "image_offset": 0x9000,
            },
        },
    ]
    edges = [
        {"subject": a, "predicate": "REFERENCES_STRING", "object": string, "attrs": {}},
        {"subject": a, "predicate": "CALLS", "object": ext, "attrs": {}},
        {"subject": b, "predicate": "CALLS", "object": a, "attrs": {}},
    ]
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (root / "nodes.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in nodes), encoding="utf-8"
    )
    (root / "edges.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in edges), encoding="utf-8"
    )
    return a, b


def write_renderer_strings(path: Path):
    path.write_text(
        json.dumps({
            "schema": "d1_executable_renderer_strings/v1",
            "strings": [{
                "text": "deferred lighting render target",
                "categories": ["lighting", "frame_graph"],
                "candidate_lea_xref_count": 1,
            }],
        }),
        encoding="utf-8",
    )


def test_direct_renderer_function_outranks_callgraph_neighbor(tmp_path):
    graph = tmp_path / "graph"
    direct, neighbor = write_graph(graph)
    strings = tmp_path / "renderer_strings.json"
    write_renderer_strings(strings)

    report = mod.analyze(graph, strings, radius=2, top=20)
    rows = {row["function_id"]: row for row in report["candidates"]}
    assert rows[direct]["direct_score"] > 0
    assert "lighting" in rows[direct]["domains"]
    assert "frame_graph" in rows[direct]["domains"]
    assert rows[direct]["renderer_external_call_count"] == 1
    assert rows[neighbor]["direct_score"] == 0
    assert rows[neighbor]["neighbor_score"] > 0
    assert rows[direct]["score"] > rows[neighbor]["score"]


def test_external_match_is_not_semantic_promotion(tmp_path):
    graph = tmp_path / "graph"
    direct, _ = write_graph(graph)
    strings = tmp_path / "renderer_strings.json"
    write_renderer_strings(strings)
    report = mod.analyze(graph, strings)
    row = next(item for item in report["candidates"] if item["function_id"] == direct)
    assert any(ev["kind"] == "renderer_external_call" for ev in row["evidence"])
    assert "prioritize" in report["policy"]
