#!/usr/bin/env python3
"""Record exact retail Atmosphere settings ownership/copy boundaries.

Loader metadata proves callback/type-object pointers, not the class ID later
resolved inside the runtime type object. No current map is activated here.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from d1_executable_probe import parse_elf64_header, parse_elf64_program_headers
from d1_global_lighting_settings_defaults import EXPECTED_SHA256


def contract(path):
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256
    segments = parse_elf64_program_headers(raw, parse_elf64_header(raw))
    dynamic = next(s for s in segments if s['type'] == 2)
    dynlib = next(s for s in segments if s['type'] == 0x61000000)
    tags = dict(struct.unpack_from('<QQ', raw, o) for o in range(dynamic['absolute_file_offset'], dynamic['absolute_file_offset'] + dynamic['file_size'], 16))
    base = dynlib['absolute_file_offset']
    relocations = {}
    for i in range(tags[0x61000031] // 24):
        off, info, addend = struct.unpack_from('<QQq', raw, base + tags[0x6100002F] + i * 24)
        relocations[off] = {'index': i, 'offset': hex(off), 'type': info & 0xFFFFFFFF, 'addend': hex(addend)}
    expected = {0x198E1E0:0x8417C0, 0x198E1F8:0x841890, 0x198EA68:0x28D75B0, 0x1992350:0x28D75B0}
    for off, addend in expected.items():
        assert relocations[off]['addend'] == hex(addend) and relocations[off]['type'] == 8
    assert struct.unpack_from('<I', raw, 0x1992358 + 0x4000)[0] == 0x09FBE029
    name_va = 0x1663F30
    name = raw[name_va + 0x4000:raw.index(b'\0', name_va + 0x4000)].decode()
    assert name == 'atmosphere settings'
    dis = Cs(CS_ARCH_X86, CS_MODE_64)
    ranges = {
        'source_tag_load': (0x8417C0,0x841887),
        'reset': (0x841890,0x84192D),
        'global_allocation': (0x841A80,0x841B1E),
        'global_setter_and_getter': (0x841EE0,0x841F18),
        'renderer_settings_snapshot_0': (0x7EBE70,0x7EBEC1),
        'renderer_settings_snapshot_1': (0x7ECE80,0x7ECECE),
        'context_copy_0': (0x807460,0x80752C),
        'context_copy_1': (0x807530,0x8075FC),
        'producer_call_primary': (0x80C403,0x80C428),
        'producer_call_secondary': (0x80B803,0x80B855),
        'secondary_mode_gate': (0x841FA0,0x84201B),
    }
    instructions = {}
    for name, (start,end) in ranges.items():
        instructions[name] = [{'va':hex(i.address),'bytes':i.bytes.hex(),'mnemonic':i.mnemonic,'operands':i.op_str}
                              for i in dis.disasm(raw[start + 0x4000:end + 0x4000],start)]
        assert instructions[name]
    lookup = {int(i['va'],16):i for rows in instructions.values() for i in rows}
    checks = {0x841844:('add','rax, 0xc'), 0x841852:('mov','edx, 0x88'),
              0x841AE5:('mov','dword ptr [rax + 0x88], 3'),
              0x841EF6:('mov','edx, 0x90'), 0x7EBE90:('mov','edx, 0xf0'),
              0x7ECE9D:('mov','edx, 0xf0'), 0x8074E6:('lea','rdi, [rbx + 0x34]'),
              0x8074EA:('add','r14, 0x191f8'), 0x8074F4:('mov','edx, 0xf0'),
              0x8075BA:('add','r14, 0x191f8'), 0x8075C4:('mov','edx, 0xf0'),
              0x80C403:('lea','rdx, [r13 + 0x34]'), 0x80C423:('call','0x8426c0'),
              0x80B831:('lea','r9, [rbx + 0x34]'), 0x842006:('call','0x8426c0')}
    for va, (mnemonic,operands) in checks.items():
        assert (lookup[va]['mnemonic'],lookup[va]['operands']) == (mnemonic,operands)
    return {'schema':'d1-atmosphere-settings-owner-contract-v1','sha256':EXPECTED_SHA256,
            'owner_global_pointer_va':'0x2709aa0','owner_name':'atmosphere settings','allocated_bytes':0xF0,
            'registered_source_type_object_va':'0x28d75b0','registered_type_name_hash':'09FBE029',
            'relevant_relocations':[relocations[o] for o in expected],
            'contract':[
                'Global allocation initializes settings +0x88 to mode 3 and source-null words +0,+0x40,+0x44.',
                'Source loader 0x8417c0 resolves the class through type object +0, zero-initializes a 0x90-byte temporary, copies exactly 0x88 source bytes beginning at tag payload +0x0c, and sends all 0x90 bytes to setter 0x841ee0. Its mode at +0x88 and texture override at +0x8c therefore remain zero.',
                'Setter copies 0x90 bytes only, preserving resolved channel indices at +0x90..+0xec in the global owner.',
                'Getter 0x841f10 returns the global settings pointer. Renderer callbacks copy all 0xf0 bytes to renderer +0x191f8.',
                'Context constructors copy renderer +0x191f8 to context +0x34, size 0xf0. Primary producer receives context +0x34 and view +0x500; secondary receives the same settings via r9 and view +0x500 after an earlier +0x4f0 base.',
                'Secondary pass accepts settings modes 0,1,4 and rejects other modes; producer alone also has an arithmetic mode-2 branch.'],
            'instructions':instructions,
            'remaining':['serialized source class ID inside runtime object is not resolved','actual map tag/activation joins','all context mode and texture-override mutations','view matrix semantic producer','atmosphere LUT generation/residency']}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('eboot',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    result=contract(args.eboot)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'owner':result['owner_global_pointer_va'],'type_name_hash':result['registered_type_name_hash'],'instruction_ranges':len(result['instructions'])}))
