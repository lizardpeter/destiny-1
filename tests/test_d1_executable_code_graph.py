import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


normalize_mod = load(
    "d1_ghidra_graph_normalize", "tools/d1_ghidra_graph_normalize.py"
)
compare_mod = load("d1_executable_compare", "tools/d1_executable_compare.py")

SHA_A = "a" * 64
SHA_B = "b" * 64


def fn(entry, offset, name, byte_hash, mnemonic_hash, count=4, start=None, end=None):
    if start is None:
        start = offset
    if end is None:
        end = offset + 0x1F
    return {
        "entry": entry,
        "image_offset": offset,
        "name": name,
        "namespace": "Global",
        "source": "ANALYSIS",
        "is_thunk": False,
        "is_external": False,
        "body_min": entry,
        "body_max": entry,
        "body_address_count": end - start + 1,
        "body_ranges": [
            {
                "min": entry,
                "max": entry,
                "min_image_offset": start,
                "max_image_offset": end,
            }
        ],
        "parameter_count": 0,
        "calling_convention": "unknown",
        "prototype": f"void {name}(void)",
        "called_function_entries": [],
        "instruction_count": count,
        "instruction_byte_count": count * 4,
        "instruction_bytes_sha256": byte_hash,
        "mnemonic_sequence_sha256": mnemonic_hash,
    }


def report(sha, version, functions):
    return {
        "schema": "d1_ghidra_code_graph/v1",
        "program": {
            "name": "eboot.bin",
            "title_id": "CUSA00219",
            "app_version": version,
            "executable_path": "eboot.bin",
            "executable_format": "ELF",
            "executable_md5": "0" * 32,
            "executable_sha256": sha,
            "language_id": "x86:LE:64:default",
            "compiler_spec": "gcc",
            "image_base": "0080000000",
        },
        "counts": {},
        "functions": functions,
        "calls": [],
        "external_functions": [],
        "external_libraries": [],
        "strings": [],
    }


def test_graph_normalizer_emits_stable_function_call_and_string_edges():
    a = fn("0080001000", 0x1000, "FUN_1000", "1" * 64, "2" * 64)
    b = fn("0080002000", 0x2000, "FUN_2000", "3" * 64, "4" * 64)
    a["called_function_entries"] = [b["entry"]]
    doc = report(SHA_A, "01.29", [a, b])
    doc["calls"] = [{"caller": a["entry"], "callee": b["entry"]}]
    doc["strings"] = [
        {
            "address": "0080010000",
            "image_offset": 0x10000,
            "length": 14,
            "data_type": "string",
            "text": "Graphics Heartbeat",
            "xrefs": [
                {
                    "from": "0080001010",
                    "from_image_offset": 0x1010,
                    "function_entry": a["entry"],
                    "function_name": a["name"],
                    "reference_type": "DATA",
                }
            ],
        }
    ]

    manifest, nodes, edges = normalize_mod.normalize(doc)
    assert manifest["counts"]["functions"] == 2
    assert manifest["counts"]["call_edges"] == 1
    assert manifest["counts"]["defined_strings"] == 1
    assert manifest["counts"]["string_xref_edges"] == 1
    assert any(e["predicate"] == "CALLS" for e in edges)
    assert any(e["predicate"] == "REFERENCES_STRING" for e in edges)
    assert any(n["kind"] == "defined_string" for n in nodes)


def test_compare_uses_exact_then_mnemonic_then_name_tiers():
    exact_a = fn("A100", 0x100, "FUN_100", "1" * 64, "a" * 64)
    mnemonic_a = fn("A200", 0x200, "FUN_200", "2" * 64, "b" * 64)
    named_a = fn("A300", 0x300, "KnownSemanticName", "3" * 64, "c" * 64)

    exact_b = fn("B180", 0x180, "FUN_180", "1" * 64, "a" * 64)
    mnemonic_b = fn("B280", 0x280, "FUN_280", "9" * 64, "b" * 64)
    named_b = fn("B380", 0x380, "KnownSemanticName", "8" * 64, "d" * 64)

    result = compare_mod.compare(
        report(SHA_A, "01.29", [exact_a, mnemonic_a, named_a]),
        report(SHA_B, "01.33", [exact_b, mnemonic_b, named_b]),
        [],
    )

    assert result["counts"]["proven_exact"] == 1
    assert result["counts"]["strong_mnemonic"] == 1
    assert result["counts"]["candidate_name"] == 1
    assert [m["status"] for m in result["matches"]] == [
        "PROVEN",
        "STRONGLY_SUPPORTED",
        "CANDIDATE",
    ]


def test_compare_locates_relocation_stable_anchor_by_image_offset():
    a = fn(
        "AFA000",
        0xFA000,
        "FUN_A",
        "1" * 64,
        "2" * 64,
        start=0xFA000,
        end=0xFABFF,
    )
    b = fn(
        "BFA000",
        0xFA000,
        "FUN_B",
        "1" * 64,
        "2" * 64,
        start=0xFA000,
        end=0xFABFF,
    )

    result = compare_mod.compare(
        report(SHA_A, "01.29", [a]),
        report(SHA_B, "01.33", [b]),
        [0xFAAF4],
    )
    anchor = result["anchor_checks"][0]
    assert anchor["image_offset"] == "0xFAAF4"
    assert len(anchor["a_functions"]) == 1
    assert len(anchor["b_functions"]) == 1
    assert anchor["same_unique_exact_function"] is True
