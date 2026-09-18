# D1 LocalShader API10 direct user-data gate — 2026-09-18

Status: **entry delivery mechanism closed; runtime writer and backing semantics unresolved**.

This checkpoint is source-closed against the pinned exact `D1_GCN_LOCALSHADER_TBUFFER_USAGE_BINDING_V1` artifact (artifact `10172731401`, report SHA-256 `6c6c07d03ed06d8b53693326cbabd9fde7c7a2f7b0c41e02939e700cf4f21127`). The reproducible census is `tools/d1_gcn_localshader_api10_entry_layout_census_v1.py`; CI run `35305035230` passed and emitted artifact `10530797555` (artifact digest `sha256:1553cda9fc1e86015a4cd0ad0a8dd86f6ae3c2d5f7ab9483f59c25d004f70afe`). Frozen output is also retained under `evidence/d1_gcn_localshader_api10_entry_layout_census_2026-09-18.json`.

## Exact result

All 39 LocalShader GCN programs that execute the 385 proven API10 typed-buffer reads receive API10 through a **direct `ImmConstBuffer` InputUsageSlot in program-entry user SGPRs**. There are exactly two usage layouts:

- 13 programs / 16 wrappers / 2,567 material occurrences: API10 begins at `s8`, descriptor window `s[8:11]`; API11 begins at `s12`.
- 26 programs / 40 wrappers / 819 material occurrences: API0 begins at `s8`, API10 begins at `s12`, descriptor window `s[12:15]`; API11 begins at `s16`. These programs additionally expose a distinct `PtrExtendedUserData` slot at `s6`.

Across the entire 39-program API10 subset there are **zero `PtrConstBufferTable` InputUsageSlots and zero `PtrResourceTable` InputUsageSlots**. `PtrExtendedUserData` appears in 26 programs, but its start register (`s6`) is disjoint from API10 and API10 remains a direct `ImmConstBuffer` slot. The prior exact reaching-state proof already established that all four SGPRs of every API10 descriptor remain unmodified program-entry state at each typed-buffer read.

Therefore the next gate is no longer "which resource table contains API10?". For this exact LocalShader subset, there is no InputUsageSlot evidence for API10 table indirection. The next gate is the runtime command/binding path that writes the four-word constant-buffer descriptor into the direct user-SGPR window selected by the OrbShdr usage table.

## What is still withheld

This result does **not** identify the Destiny engine object that supplies API10, its GPU virtual address, stride/record count, backing bytes, numeric values, or semantic role. It also does not imply that `PtrExtendedUserData` owns API10; the usage records prove they are distinct entry slots.

A semantic promotion now requires primary runtime evidence connecting the exact LocalShader wrapper/program identity to the command-buffer/user-data population path, or an equivalent capture/replay artifact that records the four descriptor dwords written to `s[8:11]` / `s[12:15]` and traces those dwords to their backing allocation. Until such evidence exists, names such as bone palette, transforms, tessellation constants, or material constants remain forbidden.
