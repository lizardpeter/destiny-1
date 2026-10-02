# D1ExportFunctionOffsets.py
#@category Destiny
#@menupath Destiny.Export Function Offsets
#
# Decompile explicit exact-build image offsets plus an optional call-neighborhood.
#
# Usage:
#   -postScript D1ExportFunctionOffsets.py <out.json> <depth> <offset> [offset...]

import json
import os

from ghidra.app.decompiler import DecompInterface

args = getScriptArgs()
if len(args) < 3:
    printerr("usage: D1ExportFunctionOffsets.py <out.json> <depth> <offset> [offset...]")
    raise SystemExit(2)

out_path = args[0]
depth = int(args[1], 0)
requested = [int(value, 0) for value in args[2:]]

program = currentProgram
fm = program.getFunctionManager()
listing = program.getListing()
image_base = program.getImageBase()


def image_offset(address):
    try:
        return int(address.subtract(image_base))
    except Exception:
        return None


def function_at_offset(offset):
    address = image_base.add(offset)
    function = fm.getFunctionAt(address)
    if function is None:
        function = fm.getFunctionContaining(address)
    return function


selected = {}
frontier = []
for offset in requested:
    function = function_at_offset(offset)
    if function is None:
        frontier.append({"requested_offset": offset, "status": "NO_FUNCTION"})
        continue
    entry = str(function.getEntryPoint())
    selected[entry] = function
    frontier.append({
        "requested_offset": offset,
        "resolved_entry": image_offset(function.getEntryPoint()),
        "name": str(function.getName()),
        "status": "FOUND",
    })

# Add bounded callers/callees. This lets a dispatcher branch be interpreted in
# context without exploding into the whole executable.
wave = list(selected.values())
seen = set(selected)
for distance in range(depth):
    nxt = []
    for function in wave:
        neighbors = []
        try:
            neighbors.extend(list(function.getCalledFunctions(monitor)))
        except Exception:
            pass
        try:
            neighbors.extend(list(function.getCallingFunctions(monitor)))
        except Exception:
            pass
        for neighbor in neighbors:
            key = str(neighbor.getEntryPoint())
            if key in seen:
                continue
            seen.add(key)
            selected[key] = neighbor
            nxt.append(neighbor)
    wave = nxt

decompiler = DecompInterface()
decompiler.toggleCCode(True)
decompiler.toggleSyntaxTree(True)
decompiler.setSimplificationStyle("decompile")
if not decompiler.openProgram(program):
    printerr("failed to initialize Ghidra decompiler")
    raise SystemExit(2)

records = []
for function in sorted(selected.values(), key=lambda f: image_offset(f.getEntryPoint()) or 0):
    instructions = []
    iterator = listing.getInstructions(function.getBody(), True)
    while iterator.hasNext():
        ins = iterator.next()
        refs = []
        for ref in ins.getReferencesFrom():
            target = ref.getToAddress()
            owner = fm.getFunctionContaining(target) if target is not None else None
            refs.append({
                "type": str(ref.getReferenceType()),
                "target": str(target) if target is not None else None,
                "target_image_offset": image_offset(target) if target is not None else None,
                "target_function_entry": (
                    image_offset(owner.getEntryPoint()) if owner is not None else None
                ),
                "target_function_name": str(owner.getName()) if owner is not None else None,
                "is_call": bool(ref.getReferenceType().isCall()),
                "is_data": bool(ref.getReferenceType().isData()),
            })
        operands = []
        for i in range(ins.getNumOperands()):
            try:
                operands.append(str(ins.getDefaultOperandRepresentation(i)))
            except Exception:
                operands.append(None)
        instructions.append({
            "address": str(ins.getAddress()),
            "image_offset": image_offset(ins.getAddress()),
            "mnemonic": str(ins.getMnemonicString()),
            "operands": operands,
            "references": refs,
        })

    dec = {"completed": False, "error": None, "c": None}
    try:
        result = decompiler.decompileFunction(function, 90, monitor)
        dec["completed"] = bool(result.decompileCompleted())
        if result.decompileCompleted():
            value = result.getDecompiledFunction()
            if value is not None:
                dec["c"] = str(value.getC())
        else:
            dec["error"] = str(result.getErrorMessage())
    except Exception as exc:
        dec["error"] = str(exc)

    records.append({
        "entry": str(function.getEntryPoint()),
        "image_offset": image_offset(function.getEntryPoint()),
        "name": str(function.getName()),
        "prototype": str(function.getPrototypeString(False, True)),
        "instruction_count": len(instructions),
        "instructions": instructions,
        "decompilation": dec,
    })

report = {
    "schema": "d1_ghidra_explicit_offsets/v1",
    "program": {
        "name": str(program.getName()),
        "executable_sha256": str(program.getExecutableSHA256()).lower(),
        "image_base": str(image_base),
    },
    "requested_offsets": requested,
    "call_depth": depth,
    "frontier": frontier,
    "function_count": len(records),
    "functions": records,
}

parent = os.path.dirname(out_path)
if parent and not os.path.isdir(parent):
    os.makedirs(parent)
with open(out_path, "wb") as fh:
    encoded = json.dumps(report, indent=2, sort_keys=True)
    if not isinstance(encoded, bytes):
        encoded = encoded.encode("utf-8")
    fh.write(encoded)
    fh.write(b"\n")

print("D1 explicit-offset export:", out_path)
print("requested=%d functions=%d" % (len(requested), len(records)))
