# incidents/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `omaha.incidents`  
**Folder path evidence:** `HYPOTHESIS` (folder name is a proposal from RTTI/log-channel clustering, not a recovered path)  
**Role:** incident metadata, announcement, heat

## Source files named in the binary

_None recovered (retail build stripped most asserts)._

## Decompiled functions

_None yet._

## Classes (74)

Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. Placement in this folder is `HYPOTHESIS` (name-token rule).

| class | typeinfo | vtable | virtual slots | bases |
|---|---|---|---|---|
| `c_accumulated_incident_metadata_interface` | `0x190a020` | `0x1909fc0` | 14 | c_basic_incident_metadata_interface |
| `c_activity_complete_incident_metadata_interface` | `0x190a2b0` | `0x190a240` | 16 | c_incident_metadata_with_specialization_interface |
| `c_activity_incident_metadata_interface` | `0x190a3c0` | `0x190a350` | 16 | c_incident_metadata_with_specialization_interface |
| `c_activity_join_incident_metadata_interface` | `0x190a4a0` | `0x190a430` | 16 | c_incident_metadata_with_specialization_interface |
| `c_basic_incident_metadata_interface` | `0x190a060` |  |  | i_incident_metadata |
| `c_buffed_kill_incident_metadata_interface` | `0x1938d00` | `0x1938c90` | 16 | c_incident_metadata_with_specialization_interface |
| `c_capturable_incident_metadata_interface` | `0x1938de0` | `0x1938d70` | 16 | c_incident_metadata_with_specialization_interface |
| `c_cinematic_incident_metadata_interface` | `0x190a570` | `0x190a510` | 14 | c_basic_incident_metadata_interface |
| `c_debug_incident_metadata_interface` | `0x190a650` | `0x190a5e0` | 16 | c_incident_metadata_with_specialization_interface |
| `c_emote_incident_metadata_interface` | `0x190a730` | `0x190a6c0` | 16 | c_incident_metadata_with_specialization_interface |
| `c_engagement_incident_metadata_interface` | `0x1938ec0` | `0x1938e50` | 16 | c_incident_metadata_with_specialization_interface |
| `c_engine_kill_incident_metadata_interface` | `0x190ad20` | `0x190ac40` | 13 | c_kill_incident_metadata_base_interface |
| `c_faction_incident_metadata_interface` | `0x190a800` | `0x190a7a0` | 14 | c_basic_incident_metadata_interface |
| `c_fireteam_incident_metadata_interface` | `0x190a8d0` | `0x190a870` | 14 | c_basic_incident_metadata_interface |
| `c_flanked_kill_incident_metadata_interface` | `0x1938fa0` | `0x1938f30` | 16 | c_incident_metadata_with_specialization_interface |
| `c_gather_material_incident_metadata_interface` | `0x190a9b0` | `0x190a940` | 16 | c_incident_metadata_with_specialization_interface |
| `c_incident_announcement_game_system` | `0x1938730` | `0x19386e0` | 9 | i_activity_game_system |
| `c_incident_client_globals` | `0x1938970` | `0x19388c0` | 21 | c_incident_shim_globals_base |
| `c_incident_client_shim` | `0x19389f0` | `0x19389a0` | 9 | c_incident_shim_base |
| `c_incident_faction_interface_client` | `0x190a0a0` | `0x190a090` | 4 | i_incident_faction |
| `c_incident_game_system` | `0x19399f0` | `0x19399a0` | 9 | i_activity_game_system |
| `c_incident_heat_game_system` | `0x19387d0` | `0x1938780` | 9 | i_activity_game_system |
| `c_incident_metadata_none_interface` | `0x190aa40` | `0x190a9e0` | 14 | c_basic_incident_metadata_interface |
| `c_incident_metadata_with_specialization_interface` | `0x190a2e0` | `0x190ad70` | 14 | i_incident_metadata |
| `c_incident_metadata_with_specialization_specialization_interface` | `0x190ae00` | `0x190adf0` | 4 | i_incident_metadata_specialization |
| `c_incident_metadata_worldserver_item_interface` | `0x190aef0` | `0x190ae80` | 16 | c_incident_metadata_with_specialization_interface |
| `c_incident_metadata_worldserver_kill_interface` | `0x190af90` | `0x190af20` | 16 | c_incident_metadata_with_specialization_interface |
| `c_incident_metadata_worldserver_progression_interface` | `0x190b070` | `0x190b000` | 16 | c_incident_metadata_with_specialization_interface |
| `c_incident_metadata_worldserver_talent_grid_interface` | `0x190b150` | `0x190b0e0` | 16 | c_incident_metadata_with_specialization_interface |
| `c_incident_networking_game_system` | `0x1940e30` | `0x1940e00` | 8 | c_game_system_interface |
| `c_incident_player_interface_client` | `0x190bbf0` | `0x190bbd0` | 6 | i_incident_player |
| `c_incident_player_interface_client_identity` | `0x1938a40` | `0x1938a20` | 6 | c_incident_player_interface_shared_identity |
| `c_incident_player_interface_shared_identity` | `0x190bc10` |  |  | i_incident_player |
| `c_incident_player_interface_unknown` | `0x190bc60` | `0x190bc40` | 6 | i_incident_player |
| `c_incident_reward_site_finder` | `0x190fd60` | `0x190fcb0` | 7 | c_reward_site_finder<s_investment_incident_reward> |
| `c_incident_shim_base` | `0x1938c20` |  |  | i_incident_shim |
| `c_incident_shim_globals_base` | `0x1938bf0` | `0x1938b40` | 21 | i_incident_shim_globals |
| `c_incident_worldserver_shim` | `0x190a170` | `0x190a120` | 9 | i_incident_shim |
| `c_insertion_point_incident_metadata_interface` | `0x190b230` | `0x190b1c0` | 16 | c_incident_metadata_with_specialization_interface |
| `c_inspiration_incident_metadata_interface` | `0x190b2d0` | `0x190b260` | 16 | c_incident_metadata_with_specialization_interface |
| `c_interaction_incident_metadata_interface` | `0x1939200` | `0x1939190` | 16 | c_incident_metadata_with_specialization_interface |
| `c_invalid_incident_metadata_interface` | `0x190ad40` | `0x190acc0` | 14 | c_basic_incident_metadata_interface |
| `c_inventory_incident_metadata_interface` | `0x19392e0` | `0x1939270` | 16 | c_incident_metadata_with_specialization_interface |
| `c_kill_confirmed_pickup_incident_metadata_interface` | `0x19393b0` | `0x1939350` | 14 | c_basic_incident_metadata_interface |
| `c_kill_incident_metadata_base_interface` | `0x190b350` |  |  | i_incident_metadata |
| `c_kill_incident_metadata_base_networking_definition` | `0x190b320` | `0x190b300` | 3 | i_incident_metadata_networking |
| `c_kill_incident_metadata_interface` | `0x1939520` | `0x19394b0` | 13 | c_kill_incident_metadata_base_interface |
| `c_kill_incident_metadata_networking_definition` | `0x1939440` | `0x1939420` | 3 | i_incident_metadata_networking |
| `c_kill_incident_metadata_specialization_definition` | `0x19393f0` | `0x19393e0` | 4 | i_incident_metadata_specialization |
| `c_perk_incident_metadata_interface` | `0x190b440` | `0x190b3d0` | 16 | c_incident_metadata_with_specialization_interface |
| `c_player_faction_incident_metadata_interface` | `0x190b520` | `0x190b4b0` | 16 | c_incident_metadata_with_specialization_interface |
| `c_player_fireteam_incident_metadata_interface` | `0x190b5f0` | `0x190b590` | 14 | c_basic_incident_metadata_interface |
| `c_player_incident_metadata_interface` | `0x190b6d0` | `0x190b660` | 16 | c_incident_metadata_with_specialization_interface |
| `c_player_orb_incident_metadata_interface` | `0x190b7b0` | `0x190b740` | 16 | c_incident_metadata_with_specialization_interface |
| `c_player_time_incident_metadata_interface` | `0x190b8c0` | `0x190b860` | 14 | c_basic_incident_metadata_interface |
| `c_player_trigger_incident_metadata_interface` | `0x190b9a0` | `0x190b930` | 16 | c_incident_metadata_with_specialization_interface |
| `c_public_event_incident_metadata_interface` | `0x190ba80` | `0x190ba10` | 16 | c_incident_metadata_with_specialization_interface |
| `c_racing_lap_complete_incident_metadata_interface` | `0x190bba0` | `0x190bb30` | 16 | c_incident_metadata_with_specialization_interface |
| `c_recover_incident_metadata_interface` | `0x1939600` | `0x1939590` | 16 | c_incident_metadata_with_specialization_interface |
| `c_rescue_incident_metadata_interface` | `0x19396e0` | `0x1939670` | 16 | c_incident_metadata_with_specialization_interface |
| `c_resurrection_incident_metadata_interface` | `0x19397c0` | `0x1939750` | 16 | c_incident_metadata_with_specialization_interface |
| `c_score_incident_metadata_interface` | `0x1939890` | `0x1939830` | 14 | c_basic_incident_metadata_interface |
| `c_sequence_incident_metadata_interface` | `0x1939970` | `0x1939900` | 16 | c_incident_metadata_with_specialization_interface |
| `c_simulation_incident_event_definition` | `0x196f3d0` | `0x196f350` | 15 | c_simulation_schematized_event_definition<s_simulation_event_incident_data> |
| `c_simulation_queue_activity_client_incident_definition` | `0x196e8f0` | `0x196e5e0` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_queue_activity_client_incident_data> |
| `c_simulation_queue_send_voice_incident_definition` | `0x196c3d0` | `0x196c3b0` | 3 | c_simulation_queue_element_schematized_definition<s_simulation_queue_voice_incident_payload> |
| `i_incident_engine_shim` | `0x190a0f0` |  |  |  |
| `i_incident_faction` | `0x190a0b8` |  |  |  |
| `i_incident_metadata` | `0x190a048` |  |  |  |
| `i_incident_metadata_networking` | `0x190b368` |  |  |  |
| `i_incident_metadata_specialization` | `0x190ae18` |  |  |  |
| `i_incident_player` | `0x190a1a0` |  |  |  |
| `i_incident_shim` | `0x190a188` |  |  |  |
| `i_incident_shim_globals` | `0x190a0d0` |  |  |  |

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
