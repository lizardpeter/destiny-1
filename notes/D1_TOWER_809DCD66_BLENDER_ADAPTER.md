# D1 Tower `809DCD66` Blender adapter

Date: 2026-09-06  
Scope: PS4 retail Tower, `VS 80CA0DDA -> PS 809DCD66`  
Status: **native-equation Blender preview path closed and executable on the active Blender 5.2.1 LTS baseline; native blend state, `api13[6:7]` runtime producers/values, and dynamic TFX `Frame[0]` time unit/phase remain unresolved**

This note extends `D1_TOWER_809DCD66_NATIVE_SHADER_PROOF.md` through the portable
Blender boundary. It does not weaken the existing native proof boundary.

Project-wide active Blender policy is recorded in `notes/BLENDER_BASELINE.md`.
The current baseline is **Blender 5.2.1 LTS**. Older 4.5.13 evidence below is
retained only as historical compatibility evidence.

## Retail tangent-W audit

The exact `80C98254` target population contains 12 geometry variants and 64
placements. The source tangent-W population over the actually referenced unique
vertices is:

```text
raw int16 W -32767 : 188
raw int16 W +32767 :  40
SNORM W       -1.0 : 188
SNORM W       +1.0 :  40
```

No source triangle mixes handedness signs:

```text
mixed-W triangles: 0
```

The native VS identity is replayed directly on every placement:

```text
Nraw = M3x3 * source_normal
Traw = M3x3 * source_tangent.xyz
invN = 1 / length(Nraw)
N    = Nraw * invN
T    = Traw * invN
B    = cross(N,T) * source_tangent.w
```

The audit found all 64 instance transforms nonsingular and orientation-preserving.
Their normalized bases are extremely close to orthogonal, but their scale is not
perfectly uniform:

```text
maximum normalized-basis orthogonality error  2.294974000284037e-07
maximum per-instance scale spread             0.002403815521812458
```

That measurable non-uniform scale matters because Bungie's VS intentionally uses
**N's reciprocal length for both N and T** rather than independently normalizing
T. The resulting native tangent lengths span approximately:

```text
0.9990098476409912 .. 1.0009784698486328
```

Therefore standard glTF `TANGENT` promotion / regenerated Blender tangent space is
**not** the proof-preserving path for this family even though source W itself is
perfectly compatible with the ordinary +/-1 handedness convention.

The faithful Blender adapter preserves source basis data explicitly:

```text
_D1_NORMAL
_D1_TANGENT_XYZ
_D1_TANGENT_W
_D1_TANGENT        # original forensic xyzw remains retained
```

and replays the native transform equations in shader nodes.

Green classification run:

```text
Actions run 34049076586
commit      63febf537eeabb5954421f8711da50c26d193553
```

Reusable audit/classifier:

```text
tools/d1_tower_809dcd66_tangent_audit.py
tools/d1_tower_809dcd66_blender_basis_gate.py
```

## Exact native-to-portable UV relation

The existing world GLB exporter applies the established D1 PNG/glTF V convention:

```text
portable_u = native_u
portable_v = 1 - native_v
```

The retail audit independently replayed both expressions and measured maximum
absolute error:

```text
base UV relation       2.9802322387695312e-08
parallax UV relation   1.1920928955078125e-07
```

Therefore if the native shader displacement is:

```text
du = -c4.x * dot(V,T) / dot(V,N)
dv = -c4.x * dot(V,B) / dot(V,N)
```

then the imported portable coordinate used by Blender must be displaced as:

```text
portable_uv2.x = portable_uv.x + du
portable_uv2.y = portable_uv.y - dv
```

or equivalently:

```text
portable_uv2.x = portable_uv.x - c4.x * Tx/Tz
portable_uv2.y = portable_uv.y + c4.x * Ty/Tz
```

The Y sign change is an adapter-space consequence of `portable_v=1-native_v`, not
a change to Bungie's shader.

## Loss-preserving GLB basis retrofit

Existing Tower GLBs already retain standard `NORMAL` plus custom `_D1_TANGENT`
VEC4. A direct GLB postprocessor exposes Blender-friendly split application
attributes without rebuilding world geometry:

```text
tools/d1_gltf_split_d1_basis_attributes.py
```

It adds:

```text
_D1_NORMAL       -> aliases existing exact NORMAL accessor
_D1_TANGENT_XYZ  -> copied from _D1_TANGENT.xyz
_D1_TANGENT_W    -> copied from _D1_TANGENT.w
```

The original BIN payload remains an exact output prefix, the original forensic
`_D1_TANGENT` remains present, and no standard `TANGENT` semantic is fabricated.

Implementation commit:

```text
624bb0295426fbe74bb004b39872ac3e2d8d7a52
```

## 24-material adapter manifest

The exact material/vector/TFX and texture evidence is flattened into a compact
Blender adapter manifest by:

```text
tools/d1_tower_809dcd66_adapter_manifest.py
```

For all 24 materials it preserves:

- exact c2/c3/c4/c5 vectors;
- serialized c6;
- static vs dynamic c6 mode;
- exact c6.x sample at abstract native `Frame[0]=0`;
- exact TFX bytecode, private constants and symbolic c6 expression;
- exact t0=`8093E9A3` / sampler `80AAE177`;
- exact t1=`8093E9A2` / sampler `80AAE176`;
- both unresolved `api13` scalars as separate explicit inputs;
- unresolved native render/blend state as unresolved;
- unresolved `Frame[0]` time unit/phase as unresolved.

`Frame[0]=0` is a valid exact initial expression sample without inventing a time
unit. It is not promoted to an animation-time mapping.

Green manifest canary:

```text
Actions run 34049203609
artifact    9994022880 d1-tower-809dcd66-adapter-manifest
artifact sha256 cca30835e32e972cabde1a2dfe982be4bf6d956ca22521bf232e234dc0f2fb49
```

## Blender 5.2.1 LTS execution closure

The actual Blender node builder is:

```text
tools/d1_blender_apply_809dcd66.py
```

All active Blender CI installs the project baseline through:

```text
tools/install_blender_lts.sh
```

The current canonical baseline is **Blender 5.2.1 LTS**.

The node builder imports a GLB carrying the explicit D1 basis attributes and
constructs the closed native semantic path:

```text
source N/T/W
 -> Object-to-World VECTOR transforms
 -> shared inv(length(Nraw))
 -> N / T / B
 -> view vector from Geometry.Incoming
 -> tangent-space view projection
 -> portable-space parallax correction
 -> t0.r palette selector
 -> t1.r displaced scalar
 -> c2/c3/c5/c6/api13 RGB chain
 -> Emission preview
```

Emission is intentionally only a Blender display/composition adapter. The native
D1 shader writes alpha zero, but the retail blend/composition state is still
unresolved, so no additive/emissive engine semantic is asserted from alpha alone.

Blender-visible Value nodes expose:

```text
D1_C6_X_AT_ABSTRACT_FRAME0_ZERO
D1_API13_DWORD6_UNRESOLVED_PREVIEW
D1_API13_DWORD7_UNRESOLVED_PREVIEW
```

The two `api13` nodes default to explicit preview fallback 1.0 unless the caller
provides overrides. The `.blend` material custom properties retain that these are
unresolved native globals.

The pinned **Blender 5.2.1 LTS** structural execution canary validates:

- glTF import of the underscore application attributes;
- shader Attribute node access;
- Object -> World VECTOR transforms;
- native-basis node construction;
- portable parallax node construction;
- texture-node plumbing;
- save/reopen persistence of nodes and proof-boundary custom properties.

Green current-baseline run:

```text
Actions run 34050905926
commit      3d214c6c0801befec2ec9873b6ce6b8fcd68e205
artifact    9994505098 d1-tower-809dcd66-blender-521-canary
artifact sha256 74aaf9224e597ecc06c722101e8bcdd2a3a4297d887f480368b3b45fcdb71f1a
```

The canary's texture pixels are synthetic structural fixtures. Exact retail t0/t1
image recovery remains independently source-closed and is exercised by the retail
scene build below.

### Historical 4.5.13 compatibility evidence

The first executable adapter closure used Blender 4.5.13 LTS. It remains useful
historical compatibility evidence but is no longer an active workflow/baseline:

```text
historical Actions run 34049476189
historical commit      3ab2f1c91331b13cf2ba4f504a0b345e86a7acec
historical artifact    9994103064 d1-tower-809dcd66-blender-4513-canary
historical artifact sha256 e0166aedf217462de59d053a3ee8a166633e26627325db1cf5291eacf8b79734
```

## Compact retail scene path

A sidecar-driven exporter avoids moving the full Tower checkpoint simply to test
this one shader family:

```text
tools/d1_tower_809dcd66_retail_scene_export.py
```

It rebuilds only the already proven target population from current retail source
buffers:

```text
12 geometry variants
64 placements
5 materials present in cell 80C98254
```

Source geometry/index identity and sidecar affine/UV selection remain canonical.
The compact GLB is then passed through the explicit-basis postprocessor and the
Blender adapter using the exact decoded retail t0/t1 PNGs.

The complete retail build is green on Blender **5.2.1 LTS**:

```text
Actions run 34050944445
commit      4401bd0c508fb93e79e38e7129869c4dd26c52e8
artifact    9994546945 d1-tower-809dcd66-retail-blender-preview
artifact sha256 440a774e6a211554c78931da4459cbe61bad1651ecb5eb5e38f2c3bc08d835db
```

The final packed Blender file is:

```text
D1_TOWER_809DCD66_RETAIL_64_NATIVE_EQUATION_PREVIEW.blend
bytes   316170
sha256  b6e4f2e6cfab90ede2f83e7113ae4cb1ab001b3ae9f55160ee2ae7c367fa2354
Blender version string: 5.2.1 LTS
```

Its source adapter GLBs are:

```text
D1_TOWER_809DCD66_RETAIL_64.glb
sha256 e2f7e76714a990048fffc8cbfaafe5441512be4b79158fd7a04550e1603cd590

D1_TOWER_809DCD66_RETAIL_64_D1_BASIS.glb
sha256 833a188f8d0687530dce0717b4964c1e0f2d2caf2b8a62c6e7f6c86f91a83dcb
```

## Remaining native proof boundary

The Blender adapter is now executable without hiding these unresolved native
items:

1. exact engine producers/names and live runtime values for `api13[6]` and
   `api13[7]`;
2. native render/blend/composition state for the alpha-zero RGB pass;
3. exact D1 producer/unit/phase for dynamic TFX `Frame[0]`;
4. bit-exact GCN reciprocal/rsqrt and raster/texture filtering behavior if a
   future renderer emulator requires hardware-level reproduction rather than the
   current semantic replay.
