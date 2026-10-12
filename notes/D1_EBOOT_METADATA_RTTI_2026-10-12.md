# D1 PS4 eboot: exact function bounds, imports, relocations and RTTI (2026-10-12)

Input: `eboot.bin` SHA-256 `672f03411c0503df…` (same file as the 2026-09-27 notes), from `destiny/CUSA00219_01.33/eboot.bin`.

## Findings

- **Toolchain:** process param SDK version `0x01700081` (SDK 1.70); build stamp `Clang3.3.0 SCE01500111`.
- **Functions:** `.eh_frame_hdr` (PT_GNU_EH_FRAME at VA `0x1869930`) holds 54,533 FDEs, which give exact start and size for each function. They span VA `0xa0`–`0x12aa720` and cover ~18.4 MB of code. Clang emits switch jump tables inline in the function ranges, as 32-bit relative entries.
- **Imports:** 642 PLT imports (JMPREL), all resolved by NID through shadPS4's `aerolib.inl`. 49 libraries: libc, libkernel, libSceGnmDriver, libSceFios2, the Np* family, and others.
- **Relocations:** 73,873 SCE RELA entries: 70,727 `R_X86_64_RELATIVE`, 3,124 `R_X86_64_64` and 22 `GLOB_DAT`. Every one targets the RW segment, and the file stores zero at each site, so the pointer values come only from the RELA addends.
- **RTTI (Itanium ABI):**
  - 2,633 typeinfo objects and 2,494 base-class links.
  - 2,430 vtables with 22,915 slots, covering 7,975 distinct virtual functions.
  - Most of the classes are UI: 569 in `cui::` and 213 in `ui::`.
  - Middleware classes present: SpeedTree, AK (Wwise), Havok/`hcl` cloth, Oodle, DemonWare and libtom.
- **Renderer anchors for the importer:**
  - `c_sun_manager`: typeinfo `0x1949590`, vtable `0x1949560`, with slots 1–3 at `0x8b29a0`, `0x8b1f10` and `0x8b2000`.
  - `c_materials_game_system`: typeinfo `0x1940810`.
  - `c_shader_component`: typeinfo `0x1955830`.

## Tools (`tools/eboot/`)

```sh
python3 tools/eboot/orbis_meta.py eboot.bin aerolib.inl meta/   # functions/imports/relocs/libs .tsv
python3 tools/eboot/rtti.py eboot.bin meta/ rtti/                # classes/bases/vtables .tsv
python3 tools/eboot/xrefs.py eboot.bin meta/ xref/               # calls.tsv (209k), drefs.tsv (313k)
```

Generated TSVs are reproducible from the eboot and are not committed. Ghidra 12.1.3 imports the eboot after one patch: set `e_type` 0xFE10 → 3, then load with `-loader-imagebase 0`.
