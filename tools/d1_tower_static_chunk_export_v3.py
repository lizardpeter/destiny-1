#!/usr/bin/env python3
"""D1 Tower baked-static exporter v3.

Composes the two narrow exporter/validator safety fixes that are now required for
current retail package families:

- validator v3 patches Corpus.payload() so patch-generation fallback can never
  cross the newest occurrence's FileEntry.Reference/class boundary;
- exporter v2 treats only Vertices1 == FFFFFFFF as an explicit null secondary
  stream, without fabricating bytes.

The actual geometry/placement implementation remains
`d1_tower_static_chunk_export.py`; this wrapper changes no placement, matrix,
material, LOD, or buffer semantics beyond those two safety rules.
"""
from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# Patch the shared Corpus class before the exporter creates a corpus.
import d1_tower_map_schema_validate_v3  # noqa: F401
# Applies the narrow null-Vertices1 exporter patch to the base exporter module.
import d1_tower_static_chunk_export_v2 as export_v2
import d1_tower_static_chunk_export as base_export

if __name__ == '__main__':
    raise SystemExit(base_export.main())
