# D1 Everything Index — Canonical Browser/RE Schema

Status: active. This is the loss-preserving index contract for the Destiny 1 reversal project.

## Objective

The index must be capable of representing **every physical Tiger resource occurrence in the archive**, whether or not its semantic class is understood yet, and then layering proven semantic identities, relationships, exports and previews on top without destroying the raw evidence.

An asset is never omitted merely because it is not an inventory item, lacks a public Bungie definition, has no current exporter, or is still an unknown reference/class hash.

## Record layers

### 1. Physical occurrence

One row for each resource entry as it physically appears in one shipped package snapshot.

Required fields:

- platform
- physical package filename
- logical package family
- package id
- patch/generation suffix
- entry index
- TagHash
- Tiger type/subtype
- reference/class hash
- byte size
- starting block and block offset
- availability/backing state
- payload SHA-256 when recoverable
- extraction/decompression errors, retained rather than suppressed

This is the bottom authority layer.

### 2. Logical Tiger resource

Groups physical occurrences that have the same exact Tiger identity while retaining every occurrence and any cross-generation conflicts.

Required fields:

- resource key
- TagHash
- occurrence list
- reference/class history
- size history
- payload-hash history
- known class label only when byte-validated
- decode status
- semantic classification status

A patch winner is not silently selected unless patch/backing semantics for that family are proven.

### 3. Evidence edge

Every relationship is a separate object, not an implicit property of proximity.

Required fields:

- source resource
- target resource/value
- edge type
- exact serialized/table offset or proven table row when applicable
- evidence kind
- decoder/tool version or commit
- confidence/status
- semantic interpretation

Evidence kinds include:

- explicit serialized TagHash/FileHash field
- exact investment table join
- EntityParent/EntityDataROI relationship
- validated runtime-rig component relationship
- validated material/texture slot relationship
- exact placement/transform record
- aligned literal TagHash co-reference
- external official Bungie presentation metadata

`aligned literal TagHash` is deliberately weaker than an ownership edge. It means only that an aligned dword in one structured payload equals a known TagHash.

### 4. Semantic asset

A semantic asset is created only after enough evidence exists to say what the resource or resource graph represents.

Examples:

- weapon
- armor piece
- character/enemy
- static prop
- animated world object
- architecture module
- terrain/world chunk
- placement/instance set
- collision resource
- material
- shader
- texture/texture plate
- skeleton
- runtime rig
- animation clip/control graph
- particle/effect/decal
- UI/Director asset
- cinematic resource
- audio resource/event
- activity/world script

Unknown resources remain valid logical Tiger resources until classified.

### 5. Export artifact

Every generated GLB/PNG/DDS/WAV/etc. records:

- source resource(s)
- exact source physical snapshot(s)
- exporter/tool + commit
- output SHA-256
- export limitations
- whether ownership/placement is proven or merely the resource was decoded in isolation

Successful decoding never upgrades relationship confidence by itself.

### 6. Preview/presentation asset

Preview provenance is mandatory:

- `PKG_EXTRACTED` — decoded from shipped package bytes
- `OFFICIAL_BUNGIE_WEB` — Bungie-authored manifest/web presentation asset, not package-derived
- `GENERATED_PREVIEW` — rendered from recovered package geometry/materials
- `COMMUNITY_REFERENCE` — optional research aid, never ownership evidence
- `NONE` — no visual yet

The HTML must surface this provenance visibly, not hide it in a details pane.

## Completeness accounting

Archive-wide completion is measured at multiple levels rather than one misleading percentage:

1. **physical occurrence coverage** — package entries inventoried / total package entries;
2. **payload recoverability** — resident/decompressible payloads / inventoried occurrences;
3. **class/schema coverage** — resources whose reference/class semantics are byte-decoded / logical resources;
4. **semantic identity coverage** — resources assigned a proven asset role / logical resources;
5. **relationship coverage** — required ownership/placement/material/rig edges proven / required edges discovered;
6. **export coverage** — semantic assets with validated exports / semantic exportable assets;
7. **preview coverage** — semantic assets with a provenance-labeled preview / semantic assets.

Inventory/item manifest coverage is a presentation subset, never the denominator for “all Destiny assets.”

## Map/world acceptance rules

A map is not “complete” because many meshes can be exported. A reconstructed map must preserve, from serialized evidence:

- world/chunk/cell membership;
- placement transforms and instance reuse;
- static vs dynamic objects;
- material/texture ownership;
- world origin/coordinate transforms;
- LOD/variant selection sufficiently to avoid guessed duplicate geometry;
- relevant collision/gameplay-only geometry when present;
- animated world-object owner/rig/clip relationships;
- environment/effect resources where required for the shipped scene.

Until those relationships are decoded, exported meshes remain isolated asset records rather than a claimed complete map.

## Current validation fixtures

The everything index must retain at minimum these already-proven fixtures:

- Gjallarhorn Year 3 full current graph (`D471D331`, exact shared owner `80AA3CA2`);
- Vex animation-bundle proxy `816CE09A` with skeleton `816CE092`, runtime rig `816CE095`, 12 controls and clips `816CE09D` / `816CE09E`;
- ordinary visible Vex model/material fixture `809C44A5 -> 809C47F4 -> 809C475F / 809C4760`, while explicitly leaving proxy-rig compatibility unresolved;
- raw UI/Director texture census: 520 headers, 508 decoded PKG PNGs across `ui_core`, `ui_menus`, and `ui_orbit`;
- Tower namespace: all 157 `ps4_city_tower*` physical members retained, with 24 non-localized core members in the initial structural census.
