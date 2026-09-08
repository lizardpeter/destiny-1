import struct

from tools.d1_material_render_state import decode_material_render_state


def payload(state16: int) -> bytes:
    b = bytearray(0x330)
    struct.pack_into('<Q', b, 0, len(b))
    struct.pack_into('<H', b, 0x20, state16)
    struct.pack_into('<I', b, 0x28, 0x80ABCDEF)
    struct.pack_into('<I', b, 0x2A8, 0x80123456)
    return bytes(b)


def test_opaque_zero_state():
    d = decode_material_render_state(payload(0x0000))
    assert d['transparent_draw_population'] is False
    assert d['portable_alpha_class'] == 'OPAQUE'
    assert d['exact_blend_state_known'] is False


def test_known_state8_selector():
    d = decode_material_render_state(payload(0x0088))
    assert d['transparent_draw_population'] is True
    assert d['portable_alpha_class'] == 'BLEND'
    assert d['unk20_low_hex'] == '0x88'
    assert d['exact_blend_state_known'] is True
    assert d['exact_blend_state_index'] == 8
    assert d['exact_blend_equation'] == 'Source + Destination*(1-SourceAlpha)'


def test_unknown_nonzero_state_is_not_overclaimed():
    d = decode_material_render_state(payload(0x0042))
    assert d['transparent_draw_population'] is True
    assert d['portable_alpha_class'] == 'BLEND'
    assert d['exact_blend_state_known'] is False
    assert d['exact_blend_state_index'] is None
    assert d['exact_blend_equation'] is None
