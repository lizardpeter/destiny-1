#!/usr/bin/env python3
"""Install the source-proven D1 codec array-offset arithmetic adapter.

The pinned Tiger animation parser stores codec-1 ``array_7`` entries in NumPy
integer scalars. ``Tag_Array_NP.read_vec`` currently adds the requested span to that
NumPy scalar before slicing. Retail Wrath clips prove valid uncompressed translation
routes whose final span crosses 32767 and ends exactly at the serialized buffer end;
NumPy int16 addition therefore wraps before the slice and yields an empty chunk.

This adapter changes only host-language offset arithmetic: offsets and amounts are
converted to Python ``int`` before addition/indexing. It does not alter codec data,
route signs, frame counts, interpolation, quantization or track math.
"""
from __future__ import annotations


def install_safe_tag_array_offsets() -> None:
    from tag.tag_array import Tag_Array_NP

    if getattr(Tag_Array_NP, "_d1_safe_offsets_installed", False):
        return

    original_read_vec = Tag_Array_NP.read_vec
    original_read_scalar = Tag_Array_NP.read_scalar

    def read_vec(self, offset, amount):
        offset_i = int(offset)
        amount_i = int(amount)
        new_offset = offset_i + amount_i
        return self.data[offset_i:new_offset], new_offset

    def read_scalar(self, offset):
        offset_i = int(offset)
        return self.data[offset_i], offset_i + 1

    Tag_Array_NP._d1_original_read_vec = original_read_vec
    Tag_Array_NP._d1_original_read_scalar = original_read_scalar
    Tag_Array_NP.read_vec = read_vec
    Tag_Array_NP.read_scalar = read_scalar
    Tag_Array_NP._d1_safe_offsets_installed = True


def main() -> int:
    install_safe_tag_array_offsets()
    from tag.tag_array import Tag_Array_NP

    assert getattr(Tag_Array_NP, "_d1_safe_offsets_installed", False)
    print("D1_TIGER_SAFE_ARRAY_OFFSETS_INSTALLED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
