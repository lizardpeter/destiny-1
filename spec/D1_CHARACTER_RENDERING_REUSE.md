# Destiny 1 character rendering reuse contract

Status: **living exact-reuse specification**  
Platform focus: final-era D1 / Rise of Iron PS4 retail

This document defines what a result learned from Xur, Tower NPCs, Crota, Guardians, or another fixture may be reused for without repeating the entire reversal, and what still requires per-asset validation.

The central rule is: **reuse the engine rule at the narrowest exact identity that proves it; never reuse a visual guess.**

## 1. Engine-wide reusable infrastructure

The following are intended as common D1 infrastructure once their source/retail validators pass on the target input:

- Tiger package/FileHash resolution and cross-package backing lookup;
- D1 `s_entity`, EntityResource, model-parent, entity-model and skeleton graph traversal;
- PS4 texture header/payload recovery and format-aware decode;
- native sampler descriptor recovery;
- material VS/PS resource-table enumeration;
- native Orbis shader -> bounded GCN extraction and disassembly;
- GCN image instruction -> exact material texture-index/resource mapping;
- D1 TFX opcode framing where the opcode width is source-/retail-closed;
- native-used versus serialized texture-slot gap census;
- D1 coordinate-basis conversion and glTF preservation checks;
- loss-preserving raw provenance in exported material/mesh/animation metadata.

These systems are not Xur-specific. A new character should run through the same code and fail closed only when it introduces a genuinely new resource class/layout.

## 2. Native shader semantics: reuse by exact bounded GCN SHA-256

Instruction-level shader equations are reusable across assets when all of the following are true:

1. shader stage agrees (`vs` or `ps`);
2. the bounded native GCN SHA-256 is byte-for-byte identical;
3. the future asset resolves its own exact local textures/constants/TFX/samplers/runtime inputs;
4. any still-open global/render/fetch/permutation boundary in the registered proof remains open for the future asset too unless independently closed.

The current machine-readable registry is:

`evidence/d1_native_shader_semantic_registry_v1.json`

Lookup is fail-closed through:

`tools/d1_shader_semantic_registry_lookup.py`

The first registry checkpoint contains **9 exact GCN programs: 6 PS + 3 VS** from the current Xur proof waves.

A concrete proof that serialized shader identity is too narrow is the shared Xur VS GCN family: serialized VS headers `8087695C`, `809DF743`, and `80A08C19` all resolve to the same exact 700-byte native GCN program. Its post-fetch equations therefore belong to the native program identity, not to one TagHash or one NPC.

## 3. Dual-quaternion character skinning

The current Xur corpus has exact post-fetch native equations for:

- one transform-palette entry / rigid DQ path;
- two-influence DQ blending;
- four-influence DQ blending with quaternion hemisphere correction.

These equations are reusable anywhere the exact registered VS GCN appears.

They are **not** permission to assume every D1 character has the same source weight encoding. Fetch-shader source layout, packed influence representation, palette index mapping and rig/control remapping remain independently validated inputs. A new character that uses a different VS GCN or different fetch shader must prove those parts before being promoted.

## 4. Skeletons, rigs and animations

The general graph/parser/export machinery is reusable, but animation correctness is validated per rig/clip family:

- skeleton topology and bind/inverse-bind decoding are common D1 mechanisms;
- packed skin influences are decoded by source storage format, not by character name;
- runtime-rig/control maps are preserved and applied rather than assuming skeleton index == control index;
- exact clip decode modes and retarget mappings are reusable only after that compression/control family is proven;
- coordinate-basis adaptation applies to the actor as a whole and must preserve mesh, bind matrices and animation channels together.

Thus solving one 70-joint Tower human dramatically reduces work for another asset using the same rig/clip architecture, but it does not justify forcing a Fallen, Vex, Hive or weapon rig through that human mapping.

## 5. Textures and materials

Texture **recovery and native binding** are generic. Texture **meaning** is shader-dataflow-specific.

For a new character:

- recover the exact texture resource in each material texture index;
- identify which indices the exact native GCN actually samples;
- reuse a registered shader equation only on an exact GCN match;
- substitute that character's literal texture resources and material constants into the equation;
- do not map a source texture to glTF base color/normal merely from adjacency, format, filename resemblance or appearance.

The generic `tools/d1_material_runtime_texture_gap_census.py` additionally detects a native-used texture index that is not serialized by the material. Such a gap is a runtime/default descriptor frontier, not permission to invent a white/black/flat-normal resource.

## 6. External material permutations

The D1 model-parent/external-material architecture is reusable, but the **live selection state remains a separate gate**.

Once the exact D1 live switch-key/value evaluator is closed, it should be implemented once as model-parent infrastructure and reused across every entity using that architecture. Until then, no NPC is visually exact merely because all candidate materials and textures were recovered.

## 7. What must never be generalized automatically

Do not propagate any of the following from one character to another without exact evidence:

- literal texture TagHashes;
- literal material CBuffer/TFX values;
- a material's selected external permutation member;
- fetch-shader byte offsets/formats;
- skeleton/control index equivalence;
- animation compression mode or retarget map;
- runtime/default texture descriptors;
- engine names/values for unresolved global buffers;
- blend/depth/raster/composition state;
- a portable Blender/PBR approximation.

## 8. Practical whole-game workflow

For each newly encountered character or enemy:

1. resolve its source-owned entity/model/skeleton/rig/material graph;
2. recover exact native textures, samplers, shader binaries and local state;
3. hash every bounded VS/PS GCN program;
4. query the exact semantic registry;
5. immediately reuse exact matches with the new asset's own parameters;
6. reverse only genuinely new GCN/fetch/rig/material-selection families;
7. add newly closed engine/family rules back to the common registry/specification;
8. export only after selection + geometry/skin + animation + native material behavior gates agree.

This is the intended scaling strategy for the whole game: each difficult asset expands shared coverage, so subsequent assets increasingly become data-resolution and validation jobs rather than fresh reversals.
