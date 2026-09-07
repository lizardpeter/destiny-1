#!/usr/bin/env python3
"""Universal-namespace adapter for d1_remote_entity_dependency_closure.py.

The underlying dependency walker predates the project-wide proof that D1 Tiger
FileHashes use banked package bits above the low 0x808... namespace. This adapter
preserves the walker's source-typed ownership behavior while replacing only its
cheap FileHash predecode with the source-validated universal decoder.

Exact tag membership is still proven by the walker's verified package catalog and
exact tag lookup. Untyped aligned values therefore remain discovery-only evidence.
"""
from __future__ import annotations

import d1_remote_entity_dependency_closure as base
from d1_filehash import decode_int, plausible_int


def universal_filehash_parts(v: int):
    if not plausible_int(v):
        return None
    return decode_int(v)


base.filehash_parts = universal_filehash_parts


if __name__ == "__main__":
    raise SystemExit(base.main())
