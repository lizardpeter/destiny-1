# D1 Xur shader semantic wave 3

Date: 2026-09-07
Target: Xur (`StringHash 46C55854`, entity model `80C88CEF`)

Status: **`D1_XUR_NATIVE_GCN_DATAFLOW_WAVE3_EXACT`**

GitHub Actions run: `34151603863`  
Workflow commit: `cd814df84f78fe03a56286c75d796edc20351816`  
Artifact: `D1-TOWER-XUR-SHADER-SEMANTIC-WAVE3`  
Artifact ID: `10029537974`  
Artifact ZIP SHA-256: `a25bcc0eae93760161852c3263b1b3df28c14f1a00b03a2043876613f5ae5e33`

The workflow completed every fail-closed proof step successfully against the pinned exact native-shader census and exact 54-material local-state checkpoints.

## Exact progress after wave 3

- **8 / 31** unique native GCN binaries now have exact instruction-level dataflow proofs.
- Those binaries cover **12 / 38** exact stage structural lifting units.
- **7 / 33** combined material structural families have both their current VS and PS native dataflow closed.
- **22 / 54** current Xur materials now have both current VS and PS native binaries dataflow-closed.
- Pixel-shader native-dataflow coverage is **22 / 54 materials**.
- Vertex-shader native-dataflow coverage is **48 / 54 materials**.

These numbers are native instruction/dataflow closure only. TFX producer semantics, render/blend/depth/raster state, live external-material permutation selection, fetch-shader byte-layout closure and full portable retail-equivalent recreation remain separate proof gates.

## Newly closed pixel-shader families

Wave 3 promotes three additional exact GCN families through `tools/d1_xur_ps_direct_rgb_normal_families_proof.py`:

### `8087688C` — 4 materials

Materials: `808762D7`, `808764CC`, `808767B0`, `808767B3`.

The exact GCN proves:

```text
nx = 2*t1.r - 1
ny = 2*t1.g - 1
nz = sqrt(saturate(1 - nx*nx - ny*ny))
N  = normalize(nx*attr1.xyz + ny*attr2.xyz + nz*attr0.xyz)

mrt1.rgb = saturate(0.5 + 0.375*N)
mrt1.a   = 0
mrt0.rgb = t0.rgb
mrt0.a   = attr0.w
```

`t1` is therefore an instruction-proven signed-XY normal source. `t0` is an instruction-proven direct MRT0 RGB source; higher-level albedo/base-color naming remains withheld.

### `80AADCB3` — 5 materials

Materials: `80876545`, `80876547`, `80876548`, `80876863`, `80876864`.

The exact GCN proves the same signed-XY normal reconstruction and direct `t0.rgb` MRT0 path, with:

```text
k = 0.375 + 0.125*t0.a
mrt1.rgb = saturate(0.5 + k*N)
mrt1.a   = b0[9]
mrt0.rgb = t0.rgb
mrt0.a   = attr0.w
```

Thus `t0.a` is instruction-proven to modulate the packed-normal scale for this family.

### `80AAE1C7` — 3 materials

Materials: `808764CF`, `808767B2`, `80876867`.

This family adds a BC4 scalar resource at `t2`. The native shader samples the resource with the W component selected by its descriptor/instruction path and proves:

```text
k = 0.375 + 0.125*t2.native_w
mrt1.rgb = saturate(0.5 + k*N)
mrt1.a   = b0[9]
mrt0.rgb = t0.rgb
mrt0.a   = attr0.w
```

No gloss/roughness/high-level material name is assigned to that scalar without additional evidence.

## Shared Xur articulated vertex path is now mostly closed

Wave 2 had already closed the one-palette-record shared VS GCN family used by 31 materials. Wave 3 adds the exact two-influence and four-influence dual-quaternion paths.

### Two-influence VS `80876960` — 3 materials

The native binary proves post-fetch lanes for two palette indices and two U8-like integer weight lanes. The weights are explicitly converted to float and multiplied by exact `1/255` in the main GCN program:

```text
w0 = float(weight0_u32) / 255
w1 = float(weight1_u32) / 255

q0 = api10[2*index0]
d0 = api10[2*index0 + 1]
q1 = api10[2*index1]
d1 = api10[2*index1 + 1]

if dot(q0,q1) < 0:
    w1 = -w1

Qraw = w0*q0 + w1*q1
inv  = 1 / length(Qraw)
Q    = Qraw * inv
D    = (w0*d0 + w1*d1) * inv
```

The exact position/tangent-basis path is:

```text
p = api11[20:22] + api11[23]*source_position
translation = 2*(D*conjugate(Q)).xyz
P = rotate(Q,p) + translation

N = rotate(Q,source_normal)
T = rotate(Q,source_tangent)
B = handedness * cross(N,T)
```

It exports the established Xur interface:

```text
param0 = float4(N, saturate(dot(api11[28:30],N)+api11[31]))
param1 = float4(T.xyz, T.z)
param2 = float4(B,1)
param3 = float4(uv,uv)
param4 = float4(P,1)
```

### Four-influence VS family `8087695B` / `809DE9AB` — 14 materials

Both serialized headers resolve to the exact same 1,052-byte GCN binary. The native program loads four real-quaternion palette records and four adjacent dual records. `q0` is the hemisphere reference; weights 1, 2 and 3 are conditionally sign-corrected independently from `dot(q0,qi)` before the blend:

```text
for i = 0..3:
    qi = api10[2*index_i]
    di = api10[2*index_i + 1]

for i = 1..3:
    if dot(q0,qi) < 0:
        wi = -wi

Qraw = sum(wi*qi)
inv  = 1 / length(Qraw)
Q    = Qraw * inv
D    = sum(wi*di) * inv

translation = 2*(D*conjugate(Q)).xyz
P = rotate(Q,p) + translation
```

Normal, tangent, handed bitangent, UV, clip-space position and `param0..param4` exports then follow the same native contract as the other shared Xur articulated VS families.

The four post-fetch weight lanes are instruction-proven as blend weights, but their **pre-main-shader fetch encoding** is deliberately not assigned yet. That belongs to the fetch-shader/source-stream closure gate.

## Why this matters for Xur skinning

The current native evidence no longer supports treating Xur articulation as a generic linear-weighted matrix skin approximation. The dominant retail Xur vertex paths are explicitly **dual-quaternion transform-palette paths**, including hemisphere-corrected two- and four-influence blending. Any portable Xur exporter that maps the source influence bytes directly to ordinary glTF linear blend skinning without reproducing/equivalently baking this native transform behavior needs separate validation before it can be called retail-equivalent.

## Next exact targets

The highest-value next pixel-shader target is `808768C0`, which covers five materials and is already paired with now-closed VS dataflow for all five. Closing that one GCN would therefore increase both-stage material coverage immediately.

In parallel, the articulated vertex frontier is now specifically narrowed to the fetch-shader/source-stream side: establish exact source offsets/formats for the post-fetch index/weight lanes and connect those bytes to the already source-closed D1 inline/separate weight formats. No guess about joint/index encoding is required in the main GCN anymore.
