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
- Conclusion: a resource's contents change only with an event on it.
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
