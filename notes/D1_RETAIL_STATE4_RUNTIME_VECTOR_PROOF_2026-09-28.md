# Destiny 1 retail renderer state-vector proof — 2026-09-28

## Exact input

All executable observations in this note come from the owner-provided PS4 Destiny 1 executable:

- SHA-256: `672f03411c0503dfbcda804cbb9fb27cdd9a8d73a8bcb71bf0c4f688073b0833`
- size: 29,249,016 bytes
- source object used by the reproducible probes: `https://r2.houseofkublai.com/destiny/CUSA00219_01.33/eboot.bin`

The executable is independently fingerprinted by the existing renderer RE workflow before any result below is accepted.

## What is now proven

Retail D1 has a mutable four-byte renderer state vector at renderer-object offsets
`+0x15D0..+0x15D3`. This is not merely a serialized material field or a later-Tiger
convention: the exact D1 executable mutates the same four bytes inside active renderer
routines and performs renderer/stage submission calls between those mutations.

The exact semantic names of all four bytes are **not** claimed here. The proof is
structural/runtime ownership.

## Function 0x80A020: runtime state mutation around renderer submission

The Ghidra exact-build function graph identifies a real function beginning at
`0x80A020` and ending at `0x80A239`. It is called by `0x80B9F0`.

Inside that function, one renderer object at `[rbx+8]` receives three state-vector
configurations in sequence.

### First state

```text
0x80A180  mov dword ptr [rax+0x15D4], 0
0x80A18E  mov byte  ptr [rax+0x15D0], 0x82
0x80A195  mov word  ptr [rax+0x15D1], 0x828F
0x80A19E  mov byte  ptr [rax+0x15D3], 0x81
```

Little-endian state4: **82 8F 82 81**.

The function then calls `0x811A90` on the `[rbx+0x20]` source object with stage-like
argument `6`.

### Second state

```text
0x80A1C6  mov byte  ptr [rax+0x15D0], 0x82
0x80A1CD  mov word  ptr [rax+0x15D1], 0x82C0
0x80A1D6  mov byte  ptr [rax+0x15D3], 0x81
```

Little-endian state4: **82 C0 82 81**.

The function then calls `0x811A90` on the `[rbx+0x18]` source object, again with
stage-like argument `6`.

### Tail/restored state

After a paired scratch/state-stack restore call to `0x82BA20`, the function writes:

```text
0x80A20C  mov dword ptr [rax+0x15D4], 0
0x80A21A  mov byte  ptr [rax+0x15D0], 0x81
0x80A221  mov word  ptr [rax+0x15D1], 0x8282
0x80A22A  mov byte  ptr [rax+0x15D3], 0x81
```

Little-endian state4: **81 82 82 81**.

The function then returns.

This mutation sequence proves that the four bytes are active renderer runtime state.
It does **not** by itself prove that `81 82 82 81` is a universal engine default;
it may be a routine-local restored/default state for this renderer path.

## Additional exact executable contexts

The renderer string/xref probe independently finds other state4 writes near authored
D1 render-surface names.

### depth_stencil_quarter neighborhood

Near the exact executable `depth_stencil_quarter` xref:

```text
0x80C5BF  mov byte ptr [rax+0x15D0], 0x81
0x80C5C6  mov word ptr [rax+0x15D1], 0x818F
0x80C5CF  mov byte ptr [rax+0x15D3], 0x81
```

State4: **81 8F 81 81**.

### half_res_depth neighborhood

Near the exact executable `half_res_depth` xref:

```text
0x8B0490  mov byte ptr [rbx+0x15D0], 0x81
0x8B0497  mov word ptr [rbx+0x15D1], 0x81A2
0x8B04A0  mov byte ptr [rbx+0x15D3], 0x81
```

State4: **81 A2 81 81**.

These contexts strengthen pass/runtime ownership and provide exact pass-context
vectors. They still do not, on their own, assign semantic names to lanes or decode
selector indices into Orbis state descriptors.

## Scratch-state helpers around the mutations

`0x82B940` and `0x82BA20` form a paired renderer scratch/state-allocation stack.
`0x82B940` advances a renderer-local allocation cursor, records the previous slot
state in a stack at `+0x1428..`, and marks the selected resource bit. `0x82BA20`
pops that record and restores the previous allocation slot/cursor.

This is relevant because the `0x80A020` state4 tail write occurs after the pop, but
the pair itself is **not** yet named as a pipeline-state push/pop operation.

## Consequence for material +0x20 state

The exact D1 material keeps four raw bytes at Material `+0x20`. Existing D1
cross-fixture evidence promotes only material byte0 `0x88` to blend-state selector
index 8.

The executable proof here supplies a separate missing fact: renderer/pass-owned
four-byte selector-shaped state exists at runtime. Therefore a zero material lane can
be represented structurally as **no material override / inherit the active renderer
pass lane**, without inventing the semantic meaning of that lane.

This is the basis for the importer-owned `D1PassStateProvider` /
`D1FixedFunctionRuntimeBindingPlan` architecture. Nonzero material selectors remain
fail-closed until their exact D1 selector-table semantics are independently proven.

## Still withheld

The following are not promoted by this evidence:

- semantic lane names for bytes 1, 2, and 3;
- selector-index -> exact Orbis blend/depth-stencil/rasterizer/depth-bias table entries;
- whether `81 82 82 81` is a global default versus a local restored state;
- exact human-facing identity of the two `0x811A90` submissions in `0x80A020`;
- pass/framebuffer ownership for arbitrary materials;
- MRTZ interaction with the effective fixed-function state.

The next proof target is the **read-side consumer** of `+0x15D0..+0x15D4`, followed
through its table lookups/native API writes. That is the point at which individual
selector lanes and indices can be promoted from structural identities into exact D1
fixed-function semantics.

## Exact merge consumer and selector application

Retail function `0x82B3F0` closes the selector-composition rule directly from D1 code.
It loads three four-byte vectors:

1. renderer base/pass state from `[renderer + 0x15D0]`;
2. source/material state from `[source + 0x20]`;
3. renderer runtime override from `[renderer + 0x15D4]`.

For both overlays, the function performs the same bytewise high-bit select:

```text
mask   = (((override >> 7) & 0x01010101) * 0xFF)
result = base XOR (mask AND (base XOR override))
```

It first composes source/material over renderer base/pass, then composes the
`+0x15D4` runtime override over that result. This is exact D1 executable behavior,
not a continued-Tiger inference.

The final low-seven-bit selector bytes are dispatched in this exact order:

- byte 0 -> `0x7DE4A0`;
- byte 1 -> `0x7E0F70` / `0x7E0DE0`;
- byte 2 -> `0x7DE590`;
- byte 3 -> `0x7DE640`.

### Byte 0: blend state

`0x7DE4A0` selects a table record and applies the resulting state to render targets
0, 1, 2 and 3 through repeated `0xF7E7C0` calls. This independently agrees with the
already cross-fixture-promoted D1 Material byte0 `0x88` -> blend-state index 8 proof.

### Byte 2: rasterizer / clip-cull state

`0x7DE590` selects 16-byte records from table `0x15D2390`. The next state table starts
at `0x15D2420`, so the exact D1 table span is `0x90 = 9 * 16` bytes.

The selected record is emitted through packet helpers that target exact GFX7 context
registers:

- `0xF80640` -> context register `0x204` = `PA_CL_CLIP_CNTL`;
- `0xF80790` -> context register `0x205` = `PA_SU_SC_MODE_CNTL`.

This closes byte 2 as the rasterizer / clip-cull state lane from D1 executable behavior.
The continued Tiger nine-state rasterizer table is useful independent convergence, but
its serialized record layout is not imported into D1.

### Byte 3: depth-bias / polygon-offset state

`0x7DE640` selects 12-byte records from table `0x15D2420`, converts the selected
values, and emits exact GFX7 polygon-offset registers:

- `0xF808A0` -> `0x2E0 = PA_SU_POLY_OFFSET_FRONT_SCALE` (+ adjacent front offset);
- `0xF80910` -> `0x2E2 = PA_SU_POLY_OFFSET_BACK_SCALE` (+ adjacent back offset).

This closes byte 3 as the depth-bias / polygon-offset state lane from D1 executable
behavior.

### Byte 1: depth / stencil state

Byte 1 is dispatched through `0x7E0F70` into the larger `0x7E0DE0` state builder.
The builder emits three exact GFX7 DB packet groups:

- `0xF7E950` -> context register `0x200 = DB_DEPTH_CONTROL`;
- `0xF7E9B0` -> context register `0x10B = DB_STENCIL_CONTROL`;
- `0xF7E840` -> two-register write beginning at
  `0x10C = DB_STENCILREFMASK`, followed by
  `0x10D = DB_STENCILREFMASK_BF`.

This closes byte 1 as the depth/stencil state lane from exact D1 executable behavior.

### Final lane ordering

All four selector categories are now independently closed from the retail D1 binary:

1. byte 0 — blend;
2. byte 1 — depth/stencil;
3. byte 2 — rasterizer / clip-cull;
4. byte 3 — depth-bias / polygon-offset.

The lane order agrees with continued Tiger lineage, but no lane category now depends
on that lineage for its D1 promotion.

## Importer consequence

The importer/runtime exact contract now preserves the native three-layer order rather
than flattening material state into a single guessed pipeline descriptor:

`renderer pass/base -> source/material -> renderer runtime override -> low7 state tables`.

The Rust importer implements the same bytewise high-bit merge in
`merge_pipeline_state_selector_bytes` and exposes a draw-time
`D1FixedFunctionRuntimeStateProvider` for the two renderer-owned vectors. The old
pass+material helper is retained only as a structural helper for cases where the
`+0x15D4` runtime override is independently proven inactive.
