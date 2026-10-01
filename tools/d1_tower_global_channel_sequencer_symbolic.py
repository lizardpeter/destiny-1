#!/usr/bin/env python3
"""Symbolically decode exact D1 RoI global-channel sequencer programs.

Input is the exact StringHash-joined Tower/global-channel report produced by
d1_tower_global_channel_join.py.  The decoder follows the D1-specific
RoI opcode revision and the sequencer framing behavior documented by the
strategy-aware Charm lineage, but it promotes no runtime semantic names.

Important sequencer-specific framing:
  * raw 0x3C (D1 PushExternInputFloat) has ONE operand byte in sequencer mode;
  * raw 0x3E (D1 PushExternInputMat4) is treated as a one-byte PopOutput in
    sequencer mode by the lineage parser.

The report is symbolic evidence only.  "SequencerScalar[k]" is an unresolved
runtime scalar input, not a claimed unit such as seconds.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUESTED = {0x11, 0x28, 0x30, 0x60}

# Raw D1 RoI opcode table.  Names are strategy-specific lineage labels; current
# retail behavior is promoted only where independently corroborated.
NAMES = {
    0x01:"Add",0x02:"Subtract",0x03:"Multiply",0x04:"Divide",
    0x05:"Multiply2",0x06:"Add2",0x07:"IsZero",0x08:"Min",0x09:"Max",
    0x0A:"LessThan",0x0B:"Dot",0x0C:"Merge_1_3",0x0D:"Merge_2_2",
    0x0E:"Merge_3_1",0x0F:"Cubic",0x10:"Lerp",0x11:"LerpSaturated",
    0x12:"MultiplyAdd",0x13:"Clamp",0x14:"Unk14",0x15:"Abs",0x16:"Sign",
    0x17:"Floor",0x18:"Ceil",0x19:"Round",0x1A:"Frac",0x1B:"Unk1b",
    0x1C:"Unk1c",0x1D:"Negate",0x1E:"VecRotSin",0x1F:"VecRotCos",
    0x20:"VecRotSinCos",0x21:"PermuteAllX",0x22:"Permute",0x23:"Saturate",
    0x25:"Unk25",0x26:"Unk26",0x27:"Triangle",0x28:"Jitter",
    0x29:"Wander",0x2A:"Rand",0x2B:"RandSmooth",0x2C:"Unk2c",
    0x2D:"Unk2d",0x2E:"TransformVec4",0x34:"PushConstantVec4",
    0x35:"LerpConstant",0x36:"LerpConstantSaturated",0x37:"Spline4Const",
    0x38:"Spline8Const",0x39:"Spline8ConstChain",0x3A:"Gradient4Const",
    0x3B:"Gradient8Const",0x3C:"PushExternInputFloat",
    0x3D:"PushExternInputVec4",0x3E:"PushExternInputMat4",
    0x3F:"PushExternInputTextureView",0x40:"PushExternInputU32",
    0x41:"PushFromOutput",0x42:"PopOutput",0x43:"PopOutputMat4",
    0x44:"PushTemp",0x45:"PopTemp",0x46:"SetShaderTexture",
    0x47:"SetShaderSampler",0x49:"PushSampler",0x4A:"PushObjectChannelVector",
    0x4B:"PushGlobalChannelVector",0x4E:"Unk50",
    0x50:"PushTexDimensions",0x51:"PushTexTileParams",0x52:"PushTexTileCount",
}

ONE = {0x22,0x34,0x35,0x36,0x37,0x38,0x39,0x3A,0x3B,0x41,0x42,0x43,
       0x44,0x45,0x46,0x47,0x49,0x4A,0x4B,0x4E}
TWO = {0x3D,0x3F,0x40,0x50,0x51,0x52}
ZERO = set(range(0x01,0x2F)) - {0x22,0x24}
ZERO |= {0x15,0x16,0x17,0x18,0x19,0x1A,0x1B,0x1C,0x1D,0x1E,0x1F,0x20,
         0x21,0x23,0x25,0x26,0x27,0x28,0x29,0x2A,0x2B,0x2C,0x2D,0x2E}

def parse(bytecode: bytes) -> list[dict]:
    out=[]; pc=0
    while pc < len(bytecode):
        at=pc; op=bytecode[pc]; pc+=1
        # Sequencer-specific D1 framing from lineage parser.
        if op == 0x3C:
            n=1
        elif op == 0x3E:
            n=1
        elif op in ONE:
            n=1
        elif op in TWO:
            n=2
        elif op in ZERO:
            n=0
        else:
            out.append({"offset":at,"opcode":f"0x{op:02X}","name":NAMES.get(op,"Unknown"),
                        "status":"UNFRAMED_UNKNOWN","operand_hex":""})
            break
        if pc+n > len(bytecode):
            out.append({"offset":at,"opcode":f"0x{op:02X}","name":NAMES.get(op,"Unknown"),
                        "status":"TRUNCATED","operand_hex":bytecode[pc:].hex().upper()})
            break
        args=bytecode[pc:pc+n]; pc+=n
        name = "SequencerPopOutput" if op == 0x3E else NAMES.get(op,"Unknown")
        out.append({"offset":at,"opcode":f"0x{op:02X}","name":name,
                    "status":"FRAMED","operand_hex":args.hex().upper(),
                    "operands":list(args)})
    return out

def pop(stack:list[str], blockers:list[str], label:str, at:int) -> str:
    if not stack:
        blockers.append(f"stack_underflow:{label}@0x{at:X}")
        return f"<UNDERFLOW:{label}@0x{at:X}>"
    return stack.pop()

def unary(stack, blockers, label, at, fmt):
    a=pop(stack,blockers,label,at); stack.append(fmt(a))

def binary(stack, blockers, label, at, fmt):
    b=pop(stack,blockers,label,at); a=pop(stack,blockers,label,at); stack.append(fmt(a,b))

def ternary(stack, blockers, label, at, fmt):
    c=pop(stack,blockers,label,at); b=pop(stack,blockers,label,at); a=pop(stack,blockers,label,at)
    stack.append(fmt(a,b,c))

def symbolic(ops:list[dict], constants:list[list[float]]) -> dict:
    stack=[]; temps={}; outputs={}; blockers=[]; deps=set()
    for row in ops:
        at=row["offset"]
        if row["status"]!="FRAMED":
            blockers.append(f"{row['status']}:{row['opcode']}@0x{at:X}"); continue
        op=int(row["opcode"],16); args=row.get("operands",[])
        if op==0x34:
            i=args[0]
            if i>=len(constants): blockers.append(f"constant_oob:{i}@0x{at:X}"); stack.append(f"C[{i}]")
            else: stack.append(f"C[{i}]={constants[i]}")
        elif op==0x3C:
            i=args[0]; deps.add(f"SequencerScalar[{i}]"); stack.append(f"SequencerScalar[{i}]")
        elif op==0x3E:  # lineage sequencer special case
            slot=args[0]; outputs[slot]=pop(stack,blockers,"SequencerPopOutput",at); stack.clear()
        elif op==0x41:
            slot=args[0]
            if slot not in outputs: blockers.append(f"output_read_before_write:{slot}@0x{at:X}")
            stack.append(outputs.get(slot,f"Output[{slot}]"))
        elif op==0x44:
            slot=args[0]
            if slot not in temps: blockers.append(f"temp_read_before_write:{slot}@0x{at:X}")
            stack.append(temps.get(slot,f"Temp[{slot}]"))
        elif op==0x45:
            temps[args[0]]=pop(stack,blockers,"PopTemp",at)
        elif op==0x4B:
            i=args[0]; deps.add(f"GlobalChannel[{i}]"); stack.append(f"GlobalChannel[{i}]")
        elif op==0x01: binary(stack,blockers,"Add",at,lambda a,b:f"({a}+{b})")
        elif op==0x02: binary(stack,blockers,"Subtract",at,lambda a,b:f"({a}-{b})")
        elif op==0x03: binary(stack,blockers,"Multiply",at,lambda a,b:f"({a}*{b})")
        elif op==0x04: binary(stack,blockers,"Divide",at,lambda a,b:f"({a}/{b})")
        elif op==0x08: binary(stack,blockers,"Min",at,lambda a,b:f"min({a},{b})")
        elif op==0x09: binary(stack,blockers,"Max",at,lambda a,b:f"max({a},{b})")
        elif op==0x0A: binary(stack,blockers,"LessThan",at,lambda a,b:f"less_than({a},{b})")
        elif op==0x0B: binary(stack,blockers,"Dot",at,lambda a,b:f"dot4({a},{b})")
        elif op==0x0E: binary(stack,blockers,"Merge_3_1",at,lambda a,b:f"merge3_1({a},{b})")
        elif op==0x10: ternary(stack,blockers,"Lerp",at,lambda a,b,t:f"lerp({a},{b},{t})")
        elif op==0x11: ternary(stack,blockers,"LerpSaturated",at,lambda a,b,t:f"saturate(lerp({a},{b},{t}))")
        elif op==0x12: ternary(stack,blockers,"MultiplyAdd",at,lambda a,b,c:f"(({a}*{b})+{c})")
        elif op==0x15: unary(stack,blockers,"Abs",at,lambda a:f"abs({a})")
        elif op==0x16: unary(stack,blockers,"Sign",at,lambda a:f"sign({a})")
        elif op==0x17: unary(stack,blockers,"Floor",at,lambda a:f"floor({a})")
        elif op==0x18: unary(stack,blockers,"Ceil",at,lambda a:f"ceil({a})")
        elif op==0x19: unary(stack,blockers,"Round",at,lambda a:f"round({a})")
        elif op==0x1A: unary(stack,blockers,"Frac",at,lambda a:f"frac({a})")
        elif op==0x1D: unary(stack,blockers,"Negate",at,lambda a:f"(-{a})")
        elif op==0x1F: unary(stack,blockers,"VecRotCos",at,lambda a:f"vec_rot_cos({a})")
        elif op==0x21: unary(stack,blockers,"PermuteAllX",at,lambda a:f"splat_x({a})")
        elif op==0x22:
            p=args[0]; unary(stack,blockers,"Permute",at,lambda a:f"permute({a},0x{p:02X})")
        elif op==0x23: unary(stack,blockers,"Saturate",at,lambda a:f"saturate({a})")
        elif op==0x27: unary(stack,blockers,"Triangle",at,lambda a:f"triangle({a})")
        elif op==0x28: unary(stack,blockers,"Jitter",at,lambda a:f"jitter({a})")
        elif op==0x29: unary(stack,blockers,"Wander",at,lambda a:f"wander({a})")
        elif op==0x2A: unary(stack,blockers,"Rand",at,lambda a:f"rand({a})")
        elif op in (0x35,0x36):
            i=args[0]; t=pop(stack,blockers,row["name"],at)
            sat="saturate(" if op==0x36 else ""; close=")" if op==0x36 else ""
            stack.append(f"{sat}lerp(C[{i}],C[{i+1}],{t}){close}")
        else:
            blockers.append(f"unsupported_symbolic:{row['opcode']}:{row['name']}@0x{at:X}")
            # Fail closed: stop carrying an unproved stack shape past this point.
            stack.append(f"<{row['name']}@0x{at:X}>")
    return {
        "dependencies":sorted(deps),
        "outputs":{str(k):v for k,v in sorted(outputs.items())},
        "final_stack":stack,
        "temp_slots":{str(k):v for k,v in sorted(temps.items())},
        "blockers":blockers,
        "fully_symbolically_closed":not blockers,
    }

def iter_requested(doc:dict):
    seen=set()
    for global_hex, programs in doc.get("requested_global_programs",{}).items():
        for p in programs:
            key=(p.get("resource_hash"),p.get("global_index"),p.get("bytecode_sha256"))
            if key in seen:
                continue
            seen.add(key)
            yield p

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--join",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    src=json.loads(a.join.read_text())
    rows=[]
    for p in iter_requested(src):
        resource_hash=p.get("resource_hash")
        idx=int(p["global_index"])
        bytecode=bytes.fromhex(p["bytecode_hex"])
        constants=p.get("constant_vec4s",[])
        ops=parse(bytecode)
        sym=symbolic(ops,constants)
        rows.append({
            "resource_hash":resource_hash,
            "global_index":idx,
            "global_index_hex":f"0x{idx:02X}",
            "local_channel_index":p.get("local_channel_index"),
            "local_channel_index_hex":p.get("local_channel_index_hex"),
            "channel_id_string_hash":p.get("channel_id_string_hash"),
            "global_default_vec4":p.get("global_default_vec4"),
            "bytecode_hex":p["bytecode_hex"],
            "bytecode_sha256":p.get("bytecode_sha256"),
            "constant_vec4s":constants,
            "lineage_dynamic_rule":p.get("is_dynamic_lineage_rule"),
            "ops":ops,
            "symbolic":sym,
        })
    by_index={}
    for r in rows:
        by_index.setdefault(r["global_index_hex"],[]).append(r)
    missing=[f"0x{x:02X}" for x in sorted(REQUESTED) if f"0x{x:02X}" not in by_index]
    out={
        "schema":"d1_tower_global_channel_sequencer_symbolic/v2",
        "status":"D1_TOWER_CHANNEL_SEQUENCER_SYMBOLIC_COMPLETE" if not missing else "D1_TOWER_CHANNEL_SEQUENCER_SYMBOLIC_PARTIAL",
        "requested_indices":[f"0x{x:02X}" for x in sorted(REQUESTED)],
        "missing_requested_indices":missing,
        "program_count":len(rows),
        "programs_by_index":by_index,
        "fully_symbolically_closed_program_count":sum(r["symbolic"]["fully_symbolically_closed"] for r in rows),
        "proof_boundary":(
            "Raw current-retail bytecode/constants and the local-ID to global-index "
            "StringHash join are exact evidence. Opcode names/framing use "
            "the D1 RoI strategy-aware lineage and sequencer special cases. Symbolic formulas "
            "promote stack/data dependencies only where the implemented operation is already "
            "corroborated by D1 material work. SequencerScalar indices retain raw identity; "
            "no seconds/ticks/phase unit is assigned here."
        ),
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({
        "status":out["status"],"program_count":len(rows),
        "indices":{k:len(v) for k,v in by_index.items()},
        "fully_symbolically_closed_program_count":out["fully_symbolically_closed_program_count"],
        "missing":missing,
    },indent=2))
    return 0 if not missing else 2

if __name__=="__main__":
    raise SystemExit(main())
