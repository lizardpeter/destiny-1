#!/usr/bin/env python3
"""Probe the retail 16-slot cyclic Atmosphere LUT selection arithmetic.

Only 0x842790..0x842837 runs, with exits replaced by RET. No tag resolver,
renderer, map, texture allocation or libc is called. Whole-ELF mapping retains
exact RIP-relative constants. The surrounding producer's source-null gates
remain outside this arithmetic oracle.
"""
import argparse
import ctypes
import hashlib
import json
import mmap
import platform
import struct
import subprocess
import tempfile
from pathlib import Path
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from d1_global_lighting_settings_defaults import EXPECTED_SHA256


def f32(x):
    return ctypes.c_float(x).value


def select(phases, tags, phase):
    phase = f32(phase)
    for i in range(16):
        j = (i + 1) & 15
        a, b = f32(phases[i]), f32(phases[j])
        if j < i:
            if b < phase:
                b = f32(b + 1)
            else:
                a = f32(a - 1)
        if phase < a or b < phase:
            continue
        blend = 0. if a == b else f32(f32(phase - a) / f32(b - a))
        return {'slot0':i,'slot1':j,'tag0':tags[i],'tag1':tags[j],
                'blend':blend,'atlas0':i/16.,'atlas1':j/16.}
    return None


def probe(path):
    if platform.machine() not in ('x86_64','AMD64') or ' avx ' not in Path('/proc/cpuinfo').read_text():
        raise RuntimeError('requires Linux x86-64 AVX')
    raw=path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256
    start,end=0x842790,0x842837
    dis=list(Cs(CS_ARCH_X86,CS_MODE_64).disasm(raw[start+0x4000:end+0x4000],start))
    assert all(i.mnemonic != 'call' for i in dis)
    assert any(i.address==0x842796 and i.op_str=='0x843050' for i in dis)
    assert struct.unpack_from('<f',raw,0x1663F10+0x4000)[0] == 1/2048.
    kernel=mmap.mmap(-1,len(raw),prot=7);kernel.write(raw)
    kernel[end+0x4000]=0xC3;kernel[0x843050+0x4000]=0xC3
    target=ctypes.addressof(ctypes.c_char.from_buffer(kernel))+start+0x4000
    log=ctypes.create_string_buffer(8)
    asm=f""".intel_syntax noprefix
.text
.global wrapper
wrapper:
 push rbx
 push r13
 push r14
 mov rbx, rdi
 mov r14, rsi
 xor edi, edi
 mov ecx, 0xffffff80
 mov r13d, 0xdeadbeef
 vmovaps xmm4, xmm0
 movabs rax, {target}
 call rax
 movabs rax, {ctypes.addressof(log)}
 mov [rax], edx
 mov [rax+4], r13d
 pop r14
 pop r13
 pop rbx
 ret
"""
    with tempfile.TemporaryDirectory() as td:
        src,obj,binary=[Path(td)/x for x in ('wrapper.s','wrapper.o','wrapper.bin')]
        src.write_text(asm)
        subprocess.run(['gcc','-c',str(src),'-o',str(obj)],check=True)
        subprocess.run(['objcopy','-O','binary','-j','.text',str(obj),str(binary)],check=True)
        wrapper=binary.read_bytes()
    trampoline=mmap.mmap(-1,len(wrapper),prot=7);trampoline.write(wrapper)
    call=ctypes.CFUNCTYPE(None,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_float)(ctypes.addressof(ctypes.c_char.from_buffer(trampoline)))
    tags=[0x80AA1000+i for i in range(16)]
    uniform=[i/16 for i in range(16)]
    scenarios=[('uniform',uniform,p) for p in [0,.03125,.0625,.5,.9375,.96875,1,-.01,-.1,-1,1.01]]
    scenarios += [('uniform_boundary',uniform,i/16) for i in range(1,16)]
    scenarios += [('duplicate', [0]*16,p) for p in [0,.4,1]]
    authored=[0,.1,.1,.2,.25,.4,.5,.6,.7,.75,.8,.85,.9,.95,.975,.99]
    scenarios += [('nonuniform',authored,p) for p in [.1,.15,.995,.975]]
    cases=[]
    for name,phases,phase in scenarios:
        settings=ctypes.create_string_buffer(0xF0)
        struct.pack_into('<16I',settings,0,*tags)
        struct.pack_into('<16f',settings,0x48,*phases)
        block=ctypes.create_string_buffer(bytes([0xA5])*0x130)
        before=bytes(block);expected=select(phases,tags,phase)
        call(block,settings,f32(phase))
        native_tags=struct.unpack('<II',log.raw)
        expected_bytes=bytearray(before)
        if expected is None:
            assert native_tags==(16,0xDEADBEEF), (name, phase, native_tags)
        else:
            assert native_tags==(expected['tag0'],expected['tag1'])
            for off,field in [(0x10,'blend'),(0x120,'atlas0'),(0x124,'atlas1')]:
                struct.pack_into('<f',expected_bytes,off,expected[field])
        assert bytes(block)==expected_bytes
        cases.append({'name':name,'phases':phases,'phase':f32(phase),'selection':expected,
                      'native_selected_tags':[f'{x:08X}' for x in native_tags],
                      'native_block_outputs':{hex(o):struct.unpack_from('<f',block,o)[0] for o in (0x10,0x120,0x124)} if expected else {}})
    return {'schema':'d1-atmosphere-lut-selection-native-oracle-v1','sha256':EXPECTED_SHA256,
            'start_va':hex(start),'end_va':hex(end),
            'source_settings':{'tags':'16 u32 at +0x00','phases':'16 f32 at +0x48'},
            'contract':'First inclusive interval wins; wrap adds 1 to upper endpoint when upper < phase, otherwise subtracts 1 from lower endpoint. Duplicate endpoints produce zero blend. Atlas offsets are selected slot indices /16.',
            'source':[{'va':hex(i.address),'bytes':i.bytes.hex(),'mnemonic':i.mnemonic,'operands':i.op_str} for i in dis],
            'cases':cases,'all_native_outputs_match':True,
            'remaining':['source class ID and map joins','tag/null activation gates','LUT texels and format','live phase provider','render validation']}


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('eboot',type=Path);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();result=probe(args.eboot)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'cases':len(result['cases']),'all_native_outputs_match':result['all_native_outputs_match']}))
