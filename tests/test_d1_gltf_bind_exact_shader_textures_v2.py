from __future__ import annotations

import io
from pathlib import Path

from PIL import Image

from tools.d1_gltf_bind_exact_shader_textures_v2 import load_native_image


def _png(rgb, size=(4, 3)) -> bytes:
    im = Image.new('RGB', size, rgb)
    b = io.BytesIO()
    im.save(b, format='PNG', optimize=False, compress_level=9)
    return b.getvalue()


def test_six_face_cubemap_atlas_is_pixel_reversible(tmp_path: Path):
    colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 255),
    ]
    faces = []
    originals = []
    for i, color in enumerate(colors):
        name = f'cube_face{i}.png'
        raw = _png(color)
        (tmp_path / name).write_bytes(raw)
        faces.append({'face': i, 'png': name})
        originals.append(Image.open(io.BytesIO(raw)).convert('RGBA'))

    atlas_png, meta = load_native_image('DEADBEEF', {'faces': faces}, tmp_path)
    assert meta['representation'] == 'decoded_cubemap_horizontal_face_atlas'
    assert meta['storage_face_order'] == [0, 1, 2, 3, 4, 5]
    assert meta['axis_mapping'] == 'UNASSIGNED_STORAGE_ORDER_ONLY'

    atlas = Image.open(io.BytesIO(atlas_png)).convert('RGBA')
    w, h = originals[0].size
    assert atlas.size == (w * 6, h)
    for i, expected in enumerate(originals):
        recovered = atlas.crop((i * w, 0, (i + 1) * w, h))
        assert recovered.tobytes() == expected.tobytes()


def test_2d_texture_is_embedded_byte_identically(tmp_path: Path):
    raw = _png((11, 22, 33), size=(5, 7))
    (tmp_path / 'flat.png').write_bytes(raw)
    embedded, meta = load_native_image('CAFEBABE', {'png': 'flat.png'}, tmp_path)
    assert embedded == raw
    assert meta['representation'] == 'decoded_2d_png'
