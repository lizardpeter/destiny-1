#!/usr/bin/env python3
"""Source-extended adapter for the D1 map data-layer census.

Adds the D1 terrain ResourcePointer schema recovered from the actual Charm D1 merge
revision without changing the base parser's ownership or pointer semantics.

Pinned source:
  MontagueM/Charm@e5c4c7b0affcc00a988441e8f913dad7d0aa9bb9
  Tiger/Schema/Static/Terrain.cs

D1 canonical hashes/offsets:
  SMapTerrainResource  SchemaStruct "371C8080" -> 80801C37, size 0x20
    +0x18 Terrain/STerrain TagHash
  STerrain             SchemaStruct "2E1B8080" -> 80801B2E, size 0xB0

The current Charm revision dropped the D1 SchemaStruct attribute from
SMapTerrainResource while retaining D1 terrain consumer code. The merge-d1 revision
is therefore the direct historical source for this D1 mapping.
"""
from __future__ import annotations

import d1_world_map_data_layer_census as base

TERRAIN_SOURCE = (
    "MontagueM/Charm@e5c4c7b0affcc00a988441e8f913dad7d0aa9bb9 "
    "Tiger/Schema/Static/Terrain.cs"
)

base.KNOWN_RESOURCE_CLASSES["80801C37"] = {
    "name": "SMapTerrainResource",
    "target_offset": 0x18,
    "target_class": "80801B2E",
}
base.PINNED_SOURCE = base.PINNED_SOURCE + " + " + TERRAIN_SOURCE


if __name__ == "__main__":
    raise SystemExit(base.main())
