# D1ExportCodeGraph.py
#@category Destiny
#@menupath Destiny.Export Code Graph
#@toolbar
#
# Ghidra post-analysis exporter for Destiny 1 executable reverse engineering.
# Run after normal auto-analysis. The script emits functions, call edges,
# external imports, defined strings, and string xrefs. Retail executable bytes
# are never copied into the output.
#
# Headless example:
#   analyzeHeadless <project-dir> D1Exec \
#     -import <eboot-or-elf> -overwrite \
#     -scriptPath <destiny-1>/tools/ghidra \
#     -postScript D1ExportCodeGraph.py <out.json> CUSA00219 01.29
#
# This script intentionally uses Python-2-compatible syntax for classic Ghidra
# Jython script execution.

import json
import os

args = getScriptArgs()
if len(args) < 1:
    printerr("usage: D1ExportCodeGraph.py <out.json> [title_id] [app_version]")
    raise SystemExit(2)

out_path = args[0]
title_id = args[1] if len(args) > 1 else None
app_version = args[2] if len(args) > 2 else None

program = currentProgram
fm = program.getFunctionManager()
listing = program.getListing()
refs = program.getReferenceManager()
external_manager = program.getExternalManager()
image_base = program.getImageBase()


def address_text(address):
    return str(address) if address is not None else None


def image_offset(address):
    if address is None:
        return None
    try:
        return int(address.subtract(image_base))
    except Exception:
        return None


def function_key(function):
    return address_text(function.getEntryPoint())


def function_record(function):
    body = function.getBody()
    entry = function.getEntryPoint()
    called = []
    try:
        callees = function.getCalledFunctions(monitor)
        for callee in callees:
            called.append(function_key(callee))
    except Exception:
        pass

    symbol = function.getSymbol()
    source = None
    try:
        source = str(symbol.getSource())
    except Exception:
        pass

    return {
        "entry": address_text(entry),
        "image_offset": image_offset(entry),
        "name": str(function.getName()),
        "namespace": str(function.getParentNamespace()),
        "source": source,
        "is_thunk": bool(function.isThunk()),
        "is_external": bool(function.isExternal()),
        "body_min": address_text(body.getMinAddress()),
        "body_max": address_text(body.getMaxAddress()),
        "body_address_count": int(body.getNumAddresses()),
        "parameter_count": int(function.getParameterCount()),
        "calling_convention": str(function.getCallingConventionName()),
        "prototype": str(function.getPrototypeString(False, True)),
        "called_function_entries": sorted(called),
    }


functions = []
function_by_entry = {}
iterator = fm.getFunctions(True)
while iterator.hasNext():
    function = iterator.next()
    record = function_record(function)
    functions.append(record)
    function_by_entry[record["entry"]] = record

calls = []
for function in functions:
    for target in function["called_function_entries"]:
        calls.append({
            "caller": function["entry"],
            "callee": target,
        })

externals = []
external_iterator = fm.getExternalFunctions()
while external_iterator.hasNext():
    function = external_iterator.next()
    location = function.getExternalLocation()
    externals.append({
        "entry": address_text(function.getEntryPoint()),
        "name": str(function.getName()),
        "prototype": str(function.getPrototypeString(False, True)),
        "library": str(location.getLibraryName()) if location is not None else None,
        "original_imported_name": (
            str(location.getOriginalImportedName())
            if location is not None and location.getOriginalImportedName() is not None
            else None
        ),
    })

external_libraries = []
try:
    for library_name in external_manager.getExternalLibraryNames():
        external_libraries.append({
            "name": str(library_name),
            "path": (
                str(external_manager.getExternalLibraryPath(library_name))
                if external_manager.getExternalLibraryPath(library_name) is not None
                else None
            ),
        })
except Exception:
    pass

strings = []
data_iterator = listing.getDefinedData(True)
while data_iterator.hasNext():
    data = data_iterator.next()
    try:
        data_type_name = str(data.getDataType().getName()).lower()
    except Exception:
        continue
    if "string" not in data_type_name and "unicode" not in data_type_name:
        continue

    value = data.getValue()
    if value is None:
        continue
    text_value = str(value)
    if not text_value:
        continue

    xrefs = []
    ref_iterator = refs.getReferencesTo(data.getAddress())
    while ref_iterator.hasNext():
        ref = ref_iterator.next()
        from_addr = ref.getFromAddress()
        owner = fm.getFunctionContaining(from_addr)
        xrefs.append({
            "from": address_text(from_addr),
            "from_image_offset": image_offset(from_addr),
            "function_entry": (
                address_text(owner.getEntryPoint()) if owner is not None else None
            ),
            "function_name": str(owner.getName()) if owner is not None else None,
            "reference_type": str(ref.getReferenceType()),
        })

    strings.append({
        "address": address_text(data.getAddress()),
        "image_offset": image_offset(data.getAddress()),
        "length": int(data.getLength()),
        "data_type": str(data.getDataType().getName()),
        "text": text_value,
        "xrefs": xrefs,
    })

report = {
    "schema": "d1_ghidra_code_graph/v1",
    "program": {
        "name": str(program.getName()),
        "title_id": title_id,
        "app_version": app_version,
        "executable_path": str(program.getExecutablePath()),
        "executable_format": str(program.getExecutableFormat()),
        "executable_md5": str(program.getExecutableMD5()),
        "executable_sha256": str(program.getExecutableSHA256()),
        "language_id": str(program.getLanguageID()),
        "compiler_spec": str(program.getCompilerSpec().getCompilerSpecID()),
        "image_base": address_text(image_base),
    },
    "counts": {
        "functions": len(functions),
        "calls": len(calls),
        "external_functions": len(externals),
        "external_libraries": len(external_libraries),
        "defined_strings": len(strings),
        "string_xrefs": sum(len(item["xrefs"]) for item in strings),
    },
    "functions": functions,
    "calls": calls,
    "external_functions": externals,
    "external_libraries": external_libraries,
    "strings": strings,
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

print("D1 code graph export: %s" % out_path)
print(
    "functions=%d calls=%d externals=%d strings=%d xrefs=%d"
    % (
        report["counts"]["functions"],
        report["counts"]["calls"],
        report["counts"]["external_functions"],
        report["counts"]["defined_strings"],
        report["counts"]["string_xrefs"],
    )
)
