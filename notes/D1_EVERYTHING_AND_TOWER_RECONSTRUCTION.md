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
