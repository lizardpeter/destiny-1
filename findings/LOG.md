# Reverse-Engineering Log

## 2026-09-03 — Sample acquisition and first verified parse

### Input

Google Drive supplied binary: `ps4_arch_cabal_005b_1.pkg`

- materialized local filename: `ps4_arch_cabal_005b_1.pkg.bin`
- size: `89,044,992` bytes
- SHA-256: `d44f2dcbaef32743da9657e38691bcd91372fd9550e96ea3d99a9ce9440c24e0`

### Container/header findings

- D1 Tiger package version = `24`
- platform code = `7` = PS4
- package id = `91` = `0x005B`
- patch id = `1`
- version fields = `3.0`
- language = none
- tool string = `evil tool_lib test pc_x64 46419.15.08.16.1336.evil 15.08.16 1336`
- header-declared file size exactly matches actual file size

### Tables

- file entries = `667`, at `0x1000`
- blocks = `626`, at `0x4000`
- named tags = `0`
- file-entry table SHA-1 from bytes: `8baf1f6f7e20e85c1475d097780264a1307a316b` — matches header
- block table SHA-1 from bytes: `aa689bff4f38d0b9c32ca34d93de3b1a73ea79bc` — matches header
- named-tag header hash is all zero because count is zero; do not incorrectly compare to SHA1(empty)

### Entry type/subtype census

| Type | Subtype | Count |
|---:|---:|---:|
| 1 | 7 | 163 |
| 16 | 0 | 146 |
| 32 | 7 | 122 |
| 5 | 1 | 122 |
| 32 | 1 | 30 |
| 65 | 1 | 30 |
| 1 | 4 | 11 |
| 32 | 4 | 11 |
| 1 | 6 | 9 |
| 32 | 6 | 9 |
| 1 | 8 | 7 |
| 32 | 8 | 7 |

Observation: several exact-count pairings strongly suggest descriptor/payload or related resource classes. This is only a **HYPOTHESIS** until entry contents are decompressed and references followed.

### References

- `0xFFFFFFFF`: 312 entries
- `0x80801AD7`: 136 entries
- `0x80800861`: 8 entries
- many references point to hashes inside package `0x005B` itself, beginning around `0x808B603A`

### Blocks

- all 626 blocks use patch id `1`
- all 626 blocks have flags `0x1`
- therefore all are compressed and none are encrypted under known flag interpretation
- no entry starts outside the block table
- no entry's calculated block span overruns the block table

### Immediate next step

Obtain an Oodle-compatible decompressor in the analysis environment, decompress all logical blocks, reconstruct every entry losslessly, then perform:

1. per-entry SHA256 and byte signatures
2. reference graph
3. 0x8080 tag structure identification
4. resource type clustering
5. mesh/texture/static-map candidate discovery
6. source-schema correlation with Charm/Phonon/tiger-pkg

## 2026-09-03 — Dependency graph and resource-class identification

Generated a package-local dependency graph from all 667 file entries.

### Reference partition

- sentinel `FFFFFFFF`: 312
- same-package FileHash references: 209
- external FileHash references: 146
- non-FileHash references: 0

All 146 external references originate from `type=16, subtype=0` entries and resolve into package-ID 0 namespace. Frequencies:

- `80801AD7`: 136
- `80800861`: 8
- `80801AF2`: 1
- `80801BD9`: 1

This strongly separates structured-tag class/shared references from local GPU/resource payload links.

### Exact local transitions

- `122 × (32,7) -> (1,7)`
- `30 × (32,1) -> (65,1)`
- `30 × (65,1) -> (5,1)`
- `11 × (32,4) -> (1,4)`
- `9 × (32,6) -> (1,6)`
- `7 × (32,8) -> (1,8)`

These relationships are saved as JSON, CSV and DOT under `evidence/graphs/ps4_arch_cabal_005b_1/`.

### D1 resource names correlated with current QuickTag

Current QuickTag's version-specific D1 classifier identifies:
- `16:0` Tag
- `32:1` Texture2D header
- `32:4 / 1:4` VertexBuffer header/data
- `32:6 / 1:6` IndexBuffer header/data
- `32:8 / 1:8` PixelShader header/data

It leaves subtype 7 unresolved/commented as ConstantBuffer for D1. We preserve that uncertainty.

### Geometry header cross-validation with Charm

- Charm `SVertexHeader` is 12 bytes; all 11 sample `32:4` entries are 12 bytes.
- Charm `SIndexHeader` is 24 bytes; all 9 sample `32:6` entries are 24 bytes.

These sample/source agreements upgrade the geometry header roles to `CONFIRMED_CROSS_SOURCE`.

### Texture reference-chain cross-validation

All 30 `32:1` Texture2D headers point to `65:1`; each of those 30 entries points to `5:1`.

Charm's D1 texture path explicitly follows a texture header reference and, when that referenced file has another valid reference, uses the second reference as the texture data source. This independently corroborates the semantic role of our exact two-hop chain.

Project-local names:
- `65:1` = `D1TextureIntermediate`
- `5:1` = `D1TextureTerminalPayload`

These are **role labels only**, not claimed official Tiger type names.

## 2026-09-03 — FileEntry `entry_b` middle-byte census

Across all 667 entries:

- bits 8..15 are always zero.
- bits 16..23 are nonzero and take exactly seven values:
  - 10: 257
  - 14: 37
  - 15: 173
  - 20: 4
  - 21: 190
  - 24: 4
  - 26: 2

The byte clearly carries structured metadata but its semantics are not yet identified. Full statistics, including type/subtype correlation, are stored in `evidence/analysis/ps4_arch_cabal_005b_1/entry_b_stats.json`.

## 2026-09-03 — Oodle decompression investigation

All sample blocks require decompression before payload-level validation. Independent current D1 implementations use Oodle 3 (`OodleLZ_Decompress`) for ROI packages.

The real sample's first compressed block begins `B7 43 E2 90 ...`, and later blocks also begin with `B7`. This is not sufficient evidence to identify the codec and is not treated as a standard modern Kraken stream.

Open-source Kraken-family implementations were reviewed as possible research aids, but have **not** been demonstrated compatible with these D1 block streams. The preferred immediate path is a user-owned `oo2core_3_win64.dll` loaded at runtime via a Linux-compatible wrapper. The proprietary runtime will not be committed into this research workspace.

## 2026-09-03 — Stored block SHA-1 semantics binary-confirmed

A dedicated verifier hashed the exact stored payload bytes for every block record in `ps4_arch_cabal_005b_1.pkg`.

- block records checked: **626**
- exact SHA-1 matches: **626 / 626**
- mismatches: **0**

Therefore, for this real PS4 Tiger v24 sample, `D1BlockEntry.sha1[20]` is **CONFIRMED_BINARY** as the SHA-1 of the block's stored on-disk payload (`offset .. offset+size`) before decompression.

Regression artifact: `evidence/packages/ps4_arch_cabal_005b_1.block_sha1_verification.json`.

## 2026-09-03 — FileEntry middle metadata byte is a reference-chain invariant

The unknown byte `entry_b[23:16]` was compared across all 209 same-package reference edges. It is preserved across **209 / 209** local links, with zero mismatches. This includes every known GPU header/data pair and every texture two-hop chain.

Examples:

- `32:7(mid=21) -> 1:7(mid=21)` — 61
- `32:7(mid=10) -> 1:7(mid=10)` — 59
- `32:1(mid=15) -> 65:1(mid=15) -> 5:1(mid=15)` — 19 chains
- `32:1(mid=14) -> 65:1(mid=14) -> 5:1(mid=14)` — 9 chains
- `32:4(mid=15) -> 1:4(mid=15)` — 11
- `32:6(mid=15) -> 1:6(mid=15)` — 8

This makes the byte very unlikely to be arbitrary per-entry data. It behaves like resource-family / allocation / streaming metadata propagated along linked resources. Its exact meaning remains **UNKNOWN**.

## 2026-09-03 — Header signature-area observation

The header field currently named `header_signature_offset` contains `0x800`. At exactly `0x800`, the package contains a dense 256-byte blob, followed by zero padding.

- offset: `0x800`
- observed blob length: `0x100` / 256 bytes
- non-zero bytes: 255 / 256
- SHA-256: `14ab10e5ee661c17cf2166916cd143c7bc988c115e23b8aae2a86d4e92d6ee6e`

The location and size are **CONFIRMED_BINARY**. Calling it a cryptographic/RSA signature remains **SOURCE_DERIVED/HYPOTHESIS** until its verification scheme/key is identified.

## 2026-09-03 — ROI structured-tag class resolution

The external/shared `reference` values on `16:0` entries were compared against QuickTag's version-specific `CLASSES_DESTINY_ROI` registry rather than a D2 or TTK registry.

Resolved in the canonical Cabal sample:

- `0x80801AD7` = `s_technique` — **136 entries**
- `0x80801BD9` = `s_expensive_light` — **1 entry**

Unresolved for ROI:

- `0x80800861` — 8 entries. QuickTag names this `s_pattern_component` in its **TTK** class table, but the ROI table uses `0x80800715` for `s_pattern_component`; therefore the TTK name is **not promoted** for our ROI sample.
- `0x80801AF2` — 1 entry, no ROI mapping found in the current QuickTag class registry.

This establishes that at least 136/146 structured tags in `arch_cabal` are shader/material **technique** tags and one is an expensive-light tag.

## 2026-09-03 — Dedicated ROI PS4 Texture2D header identified

QuickTag's current `TextureHeaderRoiPs4` parser resolves the canonical sample's `32:1` stored-size question: the struct ends at offset `0x3C`, exactly matching all 30 real Texture2D-header entry lengths. Source-derived layout: data size at `0x00`, two unknown bytes, packed GCN format at `0x06`, skipped/unknown region through `0x23`, `0xBEEFCAFE` at `0x24`, width/height/depth/array-size at `0x28..0x2F`, and three flag words at `0x30..0x3B`.

QuickTag also has a distinct ROI Xbox One header beginning with DXGI format + `tile_mode`, with `0xBEEFCAFE` at `0x2C`. This is recorded as a planned PS4↔Xbox differential validation target.

## 2026-09-03 — GitHub repository becomes canonical durable workspace

The private repository `lizardpeter/destiny-1` is now the durable source of truth. Runtime copies under `/mnt/data/Destiny1_Reversal/` are working mirrors for binary analysis and generated assets. The repository was initialized with safety ignores that exclude raw game package bytes, proprietary Oodle DLLs, compiled runtime bridges, caches, and bulk generated exports.

During migration, stale documentation was corrected before commit: the Xbox corpus is no longer marked pending mount, Oodle decompression is no longer treated as a blocker, the Xbox texture tail is retired as an unknown, and subtype 7 is promoted from loose hypothesis to `STRONGLY_SUPPORTED` ConstantBuffer role while retaining the neutral project name `GpuSubtype7`.


## 2026-09-26 — PS4 executable/code-graph track established

Executable reversal was explicitly separated from the Rust game repository and
made part of this canonical Destiny reversal workspace.

Public build evidence currently closes:

- CUSA00219 01.29 decrypted eboot SHA-256 is publicly reported as
  `7271fcb926401df8defb126cb8eb2b247134138b81e401bbacb2ab60791b795`.
- CUSA00219 01.33 is represented by an owner-dumped, unmodified shadPS4
  compatibility report.
- Multiple 01.33 emulator mappings crash in the Graphics Heartbeat thread at
  different absolute addresses but normalize to `eboot+0xFAAF4`.
- A verified 01.29 dump independently reports the same relative offset from a
  different load base. This is retained as a relocation-stable runtime anchor,
  not a proven function identity.

New code-side tooling now covers:

1. exact executable fingerprinting and SELF/ELF structural intake;
2. embedded ELF64/program-segment recovery;
3. offset-stable printable-string extraction;
4. Ghidra export of functions, exact body ranges, calls, imports, strings/xrefs;
5. per-function exact instruction-byte and mnemonic-sequence fingerprints;
6. graph-native deterministic node/edge normalization;
7. conservative promotion into the durable knowledge schema;
8. cross-version function matching with explicit proof tiers.

No retail executable bytes are committed. The immediate next evidence target is
any already-decrypted D1 PS4 executable from a known build; 01.29 is sufficient
to begin code-side function recovery while 01.33 remains the canonical final
target.


## 2026-10-12 — Global channel source of TFX opcode 0x4B closed; channel names recovered

Executable side (CUSA00219 01.33, angr decompiles under
`reconstruction/.../engine/graphics/decompiled/`):

- `frame_setup` 0x80AA80 points render-context `ctx+0x13F0` (the table RoI TFX
  opcode 0x4B indexes) at `renderer+0x18958`.
- `global_channels_copy_to_renderer` 0x8162D0, called each frame from
  `renderer_frame_prepare` 0x7ECBC0, fills that array from the global channel
  store `g_26f1fc0` (vec4 x count `g_26f1fc8`, 0x1000-byte heap
  "Extracted global channel data", allocated by 0x815420).
- Defaults come from the GlobalChannelDefaults tag (`g_26f1ff0`, loaded by
  0x8154E0): +0x08 hash array, +0x18 vec4 defaults — the same layout already
  closed by `tools/d1_global_channel_defaults_decode.py` for tag `80AE4005`.
- Accessors: `global_channel_get` 0x816100, `global_channel_set` 0x816170
  (honours override bits `g_26f1fcc`), `global_channel_find` 0x816240 (hash ->
  index, linear search of the tag's hash array).
- Runtime writers found so far: `c_sun_manager` (RTTI typeinfo 0x1949590,
  vtable 0x1949560, base `c_game_system_interface`). Slot 2 (0x8B1F10) resolves
  eight channel indices by hash; non-virtual updates 0x8B2020 (directions),
  0x8B23F0 (intensity fade by kind-2 volumes) and 0x8B2850 (shadow mode) run
  every frame from `lighting_frame_update` 0x7EBFC0.

Hash function: `0x5C579DFA` (a c_sun_manager key) is FNV-1 32 of
`sun_light_direction`, a string present verbatim in the binary. Dictionary
preimages then name 52 of the 100 channels in tag `80AE4005`
(`evidence/generated/d1_global_channel_names.json`,
`tools/d1_global_channel_names.py`). For the 0x4B frontier:

| index | hash | name | status |
|---|---|---|---|
| 0x11 | 90745795 | sun_color | STRONGLY_SUPPORTED |
| 0x28 | 1191B30B | — | UNKNOWN |
| 0x30 | E9EE5E9C | sun_transmission_color | STRONGLY_SUPPORTED |
| 0x60 | 0AD675E2 | lighting_cinematic_override | STRONGLY_SUPPORTED |

Not yet closed: who writes `sun_color`, `sun_transmission_color` and
`lighting_cinematic_override` at runtime (candidates: the per-frame passes
0x815600 / 0x815790, which blend from tag/volume data). Index 0x28 stays
unnamed.


## 2026-10-12 — Recompilation boundary: firmware import surface vs. shadPS4

`tools/eboot/d1_import_surface.py` -> `evidence/generated/d1_import_surface.json`
(shadPS4 checkout `e0a46675`, 2026-10-11).

Game-shipped code to recompile: `eboot.bin` plus two decrypted modules from
`sce_module/` — `libc.prx` (exports `libc`) and `libSceFios2.prx` (exports
`libSceFios2`). 165 eboot imports and 8 libc imports resolve to these and need
no reimplementation.

Firmware surface (unique library+NID across all three): **557 imports, 19,710
direct call sites**.

| status vs shadPS4 | imports | call sites |
|---|---|---|
| implemented | 444 | 19,376 |
| trivial body (stub or one-line accessor; heuristic) | 72 | 196 |
| not registered | 41 | 138 |

- libkernel dominates: 221 imports, ~18,500 call sites (mostly pthread mutex /
  cond). All but 7 are registered in shadPS4.
- Not registered: PSN social extras (Facebook SNS + dialog, in-game messaging,
  GameCustomDataDialog, coredump) and 13 `libSceLibcInternal` C functions used
  by `libSceFios2.prx` (printf, vsnprintf, time functions) — the latter map
  directly onto host libc.
- Graphics: only 15 `libSceGnmDriver` imports (shader-stage setters,
  default-state init, submit/flip). Command buffers are built by Gnm code
  statically linked into the eboot, so a recompilation needs a PM4 + GCN
  shader translator (shadPS4's `video_core` is the reference), not more HLE.
- `call_sites` counts direct calls into PLT stubs only; submit/flip are called
  through pointers and show 0. The eboot total (31,219) matches the
  independent capstone call index exactly.


## 2026-10-12 — GPU side of a recompilation: PM4 packets and GCN shaders vs. shadPS4

shadPS4 checkout `e0a46675` (2026-10-11).

### PM4 command packets (`tools/eboot/d1_pm4_emitters.py` -> `evidence/generated/d1_pm4_emitters.json`)

The statically linked Gnm builders sit in `0xF7C000–0xF88000` (draw/dispatch
command buffer) and `0x1005800–0x1005B00` (constant-engine buffer), and are
called from Bungie's renderer around `0x7DF000–0x7E3000`. They write
**25 distinct type-3 opcodes**; every one has a handler in shadPS4's Liverpool
command processor.

- `SET_PREDICATION` is only logged as unimplemented by shadPS4, but its two
  builders (`0xF809F0`, `0xF80A80`) have no direct callers.
- No indirect draws/dispatches, no `INDIRECT_BUFFER` (submission goes through
  `sceGnmSubmitCommandBuffers`), no async compute queue: dispatches go on the
  graphics ring (`DISPATCH_DIRECT` with the compute shader-type bit).
- Sub-modes checked by hand: `WRITE_DATA` always uses dst_sel 2 (memory) with
  `wr_one_addr = 0`, both supported. `DMA_DATA` uses caller-chosen src_sel with
  dst_sel memory or GDS; shadPS4 handles every pair except GDS→GDS. The
  fence helper at `0xF80AE0` fills memory from immediate data (src_sel DATA).
- Explicit `EVENT_WRITE` types seen at call sites: 0x2C, 0x2E, 0x31 (cache
  flush/partial-flush events; logged and ignored by shadPS4). Draw builders
  append EVENT_WRITE 0x35.

### GCN shaders (`tools/eboot/d1_gcn_isa_census.py` -> `evidence/generated/d1_gcn_isa_census.json`)

Corpus: every native shader payload (FileEntry type 1, subtypes 8, 9, 11, 12,
all ending in an `OrbShdr` footer) in the 49 package families the repository
already references — 14,849 entries, **13,692 unique shaders**, 2,525,868
instructions. Stages: 9,046 pixel, 4,545 vertex, 49 hull, 34 local, 18 domain.
Blocks were decoded with the project's Oodle 3 pipeline (exact raw-length rule)
using a scratch-only DLL; no DLL or shader bytes were committed.

- Decoding is exact for all 13,692 shaders: each consumes its OrbShdr code
  length and ends in `S_ENDPGM`. The decoder agrees instruction-for-instruction
  (170/170) with the two independent gfx700 disassemblies already in
  `evidence/generated/`.
- **129 distinct opcodes; all 129 are translated by shadPS4** (names and
  aliases taken from its own opcode tables, e.g. `V_CMP_LG_I32` = `V_CMP_NE_I32`).
- Heaviest use: V_MUL_F32, V_MAC_F32, V_MOV_B32, S_WAITCNT, V_INTERP_P1/P2,
  IMAGE_SAMPLE. Less common but present: DS_SWIZZLE_B32 (453 shaders),
  V_READLANE/V_WRITELANE (241), cube-map ops (1,260), tessellation stages.
- Not covered by this census: operand-level limits (export/render-target
  formats, image formats, MIMG modifiers) and the fetch shaders Gnm generates at
  run time; the 49 families are a sample of the game, not every package.


## 2026-10-12 — CPU side of a recompilation: x86-64 portability census

`tools/eboot/d1_x86_portability_census.py` -> `evidence/generated/d1_x86_portability.json`.

The PS4 CPU (AMD Jaguar) is x86-64, so the game's machine code can run
natively on a PC; a recompilation is relinking plus patching the places where
console and host differ. Function ranges come from each module's
`.eh_frame_hdr` FDE table (exact starts and lengths), minus the clang jump
tables that the PS4 toolchain places inside `.text`.

- **Functions:** eboot 54,533 (18.4 MB of code), libc.prx 1,999,
  libSceFios2.prx 649 — 57,181 in total. (The earlier prologue-scan estimate
  of ~38k missed frame-pointer-less leaf functions.)
- **AMD-only instructions:** no SSE4a (EXTRQ / INSERTQ / MOVNTSS / MOVNTSD)
  anywhere, so nothing faults on Intel hosts.
- **Precision differences:** 1,789 VRSQRTPS and 315 VRCPPS (all eboot). They run
  everywhere but give different low bits on Intel than on the PS4; shadPS4
  rewrites exactly these two to AMD-accurate sequences on Intel hosts.
- **TLS:** 2,542 `mov r64, fs:[0]` thread-control-block loads in the eboot; no
  other FS-relative operands. A recompile must redirect these (shadPS4 patches
  the same idiom).
- **No direct system calls** in game code (the earlier linear-sweep hits were in
  `.rodata`): every OS interaction goes through the imported firmware functions.
- **Timing / CPU identification:** 1,199 RDTSC + 1 RDTSCP (must agree with
  whatever `sceKernelGetTscFrequency` reports), 4 CPUID in one detection routine
  at `0xF12082`. 169 `int 0x41` and 180 `int3` sit on assert/debug-break paths.
- **Host CPU baseline:** ~565k VEX-encoded (AVX-128) instructions, BMI1
  (BEXTR register form ×2,492, ANDN, BLSI, BLSR, TZCNT), MOVBE ×255, LZCNT, POPCNT.
  No F16C, AES, CLMUL, and none of the instructions Jaguar lacks (AVX2, FMA3,
  FMA4, XOP, TBM) — that zero also shows the sweep stayed in real code. In host
  terms the code needs an Intel Haswell / AMD Zen class CPU or newer.
- **Indirect control flow:** 16,625 indirect calls and 2,677 indirect jumps.
  Irrelevant for an x86-64→x86-64 relink; they are the hard part only if the
  code were lifted to C or another architecture.


## 2026-10-12 — Native prototype boots Destiny 1 to the title screen (`native/`)

`native/` is a new Linux x86-64 program (`d1-native`) that runs the original
01.33 eboot and the two game-shipped modules as native code: an ELF-SCE loader
and linker, host implementations of the firmware functions it needs, and a null
GPU. Details in `native/README.md`.

What happens on a run (60–90 s, headless, no network):

1. Linking: 3,292 imports resolve to the game modules, 262+ to host code, the rest
   to logging stubs that return 0. 2,542 `fs:[0]` TCB loads are retargeted to GS.
2. `libSceFios2.prx` and `libc.prx` module_start succeed; the eboot entry runs.
3. Start-up creates the engine's threads (job ×4, async_job ×4, Graphics
   Heartbeat, Wwise `AK::EventManager`/`AK::IOThread`, voice, file I/O, NP),
   initialises audio, video out and Gnm, reads `sku_config.txt`, opens
   `ps4_client_bootstrap_unp4_0`, `ps4_ui_startup_unp4_0` and
   `ps4_ui_bootflow_unp4_0`, and hides the boot splash.
4. The frame loop runs at ~31 flips/s; each frame submits ~54 auto-index draws
   (≈1.4 k PM4 packets) — the title screen.
5. With Cross pressed the bootflow advances and stops at the online gate.

Two crashes were fixed on the way:

- `eboot+0x5D479`: an allocation-tracking call-stack capture walks eight saved-rbp
  frames; guest calls now start from a self-referencing terminal frame.
- `eboot+0xFAAF4` in **Graphics Heartbeat** — the same offset reported by shadPS4
  users (2026-09-26 entry). The heartbeat waits for a GPU frame counter; while
  waiting it tries to steal a job (`0xFB860` → `0xFAAC0`), which dereferences a
  per-thread job-system context (TLS offset −0x1068 + 0x58, set only on job
  threads by `0xFAD30`). It is only reached when GPU end-of-pipe interrupts never
  arrive; with EOP fences and interrupts delivered the wait completes and the
  path is not taken.

### Engine logging recovered

Release builds keep every log call but have no threshold table, so all messages
are dropped. `0xE4D70(channel, level)` is the gate (threshold defaults to 5) and
`0xE4AA0(message_id, text)` the emitter; hooking both (`D1_GAME_LOG=1`) prints
the engine's own log. The `world_controller:state_manager` states are named by
the table at `0x1945340` (bootflow:media_check … bootflow:prepare_for_orbit,
character:signin, character:prologue, …).

Observed bootflow with no network:

```
bootflow:media_check -> bootload -> intro_screen_display -> start   (title, waits for Cross)
start -> platform_signin
  demonware: sceNetCtlGetInfo failed (80412104); create socket failed
  Prerequisite ENUM(6) failed for reason 'error.no_ethernet_link'
platform_signin -> cleanup (kick_to_bootflow_start) -> start          (loop)
```

DemonWare 48 (`D:\bungie\external_libraries\DemonWare\48\...`) is the transport
library; `sku_manager` reports sku_type 2 `north_america_digital`, base content
version `56578-1-3407992`.
