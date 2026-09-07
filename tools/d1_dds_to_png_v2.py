#!/usr/bin/env python3
"""D1 DDS decoder extension adding source-proven PS4 GCN Format8 / R8_UNORM.

The historical decoder remains authoritative for BC1/3/4/5 and RGBA8.  Charm's
pinned PS4 GCN surface schema maps GcnSurfaceFormat.Format8 (0x01) to DXGI
R8_UNORM with 8 bits per pixel.  This adapter adds only that legacy DDS luminance
representation and delegates every other DDS format to the existing decoder.
"""
from __future__ import annotations

import struct
from pathlib import Path
from PIL import Image

from d1_dds_to_png import decode_dds as _decode_dds_v1

DDPF_LUMINANCE = 0x00020000


def _u32(b: bytes, off: int) -> int:
    return struct.unpack_from('<I', b, off)[0]


def decode_dds(path: Path) -> Image.Image:
    b = path.read_bytes()
    if len(b) >= 128 and b[:4] == b'DDS ' and _u32(b, 4) == 124:
        height = _u32(b, 12)
        width = _u32(b, 16)
        pf_flags = _u32(b, 80)
        fourcc = b[84:88]
        rgb_bits = _u32(b, 88)
        masks = tuple(_u32(b, o) for o in (92, 96, 100, 104))
        if (
            fourcc == b'\0\0\0\0'
            and rgb_bits == 8
            and masks == (0x000000FF, 0, 0, 0)
            and (pf_flags & DDPF_LUMINANCE)
        ):
            payload = b[128:]
            expected = width * height
            if len(payload) < expected:
                raise ValueError(f'{path}: R8 payload short: {len(payload)} < {expected}')
            # Preserve the one-channel storage meaning in the image itself. PNG supports L mode.
            return Image.frombytes('L', (width, height), payload[:expected], 'raw', 'L')
    return _decode_dds_v1(path)
