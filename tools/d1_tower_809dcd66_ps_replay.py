#!/usr/bin/env python3
"""Scoped semantic replay of Tower pixel shader 809DCD66 RGB arithmetic.

This module preserves the exact retail dataflow that has been closed from the
PS4 GCN stream.  It does not guess engine names for the two api13 scalars.

Inputs proven by native dataflow:

  attr0.xyz = transformed surface normal
  attr1.xyz = transformed tangent
  attr2.xyz = transformed bitangent
  attr3.xy  = base UV
  attr4.xyz = world/instance position

  api0 / material b0:
    c2      palette base RGB
    c3      palette slope/delta RGB
    c4.x    parallax displacement magnitude
    c5.rgb  RGB multiplier
    c6.x    static or TFX-produced intensity

  api12 dwords 28..30 = camera/view position for the parallax view vector
  api13 dwords 6,7    = two shared global RGB scale factors

Texture contract:

  t0.r sampled at base UV selects the material palette after saturate()
  t1.r sampled at the view-displaced UV multiplies the resulting RGB

Exact scoped RGB equation after sampling:

  palette = c2.rgb + c3.rgb * saturate(t0.r)
  rgb = palette * t1.r * c5.rgb * c6.x * api13[6] * api13[7]

The parallax UV is:

  V = normalize(camera_position - world_position)
  displaced_uv = uv - c4.x * (dot(V,T), dot(V,B)) / dot(V,N)

This is a semantic replay, not a bit-exact emulator of GCN reciprocal/rsqrt or
texture filtering.  Texture sampling is supplied by the caller so native image
format/filter/wrap handling remains independently testable.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
import numpy as np

PS_HASH = "809DCD66"


def _n3(a, name: str) -> np.ndarray:
    x = np.asarray(a, dtype=np.float32)
    if x.ndim != 2 or x.shape[1] != 3:
        raise ValueError(f"{name} must be Nx3")
    return x


def _n2(a, name: str) -> np.ndarray:
    x = np.asarray(a, dtype=np.float32)
    if x.ndim != 2 or x.shape[1] != 2:
        raise ValueError(f"{name} must be Nx2")
    return x


def _vec4(v, name: str) -> np.ndarray:
    x = np.asarray(v, dtype=np.float32)
    if x.shape != (4,):
        raise ValueError(f"{name} must be float4")
    return x


def _scalar_samples(v, n: int, name: str) -> np.ndarray:
    x = np.asarray(v, dtype=np.float32)
    if x.shape == (n,):
        return x
    if x.shape == (n, 1):
        return x[:, 0]
    raise ValueError(f"{name} must be N or Nx1")


@dataclass(frozen=True)
class ParallaxResult809DCD66:
    view_direction: np.ndarray
    tangent_view: np.ndarray
    displaced_uv: np.ndarray


def parallax_uv(
    uv,
    world_position,
    normal,
    tangent,
    bitangent,
    camera_position,
    displacement: float,
) -> ParallaxResult809DCD66:
    """Replay the view-dependent UV displacement before the t1 sample."""
    uv = _n2(uv, "uv")
    p = _n3(world_position, "world_position")
    nrm = _n3(normal, "normal")
    tan = _n3(tangent, "tangent")
    bit = _n3(bitangent, "bitangent")
    count = len(uv)
    if not (len(p) == len(nrm) == len(tan) == len(bit) == count):
        raise ValueError("varying row counts disagree")
    cam = np.asarray(camera_position, dtype=np.float32)
    if cam.shape != (3,):
        raise ValueError("camera_position must be xyz")

    view = cam[None, :] - p
    # Preserve float32 semantic ordering. GCN uses v_rsq_f32; numpy sqrt is the
    # portable semantic equivalent rather than a bit-identical approximation.
    l2 = np.float32(view[:, 1] * view[:, 1])
    l2 = np.float32(view[:, 0] * view[:, 0] + l2)
    l2 = np.float32(view[:, 2] * view[:, 2] + l2)
    if np.any(l2 <= 0) or np.any(~np.isfinite(l2)):
        raise ValueError("camera_position coincides with or invalidates a world position")
    view = view * (np.float32(1.0) / np.sqrt(l2, dtype=np.float32))[:, None]

    tvx = np.sum(view * tan, axis=1, dtype=np.float32)
    tvy = np.sum(view * bit, axis=1, dtype=np.float32)
    tvz = np.sum(view * nrm, axis=1, dtype=np.float32)

    # The retail GCN performs an unguarded reciprocal. Preserve that semantic;
    # callers can identify grazing-angle infinities rather than silently clamp.
    with np.errstate(divide="ignore", invalid="ignore"):
        inv_z = np.float32(1.0) / tvz
        scale = np.float32(displacement) * inv_z
        out = np.empty_like(uv, dtype=np.float32)
        out[:, 0] = uv[:, 0] - scale * tvx
        out[:, 1] = uv[:, 1] - scale * tvy

    tangent_view = np.stack([tvx, tvy, tvz], axis=1).astype(np.float32)
    return ParallaxResult809DCD66(
        view_direction=view.astype(np.float32),
        tangent_view=tangent_view,
        displaced_uv=out,
    )


def rgb_from_samples(
    t0_r,
    t1_r,
    *,
    c2,
    c3,
    c5,
    c6_x: float,
    api13_dword6: float,
    api13_dword7: float,
) -> np.ndarray:
    """Replay the exact post-sample RGB construction of 809DCD66."""
    a = np.asarray(t0_r, dtype=np.float32).reshape(-1)
    b = np.asarray(t1_r, dtype=np.float32).reshape(-1)
    if a.shape != b.shape:
        raise ValueError("t0_r and t1_r shapes disagree")
    c2 = _vec4(c2, "c2")
    c3 = _vec4(c3, "c3")
    c5 = _vec4(c5, "c5")

    palette_t = np.clip(a, np.float32(0.0), np.float32(1.0))
    palette = c2[:3][None, :] + c3[:3][None, :] * palette_t[:, None]
    scale = (
        np.float32(c6_x)
        * np.float32(api13_dword6)
        * np.float32(api13_dword7)
    )
    rgb = palette * c5[:3][None, :] * b[:, None] * scale
    return rgb.astype(np.float32)


@dataclass(frozen=True)
class PixelReplay809DCD66:
    base_uv: np.ndarray
    displaced_uv: np.ndarray
    t0_r: np.ndarray
    t1_r: np.ndarray
    rgb: np.ndarray
    parallax: ParallaxResult809DCD66


def replay(
    *,
    uv,
    world_position,
    normal,
    tangent,
    bitangent,
    camera_position,
    c2,
    c3,
    c4,
    c5,
    c6_x: float,
    api13_dword6: float,
    api13_dword7: float,
    sample_t0: Callable[[np.ndarray], np.ndarray],
    sample_t1: Callable[[np.ndarray], np.ndarray],
) -> PixelReplay809DCD66:
    """Replay parallax sampling and the exact RGB path with caller samplers."""
    base_uv = _n2(uv, "uv")
    c4 = _vec4(c4, "c4")
    p = parallax_uv(
        base_uv,
        world_position,
        normal,
        tangent,
        bitangent,
        camera_position,
        float(c4[0]),
    )
    t0 = _scalar_samples(sample_t0(base_uv), len(base_uv), "sample_t0 result")
    t1 = _scalar_samples(sample_t1(p.displaced_uv), len(base_uv), "sample_t1 result")
    rgb = rgb_from_samples(
        t0,
        t1,
        c2=c2,
        c3=c3,
        c5=c5,
        c6_x=c6_x,
        api13_dword6=api13_dword6,
        api13_dword7=api13_dword7,
    )
    return PixelReplay809DCD66(
        base_uv=base_uv.copy(),
        displaced_uv=p.displaced_uv,
        t0_r=t0,
        t1_r=t1,
        rgb=rgb,
        parallax=p,
    )
