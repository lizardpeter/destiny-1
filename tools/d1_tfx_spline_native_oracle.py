#!/usr/bin/env python3
"""Execute call-free/RIP-free retail D1 01.33 spline kernels, including XOR masks.

Only final VM dispatch jumps become RET. All polynomial arithmetic, threshold
comparison, XOR masking/reduction, and previous-stack-value selection are retail
instructions. Synthetic constants test semantics without claiming map ownership.
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
from d1_global_lighting_settings_defaults import EXPECTED_SHA256


def probe(path):
    if platform.machine() != 'x86_64' or ' avx ' not in Path('/proc/cpuinfo').read_text():
        raise RuntimeError('requires x86-64 AVX')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256
    first, last = 0x82a764, 0x82a9ef
    code = raw[first+0x4000:last+0x4000]
    cs = Cs(CS_ARCH_X86, CS_MODE_64)
    asm = list(cs.disasm(code, first))
    assert sum(i.size for i in asm) == len(code)
    assert not any(i.mnemonic == 'call' or 'rip' in i.op_str for i in asm)
    image = mmap.mmap(-1, len(code), prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC)
    image.write(code)
    handlers = {0x37:(0x82a764,0x82a7df), 0x38:(0x82a7e4,0x82a8d7), 0x39:(0x82a8dc,0x82a9ea)}
    for start, end in handlers.values():
        ins = next(cs.disasm(code[end-first:end-first+5], end))
        assert ins.mnemonic == 'jmp' and ins.op_str == '0x82b228'
        image[end-first:end-first+5] = b'\xc3\x90\x90\x90\x90'
    base = ctypes.addressof(ctypes.c_char.from_buffer(image))
    buffer = ctypes.create_string_buffer(64)
    output = (ctypes.addressof(buffer)+15)&~15
    below = [11.0,22.0,33.0,44.0]
    cases = []
    for opcode, (start, _) in handlers.items():
        wrapper = bytes.fromhex('4154415541564989f44989cd4989d6c578101748b8')
        wrapper += struct.pack('<Q',base+start-first)+bytes.fromhex('ffd0415e415d415cc3')
        thunk = mmap.mmap(-1,len(wrapper),prot=mmap.PROT_READ|mmap.PROT_WRITE|mmap.PROT_EXEC)
        thunk.write(wrapper)
        call = ctypes.CFUNCTYPE(None,*([ctypes.c_void_p]*4))(ctypes.addressof(ctypes.c_char.from_buffer(thunk)))
        for name, ta, tb in [
            ('ordered',[0.0,.25,.5,.75],[1.0,1.25,1.5,1.75]),
            ('unsorted',[.5,0.0,.75,.25],[1.5,1.0,1.75,1.25]),
            ('duplicate',[0.0,.25,.25,.75],[1.0,1.25,1.25,1.75]),
        ]:
            k = [[.1,.2,.3,.4],[.5,.6,.7,.8],[.9,1.0,1.1,1.2],[1.3,1.4,1.5,1.6]]
            if opcode == 0x37:
                k.append(ta)
            else:
                k.extend([[-.1,-.2,-.3,-.4],[-.5,-.6,-.7,-.8],[-.9,-1.0,-1.1,-1.2],[-1.3,-1.4,-1.5,-1.6],ta,tb])
            for x in [[-.5]*4,[0.0]*4,[.25]*4,[.625]*4,[1.5]*4,[2.0]*4,
                      [.9,-.1,.8,-.1],[-.1,.9,-.1,.9],[1.8,.5,1.9,.5],[-.1,1.5,.9,2.0]]:
                constants = ctypes.create_string_buffer(struct.pack('<'+'f'*(4*len(k)),*(v for row in k for v in row)))
                source = ctypes.create_string_buffer(struct.pack('<4f',*x))
                pc = ctypes.create_string_buffer(bytes([opcode,0]))
                ctypes.memmove(output,struct.pack('<4f',*below),16)
                call(ctypes.addressof(source),ctypes.addressof(constants),output+16,ctypes.addressof(pc))
                ptr = output if opcode == 0x39 else output+16
                bits = struct.unpack('<4I',ctypes.string_at(ptr,16))
                cases.append({'name':name,'opcode':opcode,'input':x,'below':below,'constants':k,
                              'output_bits':[f'0x{b:08x}' for b in bits]})
    return {'schema':'d1-tfx-spline-native-oracle-v1','sha256':EXPECTED_SHA256,
            'handler_range':['0x82a764','0x82a9ef'],'bytes':code.hex(),
            'assembly':[f'{i.address:x} {i.mnemonic} {i.op_str}' for i in asm],
            'scope':'finite synthetic inputs/constants; no live source scalar, activity output ownership, or render validation',
            'patch':'only three final dispatch jumps to RET; all arithmetic and masks preserved',
            'cases':cases}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('eboot',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=probe(args.eboot)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print('native cases',len(result['cases']))
