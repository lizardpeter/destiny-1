#!/usr/bin/env python3
"""D1 Tower baked-static exporter v6.

v6 keeps the proven v5 serialized-coverage Tiger reader and fixes a distinct
export-adapter bug in the 0x40 instance record: only bytes +0x00..+0x2F are the
3x4 affine object transform. Bytes +0x30..+0x3B are the shipped per-instance UV
transform and +0x3C is not a homogeneous matrix element.

Older proof GLBs passed the raw 4x4 float block to glTF. numpy/trimesh scene bounds
mostly masked this because their point transform path consumes the upper 3x4, but
Blender receives the actual node matrix and therefore sees an invalid projective
fourth row. This wrapper patches the base exporter before main() runs.
"""
from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# Preserve all v5 reader/class/null-V1 behavior first.
import d1_tower_map_schema_validate_v5  # noqa: F401
import d1_tower_static_chunk_export_v2  # noqa: F401
import d1_tower_static_chunk_export as base_export
from d1_world_static_common import affine_matrix_records

base_export.matrix_records = affine_matrix_records

if __name__ == '__main__':
    raise SystemExit(base_export.main())
