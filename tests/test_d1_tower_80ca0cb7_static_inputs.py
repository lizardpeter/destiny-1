import importlib.util
import struct
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'tower80ca0cb7', ROOT/'tools'/'d1_tower_80ca0cb7_static_inputs.py'
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules['tower80ca0cb7'] = mod
SPEC.loader.exec_module(mod)


def pack_vertex(
    pos=(1000,-2000,3000), primary_w=32767,
    uv_control=(4096,-8192,0,16384),
    normal=(100,-200,300,0), tangent=(400,-500,600,32767),
):
    v0=struct.pack('<4h',*pos,primary_w)
    v1=struct.pack('<4h',*uv_control)+struct.pack('<4h',*normal)+struct.pack('<4h',*tangent)
    assert len(v0)==8 and len(v1)==24
    return v0,v1


def test_source_word_offsets_map_to_exact_vs_groups():
    v0,v1=pack_vertex()
    d=mod.decode_static_inputs(v0,v1)
    assert d.vertex_count==1
    np.testing.assert_array_equal(d.raw_v4_v6_position,[[1000,-2000,3000]])
    np.testing.assert_array_equal(d.raw_v20_scalar,[32767])
    np.testing.assert_array_equal(d.raw_v8_v11_uv_control,[[4096,-8192,0,16384]])
    np.testing.assert_array_equal(d.raw_v12_v14_normal,[[100,-200,300]])
    np.testing.assert_array_equal(d.raw_stored_normal_w,[0])
    np.testing.assert_array_equal(d.raw_v16_v19_tangent,[[400,-500,600,32767]])
    assert bool(d.branch_a[0]) is True


def test_snorm16_endpoints_and_primary_w_attr0():
    v0,v1=pack_vertex(pos=(-32768,0,32767),primary_w=32767,uv_control=(0,0,0,32767))
    d=mod.decode_static_inputs(v0,v1)
    np.testing.assert_array_equal(d.v4_v6_position,[[-1.0,0.0,1.0]])
    np.testing.assert_array_equal(d.attr0_w,[1.0])
    np.testing.assert_array_equal(d.v8_v11_uv_control[:,2:],[[0.0,1.0]])


def test_attr3_replays_vs_instance_uv_equation():
    v0,v1=pack_vertex(uv_control=(8192,-4096,0,16384))
    d=mod.decode_static_inputs(v0,v1)
    c=np.array([5.469311714172363,1.2997846603393555,1.0627503395080566,1096572.0],dtype=np.float32)
    got=d.attr3(c)[0]
    uv=d.v8_v11_uv_control[0]
    want=np.array([c[1]+c[0]*uv[0],c[2]+c[0]*uv[1],uv[2],uv[3]],dtype=np.float32)
    np.testing.assert_allclose(got,want,rtol=0,atol=1e-7)


def test_second_retail_instance_constants_are_accepted_without_using_s11():
    v0,v1=pack_vertex(uv_control=(1000,2000,0,32767))
    d=mod.decode_static_inputs(v0,v1)
    a=d.attr3([22.309463500976562,13.954891204833984,15.941343307495117,1208840.0])
    b=d.attr3([22.309463500976562,13.954891204833984,15.941343307495117,-999.0])
    np.testing.assert_array_equal(a,b)
    assert float(a[0,3])==1.0


def test_branch_b_is_rejected_fail_closed():
    # Break branch A by making stored normal-W nonzero.
    v0,v1=pack_vertex(normal=(100,-200,300,123))
    assert not bool(mod.branch_a_mask(v1)[0])
    with pytest.raises(ValueError,match='branch-B'):
        mod.decode_static_inputs(v0,v1)


def test_referenced_only_gate_still_rejects_used_branch_b():
    a0,a1=pack_vertex()
    b0,b1=pack_vertex(normal=(1,2,3,7))
    v0=a0+b0
    v1=a1+b1
    # The unreferenced branch-B vertex may remain in the backing only under the
    # explicit relaxed gate.
    d=mod.decode_static_inputs(v0,v1,used_indices=[0],require_all_branch_a=False)
    assert d.vertex_count==2
    with pytest.raises(ValueError,match='referenced branch-B'):
        mod.decode_static_inputs(v0,v1,used_indices=[1],require_all_branch_a=False)


def test_shape_and_index_guards():
    v0,v1=pack_vertex()
    with pytest.raises(ValueError,match='stride-0x08'):
        mod.decode_static_inputs(v0[:-1],v1)
    with pytest.raises(ValueError,match='stride-0x18'):
        mod.decode_static_inputs(v0,v1[:-1])
    with pytest.raises(ValueError,match='vertex-count mismatch'):
        mod.decode_static_inputs(v0+v0,v1)
    with pytest.raises(ValueError,match='escaped'):
        mod.decode_static_inputs(v0,v1,used_indices=[1])
