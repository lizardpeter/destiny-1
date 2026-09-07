#!/usr/bin/env python3
"""D1 activity texture exporter v2: add source-proven GCN Format8/R8_UNORM.

This is an additive adapter over d1_remote_activity_texture_export.  It changes only
portable wrapping/PNG decode for GCN surface format 0x01.  Charm's pinned PS4 GCN
schema maps Format8 (0x01) to DXGI R8_UNORM and 8 bpp.  Swizzle, payload ownership,
header/backing proof, material ownership, and every other surface format remain the
historical implementation.
"""
from __future__ import annotations

import struct

import d1_texture_export as tex
import d1_remote_activity_texture_export as base
from d1_dds_to_png_v2 import decode_dds as decode_dds_v2

GCN_R8 = 0x01

_original_make_dds = tex.make_dds


def make_dds_v2(data: bytes, w: int, h: int, gfmt: int, array_size: int = 1) -> bytes:
    if gfmt != GCN_R8:
        return _original_make_dds(data, w, h, gfmt, array_size)
    if array_size != 1:
        raise NotImplementedError('R8 array/cubemap DDS wrapping requires face-aware export')
    expected = w * h
    if len(data) < expected:
        raise ValueError(f'R8 payload short: {len(data)} < {expected}')
    data = data[:expected]

    DDSD_CAPS=1; DDSD_HEIGHT=2; DDSD_WIDTH=4; DDSD_PITCH=8; DDSD_PIXELFORMAT=0x1000
    DDPF_LUMINANCE=0x00020000; DDSCAPS_TEXTURE=0x1000
    flags = DDSD_CAPS|DDSD_HEIGHT|DDSD_WIDTH|DDSD_PIXELFORMAT|DDSD_PITCH
    hdr = bytearray(124)
    struct.pack_into('<I', hdr, 0, 124)
    struct.pack_into('<I', hdr, 4, flags)
    struct.pack_into('<I', hdr, 8, h)
    struct.pack_into('<I', hdr, 12, w)
    struct.pack_into('<I', hdr, 16, w)
    struct.pack_into('<I', hdr, 72, 32)
    struct.pack_into('<I', hdr, 76, DDPF_LUMINANCE)
    hdr[80:84] = b'\0\0\0\0'
    struct.pack_into('<I', hdr, 84, 8)
    struct.pack_into('<I', hdr, 88, 0x000000FF)
    struct.pack_into('<I', hdr, 92, 0)
    struct.pack_into('<I', hdr, 96, 0)
    struct.pack_into('<I', hdr, 100, 0)
    struct.pack_into('<I', hdr, 104, DDSCAPS_TEXTURE)
    return b'DDS ' + bytes(hdr) + data


# The historical activity exporter imported these callables by value, so patch its
# module globals explicitly before invoking main().
base.make_dds = make_dds_v2
base.decode_dds = decode_dds_v2
# Name only affects portable filenames/manifests; storage identity remains header format 0x01.
base.FORMAT_NAME = dict(base.FORMAT_NAME)
base.FORMAT_NAME[GCN_R8] = 'R8_UNORM'

if __name__ == '__main__':
    raise SystemExit(base.main())
