# cui/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `engine.ui.cui`  
**Folder path evidence:** `HYPOTHESIS` (folder name is a proposal from RTTI/log-channel clustering, not a recovered path)  
**Role:** cui:: screens, widgets, event-handler components

## Source files named in the binary

_None recovered (retail build stripped most asserts)._

## Decompiled functions

_None yet._

## Classes (600)

Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. Placement in this folder is `HYPOTHESIS` (name-token rule).

| class | typeinfo | vtable | virtual slots | bases |
|---|---|---|---|---|
| `c_activity_hud_client_game_system` | `0x1935f20` | `0x1935ed0` | 9 | i_activity_game_system |
| `c_cui_character_creation_data_component` | `0x1958930` | `0x1958850` | 21 | c_cui_object_component |
| `c_cui_component` | `0x1951710` | `0x1951690` | 18 | cui::i_properties, cui::c_change_tracker @+0x8 |
| `c_cui_container_widget` | `0x1951880` | `0x1951770` | 26 | c_cui_widget |
| `c_cui_delete_character_server_message_component` | `0x1952730` | `0x1952640` | 22 | c_event_handler_component |
| `c_cui_investment_activity_quota_component` | `0x19534c0` | `0x19533e0` | 21 | c_cui_object_component |
| `c_cui_investment_character_loot_state_component` | `0x19535d0` | `0x19534f0` | 21 | c_cui_object_component |
| `c_cui_investment_character_state_component` | `0x1953680` | `0x1953600` | 18 | c_cui_component |
| `c_cui_investment_loot_pipe` | `0x1953c50` | `0x1953c40` | 4 | cui::c_screen_pipe |
| `c_cui_investment_loot_pipe_component` | `0x1953c00` | `0x1953b10` | 22 | c_screen_pipe_component |
| `c_cui_loot_pickup_item_server_message_component` | `0x19540d0` | `0x1953fe0` | 22 | c_event_handler_component |
| `c_cui_object_component` | `0x1951a10` | `0x1951930` | 21 | c_cui_component, cui::i_properties_layout @+0x88 |
| `c_cui_player_select_reference` | `0x1951a80` | `0x1951a70` | 1 | cui::c_screen_reference |
| `c_cui_screen_widget` | `0x1951c40` | `0x1951b30` | 26 | c_cui_container_widget |
| `c_cui_show_platform_party_ui_component` | `0x1955b90` | `0x1955aa0` | 22 | c_event_handler_component |
| `c_cui_signout_character_server_message_component` | `0x1955cb0` | `0x1955bc0` | 22 | c_event_handler_component |
| `c_cui_sizing_container_widget` | `0x1969240` | `0x1969130` | 26 | c_cui_container_widget |
| `c_cui_story_pipe` | `0x1950bb0` | `0x1950ba0` | 4 | cui::c_screen_pipe |
| `c_cui_survey_question_pipe` | `0x19671d0` | `0x19671c0` | 4 | cui::c_screen_pipe |
| `c_cui_survey_question_pipe_component` | `0x1967180` | `0x1967090` | 22 | c_screen_pipe_component |
| `c_cui_thud_damage_indicator_container` | `0x19651a0` | `0x1965090` | 26 | c_cui_container_widget |
| `c_cui_thud_game_state_announcement_component` | `0x19656f0` | `0x1965610` | 21 | c_cui_object_component |
| `c_cui_thud_indicator_panel` | `0x1965d30` | `0x1965c20` | 26 | c_cui_container_widget |
| `c_cui_thud_nav_mode_component` | `0x19661a0` | `0x19660c0` | 21 | c_cui_object_component |
| `c_cui_thud_progression_announcement_component` | `0x19664a0` | `0x19663c0` | 21 | c_cui_object_component |
| `c_cui_thud_waypoint_container` | `0x1966a80` | `0x1966970` | 26 | cui::c_thud_indicator_container |
| `c_cui_thud_xp_flyout_container` | `0x1966d20` | `0x1966c10` | 26 | cui::c_thud_indicator_container |
| `c_cui_transformation_container_widget` | `0x1951db0` | `0x1951ca0` | 26 | c_cui_container_widget |
| `c_cui_widget` | `0x1951ef0` | `0x1951de0` | 26 | c_cui_object_component |
| `c_simulation_queue_cui_deterministic_globals_update_definition` | `0x1951ad0` | `0x1951ab0` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_queue_cui_deterministic_globals_update_data> |
| `c_thud_data_component` | `0x1957290` | `0x19571b0` | 21 | c_cui_object_component |
| `cui::c_abort_activity_countdown_component` | `0x195a250` | `0x195a160` | 22 | c_event_handler_component |
| `cui::c_abort_matchmaking_component` | `0x19521d0` | `0x19520e0` | 22 | c_event_handler_component |
| `cui::c_activity_intro_data_component` | `0x19578c0` | `0x1957840` | 18 | c_cui_component |
| `cui::c_activity_reward_info` | `0x195a840` | `0x195a7d0` | 9 | cui::c_properties_accessor_base<cui::c_activity_reward_info> |
| `cui::c_activity_script_value_component` | `0x1957a60` | `0x19579e0` | 18 | c_cui_component |
| `cui::c_activity_tier_select_handler_component` | `0x195a4c0` | `0x195a440` | 18 | c_cui_component |
| `cui::c_alert_pipe` | `0x194d1a0` | `0x194d180` | 6 | cui::c_screen_pipe |
| `cui::c_alert_reference` | `0x1951400` | `0x19513f0` | 1 | cui::c_screen_reference |
| `cui::c_arrangement_container_widget` | `0x1952310` | `0x1952200` | 26 | c_cui_container_widget |
| `cui::c_arrangement_parameters` | `0x19514e0` | `0x1951430` | 9 | cui::i_properties |
| `cui::c_bootflow_emergency_event_handler_component` | `0x1957d40` | `0x1957c50` | 22 | c_event_handler_component |
| `cui::c_bootflow_installer_data_component` | `0x1957e50` | `0x1957dd0` | 18 | c_cui_component |
| `cui::c_bootflow_intro_component` | `0x19580e0` | `0x1957ff0` | 22 | c_event_handler_component |
| `cui::c_bootflow_screen_bounds_event_handler_component` | `0x1958200` | `0x1958110` | 22 | c_event_handler_component |
| `cui::c_bootflow_server_queue_data_component` | `0x19582b0` | `0x1958230` | 18 | c_cui_component |
| `cui::c_bootflow_server_queue_event_handler_component` | `0x19583c0` | `0x19582e0` | 21 | c_cui_object_component |
| `cui::c_bootflow_signon_server_actions_component` | `0x19584d0` | `0x19583f0` | 21 | c_cui_object_component |
| `cui::c_bootflow_start_component` | `0x19585e0` | `0x1958500` | 21 | c_cui_object_component |
| `cui::c_bootflow_start_event_handler_component` | `0x1958700` | `0x1958610` | 22 | c_event_handler_component |
| `cui::c_bootflow_user_advance_event_handler_component` | `0x1958820` | `0x1958730` | 22 | c_event_handler_component |
| `cui::c_border_widget` | `0x19679e0` | `0x19678d0` | 26 | c_cui_widget |
| `cui::c_chain_animation_container` | `0x1967b20` | `0x1967a10` | 26 | cui::c_arrangement_container_widget |
| `cui::c_change_slot` | `0x194ed40` | `0x1951f80` | 2 |  |
| `cui::c_change_tracker` | `0x1951748` |  |  |  |
| `cui::c_character_class_bucket_flyout` | `0x1958ba0` | `0x1958b40` | 11 | cui::i_flyout_data |
| `cui::c_character_creation_class_focus_observer_component` | `0x19594c0` | `0x19593c0` | 21 | c_cui_object_component |
| `cui::c_character_creation_data_component` | `0x1958bc0` | `0x1958a90` | 18 | c_cui_component |
| `cui::c_character_creation_pipe` | `0x1959620` | `0x19594f0` | 2 | cui::c_screen_pipe |
| `cui::c_character_creation_pipe_component` | `0x1959600` | `0x1959510` | 22 | c_screen_pipe_component |
| `cui::c_character_creation_race_gender_focus_observer_component` | `0x19594a0` | `0x19592d0` | 21 | c_cui_object_component |
| `cui::c_character_creation_selection_data_component` | `0x19596d0` | `0x1959650` | 18 | c_cui_component |
| `cui::c_character_creation_selection_handler_component` | `0x1959850` | `0x1959760` | 22 | c_event_handler_component |
| `cui::c_character_customization_category_flyout` | `0x19599d0` | `0x19598e0` | 11 | cui::i_flyout_data, ui::c_enable_shared_from_this<cui::c_character_customization_category_flyout> @+0x8 |
| `cui::c_character_customization_data_component` | `0x1959a10` | `0x1959950` | 18 | c_cui_component |
| `cui::c_character_customization_option_bucket` | `0x1959a60` | `0x1959880` | 9 | cui::c_properties_accessor_base<cui::c_character_customization_option_bucket> |
| `cui::c_character_race_gender_bucket_flyout` | `0x1958b10` | `0x1958a20` | 11 | cui::i_flyout_data |
| `cui::c_character_race_gender_data` | `0x1958c00` | `0x1958960` | 9 | cui::c_properties_accessor_base<cui::c_character_race_gender_data> |
| `cui::c_cinematic_bitmap_widget` | `0x195a130` | `0x195a020` | 26 | c_bitmap_widget |
| `cui::c_cinematic_overlay_data_component` | `0x1957b70` | `0x1957a90` | 21 | c_cui_object_component |
| `cui::c_cinematic_texture_camera_widget` | `0x1967dd0` | `0x1967cc0` | 26 | c_cui_widget |
| `cui::c_conditional_sound_component` | `0x194db00` | `0x194da20` | 21 | c_cui_object_component |
| `cui::c_confirmation_dialog_event_filter_component` | `0x19524f0` | `0x1952400` | 22 | c_event_handler_component |
| `cui::c_counter_component` | `0x1952610` | `0x1952520` | 22 | c_event_handler_component |
| `cui::c_crossfade_bitmap_widget` | `0x1967fa0` | `0x1967e90` | 26 | c_bitmap_widget |
| `cui::c_cui_director_select_reference` | `0x1952890` | `0x1952880` | 1 | cui::c_screen_reference |
| `cui::c_currency_reward_item_container` | `0x195c080` | `0x195bf50` | 26 | cui::c_reward_item_container |
| `cui::c_death_data_component` | `0x1964cd0` | `0x1964c50` | 18 | c_cui_component |
| `cui::c_delay_activity_countdown_component` | `0x195a7a0` | `0x195a6b0` | 22 | c_event_handler_component |
| `cui::c_dialog_data_component` | `0x194deb0` | `0x194ddd0` | 21 | c_dialog_pipe_client_component |
| `cui::c_dialog_option` | `0x194dfc0` | `0x194df50` | 9 | cui::c_properties_accessor_base<cui::c_dialog_option> |
| `cui::c_dialog_pipe` | `0x194e410` | `0x194e400` | 4 | cui::c_screen_pipe |
| `cui::c_dialog_reference` | `0x19518c0` | `0x19518b0` | 1 | cui::c_screen_reference |
| `cui::c_director_activity` | `0x1954220` | `0x19541b0` | 9 | cui::c_properties_accessor_base<cui::c_director_activity> |
| `cui::c_director_activity_data_component` | `0x195ae40` | `0x195adc0` | 18 | c_cui_component |
| `cui::c_director_activity_node_container_widget` | `0x195afd0` | `0x195aec0` | 26 | c_cui_container_widget |
| `cui::c_director_art_element_container_widget` | `0x195b190` | `0x195b080` | 26 | c_cui_container_widget |
| `cui::c_director_book_data_component` | `0x195b250` | `0x195b1d0` | 18 | c_cui_component |
| `cui::c_director_data_component_v2` | `0x195b4c0` | `0x195b440` | 18 | c_cui_component |
| `cui::c_director_line_container_widget` | `0x195b6f0` | `0x195b5e0` | 26 | c_cui_container_widget |
| `cui::c_director_panel_widget` | `0x195b830` | `0x195b720` | 26 | c_cui_container_widget |
| `cui::c_director_select_pipe` | `0x19528d0` | `0x19528c0` | 4 | cui::c_screen_pipe |
| `cui::c_director_select_pipe_component` | `0x1952850` | `0x1952760` | 22 | c_screen_pipe_component |
| `cui::c_director_select_pipe_reader_component` | `0x19529e0` | `0x1952900` | 21 | c_screen_pipe_client_component |
| `cui::c_director_select_pipe_writer_component` | `0x1952af0` | `0x1952a10` | 21 | cui::c_director_select_pipe_reader_component |
| `cui::c_director_timer_element_container_widget` | `0x195ba00` | `0x195b8f0` | 26 | c_cui_container_widget |
| `cui::c_dock_arrangement_container_widget` | `0x1952c30` | `0x1952b20` | 26 | cui::c_arrangement_container_widget |
| `cui::c_dock_arrangement_parameters` | `0x1951500` | `0x1951490` | 9 | cui::c_arrangement_parameters |
| `cui::c_dynamic_data_component` | `0x1952ef0` | `0x1952c60` | 21 | c_cui_object_component |
| `cui::c_dynamic_data_component::c_dynamic_properties` | `0x1952e00` | `0x1952db0` | 9 | cui::i_properties |
| `cui::c_dynamic_data_component::c_dynamic_properties_layout` | `0x1952d80` | `0x1952d50` | 5 | cui::i_properties_layout |
| `cui::c_dynamic_data_component::c_dynamic_properties_sequence` | `0x1952e50` | `0x1952e30` | 3 | cui::i_properties_sequence |
| `cui::c_dynamic_data_component::c_dynamic_properties_sequence_element` | `0x1952ed0` | `0x1952e80` | 9 | cui::i_properties |
| `cui::c_dynamic_properties_sequence<ui::c_shared_ptr<cui::c_roster_contact_id_container> >` | `0x195a950` | `0x195a8c0` | 5 | cui::i_properties_sequence, ui::c_vector<ui::c_shared_ptr<cui::c_roster_contact_id_container>, ui::s_allocator> @+0x8 |
| `cui::c_event_handler_component_v2` | `0x1952fb0` | `0x1952f20` | 17 | c_cui_component |
| `cui::c_event_multiplexer_component` | `0x194e970` | `0x194e890` | 21 | c_cui_object_component |
| `cui::c_external_dynamic_data_component` | `0x19530c0` | `0x1952fe0` | 21 | cui::c_dynamic_data_component |
| `cui::c_faction_data_component` | `0x195c130` | `0x195c0b0` | 18 | c_cui_component |
| `cui::c_fireteam_details_component` | `0x195c260` | `0x195c1e0` | 18 | c_cui_component |
| `cui::c_fireteam_settings_widget` | `0x195c510` | `0x195c400` | 26 | c_cui_container_widget |
| `cui::c_flyout_widget` | `0x1968100` | `0x1967ff0` | 26 | cui::c_arrangement_container_widget |
| `cui::c_hold_button_event_component` | `0x1953170` | `0x19530f0` | 18 | c_cui_component |
| `cui::c_hold_button_event_widget` | `0x1968400` | `0x19682f0` | 26 | c_cui_container_widget |
| `cui::c_in_progress_pipe` | `0x194f150` | `0x194f140` | 4 | cui::c_screen_pipe |
| `cui::c_in_progress_reference` | `0x1951900` | `0x19518f0` | 1 | cui::c_screen_reference |
| `cui::c_interface_query_table<1ul>` | `0x1960050` | `0x1960040` | 1 | cui::i_interface_provider |
| `cui::c_interface_query_table<2ul>` | `0x195d700` | `0x195d6f0` | 1 | cui::i_interface_provider |
| `cui::c_interface_query_table<4ul>` | `0x1960730` | `0x1960720` | 1 | cui::i_interface_provider |
| `cui::c_interface_query_table<5ul>` | `0x195d290` | `0x195d270` | 3 | cui::i_interface_provider |
| `cui::c_internal_dynamic_data_component` | `0x19533b0` | `0x19532d0` | 21 | cui::c_dynamic_data_component |
| `cui::c_inventory_bucket_data_component` | `0x195c7b0` | `0x195c730` | 18 | c_cui_component |
| `cui::c_inventory_item_tracker_data_component` | `0x195c860` | `0x195c7e0` | 18 | c_cui_component |
| `cui::c_investment_backpack_component` | `0x195ccd0` | `0x195cad0` | 31 | c_cui_component, cui::i_investment_item_action_interface @+0x88, cui::i_investment_item_equip_interface @+0x90, cui::i_investment_item_lockbox_overlay_interface @+0x98, cui::i_investment_item_precache_interface @+0xa0, cui::i_investment_item_select_interface @+0xa8 |
| `cui::c_investment_backpack_item` | `0x195cc90` | `0x195ca00` | 9 | cui::c_investment_item_context |
| `cui::c_investment_backpack_slot` | `0x195ce80` | `0x195cd60` | 9 | cui::c_properties_accessor_base<cui::c_investment_backpack_slot> |
| `cui::c_investment_backpack_slot_flyout` | `0x195ccb0` | `0x195ca60` | 11 | cui::i_flyout_data |
| `cui::c_investment_character_statistics_component` | `0x1953730` | `0x19536b0` | 18 | c_cui_component |
| `cui::c_investment_currency_reward_alert_data_component` | `0x195d3e0` | `0x195d360` | 18 | c_cui_component |
| `cui::c_investment_equip_inventory_item_component` | `0x1953ae0` | `0x19539f0` | 22 | c_event_handler_component |
| `cui::c_investment_infusion_data_component` | `0x195d570` | `0x195d470` | 22 | c_cui_component, cui::i_investment_item_action_interface @+0x88, cui::i_investment_item_infusion_interface @+0x90 |
| `cui::c_investment_infusion_item` | `0x195d5f0` | `0x195d410` | 9 | cui::c_properties_accessor_base<cui::c_investment_infusion_item> |
| `cui::c_investment_inventory_monitor_component` | `0x195d7b0` | `0x195d730` | 18 | c_cui_component |
| `cui::c_investment_item_activity_score` | `0x195dcc0` | `0x195dc50` | 9 | cui::c_properties_accessor_base<cui::c_investment_item_activity_score> |
| `cui::c_investment_item_comparison_component` | `0x195e3d0` | `0x195e350` | 18 | c_cui_component |
| `cui::c_investment_item_context` | `0x195e450` | `0x195e400` | 9 | cui::i_properties |
| `cui::c_investment_item_details_screen_loader_component` | `0x195e510` | `0x195e480` | 17 | cui::c_event_handler_component_v2 |
| `cui::c_investment_item_event` | `0x195e970` | `0x195e920` | 9 | cui::i_properties |
| `cui::c_investment_item_lock_event_handler` | `0x195e7d0` | `0x195e6e0` | 22 | c_event_handler_component |
| `cui::c_investment_item_lockbox_overlay_component` | `0x195e6b0` | `0x195e630` | 18 | c_cui_component |
| `cui::c_investment_item_record_node_info` | `0x195dae0` | `0x195da70` | 9 | cui::c_properties_accessor_base<cui::c_investment_item_record_node_info> |
| `cui::c_investment_item_track_progress_event` | `0x195e9f0` | `0x195e9a0` | 9 | cui::c_investment_item_event |
| `cui::c_investment_item_widget` | `0x195ea10` | `0x195e800` | 26 | c_cui_container_widget |
| `cui::c_investment_login_info_component_v2` | `0x195eb40` | `0x195eac0` | 18 | c_cui_component |
| `cui::c_investment_objective_item` | `0x195de80` | `0x195de10` | 9 | cui::c_properties_accessor_base<cui::c_investment_objective_item> |
| `cui::c_investment_progression` | `0x195b5b0` | `0x195b540` | 9 | cui::c_properties_accessor_base<cui::c_investment_progression> |
| `cui::c_investment_progression_data_component` | `0x195ee00` | `0x195ed80` | 18 | c_cui_component |
| `cui::c_investment_promotion_entry_event_handler_component` | `0x195ef20` | `0x195ee30` | 22 | c_event_handler_component |
| `cui::c_investment_quest_data_component` | `0x195efd0` | `0x195ef50` | 18 | c_cui_component |
| `cui::c_investment_record_book_component` | `0x195f2d0` | `0x195f120` | 21 | c_cui_component, cui::i_investment_item_action_interface @+0x88, cui::i_investment_item_select_interface @+0x90 |
| `cui::c_investment_record_book_reward_item` | `0x195f230` | `0x195f060` | 9 | cui::c_investment_item_context |
| `cui::c_investment_record_node_info` | `0x195f210` | `0x195f000` | 9 | cui::c_properties_accessor_base<cui::c_investment_record_node_info> |
| `cui::c_investment_record_page_info` | `0x195f250` | `0x195f0c0` | 9 | cui::c_properties_accessor_base<cui::c_investment_record_page_info> |
| `cui::c_investment_server_message_request_handler` | `0x195f770` | `0x195f740` | 5 | i_investment_bap_message_queue_callbacks |
| `cui::c_investment_stat_group_component` | `0x195f820` | `0x195f7a0` | 18 | c_cui_component |
| `cui::c_investment_talent_basic_node_info` | `0x19633b0` | `0x1963200` | 9 | cui::c_properties_accessor_base<cui::c_investment_talent_basic_node_info> |
| `cui::c_investment_talent_step` | `0x19634d0` | `0x1963460` | 9 | cui::c_properties_accessor_base<cui::c_investment_talent_step> |
| `cui::c_investment_tracked_offer_upsell_event_handler_component` | `0x195fab0` | `0x195f9c0` | 22 | c_event_handler_component |
| `cui::c_investment_vendor_bucket` | `0x19606f0` | `0x1960680` | 9 | cui::c_properties_accessor_base<cui::c_investment_vendor_bucket> |
| `cui::c_investment_vendor_interaction_display_component` | `0x195fb60` | `0x195fae0` | 18 | c_cui_component |
| `cui::c_investment_vendor_interaction_event_handler_component` | `0x195fd80` | `0x195fd00` | 18 | c_cui_component |
| `cui::c_investment_vendor_interaction_reply` | `0x195fc00` | `0x195fb90` | 9 | cui::c_properties_accessor_base<cui::c_investment_vendor_interaction_reply> |
| `cui::c_investment_vendor_item` | `0x1960320` | `0x1960080` | 9 | cui::c_properties_accessor_base<cui::c_investment_vendor_item> |
| `cui::c_investment_vendor_refund_component` | `0x195fee0` | `0x195fe10` | 20 | c_cui_component, cui::i_investment_item_action_interface @+0x88 |
| `cui::c_investment_vendor_refund_receipt` | `0x195ff40` | `0x195fdb0` | 9 | cui::c_properties_accessor_base<cui::c_investment_vendor_refund_receipt> |
| `cui::c_investment_vendor_wares_component` | `0x1960280` | `0x1960140` | 24 | c_cui_component, cui::i_investment_item_action_interface @+0x88, cui::i_investment_item_precache_interface @+0x90, cui::i_investment_item_select_interface @+0x98, cui::i_investment_item_upsell_interface @+0xa0 |
| `cui::c_invite_console_party_event_handler_component` | `0x1953d70` | `0x1953c80` | 22 | c_event_handler_component |
| `cui::c_invoke_platform_signin_event_handler_component` | `0x1953e90` | `0x1953da0` | 22 | c_event_handler_component |
| `cui::c_item_progression_reward_item_container` | `0x1960a80` | `0x1960970` | 26 | cui::c_reward_item_container |
| `cui::c_item_request_handler` | `0x1960ae0` | `0x1960ab0` | 5 | cui::c_investment_server_message_request_handler |
| `cui::c_launch_director_activity_component` | `0x195bb20` | `0x195ba30` | 22 | c_event_handler_component |
| `cui::c_leave_party_component` | `0x1953fb0` | `0x1953ec0` | 22 | c_event_handler_component |
| `cui::c_line_art_widget` | `0x1968540` | `0x1968430` | 26 | c_cui_widget |
| `cui::c_list_item_view_widget` | `0x1968680` | `0x1968570` | 26 | cui::c_view_widget |
| `cui::c_list_view_widget` | `0x19687c0` | `0x19686b0` | 26 | cui::c_view_widget |
| `cui::c_load_details_screen_destruction_callback` | `0x19673f0` | `0x19673d0` | 3 | c_cui_screen_widget::i_destruction_callback |
| `cui::c_load_screen_destruction_callback` | `0x1950300` | `0x19501e0` | 3 | c_cui_screen_widget::i_destruction_callback |
| `cui::c_long_property_enum_table` | `0x1967430` | `0x1967420` | 1 | cui::c_property_enum_table |
| `cui::c_loot_reward_item_container` | `0x1960c20` | `0x1960b10` | 26 | cui::c_reward_item_container |
| `cui::c_matchmaking_progress_component` | `0x1954180` | `0x1954100` | 18 | c_cui_component |
| `cui::c_matchmaking_roster_component` | `0x1960cd0` | `0x1960c50` | 18 | c_cui_component |
| `cui::c_medal_container` | `0x1964e10` | `0x1964d00` | 26 | c_cui_container_widget |
| `cui::c_mimic_widget` | `0x1968960` | `0x1968850` | 26 | c_cui_widget |
| `cui::c_modal_animation_container_widget` | `0x1968aa0` | `0x1968990` | 26 | c_cui_container_widget |
| `cui::c_multi_decision_maker_branch` | `0x19543f0` | `0x1954250` | 14 | cui::c_properties_accessor_base<cui::c_multi_decision_maker_branch>, cui::i_properties_layout @+0x8 |
| `cui::c_multi_decision_maker_component` | `0x1954430` | `0x1954310` | 21 | c_cui_component, cui::i_properties_layout @+0x88 |
| `cui::c_nav_mode_menu_index_component` | `0x1966250` | `0x19661d0` | 18 | c_cui_component |
| `cui::c_number_interpolation_component` | `0x1954630` | `0x19545b0` | 18 | c_cui_component |
| `cui::c_number_watcher_component` | `0x194f830` | `0x194f750` | 21 | c_cui_object_component |
| `cui::c_offscreen_indicator_container` | `0x1954810` | `0x1954700` | 26 | c_cui_container_widget |
| `cui::c_omni_arrangement_container_widget` | `0x1968be0` | `0x1968ad0` | 26 | cui::c_arrangement_container_widget |
| `cui::c_omni_stack_arrangement_container_widget` | `0x1968d20` | `0x1968c10` | 26 | cui::c_stack_arrangement_container_widget |
| `cui::c_online_friend_count_component` | `0x1960e00` | `0x1960d80` | 18 | c_cui_component |
| `cui::c_options_data_component` | `0x1954b00` | `0x1954960` | 16 | c_cui_component |
| `cui::c_options_single_setting_data_component` | `0x1954b20` | `0x19549f0` | 16 | c_cui_component |
| `cui::c_options_writer_component` | `0x19551f0` | `0x1955100` | 22 | c_event_handler_component |
| `cui::c_orbit_data_component` | `0x195bbd0` | `0x195bb50` | 18 | c_cui_component |
| `cui::c_orbit_roster_component` | `0x1960f30` | `0x1960e90` | 18 | c_cui_component |
| `cui::c_orbit_team_container` | `0x1960f10` | `0x1960e30` | 9 | cui::c_properties_accessor_base<cui::c_orbit_team_container> |
| `cui::c_overdraw_shader_component` | `0x1955300` | `0x1955220` | 21 | c_cui_object_component |
| `cui::c_pagination_component` | `0x1968dd0` | `0x1968d50` | 18 | c_cui_component |
| `cui::c_player_option_widget` | `0x19613d0` | `0x19612c0` | 26 | c_cui_container_widget |
| `cui::c_player_options_component` | `0x1961120` | `0x19610a0` | 18 | c_cui_component |
| `cui::c_player_report_component` | `0x19615d0` | `0x19614e0` | 22 | c_event_handler_component |
| `cui::c_player_report_widget` | `0x1961820` | `0x1961710` | 26 | c_cui_container_widget |
| `cui::c_player_select_pipe_vendor_helper_component` | `0x1961930` | `0x1961850` | 21 | c_screen_pipe_client_component |
| `cui::c_post_game_data_component` | `0x1963cb0` | `0x1963c30` | 18 | c_cui_component |
| `cui::c_private_lobby_option_bucket` | `0x1961ac0` | `0x19619c0` | 9 | cui::c_properties_accessor_base<cui::c_private_lobby_option_value> |
| `cui::c_private_lobby_option_value` | `0x1961aa0` | `0x1961960` | 9 | cui::c_properties_accessor_base<cui::c_private_lobby_option_value> |
| `cui::c_private_lobby_options_component` | `0x1961ae0` | `0x1961a20` | 18 | c_cui_component |
| `cui::c_private_lobby_options_select_handler` | `0x1961db0` | `0x1961d20` | 17 | cui::c_event_handler_component_v2 |
| `cui::c_progress_bar_widget` | `0x1968f90` | `0x1968e80` | 26 | c_cui_widget |
| `cui::c_progression_reward_item_container` | `0x1961ef0` | `0x1961de0` | 26 | cui::c_reward_item_container |
| `cui::c_properties_accessor_base<cui::c_activity_reward_info>` | `0x195a820` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_character_customization_option_bucket>` | `0x1959a40` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_character_race_gender_data>` | `0x1958be0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_dialog_option>` | `0x194dfa0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_director_activity>` | `0x1954200` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_investment_backpack_slot>` | `0x195ce60` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_investment_infusion_item>` | `0x195d5d0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_investment_item_activity_score>` | `0x195dca0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_investment_item_record_node_info>` | `0x195dac0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_investment_objective_item>` | `0x195de60` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_investment_progression>` | `0x195b590` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_investment_record_node_info>` | `0x195f320` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_investment_record_page_info>` | `0x195f340` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_investment_talent_basic_node_info>` | `0x1963390` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_investment_talent_step>` | `0x19634b0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_investment_vendor_bucket>` | `0x19606d0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_investment_vendor_interaction_reply>` | `0x195fbe0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_investment_vendor_item>` | `0x1960300` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_investment_vendor_refund_receipt>` | `0x195ff20` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_multi_decision_maker_branch>` | `0x19544d0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_orbit_team_container>` | `0x1960f50` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_private_lobby_option_value>` | `0x1961b00` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_quest_step_container>` | `0x19620f0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_racing_player_data>` | `0x19665f0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_roster_contact_id_container>` | `0x195aa90` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_scoreboard_player_info>` | `0x19645f0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_scoreboard_team_info>` | `0x1964500` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_tab_data>` | `0x1956370` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_thud_arsenal_objective_data>` | `0x1957470` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_thud_control_objective_data>` | `0x1957370` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_thud_control_point_properties>` | `0x1957330` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_thud_elimination_objective_data>` | `0x19573f0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_thud_ghost_properties>` | `0x19572f0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_thud_interaction_info>` | `0x1965e60` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_thud_pvp_objective_properties>` | `0x19574b0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_thud_racing_objective_data>` | `0x1957740` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_thud_rift_objective_data>` | `0x1957430` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_thud_salvage_objective_data>` | `0x19573b0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::c_thud_weapon_properties>` | `0x19572b0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_activity_requirements_not_met_entry>` | `0x195ab30` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_activity_skull_modifier>` | `0x195a3f0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_activity_type_unlock_requirement>` | `0x195a660` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_bootflow_installer_checklist_item>` | `0x1957ed0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_chain_animation_entry>` | `0x1967c20` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_character_class_bucket>` | `0x1959280` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_character_class_data>` | `0x19591e0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_character_customization_category_data_container>` | `0x1959f30` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_character_customization_category_hotspot_data>` | `0x1959fd0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_character_customization_option_data>` | `0x1959bd0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_character_race_bucket>` | `0x1958c20` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_countdown_data>` | `0x19546b0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_director_book_info>` | `0x195b320` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_faction_display_data>` | `0x1957990` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_fireteam_member_info>` | `0x195c3b0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_fireteam_privacy_option>` | `0x195c590` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_inventory_flyout_identifier>` | `0x195cea0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_investment_item_details_screen_data>` | `0x195d220` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_investment_item_record_book_info>` | `0x195dbb0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_investment_item_record_book_reward_item_info>` | `0x195d9d0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_investment_item_stat>` | `0x19539a0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_investment_item_stat_meter>` | `0x195f970` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_investment_material_requirement>` | `0x195e070` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_investment_perk_info>` | `0x1963550` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_investment_requirement_description>` | `0x1960920` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_investment_unlock_flag>` | `0x195e160` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_investment_vendor_pagination_settings>` | `0x1960340` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_login_character_info>` | `0x195ed30` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_options_bucket>` | `0x1954bc0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_options_bucket_display>` | `0x1955060` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_options_setting>` | `0x1954b80` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_options_value>` | `0x1954b40` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_player_nameplate>` | `0x195ec90` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_player_option>` | `0x1961270` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_post_game_reward>` | `0x1963d30` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_report_reason>` | `0x19615f0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_roster_contact_group>` | `0x1962b60` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_score_stat_group_info>` | `0x1964220` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_score_stat_info>` | `0x1964b40` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_scoreboard_secondary_stat_info>` | `0x19642c0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_screen_load_parameters>` | `0x195e5e0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_talent_basic_node_input_data_container>` | `0x1963160` |  |  | cui::i_properties |
| `cui::c_properties_accessor_base<cui::s_tracked_inventory_item_data>` | `0x195c9b0` |  |  | cui::i_properties |
| `cui::c_properties_accessor_proxy<c_icon_widget>` | `0x196a330` | `0x196a2e0` | 9 | cui::i_properties |
| `cui::c_properties_accessor_proxy<c_player_select_pipe_reader_component>` | `0x194fb20` | `0x194fad0` | 9 | cui::i_properties |
| `cui::c_properties_accessor_proxy<cui::c_chain_animation_container>` | `0x1967ba0` | `0x1967b50` | 9 | cui::i_properties |
| `cui::c_properties_accessor_proxy<cui::c_cinematic_texture_camera_widget>` | `0x1967e50` | `0x1967e00` | 9 | cui::i_properties |
| `cui::c_properties_accessor_proxy<cui::c_dialog_data_component>` | `0x194e120` | `0x194e0d0` | 9 | cui::i_properties |
| `cui::c_properties_accessor_proxy<cui::c_director_activity_node_container_widget>` | `0x195b050` | `0x195b000` | 9 | cui::i_properties |
| `cui::c_properties_accessor_proxy<cui::c_director_panel_widget>` | `0x195b8c0` | `0x195b870` | 9 | cui::i_properties |
| `cui::c_properties_accessor_proxy<cui::c_fireteam_settings_widget>` | `0x195c680` | `0x195c630` | 9 | cui::i_properties |
| `cui::c_properties_accessor_proxy<cui::c_flyout_widget>` | `0x1968240` | `0x19681f0` | 9 | cui::i_properties |
| `cui::c_properties_accessor_proxy<cui::c_investment_item_widget>` | `0x195ea90` | `0x195ea40` | 9 | cui::i_properties |
| `cui::c_properties_accessor_proxy<cui::c_player_option_widget>` | `0x1961450` | `0x1961400` | 9 | cui::i_properties |
| `cui::c_properties_accessor_proxy<cui::c_roster_contact_widget>` | `0x1962960` | `0x1962910` | 9 | cui::i_properties |
| `cui::c_properties_accessor_proxy<cui::c_talent_basic_node_component>` | `0x1963430` | `0x19633e0` | 9 | cui::i_properties |
| `cui::c_properties_accessor_proxy<cui::c_talent_grid_panel_widget>` | `0x19630e0` | `0x1963090` | 9 | cui::i_properties |
| `cui::c_properties_accessor_proxy<cui::c_thud_fireteam_status_player_container>` | `0x19655e0` | `0x1965590` | 9 | cui::i_properties |
| `cui::c_properties_accessor_proxy<cui::s_investment_display_metadata>` | `0x1962410` | `0x19623c0` | 9 | cui::i_properties |
| `cui::c_properties_sequence_entry_selector` | `0x19690a0` | `0x1968fc0` | 21 | c_cui_object_component |
| `cui::c_property_enum_table` | `0x1967448` |  |  |  |
| `cui::c_property_value::c_holder` | `0x1967750` |  |  |  |
| `cui::c_property_value::c_typed_holder<bool>` | `0x194cea0` | `0x194ce80` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<c_big_flags_OLD<80> >` | `0x194e170` | `0x194e150` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<c_string_hash>` | `0x194cdb0` | `0x194cd90` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::c_roster_contact_id>` | `0x194fc60` | `0x194fc40` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::c_string_reference>` | `0x194cf40` | `0x194cf20` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::c_uber_string>` | `0x1950e50` | `0x1950e30` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::c_value_ptr<c_cui_component> >` | `0x194d7b0` | `0x194d790` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::c_value_ptr<char const> >` | `0x19676e0` | `0x19676c0` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::c_value_ptr<cui::c_investment_progression> >` | `0x195b510` | `0x195b4f0` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::c_value_ptr<cui::c_multi_decision_maker_branch> >` | `0x1954520` | `0x1954500` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::c_value_ptr<cui::i_interface_provider> >` | `0x195d1a0` | `0x195d180` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::c_value_ptr<cui::s_chain_animation_entry> >` | `0x1967c90` | `0x1967c70` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::c_value_ptr<cui::s_inventory_flyout_identifier> >` | `0x195cfb0` | `0x195cf90` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::c_value_ptr<cui::s_options_bucket_display> >` | `0x1954d20` | `0x1954d00` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::c_value_ptr<s_create_character_server_message_request_arguments> >` | `0x1959730` | `0x1959710` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::c_value_ptr<s_player_configuration const> >` | `0x194fcb0` | `0x194fc90` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::c_value_ptr<utf8 const> >` | `0x1967690` | `0x1967670` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::c_value_ptr<wchar_t const> >` | `0x194f2c0` | `0x194f2a0` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::s_bounds>` | `0x1951550` | `0x1951530` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::s_changeable_hitch<char const> >` | `0x1950e00` | `0x1950de0` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::s_changeable_hitch<utf8 const> >` | `0x1967730` | `0x1967710` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::s_changeable_hitch<wchar_t const> >` | `0x194cd60` | `0x194cd40` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::s_combatant_nameplate>` | `0x1964050` | `0x1964030` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::s_investment_character_id>` | `0x194fbc0` | `0x194fba0` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::s_investment_item_id>` | `0x194fc10` | `0x194fbf0` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::s_margin>` | `0x19515a0` | `0x1951580` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::s_talent_basic_node_input_data>` | `0x19631d0` | `0x19631b0` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<cui::s_version_number>` | `0x1963a20` | `0x1963a00` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<float>` | `0x194ce00` | `0x194cde0` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<int>` | `0x194ce50` | `0x194ce30` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<s_player_identifier>` | `0x194fd00` | `0x194fce0` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<s_server_guid>` | `0x194fb70` | `0x194fb50` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<ui::c_shared_ptr<cui::c_director_activity> >` | `0x195ae90` | `0x195ae70` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<ui::c_shared_ptr<cui::c_investment_backpack_item> >` | `0x195cf10` | `0x195cef0` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<ui::c_shared_ptr<cui::c_investment_vendor_bucket> >` | `0x1967640` | `0x1967620` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<ui::c_shared_ptr<cui::c_roster_contact_id> >` | `0x19675f0` | `0x19675d0` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<ui::c_shared_ptr<cui::c_roster_contact_id_container> >` | `0x1964660` | `0x1964640` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<ui::c_shared_ptr<cui::c_scoreboard_player_info> >` | `0x19675a0` | `0x1967580` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<ui::c_shared_ptr<cui::c_scoreboard_team_info> >` | `0x1967550` | `0x1967530` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<ui::c_shared_ptr<cui::i_flyout_data> >` | `0x1954cd0` | `0x1954cb0` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<ui::c_shared_ptr<cui::i_properties> >` | `0x194e010` | `0x194dff0` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<ui::c_shared_ptr<cui::i_properties_sequence> >` | `0x194e1c0` | `0x194e1a0` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<ui::c_shared_ptr<cui::s_director_book_info> >` | `0x195b2a0` | `0x195b280` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<ui::c_shared_ptr<cui::s_faction_display_data> >` | `0x1957910` | `0x19578f0` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<ui::c_shared_ptr<cui::s_investment_item_stat> >` | `0x1953820` | `0x1953800` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<ui::c_shared_ptr<cui::s_options_bucket_display> >` | `0x1967500` | `0x19674e0` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<ui::c_shared_ptr<cui::s_options_value> >` | `0x1954c30` | `0x1954c10` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<ui::c_shared_ptr<ui::s_rich_text> >` | `0x19560d0` | `0x19560b0` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<ui::c_uber_handle>` | `0x194cef0` | `0x194ced0` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<unsigned long>` | `0x194ebf0` | `0x194ebd0` | 6 | cui::c_property_value::c_holder |
| `cui::c_property_value::c_typed_holder<vector4>` | `0x1950700` | `0x19506e0` | 6 | cui::c_property_value::c_holder |
| `cui::c_quest_step_container` | `0x1962110` | `0x19620a0` | 9 | cui::c_properties_accessor_base<cui::c_quest_step_container> |
| `cui::c_quest_step_page_component` | `0x1961fa0` | `0x1961f20` | 18 | c_cui_component |
| `cui::c_quest_step_reward_item_container` | `0x1962250` | `0x1962140` | 26 | cui::c_reward_item_container |
| `cui::c_racing_player_data` | `0x19665b0` | `0x19664d0` | 9 | cui::c_properties_accessor_base<cui::c_racing_player_data> |
| `cui::c_record_book_unseal_book_request_handler` | `0x195f2b0` | `0x195f280` | 5 | cui::c_investment_server_message_request_handler |
| `cui::c_record_completion_reward_item_container` | `0x1962390` | `0x1962280` | 26 | cui::c_reward_item_container |
| `cui::c_record_reward_redemption_event_container_widget` | `0x19554a0` | `0x1955330` | 26 | c_cui_container_widget |
| `cui::c_record_reward_redemption_request` | `0x1955480` | `0x1955450` | 5 | cui::c_investment_server_message_request_handler |
| `cui::c_reward_display_widget` | `0x1962550` | `0x1962440` | 26 | c_cui_container_widget |
| `cui::c_reward_item_container` | `0x195c060` | `0x1962580` | 26 | c_cui_container_widget |
| `cui::c_roster_component` | `0x1962720` | `0x19626a0` | 18 | c_cui_component |
| `cui::c_roster_contact_id_container` | `0x195aab0` | `0x195aa40` | 9 | cui::c_properties_accessor_base<cui::c_roster_contact_id_container> |
| `cui::c_roster_contact_widget` | `0x19628e0` | `0x19627d0` | 26 | c_cui_sizing_container_widget |
| `cui::c_roster_page_component` | `0x1962a10` | `0x1962990` | 18 | c_cui_component |
| `cui::c_row_lookup_component` | `0x19555b0` | `0x19554d0` | 21 | c_cui_object_component |
| `cui::c_sandbox_interruption_component` | `0x1956e20` | `0x1956d40` | 21 | c_cui_object_component |
| `cui::c_scoreboard_data_component` | `0x1963ef0` | `0x1963e50` | 17 | c_cui_component, cui::i_investment_item_select_interface @+0x88 |
| `cui::c_scoreboard_player_info` | `0x1964610` | `0x19645a0` | 9 | cui::c_properties_accessor_base<cui::c_scoreboard_player_info> |
| `cui::c_scoreboard_team_info` | `0x1964520` | `0x19644b0` | 9 | cui::c_properties_accessor_base<cui::c_scoreboard_team_info> |
| `cui::c_screen_pipe` | `0x194d190` |  |  |  |
| `cui::c_screen_reference` | `0x194c748` | `0x194c740` | 3 |  |
| `cui::c_show_help_ui_component` | `0x1955950` | `0x1955860` | 22 | c_event_handler_component |
| `cui::c_show_invitations_ui_component` | `0x1955a70` | `0x1955980` | 22 | c_event_handler_component |
| `cui::c_skip_cinematic_event_handler_component` | `0x1955dd0` | `0x1955ce0` | 22 | c_event_handler_component |
| `cui::c_sobject_texture_camera_widget` | `0x19693e0` | `0x19692d0` | 26 | c_cui_widget |
| `cui::c_sparrow_horn_preview_event_handler_component` | `0x1962d70` | `0x1962c80` | 22 | c_event_handler_component |
| `cui::c_stack_arrangement_container_widget` | `0x1955f10` | `0x1955e00` | 26 | cui::c_arrangement_container_widget |
| `cui::c_static_properties_layout` | `0x19678a0` | `0x1967780` | 8 | cui::c_static_properties_layout_base |
| `cui::c_static_properties_layout_base` | `0x1967810` | `0x19677d0` | 10 | cui::i_properties_layout |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_activity_reward_info>, 4ul>` | `0x195ad20` | `0x195acf0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_activity_reward_info>, 4ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_activity_reward_info>, 6ul>` | `0x195f670` | `0x195f640` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_activity_reward_info>, 6ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_character_customization_option_bucket>, 4ul>` | `0x1959dc0` | `0x1959d90` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_character_customization_option_bucket>, 4ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_character_race_gender_data>, 2ul>` | `0x1959140` | `0x1959110` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_character_race_gender_data>, 2ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_character_race_gender_data>, 8ul>` | `0x1958fa0` | `0x1958f70` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_character_race_gender_data>, 8ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_dialog_option>, 4ul>` | `0x194e080` | `0x194e040` | 7 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_dialog_option>, 4ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_director_activity>, 6ul>` | `0x195bcd0` | `0x195bca0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_director_activity>, 6ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_backpack_item>, 340ul>` | `0x195d130` | `0x195d100` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_backpack_item>, 340ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_backpack_slot>, 6ul>` | `0x195d060` | `0x195d030` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_backpack_slot>, 6ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_infusion_item>, 15ul>` | `0x195d6a0` | `0x195d670` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_infusion_item>, 15ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_item_activity_score>, 12ul>` | `0x195dd70` | `0x195dd40` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_item_activity_score>, 12ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_item_record_node_info>, 4ul>` | `0x195d860` | `0x195d830` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_item_record_node_info>, 4ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_objective_item>, 1ul>` | `0x195f6f0` | `0x195f6c0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_objective_item>, 1ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_objective_item>, 8ul>` | `0x195df30` | `0x195df00` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_objective_item>, 8ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_progression>, 32ul>` | `0x195c190` | `0x195c160` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_progression>, 32ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_progression>, 4ul>` | `0x195b3f0` | `0x195b3c0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_progression>, 4ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_record_book_reward_item>, 16ul>` | `0x195f570` | `0x195f540` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_record_book_reward_item>, 16ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_record_node_info>, 8ul>` | `0x195f5f0` | `0x195f5c0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_record_node_info>, 8ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_record_page_info>, 20ul>` | `0x195f450` | `0x195f420` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_record_page_info>, 20ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_vendor_bucket>, 32ul>` | `0x1960490` | `0x1960460` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_vendor_bucket>, 32ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_vendor_interaction_reply>, 4ul>` | `0x195fcb0` | `0x195fc80` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_vendor_interaction_reply>, 4ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_vendor_item>, 14ul>` | `0x1960630` | `0x1960600` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_vendor_item>, 14ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_vendor_item>, 4ul>` | `0x1964aa0` | `0x1964a70` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_vendor_item>, 4ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_vendor_item>, 84ul>` | `0x1960830` | `0x1960800` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_vendor_item>, 84ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_vendor_item>, 8ul>` | `0x1960560` | `0x1960530` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_vendor_item>, 8ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_vendor_refund_receipt>, 30ul>` | `0x195fff0` | `0x195ffc0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_vendor_refund_receipt>, 30ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_orbit_team_container>, 12ul>` | `0x1961000` | `0x1960fd0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_orbit_team_container>, 12ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_private_lobby_option_bucket>, 16ul>` | `0x1961cd0` | `0x1961ca0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_private_lobby_option_bucket>, 16ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_private_lobby_option_value>, 64ul>` | `0x1961c00` | `0x1961bd0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_private_lobby_option_value>, 64ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_quest_step_container>, 20ul>` | `0x1962050` | `0x1962020` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_quest_step_container>, 20ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_racing_player_data>, 6ul>` | `0x19666a0` | `0x1966670` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_racing_player_data>, 6ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_roster_contact_id_container>, 110ul>` | `0x1962780` | `0x1962750` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_roster_contact_id_container>, 110ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_roster_contact_id_container>, 12ul>` | `0x1960d30` | `0x1960d00` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_roster_contact_id_container>, 12ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_roster_contact_id_container>, 20ul>` | `0x1962be0` | `0x1962bb0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_roster_contact_id_container>, 20ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_scoreboard_player_info>, 16ul>` | `0x1964410` | `0x19643e0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_scoreboard_player_info>, 16ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_scoreboard_team_info>, 16ul>` | `0x1964130` | `0x1964100` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_scoreboard_team_info>, 16ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_tab_data>, 6ul>` | `0x1956440` | `0x1956410` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_tab_data>, 6ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_thud_control_point_properties>, 8ul>` | `0x19576a0` | `0x1957670` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_thud_control_point_properties>, 8ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_thud_interaction_info>, 3ul>` | `0x1965f30` | `0x1965f00` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_thud_interaction_info>, 3ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_thud_weapon_properties>, 3ul>` | `0x1957580` | `0x1957550` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::c_thud_weapon_properties>, 3ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::i_properties>, 32ul>` | `0x19682a0` | `0x1968270` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::i_properties>, 32ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::i_properties>, 60ul>` | `0x1968e30` | `0x1968e00` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::i_properties>, 60ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_activity_requirements_not_met_entry>, 4ul>` | `0x195ac00` | `0x195abd0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_activity_requirements_not_met_entry>, 4ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_activity_skull_modifier>, 8ul>` | `0x195a350` | `0x195a320` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_activity_skull_modifier>, 8ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_activity_type_unlock_requirement>, 16ul>` | `0x195a5c0` | `0x195a590` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_activity_type_unlock_requirement>, 16ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_bootflow_installer_checklist_item>, 16ul>` | `0x1957fa0` | `0x1957f70` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_bootflow_installer_checklist_item>, 16ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_character_class_data>, 4ul>` | `0x1958de0` | `0x1958db0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_character_class_data>, 4ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_character_customization_category_data_container>, 30ul>` | `0x1959ca0` | `0x1959c70` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_character_customization_category_data_container>, 30ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_character_customization_option_data>, 30ul>` | `0x1959e90` | `0x1959e60` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_character_customization_option_data>, 30ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_character_race_bucket>, 4ul>` | `0x1959070` | `0x1959040` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_character_race_bucket>, 4ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_fireteam_member_info>, 12ul>` | `0x195c310` | `0x195c2e0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_fireteam_member_info>, 12ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_fireteam_privacy_option>, 5ul>` | `0x195c6e0` | `0x195c6b0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_fireteam_privacy_option>, 5ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_investment_item_stat>, 16ul>` | `0x19635d0` | `0x19635a0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_item_stat>, 16ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_investment_item_stat>, 5ul>` | `0x1963be0` | `0x1963bb0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_item_stat>, 5ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_investment_item_stat>, 6ul>` | `0x1953900` | `0x19538d0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_item_stat>, 6ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_investment_item_stat_meter>, 16ul>` | `0x195f8d0` | `0x195f8a0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_item_stat_meter>, 16ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_investment_material_requirement>, 8ul>` | `0x195e2b0` | `0x195e280` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_material_requirement>, 8ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_investment_perk_info>, 18ul>` | `0x1953880` | `0x1953850` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_perk_info>, 18ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_investment_perk_info>, 6ul>` | `0x195d930` | `0x195d900` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_perk_info>, 6ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_investment_requirement_description>, 4ul>` | `0x1960410` | `0x19603e0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_requirement_description>, 4ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_investment_requirement_description>, 9ul>` | `0x1963040` | `0x1963010` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_requirement_description>, 9ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_investment_unlock_flag>, 4ul>` | `0x195e1e0` | `0x195e1b0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_unlock_flag>, 4ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_login_character_info>, 10ul>` | `0x195ebf0` | `0x195ebc0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_login_character_info>, 10ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_options_bucket_display>, 12ul>` | `0x1954d80` | `0x1954d50` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_options_bucket_display>, 12ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_options_setting>, 5ul>` | `0x1954ef0` | `0x1954ec0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_options_setting>, 5ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_options_value>, 10ul>` | `0x1954fc0` | `0x1954f90` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_options_value>, 10ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_player_option>, 12ul>` | `0x19611d0` | `0x19611a0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_player_option>, 12ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_post_game_reward>, 10ul>` | `0x1963e00` | `0x1963dd0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_post_game_reward>, 10ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_report_reason>, 10ul>` | `0x19616c0` | `0x1961690` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_report_reason>, 10ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_roster_contact_group>, 20ul>` | `0x1962ac0` | `0x1962a90` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_roster_contact_group>, 20ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_score_stat_group_info>, 2ul>` | `0x19646c0` | `0x1964690` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_score_stat_group_info>, 2ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_score_stat_group_info>, 6ul>` | `0x1964790` | `0x1964760` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_score_stat_group_info>, 6ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_score_stat_info>, 16ul>` | `0x1964340` | `0x1964310` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_score_stat_info>, 16ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_score_stat_info>, 2ul>` | `0x19648b0` | `0x1964880` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_score_stat_info>, 2ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_score_stat_info>, 6ul>` | `0x19649d0` | `0x19649a0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_score_stat_info>, 6ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_scoreboard_secondary_stat_info>, 2ul>` | `0x19640b0` | `0x1964080` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_scoreboard_secondary_stat_info>, 2ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_talent_basic_node_input_data_container>, 8ul>` | `0x1962fc0` | `0x1962f90` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_talent_basic_node_input_data_container>, 8ul> @+0x8 |
| `cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_tracked_inventory_item_data>, 4ul>` | `0x195c910` | `0x195c8e0` | 5 | cui::i_properties_sequence, ui::c_static_vector<ui::c_shared_ptr<cui::s_tracked_inventory_item_data>, 4ul> @+0x8 |
| `cui::c_string_formatter_component` | `0x1956020` | `0x1955f40` | 21 | c_cui_object_component |
| `cui::c_tab_component` | `0x19561e0` | `0x1956100` | 21 | c_cui_object_component |
| `cui::c_tab_data` | `0x1956390` | `0x1956320` | 9 | cui::c_properties_accessor_base<cui::c_tab_data> |
| `cui::c_tab_header_component` | `0x19562f0` | `0x1956210` | 21 | c_cui_object_component |
| `cui::c_talent_activation_request` | `0x1962dd0` | `0x1962da0` | 5 | cui::c_investment_server_message_request_handler |
| `cui::c_talent_basic_node_component` | `0x1963370` | `0x1963260` | 26 | c_cui_container_widget |
| `cui::c_talent_grid_panel_widget` | `0x1962f10` | `0x1962e00` | 26 | c_cui_container_widget |
| `cui::c_talent_node_set_line_container_widget` | `0x1963780` | `0x1963670` | 26 | c_cui_container_widget |
| `cui::c_talent_requirement_line_container_widget` | `0x19638c0` | `0x19637b0` | 26 | c_cui_container_widget |
| `cui::c_team_selection_event_handler_component` | `0x1956510` | `0x1956490` | 18 | c_cui_component |
| `cui::c_team_switch_event_handler_component` | `0x1964c20` | `0x1964b90` | 17 | cui::c_event_handler_component_v2 |
| `cui::c_thud_arsenal_objective_data` | `0x1957490` | `0x19570f0` | 9 | cui::c_properties_accessor_base<cui::c_thud_arsenal_objective_data> |
| `cui::c_thud_banner_container_widget` | `0x1964f50` | `0x1964e40` | 26 | c_cui_container_widget |
| `cui::c_thud_bubble_transition_announcement_component` | `0x1965060` | `0x1964f80` | 21 | c_cui_object_component |
| `cui::c_thud_control_objective_data` | `0x1957390` | `0x1956f70` | 9 | cui::c_properties_accessor_base<cui::c_thud_control_objective_data> |
| `cui::c_thud_control_point_properties` | `0x1957350` | `0x1956f10` | 9 | cui::c_properties_accessor_base<cui::c_thud_control_point_properties> |
| `cui::c_thud_damage_indicator_panel` | `0x19652e0` | `0x19651d0` | 26 | c_cui_container_widget |
| `cui::c_thud_elimination_objective_data` | `0x1957410` | `0x1957030` | 9 | cui::c_properties_accessor_base<cui::c_thud_elimination_objective_data> |
| `cui::c_thud_fireteam_status_panel` | `0x1965420` | `0x1965310` | 26 | c_cui_container_widget |
| `cui::c_thud_fireteam_status_player_container` | `0x1965560` | `0x1965450` | 26 | c_cui_container_widget |
| `cui::c_thud_game_text_channel_widget` | `0x1965830` | `0x1965720` | 26 | c_cui_container_widget |
| `cui::c_thud_game_text_container` | `0x1965970` | `0x1965860` | 26 | c_cui_container_widget |
| `cui::c_thud_ghost_properties` | `0x1957310` | `0x1956eb0` | 9 | cui::c_properties_accessor_base<cui::c_thud_ghost_properties> |
| `cui::c_thud_hit_flyout_container` | `0x1965ad0` | `0x19659a0` | 26 | cui::c_thud_indicator_container |
| `cui::c_thud_indicator_container` | `0x1965ab0` | `0x1965b00` | 26 | c_cui_container_widget |
| `cui::c_thud_interaction_data_component` | `0x1965de0` | `0x1965d60` | 18 | c_cui_component |
| `cui::c_thud_interaction_info` | `0x1965e80` | `0x1965e10` | 9 | cui::c_properties_accessor_base<cui::c_thud_interaction_info> |
| `cui::c_thud_medal_display_widget` | `0x1966090` | `0x1965f80` | 26 | c_cui_container_widget |
| `cui::c_thud_objective_display_widget` | `0x1966390` | `0x1966280` | 26 | c_cui_container_widget |
| `cui::c_thud_pvp_objective_properties` | `0x19574d0` | `0x1957150` | 9 | cui::c_properties_accessor_base<cui::c_thud_pvp_objective_properties> |
| `cui::c_thud_racing_objective_data` | `0x1957760` | `0x19576f0` | 9 | cui::c_properties_accessor_base<cui::c_thud_racing_objective_data> |
| `cui::c_thud_racing_objective_data_component` | `0x19665d0` | `0x1966530` | 18 | c_cui_component |
| `cui::c_thud_radar_blip_container` | `0x1966800` | `0x19666f0` | 26 | c_cui_container_widget |
| `cui::c_thud_radar_widget` | `0x1966940` | `0x1966830` | 26 | c_cui_container_widget |
| `cui::c_thud_rift_objective_data` | `0x1957450` | `0x1957090` | 9 | cui::c_properties_accessor_base<cui::c_thud_rift_objective_data> |
| `cui::c_thud_salvage_objective_data` | `0x19573d0` | `0x1956fd0` | 9 | cui::c_properties_accessor_base<cui::c_thud_salvage_objective_data> |
| `cui::c_thud_weapon_properties` | `0x19572d0` | `0x1956e50` | 9 | cui::c_properties_accessor_base<cui::c_thud_weapon_properties> |
| `cui::c_thud_weapon_swap_container` | `0x1966bc0` | `0x1966ab0` | 26 | c_cui_container_widget |
| `cui::c_timer_modulo_component` | `0x1957810` | `0x1957790` | 18 | c_cui_component |
| `cui::c_timestamp_countdown_component` | `0x19565c0` | `0x1956540` | 18 | c_cui_component |
| `cui::c_title_safe_configuration_widget` | `0x1969520` | `0x1969410` | 26 | cui::c_arrangement_container_widget |
| `cui::c_tournament_result_data_component` | `0x1957c20` | `0x1957ba0` | 18 | c_cui_component |
| `cui::c_tracked_change_slot` | `0x194ed50` | `0x1951fa0` | 2 | cui::c_change_slot |
| `cui::c_vendor_interaction_request_handler` | `0x1963920` | `0x19638f0` | 5 | cui::c_investment_server_message_request_handler |
| `cui::c_version_number_component` | `0x19639d0` | `0x1963950` | 18 | c_cui_component |
| `cui::c_video_widget` | `0x1969660` | `0x1969550` | 26 | c_bitmap_widget_base |
| `cui::c_view_director_pane_component` | `0x195bf20` | `0x195be30` | 22 | c_event_handler_component |
| `cui::c_view_widget` | `0x1969800` | `0x19696d0` | 26 | c_cui_sizing_container_widget |
| `cui::c_view_widget::c_dynamic_properties_helper` | `0x19697e0` | `0x1969690` | 5 | cui::i_properties_layout |
| `cui::c_voice_channel_data_component` | `0x1967280` | `0x1967200` | 18 | c_cui_component |
| `cui::c_voice_channel_switcher_component` | `0x19673a0` | `0x19672b0` | 22 | c_event_handler_component |
| `cui::c_watermark_platform_account_data_component` | `0x1956670` | `0x19565f0` | 18 | c_cui_component |
| `cui::detail::c_member_function_change_slot<cui::c_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, cui::s_compiled_binding, &cui::s_compiled_binding::on_source_component_layout_change>` | `0x19515e0` | `0x19515d0` | 4 | cui::c_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x20 |
| `cui::detail::c_member_function_change_slot<cui::c_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, cui::s_compiled_binding, &cui::s_compiled_binding::on_source_property_element_change>` | `0x1951640` | `0x1951630` | 4 | cui::c_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x20 |
| `cui::detail::c_member_function_change_slot<cui::c_tracked_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, c_cui_component, &c_cui_component::on_render_dirty_change>` | `0x1951f30` | `0x1951f20` | 4 | cui::c_tracked_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x30 |
| `cui::detail::c_member_function_change_slot<cui::c_tracked_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, c_cui_sizing_container_widget, &c_cui_sizing_container_widget::on_sizing_widget_size_change>` | `0x1969280` | `0x1969270` | 4 | cui::c_tracked_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x30 |
| `cui::detail::c_member_function_change_slot<cui::c_tracked_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, c_gate_component, &c_gate_component::on_component_property_change>` | `0x194edb0` | `0x194ed30` | 6 | cui::c_tracked_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x30 |
| `cui::detail::c_member_function_change_slot<cui::c_tracked_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, c_list_widget, &c_list_widget::on_child_item_property_change>` | `0x196a800` | `0x196a7f0` | 4 | cui::c_tracked_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x30 |
| `cui::detail::c_member_function_change_slot<cui::c_tracked_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, c_list_widget, &c_list_widget::on_child_item_update_change>` | `0x196a860` | `0x196a850` | 4 | cui::c_tracked_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x30 |
| `cui::detail::c_member_function_change_slot<cui::c_tracked_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, c_row_selector_component, &c_row_selector_component::on_component_property_change>` | `0x1950190` | `0x1950180` | 4 | cui::c_tracked_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x30 |
| `cui::detail::c_member_function_change_slot<cui::c_tracked_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, c_text_widget, &c_text_widget::on_ascii_string_change>` | `0x1950d30` | `0x1950d20` | 4 | cui::c_tracked_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x30 |
| `cui::detail::c_member_function_change_slot<cui::c_tracked_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, c_text_widget, &c_text_widget::on_string_change>` | `0x1950d90` | `0x1950d80` | 4 | cui::c_tracked_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x30 |
| `cui::detail::c_member_function_change_slot<cui::c_tracked_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, cui::c_arrangement_container_widget, &cui::c_arrangement_container_widget::on_child_widget_property_change>` | `0x19523b0` | `0x19523a0` | 4 | cui::c_tracked_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x30 |
| `cui::detail::c_member_function_change_slot<cui::c_tracked_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, cui::c_arrangement_container_widget, &cui::c_arrangement_container_widget::on_self_width_height_property_change>` | `0x1952350` | `0x1952340` | 4 | cui::c_tracked_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x30 |
| `cui::detail::c_member_function_change_slot<cui::c_tracked_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, cui::c_flyout_widget, &cui::c_flyout_widget::on_flyout_data_change>` | `0x1968140` | `0x1968130` | 4 | cui::c_tracked_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x30 |
| `cui::detail::c_member_function_change_slot<cui::c_tracked_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, cui::c_flyout_widget, &cui::c_flyout_widget::on_sub_properties_layout_change>` | `0x19681a0` | `0x1968190` | 4 | cui::c_tracked_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x30 |
| `cui::detail::c_member_function_change_slot<cui::c_tracked_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, cui::c_investment_record_book_component, &cui::c_investment_record_book_component::refresh_pages_have_new_items_properties>` | `0x195f380` | `0x195f370` | 4 | cui::c_tracked_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x30 |
| `cui::detail::c_member_function_change_slot<cui::c_tracked_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, cui::c_list_view_widget, &cui::c_list_view_widget::on_child_item_property_change>` | `0x1968800` | `0x19687f0` | 4 | cui::c_tracked_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x30 |
| `cui::detail::c_member_function_change_slot<cui::c_tracked_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, cui::c_multi_decision_maker_component, &cui::c_multi_decision_maker_component::on_branch_change>` | `0x1954560` | `0x1954550` | 4 | cui::c_tracked_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x30 |
| `cui::detail::c_member_function_change_slot<cui::c_tracked_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, cui::c_properties_sequence_entry_selector, &cui::c_properties_sequence_entry_selector::on_sub_properties_layout_change>` | `0x19690e0` | `0x19690d0` | 4 | cui::c_tracked_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x30 |
| `cui::detail::c_member_function_change_slot<cui::c_tracked_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, cui::c_row_lookup_component, &cui::c_row_lookup_component::on_component_property_change>` | `0x19555f0` | `0x19555e0` | 4 | cui::c_tracked_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x30 |
| `cui::detail::c_member_function_change_slot<cui::c_tracked_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, cui::c_string_formatter_component, &cui::c_string_formatter_component::on_variable_change>` | `0x1956060` | `0x1956050` | 4 | cui::c_tracked_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x30 |
| `cui::detail::c_member_function_change_slot<cui::c_tracked_change_slot, ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, cui::c_view_widget, &cui::c_view_widget::on_sub_properties_layout_change>` | `0x1969840` | `0x1969830` | 4 | cui::c_tracked_change_slot, ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void> @+0x30 |
| `cui::i_flyout_data` | `0x1967fc8` |  |  |  |
| `cui::i_interface_provider` | `0x195d278` |  |  |  |
| `cui::i_investment_item_action_interface` | `0x195ce08` |  |  |  |
| `cui::i_investment_item_equip_interface` | `0x195ce18` |  |  |  |
| `cui::i_investment_item_infusion_interface` | `0x195d5b8` |  |  |  |
| `cui::i_investment_item_lockbox_overlay_interface` | `0x195ce28` |  |  |  |
| `cui::i_investment_item_precache_interface` | `0x195ce38` |  |  |  |
| `cui::i_investment_item_select_interface` | `0x195ce48` |  |  |  |
| `cui::i_investment_item_upsell_interface` | `0x19602e8` |  |  |  |
| `cui::i_properties` | `0x19674b8` | `0x1967470` | 11 |  |
| `cui::i_properties_layout` | `0x1951a48` |  |  |  |
| `cui::i_properties_sequence` | `0x194e058` |  |  |  |
| `cui::s_activity_requirements_not_met_entry` | `0x195ab50` | `0x195aae0` | 9 | cui::c_properties_accessor_base<cui::s_activity_requirements_not_met_entry> |
| `cui::s_activity_skull_modifier` | `0x195a410` | `0x195a3a0` | 9 | cui::c_properties_accessor_base<cui::s_activity_skull_modifier> |
| `cui::s_activity_type_unlock_requirement` | `0x195a680` | `0x195a610` | 9 | cui::c_properties_accessor_base<cui::s_activity_type_unlock_requirement> |
| `cui::s_bootflow_installer_checklist_item` | `0x1957ef0` | `0x1957d70` | 9 | cui::c_properties_accessor_base<cui::s_bootflow_installer_checklist_item> |
| `cui::s_chain_animation_entry` | `0x1967c40` | `0x1967bd0` | 9 | cui::c_properties_accessor_base<cui::s_chain_animation_entry> |
| `cui::s_character_class_bucket` | `0x19592a0` | `0x1959230` | 9 | cui::c_properties_accessor_base<cui::s_character_class_bucket> |
| `cui::s_character_class_data` | `0x1959200` | `0x1959190` | 9 | cui::c_properties_accessor_base<cui::s_character_class_data> |
| `cui::s_character_customization_category_data_container` | `0x1959f50` | `0x1959ee0` | 9 | cui::c_properties_accessor_base<cui::s_character_customization_category_data_container> |
| `cui::s_character_customization_category_hotspot_data` | `0x1959ff0` | `0x1959f80` | 9 | cui::c_properties_accessor_base<cui::s_character_customization_category_hotspot_data> |
| `cui::s_character_customization_option_data` | `0x1959bf0` | `0x1959b80` | 9 | cui::c_properties_accessor_base<cui::s_character_customization_option_data> |
| `cui::s_character_race_bucket` | `0x1958c40` | `0x19589c0` | 9 | cui::c_properties_accessor_base<cui::s_character_race_bucket> |
| `cui::s_countdown_data` | `0x19546d0` | `0x1954660` | 9 | cui::c_properties_accessor_base<cui::s_countdown_data> |
| `cui::s_director_book_info` | `0x195b340` | `0x195b2d0` | 9 | cui::c_properties_accessor_base<cui::s_director_book_info> |
| `cui::s_faction_display_data` | `0x19579b0` | `0x1957940` | 9 | cui::c_properties_accessor_base<cui::s_faction_display_data> |
| `cui::s_fireteam_member_info` | `0x195c3d0` | `0x195c360` | 9 | cui::c_properties_accessor_base<cui::s_fireteam_member_info> |
| `cui::s_fireteam_privacy_option` | `0x195c5b0` | `0x195c540` | 9 | cui::c_properties_accessor_base<cui::s_fireteam_privacy_option> |
| `cui::s_inventory_flyout_identifier` | `0x195cec0` | `0x195cdc0` | 19 | cui::c_properties_accessor_base<cui::s_inventory_flyout_identifier> |
| `cui::s_investment_item_details_screen_data` | `0x195d240` | `0x195d1d0` | 9 | cui::c_properties_accessor_base<cui::s_investment_item_details_screen_data> |
| `cui::s_investment_item_record_book_info` | `0x195dbd0` | `0x195db60` | 9 | cui::c_properties_accessor_base<cui::s_investment_item_record_book_info> |
| `cui::s_investment_item_record_book_reward_item_info` | `0x195d9f0` | `0x195d980` | 9 | cui::c_properties_accessor_base<cui::s_investment_item_record_book_reward_item_info> |
| `cui::s_investment_item_stat` | `0x19539c0` | `0x1953950` | 9 | cui::c_properties_accessor_base<cui::s_investment_item_stat> |
| `cui::s_investment_item_stat_meter` | `0x195f990` | `0x195f920` | 9 | cui::c_properties_accessor_base<cui::s_investment_item_stat_meter> |
| `cui::s_investment_material_requirement` | `0x195e090` | `0x195e020` | 9 | cui::c_properties_accessor_base<cui::s_investment_material_requirement> |
| `cui::s_investment_perk_info` | `0x1963570` | `0x1963500` | 9 | cui::c_properties_accessor_base<cui::s_investment_perk_info> |
| `cui::s_investment_requirement_description` | `0x1960940` | `0x19608d0` | 9 | cui::c_properties_accessor_base<cui::s_investment_requirement_description> |
| `cui::s_investment_unlock_flag` | `0x195e180` | `0x195e110` | 9 | cui::c_properties_accessor_base<cui::s_investment_unlock_flag> |
| `cui::s_investment_vendor_pagination_settings` | `0x1960360` | `0x19600e0` | 9 | cui::c_properties_accessor_base<cui::s_investment_vendor_pagination_settings> |
| `cui::s_login_character_info` | `0x195ed50` | `0x195ece0` | 9 | cui::c_properties_accessor_base<cui::s_login_character_info> |
| `cui::s_options_bucket` | `0x1954be0` | `0x1954900` | 9 | cui::c_properties_accessor_base<cui::s_options_bucket> |
| `cui::s_options_bucket_display` | `0x1955080` | `0x1955010` | 9 | cui::c_properties_accessor_base<cui::s_options_bucket_display> |
| `cui::s_options_bucket_flyout` | `0x1954ae0` | `0x1954a80` | 11 | cui::i_flyout_data |
| `cui::s_options_setting` | `0x1954ba0` | `0x19548a0` | 9 | cui::c_properties_accessor_base<cui::s_options_setting> |
| `cui::s_options_value` | `0x1954b60` | `0x1954840` | 9 | cui::c_properties_accessor_base<cui::s_options_value> |
| `cui::s_player_nameplate` | `0x195ecb0` | `0x195ec40` | 9 | cui::c_properties_accessor_base<cui::s_player_nameplate> |
| `cui::s_player_option` | `0x1961290` | `0x1961220` | 9 | cui::c_properties_accessor_base<cui::s_player_option> |
| `cui::s_post_game_reward` | `0x1963d50` | `0x1963ce0` | 9 | cui::c_properties_accessor_base<cui::s_post_game_reward> |
| `cui::s_report_reason` | `0x1961610` | `0x1961480` | 9 | cui::c_properties_accessor_base<cui::s_report_reason> |
| `cui::s_roster_contact_group` | `0x1962b80` | `0x1962b10` | 9 | cui::c_properties_accessor_base<cui::s_roster_contact_group> |
| `cui::s_score_stat_group_info` | `0x1964240` | `0x19641d0` | 9 | cui::c_properties_accessor_base<cui::s_score_stat_group_info> |
| `cui::s_score_stat_info` | `0x1964b60` | `0x1964af0` | 9 | cui::c_properties_accessor_base<cui::s_score_stat_info> |
| `cui::s_scoreboard_secondary_stat_info` | `0x19642e0` | `0x1964270` | 9 | cui::c_properties_accessor_base<cui::s_scoreboard_secondary_stat_info> |
| `cui::s_screen_load_parameters` | `0x195e600` | `0x195e590` | 9 | cui::c_properties_accessor_base<cui::s_screen_load_parameters> |
| `cui::s_talent_basic_node_input_data_container` | `0x1963180` | `0x1963110` | 9 | cui::c_properties_accessor_base<cui::s_talent_basic_node_input_data_container> |
| `cui::s_tracked_inventory_item_data` | `0x195c9d0` | `0x195c960` | 9 | cui::c_properties_accessor_base<cui::s_tracked_inventory_item_data> |

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
