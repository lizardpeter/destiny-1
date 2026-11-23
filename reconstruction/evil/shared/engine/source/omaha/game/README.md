# game/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `omaha.game`  
**Folder path evidence:** `CONFIRMED_BINARY`  
**Role:** game / game_engine; *_game_system classes derive from c_game_system_interface

## Source files named in the binary

Verbatim path strings (`CONFIRMED_BINARY`). Each has a placeholder file here to be filled in.

- `d:\bungie\evil\shared\engine\source\omaha\game\game.cpp` → [`game.cpp`](game.cpp) — not yet reconstructed
- `d:\bungie\evil\shared\engine\source\omaha\game\game_engine.cpp` → [`game_engine.cpp`](game_engine.cpp) — not yet reconstructed

## Decompiled functions

| VA | name | class | evidence | pseudo-C | role |
|---|---|---|---|---|---|
| `0x591b30` | game_time_paused |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`591b30_game_time_paused.c`](decompiled/591b30_game_time_paused.c) | True while game time is paused (byte flags at *0x26BC888 bit 1, when the time globals exist). |
| `0x6e7e20` | game_local_player_unit |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`6e7e20_game_local_player_unit.c`](decompiled/6e7e20_game_local_player_unit.c) | Simulation interface +0x138: the local player's unit index or -1. |
| `0x91adb0` | player_control_initialize | c_player_control_game_system | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`91adb0_player_control_initialize.c`](decompiled/91adb0_player_control_initialize.c) | c_player_control_game_system initialize: allocates player_control_globals (0x290) and player_control_globals_deterministic (0x50). |
| `0x91af00` | player_control_dispose | c_player_control_game_system | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`91af00_player_control_dispose.c`](decompiled/91af00_player_control_dispose.c) | Frees the player control globals. |
| `0x91af20` | player_control_initialize_for_new_map | c_player_control_game_system | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`91af20_player_control_initialize_for_new_map.c`](decompiled/91af20_player_control_initialize_for_new_map.c) | Clears player control state for a new map, keeping three option bytes (+0x288..+0x28A). |
| `0x91b500` | player_control_update_player |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`91b500_player_control_update_player.c`](decompiled/91b500_player_control_update_player.c) | Per player look and move: sticks -> floats (0x926320), southpaw/legacy swaps, response curves (tag at +0x130), move vector (+0x2C0) and look (+0x2C8..+0x2DC, invert flags); look rate (0x928670) -> aim assist, curve limits, zoom scaling (weapon_zoom_magnification / weapon_zoom_look_scale) -> action[5] = yaw_rate*dt, action[6] = pitch_rate*dt (radians, +yaw left, +pitch up). d1-native's mouse look hooks here. The slot's desired facing (player_control_globals +0x20 + slot*0x1A0 + 0x18/+0x1C: yaw wrapped to [0, 2pi), pitch) integrates these deltas 1:1 each update (verified at runtime). |
| `0x91da30` | player_control_apply_movement |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`91da30_player_control_apply_movement.c`](decompiled/91da30_player_control_apply_movement.c) | Movement part of the action: left stick (state +0x2C0/+0x2C4) rotated into the unit's frame. |
| `0x91ee90` | player_control_update |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`91ee90_player_control_update.c`](decompiled/91ee90_player_control_update.c) | Per local player: builds the unit action (0x80 bytes) with player_control_build_action, suppresses it while UI / cinematics / death cam own input, applies the control fade (+0x14/+0x18), and raises action flags. |
| `0x923430` | player_set_unit_index |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`923430_player_set_unit_index.c`](decompiled/923430_player_set_unit_index.c) | Assigns a unit to a player (player table g_273EB80 +0xC0 + i*4), keeps unit count +0xBC and the per-unit player mask. |
| `0x923790` | local_player_has_unit |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`923790_local_player_has_unit.c`](decompiled/923790_local_player_has_unit.c) | 0 if player 0 has a unit, else -1. |
| `0x925ee0` | input_abstraction_initialize | c_input_abstraction_game_system | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`925ee0_input_abstraction_initialize.c`](decompiled/925ee0_input_abstraction_initialize.c) | c_input_abstraction_game_system initialize: clears 0x273ED40; per player default turn speeds 2.0944 (yaw, 120 deg/s) and 1.0472 (pitch, 60 deg/s) rad/s and the default button->action table. |
| `0x9261d0` | input_abstraction_dispose | c_input_abstraction_game_system | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`9261d0_input_abstraction_dispose.c`](decompiled/9261d0_input_abstraction_dispose.c) | Clears the input abstraction globals. |
| `0x9261f0` | input_abstraction_initialize_for_new_map | c_input_abstraction_game_system | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`9261f0_input_abstraction_initialize_for_new_map.c`](decompiled/9261f0_input_abstraction_initialize_for_new_map.c) | Marks every action binding unmapped (0x25) and enables input abstraction (0x273FBE9 = 1). |
| `0x9262f0` | input_abstraction_dispose_from_old_map | c_input_abstraction_game_system | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`9262f0_input_abstraction_dispose_from_old_map.c`](decompiled/9262f0_input_abstraction_dispose_from_old_map.c) | Disables input abstraction (0x273FBE9 = 0). |
| `0x926320` | input_abstraction_sticks_to_float |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`926320_input_abstraction_sticks_to_float.c`](decompiled/926320_input_abstraction_sticks_to_float.c) | Player state sticks (s16) -> 4 floats in [-1, 1] (left x/y, right x/y), with the optional radial response curve from the controller preferences. |
| `0x926600` | input_abstraction_reset_player |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`926600_input_abstraction_reset_player.c`](decompiled/926600_input_abstraction_reset_player.c) | Resets one player's abstracted input when input abstraction is off. |
| `0x926910` | input_abstraction_update |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`926910_input_abstraction_update.c`](decompiled/926910_input_abstraction_update.c) | Per player: copies both sticks (s16) from the gamepad state to player state +0x2A2/+0x2A6, applies the per-player dead-zone mode (axial / scaled radial, inner/outer from the controller preferences 0x5287F0), caches stick angles (+0x2AC/+0x2B0), copies touch/motion, then maps buttons to abstract actions (+0x0..). |
| `0x928560` | input_abstraction_player_state |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`928560_input_abstraction_player_state.c`](decompiled/928560_input_abstraction_player_state.c) | Returns the per-player input state: 0x273EFE0 + player * 0x300. |
| `0x928670` | input_abstraction_look_rate |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`928670_input_abstraction_look_rate.c`](decompiled/928670_input_abstraction_look_rate.c) | Look rate: yaw = state[+0x2CC] * turn_speed[0], pitch = state[+0x2D4] * turn_speed[1] (rad/s). With state +0x2A0 set (externally driven input) the values at +0x2C8/+0x2D0 are per-frame deltas and are divided by dt. |
| `0x928710` | input_abstraction_static_init |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`928710_input_abstraction_static_init.c`](decompiled/928710_input_abstraction_static_init.c) | Static constants (2pi, pi, pi/2, ...), default stick/action layout table 0x273FBF0 and unmapped (0x25) bindings. |
| `0x92a3d0` | block_detect_thread |  | Static decompilation plus d1-native runtime traces (frame timing, prologue cinematic, cinematic suppression), 2026-10-13 night | [`92a3d0_block_detect_thread.c`](decompiled/92a3d0_block_detect_thread.c) | BLOCK_DETECT thread (thread table 0x194C3A8): detects main-loop / job stalls and halts with 'hitch detected: mainloop world controller state ... stalled' (writes a crash folder). d1-native's D1_NO_BLOCK_DETECT disables it for software-rendered tests. |
| `0xbd3740` | weapon_zoom_magnification |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`bd3740_weapon_zoom_magnification.c`](decompiled/bd3740_weapon_zoom_magnification.c) | Magnification of a unit's weapon at a zoom level (1 when not zoomed / no weapon). |
| `0xbd3a50` | weapon_zoom_look_scale |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`bd3a50_weapon_zoom_look_scale.c`](decompiled/bd3a50_weapon_zoom_look_scale.c) | Per-axis look-speed scale while zoomed (1 - weapon tag +0x1B4 for yaw, 1 - +0x184 for pitch). |

## Classes (40)

Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. Placement in this folder is `HYPOTHESIS` (name-token rule).

| class | typeinfo | vtable | virtual slots | bases |
|---|---|---|---|---|
| `c_action_system_game_system` | `0x1935c40` | `0x1935c10` | 8 | c_game_system_interface |
| `c_bs_game_system` | `0x1907b20` | `0x1907af0` | 8 | c_game_system_interface |
| `c_capturable_game_system` | `0x1936910` | `0x19368e0` | 8 | c_game_system_interface |
| `c_cheats_game_system` | `0x1940bf0` | `0x1940bc0` | 8 | c_game_system_interface |
| `c_client_random_game_system` | `0x1941820` | `0x19417f0` | 8 | c_game_system_interface |
| `c_console_game_system` | `0x1941440` | `0x1941410` | 8 | c_game_system_interface |
| `c_control_globals_game_system` | `0x1938580` | `0x1938550` | 8 | c_game_system_interface |
| `c_darkness_mode_game_system` | `0x1943710` | `0x19436e0` | 8 | c_game_system_interface |
| `c_data_mine_game_system` | `0x19418e0` | `0x19418b0` | 8 | c_game_system_interface |
| `c_dumpling_cached_result_game_system` | `0x1947c50` | `0x1947c20` | 8 | c_game_system_interface |
| `c_dynamic_decal_sim_game_system` | `0x1949210` | `0x19491e0` | 8 | c_game_system_interface |
| `c_editor_game_system` | `0x19408d0` | `0x19408a0` | 8 | c_game_system_interface |
| `c_fiber_game_system` | `0x19096a0` | `0x1909670` | 8 | c_game_system_interface |
| `c_game_engine` | `0x194b470` | `0x194b430` | 10 |  |
| `c_game_engine_game_system` | `0x1941110` | `0x19410e0` | 8 | c_game_system_interface |
| `c_game_globals_game_system` | `0x19419a0` | `0x1941970` | 8 | c_game_system_interface |
| `c_game_state_game_system` | `0x1941200` | `0x19411d0` | 8 | c_game_system_interface |
| `c_game_time_game_system` | `0x1940610` | `0x19405e0` | 8 | c_game_system_interface |
| `c_ghost_link_game_system` | `0x1935e70` | `0x1935e40` | 8 | c_game_system_interface |
| `c_host_random_game_system` | `0x19417c0` | `0x1941790` | 8 | c_game_system_interface |
| `c_hs_game_system` | `0x1940b90` | `0x1940b60` | 8 | c_game_system_interface |
| `c_input_abstraction_game_system` | `0x19413e0` | `0x19413b0` | 8 | c_game_system_interface |
| `c_interface_game_system` | `0x1940c50` | `0x1940c20` | 8 | c_game_system_interface |
| `c_label_globals_game_system` | `0x1914840` | `0x1914810` | 8 | c_game_system_interface |
| `c_light_bar_game_system` | `0x1940d70` | `0x1940d40` | 8 | c_game_system_interface |
| `c_materials_game_system` | `0x1940810` | `0x19407e0` | 8 | c_game_system_interface |
| `c_omaha_game_first_game_system` | `0x1941a00` | `0x19419d0` | 8 | c_game_system_interface |
| `c_omaha_game_last_game_system` | `0x1940750` | `0x1940720` | 8 | c_game_system_interface |
| `c_overlapped_game_system` | `0x1941880` | `0x1941850` | 8 | c_game_system_interface |
| `c_particle_game_system` | `0x19492b0` | `0x1949280` | 8 | c_game_system_interface |
| `c_response_filter_game_system` | `0x1910300` | `0x19102d0` | 8 | c_game_system_interface |
| `c_rumble_game_system` | `0x1940dd0` | `0x1940da0` | 8 | c_game_system_interface |
| `c_sandbox_game_system` | `0x19407b0` | `0x1940780` | 8 | c_game_system_interface |
| `c_saved_game_files_game_system` | `0x19410b0` | `0x1941080` | 8 | c_game_system_interface |
| `c_shared_region_game_system` | `0x1941260` | `0x1941230` | 8 | c_game_system_interface |
| `c_simulated_input_game_system` | `0x1940cb0` | `0x1940c80` | 8 | c_game_system_interface |
| `c_telnet_console_game_system` | `0x19414a0` | `0x1941470` | 8 | c_game_system_interface |
| `c_time_of_day_game_system` | `0x1949690` | `0x1949660` | 8 | c_game_system_interface |
| `c_user_interface_game_system` | `0x1941580` | `0x1941550` | 8 | c_game_system_interface |
| `c_watch_window_game_system` | `0x19409b0` | `0x1940980` | 8 | c_game_system_interface |

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
