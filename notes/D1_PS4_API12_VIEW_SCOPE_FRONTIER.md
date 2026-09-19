# D1 PS4 api12[28:30] View-scope lineage frontier

Date: 2026-09-19  
Platform under promotion: **D1 PS4 retail**  
Status: **retail slot/dword/dataflow exact; View/camera producer is corroborating lineage only**

## Exact Crota retail facts

The source-closed Crota high-detail shader set contains five native pixel-shader
programs whose Sony OrbShdr input-usage tables declare `ImmConstBuffer api12`:

```text
8108E953
8108E955
8108E956
8108E958
8108E959
```

Exact GFX700 constant-buffer provenance plus terminal-output backward slicing shows
that all five consume **api12 dwords 28, 29 and 30** on their terminal color or
computed-alpha path.

The common native arithmetic is structurally:

```text
vector = api12[28:30] - attr2.xyz
vector = normalize(vector)
d      = dot(vector, attr0.xyz)
```

The resulting unnamed scalar `d` feeds the material-specific angular terms used
by the three terminal-RGB programs and both computed-alpha partner programs.

The retail-safe statement is therefore:

> api12[28:30] is one shared runtime three-component vector input to the Crota
> high-detail angular shader path.

No camera/view/light/eye/position semantic follows from the arithmetic alone.

## Charm lineage cross-check

Current Charm shader lineage contains:

```text
// Based on CBuffer index
TfxScope.View  = 12
TfxScope.Frame = 13
```

in:

```text
Tiger/Schema/Shaders/TFX Bytecode/Externs.cs
blob sha 7311688c71ab3a9e9d6eacd5393d07254688bace
```

Its Source2 shader adapter builds a `float4 cb12[15]` View-scope compatibility
buffer.  Because the first entry is a 4x4 matrix occupying vectors 0–3, the
subsequent entries place:

```text
cb12[7] = float4(g_vCameraPositionWs / 39.37, 1)
```

and `cb12[7].xyz` is exactly dwords **28–30**.

This is unusually strong lineage corroboration because both the buffer index and
the exact vector index align with the retail Crota dependency.  It is still not a
capture of the live D1 PS4 producer or bytes: the Source2 path intentionally
constructs compatibility values for export/preview.

## Why the semantic remains unpromoted

A familiar graphics interpretation would be:

```text
normalize(camera_position - surface_position) dot surface_basis
```

but two additional links remain unclosed on retail PS4:

1. the live engine producer/value identity of api12[28:30];
2. a source-level semantic identity for the relevant `attr0` and `attr2`
   varyings rather than only their exact raw GNM/VS-param lineage.

The native math plus Charm lineage is not sufficient to rename those inputs.

## Current source-closed Crota tooling

```text
tools/d1_gcn_cbuffer_usage_analyze.py
tools/d1_gcn_terminal_alpha_slice.py
tools/d1_gcn_terminal_rgb_slice.py
tools/d1_crota_angular_varying_lineage.py
tools/d1_crota_color_material_specialize.py
tools/d1_crota_attenuation_symbolic_reduce.py
.github/workflows/d1-crota-main-visual-shader-closure-v3.yml
```

## Next promotion gates

1. Run a broad PS4-native api12 dword census across independent shader corpora and
   quantify reuse of dwords 28–30.
2. Find another native program where api12[28:30] participates in a source-closed
   positional relation, not merely the same Crota family.
3. Recover an exact D1 PS4 runtime writer/producer or primary code path for
   constant-buffer slot 12.
4. Close the vertex-fetch-to-VS-param-to-PS-attr semantic chain for Crota
   `attr0` and `attr2`.
5. Until then, portable reconstruction may expose a **View-scope lineage
   candidate** but must keep the retail engine semantic/value WITHHELD.

## Policy

Retail GCN/OrbShdr evidence and Charm lineage are separate evidence classes.
A matching buffer index and vector index is corroboration, not proof of live
retail contents.
