from __future__ import annotations

import sys
import types

import numpy as np

from tools.d1_tiger_animation_safe_offsets import install_safe_tag_array_offsets


def test_numpy_int16_codec_offset_is_promoted_before_span_addition(monkeypatch):
    class FakeTagArrayNP:
        def __init__(self, data):
            self.data = data

        # These deliberately reproduce the pinned third-party implementation.
        def read_vec(self, offset, amount):
            new_offset = offset + amount
            return self.data[offset:new_offset], new_offset

        def read_scalar(self, offset):
            return self.data[offset], offset + 1

    tag_pkg = types.ModuleType('tag')
    tag_array = types.ModuleType('tag.tag_array')
    tag_array.Tag_Array_NP = FakeTagArrayNP
    monkeypatch.setitem(sys.modules, 'tag', tag_pkg)
    monkeypatch.setitem(sys.modules, 'tag.tag_array', tag_array)

    install_safe_tag_array_offsets()

    arr = FakeTagArrayNP(np.arange(33792, dtype=np.int64))
    route_offset = np.int16(32736)
    chunk, end = arr.read_vec(route_offset, 352 * 3)

    assert isinstance(end, int)
    assert end == 33792
    assert len(chunk) == 1056
    assert int(chunk[0]) == 32736
    assert int(chunk[-1]) == 33791

    value, next_offset = arr.read_scalar(np.int16(32767))
    assert int(value) == 32767
    assert isinstance(next_offset, int)
    assert next_offset == 32768
