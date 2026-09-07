#!/usr/bin/env python3
"""Current generic D1 activity asset target using texture exporter v2.

This adapter preserves the full seed/entity/model/material/geometry/animation pipeline
from d1_fresh_activity_asset_target.py and replaces only the portable activity texture
export surface with d1_remote_activity_texture_export_v2.py, which adds the
source-proven PS4 GCN Format8/R8_UNORM case.
"""
from __future__ import annotations

from pathlib import Path

import d1_fresh_activity_asset_target as base

_original_tool = base.tool


def current_tool(name: str) -> str:
    if name == 'd1_remote_activity_texture_export.py':
        return str(Path(__file__).resolve().parent / 'd1_remote_activity_texture_export_v2.py')
    return _original_tool(name)


base.tool = current_tool

# Re-export the shared driver helpers for adapters while keeping the original module
# as the authority for globals used by base.main().
main = base.main
run = base.run
load = base.load
tool = base.tool
seed_target = base.seed_target
underlying = base

if __name__ == '__main__':
    raise SystemExit(base.main())
