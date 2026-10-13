# world_controller/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `omaha.world_controller`  
**Folder path evidence:** `HYPOTHESIS` (folder name is a proposal from RTTI/log-channel clustering, not a recovered path)  
**Role:** activity/state/slice_set/matchmaking managers, bootflow (log 'world_controller:*')

## Source files named in the binary

_None recovered (retail build stripped most asserts)._

## Decompiled functions

| VA | name | class | evidence | pseudo-C | role |
|---|---|---|---|---|---|
| `0x343a90` | world_slice_set_register |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`343a90_world_slice_set_register.c`](decompiled/343a90_world_slice_set_register.c) | Registers (activity tag, slice-set entry) for a world slice slot (bubble*8 + set), or clears it with -1. |
| `0x3454c0` | world_slice_state |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`3454c0_world_slice_state.c`](decompiled/3454c0_world_slice_state.c) | Region slot state: 5 not found, 2/4/6/7 loading states, else loaded. |
| `0x751ee0` | world_controller_select_mode |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`751ee0_world_controller_select_mode.c`](decompiled/751ee0_world_controller_select_mode.c) | Selects the world-controller mode (EWC / OWC / AHWC ...; names at 0x19458E0). |
| `0x752f10` | package_set_request_load |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`752f10_package_set_request_load.c`](decompiled/752f10_package_set_request_load.c) | Package manager (0x26C93B4, 8 x {state, handle, tag}): requests loading a package set ('global resource load of ...'). |
| `0x7536f0` | package_set_status |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`7536f0_package_set_status.c`](decompiled/7536f0_package_set_status.c) | Package manager: status of a requested package set. |
| `0x75f040` | world_current_activity_name |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`75f040_world_current_activity_name.c`](decompiled/75f040_world_current_activity_name.c) | Current activity (scenario) name: instance details +0x628 (char[40]). |
| `0x75f210` | world_fireteam_from_player |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`75f210_world_fireteam_from_player.c`](decompiled/75f210_world_fireteam_from_player.c) | Finds a player's fireteam id in the activity membership (properties block +0xA0). |
| `0x75fb20` | activity_manager_check_host_connection |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`75fb20_activity_manager_check_host_connection.c`](decompiled/75fb20_activity_manager_check_host_connection.c) | Fails the instance with 'Lost connection to activity host' when nothing was received for 20 s (+0.5 s) unless +0x134 is set. |
| `0x761b50` | activity_manager_update_instance |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`761b50_activity_manager_update_instance.c`](decompiled/761b50_activity_manager_update_instance.c) | Activity manager per-instance state machine (startup, join, entity indices, instantiation, ...); logs 'waiting for ...' and times out each sub-state. |
| `0x778d60` | slice_set_process_pah_region_data |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`778d60_slice_set_process_pah_region_data.c`](decompiled/778d60_slice_set_process_pah_region_data.c) | Reads the membership's host-tabulated region table (@0x2E48, 40 x 0xD8, -1 terminated) and matches entries to the current/target region and this player's transition token (+0x38+slot). |
| `0x780e60` | slice_set_transition_update |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`780e60_slice_set_transition_update.c`](decompiled/780e60_slice_set_transition_update.c) | Slice-set transition: waits until the target region is loaded and has host-tabulated data including this player ('...not yet have valid host-tabulated data'). |
| `0x782a80` | slice_set_find_region |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`782a80_slice_set_find_region.c`](decompiled/782a80_slice_set_find_region.c) | Looks up a region in the world slice table (0x3454C0); 'Region ... cannot be found'. |
| `0x783960` | world_state_reason_name |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`783960_world_state_reason_name.c`](decompiled/783960_world_state_reason_name.c) | Maps a state-change reason index to its name (table 0x26CAF40, stride 16). |
| `0x783ac0` | world_state_transition_step |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`783ac0_world_state_transition_step.c`](decompiled/783ac0_world_state_transition_step.c) | World-controller state machine transition step (state at obj+0x1B0, names at 0x1945340). |
| `0x783ee0` | world_state_request_cleanup |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`783ee0_world_state_request_cleanup.c`](decompiled/783ee0_world_state_request_cleanup.c) | Requests the cleanup state with a change reason (used when a prerequisite fails). |
| `0x784e50` | world_state_transport_method_reason |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`784e50_world_state_transport_method_reason.c`](decompiled/784e50_world_state_transport_method_reason.c) | Reports transport_method_invalid. |
| `0x785650` | world_state_reasons_init |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`785650_world_state_reasons_init.c`](decompiled/785650_world_state_reasons_init.c) | Builds the 284-entry state-change reason table at start-up. |
| `0x78df40` | world_current_activity_index |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`78df40_world_current_activity_index.c`](decompiled/78df40_world_current_activity_index.c) | Current activity index: instance details +0x620 (u16). |
| `0x78f570` | world_controller_mode_objects |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`78f570_world_controller_mode_objects.c`](decompiled/78f570_world_controller_mode_objects.c) | Only the EWC and OWC objects exist (slots 2 and 3); AHWC has a name but no object in retail. |
| `0x78f660` | world_controller_create_mode |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`78f660_world_controller_create_mode.c`](decompiled/78f660_world_controller_create_mode.c) | Creates the world-controller object for a mode. |
| `0x7927b0` | prerequisite_ethernet_link |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`7927b0_prerequisite_ethernet_link.c`](decompiled/7927b0_prerequisite_ethernet_link.c) | Prerequisite ENUM(6): ethernet link up. |
| `0x792cd0` | world_state_check_prerequisites |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`792cd0_world_state_check_prerequisites.c`](decompiled/792cd0_world_state_check_prerequisites.c) | Walks a state's prerequisite mask (38 bits), calling 0x792ED0 for each; on failure requests cleanup with the reason. |
| `0x792ed0` | world_state_prerequisite_check |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`792ed0_world_state_prerequisite_check.c`](decompiled/792ed0_world_state_prerequisite_check.c) | Bootflow/state prerequisite switch (0..0x25): returns 0 met, 1 waiting, 2 failed. |
| `0x7958c0` | initial_slice_set_loading_init |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`7958c0_initial_slice_set_loading_init.c`](decompiled/7958c0_initial_slice_set_loading_init.c) | Sets up the 11-task graph of activity:initial_slice_set_loading (callbacks 0x795A60..0x7966E0 with dependency masks); done mask 0x7FF. |
| `0x7965a0` | initial_slice_set_loading_task_player_ready |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`7965a0_initial_slice_set_loading_task_player_ready.c`](decompiled/7965a0_initial_slice_set_loading_task_player_ready.c) | Task 9: waits for the local player's unit object (with its definition) and a positive activity-mode byte (client reference 0x10, +0x1AC); returns 1 waiting / 2 done. |
| `0x7969a0` | initial_slice_set_loading_update |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`7969a0_initial_slice_set_loading_update.c`](decompiled/7969a0_initial_slice_set_loading_update.c) | Runs the loading task graph; when completed (+0x1A8) == required (+0x198) moves on. |
| `0x799a70` | bootflow_bap_signin_update |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`799a70_bootflow_bap_signin_update.c`](decompiled/799a70_bootflow_bap_signin_update.c) | bap_signin handler update (vtable 0x1945D90, sub-step at +0x30): 21 steps loading the bootstrap/startup/investment package sets, then connecting to BAP. |
| `0x799fa0` | bootflow_bap_connect |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`799fa0_bootflow_bap_connect.c`](decompiled/799fa0_bootflow_bap_connect.c) | bap_signin: connects to BAP at the sign-on address. |
| `0x79da10` | bootflow_investment_signin_update |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`79da10_bootflow_investment_signin_update.c`](decompiled/79da10_bootflow_investment_signin_update.c) | investment_signin update: step at +0x30, sub-step at +0x34 (done at 7/3); waits for the account slot. |
| `0x79e740` | bootflow_package_registration |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`79e740_bootflow_package_registration.c`](decompiled/79e740_bootflow_package_registration.c) | package_registration: registers the manifest's patchable packages with the resource system. |
| `0x79f310` | bootflow_platform_signin_update |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`79f310_bootflow_platform_signin_update.c`](decompiled/79f310_bootflow_platform_signin_update.c) | platform_signin: requires the DemonWare network start object (status 2) and the transport. |
| `0x79fde0` | bootflow_prepare_for_orbit_update |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`79fde0_bootflow_prepare_for_orbit_update.c`](decompiled/79fde0_bootflow_prepare_for_orbit_update.c) | prepare_for_orbit: loads the orbit package sets, then enters character:signin (step at +0x30). |
| `0x7a01c0` | bootflow_profile_setup_update |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`7a01c0_bootflow_profile_setup_update.c`](decompiled/7a01c0_bootflow_profile_setup_update.c) | profile_setup: step at +0x38 (0 brightness, 2 screen bounds, 4 third screen, 7 done). |
| `0x7a02e0` | bootflow_profile_setup_completed |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`7a02e0_bootflow_profile_setup_completed.c`](decompiled/7a02e0_bootflow_profile_setup_completed.c) | profile_setup 'completed' events (0x23/0x22/0x24) moving steps 1->2, 3->4, 5->6. |
| `0x7a1470` | character_prologue_update |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`7a1470_character_prologue_update.c`](decompiled/7a1470_character_prologue_update.c) | character:prologue state update (step at +0x30). |
| `0x7a1af0` | character_signin_update |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`7a1af0_character_signin_update.c`](decompiled/7a1af0_character_signin_update.c) | character:signin: step 6 creation (UI 0x1D) without characters, else step 5 select (UI 0x1C); done when the account slot has an active character. |
| `0x7a3b70` | world_find_orbit_or_bootstrap_map |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`7a3b70_world_find_orbit_or_bootstrap_map.c`](decompiled/7a3b70_world_find_orbit_or_bootstrap_map.c) | 'could not find a registered Orbit or bootstrap map'. |
| `0x7a8dd0` | world_transition_check_prerequisites |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`7a8dd0_world_transition_check_prerequisites.c`](decompiled/7a8dd0_world_transition_check_prerequisites.c) | activity_world_transition: refuses activities with unpurchased prerequisites (0x5505A0) -> 'World-transition requires DLC'. |
| `0x7ae9b0` | prologue_intro_loading_resolve_activity |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`7ae9b0_prologue_intro_loading_resolve_activity.c`](decompiled/7ae9b0_prologue_intro_loading_resolve_activity.c) | prologue_intro_loading: takes the activity name and checks it names a loadable named tag ('Unable to obtain activity_name'). |

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
