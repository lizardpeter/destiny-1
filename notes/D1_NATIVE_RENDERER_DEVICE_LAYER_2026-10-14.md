# Native renderer: the engine's GPU device layer (2026-10-14)

Exact build: CUSA00219 01.33 `eboot.bin`. Addresses are eboot offsets. Names are
HYPOTHESIS unless stated otherwise. Call rates come from `D1_COUNT` call counters with the
null GPU, measured in-world at the prologue spawn: about 7,400–7,500 draws per frame.

## Summary

Destiny 1 does not write PS4 GPU packets throughout its code. It draws through one engine
object, called here the **GPU device**, which wraps Sony's statically linked Gnm library
(a `GfxContext` with a draw command buffer, a constant command buffer and a constant update
engine, CUE). About 150 device functions sit together at `0x7D8000–0x7E4000`, and the Gnm
packet builders sit at `0xF7C000–0xF92000`.

All draw packets come from builders called only by the device layer:

- `DRAW_INDEX_AUTO` builder `0xF7F260`: 11 callers, all in the device layer.
- `DRAW_INDEX_2` builder `0xF7F320`: 2 callers.

Only about 60 functions outside the device layer call Gnm directly. They're mostly resource
creation (texture and render-target descriptors), submission and a few special passes.

A native renderer can therefore hook the ~40 device functions that matter and implement
them in Vulkan. The PS4 command stream and its emulation drop out entirely.

## Device object layout (`this` of the functions below)

| Offset | Meaning |
|---|---|
| `+0x26` | byte: device active; draws are skipped when 0 |
| `+0x50` | `GfxContext*`. DCB at `+0`, CCB at `+0x80`, CUE at `+0xC0`; the DCB write pointer is at `+0x10`, its end at `+8` |
| `+0x1D28` | current vertex shader object (cached, `0x7DE800`) |
| `+0x1D30` | current pixel shader object (cached, `0x7DE7B0`) |
| `+0x1D60` | current vertex declaration: a u32 element count; per element `{…, +0x14 dword fmt, +0x18 offset byte, +0x19 stream byte}` (8-byte stride from `+0x10`) |
| `+0x1D68` | current index buffer handle |
| `+0x1D70` | its resolved buffer object (`+0x30` GPU address, `+0x38` index size: 0 = 16-bit, `+0x3C` size) |
| `+0x1D78[32]` | vertex stream handles |
| `+0x1DF8[32]` | vertex stream offsets |
| `+0x1E78[7][16]` | bound texture (`T#` pointer) per shader stage and slot |
| `+0x2578..+0x258C` | viewport x, y, w, h, z near, z far |
| `+0x25B4` | blend state index |
| `+0x25BC` | rasteriser / depth-bias state index |
| `+0x25C0` | depth-stencil state index |
| `+0x25E8` | stencil reference state |
| `+0x27C0` | byte: primitive restart |

**Resource handles:** `(pool = handle >> 13 & 0x3FF, slot = handle & 0x1FFF)` resolve through
the pool table at `*0x1A238A0` (0x40-byte pools: `+0x10` base, `+0x30` stride, `+0x34` mask).
Buffer objects keep their GPU address at `+0x28` (vertex) or `+0x30` (index).

## Device API

| eboot | calls/frame | name (hypothesis) | notes |
|---|---:|---|---|
| `0x7E15D0` | ~7,100 | `draw_indexed(prim, ?, first_index, count)` | prim through the table `0x15D13C0`; CUE preDraw `0xF8DF60`, `0xF7F320`, postDraw `0xF8E880` |
| `0x7E17C0` | ~160 | `draw(prim, count)` | `DRAW_INDEX_AUTO` |
| `0x7E1710` | ~60 | `draw_instanced(prim, count, instances)` | |
| `0x7E1840` | small | `draw_indexed_instanced` | |
| `0x7E1960` | small | draw from an inline vertex buffer | |
| `0x7DEC20` | ~8,500 | `set_vertex_buffer(handle, stream, offset, count)` | builds `V#` per declaration element of that stream; CUE `setVsharpInUserData`-like `0xF8B600`; cached per stream |
| `0x7DF630` | ~9,000 | `alloc_constants(stage, slot, bytes)` → pointer | allocates from the DCB (`0xF7FEB0`), builds a `V#`, binds it as a constant buffer (`0xF8B500`); the caller writes the constants through the returned pointer |
| `0x7DEE30` | ~2,800 | `set_index_buffer(handle)` | `INDEX_TYPE`, `INDEX_BUFFER_SIZE`, `INDEX_BASE`; cached |
| `0x7DE8C0` | ~2,200 | `set_texture(stage, slot, T#*)` | CUE `setTextures` `0xF8AFD0`; null → default texture `*0x1A1F4B8`; cached per stage and slot |
| `0x7DEF20` | ~700 | `set_texture(stage enum 1..4, slot, T#*)` | stage enum → hardware stages 1, 2, 3, 5 |
| `0x7E1510` | | `unbind_texture_everywhere(T#*)` | |
| `0x7DE800` | ~1,050 | `set_vs_shader(shader*)` | CUE `0xF8B790`; `shader+0` = …, `+8` fetch shader, `+0x14` registers |
| `0x7DE7B0` | ~1,050 | `set_ps_shader(shader*)` | CUE `0xF8B8C0` |
| `0x7DE4A0` | ~1,080 | `set_blend_state(index)` | fixed table `0x15D16C4`, stride 0x24; all four MRTs get the same blend |
| `0x7DE590` | ~1,085 | `set_depth_state(index)` | fixed table `0x15D2394`, stride 0x10 |
| `0x7DE640` | ~1,070 | `set_raster_state(index)` | fixed table `0x15D2424`, stride 0xC: depth bias / slope |
| `0x7E0F90` | ~1,575 | `set_stencil(ref)` | uses table `*0x1A1F4C0` / `0x15D1E38` |
| `0x7DE860` | ~1,050 | `set_primitive_setup(mode)` | |
| `0x7DE370` | ~120 | `set_viewport(x, y, w, h, znear, zfar)` | |
| `0x7E0780` | 0 in-world | `dispatch(x, y, z, …)` | |
| `0x7DC270` | per pass | `reset_state(full)` | clears every cache above and unbinds |
| `0x7DFAC0` / `0x7DFD10` | | render-target / scissor setup | to map |
| `0x7E08A0`, `0x7E0AE0`, `0x7DF850`, `0x7E0040`, `0x7E2000`, `0x7E2480`, `0x7E2760`, `0x7E2CB0` | small | full-screen and clear passes | use `0xF7E540` (RT pitch) / `0xF7E2E0` (CMASK) |
| `0x7DD6A0` | | big state / RT setup | to map |
| `0x7DCEC0`, `0x7DD060` | 1 | begin / end command buffer, prepareFlip | `0xF81220` NOP 0x3E |
| `0x7E40A0` | | submission | 25 Gnm calls |

Main draw callers, per frame: `0x82BE10` (2,111), `0x82BD10` (2,099), `0x8A9CD0` (1,463),
`0x7E16A0` (758), `0x7DA370` (303), `0x845F10` (194).

## Native renderer plan (outline)

1. **Hook the device API.** Keep the engine's own redundancy caches (it already skips
   unchanged state).
   - Shaders, blend/depth/raster tables and resource handles map one-to-one onto Vulkan
     objects.
2. **Resources.**
   - **Textures:** create a `VkImage` once per `T#` object; detile on first use and on
     engine updates.
   - **Buffers:** create once per engine handle and pool.
   - **Constants:** `alloc_constants` returns memory from our persistently mapped upload
     ring instead of the DCB.
3. **Shaders.** Translate each Gnm VS/PS (and fetch shader plus vertex declaration) once
   with shadPS4's GCN → SPIR-V recompiler; cache the results on disk.
4. **Pipelines.** Key them by (VS, PS, vertex declaration, blend, depth, raster, RT formats)
   and cache them.
5. **Bring-up order:**
   1. clears and UI;
   2. menus (class screen);
   3. the world: G-buffer, lighting, post.

   Each step is checked against the shadPS4 path, which stays as the reference and fallback.
