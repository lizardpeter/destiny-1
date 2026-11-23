# Ghidra pipeline

`.github/workflows/ghidra.yml` analyses the builds listed in `target.toml` and commits the result to
`analysis/<build>/`. Everything under `analysis/` is written by tools. If something there is wrong, fix the
script and run the pipeline again; never edit the output.

## What is committed

| Path | Contents |
|---|---|
| `analysis/<build>/functions.tsv` | Every function: address, size, name and where the name came from, address block, thunk target, instruction count, hash of its bytes, whether it decompiled |
| `analysis/<build>/summary.json` | Counts from the run |
| `analysis/<build>/unwind.tsv` | Start and length of every function in the unwind table |
| `analysis/<build>/imports.tsv` | Every address the dynamic linker writes an import into, with NID, library and name |
| `analysis/<build>/pseudocode/<block>.c` | Decompiler output for every function |
| `analysis/<build>/disasm/<block>.asm` | Disassembly of every function, with instruction bytes |
| `analysis/<build>/ghidra/` | Ghidra's own tables (`functions.tsv`, `callgraph.tsv`, `symbols.tsv`, `strings.tsv`, `types.h`) and the saved Ghidra project |
| `analysis/<build>/logs/` | Analysis and decompile logs |

There is no build of this game with symbols, so nothing says which source file a function belongs to.
Pseudocode and disassembly are grouped by 64 KB address block: function `003527d0` is in
`pseudocode/00350000.c`.

## Addresses

Addresses are image-relative, 8 lowercase hex digits. The executable's first segment has virtual address 0 and
Ghidra loads it at image base 0, so `003527d0` here is `0x3527d0` in the runtime's hooks and in the notes, and
`FUN_003527d0` in Ghidra.

## Function discovery

The executable has no section headers, so Ghidra does not find its unwind table, and by itself it only finds
functions that something calls or references directly: 46,944 here. The unwind table lists 54,533, covering
18.4 MB of code; the difference is virtual methods and callbacks. `tools/ghidra/unwind.py` reads the table
from the `PT_GNU_EH_FRAME` segment and `CreateUnwindFunctions.java` creates a function at each start before
analysis. `functions.tsv` carries the unwind table's length for each function beside Ghidra's, and
`summary.json` counts any the analysis still lacks.

## Imports

Ghidra does not read the PS4's dynamic tables, and the executable names its imports by NID (a hash).
`tools/ghidra/imports.py` reads the relocation tables from the SCE dynlib segment and resolves the NIDs with
`evidence/generated/d1_import_surface.json`. `ApplyImports.java` then labels each slot `__imp_<name>` and gives
each jump stub its import's name, so pseudocode shows `memcpy` and `sceKernelMapDirectMemory`.

## Opening the project

```
cat analysis/ps4-0133/ghidra/project.tar.gz.part-* | tar -xz -C <empty folder>
```

Open `d1.gpr` from that folder with the Ghidra version named in `target.toml`.

## Running it

The pipeline runs when `target.toml`, its own scripts or the workflow change, for builds with
`analyze = true`. A manual run can name builds. Once a build is analysed, set `analyze = false` so later
edits to `target.toml` do not repeat the work.

Jobs: `analyze` (import, unwind-table functions, auto-analysis, import naming, export, save the project), `decompile` (six shards
from the saved project), `publish` (assemble `analysis/<build>/` and commit). A cancelled run publishes
nothing, and a run that produced no pseudocode keeps the existing pseudocode.
