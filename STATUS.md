# Current Status — 2026-09-03


## Canonical storage

- Durable source of truth: private GitHub repository `lizardpeter/destiny-1`.
- Runtime working mirror: `/mnt/data/Destiny1_Reversal/`.
- Never commit raw Destiny package bytes or proprietary `oo2core_*` binaries.
- Commit confirmed docs/specs/tools/tests/lightweight evidence after each material finding.

## Executive state

The project has crossed the main payload barrier: **D1 ROI Oodle 3 decompression is working on real PS4 and Xbox One Tiger blocks** using the user's Oodle 3 DLL and the project-local experimental Linux bridge. We can now reconstruct logical entries and have successfully exported all 30 Texture2D assets in the canonical PS4 sample to visually validated DDS/PNG previews. Vertex/index topology proofs and native PS4 shader parsing are also working.

## Real corpus acquired

### Canonical PS4 sample
- `ps4_arch_cabal_005b_1.pkg`
- PS4, D1 ROI Tiger v24, package `0x005B`, patch 1
- 89,044,992 bytes
- SHA-256 `d44f2dcbaef32743da9657e38691bcd91372fd9550e96ea3d99a9ce9440c24e0`
- 667 entries / 626 blocks
- all 626 blocks resident in patch 1, compressed, and stored-payload SHA-1 verified

### Xbox One secondary corpus
- `xboxone_arch_cabal_0059_1.pkg`
- Xbox One, D1 ROI Tiger v24, package `0x0059`, patch 1
- 119,173,120 bytes
- SHA-256 `8836546ecbbbf6ba31fd50035a180c80c7bcb6407780f4b61be7a8217d24fde8`
- 8,111 entries / 2,228 block records
- 796 resident patch-1 blocks: **796/796 SHA-1 verified**
- 1,432 block records point to missing sibling `xboxone_arch_cabal_0059_0.pkg`
- Not the semantic counterpart of PS4 `005B`; retained as a high-value independent Cabal/GPU/resource corpus.

## Oodle 3 decompression — WORKING

User-supplied validation runtime:
- `oo2core_3_win64.dll`
- size 894,752 bytes
- SHA-256 `682c0aad216fae443e0f9561876cfabfddaeffcd48e5990613ad2cf47c49fa62`
- PE32+ x86-64; exports `OodleLZ_Decompress`

Project components:
- `tools/d1_oodle_probe.py`
- `tools/linoodle_min.cpp`
- `tools/build_linoodle_min.sh`
- `tools/runtime/linux-x86_64/liblinoodle3_min.so`

The custom Linux bridge is **experimental** and currently runs with `LINOODLE_SKIP_DLLMAIN=1` because this DLL's Microsoft CRT attach path crashes under the minimal Windows compatibility shim. Direct decoder invocation after PE map/relocation/import resolution succeeds.

Validation:
- PS4: 12/12 representative blocks → exactly `0x40000` decompressed bytes.
- Xbox resident patch 1: 12/12 representative blocks → exactly `0x40000` bytes.
- decoded outputs contain coherent Tiger structures and have driven successful asset extraction.

Evidence:
- `evidence/decompression/ps4_blocks_12.json`
- `evidence/decompression/xbox_blocks_12.json`
- `notes/OODLE_RUNTIME.md`

## Package layer solved / verified

- Tiger v24 header layout and little-endian PS4/Xbox parsing.
- 16-byte FileEntry bit packing.
- 32-byte BlockEntry layout.
- 68-byte NamedTagEntry source layout.
- table SHA-1 semantics.
- per-block stored-payload SHA-1 semantics.
- patch-family block ownership via `BlockEntry.patch_id`.
- D1 TagHash construction/decomposition.
- zero named-tag table behavior.
- `header_signature_offset` points to a dense 256-byte region on both real platforms; cryptographic algorithm/key still unresolved.

## Cross-platform resource graph results

`entry_b[23:16]` is preserved across **every observed local reference edge**:
- PS4: 209/209
- Xbox One: 3,171/3,171

Strongly established relationships:
- `32:4 -> 1:4` VertexBuffer header/data
- `32:6 -> 1:6` IndexBuffer header/data
- `32:1` Texture2D header with direct and two-hop payload modes
- two-hop texture mode: `32:1 -> 65:1 -> 5:1`
- `32:2 -> 1:2` TextureCube header/data
- `32:16 -> 1:16` TextureSampler header/data
- `32:8 -> 1:8` PixelShader header/data
- `32:7 -> 1:7` fixed 16-byte GPU resource header/data family
- `0:20` WwiseBank
- `8:21` WwiseStream
- `16:0` structured Tag

## GPU resource payload results

See `spec/D1_GPU_RESOURCES.md` for the detailed field map.

### VertexBuffer
- header = `0x0C`.
- PS4 marker `0xBEEFCACE` (11/11).
- Xbox marker `0xBEEFDEAD` (144/144 currently decoded).
- PS4 header data-size matches referenced payload 11/11.
- all PS4 payloads are exactly divisible by stride.

### IndexBuffer
- header = `0x18`.
- marker `0xDEADBEEF` on PS4 and decoded Xbox sample.
- PS4 data-size matches payload 9/9.
- decoded u16/u32 index ranges match candidate position-buffer vertex counts for six resource groups.

Geometry proof GLBs are under `exports/geometry/`. They preserve real topology and signed-normalized position data but **do not yet contain final object/world scale, placement, materials or complete vertex semantics**.

### Texture2D — PS4
- exact ROI header = `0x3C`.
- all 30 canonical Texture2D headers reconstructed.
- all 30 exported through the actual reference chain + Oodle + GCN deswizzle pipeline.
- successful formats: BC1, BC3, BC4, BC5.
- DDS and PNG previews are under `exports/textures/all_ps4/`.
- manifest: `evidence/decoded/ps4_texture_manifest.json`.
- contact sheet: `exports/textures/ps4_005b_contact_sheet.jpg`.

### Texture2D/Cube — Xbox One
- exact observed ROI header = `0x44`.
- previously unknown `0x38..0x43` tail is now solved as three u32 flag words: `flags1`, `flags2`, `flags3`.
- resident decoded examples validate `BEEFCAFE` magic, dimensions, DXGI format and tile mode.
- full Xbox texture export still needs Durango detiling implementation and, for many entries, missing patch 0.

### Subtype 7
Canonical PS4 header is 16 bytes. Across all 122/122 local pairs:

`payload_size == u32(header + 0x08) * 16`

All headers share marker `0x20077FAC`; word `0x04` is `0x00100000` in this corpus. 88 `s_technique` tags reference a subtype-7 header at exact tag offset `0x32C`.

QuickTag maps subtype 7 to ConstantBuffer in later Tiger generations but intentionally comments the D1 mapping out. The new binary evidence makes a D1 constant-buffer role **strongly supported**, but the project still uses neutral `GpuSubtype7` terminology pending D1-specific semantic confirmation.

### PS4 PixelShader
Seven header/data pairs are fully reconstructed.

Tiger header word 0 is solved:

`(num_input_usage_slots << 24) | shader_payload_size`

Validation:
- low 24 bits = referenced shader payload byte size, 7/7.
- high 8 bits = native PS4 `OrbShdr` footer's `num_input_usage_slots`, 7/7.

Each shader payload is:
- u32 `0xBEEB03FF`
- u32 qword count
- `qword_count * 8` bytes GCN region
- 28-byte `OrbShdr` ShaderBinaryInfo footer

All seven footer type fields independently identify pixel shader. Evidence: `evidence/decoded/ps4_pixel_shader_payloads.json`.

## Structured tags

Canonical PS4 `005B` contains 146 `16:0` tags:
- 136 × `0x80801AD7` = ROI `s_technique`
- 1 × `0x80801BD9` = ROI `s_expensive_light`
- `0x80800861` (8) and `0x80801AF2` (1) remain unresolved for ROI

A raw aligned local-TagHash scan across the 136 technique payloads found:
- 88 subtype-7 header references, all at byte offset `0x32C`.
- six Texture2D-header references at offsets `0x4A4` / `0x4AC` in a small subset of techniques.

Evidence: `evidence/decoded/ps4_technique_local_ref_scan.json`.

## Current highest-value missing data / work

1. **Xbox `xboxone_arch_cabal_0059_0.pkg`** — required for the 1,432 patch-0 blocks referenced by the Xbox patch-1 package.
2. Decode D1 model/static-map structured tags so buffer groups gain object transforms, LODs, part/material assignments and final GLB semantics.
3. Implement Xbox One Durango detiling and bulk texture export.
4. Continue D1 technique schema reversal and bind subtype-7 buffers, shaders and textures semantically.
5. Parse/disassemble PS4 GCN shader resource usage using the now-confirmed `OrbShdr` metadata.
6. Locate the actual Xbox semantic counterpart of PS4 `005B` using structural fingerprints rather than package-number assumptions.
7. Expand from this Cabal package to map/entity/model packages to validate complete static and dynamic model export.
