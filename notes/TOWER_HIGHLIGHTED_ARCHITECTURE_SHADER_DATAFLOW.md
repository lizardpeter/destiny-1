# Tower highlighted architecture shader dataflow

Date: 2026-09-05

This note records instruction-level texture semantics for the two pixel shaders
used by the large Tower composite highlighted in Blender.  It is based on exact
current PS4 native GCN streams extracted in Actions run `33988324931`, artifact
`9975960756`, and CLRX GFX700 disassembly.  Sony user-data provenance maps every
`image_sample` back to the exact D1 `TextureIndex` (`t#`); there are 12 image
instructions total and zero unmatched instructions.

## Material / shader fixtures

- material `80C988A8` -> pixel shader `80C98908`
  - t0 `80C9855D` BC4 2048x2048
  - t1 `80C9855E` BC3 512x512
  - t2 `80C9855F` BC5 512x512
  - t3 `80C9855E` BC3 512x512
  - t4 `80C9855F` BC5 512x512
  - PS vec4 container `80C98909`
- material `80C988A9` -> pixel shader `80C9890A`
  - t0 `80C98562` BC4 2048x2048
  - t1 `80C98563` BC3 2048x2048
  - t2 `80C98564` BC1 256x256
  - t3 `80C98565` BC5 2048x2048
  - t4 `80C98563` BC3 2048x2048
  - t5 `80C98564` BC1 256x256
  - t6 `80C98565` BC5 2048x2048
  - PS vec4 container `80C9890B`

The duplicate TagHashes are real serialized bindings, not exporter duplication.
The duplicated resources use distinct D1 texture/sampler slots and in `80C9890A`
some are sampled after distinct material-authored UV transforms.

## Pixel shader `80C98908`

Exact native image usage:

- `0x0038`: t0, dmask X
- `0x0040`: t1, dmask XYZW
- `0x0048`: t3, dmask XYZW
- `0x00BC`: t2, dmask XY
- `0x00C4`: t4, dmask XY

### Proven color-layer blend

The t0 scalar is transformed with material constants and interpolant `attr3.w`
and clamped (`0x007C..0x0088`). Call the resulting scalar `b`.

At `0x008C..0x00D8`, each t3 RGBA component is multiplied by a material constant,
then the shader computes the difference from t1 and MACs the result by `b`.
Per channel the dataflow is exactly of the form:

```text
surface = scaled_t3 + b * (t1 - scaled_t3)
```

So t1 and t3 are the two RGBA surface endpoints and t0 is their blend scalar.
This is not a generic `t0 == albedo` material.

### Proven normal-layer blend

At `0x011C..0x0164`, t2.xy and t4.xy are separately scale/bias decoded using
material constants.  The shader subtracts the two decoded vectors and MACs the
difference by the same t0-derived blend scalar `b`, then reconstructs +Z from
`1 - x*x - y*y` and square root.  The resulting tangent-space vector is transformed
by the interpolated tangent basis and normalized before MRT1 packing.

Therefore t2 and t4 are the two RG normal endpoints controlled by the same blend
scalar t0.  In this exact material they happen to reference the same BC5 image,
but they remain distinct native bindings/samplers.

### Deferred outputs

- MRT0 receives the blended surface result (RGB) plus interpolated surface alpha.
- MRT1 receives the reconstructed/normalized deferred normal representation.

## Pixel shader `80C9890A`

Exact native image usage:

- `0x0044`: t0, dmask X
- `0x0050`: t3, dmask XY
- `0x0094`: t1, dmask XYZW
- `0x00A0`: t2, dmask XYZW, at a material-transformed UV
- `0x00C0`: t6, dmask XY
- `0x00F0`: t4, dmask XYZW
- `0x0104`: t5, dmask XYZW, at another material-transformed UV

### Proven surface composition

As in `80C98908`, t0 is transformed with material constants / `attr3.w` to a
clamped scalar `b` (`0x0068..0x006C`).

The first surface endpoint is the component-wise product of t1 and t2.  The second
endpoint is the component-wise product of t4 and t5 followed by component-wise
material-constant scaling.  At `0x0130..0x015C` the shader computes the endpoint
difference and MACs by `b`, i.e. per channel:

```text
endpoint_a = t1 * t2
endpoint_b = material_scale * t4 * t5
surface    = endpoint_b + b * (endpoint_a - endpoint_b)
```

Thus neither t0 nor the BC3 texture by itself is the exact native base color.
t0 is a blend scalar; the BC3 and BC1 resources jointly form each surface endpoint.

### Proven normal composition

The shader samples t3.xy and t6.xy as the two normal endpoints.  At
`0x018C..0x01DC` each is scale/bias decoded from material constants; the shader
blends the decoded XY vectors by the same scalar `b`, reconstructs +Z, transforms
through the interpolated tangent basis and normalizes for deferred MRT1 output.

### Deferred outputs

- MRT0 receives the composed/blended surface RGB plus interpolated surface alpha.
- MRT1 receives the blended tangent-space normal after basis transform and deferred
  normal packing.

## Canonical role boundary

These findings are instruction-proven native semantics.  A portable glTF preview
may choose one BC3 and one BC5 resource as a visual approximation, but that does
not make those images the complete native base/normal recipes.  The exact D1
recipe includes t0 blending, duplicated sampler slots, the BC1 modulation layer in
`80C9890A`, and material vec4 constants.

The next required step for a faithful portable bake is exact recovery of PS constant
containers `80C98909` and `80C9890B`, followed by a shader-family bake adapter that
reproduces these equations rather than assigning one image directly to baseColor.
