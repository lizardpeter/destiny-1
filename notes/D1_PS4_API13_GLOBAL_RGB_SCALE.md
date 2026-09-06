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
> scales final RGB in at least two independent Tower shader families.

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
