#!/usr/bin/env python3
"""Stamp and validate reusable Destiny 1 extraction checkpoints.

The goal is selective invalidation rather than either extreme:

* never trust an old extraction merely because it exists;
* never regenerate expensive source-derived layers when none of their inputs or
  semantics changed.

Compatibility is based on the inputs that can actually change the checkpoint:
source fingerprints, hashes of the exact producer/dependency files, explicit schema
and semantic revision labels, and hashes of upstream checkpoint manifests.  The
producer Git commit is recorded for provenance but is intentionally *not* itself a
compatibility key, because unrelated repository commits must not invalidate a valid
checkpoint.

Typical use:

  # when producing a checkpoint
  d1_checkpoint_manifest.py stamp --layer entity_closure --schema v3 \
      --source packages_txt=<sha256> --semantic-revision entity-resource-v7 \
      --dependency tools/d1_remote_entity_dependency_closure_universal.py \
      --dependency tools/d1_entity_resource_probe.py \
      -o out/CHECKPOINT.json

  # before reusing it later
  d1_checkpoint_manifest.py validate --manifest cached/CHECKPOINT.json \
      --layer entity_closure --schema v3 --source packages_txt=<sha256> \
      --semantic-revision entity-resource-v7 \
      --dependency tools/d1_remote_entity_dependency_closure_universal.py \
      --dependency tools/d1_entity_resource_probe.py

A mismatch exits 2 and reports every invalidating field.  This tool never decides
semantic ownership itself; it only makes checkpoint staleness explicit and auditable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

SCHEMA = "d1_checkpoint_manifest/v1"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_kv(rows: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in rows:
        if "=" not in raw:
            raise ValueError(f"expected NAME=VALUE, got {raw!r}")
        k, v = raw.split("=", 1)
        k = k.strip()
        if not k:
            raise ValueError(f"empty key in {raw!r}")
        if k in out and out[k] != v:
            raise ValueError(f"duplicate key {k!r} with conflicting values")
        out[k] = v
    return dict(sorted(out.items()))


def current_git_sha() -> str | None:
    env = os.environ.get("GITHUB_SHA")
    if env:
        return env
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None


def dependency_map(paths: list[Path]) -> dict[str, str]:
    out: dict[str, str] = {}
    for p in paths:
        rp = p.resolve()
        if not rp.is_file():
            raise FileNotFoundError(p)
        try:
            key = str(rp.relative_to(Path.cwd().resolve()))
        except ValueError:
            key = str(rp)
        out[key.replace("\\", "/")] = sha256_file(rp)
    return dict(sorted(out.items()))


def upstream_map(paths: list[Path]) -> dict[str, str]:
    out: dict[str, str] = {}
    for p in paths:
        if not p.is_file():
            raise FileNotFoundError(p)
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("schema") != SCHEMA:
            raise ValueError(f"upstream {p} is not {SCHEMA}")
        out[p.name] = sha256_file(p)
    return dict(sorted(out.items()))


def expected_from_args(a: argparse.Namespace) -> dict:
    return {
        "layer": a.layer,
        "checkpoint_schema": a.schema_version,
        "semantic_revision": a.semantic_revision,
        "source_fingerprints": parse_kv(a.source),
        "dependency_sha256": dependency_map(a.dependency),
        "upstream_manifest_sha256": upstream_map(a.upstream_manifest),
    }


def stamp(a: argparse.Namespace) -> int:
    core = expected_from_args(a)
    out = {
        "schema": SCHEMA,
        "status": "D1_CHECKPOINT_COMPATIBILITY_STAMPED",
        **core,
        "producer_git_sha": current_git_sha(),
        "artifact_fingerprints": parse_kv(a.artifact),
        "policy": (
            "Reusable only while source_fingerprints, checkpoint_schema, semantic_revision, "
            "dependency_sha256 and upstream_manifest_sha256 all match the current requested "
            "pipeline. producer_git_sha is provenance only and does not invalidate a checkpoint "
            "when unrelated repository files change."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in (
        "status", "layer", "checkpoint_schema", "semantic_revision",
        "source_fingerprints", "dependency_sha256", "upstream_manifest_sha256",
        "producer_git_sha"
    )}, indent=2))
    return 0


def validate(a: argparse.Namespace) -> int:
    got = json.loads(a.manifest.read_text(encoding="utf-8"))
    expected = expected_from_args(a)
    mismatches: list[dict] = []
    if got.get("schema") != SCHEMA:
        mismatches.append({"field": "schema", "cached": got.get("schema"), "current": SCHEMA})
    for key, cur in expected.items():
        old = got.get(key)
        if old != cur:
            mismatches.append({"field": key, "cached": old, "current": cur})
    result = {
        "schema": "d1_checkpoint_validation/v1",
        "status": "D1_CHECKPOINT_REUSABLE" if not mismatches else "D1_CHECKPOINT_STALE",
        "manifest": str(a.manifest),
        "layer": a.layer,
        "cached_producer_git_sha": got.get("producer_git_sha"),
        "current_git_sha": current_git_sha(),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
    }
    print(json.dumps(result, indent=2))
    return 0 if not mismatches else 2


def add_common(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("--layer", required=True)
    ap.add_argument("--schema", dest="schema_version", required=True)
    ap.add_argument("--semantic-revision", required=True)
    ap.add_argument("--source", action="append", default=[], metavar="NAME=VALUE")
    ap.add_argument("--dependency", type=Path, action="append", default=[])
    ap.add_argument("--upstream-manifest", type=Path, action="append", default=[])


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("stamp")
    add_common(sp)
    sp.add_argument("--artifact", action="append", default=[], metavar="NAME=SHA256")
    sp.add_argument("-o", "--output", type=Path, required=True)
    vp = sub.add_parser("validate")
    add_common(vp)
    vp.add_argument("--manifest", type=Path, required=True)
    a = ap.parse_args()
    return stamp(a) if a.cmd == "stamp" else validate(a)


if __name__ == "__main__":
    raise SystemExit(main())
