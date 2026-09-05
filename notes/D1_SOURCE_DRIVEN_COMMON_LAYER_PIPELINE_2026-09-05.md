# D1 source-driven common-layer pipeline checkpoint — 2026-09-05

Status: **the Tower common/decal layer has been refactored from hand-written target/model lists into an ownership-derived D1 world pipeline. Fresh end-to-end CI validation is in progress; the pre-existing legacy-compatible scene regression remains green.**

## Why this refactor matters

The previous Tower visual workflows had already reconstructed the correct 327-record common layer and all 69 referenced EntityModels, but several downstream workflows still encoded historical evidence as execution inputs:

- literal common-carrier hashes;
- a literal 69-model hash array;
- pinned decal-validation artifact run IDs;
- a scene assembler that accepted only individual Tower validation JSONs.

Those inputs were valid Tower evidence, but they were not a reusable world-export architecture. The map-data-table closure now lets the exporter derive the same targets from shipped D1 ownership instead.

## Source-driven chain now implemented

```text
SMapDataTable / 808009A2
  -> exact 0x90 SMapDataEntry rows
  -> ResourcePointer / 80801AEA
  -> SStaticMapParent / 80801AC6
  -> SStaticMapData / 808008B4

per table:
  DataEntries[0].SStaticMapData
    -> table-scoped BA048080 common/decal records
    -> transform + EntityModel TagHash
    -> discovered EntityModel dependency set
    -> map-decal EntityModel geometry export
    -> instanced common-layer glTF scene

independently per row:
  direct +0x30 80801B75
    -> baked-static target
```

The table-scoped and baked walks remain separate because that is what the pinned D1 MapView source does. No common carrier is replayed once per parent row.

## Generic tools

### `tools/d1_world_static_map_target_plan.py`

Consumes the closed resource-chain census and emits:

- one `table_scoped_decal_target` from `DataEntries[0]` per table;
- independent `baked_static_target` rows for direct D1 static children;
- exact source row indices and ownership hashes.

It accepts no common or baked target hashes as discovery inputs.

### `tools/d1_world_static_map_decal_validate.py`

Generic binary validator for D1 `SStaticMapData` / `808008B4` and its `BA048080` decal/common records. The historical Tower validator is now only a compatibility wrapper around this implementation.

### `tools/d1_world_table_scoped_decal_census.py`

Consumes the target plan and materializes the actual table-scoped source records. Schema v2 preserves for each record:

- owning `SMapDataTable`;
- owning `SStaticMapData` carrier;
- exact source record offset;
- every transform matrix and source offset;
- the unknown Vector4 array;
- every EntityModel TagHash/reference check;
- singleton convenience fields without discarding the canonical arrays.

It fails closed if the number of materialized records differs from the parsed source count.

### `tools/d1_world_common_model_plan.py`

Consumes only the completed table-scoped census and derives the EntityModel dependency set and per-table/per-carrier reference histograms. It accepts **zero model hashes** on its command line.

### `tools/d1_world_common_layer_scene.py`

Preferred input is now `--census <source-driven-census.json>`. The old repeated `--validation` interface remains only for reproducing historical artifacts.

The source-driven path carries `d1_map_data_table`, carrier, record index/offset, EntityModel and original D1 matrix data into the scene/report. The glTF adapter remains:

```text
node_gltf = D1_ZUP_TO_GLTF_YUP @ transpose(BA048080 row-vector matrix)
```

## Tower regression fixture

The new generic pipeline is expected to reproduce, without using these values as discovery inputs:

- 9 `SMapDataTable` resources;
- 337 closed map rows;
- 9 table-scoped first-entry targets;
- 327 materialized BA048080 common records;
- 327 export-ready singleton transform/model records;
- 69 discovered unique EntityModels;
- 163 selected model geometry parts;
- 15,541 model triangles;
- 327 geometry-emitting record placements;
- 709 common-layer scene geometry nodes;
- 0 unresolved common records.

The already-solved baked side remains:

- 10 baked-static cells;
- 50,148 serialized placements;
- 11,728 retail-visible placements.

The false 23,141 repeated-parent common count remains forbidden.

## Workflow changes

`D1 Tower common-layer model export` now regenerates the map ownership chain, table-scoped census and generic common-model plan before exporting models. Its former literal 69-hash array has been removed. `69` remains only a Tower regression assertion.

`D1 Tower source-driven common scene` is a new downstream regression. It consumes the census and model-plan artifacts from the common-model workflow and assembles the common GLB using `--census`; it does not download the old pinned Tower decal artifact.

## Commits in this refactor

```text
e3605564  Derive D1 static-map targets from ownership chains
679306e8  Promote generic D1 static-map decal validator
d081a61b  Route Tower decal validation through generic world parser
20407c78  Census D1 table-scoped decals from ownership plan
f984422a  Validate Tower common layer from discovered map targets
f2a8c3ad  Emit exporter-ready D1 table-scoped records
ea4a5992  Consume ownership-derived common-layer census
d1247d1a  Plan D1 common models from table-scoped records
698394da  Use generic common-model dependency plan
79dbe179  Add source-driven Tower common-scene regression
```

## Remaining generalization boundary

The current Tower workflows still receive the nine known Tower `SMapDataTable` hashes as the world-root fixture. Everything downstream of those table roots is now discovered from binary ownership.

The next map-format problem is therefore narrower and cleaner than before: **derive the relevant `SMapDataTable` root set from the destination/activity/world ownership graph instead of supplying those table hashes manually.** Once that root discovery is closed, the static/common part of this pipeline can move to another D1 destination without Tower-specific carrier, model or placement lists.
