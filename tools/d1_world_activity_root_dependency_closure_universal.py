#!/usr/bin/env python3
"""Universal/current-index adapter for D1 Activity map-root dependency closure.

The original closure correctly treats a typed Tag's ordinary file-entry Reference as
a possible D1 manifest-parent FileHash when it differs from the source-typed schema.
Cross-world validation exposed an additional necessary condition: some valid shipped
typed targets carry legacy/non-file references such as 80800343. Numerically decoding
those values can yield package 0000 even though no package 0000 exists in the verified
current retail corpus.

This adapter preserves every ordinary reference as evidence but promotes it to a
physical package recovery dependency only when its decoded package family exists in
the exact current global Activity index. Source-typed targets whose ordinary reference
is not a current FileHash remain subject to the existing payload/schema validation;
they are not rejected and no phantom package is fabricated.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import d1_world_activity_root_dependency_closure as base


def _arg_value(flag: str) -> str:
    try:
        i = sys.argv.index(flag)
        return sys.argv[i + 1]
    except (ValueError, IndexError):
        raise SystemExit(f"missing required {flag} for universal adapter")


index_path = Path(_arg_value("--index"))
index_doc = json.loads(index_path.read_text(encoding="utf-8"))
available_package_ids = {
    str(x).upper().zfill(4) for x in (index_doc.get("package_families") or {}).keys()
}
if not available_package_ids:
    raise SystemExit("current Activity index contains no package_families")


def add_manifest_parent_dependencies_current_index(c, typed, required, evidence):
    """Promote only ordinary refs whose decoded package exists in current corpus."""
    for h, expected_class in sorted(typed.items()):
        if h in base.NULLS:
            continue
        tag_pid = base.pid_hex(h)
        if tag_pid.upper() not in available_package_ids:
            raise RuntimeError(
                f"source-typed tag {h} decodes to package {tag_pid} absent from current index"
            )
        required.add(tag_pid)
        meta = c.entry_meta(h)
        row = {
            "tag": h,
            "expected_class": expected_class,
            "tag_package_id": tag_pid,
            "meta": meta,
            "ordinary_reference": None,
            "manifest_parent_package_id": None,
            "manifest_parent_recovery_status": None,
        }
        if meta is not None:
            ref = base.norm(meta.get("reference", ""))
            row["ordinary_reference"] = ref
            if ref not in base.NULLS and ref != expected_class:
                try:
                    mpid = base.pid_hex(ref)
                except ValueError as ex:
                    row["manifest_parent_error"] = str(ex)
                    row["manifest_parent_recovery_status"] = "invalid_filehash_encoding"
                else:
                    row["manifest_parent_decoded_package_id"] = mpid
                    if mpid.upper() in available_package_ids:
                        required.add(mpid)
                        row["manifest_parent_package_id"] = mpid
                        row["manifest_parent_recovery_status"] = "current_package_dependency"
                    else:
                        row["manifest_parent_recovery_status"] = "decoded_package_absent_current_index"
        evidence.append(row)


base.add_manifest_parent_dependencies = add_manifest_parent_dependencies_current_index


if __name__ == "__main__":
    raise SystemExit(base.main())
