# GPU resources: how the engine creates, moves and releases them (eboot 01.33)

Established 2026-10-18 with runtime instrumentation (`D1_ND_RES_STATS`, `D1_ND_POOL_WATCH`,
`D1_ND_RES_EVENTS` in `native/src/native_gfx.cpp`) and Ghidra decompilation.

## Handles and pools

- Every engine resource is named by a 32-bit handle into the handle-pool table
  `*0x1A238A0` (0x40-byte descriptors). Pool index: `((h >> 13) >> 18 | 0x3FF) & (h >> 13)`
  (signed shifts as the engine does them); element index: `h & 0x1FFF`.
- Descriptor: `+0x10` element array, `+0x18` owner, `+0x20` end of the element array,
  `+0x30` element size (0x18 for the graphics pools), `+0x34` mask, `+0x38` ids (one short is
  0x0041 in every graphics pool seen).
- Object = `elem - (mask & *(elem + 8))`.
- A loaded package has its own pools: about 35 pools and about 1,300 vertex / index buffers in
  Earth patrol.
- `0x6FA10` relocates a whole pool by a delta (called from `0x70270`). Pool descriptors are
  written by `0x6FBC0` / `0x70C70`.

## Draws

- In-world, all but about 0.5% of draws take their vertex and index buffers from tag handles
  (`set_vertex_stream 0x7DEC20`, `set_index_buffer 0x7DEE30`).
- Every texture slot's T# pointer is a resource object of type 1-3, whose T# is at `+0`.
  The exception is the engine's own dynamic textures (e.g. 4 KiB tables around `0x562A5F000`),
  which have no resource events and are written by the CPU.

## The platform graphics callback table

The core resource manager drives the PS4 graphics layer through 15 callbacks, registered by
`0x7D3400` via `0xCFCC0` into `0x254EE30..0x254EEA0`:

| Global | Function | Role |
|---|---|---|
| `0x254EE30` | `0x7D2E60` | alignment per type (table `0x15D1010`) |
| `0x254EE38` | `0x7D2E80` | bind memory to a resource (type, handle, address) |
| `0x254EE40` | `0x7D3160` | re-point a resource at new memory (after a move) |
| `0x254EE48` | `0x7D2FE0` | release (textures: drop the top mip via `0x7D4480`; buffers: nothing) |
| `0x254EE50` / `0x254EE58` | `0x7D32B0` / `0x7D3350` | create engine-made index buffers (`0x7D3CB0` / `0x7D3BA0`) |
| `0x254EE60` | `0x7D4E20` | build resources from tag data |
| `0x254EE70` | `0x7D3560` | move: GPU copy (copy queue, `0x7DA960`) to new memory |
| `0x254EE78` | `0x7D37B0` | commit a move: swap handles and memory |
| `0x254EE80` | `0x7D4480` | rebuild a texture's T# for its resident mips |
| `0x254EE88` | `0x7D5520` | is the texture fully resident |
| `0x254EE98` | `0x7D39D0` | address / offset queries |
| `0x254EEA0` | `0x7D55C0` | flags |

Types in the bind / re-point dispatchers:

| Type | Bind | Re-point | Meaning |
|---|---|---|---|
| 1-3 | `0x7D4D40` | `0x7D4840` | textures (2D / 3D / cube): `0x7D61A0` sets the T# base (`0xF841B0`) |
| 4 | `0x7D4C30` | `0x7D4720` | vertex buffer: `+0x28` base (`0x7D64A0`), `+0` size, `+4` stride, count = size / stride |
| 6 | `0x7D4CB0` | `0x7D47B0` | index buffer: `+0x30` base, `+0x3C` count, `+0x38` 32-bit, `+8` size |
| 7, 9-0x12 | | | other kinds; 8 and 9 hold a descriptor at `+8` / `+0x18` (`0x7D4B90` / `0x7D48C0`); no draw texture is of these kinds |

The bind and re-point dispatchers start with a switch table and cannot be trampolined:
they are wrapped through the table entries instead.

## What the events guarantee (measured, Earth patrol, 5 minutes)

- Every buffer and texture a draw used had been bound by an event.
  - About 12 million buffer uses and 42 million texture uses: none unregistered.
- Contents at first use equal the contents at bind: 11,160 buffers and 3,887 textures, none
  changed.
- While a resource stays bound, nothing writes it.
  - Sampled every 10 s: 894 buffers unchanged.
  - Textures: 1,180 unchanged. The few that changed had been moved or unloaded: their
    descriptor named other memory.
- Moves are constant: about 27,600 vertex-buffer and 40,000 texture re-points.
  - 83,543 of 83,556 re-points carried identical contents.
  - The 13 others: 4 handle swaps (`0x7D37B0`), 9 same-size textures with new contents.
- Conclusion: a resource's contents change only with an event on it, or through a GPU copy
  command (DMA_DATA) in a command list.
  - The engine copies streamed mips and new glyphs (fmt 134 / 138 textures, e.g. 1024x512)
    into resource textures on the copy queue, just before the draws that use them.
  - Such a copy carries no resource event: the renderer marks every texture in the written
    memory stale and copies it again (about 3 per second in patrol).
  - The renderer keeps its copy per resource and epoch.
  - After an event, it compares contents once, so a move costs a hash and nothing else.

## Native implementation

`resreg` (`native_gfx.cpp`): a lock-free table from resource object to `id << 32 | epoch`,
fed by the wrapped callbacks. Captured draws carry it per T# slot, vertex declaration element
and index buffer.

The renderer (`gfx/nrender.cpp`):
- **Textures** are keyed by resource id plus the T# without its base address.
- **Buffers** are kept as whole-buffer copies keyed by resource id plus offset.
- Neither is write-protected or version-checked.
- Unregistered memory (dynamic textures, inline vertices) keeps write tracking.
- `D1_ND_RES=0` turns the event path off.

## Dynamic memory: what is no engine resource (2026-10-18, later)

After the resource events, a fault census (`D1_NG_LOG_FAULTS`: writing code address and what
the renderer kept there) showed three kinds of memory still write-tracked.

- **Dynamic geometry: about 170 vertex and 107 index buffers per frame.** These sit in pool
  1028 (the engine's global pool) with memory around `0x5_6269_xxxx`.
  - They come in pairs and triples (handles `…18/19`, `…1A/1B`, `…1C/1D/1E`): double- and
    triple-buffered buffers the CPU fills every frame.
  - Native: copied for each draw (the vertex range it uses), never cached or tracked, as a PC
    engine treats dynamic buffers. About 0.1 MiB per frame in patrol.
- **Dynamic textures: about 11, about 600 KiB.**
  - The engine writes them only through a lock / unlock API over a table of 0xE0-byte slots at
    `0x26F23B0`: lock `0x818F80 -> 0x81A600`, unlock `0x818FA0 -> 0x81A640`, descriptor
    `0x818DD0`.
    - Slot memory: `+0x40` (or `+0x48` when flag bit 3 of `+0` is set).
    - Row pitch: `+0xD8`. Locked bit: bit 2 of byte `+2`.
  - Only five functions lock slots: `0x33E600`, `0x8439E0`, `0x88FE50`, `0x8A3620`,
    `0x8CC630`.
    - `0x88FE50` refreshes two double-buffered tables every frame: slots 6/7 (pitch 512) and
      8/9 (32x32, pitch 64) at `0x578B00000..`.
  - Native: the unlock is replaced (it only clears the locked bit) and announces "the CPU wrote
    this memory", the equivalent of Unmap.
- **Small render targets the CPU may rewrite** (light tables): announced the same way. Copies
  are kept per address generation, bumped by those announcements and by the copy-queue /
  WRITE_DATA writes the renderer executes itself.
- **Our own readbacks** of small targets used to fault on our own protection. With nothing
  protected, they no longer do.

Result: no page is write-protected any more, so there are 0 write faults in patrol and orbit,
on both Linux and Windows. `D1_NG_VERIFY_DYN=1` hashes every dynamic texture at every use:
525 checks, 0 changed without an event.

## Stale registry entries (2026-10-18)

Registrations are keyed by object address and were never removed. Handle pools are freed (a
package unloads) and relocated (`0x6FA10`), so an old object address can later hold anything.
In an orbit run, about 130 lookups hit addresses whose registered handle no longer resolved
there (`handle ... now names 0`). Several were around `0x4045_xxxx`, where the UI builds T#s in
scratch memory. The registry now stores the handle with each entry and rejects the entry when
`resolve_handle_safe(handle)` names another address.


## Resource Bind/Repoint Dispatch, Streaming Mips, Submesh VBs & Camera FOV (2026-11-23)

- **Resource manager bind (`0x7D2E80`, `*0x254EE38`) and repoint (`0x7D3160`, `*0x254EE40`) 18-type switch tables (`0x7D2F84` / `0x7D3258`)**:
  - Types **1, 2, 3** -> `0x7D4D40` / `0x7D4840`: Texture (`Gnm::Texture`, 32-byte `T#` at tag `+0x00`; authored full dimensions at `+0x28` u16 `full_width`, `+0x2A` u16 `full_height`, `+0x2C` u16 `full_depth`, `+0x31` u8 `full_mips`, `+0x34` u8 `has_hi_mip`).
  - Type **4** -> `0x7D4C30` / `0x7D4720`: Vertex Buffer (`+0x0` u32 size, `+0x4` u32 stride, `+0x28` u64 base, `+0x30` u32 vertex count).
  - Type **6** -> `0x7D4CB0` / `0x7D47B0`: Index Buffer (`+0x8` u64 size, `+0x30` u64 base, `+0x38` u32 is_32bit, `+0x3C` u32 index count).
  - Type **7** -> `0x7D4DA0`: Generic `Gnm::Buffer` (`V#` at tag address).
  - Type **8** -> `0x7D4B90`: Texture with 8-byte header (`Gnm::Texture` 32-byte `T#` at `tag + 0x08`, NOT a pixel shader).
  - Type **9** -> `0x7D48C0`: Vertex Shader (`VsWrapper` at tag address, `Gnm::VsShader` at `+0x14`, fetch shader at `+0x08`).
  - Type **10** -> `0x7D4AB0`: Geometry Shader; Types **11 & 14** -> `0x7D4970`: LS/ES Shader.
  - Types **12 & 13** -> `0x7D49F0`: Pixel Shader (`Gnm::PsShader` at tag `+0x00`, `spiShaderPgmLoPs/HiPs` at `+0x08/+0x0C`).
  - Type **18** -> `0x73D50`: Generic data block pointer.
- **Streamed texture mip lifecycle (`0x0CB940` -> `0x0E01E0` -> `0x7D4480` `texture_mips`)**:
  - When a streamed texture (`*(uint8_t*)(tag + 0x34) != 0`) binds with an active hi-mip block, `0x0CB940` first calls `h_bind` (`0x7D4D40`), which writes `T#.base = hi_mip_addr` while `T#.width/height/last_level` are still at the half-resolution low-mip count (`full_mips - 1`), and then calls `0x7D4480(handle, low_mip_addr, hi_mip_addr)` (`h_mips`) to set `T#.width/height` to `full_w x full_h` and `last_level` to `full_mips - 1`.
  - When `hi_mip_addr != 0`, only mip `0` resides at `hi_mip_addr`; mips `1..full_mips-1` remain at `low_mip_addr`. The renderer allocates one permanent full-mip `VkImage` (`full_w x full_h`, `full_mips` levels) keyed solely by resource ID (`res >> 32`), uploads mips `1..full_mips-1` from `low_mip_addr` and mip `0` from `hi_mip_addr` in place, and switches the active mip range via `VkImageView` `baseMipLevel` (`0` vs `1`).
- **Multi-submesh vertex declaration switch (`0x845DE0` -> `0x7DEB70`)**:
  - In `0x845DE0`, when consecutive submeshes of the same mesh (`uVar24 == local_874`) use different vertex declarations (`uVar8 != local_894`), the engine calls `0x7DEB70` (`set_vertex_decl`), which resets `dev + 0x1D78[0..31] = 0xFFFFFFFF` (the device redundant-bind cache) without unbinding CUE stream 0/1 (`0xF8B600`), and skips re-calling `0x7DEC20` (`set_vertex_buffer`) for stream 0/1. `DevState::vb_handle[32]` preserves the bound stream handles across `0x7DEB70` so submeshes 1+ are not dropped as `"null vertex buffer"`.
- **TFX technique state application (`0x82B3F0..0x82B830`)**:
  - TFX techniques store 4 render-state indices at `technique + 0x20`, a VS handle at `technique + 0x28` (`0x82D070`), and a PS handle at `technique + 0x2A8` (`0x82D020`). Hooking `0x82B490`, `0x82B5C0`, and `0x82B730` alongside `resreg` types `9`, `12`, and `13` pre-translates shaders and warm-builds persisted `DiskPipeSpec` pipelines (`native_pipelines.bin.specs`) off the draw path.
- **First-person world camera vs. weapon viewmodel FOV (`0x526FE0`, `0x5270E0`, `0xBD3BF0`, `0x6BF320`, `0x8EFAB0`)**:
  - `0x526F80` resolves the camera globals tag (`*(float*)(g + 0x18) = 1.25663706 rad = 72.0 deg`). `0x526FE0` returns the default world camera horizontal FOV in radians, and `0x5270E0` returns the first-person base world horizontal FOV in radians to `0xBD3BF0(unit, zoom_slot)`, which divides `0x5270E0()` by the weapon ADS zoom magnification `0xBD3740()`.
  - `0x6BF320` stores weapon viewmodel FOV (`param_3[4] = 0x737C80`) separately from world camera FOV (`param_3[5] = 0xBD3BF0`). `0x8EFAB0` writes world FOV to `DAT_0273c3e0 + 0x4ac` (building the visibility culling frustum before culling and `"first-person environment view"` in `0x52CE20`) and weapon viewmodel FOV to `DAT_0273c3e0 + 0x554` (`"first-person player view"` / `"first-person iron sight view"` in `0x80F730`).
