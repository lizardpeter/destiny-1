# SMGExportUnmatchedSlices.py
#@category SuperMarioGalaxy
#
# Decompile a prioritized list of exact RMGE01 function addresses.
# Input JSON schema:
# {"functions":[{"address":"0x80001234","size":123,"name":"fn_..."}]}
#
# Output contains only derived decompiler/disassembly metadata, never raw DOL bytes.

import json

from ghidra.app.decompiler import DecompInterface

args = getScriptArgs()
if len(args) < 2:
    printerr("usage: SMGExportUnmatchedSlices.py <frontier.json> <out.json> [max_functions]")
    raise SystemExit(2)

frontier_path = args[0]
out_path = args[1]
max_functions = int(args[2]) if len(args) > 2 else 128

program = currentProgram
fm = program.getFunctionManager()
listing = program.getListing()

with open(frontier_path, "rb") as fh:
    frontier = json.loads(fh.read().decode("utf-8"))

decompiler = DecompInterface()
decompiler.toggleCCode(True)
decompiler.toggleSyntaxTree(True)
decompiler.setSimplificationStyle("decompile")
if not decompiler.openProgram(program):
    printerr("failed to initialize Ghidra decompiler")
    raise SystemExit(2)

records = []
missing = []

for row in frontier.get("functions", [])[:max_functions]:
    address_text = row.get("address")
    try:
        address = toAddr(address_text)
    except Exception:
        missing.append({"frontier": row, "reason": "invalid address"})
        continue

    function = fm.getFunctionAt(address)
    if function is None:
        try:
            disassemble(address)
        except Exception:
            pass
        function = fm.getFunctionAt(address)
    if function is None:
        try:
            function = createFunction(address, row.get("name"))
        except Exception:
            function = None
    if function is None:
        function = fm.getFunctionContaining(address)
    if function is None:
        missing.append({"frontier": row, "reason": "no function at address"})
        continue

    calls = []
    iterator = listing.getInstructions(function.getBody(), True)
    instruction_count = 0
    mnemonics = {}
    while iterator.hasNext():
        ins = iterator.next()
        instruction_count += 1
        mn = str(ins.getMnemonicString())
        mnemonics[mn] = mnemonics.get(mn, 0) + 1
        for ref in ins.getReferencesFrom():
            if not ref.getReferenceType().isCall():
                continue
            target = ref.getToAddress()
            owner = fm.getFunctionContaining(target) if target is not None else None
            calls.append({
                "from": str(ins.getAddress()),
                "target": str(target) if target is not None else None,
                "target_function": str(owner.getName()) if owner is not None else None,
                "target_entry": str(owner.getEntryPoint()) if owner is not None else None,
            })

    dec = {"completed": False, "error": None, "c": None}
    try:
        result = decompiler.decompileFunction(function, 120, monitor)
        dec["completed"] = bool(result.decompileCompleted())
        if result.decompileCompleted():
            df = result.getDecompiledFunction()
            if df is not None:
                dec["c"] = str(df.getC())
        else:
            dec["error"] = str(result.getErrorMessage())
    except Exception as exc:
        dec["error"] = str(exc)

    records.append({
        "frontier": row,
        "entry": str(function.getEntryPoint()),
        "ghidra_name": str(function.getName()),
        "prototype": str(function.getPrototypeString(False, True)),
        "calling_convention": str(function.getCallingConventionName()),
        "body_address_count": int(function.getBody().getNumAddresses()),
        "instruction_count": instruction_count,
        "mnemonic_counts": mnemonics,
        "calls": calls,
        "decompilation": dec,
    })

report = {
    "schema": "smg_rmge01_ghidra_unmatched_slices/v1",
    "program": {
        "name": str(program.getName()),
        "executable_sha256": str(program.getExecutableSHA256()).lower(),
        "language_id": str(program.getLanguageID()),
        "compiler_spec": str(program.getCompilerSpec().getCompilerSpecID()),
    },
    "requested": min(len(frontier.get("functions", [])), max_functions),
    "exported": len(records),
    "missing": len(missing),
    "functions": records,
    "missing_functions": missing,
}

with open(out_path, "wb") as fh:
    fh.write(json.dumps(report, indent=2, sort_keys=True).encode("utf-8"))
    fh.write(b"\n")

print("SMG RMGE01 decompiler export: %d exported, %d missing" % (len(records), len(missing)))
