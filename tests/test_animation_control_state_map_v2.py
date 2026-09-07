from __future__ import annotations

import struct

import pytest

from tools.d1_animation_control_state_map_v2 import decode_control


def _payload(packed: int, boundary_word: int = 0) -> bytes:
    b = bytearray(0x300)

    # Animation list: one declared FileHash at 0x210 and an auditable boundary word.
    struct.pack_into('<I', b, 0x08, 1)
    struct.pack_into('<I', b, 0x10, 0x200 - 0x10)
    struct.pack_into('<I', b, 0x200, 1)
    struct.pack_into('<I', b, 0x208, 0x808005A1)
    struct.pack_into('<I', b, 0x210, 0x80AA0001)
    struct.pack_into('<I', b, 0x214, boundary_word)

    # One selector record at 0x110.
    struct.pack_into('<I', b, 0x68, 1)
    struct.pack_into('<I', b, 0x70, 0x100 - 0x70)
    struct.pack_into('<I', b, 0x100, 1)
    struct.pack_into('<I', b, 0x108, 0x80802831)
    struct.pack_into('<I', b, 0x120, 0x12345678)
    struct.pack_into('<f', b, 0x124, 0.5)
    struct.pack_into('<I', b, 0x128, packed)
    return bytes(b)


def test_final_clip_plus_zero_tail_is_preserved_not_promoted():
    out = decode_control(_payload(0x00020000, boundary_word=0))
    state = out['state_table']['records'][0]

    assert out['animation_list']['count'] == 1
    assert out['animation_list']['boundary_word_u32'] == '00000000'
    assert out['state_table']['implicit_null_tail_count'] == 1
    assert state['selection_kind'] == 'range_with_implicit_null_tail'
    assert state['selection_range_valid'] is True
    assert state['implicit_null_count'] == 1
    assert [x['tag_hash'] for x in state['selected_animations']] == ['80AA0001']


def test_same_one_past_shape_without_zero_boundary_fails_closed():
    with pytest.raises(ValueError, match='outside the source-proven null-tail form'):
        decode_control(_payload(0x00020000, boundary_word=0x80AA0002))


def test_more_than_one_past_is_not_generalized():
    with pytest.raises(ValueError, match='outside the source-proven null-tail form'):
        decode_control(_payload(0x00030000, boundary_word=0))


def test_ordinary_range_and_explicit_empty_sentinel_remain_unchanged():
    ordinary = decode_control(_payload(0x00010000, boundary_word=0xDEADBEEF))
    state = ordinary['state_table']['records'][0]
    assert state['selection_kind'] == 'range'
    assert state['implicit_null_count'] == 0
    assert state['selected_animations'][0]['tag_hash'] == '80AA0001'

    empty = decode_control(_payload(0x0000FFFF, boundary_word=0xDEADBEEF))
    state = empty['state_table']['records'][0]
    assert state['selection_kind'] == 'empty_sentinel'
    assert state['selected_animations'] == []
