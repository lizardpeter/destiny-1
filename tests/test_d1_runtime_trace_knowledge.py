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


trace_mod = load("d1_runtime_trace_knowledge", "tools/d1_runtime_trace_knowledge.py")
db_mod = load("d1_knowledge_db_trace_test", "tools/d1_knowledge_db.py")


def base_trace():
    return {
        "schema": "d1_runtime_code_trace/v1",
        "trace_id": "fixture:time_control",
        "record_id": "fixture_time_control_trace",
        "title": "Fixture TIME_CONTROL trace",
        "label": "TIME_CONTROL startup trace",
        "updated_utc": "2026-09-26T13:00:00Z",
        "build": {
            "platform": "Xbox 360",
            "title_id": "41560907",
            "build_label": "Destiny pre-release",
            "sha256": None,
        },
        "source": {
            "kind": "runtime_report",
            "locator": "https://example.invalid/trace",
            "sha256": None,
            "details": {},
        },
        "thread": {
            "name": "TIME_CONTROL",
            "handle": "F8000030",
            "is_thread_start": True,
        },
        "fault": {
            "exception": "0xC0000005",
        },
        "frames": [
            {
                "depth": 0,
                "address": "0x8365B858",
                "symbol": "sub_8365B858",
                "generated_line": 48741,
            },
            {
                "depth": 1,
                "address": "0x8365B938",
                "symbol": "sub_8365B938",
                "generated_line": 48866,
            },
        ],
        "globals": [
            {
                "address": "0x83FF3B84",
                "access": "read",
                "source_function_address": "0x8365B858",
                "instruction": "lwz r11,15236(r31)",
            }
        ],
    }


def test_trace_promotes_frames_without_static_calls(tmp_path):
    path = tmp_path / "trace.json"
    doc = base_trace()
    path.write_text(json.dumps(doc), encoding="utf-8")
    record = trace_mod.promote(path, doc)

    assert any(n["kind"] == "runtime_code_trace" for n in record["nodes"])
    functions = [n for n in record["nodes"] if n["kind"] == "function"]
    assert len(functions) == 2
    assert all(n["status"] == "STRONGLY_SUPPORTED" for n in functions)
    assert any(n["kind"] == "guest_global" for n in record["nodes"])
    assert sum(
        e["predicate"] == "HAS_RUNTIME_STACK_FRAME" for e in record["edges"]
    ) == 2
    assert not any(e["predicate"] == "CALLS" for e in record["edges"])
    assert any(e["predicate"] == "READS_GUEST_GLOBAL" for e in record["edges"])

    db_mod.validate_record(path, record)


def test_exact_build_sha_promotes_executable_existence_to_proven(tmp_path):
    path = tmp_path / "trace.json"
    doc = base_trace()
    doc["build"]["sha256"] = "a" * 64
    path.write_text(json.dumps(doc), encoding="utf-8")
    record = trace_mod.promote(path, doc)
    executable = next(n for n in record["nodes"] if n["kind"] == "executable_build")
    assert executable["status"] == "PROVEN"
    assert executable["attrs"]["identity_basis"] == "exact_sha256"


def test_global_source_must_be_a_frame(tmp_path):
    path = tmp_path / "trace.json"
    doc = base_trace()
    doc["globals"][0]["source_function_address"] = "0x81234567"
    path.write_text(json.dumps(doc), encoding="utf-8")
    try:
        trace_mod.promote(path, doc)
    except ValueError as exc:
        assert "is not a runtime frame" in str(exc)
    else:
        raise AssertionError("global access from unknown frame must fail")


def test_duplicate_frame_depth_fails(tmp_path):
    path = tmp_path / "trace.json"
    doc = base_trace()
    doc["frames"][1]["depth"] = 0
    path.write_text(json.dumps(doc), encoding="utf-8")
    try:
        trace_mod.promote(path, doc)
    except ValueError as exc:
        assert "duplicate runtime frame depth" in str(exc)
    else:
        raise AssertionError("duplicate runtime frame depths must fail")
