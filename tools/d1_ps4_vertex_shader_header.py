#!/usr/bin/env python3
"""Decode Destiny 1 PS4 type 32/subtype 9 vertex-shader headers.

Retail Spektar shaders close this structure against public Sony/Gnmx layout:

  +0x00..+0x13  D1/Tiger wrapper (preserved; only repeated shader-size is checked)
  +0x14         Gnmx::ShaderCommonData
  +0x1C         Gnm::VsStageRegisters (7 dwords)
  +0x38         numInputSemantics, numExportSemantics, gsMode, fetchControl
  +0x3C         InputUsageSlot[numInputUsageSlots] (4 bytes each)
                 VertexInputSemantic[numInputSemantics] (4 bytes each)
                 VertexExportSemantic[numExportSemantics] (2 bytes each)
                 trailing bytes/padding preserved verbatim

The semantic byte in Gnm::VertexInputSemantic is a native link semantic number,
not a PSSL source-language name.  This decoder therefore reports native semantic
IDs, VGPRs and component counts without inventing POSITION/TEXCOORD/etc names.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entry_extract import EntryReader
from d1_ps4_shader_binary_probe import USAGE_NAMES, find_footer, parse_binary_info

VERTEX_SHADER_TYPE = 32
VERTEX_SHADER_SUBTYPE = 9
GNMX_BASE = 0x14
GNMX_USAGE_BASE = 0x3C


def u32(b: bytes, o: int) -> int:
    if o < 0 or o + 4 > len(b):
        raise ValueError((o, len(b)))
    return struct.unpack_from('<I', b, o)[0]


def parse_input_usage_slot(b: bytes, o: int, index: int) -> dict:
    usage, api_slot, start_reg, flags = struct.unpack_from('<4B', b, o)
    return {
        'index': index,
        'offset': o,
        'usage_type': usage,
        'usage_name': USAGE_NAMES.get(usage, f'Unknown_{usage:02X}'),
        'api_slot': api_slot,
        'start_register': start_reg,
        'register_count_bit': flags & 1,
        'resource_type_bit': (flags >> 1) & 1,
        'chunk_mask': (flags >> 4) & 0x0F,
        'raw_hex': b[o:o+4].hex(),
    }


def parse_vertex_input_semantic(b: bytes, o: int, index: int) -> dict:
    semantic, vgpr, size, flags = struct.unpack_from('<4B', b, o)
    return {
        'index': index,
        'offset': o,
        'semantic': semantic,
        'vgpr': vgpr,
        'size_in_elements': size,
        'byte3': flags,
        'raw_hex': b[o:o+4].hex(),
    }


def parse_vertex_export_semantic(b: bytes, o: int, index: int) -> dict:
    semantic, packed = struct.unpack_from('<2B', b, o)
    return {
        'index': index,
        'offset': o,
        'semantic': semantic,
        'out_index': packed & 0x1F,
        'export_f16_bit': (packed >> 6) & 1,
        'raw_hex': b[o:o+2].hex(),
    }


def parse_header(b: bytes, native_payload: bytes | None = None) -> dict:
    if len(b) < GNMX_USAGE_BASE:
        raise ValueError(f'vertex shader header only {len(b)} bytes')

    wrapper0 = u32(b, 0x00)
    wrapper_shader_size = u32(b, 0x04)
    common0 = u32(b, 0x14)
    shader_size = common0 & 0x7FFFFF
    uses_srt = bool((common0 >> 23) & 1)
    usage_count = (common0 >> 24) & 0xFF
    embedded_cb_dqwords, scratch_dw = struct.unpack_from('<HH', b, 0x18)

    input_count, export_count, gs_mode, fetch_control = struct.unpack_from('<4B', b, 0x38)
    usage_start = GNMX_USAGE_BASE
    input_start = usage_start + usage_count * 4
    export_start = input_start + input_count * 4
    known_end = export_start + export_count * 2
    if known_end > len(b):
        raise ValueError(
            f'header tables exceed payload: usage={usage_count} input={input_count} '
            f'export={export_count} known_end=0x{known_end:X} size=0x{len(b):X}'
        )

    stage_regs = {
        'spi_shader_pgm_lo_vs': f'{u32(b,0x1C):08X}',
        'spi_shader_pgm_hi_vs': f'{u32(b,0x20):08X}',
        'spi_shader_pgm_rsrc1_vs': f'{u32(b,0x24):08X}',
        'spi_shader_pgm_rsrc2_vs': f'{u32(b,0x28):08X}',
        'spi_vs_out_config': f'{u32(b,0x2C):08X}',
        'spi_shader_pos_format': f'{u32(b,0x30):08X}',
        'pa_cl_vs_out_cntl': f'{u32(b,0x34):08X}',
    }

    row = {
        'header_size': len(b),
        'tiger_wrapper': {
            'word0': f'{wrapper0:08X}',
            'word0_low24': wrapper0 & 0xFFFFFF,
            'word0_high8': (wrapper0 >> 24) & 0xFF,
            'shader_size_repeat': wrapper_shader_size,
            'bytes_08_13_hex': b[0x08:0x14].hex(),
        },
        'gnmx': {
            'base_offset': GNMX_BASE,
            'shader_size': shader_size,
            'uses_srt': uses_srt,
            'num_input_usage_slots': usage_count,
            'embedded_constant_buffer_size_dqwords': embedded_cb_dqwords,
            'scratch_size_dwords_per_thread': scratch_dw,
            'stage_registers': stage_regs,
            'num_input_semantics': input_count,
            'num_export_semantics': export_count,
            'gs_mode_or_num_input_semantics_cs': gs_mode,
            'fetch_control': fetch_control,
            'vertex_offset_user_register': fetch_control & 0x0F,
            'instance_offset_user_register': (fetch_control >> 4) & 0x0F,
            'input_usage_slots': [
                parse_input_usage_slot(b, usage_start + i*4, i) for i in range(usage_count)
            ],
            'input_semantics': [
                parse_vertex_input_semantic(b, input_start + i*4, i) for i in range(input_count)
            ],
            'export_semantics': [
                parse_vertex_export_semantic(b, export_start + i*2, i) for i in range(export_count)
            ],
        },
        'table_offsets': {
            'usage_start': usage_start,
            'input_start': input_start,
            'export_start': export_start,
            'known_end': known_end,
        },
        'trailing_bytes_hex': b[known_end:].hex(),
        'checks': {
            'wrapper_shader_size_matches_gnmx_shader_size': wrapper_shader_size == shader_size,
            'input_semantic_ids_unique': len({x['semantic'] for x in [parse_vertex_input_semantic(b,input_start+i*4,i) for i in range(input_count)]}) == input_count,
            'input_semantic_byte3_zero': all(b[input_start+i*4+3] == 0 for i in range(input_count)),
        },
    }

    if native_payload is not None:
        footer, loc = find_footer(native_payload)
        row['native_checks'] = {'orbshdr_locator': loc, 'resolved': footer is not None}
        if footer is not None:
            info = parse_binary_info(native_payload, footer)
            row['native_checks'].update({
                'binary_info': info,
                'stage_is_vertex_shader': info['stage'] == 'VertexShader',
                'gnmx_shader_size_matches_orbshdr_end': shader_size == footer + 28,
                'usage_count_matches_orbshdr': usage_count == info['num_input_usage_slots'],
            })
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('pkg', type=Path)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--tag-hash', action='append', required=True)
    ap.add_argument('-o', '--output', type=Path)
    a = ap.parse_args()
    r = EntryReader(a.pkg, a.runtime)
    by = {e['tag_hash'].upper(): e for e in r.entries}
    rows=[]
    for raw in a.tag_hash:
        tag=raw.upper().removeprefix('0X')
        e=by.get(tag)
        rec={'tag_hash':tag,'present':e is not None}
        if e is not None:
            rec['entry']={k:e[k] for k in ('index','type','subtype','reference','file_size')}
            if (e['type'],e['subtype']) != (VERTEX_SHADER_TYPE,VERTEX_SHADER_SUBTYPE):
                rec['error']='not D1 PS4 32:9 vertex shader header'
            elif r.available(e['index']):
                hb=r.entry(e['index'])
                ne=by.get(e['reference'].upper())
                nb=r.entry(ne['index']) if ne is not None and r.available(ne['index']) else None
                rec['decoded']=parse_header(hb,nb)
        rows.append(rec)
    rep={'schema':'d1_ps4_vertex_shader_header/v1','package':str(a.pkg),'rows':rows}
    text=json.dumps(rep,indent=2)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text+'\n')
    print(text)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
