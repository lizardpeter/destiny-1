#!/usr/bin/env python3
"""Scoped semantic replay of Tower VS 80CA0DDA pixel-facing varyings.

Retail differential proof against the already-closed static-world VS 80CA0CB7
shows that 80CA0DDA keeps the same instance affine, UV affine and tangent-basis
arithmetic while reducing the native input interface:

  80CA0CB7: sem1 -> v8..v11, sem4 -> v20
  80CA0DDA: sem1 -> v8..v9,  no sem4

The reduced shader hardcodes the removed control exports:

  param0.w = 1
  param3.z = 0
  param3.w = 1

Position, UV.xy, normal.xyz and tangent.xyzw therefore reuse the already-locked
Tower stride-8 + stride-24 branch-A source reconstruction.  This module replays
only the native varyings that feed pixel shader 809DCD66; it does not assign
PBR semantics or emulate the later view/projection position export.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from d1_tower_80ca0cb7_static_inputs import StaticInputs80CA0CB7
from d1_tower_80ca0cb7_vs_replay import instance_basis, instance_positions

VS_HASH = "80CA0DDA"


def _record(record16) -> np.ndarray:
    r = np.asarray(record16, dtype=np.float32)
    if r.shape == (4, 4):
        return r
    if r.shape == (16,):
        return r.reshape(4, 4)
    raise ValueError("instance record must be 16 floats or a 4x4 array")


@dataclass(frozen=True)
class PixelVaryings80CA0DDA:
    """Exact semantic replay of param0..param4 before interpolation."""

    param0: np.ndarray
    param1: np.ndarray
    param2: np.ndarray
    param3: np.ndarray
    param4: np.ndarray

    @property
    def normal(self) -> np.ndarray:
        return self.param0[:, :3]

    @property
    def tangent(self) -> np.ndarray:
        return self.param1[:, :3]

    @property
    def bitangent(self) -> np.ndarray:
        return self.param2[:, :3]

    @property
    def uv(self) -> np.ndarray:
        return self.param3[:, :2]

    @property
    def world_position(self) -> np.ndarray:
        return self.param4[:, :3]


def replay_pixel_varyings(inputs: StaticInputs80CA0CB7, record16) -> PixelVaryings80CA0DDA:
    """Replay the exact 80CA0DDA varyings consumed by PS 809DCD66.

    ``record16`` is the exact 16-float static instance record.  Rows 0..2 are
    the 3x4 affine.  Dwords 12..15 are the same static UV-control row already
    proven for 80CA0CB7, where:

      uv.x = s9  + s8 * source_uv.x
      uv.y = s10 + s8 * source_uv.y

    80CA0DDA does not fetch the adjacent packed source-control words or primary
    position-W lane used by 80CA0CB7.
    """
    r = _record(record16)
    world = instance_positions(inputs.v4_v6_position, r)
    basis = instance_basis(inputs, r)
    n = inputs.vertex_count

    s8, s9, s10, _s11 = r[3]
    uv = np.empty((n, 2), dtype=np.float32)
    uv[:, 0] = np.float32(s9) + np.float32(s8) * inputs.v8_v11_uv_control[:, 0]
    uv[:, 1] = np.float32(s10) + np.float32(s8) * inputs.v8_v11_uv_control[:, 1]

    param0 = np.empty((n, 4), dtype=np.float32)
    param0[:, :3] = basis.attr0_normal
    param0[:, 3] = np.float32(1.0)

    param1 = np.empty((n, 4), dtype=np.float32)
    param1[:, :3] = basis.attr1_tangent
    # Exact GCN export repeats the third transformed tangent lane in W.
    param1[:, 3] = basis.attr1_tangent[:, 2]

    param2 = np.empty((n, 4), dtype=np.float32)
    param2[:, :3] = basis.attr2_bitangent
    param2[:, 3] = np.float32(1.0)

    param3 = np.empty((n, 4), dtype=np.float32)
    param3[:, :2] = uv
    param3[:, 2] = np.float32(0.0)
    param3[:, 3] = np.float32(1.0)

    param4 = np.empty((n, 4), dtype=np.float32)
    param4[:, :3] = world
    param4[:, 3] = np.float32(1.0)

    return PixelVaryings80CA0DDA(
        param0=param0,
        param1=param1,
        param2=param2,
        param3=param3,
        param4=param4,
    )
