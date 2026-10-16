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

### Second gate: Bungie STUN during platform_signin

With `D1_NET=link` (interface up, real host UDP sockets, local PSN user
reported signed in, DNS refused) the ethernet prerequisite passes and
`bootflow:platform_signin` instead runs DemonWare's NAT discovery. It resolves
`stun1`–`stun8` under `signon.deadorbit.net` and `signon.gravityshavings.net`
(Bungie domains), cannot, logs `External STUN client failed`, and leaves with
`error.transport_method_invalid` → cleanup → `bootflow:start`. Every later
bootflow state (account_signin, bap_signin, investment_signin, profile_setup,
prepare_for_orbit) is reached only after this one, so reaching orbit needs
either a local stand-in for Bungie's sign-on / DemonWare / BAP services or a
client-side bypass of those states.

### Bypass investigation: world_controller state machine and the first three gates

`world_controller:state_manager` states (name table `0x1945340`, 37 entries):
bootflow:media_check, bootload, intro_screen_display, start, platform_signin,
platform_account_warnings, enumerate_content_rights, account_signin, eula, upsell,
email, confirm_account_transfer, content_check, content_install,
insufficient_content_space, illegal_dlc_media, queuing, package_registration,
bap_signin, investment_signin, profile_setup, prepare_for_orbit;
character:signin, character:prologue; cleanup; setup:orbit_loading, orbit,
activity_session_creation, matchmaking, activity_host_setup,
prologue_intro_loading, orbit_outro, activity_world_transition;
activity:initial_slice_set_loading, physics_join, in_world, watch_video.

- State-change reasons: 284-entry table built at start-up (`0x785650`), base
  `0x26CAF40`, stride 16 (`0x783960` maps index → name). `error.no_ethernet_link`
  = 143, `error.transport_method_invalid` = 144.
- Prerequisites: each state has a 38-bit prerequisite mask (`state+8`);
  `0x792CD0` walks it and calls `0x792ED0(state, n, ctx, &reason)` → 0 satisfied,
  1 pending, 2 failed (failure → `0x783EE0(cleanup, reason)`). ENUM(6) is the
  ethernet-link prerequisite (`0x7927B0`).
- platform_signin's own update (`0x79F310`) requires the DemonWare network start
  object (`g_2F66F68`, status 2 = started; `0x2EB340` / `0x2EBD40`) and the
  platform user's online flags; otherwise it requests cleanup with
  `transport_method_invalid` via `0x784E50`.

With `D1_BYPASS=prereq,transport` and `D1_NET=link`:

```
platform_signin -> platform_account_warnings -> enumerate_content_rights -> account_signin
  networking:signon: _retrieving_platform_token
  POST https://auth.api.sp-int.ac.playstation.net:443/2.0/oauth/token   (not sent)
  retrieveSCEAccessToken returned result code 715 -> signon _error
account_signin -> cleanup (error.bungie_server_connection) -> start
```

account_signin is the Bungie sign-on service (`c_signon_service_client`): it needs a
PSN OAuth token, then a sign-on request to Bungie. The states after it
(bap_signin, investment_signin, profile_setup) load the account, characters and
inventory from Bungie's BAP / investment services, and activities run against a
remote activity host (`c_investment_bap_message_client_to_bap_get_activity_host_proxy_request`,
`..._activity_host_to_world_server_response`). The client does contain offline /
host-migration session code (`Creating offline host migration session`), so
whether it can host a world locally is the next question to answer.

## 2026-10-12 — First rendered frames: temporary renderer in d1-native

`native/renderer/` builds shadPS4's `video_core` and `shader_recompiler` (from an
external checkout, tested at `e0a46675`) into d1-native with
`-DD1_RENDERER_SHADPS4=ON -DSHADPS4_DIR=...`. It is a stop-gap until the planned
Rust/Vulkan renderer; it makes the combined binary GPL-2.0-or-later, and none of
shadPS4's source is copied into this repository apart from the Gnm command
builders and flip patching in `renderer/glue/d1_renderer.cpp`.

What d1-native supplies in place of shadPS4's emulator core
(`renderer/glue/core_glue.cpp`, `renderer/shim/`):

- Guest memory: the guest runs natively, so guest addresses are host addresses.
  Direct/flexible mappings are reported to the rasterizer (`MapMemory` +
  `RegisterMemory`); GPU writes back to guest memory go through `/proc/self/mem`
  so they do not trip write tracking.
- CPU write tracking: the rasterizer write-protects pages it caches; d1-native's
  SIGSEGV handler hands such faults to it first. Kernel reads into protected pages
  would fail with EFAULT, so `sceKernelRead`/`Pread` touch the destination first.
- Flips: the game's last DCB of a frame ends in a 64-dword `prepareFlip` NOP
  (`0xC03E1000`), which is patched into a label write plus a flip marker; the
  command processor raises GfxFlip in stream order, d1-native updates flip status
  and events, and optionally saves the frame (`D1_FRAMES=<dir>`,
  `D1_FRAME_EVERY=<n>`).
- Headless Vulkan: a window-system-"Headless" instance, no swapchain. Tested on
  lavapipe (llvmpipe, Vulkan 1.4) in the container.

One game-side fix was needed: `eboot+0xFAAF4` again, now in the Graphics
Heartbeat's wait for the GPU frame counter (`0x7DD1CA`). While waiting, the
heartbeat calls `0xFB860` → `0xFAAC0` to run a pending job, which dereferences the
thread's job context (TLS slot read by `0xFC520`, set only for job-system threads
by `0xFAD30`, whose only writer is `0xFC540`). The heartbeat is not a job thread,
so the path crashes whenever the GPU is behind. A guard hook on `0xFAAC0` returns
"no job run" when the context is null; the caller then sleeps 300 µs and polls
again. This is very likely the same crash shadPS4 users report for 01.29/01.33.

Result on lavapipe (software rendering, ~13 frames/s): the Bungie logo, the
animated DESTINY title, and — without network — the "ATTENTION / No internet
connection detected … canary" dialog (`error.no_ethernet_link`), all rendered
correctly at 1920×1080 by the game's own shaders.

### Window and input

The renderer build now opens an SDL2 window (X11/Wayland) and presents each
flipped video-out buffer through a Vulkan swapchain, letterboxed. Keyboard and
SDL game controllers feed `scePadRead`/`scePadReadState`. Checked under Xvfb with
injected key presses: title screen ("PRESS ⊗ TO PLAY") → Enter → platform_signin →
no-network dialog → Enter → back to the title.

### Backend routing (`D1_BACKEND`)

Decision: the online services are to be replaced by a backend server of our own,
run on the same machine for testing and on another machine later, never the real
services. d1-native now takes the server's address from `D1_BACKEND`:

- DNS: names under `deadorbit.net`, `gravityshavings.net`, `bungie.net`,
  `bungie.com`, `demonware.net`, `playstation.net` and
  `sonyentertainmentnetwork.com` resolve to the backend; everything else is
  refused. The eboot's own host list: `signon.{deadorbit,gravityshavings}.net`,
  `stun1-8.signon.{deadorbit,gravityshavings}.net`, `stun.{us,eu,jp,au}.demonware.net`,
  `dm-partnernet.upload.deadorbit.net`, `www.bungie.net`, `help.bungie.net`,
  `auth.api.%s.ac.playstation.net/2.0/oauth/token`.
- HTTP(S) through libSceHttp is sent as plain HTTP/1.1 to the backend
  (`D1_BACKEND_HTTP_PORT`, default 8080) with the original `Host` header and an
  `X-D1-Original-URL` header; the response is returned to the game as is.
  Since libSceHttp is HLE, TLS never comes into it.

First request received by a probe server (with `D1_BYPASS=prereq,transport`):
`POST https://auth.api.sp-int.ac.playstation.net/2.0/oauth/token`, form-encoded
`grant_type=authorization_code`, the game's PSN client id/secret, the
authorization code from `sceNpAuthGetAuthorizationCode`, scope
`openid,openid:duid,psn:s2s`. With an error answer the game retries every ~9 s.
This is the first thing the backend must answer (an OAuth token response).

### Activity host: what the client contains (first pass)

- World-controller modes (`0x751EE0` → `0x78F660`, names at `0x19458E0`):
  `SWC`, `DWC`, `EWC` (`c_editor_world_controller`), `OWC`
  (`c_online_world_controller`), `AHWC` (activity host). The retail client builds
  only the EWC and OWC objects (`0x78F570`: slots 2 and 3); AHWC has a name and a
  slot but **no implementation in the client** — the activity host's own logic
  ships only on Bungie's servers. The status line "ACTIVITY HOST RUNNING OUT OF
  PROCESS (AHWC)" (`0xAE681D`) is debug text for that mode.
- Mode choice at start-up (`0x52C020`): a stripped override (`0x1CF60` → −1), then
  EWC if the start-up flag read by `0x239B70` is set, otherwise OWC. Forcing EWC
  (`D1_WORLD_CONTROLLER=editor`) runs the main loop but never starts the bootflow
  or video; the editor controller presumably waits for tool commands. Not a
  shortcut to offline play.
- The command line parser (`0x1730`) still accepts `/init:<file>.txt`, `/user:`
  and `/machine_name:`, but `console_execute_commands_from_buffer not supported in
  release` (`0x6E95F0`) — init files cannot run console commands in this build.
- What the client simulates itself: AI actors, path finding, perception, the
  AI spawn system, squads and encounters (`ai: actor executor update job`,
  `c_ai_spawn_system`, `encounter manager`), player spawning, physics, entity
  authority hand-off between peers (`simulation_queue_entity_claim_authority`,
  `authority-over-domain`). It loads activities by name from registered maps
  (`0x7A3B70`: "could not find a registered Orbit or bootstrap map").
- What goes through the activity host: the 50+ `client_to_activity_host_*`,
  `activity_host_to_client_*`, `bap_to_activity_host_*` and `*_world_server_*`
  message types — session/reservation management, activity start-up
  ("activity host startup request/response"), authoritative counts
  ("critical squad … alive count client vs auth"), and the world server's item,
  kill, progression and talent-grid records.

Working conclusion: the combat simulation is client-side, so a local backend does
not need to run the game world. It needs to (1) answer the services (sign-on, BAP,
investment) and (2) implement the activity host's *protocol role* — session
start-up, reservations, authoritative bookkeeping and rewards — which is message
handling rather than world simulation. How much game logic hides inside (2)
(mission progression, objective state) is the next thing to measure, by decoding
the activity host message payloads.

### Frame rate unlock

The 30 fps cap is the game's own limiter, not the flip rate or vblank (raising the
emulated vblank to 120 Hz changed nothing). `0x593F00` builds the "time control
config globals" (pointer `0x26BCD08`, 0x48 bytes) from a config of float seconds:
`+0x08` frame period µs (33366 = 29.97 fps), `+0x10` 15000, `+0x18`…`+0x30`
vblank-derived periods (16683 µs = 59.94 Hz), `+0x38` integer target fps (30).
The main loop (`0x594460`) waits for the next period; `0x593890` (frame time in
seconds) and `0x5938B0` (fps) derive from `+0x08` and feed `0x591710`.

`D1_FPS=<n>` (hook on `0x593F00`) rewrites `+0x08` and `+0x38`. Measured with the
null GPU: 60 → 64 flips/s, 120 → 127, 240 → 251 (30 s runs including start-up).
The intro screen lasts 6.9 s at both 30 and 60 fps, so UI timing is wall-clock
based. Whether in-world simulation (movement, physics, animation) stays correct
needs testing in a world.

Low latency (renderer build): Mailbox presentation by default (`D1_PRESENT`), and
input is sampled every 1 ms.

Note: one of ~10 runs with stdout piped through a timestamper never started the
bootflow (main loop ran, no state changes). Not reproduced since; watch for a
start-up race.

## 2026-10-12 — Replacement backend: sign-on, content manifest, package registration

`backend/` (Rust, `d1-backend`) answers the online services; d1-native routes them
to it (`D1_BACKEND`). The bootflow now runs, with our own server only, through
`account_signin`, `content_check` and `package_registration` to `bap_signin`.

- **PSN token**: JSON with `scope` and an `id_token` (JWT-shaped, unchecked); used by
  DemonWare's `bdAuthPS4::handleGetAccessTokenReply` (`0x122C070`).
- **Sign-on** (`POST /SignOn?platform=orbis&build=56578.17.04.12.1251.evil`):
  protobuf both ways. Bungie messages are "schematized": a generic decoder
  (`0xA2020`/`0xA17D0`) driven by tables of 23-byte field records
  `{u32 field, u8 kind|type, u8 pad, s8 flag offset, u32 size, u32 max count, u64
  nested schema/default}` (kind: 0x00 required, 0x10 optional, 0x20 repeated, 0x30
  custom callback; type 0 varint, 2 fixed32, 4 bytes, 5 string, 6 message). Schemas
  can be dumped automatically. Response (`0x1910CC0`): field 1 type (0 success,
  1 denied/offline, 2 queued, 3 offline), 2 success {session keys, security token,
  expiry, next server IPv4/port}, 4 client_config {cookie, social id, engine config
  stream}, 5 silo id, 6 content version, 12 server clock, 13 environment.
- **Engine configuration** rides in client_config field 3: `u32 0x123456`, then
  `{u32 id, value}` pairs ending with id 0, applied by a 40 KB switch (`0x1033F80`)
  into the "Engine Configuration" global. Id 100 = content manifest URL, 101 =
  expected manifest GUID, 102 = URL suffix.
- **Content manifest** (`0x2B0980`, schema `0x1911470`): signature-checked only
  when the byte at `0x18DC974` is set; d1-native clears it with `D1_BACKEND`.
  Field 3 lists the patchable packages that `package_registration` (`0x79E740`)
  registers; registration (`0xD6300`) verifies each package header's own RSA
  signature and requires header u16 `0x04` == entry field 3 (package id) and header
  u64 `0x08` == entry field 4, so the backend reads both from the package files.
  With 405 packages (newest generation of each id, English) registration passes.
- Packages are staged locally as sparse files holding only header and tables
  (registration reads 0x140 bytes of each); full files are fetched as the game
  reads them (`D1_FILE_LOG=2` logs the first read of every MiB).

Next gate: `bootflow:bap_signin` — the BAP protocol (address from the sign-on
response; nothing has connected to it yet).

## 2026-10-12 — settings file, v-sync and Discord presence

- `<data>/d1-native.cfg` (settings.cpp) holds window size, fullscreen, v-sync, fps and Discord
  options; env vars override. V-sync maps to the swapchain present mode: on = Fifo,
  off = Mailbox (default), off-tearing = Immediate. F11 / Alt+Enter toggle borderless
  fullscreen. Verified under Xvfb: 1600x900 window, fullscreen start (1920x1080 drawable),
  F11 back to windowed, present mode logged.
- Render resolution: reporting 3840x2160 from `sceVideoOutGetResolutionStatus` still gets
  1920x1080 video-out buffers and render targets, so the output scales to the window and the
  internal resolution needs a patch in the engine's render-target setup (to find).
- Discord Rich Presence speaks Discord's local IPC protocol directly (handshake op 0, then
  SET_ACTIVITY op 1 frames on `discord-ipc-N`) from a worker thread; no SDK. Activity text
  comes from the world-controller state machine (hook on the transition step 0x783AC0,
  state at obj+0x1B0, names at 0x1945340). Verified against a fake IPC server: handshake,
  then "At the title screen" → "Signing in" as the bootflow advanced. Needs an application id.

## 2026-10-12 — Windows build

- d1-native, the temporary renderer and d1-backend cross-compile for Windows (llvm-mingw;
  Rust x86_64-pc-windows-gnullvm). Verified under Wine (+ lavapipe): boots to
  `bootflow:bap_signin`, renders the Bungie logo and Signing In screen, starts its own
  backend from its folder. Details in native/README.md.
- Single-folder layout: d1-native.cfg / logs / data/ / game/ next to the executable.
- Start-up hang root cause: `sceNpRegisterStateCallback` returned 1; the NP toolkit
  (0xFA7E10) treats non-zero as failure, its thread (0xF90B30) tears down and signals the
  main thread, which waits forever if it had not started waiting yet. Returns 0 now.
- ENGINE OOM in content_check root cause: `sceAppContentGetAddcontInfoList` (called by
  0xBBE60 as count-then-fill) was a logging stub that never wrote the count, so the add-on
  count was stack garbage (once 862 million entries x 0x18 = 19 GB, heap id 45). Implemented
  with the other AppContent / PlayGo / DiscMap calls that return results through pointers.
- LLVM's `__builtin_setjmp` restores a wrong frame pointer with the Win64 frame layout;
  thread exit uses a small assembly entry/exit pair instead (`d1_call_guest_exitable`).

## 2026-10-12 — bap_signin: package generations, POSIX sockets, BAP transport

- **bap_signin** (handler vtable 0x1945D90, update 0x799A70, sub-step at handler+0x30) runs
  21 steps: unload bootstrap-unpatchable, load the package sets "client_bootstrap_patchable"
  (3), "client_startup_globals", "investment_assets"/"investment_globals" (6, 7) through the
  package manager at 0x26C93B4 (8 x {state, handle, tag}; 0x752F10 request, 0x7536F0 status),
  then connects to BAP (0x799FA0). Sub-steps are logged ("bootflow: bap_signin step a -> b").
- **Stuck at step 12** (loading set 3, tag 0x80AE4000): newer package generations keep
  blocks in older generation files (block `patch_id`): ps4_client_bootstrap_patchabl_0172_5
  has 150 blocks in _5 and 46 in _0/_1/_2/_4, its first entry in _0. The loader only opens
  files the content manifest registered, and the backend listed only the newest generation.
  Listing every generation (English + neutral: 1392 of the client's 1500 slots) fixes it;
  steps 12-21 then complete. (Global resource loads go through the simulation queue as event
  0x4E, applied by 0x34B920; D1_BYPASS=localres forces the local path at 0x34A278 but is not
  needed.)
- **BAP address**: sign-on field 2.6 is the IPv4 bytes as a little-endian u32 (127.0.0.1 =
  0x0100007F); big-endian showed up as 1.0.0.127.
- **POSIX sockets**: BAP (c_network_server_bap_connection, 0xB2Exxx-0xB33xxx) and DemonWare
  use libkernel `socket/connect/select/recv/send/setsockopt/close`, which were logging stubs
  returning 0. Implemented (FreeBSD constants, BSD sockaddr, fd_set of 64-bit words; `close`
  routes sockets to the network layer).
- **BAP transport** (states: _acquiring_server, _connecting, _listening, _channel_starting,
  _authenticating, _setup_primary_register_subscriber, _setup_primary_register_relay_client,
  _connected): TCP; every message is an envelope `u8 version (1), u8 kind (1 = plain,
  0/2 = signed/encrypted), u32 big-endian size` (0xB2FA10), then a signature (0xB2FC70)
  and payload. In _channel_starting the client queues a channel-startup request (0xB336F0:
  type 5, message 0x1E, a key "DESTIN\x94\x15" + 120 random bytes) and polls recv(6) for
  envelopes; nothing is sent yet (update_sending 0xB2F3D0). Next: the send path and the
  server's first message.
- Research tools: D1_COUNT=<offsets> counts calls to game functions; D1_FILE_LOG=3 logs
  every read; d1-native waits for the backend's port before booting.

## 2026-10-13: BAP authentication, investment sign-in, profile setup

- **Secure hello (0x19 -> 0x1A)**: payload `u32 BE L | IV[16] | AES-128-CBC/PKCS#7 | HMAC-SHA256[32]`,
  MAC over `[0, L-28)` (length prefix included). AES key = sign-on success field 2, HMAC key =
  field 3 (0xB34F70). Plaintext = 12-byte nonce + 16-byte channel key (0x6CF80).
- **Channel**: AES-128-GCM (libtomcrypt; 0x6CD20 encrypt, 0x6CE20 decrypt), no AAD, 16-byte tag,
  nonce per direction incremented little-endian after each message. The client flips byte 11 of
  its *send* nonce. Kind-1 envelope = tag + ciphertext.
- **Message ids** come from vtable slot 0 of each `c_investment_bap_message_*` class (slot 1 =
  header class). 121 queuez_register, 302 register_relay_client, 12/14 (un)subscribe and 250
  echo all take empty responses (`id + 1`).
- **Response matching (0xB30960)**: a response is matched only against the *oldest* outstanding
  request in each send queue. One unanswered message (e.g. 32 user_message or 21
  purchased_offers) blocks every later reply in that queue. Answer everything, in order.
- **World server messages (10/11)**: MSB-first bitstream `u16 id | struct | has_extra (u16 len +
  bytes)`. The structs are serialized from the engine's runtime type descriptors (reader
  0x101EB30, kind handlers 0x19131B0). backend/data/investment_schema.json is a dump of the
  message table, the family slot table and every reachable type, taken from the running
  client with gdb.
- **Sign-in**:
  - 0x1F7 response: {status, account id (must be non-zero, kept in the account slot), i32,
    i32, family-5 root object whose soid must be 0x7FFFFFFFFFFFFFFF}.
  - 0xCE {family, root} subscribes; its response's extra blob is a queuez update (same format
    as notification 123) carrying the family baseline. Family 3 = account summary
    (0x80801951 + up to 10 character summaries 0x80801954).
  - Family 4 (profile, 0x80801803) is pushed as notification 123 once the client has moved it
    to replication state 2. investment_signin waits for it (account slot ready flag, 0x586970).
- **Queuez update**: `u32 BE count | per family: u32 type, u64 root, i32 version, u8 flags
  (bit 0 baseline), u32 n | per object: u32 type hash, u64 soid, u32 len, bitstream`. The first
  member of each object must be its soid.
- **profile_setup**: brightness / screen bounds / third screen. Each finishes with a
  "completed" event (0x7A02E0). `D1_BYPASS=profile` completes them for headless tests.
- **Renderer**: shadPS4 lacked V_CMP_CLASS with a quiet-NaN-only mask. Fixed by
  native/renderer/patches, which are applied to copies in the build tree.
- **Status**: reaches bootflow:prepare_for_orbit with a stable BAP connection.

## 2026-10-13 (later): character select to orbit

- **prepare_for_orbit** loads the orbit package sets, then enters character:signin.
- **character:signin** (0x7A1AF0):
  - With no characters it goes to step 6, the creation screens (UI 0x1D).
  - Otherwise it goes to step 5, select (UI 0x1C).
  - It finishes when the account slot has an active character. That is the profile's +0x68
    id, backed by a family-4 slot-1 object 0x80801743 (0x586510 / 0x586970).
- **Character creation**: 0x1F5 request 0x80801860 {race/gender/class (3 x i8), appearance
  0x8080181A, 17-byte block}. Response {status, character id}.
  - The backend stores the request (`<data>/backend/account.json`), answers with the new id
    and pushes account + profile baselines.
  - The summary (0x80801954) and the active character (0x80801714) both start {soid, rgc,
    appearance}.
- **Voice**: the game finds voice port records by the ids sceVoiceCreatePort returned and
  dereferences the lookup unchecked (0xB49210). The ports need real ids.
- **PSN web API**: d1-native forwards every libSceNpWebApi request to the backend as
  `<METHOD> /npwebapi/<group><path>`.
  - The fireteam session needs sessionInvitation `POST /v1/sessions` -> {"sessionId"}.
  - Presence and friend-list calls get `{}`.
- **More BAP**:
  - 23 account id translation: bitstream, u16 count, from/to types (7 platform id, 0xFF
    membership id). The reply repeats the request, then appends the to-list.
  - 18 client config: protobuf 0x15B67E0, {1 cookie, 2 id}.
  - 12 subscription {u8 family, u64 BE root}: acknowledge, then push that family's baseline.
    Families 0 and 2 (rooted at the account) get empty baselines for now.
  - 0xCD returns the family-5 root like 0x1F7.
- **Status**: with a character on the account, the headless run reaches setup:orbit (the
  Director).

## 2026-10-13 (evening): activity host, into the prologue world

- **AH discovery**: BAP 16 → 17 (16 bytes: echoed u64 id, IPv4 network order, u32 BE port).
  The client opens a second BAP connection ("FAH") with the same handshake.
- **Host startup**: request 6 kind 3 (0x55BD10: raw 0xE0C-byte struct, two length-prefixed
  blobs at +0 and +0x202; the first holds the activity index and insertion point as i16
  +0x8000). Response 7: kind 2, u64 BE AH id, 0x80 bytes.
- **Messages**: client → host is notification 8 (header + u64 target id; payload
  `[1][u32 type][u32 len][u32 0][data]`). Host → client is **bap_to_client 9** (base header,
  payload `[1][u64 id][u32 type][u32 len][data]`, decoder 0x55F2C0). Notification 100 is
  only relayed by the client to the service named in its header. Host types are dispatched
  through 0x1910480; payloads are engine-type bitstreams (0x2A4AC0).
- **Join sequence** the client accepts:
  - 4 join result (echo identity, nonce must match, result 0)
  - 0 entity indices (384-word bitmask)
  - 11 membership. It is applied as an update (0x2C9AE0): a "present" bit, then 0x808009ED,
    with players (identity + properties block from the join request), valid-slot masks, and
    the host-tabulated region table (region 0 with the player's transition token 1)
  - 1 instance state (0x80800E76). It carries:
    - valid flag
    - bubble count (+0x10, must equal the scenario tag's +0x48 count: 22 for the prologue)
    - per-bubble slice-set index (+0x14, 0 = first)
    - activity checksum (+0x5C = u32 at scenario tag data +0xC: 0x8FE07299)
    - details +0x60, holding the activity index (+0x620), insertion point (+0x622) and
      scenario name (+0x628, "act_cosmo_m0_highway")
- **Keep-alive**: the client drops a host it hears nothing from for 20 s (connection +0x1EF8).
  Host type 27 (sync token, echoed in client type 28) every 5 s.
- **Purchase prerequisite**: the world transition evaluates `f[0x1A3] || f[0x1B8]` (scope-0
  flags), now set true in the profile overrides.
- **Result**: the world changes to act_cosmo_m0_highway, the initial slice set (PRV00.00)
  precaches and switches, and the player spawns (simulation authority is local; a unit is
  assigned).
- **Remaining gap**: loading task 9 (0x7965A0) also needs the current activity-mode
  reference (client reference type 0x10, byte +0x1AC). That reference still points at the
  Cosmodrome ambient activity's tag 0x80CD0C34 (value -1), not the prologue's.
  D1_BYPASS=spawn completes the task once the player has a unit. With it the client goes
  through physics_join into **activity:in_world**.

## 2026-10-13 (night): native keyboard and mouse

The game has no keyboard or mouse code (imports are only scePad* and sceImeDialog*;
"keyboard" in the binary is the on-screen keyboard and a crash-screen debug input). It
does have a clean input layering, reversed statically from the scePadReadState call site:

- **Pad**: `gamepad_poll_all` 0xAE1E0 -> `gamepad_poll` 0xAE0C0 (scePadReadState) ->
  `gamepad_state_update` 0xADC00. Engine gamepad state is 0xC0 bytes per pad (pad 0 at
  the global 0x1AD40F0): triggers +0/+1, per-button held counters, sticks as s16 at +0x44
  lx, +0x46 ly (up positive), +0x48 rx, +0x4A ry, touch points, motion.
- **Input abstraction** (`c_input_abstraction_game_system`, globals 0x273ED40, per player
  0x300 at 0x273EFE0 via 0x928560): `input_abstraction_update` 0x926910 copies the sticks,
  applies the per-player dead-zone mode and maps buttons to abstract actions. Default
  turn speeds per player: 2.0944 rad/s yaw (120 deg/s), 1.0472 rad/s pitch (60 deg/s).
- **Player control** (`c_player_control_game_system`, globals *0x273EB28, 0x1A0 per slot
  at +0x20): `player_control_update` 0x91EE90 builds each local player's unit action.
  `player_control_update_player` 0x91B500 does look and move: sticks -> floats (0x926320),
  southpaw/legacy swaps, response curves, look rate (0x928670: yaw = state[+0x2CC] x
  turn_speed[0], pitch = state[+0x2D4] x turn_speed[1]), aim assist, curve limits and
  zoom scaling (0xBD3740 magnification, 0xBD3A50 per-weapon look scale), ending with
  **action[5] = yaw_rate x dt, action[6] = pitch_rate x dt** (radians; +yaw turns left,
  +pitch looks up). Look is locked while player_control_globals +0xC bit 0 is set or game
  time is paused (0x591B30).
- An externally driven mode exists: with input state +0x2A0 set, +0x2C8/+0x2D0 are
  per-frame deltas (divided by dt in 0x928670) and the stick pipeline is skipped. It is
  what simulated input uses.

**d1-native mouse look** hooks 0x91B500 and, after the game's own math, adds raw mouse
counts x `mouse_sensitivity` (Source scale, 0.022 deg/count) to action[5]/action[6], scaled
by the same zoom slowdown the game applies to the stick (`mouse_zoom_scale`). The mouse
therefore skips stick quantization, response curves, turn acceleration, dead zones and aim
assist; a controller keeps working alongside. Counts come from SDL relative mode on raw
input without OS acceleration, accumulated by the 1 ms window loop and drained by the hook,
and counts older than 250 ms of not-running player control are dropped. Keyboard keys and
mouse buttons map to the PS4 buttons (README). Headless check (`D1_MOUSE_TEST=40,-10
D1_MOUSE_TRACE=1`, saved account, `D1_BYPASS=...,profile,spawn`): from activity:in_world
on, every player update adds -0.0307 rad yaw / +0.0077 rad pitch (sensitivity 2) with look
unlocked and no zoom.
Runtime check of the effect: the slot's desired facing (player_control_globals +0x20 +
slot x 0x1A0 + 0x18 yaw, +0x1C pitch) moves by exactly the injected delta every update
(yaw 0 -> 6.2525 -> 6.2217 ..., i.e. -0.0307 rad per frame wrapping at 2pi; pitch +0.0077),
so mouse counts reach the aim 1:1 with no smoothing or acceleration; mouse right turns
right, mouse up looks up.

## 2026-10-14: audio, unlimited frame rate, intro skip, and why the world is black

- **Audio**: the game opens one sceAudioOut port (1024 frames, 48 kHz, format 7 = float
  7.1 "std" order: L R C LFE side back) and Wwise mixes everything in software; no AJM
  codec instance is created through the intro cinematic. d1-native now plays that port
  through SDL (device downmix), paced by the device queue (~3 buffers).
- **Frame rate**: pacing and tick length share time-control +0x08. The main loop waits
  until last + period (`add rcx,[rsi+8]` at 0x594A3B); game_time (0x591710) runs
  elapsed / period ticks. `fps = 0` (default) NOPs the wait and sets the period to each
  frame's real duration (1-33.4 ms) just before 0x591710: one tick per rendered frame.
- **Intro cinematic**: character:prologue (0x7A1470) step 2 plays it on the cinematic
  player at 0x295C0A0; the game's own skip (Square/Triangle) is gated by world controller
  +0x2E39. `skip_intro` calls the stop (0x33E110) instead.
- **Loading cinematics** are suppressed by design for the prologue launch: the activity
  selection (*0x26BC068) is {kind 1, activity 164, insertion -1} at load (0x766750), so
  prologue intro playback / cinematic exchange / filler tasks are skipped.
- **Black screen in activity:in_world**: the game director (c_game_director, update
  0x8ED0F0) switches to camera type 5, c_dead_camera (vtable 0x1949ED0), every frame,
  because the local player's unit (local player table 0x273EB80 +0xC4, read by 0x9236D0)
  is -1. +0xC0 (player datum) is set; the player never gets a body. The null GPU still
  counts ~440 draws per frame (UI / loading layers), and the software-rendered frames
  are pure black (mean 0). Units are attached by 0x911C50 (player datum +0x644); the only
  caller passing a real unit restores a previous one (0x90E840), so the spawn path itself
  is next. Loading task 9 waits for exactly this unit; D1_BYPASS=spawn hides it.
- shadPS4 texture cache: an equal-address overlap where only the image type differs
  (a 32x32x32 RGBA8 volume where a smaller 2D image lived) hit UNREACHABLE; patched to
  treat it like a tiling-mode reuse (renderer/patches/0002).
- Test bench: lavapipe caps one allocation at 2 GiB and buffers at 4 GiB - 1, below
  shadPS4's 4 GiB sparse arenas (test builds use 2 GiB arenas); the game's BLOCK_DETECT
  thread (0x92A3D0) halts slow runs (D1_NO_BLOCK_DETECT).

## 2026-10-14: internal render resolution

The game never asks the system for a resolution (no Neo/Pro mode, sceVideoOutGetResolution
Status ignored): the GPU device init (0x7E40A0) hardcodes the display size as two
immediates, `mov [r13+0x28F8], 1920` (0x7E40D0) and `mov [r13+0x28FC], 1080` (0x7E40DA),
and everything else sizes from those fields. `render_resolution` (D1_RENDER_RESOLUTION)
patches both: at 2560x1440 video out registers 2560x1440 buffers and the title, UI and
loading screens render at full 2560x1440 with correct layout (the UI keeps its 1920x1080
reference canvas at 0x166EE18 and scales). 3D scenes at higher resolutions still need
checking on real hardware (the software test bench is too slow to reach them quickly).

## 2026-10-14: the player spawns (black screen fixed)

The dead camera came from a chain of three missing pieces of server-side state. With all
three supplied the local player gets a unit in activity:in_world and the director keeps
camera type 4 instead of the dead camera (5).

- **Player definition** (`can_spawn` 0x415700, first gate `0x1192B0(entity) == 0`): a
  player simulation entity's definition (+0x50) is a client reference of type 0xC (16 per
  world, content type 0x80802236, group key 0x4786C0E0 indices 5..20 in the prologue).
  0x1195F0 binds the entity to the reference whose 8-byte id at object +0x258 equals the
  id the entity was created with (+0x18 = membership properties @0xA0; with one player
  that is the character id). The id arrives as data of type 0x808022A5 (0x78 bytes:
  @0 0x80800540 {i32, u32, bool, bool, bool, i8, i8}, @0x10 0x80802619, @0x40 0x80800646
  {u64 id, u8, i8, member list}, @0x70, @0x74) through a content-declared data binding:
  the class's handler table (0x19A35C0: {event hash, handler}) maps 0x3088896A to
  0x409710, which copies it to +0x218 and rebinds players. Nothing in the client
  publishes it, and the activity host's client-reference message (7, 0x29D7E0) only reaches
  objects with a message delegate at +0x108, which these do not have.
- **Spawn-ready flag**: when the local machine is the reference's authority (0x108470 ==
  0), 0x409430 points the active data (+0x1F8/+0x200) at the local copy +0x290, which
  0x4098E0 builds. Its bool @+0x299 (what `can_spawn` reads as `info+9`) is set only while
  the published i32 at +0x250 (0x80802619 @0x28) equals the player's byte at player data
  +0x738 (players at *(0x273EA80)+8, 0x2AF0 each) and 0x77B920 (state 0x7680F0 == 4).
- **Activity lifetime state** (0x10C500, client reference type 0x10, byte +0x1AC):
  states 3 and 6 allow spawning. The object's class (0x4044B0 / 0x4044F0 receive /
  0x404550 publish) copies a published byte into +0x1AC and publishes its own +0x1AD; no
  client code writes +0x1AD, so the value belongs to the activity's script owner.
- **Body** (spawn location found, then `*0x66AE60(player) == -1`, so no object is
  created): the player configuration at player data +0x1660 (0x1098 bytes, body tag
  first) is built by 0x912240 from the player's character data (+0x850: race, gender,
  class, ...; flag +0x613 bit 1), which 0x911850 applies from the character data cache
  (0x58D940 / 0x58DAE0, 20 entries of 0xE48 keyed by character id). The cache follows
  the peer subscription manager (c_investment_peer_subscription_manager, 0x57D1D0),
  whose roster the simulation host enqueues as simulation-queue element 0x2B
  (s_investment_peer_subscription_state, producer 0x58B570 from the investment roster
  0x26BC448, handler 0x104A290). The manager subscribes **investment family 0** for each
  member account; the cache looks up slot 0 0x80801921 {soid = account id, @8 character
  id} and then slot 1 0x808017FD {soid = character id, {race, gender, class},
  appearance, loadout 0x80801855, ...}.

What changed:
- backend: family 0 baseline for the account (peer account + peer character objects).
  With it the client builds the player configuration (body tag 0x80A6A06C for the test
  character) on its own.
- d1-native (`spawn` bypass): publishes the player's id (and the matching @0x250 value,
  valid flag @9) to the first free type-0xC reference through the game's own handler
  0x409710, and reports activity lifetime state 3 while the game has none
  (D1_FORCE_LIFETIME overrides). Both stand in for activity-host state whose delivery path
  is not found yet; D1_TRACE_SPAWN logs every gate.
- backend: engine-type kinds 23 (type handle: presence bit + u32) and 35 (8-byte id) in the
  bitstream codec; client-reference message types merged into the schema.

## 2026-10-14: in-world rendering performance (first pass)

First in-world frames on real hardware (Intel Arc iGPU, 1080p) ran at ~9.5 fps with a
blotchy, posterised, blurred image. What the instrumented software-renderer runs show:

- **Colour-grading LUT churn**: the game binds its 32x32x32 RGBA8 colour-grading volume
  (tile 0x13) as a 32x32 2D array (2 layers at a time) as well as a volume. shadPS4 resolved
  the overlap to the cached volume, found fewer "resources" (a volume has one array layer)
  and freed and recreated it from guest memory on every bind: ~1000 times a second during
  loading/in-world, and every recreation threw away what the GPU had rendered into it.
  Fixed by treating 2D bindings over a volume's slices as a 2D-array view of it (the
  volume is already created 2D-array compatible) and making barriers on volumes always cover
  the whole image (renderer patches 0004, 0005).
- **Write-tracking faults are not the cost**: 0-13 per game frame.
- **Shader compilation**: ~250-460 pipelines on the way into the world; they were recompiled
  every run (the pipeline cache was stubbed out). Now kept in `<data>/shader_cache`.
- The renderer shim used shadPS4's inline fetch-shader path (a debugging path); now the
  stock vertex-input path.
- Open: software-rendered runs sometimes sit in world-controller `cleanup` with tasks
  0x0000400040000000 active (15 s in one run, >25 min in others); not yet explained.
- Open: the in-world image itself (blur/posterisation) is not reproduced locally (the
  software runs reach in_world but present black); the stock-shadPS4 A/B and the prologue
  wake-up effect are still to check.

## 2026-10-15: prologue start point (first tests)

- The client asks the activity host for insertion point -1 ("activity host startup ...
  insertion_point_index=-1"); our host echoed -1 into the instance details (+0x682).
- `D1B_INSERTION=0` (backend, research) answers 0 instead: the player never gets a unit
  (spawn never completes; the camera stays on the pre-spawn transmat glare at the same
  ambient Cosmodrome spot). So insertion 0 is not the car-graveyard start by itself, and
  the start location is not chosen from the insertion point alone.
- `D1_ALLOW_LOADING_CINE` (client, research): the loading cinematics play (cloud descent)
  and the player still spawns at the ambient spot at night: the Ghost revive / dialogue is
  the mission script (activity host), not a loading cinematic.
- Next: log every client -> activity host message during the prologue, and trace the spawn
  location choice in can_spawn (0x415700) to see what data picks the start point.

## 2026-10-15: the prologue's mission structure is in the client packages

Named-tag tables of all 1,395 packages: 748 unique named tags. Each activity has a plain
tag (class 0x808008BA, e.g. `act_cosmo_m0_highway`, 72 bytes) whose two children are its
`:scenario_client` (0x80800616: 22 bubbles, class 0x808008F0) and the loading-cinematic
table (0x80800499: `spaceflight_filler`, `spaceflight_out`, `same_dest_filler`). No
separate server tag hangs off the scenario.

The activity package (`ps4_cosmo_activities_activity_025c`, patch 5, 8,192 entries, all
decoded with Oodle 3) carries the mission graph by name:

- **Class 0x8080076E** (55 tags, ~6.5 KB each): the mission's object table: phases
  `cosmo_m0_phase00_highway_intro`, `phase00_highway`, `phase01_breach`, `phase01b_breach`,
  `phase02_graveyard`, `phase03_hangar`, `phase04_outro`; per objective
  `._player_objective`, `._incoming_sequence`, `._completion_sequence`, `._nav_point`,
  `._trigger_volume`, `._player_trigger`; cinematics `pf_104_res._cinematic` /
  `pf_104_res_fp` (phase00_highway_intro: the resurrection), `pf_104a_pwr`, `pf_105_cto`;
  per-phase `globals`, gating `tg_m0_gating` / `sv_m0_gating`.
- **Class 0x80800861** (entity resources): named trigger volumes and sequences,
  e.g. `tv_player_rez`, `tv_ghost_scan`, `tv_first_obj`, `seq_d_o1_10` ... `seq_d_o5_30`
  (dialogue per objective), `seq_fallen_*`, `seq_ambush_*`, `tv_music_*`.
- The client binary has none of the objective suffix strings (`_player_objective`,
  `_incoming_sequence`, ...).

Open question: whether the logic that connects these (trigger -> sequence -> objective
-> next phase) is also data here (some other class referencing these objects), or only
existed in the activity host. Next: find what references the 0x8080076E objects and
decode that class.

## 2026-10-15: activity host message catalogue, script channel, object kinds

**Message names.** The pointer table at 0x1910760 names every activity message type in
order (0 `entity_slots_allocated`, 1 `global_activity_state`, 2 `world_globals_state`,
3 `join_request`, 4 `join_result`, 5 `sensor_auth_update`, 6 `sensor_sense_update`,
7 `sensor_message`, 8 `request_activity_host`, 9 `start_activity_host`,
10 `start_activity_host_response`, 11 `replicate_membership`, 12/13 peer reservations,
14 `peer_leave_request`, 15/16 keepalive, 17 `activity_client_request_state_refresh`,
18 `incident`, 19/20 entity indices, 21 `client_authoritative_data_update`,
22 `client_identity_update`, 23-32 entity-slot authority, 33 `process_debug_command`,
34 `debug_request_migration`, 35 `connectivity_failure`, 36 `membership_acknowledgement`,
37 `send_client_heartbeat`, **38 `script_state`, 39 `script_event`,
40 `request_script_updates`**, 41 `bug_claw`, 42 `advance_replication_epoch`,
43 `reservations_failed`, 44 `report_lag_switch`, 45 `connection_quality_report`,
46 `speculative_migration`, 47 `high_water`, 48 `refresh_inspirations`). The numbering
matches the types the backend already uses (4, 11, 1, 27/28). The client handles host
types {0,1,2,4,5,7,10,11,18,23,24,27,29,38,39,42,43} (table 0x1910480: {type, handler}).

**Script channel.** `script_state` (38, handler 0x29DE50) payload type 0x808052E5:
u32 count (10 bits) + up to 512 entries 0x80800D22 {u32, u32, u32, i32 value}.
`script_event` (39, handler 0x1019600) payload 0x80800C0A -> 0x808009A6 {u32, u32, u32,
u8 (2 bits), u8[256]}. Payload type ids are registered at start-up (0x2697F80,
0x269AD80; read with D1_PEEK). So the mission script runs on the host and only its
variables and events reach the client.

**Engine type layouts.** 4,088 compiled type layouts sit in eboot.bin (field block:
u64 count, u32 type id, u32 size, ...; tools/d1_engine_type_layout_scan.py). Content tag
classes (0x8080076E etc.) are not among them (the client parses those with fixed code).

**Object kinds** (class 0x8080076E object table, tools/d1_activity_object_table.py):
0x3c phase, 0x3b script object (objectives, `utils`, `nightfall_controller`), 0x3a trigger
volume, 0x1d player trigger, 0x2c nav/attach point, 0x20 player objective, 0x05 sequence
(incl. `_dialog_sequence`), 0x04 object/door, 0x3d object/squad, 0x37 array.

**Incidents / Xetrov.** The client's incident system (74 classes: kill, player trigger,
sequence, insertion point, resurrection, activity complete, ...) reports gameplay events;
`client_to_xetrov` messages carry them to a service named Xetrov ("vortex" reversed).

Status: no script code found in the activity package so far (name-hash search hits were
Wwise audio; classes 0x80800734 / 0x80801AD7 / 0x80801A6A not decoded yet).

## 2026-10-15 (evening): every engine type, every field kind, more host messages

- **Schema**: the 4,088 layouts scanned from eboot.bin agree exactly with all 515 types the
  backend schema already had (dumped from a running game); the other 3,573 are merged into
  `backend/data/investment_schema.json` (4,137 types).
- **Field kinds** (per-kind decoders, table 0x1913060): 0/17 nothing; 2 bit; 3-10 ints;
  11 f32, or `p2` quantized bits when 0 < p2 < 32 (0x72C20); 12 64 raw bits; 13 point3d
  (0x2CA900: 3 x 32 bits; a quantized form exists behind flag 0x267FB28, 0 at run time);
  14 vector3d (bit zero, else 19-bit direction + 16-bit length); 18/20/21/22/23 bit +
  u32; 19 bit + u32 + 6 bits; 24/25 variant (6-bit kind, then that kind); 26 128 raw bits;
  27/28 bit, then bit ? (u32, u32, 12 bits) : 192 raw bits; 29 optional (u32, 6 bits) +
  128 raw bits; 34/41 typed value (type handle 0x80800046, then that type); 35 8 bytes.
  15 and 16 (rare) not done. Both decoders (backend Rust, tools/d1_engine_type_decode.py)
  now handle these.
- **Host message payloads** (type ids registered at start-up, read with D1_PEEK):
  0 `entity_slots_allocated` 0x80800D64, 1 `global_activity_state` 0x80800E76,
  2 `world_globals_state` 0x80800DC1 = {bool, f32} (handed to the world interface,
  0x2409E0), 38 `script_state` 0x808052E5, 39 `script_event` 0x80800C0A.
- `world_globals_state` {true, 0.35} (backend `D1B_WORLD_GLOBAL`) did not change the
  prologue's lighting (still night).
- Client -> host payload candidates by exact-fit decoding: 6 `sensor_sense_update`
  0x808024D0 or 0x8080306A; 18 `incident` 0x80801802 / 0x8080181B / 0x8080184E (two u64
  + 0x8080097D) or 0x8080198E; 47 `high_water` and 37 heartbeat 4-5 candidates each.
- The "activity mode" client reference (type 0x10) the spawn waits on is
  0x80CD0C34, an entity resource (class 0x80800861) in the Cosmodrome **ambient**
  package (`ps4_cosmo_ambient_activityonl_0268`). The prologue's own script objects
  (phases, objectives, ...) never get instantiated: they are host-side entities, and our
  host creates none, so the client runs on the destination's ambient (patrol) content.

## 2026-10-15 (night): mission objects in the client, and what is missing

**Client references are the mission objects.** `D1_TRACE_REFS=<secs>` (native, research) logs
the client-reference groups and every reference by type. In the prologue world the
reference types are exactly the object kinds of the content units' object tables
(0x3c phase, 0x3b script object, 0x3a trigger volume, 0x1d player trigger, 0x2c nav point,
0x20 objective, 0x05 sequence, 0x06 cinematic, 0x37 array, 0x3d object, 0x04 object, plus
0xc player definitions x16, 0xf, 0x10 activity lifetime, 0x11, 0x22, 0x27).

Groups (manager ints from [5], 5 per group: key, flags, defining tag, count, start):
0 `96e0a5e5` (93 refs, no tag; declared by content units 0x80CB905A and ambient
0x80CD0252), 1 `992bb471` (95 refs, tag 0x80CC0500; the key is the scenario hash at
+0x08 of `act_cosmo_m0_highway`; the prologue's mission content units declare it at +0x0C),
2 `3c2f5ed5` (21, 0x80A5EA2B), 3 `4786c0e0` (player definitions). Content units
(0x8080076E): +0x08 destination hash (0xB22417AE = cosmo), +0x0C group key.

A reference id is {u32 group key, i8, i16 index}; 0x1071D0 finds the group, adds the
index to its start and returns the entry (manager +0x520 + e x 0x38: object handle,
offset). Message 7 (0x29D7E0) then hands a typed value to the object's delegate at
+0x108 (0x353340) if the entry is bound.

**Bound vs unbound.** Bound entries have handles 0xSSfa20NN: low 16 bits 0x2000+ = the
client's entity index range (8192..). Objectives, sequences, trigger volumes and nav points
are bound (the client spawned them). All 7 phases, all 16 script objects, 3 of 4
cinematics (incl. `pf_104_res`), most player triggers, arrays and kind 0x04/0x1c/0x1e
objects are unbound (0xFFFFFFFF): host-spawned entities that no one creates.

**Ruled out** (no change to the unbound set, spawn or lighting):
- granting the client every entity index (backend `D1B_GRANT_ALL_INDICES`);
- message 23 `claim_authority_over_abandoned_entity_slots` (payload 0x80800D58 {u8,
  u32[384] mask, i3}; backend `D1B_CLAIM=<u8>,<i3>`) over slots 0..8191 (nothing was
  abandoned: the entities were never created);
- `script_state` / `script_event`: the handlers decode into stack buffers and drop them
  (payload entries are FNV-1 hashes, initialised to 0x811C9DC5 = ""); a debugging channel.

Other payload types: 24 purge 0x80800D10 {i3, u8, mask}, 27 reset authority mask and
29 query mask 0x80800D31 / 0x80800B09 {i32}. 23/24/2 go to the world interface object
*0x264C798 (vtable +0x340 / +0x350 / +0x368).

Next: how host-spawned entities reach a client (the replication path for the host's index
range), starting from where an unbound phase entry gets bound.

**Reference manager code** (manager = *(0x1AD5030 + ctx x stride + pool), ctx 0x25D6FF8):
0x106BF0 creates it ("client_reference_manager", 0x2BE20 bytes), 0x106CE0 clears it,
0x100D5E0 adds a group {key, defining tag: list of 0x10-byte entries with the kind byte at
+0}, entries start unbound (-1, two 0x18-byte slots each), 0x100D2E0 removes a group,
0x100D0A0 / 0x100D210 / 0x1071D0 / 0x100CB80 / 0x100CCE0 look entries up (by
id, by type+index, by handle). 0x1195F0 (player entity -> fireteam reference) is one
binder; entries are bound when the owning entity spawns.

**Sensors.** 0x29F720 sweeps the reference types in a bitmask (*0x2655630; trigger
volumes 0x3a, nav points 0x2c, 0x29/0x2a/0x2d/0x39) and reports bound ones (0x352E30):
these are the client's `sensor_sense_update` (6) messages. With incidents (18) they are the
host's inputs: which triggers the player is in, what happened.

Still open: the transport for host-spawned entities (phases, script objects, cinematics).
The client sends no UDP to the host (only the BAP TCP connection), so either they arrive
over BAP or the client spawns them itself on a signal not found yet.

**Object table index = reference index.** Group 0's entries line up with the prologue
content unit's object table (80CB8165) entry by entry: [0] static skeleton (kind 4),
[1]/[2] `pf_104_res(_fp)._cinematic` (6), [3] first `_player_objective` (0x20), [4]/[5]
its sequences (5), [6] `o_weapon` (4), ... So a mission object's reference id is
{group key, -, index in the object table}.

**No message delegates.** D1_TRACE_REFS now also dumps the delegate block (object +0x108)
of the first bound reference of each type: in the prologue every one is unset
(ffffffff ffffffff ffffffff 0 ...), objectives, sequences, the bound cinematic, nav
points, trigger volumes, player definitions alike. Message 7 (0x29D7E0) skips objects
whose +0x108 is 0 or -1, so in this state it reaches none of them.

**Relay.** The client registers as a NAT relay client at sign-in (302); the relay
(300 initiate / request_relay_connection / nat_punch_relay_intro) is the console-to-console
channel fallback, not an activity host transport.

## 2026-10-15 (late): simulation queue map, cinematics, host incidents

- **Fast test runs**: `D1_WINDOW=0 D1_NATIVE_GFX=off` (no window, null GPU) reaches
  activity:in_world in ~45 s on the 2-core test VM instead of 7-15 min; the software
  Vulkan driver (llvmpipe) had been saturating both cores even with D1_RENDERER_LATE.
- **Simulation queue element types** (definitions at *(0x2689508)[type], classes from the
  RTTI tables; D1_TRACE_REFS logs them): 0x6 entity handoff, 0x7 claim authority, 0x8
  authority change, 0xd machine update, 0x15 activity-client purge, 0x16 advance replication
  epoch, 0x17 global state, 0x18 world globals, **0x19 activity-client incident**, 0x1a join
  result, 0x1b membership, 0x1c entity slots, 0x1d-0x1f activity manager instance
  start/create client/dispose, 0x20 investment activity proxy set activity state, 0x22-0x32
  investment, 0x35 cinematic camera emote, **0x37 cinematic object, 0x38 cache gear, 0x39
  cinematic start/stop, 0x3a cinematic batch request**, 0x40 ghost dialog transmat event,
  0x45-0x4b UI, 0x4f slice-set transition, 0x51 global status, **0x52 player
  resurrection**, 0x53 objective abandon, 0x55 skip cinematic, 0x5c video playback complete,
  0x5d end game (vtables in the log).
- Host messages land in the queue: incident (18) -> world interface +0x348 -> 0xBB2170 ->
  element 0x19; sensor_auth_update (5) -> +0x338 -> 0xBB1C10 -> element 0x13 (world
  interface *0x264C798 = 0x1943F08, vtable 0x19439A0).
- **Incident payload** 0x8080097D (host and client): {u5 count, u12 kinds[25]},
  {u1, {u5 count, u32[25]}}, {u9 length, u8 blob[500]}; kind-specific metadata is packed
  in the blob.
- **World cinematics** (0x7652E0 applies element 0x39: payload {u32 id, i8, u8 flags};
  flags 0x21 start, 0x31 start first person, 0x2 stop, 0x51 play the prepared slot).
  The registered list (*0x26AFEF0: count @+0x1350, entries @+0x1320 + 0x38 i) is empty in
  the prologue world. These are the world controller's loading cinematics: with
  D1_ALLOW_LOADING_CINE the prologue loads "the intro and filler cinematics" (log), plays the
  spaceflight cloud descent, then "Timeout entering the prologue-filler (given 900 ticks)".
  The client's own prologue step 4 (0x7A1470) writes the selection {kind 1, ...}, so the
  suppression is retail behaviour; these travel cinematics are not the resurrection
  (`pf_104_res` is a mission object, kind 6, group 0 index 1, unbound).

Next lead: what the client does with a host incident (element 0x19 apply) - incidents have
cinematic, sequence, resurrection and insertion-point metadata kinds.

- Host incidents (element 0x19, apply 0xBB26A0 -> 0x2A20C0) go to the incident game system
  (vtable +0x98): announcements / heat / rewards, not cinematics.
- The client has no phase, script-object or encounter-script classes (RTTI): the mission
  logic and the host-spawned objects' code existed only in the activity host.
- Membership (0x808009ED) does not serialize the host id (+0x5020); "the AH has not
  acknowledged this" is not fixable through membership.

Where this leaves the activity host: its inputs are known (sensors, incidents); the client
systems a mission drives are present and reachable through the simulation queue (cinematic
object/start-stop 0x37/0x39, player resurrection 0x52, ghost dialog / transmat 0x40,
objectives, slice-set transitions); the original transport for host-spawned entities is not
found (no UDP to the host; possibly the NAT relay channel + replication protocol).

## 2026-10-15 (night): probe - how a host machine's entities would reach a client

- Simulation **views** are per remote machine: the domain membership watcher (0xBA3770)
  creates a view for a machine id in the domain only if that machine is a peer of the
  network session (session 0x75F130, state +0x8C48 in 4..9; machine records 0x168 bytes at
  membership +0x30) with a connected channel (0xAF8D60 entry +0x1CA8 == 5). Views establish
  with a signature check ("view ... signature didn't match our local, dying").
- So a host that owns entities must be a **session peer with a channel**: the stack is
  UDP -> Demonware secure transport (bdSocketRouter, bdSecurityID / bdSecurityKeyMap,
  bdCrypto*) -> Bungie channel (connect request/response, channel ids, sequences; 149 log
  strings; NAT relay fallback) -> network / managed session membership (~400 log strings,
  44 classes) -> simulation view -> replication (entity database / event manager /
  control / player views, 12 classes).
- The client contains both ends of every layer (consoles replicate to each other), so it
  is reversible from the binary; the security layer can be hooked in the runtime rather
  than reimplemented. The same stack is what console-to-console co-op needs.

## 2026-10-15 (night): co-op path, step 1 - the PSN session data

The fireteam's PSN session (`POST sessionInvitation/v1/sessions`, multipart) has three
parts; the backend now keeps them per session (and writes them to `<data>/sessions/<id>/`):
- `session-request` JSON: `{"availablePlatforms":["PS4"],"sessionMaxUser":1,
  "sessionName":"Destiny Fireteam","sessionPrivacy":"public","sessionStatus":"",
  "sessionType":"owner-bind"}` (max 1 user in the prologue: the opening mission is solo);
- `session-image` (42,882 bytes);
- `session-data` (78 bytes), what a joining console reads:
  ```
  5d6dc3f3 3303e021            8-byte id
  0a00020f 0c02                10.0.2.15:3074 (host address)
  00ff 00ff 0000 00ff 00ff 0000
  0a00020f 0c02 02d1           address again (+ 0x02d1)
  00000001 0200 00000000
  48401dff63af4ed14cc8a24e84035570   16 bytes: security key (DemonWare)?
  ```
Between two real clients the secure transport (layer 1) is DemonWare's own code once the
joiner has this blob; what the services must provide is the session data, the invitation /
join flow, and a network path between the consoles.
