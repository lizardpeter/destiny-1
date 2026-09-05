#!/usr/bin/env python3
"""Shared Destiny 1 ROI world/static export utilities.

This module deliberately separates the 0x40 baked-static instance record into the
parts the retail D1 map code actually uses:

  +0x00..+0x2F  3x4 affine object transform
  +0x30         float UV scale
  +0x34         float UV translate X
  +0x38         float UV translate Y
  +0x3C         fourth row tail/unknown (NOT part of the affine transform)

MontevenDynamicExtractor's D1Map::GetDataTable independently parses the same
record this way and later applies the three UV values per instance. Treating the
last 16 bytes as a fourth matrix row creates a projective glTF/Blender transform
and is incorrect even though numpy/trimesh bounds can look plausible because
many of their point-transform paths only consume the upper 3x4.

D1 world coordinates are Z-up. glTF 2.0's conventional world basis is Y-up. The
D1_TO_GLTF_Y_UP matrix is therefore an export-adapter basis conversion; it does
not alter the source-space placement evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np


D1_TO_GLTF_Y_UP = np.array([
    [1.0,  0.0, 0.0, 0.0],
    [0.0,  0.0, 1.0, 0.0],
    [0.0, -1.0, 0.0, 0.0],
    [0.0,  0.0, 0.0, 1.0],
], dtype=np.float64)


@dataclass(frozen=True)
class D1StaticInstanceRecord:
    affine: np.ndarray
    uv_scale: float
    uv_translate_x: float
    uv_translate_y: float
    tail_3c: float

    @property
    def uv_transform(self) -> tuple[float, float, float]:
        return (self.uv_scale, self.uv_translate_x, self.uv_translate_y)


def parse_static_instance_records(data: bytes, count: int) -> list[D1StaticInstanceRecord]:
    expected = count * 0x40
    if len(data) != expected:
        raise ValueError(f"transform backing {len(data)} != {count}*0x40 ({expected})")
    vals = np.frombuffer(data, dtype="<f4").reshape(count, 4, 4)
    if not np.isfinite(vals).all():
        raise ValueError("non-finite D1 baked-static instance record")

    out: list[D1StaticInstanceRecord] = []
    for raw in vals:
        m = np.eye(4, dtype=np.float64)
        # Only the first three shipped rows are the affine SRT matrix. The final
        # row is per-instance UV metadata, not homogeneous transform data.
        m[:3, :4] = raw[:3, :4].astype(np.float64)
        out.append(D1StaticInstanceRecord(
            affine=m,
            uv_scale=float(raw[3, 0]),
            uv_translate_x=float(raw[3, 1]),
            uv_translate_y=float(raw[3, 2]),
            tail_3c=float(raw[3, 3]),
        ))
    return out


def affine_matrix_records(data: bytes, count: int) -> list[np.ndarray]:
    return [x.affine for x in parse_static_instance_records(data, count)]


def apply_d1_instance_uv(uv: np.ndarray, uv_scale: float, tx: float, ty: float) -> np.ndarray:
    """Apply the shipped D1 baked-static per-instance UV transform.

    Cross-source D1 implementation:
      u = u * scale + tx
      v = v * -scale + 1 - ty
    """
    a = np.asarray(uv, dtype=np.float32)
    if a.ndim != 2 or a.shape[1] != 2:
        raise ValueError(f"UV array must be Nx2, got {a.shape}")
    out = a.copy()
    out[:, 0] = out[:, 0] * uv_scale + tx
    out[:, 1] = out[:, 1] * (-uv_scale) + (1.0 - ty)
    return out


def d1_world_to_gltf_matrix(m: np.ndarray) -> np.ndarray:
    """Left-multiply a D1 world transform by the Z-up -> glTF Y-up adapter.

    Local packed vertex coordinates remain byte-faithful. This is equivalent to
    putting one D1_TO_GLTF_Y_UP root above the entire scene, while being robust
    to exporters that flatten scene graph roots.
    """
    a = np.asarray(m, dtype=np.float64)
    if a.shape != (4, 4):
        raise ValueError(a.shape)
    return D1_TO_GLTF_Y_UP @ a
