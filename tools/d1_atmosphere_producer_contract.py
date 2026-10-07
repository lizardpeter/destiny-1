#!/usr/bin/env python3
"""Recover exact Atmosphere extern producer/channel contract from 01.33 ELF.

This records producer evidence; it does not claim atmosphere LUT texels, live
channels, camera transforms or all nonlinear coefficient conversions are closed.
Requires capstone and pyelftools, and the verified owner-provided eboot.bin.
"""
import argparse
import json
from pathlib import Path

from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_REG_RIP, X86_REG_R14, X86_REG_RBX
from d1_global_lighting_settings_defaults import inspect


def contract(path):
    identity = inspect(path)
    data = path.read_bytes()
    dis = Cs(CS_ARCH_X86, CS_MODE_64)
    dis.detail = True

    def instructions(start, end):
        # This exact ELF's executable PT_LOAD maps VA 0 to file offset 0x4000;
        # inspect() verifies the complete source identity first.
        return list(dis.disasm(data[start + 0x4000:end + 0x4000], start))

    def rows(start, end):
        return [{"va": hex(i.address), "bytes": i.bytes.hex(),
                 "mnemonic": i.mnemonic, "operands": i.op_str}
                for i in instructions(start, end)]

    names = []
    for i in instructions(0x8431CB, 0x8432BC):
        if i.mnemonic == "mov" and i.operands[0].type == X86_OP_MEM:
            dst, src = i.operands
            assert dst.mem.base == X86_REG_RIP and src.type == X86_OP_IMM
            names.append({"hash": src.imm & 0xFFFFFFFF,
                          "hash_hex": f"{src.imm & 0xFFFFFFFF:08X}",
                          "global_va": hex(i.address + i.size + dst.mem.disp),
                          "initializer_va": hex(i.address),
                          "settings_index_offset": hex(0x90 + len(names) * 4)})
    assert len(names) == 24
    # Walk only a verified instruction range. Each source settings index load
    # is followed by the exact channel fetch and destination write.
    source = None
    mappings = []
    for i in instructions(0x84293E, 0x842C71):
        ops = i.operands
        if i.mnemonic == "mov" and len(ops) == 2 and ops[1].type == X86_OP_MEM and ops[1].mem.base == X86_REG_R14:
            source = ops[1].mem.disp
        if source is None:
            continue
        dst = None
        if i.mnemonic == "lea" and len(ops) == 2 and ops[1].type == X86_OP_MEM and ops[1].mem.base == X86_REG_RBX:
            dst = ops[1].mem.disp
        elif i.mnemonic == "vmovss" and ops[0].type == X86_OP_MEM and ops[0].mem.base == X86_REG_RBX:
            dst = ops[0].mem.disp
        # First full-vector destination uses `mov rdx,rbx; sub rdx,-0x80`.
        elif i.address == 0x84294F:
            dst = 0x80
        if dst is not None:
            name = names[(source - 0x90) // 4]
            mappings.append({**name, "extern_offset": hex(dst), "extern_word": dst // 4,
                             "copied_lanes": 4 if source in (0x90, 0xBC, 0xD0, 0xEC) else 1,
                             "destination_va": hex(i.address)})
            source = None
    assert len(mappings) == 24
    return {"schema": "d1-atmosphere-producer-contract-v1", "sha256": identity["sha256"],
            "extern_id": 7, "extern_bytes": 0x130, "producer_va": "0x8426c0",
            "channel_fetch_va": "0x816140", "channel_index_resolver_va": "0x816240",
            "channel_name_initialization": "0x8431cb..0x8432bb",
            "channel_mappings_before_coefficient_transforms": mappings,
            "closure": "exact producer size and pre-transform channel routing only",
            "remaining": ["map activity atmosphere settings ownership and active LUT pair",
                          "live channel evaluation and camera transforms",
                          "nonlinear conversions at 0x842c71..0x842fdc",
                          "screen-space/sky LUT generation and texture residency"],
            "instructions": {"producer": rows(0x8426C0, 0x843075),
                             "settings_channel_index_setup": rows(0x841B50, 0x841E28),
                             "channel_fetch": rows(0x816140, 0x816161),
                             "channel_hashes": rows(0x8431C0, 0x8432BC)}}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("eboot", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    args.output.write_text(json.dumps(contract(args.eboot), indent=2) + "\n")
