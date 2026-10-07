#!/usr/bin/env python3
"""Run D1 01.33 Gradient4/8 kernels with the source-initialized BSS tolerance.

Map PT_LOAD segments at their virtual offsets, zero BSS, and supply only the
16-byte tolerance whose initializer is proven here. Do not map arbitrary ELF
file bytes into BSS. Both handlers are call-free; only the final dispatch jump
is changed to RET. This tests arithmetic, not live channel ownership or renders.
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
from elftools.elf.elffile import ELFFile
from d1_global_lighting_settings_defaults import EXPECTED_SHA256


def probe(path):
    if platform.machine() != "x86_64" or " avx " not in Path("/proc/cpuinfo").read_text():
        raise RuntimeError("requires x86-64 AVX")
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256
    with path.open("rb") as f:
        segments = [dict(s.header) for s in ELFFile(f).iter_segments() if s['p_type'] == 'PT_LOAD']
    image = mmap.mmap(-1, max(s['p_vaddr'] + s['p_memsz'] for s in segments),
                      prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC)
    for s in segments:
        image[s['p_vaddr']:s['p_vaddr'] + s['p_filesz']] = raw[s['p_offset']:s['p_offset'] + s['p_filesz']]
    # 94813 LEA rcx,BSS; 9486e load xmm1,RODATA; 948d7 store [rcx],xmm1.
    assert image[0x94813:0x9481a] == bytes.fromhex('488d0d061ba301')
    assert image[0x9486e:0x94876] == bytes.fromhex('c5f8280d6ac35701')
    assert image[0x948d7:0x948db] == bytes.fromhex('c5f82909')
    tolerance = bytes(image[0x1610be0:0x1610bf0])
    assert struct.unpack('<4I', tolerance) == (0x38d1b717,) * 4
    assert bytes(image[0x1ac6320:0x1ac6330]) == bytes(16)
    image[0x1ac6320:0x1ac6330] = tolerance
    assert image[0x82acf7:0x82acfc] == bytes.fromhex('e92c050000')
    image[0x82acf7:0x82acfc] = b'\xc3\x90\x90\x90\x90'
    base = ctypes.addressof(ctypes.c_char.from_buffer(image))
    cs = Cs(CS_ARCH_X86, CS_MODE_64)
    handlers = {0x3a: 0x82a9ef, 0x3b: 0x82ab1c}
    for start in handlers.values():
        assert not any(i.mnemonic == 'call' for i in cs.disasm(bytes(image[start:0x82acfc]), start))
    output = ctypes.create_string_buffer(32)
    outptr = (ctypes.addressof(output) + 15) & ~15
    cases = []
    for opcode, start in handlers.items():
        # SysV args input, constants, output, PC. Preserve r12/r13/r14.
        wrapper = bytes.fromhex('4154415541564989f44989cd4989d6c578101748b8')
        wrapper += struct.pack('<Q', base + start) + bytes.fromhex('ffd0415e415d415cc3')
        thunk = mmap.mmap(-1, len(wrapper), prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC)
        thunk.write(wrapper)
        call = ctypes.CFUNCTYPE(None, *([ctypes.c_void_p] * 4))(ctypes.addressof(ctypes.c_char.from_buffer(thunk)))
        eps = struct.unpack('<f', tolerance[:4])[0]
        next_eps = struct.unpack('<f', struct.pack('<I', 0x38d1b718))[0]
        matrices = [
            ('regular', [0.0, .25, .5, .75], [0.0, .25, .5, .75]),
            ('narrow', [0.0, .00005, .25, .75], [0.0, .00005, .25, .75]),
            ('equal_epsilon', [0.0, eps, .25, .75], [0.0, eps, .25, .75]),
            ('above_epsilon', [0.0, next_eps, .25, .75], [0.0, next_eps, .25, .75]),
            ('duplicate', [0.0, 0.0, .25, .75], [0.0, 0.0, .25, .75]),
            ('descending', [.75, .5, .25, 0.0], [.75, .5, .25, 0.0]),
        ]
        for name, t1, t2 in matrices:
            k = [[0.0] * 4 for _ in range(6 if opcode == 0x3a else 11)]
            for lane in range(4):
                k[1 + lane][lane] = 1.0
                if opcode == 0x3b:
                    k[5 + lane][lane] = 2.0
            k[5 if opcode == 0x3a else 9] = t1
            if opcode == 0x3b:
                k[10] = t2
            inputs = [[-.1] * 4, [0.0] * 4, [.000025] * 4,
                      [eps / 2] * 4, [.375] * 4, [1.0] * 4,
                      [.9, -.1, .3, .8]]
            for x in inputs:
                source = ctypes.create_string_buffer(struct.pack('<4f', *x))
                constants = ctypes.create_string_buffer(struct.pack('<' + 'f' * (4 * len(k)), *(v for row in k for v in row)))
                pc = ctypes.create_string_buffer(bytes([opcode, 0]))
                call(ctypes.addressof(source), ctypes.addressof(constants), outptr, ctypes.addressof(pc))
                cases.append({'name': name, 'opcode': opcode, 'input': x, 'constants': k,
                              'output_bits': [f'0x{v:08x}' for v in struct.unpack('<4I', ctypes.string_at(outptr, 16))]})
        # Cancellation witnesses distinguish pairwise, sequential, FMA, and
        # Gradient8 per-lane bank combination before horizontal reduction.
        k = [[0.0] * 4 for _ in range(6 if opcode == 0x3a else 11)]
        k[1] = [1e8, 1.0, -1e8, 1.0]
        k[2] = [16777216.0, 1.0, -16777216.0, 3.0]
        k[3] = [.1, .2, .3, .4]
        k[4] = [-0.0] * 4
        k[5 if opcode == 0x3a else 9] = [0.0, .25, .5, .75]
        if opcode == 0x3b:
            k[5] = [-1e8, 1.0, 1e8, 1.0]
            k[6] = [-16777216.0, 1.0, 16777216.0, 3.0]
            k[10] = [0.0, .25, .5, .75]
        for x in [[1.0]*4, [.375]*4, [.9, .4, .7, .8]]:
            source = ctypes.create_string_buffer(struct.pack('<4f', *x))
            constants = ctypes.create_string_buffer(struct.pack('<' + 'f' * (4 * len(k)), *(v for row in k for v in row)))
            pc = ctypes.create_string_buffer(bytes([opcode, 0]))
            call(ctypes.addressof(source), ctypes.addressof(constants), outptr, ctypes.addressof(pc))
            cases.append({'name': 'cancellation', 'opcode': opcode, 'input': x, 'constants': k,
                          'output_bits': [f'0x{v:08x}' for v in struct.unpack('<4I', ctypes.string_at(outptr, 16))]})
    ranges = [(0x9477a, 0x949ee), (0x82a9ef, 0x82acfc)]
    return {'schema': 'd1-tfx-gradient-native-oracle-v1', 'sha256': EXPECTED_SHA256,
            'bss_tolerance_va': '0x1ac6320', 'rodata_tolerance_va': '0x1610be0',
            'tolerance_bits': '0x38d1b717', 'tolerance': eps,
            'initialization': '94813 rcx=BSS; 9486e xmm1=RODATA; 948d7 [rcx]=xmm1 (registers unmodified between relevant instructions)',
            'scope': 'finite arithmetic only; zero BSS with only proven tolerance supplied; final dispatch jump patched to RET; no live map/render claims',
            'ranges': [{'va': hex(a), 'bytes': raw[a+0x4000:b+0x4000].hex(),
                        'assembly': [f'{i.address:x} {i.mnemonic} {i.op_str}' for i in cs.disasm(raw[a+0x4000:b+0x4000],a)]} for a,b in ranges],
            'cases': cases}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('eboot', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = probe(args.eboot)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('native cases', len(result['cases']), 'tolerance', result['tolerance_bits'])
