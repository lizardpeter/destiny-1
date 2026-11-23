# Census of CPU writes into GPU-read memory (eboot 01.33)

Started 2026-11-22. Goal: a complete list of the code that writes memory the GPU reads without
going through a resource event, so each can be handled at its source.

## Method

- Run with every GPU-read range write-protected: `D1_ND_RES=0 D1_NG_DYNAMIC_COPY=0`.
- `D1_NG_CENSUS=<file>` (new) keeps every writer for the whole run: the writing code address,
  the two guest callers above it (frame pointers), the address range written and what the
  renderer kept there. `D1_NG_LOG_FAULTS` alone still prints the top 24 per interval.
- Each writer is then identified in Ghidra.

## How the engine gets its memory

- The eboot maps memory at three call sites only: `0x2487` (start-up), `0xB46C4` (the engine's
  memory system) and `0x1279240`.
- `0xB4630(region, size, from_top)` commits memory for a region: `sceKernelAllocateDirectMemory`
  + `sceKernelMapDirectMemory` with protection 0x33 (CPU and GPU read / write). Memory type 3
  (write-combined, GPU) when the region's type field (`+0x6C`) is 1, else type 0.
- `0xB4780(type, size, name, region)` reserves a region's address range
  (`sceKernelReserveVirtualRange`) and names it (`sceKernelSetVirtualRangeName`).
- The regions are a table of 0x70-byte entries at `0x1AF9D68`; `0xB3080` maps the ten
  allocation classes onto them. "Tag Memory" is created through `0xB21C0`.

## Writers found so far

Runs: the prologue mission (about 5 minutes in the world), and orbit followed by Earth patrol
with the Ghost and the menu opened (about 7 minutes). Both runs show the same sites.

| Writer | Callers | Memory | What it is |
|---|---|---|---|
| `libc.prx` memcpy | `0x8BE0D3`, `0x8BE12F` in `0x8BE050` <- `0x8BE560` | `0x562A60000` 512x512 R8, `0x562A5F000` 512x1 | UI glyph cache upload: copies the CPU-side glyph bitmap row by row into the texture, then the 512x1 table. Runs when the cache's dirty field (`+0x48`) is set; callers `0x8D8176`, `0x8D8203`. No lock / unlock. |
| `0x88FFAA` | `0x7EAE80` <- `0x23C9DA` | `0x578B08000` 32x32 tables | per-frame table refresh (`0x88FE50`, lock / unlock path, already announced) |
| `libc.prx` memcpy | `0x80D77` (`0x80D00`) <- `0x6C1D9`, `0x6C37D` (`0x6C050`) | `0x4CA5BB000..0x4FC580000` (resource memory) | loader scatter-copy: places a chunk of loaded data into a list of destination segments (16-byte entries: pointer, size, offset). Load-time fill of resource memory, before the resource is bound. |
| `0xF882D2`, `0xF882FA` | (`0xF88060`) <- `0xF8A2C7` <- `0xF8A3DD` | resource textures up to 1820x1024 | GpuAddress tiling of a CPU surface into texture memory |
| `libc.prx` memcpy | `0x833A03` <- `0x7ED63B`; `0x8A96F3` <- `0x7F9FF5`; `0x85B86E` <- `0x80529F` | `0x5626xxxxx`, `0x5629xxxxx` (dynamic pool) | dynamic buffer fills; to identify |
| `0x8CB315` | `0x7F9E06` <- `0x80529F` | `0x5626A5A00..` | dynamic buffer fill; to identify |
| `0xD4B4DC` | `0xD5ECF7` <- `0x84D8B8` | `0x5629EE950..` | dynamic buffer fill; to identify |
| host libc memcpy | (our own threads) | resource memory, small render targets | file reads into resource memory and the renderer's own readbacks |

Still to run: the Tower, the character and inventory screens, the director, a strike.

## What the renderer does with each (2026-11-22)

- **Glyph cache upload `0x8BE050`**: hooked. After it runs, both textures are announced as
  written (`ng::cpu_wrote`), as a PC engine's texture update would be. In a patrol run with the
  Ghost opened: 93 / 24 / 127 uploads per 10 s interval when new text appears, and the
  per-submission content compare reports 0 "changed without an event" (it reported 6 per
  interval before the hook).
- **Tiler `0xF8A330(out, in, tiling parameters)`**, called by the resource builder `0x7D4E20`
  (callback table entry `0x254EE60`): hooked. The destination is announced as written, so a
  texture copy made before the tiling finished (the loader thread uploads at bind) is made
  again.
- **Dynamic textures written after their list ended**: seen here too (2 and 6 per interval),
  handled by the compare at submission.
- **Dynamic vertices, indices and constants read from guest memory**: a recorded list's copies
  are compared with the source and copied again when the list is submitted (`Sub::recopy`),
  because the console's GPU reads them only after submission. 0 changed in about 3,300 copies
  per interval here; the log line "dynamic data filled after its list ended" shows the count
  on a fast machine.
