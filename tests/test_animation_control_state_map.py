from __future__ import annotations

import struct

from tools.d1_animation_control_state_map import decode_control


def _payload(records: list[tuple[int, int]]) -> bytes:
    b = bytearray(0x300)
    # Animation list: one FileHash at 0x210.
    struct.pack_into('<I', b, 0x08, 1)
    struct.pack_into('<I', b, 0x10, 0x200 - 0x10)
    struct.pack_into('<I', b, 0x200, 1)
    struct.pack_into('<I', b, 0x208, 0x808005A1)
    struct.pack_into('<I', b, 0x210, 0x80AA0001)

    # State table records begin at 0x110.
    struct.pack_into('<I', b, 0x68, len(records))
    struct.pack_into('<I', b, 0x70, 0x100 - 0x70)
    struct.pack_into('<I', b, 0x100, len(records))
    struct.pack_into('<I', b, 0x108, 0x80802831)
    for i, (state_hash, packed) in enumerate(records):
        o = 0x110 + 0x20 * i
        struct.pack_into('<I', b, o + 0x10, state_hash)
        struct.pack_into('<f', b, o + 0x14, 0.0)
        struct.pack_into('<I', b, o + 0x18, packed)
    return bytes(b)


def test_zero_count_ffff_start_is_retail_empty_sentinel():
    out = decode_control(_payload([
        (0x6686E16A, 0x0000FFFF),
        (0x6FB760FF, 0x00010000),
    ]))

    assert out['state_table']['empty_sentinel_count'] == 1
    empty, selected = out['state_table']['records']
    assert empty['selection_kind'] == 'empty_sentinel'
    assert empty['selection_range_valid'] is True
    assert empty['selected_animations'] == []
    assert selected['selection_kind'] == 'range'
    assert selected['selected_animations'][0]['tag_hash'] == '80AA0001'


def test_non_sentinel_out_of_range_selector_still_fails_closed():
    try:
        decode_control(_payload([(0x12345678, 0x00010005)]))
    except ValueError as ex:
        assert 'selector ranges exceed animation list' in str(ex)
    else:
        raise AssertionError('ordinary out-of-range selector must not be accepted')
