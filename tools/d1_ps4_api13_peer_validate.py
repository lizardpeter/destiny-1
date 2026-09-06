#!/usr/bin/env python3
"""Validate the independent PS4 api13[6:7] peer shader 80CA0BE9.

The target is deliberately narrow and source preserving.  It checks the exact
CLRX/GFX700 instruction sequence already extracted from retail PS4 shader
80CA0BE9 and proves only this arithmetic statement:

    api13[6] * api13[7]

multiplies the RGB lanes immediately before MRT0 packing, while the separately
carried alpha lane is not multiplied by either api13 scalar.

No engine name or live runtime value is assigned to api13 by this validator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SHADER = "80CA0BE9"
GCN_SHA256 = "86282025ea6bbe21ca42153702d14fbf443b5f2d605cf96f5f15d11663170b70"

LOAD = r"s_buffer_load_dwordx2\s+s\[10:11\],\s*s\[12:15\],\s*0x6"
ALPHA_LOCAL = r"v_mul_f32\s+v1,\s*s3,\s*v0"
API7 = r"v_mul_f32\s+v7,\s*s11,\s*v1"
PRODUCT = r"v_mul_f32\s+v2,\s*s10,\s*v7"
RGB_AFTER_PRODUCT = [
    r"v_mul_f32\s+v3,\s*v3,\s*v2",
    r"v_mul_f32\s+v4,\s*v4,\s*v2",
    r"v_mul_f32\s+v0,\s*v0,\s*v2",
]
PACK_RG = r"v_cvt_pkrtz_f16_f32\s+v2,\s*v3,\s*v4"
PACK_BA = r"v_cvt_pkrtz_f16_f32\s+v0,\s*v0,\s*v1"
EXPORT = r"exp\s+mrt0,\s*v2,\s*v2,\s*v0,\s*v0\s+done\s+compr\s+vm"


def code_bytes_from_clrx(text: str) -> bytes:
    """Reconstruct the raw GCN bytes from CLRX hex comments in address order."""
    rows=[]
    for line in text.splitlines():
        m=re.match(r"/\*([0-9A-Fa-f]{12}):\s*([0-9A-Fa-f ]+)\*/",line.strip())
        if not m:
            continue
        addr=int(m.group(1),16)
        words=m.group(2).split()
        raw=b"".join(bytes.fromhex(w)[::-1] for w in words)
        rows.append((addr,raw))
    if not rows:
        raise ValueError("no CLRX hexcode rows")
    rows.sort()
    out=bytearray()
    if rows[0][0]!=0:
        raise ValueError(f"first GCN address is {rows[0][0]:#x}, expected 0")
    for addr,raw in rows:
        if addr!=len(out):
            raise ValueError(f"non-contiguous CLRX code at {addr:#x}, expected {len(out):#x}")
        out.extend(raw)
    return bytes(out)


def must(pattern:str,text:str,label:str,violations:list[str],start:int=0):
    m=re.search(pattern,text[start:],re.I)
    if not m:
        violations.append(f"missing {label}: {pattern}")
        return None
    # Convert substring-relative positions back to the full text.
    return (start+m.start(), start+m.end())


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--disasm",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    text=a.disasm.read_text(errors="replace")
    code=code_bytes_from_clrx(text)
    sha=hashlib.sha256(code).hexdigest()
    violations=[]
    if sha!=GCN_SHA256:
        violations.append(f"GCN sha256 {sha} != {GCN_SHA256}")

    load=must(LOAD,text,"api13 dwordx2 load",violations)
    cursor=load[1] if load else 0
    alpha=must(ALPHA_LOCAL,text,"separate alpha/local lane construction",violations,cursor)
    cursor=alpha[1] if alpha else cursor
    api7=must(API7,text,"api13[7] multiply",violations,cursor)
    cursor=api7[1] if api7 else cursor
    product=must(PRODUCT,text,"api13[6]*api13[7] product",violations,cursor)
    cursor=product[1] if product else cursor

    rgb_hits=[]
    for i,pat in enumerate(RGB_AFTER_PRODUCT):
        hit=must(pat,text,f"RGB lane {i} api13 product multiply",violations,cursor)
        if hit:
            rgb_hits.append(hit)
            cursor=hit[1]
    pack_rg=must(PACK_RG,text,"RG pack",violations,cursor)
    cursor=pack_rg[1] if pack_rg else cursor
    pack_ba=must(PACK_BA,text,"BA pack with untouched alpha lane v1",violations,cursor)
    cursor=pack_ba[1] if pack_ba else cursor
    export=must(EXPORT,text,"MRT0 compressed export",violations,cursor)

    # Alpha is v1 at PACK_BA. Between the api13 load and BA packing, allow v1 to
    # be read as an input (s11*v1) but reject any api13-dependent write to v1.
    if load and pack_ba:
        bounded=text[load[0]:pack_ba[0]]
        for line in bounded.splitlines():
            if re.search(r"v_mul_f32\s+v1,\s*s1[01]\b",line,re.I):
                violations.append(f"api13 unexpectedly writes alpha lane v1: {line.strip()}")

    out={
        "schema_version":2,
        "status":"D1_PS4_API13_PEER_80CA0BE9_VALIDATED" if not violations else "D1_PS4_API13_PEER_80CA0BE9_FAILED",
        "shader":SHADER,
        "gcn_bytes":len(code),
        "gcn_sha256":sha,
        "api13_descriptor_registers":"s[12:15]",
        "api13_load":{"start_dword":6,"width_dwords":2,"destinations":{"dword6":"s10","dword7":"s11"}},
        "proven_arithmetic":"rgb *= api13[6] * api13[7]; alpha lane v1 is packed separately and is not multiplied by api13[6] or api13[7]",
        "producer_name_resolved":False,
        "runtime_values_resolved":False,
        "violations":violations,
        "policy":"Exact PS4 retail GCN arithmetic only; no producer/name/value semantic inferred.",
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
    return 0 if not violations else 2

if __name__=="__main__": raise SystemExit(main())
