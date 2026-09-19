# D1 PS4 `api13[6:7]` global RGB-scale proof

Date: 2026-09-06  
Platform: **PS4 retail only**  
Status: **independent native-shader arithmetic corroboration closed; engine producer/name/live values unresolved**

## Scope

The Tower `809DCD66` reversal established that pixel-shader `api13` dwords 6 and
7 both survive into final RGB as independent scalar multipliers.  This note
records the independent PS4-only corroboration so that conclusion does not depend
on Xbox/DXBC evidence.

No engine name such as exposure, brightness, frame scale, global lighting, or
postprocess gain is assigned here.  Those names require direct producer evidence.

## Cross-corpus census

Existing exact retail PS4 shader artifacts were re-analyzed with the generic
OrbShdr/GCN constant-buffer mapper:

```text
Tower top shaders      40 rows
Tower common shaders   65 rows
Tower light shaders    32 rows
                       -------
                       137 rows
                       135 unique pixel shaders
```

The union contains exactly one shader using `ImmConstBuffer api13`:

```text
80CA0BE9
```

Its sole `api13` scalar-buffer access is:

```text
s_buffer_load_dwordx2 s[10:11], s[12:15], 0x6
```

The native `OrbShdr` input-usage table maps `s[12:15]` to `ImmConstBuffer api13`.
Therefore:

```text
s10 = api13[6]
s11 = api13[7]
```

Green census:

```text
Actions run 34053028846
commit      2444074df7395d1692b1c3cba93a903f1063358c
```

Reusable census:

```text
tools/d1_ps4_api13_census.py
.github/workflows/d1-ps4-api13-census.yml
```

## Independent peer shader

Exact retail peer identity:

```text
material        80CA0BC6
vertex shader   80AAE147
pixel shader    80CA0BE9
native PS       80CA0BF7
package         ps4_city_tower_destination_0250_5.pkg
textures        none
```

Native GCN identity:

```text
code bytes      480
gcn sha256      86282025ea6bbe21ca42153702d14fbf443b5f2d605cf96f5f15d11663170b70
```

The relevant terminal dataflow is:

```text
s_buffer_load_dwordx2 s[10:11], s[12:15], 0x6
...
v_mul_f32 v1, s3, v0
...
v_mul_f32 v7, s11, v1
...
v_mul_f32 v2, s10, v7
v_mul_f32 v3, v3, v2
v_mul_f32 v4, v4, v2
v_mul_f32 v0, v0, v2
v_cvt_pkrtz_f16_f32 v2, v3, v4
v_cvt_pkrtz_f16_f32 v0, v0, v1
exp mrt0, v2, v2, v0, v0 done compr vm
```

Thus the peer shader forms:

```text
scale = api13[6] * api13[7] * local_scalar
```

and applies the resulting scale to all three RGB lanes before packing.  The
separately carried alpha lane `v1` is packed afterward and is not multiplied by
`api13[6]` or `api13[7]`.

This is materially different from the `809DCD66` family: `80CA0BE9` is a
textureless procedural shader with a different material/TFX family.  The shared
use of the exact same global dword pair is therefore independent corroboration,
not duplicate material evidence.

Reusable exact-dataflow validator:

```text
tools/d1_ps4_api13_peer_validate.py
```

## What is now proven

Across two independent PS4 retail pixel shaders:

```text
809DCD66  rgb *= api13[6] * api13[7]
80CA0BE9  rgb *= api13[6] * api13[7] * local_scalar
```

For both, the `api13` pair participates in RGB intensity and is not an opacity
source.

Therefore the strongest source-safe description is:

> `api13[6]` and `api13[7]` are shared PS4 runtime scalar inputs whose product
> scales final RGB in at least two independent Tower shader families.  The Crota
> expansion below raises the observed cross-family count without resolving the producer.

## Crota high-detail expansion — 2026-09-19

The source-closed Crota high-detail material reversal adds three more native PS4
pixel-shader programs with the same terminal-RGB dependency:

```text
8108E953  gcn a5fe9ef18b14e9f204aedd5f0d8cf34021bf5812f445521cd9b9fec18dfd9552
8108E955  gcn 2bb9b4e27b0aa204e5d0b47ce8d85746853da1187d8b0ce2700b94009810795f
8108E956  gcn b2b8147deb1b5ed70ee9306784d8760eb82b7aef6cb07cf308e3ed64645d9e69
```

For each program, exact Sony input-usage provenance plus terminal-RGB backward
slicing proves that **R, G, and B all depend on api13 dwords 6 and 7**.  Material
specialization leaves the same factor in every selected Crota high-detail color
material:

```text
8108E953  RGB = local_color_term * api13[6] * api13[7]
8108E955  RGB = local_color_term * api13[6] * api13[7]
8108E956  RGB = local_color_term * api13[6] * api13[7]
```

The paired Crota computed-alpha programs provide a useful negative control:

```text
8108E958  terminal MRT0.A has no api13 dependency
8108E959  terminal MRT0.A has no api13 dependency
```

For the selected retail materials, the attenuation branch can be specialized much
further (including exact BC1 alpha-one substitutions), yet api13 remains absent
from terminal alpha.  This independently reinforces the earlier Tower conclusion
that this pair belongs on the **RGB scale path**, not the opacity path.

Reusable Crota proofs:

```text
tools/d1_gcn_cbuffer_usage_analyze.py
tools/d1_gcn_terminal_rgb_slice.py
tools/d1_gcn_terminal_alpha_slice.py
tools/d1_crota_api13_family_boundary.py
tools/d1_crota_color_material_specialize.py
.github/workflows/d1-crota-main-visual-shader-closure-v3.yml
```

The strongest source-safe description is therefore now:

> `api13[6]` and `api13[7]` are shared PS4 runtime scalar inputs whose product
> scales terminal RGB across at least five independently structured retail pixel
> shader programs/families observed in Tower and Crota evidence.  The exact engine
> producer/name and live values remain unresolved.

This expansion does **not** promote the Charm `Frame scope` label or its preview
fallback values into retail proof.

## Frame-scope lineage lead — not yet retail proof

Pinned Charm renderer lineage labels constant buffer 13 as `Frame scope`.  Its
Source2 export path supplies `cb13_0 = Time`; a later revision also supplies
`cb13_1 = float4(0.25,1,1,1)`.  Under ordinary float4 indexing, dwords 6 and 7
would be `cb13_1.zw = 1,1`.

This is a strong lead because it matches the explicit 1.0 preview fallbacks used
by the current Blender adapter.  It is **not promoted here** because that exporter
contains hand-authored compatibility values and is not itself a capture of live
D1 PS4 runtime constant-buffer contents.

Historical lineage checked:

```text
Charm merge-d1 commit e5c4c7b0affcc00a988441e8f913dad7d0aa9bb9
  Source2 path did not yet provide the later cb13_1 fallback.

Charm material-view commit 2512d0fd0a807a27e49ddf3484e969393b05e186
  explicitly emitted cb13_0 = Time.

later Charm lineage
  labels resource index 13 as Frame scope and emits cb13_1 = float4(0.25,1,1,1).
```

The next promotion requires direct D1 evidence for the runtime producer or live
buffer contents.

## Remaining boundary

1. Recover the exact D1 runtime producer/name for API 13 / constant-buffer 13.
2. Recover live retail values for dwords 6 and 7, rather than relying on the
   lineage fallback of 1.0/1.0.
3. Keep the two scalars separate in forensic/export metadata even if their retail
   default values later prove equal.
4. Do not use either scalar as opacity or blend-state evidence.
