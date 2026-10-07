#!/usr/bin/env python3
"""Run actual sequencer VM arithmetic against independently pinned material TFX cases.

Map source PT_LOAD segments at virtual offsets, zero BSS, supply only the proven
retail gradient tolerance. Patch final dispatch jumps to RET. Runtime scalar
meanings, descriptor joins, output-slot ownership, and update order remain open.
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


def probe(path, evidence):
    if platform.machine() != 'x86_64' or ' avx ' not in Path('/proc/cpuinfo').read_text():
        raise RuntimeError('requires x86-64 AVX')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256
    with path.open('rb') as f:
        segments = [dict(s.header) for s in ELFFile(f).iter_segments() if s['p_type'] == 'PT_LOAD']
    image = mmap.mmap(-1, max(s['p_vaddr'] + s['p_memsz'] for s in segments),
                      prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC)
    for s in segments:
        image[s['p_vaddr']:s['p_vaddr'] + s['p_filesz']] = raw[s['p_offset']:s['p_offset'] + s['p_filesz']]
    assert bytes(image[0x1ac6320:0x1ac6330]) == bytes(16)
    tolerance = bytes(image[0x1610be0:0x1610bf0])
    assert struct.unpack('<4I', tolerance) == (0x38d1b717,) * 4
    image[0x1ac6320:0x1ac6330] = tolerance
    cs = Cs(CS_ARCH_X86, CS_MODE_64)
    handlers = {0x2a: (0x238085, 0x238153), 0x37: (0x238b2f, 0x238ba4),
                0x38: (0x238ba9, 0x238c90), 0x39: (0x238c95, 0x238d97),
                0x3a: (0x238d9c, 0x239091), 0x3b: (0x238ec4, 0x239091)}
    ranges = []
    for opcode, (start, end) in handlers.items():
        displacement = struct.unpack_from('<i', raw, 0x239138 + 0x4000 + (opcode - 1) * 4)[0]
        assert 0x239138 + displacement == start
        # Read source bytes, because Gradient4/8 share the same terminal jump.
        terminal = next(cs.disasm(raw[end + 0x4000:end + 0x4000 + 5], end))
        assert terminal.mnemonic == 'jmp' and terminal.op_str == '0x2390d0'
        code = raw[start + 0x4000:end + terminal.size + 0x4000]
        asm = list(cs.disasm(code, start))
        assert sum(i.size for i in asm) == len(code)
        assert not any(i.mnemonic == 'call' for i in asm)
        ranges.append({'opcode': opcode, 'start': hex(start), 'exit': hex(end), 'bytes': code.hex(),
                       'assembly': [f'{i.address:x} {i.mnemonic} {i.op_str}' for i in asm]})
        image[end:end + terminal.size] = b'\xc3' + b'\x90' * (terminal.size - 1)
    base = ctypes.addressof(ctypes.c_char.from_buffer(image))
    suite, provenance = [], []
    for name in ['d1-tfx-gradient-native-oracle-20261007.json',
                 'd1-tfx-spline-native-oracle-20261007.json',
                 'd1-tfx-rand-sequencer-native-oracle-20261007.json']:
        data = (evidence / name).read_bytes()
        j = json.loads(data)
        assert j['sha256'] == EXPECTED_SHA256
        provenance.append({'path': name, 'sha256': hashlib.sha256(data).hexdigest()})
        for index, original in enumerate(j['cases']):
            c = dict(original)
            if 'opcode' not in c:
                c.update(opcode=0x2a, input=[c['input_x'], 123.0, -456.0, .25], constants=[])
            c.update(source_case=index, source_evidence=name)
            suite.append(c)
    buffer = ctypes.create_string_buffer(64)
    output = (ctypes.addressof(buffer) + 15) & ~15
    wrappers, results = {}, []
    for opcode, (start, _) in handlers.items():
        # SysV input/constants/output/PC -> xmm7/rbx/r15/r12. Preserve callee-save registers.
        wrapper = bytes.fromhex('53415441574889f34989cc4989d7c5f8103f48b8')
        wrapper += struct.pack('<Q', base + start) + bytes.fromhex('ffd0415f415c5bc3')
        thunk = mmap.mmap(-1, len(wrapper), prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC)
        thunk.write(wrapper)
        call = ctypes.CFUNCTYPE(None, *([ctypes.c_void_p] * 4))(ctypes.addressof(ctypes.c_char.from_buffer(thunk)))
        wrappers[opcode] = (thunk, call)
    for c in suite:
        source = ctypes.create_string_buffer(struct.pack('<4f', *c['input']))
        k = c['constants']
        constants = ctypes.create_string_buffer(struct.pack('<' + 'f' * (4 * len(k)), *(v for row in k for v in row)))
        pc = ctypes.create_string_buffer(bytes([c['opcode'], 0]))
        ctypes.memmove(output, struct.pack('<4f', *c.get('below', [0.0] * 4)), 16)
        wrappers[c['opcode']][1](ctypes.addressof(source), ctypes.addressof(constants), output + 16, ctypes.addressof(pc))
        ptr = output if c['opcode'] == 0x39 else output + 16
        bits = [f'0x{b:08x}' for b in struct.unpack('<4I', ctypes.string_at(ptr, 16))]
        assert bits == c['output_bits'], (c['opcode'], c['source_case'], bits, c['output_bits'])
        results.append({'opcode': c['opcode'], 'source_evidence': c['source_evidence'],
                        'source_case': c['source_case'], 'sequencer_output_bits': bits,
                        'matches_material_tfx': True})
    return {'schema': 'd1-sequencer-arithmetic-native-oracle-v1', 'sha256': EXPECTED_SHA256,
            'vm_entry': '0x237710', 'jump_table': '0x239138', 'ranges': ranges, 'provenance': provenance,
            'scope': 'Isolated arithmetic only; scalar0 meanings, descriptor joins, output-slot ownership and update order remain open.',
            'cases': results}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('eboot', type=Path)
    parser.add_argument('--evidence-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = probe(args.eboot, args.evidence_dir)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('actual sequencer native cases', len(result['cases']), 'all match material TFX')
