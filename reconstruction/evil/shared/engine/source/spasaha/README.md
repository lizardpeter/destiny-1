# spasaha/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `spasaha`  
**Folder path evidence:** `CONFIRMED_BINARY`  
**Role:** Destiny-specific game layer; Jam target engine_source_spasaha_spasaha -> tiger_release_final.elf

## Sub-folders

- [`investment/`](investment/README.md) — items, vendors, talent grids, rewards
- [`spasahalib/`](spasahalib/README.md) — Destiny game library
- [`xetrov/`](xetrov/README.md) — xetrov client/engine shim and message queue

## Source files named in the binary

_None recovered (retail build stripped most asserts)._

## Decompiled functions

| VA | name | class | evidence | pseudo-C | role |
|---|---|---|---|---|---|
| `0x25a550` | definitions_manager |  | Static decompilation plus d1-native research traces (D1_TRACE_* / D1_BYPASS runs: co-op joining, replication, Director, unlock flags, gear), 2026-10-15/16; names are HYPOTHESIS | [`25a550_definitions_manager.c`](decompiled/25a550_definitions_manager.c) | Definitions manager accessor. Vtable +0x290 / +0x298 / +0x2A0 list the master flag index of each stored unlock-flag slot (profile 3100 at +0x383C, profile extra 274 at +0x5430, character 2189 at +0x53C0; {i32 count, i64 relative array @+8} of 8-byte entries, i16 master index @+0x14); +0x100 the equipment slot order; +0x168 the inventory item map; +0x410 item definitions by index. |
| `0x25a6e0` | activity_definitions |  | Static decompilation plus d1-native research traces (D1_TRACE_* / D1_BYPASS runs: co-op joining, replication, Director, unlock flags, gear), 2026-10-15/16; names are HYPOTHESIS | [`25a6e0_activity_definitions.c`](decompiled/25a6e0_activity_definitions.c) | Activity definitions: content globals (*0x26527E8) vtable +0x38 -> block {count @0, relptr @8 -> 16-byte entries, relptr @+8 -> 0x100-byte definition}; definition +0 activity hash, +0x58 scenario name, +0x88 type tag, +0xA4 matchmaking content hash. 653 definitions. |
| `0x528c50` | activity_availability_provider_query |  | Static decompilation plus d1-native research traces (D1_TRACE_* / D1_BYPASS runs: co-op joining, replication, Director, unlock flags, gear), 2026-10-15/16; names are HYPOTHESIS | [`528c50_activity_availability_provider_query.c`](decompiled/528c50_activity_availability_provider_query.c) | Availability provider (*0x26527D8) vtable +0x40: answers an activity's availability; 7 = unavailable, seen for e.g. Moon missions. |
| `0x58fd40` | director_show_activity_nodes |  | Static decompilation plus d1-native research traces (D1_TRACE_* / D1_BYPASS runs: co-op joining, replication, Director, unlock flags, gear), 2026-10-15/16; names are HYPOTHESIS | [`58fd40_director_show_activity_nodes.c`](decompiled/58fd40_director_show_activity_nodes.c) | Director: shows an activity node when its state (0x264360) is 3 or higher (4 = newly available); d1-native D1_BYPASS=activities reports locked nodes (2) as 3. |
| `0x5909b0` | director_destination_state |  | Static decompilation plus d1-native research traces (D1_TRACE_* / D1_BYPASS runs: co-op joining, replication, Director, unlock flags, gear), 2026-10-15/16; names are HYPOTHESIS | [`5909b0_director_destination_state.c`](decompiled/5909b0_director_destination_state.c) | Director destinations: each destination has two more unlock expressions besides its activity state list; the solar-system gates are flags 3850, 98, 2539 and 170\|2549. |

## Classes (13)

Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. Placement in this folder is `HYPOTHESIS` (name-token rule).

| class | typeinfo | vtable | virtual slots | bases |
|---|---|---|---|---|
| `c_achievements_spasaha_game_system` | `0x1941380` | `0x1941350` | 8 | c_game_system_interface |
| `c_activity_engine_shim_spasaha` | `0x19360d0` | `0x1935f70` | 43 | c_activity_engine_shim |
| `c_character_engine_shim_spasaha` | `0x1937a90` | `0x1937a80` | 4 | i_character_engine_shim |
| `c_incident_engine_shim_spasaha` | `0x1938ab0` | `0x1938a70` | 7 | i_incident_engine_shim |
| `c_investment_engine_shim_spasaha` | `0x1939c50` | `0x1939c00` | 9 | i_investment_engine_shim |
| `c_networking_engine_shim_spasaha` | `0x1941aa0` | `0x1941a80` | 3 | i_networking_engine_shim |
| `c_player_manager_spasaha_game_system` | `0x1944520` | `0x19444f0` | 8 | c_game_system_interface |
| `c_rich_presence_spasaha_game_system` | `0x1941320` | `0x19412f0` | 8 | c_game_system_interface |
| `c_spasaha_ai_game_interface` | `0x19375b0` | `0x19374f0` | 26 | c_ai_game_interface |
| `c_spasaha_debug_render_game_interface` | `0x1938660` | `0x1938650` | 1 | c_debug_render_game_interface |
| `c_spasaha_engine_interface` | `0x1943ef0` | `0x19439a0` | 172 | c_engine_interface |
| `c_spasaha_global_interface` | `0x1938620` | `0x19385f0` | 8 | c_game_system_interface |
| `c_xetrov_engine_shim_spasaha` | `0x1947770` | `0x1947750` | 6 | c_xetrov_engine_shim |

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
