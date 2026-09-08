#!/usr/bin/env python3
"""Decode linearized DDS files produced by d1_texture_export.py to PNG.

This module intentionally has **no third-party runtime dependencies**. D1 texture
workflows run on fresh CI images, so relying on host Pillow/texture2ddecoder made
an otherwise exact package/texture closure fail before decoding began.

The D1 exporter has already handled Tiger package lookup, PS4 resource metadata
and swizzle removal. This file only decodes the standard DDS payload emitted by
that exporter and writes a simple lossless RGBA PNG.

Supported DDS pixel formats:
- BC1 / DXT1
- BC2 / DXT3
- BC3 / DXT5
- BC4 / ATI1
- BC5 / ATI2
- validated 32-bit RGBA8 masks used by d1_texture_export.py

BC4 PNGs replicate the decoded red channel into RGB for viewability. BC5 PNGs
preserve the native two channels as R/G and write B=0, A=255. Shader semantics
must continue to use the exact t# role proof rather than infer meaning from PNG
appearance.
"""
from __future__ import annotations

import argparse
import binascii
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path


def u32(b: bytes, off: int) -> int:
    return struct.unpack_from('<I', b, off)[0]


def _rgb565(v: int) -> tuple[int, int, int]:
    r = (v >> 11) & 31
    g = (v >> 5) & 63
    b = v & 31
    return ((r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2))


def _lerp8(a: int, b: int, na: int, nb: int, den: int) -> int:
    return (na * a + nb * b) // den


def _bc_color_palette(c0: int, c1: int, allow_bc1_transparency: bool) -> list[tuple[int, int, int, int]]:
    a = _rgb565(c0)
    b = _rgb565(c1)
    p0 = (*a, 255)
    p1 = (*b, 255)
    if allow_bc1_transparency and c0 <= c1:
        p2 = tuple((a[i] + b[i]) // 2 for i in range(3)) + (255,)
        p3 = (0, 0, 0, 0)
    else:
        p2 = tuple(_lerp8(a[i], b[i], 2, 1, 3) for i in range(3)) + (255,)
        p3 = tuple(_lerp8(a[i], b[i], 1, 2, 3) for i in range(3)) + (255,)
    return [p0, p1, p2, p3]


def _alpha_palette(a0: int, a1: int) -> list[int]:
    if a0 > a1:
        return [
            a0, a1,
            _lerp8(a0, a1, 6, 1, 7),
            _lerp8(a0, a1, 5, 2, 7),
            _lerp8(a0, a1, 4, 3, 7),
            _lerp8(a0, a1, 3, 4, 7),
            _lerp8(a0, a1, 2, 5, 7),
            _lerp8(a0, a1, 1, 6, 7),
        ]
    return [
        a0, a1,
        _lerp8(a0, a1, 4, 1, 5),
        _lerp8(a0, a1, 3, 2, 5),
        _lerp8(a0, a1, 2, 3, 5),
        _lerp8(a0, a1, 1, 4, 5),
        0, 255,
    ]


def _decode_bc_alpha_block(block: bytes) -> list[int]:
    if len(block) != 8:
        raise ValueError(f'BC alpha block must be 8 bytes, got {len(block)}')
    pal = _alpha_palette(block[0], block[1])
    bits = int.from_bytes(block[2:8], 'little')
    return [pal[(bits >> (3 * i)) & 7] for i in range(16)]


def _blit_block(out: bytearray, width: int, height: int, bx: int, by: int,
                pixels: list[tuple[int, int, int, int]]) -> None:
    for py in range(4):
        y = by * 4 + py
        if y >= height:
            continue
        for px in range(4):
            x = bx * 4 + px
            if x >= width:
                continue
            p = pixels[py * 4 + px]
            off = (y * width + x) * 4
            out[off:off + 4] = bytes(p)


def _decode_bc1(payload: bytes, width: int, height: int) -> bytes:
    bw = (width + 3) // 4
    bh = (height + 3) // 4
    need = bw * bh * 8
    if len(payload) < need:
        raise ValueError(f'BC1 payload short: {len(payload)} < {need}')
    out = bytearray(width * height * 4)
    pos = 0
    for by in range(bh):
        for bx in range(bw):
            c0, c1, idx = struct.unpack_from('<HHI', payload, pos)
            pos += 8
            pal = _bc_color_palette(c0, c1, True)
            pix = [pal[(idx >> (2 * i)) & 3] for i in range(16)]
            _blit_block(out, width, height, bx, by, pix)
    return bytes(out)


def _decode_bc2(payload: bytes, width: int, height: int) -> bytes:
    bw = (width + 3) // 4
    bh = (height + 3) // 4
    need = bw * bh * 16
    if len(payload) < need:
        raise ValueError(f'BC2 payload short: {len(payload)} < {need}')
    out = bytearray(width * height * 4)
    pos = 0
    for by in range(bh):
        for bx in range(bw):
            alpha_bits = int.from_bytes(payload[pos:pos + 8], 'little')
            c0, c1, idx = struct.unpack_from('<HHI', payload, pos + 8)
            pos += 16
            pal = _bc_color_palette(c0, c1, False)
            pix = []
            for i in range(16):
                r, g, b, _ = pal[(idx >> (2 * i)) & 3]
                a = ((alpha_bits >> (4 * i)) & 0xF) * 17
                pix.append((r, g, b, a))
            _blit_block(out, width, height, bx, by, pix)
    return bytes(out)


def _decode_bc3(payload: bytes, width: int, height: int) -> bytes:
    bw = (width + 3) // 4
    bh = (height + 3) // 4
    need = bw * bh * 16
    if len(payload) < need:
        raise ValueError(f'BC3 payload short: {len(payload)} < {need}')
    out = bytearray(width * height * 4)
    pos = 0
    for by in range(bh):
        for bx in range(bw):
            alpha = _decode_bc_alpha_block(payload[pos:pos + 8])
            c0, c1, idx = struct.unpack_from('<HHI', payload, pos + 8)
            pos += 16
            pal = _bc_color_palette(c0, c1, False)
            pix = []
            for i in range(16):
                r, g, b, _ = pal[(idx >> (2 * i)) & 3]
                pix.append((r, g, b, alpha[i]))
            _blit_block(out, width, height, bx, by, pix)
    return bytes(out)


def _decode_bc4(payload: bytes, width: int, height: int) -> bytes:
    bw = (width + 3) // 4
    bh = (height + 3) // 4
    need = bw * bh * 8
    if len(payload) < need:
        raise ValueError(f'BC4 payload short: {len(payload)} < {need}')
    out = bytearray(width * height * 4)
    pos = 0
    for by in range(bh):
        for bx in range(bw):
            chan = _decode_bc_alpha_block(payload[pos:pos + 8])
            pos += 8
            pix = [(v, v, v, 255) for v in chan]
            _blit_block(out, width, height, bx, by, pix)
    return bytes(out)


def _decode_bc5(payload: bytes, width: int, height: int) -> bytes:
    bw = (width + 3) // 4
    bh = (height + 3) // 4
    need = bw * bh * 16
    if len(payload) < need:
        raise ValueError(f'BC5 payload short: {len(payload)} < {need}')
    out = bytearray(width * height * 4)
    pos = 0
    for by in range(bh):
        for bx in range(bw):
            red = _decode_bc_alpha_block(payload[pos:pos + 8])
            green = _decode_bc_alpha_block(payload[pos + 8:pos + 16])
            pos += 16
            pix = [(red[i], green[i], 0, 255) for i in range(16)]
            _blit_block(out, width, height, bx, by, pix)
    return bytes(out)


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    body = kind + payload
    return struct.pack('>I', len(payload)) + body + struct.pack('>I', binascii.crc32(body) & 0xFFFFFFFF)


def _encode_png_rgba(width: int, height: int, rgba: bytes) -> bytes:
    expected = width * height * 4
    if len(rgba) != expected:
        raise ValueError(f'RGBA byte count mismatch: {len(rgba)} != {expected}')
    stride = width * 4
    raw = b''.join(b'\x00' + rgba[y * stride:(y + 1) * stride] for y in range(height))
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    return (
        b'\x89PNG\r\n\x1a\n'
        + _png_chunk(b'IHDR', ihdr)
        + _png_chunk(b'IDAT', zlib.compress(raw, 9))
        + _png_chunk(b'IEND', b'')
    )


@dataclass(frozen=True)
class DecodedImage:
    width: int
    height: int
    rgba: bytes
    mode: str = 'RGBA'

    def save(self, path: str | Path) -> None:
        Path(path).write_bytes(_encode_png_rgba(self.width, self.height, self.rgba))


def decode_dds(path: Path) -> DecodedImage:
    b = path.read_bytes()
    if len(b) < 128 or b[:4] != b'DDS ':
        raise ValueError(f'{path}: not a standard DDS file')
    if u32(b, 4) != 124:
        raise ValueError(f'{path}: unsupported DDS header size {u32(b,4)}')

    height = u32(b, 12)
    width = u32(b, 16)
    if width <= 0 or height <= 0:
        raise ValueError(f'{path}: invalid dimensions {width}x{height}')
    pf_flags = u32(b, 80)
    fourcc = b[84:88]
    rgb_bits = u32(b, 88)
    rmask, gmask, bmask, amask = (u32(b, o) for o in (92, 96, 100, 104))
    payload = b[128:]

    if fourcc == b'DXT1':
        rgba = _decode_bc1(payload, width, height)
    elif fourcc == b'DXT3':
        rgba = _decode_bc2(payload, width, height)
    elif fourcc == b'DXT5':
        rgba = _decode_bc3(payload, width, height)
    elif fourcc == b'ATI1':
        rgba = _decode_bc4(payload, width, height)
    elif fourcc == b'ATI2':
        rgba = _decode_bc5(payload, width, height)
    elif fourcc == b'\0\0\0\0' and rgb_bits == 32 and (rmask, gmask, bmask, amask) == (
        0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000
    ):
        expected = width * height * 4
        if len(payload) < expected:
            raise ValueError(f'{path}: RGBA8 payload short: {len(payload)} < {expected}')
        rgba = payload[:expected]
    else:
        raise NotImplementedError(
            f'{path}: unsupported DDS pixel format flags={pf_flags:#x} fourcc={fourcc!r} '
            f'rgb_bits={rgb_bits} masks={[hex(x) for x in (rmask,gmask,bmask,amask)]}'
        )

    return DecodedImage(width, height, rgba)


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
