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
