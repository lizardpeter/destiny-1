#!/usr/bin/env python3
"""Reproducible static code comparison for verified Oodle 2.3 and Rust DLLs.

Never uploads DLL bytes: emits textual instruction statistics, function boundaries,
small disassembly excerpts, and (when PDB is available) resolved Rust symbols.
"""
import argparse
import collections
import ctypes
import json
import os
import re
from pathlib import Path

import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

MAX_FUNC_INSNS = 9000
EXCERPT_INSNS = 55
INT_BITS = ("shr", "shl", "sar", "ror", "rol", "shrx", "shlx", "bextr",
            "bsf", "bsr", "lzcnt", "tzcnt", "popcnt", "bswap", "movbe")


def symenum_windows(dll: Path):
    if os.name != "nt":
        return {"error": "Windows DbgHelp unavailable"}
    try:
        from ctypes import wintypes as w
        class SymbolInfoW(ctypes.Structure):
            _fields_ = [
                ("SizeOfStruct", w.ULONG), ("TypeIndex", w.ULONG),
                ("Reserved", ctypes.c_ulonglong * 2), ("Index", w.ULONG),
                ("Size", w.ULONG), ("ModBase", ctypes.c_ulonglong),
                ("Flags", w.ULONG), ("Value", ctypes.c_ulonglong),
                ("Address", ctypes.c_ulonglong), ("Register", w.ULONG),
                ("Scope", w.ULONG), ("Tag", w.ULONG),
                ("NameLen", w.ULONG), ("MaxNameLen", w.ULONG),
                ("Name", w.WCHAR * 1)]
        dbghelp = ctypes.WinDLL("dbghelp.dll", use_last_error=True)
        kernel = ctypes.WinDLL("kernel32.dll", use_last_error=True)
        kernel.GetCurrentProcess.restype = w.HANDLE
        proc = kernel.GetCurrentProcess()
        dbghelp.SymSetOptions.argtypes = [w.DWORD]
        dbghelp.SymSetOptions.restype = w.DWORD
        dbghelp.SymSetOptions(0x2 | 0x4 | 0x10)
        dbghelp.SymInitializeW.argtypes = [w.HANDLE, w.LPCWSTR, w.BOOL]
        dbghelp.SymInitializeW.restype = w.BOOL
        if not dbghelp.SymInitializeW(proc, None, False):
            return {"error": "SymInitializeW failed " + str(ctypes.get_last_error())}
        try:
            dbghelp.SymLoadModuleExW.argtypes = [
                w.HANDLE, w.HANDLE, w.LPCWSTR, w.LPCWSTR,
                ctypes.c_ulonglong, w.DWORD, ctypes.c_void_p, w.DWORD]
            dbghelp.SymLoadModuleExW.restype = ctypes.c_ulonglong
            base = dbghelp.SymLoadModuleExW(proc, None, str(dll.resolve()),
                                              None, 0, 0, None, 0)
            if not base:
                return {"error": "SymLoadModuleExW failed " + str(ctypes.get_last_error())}
            callback_t = ctypes.WINFUNCTYPE(w.BOOL, ctypes.POINTER(SymbolInfoW), w.ULONG,
                                             ctypes.c_void_p)
            symbols = []
            def callback(info, _size, _context):
                s = info.contents
                name_addr = ctypes.addressof(s) + SymbolInfoW.Name.offset
                name = ctypes.wstring_at(name_addr, s.NameLen)
                if any(t in name.lower() for t in (
                    "lzh", "quantum", "huffman", "decode", "copy_match", "oodle")):
                    symbols.append({"name": name[:360],
                                    "rva": hex(int(s.Address - base)),
                                    "size": int(s.Size)})
                return True
            handler = callback_t(callback)
            dbghelp.SymEnumSymbolsW.argtypes = [
                w.HANDLE, ctypes.c_ulonglong, w.LPCWSTR, callback_t, ctypes.c_void_p]
            dbghelp.SymEnumSymbolsW.restype = w.BOOL
            ok = dbghelp.SymEnumSymbolsW(proc, base, "*", handler, None)
            return {"loaded_base": hex(base), "enum_success": bool(ok),
                    "error_code": ctypes.get_last_error() if not ok else 0,
                    "matching_symbols": symbols[:180], "matched_total": len(symbols)}
        finally:
            dbghelp.SymCleanup.argtypes = [w.HANDLE]
            dbghelp.SymCleanup(proc)
    except Exception as exc:
        return {"error": type(exc).__name__ + ": " + str(exc)}


def analyze_function(pe, rva, max_insns=MAX_FUNC_INSNS):
    # Prefer real unwind metadata to guessing the end of a function.
    bound = None
    for fn in getattr(pe, "DIRECTORY_ENTRY_EXCEPTION", []):
        struct = fn.struct
        start, end = int(struct.BeginAddress), int(struct.EndAddress)
        if start <= rva < end:
            bound = (start, end)
            break
    max_bytes = 25000
    if bound:
        max_bytes = min(max_bytes, bound[1] - rva)
    code = pe.get_data(rva, max_bytes)
    if not code:
        return {"rva":hex(rva), "error":"RVA not mapped to bytes"}
    dis = Cs(CS_ARCH_X86, CS_MODE_64)
    dis.detail = False
    rows, mnemonics, family = [], collections.Counter(), collections.Counter()
    for ins in dis.disasm(code, pe.OPTIONAL_HEADER.ImageBase + rva):
        mnemonics[ins.mnemonic] += 1
        n = ins.mnemonic
        if n.startswith("j"):
            family["conditional_branch" if n!="jmp" else "unconditional_jump"] += 1
        if n=="call": family["call"] += 1
        if n.startswith(INT_BITS): family["integer_bit_ops"] += 1
        if any(reg in ins.op_str.lower() for reg in ("xmm","ymm","zmm")):
            family["vector_register_operand"] += 1
        if "[" in ins.op_str: family["memory_operand"] += 1
        if len(rows) < EXCERPT_INSNS:
            rows.append(f"0x{ins.address:016x}  {n:9s} {ins.op_str}")
        if sum(mnemonics.values())>=max_insns:
            break
    return {
        "requested_rva": hex(rva),
        "pdata_function_bounds": list(map(hex,bound)) if bound else None,
        "instructions_analyzed": sum(mnemonics.values()),
        "coverage_limited":sum(mnemonics.values())>=max_insns or max_bytes==25000,
        "instruction_categories": dict(family),
        "top_mnemonics": mnemonics.most_common(26),
        "notable_instructions": {k:v for k,v in mnemonics.items() if k.startswith(INT_BITS)},
        "entry_excerpt": rows,
    }


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--oodle",type=Path,required=True)
    a.add_argument("--rust",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    args=a.parse_args()
    result = {"notes": [
        "Static disassembly is not a CPU-cycle or dynamic-hotspot profile.",
        "Original Oodle RVA names are grounded in previous confirmed reverse engineering.",
        "DLL internal functions may have no public symbol; Rust PDB symbol enumeration is best effort.",
    ]}
    for label,path,rvas in [
        ("oodle23",args.oodle,[0x75dc0,0x78b20,0x5f8b0]),
        ("rust",args.rust,[])]:
        pe=pefile.PE(str(path),fast_load=False)
        exports=[]
        if hasattr(pe,"DIRECTORY_ENTRY_EXPORT"):
            for e in pe.DIRECTORY_ENTRY_EXPORT.symbols:
                name=(e.name or b"").decode("utf-8","replace")
                if "Decompress" in name or "Decode" in name:
                    exports.append({"name":name,"rva":hex(e.address)})
                    if label=="rust" and name=="OodleLZ_Decompress": rvas.append(int(e.address))
        summaries=[analyze_function(pe,rva) for rva in rvas]
        result[label]={"binary_name":path.name,"image_base":hex(pe.OPTIONAL_HEADER.ImageBase),
                       "size_bytes":path.stat().st_size,
                       "exports_relevant":exports[:35], "functions":summaries}
        if label=="rust":
            syms=symenum_windows(path)
            result[label]["debug_symbols"]=syms
            candidates=[]
            for symbol in syms.get("matching_symbols",[]):
                name=symbol["name"].lower()
                if any(x in name for x in ("decode_quantum", "decode_stream_into","decode_fast_multi",
                                            "copy_match_into","decode_stream_into_generic")):
                    try: rva=int(symbol["rva"],16)
                    except ValueError: continue
                    if rva > 0 and rva not in candidates: candidates.append(rva)
            result[label]["symbolized_hot_functions"] = [
                analyze_function(pe,rva,2600) for rva in candidates[:15]]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("DISASM_OVERVIEW",json.dumps({
        name: {"exports":r["exports_relevant"][:4],
               "functions":[{"rva":f["requested_rva"],"size":f["instructions_analyzed"],
                            "classes":f.get("instruction_categories")} for f in r["functions"]]}
        for name,r in result.items() if name in ("oodle23","rust")
    }))
    print("PDB_SYM_SUMMARY",json.dumps({
        k:v for k,v in result["rust"]["debug_symbols"].items()
        if k not in ("matching_symbols",)}))
    print("RUST_HOT_SYMBOL_NAMES",json.dumps(result["rust"]["debug_symbols"].get("matching_symbols",[])[:22]))
    print("STATIC_DISASM_REPORT",str(args.out))
if __name__=="__main__":
    main()
