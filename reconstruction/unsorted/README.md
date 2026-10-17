# Unsorted decompiles

Unedited Ghidra 11.4.2 decompiler output for 1165 functions of the 01.33 eboot
(CUSA00219, `eboot.bin` SHA-256 `672f0341…0833`) that were decompiled during the
research sessions of 2026-10-12 .. 2026-10-16 but are **not yet attributed to a
subsystem** and have no entry in `reconstruction/functions.json`.

- `decompiled/<va>.c`: one file per function, named by its eboot virtual address (hex,
  the function's entry point). Ghidra's output as written, not cleaned up or verified.
  Names inside (`FUN_xxxxxxxx`, `DAT_xxxxxxxx`) are Ghidra's defaults.
- `index.json`: `va`, `size_bytes` (from the eboot's `.eh_frame_hdr` FDE table) and
  `direct_call_sites` (number of `call rel32` instructions in the executable segment that
  target the function, found by a byte scan restricted to known functions: approximate,
  indirect and virtual calls are not counted).

Being here says nothing about a function's role: most were decompiled because they were
called from, or called, a function under investigation. When a function's behaviour is
established, add it to `functions.json` with its subsystem and role, move its file into
that subsystem's `decompiled/` folder as `<va>_<name>.c`, and remove it from `index.json`.

## Reproducing a decompile

1. Relocated flat image of the eboot at base 0 (SCE dynamic relocations applied): the
   `Image(path).mem` bytes of `tools/eboot/d1_reconstruction_tree.py`
   (`eboot.reloc.bin`, 49,719,248 bytes, SHA-256 `61552318…91ee0c`).
2. Function starts from `.eh_frame_hdr`: `functions_from_eh` in
   `tools/eboot/d1_x86_portability_census.py`, written as one hex start per line.
3. Ghidra project: import the image headless as `x86:LE:64:default:gcc`, run
   auto-analysis, and post-script `tools/ghidra/D1CreateFunctions.java <starts file>`
   (creates a function at every FDE start; 54,221 of 54,533 created).
4. Decompile (read-only, no re-analysis):

   ```bash
   analyzeHeadless <proj_dir> d1 -process eboot.reloc.bin -readOnly -noanalysis \
     -scriptPath <destiny-1>/tools/ghidra -postScript D1Decompile.java <out_dir> <hex addr>...
   ```

   `D1Decompile.java` decompiles the function containing each address (120 s timeout)
   and writes `<out_dir>/<entry hex>.c`. The research sessions wrapped this command in a
   one-line shell script (`dec.sh <hex addrs without 0x>`) outside the repository.
