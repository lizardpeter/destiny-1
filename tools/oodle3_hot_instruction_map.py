#!/usr/bin/env python3
"""Attach exact x64 instructions to sampled CPU addresses from one ETW run.

IMPORTANT: Must use the *same DLL bytes* used for ETW sampling. The code and
PDB layout can differ across runners even when source code is unchanged.
"""
import argparse
import collections
import json
from pathlib import Path

import pefile
from capstone import Cs,CS_ARCH_X86,CS_MODE_64

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--dll",type=Path,required=True)
    p.add_argument("--summary",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    summary=json.loads(args.summary.read_text())
    pe=pefile.PE(str(args.dll))
    image_base=None
    for text in summary.get("image_load_candidates",[]):
        parts=[x.strip() for x in text.split(",")]
        if parts[0] in ("ImageId","I-Start") and args.dll.name.lower() in text.lower():
            try: image_base=int(parts[3],16)
            except (IndexError,ValueError): continue
            break
    if image_base is None:
        raise RuntimeError("No ASLR image load base in same-run ETW trace")
    exceptions=[(int(f.struct.BeginAddress),int(f.struct.EndAddress))
                for f in pe.DIRECTORY_ENTRY_EXCEPTION]
    dis=Cs(CS_ARCH_X86,CS_MODE_64)
    mapped={}
    cache={}
    def decode_pc(rva):
        if rva in mapped:return mapped[rva]
        bound=next(((a,b) for a,b in exceptions if a<=rva<b),None)
        if not bound:
            return {"rva":hex(rva),"reason":"No PE unwind function"}
        if bound not in cache:
            start,end=bound
            instructions={}
            for ins in dis.disasm(pe.get_data(start,end-start),start):
                instructions[ins.address]=ins
            cache[bound]=instructions
        ins=cache[bound].get(rva)
        if ins is None:
            return {"rva":hex(rva),"pdata_start":hex(bound[0]),
                    "pdata_end":hex(bound[1]),"reason":"No exact instruction boundary"}
        return {"rva":hex(rva),"pdata_start":hex(bound[0]),
                "pdata_end":hex(bound[1]),"mnemonic":ins.mnemonic,"operands":ins.op_str}
    top=[]
    tally=collections.Counter()
    for entry in summary.get("top_instruction_pcs",[]):
        ip=int(entry["address"],16)
        rva=ip-image_base
        instr=decode_pc(rva)
        weight=entry["weight"]
        if "mnemonic" in instr:tally[instr["mnemonic"]]+=weight
        top.append({**instr,"samples":weight,
                    "fraction":entry["fraction"]})
    buckets=[]
    for item in summary["top_64_byte_buckets"][:9]:
        start=int(item["start_va"],16)-image_base
        # For each hot bin, map the exact sampled IPs in its 64-byte span
        # and display disassembled instructions on boundaries.
        bound=next(((a,b) for a,b in exceptions if a<=start<b),None)
        if not bound:continue
        if bound not in cache:decode_pc(start)
        instructions=cache.get(bound,{})
        code=[{"rva":hex(addr),"asm":ins.mnemonic+" "+ins.op_str,
               "samples":next((int(x["weight"]) for x in summary["top_instruction_pcs"]
                   if int(x["address"],16)-image_base==addr),0)}
              for addr,ins in instructions.items() if start<=addr<start+64]
        buckets.append({"start_rva":hex(start),"weight":item["weight"],
                        "fraction":item["fraction"],"pdata_start":hex(bound[0]),
                        "instructions":code[:38]})
    result={"decoder":summary["module"],"binary":args.dll.name,
            "actual_load_base":hex(image_base),
            "total_weight":summary["total_weight"],
            "top_weighted_instructions":top,
            "top_64b_disassembly":buckets,
            "weighted_instruction_mnemonics_among_top_45":tally.most_common()}
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print("INSTRUCTION_LEVEL_HOTSPOTS",json.dumps({
        "module":args.dll.name,
        "total_samples":summary["total_weight"],
        "top_sampled_instructions":top[:13],
        "top_weighted_mnemonics":tally.most_common(14),
        "two_hottest_64B_disassemblies":buckets[:2]},sort_keys=True))
if __name__=="__main__":
    main()
