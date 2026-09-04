#!/usr/bin/env python3
"""Decode the linearized DDS files produced by d1_texture_export.py to PNG.

This tool is deliberately downstream of D1 swizzle/resource reconstruction:
it does not know Tiger package layout.  It only decodes standard DDS payloads
that our exporter has already linearized, making the PNG step independent of
Pillow's optional/host-version DDS codec behavior.

Supported fixture formats: BC1/DXT1, BC3/DXT5, BC4/ATI1, BC5/ATI2, RGBA8.
"""
from __future__ import annotations

import argparse
import struct
from pathlib import Path

from PIL import Image
import texture2ddecoder


def u32(b: bytes, off: int) -> int:
    return struct.unpack_from('<I', b, off)[0]


def decode_dds(path: Path) -> Image.Image:
    b = path.read_bytes()
    if len(b) < 128 or b[:4] != b'DDS ':
        raise ValueError(f'{path}: not a standard DDS file')
    if u32(b, 4) != 124:
        raise ValueError(f'{path}: unsupported DDS header size {u32(b,4)}')

    height = u32(b, 12)
    width = u32(b, 16)
    pf_flags = u32(b, 80)
    fourcc = b[84:88]
    rgb_bits = u32(b, 88)
    rmask, gmask, bmask, amask = (u32(b, o) for o in (92, 96, 100, 104))
    payload = b[128:]

    if fourcc == b'DXT1':
        raw = texture2ddecoder.decode_bc1(payload, width, height)
        return Image.frombytes('RGBA', (width, height), raw, 'raw', 'BGRA')
    if fourcc == b'DXT5':
        raw = texture2ddecoder.decode_bc3(payload, width, height)
        return Image.frombytes('RGBA', (width, height), raw, 'raw', 'BGRA')
    if fourcc == b'ATI1':
        raw = texture2ddecoder.decode_bc4(payload, width, height)
        return Image.frombytes('RGBA', (width, height), raw, 'raw', 'BGRA')
    if fourcc == b'ATI2':
        raw = texture2ddecoder.decode_bc5(payload, width, height)
        return Image.frombytes('RGBA', (width, height), raw, 'raw', 'BGRA')

    # d1_texture_export.py writes its validated PS4 RGBA8 surfaces with these
    # exact masks, and its unswizzled bytes are ordinary R,G,B,A byte order.
    if fourcc == b'\0\0\0\0' and rgb_bits == 32 and (rmask, gmask, bmask, amask) == (
        0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000
    ):
        expected = width * height * 4
        if len(payload) < expected:
            raise ValueError(f'{path}: RGBA8 payload short: {len(payload)} < {expected}')
        return Image.frombytes('RGBA', (width, height), payload[:expected], 'raw', 'RGBA')

    raise NotImplementedError(
        f'{path}: unsupported DDS pixel format flags={pf_flags:#x} fourcc={fourcc!r} '
        f'rgb_bits={rgb_bits} masks={[hex(x) for x in (rmask,gmask,bmask,amask)]}'
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('dds', type=Path, nargs='+')
    ap.add_argument('--overwrite', action='store_true')
    args = ap.parse_args()
    for src in args.dds:
        dst = src.with_suffix('.png')
        if dst.exists() and not args.overwrite:
            print(f'keep {dst}')
            continue
        im = decode_dds(src)
        im.save(dst)
        print(f'wrote {dst} {im.width}x{im.height} {im.mode}')


if __name__ == '__main__':
    main()
