import importlib.util
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

SPEC = importlib.util.spec_from_file_location(
    "d1_executable_renderer_strings",
    TOOLS / "d1_executable_renderer_strings.py",
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules["d1_executable_renderer_strings"] = mod
SPEC.loader.exec_module(mod)


def synthetic_renderer_elf() -> bytes:
    data = bytearray(0x400)
    data[:16] = bytes([
        0x7F, ord("E"), ord("L"), ord("F"),
        2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    ])
    struct.pack_into(
        "<HHIQQQIHHHHHH",
        data,
        16,
        2,
        0x3E,
        1,
        0x400110,
        64,
        0,
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
        1,
        5,
        0x100,
        0x400000,
        0x400000,
        0x200,
        0x200,
        0x1000,
    )
    string_offset = 0x180
    text = b"deferred lighting render target\x00"
    data[string_offset:string_offset + len(text)] = text

    instruction_offset = 0x110
    instruction_va = 0x400000 + (instruction_offset - 0x100)
    target_va = 0x400000 + (string_offset - 0x100)
    displacement = target_va - (instruction_va + 7)
    data[instruction_offset:instruction_offset + 3] = b"\x48\x8D\x05"
    struct.pack_into("<i", data, instruction_offset + 3, displacement)
    data[instruction_offset + 7] = 0xC3
    return bytes(data)


def test_classify_renderer_domains():
    assert "lighting" in mod.classify("deferred lighting pass")
    assert "frame_graph" in mod.classify("render target allocation")
    assert "fixed_function" in mod.classify("depth stencil state")
    assert "shader_material" in mod.classify("pixel shader resource table")
    assert mod.classify("ordinary gameplay message") == []


def test_analyze_keeps_exact_sha_and_candidate_xref(tmp_path):
    exe = tmp_path / "eboot.bin"
    exe.write_bytes(synthetic_renderer_elf())
    result = mod.analyze(exe, limit_per_category=16)
    assert result["schema"] == "d1_executable_renderer_strings/v1"
    row = next(
        item
        for item in result["strings"]
        if item["text"] == "deferred lighting render target"
    )
    assert set(row["categories"]) >= {"lighting", "frame_graph"}
    assert row["candidate_lea_xref_count"] == 1
    assert (
        row["candidate_lea_xrefs"][0]["file_offset"]
        == 0x110
    )
    assert result["counts"]["candidate_lea_xrefs"] == 1
