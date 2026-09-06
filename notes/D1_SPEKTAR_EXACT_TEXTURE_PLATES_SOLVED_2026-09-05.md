# D1 Spektar Pandion exact texture plates solved — 2026-09-05

This note records closure of the exact retail texture-source and texture-plate reconstruction stage for the masculine Titan Spektar Pandion five-piece set.

## Source-complete result

The exact visual-context chain identifies five model-parent texture-plate headers:

```text
80A82BA3
80A85683
80A85F6C
80A8402F
80A7DC27
```

The plate census resolves 159 unique retail source texture FileHashes across those five headers. After fixing D1 Tiger variable Oodle block sizing, the generation-safe exporter resolves:

```text
requested source textures   159
resolved source textures    159
failed                        0
missing                       0
```

The four formerly blocked `013F` headers now resolve normally and with zero fallback attempts:

```text
80A7FB3B
80A7FB3E
80A7FE41
80A7FE47
```

## Exact composed plate set

No source image is resized during composition.

```text
80A82BA3
  albedo  80A82BA4  2048x2048  11 transforms
  normal  80A82BA5  2048x2048  11 transforms
  gstack  80A82BA6  2048x2048  11 transforms

80A85683
  albedo  80A8568F  2048x2048  15 transforms
  normal  80A85690  2048x2048  15 transforms
  gstack  80A85691  2048x2048  15 transforms

80A85F6C
  albedo  80A85F6D  2048x2048   8 transforms
  normal  80A85F6F  2048x2048   8 transforms
  gstack  80A85F6E  2048x2048   8 transforms

80A8402F
  albedo  80A84031  1024x1024  11 transforms
  normal  80A85CB4  1024x1024  11 transforms
  gstack  80A84032  1024x1024  11 transforms

80A7DC27
  albedo  80A7DC28  2048x2048  13 transforms
  normal  80A7DC29  2048x2048  13 transforms
  gstack  80A7DC2A  2048x2048  13 transforms
```

Validation result:

```text
SUCCESS 159 source textures -> 15 exact plate images
```

All five headers contain exactly the roles `albedo`, `normal`, and `gstack` in this census.

## CI provenance

Workflow:

```text
.github/workflows/d1-spektr-pandion-texture-plate-build.yml
```

Green run:

```text
run       34001528788
job       101401141549
artifact  9979644529
name      d1-spektr-pandion-exact-texture-plates
ZIP SHA-256
b7e2d1f61445b2d89dd5385e615fbe4bc4ce6ff5e9c6c0bd50b22af9561e37a5
```

The artifact contains 335 files and includes the 159 decoded texture sources, all 15 composed plate PNGs, and exact manifests/reports.

## Remaining fidelity work

This closes extraction and reconstruction of the model texture plates. It does **not** by itself prove final retail shader appearance.

Remaining visual stages are:

1. bind each exact model-parent plate set to the corresponding model primitives in the corrected-UV rigged GLB;
2. decode/replicate D1 GStack channel/material semantics rather than guessing PBR mappings;
3. resolve D1 gear dye channel/index selection and exact `SDye_D1` parameters/textures;
4. validate a lit render against retail visual references.

Until stages 2–3 are source-closed, GStack channels and dye coloration must not be assigned guessed metallic/roughness/color semantics.
