# networking/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `omaha.networking`  
**Folder path evidence:** `CONFIRMED_BINARY`  
**Role:** sessions, channels, STUN, DemonWare, signon (log 'networking:*')

## Sub-folders

- [`bap/`](bap/README.md) — BAP connection/message queues, investment BAP messages
- [`delivery/`](delivery/README.md) — network_link

## Source files named in the binary

_None recovered (retail build stripped most asserts)._

## Decompiled functions

| VA | name | class | evidence | pseudo-C | role |
|---|---|---|---|---|---|
| `0xadec40` | network_config_snapshot |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`adec40_network_config_snapshot.c`](decompiled/adec40_network_config_snapshot.c) | Per-frame copy of Engine Configuration (0x3330-byte block at *0x2693DF8) sub-blocks via ~25 getters 0x34E330..0x34E5F0 into networking-config mirror 0x27BD1D0..0x27BE57F; mirror read only by networking/session/matchmaking code (0xAE3000..0xBBC000). |
| `0xadf6c0` | network_config_frame_update |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`adf6c0_network_config_frame_update.c`](decompiled/adf6c0_network_config_frame_update.c) | Calls 0xADEC40, derives 1000/config[+0x5A0+0x18] frame-time limit, resets stale 28-byte entries at mirror+0x6F8. |

## Classes (100)

Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. Placement in this folder is `HYPOTHESIS` (name-token rule).

| class | typeinfo | vtable | virtual slots | bases |
|---|---|---|---|---|
| `c_client_set_channel_atom_control` | `0x19073a0` | `0x1907340` | 11 | c_client_instant_atom_control |
| `c_demonware_allocator` | `0x1914200` | `0x19141e0` | 3 | c_allocation_interface |
| `c_demonware_external_nat_punch_client` | `0x19142c0` | `0x19142a0` | 3 | bdExternalIntroducerInterface |
| `c_demonware_http_client_private` | `0x1904ec0` | `0x1904e90` | 5 | bdHTTPWrapper |
| `c_demonware_http_interceptor` | `0x1904f50` | `0x1904f00` | 4 | bdUploadInterceptor, bdDownloadInterceptor @+0x8 |
| `c_demonware_stun_shim` | `0x1914190` | `0x1914130` | 11 | bdStunClientInterface |
| `c_faction_channel_component_game_system` | `0x1942e70` | `0x1942e40` | 8 | c_game_system_interface |
| `c_fallback_demonware_allocator` | `0x1911590` | `0x1911570` | 3 | c_allocation_interface |
| `c_generic_network_session_parameter<bool>` | `0x196d0d0` | `0x196d000` | 24 | c_generic_network_session_parameter_data<bool> |
| `c_generic_network_session_parameter<e_language>` | `0x196d3d0` | `0x196d300` | 24 | c_generic_network_session_parameter_data<e_language> |
| `c_generic_network_session_parameter<e_life_cycle_disbanding_reason>` | `0x196ceb0` | `0x196cde0` | 24 | c_generic_network_session_parameter_data<e_life_cycle_disbanding_reason> |
| `c_generic_network_session_parameter<s_activity_start_status>` | `0x196d7b0` | `0x196d6e0` | 24 | c_generic_network_session_parameter_data<s_activity_start_status> |
| `c_generic_network_session_parameter<s_network_quality_live_for_all_peers>` | `0x196e100` |  |  | c_generic_network_session_parameter_data<s_network_quality_live_for_all_peers> |
| `c_generic_network_session_parameter<s_network_session_active_join_controls>` | `0x196dd50` | `0x196dc80` | 24 | c_generic_network_session_parameter_data<s_network_session_active_join_controls> |
| `c_generic_network_session_parameter<s_network_session_atomic_cascade_join_data>` | `0x196dc50` | `0x196db80` | 24 | c_generic_network_session_parameter_data<s_network_session_atomic_cascade_join_data> |
| `c_generic_network_session_parameter<s_network_session_desired_join_controls>` | `0x196d4d0` | `0x196d400` | 24 | c_generic_network_session_parameter_data<s_network_session_desired_join_controls> |
| `c_generic_network_session_parameter<s_network_session_parameter_initial_slice_set_status>` | `0x196ccb0` | `0x196cbe0` | 24 | c_generic_network_session_parameter_data<s_network_session_parameter_initial_slice_set_status> |
| `c_generic_network_session_parameter<s_network_session_parameter_orbit>` | `0x196da70` | `0x196d9a0` | 24 | c_generic_network_session_parameter_data<s_network_session_parameter_orbit> |
| `c_generic_network_session_parameter<s_network_session_parameter_session_messaging>` | `0x196cfb0` |  |  | c_generic_network_session_parameter_data<s_network_session_parameter_session_messaging> |
| `c_generic_network_session_parameter<s_network_session_remote_session_join_data>` | `0x196d2d0` | `0x196d200` | 24 | c_generic_network_session_parameter_data<s_network_session_remote_session_join_data> |
| `c_generic_network_session_parameter<s_network_session_remote_session_join_result>` | `0x196d1d0` | `0x196d100` | 24 | c_generic_network_session_parameter_data<s_network_session_remote_session_join_result> |
| `c_generic_network_session_parameter<s_network_session_user_join_controls>` | `0x196d5d0` | `0x196d500` | 24 | c_generic_network_session_parameter_data<s_network_session_user_join_controls> |
| `c_generic_network_session_parameter<s_replicated_activity_matchmaking_progress>` | `0x196cdb0` | `0x196cce0` | 24 | c_generic_network_session_parameter_data<s_replicated_activity_matchmaking_progress> |
| `c_generic_network_session_parameter_data<bool>` | `0x196d0b0` |  |  | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<e_language>` | `0x196d3b0` |  |  | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<e_life_cycle_disbanding_reason>` | `0x196ce90` |  |  | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<s_activity_host_connection_information>` | `0x196db30` |  |  | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<s_activity_information>` | `0x196d690` |  |  | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<s_activity_start_status>` | `0x196d790` |  |  | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<s_desired_activity_information>` | `0x196d950` |  |  | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<s_desired_roster_join_activity>` | `0x196d870` |  |  | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<s_network_quality_live_for_all_peers>` | `0x196e0e0` | `0x196e130` | 18 | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<s_network_session_active_join_controls>` | `0x196dd30` |  |  | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<s_network_session_atomic_cascade_join_data>` | `0x196dc30` |  |  | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<s_network_session_desired_join_controls>` | `0x196d4b0` |  |  | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<s_network_session_parameter_countdown_timer>` | `0x196dfd0` |  |  | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<s_network_session_parameter_initial_slice_set_status>` | `0x196cc90` |  |  | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<s_network_session_parameter_orbit>` | `0x196da50` |  |  | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<s_network_session_parameter_session_messaging>` | `0x196cf90` |  |  | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<s_network_session_remote_session_join_data>` | `0x196d2b0` |  |  | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<s_network_session_remote_session_join_result>` | `0x196d1b0` |  |  | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<s_network_session_user_join_controls>` | `0x196d5b0` |  |  | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<s_network_session_world_controller_goal>` | `0x196de10` |  |  | c_network_session_parameter_base |
| `c_generic_network_session_parameter_data<s_replicated_activity_matchmaking_progress>` | `0x196cd90` |  |  | c_network_session_parameter_base |
| `c_group_session_qos_reply_manager` | `0x196b970` | `0x196b950` | 6 | c_session_qos_reply_manager |
| `c_group_target_session_qos_reply_manager` | `0x196b9c0` | `0x196b9a0` | 6 | c_group_session_qos_reply_manager |
| `c_http_download_stream_callback` | `0x1907f98` |  |  |  |
| `c_http_upload_stream_callback` | `0x1904cc8` |  |  |  |
| `c_local_player_channel_link_component_game_system` | `0x1943150` | `0x1943120` | 8 | c_game_system_interface |
| `c_network_channel_client` | `0x196b018` |  |  |  |
| `c_network_channel_direct_security_manager` | `0x196b310` | `0x196b220` | 32 | c_network_channel_security_interface |
| `c_network_channel_owner` | `0x196cab8` |  |  |  |
| `c_network_channel_passive_security_manager` | `0x196b580` | `0x196b490` | 32 | c_network_channel_security_interface |
| `c_network_channel_security_interface` | `0x196b328` |  |  |  |
| `c_network_connection` | `0x196b450` | `0x196b400` | 9 | c_network_channel_client |
| `c_network_crash_propagator_stub` | `0x1904da0` | `0x1904d60` | 7 | i_crash_report_files |
| `c_network_demonware_logger` | `0x19115e0` | `0x19115c0` | 3 | bdLogSubscriber |
| `c_network_game_system` | `0x196afe0` | `0x196afb0` | 8 | c_game_system_interface |
| `c_network_leaderboard_skill_interface` | `0x196bc48` |  |  |  |
| `c_network_leaderboard_skillz` | `0x196bc20` | `0x196bbc0` | 11 | c_network_leaderboard_skill_interface |
| `c_network_message_gateway` | `0x196c180` | `0x196c170` | 1 | c_network_out_of_band_consumer |
| `c_network_message_queue` | `0x196c220` | `0x196c1d0` | 9 | c_network_channel_client |
| `c_network_out_of_band_consumer` | `0x196c198` |  |  |  |
| `c_network_session` | `0x196c8e0` | `0x196c890` | 9 | c_network_channel_owner |
| `c_network_session_parameter_base` | `0x196def0` | `0x196de60` | 20 |  |
| `c_network_session_parameter_countdown_timer` | `0x196dfb0` | `0x196df10` | 19 | c_generic_network_session_parameter_data<s_network_session_parameter_countdown_timer> |
| `c_network_session_parameter_live_quality` | `0x196e0c0` | `0x196e000` | 23 | c_generic_network_session_parameter<s_network_quality_live_for_all_peers> |
| `c_network_session_parameter_session_messaging` | `0x196cfd0` | `0x196cee0` | 24 | c_generic_network_session_parameter<s_network_session_parameter_session_messaging> |
| `c_network_webstats_game_system` | `0x1941500` | `0x19414d0` | 8 | c_game_system_interface |
| `c_networking_engine_shim_game_system` | `0x1941b00` | `0x1941ad0` | 8 | c_game_system_interface |
| `c_online_presence_enumerate_task` | `0x196c380` | `0x196c340` | 7 | c_xoverlapped_task |
| `c_orbis_binary_session_async_request_base` | `0x1911e80` | `0x1911e50` | 8 | c_orbis_session_async_request_base |
| `c_orbis_create_session_async_request` | `0x1911a40` | `0x1911a10` | 8 | c_orbis_json_session_async_request_base |
| `c_orbis_delete_session_async_request` | `0x19119e0` | `0x19119b0` | 8 | c_orbis_json_session_async_request_base |
| `c_orbis_delete_session_member_async_request` | `0x1911920` | `0x19118f0` | 8 | c_orbis_json_session_async_request_base |
| `c_orbis_get_session_async_request` | `0x19116e0` | `0x19116b0` | 8 | c_orbis_json_session_async_request_base |
| `c_orbis_get_session_data_async_request` | `0x1911740` | `0x1911710` | 8 | c_orbis_binary_session_async_request_base |
| `c_orbis_get_session_list_async_request` | `0x1912230` | `0x1912200` | 8 | c_orbis_json_session_async_request_base |
| `c_orbis_join_session_async_request` | `0x1911980` | `0x1911950` | 8 | c_orbis_json_session_async_request_base |
| `c_orbis_json_session_async_request_base` | `0x1911e20` | `0x1911df0` | 8 | c_orbis_session_async_request_base |
| `c_orbis_session_async_request_base` | `0x1911e98` |  |  |  |
| `c_orbis_update_session_async_request` | `0x19118c0` | `0x1911890` | 8 | c_orbis_json_session_async_request_base |
| `c_orbis_update_session_image_async_request` | `0x19121d0` | `0x19121a0` | 8 | c_orbis_json_session_async_request_base |
| `c_perk_context_channel_query` | `0x1943590` | `0x1943530` | 14 | c_perk_context |
| `c_platform_social_presence_query_task_director` | `0x1911ee0` | `0x1911ed0` | 25 |  |
| `c_posse_session_qos_reply_manager` | `0x196b920` | `0x196b900` | 6 | c_session_qos_reply_manager |
| `c_rich_presence_provider` | `0x1942b20` | `0x1942ad0` | 9 | i_rich_presence_provider |
| `c_secure_connection_owner_manager` | `0x196b6d0` | `0x196b5e0` | 32 | c_network_channel_security_interface |
| `c_session_qos_reply_manager` | `0x196b8e0` | `0x196b8c0` | 6 |  |
| `c_signon_state_complete` | `0x1910fe0` | `0x1910f50` | 3 | c_signon_state_handler_base |
| `c_signon_state_handler_base` | `0x19110d8` |  |  |  |
| `c_signon_state_retrieving_platform_token` | `0x1910fa0` | `0x1910ef0` | 3 | c_signon_state_handler_base |
| `c_signon_state_sending_signon_request` | `0x1910fc0` | `0x1910f20` | 3 | c_signon_state_handler_base |
| `c_signon_state_waiting_to_retry` | `0x1911000` | `0x1910f80` | 3 | c_signon_state_handler_base |
| `c_social_presence_account_translation_callback` | `0x1940500` | `0x1940460` | 3 | i_investment_bap_message_queue_callbacks |
| `c_transport_demonware_qos_listener` | `0x1914320` | `0x1914300` | 6 | bdQoSProbeListener |
| `c_transport_game_system` | `0x1941940` | `0x1941910` | 8 | c_game_system_interface |
| `c_transport_late_game_system` | `0x19406d0` | `0x19406a0` | 8 | c_game_system_interface |
| `i_networking_engine_shim` | `0x1941b18` |  |  |  |
| `i_rich_presence_provider` | `0x1942b40` |  |  |  |

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
