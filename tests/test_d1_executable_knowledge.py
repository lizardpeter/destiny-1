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


kg = load("d1_executable_knowledge", "tools/d1_executable_knowledge.py")
db = load("d1_knowledge_db_for_exec_test", "tools/d1_knowledge_db.py")


KNOWN_SHA = "7271fcb926401df8defb126cb8eb2b247134138b81e401bbacb2ab60791b795"


def known_probe() -> dict:
    return {
        "schema": "d1_executable_probe/v2",
        "file_size": 0x1234,
        "sha256": KNOWN_SHA,
        "container": "ps4_self",
        "known_build": {
            "title_id": "CUSA00219",
            "app_version": "01.29",
            "artifact": "decrypted_eboot",
        },
        "embedded_elf_offset": 0x100,
        "elf_header": {
            "offset": 0x100,
            "class": 64,
            "endianness": "little",
            "machine_name": "x86_64",
            "entry": "0x400100",
            "supported": True,
        },
        "program_headers": [
            {
                "index": 0,
                "type": 1,
                "type_name": "PT_LOAD",
                "flags": 5,
                "readable": True,
                "writable": False,
                "executable": True,
                "file_offset": 0x1000,
                "absolute_file_offset": 0x1100,
                "virtual_address": "0x400000",
                "physical_address": "0x400000",
                "file_size": 0x2000,
                "memory_size": 0x2000,
                "alignment": 0x1000,
            }
        ],
        "research_anchors": {
            "graphics_heartbeat_code_offset": "0xFAAF4"
        },
    }


def test_known_fingerprint_promotes_supported_build_and_valid_graph(tmp_path):
    report = tmp_path / "probe.json"
    report.write_text(json.dumps(known_probe()), encoding="utf-8")
    record = kg.make_record(
        known_probe(),
        report,
        updated_utc="2026-09-26T12:00:00Z",
    )

    executable = next(n for n in record["nodes"] if n["kind"] == "executable_build")
    assert executable["status"] == "STRONGLY_SUPPORTED"
    assert record["scope"]["title_id"] == "CUSA00219"
    assert record["scope"]["app_version"] == "01.29"
    assert any(n["kind"] == "elf_program_segment" for n in record["nodes"])

    out = tmp_path / "record.json"
    out.write_text(json.dumps(record), encoding="utf-8")
    assert db.validate_record(out, record) == []


def test_unknown_fingerprint_requires_explicit_identity(tmp_path):
    probe = known_probe()
    probe["sha256"] = "0" * 64
    probe["known_build"] = None
    report = tmp_path / "unknown.json"
    report.write_text(json.dumps(probe), encoding="utf-8")

    try:
        kg.make_record(probe, report, updated_utc="2026-09-26T12:00:00Z")
    except ValueError as exc:
        assert "--title-id" in str(exc)
    else:
        raise AssertionError("unknown fingerprint must not acquire guessed build identity")


def test_operator_labeled_unknown_build_stays_candidate(tmp_path):
    probe = known_probe()
    probe["sha256"] = "1" * 64
    probe["known_build"] = None
    report = tmp_path / "unknown.json"
    report.write_text(json.dumps(probe), encoding="utf-8")

    record = kg.make_record(
        probe,
        report,
        title_id="CUSA00219",
        app_version="01.33",
        updated_utc="2026-09-26T12:00:00Z",
    )
    executable = next(n for n in record["nodes"] if n["kind"] == "executable_build")
    assert executable["status"] == "CANDIDATE"

    out = tmp_path / "record.json"
    out.write_text(json.dumps(record), encoding="utf-8")
    assert db.validate_record(out, record) == []
