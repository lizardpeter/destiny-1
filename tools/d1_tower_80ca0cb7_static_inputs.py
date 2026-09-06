#!/usr/bin/env python3
"""Scoped source-to-VGPR reconstruction for Tower VS 80CA0CB7.

This is deliberately *not* a generic Destiny 1 vertex-layout declaration and it
is not a claim that Sony GnmBuffer descriptor bytes have been recovered.

The scope is the retail Tower baked-static family for which all of the following
have been independently closed:

* primary stride = 0x08;
* secondary stride = 0x18;
* material vertex shader = 80CA0CB7;
* the native VS header has five input semantics with component spans
  (v4..v6), (v8..v11), (v12..v14), (v16..v19), and v20;
* all 59 resolved 8+24 draws in table 80C99827 use VS 80CA0CB7;
* all 26 secondary backing buffers and all 18,137 referenced retail vertices
  satisfy the D1 stride-0x18 branch-A serialization:
      UV/control @ +0x00 (8 bytes)
      normal     @ +0x08 (int16x4; W stored but VS semantic is XYZ)
      tangent    @ +0x10 (int16x4)
  with zero branch-B vertices in the entire scoped family;
* archived D1 readers independently normalize these packed int16 values by
  32767, matching the ordinary per-instance UV scales consumed by 80CA0CB7.

Within that scope, byte exhaustion plus the exact VS semantic component counts
produce one coherent source-word mapping:

  stream 0 (stride 8)
    +0x00 int16x3 -> v4,v5,v6      position xyz
    +0x06 int16x1 -> v20           source position-W scalar

  stream 1 (stride 24, branch A)
    +0x00 int16x4 -> v8..v11       UV.xy + two material-control words
    +0x08 int16x3 -> v12..v14      normal xyz
    +0x0E int16   -> stored normal W, not fetched by the 3-component semantic
    +0x10 int16x4 -> v16..v19      tangent xyzw

For material 80C9993C specifically, v10 is zero, v11 spans [0, 1], and v20 is
1.0 on both visible draw ranges.  The paired VS exports:

  attr3.xy = (s9,s10) + s8 * (v8,v9)
  attr3.zw = (v10,v11)
  attr0.w  = v20

where s8..s11 are dwords 12..15 (+0x30..+0x3C) of the exact 0x40 instance
record.  No glTF/PBR meaning is assigned here.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

VS_HASH = "80CA0CB7"
PRIMARY_STRIDE = 0x08
SECONDARY_STRIDE = 0x18


def snorm16(raw: np.ndarray) -> np.ndarray:
    """D1 packed signed-16 normalization used by the pinned source readers."""
    a = np.asarray(raw, dtype=np.int16)
    out = a.astype(np.float32) / np.float32(32767.0)
    return np.maximum(out, np.float32(-1.0))


def _i16_words(data: bytes, stride: int) -> np.ndarray:
    if stride <= 0 or len(data) % stride:
        raise ValueError(f"payload size {len(data)} is not divisible by stride {stride}")
    return np.frombuffer(data, dtype='<i2').reshape(len(data) // stride, stride // 2)


def branch_a_mask(v1: bytes) -> np.ndarray:
    """Return the measured Charm/D1 stride-0x18 branch-A selector per vertex."""
    if len(v1) % SECONDARY_STRIDE:
        raise ValueError("secondary payload is not stride-0x18 aligned")
    b = np.frombuffer(v1, dtype=np.uint8).reshape(-1, SECONDARY_STRIDE)
    normal_w = np.frombuffer(b[:, 0x0E:0x10].copy().tobytes(), dtype='<i2')
    tangent_w = np.frombuffer(b[:, 0x16:0x18].copy().tobytes(), dtype='<i2')
    return (normal_w == 0) & ((tangent_w == 32767) | (tangent_w == -32767))


@dataclass(frozen=True)
class StaticInputs80CA0CB7:
    """Raw and normalized inputs reconstructed for the scoped Tower family."""

    # Native VS input groups, normalized exactly as D1 signed packed shorts.
    v4_v6_position: np.ndarray
    v8_v11_uv_control: np.ndarray
    v12_v14_normal: np.ndarray
    v16_v19_tangent: np.ndarray
    v20_scalar: np.ndarray

    # Matching untouched signed source words for forensic round-trip checks.
    raw_v4_v6_position: np.ndarray
    raw_v8_v11_uv_control: np.ndarray
    raw_v12_v14_normal: np.ndarray
    raw_v16_v19_tangent: np.ndarray
    raw_v20_scalar: np.ndarray
    raw_stored_normal_w: np.ndarray
    branch_a: np.ndarray

    @property
    def vertex_count(self) -> int:
        return int(len(self.v20_scalar))

    def attr3(self, instance_dwords12_15) -> np.ndarray:
        """Replay the exact 80CA0CB7 param3 export for one instance record.

        ``instance_dwords12_15`` is the four-float source slice at +0x30..+0x3C.
        Only s8,s9,s10 are used by this export; s11 is preserved by callers if
        needed elsewhere.
        """
        c = np.asarray(instance_dwords12_15, dtype=np.float32)
        if c.shape != (4,):
            raise ValueError("instance_dwords12_15 must contain exactly four floats")
        s8, s9, s10, _s11 = c
        out = np.empty((self.vertex_count, 4), dtype=np.float32)
        out[:, 0] = s9 + s8 * self.v8_v11_uv_control[:, 0]
        out[:, 1] = s10 + s8 * self.v8_v11_uv_control[:, 1]
        out[:, 2] = self.v8_v11_uv_control[:, 2]
        out[:, 3] = self.v8_v11_uv_control[:, 3]
        return out

    @property
    def attr0_w(self) -> np.ndarray:
        """Exact VS source for param0.w / PS attr0.w in this shader family."""
        return self.v20_scalar


def decode_static_inputs(
    v0: bytes,
    v1: bytes,
    *,
    used_indices: np.ndarray | list[int] | tuple[int, ...] | None = None,
    require_all_branch_a: bool = True,
) -> StaticInputs80CA0CB7:
    """Decode the scoped 8+24 Tower source layout into 80CA0CB7 inputs.

    The routine fails closed on a branch-B vertex.  By default every backing
    vertex must be branch A, matching the retail 80C99827 census.  A caller may
    set ``require_all_branch_a=False`` to gate only explicitly supplied used
    indices, but no branch-B vertex is ever decoded through this mapping.
    """
    if len(v0) % PRIMARY_STRIDE:
        raise ValueError("primary payload is not stride-0x08 aligned")
    if len(v1) % SECONDARY_STRIDE:
        raise ValueError("secondary payload is not stride-0x18 aligned")
    n0 = len(v0) // PRIMARY_STRIDE
    n1 = len(v1) // SECONDARY_STRIDE
    if n0 != n1:
        raise ValueError(f"primary/secondary vertex-count mismatch: {n0} != {n1}")

    a = branch_a_mask(v1)
    if used_indices is None:
        selected = np.arange(n0, dtype=np.int64)
    else:
        selected = np.asarray(used_indices, dtype=np.int64).reshape(-1)
        if len(selected) == 0:
            raise ValueError("used_indices cannot be empty")
        if int(selected.min()) < 0 or int(selected.max()) >= n0:
            raise ValueError("used_indices escaped source vertex bounds")
    if require_all_branch_a:
        bad = np.flatnonzero(~a)
        if len(bad):
            raise ValueError(f"scoped 80CA0CB7 mapping rejected {len(bad)} branch-B backing vertices")
    else:
        bad_used = selected[~a[selected]]
        if len(bad_used):
            raise ValueError(f"scoped 80CA0CB7 mapping rejected {len(bad_used)} referenced branch-B vertices")

    p = _i16_words(v0, PRIMARY_STRIDE)
    s = _i16_words(v1, SECONDARY_STRIDE)

    # Branch A byte layout, expressed directly in signed 16-bit source words.
    raw_pos = p[:, 0:3].copy()
    raw_w = p[:, 3].copy()
    raw_uv_control = s[:, 0:4].copy()
    raw_normal = s[:, 4:7].copy()
    raw_normal_w = s[:, 7].copy()
    raw_tangent = s[:, 8:12].copy()

    return StaticInputs80CA0CB7(
        v4_v6_position=snorm16(raw_pos),
        v8_v11_uv_control=snorm16(raw_uv_control),
        v12_v14_normal=snorm16(raw_normal),
        v16_v19_tangent=snorm16(raw_tangent),
        v20_scalar=snorm16(raw_w),
        raw_v4_v6_position=raw_pos,
        raw_v8_v11_uv_control=raw_uv_control,
        raw_v12_v14_normal=raw_normal,
        raw_v16_v19_tangent=raw_tangent,
        raw_v20_scalar=raw_w,
        raw_stored_normal_w=raw_normal_w,
        branch_a=a.copy(),
    )
