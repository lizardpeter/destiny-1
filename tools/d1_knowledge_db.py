#!/usr/bin/env python3
"""Validate Git-friendly D1 reversal knowledge records and build SQLite.

Canonical data lives under knowledge/records/*.json. The SQLite database is a
generated query surface and should not be treated as the source of truth.

The validator deliberately enforces proof-state and referential-integrity rules
without third-party dependencies so it can run in every GitHub Actions job.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

SCHEMA = "d1_knowledge_record/v1"
STATUSES = {
    "PROVEN",
    "STRONGLY_SUPPORTED",
    "CANDIDATE",
    "UNRESOLVED",
    "REJECTED",
    "TARGET",
}
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def load_records(root: Path) -> list[tuple[Path, dict]]:
    files = sorted(p for p in root.glob("*.json") if p.is_file())
    if not files:
        raise ValueError(f"no knowledge records found under {root}")
    out = []
    for path in files:
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except Exception as ex:
            raise ValueError(f"{path}: invalid JSON: {ex}") from ex
        out.append((path, doc))
    return out


def require_string(obj: dict, key: str, errors: list[str], where: str) -> str | None:
    value = obj.get(key)
    if not isinstance(value, str) or not value:
        errors.append(f"{where}: {key} must be a non-empty string")
        return None
    return value


def unique_ids(rows: object, key: str, errors: list[str], where: str) -> set[str]:
    if not isinstance(rows, list):
        errors.append(f"{where} must be an array")
        return set()
    seen: set[str] = set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"{where}[{i}] must be an object")
            continue
        value = row.get(key)
        if not isinstance(value, str) or not value:
            errors.append(f"{where}[{i}].{key} must be a non-empty string")
            continue
        if value in seen:
            errors.append(f"{where}: duplicate {key} {value}")
        seen.add(value)
    return seen


def validate_status(row: dict, errors: list[str], where: str) -> None:
    status = row.get("status")
    if status not in STATUSES:
        errors.append(f"{where}: invalid status {status!r}; allowed={sorted(STATUSES)}")


def validate_record(path: Path, doc: dict) -> list[str]:
    errors: list[str] = []
    prefix = str(path)
    if not isinstance(doc, dict):
        return [f"{prefix}: top level must be an object"]
    if doc.get("schema") != SCHEMA:
        errors.append(f"{prefix}: schema must be {SCHEMA!r}")
    record_id = require_string(doc, "record_id", errors, prefix)
    require_string(doc, "title", errors, prefix)
    require_string(doc, "updated_utc", errors, prefix)

    for key in ("nodes", "edges", "assertions", "sources", "rejections", "frontiers"):
        if key not in doc:
            errors.append(f"{prefix}: missing required array {key}")
        elif not isinstance(doc[key], list):
            errors.append(f"{prefix}: {key} must be an array")

    node_ids = unique_ids(doc.get("nodes", []), "id", errors, f"{prefix}:nodes")
    edge_ids = unique_ids(doc.get("edges", []), "id", errors, f"{prefix}:edges")
    assertion_ids = unique_ids(doc.get("assertions", []), "id", errors, f"{prefix}:assertions")
    source_ids = unique_ids(doc.get("sources", []), "id", errors, f"{prefix}:sources")
    rejection_ids = unique_ids(doc.get("rejections", []), "id", errors, f"{prefix}:rejections")
    frontier_ids = unique_ids(doc.get("frontiers", []), "id", errors, f"{prefix}:frontiers")
    _ = (record_id, edge_ids, rejection_ids, frontier_ids)

    for i, row in enumerate(doc.get("nodes", [])):
        if not isinstance(row, dict):
            continue
        where = f"{prefix}:nodes[{i}]"
        require_string(row, "kind", errors, where)
        validate_status(row, errors, where)
        attrs = row.get("attrs", {})
        if not isinstance(attrs, dict):
            errors.append(f"{where}: attrs must be an object when present")

    for i, row in enumerate(doc.get("assertions", [])):
        if not isinstance(row, dict):
            continue
        where = f"{prefix}:assertions[{i}]"
        validate_status(row, errors, where)
        require_string(row, "claim", errors, where)
        refs = row.get("source_ids")
        if not isinstance(refs, list):
            errors.append(f"{where}: source_ids must be an array")
        else:
            for source_id in refs:
                if source_id not in source_ids:
                    errors.append(f"{where}: unknown source_id {source_id!r}")
        if not isinstance(row.get("details", {}), dict):
            errors.append(f"{where}: details must be an object when present")

    for i, row in enumerate(doc.get("sources", [])):
        if not isinstance(row, dict):
            continue
        where = f"{prefix}:sources[{i}]"
        require_string(row, "kind", errors, where)
        require_string(row, "locator", errors, where)
        sha = row.get("sha256")
        if sha is not None and (not isinstance(sha, str) or not SHA256_RE.fullmatch(sha)):
            errors.append(f"{where}: sha256 must be 64 hexadecimal characters or null")
        if not isinstance(row.get("details", {}), dict):
            errors.append(f"{where}: details must be an object when present")

    for i, row in enumerate(doc.get("edges", [])):
        if not isinstance(row, dict):
            continue
        where = f"{prefix}:edges[{i}]"
        subject = require_string(row, "subject", errors, where)
        predicate = require_string(row, "predicate", errors, where)
        obj = require_string(row, "object", errors, where)
        _ = predicate
        validate_status(row, errors, where)
        if subject and subject not in node_ids:
            errors.append(f"{where}: subject {subject!r} is not a node in this record")
        if obj and obj not in node_ids:
            errors.append(f"{where}: object {obj!r} is not a node in this record")
        refs = row.get("assertion_ids", [])
        if not isinstance(refs, list):
            errors.append(f"{where}: assertion_ids must be an array")
        else:
            for assertion_id in refs:
                if assertion_id not in assertion_ids:
                    errors.append(f"{where}: unknown assertion_id {assertion_id!r}")
        if not isinstance(row.get("attrs", {}), dict):
            errors.append(f"{where}: attrs must be an object when present")

    for i, row in enumerate(doc.get("rejections", [])):
        if not isinstance(row, dict):
            continue
        where = f"{prefix}:rejections[{i}]"
        candidate = require_string(row, "candidate_node", errors, where)
        rejected_as = require_string(row, "rejected_as", errors, where)
        require_string(row, "reason", errors, where)
        if candidate and candidate not in node_ids:
            errors.append(f"{where}: candidate_node {candidate!r} is not a node in this record")
        if rejected_as and rejected_as not in node_ids:
            errors.append(f"{where}: rejected_as {rejected_as!r} is not a node in this record")
        refs = row.get("assertion_ids")
        if not isinstance(refs, list):
            errors.append(f"{where}: assertion_ids must be an array")
        else:
            for assertion_id in refs:
                if assertion_id not in assertion_ids:
                    errors.append(f"{where}: unknown assertion_id {assertion_id!r}")

    for i, row in enumerate(doc.get("frontiers", [])):
        if not isinstance(row, dict):
            continue
        where = f"{prefix}:frontiers[{i}]"
        require_string(row, "question", errors, where)
        require_string(row, "next_proof", errors, where)
        refs = row.get("related_nodes", [])
        if not isinstance(refs, list):
            errors.append(f"{where}: related_nodes must be an array")
        else:
            for node_id in refs:
                if node_id not in node_ids:
                    errors.append(f"{where}: unknown related node {node_id!r}")

    return errors


def validate_all(records: list[tuple[Path, dict]]) -> None:
    errors: list[str] = []
    record_ids: dict[str, Path] = {}
    for path, doc in records:
        errors.extend(validate_record(path, doc))
        rid = doc.get("record_id") if isinstance(doc, dict) else None
        if isinstance(rid, str):
            old = record_ids.get(rid)
            if old is not None:
                errors.append(f"duplicate record_id {rid!r}: {old} and {path}")
            else:
                record_ids[rid] = path
    if errors:
        raise ValueError("knowledge validation failed:\n" + "\n".join(f"- {x}" for x in errors))


def jd(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def build_db(records: list[tuple[Path, dict]], db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    try:
        con.executescript(
            """
            PRAGMA foreign_keys=ON;
            PRAGMA user_version=1;
            CREATE TABLE records(
              record_id TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              updated_utc TEXT NOT NULL,
              source_path TEXT NOT NULL,
              source_sha256 TEXT NOT NULL,
              scope_json TEXT NOT NULL
            );
            CREATE TABLE nodes(
              record_id TEXT NOT NULL,
              node_id TEXT NOT NULL,
              kind TEXT NOT NULL,
              status TEXT NOT NULL,
              label TEXT,
              attrs_json TEXT NOT NULL,
              PRIMARY KEY(record_id,node_id),
              FOREIGN KEY(record_id) REFERENCES records(record_id) ON DELETE CASCADE
            );
            CREATE TABLE assertions(
              record_id TEXT NOT NULL,
              assertion_id TEXT NOT NULL,
              status TEXT NOT NULL,
              claim TEXT NOT NULL,
              details_json TEXT NOT NULL,
              PRIMARY KEY(record_id,assertion_id),
              FOREIGN KEY(record_id) REFERENCES records(record_id) ON DELETE CASCADE
            );
            CREATE TABLE sources(
              record_id TEXT NOT NULL,
              source_id TEXT NOT NULL,
              kind TEXT NOT NULL,
              locator TEXT NOT NULL,
              sha256 TEXT,
              details_json TEXT NOT NULL,
              PRIMARY KEY(record_id,source_id),
              FOREIGN KEY(record_id) REFERENCES records(record_id) ON DELETE CASCADE
            );
            CREATE TABLE assertion_sources(
              record_id TEXT NOT NULL,
              assertion_id TEXT NOT NULL,
              source_id TEXT NOT NULL,
              PRIMARY KEY(record_id,assertion_id,source_id),
              FOREIGN KEY(record_id,assertion_id) REFERENCES assertions(record_id,assertion_id) ON DELETE CASCADE,
              FOREIGN KEY(record_id,source_id) REFERENCES sources(record_id,source_id) ON DELETE CASCADE
            );
            CREATE TABLE edges(
              record_id TEXT NOT NULL,
              edge_id TEXT NOT NULL,
              subject_id TEXT NOT NULL,
              predicate TEXT NOT NULL,
              object_id TEXT NOT NULL,
              status TEXT NOT NULL,
              attrs_json TEXT NOT NULL,
              PRIMARY KEY(record_id,edge_id),
              FOREIGN KEY(record_id,subject_id) REFERENCES nodes(record_id,node_id),
              FOREIGN KEY(record_id,object_id) REFERENCES nodes(record_id,node_id)
            );
            CREATE TABLE edge_assertions(
              record_id TEXT NOT NULL,
              edge_id TEXT NOT NULL,
              assertion_id TEXT NOT NULL,
              PRIMARY KEY(record_id,edge_id,assertion_id),
              FOREIGN KEY(record_id,edge_id) REFERENCES edges(record_id,edge_id) ON DELETE CASCADE,
              FOREIGN KEY(record_id,assertion_id) REFERENCES assertions(record_id,assertion_id) ON DELETE CASCADE
            );
            CREATE TABLE rejections(
              record_id TEXT NOT NULL,
              rejection_id TEXT NOT NULL,
              candidate_node_id TEXT NOT NULL,
              rejected_as TEXT NOT NULL,
              reason TEXT NOT NULL,
              PRIMARY KEY(record_id,rejection_id),
              FOREIGN KEY(record_id,candidate_node_id) REFERENCES nodes(record_id,node_id),
              FOREIGN KEY(record_id,rejected_as) REFERENCES nodes(record_id,node_id)
            );
            CREATE TABLE rejection_assertions(
              record_id TEXT NOT NULL,
              rejection_id TEXT NOT NULL,
              assertion_id TEXT NOT NULL,
              PRIMARY KEY(record_id,rejection_id,assertion_id),
              FOREIGN KEY(record_id,rejection_id) REFERENCES rejections(record_id,rejection_id) ON DELETE CASCADE,
              FOREIGN KEY(record_id,assertion_id) REFERENCES assertions(record_id,assertion_id) ON DELETE CASCADE
            );
            CREATE TABLE frontiers(
              record_id TEXT NOT NULL,
              frontier_id TEXT NOT NULL,
              question TEXT NOT NULL,
              next_proof TEXT NOT NULL,
              PRIMARY KEY(record_id,frontier_id),
              FOREIGN KEY(record_id) REFERENCES records(record_id) ON DELETE CASCADE
            );
            CREATE TABLE frontier_nodes(
              record_id TEXT NOT NULL,
              frontier_id TEXT NOT NULL,
              node_id TEXT NOT NULL,
              PRIMARY KEY(record_id,frontier_id,node_id),
              FOREIGN KEY(record_id,frontier_id) REFERENCES frontiers(record_id,frontier_id) ON DELETE CASCADE,
              FOREIGN KEY(record_id,node_id) REFERENCES nodes(record_id,node_id)
            );
            CREATE INDEX idx_nodes_node_id ON nodes(node_id);
            CREATE INDEX idx_nodes_kind ON nodes(kind);
            CREATE INDEX idx_nodes_status ON nodes(status);
            CREATE INDEX idx_edges_subject ON edges(subject_id);
            CREATE INDEX idx_edges_object ON edges(object_id);
            CREATE INDEX idx_edges_predicate ON edges(predicate);
            CREATE INDEX idx_edges_status ON edges(status);
            CREATE INDEX idx_assertions_status ON assertions(status);
            CREATE INDEX idx_sources_sha256 ON sources(sha256);
            """
        )

        for path, doc in records:
            rid = doc["record_id"]
            source_sha = hashlib.sha256(path.read_bytes()).hexdigest()
            con.execute(
                "INSERT INTO records VALUES (?,?,?,?,?,?)",
                (rid, doc["title"], doc["updated_utc"], str(path), source_sha, jd(doc.get("scope", {}))),
            )
            for row in doc["nodes"]:
                con.execute(
                    "INSERT INTO nodes VALUES (?,?,?,?,?,?)",
                    (rid, row["id"], row["kind"], row["status"], row.get("label"), jd(row.get("attrs", {}))),
                )
            for row in doc["assertions"]:
                con.execute(
                    "INSERT INTO assertions VALUES (?,?,?,?,?)",
                    (rid, row["id"], row["status"], row["claim"], jd(row.get("details", {}))),
                )
            for row in doc["sources"]:
                con.execute(
                    "INSERT INTO sources VALUES (?,?,?,?,?,?)",
                    (rid, row["id"], row["kind"], row["locator"], row.get("sha256"), jd(row.get("details", {}))),
                )
            for row in doc["assertions"]:
                for source_id in row.get("source_ids", []):
                    con.execute("INSERT INTO assertion_sources VALUES (?,?,?)", (rid, row["id"], source_id))
            for row in doc["edges"]:
                con.execute(
                    "INSERT INTO edges VALUES (?,?,?,?,?,?,?)",
                    (rid, row["id"], row["subject"], row["predicate"], row["object"], row["status"], jd(row.get("attrs", {}))),
                )
                for assertion_id in row.get("assertion_ids", []):
                    con.execute("INSERT INTO edge_assertions VALUES (?,?,?)", (rid, row["id"], assertion_id))
            for row in doc["rejections"]:
                con.execute(
                    "INSERT INTO rejections VALUES (?,?,?,?,?)",
                    (rid, row["id"], row["candidate_node"], row["rejected_as"], row["reason"]),
                )
                for assertion_id in row["assertion_ids"]:
                    con.execute("INSERT INTO rejection_assertions VALUES (?,?,?)", (rid, row["id"], assertion_id))
            for row in doc["frontiers"]:
                con.execute(
                    "INSERT INTO frontiers VALUES (?,?,?,?)",
                    (rid, row["id"], row["question"], row["next_proof"]),
                )
                for node_id in row.get("related_nodes", []):
                    con.execute("INSERT INTO frontier_nodes VALUES (?,?,?)", (rid, row["id"], node_id))
        con.commit()
        result = con.execute("PRAGMA foreign_key_check").fetchall()
        if result:
            raise ValueError(f"SQLite foreign-key validation failed: {result[:20]}")
    finally:
        con.close()


def summary(records: list[tuple[Path, dict]], db_path: Path | None) -> dict:
    node_kinds = Counter()
    node_statuses = Counter()
    edge_predicates = Counter()
    assertion_statuses = Counter()
    totals = Counter()
    for _, doc in records:
        totals["records"] += 1
        for row in doc["nodes"]:
            totals["nodes"] += 1
            node_kinds[row["kind"]] += 1
            node_statuses[row["status"]] += 1
        for row in doc["edges"]:
            totals["edges"] += 1
            edge_predicates[row["predicate"]] += 1
        for row in doc["assertions"]:
            totals["assertions"] += 1
            assertion_statuses[row["status"]] += 1
        totals["sources"] += len(doc["sources"])
        totals["rejections"] += len(doc["rejections"])
        totals["frontiers"] += len(doc["frontiers"])
    out = {
        "schema": "d1_knowledge_db_summary/v1",
        "status": "D1_KNOWLEDGE_DB_VALID",
        **dict(totals),
        "node_kind_counts": dict(sorted(node_kinds.items())),
        "node_status_counts": dict(sorted(node_statuses.items())),
        "edge_predicate_counts": dict(sorted(edge_predicates.items())),
        "assertion_status_counts": dict(sorted(assertion_statuses.items())),
    }
    if db_path is not None and db_path.exists():
        out["sqlite_path"] = str(db_path)
        out["sqlite_sha256"] = hashlib.sha256(db_path.read_bytes()).hexdigest()
        out["sqlite_bytes"] = db_path.stat().st_size
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", type=Path, default=Path("knowledge/records"))
    ap.add_argument("--db", type=Path)
    ap.add_argument("--summary", type=Path)
    ap.add_argument("--validate-only", action="store_true")
    a = ap.parse_args()

    try:
        records = load_records(a.records)
        validate_all(records)
        if a.validate_only:
            out = summary(records, None)
        else:
            if a.db is None:
                raise ValueError("--db is required unless --validate-only is used")
            build_db(records, a.db)
            out = summary(records, a.db)
        if a.summary:
            a.summary.parent.mkdir(parents=True, exist_ok=True)
            a.summary.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(out, indent=2))
        return 0
    except Exception as ex:
        print(str(ex), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
