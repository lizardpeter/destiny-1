import importlib.util
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'grass80c9994a', ROOT/'tools'/'d1_tower_grass_shader_80c9994a.py'
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules['grass80c9994a'] = mod
SPEC.loader.exec_module(mod)


def test_exact_material_identity_and_slots():
    assert mod.MATERIAL == '80C9993C'
    assert mod.VERTEX_SHADER == '80CA0CB7'
    assert mod.PIXEL_SHADER == '80C9994A'
    assert mod.TEXTURE_SLOTS == {
        0:'80C9988C', 1:'80C9988D', 2:'80C9988C', 3:'80C9988D', 4:'80C9988E'
    }


def test_blend_weight_matches_native_mad_and_clamp():
    # Exact PS equation: saturate(3*attr3.w - 2*t4.r).
    control=np.array([0.0, 0.25, 0.5, 0.75, 1.0],dtype=np.float32)
    mask=np.array([0.0, 0.5, 0.25, 1.0, 0.0],dtype=np.float32)
    got=mod.blend_weight(control,mask)
    want=np.clip(3.0*control-2.0*mask,0.0,1.0)
    np.testing.assert_allclose(got,want,rtol=0,atol=1e-7)
    np.testing.assert_array_equal(got,np.array([0.0,0.0,1.0,0.25,1.0],dtype=np.float32))


def test_ps_uv_scales_are_exact_material_constants():
    uv=np.array([0.2,-0.1],dtype=np.float32)
    a,b,m=mod.ps_uvs(uv)
    np.testing.assert_allclose(a,3.662899971008301*uv+[0.25029999017715454,0.0],rtol=0,atol=1e-7)
    np.testing.assert_allclose(b,4.5*uv,rtol=0,atol=1e-7)
    np.testing.assert_array_equal(b,m)


def test_base_rgb_selects_t2_at_zero_weight_and_adjusted_t0_at_one():
    t0=np.array([0.10,0.30,0.90],dtype=np.float32)
    t2=np.array([0.80,0.70,0.60],dtype=np.float32)
    tint=np.array([0.53355938,0.43123183,0.40294340],dtype=np.float32)
    adjusted=mod.branch0_rgb(t0,tint)

    zero=mod.base_rgb(t0,t2,mask_r=1.0,attr3_w=0.0,tint_rgb=tint)
    one=mod.base_rgb(t0,t2,mask_r=0.0,attr3_w=1.0,tint_rgb=tint)
    np.testing.assert_allclose(zero,t2,rtol=0,atol=1e-7)
    np.testing.assert_allclose(one,adjusted,rtol=0,atol=1e-7)


def test_bc3_alpha_is_auxiliary_not_mrt0_opacity():
    # The reference function exposes the shader's internal alpha blend only;
    # MRT0 alpha is attr0.w and therefore deliberately has no opacity helper.
    got=mod.auxiliary_alpha(t0_a=0.75,t2_a=0.2,mask_r=0.0,attr3_w=1.0)
    assert np.isclose(float(got),0.5)
    assert not hasattr(mod,'opacity_from_bc3_alpha')


def test_normal_branch_and_z_reconstruction():
    t1=np.array([0.75,0.50],dtype=np.float32) # decoded [0.5,0]
    t3=np.array([0.50,0.75],dtype=np.float32) # decoded [0,0.5]
    n0=mod.normal_xy(t1,t3,mask_r=1.0,attr3_w=0.0)
    n1=mod.normal_xy(t1,t3,mask_r=0.0,attr3_w=1.0)
    np.testing.assert_allclose(n0,[0.0,0.5],rtol=0,atol=1e-7)
    np.testing.assert_allclose(n1,[0.5,0.0],rtol=0,atol=1e-7)
    assert np.isclose(float(mod.reconstruct_normal_z(np.array([0.6,0.8],dtype=np.float32))),0.0,atol=1e-7)
