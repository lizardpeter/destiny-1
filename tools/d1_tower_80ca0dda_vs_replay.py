#!/usr/bin/env python3
"""Scoped source decode and semantic replay for Tower VS 80CA0DDA.

Retail PS4 evidence closes this family more tightly than the earlier 80CA0CB7
comparison alone:

* native input interface:
    semantic0 -> v4..v6   (3 components)
    semantic1 -> v8..v9   (2 components)
    semantic2 -> v12..v14 (3 components)
    semantic3 -> v16..v19 (4 components)
* target Tower geometry using PS 809DCD66 is primary stride 0x08 plus secondary
  stride 0x14 (20 bytes), not the 0x18 control-bearing sibling layout;
* pinned D1 ReadD1VertexData gives the unambiguous 8+20 serialization:

    primary +0x00 int16x3 -> position xyz
    primary +0x06 int16   -> stored source word, not fetched by this VS

    secondary +0x00 int16x2 -> UV xy
    secondary +0x04 int16x4 -> normal storage; VS fetches xyz
    secondary +0x0C int16x4 -> tangent xyzw

The native GCN shares the same instance affine, UV affine, transformed tangent
basis and world-position construction as 80CA0CB7, but hardcodes the removed
control outputs:

    param0.w = 1
    param3.z = 0
    param3.w = 1

This module replays param0..param4 exactly at semantic float32 level.  It does
not emulate GCN rsq bit-for-bit and does not assign glTF/PBR meanings.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

VS_HASH = "80CA0DDA"
PRIMARY_STRIDE = 0x08
SECONDARY_STRIDE = 0x14


def snorm16(raw: np.ndarray) -> np.ndarray:
    a = np.asarray(raw, dtype=np.int16)
    x = a.astype(np.float32) / np.float32(32767.0)
    return np.maximum(x, np.float32(-1.0))


def _i16_words(data: bytes, stride: int) -> np.ndarray:
    if stride <= 0 or len(data) % stride:
        raise ValueError(f"payload size {len(data)} is not divisible by stride {stride}")
    return np.frombuffer(data, dtype='<i2').reshape(len(data) // stride, stride // 2)


@dataclass(frozen=True)
class StaticInputs80CA0DDA:
    v4_v6_position: np.ndarray
    v8_v9_uv: np.ndarray
    v12_v14_normal: np.ndarray
    v16_v19_tangent: np.ndarray
    raw_position: np.ndarray
    raw_primary_word3: np.ndarray
    raw_uv: np.ndarray
    raw_normal_storage: np.ndarray
    raw_tangent: np.ndarray

    @property
    def vertex_count(self) -> int:
        return int(len(self.v4_v6_position))


def decode_static_inputs(v0: bytes, v1: bytes) -> StaticInputs80CA0DDA:
    """Decode the exact scoped 8+20 retail source layout."""
    p = _i16_words(v0, PRIMARY_STRIDE)
    s = _i16_words(v1, SECONDARY_STRIDE)
    if len(p) != len(s):
        raise ValueError(f"primary/secondary vertex-count mismatch: {len(p)} != {len(s)}")

    raw_pos = p[:, 0:3].copy()
    raw_p3 = p[:, 3].copy()
    raw_uv = s[:, 0:2].copy()
    raw_norm4 = s[:, 2:6].copy()
    raw_tan = s[:, 6:10].copy()

    out = StaticInputs80CA0DDA(
        v4_v6_position=snorm16(raw_pos),
        v8_v9_uv=snorm16(raw_uv),
        v12_v14_normal=snorm16(raw_norm4[:, :3]),
        v16_v19_tangent=snorm16(raw_tan),
        raw_position=raw_pos,
        raw_primary_word3=raw_p3,
        raw_uv=raw_uv,
        raw_normal_storage=raw_norm4,
        raw_tangent=raw_tan,
    )
    for name, a in (
        ('position', out.v4_v6_position), ('uv', out.v8_v9_uv),
        ('normal', out.v12_v14_normal), ('tangent', out.v16_v19_tangent),
    ):
        if not np.isfinite(a).all():
            raise ValueError(f"non-finite decoded {name}")
    return out


def _record(record16) -> np.ndarray:
    r = np.asarray(record16, dtype=np.float32)
    if r.shape == (4, 4):
        return r
    if r.shape == (16,):
        return r.reshape(4, 4)
    raise ValueError("instance record must be 16 floats or a 4x4 array")


def record_from_sidecar(source_affine, uv_transform, tail_0x3c: float) -> np.ndarray:
    """Reconstruct the exact shader-facing 16-float record from world sidecar fields.

    World export stores rows 0..2 as ``source_affine`` and exposes the shader's
    dwords 12..14 separately as ``uv_transform``; dword 15 is ``tail_0x3c``.
    """
    a = np.asarray(source_affine, dtype=np.float32)
    uv = np.asarray(uv_transform, dtype=np.float32)
    if a.shape != (4, 4) or uv.shape != (3,):
        raise ValueError("source_affine must be 4x4 and uv_transform must have 3 floats")
    r = np.empty((4, 4), dtype=np.float32)
    r[:3, :] = a[:3, :]
    r[3, :3] = uv
    r[3, 3] = np.float32(tail_0x3c)
    return r


def _row_dot_xyz(rows: np.ndarray, vectors: np.ndarray) -> np.ndarray:
    v = np.asarray(vectors, dtype=np.float32)
    out = np.empty((len(v), 3), dtype=np.float32)
    for axis in range(3):
        row = rows[axis]
        q = np.float32(row[2]) * v[:, 2]
        q = np.float32(row[1]) * v[:, 1] + q
        q = np.float32(row[0]) * v[:, 0] + q
        out[:, axis] = q
    return out


@dataclass(frozen=True)
class PixelVaryings80CA0DDA:
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


def replay_pixel_varyings(inputs: StaticInputs80CA0DDA, record16) -> PixelVaryings80CA0DDA:
    """Replay param0..param4 exported by native 80CA0DDA before interpolation."""
    r = _record(record16)
    n = inputs.vertex_count

    world = _row_dot_xyz(r[:3, :3], inputs.v4_v6_position)
    world[:, 0] = np.float32(r[0, 3]) + world[:, 0]
    world[:, 1] = np.float32(r[1, 3]) + world[:, 1]
    world[:, 2] = np.float32(r[2, 3]) + world[:, 2]

    nraw = _row_dot_xyz(r[:3, :3], inputs.v12_v14_normal)
    traw = _row_dot_xyz(r[:3, :3], inputs.v16_v19_tangent[:, :3])
    length2 = np.float32(nraw[:, 1] * nraw[:, 1])
    length2 = np.float32(nraw[:, 0] * nraw[:, 0] + length2)
    length2 = np.float32(nraw[:, 2] * nraw[:, 2] + length2)
    if np.any(~np.isfinite(length2)) or np.any(length2 <= 0):
        raise ValueError("invalid transformed normal length")
    inv = np.float32(1.0) / np.sqrt(length2, dtype=np.float32)
    normal = nraw * inv[:, None]
    tangent = traw * inv[:, None]
    tangent_w = inputs.v16_v19_tangent[:, 3]
    bitangent = np.cross(normal, tangent).astype(np.float32) * tangent_w[:, None]

    s8, s9, s10, _s11 = r[3]
    uv = np.empty((n, 2), dtype=np.float32)
    uv[:, 0] = np.float32(s9) + np.float32(s8) * inputs.v8_v9_uv[:, 0]
    uv[:, 1] = np.float32(s10) + np.float32(s8) * inputs.v8_v9_uv[:, 1]

    param0 = np.empty((n, 4), dtype=np.float32)
    param0[:, :3] = normal
    param0[:, 3] = np.float32(1.0)

    param1 = np.empty((n, 4), dtype=np.float32)
    param1[:, :3] = tangent
    param1[:, 3] = tangent[:, 2]  # native export duplicates v4

    param2 = np.empty((n, 4), dtype=np.float32)
    param2[:, :3] = bitangent
    param2[:, 3] = np.float32(1.0)

    param3 = np.empty((n, 4), dtype=np.float32)
    param3[:, :2] = uv
    param3[:, 2] = np.float32(0.0)
    param3[:, 3] = np.float32(1.0)

    param4 = np.empty((n, 4), dtype=np.float32)
    param4[:, :3] = world
    param4[:, 3] = np.float32(1.0)

    for a in (param0, param1, param2, param3, param4):
        if not np.isfinite(a).all():
            raise ValueError("non-finite 80CA0DDA varying")

    return PixelVaryings80CA0DDA(param0, param1, param2, param3, param4)
