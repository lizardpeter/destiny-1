# Destiny 1 Everything Index and Tower Reconstruction

Status: active, 2026-09-05.

## Scope

The project target is **literally every recoverable Destiny 1 asset/resource**, not only inventory items or weapons.

The browser and reverse-engineering corpus must retain and progressively classify:

- entities and EntityResource graphs;
- characters/enemies;
- weapons, armor, ships, vehicles and Ghosts;
- static and dynamic props;
- animated world objects;
- architecture, terrain, world chunks/bubbles and placements;
- collision/gameplay geometry when decoded;
- materials, shaders, samplers, textures and texture plates;
- skeletons, runtime rigs, control graphs and animation clips;
- effects, particles and decals;
- UI and Director/orbit resources;
- cinematics;
- audio resources/events;
- activity/world scripting resources;
- every still-unknown Tiger class/entry, retained by exact TagHash/type/reference until classified.

Unknown resources are not discarded merely because an exporter does not yet understand them.

## Provenance policy for the HTML/browser

Every image/preview is explicitly categorized:

1. **PKG EXTRACTED** — decoded from shipped PS4 Tiger package bytes. Package generation, TagHash, stream/backing hashes and dimensions are retained where applicable.
2. **Official Bungie manifest/web asset** — real Bungie-authored Destiny 1 presentation metadata or Bungie-hosted image (icons, PGCR art, etc.), but not extracted from the package corpus.
3. **Generated Preview** — rendered from package-recovered geometry/materials for browsing.
4. **Unknown / no preview** — retained until a proven visual can be associated.

Official Bungie manifest/web presentation data may supply names and useful corroboration, but it never establishes a Tiger ownership edge.

## Raw UI / Director package census

The tolerant direct-offset UI census completed successfully in Actions run `33942166285`, artifact `9962232859` (`d1-ui-art-census-v2`).

Recovered directly from the PS4 package archive:

| package family | texture headers | resolved PNGs | failed generations/resources |
|---|---:|---:|---:|
| `ps4_ui_core_000a` | 31 | 29 | 2 |
| `ps4_ui_menus_0018` | 39 | 35 | 4 |
| `ps4_ui_orbit_0026` | 450 | 444 | 6 |
| `ps4_ui_pve_002d` | 0 | 0 | 0 |
| `ps4_ui_pvp_0034` | 0 | 0 | 0 |
| **total** | **520** | **508** | **12** |

`ui_orbit` visibly contains Director/orbit presentation resources such as planets, activity/emblem/faction/playlist glyphs, selection graphics and background/panel art. Those visual observations are useful for triage only. Each recovered image remains indexed by its exact TagHash and package-generation provenance; it is not assigned to a named activity/map merely because it looks similar.

## Vex animated-object fixture belongs in the everything index

The previously validated animated Vex object is not to be lost merely because it is not an inventory item.

Current proven proxy/bundle fixture:

- `s_entity_model` proxy: `816CE09A`
- skeleton EntityResource: `816CE092`
- 12 skeleton nodes
- runtime rig EntityResource: `816CE095`
- secondary runtime-rig class: `0x808008B2`
- validated runtime component fingerprint: `76F7A98E`
- 12 controls
- validated identity bone/control mapping `0..11`
- clip `816CE09D`, animation hash `6FB760FF`
- clip `816CE09E`, animation hash `D3FD602F`

The rigged/animated GLB validates mesh + skeleton + skinning + animation. It is intentionally classified as an **animation-bundle/proxy model**, not the final ordinary visible Vex body.

The strongest currently proven ordinary visible Vex material-control fixture remains:

`809C44A5 -> 809C47F4 -> materials 809C475F / 809C4760`

Its material/render relationship is proven; compatibility with the 12-control proxy rig is not yet proven.

## Archive-wide family census tool

`tools/d1_everything_family_census.py` was added to make an exact, loss-preserving resource census reusable for maps and arbitrary asset families.

It:

- preserves every physical snapshot occurrence rather than silently selecting a patch winner;
- records every entry's TagHash, type/subtype, reference/class hash, size, block location and availability;
- names only previously byte-validated reference classes;
- hashes/decodes resident payloads within conservative size bounds;
- records all unknown classes unchanged;
- scans resident type-16 structured payloads for **aligned literal TagHash** matches to resources in the supplied corpus;
- labels those literal matches as co-reference evidence only, never automatic ownership/placement semantics;
- produces JSON plus union-entry and literal-edge CSVs.

## Tower: first complete map reconstruction target

Exact archive root: `ps4_city_tower`.

The goal is not to dump all meshes into one scene. A correct Tower export must recover the world assembly/placement semantics sufficiently to preserve the shipped transforms and relationships among static world geometry, props, animated entities, materials/textures, collision/environment resources and other required content.

Workflow `.github/workflows/d1-tower-map-census.yml` (initial commit `969d0d8fe9b8df5f6ae96f529ec05bba340f4553`) starts the byte-backed reconstruction by:

1. reading the real archive `packages.txt`;
2. discovering exact `ps4_city_tower_<package-id>_<patch>.pkg` filenames rather than guessing a package ID;
3. sparse-locating those members in the split TAR and recording exact TAR offsets, sizes and SHA-256 values;
4. extracting only the Tower package bytes;
5. running the everything census across all recovered Tower snapshots;
6. decoding every directly recoverable Tower texture with the tolerant generation-safe texture path;
7. attempting generic export of every resident `s_entity_model` candidate while recording the source snapshot used;
8. explicitly refusing to infer world placement/ownership from successful model decoding;
9. emitting a compact Tower summary plus the complete resource/reference/literal-edge evidence needed to identify the actual world/static-placement structures next.

Initial Actions run: `33943092135`.

## Tower census completed

The complete Tower-core census run `33943271839` succeeded. Artifact `9963042289` (`d1-tower-map-census-v1`) contains the loss-preserving entry graph, literal edges, texture census, and generic model exports.

Exact current totals:

- 24 physical Tower-core package snapshots across package IDs `023D`, `0244`, `024C`, `0250`;
- 116,794 physical Tiger entry occurrences;
- 21,120 union TagHashes;
- 170,864 aligned literal co-reference edges;
- 1,492 `s_entity_model` occurrences;
- 503 animation-clip occurrences;
- 1,956 `s_entity` occurrences;
- 7,944 EntityResource occurrences;
- 769 texture headers, 748 resolved textures, 21 unresolved;
- 338 `s_entity_model` candidates, 108 successfully exported by the generic exporter.

## First binary-confirmed Tower baked-static chain

`evidence/d1_tower_static_map_validated_chains.json` (initial commit `85788d082c7609c009ee4b086beb38a4831c15d5`) records the first Tower chain that passes all current strict binary invariants in the recovered Tower+`009F` corpus.

The exact chain is:

```text
80CA0B70  class 808008B4 / SStaticMapData candidate
  +0x30 -> 80CA0B96  class 80801B75 / D1 static-map data
              instance count = 123
              instance backing = 80CA0BAE
              backing bytes = 7,872 = 123 * 0x40 exactly
              all matrix floats finite

              static table 80CA0BA0  class 80801A90  43 meshes / 43 infos
              static table 80CA0BA1  class 80801A90  49 meshes / 49 infos
              static table 80CA0BA2  class 80801A90  20 meshes / 20 infos
              static table 80CA0BA3  class 80801A90  12 meshes / 12 infos
```

Totals for this chain:

- 124 baked-static mesh records;
- 124 static-info records;
- **556 serialized placed-geometry references**;
- all 123 transform indices `0..122` are actually referenced;
- all 124 V0/V1/index target triples resolve;
- all 124 triples are consecutive FileHashes;
- all static/material/transform indices pass bounds checks;
- primitive type is `3` for all 124 records;
- 112 buffer triples are Tower-local (`0250`); 12 are in `009F`;
- 22 unique serialized material hashes.

This is **confirmed binary structure**, not yet a claim that the entire Tower world has been reconstructed.

Across all 31 unique `808008B4` Tower candidates, `80CA0B70` is currently the only resource that passes every strict invariant in the recovered corpus. The other 30 remain explicit failures rather than being force-fit to the schema.

## Independent static-to-entity-model geometry corroboration

`tools/d1_tower_static_model_crosscheck.py` (initial commit `21b4d3e9de34e22d7dc67324ef5b6e7e00baf36a`) compares baked-static records to ordinary decoded `s_entity_model` primitive groups by **exact serialized equality only**:

- V0 FileHash;
- V1 FileHash;
- index FileHash;
- index offset;
- index count;
- primitive type;
- LOD/detail level.

For `80CA0B70`, 24 of 124 baked-static records have exact independent counterparts in already decoded ordinary models:

- 18 via `s_entity_model 80CA0B95`;
- 6 via `s_entity_model 80CA0F39`;
- 3 unique shared buffer triples;
- all 24 have one unique, non-conflicting vertex decode signature;
- zero scale/translation/stride conflicts.

The remaining 100 records are not classified as wrong; they simply lack an exact counterpart among the 108 generic model exports currently supplied to the verifier.

This creates an independent test fixture for packed static geometry. `tools/d1_tower_static_quantization_proof.py` (initial commit `f786edcab596f0f327c3c57c54104985863bc0de`) algebraically factors the independently decoded `model_scale` / `model_translation` from the shipped 0x40 static matrices and measures affine/similarity residuals for both raw and transposed conventions. It intentionally does not use visual fit.

## Tower static materials and exact texture co-references

The 124 static records reference 22 unique PS4 material resources. All 22 are class `80801AD7`; seven have payload conflicts across the six `0250` snapshots, so patch generations are preserved rather than silently collapsed.

`tools/d1_material_literal_reference_join.py` and `evidence/d1_tower_80ca0b70_material_references.json` (initial evidence commit `0c8c710ddc7bcd81536f80c6c7ee6c85f4e25c57`) checkpoint the current byte-backed material evidence:

- 22 materials;
- 35 exact fixed-field references matching offsets already decoded by `tools/d1_material_decode.py` (`+0x28` vertex shader, `+0x2A8` pixel shader, `+0x32C` PS vector container where present);
- 9 materials contain exact serialized literal references to recovered texture headers;
- 10 unique recovered texture headers;
- 13 material→texture literal occurrences.

The material→texture edge is proven as serialized co-reference, but **texture stage and texture_index are not assigned from the literal scan**. The dedicated proof workflow re-parses the material dynamic arrays from shipped current-generation bytes before promoting stage/slot semantics.

## Outer map-data chain above the static map

A pinned external schema snapshot (`MontagueM/Charm`, commit `50d36ee1f9ecadad7522504c20b1f3f9c97e30af`) provides candidate D1 layouts for `SMapDataTable`, `SMapDataEntry`, `SMapDataResource`, `SStaticMapParent`, and `ResourcePointer`. These source-derived names/layouts are treated as hypotheses until the shipped PS4 bytes satisfy the exact offsets/classes.

The existing Tower census already supplies a strong literal chain:

```text
80CA0B0E  class 808009A2 / source-derived SMapDataTable
  contains 10 stable literal refs at 0x18 spacing:
    80CA0B22 ... 80CA0B2B  all class 80801AC6

80CA0B27  class 80801AC6 / source-derived SStaticMapParent
  +0x08 -> 80CA0B70

80CA0B70
  +0x30 -> 80CA0B96
```

`80CA0B27 -> 80CA0B70` is especially strong: the shipped reference is at exactly `+0x08`, the field that the pinned D1 `SStaticMapParent` schema identifies as `StaticMap`.

Nine sibling parents (`80CA0B22-26`, `80CA0B28-2B`) point at `80CA0B6F`; that static-map candidate currently fails the strict validator because its D1-static-data link is unresolved/`FFFFFFFF`. Only `80CA0B27` points to the fully passing `80CA0B70` chain.

The map-data table is itself stably referenced by unknown-class resource `80CA0B19` (`80800343`) at `+0x44`; that upstream semantic remains unresolved.

This candidate outer chain is checkpointed in `evidence/d1_tower_80ca0b70_outer_chain_candidate.json` (initial commit `1d961ef446d2890b86cf45a33c1910e8770ba1f4`). `tools/d1_tower_map_data_resource_validate.py` (initial commit `062d7e8d622a8169ed1bb2f763f5317df63569d9`) performs the missing decisive proof by parsing the shipped `SMapDataEntry +0x88` relative ResourcePointer, requiring resource class `80801AEA`, then `+0x0C -> 80CA0B27`, then parent `+0x08 -> 80CA0B70`.

Only after that passes is the containing `SMapDataEntry` rotation/translation allowed to become the outer world transform for this static resource.

## Targeted proof workflow and runner incident

`.github/workflows/d1-tower-80ca0b70-quantization-material-proof.yml` (initial commit `4c22c25c7db75fd68bed1d6c04002f7b53512880`) is SHA-locked to the exact six `0250` package members and four `009F` members recovered by successful validator run `33944444030`. It range-copies those exact bytes directly instead of rescanning the full split TAR.

Its intended proof sequence is:

1. revalidate `80CA0B70 -> 80CA0B96`;
2. independently decode `80CA0B95` and `80CA0F39`;
3. reproduce the 24 exact static/model crossmatches;
4. algebraically prove or reject how packed vertex quantization composes with the 0x40 matrices;
5. parse all 22 current-generation material dynamic arrays and promote texture stage/index only from those bytes;
6. preserve a diagnostic artifact even when a hypothesis is rejected.

The first run `33946377240` did **not execute any workflow code**. GitHub returned a failed job with no steps/runner provisioned, matching the separate contemporaneous Actions runner failure seen on other workflows. This is infrastructure/account-runner state, not a Tower decoder/exporter failure. The tools/evidence remain committed and ready to run when a hosted runner is provisioned again.

## Acceptance boundary for a whole Tower export

Do not call a GLB/scene the Tower merely because it contains many meshes. A final reconstruction needs byte-backed answers for at least:

- which resources are world/static geometry vs ordinary entity models;
- how map chunks/bubbles/cells are related;
- serialized placement transforms and instancing/reuse;
- material and texture ownership per visible geometry;
- static/dynamic prop placement;
- animated entity ownership and rig/clip relationships where applicable;
- coordinate-system/global-origin handling;
- collision or gameplay-only geometry if present and separable;
- LOD/variant/streaming behavior sufficiently understood to choose retail-visible geometry without guessed duplication.

Every unresolved relationship remains visible as unresolved rather than being filled by proximity or visual plausibility.
