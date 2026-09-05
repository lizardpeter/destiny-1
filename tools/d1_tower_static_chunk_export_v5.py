#!/usr/bin/env python3
"""D1 Tower baked-static exporter v5.

Composes the proven Tower export stack with serialized-coverage D1 Tiger block sizing:
- validator v5 / SizedEntryReader for partial Oodle logical blocks;
- validator v3's class-stable TagHash occurrence policy;
- exporter v2's explicit FFFFFFFF Vertices1-null semantics;
- base D1 baked-static geometry/placement implementation.
"""
from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# Patch Corpus reader policy before the exporter creates a Corpus.
import d1_tower_map_schema_validate_v5  # noqa: F401
# Patch the base exporter with the explicit null-Vertices1 rule.
import d1_tower_static_chunk_export_v2  # noqa: F401
import d1_tower_static_chunk_export as base_export

if __name__ == '__main__':
    raise SystemExit(base_export.main())
