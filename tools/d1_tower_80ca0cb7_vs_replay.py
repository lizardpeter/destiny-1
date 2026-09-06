#!/usr/bin/env python3
"""Scoped semantic replay of Tower VS 80CA0CB7 instance outputs.

This module builds on ``d1_tower_80ca0cb7_static_inputs`` and replays the
source-closed portion of the native GCN vertex shader which produces world/model
position and the three basis varyings consumed by pixel shader 80C9994A.

From the exact disassembly:

  P = (row0.xyz dot position + row0.w,
       row1.xyz dot position + row1.w,
       row2.xyz dot position + row2.w)

  Nraw = M3x3 * sourceNormal
  invN  = rsq(dot(Nraw,Nraw))
  attr0.xyz = Nraw * invN
  attr1.xyz = (M3x3 * sourceTangent.xyz) * invN
  attr2.xyz = sourceTangent.w * cross(attr0.xyz, attr1.xyz)
  attr0.w   = v20

The shader uses the *normal* reciprocal length for both attr0 and attr1.  That
is intentionally preserved instead of independently normalizing the tangent.
The routine uses ordinary float32 reciprocal sqrt for the semantic replay; it is
not a bit-for-bit emulator of the GCN v_rsq_f32 approximation.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from d1_tower_80ca0cb7_static_inputs import StaticInputs80CA0CB7

VS_HASH = "80CA0CB7"


def _record(record16) -> np.ndarray:
    r = np.asarray(record16, dtype=np.float32)
    if r.shape == (4, 4):
        return r
    if r.shape == (16,):
        return r.reshape(4, 4)
    raise ValueError("instance record must be 16 floats or a 4x4 array")


def _row_dot_xyz(rows: np.ndarray, vectors: np.ndarray) -> np.ndarray:
    """Replay the GCN z + y + x multiply/add ordering in float32."""
    v = np.asarray(vectors, dtype=np.float32)
    out = np.empty((len(v), 3), dtype=np.float32)
    for axis in range(3):
        row = rows[axis]
        q = np.float32(row[2]) * v[:, 2]
        q = np.float32(row[1]) * v[:, 1] + q
        q = np.float32(row[0]) * v[:, 0] + q
        out[:, axis] = q
    return out


def instance_positions(source_positions: np.ndarray, record16) -> np.ndarray:
    """Replay the instance-record affine before the later view/projection CB."""
    r = _record(record16)
    p = np.asarray(source_positions, dtype=np.float32)
    if p.ndim != 2 or p.shape[1] != 3:
        raise ValueError("source_positions must be Nx3")
    out = _row_dot_xyz(r[:3, :3], p)
    out[:, 0] = np.float32(r[0, 3]) + out[:, 0]
    out[:, 1] = np.float32(r[1, 3]) + out[:, 1]
    out[:, 2] = np.float32(r[2, 3]) + out[:, 2]
    return out


@dataclass(frozen=True)
class BasisOutputs80CA0CB7:
    attr0_normal: np.ndarray
    attr1_tangent: np.ndarray
    attr2_bitangent: np.ndarray
    attr0_w: np.ndarray
    normal_length: np.ndarray
    tangent_w: np.ndarray


def instance_basis(inputs: StaticInputs80CA0CB7, record16) -> BasisOutputs80CA0CB7:
    """Replay the attr0/attr1/attr2 basis exports of 80CA0CB7."""
    r = _record(record16)
    nraw = _row_dot_xyz(r[:3, :3], inputs.v12_v14_normal)
    traw = _row_dot_xyz(r[:3, :3], inputs.v16_v19_tangent[:, :3])

    # The native program computes dot by three float32 mul/mac operations before
    # v_rsq_f32.  Preserve float32 accumulation order, then use semantic rsqrt.
    length2 = np.float32(nraw[:, 1] * nraw[:, 1])
    length2 = np.float32(nraw[:, 0] * nraw[:, 0] + length2)
    length2 = np.float32(nraw[:, 2] * nraw[:, 2] + length2)
    if np.any(~np.isfinite(length2)) or np.any(length2 <= 0):
        raise ValueError("invalid transformed normal length")
    length = np.sqrt(length2, dtype=np.float32)
    inv = np.float32(1.0) / length

    attr0 = nraw * inv[:, None]
    attr1 = traw * inv[:, None]
    tw = inputs.v16_v19_tangent[:, 3].astype(np.float32, copy=False)
    attr2 = np.cross(attr0, attr1).astype(np.float32) * tw[:, None]
    return BasisOutputs80CA0CB7(
        attr0_normal=attr0.astype(np.float32),
        attr1_tangent=attr1.astype(np.float32),
        attr2_bitangent=attr2.astype(np.float32),
        attr0_w=inputs.v20_scalar.astype(np.float32, copy=True),
        normal_length=length.astype(np.float32),
        tangent_w=tw.copy(),
    )
