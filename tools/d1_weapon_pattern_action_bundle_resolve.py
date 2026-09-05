#!/usr/bin/env python3
"""Resolve action/context bundles serialized by D1 weapon sandbox patterns.

Each retail weapon-pattern index is already joined to an exact sandbox-pattern
`s_entity` by d1_weapon_pattern_assignment_probe.py.  That s_entity contains a
Resource[] of cross-package FileHashes.  Some of those resources are structured
EntityResources which themselves serialize an action-control/context/wrapper
triple, e.g. the Gjallarhorn pattern-39 resource 80AAECD6 contains:

    80AA2DCD -> 80802C0E
    80AADE4C -> 80800368
    80AA2DDB -> 8080222A

This resolver performs that discovery for every supplied weapon pattern.  It
uses FileHash package/id routing and exact entry references only.  No adjacency
or weapon-type inference is used.
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_investment_arrangement_probe import filehash_pkg_index
from d1_remote_investment_parent_probe import RemoteLogicalPackage, parse_member
from d1_remote_s_entity_resource_package_find import parse_entity_resources
from d1_split_tar_extract import SplitHttpTar

ACTION_CONTROL_REF = "80802C0E"
ACTION_WRAPPER_REF = "8080222A"
CONTEXT_TABLE_REF = "80800368"
INTERESTING_REFS = {ACTION_CONTROL_REF, ACTION_WRAPPER_REF, CONTEXT_TABLE_REF}


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from("<I", b, o)[0]


def load_member_catalog(path: Path, needed: set[int] | None = None) -> dict[int, list]:
    src = json.loads(path.read_text())
    out = {}
    for key, rows in src.get("families", {}).items():
        pkg = int(key, 16)
        if needed is not None and pkg not in needed:
            continue
        specs = []
        for row in rows:
            off = int(str(row["data_offset"]), 0)
            spec = parse_member(f"{row['name']}:0x{off:X}:{int(row['size'])}")
            if spec.pkg_id != pkg:
                raise ValueError(f"catalog {path}: {key} contains mismatched member {row['name']}")
            specs.append(spec)
        out[pkg] = specs
    if needed is not None:
        missing = sorted(needed - set(out))
        if missing:
            raise ValueError(f"catalog {path} missing package ids {[f'{x:04X}' for x in missing]}")
    return out


def entry_exact(remote: RemoteLogicalPackage, value: int):
    pkg, idx = filehash_pkg_index(value)
    if pkg != remote.h["pkg_id"] if hasattr(remote, "h") else False:
        return None
    if idx >= len(remote.entries):
        return None
    e = remote.entries[idx]
    if int(e["tag_hash"], 16) != value:
        return None
    return e


def exact_entry(remotes: dict[int, RemoteLogicalPackage], value: int):
    pkg, idx = filehash_pkg_index(value)
    r = remotes.get(pkg)
    if r is None or idx >= len(r.entries):
        return None
    e = r.entries[idx]
    if int(e["tag_hash"], 16) != value:
        return None
    return r, e


def scan_resource_payload(b: bytes, globals_remotes: dict[int, RemoteLogicalPackage]) -> list[dict]:
    hits = []
    for off in range(0, len(b) - 3, 4):
        v = u32(b, off)
        q = exact_entry(globals_remotes, v)
        if q is None:
            continue
        _, e = q
        ref = e["reference"].upper()
        if ref in INTERESTING_REFS:
            hits.append({
                "offset": off,
                "tag_hash": f"{v:08X}",
                "reference": ref,
                "entry_index": e["index"],
                "size": e["file_size"],
            })
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("weapon_patterns_json", type=Path)
    ap.add_argument("--investment-member-catalog", type=Path, required=True)
    ap.add_argument("--globals-member-catalog", type=Path, required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    src = json.loads(args.weapon_patterns_json.read_text())
    patterns = [x for x in src.get("patterns", []) if x.get("sandbox_assignment_found") and x.get("entity_relation_hash")]
    pattern_pkgs = {int(x["entity_relation_package_id"]) for x in patterns}

    inv_specs = load_member_catalog(args.investment_member_catalog, pattern_pkgs)
    global_specs = load_member_catalog(args.globals_member_catalog)
    base = args.base_url.rstrip("/")
    arc = SplitHttpTar([f"{base}/packages.tar.{i:03d}" for i in range(1, args.part_count + 1)], retries=6, timeout=90)

    investment = {pkg: RemoteLogicalPackage(arc, {m.patch_id: m for m in specs}, args.runtime) for pkg, specs in inv_specs.items()}
    globals_remotes = {pkg: RemoteLogicalPackage(arc, {m.patch_id: m for m in specs}, args.runtime) for pkg, specs in global_specs.items()}

    reports = []
    bundle_count = 0
    resource_class_counts = collections.Counter()
    errors = []
    for n, p in enumerate(patterns, 1):
        entity_hash = p["entity_relation_hash"].upper()
        pkg, idx = filehash_pkg_index(int(entity_hash, 16))
        r = investment[pkg]
        row = {
            "weapon_pattern_index": p["weapon_pattern_index"],
            "pattern_global_tag_id_hash": p["pattern_global_tag_id_hash"],
            "weapon_type_hash": p["weapon_type_hash"],
            "pattern_hash": p["pattern_hash"],
            "pattern_entity": entity_hash,
            "pattern_entity_package_id": pkg,
            "pattern_entity_file_index": idx,
            "resources": [],
            "action_bundles": [],
        }
        try:
            if idx >= len(r.entries):
                raise ValueError("pattern entity index beyond package")
            e = r.entries[idx]
            if e["tag_hash"].upper() != entity_hash:
                raise ValueError(f"pattern entity entry mismatch {e['tag_hash']}")
            if e["reference"].upper() != "80800734":
                raise ValueError(f"pattern entity reference {e['reference']} is not s_entity")
            b = r.entry(idx)
            resources = parse_entity_resources(b)
            for rr in resources:
                rh = rr["resource_hash"]
                rpkg = rr["resource_package_id"]
                rec = dict(rr)
                if rpkg in globals_remotes and rh not in ("00000000", "FFFFFFFF"):
                    q = exact_entry(globals_remotes, int(rh, 16))
                    if q is None:
                        rec["read_status"] = "global_entry_not_exact"
                    else:
                        gr, ge = q
                        rec["entry_reference"] = ge["reference"].upper()
                        rec["entry_size"] = ge["file_size"]
                        resource_class_counts[ge["reference"].upper()] += 1
                        try:
                            gb = gr.entry(ge["index"])
                            hits = scan_resource_payload(gb, globals_remotes)
                            rec["interesting_serialized_refs"] = hits
                            byref = collections.defaultdict(list)
                            for h in hits:
                                byref[h["reference"]].append(h["tag_hash"])
                            controls = list(dict.fromkeys(byref[ACTION_CONTROL_REF]))
                            wrappers = list(dict.fromkeys(byref[ACTION_WRAPPER_REF]))
                            contexts = list(dict.fromkeys(byref[CONTEXT_TABLE_REF]))
                            if controls and wrappers and contexts:
                                bundle = {
                                    "carrier_resource": rh,
                                    "carrier_reference": ge["reference"].upper(),
                                    "action_controls": controls,
                                    "wrappers": wrappers,
                                    "context_tables": contexts,
                                    "serialized_hits": hits,
                                }
                                row["action_bundles"].append(bundle)
                                bundle_count += 1
                        except Exception as ex:
                            rec["read_error"] = repr(ex)
                row["resources"].append(rec)
        except Exception as ex:
            row["error"] = repr(ex)
            errors.append({"weapon_pattern_index": p["weapon_pattern_index"], "pattern_entity": entity_hash, "error": repr(ex)})
        reports.append(row)
        if n % 25 == 0:
            print(f"patterns {n}/{len(patterns)} bundles={bundle_count}", flush=True)

    patterns_with_bundle = sum(bool(x["action_bundles"]) for x in reports)
    out = {
        "schema": "d1_weapon_pattern_action_bundle_resolution/v1",
        "pattern_count": len(reports),
        "patterns_with_action_bundle": patterns_with_bundle,
        "patterns_without_action_bundle": len(reports) - patterns_with_bundle,
        "total_action_bundle_candidates": bundle_count,
        "resource_reference_counts": dict(resource_class_counts),
        "patterns": reports,
        "errors": errors[:500],
        "remote_block_cache_sizes": {
            "investment": {f"{p:04X}": len(r.block_cache) for p, r in investment.items()},
            "globals": {f"{p:04X}": len(r.block_cache) for p, r in globals_remotes.items()},
        },
        "evidence_policy": "Pattern entities come from the retail weapon-pattern assignment join. Resource FileHashes come from each s_entity Resource[]. Bundle controls/context/wrappers must be serialized inside the referenced resource payload and resolve to exact global entries.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k not in ("patterns", "errors", "remote_block_cache_sizes", "resource_reference_counts")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
