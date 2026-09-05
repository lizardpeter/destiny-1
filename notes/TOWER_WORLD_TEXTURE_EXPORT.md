# Tower world texture export checkpoint

Date: 2026-09-05

## Scope

This checkpoint covers the nine-cell retail-visible Tower baked-static material set and the first three-cell Blender/glTF texture adapter. It is deliberately built as a regression fixture for the generic D1 world exporter, not as Tower-only asset logic.

## Exact dependency closure

The retail visibility pass selects **472 unique D1 ROI materials** across the nine Tower cells.

Those materials reference:

- **191 unique pixel-shader families**
- **657 unique Texture TagHashes** through exact material `TextureIndex` (`t#`) bindings

The first corpus resolved 635/657. The remaining 22 were traced to physical logical package families `0154`, `0155`, `0156`, `0157/0158`, and `01DB`. Exact physical TAR member locations are recorded in:

- `evidence/d1_tower_texture_dependency_member_catalog.json`

The incremental closure run `33982669592` then re-resolved only the 22 failed texture rows and reached:

```text
visible materials       472
unique texture tags     657
decoded texture tags    657
texture errors            0
PNG outputs             707
missing package IDs       0
```

The 707 PNG count exceeds the TagHash count because six-face cubemaps export one PNG per face.

No texture substitution, same-name fallback, or guessed package ownership is used. The canonical manifest preserves:

```text
material hash
  -> vertex/pixel shader hash
  -> exact stage + TextureIndex/t#
  -> exact Texture TagHash
  -> Texture2D header/backing chain
  -> decoded DDS/PNG
```

## First portable textured world adapter

The corrected three-cell world fixture contains:

```text
4702 retail-visible placement nodes
773 geometry variants
773 geometry variants with UV0
756 geometry variants with decoded normals
0 non-affine placement matrices
```

Two preview GLBs were generated without modifying the canonical D1 material records:

### Strong base preview

```text
file: D1_TOWER_THREE_CELL_TEXTURED_STRONG_BASE.glb
bytes: 214487504
sha256: 1e7a0d60c21c654f394dc162f9b5d233a1bcb6860a1872fa727f4d76eb6c596d
textured geometry variants: 476 / 773
textured material hashes: 119
placement nodes after reload: 4702 / 4702
```

This binds only color-capable `t0` textures that are paired with a same-resolution BC5 vector resource. That pairing is a strong format/topology hint, **not** a canonical shader-semantic proof.

### Broad base preview

```text
file: D1_TOWER_THREE_CELL_TEXTURED_BROAD_BASE.glb
bytes: 253113372
sha256: f63615eadffaa8f0d7a2aff1133363d73aa895efd3c856fd8b6385ab8cbcac40
textured geometry variants: 615 / 773
textured material hashes: 170
placement nodes after reload: 4702 / 4702
```

This additionally permits materials whose sole color-capable PS resource is `t0`. It is intentionally labelled preview-only.

The adapter never promotes these inferences into `KNOWN_PIXEL_SHADER_ROLES`, keeps alpha opaque until blend/alpha semantics are proven, and can optionally reconstruct portable RGB normals from BC5 XY only when explicitly requested.

## Preview semantic inventory

Across the 472 visible materials:

```text
base-color preview candidate:
  STRONG_FORMAT_CANDIDATE   173
  MEDIUM_PREVIEW_CANDIDATE  118
  NONE                      181

BC5 normal-vector preview candidate:
  STRONG_FORMAT_CANDIDATE   173
  NONE                      299
```

The largest unresolved semantic families are currently:

```text
8093EB1E  43 materials  t0/t1 both color-capable 2D
80AAE1C6  26 materials  t0/t1 both color-capable 2D
809DCD66  24 materials  t0/t1 both color-capable 2D
80CA0DD5  12 materials  color + cubemap + color
80AAE2AD  11 materials  color + cubemap + color + color
```

These are not assigned arbitrary PBR roles. Their native shader machine code is the next authority.

## Native color-space storage hints

The generic texture exporter records a separate native storage interpretation based on the source-correlated ROI GCN-surface-to-DXGI mapping:

```text
BC1 / BC2 / BC3 / BC7 -> sRGB storage hint
BC4 / BC5             -> linear storage hint
RGBA8                  -> linear storage hint
```

This is **not** a semantic-role statement. For example, a BC3 resource may still be a packed control texture despite the native surface format's sRGB interpretation.

## Highlighted suspicious Tower object

The previously highlighted geometry uses material `80C98898`, pixel shader `80AADC40`, and exact `t0` texture `80BB612C`.

`80BB612C` is now recovered from logical package namespace `01DB` and decodes as a 4x4 RGBA8 resource whose pixels are uniformly `(64,64,64,255)`. It is therefore real shared-environment material data, not fabricated geometry or a missing-texture placeholder introduced by the exporter.

The object remains in the scene. The project policy is to fix transform/material interpretation rather than delete legitimate serialized placements.

## Shader-semantic frontier

A reusable world shader extractor now follows:

```text
visible material -> pixel shader header -> native PS4 payload -> OrbShdr metadata -> bounded GCN code
```

The first top-40 pass extracted exact code for 28/40 families (16,936 bytes total). The 12 gaps were traced specifically to package namespaces `0156`, `00EC`, and `00EE`, not parser ambiguity.

Exact `00EC` and `00EE` physical members are now byte-located and recorded in:

- `evidence/d1_tower_shader_dependency_member_catalog.json`

The current workflow recovers `0156 + 00EC + 00EE` before extracting/disassembling the top 40 families with pinned CLRX GFX700 support. Exact instruction dataflow will be used to promote `t#` roles; visual/format heuristics will remain preview-only.

## Scaling to all D1 worlds

The intended reusable layering is now:

```text
split-TAR physical member index
  -> Tiger package / FileHash resolution
  -> map ownership + static-map schema
  -> retail visibility
  -> geometry + UV + normals
  -> exact material/shader/t# dependency graph
  -> texture header/backing decode
  -> shader-semantic proof
  -> portable glTF/Blender material adapter
```

A complete remote split-TAR member indexer (`tools/d1_split_tar_index.py`) is also being validated so future TagHash package namespaces can be recovered without one-off bounded archive scans.
