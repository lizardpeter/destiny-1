# simulation/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `omaha.simulation`  
**Folder path evidence:** `HYPOTHESIS` (folder name is a proposal from RTTI/log-channel clustering, not a recovered path)  
**Role:** simulation queue, replication, determinism

## Source files named in the binary

_None recovered (retail build stripped most asserts)._

## Decompiled functions

| VA | name | class | evidence | pseudo-C | role |
|---|---|---|---|---|---|
| `0x1071d0` | client_reference_lookup |  | Static decompilation plus d1-native D1_TRACE_SPAWN / gdb runs into activity:in_world (player gets a unit), 2026-10-14 | [`1071d0_client_reference_lookup.c`](decompiled/1071d0_client_reference_lookup.c) | Client reference id {key, i8, index} -> entry {handle, offset, ...}: groups at manager +0xC (count, start, key; stride 0x14, group count +8), entries at +0x520 + index * 0x38 (+ slot * 0x18). |
| `0x119210` | player_entity_definition_identity |  | Static decompilation plus d1-native D1_TRACE_SPAWN / gdb runs into activity:in_world (player gets a unit), 2026-10-14 | [`119210_player_entity_definition_identity.c`](decompiled/119210_player_entity_definition_identity.c) | Entity -> identity block of its definition reference ([+0x208] + [+0x210] = object +0x258: u64 id, u8, i8 @+9). |
| `0x1192b0` | player_entity_definition_info |  | Static decompilation plus d1-native D1_TRACE_SPAWN / gdb runs into activity:in_world (player gets a unit), 2026-10-14 | [`1192b0_player_entity_definition_info.c`](decompiled/1192b0_player_entity_definition_info.c) | Entity handle -> active data of its definition reference (0x1192E0: binding at object +0x1F8/+0x200; the local authority copy +0x290 when the local machine owns it, else the published +0x218). Byte +9 = spawn-ready. |
| `0x1195f0` | player_entity_bind_definition |  | Static decompilation plus d1-native D1_TRACE_SPAWN / gdb runs into activity:in_world (player gets a unit), 2026-10-14 | [`1195f0_player_entity_bind_definition.c`](decompiled/1195f0_player_entity_bind_definition.c) | Binds player simulation entities to type-0xC client references: iterates the type-0xC references (manager +0x2BD4E count) and sets entity +0x50 (0x301C60) to the reference whose id (object at [ref+0x208] + [ref+0x210], i.e. +0x258) equals the given 8-byte id; 0x1293F0 records the entity on the reference (+0x1F0). |
| `0x3007e0` | simulation_queue_apply |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`3007e0_simulation_queue_apply.c`](decompiled/3007e0_simulation_queue_apply.c) | Applies queued simulation events through the registered callback (g_2689548 = 0xBB4690). |
| `0x300b90` | simulation_queue_insert |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`300b90_simulation_queue_insert.c`](decompiled/300b90_simulation_queue_insert.c) | Enqueues a simulation event unless this machine is a remote client (0x240E60). |
| `0x300be0` | simulation_queue_exists |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`300be0_simulation_queue_exists.c`](decompiled/300be0_simulation_queue_exists.c) | True when the simulation queue global (g_2689540) exists. |
| `0x301470` | simulation_player_entity_init |  | Static decompilation plus d1-native D1_TRACE_SPAWN / gdb runs into activity:in_world (player gets a unit), 2026-10-14 | [`301470_simulation_player_entity_init.c`](decompiled/301470_simulation_player_entity_init.c) | Player simulation entity init: copies the 0x38-byte identity (+8..+0x40; +0x18 = binding id), +0x44 index, +0x48 handle, +0x4C player, sets definition +0x50 = -1, +0x54/+0x150/+0x154 = -1. |
| `0x301c60` | player_entity_set_definition |  | Static decompilation plus d1-native D1_TRACE_SPAWN / gdb runs into activity:in_world (player gets a unit), 2026-10-14 | [`301c60_player_entity_set_definition.c`](decompiled/301c60_player_entity_set_definition.c) | Setter: entity +0x50 = definition (type-0xC client reference handle). |
| `0x302640` | simulation_player_entity_create |  | Static decompilation plus d1-native D1_TRACE_SPAWN / gdb runs into activity:in_world (player gets a unit), 2026-10-14 | [`302640_simulation_player_entity_create.c`](decompiled/302640_simulation_player_entity_create.c) | Creates a player simulation entity (pool 0x2689580): init 0x301470 from the player update (id at +0x18 = membership properties @0xA0, else +0x28), then 0x1195F0 binds its definition (+0x50) to the matching type-0xC client reference. |
| `0x34b920` | simulation_apply_global_resource_load |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`34b920_simulation_apply_global_resource_load.c`](decompiled/34b920_simulation_apply_global_resource_load.c) | Applies simulation event 0x4E (global resource load). |
| `0x4044f0` | activity_lifetime_reference_on_data |  | Static decompilation plus d1-native D1_TRACE_SPAWN / gdb runs into activity:in_world (player gets a unit), 2026-10-14 | [`4044f0_activity_lifetime_reference_on_data.c`](decompiled/4044f0_activity_lifetime_reference_on_data.c) | Activity lifetime reference (client reference type 0x10) data handler: copies the published byte (type *0x19B2B18) to +0x1AC, which 0x10C500 reports. |
| `0x404550` | activity_lifetime_reference_publish |  | Static decompilation plus d1-native D1_TRACE_SPAWN / gdb runs into activity:in_world (player gets a unit), 2026-10-14 | [`404550_activity_lifetime_reference_publish.c`](decompiled/404550_activity_lifetime_reference_publish.c) | Activity lifetime reference authority producer: publishes the byte at +0x1AD (type *0x19B2B20). No client code writes +0x1AD. |
| `0x409430` | player_reference_bind_active |  | Static decompilation plus d1-native D1_TRACE_SPAWN / gdb runs into activity:in_world (player gets a unit), 2026-10-14 | [`409430_player_reference_bind_active.c`](decompiled/409430_player_reference_bind_active.c) | Points the reference's bindings: +0x208/+0x210 -> +0x258 (identity), +0x318/+0x320 -> +0x288, +0x1F8/+0x200 -> +0x290 (local authority state) when an entity is bound and 0x108470 == 0 (local authority), else +0x218 (published data). |
| `0x409710` | player_reference_on_data |  | Static decompilation plus d1-native D1_TRACE_SPAWN / gdb runs into activity:in_world (player gets a unit), 2026-10-14 | [`409710_player_reference_on_data.c`](decompiled/409710_player_reference_on_data.c) | Type-0xC client reference data handler (class table 0x19A35C0, event hash 0x3088896A, data type 0x808022A5): copies 0x78 bytes to object +0x218, rebinds entities when the id at +0x258 changes (0x1195F0 old and new), refreshes. Used by d1-native's spawn bypass to publish the player's id. |
| `0x4098e0` | player_reference_build_authority_state |  | Static decompilation plus d1-native D1_TRACE_SPAWN / gdb runs into activity:in_world (player gets a unit), 2026-10-14 | [`4098e0_player_reference_build_authority_state.c`](decompiled/4098e0_player_reference_build_authority_state.c) | Authority producer for the type-0xC reference (event hash 0x24D7DDECB): fills the local state at +0x290 (slice-set value, +0x298 valid when < 0x80 and not 0x9141F0, +0x299 spawn-ready when +0x298, published i32 +0x250 == player byte +0x738 (+0x2C8) and 0x77B920), +0x29A..+0x2CE from player data; remote authority copies the owner's state instead. |
| `0x412800` | player_spawning_update |  | Static decompilation plus d1-native D1_TRACE_SPAWN / gdb runs into activity:in_world (player gets a unit), 2026-10-14 | [`412800_player_spawning_update.c`](decompiled/412800_player_spawning_update.c) | Player spawning update: per player simulation entity (table 0x2689580) checks can_spawn (0x415700, call sites 0x412BFA and 0x412DCF), runs the respawn timer, picks a spawn location (0x3DD9C0 spawn tag, candidates via 0x415170) and creates the body from the player configuration (body tag *0x66AE60(player) at player data +0x1660; object create 0x308CA0 at 0x413A6F). No body tag = no unit. |
| `0x415700` | player_can_spawn |  | Static decompilation plus d1-native D1_TRACE_SPAWN / gdb runs into activity:in_world (player gets a unit), 2026-10-14 | [`415700_player_can_spawn.c`](decompiled/415700_player_can_spawn.c) | Spawn gate for a player simulation entity: slice-set gate (0x3430B0/0x3455E0/0x345610/0x12D730), entity definition data valid (0x1192B0, byte +9 = spawn-ready flag of the type-0xC reference's active data), activity lifetime state 3 or 6 (0x10C500, else 'can't spawn due to the current activity lifetime state'), tags 0x240840/0x240880 +0x1C, the reference's data blocks (0x3F3CE0/0x3F3DE0) and 0x3D5F30. |
| `0x66ae90` | player_set_configuration |  | Static decompilation plus d1-native D1_TRACE_SPAWN / gdb runs into activity:in_world (player gets a unit), 2026-10-14 | [`66ae90_player_set_configuration.c`](decompiled/66ae90_player_set_configuration.c) | Installs a player configuration at player data +0x1660 (0x104F3A0), resetting dependent state when the body changes. |
| `0x906f70` | simulation_is_remote_client |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`906f70_simulation_is_remote_client.c`](decompiled/906f70_simulation_is_remote_client.c) | True when this machine is a simulation client (game globals in progress and *g_273DCD8 set); false = local authority. |
| `0x911850` | player_apply_character_data |  | Static decompilation plus d1-native D1_TRACE_SPAWN / gdb runs into activity:in_world (player gets a unit), 2026-10-14 | [`911850_player_apply_character_data.c`](decompiled/911850_player_apply_character_data.c) | Applies a character data cache entry to a player: player +0x613 \|= 2, copies the character data to +0x850 (0x104A2B0), builds the configuration (0x912240) and installs it (0x73DAC0 -> 0x66AE90 -> player data +0x1660). |
| `0x912240` | player_configuration_build |  | Static decompilation plus d1-native D1_TRACE_SPAWN / gdb runs into activity:in_world (player gets a unit), 2026-10-14 | [`912240_player_configuration_build.c`](decompiled/912240_player_configuration_build.c) | Builds the player configuration (0x1098 bytes, type *0x19B1BA0) from the player's character data (+0x850 race/gender/class, +0x85C body tag, appearance, gear) when 0x52B090, 0x549510 and player +0x613 bit 1 hold. |
| `0xbad260` | simulation_apply_player_update |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`bad260_simulation_apply_player_update.c`](decompiled/bad260_simulation_apply_player_update.c) | Decodes a player-update event and applies it (players apply-added / remove / swap). |
| `0xbb1c10` | simulation_insert_host_event |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`bb1c10_simulation_insert_host_event.c`](decompiled/bb1c10_simulation_insert_host_event.c) | Host message 5 payload -> simulation event 0x13 when this machine is the authority. |
| `0xbb4690` | simulation_event_apply |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`bb4690_simulation_event_apply.c`](decompiled/bb4690_simulation_event_apply.c) | Applies one simulation-queue element by type (1..0x3D), e.g. 0xC player update (0xBAD260). |
| `0x100cb80` | client_reference_iterate |  | Static decompilation plus d1-native D1_TRACE_SPAWN / gdb runs into activity:in_world (player gets a unit), 2026-10-14 | [`100cb80_client_reference_iterate.c`](decompiled/100cb80_client_reference_iterate.c) | Client reference iterator {manager, i16 index, i32 type, bool}: type registry +0x2BD1C {start, count}, index list +0x2A51C, entry +0x520 + e * 0x38 -> {handle, offset}. |

## Classes (142)

Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. Placement in this folder is `HYPOTHESIS` (name-token rule).

| class | typeinfo | vtable | virtual slots | bases |
|---|---|---|---|---|
| `c_cinematic_video_playback_complete_simulation_queue_definition` | `0x1937e00` | `0x1937de0` | 3 | c_simulation_queue_element_schematized_definition<s_cinematic_video_playback_complete_simulation_queue_data> |
| `c_determinism_engine_game_system` | `0x1909630` | `0x1909600` | 8 | c_game_system_interface |
| `c_network_channel_simulation_gatekeeper` | `0x196b1c0` | `0x196b170` | 9 | c_network_channel_client |
| `c_physics_simulation_finished_listener` | `0x1908a50` | `0x1908a30` | 6 | hkpWorldPostSimulationListener |
| `c_simulation_action_weapon_fire_debug_event_definition` | `0x196fb80` | `0x196fb00` | 15 | c_simulation_schematized_event_definition<s_simulation_weapon_fire_debug_event_data> |
| `c_simulation_action_weapon_fire_event_definition` | `0x196fad0` | `0x196fa50` | 15 | c_simulation_schematized_event_definition<s_simulation_weapon_fire_event_data> |
| `c_simulation_biped_debug_teleport_event_definition` | `0x196f050` | `0x196efd0` | 15 | c_simulation_schematized_event_definition<s_simulation_biped_debug_teleport_event_data> |
| `c_simulation_biped_throw_initiate_event_definition` | `0x196efa0` | `0x196ef20` | 15 | c_simulation_schematized_event_definition<s_simulation_biped_throw_initiate_event_data> |
| `c_simulation_bulk_projectile_impact_damage_caused_event_definition` | `0x1938070` | `0x1937ff0` | 15 | c_simulation_schematized_event_definition<s_simulation_bulk_projectile_impact_damage_caused_event_data> |
| `c_simulation_channel_manager` | `0x196e300` | `0x196e2b0` | 9 | c_network_channel_owner |
| `c_simulation_console_command_event_definition` | `0x196eec0` | `0x196ee40` | 15 | c_simulation_schematized_event_definition<s_simulation_console_command_event_data> |
| `c_simulation_damage_caused_event_definition` | `0x1938120` | `0x19380a0` | 15 | c_simulation_schematized_event_definition<s_simulation_damage_caused_event_data> |
| `c_simulation_debug_update_client_interface` | `0x196e3a0` |  |  |  |
| `c_simulation_definition_table_allocator` | `0x196e270` | `0x196e250` | 3 | c_allocation_interface |
| `c_simulation_entity_definition` | `0x196e320` |  |  |  |
| `c_simulation_event_definition` | `0x1938348` |  |  |  |
| `c_simulation_game_system` | `0x196e220` | `0x196e1f0` | 8 | c_game_system_interface |
| `c_simulation_impact_damage_caused_event_definition` | `0x1937fc0` | `0x1937f40` | 15 | c_simulation_schematized_event_definition<s_simulation_impact_damage_caused_event_data> |
| `c_simulation_melee_strike_event_definition` | `0x1943210` | `0x1943190` | 15 | c_simulation_schematized_event_definition<s_simulation_melee_strike_event_data> |
| `c_simulation_player_broadcast_entity_definition` | `0x196f520` | `0x196f420` | 30 | c_simulation_entity_definition |
| `c_simulation_player_set_camera_target_event_definition` | `0x196f200` | `0x196f180` | 15 | c_simulation_schematized_event_definition<s_simulation_player_set_camera_target_event_data> |
| `c_simulation_player_set_group_recovery_granting_event_definition` | `0x196f150` | `0x196f0d0` | 15 | c_simulation_schematized_event_definition<s_simulation_player_set_group_recovery_granting_event_data> |
| `c_simulation_player_transition_alarm_event_definition` | `0x196f2b0` | `0x196f230` | 15 | c_simulation_schematized_event_definition<s_simulation_player_transition_alarm_event_data> |
| `c_simulation_predicted_death_event_definition` | `0x19381d0` | `0x1938150` | 15 | c_simulation_schematized_event_definition<s_simulation_predicted_death_event_data> |
| `c_simulation_predicted_hard_ping_event_definition` | `0x1938280` | `0x1938200` | 15 | c_simulation_schematized_event_definition<s_simulation_predicted_hard_ping_event_data> |
| `c_simulation_quality_debug_update_client` | `0x196e380` | `0x196e340` | 7 | c_simulation_debug_update_client_interface |
| `c_simulation_queue_cheat_drop_object_definition` | `0x196ea10` | `0x196e790` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_queue_cheat_drop_object_data> |
| `c_simulation_queue_cheat_hop_on_object_definition` | `0x196ea30` | `0x196e7c0` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_queue_cheat_hop_on_object_data> |
| `c_simulation_queue_cinematic_batch_request_definition` | `0x1944ed0` | `0x1944e20` | 3 | c_simulation_queue_element_schematized_definition<s_world_controller_cinematics_batch_request> |
| `c_simulation_queue_cinematic_cache_gear_definition` | `0x1944f30` | `0x1944eb0` | 3 | c_simulation_queue_element_schematized_definition<s_world_controller_cinematics_cache_gear> |
| `c_simulation_queue_cinematic_camera_emote_action_definition` | `0x196ea90` | `0x196e850` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_queue_cinematic_camera_emote_action> |
| `c_simulation_queue_cinematic_object_definition` | `0x1944f10` | `0x1944e80` | 3 | c_simulation_queue_element_schematized_definition<s_world_controller_cinematics_object_request> |
| `c_simulation_queue_cinematic_start_stop_definition` | `0x1944ef0` | `0x1944e50` | 3 | c_simulation_queue_element_schematized_definition<s_world_controller_cinematics_start_stop_request> |
| `c_simulation_queue_element_schematized_definition<s_activity_cinematic_skip_payload>` | `0x1935d30` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_activity_objectives_abandon_current_payload>` | `0x1936250` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_cinematic_video_playback_complete_simulation_queue_data>` | `0x1937e20` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_end_game_payload>` | `0x194b3f0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_entity_authority_change_payload>` | `0x196e4f0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_ghost_dialog_transmat_event>` | `0x1942fd0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_investment_game_reset_state>` | `0x193ea00` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_investment_game_update_state>` | `0x193ea20` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_investment_local_time_update>` | `0x193feb0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_investment_online_world_controller_activity_state>` | `0x1940290` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_investment_peer_subscription_state>` | `0x1940370` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_investment_profile_manager_event_schedule_high_priority_flush>` | `0x193f9a0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_investment_profile_manager_event_set_account_profile_nondeterministic_chunk>` | `0x193f960` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_investment_profile_manager_event_set_character_profile_nondeterministic_chunk>` | `0x193f980` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_investment_server_object_family_select_character_refresh>` | `0x193fef0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_investment_server_object_manager_event_start_family_replication>` | `0x193e690` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_investment_server_object_manager_event_stop_family_replication>` | `0x193e6b0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_investment_server_object_manager_event_update_family_playing_state>` | `0x193e6d0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_investment_server_object_manager_event_update_family_record_force_subscription>` | `0x193e6f0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_investment_ui_trigger_manager_nondeterministic_state>` | `0x193fcf0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_investment_ui_trigger_manager_ui_event>` | `0x193fcd0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_investment_universe_performance_counter_update>` | `0x193fed0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_investment_world_tag_loader_cache_state>` | `0x193ed40` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_join_target_player_definition>` | `0x193f490` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_network_quality_tracker_update_payload>` | `0x1912430` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_player_is_local_fireteam_leader_data>` | `0x196ed40` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_player_resurrection_payload>` | `0x1936fb0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_player_speaking_data>` | `0x196ed20` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_machine_update>` | `0x196edd0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_client_advance_replication_epoch_data>` | `0x196eb60` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_client_entity_slots_allocation_data>` | `0x196ec20` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_client_global_state_data>` | `0x196eb80` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_client_incident_data>` | `0x196ebc0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_client_join_result_data>` | `0x196ebe0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_client_membership_data>` | `0x196ec00` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_client_world_globals_state_data>` | `0x196eba0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_manager_instance_create_client>` | `0x196ec60` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_manager_instance_dispose>` | `0x196ec80` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_manager_instance_start>` | `0x196ec40` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_queue_cheat_drop_object_data>` | `0x196ece0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_queue_cheat_hop_on_object_data>` | `0x196ed00` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_queue_cinematic_camera_emote_action>` | `0x196ed60` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_queue_cui_deterministic_globals_update_data>` | `0x1951af0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_queue_facet_notify_prepare_failure_payload>` | `0x196f6b0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_queue_global_status_event_data>` | `0x196ecc0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_queue_slice_set_transition_action>` | `0x196eca0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_queue_user_interface_voice_notification_payload>` | `0x194cac0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_simulation_queue_voice_incident_payload>` | `0x196c440` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_ui_nux_screen_change_event>` | `0x1942810` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_ui_nux_toast_result>` | `0x19427f0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_ui_vendor_dialogue_action>` | `0x19698d0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_world_controller_cinematics_batch_request>` | `0x1944f70` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_world_controller_cinematics_cache_gear>` | `0x1944fd0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_world_controller_cinematics_object_request>` | `0x1944fb0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition<s_world_controller_cinematics_start_stop_request>` | `0x1944f90` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_element_schematized_definition_base_type` | `0x1912420` |  |  |  |
| `c_simulation_queue_end_game_definition` | `0x194b3d0` | `0x194b3b0` | 3 | c_simulation_queue_element_schematized_definition<s_end_game_payload> |
| `c_simulation_queue_entity_authority_change_definition` | `0x196e480` | `0x196e420` | 3 | c_simulation_queue_element_schematized_definition<s_entity_authority_change_payload> |
| `c_simulation_queue_entity_claim_authority_definition` | `0x196e460` | `0x196e3f0` | 3 | c_simulation_queue_mutable_element_schematized_definition<s_entity_claim_authority_payload> |
| `c_simulation_queue_entity_handoff_definition` | `0x196e440` | `0x196e3c0` | 3 | c_simulation_queue_mutable_element_schematized_definition<s_entity_handoff_payload> |
| `c_simulation_queue_facet_notify_prepare_failure` | `0x196f690` | `0x196f550` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_queue_facet_notify_prepare_failure_payload> |
| `c_simulation_queue_ghost_dialog_transmat_event_definition` | `0x1942fb0` | `0x1942f90` | 3 | c_simulation_queue_element_schematized_definition<s_ghost_dialog_transmat_event> |
| `c_simulation_queue_global_status_definition` | `0x196e9f0` | `0x196e760` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_queue_global_status_event_data> |
| `c_simulation_queue_join_target_player_definition` | `0x193f450` | `0x193f3d0` | 3 | c_simulation_queue_element_schematized_definition<s_join_target_player_definition> |
| `c_simulation_queue_machine_update_definition` | `0x196edb0` | `0x196ed90` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_machine_update> |
| `c_simulation_queue_mutable_element_schematized_definition<s_entity_claim_authority_payload>` | `0x196e4d0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_mutable_element_schematized_definition<s_entity_handoff_payload>` | `0x196e4b0` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_mutable_element_schematized_definition<s_simulation_queue_activity_client_purge_data>` | `0x196eb40` |  |  | c_simulation_queue_element_schematized_definition_base_type |
| `c_simulation_queue_network_quality_tracker_update_definition` | `0x1912400` | `0x19123e0` | 3 | c_simulation_queue_element_schematized_definition<s_network_quality_tracker_update_payload> |
| `c_simulation_queue_player_is_local_fireteam_leader_definition` | `0x196ea70` | `0x196e820` | 3 | c_simulation_queue_element_schematized_definition<s_player_is_local_fireteam_leader_data> |
| `c_simulation_queue_player_resurrection_definition` | `0x1936f60` | `0x1936f00` | 3 | c_simulation_queue_element_schematized_definition<s_player_resurrection_payload> |
| `c_simulation_queue_player_speaking_definition` | `0x196ea50` | `0x196e7f0` | 3 | c_simulation_queue_element_schematized_definition<s_player_speaking_data> |
| `c_simulation_queue_send_user_interface_voice_notification_definition` | `0x194caa0` | `0x194ca80` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_queue_user_interface_voice_notification_payload> |
| `c_simulation_queue_ui_nux_screen_change_event_definition` | `0x19427c0` | `0x1942780` | 3 | c_simulation_queue_element_schematized_definition<s_ui_nux_screen_change_event> |
| `c_simulation_queue_ui_nux_toast_result_definition` | `0x19427a0` | `0x1942750` | 3 | c_simulation_queue_element_schematized_definition<s_ui_nux_toast_result> |
| `c_simulation_queue_ui_trigger_manager_nondeterministic_state` | `0x193fca0` | `0x193fbc0` | 3 | c_simulation_queue_element_schematized_definition<s_investment_ui_trigger_manager_nondeterministic_state> |
| `c_simulation_queue_ui_trigger_manager_ui_clear_event` | `0x193fc80` | `0x193fb90` | 3 | c_simulation_queue_element_schematized_definition<s_investment_ui_trigger_manager_ui_event> |
| `c_simulation_queue_ui_trigger_manager_ui_success_event` | `0x193fc60` | `0x193fb60` | 3 | c_simulation_queue_element_schematized_definition<s_investment_ui_trigger_manager_ui_event> |
| `c_simulation_queue_ui_vendor_dialogue_action_definition` | `0x19698b0` | `0x1969890` | 3 | c_simulation_queue_element_schematized_definition<s_ui_vendor_dialogue_action> |
| `c_simulation_refereed_death_event_definition` | `0x1938330` | `0x19382b0` | 15 | c_simulation_schematized_event_definition<s_simulation_refereed_death_event_data> |
| `c_simulation_schematized_event_definition<s_simulation_biped_debug_teleport_event_data>` | `0x196f090` |  |  | c_simulation_event_definition |
| `c_simulation_schematized_event_definition<s_simulation_biped_throw_initiate_event_data>` | `0x196f070` |  |  | c_simulation_event_definition |
| `c_simulation_schematized_event_definition<s_simulation_bulk_projectile_impact_damage_caused_event_data>` | `0x1938380` |  |  | c_simulation_event_definition |
| `c_simulation_schematized_event_definition<s_simulation_console_command_event_data>` | `0x196eee0` |  |  | c_simulation_event_definition |
| `c_simulation_schematized_event_definition<s_simulation_damage_caused_event_data>` | `0x19383a0` |  |  | c_simulation_event_definition |
| `c_simulation_schematized_event_definition<s_simulation_event_incident_data>` | `0x196f3f0` |  |  | c_simulation_event_definition |
| `c_simulation_schematized_event_definition<s_simulation_impact_damage_caused_event_data>` | `0x1938360` |  |  | c_simulation_event_definition |
| `c_simulation_schematized_event_definition<s_simulation_melee_strike_event_data>` | `0x1943230` |  |  | c_simulation_event_definition |
| `c_simulation_schematized_event_definition<s_simulation_player_set_camera_target_event_data>` | `0x196f2f0` |  |  | c_simulation_event_definition |
| `c_simulation_schematized_event_definition<s_simulation_player_set_group_recovery_granting_event_data>` | `0x196f2d0` |  |  | c_simulation_event_definition |
| `c_simulation_schematized_event_definition<s_simulation_player_transition_alarm_event_data>` | `0x196f310` |  |  | c_simulation_event_definition |
| `c_simulation_schematized_event_definition<s_simulation_predicted_death_event_data>` | `0x19383c0` |  |  | c_simulation_event_definition |
| `c_simulation_schematized_event_definition<s_simulation_predicted_hard_ping_event_data>` | `0x19383e0` |  |  | c_simulation_event_definition |
| `c_simulation_schematized_event_definition<s_simulation_refereed_death_event_data>` | `0x1938400` |  |  | c_simulation_event_definition |
| `c_simulation_schematized_event_definition<s_simulation_spawn_orbs_event_data>` | `0x1942c60` |  |  | c_simulation_event_definition |
| `c_simulation_schematized_event_definition<s_simulation_weapon_empty_click_event_data>` | `0x196fd60` |  |  | c_simulation_event_definition |
| `c_simulation_schematized_event_definition<s_simulation_weapon_fire_debug_event_data>` | `0x196fd20` |  |  | c_simulation_event_definition |
| `c_simulation_schematized_event_definition<s_simulation_weapon_fire_event_data>` | `0x196fd00` |  |  | c_simulation_event_definition |
| `c_simulation_schematized_event_definition<s_simulation_weapon_reload_event_data>` | `0x196fd40` |  |  | c_simulation_event_definition |
| `c_simulation_sobject_entity_definition` | `0x196f670` | `0x196f580` | 32 | c_simulation_entity_definition |
| `c_simulation_sobject_message_event_definition` | `0x196f750` | `0x196f6e0` | 16 | c_simulation_event_definition |
| `c_simulation_spawn_orbs_event_definition` | `0x1942c40` | `0x1942bc0` | 15 | c_simulation_schematized_event_definition<s_simulation_spawn_orbs_event_data> |
| `c_simulation_squad_entity_definition` | `0x196f880` | `0x196f790` | 32 | c_simulation_entity_definition |
| `c_simulation_test_entity_definition` | `0x196f9a0` | `0x196f8b0` | 32 | c_simulation_entity_definition |
| `c_simulation_view_telemetry_provider_interface` | `0x1943f68` |  |  |  |
| `c_simulation_view_telemetry_provider_omaha` | `0x1943f50` | `0x1943f30` | 6 | c_simulation_view_telemetry_provider_interface |
| `c_simulation_weapon_empty_click_event_definition` | `0x196fce0` | `0x196fc60` | 15 | c_simulation_schematized_event_definition<s_simulation_weapon_empty_click_event_data> |
| `c_simulation_weapon_reload_event_definition` | `0x196fc30` | `0x196fbb0` | 15 | c_simulation_schematized_event_definition<s_simulation_weapon_reload_event_data> |
| `c_simulation_weapons_game_system` | `0x196fa20` | `0x196f9f0` | 8 | c_game_system_interface |

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
