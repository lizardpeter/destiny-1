#!/usr/bin/env python3
"""Census D1 Investment EntityParents that resolve into selected Hive packages.

Source-closed chain:

  80A7E1DD EntityArrangementMap
    assignment_hash -> EntityParent FileHash
  EntityParent +0x10
    -> final EntityDataROI FileHash

The tool opens every parent through its encoded verified package family and admits a
hit only when the final FileHash decodes to one of --target-package-id.  It then
resolves the final tag itself and records its exact class/type/subtype/size.  No
assignment hash, string, package locality, or model resemblance is treated as actor
identity.

This is intended for the Crota/Hive archetype investigation but is package-generic.
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from d1_filehash import decode_int, plausible_int
from d1_investment_arrangement_probe import parse_assignment_map
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_model_tgxm_signature_match import LazyExactHashResolver
from d1_split_tar_extract import SplitHttpTar

ASSIGNMENT_MAP = "80A7E1DD"
NULLS = {0, 0xFFFFFFFF}


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def parts(v: int) -> tuple[int, int]:
    if not plausible_int(v):
        raise ValueError(f"not a plausible D1 FileHash: {v:08X}")
    return decode_int(v)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--member-catalog", type=Path, action="append", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--investment-package-id", action="append", type=lambda x: int(x, 0), default=[])
    ap.add_argument("--target-package-id", action="append", type=lambda x: int(x, 0), required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    cats = load_catalogs(a.member_catalog)
    allowed_parent_pkgs = set(a.investment_package_id)
    if not allowed_parent_pkgs:
        # D1 ROI Investment asset families observed in the exact arrangement corpus.
        allowed_parent_pkgs = {x for x in range(0x0135, 0x0147) if x in cats}
    missing_parent = sorted(x for x in allowed_parent_pkgs if x not in cats)
    if missing_parent:
        raise SystemExit("missing verified Investment package catalogs: " + ",".join(f"{x:04X}" for x in missing_parent))
    targets = set(a.target_package_id)
    missing_targets = sorted(x for x in targets if x not in cats)
    if missing_targets:
        raise SystemExit("missing verified target package catalogs: " + ",".join(f"{x:04X}" for x in missing_targets))

    base = a.base_url.rstrip("/")
    arc = SplitHttpTar([f"{base}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    resolver = LazyExactHashResolver(arc, cats, a.runtime)

    _mv, me, mb = resolver.bytes(ASSIGNMENT_MAP)
    amap = parse_assignment_map(mb)
    parent_to_assignments: dict[int, list[int]] = collections.defaultdict(list)
    invalid_parent_hashes = []
    for assignment, parent in amap.items():
        if parent in NULLS:
            continue
        try:
            ppkg, _ = parts(parent)
        except Exception as ex:
            invalid_parent_hashes.append({"assignment": f"{assignment:08X}", "parent": f"{parent:08X}", "error": repr(ex)})
            continue
        if ppkg in allowed_parent_pkgs:
            parent_to_assignments[parent].append(assignment)

    hits = []
    errors = []
    final_package_counts = collections.Counter()
    final_class_counts = collections.Counter()
    final_hash_counts = collections.Counter()
    parent_pkg_counts = collections.Counter()

    for n, parent in enumerate(sorted(parent_to_assignments), 1):
        ph = f"{parent:08X}"
        try:
            ppkg, pidx = parts(parent)
            parent_pkg_counts[ppkg] += 1
            pv, pe, pb = resolver.bytes(ph)
            if len(pb) < 0x14:
                raise ValueError(f"EntityParent payload too short: {len(pb)}")
            final = struct.unpack_from("<I", pb, 0x10)[0]
            if final in NULLS:
                continue
            fpkg, fidx = parts(final)
            final_package_counts[fpkg] += 1
            if fpkg not in targets:
                continue
            fh = f"{final:08X}"
            fv, fe = resolver.locate(fh)
            ref = norm(fe.get("reference", "FFFFFFFF"))
            final_class_counts[ref] += 1
            final_hash_counts[fh] += 1
            row = {
                "parent_hash": ph,
                "parent_package_id": f"{ppkg:04X}",
                "parent_file_index": pidx,
                "parent_reference": norm(pe.get("reference", "FFFFFFFF")),
                "parent_size": int(pe.get("file_size", 0)),
                "assignment_hashes": [f"{x:08X}" for x in sorted(parent_to_assignments[parent])],
                "final_entity_data_hash": fh,
                "final_package_id": f"{fpkg:04X}",
                "final_file_index": fidx,
                "final_reference": ref,
                "final_type": int(fe.get("type", -1)),
                "final_subtype": int(fe.get("subtype", -1)),
                "final_size": int(fe.get("file_size", 0)),
            }
            hits.append(row)
            print("HIVE_PARENT", n, "/", len(parent_to_assignments), json.dumps(row, separators=(",", ":")), flush=True)
        except Exception as ex:
            errors.append({"parent_hash": ph, "error": repr(ex)})
        if n % 500 == 0:
            print("PROGRESS", n, "/", len(parent_to_assignments), "HITS", len(hits), "ERRORS", len(errors), flush=True)

    unique_final_sentities = sorted({x["final_entity_data_hash"] for x in hits if x["final_reference"] == "80800734"})
    out = {
        "schema": "d1_remote_investment_hive_parent_census/v1",
        "status": "D1_REMOTE_INVESTMENT_HIVE_PARENT_CENSUS_COMPLETE" if not errors and not invalid_parent_hashes else "D1_REMOTE_INVESTMENT_HIVE_PARENT_CENSUS_WITH_ERRORS",
        "assignment_map": {
            "tag_hash": ASSIGNMENT_MAP,
            "reference": norm(me.get("reference", "FFFFFFFF")),
            "mapping_count": len(amap),
        },
        "investment_package_ids": [f"{x:04X}" for x in sorted(allowed_parent_pkgs)],
        "target_package_ids": [f"{x:04X}" for x in sorted(targets)],
        "candidate_parent_count": len(parent_to_assignments),
        "hit_count": len(hits),
        "unique_final_hash_count": len(final_hash_counts),
        "unique_final_sentity_count": len(unique_final_sentities),
        "unique_final_sentities": unique_final_sentities,
        "parent_package_counts": {f"{k:04X}": v for k, v in sorted(parent_pkg_counts.items())},
        "final_package_counts": {f"{k:04X}": v for k, v in sorted(final_package_counts.items())},
        "hit_final_reference_counts": dict(sorted(final_class_counts.items())),
        "hit_final_hash_counts": dict(sorted(final_hash_counts.items())),
        "hits": hits,
        "invalid_parent_hashes": invalid_parent_hashes,
        "errors": errors,
        "policy": (
            "Every hit follows the exact retail EntityArrangementMap assignment->EntityParent edge and the fixed D1 EntityParent +0x10 EntityDataROI field. "
            "Target package selection does not imply semantic identity. Only final tags whose exact class is 80800734 are emitted as s_entity closure candidates; "
            "assignment hashes remain opaque selectors until a separate source schema gives them semantics."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print("STATUS", out["status"], "PARENTS", len(parent_to_assignments), "HITS", len(hits), "UNIQUE_FINAL", len(final_hash_counts), "SENTITIES", len(unique_final_sentities), "ERRORS", len(errors))
    return 0 if out["status"] == "D1_REMOTE_INVESTMENT_HIVE_PARENT_CENSUS_COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
