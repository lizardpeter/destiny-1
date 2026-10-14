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
