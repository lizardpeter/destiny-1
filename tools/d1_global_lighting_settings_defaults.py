#!/usr/bin/env python3
"""Verify GlobalLighting[38:42] retail defaults directly from the 01.33 ELF.

Requires capstone and pyelftools. Input can be downloaded from
https://r2.houseofkublai.com/destiny/CUSA00219_01.33/eboot.bin
These are mutable engine configuration defaults, not captured live overrides.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_REG_RIP
from elftools.elf.elffile import ELFFile

EXPECTED_SHA256 = "672f03411c0503dfbcda804cbb9fb27cdd9a8d73a8bcb71bf0c4f688073b0833"
DEFAULT_SOURCE = 0x27368B8
LIVE_SETTINGS = 0x2736860
FIELD_OFFSETS = (0x3C, 0x40, 0x50, 0x54)


def inspect(path):
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError(f"wrong executable SHA256: {digest}")
    with path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [dict(s.header) for s in elf.iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def read(va, length):
        for seg in segments:
            delta = va - seg["p_vaddr"]
            if 0 <= delta and delta + length <= seg["p_filesz"]:
                start = seg["p_offset"] + delta
                return data[start:start + length]
        raise ValueError(f"unbacked executable address: {va:x}")

    dis = Cs(CS_ARCH_X86, CS_MODE_64)
    dis.detail = True

    def window(start, end):
        raw = read(start, end - start)
        return {"start_va": hex(start), "bytes": raw.hex(), "instructions": [
            {"va": hex(i.address), "bytes": i.bytes.hex(),
             "mnemonic": i.mnemonic, "operands": i.op_str}
            for i in dis.disasm(raw, start)]}

    writes = {}
    for ins in dis.disasm(read(0x8B0180, 0x8B026A - 0x8B0180), 0x8B0180):
        ops = ins.operands
        if ins.mnemonic == "mov" and len(ops) == 2:
            dst, src = ops
            if dst.type == X86_OP_MEM and dst.mem.base == X86_REG_RIP and src.type == X86_OP_IMM:
                target = ins.address + ins.size + dst.mem.disp
                writes[target] = (src.imm & 0xFFFFFFFF, ins.address)
    words = []
    for word, offset, expected in zip(range(38, 42), FIELD_OFFSETS, (0, 0, 0x3F800000, 0x3F800000)):
        bits, writer = writes[DEFAULT_SOURCE + offset]
        if bits != expected:
            raise ValueError(f"unexpected default for word {word}: {bits:x}")
        words.append({"word": word, "settings_offset": hex(offset),
                      "default_bits": f"0x{bits:08x}",
                      "default_float": struct.unpack("<f", struct.pack("<I", bits))[0],
                      "writer_va": hex(writer)})
    # Check the snapshot getter and the complete 11-qword default copy.
    assert read(0x8AFCC0, 8).hex() == "488d8740930100c3"
    assert read(0x8B0261, 9).hex() == "b90b000000f348a5c3"
    # Verify consumer source/destination fields, rather than inferring their order.
    consumer = list(dis.disasm(read(0x88E971, 0x88E9A5 - 0x88E971), 0x88E971))
    loads = [i.operands[1].mem.disp for i in consumer
             if i.mnemonic == "vmovss" and i.operands[1].type == X86_OP_MEM]
    stores = [i.operands[0].mem.disp for i in consumer
              if i.mnemonic == "vmovss" and i.operands[0].type == X86_OP_MEM]
    assert loads == list(FIELD_OFFSETS), loads
    assert stores == [word * 4 for word in range(38, 42)], stores
    return {"schema": "d1-global-lighting-settings-defaults-v1", "sha256": digest,
            "scope": "CUSA00219 01.33 mutable engine settings defaults; live overrides uncaptured",
            "default_source_va": hex(DEFAULT_SOURCE), "live_settings_va": hex(LIVE_SETTINGS),
            "settings_size": 0x58, "renderer_snapshot_offset": "0x19340", "words": words,
            "windows": {"getter": window(0x8AFCC0, 0x8AFCC8),
                        "consumer": window(0x88E969, 0x88E9A5),
                        "initializer": window(0x8B0180, 0x8B026A),
                        "mutable_settings_setter": window(0x8AFCD0, 0x8AFD10),
                        "snapshot_copy": window(0x8AFD10, 0x8AFD70)}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("eboot", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(inspect(args.eboot), indent=2) + "\n"
    if args.output:
        args.output.write_text(result)
    else:
        print(result, end="")
