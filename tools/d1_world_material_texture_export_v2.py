#!/usr/bin/env python3
"""D1 world material/texture exporter v2: add source-proven GCN Format8/R8_UNORM.

This is a bounded adapter over ``d1_world_material_texture_export``.  It changes
only portable wrapping/PNG decoding and the manifest label for PS4 GCN surface
format 0x01.  The underlying D1 texture exporter already owns exact header/backing
resolution, expected R8 byte sizing, and PS4 unswizzle.  Charm's pinned PS4 GCN
schema maps Format8 (0x01) to DXGI R8_UNORM, 8 bits per pixel.

Material ownership, shader/t# bindings, FileHash dependency discovery, swizzle,
and every other surface format remain the historical generic-world implementation.
"""
from __future__ import annotations

import d1_world_material_texture_export as base
from d1_remote_activity_texture_export_v2 import make_dds_v2
from d1_dds_to_png_v2 import decode_dds as decode_dds_v2

GCN_R8 = 0x01

# The base world exporter imported these callables by value, so patch its module
# globals explicitly before invoking main().
base.make_dds = make_dds_v2
base.decode_dds = decode_dds_v2
base.FORMAT_NAME = dict(base.FORMAT_NAME)
base.FORMAT_NAME[GCN_R8] = 'R8_UNORM'
base.ROI_COLORSPACE_HINT = dict(base.ROI_COLORSPACE_HINT)
base.ROI_COLORSPACE_HINT['R8_UNORM'] = 'linear'

if __name__ == '__main__':
    raise SystemExit(base.main())
