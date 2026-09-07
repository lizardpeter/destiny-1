# D1 Tower Xur texture, shader, and material-permutation proof boundary

Date: 2026-09-07
Target identity: Xur (`StringHash 46C55854`)
Tower serialized entities: `80C7ACC8`, `80C885AA`
Entity model: `80C88CEF`

This note is the authoritative boundary between what is already source-/binary-proven and what is still only a portable preview or an open reverse-engineering target.

## Exact texture closure: solved at the native resource-binding level

The pinned Xur textured checkpoint accepted by `.github/workflows/d1-tower-xur-exact-textured-all-actions.yml` proves:

- 54 exact D1 materials in the Xur model export.
- 104 exact source texture resources embedded.
- 232 exact pixel-shader texture binding edges.
- 0 vertex-shader texture binding edges for this Xur material set.
- 52/54 materials receive an evidence-scoped portable glTF base-color preview binding.
- 45/54 materials receive an evidence-scoped portable glTF normal preview binding.

The authoritative texture representation is **not** the glTF PBR slot assignment. The authoritative representation is the exact native material -> shader stage -> `t#` -> Texture TagHash graph preserved by `material_texture_manifest.json` and copied into glTF material/image extras by `tools/d1_gltf_bind_exact_shader_textures_v3.py`.

Therefore:

- source texture discovery/recovery is closed for the current Xur checkpoint;
- native texture TagHashes and shader-register indices are preserved exactly;
- portable `baseColorTexture` / `normalTexture` bindings remain preview adapters only.

## Shader closure: binaries/resources are recoverable, Xur shader semantics are not yet fully recreated

The repository already has a validated PS4 shader path:

1. material -> D1 VS/PS shader header TagHash;
2. shader header -> native Orbis shader payload FileHash;
3. exact `OrbShdr` footer and bounded machine-code length;
4. exact native GCN bytes;
5. CLRX GFX700 disassembly to `s_endpgm`;
6. instruction/resource census and image-resource usage analysis.

`notes/PS4_09A_SHADER_DATAFLOW.md` proves that this path can reach instruction-level equations for individual retail D1 materials, including exact UV transforms, normal reconstruction, cubemap sampling, palette math, output MRT behavior, and local constant usage.

That does **not** mean all 54 Xur materials have already had their native shader arithmetic lifted/recreated. The current Xur GLB explicitly preserves the policy:

> All exact native D1 texture bindings are retained. Portable base/normal preview bindings remain an approximation where native shader semantics are not yet recreated.

Open Xur shader work therefore consists of:

- census every unique Xur VS and PS;
- recover every native payload with zero missing shader/package dependencies;
- bounded-disassemble every unique native shader;
- map every native image instruction back to exact `t#` resources;
- recover material-local constant blocks/samplers/TFX streams for all 54 materials;
- lift per-shader arithmetic and output/MRT behavior;
- recover required higher-level/global constant producers;
- recover exact render/blend/depth/raster state where it changes the visible result;
- only then reproduce the retail shader in a portable renderer rather than approximating it with glTF PBR.

## Material permutation selection: current `main` is still permutation-index 0

The repository was rechecked before this note was written. `tools/d1_render_owner_probe.py` currently parses:

- `TexturePlatesROI`;
- `ExternalMaterialsMap`;
- the full `ExternalMaterials` bank;
- and records the first material for each range as the current Charm-style convenience selection.

It does **not** yet contain an authoritative D1 live switch-key/value evaluator. The actual current export path still behaves as permutation index 0 for an external-material range unless another source-specific resolver overrides it.

This matters because a visually exact Xur export requires two different kinds of closure:

1. **selection closure** — prove which external-material member retail Xur selects for every `VariantShaderIndex`;
2. **shading closure** — reproduce the selected materials' native shader behavior.

Do not mark Xur visually exact until both are closed.

## Comparative implementation evidence

The current MIDA/Charm-family implementation contains a later-strategy `ModelPermutation` mechanism that builds switch-key/value sets and maps exact sorted key/value combinations to permutation indices. Its model-parent schema uses descriptor/index arrays plus switch records. This is useful structural evidence, but its Marathon class hashes/offsets are **not** D1 authority. Any D1 implementation must first be calibrated against exact D1 `0x80801A9C` parent bytes and must fail closed when a pointer/count/range does not validate.

## Immediate continuation

The next durable checkpoint is an Xur-specific all-shader census/disassembly workflow that reuses the pinned exact textured artifact, subsets the exact 54-material manifest, recovers every VS/PS header and native dependency package, disassembles all unique shader binaries, validates PS image-resource usage against exact `t#` texture bindings, and emits a small proof artifact. After that, shader families can be grouped by identical native code/usage so semantic lifting work is done once per unique program rather than once per material.
