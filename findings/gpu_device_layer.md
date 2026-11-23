# Destiny 1 (CUSA00219 01.33) — Bungie GPU device layer map

Sources: Ghidra decompiles in `ghidra/out/<addr>.c`, disassembly `full.s`, caller counts by direct
`call`/`jmp` (tail calls included). Addresses are eboot offsets. **Names are proposals** unless stated.
"CONFIRMED" = read from the decompile; "GUESS" = inferred from usage or from the Gnm/Gnmx API.

## 0. The layers

```
renderer / TFX (0x7E6000-0x8C0000; render jobs 0x810660, TFX 0x829300/0x82b3f0..0x82be10)
      |  ints (preset indices), Bungie tag handles, Bungie shader wrappers, Gnm::Texture* (from tags)
      v
Bungie device layer  (0x7DA000-0x7E6000)       <- recommended replacement surface
      |  "Device context" D (0x2860 bytes, one per recording thread), caches last-bound state
      v
Sony Gnmx (static, 0xF88000-0xF90000): GfxContext (D+0x60/+0xEC0), ConstantUpdateEngine (gfx+0xC0)
      v
Sony Gnm builders (0xF7C000-0xF88000) -> PM4 into the DCB/CCB
```

Every engine draw/dispatch/clear/copy reaches the GPU through the Bungie device functions below; the
renderer never calls Gnm/Gnmx directly except a handful of resource-descriptor setup sites (§4).

## 1. Device-layer functions

`D` = device context (param 1, sometimes typed `long*`), `G = *(D+0)` = global device,
`gfx = *(D+0x50)` = current Gnmx GfxContext, `cue = gfx+0xC0` (ConstantUpdateEngine).
Gnm shader stage numbers: 0 CS, 1 PS, 2 VS, 3 GS, 4 ES, 5 HS, 6 LS (GUESS from Gnm enum; consistent
with the per-stage caches below). Bungie "API stage" (TFX / 0x7def20 arg) maps 1→PS 2→VS 3→GS 4→HS
5→CS 6→LS 7→ES (CONFIRMED from 0x7def20's switch; 0x7e2c90 does the mapping for TFX).

### Command-list lifecycle / submission
| addr | name | signature | what it does | callers |
|---|---|---|---|---|
| 7dc180 | device_context_init | (D) | zero D, init the two GfxContexts (f8eb70 at D+0x60, D+0xEC0), reset state, D+0x26=1 (enabled) | — |
| 7e40a0 | device_init | (D, desc) | GfxContext init (f8eba0 ×2 with DCB/CCB memory), video out open + 3 display RenderTargets (f81f80, fmt 0xF2E00A), flip queue "eq_to_wait_flip", "ORBIS vertex stream layouts" pool, builds the built-in shaders (copy/clear VS/PS at G+0x20..0x60) from embedded binaries (7e4fd0/f8e910) | 1 (7e3740) |
| 7e3740 | device_system_init | (G') | allocs G (0x13438), device_init for main D (G+0x10), then 6 worker D's (7e5d50) at G+0x2910+i*0x2860 | |
| 7e3a20 | device_context_get | (G, i) → G+0x2910+i*0x2860 | worker context i (0..5) | 1 (0x810660) |
| 7e38c0/7e3910 | device_context_acquire_main | | bind main D to the thread: TLS `fs:[*0x1a1f4c8]` = D | |
| 7e3a00 | device_context_current | () → TLS D | | many |
| 7e3860/7e39a0 | device_context_release | | clear TLS | |
| 7dcce0 | cmdlist_begin | (D) | take slot G+0x2e0+n*0x938 (command-list record), select GfxContext D+0x60+idx*0xE60 (idx = G+0xB4), reset cached state (7dc270), register with the ordering system 0x26e4840 (7ef9c0) | 6 |
| 7dd6a0 | cmdlist_begin_inherit | (D, cmdlist rec, ?, saved_state*) | begin a worker list and *restore* a full state snapshot (4 RTs + depth RT, viewport/scissor, blend/DS/raster presets, …) from the main context: used by parallel render jobs | 1 (0x810660) |
| 7dcec0 | cmdlist_end | (D, ?, flush_kind) | close DCB (7ef3a0 end-of-list label, 7db810 records DCB/CCB ranges), queue the record into G's submit ring (G+200[64]), flip GfxContext index | 4 |
| 7de950 | cmdlist_end_and_maybe_submit | (D) | as above, then 7dd060 if `DAT_018dcc30` | 1 |
| 7dd060 | device_submit_queued | (D) | drain G's ring: wait for GPU progress, `sceGnmSubmitCommandBuffers` / `sceGnmSubmitAndFlipCommandBuffers` (import thunks 0x12ac5f6 / 0x12ac606), GPU timing stats at G+0x13310.. | 4 |
| 7dcaf0 | device_frame_reset | (D) | gfx reset (f8ede0), CE ring reset (f84db0), 7dc270 | 3 |
| 7dacf0 / 7db340 | gpu_copy_queue_flush / _item | | ring of pending GPU memory copies (0x26df268, 16-dword items) → DmaData (f8f3a0) in ≤4000-item command lists. Used for buffer/texture uploads to GPU memory (GUESS: streaming) | 4 / 1 |
| 7e03a0 | gpu_flush_wait | (D) | EOS write + WaitRegMem + event 0x38 (cache flush & wait): a full barrier | 7 |
| 7e5590 | present_prepare | (D, size) | sets display RT (f811c0 flip target), viewport, depth off, binds back buffer as RT0 (f8f0e0) | 2 |

### State (all cache the last value in D and skip redundant calls)
| addr | name | signature | GPU state | D fields | callers |
|---|---|---|---|---|---|
| 7dc270 | state_reset | (D, full) | unbind 4 RTs + depth RT, index buffer, VS/PS, every T#/S# slot of all 7 stages, CB slot VS0 | 0x1d20-0x1d50, 0x1d60, 0x1d68/70, 0x1d78[32], 0x1df8[32], 0x1e78[7][16] T#*, 0x2278.. S#*, 0x25a8-0x25e8, 0x27c0 | 7 |
| 7dfd10 | set_render_targets | (D, rt_set*) | 4 color RenderTargets (Gnm::RenderTarget, 0x2C bytes each at rt_set+0x00.., enables at +0xC0[4]) → f8f0e0(gfx, i, rt); depth (Gnm::DepthRenderTarget at +0xD4, enable +0x108) → f7eec0; full-target viewport if +0x1B0 size | copies to D+0x26e4+i*0x2c, D+0x26b0, D+0x27c4[4] | 4 |
| 7de370 | set_viewport | (zmin f, zmax f, D, x, y, w, h) | VIEWPORT 0 scale/offset (f80340) | D+0x2578..0x258c | 33 |
| 7dfac0 | set_viewport_scissor | (zmin, zmax, D, x,y,w,h) | viewport + screen scissor (f80440) + guard band (f7ebb0/f7ec30) | +0x2578.., +0x2590.. | 3 |
| 7e0430 | restore_viewport_and_targets | (D) | re-applies viewport, blend, depth control, 5 RTs, depth RT, clears cached VS/PS | | 5 |
| 7de4a0 | set_blend_preset | (D, idx) | CB_BLEND{0..3}_CONTROL from table 0x15d16c4 (stride 0x24) + CB_TARGET_MASK (f7e740) | +0x25b4, +0x25d8 | 17 |
| 7de590 | set_depth_preset | (D, idx) | DB_DEPTH_CONTROL (f80790) + DB_RENDER_CONTROL? (f80640) from table 0x15d2394 (stride 0x10) | +0x25c0, +0x25d0/d4 | 17 |
| 7de640 | set_poly_offset_preset | (D, idx) | depth bias: PA_SU_POLY_OFFSET_* (f808a0/f80910/f80830) from table 0x15d2424 (stride 0xC) | +0x25bc | 6 |
| 7e0f70 / 7e0f90 / 7e0de0 | set_stencil_preset | (D, idx[, ref]) | DB_DEPTH_CONTROL stencil part, DB_STENCIL_CONTROL, stencil ref/masks (f7e950/f7e840/f7e9b0) from table PTR_01a1f4c0 (stride 0x28) or default 0x15d1e38 | +0x25b8, +0x25dc..0x25e8 | 28/3/3 |
| 7de710 | set_depth_bounds | (min, max, D, enable) | depth bounds test (f81dd0 + f7ea80) | +0x25c4..0x25cc | 2 |
| 7de860 | set_primitive_setup | (D, mode) | PA_SU_SC_MODE_CNTL-type state (f7fe20; cull/fill, value 0xAD/0xB0 special) + f7fa90 | +0x25f0 | 4 |
| 7e2a80 | set_index_reset | (D, bool) | primitive restart (f806d0) | +0x27c0 | 6 |
| 7de800 | set_vs | (D, VsWrapper*) | CUE setVsShader(cue, &w->gnmVs(+0x14), w->modifier(+0), w->fetchShaderAddr(+8)) | +0x1d28 | 4 (TFX 82b490/82b5c0/82b730, 7c95a0) |
| 7de7b0 | set_ps | (D, Gnm::PsShader*) | CUE setPsShader | +0x1d30 | 4 |
| 7deb70 | set_vertex_layout | (D, layout*) | selects a vertex stream layout (count @+0; per element 8 bytes from +0x14: +0x14 fmt dword, +0x18 offset byte, +0x19 stream byte); invalidates bound streams | +0x1d60 | 22 |
| 7dec20 | set_vertex_stream | (D, vb_tag_handle, stream, offset, count) | resolves Bungie vertex-buffer tag (tag table 0x1a238a0: +0x28 base, +0x30 vertex count; stride = layout[stream+1]) and builds one V# per layout element of that stream (f7cf90 initAsVertexBuffer) → CUE setVertexBuffers(VS, elem, 1, V#) (f8b600) | +0x1d78[32] handle, +0x1df8[32] offset | 46 |
| 7dee30 | set_index_buffer | (D, ib_tag_handle) | tag +0x30 base, +0x38 32-bit flag, +0x3c count → setIndexSize (f7f790), setIndexCount (f7f840), setIndexBuffer (f7f7e0); restart index 0xffff/0xffffffff | +0x1d68, +0x1d70 | 20 |
| 7def20 | set_texture | (D, api_stage, slot, Gnm::Texture*) | CUE setTextures(stage, slot, 1, T#) (f8afd0); null → dummy T# `PTR_01a1f4b8`; invalid (f84710) → dummy | +0x1e78+stage*0x80+slot*8 | 2 (TFX 829300) |
| 7de8c0 | set_texture_gnm_stage | (D, gnm_stage, slot, T#*) | same, Gnm stage index | | 1 (82be10) |
| 7df310 / 7df250 / 7e1110 | set_ps_texture / _from_tag / _null | | PS stage T# from pointer / texture tag handle (tag data *is* the 32-byte Gnm::Texture; 0x57f80 is identity) / dummy | | 8 / 3 / 2 |
| 7e1510 | unbind_texture_everywhere | (D, T#*) | replace a T# in every stage/slot by the dummy (before a texture is freed / rendered to) | | 23 |
| 7df420, 7df4b0, 7df540, 7df5c0 | set_samplers_{ps,vs,es?,gs?} | (D, first_slot, count, Gnm::Sampler*) | CUE setSamplers(stage, slot, n, S#) (f8b410); caches at +0x2278/+0x22f8/+0x2378/+0x23f8 (S# ptrs). Not in the function-start table (inside 0x7df310's extent) | | 2/1/1/1 (TFX 0x82af83.., 0x7cad7f) |
| 7df630 | alloc_constant_buffer | (D, gnm_stage, slot, bytes) → void* | allocate from the DCB (f7feb0), init V# (f7d180), CUE setConstantBuffers(stage, slot, 1, V#) (f8b500); caller fills the returned memory | | 24 (TFX 82bd10, 81fb90.., 89c660, 8b3980) |

### Draws / dispatch
All draws: `setPrimitiveType(table 0x15d13c0[prim])` (f7f1e0) → `cue.preDraw` (f8df60) → Gnm draw → `cue.postDraw` (f8e880). Gated on D+0x26.
| addr | name | signature | packet | callers |
|---|---|---|---|---|
| 7e15d0 | draw_indexed | (D, prim, ?, first_index, index_count) | DrawIndex2 at index buffer base + first*(size) | 9 (via 7da370 thunk ×10) |
| 7e16a0 | draw_indexed_instanced | (D, prim, …, instances, …) | setNumInstances + 7e15d0 | 1 (via 7da3b0) |
| 7e17c0 | draw | (D, prim, vertex_count) | DrawIndexAuto | 40 |
| 7e1710 | draw_instanced | (D, prim, count, ?, instances) | NumInstances + DrawIndexAuto | 3 |
| 7e1840 | draw_indexed_up | (D, prim, index_ptr, prim_count) | indices in user memory (CPU pointer *D+0?), count from prim count | 2 |
| 7e1960 | draw_up | (D, prim, prim_count, vertices*, stride) | copies vertices into the DCB (f7feb0), V# per layout element, DrawIndexAuto ("draw user primitives": UI/debug) | 4 |
| 7e0780 | dispatch | (D, cs?, x, y, z, flush) | CUE preDispatch (f8e680), DispatchDirect (f7f4a0); optional EOS label + wait | 2 (7e05c0, 7e1d10) |
| 7e2cb0 | draw_fullscreen | (u0v0, u1v1 (xmm), D, w, h) | built-in VS/PS at G+0x132f0/+0x132f8, CB VS0 = {1/w,1/h,uv}, rect list (prim 0x11), 3 verts | 2 |

### Built-in passes (fullscreen rect-list draws using the built-in shaders)
| addr | name | notes | callers |
|---|---|---|---|
| 7e0240 | bind_single_rt | RT0 = arg, others/depth null, blend/depth off, full viewport | 4 |
| 7e0040 | copy_texture | VS G+0x20/+0x48, PS chosen by format (G+0x50/0x60), T# PS0, rect, then EOS wait | 3 |
| 7e0ae0 / 7e08a0 | copy_depth / resolve_depth | depth→color copies through 7df850; f83530 builds a T# over the depth surface | 2 / 1 |
| 7df850 | clear_depth_by_draw | depth RT bound, DB_RENDER_CONTROL clear bits (f7e8d0 0xCC), rect draw, EOS wait | 3 |
| 7e2480 | clear_color_targets | (clear color xmm0/1, D, mrt_mask) PS = G+0x28+k*8, CB PS0 = color | 1 (7e2a00) |
| 7e2760 | clear_depth_stencil | rect draw with stencil/depth write state | 1 (7e2a00) |
| 7e2000 | decompress_target | fast-clear eliminate / DB decompress pass (f7fcd0, f7d730 CMASK) | 4 |
| 7e1d10 / 7e1ea0 / 7e2200 | clear_by_compute | RW buffer/texture (f8b0c0/f8b2e0) + dispatch: CMASK/HTILE/fast clears | 1 each |
| 7e05c0 | compute_copy | CB CS0 (6 dwords), T# CS0, RW T# CS0 (f8b1f0), dispatch (w+7)/8 × (h+7)/8 | 1 |
| 7e12c0 / 7e1390 | occlusion_begin / occlusion_end | zero 16 qwords of the query, ZPASS / predication (f80ae0, f805c0) | 4 / 4 |

### Gnmx entry points used (Sony library, for reference)
| addr | GUESS (Gnmx API) | evidence |
|---|---|---|
| f8afd0 | ConstantUpdateEngine::setTextures(stage, slot, n, T#[8 dwords]) | copies n*8 dwords to CE shadow at stage*0x642+slot*8, dirty bits |
| f8b410 | CUE::setSamplers (4 dwords, offset 0x480) | |
| f8b500 | CUE::setConstantBuffers (V#, offset 0x540) | |
| f8b600 | CUE::setVertexBuffers | |
| f8b0c0 / f8b1f0 / f8b2e0 | CUE::setRwBuffers / setRwTextures / setBuffers | |
| f8b790 | CUE::setVsShader(cue, VsShader*, modifier, fetchShaderAddr) | stores at +0x2a8, user-data from shader +0x8.. |
| f8b8c0 | CUE::setPsShader(cue, PsShader*) | +0x2b0 |
| f8b980 | CUE::setCsShader | |
| f8df60 / f8e880 | CUE::preDraw / postDraw (flush dirty CE RAM → user SGPRs; f8bff0 DumpConstRam, f8d880 SetShReg) | |
| f8e680 | CUE::preDispatch | |
| f8f0e0 | GfxContext::setRenderTarget(slot, RenderTarget*) (copies the 0x2C-byte RT, CMASK/fmask fixups) | |
| f7eec0 | GfxContext::setDepthRenderTarget | |
| f8f4b0 | Gnmx::setupScreenViewport | |
| f7feb0 | CommandBuffer::allocateFromCommandBuffer(size, align) | |
| f7f1e0 / f7f260 / f7f320 / f7f890 | setPrimitiveType / drawIndexAuto / drawIndex / setNumInstances | |
| f7f790 / f7f840 / f7f7e0 / f80730 | setIndexSize / setIndexCount / setIndexBuffer / setPrimitiveRestartIndex | |

## 2. Device context layout (D, 0x2860 bytes)

| off | meaning |
|---|---|
| +0x00 | G (global device: +0x20..0x60 built-in shader wrappers, +0x80 video-out handle, +0xA0 flip event queue, +0xB0 back buffer index, +0xB4 GfxContext ping-pong index, +0xB8/BC GPU progress labels, +0xC8[64] submit ring, +0x2C8/2CC ring head/tail, +0x2E0+n*0x938 command-list records, +0x132E0.., +0x132F0/F8 fullscreen VS/PS, +0x13300 fullscreen V#, +0x13310[8] GPU timing) |
| +0x10/+0x14 | lock words |
| +0x18 | owning thread id (0x7dc9e0) |
| +0x24 | flag (selects stencil table) |
| +0x26 | draws enabled |
| +0x50 | current Gnmx GfxContext* (one of the two below) |
| +0x58 | current command-list record |
| +0x60, +0xEC0 | two Gnmx GfxContexts (0xE60 bytes; DCB at gfx+0, CCB gfx+0x80, CUE gfx+0xC0) — double-buffered between lists |
| +0x1d20..0x1d50 | cached VS (+0x1d28), PS (+0x1d30), others (value 1 = unknown/invalid) |
| +0x1d60 | vertex stream layout*; +0x1d68 index-buffer tag handle; +0x1d70 index-buffer tag data |
| +0x1d78[32] | vertex stream tag handles; +0x1df8[32] stream offsets |
| +0x1e78[7][16] | bound T# pointers per Gnm stage (0x80 per stage) |
| +0x2278/+0x22f8/+0x2378/+0x23f8 [16] | bound S# pointers (PS, VS, …) |
| +0x2578..0x258c | viewport x,y,w,h,zmin,zmax; +0x2590..0x259c scissor |
| +0x25a8..0x25f0 | preset indices and packed register values (blend +0x25b4/+0x25d8, depth +0x25c0/+0x25d4, stencil +0x25b8/+0x25dc/+0x25e0/+0x25e4, poly offset +0x25bc, depth bounds +0x25c4..cc, prim setup +0x25f0) |
| +0x26b0 | depth RenderTarget copy (0x34); +0x26e4+i*0x2c color RenderTarget copies (4) |
| +0x27c0 | primitive restart flag; +0x27c4[4] RT enables |
| +0x28fc / +0x28f8 (param_1[0x51f]) | display width/height (GUESS) |

Contexts: main D at G+0x10 (render thread, TLS), 6 workers at G+0x2910+i*0x2860 (0x7e3a20), used by
render jobs (0x810660: picks worker `param[8]`, begins with 7dd6a0 inheriting the main context's
saved state at `frame+0xc18`, builds a TFX render context (0x822270/0x822350, D at +0x15c0)).
**Command building is multi-threaded**: up to 7 contexts record concurrently; lists are ordered
by the dependency/label system at 0x26e4840 (7ef9c0 register, 7ef890, 7ef3a0 end label) and
submitted in order by 7dd060. A replacement can record each context into its own Vulkan
secondary/primary command buffer and keep that ordering.

## 3. API surface a replacement must implement

Minimum (everything the renderer calls): 7dcce0, 7dd6a0, 7dcec0, 7de950, 7dd060, 7dcaf0, 7dc270,
7dfd10, 7de370, 7dfac0, 7e0430, 7de4a0, 7de590, 7de640, 7e0f70/7e0f90/7e0de0, 7de710, 7de860,
7e2a80, 7de800, 7de7b0, 7deb70, 7dec20, 7dee30, 7def20, 7de8c0, 7df310, 7df250, 7e1110, 7e1510,
7df420/7df4b0/7df540/7df5c0, 7df630, 7e15d0, 7e16a0, 7e17c0, 7e1710, 7e1840, 7e1960, 7e0780,
7e2cb0, 7e0240, 7e0040, 7e0ae0, 7e08a0, 7df850, 7e2480, 7e2760, 7e2000, 7e1d10/7e1ea0/7e2200,
7e05c0, 7e12c0, 7e1390, 7e03a0, 7dacf0/7db340 (GPU copies), 7e5590 (present), plus init 7e40a0.
≈55 functions. Callers outside: TFX (82b3f0/82b490/82b5c0/82b730/82bd10/82be10/829300), render
features 0x7c5080–0x8c2aa0, 0x106cf20/0x1073400/0x1055e80 (late-binary callers of 7dec20/7e12c0).
Direct Gnm/Gnmx users outside this layer (descriptor setup, not command emission): 0x7ca770,
0x7d3ba0–0x7d6220 (texture/RT descriptor setup: f83530 Texture init, f841b0 setBaseAddress,
f84620/f84690 mip range), 0x819d20–0x81c460 (render target / texture views for passes),
0x8bdc10, 0x8be050, 0x05bf50/0x05c5b0/0x0c6aa0 (debug/screenshot), 0xf8xxxx Gnmx internals.

## 4. Resource representation

- **Shaders**: VS = Bungie wrapper `{u32 shader_modifier @0, u64 fetch_shader_addr @8, Gnm::VsShader @+0x14}`
  (7de800), from the TFX technique (0x82d070); PS = raw `Gnm::PsShader*` (0x82d020). CS via
  0x7e0780 path (built-ins). Fetch shaders are pre-generated (address in the wrapper) — the vertex
  layout (+0x1d60) gives formats/offsets directly, so a native path can skip fetch-shader parsing.
- **Textures**: Bungie texture tags whose tag data *is* a 32-byte `Gnm::Texture` (T#) — 0x57f80 is
  the identity accessor (347 callers). GPU memory comes from the tag/package loader; descriptors are
  patched at 0x7d3ba0..0x7d6220 (setBaseAddress, mip range: streaming, GUESS). Samplers: `Gnm::Sampler*` arrays from TFX.
- **Vertex / index buffers**: Bungie tag handles (index into tag table `*0x1a238a0`, 0x40-byte
  slots) — VB tag +0x28 base, +0x30 count; IB tag +0x30 base, +0x38 is32, +0x3c count. Stable,
  loaded with the package: ideal for one-time upload + caching by handle.
- **Constant buffers**: transient, allocated in the DCB per draw by 0x7df630 and filled by the
  caller (TFX bytecode interpreter 0x829300 / bespoke code). Native path: same allocator API backed
  by a Vulkan ring.
- **Render targets**: `Gnm::RenderTarget` (0x2C) / `Gnm::DepthRenderTarget` (0x34) structs inside a
  Bungie RT-set struct (7dfd10); created by 0x819d20..0x81c460 / 0x7e40a0 (display buffers).
- **GPU copies / uploads**: queue at 0x26df268 flushed by 0x7dacf0 (DmaData); 7e05c0 compute copy.

## 5. Recommended hook points and risks

Hook (replace) the ~55 Bungie device functions, not Gnmx: their arguments are already semantic
(preset indices, tag handles, T#/S# pointers, shader wrappers), they cache state per context,
and every engine draw passes through them. Gnmx CUE preDraw/postDraw is a poorer cut (state already
lowered to CE RAM / SH registers). Plan:
1. Per device context D → our VkCommandBuffer + state block; hook 7dcce0/7dd6a0/7dcec0/7dd060 to
   begin/end/submit in the existing order (ring G+0xC8, flip in 7dd060).
2. Map preset tables (0x15d16c4 blend, 0x15d2394 depth, 0x15d2424 poly offset, stencil table
   *0x1a1f4c0) once into Vulkan dynamic state / pipeline keys.
3. Shaders: translate the Gnm shader binaries once (existing GCN→SPIR-V), keyed by wrapper pointer;
   vertex input from the layout (+0x1d60) instead of fetch shaders.
4. Textures/VB/IB by tag pointer → persistent VkImage/VkBuffer (upload on first bind; invalidate
   from the streaming patch sites / GPU copy queue).

Risks: (a) other code may still write PM4 directly or read GfxContext internals (e.g. 0x7e0780 pokes
gfx+0x28 flags; occlusion/predication results are read back by the CPU from query memory);
(b) labels/EOP writes the CPU waits on (7dd060 waits on G+0xBC vs *0x26e4860; 7ef3a0 labels) must
still be signalled; (c) compute passes write GPU memory the CPU or later passes read as T#s
(aliasing of RT memory and textures — the current renderer's hardest problem remains); (d) Gnmx
internals called from outside the layer (0x7d3ba0..0x81c460) only build descriptors — harmless
but their T# base addresses still refer to guest memory; (e) the sampler setters 0x7df420.. are
missing from the function-start table; (f) unknown semantics remain for several args (marked GUESS).
