# world_controller/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `omaha.world_controller`  
**Folder path evidence:** `HYPOTHESIS` (folder name is a proposal from RTTI/log-channel clustering, not a recovered path)  
**Role:** activity/state/slice_set/matchmaking managers, bootflow (log 'world_controller:*')

## Source files named in the binary

_None recovered (retail build stripped most asserts)._

## Decompiled functions

_None yet._

## Classes (87)

Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. Placement in this folder is `HYPOTHESIS` (name-token rule).

| class | typeinfo | vtable | virtual slots | bases |
|---|---|---|---|---|
| `c_activity_client` | `0x1910590` | `0x1910400` | 10 | i_activity_client_endpoint_interface, i_activity_message_recipient_interface @+0x8 |
| `c_activity_client_messaging_interface_bap::c_activity_host_transport_address_resolver` | `0x1941be0` | `0x1941bd0` | 1 | i_investment_bap_message_queue_callbacks |
| `c_activity_engine_shim` | `0x19360e8` |  |  |  |
| `c_activity_fade_game_system` | `0x1935de0` | `0x1935d90` | 9 | i_activity_game_system |
| `c_activity_game_system` | `0x19370c0` | `0x1937070` | 9 | i_activity_game_system |
| `c_activity_loader` | `0x1914c70` | `0x1914c40` | 8 | c_game_system_interface |
| `c_activity_quarantine_system` | `0x1936e70` | `0x1936e20` | 9 | i_activity_game_system |
| `c_activity_scoreboard_game_system` | `0x1906a50` | `0x1906a20` | 8 | c_game_system_interface |
| `c_activity_timer_client_interface` | `0x1906b40` | `0x1906b30` | 4 | c_activity_timer_interface_base |
| `c_activity_timer_interface_base` | `0x1906b58` |  |  |  |
| `c_bungie_matchmaking_service` | `0x1942520` | `0x1942470` | 24 | i_online_matchmaking_interface |
| `c_editor_world_controller` | `0x1944ce0` | `0x1944c80` | 11 | c_world_controller_interface |
| `c_feature_condition_matches_activity_type` | `0x190f960` | `0x190f8b0` | 1 | i_feature_condition |
| `c_feature_condition_matches_exact_activity` | `0x190f980` | `0x190f8d0` | 1 | i_feature_condition |
| `c_mock_activity_vendor_list_component` | `0x19568a0` | `0x19567c0` | 21 | c_cui_object_component |
| `c_network_session_parameter_activity` | `0x196d6b0` | `0x196d600` | 20 | c_generic_network_session_parameter_data<s_activity_information> |
| `c_network_session_parameter_activity_host` | `0x196db50` | `0x196daa0` | 20 | c_generic_network_session_parameter_data<s_activity_host_connection_information> |
| `c_network_session_parameter_desired_activity` | `0x196d970` | `0x196d8c0` | 20 | c_generic_network_session_parameter_data<s_desired_activity_information> |
| `c_network_session_parameter_desired_roster_join_activity` | `0x196d890` | `0x196d7e0` | 20 | c_generic_network_session_parameter_data<s_desired_roster_join_activity> |
| `c_network_session_parameter_world_controller_goal` | `0x196de30` | `0x196dd80` | 20 | c_generic_network_session_parameter_data<s_network_session_world_controller_goal> |
| `c_omaha_world_controller_shim` | `0x194b610` | `0x194b5e0` | 8 | c_omaha_world_controller_shim_interface |
| `c_omaha_world_controller_shim_interface` | `0x194b630` |  |  |  |
| `c_online_world_controller` | `0x19454e0` | `0x1945480` | 11 | c_world_controller_interface |
| `c_online_world_controller_ui_nagging_prompt_result_handler` | `0x19458c0` | `0x19458b0` | 4 | i_online_world_controller_ui_dialog_result_handler |
| `c_orbit_recall_handler` | `0x195be00` | `0x195bd20` | 21 | c_cui_object_component |
| `c_orbiting_camera` | `0x194ac30` | `0x194ab80` | 24 | c_camera |
| `c_playback_activity_endpoint` | `0x1944dc0` | `0x1944d70` | 9 | i_activity_client_endpoint_interface |
| `c_simulation_queue_activity_cinematic_skip_current_definition` | `0x1935d10` | `0x1935cf0` | 3 | c_simulation_queue_element_schematized_definition<s_activity_cinematic_skip_payload> |
| `c_simulation_queue_activity_client_advance_replication_epoch_definition` | `0x196e890` | `0x196e550` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_client_advance_replication_epoch_data> |
| `c_simulation_queue_activity_client_entity_slots_allocation_definition` | `0x196e950` | `0x196e670` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_client_entity_slots_allocation_data> |
| `c_simulation_queue_activity_client_global_state_definition` | `0x196e8b0` | `0x196e580` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_client_global_state_data> |
| `c_simulation_queue_activity_client_join_result_definition` | `0x196e910` | `0x196e610` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_client_join_result_data> |
| `c_simulation_queue_activity_client_membership_definition` | `0x196e930` | `0x196e640` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_client_membership_data> |
| `c_simulation_queue_activity_client_purge_definition` | `0x196e870` | `0x196e520` | 3 | c_simulation_queue_mutable_element_schematized_definition<s_simulation_queue_activity_client_purge_data> |
| `c_simulation_queue_activity_client_world_globals_state_definition` | `0x196e8d0` | `0x196e5b0` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_client_world_globals_state_data> |
| `c_simulation_queue_activity_manager_instance_create_client_definition` | `0x196e990` | `0x196e6d0` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_manager_instance_create_client> |
| `c_simulation_queue_activity_manager_instance_dispose_definition` | `0x196e9b0` | `0x196e700` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_manager_instance_dispose> |
| `c_simulation_queue_activity_manager_instance_start_definition` | `0x196e970` | `0x196e6a0` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_manager_instance_start> |
| `c_simulation_queue_activity_objective_abandon_current_definition` | `0x1936230` | `0x1936210` | 3 | c_simulation_queue_element_schematized_definition<s_activity_objectives_abandon_current_payload> |
| `c_simulation_queue_slice_set_transition_definition` | `0x196e9d0` | `0x196e730` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_queue_slice_set_transition_action> |
| `c_slice_set_loader` | `0x1914d30` | `0x1914d00` | 8 | c_game_system_interface |
| `c_world_controller_engine_interface` | `0x1944cf8` |  |  |  |
| `c_world_controller_interface` | `0x1944d10` |  |  | c_world_controller_engine_interface |
| `c_world_controller_omaha_hook_game_system` | `0x1940870` | `0x1940840` | 8 | c_game_system_interface |
| `c_world_controller_state_activity_in_world_handler` | `0x1945b20` | `0x1945ad0` | 12 | c_world_controller_tiger_base_state_handler |
| `c_world_controller_state_activity_initial_slice_set_loading_handler` | `0x1945aa0` | `0x1945a50` | 12 | c_world_controller_tiger_base_state_handler |
| `c_world_controller_state_activity_physics_join_handler` | `0x1945ba0` | `0x1945b50` | 12 | c_world_controller_tiger_base_state_handler |
| `c_world_controller_state_activity_watch_video_handler` | `0x1945c20` | `0x1945bd0` | 12 | c_world_controller_tiger_base_state_handler |
| `c_world_controller_state_bootflow_account_signin_handler` | `0x1945d40` | `0x1945c50` | 14 | c_world_controller_tiger_base_state_handler, i_online_world_controller_ui_boot_flow_context @+0x30 |
| `c_world_controller_state_bootflow_bootload_handler` | `0x1945e80` | `0x1945e30` | 12 | c_world_controller_tiger_base_state_handler |
| `c_world_controller_state_bootflow_confirm_account_transfer_handler` | `0x1945ff0` | `0x1945ee0` | 13 | c_world_controller_tiger_base_state_handler, i_online_world_controller_ui_boot_flow_context @+0x30, i_online_world_controller_ui_dialog_result_handler @+0x38 |
| `c_world_controller_state_bootflow_content_check_handler` | `0x19460a0` | `0x1946050` | 12 | c_world_controller_tiger_base_state_handler |
| `c_world_controller_state_bootflow_content_install_handler` | `0x19461b0` | `0x19460d0` | 12 | c_world_controller_tiger_base_state_handler, i_online_world_controller_ui_boot_flow_context @+0x30 |
| `c_world_controller_state_bootflow_email_handler` | `0x1946310` | `0x1946200` | 13 | c_world_controller_tiger_base_state_handler, i_online_world_controller_ui_boot_flow_context @+0x30, i_online_world_controller_ui_dialog_result_handler @+0x38 |
| `c_world_controller_state_bootflow_enumerate_content_rights_handler` | `0x19463c0` | `0x1946370` | 12 | c_world_controller_tiger_base_state_handler |
| `c_world_controller_state_bootflow_eula_handler` | `0x19464e0` | `0x19463f0` | 13 | c_world_controller_tiger_base_state_handler, i_online_world_controller_ui_boot_flow_context @+0x30 |
| `c_world_controller_state_bootflow_intro_screen_display_handler` | `0x1946610` | `0x1946530` | 11 | c_world_controller_tiger_base_state_handler, i_online_world_controller_ui_boot_flow_context @+0x30 |
| `c_world_controller_state_bootflow_media_check_handler` | `0x1946730` | `0x19466e0` | 12 | c_world_controller_tiger_base_state_handler |
| `c_world_controller_state_bootflow_package_registration_handler` | `0x19467e0` | `0x1946790` | 12 | c_world_controller_tiger_base_state_handler |
| `c_world_controller_state_bootflow_platform_account_warnings_handler` | `0x1946900` | `0x1946880` | 12 | c_world_controller_tiger_base_state_handler, i_online_world_controller_ui_dialog_result_handler @+0x30 |
| `c_world_controller_state_bootflow_platform_signin_handler` | `0x1946a60` | `0x1946950` | 13 | c_world_controller_tiger_base_state_handler, i_online_world_controller_ui_boot_flow_context @+0x30, i_online_world_controller_ui_dialog_result_handler @+0x38 |
| `c_world_controller_state_bootflow_prepare_for_orbit_handler` | `0x1946b10` | `0x1946ac0` | 12 | c_world_controller_tiger_base_state_handler |
| `c_world_controller_state_bootflow_profile_setup_handler` | `0x1946c30` | `0x1946b40` | 13 | c_world_controller_tiger_base_state_handler, i_online_world_controller_ui_boot_flow_context @+0x30 |
| `c_world_controller_state_bootflow_queuing_handler` | `0x1946d80` | `0x1946c80` | 15 | c_world_controller_tiger_base_state_handler, i_online_world_controller_ui_boot_flow_context @+0x30 |
| `c_world_controller_state_bootflow_start_handler` | `0x1946eb0` | `0x1946dd0` | 11 | c_world_controller_tiger_base_state_handler, i_online_world_controller_ui_boot_flow_context @+0x30 |
| `c_world_controller_state_bootflow_upsell_handler` | `0x1946fd0` | `0x1946f00` | 10 | c_world_controller_tiger_base_state_handler, i_online_world_controller_ui_boot_flow_context @+0x30 |
| `c_world_controller_state_character_prologue_handler` | `0x1947070` | `0x1947020` | 12 | c_world_controller_tiger_base_state_handler |
| `c_world_controller_state_character_signin_handler` | `0x1947190` | `0x19470a0` | 13 | c_world_controller_tiger_base_state_handler, i_online_world_controller_ui_boot_flow_context @+0x30 |
| `c_world_controller_state_cleanup_handler` | `0x1947260` | `0x19471e0` | 12 | c_world_controller_tiger_base_state_handler, i_online_world_controller_ui_dialog_result_handler @+0x30 |
| `c_world_controller_state_handler` | `0x1945a28` |  |  |  |
| `c_world_controller_state_setup_activity_host_setup_handler` | `0x1947300` | `0x19472b0` | 12 | c_world_controller_tiger_base_state_handler |
| `c_world_controller_state_setup_activity_session_creation_handler` | `0x1947380` | `0x1947330` | 12 | c_world_controller_tiger_base_state_handler |
| `c_world_controller_state_setup_activity_world_transition_handler` | `0x1947400` | `0x19473b0` | 12 | c_world_controller_tiger_base_state_handler |
| `c_world_controller_state_setup_matchmaking_handler` | `0x1947480` | `0x1947430` | 12 | c_world_controller_tiger_base_state_handler |
| `c_world_controller_state_setup_orbit_handler` | `0x1947500` | `0x19474b0` | 12 | c_world_controller_tiger_base_state_handler |
| `c_world_controller_state_setup_orbit_loading_handler` | `0x1947580` | `0x1947530` | 12 | c_world_controller_tiger_base_state_handler |
| `c_world_controller_state_setup_orbit_outro_handler` | `0x1947600` | `0x19475b0` | 12 | c_world_controller_tiger_base_state_handler |
| `c_world_controller_state_setup_prologue_intro_loading_handler` | `0x1947680` | `0x1947630` | 12 | c_world_controller_tiger_base_state_handler |
| `c_world_controller_tiger_base_state_handler` | `0x1945a10` | `0x19459c0` | 12 | c_world_controller_state_handler |
| `i_activity_client_endpoint_interface` | `0x19105c8` |  |  |  |
| `i_activity_client_messaging_interface` | `0x1941c50` |  |  | i_activity_message_recipient_handler_interface |
| `i_activity_game_system` | `0x1935e00` |  |  |  |
| `i_activity_message_recipient_handler_interface` | `0x1941c38` |  |  |  |
| `i_activity_message_recipient_interface` | `0x19105d8` |  |  |  |
| `i_online_matchmaking_interface` | `0x1942538` |  |  |  |
| `i_online_world_controller_ui_boot_flow_context` | `0x1945890` |  |  |  |
| `i_online_world_controller_ui_dialog_result_handler` | `0x19426a8` |  |  |  |

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
