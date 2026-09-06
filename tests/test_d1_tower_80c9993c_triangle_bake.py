import importlib.util
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'tools'
sys.path.insert(0, str(TOOLS))
SPEC = importlib.util.spec_from_file_location(
    'grass_bake80c9993c', TOOLS / 'd1_tower_80c9993c_triangle_bake.py'
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules['grass_bake80c9993c'] = mod
SPEC.loader.exec_module(mod)


def test_srgb_roundtrip_reference_values():
    x = np.array([0.0, 0.003, 0.04045, 0.2, 0.5, 1.0], dtype=np.float32)
    y = mod.linear_to_srgb(mod.srgb_to_linear(x))
    np.testing.assert_allclose(y, x, rtol=0, atol=2e-6)


def test_repeat_bilinear_texel_centers_and_wrap():
    # Four scalar texels stored as RGBA channels for easy exact checks.
    im = np.zeros((2, 2, 4), dtype=np.float32)
    im[0, 0] = [0, 0, 0, 1]
    im[0, 1] = [1, 0, 0, 1]
    im[1, 0] = [0, 1, 0, 1]
    im[1, 1] = [1, 1, 0, 1]
    # Normalized texel centers for a 2x2 texture.
    uv = np.array([[0.25,0.25], [0.75,0.25], [0.25,0.75], [0.75,0.75]], dtype=np.float32)
    got = mod.sample_repeat_bilinear(im, uv)
    np.testing.assert_allclose(got, im.reshape(-1,4), rtol=0, atol=1e-7)
    # Integer shifts must wrap exactly to the same samples.
    got_wrap = mod.sample_repeat_bilinear(im, uv + np.array([2.0,-3.0], dtype=np.float32))
    np.testing.assert_allclose(got_wrap, got, rtol=0, atol=1e-7)
    # u=v=0 lies on the wrapped corner between all four texels.
    center = mod.sample_repeat_bilinear(im, np.array([0.0,0.0], dtype=np.float32))
    np.testing.assert_allclose(center, np.mean(im.reshape(-1,4),axis=0), rtol=0, atol=1e-7)


def test_private_cell_barycentrics_are_normalized_and_vertices_exact():
    bary, pix = mod.atlas_cell_barycentrics(64, 3)
    assert bary.shape == (64,64,3)
    np.testing.assert_allclose(np.sum(bary,axis=-1), 1.0, rtol=0, atol=1e-6)
    assert np.all(bary >= 0.0)
    # The declared vertex pixel centers must evaluate to one-hot coordinates.
    for i, p in enumerate(pix):
        x = int(np.floor(p[0])); y = int(np.floor(p[1]))
        want = np.zeros(3,dtype=np.float32); want[i] = 1.0
        np.testing.assert_allclose(bary[y,x], want, rtol=0, atol=1e-6)


def test_bake_cell_native_branch_endpoints_constant_textures():
    # Constant source maps remove texture-coordinate dependence entirely.
    color_srgb = np.empty((2,2,4),dtype=np.float32)
    color_srgb[...] = [0.6,0.3,0.1,0.8]
    color_linear = color_srgb.copy()
    color_linear[...,:3] = mod.srgb_to_linear(color_srgb[...,:3])
    mask_zero = np.zeros((2,2,4),dtype=np.float32)
    mask_one = np.ones((2,2,4),dtype=np.float32)
    bary, _ = mod.atlas_cell_barycentrics(16,2)

    # attr3.w=0 and mask=1 forces w=0 -> unadjusted t2.
    attr_zero = np.array([[0,0,0,0]]*3,dtype=np.float32)
    out0 = mod.bake_cell(attr_zero,color_linear,mask_one,bary)
    np.testing.assert_array_equal(out0[...,3], 255)
    # Re-encoding the linearized constant should recover the original sRGB byte values.
    expected0 = np.rint(color_srgb[0,0,:3]*255.0).astype(np.uint8)
    assert np.all(out0[...,:3] == expected0)

    # attr3.w=1 and mask=0 forces w=1 -> adjusted t0 branch.
    attr_one = np.array([[0,0,0,1]]*3,dtype=np.float32)
    out1 = mod.bake_cell(attr_one,color_linear,mask_zero,bary)
    adjusted = mod.grass.branch0_rgb(color_linear[0,0,:3],mod.TINT_RGB)
    expected1 = np.rint(mod.linear_to_srgb(adjusted)*255.0).astype(np.uint8)
    assert np.all(out1[...,:3] == expected1)
    assert not np.array_equal(expected1, expected0)


def test_target_identity_and_tint_are_locked():
    assert mod.MATERIAL == '80C9993C'
    assert mod.TABLE == '80C99827'
    assert mod.D1_STATIC == '80C994B2'
    assert mod.TRANSFORMS == '80C99845'
    assert mod.INFO_INDICES == (976,978)
    np.testing.assert_allclose(mod.TINT_RGB,
        [0.5335593819618225,0.431231826543808,0.4029434025287628],rtol=0,atol=0)
