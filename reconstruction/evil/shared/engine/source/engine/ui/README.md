# ui/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `engine.ui`  
**Folder path evidence:** `HYPOTHESIS` (folder name is a proposal from RTTI/log-channel clustering, not a recovered path)  
**Role:** ui:: core containers and properties

## Sub-folders

- [`cui/`](cui/README.md) — cui:: screens, widgets, event-handler components

## Source files named in the binary

_None recovered (retail build stripped most asserts)._

## Decompiled functions

_None yet._

## Classes (216)

Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. Placement in this folder is `HYPOTHESIS` (name-token rule).

| class | typeinfo | vtable | virtual slots | bases |
|---|---|---|---|---|
| `font::c_face_map` | `0x19498a8` |  |  |  |
| `font::c_freetype_cache` | `0x1949930` | `0x19498d0` | 6 | font::ft::c_allocator, font::c_face_map @+0x28 |
| `font::ft::c_allocator` | `0x19499b0` | `0x1949980` | 5 | FT_MemoryRec_ @+0x8 |
| `ui::c_empty_base<s_rich_text_deleter, 0, void>` | `0x1949a30` |  |  | s_rich_text_deleter |
| `ui::c_empty_base<ui::c_indirect_allocator<cui::c_screen_change_slot_pools>, 0, void>` | `0x194ed80` |  |  | ui::c_indirect_allocator<cui::c_screen_change_slot_pools> |
| `ui::c_empty_base<ui::c_tag_loader::s_handle_request_deleter, 0, void>` | `0x1969bc0` |  |  | ui::c_tag_loader::s_handle_request_deleter |
| `ui::c_empty_base<ui::c_tag_loader::s_investment_item_request_deleter, 0, void>` | `0x1969b10` |  |  | ui::c_tag_loader::s_investment_item_request_deleter |
| `ui::c_empty_base<ui::c_tag_loader::s_investment_talent_grid_request_deleter, 0, void>` | `0x1969a60` |  |  | ui::c_tag_loader::s_investment_talent_grid_request_deleter |
| `ui::c_empty_base<ui::s_allocator, 0, void>` | `0x195a8f0` |  |  | ui::s_allocator |
| `ui::c_enable_shared_from_this<cui::c_character_customization_category_flyout>` | `0x1959a28` |  |  |  |
| `ui::c_fullscreen_fx_manager` | `0x1969930` | `0x1969900` | 8 | c_game_system_interface |
| `ui::c_indirect_allocator<cui::c_screen_change_slot_pools>` | `0x194ed68` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_activity_reward_info>, 4ul>` | `0x195ad08` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_activity_reward_info>, 6ul>` | `0x195f658` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_character_customization_option_bucket>, 4ul>` | `0x1959da8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_character_race_gender_data>, 2ul>` | `0x1959128` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_character_race_gender_data>, 8ul>` | `0x1958f88` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_dialog_option>, 4ul>` | `0x194e068` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_director_activity>, 6ul>` | `0x195bcb8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_backpack_item>, 340ul>` | `0x195d118` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_backpack_slot>, 6ul>` | `0x195d048` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_infusion_item>, 15ul>` | `0x195d688` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_item_activity_score>, 12ul>` | `0x195dd58` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_item_record_node_info>, 4ul>` | `0x195d848` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_objective_item>, 1ul>` | `0x195f6d8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_objective_item>, 8ul>` | `0x195df18` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_progression>, 32ul>` | `0x195c178` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_progression>, 4ul>` | `0x195b3d8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_record_book_reward_item>, 16ul>` | `0x195f558` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_record_node_info>, 8ul>` | `0x195f5d8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_record_page_info>, 20ul>` | `0x195f438` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_vendor_bucket>, 32ul>` | `0x1960478` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_vendor_interaction_reply>, 4ul>` | `0x195fc98` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_vendor_item>, 14ul>` | `0x1960618` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_vendor_item>, 4ul>` | `0x1964a88` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_vendor_item>, 84ul>` | `0x1960818` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_vendor_item>, 8ul>` | `0x1960548` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_investment_vendor_refund_receipt>, 30ul>` | `0x195ffd8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_orbit_team_container>, 12ul>` | `0x1960fe8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_private_lobby_option_bucket>, 16ul>` | `0x1961cb8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_private_lobby_option_value>, 64ul>` | `0x1961be8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_quest_step_container>, 20ul>` | `0x1962038` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_racing_player_data>, 6ul>` | `0x1966688` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_roster_contact_id_container>, 110ul>` | `0x1962768` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_roster_contact_id_container>, 12ul>` | `0x1960d18` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_roster_contact_id_container>, 20ul>` | `0x1962bc8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_scoreboard_player_info>, 16ul>` | `0x19643f8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_scoreboard_team_info>, 16ul>` | `0x1964118` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_tab_data>, 6ul>` | `0x1956428` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_thud_control_point_properties>, 8ul>` | `0x1957688` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_thud_interaction_info>, 3ul>` | `0x1965f18` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::c_thud_weapon_properties>, 3ul>` | `0x1957568` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::i_properties>, 32ul>` | `0x1968288` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::i_properties>, 60ul>` | `0x1968e18` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_activity_requirements_not_met_entry>, 4ul>` | `0x195abe8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_activity_skull_modifier>, 8ul>` | `0x195a338` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_activity_type_unlock_requirement>, 16ul>` | `0x195a5a8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_bootflow_installer_checklist_item>, 16ul>` | `0x1957f88` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_character_class_data>, 4ul>` | `0x1958dc8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_character_customization_category_data_container>, 30ul>` | `0x1959c88` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_character_customization_option_data>, 30ul>` | `0x1959e78` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_character_race_bucket>, 4ul>` | `0x1959058` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_fireteam_member_info>, 12ul>` | `0x195c2f8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_fireteam_privacy_option>, 5ul>` | `0x195c6c8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_item_stat>, 16ul>` | `0x19635b8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_item_stat>, 5ul>` | `0x1963bc8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_item_stat>, 6ul>` | `0x19538e8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_item_stat_meter>, 16ul>` | `0x195f8b8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_material_requirement>, 8ul>` | `0x195e298` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_perk_info>, 18ul>` | `0x1953868` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_perk_info>, 6ul>` | `0x195d918` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_requirement_description>, 4ul>` | `0x19603f8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_requirement_description>, 9ul>` | `0x1963028` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_investment_unlock_flag>, 4ul>` | `0x195e1c8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_login_character_info>, 10ul>` | `0x195ebd8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_options_bucket_display>, 12ul>` | `0x1954d68` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_options_setting>, 5ul>` | `0x1954ed8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_options_value>, 10ul>` | `0x1954fa8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_player_option>, 12ul>` | `0x19611b8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_post_game_reward>, 10ul>` | `0x1963de8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_report_reason>, 10ul>` | `0x19616a8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_roster_contact_group>, 20ul>` | `0x1962aa8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_score_stat_group_info>, 2ul>` | `0x19646a8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_score_stat_group_info>, 6ul>` | `0x1964778` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_score_stat_info>, 16ul>` | `0x1964328` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_score_stat_info>, 2ul>` | `0x1964898` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_score_stat_info>, 6ul>` | `0x19649b8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_scoreboard_secondary_stat_info>, 2ul>` | `0x1964098` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_talent_basic_node_input_data_container>, 8ul>` | `0x1962fa8` |  |  |  |
| `ui::c_static_vector<ui::c_shared_ptr<cui::s_tracked_inventory_item_data>, 4ul>` | `0x195c8f8` |  |  |  |
| `ui::c_tag_loader::s_handle_request_deleter` | `0x1969bb0` |  |  |  |
| `ui::c_tag_loader::s_investment_item_request_deleter` | `0x1969b00` |  |  |  |
| `ui::c_tag_loader::s_investment_talent_grid_request_deleter` | `0x1969a50` |  |  |  |
| `ui::c_vector<ui::c_shared_ptr<cui::c_roster_contact_id_container>, ui::s_allocator>` | `0x195a920` |  |  | ui::c_empty_base<ui::s_allocator, 0, void> |
| `ui::detail::c_shared_ptr_tracker<cui::c_activity_reward_info>` | `0x195acc0` | `0x195aca0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_character_class_bucket_flyout>` | `0x1958c90` | `0x1958c70` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_character_customization_category_flyout>` | `0x1959b00` | `0x1959ae0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_character_customization_option_bucket>` | `0x1959c40` | `0x1959c20` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_character_race_gender_bucket_flyout>` | `0x1958ce0` | `0x1958cc0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_character_race_gender_data>` | `0x1958ea0` | `0x1958e80` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_dialog_option>` | `0x194df20` | `0x194df00` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_director_activity>` | `0x195bc20` | `0x195bc00` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_dynamic_properties_sequence<ui::c_shared_ptr<cui::c_roster_contact_id_container> > >` | `0x195a890` | `0x195a870` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_investment_backpack_item>` | `0x195cf60` | `0x195cf40` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_investment_backpack_slot>` | `0x195d2e0` | `0x195d2c0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_investment_backpack_slot_flyout>` | `0x195d330` | `0x195d310` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_investment_infusion_item>` | `0x195d640` | `0x195d620` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_investment_item_activity_score>` | `0x195dd10` | `0x195dcf0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_investment_item_lockbox_overlay_token>` | `0x195d000` | `0x195cfe0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_investment_item_record_node_info>` | `0x195db30` | `0x195db10` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_investment_objective_item>` | `0x195ded0` | `0x195deb0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_investment_progression>` | `0x195b390` | `0x195b370` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_investment_record_book_reward_item>` | `0x195f4c0` | `0x195f4a0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_investment_record_node_info>` | `0x195f510` | `0x195f4f0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_investment_record_page_info>` | `0x195f3f0` | `0x195f3d0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_investment_vendor_bucket>` | `0x1960780` | `0x1960760` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_investment_vendor_interaction_reply>` | `0x195fc50` | `0x195fc30` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_investment_vendor_item>` | `0x19607d0` | `0x19607b0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_investment_vendor_refund_receipt>` | `0x195ff90` | `0x195ff70` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_load_details_screen_destruction_callback>` | `0x195e560` | `0x195e540` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_load_screen_destruction_callback>` | `0x1950370` | `0x1950350` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_orbit_team_container>` | `0x1960fa0` | `0x1960f80` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_private_lobby_option_bucket>` | `0x1961b50` | `0x1961b30` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_private_lobby_option_value>` | `0x1961ba0` | `0x1961b80` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_properties_set<cui::c_roster_contact_id_container, 10ul, cui::c_roster_contact_id_container::s_identifier_ordering> >` | `0x195a9c0` | `0x195a9a0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_quest_step_container>` | `0x1961ff0` | `0x1961fd0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_racing_player_data>` | `0x1966640` | `0x1966620` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_roster_contact_id_container>` | `0x195aa10` | `0x195a9f0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_scoreboard_player_info>` | `0x19641a0` | `0x1964180` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_scoreboard_team_info>` | `0x1964000` | `0x1963fe0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_activity_reward_info>, 4ul> >` | `0x195ad90` | `0x195ad70` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_character_customization_option_bucket>, 4ul> >` | `0x1959d60` | `0x1959d40` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_character_race_gender_data>, 2ul> >` | `0x19590e0` | `0x19590c0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_character_race_gender_data>, 8ul> >` | `0x1958f40` | `0x1958f20` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_director_activity>, 6ul> >` | `0x195bc70` | `0x195bc50` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_backpack_item>, 340ul> >` | `0x195d0d0` | `0x195d0b0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_item_activity_score>, 12ul> >` | `0x195dde0` | `0x195ddc0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_item_record_node_info>, 4ul> >` | `0x195d800` | `0x195d7e0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_objective_item>, 8ul> >` | `0x195dfa0` | `0x195df80` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_vendor_item>, 14ul> >` | `0x19605d0` | `0x19605b0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_vendor_item>, 4ul> >` | `0x1964a40` | `0x1964a20` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_vendor_item>, 84ul> >` | `0x19608a0` | `0x1960880` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_investment_vendor_item>, 8ul> >` | `0x1960500` | `0x19604e0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_private_lobby_option_value>, 64ul> >` | `0x1961c70` | `0x1961c50` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_roster_contact_id_container>, 12ul> >` | `0x1961070` | `0x1961050` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_roster_contact_id_container>, 20ul> >` | `0x1962c50` | `0x1962c30` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_scoreboard_player_info>, 16ul> >` | `0x1964480` | `0x1964460` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::c_thud_control_point_properties>, 8ul> >` | `0x1957640` | `0x1957620` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_activity_requirements_not_met_entry>, 4ul> >` | `0x195ac70` | `0x195ac50` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_activity_skull_modifier>, 8ul> >` | `0x195a2f0` | `0x195a2d0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_activity_type_unlock_requirement>, 16ul> >` | `0x195a560` | `0x195a540` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_character_class_data>, 4ul> >` | `0x1958d80` | `0x1958d60` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_character_customization_option_data>, 30ul> >` | `0x1959e30` | `0x1959e10` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_character_race_bucket>, 4ul> >` | `0x1959010` | `0x1958ff0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_investment_item_stat>, 16ul> >` | `0x1963640` | `0x1963620` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_investment_item_stat>, 5ul> >` | `0x1963b80` | `0x1963b60` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_investment_material_requirement>, 8ul> >` | `0x195e320` | `0x195e300` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_investment_perk_info>, 6ul> >` | `0x195d8d0` | `0x195d8b0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_investment_unlock_flag>, 4ul> >` | `0x195e250` | `0x195e230` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_options_setting>, 5ul> >` | `0x1954e90` | `0x1954e70` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_options_value>, 10ul> >` | `0x1954f60` | `0x1954f40` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_score_stat_group_info>, 2ul> >` | `0x1964730` | `0x1964710` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_score_stat_group_info>, 6ul> >` | `0x1964800` | `0x19647e0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_score_stat_info>, 16ul> >` | `0x19643b0` | `0x1964390` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_score_stat_info>, 2ul> >` | `0x1964850` | `0x1964830` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_static_properties_sequence<ui::c_shared_ptr<cui::s_score_stat_info>, 6ul> >` | `0x1964970` | `0x1964950` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_tab_data>` | `0x19563e0` | `0x19563c0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_thud_control_point_properties>` | `0x19575f0` | `0x19575d0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_thud_interaction_info>` | `0x1965ed0` | `0x1965eb0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::c_thud_weapon_properties>` | `0x1957520` | `0x1957500` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_activity_requirements_not_met_entry>` | `0x195aba0` | `0x195ab80` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_activity_skull_modifier>` | `0x195a2a0` | `0x195a280` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_activity_type_unlock_requirement>` | `0x195a510` | `0x195a4f0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_bootflow_installer_checklist_item>` | `0x1957f40` | `0x1957f20` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_character_class_bucket>` | `0x1958e50` | `0x1958e30` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_character_class_data>` | `0x1958d30` | `0x1958d10` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_character_customization_category_data_container>` | `0x1959ab0` | `0x1959a90` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_character_customization_category_hotspot_data>` | `0x1959d10` | `0x1959cf0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_character_customization_option_data>` | `0x1959b50` | `0x1959b30` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_character_race_bucket>` | `0x1958ef0` | `0x1958ed0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_faction_display_data>` | `0x1964570` | `0x1964550` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_fireteam_member_info>` | `0x195c2b0` | `0x195c290` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_fireteam_privacy_option>` | `0x195c600` | `0x195c5e0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_investment_item_record_book_info>` | `0x195dc20` | `0x195dc00` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_investment_item_record_book_reward_item_info>` | `0x195da40` | `0x195da20` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_investment_item_stat>` | `0x19537d0` | `0x19537b0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_investment_item_stat_meter>` | `0x195f870` | `0x195f850` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_investment_material_requirement>` | `0x195dff0` | `0x195dfd0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_investment_perk_info>` | `0x1953780` | `0x1953760` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_investment_requirement_description>` | `0x19603b0` | `0x1960390` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_investment_unlock_flag>` | `0x195e0e0` | `0x195e0c0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_login_character_info>` | `0x195eb90` | `0x195eb70` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_options_bucket>` | `0x1954c80` | `0x1954c60` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_options_bucket_flyout>` | `0x19550d0` | `0x19550b0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_options_setting>` | `0x1954df0` | `0x1954dd0` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_options_value>` | `0x1954e40` | `0x1954e20` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_player_option>` | `0x1961170` | `0x1961150` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_post_game_reward>` | `0x1963da0` | `0x1963d80` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_report_reason>` | `0x1961660` | `0x1961640` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_roster_contact_group>` | `0x1962a60` | `0x1962a40` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_score_stat_group_info>` | `0x1963f60` | `0x1963f40` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_score_stat_info>` | `0x1964920` | `0x1964900` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_scoreboard_secondary_stat_info>` | `0x1963fb0` | `0x1963f90` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_talent_basic_node_input_data_container>` | `0x1962f60` | `0x1962f40` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<cui::s_tracked_inventory_item_data>` | `0x195c8b0` | `0x195c890` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<ui::c_tab_list_stack>` | `0x1969da0` | `0x1969d80` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker<ui::c_texture_camera_instance_handle>` | `0x1969d50` | `0x1969d30` | 6 | ui::detail::c_shared_tracker |
| `ui::detail::c_shared_ptr_tracker_with_deleter<ui::s_rich_text, s_rich_text_deleter>` | `0x1949a60` | `0x1949a00` | 8 | ui::detail::c_shared_tracker, ui::c_empty_base<s_rich_text_deleter, 0, void> @+0x10 |
| `ui::detail::c_shared_ptr_tracker_with_deleter_and_allocator<ui::c_tag_loader::c_handle_request, ui::c_tag_loader::s_handle_request_deleter, ui::c_indirect_allocator<ui::c_tag_loader::c_tracker_allocator> >` | `0x1969bf0` | `0x1969b90` | 8 | ui::detail::c_shared_tracker, ui::c_empty_base<ui::c_tag_loader::s_handle_request_deleter, 0, void> @+0x10 |
| `ui::detail::c_shared_ptr_tracker_with_deleter_and_allocator<ui::c_tag_loader::c_investment_item_request, ui::c_tag_loader::s_investment_item_request_deleter, ui::c_indirect_allocator<ui::c_tag_loader::c_tracker_allocator> >` | `0x1969b40` | `0x1969ae0` | 8 | ui::detail::c_shared_tracker, ui::c_empty_base<ui::c_tag_loader::s_investment_item_request_deleter, 0, void> @+0x10 |
| `ui::detail::c_shared_ptr_tracker_with_deleter_and_allocator<ui::c_tag_loader::c_investment_talent_grid_request, ui::c_tag_loader::s_investment_talent_grid_request_deleter, ui::c_indirect_allocator<ui::c_tag_loader::c_tracker_allocator> >` | `0x1969a90` | `0x1969a30` | 8 | ui::detail::c_shared_tracker, ui::c_empty_base<ui::c_tag_loader::s_investment_talent_grid_request_deleter, 0, void> @+0x10 |
| `ui::detail::c_shared_tracker` | `0x1949aa0` |  |  |  |
| `ui::detail::s_cinematic_texture_camera_instance` | `0x1969cb0` | `0x1969c50` | 6 | ui::detail::s_texture_camera_instance @+0x8, ui::i_cinematic_texture_camera_simulation_queue_callback, s_object_iteration_interface @+0x10 |
| `ui::detail::s_texture_camera_instance` | `0x1969cf8` |  |  |  |
| `ui::i_cinematic_texture_camera_simulation_queue_callback` | `0x1969c30` |  |  |  |
| `ui::s_allocator` | `0x195a8d8` |  |  |  |

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
