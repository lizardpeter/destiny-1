# D1ExportTerrainRuntime.py
#@category Destiny
#@menupath Destiny.Export Terrain Runtime Frontier
#
# Exact-build executable probe for the D1 RoI terrain runtime producer edge.
# It ranks functions by independent evidence:
#   * exact STerrain / SMapTerrainResource class immediates,
#   * fixed pixel-resource descriptor offsets consistent with slot 14,
#   * literal slot index 14,
#   * terrain/dyemap symbol or string references,
#   * call-graph proximity to known renderer submission functions.
#
# Semantics are deliberately not assigned from these scores.  The output is
# decompiler/disassembly evidence for a later proof step.
#
# Usage:
#   -postScript D1ExportTerrainRuntime.py <out.json> [max_functions]

import json
import os

from ghidra.app.decompiler import DecompInterface
from ghidra.program.model.scalar import Scalar

args = getScriptArgs()
if len(args) < 1:
    printerr("usage: D1ExportTerrainRuntime.py <out.json> [max_functions]")
    raise SystemExit(2)

out_path = args[0]
max_functions = int(args[1]) if len(args) > 1 else 160

program = currentProgram
fm = program.getFunctionManager()
listing = program.getListing()
refs = program.getReferenceManager()
symbols = program.getSymbolTable()
image_base = program.getImageBase()

TARGET_CLASSES = {
    0x80801B2E: "STerrain",
    0x80801C37: "SMapTerrainResource",
}
# Native PS texture descriptors are 8 dwords = 32 bytes.  Resource-table
# texture slot 14 therefore begins at 14 * 0x20 = 0x1C0.
SLOT14_DESCRIPTOR_OFFSET = 0x1C0
SLOT14_INDEX = 14
RENDER_SEED_OFFSETS = [
    0x811100,  # renderer job registration neighborhood
    0x8113E0,  # setup/extract diagnostic helper neighborhood
    0x811400,  # render_submit_view job
]


def address_text(address):
    return str(address) if address is not None else None


def image_offset(address):
    if address is None:
        return None
    try:
        return int(address.subtract(image_base))
    except Exception:
        return None


def containing_at_offset(offset):
    try:
        address = image_base.add(offset)
    except Exception:
        return None
    function = fm.getFunctionAt(address)
    if function is None:
        function = fm.getFunctionContaining(address)
    return function


terrain_data = []
data_iterator = listing.getDefinedData(True)
while data_iterator.hasNext():
    data = data_iterator.next()
    value = data.getValue()
    if value is None:
        continue
    text_value = str(value)
    lower = text_value.lower()
    if "terrain" not in lower and "dyemap" not in lower and "dye_map" not in lower:
        continue
    xrefs = []
    ri = refs.getReferencesTo(data.getAddress())
    while ri.hasNext():
        ref = ri.next()
        owner = fm.getFunctionContaining(ref.getFromAddress())
        xrefs.append({
            "from": address_text(ref.getFromAddress()),
            "from_image_offset": image_offset(ref.getFromAddress()),
            "function_entry": address_text(owner.getEntryPoint()) if owner is not None else None,
            "function_name": str(owner.getName()) if owner is not None else None,
            "reference_type": str(ref.getReferenceType()),
        })
    terrain_data.append({
        "address": address_text(data.getAddress()),
        "image_offset": image_offset(data.getAddress()),
        "text": text_value,
        "xrefs": xrefs,
    })


terrain_symbols = []
symbol_iterator = symbols.getAllSymbols(True)
while symbol_iterator.hasNext():
    symbol = symbol_iterator.next()
    name = str(symbol.getName())
    lower = name.lower()
    if "terrain" not in lower and "dyemap" not in lower and "dye_map" not in lower:
        continue
    address = symbol.getAddress()
    owner = fm.getFunctionContaining(address) if address is not None else None
    terrain_symbols.append({
        "name": name,
        "address": address_text(address),
        "image_offset": image_offset(address),
        "symbol_type": str(symbol.getSymbolType()),
        "source": str(symbol.getSource()),
        "function_entry": address_text(owner.getEntryPoint()) if owner is not None else None,
        "function_name": str(owner.getName()) if owner is not None else None,
    })


records = {}
function_by_entry = {}
iterator = fm.getFunctions(True)
while iterator.hasNext():
    function = iterator.next()
    entry = address_text(function.getEntryPoint())
    function_by_entry[entry] = function
    direct = 0
    evidence = []
    class_hits = []
    slot14_offset_hits = []
    slot14_index_hits = []
    small_descriptor_hits = []

    instructions = listing.getInstructions(function.getBody(), True)
    while instructions.hasNext():
        instruction = instructions.next()
        mnemonic = str(instruction.getMnemonicString())
        operand_text = []
        for operand_index in range(instruction.getNumOperands()):
            try:
                operand_text.append(str(instruction.getDefaultOperandRepresentation(operand_index)))
            except Exception:
                operand_text.append(None)
            for obj in instruction.getOpObjects(operand_index):
                if not isinstance(obj, Scalar):
                    continue
                bits = int(obj.bitLength())
                if bits <= 0 or bits > 64:
                    continue
                value = int(obj.getUnsignedValue())
                if bits <= 32:
                    value32 = value & 0xFFFFFFFF
                    if value32 in TARGET_CLASSES:
                        row = {
                            "instruction": address_text(instruction.getAddress()),
                            "instruction_image_offset": image_offset(instruction.getAddress()),
                            "mnemonic": mnemonic,
                            "operand_index": operand_index,
                            "value_hex": "0x%08X" % value32,
                            "role": TARGET_CLASSES[value32],
                        }
                        class_hits.append(row)
                        direct += 120
                    if value32 == SLOT14_DESCRIPTOR_OFFSET:
                        row = {
                            "instruction": address_text(instruction.getAddress()),
                            "instruction_image_offset": image_offset(instruction.getAddress()),
                            "mnemonic": mnemonic,
                            "operands": operand_text,
                        }
                        slot14_offset_hits.append(row)
                        direct += 12
                    if value32 == SLOT14_INDEX:
                        row = {
                            "instruction": address_text(instruction.getAddress()),
                            "instruction_image_offset": image_offset(instruction.getAddress()),
                            "mnemonic": mnemonic,
                            "operands": operand_text,
                        }
                        slot14_index_hits.append(row)
                        direct += 1
                    if value32 in (0x20, 0x40, 0x80, 0xE0):
                        small_descriptor_hits.append({
                            "instruction": address_text(instruction.getAddress()),
                            "instruction_image_offset": image_offset(instruction.getAddress()),
                            "mnemonic": mnemonic,
                            "value_hex": "0x%X" % value32,
                        })

    if direct > 0:
        evidence.extend(class_hits)
        evidence.extend(slot14_offset_hits)
        records[entry] = {
            "function": function,
            "direct_score": direct,
            "class_hits": class_hits,
            "slot14_descriptor_offset_hits": slot14_offset_hits,
            "slot14_index_hits": slot14_index_hits,
            "small_descriptor_hits": small_descriptor_hits,
            "evidence": evidence,
        }


def ensure_record(function):
    if function is None:
        return None
    entry = address_text(function.getEntryPoint())
    if entry not in records:
        records[entry] = {
            "function": function,
            "direct_score": 0,
            "class_hits": [],
            "slot14_descriptor_offset_hits": [],
            "slot14_index_hits": [],
            "small_descriptor_hits": [],
            "evidence": [],
        }
    return records[entry]


# Promote true code/string xrefs and named terrain symbols if Ghidra recovered any.
for item in terrain_data:
    for xref in item["xrefs"]:
        owner = function_by_entry.get(xref.get("function_entry"))
        row = ensure_record(owner)
        if row is not None:
            row["direct_score"] += 200
            row["evidence"].append({
                "kind": "terrain_defined_string_xref",
                "text": item["text"],
                "xref": xref,
            })

for item in terrain_symbols:
    owner = function_by_entry.get(item.get("function_entry"))
    row = ensure_record(owner)
    if row is not None:
        row["direct_score"] += 250
        row["evidence"].append({
            "kind": "terrain_symbol",
            "symbol": item,
        })

# Known exact renderer submission neighborhoods are seeds, not semantic labels.
for offset in RENDER_SEED_OFFSETS:
    function = containing_at_offset(offset)
    row = ensure_record(function)
    if row is not None:
        row["direct_score"] += 60
        row["evidence"].append({
            "kind": "known_renderer_submission_neighborhood",
            "image_offset": offset,
        })

# Call-graph propagation, three hops in either direction.
seed_entries = [entry for entry, row in records.items() if row["direct_score"] > 0]
propagated = {}
nearest = {}
for seed_entry in seed_entries:
    seed = function_by_entry.get(seed_entry)
    if seed is None:
        continue
    seed_score = records[seed_entry]["direct_score"]
    queue = [(seed, 0)]
    seen = {seed_entry: True}
    while queue:
        current, distance = queue.pop(0)
        if distance >= 3:
            continue
        neighbors = []
        try:
            neighbors.extend(list(current.getCalledFunctions(monitor)))
        except Exception:
            pass
        try:
            neighbors.extend(list(current.getCallingFunctions(monitor)))
        except Exception:
            pass
        for neighbor in neighbors:
            entry = address_text(neighbor.getEntryPoint())
            if entry in seen:
                continue
            seen[entry] = True
            next_distance = distance + 1
            weight = float(seed_score) / float(2 ** next_distance)
            propagated[entry] = propagated.get(entry, 0.0) + weight
            nearest.setdefault(entry, []).append(seed_entry)
            queue.append((neighbor, next_distance))
            ensure_record(neighbor)

# Rank: exact class/symbol/xref evidence dominates; slot-14 evidence matters most
# when it is also close to renderer submission.
ranked = []
for entry, row in records.items():
    score = float(row["direct_score"]) + propagated.get(entry, 0.0)
    # Literal index 14 is too common to seed alone.  Count it only when the
    # function is already within the proven renderer/terrain neighborhood.
    if (row["direct_score"] > 0 or propagated.get(entry, 0.0) > 0) and row["slot14_index_hits"]:
        score += min(10, len(row["slot14_index_hits"]))
    if score <= 0:
        continue
    function = row["function"]
    ranked.append({
        "entry": entry,
        "image_offset": image_offset(function.getEntryPoint()),
        "name": str(function.getName()),
        "prototype": str(function.getPrototypeString(False, True)),
        "direct_score": row["direct_score"],
        "neighbor_score": round(propagated.get(entry, 0.0), 3),
        "score": round(score, 3),
        "class_hits": row["class_hits"],
        "slot14_descriptor_offset_hits": row["slot14_descriptor_offset_hits"],
        "slot14_index_hits": row["slot14_index_hits"],
        "small_descriptor_hits": row["small_descriptor_hits"],
        "evidence": row["evidence"],
        "neighbor_seed_entries": sorted(set(nearest.get(entry, []))),
    })

ranked.sort(key=lambda row: (-row["score"], row["image_offset"] if row["image_offset"] is not None else 1 << 62))
ranked = ranked[:max_functions]


def reference_rows(instruction):
    out = []
    for ref in instruction.getReferencesFrom():
        target = ref.getToAddress()
        owner = fm.getFunctionContaining(target) if target is not None else None
        out.append({
            "type": str(ref.getReferenceType()),
            "target": address_text(target),
            "target_image_offset": image_offset(target),
            "target_function_entry": address_text(owner.getEntryPoint()) if owner is not None else None,
            "target_function_name": str(owner.getName()) if owner is not None else None,
            "is_call": bool(ref.getReferenceType().isCall()),
            "is_data": bool(ref.getReferenceType().isData()),
        })
    return out


decompiler = DecompInterface()
decompiler.toggleCCode(True)
decompiler.toggleSyntaxTree(True)
decompiler.setSimplificationStyle("decompile")
if not decompiler.openProgram(program):
    printerr("failed to initialize Ghidra decompiler")
    raise SystemExit(2)

functions_out = []
for rank in ranked:
    function = function_by_entry.get(rank["entry"])
    if function is None:
        continue
    instructions_out = []
    iterator = listing.getInstructions(function.getBody(), True)
    while iterator.hasNext():
        instruction = iterator.next()
        operands = []
        for operand_index in range(instruction.getNumOperands()):
            try:
                operands.append(str(instruction.getDefaultOperandRepresentation(operand_index)))
            except Exception:
                operands.append(None)
        instructions_out.append({
            "address": address_text(instruction.getAddress()),
            "image_offset": image_offset(instruction.getAddress()),
            "mnemonic": str(instruction.getMnemonicString()),
            "operands": operands,
            "references": reference_rows(instruction),
        })

    decompilation = {"completed": False, "error": None, "c": None}
    try:
        result = decompiler.decompileFunction(function, 60, monitor)
        decompilation["completed"] = bool(result.decompileCompleted())
        if result.decompileCompleted():
            value = result.getDecompiledFunction()
            if value is not None:
                decompilation["c"] = str(value.getC())
        else:
            decompilation["error"] = str(result.getErrorMessage())
    except Exception as exc:
        decompilation["error"] = str(exc)

    functions_out.append({
        "rank": rank,
        "body_min": address_text(function.getBody().getMinAddress()),
        "body_max": address_text(function.getBody().getMaxAddress()),
        "instruction_count": len(instructions_out),
        "instructions": instructions_out,
        "decompilation": decompilation,
    })

report = {
    "schema": "d1_terrain_runtime_frontier/v1",
    "program": {
        "name": str(program.getName()),
        "executable_sha256": str(program.getExecutableSHA256()).lower(),
        "image_base": address_text(image_base),
        "language_id": str(program.getLanguageID()),
    },
    "proof_policy": (
        "Candidate scores are discovery aids only. STerrain/dyemap/T14 semantic "
        "promotion requires direct retail code/data flow; slot-14 arithmetic or "
        "tooling names alone are not sufficient."
    ),
    "targets": {
        "STerrain_class": "0x80801B2E",
        "SMapTerrainResource_class": "0x80801C37",
        "pixel_resource_slot_index": 14,
        "texture_descriptor_size_bytes": 32,
        "slot14_descriptor_offset": "0x1C0",
        "renderer_seed_offsets": ["0x%X" % x for x in RENDER_SEED_OFFSETS],
    },
    "terrain_defined_data": terrain_data,
    "terrain_symbols": terrain_symbols,
    "candidate_count": len(ranked),
    "exported_function_count": len(functions_out),
    "functions": functions_out,
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

print("D1 terrain runtime frontier: %s" % out_path)
print("terrain_data=%d terrain_symbols=%d candidates=%d exported=%d" % (
    len(terrain_data), len(terrain_symbols), len(ranked), len(functions_out)
))
