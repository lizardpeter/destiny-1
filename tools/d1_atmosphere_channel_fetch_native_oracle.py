#!/usr/bin/env python3
"""Execute retail channel lookup/fetch against source-pinned default keys.

Runs unmodified 0x816240 and 0x816140 in a zero-extended ELF mapping. Synthetic
tag-storage pointers reproduce only the field loads read by the resolver; this
does not execute archive loading or prove live map channel/settings ownership.
"""
import argparse
import ctypes
import hashlib
import json
import mmap
import platform
import struct
from pathlib import Path

from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from d1_atmosphere_default_channel_join import join
from d1_global_lighting_settings_defaults import EXPECTED_SHA256


def probe(path, defaults_path):
    if platform.machine() not in ('x86_64', 'AMD64') or ' avx ' not in Path('/proc/cpuinfo').read_text():
        raise RuntimeError('requires Linux x86-64 AVX')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256
    defaults = json.loads(defaults_path.read_bytes())
    joined = join(path, defaults_path)  # Pins source identity and key uniqueness.
    channels = defaults['channels']
    assert [row['index'] for row in channels] == list(range(len(channels)))
    dis = Cs(CS_ARCH_X86, CS_MODE_64)
    ranges = {'resolver': (0x816240, 0x8162CE), 'fetch': (0x816140, 0x816161)}
    instructions = {
        name: list(dis.disasm(raw[a + 0x4000:b + 0x4000], a))
        for name, (a, b) in ranges.items()
    }
    assert all(i.mnemonic != 'call' for rows in instructions.values() for i in rows)
    by_va = {i.address: i for rows in instructions.values() for i in rows}
    assert by_va[0x816249].op_str == 'r8d, 0xffffffff'
    assert by_va[0x8162CA].op_str == 'eax, r8d'
    assert by_va[0x816144].op_str == '0x816160'
    assert by_va[0x816148].op_str == '0x816160'
    # Addresses decoded from exact retail RIP-relative instructions.
    tag_global = by_va[0x816240].address + by_va[0x816240].size + 0x1EDBDA9
    package_got = by_va[0x81626E].address + by_va[0x81626E].size + 0x120D62B
    assert tag_global == 0x26F1FF0 and package_got == 0x1A238A0

    kernel = mmap.mmap(-1, 0x2800000 + 0x4000, prot=7)
    kernel.write(raw)
    base = ctypes.addressof(ctypes.c_char.from_buffer(kernel))
    address = lambda va: base + 0x4000 + va
    # Retail decodes 0x80800000 into table slot 0x400 / entry 0. Its
    # signed-shift mask differs from the archive's ordinary package-ID helper.
    package_table = ctypes.create_string_buffer(0x401 * 0x40)
    table_owner = ctypes.create_string_buffer(8)
    entry = ctypes.create_string_buffer(0x18)
    key_array = ctypes.create_string_buffer(0x10 + len(channels) * 4)
    struct.pack_into('<Q', table_owner, 0, ctypes.addressof(package_table))
    struct.pack_into('<Q', package_table, 0x400 * 0x40 + 0x10, ctypes.addressof(entry))
    struct.pack_into('<I', package_table, 0x400 * 0x40 + 0x30, 0x18)
    struct.pack_into('<I', package_table, 0x400 * 0x40 + 0x34, 0)  # Relative-base mask.
    struct.pack_into('<Q', entry, 8, len(channels))
    struct.pack_into('<q', entry, 0x10,
                     ctypes.addressof(key_array) - (ctypes.addressof(entry) + 0x10))
    for row in channels:
        struct.pack_into('<I', key_array, 0x10 + row['index'] * 4, int(row['string_hash'], 16))
    ctypes.c_uint32.from_address(address(tag_global)).value = 0x80800000
    ctypes.c_uint64.from_address(address(package_got)).value = ctypes.addressof(table_owner)
    resolve = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.POINTER(ctypes.c_uint32))(address(0x816240))
    fetch = ctypes.CFUNCTYPE(ctypes.c_uint8, ctypes.c_void_p, ctypes.c_int32, ctypes.c_void_p)(address(0x816140))
    # vmovaps requires exact 16-byte alignment for source and destination.
    vectors_storage = ctypes.create_string_buffer(len(channels) * 16 + 15)
    vectors = (ctypes.addressof(vectors_storage) + 15) & ~15
    for row in channels:
        ctypes.memmove(vectors + row['index'] * 16, struct.pack('<4f', *row['default_vec4']), 16)
    context = ctypes.create_string_buffer(16)
    struct.pack_into('<I', context, 0, len(channels))
    struct.pack_into('<Q', context, 8, vectors)
    output_storage = ctypes.create_string_buffer(31)
    output = (ctypes.addressof(output_storage) + 15) & ~15
    sentinel = bytes.fromhex('123456789abcdef0fedcba9876543210')
    cases = []
    keys = [(row['string_hash'], row['index']) for row in channels]
    keys += [(row['hash_hex'], -1) for row in joined['missing_source_keys']]
    for key, expected_index in keys:
        value = ctypes.c_uint32(int(key, 16))
        index = resolve(ctypes.byref(value))
        assert index == expected_index, (key, index, expected_index)
        ctypes.memmove(output, sentinel, 16)
        admitted = fetch(context, index, output)
        result = ctypes.string_at(output, 16)
        expected = sentinel if index < 0 else ctypes.string_at(vectors + index * 16, 16)
        assert admitted == (index >= 0) and result == expected
        cases.append({'hash': key, 'native_index': index,
                      'native_fetch_success': bool(admitted), 'native_output_hex': result.hex()})
    for index in [-2147483648, -2, len(channels), len(channels) + 1, 2147483647]:
        ctypes.memmove(output, sentinel, 16)
        assert fetch(context, index, output) == 0
        assert ctypes.string_at(output, 16) == sentinel
        cases.append({'native_index': index, 'native_fetch_success': False,
                      'native_output_hex': sentinel.hex()})
    ctypes.c_uint32.from_address(address(tag_global)).value = 0xFFFFFFFF
    assert resolve(ctypes.byref(ctypes.c_uint32(int(channels[0]['string_hash'], 16)))) == -1
    return {
        'schema': 'd1-atmosphere-channel-fetch-native-oracle-v1',
        'eboot_sha256': EXPECTED_SHA256,
        'defaults_tag': joined['defaults_tag'],
        'defaults_payload_sha256': joined['defaults_payload_sha256'],
        'all_native_outputs_match': True, 'cases': cases,
        'missing_atmosphere_keys': joined['missing_source_keys'],
        'source': {name: [{'va': hex(i.address), 'bytes': i.bytes.hex(),
                          'mnemonic': i.mnemonic, 'operands': i.op_str} for i in rows]
                   for name, rows in instructions.items()},
        'contract': 'First matching source key index; absent key or null defaults handle returns -1. Fetch rejects negative/out-of-range indices without writing any destination byte.',
        'scope': 'Exact lookup/fetch routines with synthetic resource storage and source-pinned keys/vectors. Does not establish the prior destination values, live overrides, map settings/LUT joins, or a rendered scene.',
    }


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('eboot', type=Path)
    ap.add_argument('--defaults', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    result = probe(args.eboot, args.defaults)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'cases': len(result['cases']), 'all_native_outputs_match': True}))
