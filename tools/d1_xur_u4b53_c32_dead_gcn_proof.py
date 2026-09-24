#!/usr/bin/env python3
"""Prove the Xur-visible U4B[53] -> PS CBuffer c32 stores are dead to native GCN.

Inputs are independently pinned:
- the green visible-PS symbolic TFX contract, which proves U4B[53] writes only
  target Vec4 slot 32 for the scoped Xur materials;
- exact native GCN disassemblies for PS 8087630D, 809D836C and 809D8370.

D1 material CBuffer Vec4 slot 32 occupies byte range 0x200..0x20F.  This proof
enumerates every scalar buffer load in each native shader, expands its byte range,
and fails closed if any load overlaps c32 or if an unparsed s_buffer_load exists.

It does not rename opcode 0x4B.  It proves only that its remaining Xur-visible
PS writes cannot affect these native shaders because the written slot is unread.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path

TARGET_SLOT=32
TARGET_START=TARGET_SLOT*16
TARGET_END=TARGET_START+15
SHADERS=("8087630D","809D836C","809D8370")
EXPECTED_TFX_ROWS={
    ("80876CAE","8087630D",32,"U4B[53]"),
    ("80C8822E","809D836C",32,"U4B[53]"),
    ("80C8822F","809D8370",32,"U4B[53]"),
    ("80C888C9","809D836C",32,"U4B[53]"),
}
LOAD_RE=re.compile(
    r"\bs_buffer_load_(dword|dwordx2|dwordx4)\b[^\n]*?\b(0x[0-9a-fA-F]+|\d+)\s*$"
)
ANY_LOAD_RE=re.compile(r"\bs_buffer_load_[A-Za-z0-9_]+\b")

def width(kind:str)->int:
    return {"dword":4,"dwordx2":8,"dwordx4":16}[kind]

def parse_shader(path:Path,shader:str)->dict:
    text=path.read_text()
    rows=[];unparsed=[]
    for line_no,line in enumerate(text.splitlines(),1):
        if not ANY_LOAD_RE.search(line):
            continue
        m=LOAD_RE.search(line)
        if not m:
            unparsed.append({"line":line_no,"text":line.strip()})
            continue
        off=int(m.group(2),0);size=width(m.group(1))
        end=off+size-1
        rows.append({
            "line":line_no,"opcode":"s_buffer_load_"+m.group(1),
            "offset_bytes":off,"size_bytes":size,"end_bytes":end,
            "overlaps_c32":not (end<TARGET_START or off>TARGET_END),
            "text":line.strip(),
        })
    return {
        "shader":shader,
        "disassembly":str(path),
        "disassembly_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
        "scalar_buffer_load_count":len(rows),
        "unparsed_scalar_buffer_load_count":len(unparsed),
        "unparsed_scalar_buffer_loads":unparsed,
        "max_loaded_end_byte":max((x["end_bytes"] for x in rows),default=-1),
        "c32_overlap_count":sum(x["overlaps_c32"] for x in rows),
        "loads":rows,
    }

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--symbolic-contract",type=Path,required=True)
    ap.add_argument("--disasm-dir",type=Path,required=True)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args();viol=[]

    sym=json.loads(a.symbolic_contract.read_text())
    if sym.get("status")!="D1_XUR_VISIBLE_PS_TFX_SYMBOLIC_CONTRACT_EXACT":
        viol.append("symbolic contract not exact")
    rows=sym.get("unresolved_dependency_rows") or []
    u4b=[]
    for r in rows:
        refs=r.get("source_refs") or []
        if "U4B[53]" in refs:
            if len(refs)!=1:
                viol.append(f"{r.get('material')}: U4B row has extra sources {refs!r}")
            u4b.append((str(r.get("material")),str(r.get("pixel_shader")),int(r.get("target")),"U4B[53]"))
    if set(u4b)!=EXPECTED_TFX_ROWS:
        viol.append(f"U4B[53] symbolic row set changed: {sorted(u4b)!r}")
    if any(target!=TARGET_SLOT for _,_,target,_ in u4b):
        viol.append("U4B[53] writes a target other than c32")
    other_u4b=[
        r for r in rows
        if any(str(x).startswith("U4B[") for x in (r.get("source_refs") or []))
        and "U4B[53]" not in (r.get("source_refs") or [])
    ]
    if other_u4b:
        viol.append(f"other unresolved U4B producers entered visible PS scope: {other_u4b!r}")

    shader_rows=[]
    for sh in SHADERS:
        p=a.disasm_dir/f"PS_{sh}.s"
        if not p.is_file():
            viol.append(f"{sh}: disassembly missing")
            continue
        q=parse_shader(p,sh);shader_rows.append(q)
        if q["unparsed_scalar_buffer_load_count"]:
            viol.append(f"{sh}: unparsed scalar buffer loads")
        if not q["scalar_buffer_load_count"]:
            viol.append(f"{sh}: no scalar buffer loads parsed")
        if q["c32_overlap_count"]:
            viol.append(f"{sh}: native load overlaps c32")
        if q["max_loaded_end_byte"]>=TARGET_START:
            # This is stricter than overlap and catches future high-offset loads.
            viol.append(f"{sh}: native scalar-buffer load reaches >= c32 start: {q['max_loaded_end_byte']:#x}")

    dead=(
        len(u4b)==4 and len(shader_rows)==3 and
        all(x["unparsed_scalar_buffer_load_count"]==0 for x in shader_rows) and
        all(x["c32_overlap_count"]==0 and x["max_loaded_end_byte"]<TARGET_START for x in shader_rows)
    )
    if not dead:viol.append("U4B[53] c32 dead-write theorem not established")

    out={
        "schema_version":1,
        "status":"D1_XUR_U4B53_C32_NATIVE_PS_DEAD_WRITE_EXACT" if not viol else "D1_XUR_U4B53_C32_NATIVE_PS_DEAD_WRITE_VIOLATIONS",
        "target":{"producer_symbol":"U4B[53]","cbuffer_vec4_slot":TARGET_SLOT,"byte_range":[TARGET_START,TARGET_END]},
        "symbolic_contract":{
            "path":str(a.symbolic_contract),
            "sha256":hashlib.sha256(a.symbolic_contract.read_bytes()).hexdigest(),
            "u4b53_rows":[
                {"material":m,"pixel_shader":sh,"target":t,"source":src}
                for m,sh,t,src in sorted(u4b)
            ],
        },
        "native_shader_rows":shader_rows,
        "proof":{
            "all_visible_U4B53_stores_target_only_c32":len(u4b)==4 and all(x[2]==32 for x in u4b),
            "all_three_native_shaders_have_only_parsed_immediate_scalar_buffer_loads":len(shader_rows)==3 and all(x["unparsed_scalar_buffer_load_count"]==0 for x in shader_rows),
            "no_native_scalar_buffer_load_overlaps_c32":len(shader_rows)==3 and all(x["c32_overlap_count"]==0 for x in shader_rows),
            "all_native_scalar_buffer_loads_end_below_c32":len(shader_rows)==3 and all(x["max_loaded_end_byte"]<TARGET_START for x in shader_rows),
            "U4B53_is_dead_to_scoped_native_pixel_shaders":dead,
            "opcode_0x4B_semantic_identity_proven":False,
        },
        "consequence":"For the current Xur-visible PS scope, exact TFX writes sourced by U4B[53] modify only b0/c32 bytes 0x200..0x20F. Native PS 8087630D, 809D836C and 809D8370 never load that byte range. Therefore U4B[53] cannot alter their native pixel-shader outputs and is removed as a visible-material reconstruction blocker, without assigning a semantic name to opcode 0x4B.",
        "violations":viol,
        "policy":"Dead-write proof only. This does not rename 0x4B, does not prove the runtime value of channel/index 53, and does not generalize beyond the exact scoped TFX rows and native shader binaries.",
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({
        "status":out["status"],
        "target":out["target"],
        "shader_max_loaded_end_bytes":{x["shader"]:x["max_loaded_end_byte"] for x in shader_rows},
        "proof":out["proof"],
        "violations":viol,
    },indent=2))
    return 0 if not viol else 2

if __name__=="__main__":raise SystemExit(main())
