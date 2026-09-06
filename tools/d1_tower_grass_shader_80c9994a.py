#!/usr/bin/env python3
"""Reference arithmetic for the Tower grass pixel shader 80C9994A.

This module intentionally models only operations closed directly from the native
PS4 GCN disassembly and exact material constants for material 80C9993C.  It does
not guess the unresolved runtime vertex-fetch mapping, blend/render state, or
VS input descriptor formats.

Exact texture bindings for 80C9993C:
  t0 = 80C9988C (BC3)
  t1 = 80C9988D (BC5)
  t2 = 80C9988C (same BC3, second coordinate scale)
  t3 = 80C9988D (same BC5, second coordinate scale)
  t4 = 80C9988E (BC4 scalar blend mask)

The native PS computes:
  weight = saturate(3 * attr3.w - 2 * t4.r)

That same weight selects between the two BC3 colour branches and the two BC5
normal branches.  BC3 alpha is *not* used as plane opacity.  MRT0 alpha comes
from interpolated attr0.w, which the paired VS 80CA0CB7 exports from v20.
"""
from __future__ import annotations

import numpy as np

MATERIAL = "80C9993C"
VERTEX_SHADER = "80CA0CB7"
PIXEL_SHADER = "80C9994A"
TEXTURE_SLOTS = {
    0: "80C9988C",
    1: "80C9988D",
    2: "80C9988C",
    3: "80C9988D",
    4: "80C9988E",
}

# Exact material constants consumed by the relevant PS paths.
UV_BRANCH0_SCALE = np.float32(3.662899971008301)
UV_BRANCH0_BIAS = np.array([0.25029999017715454, 0.0], dtype=np.float32)
UV_BRANCH2_SCALE = np.float32(4.5)
UV_BRANCH2_BIAS = np.array([0.0, 0.0], dtype=np.float32)
BLEND_SCALE = np.float32(3.0)
MASK_SCALE = np.float32(-2.0)
BRANCH0_RGB_SUB = np.float32(0.25)
BRANCH0_RGB_MUL = np.float32(4.0)


def saturate(x):
    """AMD/PSSL clamp modifier used by the shader: clamp to [0, 1]."""
    return np.clip(np.asarray(x, dtype=np.float32), 0.0, 1.0)


def blend_weight(attr3_w, mask_r):
    """Exact 80C9994A material-selection weight.

    Native GCN: v6 = clamp(s0 * attr3.w + s1 * t4.r), where vec11.xy is
    [3.0, -2.0].
    """
    control = np.asarray(attr3_w, dtype=np.float32)
    mask = np.asarray(mask_r, dtype=np.float32)
    return saturate(BLEND_SCALE * control + MASK_SCALE * mask)


def ps_uvs(attr3_xy):
    """Return the three PS texture-coordinate pairs derived from attr3.xy.

    attr3.xy is already the paired VS output.  This routine deliberately does
    not apply the still draw-dependent VS scale/bias that produces attr3.xy.
    """
    uv = np.asarray(attr3_xy, dtype=np.float32)
    if uv.shape[-1] != 2:
        raise ValueError("attr3_xy must have a final dimension of 2")
    branch0 = UV_BRANCH0_SCALE * uv + UV_BRANCH0_BIAS
    branch2 = UV_BRANCH2_SCALE * uv + UV_BRANCH2_BIAS
    mask = UV_BRANCH2_SCALE * uv + UV_BRANCH2_BIAS
    return branch0, branch2, mask


def branch0_rgb(t0_rgb, tint_rgb):
    """Exact adjusted t0 RGB branch before the two-branch lerp.

    GCN forms saturate(t0.rgb - 0.25) plus
    tint.rgb * saturate(4 * t0.rgb).
    """
    t0 = np.asarray(t0_rgb, dtype=np.float32)
    tint = np.asarray(tint_rgb, dtype=np.float32)
    if t0.shape[-1] != 3 or tint.shape[-1] != 3:
        raise ValueError("RGB inputs must have a final dimension of 3")
    return saturate(t0 - BRANCH0_RGB_SUB) + tint * saturate(BRANCH0_RGB_MUL * t0)


def base_rgb(t0_rgb, t2_rgb, mask_r, attr3_w, tint_rgb):
    """Exact RGB branch selection from 80C9994A."""
    a = branch0_rgb(t0_rgb, tint_rgb)
    b = np.asarray(t2_rgb, dtype=np.float32)
    if b.shape[-1] != 3:
        raise ValueError("t2_rgb must have a final dimension of 3")
    w = blend_weight(attr3_w, mask_r)
    return b + np.expand_dims(w, axis=-1) * (a - b)


def auxiliary_alpha(t0_a, t2_a, mask_r, attr3_w):
    """Scalar BC3-alpha branch used internally by the shader.

    This is not MRT0 opacity.  It is retained because it participates in the
    later normal/output auxiliary math.
    """
    a0 = saturate(np.asarray(t0_a, dtype=np.float32) - BRANCH0_RGB_SUB)
    a2 = np.asarray(t2_a, dtype=np.float32)
    w = blend_weight(attr3_w, mask_r)
    return a2 + w * (a0 - a2)


def decode_bc5_xy(sample_rg):
    """Decode the BC5 RG sample into signed tangent-space X/Y."""
    rg = np.asarray(sample_rg, dtype=np.float32)
    if rg.shape[-1] != 2:
        raise ValueError("BC5 input must have a final dimension of 2")
    return np.float32(2.0) * rg - np.float32(1.0)


def normal_xy(t1_rg, t3_rg, mask_r, attr3_w):
    """Exact two-branch BC5 XY lerp performed before Z reconstruction."""
    n1 = decode_bc5_xy(t1_rg)
    n3 = decode_bc5_xy(t3_rg)
    w = blend_weight(attr3_w, mask_r)
    return n3 + np.expand_dims(w, axis=-1) * (n1 - n3)


def reconstruct_normal_z(xy):
    """PS normal-Z reconstruction: sqrt(saturate(1 - x*x - y*y))."""
    v = np.asarray(xy, dtype=np.float32)
    if v.shape[-1] != 2:
        raise ValueError("normal xy must have a final dimension of 2")
    z2 = saturate(np.float32(1.0) - np.sum(v * v, axis=-1))
    return np.sqrt(z2).astype(np.float32)
