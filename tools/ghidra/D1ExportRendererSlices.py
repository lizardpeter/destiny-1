# D1ExportRendererSlices.py
#@category Destiny
#@menupath Destiny.Export Renderer Slices
#
# Focused Ghidra exporter for the ranked D1 renderer frontier.
#
# Usage:
#   -postScript D1ExportRendererSlices.py <frontier.json> <out.json> [max_functions]
#
# The frontier JSON is produced by tools/d1_executable_renderer_frontier.py.
# This script exports only the selected functions: disassembly operands, memory/
# call references, P-code mnemonics and decompiler text. It never embeds the
# original executable bytes.
#
# Python-2-compatible for classic Ghidra Jython.

import json
import os

from ghidra.app.decompiler import DecompInterface
from ghidra.program.model.scalar import Scalar

args = getScriptArgs()
if len(args) < 2:
    printerr(
        "usage: D1ExportRendererSlices.py <frontier.json> <out.json> [max_functions]"
    )
    raise SystemExit(2)

frontier_path = args[0]
out_path = args[1]
max_functions = int(args[2]) if len(args) > 2 else 48

program = currentProgram
fm = program.getFunctionManager()
listing = program.getListing()
image_base = program.getImageBase()

with open(frontier_path, "rb") as fh:
    frontier = json.loads(fh.read().decode("utf-8"))

if frontier.get("schema") != "d1_executable_renderer_frontier/v1":
    printerr("unsupported frontier schema %r" % frontier.get("schema"))
    raise SystemExit(2)

program_sha = str(program.getExecutableSHA256()).lower()
frontier_sha = str(frontier.get("executable_sha256") or "").lower()
if frontier_sha and program_sha and frontier_sha != program_sha:
    printerr(
        "frontier executable SHA-256 %s does not match current program %s"
        % (frontier_sha, program_sha)
    )
    raise SystemExit(2)


def address_text(address):
    return str(address) if address is not None else None


def image_offset(address):
    if address is None:
        return None
    try:
        return int(address.subtract(image_base))
    except Exception:
        return None


def scalar_values(instruction):
    out = []
    for operand_index in range(instruction.getNumOperands()):
        for obj in instruction.getOpObjects(operand_index):
            if not isinstance(obj, Scalar):
                continue
            bits = int(obj.bitLength())
            if bits <= 0 or bits > 64:
                continue
            value = int(obj.getUnsignedValue())
            row = {
                "operand_index": operand_index,
                "bit_length": bits,
                "value_u64": value,
                "value_hex": "0x%X" % value,
            }
            if bits <= 32 and 0x80800000 <= value <= 0x827FFFFF:
                row["d1_hash_literal_candidate"] = True
            if value <= 0x100:
                row["small_state_literal_candidate"] = True
            out.append(row)
    return out


def pcode_rows(instruction):
    out = []
    try:
        ops = instruction.getPcode()
    except Exception:
        return out
    for op in ops:
        inputs = []
        for i in range(op.getNumInputs()):
            inputs.append(str(op.getInput(i)))
        output = op.getOutput()
        out.append({
            "mnemonic": str(op.getMnemonic()),
            "output": str(output) if output is not None else None,
            "inputs": inputs,
        })
    return out


def reference_rows(instruction):
    out = []
    for ref in instruction.getReferencesFrom():
        target = ref.getToAddress()
        owner = fm.getFunctionContaining(target) if target is not None else None
        row = {
            "type": str(ref.getReferenceType()),
            "target": address_text(target),
            "target_image_offset": image_offset(target),
            "target_function_entry": (
                address_text(owner.getEntryPoint()) if owner is not None else None
            ),
            "target_function_name": (
                str(owner.getName()) if owner is not None else None
            ),
            "is_call": bool(ref.getReferenceType().isCall()),
            "is_data": bool(ref.getReferenceType().isData()),
        }
        try:
            data = listing.getDataAt(target)
            if data is not None:
                row["target_data_type"] = str(data.getDataType().getName())
                value = data.getValue()
                if value is not None:
                    text = str(value)
                    if len(text) <= 512:
                        row["target_data_value"] = text
        except Exception:
            pass
        out.append(row)
    return out


def function_record(function, frontier_row, decompiler):
    instructions = []
    pcode_counts = {}
    refs_by_type = {}
    iterator = listing.getInstructions(function.getBody(), True)
    while iterator.hasNext():
        instruction = iterator.next()
        operands = []
        for operand_index in range(instruction.getNumOperands()):
            try:
                operands.append(
                    str(instruction.getDefaultOperandRepresentation(operand_index))
                )
            except Exception:
                operands.append(None)
        pcode = pcode_rows(instruction)
        references = reference_rows(instruction)
        for row in pcode:
            name = row["mnemonic"]
            pcode_counts[name] = pcode_counts.get(name, 0) + 1
        for row in references:
            name = row["type"]
            refs_by_type[name] = refs_by_type.get(name, 0) + 1
        instructions.append({
            "address": address_text(instruction.getAddress()),
            "image_offset": image_offset(instruction.getAddress()),
            "mnemonic": str(instruction.getMnemonicString()),
            "operands": operands,
            "scalars": scalar_values(instruction),
            "references": references,
            "pcode": pcode,
        })

    decompilation = {
        "completed": False,
        "error": None,
        "c": None,
    }
    try:
        result = decompiler.decompileFunction(function, 90, monitor)
        decompilation["completed"] = bool(result.decompileCompleted())
        if result.decompileCompleted():
            decompiled = result.getDecompiledFunction()
            if decompiled is not None:
                decompilation["c"] = str(decompiled.getC())
        else:
            decompilation["error"] = str(result.getErrorMessage())
    except Exception as exc:
        decompilation["error"] = str(exc)

    return {
        "frontier": frontier_row,
        "entry": address_text(function.getEntryPoint()),
        "image_offset": image_offset(function.getEntryPoint()),
        "name": str(function.getName()),
        "namespace": str(function.getParentNamespace()),
        "prototype": str(function.getPrototypeString(False, True)),
        "parameter_count": int(function.getParameterCount()),
        "calling_convention": str(function.getCallingConventionName()),
        "body_address_count": int(function.getBody().getNumAddresses()),
        "instruction_count": len(instructions),
        "pcode_operation_counts": pcode_counts,
        "reference_type_counts": refs_by_type,
        "instructions": instructions,
        "decompilation": decompilation,
    }


decompiler = DecompInterface()
decompiler.toggleCCode(True)
decompiler.toggleSyntaxTree(True)
decompiler.setSimplificationStyle("decompile")
if not decompiler.openProgram(program):
    printerr("failed to initialize Ghidra decompiler")
    raise SystemExit(2)

records = []
missing = []
for frontier_row in frontier.get("candidates", [])[:max_functions]:
    offset = frontier_row.get("image_offset")
    if not isinstance(offset, (int, long)):
        missing.append({
            "function_id": frontier_row.get("function_id"),
            "reason": "candidate has no integer image_offset",
        })
        continue
    try:
        address = image_base.add(offset)
    except Exception:
        missing.append({
            "function_id": frontier_row.get("function_id"),
            "image_offset": offset,
            "reason": "image offset cannot be mapped into current program",
        })
        continue

    function = fm.getFunctionAt(address)
    if function is None:
        function = fm.getFunctionContaining(address)
    if function is None:
        missing.append({
            "function_id": frontier_row.get("function_id"),
            "image_offset": offset,
            "reason": "no Ghidra function at/containing frontier offset",
        })
        continue
    records.append(function_record(function, frontier_row, decompiler))

report = {
    "schema": "d1_ghidra_renderer_slices/v1",
    "program": {
        "name": str(program.getName()),
        "executable_sha256": program_sha,
        "image_base": address_text(image_base),
        "language_id": str(program.getLanguageID()),
        "compiler_spec": str(program.getCompilerSpec().getCompilerSpecID()),
    },
    "frontier_schema": frontier.get("schema"),
    "frontier_candidate_count": len(frontier.get("candidates", [])),
    "requested_max_functions": max_functions,
    "exported_function_count": len(records),
    "missing_function_count": len(missing),
    "policy": (
        "Decompiler/disassembly output is exact-build evidence tied to executable "
        "SHA-256. Frontier scores are discovery priorities only; semantic names "
        "must be promoted separately from demonstrated control/data flow."
    ),
    "functions": records,
    "missing": missing,
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

print("D1 renderer slice export: %s" % out_path)
print(
    "frontier=%d exported=%d missing=%d"
    % (
        report["frontier_candidate_count"],
        report["exported_function_count"],
        report["missing_function_count"],
    )
)
