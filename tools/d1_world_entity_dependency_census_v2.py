#!/usr/bin/env python3
"""Universal-FileHash adapter for ``d1_world_entity_dependency_census.py``.

The underlying census semantics are source-pinned and remain unchanged. Its legacy
``pkgid`` helper predates validation of D1 Tiger's banked package namespace and is
used only for report/recovery-target annotations. This adapter replaces exactly that
helper with ``d1_filehash.package_hex`` before running the original census.

All entity/resource/model/skeleton/name parsing therefore remains owned by the
historical implementation while every reported dependency package ID now uses the
same source-validated universal decoder as the world exporters.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import d1_world_entity_dependency_census as base
from d1_filehash import package_hex

NULLS = {"00000000", "FFFFFFFF"}


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def universal_pkgid(h: object) -> str | None:
    value = norm(h)
    if value in NULLS:
        return None
    try:
        return package_hex(value).lower()
    except Exception:
        return None


base.pkgid = universal_pkgid


if __name__ == "__main__":
    raise SystemExit(base.main())
