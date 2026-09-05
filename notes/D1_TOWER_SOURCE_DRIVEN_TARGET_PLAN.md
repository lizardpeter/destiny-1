# D1 Tower source-driven map target plan

Status: **ownership-derived target selection closed; no hand-written common-carrier list is required.**

This note records the bridge from the binary-closed D1 `SMapDataTable` ownership layer to downstream common/decal and baked-static processing.

## Canonical source behavior

Pinned D1 `MapView.ExtractDataTables` behavior has two independent walks:

1. `LoadDecalsIntoExporterScene` uses `DataEntries[0]` exactly once for each `SMapDataTable`.
2. Baked-static loading walks the map entries independently and processes the rows whose `SStaticMapData` has a direct D1 `80801B75` child.

Therefore table-scoped common/decal selection must not be reconstructed by repeating a common carrier once for every parent row, and baked-static selection must not be inferred from the first row.

The generic bridge is now implemented by:

- `tools/d1_world_static_map_resource_chain_census.py`
- `tools/d1_world_static_map_target_plan.py`
- `tools/d1_world_static_map_decal_validate.py`
- `tools/d1_world_table_scoped_decal_census.py`

The old `tools/d1_tower_static_map_decal_validate.py` path is retained only as a compatibility wrapper around the generic validator.

## Tower target plan from the completed 337-row chain

The source-driven plan emits exactly:

- **9** table-scoped `DataEntries[0]` decal/common targets;
- **10** independently classified baked-static targets;
- **19** total validation/export targets;
- **327** map rows referencing the nine table-scoped common carriers;
- **10** map rows referencing the ten baked carriers.

All nine table-scoped targets are classified `no_direct_d1_static_child` in the current Tower bytes. All ten baked targets are classified `direct_d1_baked_static`.

Exact row ownership:

```text
map table  table-scoped row 0 target   baked target row(s)
---------  -------------------------   -------------------
80C98028   80C98191 x38                row 19 -> 80C98254 -> 80C98258
80C984A0   80C984D7 x13                row  7 -> 80C984D8 -> 80C9858B
80C9895C   80C98A69 x78                row 39 -> 80C98A6B -> 80C98A77
80C989F7   80C993A2 x110               row  1 -> 80C993CD -> 80C994B1
                                        row 56 -> 80C993CF -> 80C994B2
80C997DF   80C997F4 x3                 row  3 -> 80C997F5 -> 80C9981A
80C99956   80C99980 x21                row 11 -> 80C99981 -> 80C9999B
80CA0B0E   80CA0B6F x9                 row  5 -> 80CA0B70 -> 80CA0B96
80CA0B11   80CA0B71 x53                row 27 -> 80CA0B72 -> 80CA0B98
80CA0C4E   80CA0C5F x2                 row  2 -> 80CA0C60 -> 80CA0C6B
```

This proves the two source operations are not interchangeable. The common/decal carrier is consistently row 0 for the current Tower tables, while baked rows can occur anywhere in the table.

## Regression policy

The exporter should derive targets in this order:

```text
SMapDataTable
  -> exact 0x90 SMapDataEntry rows
  -> ResourcePointer / 80801AEA
  -> SStaticMapParent / 80801AC6
  -> SStaticMapData / 808008B4

per table:
  table-scoped decal target = DataEntries[0].SStaticMapData, once

per row:
  if SStaticMapData +0x30 resolves to current 80801B75:
      baked-static target
  else:
      no direct D1 baked child
```

Tower regression assertions remain useful as tests, but they are not target-discovery inputs. A future world is allowed to have different counts, different hashes, and even a first-row target that also carries a baked child; the generic plan preserves that possibility instead of encoding the Tower split as a universal rule.

The current Tower regression must retain:

- 9 table-scoped targets;
- 10 baked targets;
- 327 table-scoped carrier row references;
- 337 total map rows;
- no ownership violations;
- no re-expansion to the false 23,141 common placements.
