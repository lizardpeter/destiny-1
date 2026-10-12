# core/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `engine.core`  
**Folder path evidence:** `HYPOTHESIS` (folder name is a proposal from RTTI/log-channel clustering, not a recovered path)  
**Role:** allocators, containers, threading, crash reporting, input converters, character action_impl classes

## Source files named in the binary

_None recovered (retail build stripped most asserts)._

## Decompiled functions

| VA | name | class | evidence | pseudo-C | role |
|---|---|---|---|---|---|
| `0x3527d0` | engine_configuration_register |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`3527d0_engine_configuration_register.c`](decompiled/3527d0_engine_configuration_register.c) | Registers named global block 'Engine Configuration' (0x3330 bytes, align 4) via sub_23e010 into g_2693DF8. |

## Classes (145)

Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. Placement in this folder is `HYPOTHESIS` (name-token rule).

| class | typeinfo | vtable | virtual slots | bases |
|---|---|---|---|---|
| `(anonymous namespace)::Fios2Iter` | `0x19eee80` | `0x19eee50` | 5 | hkFileSystem::Iterator::Impl |
| `(anonymous namespace)::c_input_value_converter` | `0x19378a0` |  |  |  |
| `(anonymous namespace)::c_input_value_converter_legacy_automatic` | `0x19379b0` | `0x1937870` | 2 | (anonymous namespace)::c_input_value_converter |
| `(anonymous namespace)::c_input_value_converter_scalar` | `0x1937990` | `0x1937850` | 2 | (anonymous namespace)::c_input_value_converter |
| `(anonymous namespace)::c_input_value_converter_undefined` | `0x19379d0` | `0x1937890` | 6 | (anonymous namespace)::c_input_value_converter |
| `(anonymous namespace)::c_input_value_converter_world_space_vector` | `0x19378b0` | `0x1937770` | 2 | (anonymous namespace)::c_input_value_converter |
| `(anonymous namespace)::c_input_value_converter_world_space_yaw_pitch_bounded` | `0x1937910` | `0x19377d0` | 2 | (anonymous namespace)::c_input_value_converter |
| `(anonymous namespace)::c_input_value_converter_world_space_yaw_pitch_unbounded` | `0x19378d0` | `0x1937790` | 2 | (anonymous namespace)::c_input_value_converter |
| `(anonymous namespace)::c_input_value_converter_world_space_yaw_pitch_unbounded_lerping` | `0x19378f0` | `0x19377b0` | 2 | (anonymous namespace)::c_input_value_converter |
| `c_action_api` | `0x19323b0` |  |  |  |
| `c_action_impl_animation_base` | `0x1932580` |  |  | c_action_api |
| `c_action_impl_bunker` | `0x1932710` | `0x1932680` | 17 | c_action_api |
| `c_action_impl_bunker_idle` | `0x19327d0` | `0x1932740` | 17 | c_action_api |
| `c_action_impl_controlled_fall` | `0x1932890` | `0x1932800` | 17 | c_action_api |
| `c_action_impl_death` | `0x1932950` | `0x19328c0` | 17 | c_action_api |
| `c_action_impl_double_jump` | `0x1932a40` | `0x19329b0` | 17 | c_action_api |
| `c_action_impl_downhill_slide` | `0x1932b00` | `0x1932a70` | 17 | c_action_api |
| `c_action_impl_emote` | `0x1932c90` | `0x1932c00` | 17 | c_action_api |
| `c_action_impl_evade` | `0x1932d70` | `0x1932ce0` | 17 | c_action_api |
| `c_action_impl_floating_locomotion` | `0x1932e30` | `0x1932da0` | 17 | c_action_api |
| `c_action_impl_ghost_deploy` | `0x1932f00` | `0x1932e70` | 17 | c_action_api |
| `c_action_impl_ghost_summon` | `0x19330c0` | `0x1933030` | 17 | c_action_api |
| `c_action_impl_glide` | `0x1933180` | `0x19330f0` | 17 | c_action_api |
| `c_action_impl_grenade` | `0x1933250` | `0x19331b0` | 19 | c_action_api |
| `c_action_impl_jetpack` | `0x1933310` | `0x1933280` | 17 | c_action_api |
| `c_action_impl_jump` | `0x19333d0` | `0x1933340` | 17 | c_action_api |
| `c_action_impl_loki_play_animation` | `0x1933490` | `0x1933400` | 17 | c_action_api |
| `c_action_impl_mechanical_locomotion` | `0x1935520` | `0x1935490` | 17 | c_action_api |
| `c_action_impl_melee_recover` | `0x1933550` | `0x19334c0` | 17 | c_action_api |
| `c_action_impl_motion_controller_locomotion` | `0x19336e0` | `0x1933650` | 17 | c_action_api |
| `c_action_impl_ping_hard` | `0x19337b0` | `0x1933720` | 17 | c_action_api |
| `c_action_impl_power_melee` | `0x1933ea0` | `0x1933e10` | 17 | c_action_api |
| `c_action_impl_resurrect` | `0x1934020` | `0x1933f90` | 17 | c_action_api |
| `c_action_impl_seat_enter` | `0x19340f0` | `0x1934060` | 17 | c_action_api |
| `c_action_impl_seat_exit` | `0x19341c0` | `0x1934130` | 17 | c_action_api |
| `c_action_impl_seat_idle` | `0x1934280` | `0x19341f0` | 17 | c_action_api |
| `c_action_impl_simple_animation` | `0x19344c0` | `0x1934430` | 17 | c_action_api |
| `c_action_impl_staged_firing` | `0x1934700` | `0x1934670` | 17 | c_action_api |
| `c_action_impl_stagger` | `0x19347e0` | `0x1934750` | 17 | c_action_api |
| `c_action_impl_state_machine` | `0x19348a0` | `0x1934810` | 17 | c_action_api |
| `c_action_impl_steal_hop_on` | `0x1934960` | `0x19348d0` | 17 | c_action_api |
| `c_action_impl_stutter_step` | `0x1934a20` | `0x1934990` | 17 | c_action_api |
| `c_action_impl_surprise` | `0x1934ae0` | `0x1934a50` | 17 | c_action_api |
| `c_action_impl_turret_locomotion` | `0x1935850` | `0x19357c0` | 17 | c_action_api |
| `c_action_impl_void_bow` | `0x1934d30` | `0x1934c90` | 19 | c_action_impl_grenade |
| `c_allocation_interface` | `0x1904a60` |  |  |  |
| `c_animation_state_container_widget` | `0x1969ef0` | `0x1969de0` | 26 | c_cui_container_widget |
| `c_banhammer_controller_monitor` | `0x196bac0` | `0x196baa0` | 3 | c_controller_monitor |
| `c_broadphase_border` | `0x1908520` | `0x1908440` | 10 | hkpBroadPhaseBorder |
| `c_client_atom_control` | `0x1906eb8` |  |  |  |
| `c_client_control_flag_atom_control` | `0x1907160` | `0x1907100` | 11 | c_client_instant_atom_control |
| `c_client_face_atom_control` | `0x1906f00` | `0x1906df0` | 11 | c_client_trivial_atom_control |
| `c_client_instant_atom_control` | `0x1906fb0` | `0x1906f50` | 11 | c_client_trivial_atom_control |
| `c_client_move_to_atom_control` | `0x1906f20` | `0x1906e60` | 13 | c_client_atom_control |
| `c_client_sequence_atom_control` | `0x1907280` | `0x1907220` | 11 | c_client_trivial_atom_control |
| `c_client_set_temperament_atom_control` | `0x19071f0` | `0x1907190` | 11 | c_client_instant_atom_control |
| `c_client_sleep_atom_control` | `0x1907040` | `0x1906fe0` | 11 | c_client_trivial_atom_control |
| `c_client_snap_to_atom_control` | `0x19070d0` | `0x1907070` | 11 | c_client_instant_atom_control |
| `c_client_trivial_atom_control` | `0x1906ee0` |  |  | c_client_atom_control |
| `c_controller_input_message` | `0x194c9b0` | `0x194c990` | 6 | c_message |
| `c_controller_monitor` | `0x194c838` | `0x194c860` | 3 |  |
| `c_core_save_crash_reporter` | `0x1909730` | `0x19096f0` | 7 | i_crash_report_files |
| `c_crash_dump_writer` | `0x1905a60` | `0x1905a20` | 7 | i_crash_report_files |
| `c_crash_info_dumper` | `0x1905b30` | `0x1905b00` | 5 | c_formatted_output |
| `c_crash_info_writer` | `0x1905ad0` | `0x1905a90` | 7 | i_crash_report_files |
| `c_crash_keyboard_input` | `0x1905ba0` | `0x1905b60` | 7 | i_crash_report_files |
| `c_crash_report_upload_status` | `0x1905c00` | `0x1905bf0` | 1 | c_upload_client_update<c_demonware_http_upload_client> |
| `c_crash_upload_header_info` | `0x1904e60` | `0x1904e20` | 7 | i_crash_report_files |
| `c_crs_test_double_tapper` | `0x1905d50` | `0x1905d10` | 7 | i_crash_report_files |
| `c_cseries_base_allocation` | `0x194b190` | `0x194b170` | 3 | c_allocation_interface |
| `c_cui_screen_widget::i_destruction_callback` | `0x1951c68` |  |  |  |
| `c_custom_animation_container_widget` | `0x196a030` | `0x1969f20` | 26 | c_cui_container_widget |
| `c_enemy_reward_site_finder` | `0x190fd80` | `0x190fd00` | 7 | c_reward_site_finder<s_investment_combatant_reward> |
| `c_engine_interface` | `0x19098a0` |  |  |  |
| `c_feature_condition_is_completed` | `0x190f920` | `0x190f870` | 1 | i_feature_condition |
| `c_feature_condition_is_playable` | `0x190f940` | `0x190f890` | 1 | i_feature_condition |
| `c_feature_condition_matches_exact_stat_level` | `0x190f9a0` | `0x190f8f0` | 1 | i_feature_condition |
| `c_focused_animation_container_widget` | `0x196a170` | `0x196a060` | 26 | c_cui_container_widget |
| `c_formatted_output` | `0x1904a40` |  |  |  |
| `c_game_achievements_proxy` | `0x1942a90` | `0x1942a40` | 12 | i_achievements_proxy |
| `c_game_system_interface` | `0x1906748` |  |  |  |
| `c_game_system_list` | `0x1909870` | `0x1909840` | 8 | c_game_system_interface |
| `c_global_tag_registry` | `0x1914c00` | `0x1914bd0` | 8 | c_game_system_interface |
| `c_gpu_owner_visitor` | `0x1905f28` |  |  |  |
| `c_icon_widget` | `0x196a2b0` | `0x196a1a0` | 26 | c_bitmap_widget_base |
| `c_input_event_container_widget` | `0x196a470` | `0x196a360` | 26 | c_cui_container_widget |
| `c_letterbox_manager` | `0x1949470` | `0x1949440` | 8 | c_game_system_interface |
| `c_list_widget` | `0x196a7c0` | `0x196a5e0` | 52 | c_cui_container_widget |
| `c_marketplace_product_info_async_task` | `0x19117a0` | `0x1911770` | 8 | c_platform_async_np_future_task<sce::Toolkit::NP::ProductInfoDetailed> |
| `c_message` | `0x194c970` | `0x194c950` | 6 |  |
| `c_one_off_animation_container_widget` | `0x196a9c0` | `0x196a8b0` | 26 | c_cui_container_widget |
| `c_playgo_install_watcher` | `0x1907e70` | `0x1907dc0` | 15 | i_dlc_category_installer, i_dlc_installer_progress @+0x8 |
| `c_progress_indicator_widget` | `0x196ab00` | `0x196a9f0` | 26 | c_cui_container_widget |
| `c_replication_control_view` | `0x196c530` | `0x196c4b0` | 15 | c_replication_scheduler_client |
| `c_replication_event_manager_view` | `0x196c7a0` | `0x196c720` | 15 | c_replication_scheduler_client |
| `c_replication_scheduler` | `0x196b090` | `0x196b040` | 9 | c_network_channel_client |
| `c_replication_scheduler_client` | `0x196c548` |  |  |  |
| `c_reports_formatted_output` | `0x1905290` | `0x1905260` | 8 | c_formatted_output |
| `c_reward_site_finder<s_investment_combatant_reward>` | `0x190fdd0` |  |  | i_reward_site_finder |
| `c_reward_site_finder<s_investment_incident_reward>` | `0x190fdb0` |  |  | i_reward_site_finder |
| `c_roster_account_translation_callback` | `0x193fa90` | `0x193f9f0` | 3 | i_investment_bap_message_queue_callbacks |
| `c_rsat_detect_stale_references_processor` | `0x196c630` | `0x196c5a0` | 3 | c_rsat_sanitize_entity_reference_processor |
| `c_schema_record_allocation_interface` | `0x1906298` | `0x19061b0` | 31 |  |
| `c_scratch_allocation` | `0x19051d0` | `0x19051a0` | 3 | c_allocation_interface |
| `c_screen_area_fx_manager` | `0x1949310` | `0x19492e0` | 8 | c_game_system_interface |
| `c_screenshot_writer` | `0x1905e40` | `0x1905e00` | 7 | i_crash_report_files |
| `c_sensor_dump_formatted_output` | `0x1913f80` | `0x1913f50` | 8 | c_reports_formatted_output |
| `c_sequence_input_handler_base` | `0x1944330` |  |  |  |
| `c_sequence_input_handler_button` | `0x19442b0` | `0x1944220` | 2 | c_sequence_input_handler_base |
| `c_sequence_input_handler_chord` | `0x19442d0` | `0x1944240` | 2 | c_sequence_input_handler_base |
| `c_sequence_input_handler_sequence` | `0x19442f0` | `0x1944260` | 4 | c_sequence_input_handler_base |
| `c_sequence_input_handler_stick_flick` | `0x1944290` | `0x1944200` | 2 | c_sequence_input_handler_base |
| `c_sequence_input_handler_stick_range` | `0x1944270` | `0x19441e0` | 2 | c_sequence_input_handler_base |
| `c_simple_subscreen_widget` | `0x196ac40` | `0x196ab30` | 27 | c_subscreen_widget |
| `c_status_crash_reporter` | `0x1909900` | `0x19098c0` | 7 | i_crash_report_files |
| `c_status_retail_crash_output` | `0x1909970` | `0x1909940` | 5 | c_formatted_output |
| `c_subscreen_widget` | `0x196ad80` | `0x196ac70` | 27 | c_cui_container_widget |
| `c_target_acquisition_query_filter` | `0x1942db0` | `0x1942d80` | 5 | c_weapon_aim_query_filter |
| `c_task_manager<e_activity_in_world_task, c_world_controller_state_activity_in_world_handler>` | `0x1945540` | `0x1945510` | 8 | i_task_status_provider |
| `c_task_manager<e_activity_session_creation_task, c_world_controller_state_setup_activity_session_creation_handler>` | `0x1945630` | `0x1945610` | 6 | i_task_status_provider |
| `c_task_manager<e_activity_slice_set_loading_task, c_world_controller_state_activity_initial_slice_set_loading_handler>` | `0x1945590` | `0x1945570` | 6 | i_task_status_provider |
| `c_task_manager<e_activity_world_transition_task, c_world_controller_state_setup_activity_world_transition_handler>` | `0x19455e0` | `0x19455c0` | 6 | i_task_status_provider |
| `c_task_manager<e_bootflow_media_check_task, c_world_controller_state_bootflow_media_check_handler>` | `0x1945720` | `0x1945700` | 6 | i_task_status_provider |
| `c_task_manager<e_cleanup_task, c_world_controller_state_cleanup_handler>` | `0x19456d0` | `0x19456b0` | 6 | i_task_status_provider |
| `c_task_manager<e_orbit_loading_task, c_world_controller_state_setup_orbit_loading_handler>` | `0x1945680` | `0x1945660` | 6 | i_task_status_provider |
| `c_text_widget` | `0x1950cf0` | `0x1950be0` | 26 | c_cui_widget |
| `c_thread_base` | `0x1906318` | `0x19062d0` | 3 |  |
| `c_thread_wrapper` | `0x1906330` | `0x1906300` | 5 | c_thread_base |
| `c_upload_client_update<c_demonware_http_upload_client>` | `0x1905c18` |  |  |  |
| `c_verification_failure_popup_handler` | `0x1946800` | `0x1946760` | 2 | i_online_world_controller_ui_dialog_result_handler |
| `c_verify_strings_task<2u, 128u>` | `0x194ca30` | `0x194ca00` | 5 | c_verify_strings_task_base |
| `c_verify_strings_task_base` | `0x196c290` | `0x196c270` | 6 | c_xoverlapped_task |
| `c_visibility_game_system_interface` | `0x19488f0` | `0x19488c0` | 8 | c_game_system_interface |
| `c_watchdog_progress_handler` | `0x19049a0` | `0x1904930` | 13 | i_watchdog_progress_handler |
| `c_xoverlapped_task` | `0x194c7d8` |  |  |  |
| `defrag_handle_relocated_gpu_entry(uint_address, uint_address, void*, void const*)::c_gpu_owner_defrag_update_visitor` | `0x1905f40` | `0x1905f20` | 3 | c_gpu_owner_visitor |
| `i_achievements_proxy` | `0x1942ab0` |  |  |  |
| `i_authority_change_callback_interface` | `0x19065d0` |  |  |  |
| `i_crash_report_progress` | `0x19049b8` | `0x1905c40` | 10 |  |
| `i_feature_condition` | `0x190f9e0` |  |  |  |
| `i_reward_site_finder` | `0x190fd98` |  |  |  |
| `i_task_status_provider` | `0x1945530` |  |  |  |
| `i_watchdog_progress_handler` | `0x19049d0` |  |  | i_crash_report_progress |
| `resourcerer_allocate_gpu_resource_internal(c_common_handle, c_common_handle, intsize, intsize, s_resourcerer_packed_flags, e_resourcerer_gpu_memory_location, e_resourcerer_gpu_memory_location, void**, intsize*, e_resourcerer_gpu_memory_location*)::c_gpu_owner_extra_update_visitor` | `0x1905f80` | `0x1905f70` | 1 | c_gpu_owner_visitor |
| `s_rich_text_deleter` | `0x1949a20` |  |  |  |

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
