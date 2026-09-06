import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'tools'
sys.path.insert(0, str(TOOLS))
SPEC = importlib.util.spec_from_file_location(
    'vs80ca0cb7', TOOLS / 'd1_tower_80ca0cb7_vs_replay.py'
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules['vs80ca0cb7'] = mod
SPEC.loader.exec_module(mod)


def inputs(normals, tangents, alpha=1.0):
    n = np.asarray(normals, dtype=np.float32).reshape(-1, 3)
    t = np.asarray(tangents, dtype=np.float32).reshape(-1, 4)
    assert len(n) == len(t)
    return SimpleNamespace(
        v12_v14_normal=n,
        v16_v19_tangent=t,
        v20_scalar=np.full(len(n), np.float32(alpha), dtype=np.float32),
    )


def test_instance_position_uses_only_first_three_rows():
    # The fourth 0x40-record row is per-instance shader/UV data, not spatial.
    record = np.array([
        [2.0, 0.0, 0.0, 10.0],
        [0.0, 3.0, 0.0, 20.0],
        [0.0, 0.0, 4.0, 30.0],
        [5.5, 6.5, 7.5, 123456.0],
    ], dtype=np.float32)
    p = np.array([[1.0, 2.0, 3.0], [-1.0, 0.5, 0.25]], dtype=np.float32)
    got = mod.instance_positions(p, record)
    want = np.array([[12.0, 26.0, 42.0], [8.0, 21.5, 31.0]], dtype=np.float32)
    np.testing.assert_allclose(got, want, rtol=0, atol=1e-6)

    changed_tail = record.copy()
    changed_tail[3] = [-999.0, 888.0, -777.0, 0.0]
    np.testing.assert_array_equal(mod.instance_positions(p, changed_tail), got)


def test_identity_basis_and_handedness():
    record = np.eye(4, dtype=np.float32)
    i = inputs([[0, 0, 1], [0, 0, 1]], [[1, 0, 0, 1], [1, 0, 0, -1]])
    got = mod.instance_basis(i, record)
    np.testing.assert_allclose(got.attr0_normal, [[0, 0, 1], [0, 0, 1]], rtol=0, atol=1e-7)
    np.testing.assert_allclose(got.attr1_tangent, [[1, 0, 0], [1, 0, 0]], rtol=0, atol=1e-7)
    np.testing.assert_allclose(got.attr2_bitangent, [[0, 1, 0], [0, -1, 0]], rtol=0, atol=1e-7)
    np.testing.assert_array_equal(got.tangent_w, [1.0, -1.0])
    np.testing.assert_array_equal(got.attr0_w, [1.0, 1.0])


def test_tangent_reuses_normal_reciprocal_length_exactly():
    # Native VS does not independently normalize the transformed tangent.
    record = np.array([
        [2.0, 0.0, 0.0, 0.0],
        [0.0, 3.0, 0.0, 0.0],
        [0.0, 0.0, 4.0, 0.0],
        [111.0, 222.0, 333.0, 444.0],
    ], dtype=np.float32)
    i = inputs([[0, 0, 1]], [[1, 0, 0, 1]])
    got = mod.instance_basis(i, record)
    np.testing.assert_allclose(got.normal_length, [4.0], rtol=0, atol=1e-7)
    np.testing.assert_allclose(got.attr0_normal, [[0, 0, 1]], rtol=0, atol=1e-7)
    np.testing.assert_allclose(got.attr1_tangent, [[0.5, 0, 0]], rtol=0, atol=1e-7)
    np.testing.assert_allclose(got.attr2_bitangent, [[0, 0.5, 0]], rtol=0, atol=1e-7)


def test_zero_transformed_normal_fails_closed():
    record = np.eye(4, dtype=np.float32)
    i = inputs([[0, 0, 0]], [[1, 0, 0, 1]])
    with pytest.raises(ValueError, match='normal length'):
        mod.instance_basis(i, record)
