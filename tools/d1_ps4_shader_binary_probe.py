#!/usr/bin/env python3
"""Decode the native PS4 GCN/OrbShdr binary referenced by a D1 shader header.

Destiny 1 PS4 shader FileEntries (pixel shaders are observed as 32:8) are small
engine headers whose FileEntry.Reference points at the native Orbis GCN binary.
The native binary begins with the standard Gnm marker instruction and carries a
trailing ShaderBinaryInfo structure whose seven-byte signature is ``OrbShdr``.

The layout used here is source-correlated with public Orbis implementations
(Orbital/GPCS4) and every claimed offset/check is emitted so it can be validated
against retail bytes rather than trusted implicitly.

Of particular value, ShaderBinaryInfo locates the InputUsageSlot table. Those
4-byte records identify immediate resources, samplers and constant buffers plus
API slots and user-data registers without requiring full GCN instruction
translation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_entry_extract import EntryReader, decode_known

ORB_MAGIC = b"OrbShdr"
FIRST_TOKEN = 0xBEEB03FF

USAGE_NAMES = {
    0x00: "ImmResource",
    0x01: "ImmSampler",
    0x02: "ImmConstBuffer",
    0x03: "ImmVertexBuffer",
    0x04: "ImmRwResource",
    0x05: "ImmAluFloatConst",
    0x06: "ImmAluBool32Const",
    0x07: "ImmGdsCounterRange",
    0x08: "ImmGdsMemoryRange",
    0x09: "ImmGwsBase",
    0x0A: "ImmLdsEsgsSize",
    0x0B: "SubPtrFetchShader",
    0x0C: "PtrResourceTable",
    0x0D: "PtrInternalResourceTable",
    0x0E: "PtrSamplerTable",
    0x0F: "PtrConstBufferTable",
    0x10: "PtrVertexBufferTable",
    0x11: "PtrSoBufferTable",
    0x12: "PtrRwResourceTable",
    0x13: "PtrInternalGlobalTable",
    0x14: "PtrExtendedUserData",
    0x15: "PtrIndirectResourceTable",
    0x16: "PtrIndirectInternalResourceTable",
    0x17: "PtrIndirectRwResourceTable",
    0x18: "ImmShaderResourceTable",
    0x19: "ImmLdsEsgsSizeNeo",
}

STAGE_NAMES = {
    0: "PixelShader",
    1: "VertexShader",
    2: "ExportShader",
    3: "LocalShader",
    4: "ComputeShader",
    5: "GeometryShader",
    6: "Unknown",
    7: "HullShader",
    8: "DomainShader",
}


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from('<I', b, o)[0]


def find_footer(payload: bytes) -> tuple[int | None, dict]:
    checks = {}
    if len(payload) < 8:
        return None, {'payload_at_least_8': False}
    w0, w1 = struct.unpack_from('<II', payload, 0)
    checks['payload_at_least_8'] = True
    checks['first_token'] = f'{w0:08X}'
    checks['first_token_standard'] = w0 == FIRST_TOKEN
    checks['size_token'] = w1

    # GPCS4/Orbis rule: ShaderBinaryInfo is token + (token[1] + 1) * 2 dwords.
    formula = (w1 + 1) * 8
    checks['formula_footer_offset'] = formula
    checks['formula_footer_in_bounds'] = formula + 28 <= len(payload)
    checks['formula_magic_matches'] = (
        formula + len(ORB_MAGIC) <= len(payload)
        and payload[formula:formula + len(ORB_MAGIC)] == ORB_MAGIC
    )
    all_magic = []
    start = 0
    while True:
        p = payload.find(ORB_MAGIC, start)
        if p < 0:
            break
        all_magic.append(p)
        start = p + 1
    checks['orbshdr_offsets'] = all_magic
    if checks['formula_magic_matches']:
        return formula, checks
    if len(all_magic) == 1 and all_magic[0] + 28 <= len(payload):
        checks['used_unique_magic_fallback'] = True
        return all_magic[0], checks
    return None, checks


def parse_binary_info(payload: bytes, off: int) -> dict:
    if off + 28 > len(payload):
        raise ValueError('ShaderBinaryInfo out of bounds')
    if payload[off:off + 7] != ORB_MAGIC:
        raise ValueError('ShaderBinaryInfo magic mismatch')
    version = payload[off + 7]
    packed = u32(payload, off + 8)
    low8 = packed & 0xff
    length = (packed >> 8) & 0xffffff
    stage = (low8 >> 2) & 0x0f
    source_type = (low8 >> 6) & 0x03
    info = {
        'offset': off,
        'magic': 'OrbShdr',
        'version': version,
        'packed_type_length': f'{packed:08X}',
        'pssl_or_cg': bool(low8 & 0x01),
        'cached': bool(low8 & 0x02),
        'stage_value': stage,
        'stage': STAGE_NAMES.get(stage, f'Unknown{stage}'),
        'source_type': source_type,
        'code_length_bytes': length,
        'chunk_usage_base_offset_dwords': payload[off + 12],
        'num_input_usage_slots': payload[off + 13],
        'is_srt': bool(payload[off + 14] & 0x01),
        'is_srt_used_info_valid': bool(payload[off + 14] & 0x02),
        'is_extended_usage_info': bool(payload[off + 14] & 0x04),
        'reserved3': payload[off + 15],
        'shader_hash0': f'{u32(payload, off + 16):08X}',
        'shader_hash1': f'{u32(payload, off + 20):08X}',
        'crc32': f'{u32(payload, off + 24):08X}',
    }
    return info


def parse_usage(payload: bytes, footer: int, info: dict) -> dict:
    chunk_dw = info['chunk_usage_base_offset_dwords']
    count = info['num_input_usage_slots']
    usage_masks_off = footer - chunk_dw * 4
    slots_off = usage_masks_off - count * 4
    if slots_off < 0 or usage_masks_off < slots_off or footer > len(payload):
        raise ValueError('input usage table offsets out of bounds')
    slots = []
    for i in range(count):
        o = slots_off + i * 4
        usage, api_slot, start_reg, flags = struct.unpack_from('<4B', payload, o)
        slots.append({
            'index': i,
            'offset': o,
            'usage_type': usage,
            'usage_name': USAGE_NAMES.get(usage, f'Unknown_{usage:02X}'),
            'api_slot': api_slot,
            'start_register': start_reg,
            'register_count_bit': flags & 0x01,
            'resource_type_bit': (flags >> 1) & 0x01,
            'resource_descriptor_kind': (
                'T# texture/image' if usage in (0x00, 0x04) and ((flags >> 1) & 1)
                else 'V# buffer' if usage in (0x00, 0x04)
                else None
            ),
            'reserved_bits_2_3': (flags >> 2) & 0x03,
            'chunk_mask': (flags >> 4) & 0x0f,
            'raw_hex': payload[o:o + 4].hex(),
        })
    masks = [f'{u32(payload, usage_masks_off + i * 4):08X}' for i in range(chunk_dw)]
    return {
        'input_usage_slots_offset': slots_off,
        'usage_masks_offset': usage_masks_off,
        'usage_masks_dwords': masks,
        'slots': slots,
    }


def probe_one(r: EntryReader, by: dict[str, dict], tag: str, dump_dir: Path | None) -> dict:
    e = by.get(tag)
    if e is None:
        return {'tag_hash': tag, 'present': False}
    row = {
        'tag_hash': tag,
        'present': True,
        'header_entry_index': e['index'],
        'header_type': e['type'],
        'header_subtype': e['subtype'],
        'header_size': e['file_size'],
        'payload_reference': e['reference'],
        'header_available': r.available(e['index']),
    }
    if not row['header_available']:
        return row
    header = r.entry(e['index'])
    row['header_decode'] = decode_known(e, header, r.h['platform'])
    target = by.get(e['reference'].upper())
    if target is None:
        row['payload_entry'] = None
        return row
    row['payload_entry'] = {
        'tag_hash': target['tag_hash'], 'entry_index': target['index'],
        'type': target['type'], 'subtype': target['subtype'],
        'size': target['file_size'], 'reference': target['reference'],
        'available': r.available(target['index']),
    }
    if not row['payload_entry']['available']:
        return row
    payload = r.entry(target['index'])
    row['payload_sha256'] = hashlib.sha256(payload).hexdigest()
    row['payload_size'] = len(payload)
    row['header_declared_payload_matches_actual'] = (
        row['header_decode'].get('embedded_data_size') == len(payload)
    )
    footer, checks = find_footer(payload)
    row['orbshdr_locator'] = checks
    row['prefix_32'] = payload[:32].hex()
    row['suffix_64'] = payload[-64:].hex()
    if footer is not None:
        info = parse_binary_info(payload, footer)
        row['binary_info'] = info
        row['code_sha256'] = hashlib.sha256(payload[:info['code_length_bytes']]).hexdigest()
        row['code_length_within_payload'] = info['code_length_bytes'] <= len(payload)
        row['code_length_before_footer'] = info['code_length_bytes'] <= footer
        row['bytes_between_code_and_footer'] = footer - info['code_length_bytes']
        try:
            row['usage'] = parse_usage(payload, footer, info)
        except Exception as ex:
            row['usage_error'] = repr(ex)
    if dump_dir:
        dump_dir.mkdir(parents=True, exist_ok=True)
        (dump_dir / f'{tag}_header.bin').write_bytes(header)
        (dump_dir / f'{target["tag_hash"]}_native_shader.bin').write_bytes(payload)
        if footer is not None and 'binary_info' in row:
            n = row['binary_info']['code_length_bytes']
            (dump_dir / f'{tag}_gcn_code.bin').write_bytes(payload[:n])
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('pkg', type=Path)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--tag-hash', action='append', required=True)
    ap.add_argument('--dump-dir', type=Path)
    ap.add_argument('-o', '--output', type=Path)
    args = ap.parse_args()
    r = EntryReader(args.pkg, args.runtime)
    if r.h['platform'] != 'PS4':
        raise SystemExit(f'PS4-only probe; package platform is {r.h["platform"]}')
    by = {e['tag_hash'].upper(): e for e in r.entries}
    rows = [probe_one(r, by, raw.upper().removeprefix('0X'), args.dump_dir) for raw in args.tag_hash]
    rep = {'package': str(r.pkg), 'platform': r.h['platform'], 'shaders': rows}
    text = json.dumps(rep, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + '\n')
        print('wrote', args.output)
    else:
        print(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
