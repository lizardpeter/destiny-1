# investment/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `spasaha.investment`  
**Folder path evidence:** `HYPOTHESIS` (folder name is a proposal from RTTI/log-channel clustering, not a recovered path)  
**Role:** items, vendors, talent grids, rewards

## Source files named in the binary

_None recovered (retail build stripped most asserts)._

## Decompiled functions

| VA | name | class | evidence | pseudo-C | role |
|---|---|---|---|---|---|
| `0x28e530` | unlock_expression_test |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`28e530_unlock_expression_test.c`](decompiled/28e530_unlock_expression_test.c) | Evaluates an unlock expression against the flag store. |
| `0x28e590` | unlock_expression_eval |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`28e590_unlock_expression_eval.c`](decompiled/28e590_unlock_expression_eval.c) | Unlock-expression stack VM: op 1 push flag, 2 NOT, 3 OR, 4 AND, 10 push counter, 11 literal, 0x15 negate. |
| `0x5505c0` | activity_unpurchased_prerequisite |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`5505c0_activity_unpurchased_prerequisite.c`](decompiled/5505c0_activity_unpurchased_prerequisite.c) | Evaluates the activity's purchase prerequisites (unlock expressions, 0x28E530) and returns the first unmet one or -1. |

## Classes (109)

Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. Placement in this folder is `HYPOTHESIS` (name-token rule).

| class | typeinfo | vtable | virtual slots | bases |
|---|---|---|---|---|
| `c_activity_complete_incident_metadata_investment_interface` | `0x190a210` | `0x190a200` | 4 | i_incident_metadata_investment |
| `c_investment_account_progression_const_iterator` | `0x190fbc0` | `0x190fb30` | 4 | i_investment_progression_const_iterator |
| `c_investment_activity_fireteam_requirements_client_iterator` | `0x1939b30` | `0x1939a90` | 6 | c_investment_activity_requirements_client_iterator |
| `c_investment_activity_fireteam_requirements_iterator` | `0x190f760` | `0x190f700` | 6 | c_investment_activity_requirements_iterator |
| `c_investment_activity_leader_requirements_client_iterator` | `0x1939b10` | `0x1939a50` | 6 | c_investment_activity_requirements_client_iterator |
| `c_investment_activity_leader_requirements_iterator` | `0x190f740` | `0x190f6d0` | 4 | c_investment_activity_requirements_iterator |
| `c_investment_activity_proxy_game_system` | `0x1940250` | `0x1940200` | 9 | i_investment_game_system |
| `c_investment_activity_requirements_client_iterator` | `0x1939af0` |  |  | c_investment_label_elements_client_iterator<s_investment_activity_requirements_label_shared_definition, s_investment_activity_playing_requirements_shared_definition, s_investment_unlock_flag_expression, s_investment_activity_requirements_label_client_definition, s_investment_activity_playing_requirements_client_definition, s_investment_activity_requirement_client_definition> |
| `c_investment_activity_requirements_iterator` | `0x190f720` |  |  | c_investment_label_elements_iterator<s_investment_activity_requirements_label_shared_definition, s_investment_activity_playing_requirements_shared_definition, s_investment_unlock_flag_expression> |
| `c_investment_activity_reward_tracker_game_system` | `0x193e7c0` | `0x193e770` | 9 | i_investment_game_system |
| `c_investment_activity_selection_manager_game_system` | `0x193e850` | `0x193e800` | 9 | i_investment_game_system |
| `c_investment_activity_unlock_strings_iterator` | `0x1939b50` | `0x1939ad0` | 6 | c_investment_label_elements_iterator<s_investment_activity_unlock_strings_label_client_definition, st_dynamic_array<s_investment_activity_unlock_string_client_definition>, s_investment_activity_unlock_string_client_definition> |
| `c_investment_character_equipment_const_iterator` | `0x190fa50` | `0x190fa00` | 2 |  |
| `c_investment_character_progression_const_iterator` | `0x190fbe0` | `0x190fb60` | 4 | i_investment_progression_const_iterator |
| `c_investment_character_progression_iterator` | `0x190fc60` | `0x190fc30` | 8 | c_investment_character_progression_const_iterator |
| `c_investment_character_usable_equipment_const_iterator` | `0x190fa60` | `0x190fa20` | 2 | c_investment_character_equipment_const_iterator |
| `c_investment_character_usable_equipment_with_default_gear_const_iterator` | `0x190fa80` | `0x190fa40` | 6 | c_investment_character_usable_equipment_const_iterator |
| `c_investment_client_item_repository` | `0x193e8b0` | `0x193e890` | 6 | i_investment_item_repository |
| `c_investment_equipped_item_progression_const_iterator` | `0x190fc00` | `0x190fb90` | 2 | c_investment_character_usable_equipment_const_iterator |
| `c_investment_game_manager_game_system` | `0x193e990` | `0x193e940` | 9 | i_investment_game_system |
| `c_investment_globals_interface` | `0x190d4b0` | `0x190cf40` | 173 | i_investment_globals_interface |
| `c_investment_inventory_active_objective_item_iterator<(e_investment_inventory_bucket_scope_type)0, 340>` | `0x190fb00` | `0x190fae0` | 6 | c_investment_inventory_visible_iterator<(e_investment_inventory_bucket_scope_type)0, 340> |
| `c_investment_inventory_iterator<326>` | `0x193a0b8` | `0x193a0a0` | 5 |  |
| `c_investment_inventory_iterator<340>` | `0x190f7f0` | `0x190fab0` | 3 |  |
| `c_investment_inventory_visible_iterator<(e_investment_inventory_bucket_scope_type)0, 340>` | `0x190f800` | `0x1910140` | 40 | c_investment_inventory_iterator<340> |
| `c_investment_item_loader_game_system` | `0x193eb10` | `0x193eac0` | 9 | i_investment_game_system |
| `c_investment_item_progression_const_iterator<(e_investment_inventory_bucket_scope_type)0, 340>` | `0x190f820` |  |  | c_investment_inventory_visible_iterator<(e_investment_inventory_bucket_scope_type)0, 340> |
| `c_investment_item_progression_iterator<(e_investment_inventory_bucket_scope_type)0, 340>` | `0x190f840` | `0x190f7d0` | 8 | c_investment_item_progression_const_iterator<(e_investment_inventory_bucket_scope_type)0, 340> |
| `c_investment_joinability_manager_game_system` | `0x193f470` | `0x193f400` | 9 | i_investment_game_system |
| `c_investment_label_elements_client_iterator<s_investment_activity_requirements_label_shared_definition, s_investment_activity_playing_requirements_shared_definition, s_investment_unlock_flag_expression, s_investment_activity_requirements_label_client_definition, s_investment_activity_playing_requirements_client_definition, s_investment_activity_requirement_client_definition>` | `0x1939b70` |  |  | c_investment_label_elements_iterator<s_investment_activity_requirements_label_shared_definition, s_investment_activity_playing_requirements_shared_definition, s_investment_unlock_flag_expression> |
| `c_investment_label_elements_iterator<s_investment_activity_requirements_label_shared_definition, s_investment_activity_playing_requirements_shared_definition, s_investment_unlock_flag_expression>` | `0x190f790` |  |  | c_investment_label_iterator<s_investment_activity_requirements_label_shared_definition> |
| `c_investment_label_elements_iterator<s_investment_activity_unlock_strings_label_client_definition, st_dynamic_array<s_investment_activity_unlock_string_client_definition>, s_investment_activity_unlock_string_client_definition>` | `0x1939ba0` |  |  | c_investment_label_iterator<s_investment_activity_unlock_strings_label_client_definition> |
| `c_investment_label_iterator<s_investment_activity_requirements_label_shared_definition>` | `0x190f780` |  |  |  |
| `c_investment_label_iterator<s_investment_activity_unlock_strings_label_client_definition>` | `0x1939b88` |  |  |  |
| `c_investment_latency_record_manager_game_system` | `0x193f600` | `0x193f5b0` | 9 | i_investment_game_system |
| `c_investment_location_manager_game_system` | `0x193f720` | `0x193f6d0` | 9 | i_investment_game_system |
| `c_investment_loot_latency_record_from_incident_updater` | `0x193f680` | `0x193f670` | 4 | i_investment_loot_latency_record_update_interface |
| `c_investment_loot_latency_record_from_loot_state_updater` | `0x193f640` | `0x193f630` | 4 | i_investment_loot_latency_record_update_interface |
| `c_investment_loot_object_manager_game_system` | `0x1940190` | `0x1940140` | 9 | i_investment_game_system |
| `c_investment_peer_subscription_manager_game_system` | `0x193f7b0` | `0x193f760` | 9 | i_investment_game_system |
| `c_investment_peer_subscription_proxy_game_system` | `0x1940350` | `0x1940300` | 9 | i_investment_game_system |
| `c_investment_peer_subscription_proxy_simulation_queue_handler` | `0x1940390` | `0x19402d0` | 3 | c_simulation_queue_element_schematized_definition<s_investment_peer_subscription_state> |
| `c_investment_player_identifier_proxy_game_system` | `0x1940420` | `0x19403d0` | 9 | i_investment_game_system |
| `c_investment_profile_manager_game_system` | `0x193f8d0` | `0x193f880` | 9 | i_investment_game_system |
| `c_investment_roster_game_system` | `0x193fa70` | `0x193fa20` | 9 | i_investment_game_system |
| `c_investment_roster_party_details_game_system` | `0x193fb20` | `0x193fad0` | 9 | i_investment_game_system |
| `c_investment_server_message_response_handler` | `0x193a110` | `0x193a100` | 1 | i_investment_bap_message_queue_callbacks |
| `c_investment_server_object_manager_game_system` | `0x193e5d0` | `0x193e580` | 9 | i_investment_game_system |
| `c_investment_social_presence_game_system` | `0x19404e0` | `0x1940490` | 9 | i_investment_game_system |
| `c_investment_talent_grid_ability_iterator` | `0x1910060` | `0x190ff20` | 4 | c_investment_talent_grid_internal_ability_iterator |
| `c_investment_talent_grid_ability_mod_iterator` | `0x1910040` | `0x190fef0` | 4 | c_investment_talent_grid_internal_ability_iterator |
| `c_investment_talent_grid_const_iterator` | `0x19100b8` |  |  |  |
| `c_investment_talent_grid_internal_ability_iterator` | `0x1910020` | `0x190fec0` | 4 | c_investment_talent_grid_provided_effect_iterator |
| `c_investment_talent_grid_intrinsic_unlock_flag_iterator` | `0x1910080` | `0x190ff50` | 4 | c_investment_talent_grid_provided_effect_iterator |
| `c_investment_talent_grid_intrinsic_unlock_value_iterator` | `0x19100a0` | `0x190ff80` | 4 | c_investment_talent_grid_provided_effect_iterator |
| `c_investment_talent_grid_iterator` | `0x19100f0` | `0x19100e0` | 1 | c_investment_talent_grid_const_iterator |
| `c_investment_talent_grid_perk_iterator` | `0x190ffe0` | `0x190fe60` | 4 | c_investment_talent_grid_provided_effect_iterator |
| `c_investment_talent_grid_provided_effect_iterator` | `0x190ffb0` | `0x190fe00` | 4 |  |
| `c_investment_talent_grid_stat_iterator` | `0x1910000` | `0x190fe90` | 4 | c_investment_talent_grid_provided_effect_iterator |
| `c_investment_talent_grid_step_iterator` | `0x190ffc0` | `0x190fe30` | 4 | c_investment_talent_grid_provided_effect_iterator |
| `c_investment_talent_grid_step_progress_iterator` | `0x193a080` | `0x193a070` | 4 |  |
| `c_investment_translation_manager_game_system` | `0x1940590` | `0x1940540` | 9 | i_investment_game_system |
| `c_investment_ui_trigger_manager_game_system` | `0x193fc40` | `0x193fbf0` | 9 | i_investment_game_system |
| `c_investment_user_manager_game_system` | `0x193fe20` | `0x193fdd0` | 9 | i_investment_game_system |
| `c_investment_user_message_manager_game_system` | `0x193ff90` | `0x193ff40` | 9 | i_investment_game_system |
| `c_investment_world_tag_loader_cache_base<128, (e_world_tag_request_type)1>` | `0x193f1e0` | `0x193f130` | 21 | i_investment_world_tag_loader_cache |
| `c_investment_world_tag_loader_cache_base<1460, (e_world_tag_request_type)1>` | `0x193f3a0` | `0x193f2f0` | 21 | i_investment_world_tag_loader_cache |
| `c_investment_world_tag_loader_cache_base<16, (e_world_tag_request_type)1>` | `0x193f020` | `0x193ef70` | 21 | i_investment_world_tag_loader_cache |
| `c_investment_world_tag_loader_cache_base<340, (e_world_tag_request_type)1>` | `0x193ee60` | `0x193eda0` | 23 | i_investment_world_tag_loader_cache |
| `c_investment_world_tag_loader_cache_base<4, (e_world_tag_request_type)1>` | `0x193ef40` | `0x193ee90` | 21 | i_investment_world_tag_loader_cache |
| `c_investment_world_tag_loader_cache_base<40, (e_world_tag_request_type)1>` | `0x193f2c0` | `0x193f210` | 21 | i_investment_world_tag_loader_cache |
| `c_investment_world_tag_loader_cache_base<768, (e_world_tag_request_type)2>` | `0x193f100` | `0x193f050` | 21 | i_investment_world_tag_loader_cache |
| `c_investment_world_tag_loader_cache_state_simulation_queue_handler` | `0x193ed60` | `0x193ea90` | 3 | c_simulation_queue_element_schematized_definition<s_investment_world_tag_loader_cache_state> |
| `c_investment_world_tag_loader_fill_desired_handles_character_creation` | `0x193ec90` | `0x193ec80` | 1 | i_investment_world_tag_loader_fill_desired |
| `c_investment_world_tag_loader_fill_desired_items_activity_reward_incidents` | `0x193ed10` | `0x193ed00` | 1 | i_investment_world_tag_loader_fill_desired |
| `c_investment_world_tag_loader_fill_desired_items_character_instance` | `0x193eb50` | `0x193eb40` | 1 | i_investment_world_tag_loader_fill_desired |
| `c_investment_world_tag_loader_fill_desired_items_default_gear` | `0x193ec50` | `0x193ec40` | 1 | i_investment_world_tag_loader_fill_desired |
| `c_investment_world_tag_loader_fill_desired_items_peer_view` | `0x193ebd0` | `0x193ebc0` | 1 | i_investment_world_tag_loader_fill_desired |
| `c_investment_world_tag_loader_fill_desired_items_select_character_view` | `0x193ec10` | `0x193ec00` | 1 | i_investment_world_tag_loader_fill_desired |
| `c_investment_world_tag_loader_fill_desired_string_lists_rich_presence` | `0x193ecd0` | `0x193ecc0` | 1 | i_investment_world_tag_loader_fill_desired |
| `c_investment_world_tag_loader_fill_desired_talent_grids_character_instance` | `0x193eb90` | `0x193eb80` | 1 | i_investment_world_tag_loader_fill_desired |
| `c_mock_investment_state_component` | `0x1956ad0` | `0x19569f0` | 21 | c_cui_object_component |
| `c_player_time_incident_metadata_investment_interface` | `0x190b830` | `0x190b820` | 4 | i_incident_metadata_investment |
| `c_racing_lap_complete_incident_metadata_investment_interface` | `0x190bb00` | `0x190baf0` | 4 | i_incident_metadata_investment |
| `c_simulation_queue_investment_activity_proxy_set_activity_state` | `0x1940270` | `0x19401d0` | 3 | c_simulation_queue_element_schematized_definition<s_investment_online_world_controller_activity_state> |
| `c_simulation_queue_investment_game_set_reset_state` | `0x193e9b0` | `0x193e8e0` | 3 | c_simulation_queue_element_schematized_definition<s_investment_game_reset_state> |
| `c_simulation_queue_investment_game_set_update_state` | `0x193e9d0` | `0x193e910` | 3 | c_simulation_queue_element_schematized_definition<s_investment_game_update_state> |
| `c_simulation_queue_investment_local_time_update_definition` | `0x193fe40` | `0x193fd40` | 3 | c_simulation_queue_element_schematized_definition<s_investment_local_time_update> |
| `c_simulation_queue_investment_profile_schedule_high_priority_flush` | `0x193f930` | `0x193f850` | 3 | c_simulation_queue_element_schematized_definition<s_investment_profile_manager_event_schedule_high_priority_flush> |
| `c_simulation_queue_investment_profile_set_account_profile_nondeterministic` | `0x193f8f0` | `0x193f7f0` | 3 | c_simulation_queue_element_schematized_definition<s_investment_profile_manager_event_set_account_profile_nondeterministic_chunk> |
| `c_simulation_queue_investment_profile_set_character_profile_nondeterministic` | `0x193f910` | `0x193f820` | 3 | c_simulation_queue_element_schematized_definition<s_investment_profile_manager_event_set_character_profile_nondeterministic_chunk> |
| `c_simulation_queue_investment_server_object_family_select_character_refresh` | `0x193fe80` | `0x193fda0` | 3 | c_simulation_queue_element_schematized_definition<s_investment_server_object_family_select_character_refresh> |
| `c_simulation_queue_investment_server_object_manager_start_family_replication` | `0x193e5f0` | `0x193e4c0` | 3 | c_simulation_queue_element_schematized_definition<s_investment_server_object_manager_event_start_family_replication> |
| `c_simulation_queue_investment_server_object_manager_stop_family_replication` | `0x193e610` | `0x193e4f0` | 3 | c_simulation_queue_element_schematized_definition<s_investment_server_object_manager_event_stop_family_replication> |
| `c_simulation_queue_investment_server_object_manager_update_family_playing_state` | `0x193e630` | `0x193e520` | 3 | c_simulation_queue_element_schematized_definition<s_investment_server_object_manager_event_update_family_playing_state> |
| `c_simulation_queue_investment_server_object_manager_update_family_record_force_subscription` | `0x193e650` | `0x193e550` | 3 | c_simulation_queue_element_schematized_definition<s_investment_server_object_manager_event_update_family_record_force_subscription> |
| `c_simulation_queue_investment_user_manager_universe_update_definition` | `0x193fe60` | `0x193fd70` | 3 | c_simulation_queue_element_schematized_definition<s_investment_universe_performance_counter_update> |
| `c_world_controller_state_bootflow_investment_signin_handler` | `0x19466b0` | `0x1946660` | 12 | c_world_controller_tiger_base_state_handler |
| `i_incident_metadata_investment` | `0x190a2c8` |  |  |  |
| `i_investment_engine_shim` | `0x1939c68` |  |  |  |
| `i_investment_game_system` | `0x1940118` |  |  |  |
| `i_investment_globals_interface` | `0x190cf18` |  |  |  |
| `i_investment_item_repository` | `0x190dbe0` |  |  |  |
| `i_investment_loot_latency_record_update_interface` | `0x193f698` |  |  |  |
| `i_investment_progression_const_iterator` | `0x190fc50` |  |  |  |
| `i_investment_utility_context` | `0x190dbf0` |  |  |  |
| `i_investment_world_tag_loader_cache` | `0x193ee48` |  |  |  |
| `i_investment_world_tag_loader_fill_desired` | `0x193ed28` |  |  |  |
| `s_investment_utility_context` | `0x190dbc0` | `0x190dad0` | 29 | i_investment_utility_context |

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
