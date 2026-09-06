import importlib.util
import json
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'tools'
sys.path.insert(0, str(TOOLS))
SPEC = importlib.util.spec_from_file_location(
    'grass_color_normal', TOOLS / 'd1_tower_80c9993c_color_normal_bake.py'
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules['grass_color_normal'] = mod
SPEC.loader.exec_module(mod)


def test_native_normal_cell_identity_basis_and_constant_bc5():
    bary, _ = mod.rgb_bake.atlas_cell_barycentrics(16, 2)
    # Constant BC5 RG=[0.75,0.5] decodes to x=+0.5,y=0,z=sqrt(0.75).
    normal = np.empty((2, 2, 4), dtype=np.float32)
    normal[...] = [0.75, 0.5, 0.0, 1.0]
    mask = np.zeros((2, 2, 4), dtype=np.float32)
    # attr3.w=1, mask=0 => blend weight=1, so t1 branch is selected.
    attr3 = np.array([[0, 0, 0, 1]] * 3, dtype=np.float32)
    attr0 = np.array([[0, 0, 1]] * 3, dtype=np.float32)
    attr1 = np.array([[1, 0, 0]] * 3, dtype=np.float32)
    attr2 = np.array([[0, 1, 0]] * 3, dtype=np.float32)
    nts, world = mod.native_normal_cell(attr3, attr0, attr1, attr2, normal, mask, bary)
    want = np.array([0.5, 0.0, np.sqrt(0.75)], dtype=np.float32)
    np.testing.assert_allclose(nts, np.broadcast_to(want, nts.shape), rtol=0, atol=2e-6)
    np.testing.assert_allclose(world, np.broadcast_to(want, world.shape), rtol=0, atol=2e-6)
    np.testing.assert_allclose(np.linalg.norm(world, axis=-1), 1.0, rtol=0, atol=2e-6)


def test_triangle_frame_and_normal_encoding_roundtrip():
    # Deliberately left-handed bitangent hint so tangent.w must be -1.
    a0 = np.array([[0, 0, 1]] * 3, dtype=np.float32)
    a1 = np.array([[1, 0, 0]] * 3, dtype=np.float32)
    a2 = np.array([[0, -1, 0]] * 3, dtype=np.float32)
    n, t, b, w = mod.triangle_reference_frame(a0, a1, a2)
    np.testing.assert_allclose(n, [0, 0, 1], rtol=0, atol=1e-7)
    np.testing.assert_allclose(t, [1, 0, 0], rtol=0, atol=1e-7)
    np.testing.assert_allclose(b, [0, -1, 0], rtol=0, atol=1e-7)
    assert w == -1.0

    world = mod.unit(np.array([[[0.3, -0.4, 0.8660254]]], dtype=np.float32))
    enc = mod.encode_normal_in_frame(world, n, t, b)
    decoded = enc[0, 0, :3].astype(np.float32) / 255.0 * 2.0 - 1.0
    decoded = mod.unit(decoded)
    rebuilt = decoded[0] * t + decoded[1] * b + decoded[2] * n
    np.testing.assert_allclose(rebuilt, world[0, 0], rtol=0, atol=0.012)


def test_y_up_rotation_maps_d1_axes():
    v = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
    got = mod.rotate_rows_y_up(v)
    np.testing.assert_array_equal(got, [[1, 0, 0], [0, 0, -1], [0, 1, 0]])


def test_glb_tangent_semantic_patch(tmp_path):
    verts = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
    faces = np.array([[0, 1, 2]], dtype=np.int64)
    normals = np.array([[0, 0, 1]] * 3, dtype=np.float32)
    tangents = np.array([[1, 0, 0, 1]] * 3, dtype=np.float32)
    uv = np.array([[0, 0], [1, 0], [0, 1]], dtype=np.float32)
    image = Image.new('RGBA', (2, 2), (128, 128, 255, 255))
    material = trimesh.visual.material.PBRMaterial(
        name='test', baseColorTexture=image, normalTexture=image,
        metallicFactor=0.0, roughnessFactor=1.0
    )
    mesh = trimesh.Trimesh(
        vertices=verts, faces=faces, vertex_normals=normals,
        vertex_attributes={'TANGENT': tangents}, process=False
    )
    mesh.visual = trimesh.visual.TextureVisuals(uv=uv, material=material)
    scene = trimesh.Scene(mesh)
    path = tmp_path / 'test.glb'
    scene.export(path)

    before = mod.glb_json(path)
    attrs_before = before['meshes'][0]['primitives'][0]['attributes']
    assert '_TANGENT' in attrs_before and 'TANGENT' not in attrs_before
    changed = mod.patch_glb_standard_tangent(path)
    assert changed == 1
    after = mod.glb_json(path)
    attrs_after = after['meshes'][0]['primitives'][0]['attributes']
    assert 'TANGENT' in attrs_after and '_TANGENT' not in attrs_after
    assert 'NORMAL' in attrs_after and 'TEXCOORD_0' in attrs_after
    assert 'normalTexture' in after['materials'][0]


def test_native_debug_encoding_identity_values():
    nts = np.array([[[ -1.0, 0.0, 1.0 ]]], dtype=np.float32)
    out = mod.encode_native_tangent_debug(nts)
    # 0.5 maps to the ordinary 8-bit midpoint with round-to-nearest.
    np.testing.assert_array_equal(out[0, 0], [0, 128, 255, 255])
