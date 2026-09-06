# D1 Spektar Pandion textured + rigged + animated Guardian — 2026-09-05

The masculine Titan Spektar Pandion pipeline now produces one GLB containing exact retail geometry, corrected UVs, exact retail skin weights, the exact Guardian armature/animation, and the exact model-parent texture plates.

## Final combined artifact

```text
SPEKTAR_PANDION_TITAN_MASCULINE_TEXTURED_RIGGED_ANIMATED.glb
bytes       18,684,824
SHA-256     0e946ef10215206469bdd00cb104c51638f78f367acd981db4b16dc31b3e1a75
```

GitHub Actions:

```text
workflow    D1 Spektar Pandion textured rigged animation
run         34001947931
job         101402263083
artifact    9979741760
name        D1-Spektar-Pandion-Titan-Masculine-TEXTURED-RIGGED-ANIMATED
ZIP SHA-256 9f9264387106f92136a779d5692b9b5efb3c5bf1ef107cea652c8110f081ce71
```

## Exact content validated

```text
models                  5
primitives              69
materials used          5
exact images embedded   15
skin joints             67
animation               STATE_13433E07_809D8572
clip frames             324
```

All 69 primitives retain `TEXCOORD_0`, `JOINTS_0`, and `WEIGHTS_0`.

Exact model -> model-parent texture plate:

```text
809FDB1E -> 80A85F6C   9 primitives   Spektar Pandion Mark
80A816E4 -> 80A8402F  10 primitives   Spektar Pandion Helmet
80A8274E -> 80A82BA3  16 primitives   Spektar Pandion Gauntlets
80A85682 -> 80A85683  16 primitives   Spektar Pandion Plate
80A862BA -> 80A7DC27  18 primitives   Spektar Pandion Greaves
```

For every model the exact `albedo`, `normal`, and `gstack` plate is embedded. Albedo and normal are bound to standard glTF slots for immediate viewing. GStack is embedded and provenance-linked but intentionally not mapped to standard PBR channels yet.

## Important fidelity boundary

This is now a source-authentic textured character asset, but not yet a proof of pixel-identical retail D1 shading.

The standard glTF preview uses neutral `metallic=0` / `roughness=1` compatibility factors. Those are explicitly **not** asserted to be Destiny 1 material values.

Remaining source-closure work:

1. resolve the exact D1 gear dye entries for the five selected inventory items;
2. resolve `DyeIndex -> ArtDyeReference -> DyeManifestHash -> SDye_D1` and the three armor dye channels;
3. reproduce the `SDye_D1` primary/secondary colors, decal/detail textures/transforms, specular properties, and subsurface strength;
4. source-close GStack channel meanings and native material/shader response;
5. validate rendered output against a retail reference.

No GStack or dye semantics should be guessed merely to make the preview look closer.
