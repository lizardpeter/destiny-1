#!/usr/bin/env python3
"""Corrected runner for d1_remote_tower_placement_permutation_calibration.

Tiger DynamicArray allocation metadata in these D1 payloads serializes the element
class at element_start-0x08 and a zero lane at element_start-0x04.  The v1 probe
incorrectly tested element_start-0x04 as the class slot.  Keep every other proof
boundary unchanged and patch only that validation point.
"""
from __future__ import annotations

import d1_remote_tower_placement_permutation_calibration as base


def decode_s152(b: bytes, base_offset: int) -> dict:
    a = base.dyn(b, base_offset + 0x10, 8)
    if a['count']:
        start = a['element_start']
        if start < 8:
            raise ValueError(f'S152 element allocation prefix OOB at 0x{base_offset:X}')
        marker = base.u32(b, start - 8)
        zero_lane = base.u32(b, start - 4)
        if marker != base.S4E2A or zero_lane != 0:
            raise ValueError(
                f'S152 S4E2A allocation prefix mismatch at 0x{base_offset:X}: '
                f'marker={marker:08X} zero_lane={zero_lane:08X}'
            )
    rows = []
    for i in range(a['count']):
        o = a['element_start'] + i * 8
        rows.append({
            'index': i,
            'offset': o,
            'pair': [f'{base.u32(b,o):08X}', f'{base.u32(b,o+4):08X}'],
            'unk00_tiger_hash': f'{base.u32(b,o):08X}',
            'type_string_hash': f'{base.u32(b,o+4):08X}',
        })
    return {
        'base_offset': base_offset,
        'array': a,
        'allocation_prefix': {
            'class_offset': a['element_start'] - 8 if a['count'] else None,
            'class_hash': f'{base.u32(b,a["element_start"]-8):08X}' if a['count'] else None,
            'zero_lane_offset': a['element_start'] - 4 if a['count'] else None,
            'zero_lane': base.u32(b,a['element_start']-4) if a['count'] else None,
        },
        'records': rows,
    }


base.decode_s152 = decode_s152

if __name__ == '__main__':
    raise SystemExit(base.main())
