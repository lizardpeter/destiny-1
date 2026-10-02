#!/usr/bin/env python3
"""Inventory exact D1 RoI terrain pixel TFX programs.

This is evidence-only. It uses the authoritative selected terrain materials,
strips only the independently proven RoI PS resource-assignment prefix
(49/index/47/destination pairs), and inventories the remaining expression
bytecode with the pinned D1 TFX framing.

No renderer support policy is imported from Rust-test and no unknown opcode
semantics are promoted here.
"""
from __future__ import annotations

import argparse, collections, hashlib, json
from pathlib import Path

import d1_tower_map_schema_validate_v5 as v5
from d1_material_decode import parse_material
from d1_tfx_program_inventory import disassemble
from d1_roi_tfx_resource_assignment_prefix_proof import prefix as decode_prefix

NULLS={"00000000","FFFFFFFF"}

def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",type=Path,action="append",required=True)
    ap.add_argument("--runtime",type=Path,required=True)
    ap.add_argument("--terrain-resources",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()

    resources=json.loads(a.terrain_resources.read_text(encoding="utf-8"))
    if resources.get("status")!="D1_WORLD_TERRAIN_PS_RESOURCE_CENSUS_COMPLETE":
        raise SystemExit("terrain PS resource census is not complete")

    selected=sorted({norm(r["material"]) for r in resources["materials"]})
    c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())

    rows=[]
    op_hist=collections.Counter()
    extern_hist=collections.Counter()
    extern_detail=collections.Counter()
    unknown42_targets=collections.Counter()
    output_targets=collections.Counter()
    prefix_pairs=collections.Counter()
    unique_programs=collections.defaultdict(list)
    violations=[]

    for mh in selected:
        meta=c.entry_meta(mh)
        payload,src=c.payload(mh)
        row={"material":mh,"source":src}
        if meta is None or payload is None:
            row["status"]="MISSING"
            violations.append({"material":mh,"error":"material unavailable in recovered snapshots"})
            rows.append(row);continue
        try:
            mat=parse_material(payload,"PS4")
        except Exception as ex:
            row["status"]="DECODE_ERROR";row["error"]=repr(ex)
            violations.append({"material":mh,"error":repr(ex)})
            rows.append(row);continue

        raw=bytes.fromhex(mat["ps_tfx_bytecode"]["bytes_hex"])
        pairs,tail_offset=decode_prefix(raw)
        tail=raw[tail_offset:]
        private=[x.get("value") for x in mat["ps_tfx_bytecode_constants"].get("items",[])]
        cb=[x.get("value") for x in mat["ps_cbuffers"].get("items",[])]
        decoded=disassemble(tail,private,cb)
        if not decoded["complete"]:
            violations.append({
                "material":mh,
                "error":"post-prefix TFX disassembly incomplete",
                "unknown":decoded.get("unknown_opcodes"),
                "truncated":decoded.get("truncated"),
            })

        sha=hashlib.sha256(tail).hexdigest()
        unique_programs[sha].append(mh)
        for p in pairs:
            prefix_pairs[(int(p.get("source_index",p.get("sampler_index",0))),int(p.get("destination",0)))] += 1
        for op in decoded["ops"]:
            op_hist[op["name"]]+=1
            if "extern_name" in op:
                extern_hist[op["extern_name"]]+=1
                extern_detail[(
                    op["extern_name"],
                    int(op.get("extern_element",0)),
                    op["name"],
                    op.get("extern_byte_offset_hex"),
                )]+=1
            if op["name"]=="Unk42" and op.get("operand_bytes"):
                unknown42_targets[int(op["operand_bytes"][0])]+=1
            if op["name"] in ("PopOutput","PopOutputMat4") and op.get("operand_bytes"):
                output_targets[(op["name"],int(op["operand_bytes"][0]))]+=1

        row.update({
            "status":"D1_TERRAIN_PIXEL_TFX_EXACTLY_FRAMED" if decoded["complete"] else "PARTIAL",
            "pixel_shader":norm(mat["pixel_shader"]),
            "raw_bytecode_bytes":len(raw),
            "resource_prefix_pair_count":len(pairs),
            "resource_prefix_bytes":tail_offset,
            "resource_prefix_pairs":pairs,
            "expression_bytes":len(tail),
            "expression_sha256":sha,
            "private_constant_count":len(private),
            "initial_ps_cbuffer_count":len(cb),
            "expression":decoded,
        })
        rows.append(row)

    program_groups=[
        {"expression_sha256":sha,"material_count":len(mats),"materials":sorted(mats)}
        for sha,mats in sorted(unique_programs.items())
    ]
    empty=sum(r.get("expression_bytes")==0 for r in rows)
    extern_materials=sum(any("extern_name" in op for op in r.get("expression",{}).get("ops",[])) for r in rows)
    unk42_materials=sum(any(op.get("name")=="Unk42" for op in r.get("expression",{}).get("ops",[])) for r in rows)

    out={
        "schema_version":1,
        "status":"D1_TERRAIN_PIXEL_TFX_CENSUS_COMPLETE" if not violations else "D1_TERRAIN_PIXEL_TFX_CENSUS_PARTIAL",
        "selected_material_count":len(selected),
        "framed_material_count":sum(r.get("status")=="D1_TERRAIN_PIXEL_TFX_EXACTLY_FRAMED" for r in rows),
        "empty_expression_material_count":empty,
        "live_extern_material_count":extern_materials,
        "unk42_material_count":unk42_materials,
        "unique_expression_count":len(program_groups),
        "opcode_histogram":dict(sorted(op_hist.items())),
        "extern_histogram":dict(sorted(extern_hist.items())),
        "extern_request_histogram":{
            f"{name}[0x{element:02X}] {kind}{' '+str(off) if off else ''}":count
            for (name,element,kind,off),count in sorted(extern_detail.items())
        },
        "unknown42_target_histogram":{str(k):v for k,v in sorted(unknown42_targets.items())},
        "output_target_histogram":{f"{name}:{slot}":v for (name,slot),v in sorted(output_targets.items())},
        "resource_prefix_pair_histogram":{f"{src}->{dst}":v for (src,dst),v in sorted(prefix_pairs.items())},
        "program_groups":program_groups,
        "materials":rows,
        "violations":violations,
        "proof_boundary":(
            "Exact selected SMaterial_ROI pixel TFX bytes after stripping only the independently "
            "proven 49/index/47/destination resource-assignment prefix. This report inventories "
            "framing, opcodes, typed extern requests and output targets; it does not assert "
            "renderer support or assign semantics to unresolved operations."
        ),
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:out[k] for k in (
        "status","selected_material_count","framed_material_count",
        "empty_expression_material_count","live_extern_material_count",
        "unk42_material_count","unique_expression_count","opcode_histogram",
        "extern_histogram","extern_request_histogram","unknown42_target_histogram",
        "output_target_histogram","violations"
    )},indent=2))
    return 0 if not violations else 2

if __name__=="__main__":
    raise SystemExit(main())
