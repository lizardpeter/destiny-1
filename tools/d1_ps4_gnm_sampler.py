#!/usr/bin/env python3
"""Decode the 128-bit PS4/GCN sampler resource descriptor.

Bit layout follows the Sea Islands / PS4-compatible sampler resource definition
used by shadPS4 (AmdGpu::Sampler).  This module deliberately accepts only the
exact 16-byte descriptor emitted by the D1 material parser.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

CLAMP_MODE = {
    0: "wrap",
    1: "mirror",
    2: "clamp_last_texel",
    3: "mirror_once_last_texel",
    4: "clamp_half_border",
    5: "mirror_once_half_border",
    6: "clamp_border",
    7: "mirror_once_border",
}
ANISO_RATIO = {0: 1, 1: 2, 2: 4, 3: 8, 4: 16}
DEPTH_COMPARE = {
    0: "never", 1: "less", 2: "equal", 3: "less_equal",
    4: "greater", 5: "not_equal", 6: "greater_equal", 7: "always",
}
FILTER_MODE = {0: "blend", 1: "min", 2: "max"}
FILTER = {0: "point", 1: "bilinear", 2: "aniso_point", 3: "aniso_linear"}
MIP_FILTER = {0: "none", 1: "point", 2: "linear"}
BORDER_COLOR = {0: "transparent_black", 1: "opaque_black", 2: "white", 3: "custom"}


def _bits(x: int, offset: int, width: int) -> int:
    return (x >> offset) & ((1 << width) - 1)


def _signed(value: int, width: int) -> int:
    sign = 1 << (width - 1)
    return (value ^ sign) - sign


def decode_sampler_bytes(raw: bytes) -> dict:
    if len(raw) != 16:
        raise ValueError(f"PS4 GNM sampler descriptor must be exactly 16 bytes, got {len(raw)}")
    raw0 = int.from_bytes(raw[:8], "little")
    raw1 = int.from_bytes(raw[8:], "little")

    cx = _bits(raw0, 0, 3)
    cy = _bits(raw0, 3, 3)
    cz = _bits(raw0, 6, 3)
    aniso = _bits(raw0, 9, 3)
    depth = _bits(raw0, 12, 3)
    fm = _bits(raw0, 29, 2)
    mag = _bits(raw1, 20, 2)
    minf = _bits(raw1, 22, 2)
    mip = _bits(raw1, 26, 2)
    border = _bits(raw1, 62, 2)
    lod_bias_raw = _bits(raw1, 0, 14)

    return {
        "raw_hex": raw.hex(),
        "raw0_hex": f"{raw0:016X}",
        "raw1_hex": f"{raw1:016X}",
        "clamp_x": CLAMP_MODE[cx],
        "clamp_y": CLAMP_MODE[cy],
        "clamp_z": CLAMP_MODE[cz],
        "clamp_x_value": cx,
        "clamp_y_value": cy,
        "clamp_z_value": cz,
        "max_aniso": ANISO_RATIO.get(aniso),
        "max_aniso_value": aniso,
        "depth_compare": DEPTH_COMPARE[depth],
        "force_unnormalized": bool(_bits(raw0, 15, 1)),
        "aniso_threshold": _bits(raw0, 16, 3),
        "mc_coord_trunc": bool(_bits(raw0, 19, 1)),
        "force_degamma": bool(_bits(raw0, 20, 1)),
        "aniso_bias": _bits(raw0, 21, 6),
        "trunc_coord": bool(_bits(raw0, 27, 1)),
        "disable_cube_wrap": bool(_bits(raw0, 28, 1)),
        "filter_mode": FILTER_MODE.get(fm, f"reserved_{fm}"),
        "min_lod": _bits(raw0, 32, 12) / 256.0,
        "max_lod": _bits(raw0, 44, 12) / 256.0,
        "perf_mip": _bits(raw0, 56, 4),
        "perf_z": _bits(raw0, 60, 4),
        "lod_bias": _signed(lod_bias_raw, 14) / 256.0,
        "lod_bias_sec": _bits(raw1, 14, 6),
        "xy_mag_filter": FILTER[mag],
        "xy_min_filter": FILTER[minf],
        "z_filter_value": _bits(raw1, 24, 2),
        "mip_filter": MIP_FILTER.get(mip, f"reserved_{mip}"),
        "mip_point_preclamp": bool(_bits(raw1, 28, 1)),
        "disable_lsb_ceil": bool(_bits(raw1, 29, 1)),
        "border_color_ptr": _bits(raw1, 32, 12),
        "border_color_type": BORDER_COLOR[border],
    }


def decode_sampler_hex(raw_hex: str) -> dict:
    s = raw_hex.strip().removeprefix("0x").replace(" ", "")
    raw = bytes.fromhex(s)
    return decode_sampler_bytes(raw)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("descriptor", nargs="+", help="16-byte descriptor as 32 hex digits")
    ap.add_argument("-o", "--output", type=Path)
    a = ap.parse_args()
    out = [decode_sampler_hex(x) for x in a.descriptor]
    text = json.dumps(out, indent=2)
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
