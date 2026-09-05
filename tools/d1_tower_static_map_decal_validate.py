#!/usr/bin/env python3
"""Compatibility wrapper for the generic D1 static-map decal validator.

The implementation moved to `d1_world_static_map_decal_validate.py` after the Tower
map-data ownership layer was closed. Keep this entry point so historical workflows and
notes remain reproducible while all new world work uses the generic module.
"""
from __future__ import annotations

from d1_world_static_map_decal_validate import *  # noqa: F401,F403
from d1_world_static_map_decal_validate import main


if __name__ == '__main__':
    raise SystemExit(main())
