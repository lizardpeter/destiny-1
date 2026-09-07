#!/usr/bin/env python3
"""Corrected runner for the source-decoded Xur placement configuration probe.

The D1 DynamicArray allocation prefix stores S4E2A8080 at element_start-0x08 and
a zero lane at element_start-0x04.  This patches only that allocation-prefix
validation; the v3 proof policy and E6/E7/E8 fail-closed gates are unchanged.
"""
from __future__ import annotations

import d1_remote_xur_scripted_owner_switch_probe as base


def decode_xur_placement(b: bytes, xoff: int) -> dict:
    if xoff + 0x90 > len(b):
        raise ValueError(f'SMapDataEntry exceeds payload at Xur offset 0x{xoff:X}')
    data_ptr = base.resource_pointer(b, xoff + 0x88)
    if data_ptr.get('class_hash') != f'{base.S152_CLASS:08X}':
        raise ValueError(f'Xur DataResource is not S152B8080 at 0x{xoff:X}: {data_ptr}')
    s152 = data_ptr['target_offset']
    arr = base.dynamic_array(b, s152 + 0x10, 8)
    marker = zero_lane = None
    if arr['count']:
        start = arr['element_start']
        if start < 8:
            raise ValueError(f'S152 element allocation prefix OOB at 0x{xoff:X}')
        marker = base.u32(b, start - 8)
        zero_lane = base.u32(b, start - 4)
        if marker != base.S4E2A_CLASS or zero_lane != 0:
            raise ValueError(
                f'S152 allocation prefix mismatch at 0x{xoff:X}: '
                f'marker={marker:08X} zero_lane={zero_lane:08X}'
            )
    records = []
    for i in range(arr['count']):
        o = arr['element_start'] + i * 8
        records.append({
            'index': i,
            'offset': o,
            'offset_hex': f'0x{o:X}',
            'unk00_tiger_hash': f'{base.u32(b,o):08X}',
            'type_string_hash': f'{base.u32(b,o+4):08X}',
        })
    pairs = [(r['unk00_tiger_hash'], r['type_string_hash']) for r in records]
    return {
        'xur_offset': xoff,
        'xur_offset_hex': f'0x{xoff:X}',
        'smap_class_expected': f'{base.SMAP_CLASS:08X}',
        'data_resource_pointer': data_ptr,
        's152_payload_offset': s152,
        's152_payload_offset_hex': f'0x{s152:X}',
        's152_array': arr,
        's4e2a_allocation_prefix': {
            'class_offset': arr['element_start'] - 8 if arr['count'] else None,
            'class_hash': f'{marker:08X}' if marker is not None else None,
            'zero_lane_offset': arr['element_start'] - 4 if arr['count'] else None,
            'zero_lane': zero_lane,
        },
        's4e2a_records': records,
        'exact_expected_xur_config': pairs == base.EXPECTED_XUR_CONFIG,
    }


base.decode_xur_placement = decode_xur_placement

if __name__ == '__main__':
    raise SystemExit(base.main())
