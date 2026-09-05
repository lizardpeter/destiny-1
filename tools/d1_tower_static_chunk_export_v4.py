#!/usr/bin/env python3
"""D1 Tower baked-static exporter v4.

Composes:
- validator v4 immediate-previous-logical-block Oodle history fallback;
- validator v3 class-stable TagHash occurrence policy;
- exporter v2's explicit FFFFFFFF Vertices1-null handling;
- the base baked-static geometry/placement exporter.
"""
from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# Patch Corpus reader policy before the base exporter imports/uses Corpus.
import d1_tower_map_schema_validate_v4  # noqa: F401
import d1_tower_static_chunk_export_v2  # noqa: F401
import d1_tower_static_chunk_export as base_export

if __name__ == '__main__':
    raise SystemExit(base_export.main())
