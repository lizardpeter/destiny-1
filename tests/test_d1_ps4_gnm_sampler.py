import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'd1_ps4_gnm_sampler', ROOT/'tools'/'d1_ps4_gnm_sampler.py'
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules['d1_ps4_gnm_sampler'] = mod
SPEC.loader.exec_module(mod)
decode_sampler_bytes = mod.decode_sampler_bytes


def pack(raw0: int, raw1: int) -> bytes:
    return raw0.to_bytes(8, 'little') + raw1.to_bytes(8, 'little')


def test_wrap_bilinear_linear_mip():
    raw0 = 0
    raw1 = (1 << 20) | (1 << 22) | (2 << 26)
    d = decode_sampler_bytes(pack(raw0, raw1))
    assert (d['clamp_x'], d['clamp_y'], d['clamp_z']) == ('wrap', 'wrap', 'wrap')
    assert d['xy_mag_filter'] == 'bilinear'
    assert d['xy_min_filter'] == 'bilinear'
    assert d['mip_filter'] == 'linear'


def test_independent_clamps_and_signed_lod_bias():
    raw0 = (2 << 0) | (1 << 3) | (6 << 6) | (3 << 9) | (7 << 12) | (1 << 15)
    # -1.0 in signed 14-bit 8.8 fixed point is -256 => 0x3f00.
    raw1 = 0x3F00 | (3 << 20) | (2 << 22) | (1 << 26) | (2 << 62)
    d = decode_sampler_bytes(pack(raw0, raw1))
    assert d['clamp_x'] == 'clamp_last_texel'
    assert d['clamp_y'] == 'mirror'
    assert d['clamp_z'] == 'clamp_border'
    assert d['max_aniso'] == 8
    assert d['depth_compare'] == 'always'
    assert d['force_unnormalized'] is True
    assert d['lod_bias'] == -1.0
    assert d['xy_mag_filter'] == 'aniso_linear'
    assert d['xy_min_filter'] == 'aniso_point'
    assert d['mip_filter'] == 'point'
    assert d['border_color_type'] == 'white'


def test_retail_80aae177_descriptor_fixture():
    # Exact 16-byte descriptor payload at +0x08 in the validated D1 sampler tag.
    # Source words: 00000000 00F00000 0A503F80 00000000.
    raw = bytes.fromhex('000000000000f000803f500a00000000')
    d = decode_sampler_bytes(raw)
    assert (d['clamp_x'],d['clamp_y'],d['clamp_z']) == ('wrap','wrap','wrap')
    assert d['xy_mag_filter'] == 'bilinear'
    assert d['xy_min_filter'] == 'bilinear'
    assert d['mip_filter'] == 'linear'
    assert d['min_lod'] == 0.0
    assert d['max_lod'] == 15.0
    assert d['lod_bias'] == -0.5


def test_reject_wrong_descriptor_size():
    try:
        decode_sampler_bytes(b'\x00' * 15)
    except ValueError:
        pass
    else:
        raise AssertionError('expected size rejection')
