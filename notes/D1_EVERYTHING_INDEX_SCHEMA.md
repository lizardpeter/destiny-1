# D1 Everything Index — Canonical Browser/RE Schema

Status: active. This is the loss-preserving index contract for the Destiny 1 reversal project.

## Objective

The index must be capable of representing **every physical Tiger resource occurrence in the archive and every recoverable code-side object in each analyzed executable build**, whether or not its semantic role is understood yet, and then layering proven semantic identities, relationships, implementations, exports and previews on top without destroying the raw evidence.

An asset or code object is never omitted merely because it is unnamed, lacks a public Bungie definition, has no current exporter/decompiler, or is still an unknown reference/class/function. Tiger-resource identity and executable-code identity remain separate authority layers until an evidence edge proves a relationship.

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



### 3. Executable build

One immutable record for each exact executable artifact that enters code-side analysis.

Required fields:

- game/platform/title ID and reported application version;
- exact executable SHA-256 and byte size;
- identity proof state and provenance;
- container type (`PS4 SELF`, plain/recovered ELF, or unknown);
- embedded ELF offset when present;
- ELF architecture, entry point, program segments and executable ranges when decoded;
- image-base/load-base observations kept separately from image-relative offsets;
- external/private blob locator when retained outside Git;
- analysis-tool versions and import options;
- known runtime anchors;
- whether decrypted executable bytes are actually available to the analysis workspace.

**The executable SHA-256 is the primary code-side namespace.** Version labels do not merge two binaries, and two binaries with the same title/application label remain distinct until byte identity is proven.

Retail executable bytes are not stored in this Git repository. Git stores hashes, structural reports, derived code graphs, evidence and reconstructed source/pseudocode.

### 4. Executable function

Every recovered function belongs to exactly one exact executable SHA-256.

Required fields:

- executable SHA-256;
- image-relative entry offset;
- exact body ranges rather than an assumed contiguous span;
- function-boundary source/tool and analysis version;
- instruction count and instruction-byte count;
- exact instruction-byte SHA-256;
- mnemonic-sequence SHA-256;
- recovered/generated name and name provenance;
- namespace;
- calling convention and prototype when available;
- thunk/external status;
- proof/reversal state;
- decompilation/pseudocode artifact reference when produced;
- reconstructed implementation reference when produced;
- validation/equivalence evidence for any implementation.

Function names such as Ghidra `FUN_...` are presentation labels, not semantic identities. Stable function identity is anchored to exact executable SHA-256 plus image-relative entry/body evidence.

### 5. Executable import / external library

Imports are first-class code objects.

Required fields:

- owning executable SHA-256;
- library/module identity;
- imported function name or ordinal/NID when available;
- original imported name provenance;
- thunk/import address when present;
- callers/xrefs;
- semantic classification only when demonstrated.

This layer is particularly useful for locating networking, threading, allocation, PS4 system-service, GPU, audio and decompression boundaries before internal function names are recovered.

### 6. Defined/debug string

Every useful executable string retains:

- exact executable SHA-256;
- image-relative address/file offset when available;
- encoding/data type;
- exact text or a content hash when text should not be duplicated;
- every code/data xref;
- owning/referencing function;
- semantic interpretation and proof state.

Strings are **anchors**, not function names. A function referencing `Graphics Heartbeat`, a Tiger class name, or a diagnostic message is not automatically assigned that semantic role without surrounding control/data-flow evidence.

### 7. Code edge

Code relationships are explicit graph edges. Core predicates include:

- `HAS_FUNCTION`
- `CALLS`
- `IMPORTS_LIBRARY`
- `IMPORTS_FUNCTION`
- `REFERENCES_STRING`
- `READS_GLOBAL`
- `WRITES_GLOBAL`
- `LOADS_CONSTANT`
- `SPAWNS_THREAD`
- `INVOKES_DECOMPRESSION`

Every edge records its exact build, source address/xref when applicable, derivation tool, and proof state.

### 8. Cross-version function equivalence

Cross-build matching is a relationship, never an overwrite.

Allowed default promotion policy:

- unique exact instruction-byte fingerprint match under recovered function boundaries -> `PROVEN` body equality;
- unique mnemonic-sequence + instruction-count match -> `STRONGLY_SUPPORTED` structural correspondence;
- unique preserved non-generated function/symbol name -> `CANDIDATE`;
- matching image-relative offset alone -> **no identity promotion**.

A cross-version match retains both original function nodes and creates an explicit equivalence/correspondence edge. Differences in immediates, constants, calls, body ranges, CFG or referenced data remain queryable.

### 9. Code ↔ Tiger/resource bridge

This is the layer that makes the executable valuable to the existing Destiny graph.

A function may be linked to package/resource knowledge only by evidence such as:

- direct comparison with a serialized class/TagHash constant;
- exact parser field offsets matching a byte-closed Tiger structure;
- xrefs to raw/debug strings tied to an existing resource class;
- call/data flow into a known package reader/decompressor;
- code consuming a proven shader/material/texture/skeleton/animation/world layout;
- runtime trace linking an exact code address to an exact resource/tag;
- source-correlated constant/table identity.

Representative predicates:

- `PARSES_TIGER_STRUCTURE`
- `RESOLVES_TAG_HASH`
- `CONSUMES_RESOURCE_CLASS`
- `DECODES_TEXTURE`
- `DECODES_ANIMATION`
- `SELECTS_MATERIAL`
- `BINDS_SHADER_RESOURCE`
- `EVALUATES_SHADER_PROGRAM`
- `LOADS_WORLD_GRAPH`
- `OWNS_RUNTIME_BEHAVIOR_FOR`
- `IMPLEMENTS_SEMANTIC_ASSET_BEHAVIOR`

The target graph path is therefore loss-preserving:

```text
exact executable build
  -> function
  -> call/data-flow evidence
  -> Tiger parser/resource/class/tag
  -> semantic asset
  -> reconstructed pseudocode/implementation
  -> validation evidence
```

No edge is inferred merely because a function and an asset are both relevant to the same subsystem.


### 10. Evidence edge

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

### 11. Semantic asset

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

### 12. Export artifact

Every generated GLB/PNG/DDS/WAV/etc. records:

- source resource(s)
- exact source physical snapshot(s)
- exporter/tool + commit
- output SHA-256
- export limitations
- whether ownership/placement is proven or merely the resource was decoded in isolation

Successful decoding never upgrades relationship confidence by itself.

### 13. Preview/presentation asset

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
7. **preview coverage** — semantic assets with a provenance-labeled preview / semantic assets;
8. **executable acquisition coverage** — fingerprinted/decrypted executable builds available / builds targeted for analysis;
9. **function discovery coverage** — recovered function bodies / executable code ranges attributable to functions;
10. **function semantic coverage** — functions with evidence-backed semantic roles / recovered functions;
11. **call/import graph coverage** — recovered calls/imports/xrefs / discoverable analyzed code relationships;
12. **code ↔ resource linkage coverage** — package/resource schemas with at least one proven executable consumer / code-relevant reversed schemas;
13. **decompilation coverage** — functions with retained decompiler/pseudocode artifacts / recovered functions;
14. **reimplementation coverage** — semantically recovered functions/subsystems with validated portable implementations / implementation targets.

These denominators remain separate. A high package-export percentage does not imply code reversal completeness, and a high function-discovery percentage does not imply semantic understanding.

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


## Code-side canonical identity and storage policy

The code graph is keyed by executable SHA-256, not by filename or reported app version.

Recommended durable/private object layout when executable bytes are lawfully available:

```text
destiny1/ps4/executables/<title_id>/<app_version>/<sha256>/eboot.bin
destiny1/ps4/executables/<title_id>/<app_version>/<sha256>/modules/<name>.sprx
destiny1/ps4/derived/codegraph/<sha256>/ghidra.json
destiny1/ps4/derived/codegraph/<sha256>/nodes.jsonl
destiny1/ps4/derived/codegraph/<sha256>/edges.jsonl
destiny1/ps4/derived/decomp/<sha256>/<function-id>.*
```

The graph stores the content hash and object locator. It does not embed large binary blobs.

Current code-side tooling:

- `tools/d1_executable_probe.py`
- `tools/d1_executable_knowledge.py`
- `tools/ghidra/D1ExportCodeGraph.py`
- `tools/d1_ghidra_graph_normalize.py`
- `tools/d1_executable_compare.py`

The relocation-stable public runtime anchor at `eboot + 0xFAAF4` is represented as an evidence node. It must remain distinct from a function identity until exact executable bytes close the containing function and cross-version comparison.
