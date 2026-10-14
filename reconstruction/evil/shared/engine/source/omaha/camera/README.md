# camera/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `omaha.camera`  
**Folder path evidence:** `HYPOTHESIS` (folder name is a proposal from RTTI/log-channel clustering, not a recovered path)  
**Role:** cameras, director, cinematics, observer

## Source files named in the binary

_None recovered (retail build stripped most asserts)._

## Decompiled functions

| VA | name | class | evidence | pseudo-C | role |
|---|---|---|---|---|---|
| `0x900ad0` | player_camera_impulse_offset |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`900ad0_player_camera_impulse_offset.c`](decompiled/900ad0_player_camera_impulse_offset.c) | Sums up to 8 timed camera impulses (shake / kick curves at 0x273DA50) into a yaw/pitch offset; the player update adds recoil and the stick look on top. |

## Classes (33)

Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. Placement in this folder is `HYPOTHESIS` (name-token rule).

| class | typeinfo | vtable | virtual slots | bases |
|---|---|---|---|---|
| `c_animated_trick_camera` | `0x1949b70` | `0x1949ac0` | 24 | c_camera |
| `c_authored_camera` | `0x1949c50` | `0x1949ba0` | 24 | c_camera |
| `c_camera` | `0x1949d30` | `0x1949c80` | 24 |  |
| `c_camera_globals_game_system` | `0x1938510` | `0x19384e0` | 8 | c_game_system_interface |
| `c_cinematic_camera` | `0x1949ea0` | `0x1949df0` | 24 | c_camera |
| `c_cinematic_graphics_manager` | `0x1937d60` | `0x1937d30` | 8 | c_game_system_interface |
| `c_combatant_sensor_authority_change_observer` | `0x1907a50` | `0x1907a30` | 3 | i_authority_change_callback_interface |
| `c_dead_camera` | `0x1949f80` | `0x1949ed0` | 24 | c_camera |
| `c_debug_director` | `0x194a020` | `0x1949fb0` | 13 | c_director |
| `c_demo_camera` | `0x194a100` | `0x194a050` | 24 | c_camera |
| `c_director` | `0x194a198` | `0x194a130` | 15 |  |
| `c_director_game_system` | `0x1940f50` | `0x1940f20` | 8 | c_game_system_interface |
| `c_editor_director` | `0x194a400` | `0x194a390` | 13 | c_director |
| `c_first_person_camera` | `0x194a4e0` | `0x194a430` | 24 | c_camera |
| `c_flying_camera` | `0x194a5c0` | `0x194a510` | 24 | c_camera |
| `c_following_camera` | `0x194a6a0` | `0x194a5f0` | 24 | c_camera |
| `c_game_director` | `0x194a750` | `0x194a6e0` | 13 | c_director |
| `c_game_interface_camera` | `0x194a830` | `0x194a780` | 24 | c_camera |
| `c_killer_camera` | `0x194a280` | `0x194a1d0` | 24 | c_orbiting_camera |
| `c_linked_flying_camera` | `0x194a910` | `0x194a860` | 24 | c_flying_camera |
| `c_loading_cinematic_data_component` | `0x1963b30` | `0x1963a50` | 21 | c_cui_object_component |
| `c_loki_director` | `0x194a9b0` | `0x194a940` | 13 | c_director |
| `c_look_at_camera` | `0x194aa90` | `0x194a9e0` | 24 | c_flying_camera |
| `c_null_camera` | `0x194a360` | `0x194a2b0` | 24 | c_camera |
| `c_observer_director` | `0x194ab50` | `0x194aae0` | 16 | c_director |
| `c_observer_game_system` | `0x1940ef0` | `0x1940ec0` | 8 | c_game_system_interface |
| `c_respawning_camera` | `0x194ad10` | `0x194ac60` | 24 | c_camera |
| `c_saved_film_director` | `0x194adb0` | `0x194ad40` | 16 | c_observer_director |
| `c_space_flight_director` | `0x194ae50` | `0x194ade0` | 13 | c_director |
| `c_squad_sensor_authority_change_observer` | `0x19065b0` | `0x1906590` | 3 | i_authority_change_callback_interface |
| `c_static_camera` | `0x194af30` | `0x194ae80` | 24 | c_camera |
| `c_target_aligned_camera` | `0x194b010` | `0x194af60` | 24 | c_camera |
| `c_tracked_target_camera` | `0x194b100` | `0x194b050` | 24 | c_camera |

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
