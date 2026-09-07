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

## Native shader binary/resource closure: solved for the current 54-material Xur checkpoint

Workflow `.github/workflows/d1-tower-xur-all-native-shader-census.yml` completed successfully in GitHub Actions run `34145462195`.

Durable workflow commit: `7e2353c9044e92a2191b96d5843b2e56a2f2f125`.

Proof artifact:

- name: `D1-TOWER-XUR-ALL-NATIVE-SHADER-CENSUS`
- artifact ID: `10027557806`
- artifact ZIP SHA-256: `e26febd88c0fcc05d998ec7dab04efcf1582095ee594a459ec472c530c7a5086`
- artifact size: 323,302 bytes
- 156 files

The completed census proves:

- 54 exact Xur materials;
- 25 unique pixel-shader header TagHashes;
- 11 unique vertex-shader header TagHashes;
- 36 total unique shader headers;
- 36/36 shader headers resolved to native Orbis shader payloads;
- 36/36 bounded native GCN payloads extracted with zero errors;
- total bounded GCN size = 30,428 bytes;
- all 36 bounded programs CLRX-disassemble in pinned raw `GFX700` mode through `s_endpgm` with no decoder stderr;
- 31 unique bounded GCN programs after grouping exact code by SHA-256;
- no additional native-program package family was required after resolving the exact headers;
- all 25 Xur pixel shaders were analyzed for native image-resource usage;
- 116 native GCN image instructions were found;
- all 116/116 image instructions were resolved back to exact D1 texture-resource indices;
- 0 unmatched image instructions;
- 0 missing pixel-shader disassemblies;
- the existing proven shader-role table remains valid against this Xur-native census with zero validation errors.

The fail-closed final status is:

`D1_XUR_SHADER_BINARY_AND_IMAGE_RESOURCE_CLOSURE_EXACT`

This is stronger than merely retaining shader TagHashes in a GLB: the exact retail PS4 machine code itself is now recovered and bounded for every VS and PS used by the current 54-material Xur checkpoint, and every native pixel-shader image instruction is connected back to the exact serialized D1 `t#` resource namespace.

## Exact material-local shader state: solved for all 54 current Xur materials

Workflow `.github/workflows/d1-tower-xur-material-local-state.yml` reran green after the D1-specific TFX framing correction in commit `b82e6bd8be60287f821a634aec23389e14fd1a9f`.

Successful GitHub Actions run: `34147104709`.

Proof artifact:

- name: `D1-TOWER-XUR-EXACT-MATERIAL-LOCAL-STATE`
- artifact ID: `10028092407`
- artifact ZIP SHA-256: `83c5b4af4590d986fb917ddc9da4098e2d1272ad30025db8395f53cac61e4407`
- artifact size: 116,059 bytes

The exact checkpoint status is:

`D1_XUR_MATERIAL_LOCAL_STATE_EXACT`

It proves:

- 54/54 materials resolved with zero violations;
- 11 exact VS identities and 25 exact PS identities, exactly matching the native shader census;
- 19 unique material TFX programs after grouping by stage + exact bytecode SHA-256;
- 19 exact external Vector4 constant containers and 19 exact referenced payloads;
- no extra package families were required to recover those payloads;
- 2 unique native PS4 sampler resources;
- all 108 material stage streams (54 VS + 54 PS) are now completely TFX-framed;
- all 54 VS stages use inline CBuffer storage;
- 15 PS stages use inline CBuffer storage only;
- 39 PS stages contain an external Vector4 container whose data is byte/word-identical to the inline PS CBuffer values;
- material state lane `+0x20` currently separates as 43 x `00000000` and 11 x `00008100` without assigning an unsupported semantic meaning;
- the only TFX extern class present in this exact Xur local-state corpus is `Frame`, with 52 occurrences after complete framing.

### D1 TFX opcode `0x42` framing closure

The earlier local-state run failed closed on six VS streams because the pinned Charm table labels opcode `0x42` as `Unk42` but does not consume the following byte. Exact D1 Rise-of-Iron PS4 retail material streams independently prove that D1 `0x42` consumes **one following `u8` operand**:

- applying that one-byte width closes every one of the 108 Xur VS/PS streams;
- the Xur corpus contains exactly 54 `0x42` occurrences;
- each consumed operand is a valid index into that stage's serialized CBuffer Vec4 array;
- no unknown or truncated TFX opcode remains in the 54-material checkpoint.

`tools/d1_tfx_program_inventory.py` now records this as a **framing promotion only**. The operation remains named `Unk42`; its semantic meaning is intentionally withheld.

The fully framed Xur TFX corpus contains, among other operations, 201 `PushConstantVec4`, 72 `Multiply`, 61 `Saturate`, 54 `Unk42`, 52 `PushExternInputFloat`, 49 `MultiplyAdd`, 44 `Permute`, 21 `Lerp`, 15 `Jitter`, 15 `Add`, and 13 `LerpConstant` operations. These are inventory counts, not semantic labels for material roles.

## Exact shader semantic-lifting frontier: now reduced and reproducible

The exact GCN census and exact material-local state are now joined by `tools/d1_xur_shader_semantic_frontier.py` and `.github/workflows/d1-tower-xur-shader-semantic-frontier.yml`.

Stable workflow run: `34147886184` at commit `e07508845d797af0596d3aab4717a076033e3783`.

Proof artifact:

- name: `D1-TOWER-XUR-EXACT-SHADER-SEMANTIC-FRONTIER`
- artifact ID: `10028306273`
- artifact ZIP SHA-256: `ba6c6872c7d100f3da381e95b9dcfa33bf19227575f0380207334d9727ad9bee`
- retention: 90 days

The fail-closed status is:

`D1_XUR_SHADER_SEMANTIC_LIFTING_FRONTIER_EXACT`

The reducer validates the two upstream exact checkpoints and converts the 54 materials into a deterministic semantic-lifting queue:

- 31 exact native GCN program families;
- 38 exact **stage structural lifting units** = 12 VS units + 26 PS units;
- 33 exact **combined material structural families** across the 54 materials;
- all 116 exact PS image instructions remain accounted for.

A structural lifting unit means the same native GCN SHA-256, TFX SHA-256, local state/layout counts, ordered native sampler-descriptor payloads, vector-storage relation, and preserved material state fields. Literal texture TagHashes and literal constant values are deliberately treated as parameters rather than grouping keys. Therefore this reduction is a source-owned work-reduction result, **not** a claim that materials in one family produce identical pixels.

The largest combined material family contains six materials (`8087652C`, `8087652D`, `8087652E`, `8087652F`, `80876530`, `80876533`) and uses PS `80876EDF` / native GCN SHA beginning `966131017fed...`. That family is the first high-coverage semantic-lifting target.

## Shader semantic recreation: still open, but the local-state frontier is no longer open-ended

Binary/resource closure and material-local-state closure are not the same thing as retail-equivalent portable shading.

`notes/PS4_09A_SHADER_DATAFLOW.md` proves that the pipeline can lift individual D1 native programs to instruction-level equations, including UV transforms, normal reconstruction, cubemap sampling, palette math, output MRT behavior, and local constant usage. Xur no longer needs to be treated as 54 unrelated materials. The remaining semantic work is bounded by the exact queues above.

Remaining shader work is now:

- lift the arithmetic/dataflow for the 31 exact native GCN binaries, starting with the highest-coverage PS/VS families;
- attach the already exact TFX/CBuffer/sampler inputs to those lifted equations;
- recover the required higher-level/global constant producers where a program depends on them;
- recover exact render/blend/depth/raster state where it changes visible output;
- distinguish instruction-proven texture semantics from preview-only role guesses;
- implement a retail-equivalent portable renderer/material adapter from the recovered equations and states;
- validate output against retail reference behavior before promoting visual equivalence.

Until that is done, the current glTF `baseColorTexture` / `normalTexture` assignments remain a preview adapter and must not be described as the retail shader.

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

Two proof tracks can now proceed without guessing:

1. **Xur shader semantic lifting** — start with the six-material `80876EDF` PS family, promote only equations and texture meanings directly proven by its exact GCN dataflow, then continue down the 38 exact stage-structural units.
2. **D1 live external-material permutation selection** — calibrate the exact D1 `0x80801A9C` model-parent layout from retail bytes, identify its descriptor/index/switch structures without importing later-strategy offsets, locate the instantiated Xur switch-key/value state, and make external-material selection fail-closed and source-owned.

The final Xur visual checkpoint should only be promoted once these two tracks meet: exact selected material member + exact native-equivalent shading for that member.
