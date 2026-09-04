# PS4 011C small-component shader proof

Date: 2026-09-04

This checkpoint closes the native shader role of the final small-component
material on weapon model `80A39E12`.

## Resource chain

Final small-component model binding:

- material: `80A3D294`
- vertex shader: `80AAE149`
- pixel shader: `80AA9D63`
- pixel Vector4 container: `80AAE1E1`
- native sampler: `80AAE1D5`
- TextureIndex 0: `80AA9D4D`

`80AA9D4D` is the already-recovered 1024x1024 BC3 atlas from the final
`ps4_globals_0154_5.pkg` logical snapshot.

## Exact retail GCN proof

GitHub Actions run `33901458176` completed successfully from commit
`b2d6d69873248cddfb349482b8b7de18aa379187` and produced artifact
`80AA9D63-clrx-disassembly` (artifact id `9947860850`).

The bounded native GCN code has SHA-256:

`c846c4182497fb5f7e98226964f91045e2c8fab244141c380845800968fdbf51`

The CLRX GCN1.1 disassembly proves the following relevant dataflow:

```text
v_interp ... attr0.x -> v2
v_interp ... attr0.y -> v3
image_sample v[0:3], v[2:5], s[4:11], s[12:15] dmask:15
...
s_buffer_load_dword s0, s[0:3], 0x5
v_max_f32 v4, s0, s0 clamp
v_madak_f32 v0, v4, v5, -0.5
v_cmp_gt_f32 vcc, 0, v0
...
exp mrt0 ...
```

Thus the texture is sampled from interpolated `attr0.xy`, i.e. the exported
mesh `TEXCOORD_0` path.

The shader's sampled RGB values flow to MRT0 RGB. Sampled alpha is used by the
coverage/discard test; native MRT0 alpha is not established as the texture's
alpha value and must not be invented as such.

## Constant-buffer closure and exact alpha threshold

PS Vector4 container `80AAE1E1` is a validated PS4 subtype-7 Vector4 resource:

```text
vec0 = [ 0.0, 0.0, 0.0, 0.0 ]
vec1 = [-4.0, 1.0, 1.0, 1.0 ]
```

The shader performs `s_buffer_load_dword ... 0x5`, so it reads dword 5, which
is `vec1.y = 1.0f`.

The clamp therefore remains exactly `1.0`, and the shader kill expression is:

```text
coverage = 1.0 * sampled_alpha - 0.5
discard when coverage < 0
```

which reduces exactly to:

```text
discard when sampled_alpha < 0.5
```

This is byte/instruction proven, not a visual interpretation of the atlas.

## Native sampler `80AAE1D5`

The validated sampler descriptor decodes as:

- wrap X: `Wrap`
- wrap Y: `Wrap`
- wrap Z: `Wrap`
- mag filter: `AnisoBilinear`
- min filter: `AnisoBilinear`
- mip filter: `Linear`
- border color: `TransBlack`

Core glTF cannot encode the exact native anisotropic sampler descriptor.
Portable export therefore uses repeat wrapping plus linear mipmapped filtering,
while preserving the exact native sampler hash and decoded fields in extras.

## Authorized glTF mapping

The following portable mapping is now evidence-backed and no longer speculative:

- image: exact decoded `80AA9D4D` BC3 atlas
- coordinates: `TEXCOORD_0`
- RGB: `pbrMetallicRoughness.baseColorTexture`
- coverage: `alphaMode = MASK`
- threshold: `alphaCutoff = 0.5`
- wrap S/T: `REPEAT`

Metallic/roughness values remain explicitly portable approximations because
this shader proof does not assign native PBR metal/roughness semantics.

Implementation commit:

- `0280f47aedbf3ce68d5f2bc88709be52a1c5a327` — `Map proven 011c small atlas alpha-test material`

The production 011C workflow also pins the shader-code SHA, Vector4 constant,
and sampler descriptor before building the final 12-animation GLB.
