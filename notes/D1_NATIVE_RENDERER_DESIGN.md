# Native renderer design (Vulkan 1.4, no shadPS4)

Status 2026-10-14:
- The device layer is mapped: see `D1_NATIVE_RENDERER_DEVICE_LAYER_2026-10-14.md`.
- Our own GCN decoder, SPIR-V builder and translator are done: all 384 shaders seen in-world
  translate with no remarks and pass `spirv-val`.
- This file is the plan for the runtime side.

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
