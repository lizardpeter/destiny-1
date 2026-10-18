# Native renderer design (Vulkan 1.4, no shadPS4)

Status 2026-10-14:
- The device layer is mapped: see `D1_NATIVE_RENDERER_DEVICE_LAYER_2026-10-14.md`.
- Our own GCN decoder, SPIR-V builder and translator are done: all 384 shaders seen in-world
  translate with no remarks and pass `spirv-val`.
- This file is the plan for the runtime side.

## Status 2026-10-14 (evening): the native renderer draws the game

`D1_NATIVE_GFX=render` (with `D1_RENDERER=0`) runs the game on the null GPU and executes every
draw with our own Vulkan renderer (`gfx/nrender.cpp`, capture in `src/native_gfx.cpp`). No
shadPS4 code runs. Every 60th frame was drawn on lavapipe; in-world frames are complete
(geometry, deferred lighting, sky, post-processing, HUD).

### How a draw is captured (device object fields, eboot 01.33)

| Field | Content |
|---|---|
| `+0x1D28` / `+0x1D30` | VS object / PS object (null PS: depth-only) |
| `+0x1D60` | vertex declaration: count, strides per stream at `+4`, elements at `+0x10` (fmt `+0x14`, offset `+0x18`, stream `+0x19`) |
| `+0x1D78[s]` / `+0x1DF8[s]` | stream handle / offset; V#s are built with the engine's own `0xF7CF90` |
| `+0x1E78 + stage*0x80` | T# pointers (Gnm stage 1 = PS, 2 = VS). **Copied at record time**: the engine builds some T#s in temporary memory |
| `+0x2278` / `+0x22F8` | S# pointers, PS / VS (copied too) |
| `+0x25D0` | PA_CL_CLIP_CNTL |
| `+0x25D4` | PA_SU_SC_MODE_CNTL (cull, face, polygon offset enables) |
| `+0x25D8` | CB_BLEND0_CONTROL (all MRTs) |
| `+0x25DC` / `+0x25E0` / `+0x25E4` | DB_DEPTH_CONTROL / DB_STENCIL_CONTROL / DB_STENCILREFMASK |
| `+0x25B4` | blend index: CB_TARGET_MASK = `*(0x15D16E0 + i*0x24)` |
| `+0x25BC` | raster index: polygon offset = table `0x15D2424` (`+0`×2 offset, `+4`×32 slope) |
| `+0x2578..+0x258C` | viewport x, y, w, h, znear, zfar |
| `+0x26B0` / `+0x26E4 + i*0x2C` | Gnm DepthRenderTarget / RenderTarget[5] |

Constant buffers are not cached in the device: `alloc_constants` (`0x7DF630`) is hooked and
the returned pointer and size are kept per device, stage and slot.

| Hook | Notes |
|---|---|
| `0x7E15D0` draw_indexed | index buffer object `+0x1D70`: address `+0x30`, 32-bit if `+0x38` |
| `0x7E16A0` draw_indexed_instanced | sets the instance count around its draw_indexed call |
| `0x7E17C0` / `0x7E1710` | draw / draw_instanced |
| `0x7E1840` | draw from the engine's shared 16-bit index buffer (`**device`) |
| `0x7E1960` | inline vertices (copied; V# bases become offsets into the copy) |
| `0x7E2A00` clear(flags) | bits 2..5 color MRT 0..3 (color at `+0x40`), 0x40 depth (`+0x20`, stored as 1−z unless `+0x24`), 0x80 stencil (`+0x25`) |
| `0x7DEC20` set_vertex_buffer | record count per stream (handles with bit 31 use 14 pool bits) |

Primitive table `0x15D13C0`: engine prim 0..7 → 1, 2, 3, 4, 5, 6, 0x11 (rect list), 0x13 (quad list).

Internal passes that only manage CMASK / HTILE (`0x7E2390` fast-clear eliminate, `0x7E08A0`,
`0x7E0AE0`, `0x7DF850`) need nothing: our targets have no compression metadata.

### Ordering

Each record keeps the DCB write position when it was made. At `sceGnmSubmitCommandBuffers`
the submitted DCBs (and the INDIRECT_BUFFERs they call) give address ranges; the records inside
them are executed in (range, position) order, synchronously.

### Rendering

- Shaders: our translator; PS inputs are remapped from the Gnm semantic tables (PS input
  semantics u16 after the usage slots; VS export semantics u16 `{semantic, outIndex}`).
- Fetch shaders read per-instance streams with the instance id (v3): those bindings use
  instance rate.
- Rect lists: a generated geometry shader finds the right-angle corner (opposite the longest
  edge) and emits the fourth. Quad lists: indices rebuilt. Cube coordinates (s, t, face) are
  turned back into directions.
- Render targets are our images keyed by (address, format, size, slices); a T# whose base is a
  target samples it. Layered targets (CB_COLOR_VIEW slice range, e.g. the 32×32×32 grading
  LUT) are 3D images rendered slice by slice.
- Debugging: `D1_NG_FRAMES` + `D1_NG_DUMP_EVERY`, `D1_NG_TARGETS` (every target of a written
  frame), `D1_NG_PASSLOG=world` (pass list with texture resolution), `D1_NG_DEBUG=<frame>`.

## What runs where

```
engine threads (4 recording threads, 5 device objects)
  device API hooks (draw, bind, state, constants, targets)   <- record Vulkan directly
      |  one primary VkCommandBuffer per device command buffer (begin 0x7DCEC0 .. end 0x7DD060)
      v
sceGnmSubmitCommandBuffers / SubmitAndFlip (game's submission order)
  - map each submitted DCB to its recorded VkCommandBuffer
  - vkQueueSubmit2 in that order, with a timeline semaphore value per submission
  - the DCB is still scanned for the packets the CPU depends on (EOP / RELEASE_MEM labels,
    WRITE_DATA); they are applied when the GPU work actually completes
completion thread
  - waits on the timeline semaphore, then writes labels and raises the EOP / flip events
present
  - the flip's video-out buffer is a native image -> blit to the swapchain (window, overlay)
```

## Resources (created once, never looked up per draw)

| Engine object | Native object | Notes |
|---|---|---|
| shader object (VS / PS) | `VkShaderModule` (translated, cached on disk by code hash) | The vertex shader is keyed with its fetch shader. Variants by bound texture dimensions. |
| VS + PS + vertex decl + blend / depth / raster / stencil index + target formats + primitive | `VkPipeline` (cached; pipeline cache on disk) | ~400 per frame in-world; precompile known combinations at load. |
| texture `T#` (pointer to a stable engine object) | `VkImage` + view | Detiled on first use; refreshed when the engine streams new data in. |
| render target / depth target | `VkImage` (render target + sampled) | Same memory is aliased by the engine. Keyed by (address, format, size), so aliasing creates a separate image only when the description differs. |
| vertex / index buffer handle | `VkBuffer` | Imported guest memory (`VK_EXT_external_memory_host`) where possible, else copied with page-write tracking. |
| `alloc_constants` | slice of our persistently mapped upload ring | We return our own pointer: the engine writes straight into GPU-visible memory; the ring is recycled by our fences. |

## Descriptors

Push descriptors (core in Vulkan 1.4), set 0 for the VS and set 1 for the PS:
- binding = texture slot;
- 16 + sampler slot;
- 32 + constant buffer slot.

The device layer already skips redundant binds; we push only what changed before each draw.

## Milestones

1. **Vulkan bootstrap.** Our own loader, instance and device (1.4; dynamic rendering, sync2,
   push descriptors, maintenance5), plus the swapchain in the existing window. The null GPU
   keeps the game running.
2. **Clears and present.** The render-target / clear passes and the flip go to native images,
   so a solid frame reaches the window.
3. **UI.** Textured quads: textures, samplers, constant ring, the simplest pipelines.
4. **Menus and the class screen.**
5. **World.** G-buffer, lighting, shadows, post: every remaining pass, compared frame by frame
   against the shadPS4 reference path.
6. **Remove the shadPS4 renderer** from the build.

## Checks at each step

- Every translated shader passes `spirv-val`. This is the `d1-shadertool translate` tool plus
  the dump from `D1_NATIVE_GFX=observe D1_NATIVE_GFX_DUMP`.
- Native frames are compared against the shadPS4 path on the same scene (lavapipe locally,
  `D1_RENDER_EVERY` for in-world).
- Per-frame CPU cost goes in the perf overlay: the target is ~1–2 µs per draw on the engine's
  own recording threads.

## Status 2026-10-17: from capture-and-convert to the native device layer

Measured on the user's RTX 5090 (test-19, Earth patrol, ~3,900 draws a frame): the renderer
thread spends ~10.4 ms a frame converting captured draws (commands 3.6, pipeline 2.5,
descriptors 1.25, geometry 1-3 ms) and the game's frame is 13-19 ms. Today's state:

1. **No Gnm on the draw path (done, test-21).** Draws are captured at the device API
   (`findings/gpu_device_layer.md`) and the engine's Gnm draw code (CUE preDraw / postDraw,
   draw packets) no longer runs; recording threads queue their records in per-thread inboxes
   (no shared lock). State setters and events still go through Gnmx / PM4, so the null GPU
   still answers labels, EOP, occlusion dumps and DMA from the command buffers, and the
   (range, position) ordering above still holds.
2. **Parallel recording (next).** Split `Renderer::draw` into
   - *resolve*: everything that touches shared caches - pipeline (memoized), shader modules,
     image views, samplers, geometry cache entries, ring copies of constants - producing a
     plain `ResolvedDraw` (pipeline + layout, vertex / index bindings, descriptor writes,
     viewport, scissor, stencil, depth bias, predication slot);
   - *record*: `vkCmd*` calls from a `ResolvedDraw` only, with the redundant-state filter.
   Then record runs of plain draws inside one render pass in parallel: each run goes to a
   secondary command buffer recorded on a worker thread (inheritance: the pass's
   `VkCommandBufferInheritanceRenderingInfo`), the primary keeps pass begins / ends, clears,
   queries, predication, DMA / WRITE_DATA events and `vkCmdExecuteCommands` in order.
   Resolve is made thread-safe next (read-mostly caches behind shared locks, creation under
   an exclusive lock, per-worker ring regions) so that it runs in the workers too.
3. **Recording on the engine's own threads (after 2).** Each device context (main + 6
   workers, `G+0x10` / `G+0x2910+i*0x2860`) gets a recorder; a command list
   (`cmdlist_begin 0x7DCCE0` / `cmdlist_begin_inherit 0x7DD6A0` .. `cmdlist_end 0x7DCEC0`)
   becomes one primary command buffer recorded as the engine calls the device API, submitted
   in the engine's order by `device_submit_queued 0x7DD060`. Needs, from the device layer
   instead of PM4: occlusion (`0x7E12C0` / `0x7E1390`), the GPU copy queue (`0x7DACF0`),
   labels / EOP the CPU waits on (`0x7EF3A0`, `G+0xB8/BC`), and the constant-buffer bindings
   the constant update engine shares between contexts (a worker list sees the main
   context's bindings as of its submission point: snapshot them at `0x7DD6A0`).
4. **Persistent resources by engine handle.** Vertex / index buffers by tag handle
   (`set_vertex_stream 0x7DEC20`, `set_index_buffer 0x7DEE30`), textures by their tag's T#
   pointer, uploaded when loaded or streamed (descriptor patch sites `0x7D3BA0..0x7D6220`,
   copy queue) instead of write-watching guest memory.

Each step stays behind a switch with the previous path as fallback, and is checked against
frame dumps of the patrol and orbit scenes (`wrun.sh`, `orbrun.sh`) before it ships.

## Status 2026-10-18: lists recorded on the engine's threads (step 3 above)

`D1_ND_RECORD` (default on): every command list is recorded into its own Vulkan command
buffer by the engine thread that ends it (`cmdlist_end 0x7DCEC0` /
`cmdlist_end_and_submit 0x7DE950`, before the engine's own end runs). The GPU queue thread
only fills late constant buffers and submits the recorded command buffers in the engine's
submission order.

- **Recorders.** All per-recording state (command buffer, pass, state filter, queries,
  predication) is a `Recorder`; `rc()` is the calling thread's. Each submission slot has its
  own command pool. Slots are Idle / Recording / Recorded / Inflight.
- **Locking.** The renderer lock is held for everything that changes shared state: target
  set-up, pass changes, clears, queries, readbacks. It is released while runs of plain draws
  record, which take it only on cache misses. Each recording thread keeps its own pipeline
  cache, keyed by `targets_gen` (addresses whose sampled image changes kind use the shared
  memo). The flip releases the lock while waiting for the GPU and while presenting.
- **Uploads.** Texture uploads and new targets go to one shared upload slot, submitted
  before the next recorded lists (and before any list executed the old way).
- **Lifetimes.** Dropped images and geometry regions wait in a graveyard tagged with the
  recording sequence. They are freed once no slot that began at or before that tag is still
  in use. The ring's oldest live allocation is the minimum over the slots in use.
- **Constant buffers across lists.** The constant engine's bindings carry across command
  buffers. Measured with `D1_ND_CB_CHECK`: almost every draw of the worker contexts uses
  bindings made by lists submitted before it. A snapshot at list begin (in list-end order)
  disagrees for ~80% of them, so these bindings are only known at submission. A draw's slot
  that its list did not bind before it gets `addr = kLateCb | stage << 4 | slot`. The list
  reads one ring region per such slot, filled at submission from the bindings in effect
  when the list starts. An unbinding inside the list counts as a binding: the draw then
  keeps the buffer it captured, exactly the rule of the replay at submission. (A dark cloud
  over the aurora seen while fixing this turned out to be the sky's weather: it varies between
  runs on every path.)
- **CPU-visible events.** DMA is done at record time (in order with the list's draws) and
  again at submission. WRITE_DATA (labels) is done at submission only.
- Checked against the old path on patrol and orbit (frame dumps): differences match the
  run-to-run noise (wind, flickering lamps, idle animation).

## Status 2026-10-18 (later): GPU resources by the engine's own events (step 4 above)

See `findings/gpu_resources.md`. The core resource manager's graphics callbacks are wrapped:
bind, re-point, release, move and mip changes. Every texture, vertex buffer and index buffer
object gets an id and an epoch.

- **Draws** carry the identity per T# slot, vertex element and index buffer.
- **Renderer keys:** textures by identity plus the T# without its base address; buffers as
  whole-buffer copies by identity.
- **No write tracking:** neither is write-protected nor version-checked. After an event, the
  contents are compared once, so a move keeps the GPU copy.
- **Loader thread:** uploads resources when the engine binds or moves them, as a PC engine
  uploads at load.
  - Textures are detiled without the renderer lock and committed into the shared upload slot.
  - Work for a resource that changed again meanwhile is dropped.
- **Dynamic memory** keeps write tracking: the engine's own CPU-written textures and inline
  vertices.
- **Measured** (patrol, lavapipe): per frame, write faults 50 -> 5, geometry uploads 8.4 -> 0.9
  MiB, texture copies 11.3 -> 4.8 MiB; geometry memory 271 -> 48 MiB.
- Orbit loading: 2,061 textures and 5,310 buffers were uploaded ahead of use and 10,380 moves
  kept without a re-upload.
- Frames match the old path within run-to-run noise.
