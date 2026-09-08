#!/usr/bin/env python3
"""Canonical D1 material render-state decoder.

This module is deliberately destination-neutral.  It decodes source fields that
both Blender adapters and the Rust renderer need, without assuming glTF/PBR
semantics.

Source-backed semantics currently closed:
- D1 Material class: 80801AD7.
- material +0x20 as a 16-bit render-state field.
- +0x20 != 0 belongs to D1's transparent draw population.
- low byte 0x88 selects native blend-state index 8 with the independently closed
  equation Source + Destination * (1 - SourceAlpha).

Unknown nonzero render states remain transparent-classified but their exact blend
equations are intentionally not guessed.
"""
from __future__ import annotations

import hashlib
import struct
from typing import Any

MATERIAL_CLASS = '80801AD7'
KNOWN_BLEND_SELECTOR = 0x88
KNOWN_BLEND_STATE_INDEX = 8
KNOWN_BLEND_EQUATION = 'Source + Destination*(1-SourceAlpha)'


def norm_hash(x: Any) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def decode_material_render_state(payload: bytes) -> dict:
    if len(payload) < 0x2AC:
        raise ValueError(f'D1 material payload too short for render state: {len(payload)}')

    raw16 = struct.unpack_from('<H', payload, 0x20)[0]
    lo = payload[0x20]
    hi = payload[0x21]
    transparent = raw16 != 0
    known = lo == KNOWN_BLEND_SELECTOR

    return {
        'payload_bytes': len(payload),
        'payload_sha256': hashlib.sha256(payload).hexdigest(),
        'unk08_u32': struct.unpack_from('<I', payload, 0x08)[0],
        'unk0c_u32': struct.unpack_from('<I', payload, 0x0C)[0],
        'unk10_hex': f"{struct.unpack_from('<I', payload, 0x10)[0]:08X}",
        'unk20_raw_u16': raw16,
        'unk20_hex': f'0x{raw16:04X}',
        'unk20_low_u8': lo,
        'unk20_low_hex': f'0x{lo:02X}',
        'unk20_high_u8': hi,
        'transparent_draw_population': transparent,
        'portable_alpha_class': 'BLEND' if transparent else 'OPAQUE',
        'exact_blend_state_known': known,
        'exact_blend_state_index': KNOWN_BLEND_STATE_INDEX if known else None,
        'exact_blend_equation': KNOWN_BLEND_EQUATION if known else None,
        'vertex_shader': f"{struct.unpack_from('<I', payload, 0x28)[0]:08X}",
        'pixel_shader': f"{struct.unpack_from('<I', payload, 0x2A8)[0]:08X}",
        'proof': {
            'unk20_nonzero_transparent_population_source_closed': True,
            'blend_selector_0x88_state8_equation_source_closed': True,
            'other_nonzero_blend_equations_source_closed': False,
        },
    }
