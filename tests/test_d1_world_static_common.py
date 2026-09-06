import importlib.util
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'tools'
sys.path.insert(0, str(TOOLS))
SPEC = importlib.util.spec_from_file_location(
    'world_static_common', TOOLS / 'd1_world_static_common.py'
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules['world_static_common'] = mod
SPEC.loader.exec_module(mod)


def test_static_record_is_3x4_affine_plus_shader_tail():
    raw = np.array([
        [2.0, 0.0, 0.0, 10.0],
        [0.0, 3.0, 0.0, 20.0],
        [0.0, 0.0, 4.0, 30.0],
        [5.5, 6.5, 7.5, 123456.0],
    ], dtype='<f4')
    rec = mod.parse_static_instance_records(raw.tobytes(), 1)[0]
    np.testing.assert_allclose(rec.affine, [
        [2.0, 0.0, 0.0, 10.0],
        [0.0, 3.0, 0.0, 20.0],
        [0.0, 0.0, 4.0, 30.0],
        [0.0, 0.0, 0.0, 1.0],
    ], rtol=0, atol=0)
    assert rec.uv_transform == (5.5, 6.5, 7.5)
    assert rec.tail_3c == 123456.0


def test_affine_records_never_emit_projective_fourth_row():
    rows = np.zeros((2, 4, 4), dtype='<f4')
    rows[0, :3, :4] = np.eye(3, 4, dtype=np.float32)
    rows[1, :3, :4] = np.array([
        [1, 0, 0, 4], [0, 1, 0, 5], [0, 0, 1, 6]
    ], dtype=np.float32)
    rows[0, 3] = [1, 2, 3, 100]
    rows[1, 3] = [9, 8, 7, 200]
    mats = mod.affine_matrix_records(rows.tobytes(), 2)
    for m in mats:
        np.testing.assert_array_equal(m[3], [0.0, 0.0, 0.0, 1.0])


def test_d1_z_up_to_gltf_y_up_basis_is_rigid():
    r = mod.D1_TO_GLTF_Y_UP[:3, :3]
    np.testing.assert_allclose(r @ r.T, np.eye(3), rtol=0, atol=0)
    assert np.isclose(np.linalg.det(r), 1.0)
    # D1 +Z becomes glTF +Y; D1 +Y becomes glTF -Z.
    np.testing.assert_array_equal(r @ np.array([0.0, 0.0, 1.0]), [0.0, 1.0, 0.0])
    np.testing.assert_array_equal(r @ np.array([0.0, 1.0, 0.0]), [0.0, 0.0, -1.0])
