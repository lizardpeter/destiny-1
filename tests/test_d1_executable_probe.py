import importlib.util
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "d1_executable_probe", ROOT / "tools" / "d1_executable_probe.py"
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules["d1_executable_probe"] = mod
SPEC.loader.exec_module(mod)


def synthetic_elf64() -> bytes:
    data = bytearray(0x200)
    data[:16] = bytes([
        0x7F, ord("E"), ord("L"), ord("F"),
        2,  # ELF64
        1,  # little-endian
        1,  # version
        0,  # SYSV
        0, 0, 0, 0, 0, 0, 0, 0,
    ])
    struct.pack_into(
        "<HHIQQQIHHHHHH",
        data,
        16,
        2,          # ET_EXEC
        0x3E,       # x86_64
        1,
        0x400100,   # entry
        64,         # phoff
        0,          # shoff
        0,
        64,
        56,
        1,
        64,
        0,
        0,
    )
    struct.pack_into(
        "<IIQQQQQQ",
        data,
        64,
        1,          # PT_LOAD
        5,          # R|X
        0x100,
        0x400000,
        0x400000,
        0x80,
        0x80,
        0x1000,
    )
    data[0x100:0x10D] = b"DESTINY_TEST\x00"
    return bytes(data)


def test_plain_elf64_header_and_executable_segment():
    raw = synthetic_elf64()
    assert mod.find_embedded_elf(raw) == 0
    header = mod.parse_elf64_header(raw, 0)
    assert header["class"] == 64
    assert header["machine_name"] == "x86_64"
    assert header["entry"] == "0x400100"
    ph = mod.parse_elf64_program_headers(raw, header)
    assert len(ph) == 1
    assert ph[0]["type_name"] == "PT_LOAD"
    assert ph[0]["readable"] is True
    assert ph[0]["writable"] is False
    assert ph[0]["executable"] is True
    assert ph[0]["file_offset"] == 0x100
    assert ph[0]["absolute_file_offset"] == 0x100


def test_self_can_locate_embedded_elf():
    elf = synthetic_elf64()
    raw = bytearray(0x100 + len(elf))
    raw[:4] = mod.PS4_SELF_MAGIC
    raw[4:8] = bytes([1, 1, 1, 0])
    struct.pack_into("<I", raw, 8, 0x401)
    struct.pack_into("<HH", raw, 12, 0x100, 0)
    struct.pack_into("<Q", raw, 16, len(raw))
    struct.pack_into("<HH", raw, 24, 1, 0)
    raw[0x100:] = elf

    assert mod.classify(raw) == "ps4_self"
    assert mod.find_embedded_elf(raw) == 0x100
    self_header = mod.parse_self_header(raw)
    assert self_header["declared_file_size"] == len(raw)

    elf_header = mod.parse_elf64_header(raw, 0x100)
    assert elf_header["entry"] == "0x400100"
    ph = mod.parse_elf64_program_headers(raw, elf_header)
    assert ph[0]["executable"] is True
    assert ph[0]["absolute_file_offset"] == 0x200


def test_printable_strings_preserve_file_offsets():
    raw = b"\x00abc\x00hello_world\x00\xffDestiny 1\x00"
    strings = mod.printable_ascii_strings(raw, min_length=5)
    assert strings == [
        {"file_offset": 5, "length": 11, "text": "hello_world"},
        {"file_offset": 18, "length": 9, "text": "Destiny 1"},
    ]


def test_known_0129_hash_lookup():
    known = mod.KNOWN_BUILDS[
        "7271fcb926401df8defb126cb8eb2b247134138b81e401bbacb2ab60791b795"
    ]
    assert known["title_id"] == "CUSA00219"
    assert known["app_version"] == "01.29"
