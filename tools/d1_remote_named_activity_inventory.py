#!/usr/bin/env python3
"""Inventory current D1 named activity roots across a verified split-TAR corpus.

This is the remote counterpart to d1_world_activity_map_root_census.py's named-tag
selection. It reads only current package metadata ranges: header plus serialized
0x44-byte named/global tag table. No package payload decompression is needed.

Source-pinned D1 activity named classes:
  8080052E  SActivity_ROI
  80800616  SUnkActivity_ROI

D1's named table is global-registration metadata: a package may register a named
FileHash whose encoded physical package is a different family. Both the registering
package and encoded target package are therefore preserved explicitly.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

from d1_pkg_probe import parse_header, parse_named
from d1_split_tar_extract import SplitHttpTar
from d1_world_activity_map_root_census import (
    ACTIVITY_ROI,
    UNK_ACTIVITY_ROI,
    canonical_named_class,
    charm_display,
)

NAMED_SLOT_STRIDE = 0x44
NULL_SHA1 = "0" * 40


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def filehash_package_id(h: str) -> int | None:
    """Exact D1 Tiger FileHash package decode used by the established project path."""
    v = int(norm(h), 16)
    if v in (0, 0xFFFFFFFF):
        return None
    pkg = ((v >> 13) & 0x3FF) + ((((v >> 23) & 3) - 1) * 0x400)
    return pkg if pkg >= 0 else None


def load_catalogs(paths: list[Path]) -> dict[int, list[dict]]:
    families: dict[int, list[dict]] = {}
    for path in paths:
        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc.get("schema") != "d1_remote_package_member_catalog/v1":
            raise ValueError(f"{path}: unexpected schema {doc.get('schema')!r}")
        for raw_pkg, members in doc.get("families", {}).items():
            pkg = int(raw_pkg, 16)
            old = families.get(pkg)
            if old is not None and old != members:
                raise ValueError(f"conflicting catalog family {pkg:04X}")
            families[pkg] = list(members)
    if not families:
        raise ValueError("catalog contains no package families")
    return families


def choose_current(members: list[dict]) -> dict:
    return max(
        members,
        key=lambda x: (
            int(x.get("header_patch_id", -1)),
            int(x.get("filename_generation", -1)),
            str(x.get("name", "")),
        ),
    )


def merge_rows(rows: list[dict]) -> tuple[list[dict], list[str]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["tag_hash"]].append(row)
    merged = []
    violations = []
    for h in sorted(grouped):
        xs = grouped[h]
        classes = sorted({x["class_hash_canonical"] for x in xs})
        if len(classes) != 1:
            violations.append(f"current_named_tag_class_conflict:{h}:{classes}")
        aliases = []
        indices = []
        registrations = []
        for x in xs:
            name = x.get("name")
            if name not in aliases:
                aliases.append(name)
            indices.append(int(x["index"]))
            registrations.append(
                {
                    "registered_by_package_id": x["registered_by_package_id"],
                    "source_member": x["source_member"],
                    "source_generation": x["source_generation"],
                    "source_patch_id": x["source_patch_id"],
                    "named_table_index": int(x["index"]),
                    "name": name,
                }
            )
        display = max((x for x in aliases if x is not None), key=len, default=None)
        base = dict(xs[0])
        base["name"] = display
        base["aliases"] = aliases
        base["named_table_indices"] = indices
        base["alias_count"] = len(xs)
        base["registration_package_ids"] = sorted(
            {x["registered_by_package_id"] for x in xs}
        )
        base["registrations"] = registrations
        merged.append(base)
    return merged, violations


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--member-catalog", action="append", type=Path, required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    families = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip("/")
    archive = SplitHttpTar(
        [f"{base}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=90,
    )

    packages = []
    all_rows = []
    violations = []
    cross_package_registration_count = 0
    for n, pkg in enumerate(sorted(families), 1):
        member = choose_current(families[pkg])
        data_offset = int(member["data_offset"])
        size = int(member["size"])
        head = archive.read_at(data_offset, 0x140)
        h = parse_header(io.BytesIO(head))
        if int(h["pkg_id"]) != pkg:
            violations.append(
                f"{member['name']}:header_pkg_id:{int(h['pkg_id']):04X}!={pkg:04X}"
            )
            continue
        count = int(h["named_tag_table_count"])
        off = int(h["named_tag_table_offset"])
        expected_sha = str(h.get("named_tag_table_hash") or "").lower()
        if count == 0:
            raw = b""
        else:
            table_bytes = count * NAMED_SLOT_STRIDE
            if off <= 0 or off + table_bytes > size:
                violations.append(
                    f"{member['name']}:named_table_bounds:{off}+{table_bytes}>{size}"
                )
                continue
            raw = archive.read_at(data_offset + off, table_bytes)
        actual_sha = hashlib.sha1(raw).hexdigest()
        absent_zero = count == 0 and off == 0 and expected_sha == NULL_SHA1
        sha_matches = True if absent_zero else (
            actual_sha == expected_sha if expected_sha else None
        )
        if sha_matches is False:
            violations.append(f"{member['name']}:named_tag_table_sha1_mismatch")

        parsed = parse_named(raw)
        if len(parsed) != count:
            violations.append(f"{member['name']}:named_parse_count:{len(parsed)}!={count}")
        pkg_rows = []
        for e in parsed:
            th = norm(e["tag_hash"])
            raw_cls = norm(e["class_hash"])
            encoded_pkg = filehash_package_id(th)
            if encoded_pkg is None or encoded_pkg not in families:
                violations.append(
                    f"{member['name']}:named_tag_target_package_absent:{th}:{encoded_pkg!r}"
                )
            cross = encoded_pkg is not None and encoded_pkg != pkg
            if cross:
                cross_package_registration_count += 1
            row = {
                **e,
                "tag_hash": th,
                "class_hash_raw_uint": raw_cls,
                "class_hash_charm_display": charm_display(raw_cls),
                "class_hash_canonical": canonical_named_class(raw_cls),
                "registered_by_package_id": f"{pkg:04X}",
                "tag_encoded_package_id": None if encoded_pkg is None else f"{encoded_pkg:04X}",
                "cross_package_registration": cross,
                "source_package_id": f"{pkg:04X}",
                "source_member": member["name"],
                "source_generation": int(member.get("filename_generation", -1)),
                "source_patch_id": int(member.get("header_patch_id", -1)),
            }
            pkg_rows.append(row)
            all_rows.append(row)
        packages.append(
            {
                "package_id": f"{pkg:04X}",
                "member": member["name"],
                "member_size": size,
                "filename_generation": int(member.get("filename_generation", -1)),
                "header_patch_id": int(member.get("header_patch_id", -1)),
                "named_tag_table_count": count,
                "named_tag_table_offset": off,
                "named_tag_table_sha1_expected": expected_sha,
                "named_tag_table_sha1_actual": actual_sha,
                "named_tag_table_sha1_matches": sha_matches,
                "named_class_counts": dict(Counter(x["class_hash_canonical"] for x in pkg_rows)),
                "cross_package_named_registration_count": sum(
                    1 for x in pkg_rows if x["cross_package_registration"]
                ),
            }
        )
        if n % 50 == 0:
            print(f"SCANNED {n}/{len(families)} packages", flush=True)

    merged, merge_violations = merge_rows(all_rows)
    violations.extend(merge_violations)
    map_roots = [x for x in merged if x["class_hash_canonical"] == ACTIVITY_ROI]
    scenario_roots = [x for x in merged if x["class_hash_canonical"] == UNK_ACTIVITY_ROI]
    activity_roots = sorted(
        map_roots + scenario_roots,
        key=lambda x: (x["tag_encoded_package_id"] or "", x["tag_hash"]),
    )
    report = {
        "schema": "d1_remote_named_activity_inventory/v1",
        "status": (
            "D1_REMOTE_NAMED_ACTIVITY_INVENTORY_EXACT"
            if not violations
            else "D1_REMOTE_NAMED_ACTIVITY_INVENTORY_WITH_VIOLATIONS"
        ),
        "source_classes": {"activity_roi": ACTIVITY_ROI, "unk_activity_roi": UNK_ACTIVITY_ROI},
        "package_family_count": len(families),
        "package_scan_count": len(packages),
        "current_named_row_count": len(all_rows),
        "current_unique_named_tag_count": len(merged),
        "current_alias_row_count": len(all_rows) - len(merged),
        "cross_package_named_registration_count": cross_package_registration_count,
        "current_unique_class_counts": dict(Counter(x["class_hash_canonical"] for x in merged)),
        "map_activity_root_count": len(map_roots),
        "scenario_activity_root_count": len(scenario_roots),
        "activity_root_count": len(activity_roots),
        "packages_registering_activity_roots": len(
            {p for x in activity_roots for p in x["registration_package_ids"]}
        ),
        "physical_packages_containing_activity_roots": len(
            {x["tag_encoded_package_id"] for x in activity_roots if x["tag_encoded_package_id"]}
        ),
        "map_activity_roots": map_roots,
        "scenario_activity_roots": scenario_roots,
        "activity_roots": activity_roots,
        "packages": packages,
        "violations": violations,
        "policy": (
            "Current package selection is highest header patch id then filename generation in the "
            "checksum-pinned catalog. Named rows/aliases are serialized retail global-registration "
            "metadata. The registering package and FileHash-encoded physical target package are "
            "preserved separately and may legitimately differ. Only source-pinned named classes "
            "8080052E and 80800616 are admitted as activity roots. Names remain provenance/discovery "
            "text and do not create ownership edges."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        "STATUS", report["status"], "PACKAGES", report["package_scan_count"],
        "NAMED_ROWS", report["current_named_row_count"],
        "UNIQUE_NAMED", report["current_unique_named_tag_count"],
        "CROSS_PACKAGE_REGISTRATIONS", report["cross_package_named_registration_count"],
        "MAP_ROOTS", report["map_activity_root_count"],
        "SCENARIO_ROOTS", report["scenario_activity_root_count"],
        "ALL_ACTIVITY_ROOTS", report["activity_root_count"],
        "REGISTERING_PACKAGES", report["packages_registering_activity_roots"],
        "PHYSICAL_ACTIVITY_PACKAGES", report["physical_packages_containing_activity_roots"],
        "VIOLATIONS", len(violations),
    )
    for r in activity_roots:
        print(
            "ACTIVITY", r["tag_hash"], r["class_hash_canonical"],
            "TARGET_PKG", r.get("tag_encoded_package_id"),
            "REGISTERED_BY", r.get("registration_package_ids"),
            r.get("name"), r.get("aliases"),
        )
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
