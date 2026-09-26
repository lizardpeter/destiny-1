import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "d1_knowledge_db_cross_record", ROOT / "tools" / "d1_knowledge_db.py"
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules["d1_knowledge_db_cross_record"] = mod
SPEC.loader.exec_module(mod)


def base_record(record_id: str, nodes: list[dict], **extra):
    doc = {
        "schema": "d1_knowledge_record/v1",
        "record_id": record_id,
        "title": record_id,
        "updated_utc": "2026-09-26T13:00:00Z",
        "nodes": nodes,
        "edges": [],
        "assertions": [],
        "sources": [],
        "rejections": [],
        "frontiers": [],
    }
    doc.update(extra)
    return doc


def write(path: Path, doc: dict):
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path, doc


def test_cross_record_edge_validates_and_builds_sqlite(tmp_path):
    asset = base_record(
        "asset_record",
        [
            {
                "id": "material:80AAE14B",
                "kind": "material",
                "status": "PROVEN",
                "label": "retail material",
                "attrs": {},
            }
        ],
    )
    code = base_record(
        "code_record",
        [
            {
                "id": "function:0129:0000000000123456",
                "kind": "function",
                "status": "STRONGLY_SUPPORTED",
                "label": "candidate material consumer",
                "attrs": {},
            }
        ],
        external_nodes=[
            {
                "id": "material:80AAE14B",
                "record_id": "asset_record",
                "note": "canonical material node owned by the asset record",
            }
        ],
        edges=[
            {
                "id": "edge:function_material",
                "subject": "function:0129:0000000000123456",
                "predicate": "CONSUMES_RESOURCE_CLASS",
                "object": "material:80AAE14B",
                "status": "STRONGLY_SUPPORTED",
                "assertion_ids": [],
                "attrs": {"evidence": "exact_xref_fixture"},
            }
        ],
    )

    records = [
        write(tmp_path / "asset.json", asset),
        write(tmp_path / "code.json", code),
    ]
    mod.validate_all(records)

    db_path = tmp_path / "knowledge.sqlite"
    mod.build_db(records, db_path)
    con = sqlite3.connect(db_path)
    try:
        assert con.execute("PRAGMA user_version").fetchone()[0] == 2
        assert con.execute(
            "SELECT node_id,target_record_id FROM external_node_refs"
        ).fetchone() == ("material:80AAE14B", "asset_record")
        assert con.execute(
            "SELECT subject_id,predicate,object_id FROM edges "
            "WHERE record_id='code_record'"
        ).fetchone() == (
            "function:0129:0000000000123456",
            "CONSUMES_RESOURCE_CLASS",
            "material:80AAE14B",
        )
        owners = con.execute(
            "SELECT record_id FROM nodes WHERE node_id='material:80AAE14B'"
        ).fetchall()
        assert owners == [("asset_record",)]
    finally:
        con.close()


def test_missing_external_node_fails_global_validation(tmp_path):
    code = base_record(
        "code_record",
        [
            {
                "id": "function:0129:1",
                "kind": "function",
                "status": "CANDIDATE",
                "attrs": {},
            }
        ],
        external_nodes=[{"id": "material:DOES_NOT_EXIST"}],
        edges=[
            {
                "id": "bad_edge",
                "subject": "function:0129:1",
                "predicate": "CONSUMES_RESOURCE_CLASS",
                "object": "material:DOES_NOT_EXIST",
                "status": "CANDIDATE",
                "assertion_ids": [],
                "attrs": {},
            }
        ],
    )
    records = [write(tmp_path / "code.json", code)]
    try:
        mod.validate_all(records)
    except ValueError as exc:
        assert "not declared by any knowledge record" in str(exc)
    else:
        raise AssertionError("unresolved external node must fail closed")


def test_target_record_must_own_external_node(tmp_path):
    asset = base_record(
        "asset_record",
        [
            {
                "id": "material:REAL",
                "kind": "material",
                "status": "PROVEN",
                "attrs": {},
            }
        ],
    )
    code = base_record(
        "code_record",
        [
            {
                "id": "function:0129:1",
                "kind": "function",
                "status": "CANDIDATE",
                "attrs": {},
            }
        ],
        external_nodes=[
            {"id": "material:OTHER", "record_id": "asset_record"}
        ],
    )
    records = [
        write(tmp_path / "asset.json", asset),
        write(tmp_path / "code.json", code),
    ]
    try:
        mod.validate_all(records)
    except ValueError as exc:
        assert "is not declared by target record" in str(exc)
    else:
        raise AssertionError("target record ownership mismatch must fail closed")
