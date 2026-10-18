# Destiny 1 (01.33): what the engine's CPU expects from the GPU / device layer

This document covers what a native Vulkan device layer must signal so the engine keeps running.
It is based on Ghidra decompiles in `ghidra/out/`, the disassembly in `full.s`, and import names
from `evidence/generated/d1_import_surface.json` (PLT stub + 6 = Ghidra `thunk_FUN_...`; the
mapping is in `plt_names.tsv`).

Abbreviations:
- `D` is a device context; `G = *D` is the global device.
- `CBM` is the command-buffer memory manager at `0x26E4840`.

Marked GUESS where inferred.

## 1. Command lists, labels, submission

### CBM (`0x26E4840`): one GPU-written label orders and recycles everything

**Layout:**

| Offset | Field |
|---|---|
| +0x00 | `slot table`: 0x200 entries of `{i32 value, u32 mem}` |
| +0x08 | read index |
| +0x0C | write index |
| +0x1C | running counter (starts at 1, 0x7EF510) |
| +0x20 | `label`: a pointer to one u32 in GPU memory (`0x7EF560`: `b49b0(4, 0xE)`, initialised to 0) |
| +0x28, +0x30 | DCB/CCB memory allocator: 0x80000-byte chunks, `0x7EF8B0` / `0x7EEF80` |

`DAT_026E4860` = `CBM+0x20` = the label pointer.

**Slot lifecycle:**
- **Allocate** (`0x7EF460`, called from `cmdlist_begin` via `0x7EF890`): `slot.value = counter + 0x80000`, then `counter++`.
  - If the slot is still busy, it first waits in `0x7EF180` (see the next item).
- **Wait on a busy slot** (`0x7EF180`): `while (*label - slot.value < 0) sceKernelUsleep(30)` (`0x7EF180`).
  - This is a hard CPU wait on the GPU label. It is the back-pressure when all 512 list slots are in flight.
- **End-of-list label** (`0x7EF3A0`, called by `cmdlist_end 0x7DCEC0` and `0x7DE950`): `slot.value -= 0x80000` (it becomes the list's counter `n`).
  - It then emits **EVENT_WRITE_EOP** through `f80c90(gfx, 4, 0, label, 1, n, 0, 0)`: when the list finishes, the GPU writes the 32-bit `n` to `*label` (data_sel 1, no interrupt).
  - This happens for every list, because `DAT_026DF291` is in .bss, always 0, and has no writers.
- **Reclaim** (`0x7EF2A0`, polled by the allocator `0x7EF8B0`, which spins with `usleep(10)` up to 1.5M tries):
  - Once `*label - slot.value >= 0`, the slot is cleared and its DCB memory is freed (`0x6AEF0`).
  - Value `0xCDCDCDCD` means "Found invalid", which aborts.

**What the CPU relies on:**
- `*label` must rise monotonically through list counters, in **submission order**.
- Signed 32-bit differences are used for every comparison.
- A native layer writes `n` to `*label` when (or after) that list's GPU work completes.
  - It is safe to write as soon as the list's Vulkan work is submitted, as long as our own frames-in-flight limit paces the CPU.
  - If it is never written, the engine deadlocks within 512 lists or 2 frames.

### Command-list records and the submit ring (`G`)

**Records:** `G+0x2E0 + n*0x938` (`n = G+0x2DC++`, reset per frame in `0x7DCB50`).

| Record offset | Field |
|---|---|
| +0x18 | ready flag: 0 while recording, 1 when ended (atomic) |
| +0x1C | CBM slot |
| +0x20 | GfxContext index |
| +0x24 | segment count (max 64, "Ran out of command buffer segments") |
| +0x28 | "flip list" byte |
| +0x30 [64] | DCB address |
| +0x230 [64] | CCB address |
| +0x430 [64] | DCB bytes |
| +0x530 [64] | CCB bytes |
| +0x630 / +0x730 / +0x830 | per-segment tags (`0x7DB810`) |
| +0x930 | ring index |

**Ring:** `G+0xC8` (`200`) holds `[64]` record pointers. Write index `G+0x2C8` (incremented by enqueue), read index `G+0x2CC`, pending count `G+0xC0`.

**Ring entries are made in two ways:**
- **`cmdlist_end 0x7DCEC0`** enqueues the record if it has any DCB/CCB bytes, and flips `G+0xB4 ^= 1`.
- **`0x7DEA90`** (called from `0x811AB0`, the main-thread job kickoff) *reserves* a ring entry for a worker list before the worker records it. The ready flag is 0, `G+0xB4 ^= 1`, and a CBM slot is allocated.
  - The worker (render job `0x810660` on a job thread) then begins on that record with `cmdlist_begin_inherit 0x7DD6A0`, using worker context `G+0x2910 + i*0x2860` from `0x7E3A20`.
  - It ends with `0x7DE950`, which writes the EOP label, sets ready = 1, and submits if `DAT_018DCC30 = 1` (initial data) and the GPU has caught up (`*label - G+0xBC >= 0`).

**Order within a stage, as built by `0x811AB0`:**
1. End the main list with `0x7DCEC0(D, rec, 0)`.
2. Reserve one record per job with `0x7DEA90`.
3. Kick the jobs (`0xFB400` / `0xFB4F0` / `0xFB670`).
4. Begin a new main list with `0x7DCCE0`.

So the ring order is main, workers, main.

**`device_submit_queued 0x7DD060`** drains the ring in order under the `G+0x2D4` lock (taken if `G+0x2D8`). For each entry:
- It stops at the first entry that is not ready (`rec+0x18 == 0`). This is the only ordering mechanism.
- It waits `while (*label - G+0xBC < 0) { if (!0xFB860()) usleep(300); }`, where `G+0xBC` is the counter of the flip list from 2 flips ago. This is the frame-latency limit, explained below.
- If the entry is not a flip list: `sceGnmSubmitCommandBuffers(rec+0x24, rec+0x30, rec+0x430, rec+0x230, rec+0x530)`.
- If it is a flip list:
  - It records GPU timing in `G+0x13310 [8 x 0x20]` (described below).
  - It calls `sceVideoOutSetFlipRate(G+0x80, G+0x13428)`. The engine switches 30/60 Hz by measuring flip intervals, which is why the log toggles "flip rate 0/1".
  - It calls `sceGnmSubmitAndFlipCommandBuffers(count, dcbs, dcbsizes, ccbs, ccbsizes, G+0x80 videoHandle, G+0xB0 buffer index, flipMode 1, flipArg = ++G+0x13418)`.
  - On failure it builds a tiny list on the current GfxContext (`f80c90` label write, `f81220` NOP marker) and resubmits it.

**Threads:**
- Main lists are recorded on the render thread (main `D = G+0x10`, bound through TLS `fs:[*0x1A1F4C8]` by `0x7E3910`).
- Worker lists are recorded on job threads (`job #0..3`).
- `0x7DD060` runs on the render thread (`0x7DCE80`, the end of the frame) and on job threads (`0x7DE950`).
- The GPU copy flush (`0x7DB340` / `0x7DB4B0`) also submits from the render thread.

**GPU-side waits:**
- No WAIT_REG_MEM between lists.
- Every WAIT_REG_MEM (`f80E00`) is an in-list full barrier on a dword the same list writes just before with EOS/EOP. The callers are:
  - `0x7E03A0` gpu_flush_wait (also `f80f10` event 0x38, a cache flush)
  - `0x7DF850`
  - `0x7E0040`
  - `0x7E0780` with the flush flag
  - `0x7E1EA0`
  - `0x7E2000`
- In Vulkan these are full pipeline barriers inside the command buffer.
- Cross-list ordering is purely submission order, so a single queue with submissions in ring order is enough.

**Frame latency:**
- In `0x7DCEC0`, when `param_3 == 1` (the flip list): `G+0xBC = G+0xB8` and `G+0xB8 = this list's counter`.
- `0x7DD060` (and `0x7DE950`'s "caught up" test) wait until the GPU has finished the flip list two frames back. GfxContexts are double-buffered (`D+0x60` / `D+0xEC0` via `G+0xB4`).

**Per-frame reset:** `0x7DCB50` (from `present_prepare 0x7E5590`) zeroes `G+0x2DC`, `G+0x2D0`, `G+0xC0`, `G+0x132E0[buf]` and begins the frame's first main list.

## 2. Frame pacing and flip

**Device init (`0x7E40A0`)** sets up:
- `sceVideoOutOpen` (`G+0x80` = handle).
- `sceKernelCreateEqueue(G+0xA0, "eq_to_wait_flip")`.
- **`sceGnmAddEqEvent(eq, 0x40 /*EOP*/, 0)`** and **`sceVideoOutAddFlipEvent(eq, handle, 0)`**.
- `sceVideoOutSetFlipRate(handle, 1)`.
- `sceVideoOutRegisterBuffers(handle, 0, 3 buffers)`.

**Frame start (`0x7E5450`**, called by the frame function `0x7ED5F0` from `0x7EAD40`, and by the "Graphics Heartbeat" loading-screen loop `0x7E6420`, thread named at `0x7E6310`), once buffer 0 has been reached (`D+0x28E4`):
- `sceKernelWaitEqueue(eq, 1 event, timeout NULL)`: it waits for **one EOP or flip event**.
- Then `do sceVideoOutGetFlipStatus(...); while (gcQueueNum >= 3) usleep(1)`.
- It also matches `flipArg` against the `G+0x13310` timing ring and stores `{tsc, gcQueueNum, flipPendingNum}`.

**Frame end (`0x7DCE80`):**
1. `f80D70(gfx, 4, 0)` is **EVENT_WRITE_EOP with interrupt and no data**. It raises the EOP event (0x40) on `eq_to_wait_flip` when the frame's GPU work completes.
2. `cmdlist_end(D)`, the flip list.
3. `device_submit_queued(D)`.

**After that, `0x7E56C0`:**
- `G+0xB0 = (G+0xB0 + 1) % 3` (next back buffer).
- `sceSystemServiceHideSplashScreen` once.
- **`sceGnmSubmitDone()`**.

**`present_prepare 0x7E5590`:**
- `sceGnmInsertWaitFlipDone(gfx, handle, G+0xB0)` (via `f811C0`): a GPU wait until that display buffer is no longer scanned out.
- Binds display render target `D + 0x2860 + buf*0x2C`.

**What a native layer must do on each flip:**
- **Present** the frame.
- **Run the HLE flip bookkeeping.** This is our `do_flip(index, arg)` in `hle_gpu.cpp`:
  - FlipStatus count, `flip_arg`, `tsc`, `current_buffer`
  - `gc_queue_num` / `flip_pending_num` decrement
  - trigger `kFilterVideoOut` event 6 on `flip_eqs`
- **Trigger the Gnm EOP event (0x40)** on the equeues registered with `sceGnmAddEqEvent`. This is our `signal_eop()`, now called when the null GPU sees an EOP with `int_sel`.

The engine needs at least one of those two events per frame, and `gcQueueNum < 3`.

SubmitAndFlip's side effects (our HLE `sceGnmSubmitAndFlipCommandBuffers`) are:
- `gc_queue_num++` / `flip_pending_num++` at submit
- `do_flip` at present

Keep them, minus the DCB parsing. `sceGnmSubmitDone` can be a no-op. `InsertWaitFlipDone` maps to swapchain image acquisition.

**GPU timing ring:** `G+0x13310 [8 x {flipArg, submitTsc, flipTsc, gc/pending}]`. It is only used to choose the flip rate (`G+0x13428`, threshold `DAT_0165FE38`); our SetFlipRate only logs.

## 3. Other places the CPU waits for or reads GPU results

**Occlusion queries:**
- **Calls:** `occlusion_begin 0x7E12C0` / `occlusion_end 0x7E1390`, on `D` with a query handle `*q = {i32 busy, u64* results}`.
- **Begin:**
  - The CPU zeroes the 16 qwords of results.
  - `f80AE0(gfx, 0, addr)` emits DMA_DATA (zero 0x80 bytes), WAIT_REG_MEM and EVENT_WRITE ZPASS_DONE (event 0x15) into `results + 0`.
  - `f805C0` sets DB_COUNT_CONTROL to perfect counts.
- **End:** ZPASS_DONE into `results + 8`.
- **Result layout:** 8 DBs × `{u64 begin, u64 end}`, stride 16. Bit 63 of each is the valid bit.
- **CPU reader `0x7E13E0`** (called by `0x1057390`): ready only when **all 16 qwords have bit 63 set**. Visible samples = Σ(end − begin). It is polled, not waited on.
- **Callers:**
  - `0x7FC800` (lens flares / light halos; also **GPU predication**: `0x7E14B0` predication_begin(D, q) → SET_PREDICATION `f809F0`, and `0x7E14D0` predication_end → `f80A80`; neither is in the function-start table)
  - `0x7D1840` (object visibility via `0x7D2170`)
  - `0x1055E80` / `0x1055FD0` (the late-binary visibility system that reads results through `0x1057390`)
- **Native requirement:** Vulkan occlusion query per begin/end. Write `begin = 0 | bit63` and `end = count | bit63` (or cumulative counters) into all 16 qwords when the query completes. Predicated draws use conditional rendering.

**`gpu_flush_wait 0x7E03A0`:** GPU-side only. EOP writes 1 to a dword in the DCB, then WAIT_REG_MEM for 1, then event 0x38. In Vulkan this is a full barrier. The CPU does not wait.

**GPU copy queue (`0x26DF268`, 0xA00 items of 0x40 bytes):**
- **Head/tail:** `+0x28000` (u32 write, u32 read).
- **Item:**

  | Offset | Field |
  |---|---|
  | +0x00 | state (1 = filled) |
  | +0x08 | src |
  | +0x10 | dst |
  | +0x18 | bytes |
  | +0x20 | completion callback |
  | +0x28 / +0x30 | callback args |
  | +0x38 | fence |
  | +0x3C | status (0 queued, 1 submitted, 2 done) |

- **Producers** (`0x7DA960`):
  - `0xDB260`: resource relocation / defragmentation (from `0xD9FE0`)
  - `0x7D3560`, `0x7D37B0`: texture stream-in or swap (from `0x7D4E20`)
- **Flush** `0x7DACF0` (render thread, each frame from `0x7EAD40`):
  - `0x7DB2D0` takes batch fence `n = DAT_026DF280++` and begins a list.
  - `0x7DB340` emits DMA_DATA src→dst (`f8F3A0`) per item, in chunks, at most 4000 per list; then sets `status = 1` and `fence = n`.
  - `0x7DB4B0` emits EOP `f80c90(..., DAT_026DF288, 1, n)`, then ends and submits the list.
- **Second label:** `DAT_026DF288` is a u32 in GPU memory, initialised to `DAT_026DF280 - 1` (`0x7DB230`).
- **Completion** `0x7DAB10` (render thread, after the flush): for each submitted item with `*DAT_026DF288 - fence >= 0`, it calls the callback, which finalises the relocation (frees the old memory, updates handles), then sets `status = 2`.
- **Native requirement:** memmove src→dst (guest memory; the engine's resources live there), invalidate our caches for `[dst, dst+bytes)` and `[src...)`, then write `n` to `*DAT_026DF288`.

**Render-target readbacks:** no explicit CPU wait was found in this pass. The current renderer writes small never-sampled targets back (`queue_readbacks`). GUESS: exposure/luminance. Keep the existing behaviour.

**GPU exception watchdog:** `gpu_exception_watchdog` (`0x8061A0` / `0x8062A0`):
- `sceKernelCreateEqueue` + `sceKernelAddGpuExceptionEvent`, then it blocks in `sceKernelWaitEqueue`.
- Events `0xA0D0C005..8` only print "GPU Exception" messages.
- Native requirement: nothing (never signal it).

**GPU timestamps:** no EOP with data_sel 3/4 (GPU clock) was found in the device layer. Timing uses FlipStatus TSC.

## 4. Compute

**Dispatch paths:**
- The only DispatchDirect is `f7F4A0`, called only by `dispatch 0x7E0780` (CUE preDispatch `f8E680`, `setCsShader` `f8B980`; optional flush: EOS + WAIT_REG_MEM + event).
- `0x7E0780` callers:
  - **`compute_copy 0x7E05C0`** (from `0x818AE0`): CB CS0 = 6 dwords, T# CS0 source, RW T# CS0 destination (`f8B1F0`), groups (w+7)/8 × (h+7)/8, built-in CS.
  - **`clear_by_compute 0x7E1D10`** (from `0x7E1EA0` ← `0x7E2200` ← `clear_color_targets 0x7E2480`): RW buffer / RW texture (`f8B0C0` / `f8B2E0`) fills, i.e. CMASK/HTILE/fast-clear metadata. Native requirement: plain clears, no metadata.
- **Surface to implement:** one copy kernel (texture → RW texture) and the clear path. No engine (TFX) compute shaders were found.

## 5. Other per-frame code that touches Gnm outside the device layer

These calls build **descriptors only**: Texture/RenderTarget/Buffer init, setBaseAddress, mip range, format queries. No PM4 is written.
- `0x7CA770`
- `0x7D3BA0..0x7D6220` (texture / render-target descriptor setup, streaming patches)
- `0x819D20..0x81C460` (pass render-target and texture views; `f7D730` / `f7E540` / `f82AD0` / `f82B00` are format and size accessors)
- `0x8BDC10` / `0x8BE050`

**Device-layer users, not PM4:**
- `0x1055E80` / `0x1055FD0`: occlusion
- `0x106CF20` / `0x1073400`: draws and streams through the device layer

**Gnm imports and where they're called:**
- `sceGnmSubmitDone`: `0x7E56C0`; `0x5B0E0` via `f84810`
- shader setters: `f7F8E0` and neighbours, inside Gnmx
- `DrawInitDefaultHardwareState`: `f7E5E0`
- `DispatchInitDefaultHardwareState`: `f84DB0`
- `IsUserPaEnabled`: `f848F0`

**Conclusion:** once the device layer (§1–§4, plus `0x7E14B0` / `0x7E14D0` / `0x7E2A00` clear) is replaced, nothing else emits PM4 per frame.

## Minimal signal set for a native layer

1. **List counter:** per list, the CBM counter `n` (from `slot.value - 0x80000` at end) → `*(u32*)*(0x26E4860)`, in ring order.
   - `G+0xB8` / `G+0xBC` keep working if `0x7DCEC0`'s bookkeeping runs or is reproduced.
2. **Frame end:** EOP event 0x40 on Gnm-registered equeues, plus the flip event and FlipStatus updates (`do_flip`). `gc_queue_num` must stay below 3 while frames are queued.
3. **Copy batches:** `n` → `*(u32*)DAT_026DF288` after the memmoves.
4. **Occlusion:** all 16 result qwords with bit 63 when a query completes.
5. **Nothing else** is waited on by the CPU.
