#!/usr/bin/env python3
"""PS4 checkpoint adapter for d1_gltf_append_retail_animation_library.

Existing exact Guardian checkpoints serialize d1PublishedPlayerBoneHash as an
8-digit hexadecimal string (for example ``C67D...``), while bone indices are JSON
integers. The core appender deliberately treats the GLB palette as authoritative
input evidence; this adapter only teaches that verifier how to parse the already
serialized hexadecimal representation. No GLB data is rewritten before the core
non-destructive checks run.
"""
from __future__ import annotations

import d1_gltf_append_retail_animation_library as core


def _node_extra_int(extras: dict | None, *keys: str) -> int | None:
    if not isinstance(extras, dict):
        return None
    for key in keys:
        if key not in extras:
            continue
        value = extras[key]
        try:
            if isinstance(value, str):
                s = value.strip()
                if s.lower().startswith('0x'):
                    return int(s, 16)
                try:
                    return int(s, 10)
                except ValueError:
                    return int(s, 16)
            return int(value)
        except (TypeError, ValueError):
            return None
    return None


core.node_extra_int = _node_extra_int

if __name__ == '__main__':
    raise SystemExit(core.main())
