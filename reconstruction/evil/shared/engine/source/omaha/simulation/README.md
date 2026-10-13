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
| `0x3007e0` | simulation_queue_apply |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`3007e0_simulation_queue_apply.c`](decompiled/3007e0_simulation_queue_apply.c) | Applies queued simulation events through the registered callback (g_2689548 = 0xBB4690). |
| `0x300b90` | simulation_queue_insert |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`300b90_simulation_queue_insert.c`](decompiled/300b90_simulation_queue_insert.c) | Enqueues a simulation event unless this machine is a remote client (0x240E60). |
| `0x906f70` | simulation_is_remote_client |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`906f70_simulation_is_remote_client.c`](decompiled/906f70_simulation_is_remote_client.c) | True when this machine is a simulation client (game globals in progress and *g_273DCD8 set); false = local authority. |
| `0xbad260` | simulation_apply_player_update |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`bad260_simulation_apply_player_update.c`](decompiled/bad260_simulation_apply_player_update.c) | Decodes a player-update event and applies it (players apply-added / remove / swap). |
| `0xbb1c10` | simulation_insert_host_event |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`bb1c10_simulation_insert_host_event.c`](decompiled/bb1c10_simulation_insert_host_event.c) | Host message 5 payload -> simulation event 0x13 when this machine is the authority. |
| `0xbb4690` | simulation_event_apply |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`bb4690_simulation_event_apply.c`](decompiled/bb4690_simulation_event_apply.c) | Applies one simulation-queue element by type (1..0x3D), e.g. 0xC player update (0xBAD260). |

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
