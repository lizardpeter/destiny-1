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
| `0xa17d0` | schema_protobuf_codec_b |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`a17d0_schema_protobuf_codec_b.c`](decompiled/a17d0_schema_protobuf_codec_b.c) | Schematized protobuf codec (pair of 0xA2020), 23-byte field records. |
| `0xa2020` | schema_protobuf_codec_a |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`a2020_schema_protobuf_codec_a.c`](decompiled/a2020_schema_protobuf_codec_a.c) | Schematized protobuf codec (one of the encode/decode pair with 0xA17D0) driven by tables of 23-byte field records. |
| `0x298aa0` | activity_client_init |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`298aa0_activity_client_init.c`](decompiled/298aa0_activity_client_init.c) | Activity client construction: messaging interface (+0xE50), instance object (+0xE58), local machine id (+0xE68), clears entity indices, tokens, membership. |
| `0x2998f0` | activity_client_ready_for_instantiation |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`2998f0_activity_client_ready_for_instantiation.c`](decompiled/2998f0_activity_client_ready_for_instantiation.c) | True when the instance state is valid (+0x50B0[0] set, [1] clear), entity indices arrived (+0x64AA) and the client is established (+0x131 bit 0). |
| `0x299b00` | activity_client_check_activity_checksum |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`299b00_activity_client_check_activity_checksum.c`](decompiled/299b00_activity_client_check_activity_checksum.c) | Compares instance +0x5C with the u32 at +0xC of the loaded activity tag; mismatch fails the world transition ('activity checksum mismatch'). |
| `0x299d10` | activity_client_send_to_host |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`299d10_activity_client_send_to_host.c`](decompiled/299d10_activity_client_send_to_host.c) | Encodes an engine-type payload and sends it to the host with a client message type. |
| `0x299e30` | activity_client_dispatch_host_message |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`299e30_activity_client_dispatch_host_message.c`](decompiled/299e30_activity_client_dispatch_host_message.c) | Dispatches a host message by type through the 17-entry table 0x1910480 (type, handler); logs unknown types and handler failures. |
| `0x29a5e0` | activity_client_instance_details |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`29a5e0_activity_client_instance_details.c`](decompiled/29a5e0_activity_client_instance_details.c) | Pointer to the instance details (+0x50B0 + 0x60) once the instance state arrived (+0x130 bit 6). |
| `0x29c710` | activity_client_apply_join_result |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`29c710_activity_client_apply_join_result.c`](decompiled/29c710_activity_client_apply_join_result.c) | Join result: nonce must match the request (+0x173*8); result 0 copies the 0x1A8-byte result, keeps u16 @0x196/@0x198, marks the client joined (+0x130 bit 5). |
| `0x29d130` | activity_client_apply_membership |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`29d130_activity_client_apply_membership.c`](decompiled/29d130_activity_client_apply_membership.c) | Applies a membership update: copies the current 0x5038-byte membership, decodes the message over it with 0x2C9AE0 (present bit + 0x808009ED), stores it (+0xE70), marks the client established (+0x131 bit 0) and finds the local player's slot. |
| `0x29d400` | activity_client_time_since_receive |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`29d400_activity_client_time_since_receive.c`](decompiled/29d400_activity_client_time_since_receive.c) | Time since the messaging interface last received anything (used by the 20 s lost-host check). |
| `0x29d950` | activity_client_on_membership |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`29d950_activity_client_on_membership.c`](decompiled/29d950_activity_client_on_membership.c) | Host message 11: forwards to 0x29D130. |
| `0x29d960` | activity_client_send_sync_token |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`29d960_activity_client_send_sync_token.c`](decompiled/29d960_activity_client_send_sync_token.c) | Sends client message 28 with the token from +0x64AC. |
| `0x29ddf0` | activity_client_on_host_event |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`29ddf0_activity_client_on_host_event.c`](decompiled/29ddf0_activity_client_on_host_event.c) | Host message 5: passes the raw payload to the simulation (vtable +0x338 -> 0xBB1C10); error bit +0x131\|2 on failure. |
| `0x29de50` | activity_client_on_debug_update |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`29de50_activity_client_on_debug_update.c`](decompiled/29de50_activity_client_on_debug_update.c) | Host message 38: decodes 0x808052E5 plus up to 8000 raw bytes; the result is not applied (verification/debug only). |
| `0x2a0840` | activity_client_is_acknowledged_host |  | Static decompilation plus d1-native runtime traces (frame timing, prologue cinematic, cinematic suppression), 2026-10-13 night | [`2a0840_activity_client_is_acknowledged_host.c`](decompiled/2a0840_activity_client_is_acknowledged_host.c) | membership (AC +0xE70) host id +0x5020 == AC +0xE68. |
| `0x2a0d20` | activity_instance_validate_and_load_bubbles |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`2a0d20_activity_instance_validate_and_load_bubbles.c`](decompiled/2a0d20_activity_instance_validate_and_load_bubbles.c) | World transition: instance bubble count (+0x10) must equal the activity tag's count (+0x48), then registers each bubble's selected slice set (+0x14[i], 0 = first) in the world slice table via 0x343A90. |
| `0x2a2c60` | activity_instance_set_state |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`2a2c60_activity_instance_set_state.c`](decompiled/2a2c60_activity_instance_set_state.c) | Copies a 0x6B0-byte instance state into +0x50B0 and sets +0x50A8. |
| `0x2a5390` | membership_set_host |  | Static decompilation plus d1-native runtime traces (frame timing, prologue cinematic, cinematic suppression), 2026-10-13 night |  | Sets membership +0x5020 (i64 host id); not called directly anywhere in 01.33. |
| `0x2a53a0` | membership_host_equals |  | Static decompilation plus d1-native runtime traces (frame timing, prologue cinematic, cinematic suppression), 2026-10-13 night | [`2a53a0_membership_host_equals.c`](decompiled/2a53a0_membership_host_equals.c) | Compares membership +0x5020 (i64 host id) with a given id. |
| `0x2a5520` | membership_find_machine |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`2a5520_membership_find_machine.c`](decompiled/2a5520_membership_find_machine.c) | Finds the slot whose machine id matches, among the valid-slot mask (+0x502C). |
| `0x2aa420` | signon_response_handler |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`2aa420_signon_response_handler.c`](decompiled/2aa420_signon_response_handler.c) | Sign-on response (schema 0x1910CC0): field 1 type (0 success) and per-type payloads. |
| `0x2aad90` | signon_engine_configuration_callback |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`2aad90_signon_engine_configuration_callback.c`](decompiled/2aad90_signon_engine_configuration_callback.c) | Callback decoding the engine configuration stream from the sign-on response. |
| `0x2aada0` | signon_success |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`2aada0_signon_success.c`](decompiled/2aada0_signon_success.c) | Sign-on success path: BAP address (field 2.6, IPv4 as little-endian u32), session keys (fields 2/3), engine configuration stream. |
| `0x2b0980` | content_manifest_handler |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`2b0980_content_manifest_handler.c`](decompiled/2b0980_content_manifest_handler.c) | Content manifest (schema 0x1911470): signature-checked only when the byte at 0x18DC974 is set; field 3 lists patchable packages. |
| `0x595690` | activity_client_bap_last_receive_time | c_activity_client_messaging_interface_bap | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`595690_activity_client_bap_last_receive_time.c`](decompiled/595690_activity_client_bap_last_receive_time.c) | Messaging interface +0x28: last-receive time of the AC's BAP service. (vtable 0x1941B40 slot 5) |
| `0x5956a0` | activity_client_bap_send | c_activity_client_messaging_interface_bap | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`5956a0_activity_client_bap_send.c`](decompiled/5956a0_activity_client_bap_send.c) | Sends an activity message to the host as client_to_activity_host 8: builds [1][u32 type][u32 len][u32 0][data] and sends kind 0x11 via the AC's BAP service (+0x7C). (vtable 0x1941B40 slot 6) |
| `0x595db0` | activity_client_bap_startup_response |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`595db0_activity_client_bap_startup_response.c`](decompiled/595db0_activity_client_bap_startup_response.c) | Messaging-interface callback for the host-startup response (7): passes the 0x88-byte body to the activity client as host message type 10. |
| `0x595fc0` | activity_client_bap_proxy_response |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`595fc0_activity_client_bap_proxy_response.c`](decompiled/595fc0_activity_client_bap_proxy_response.c) | Messaging-interface callback for the activity-host proxy response (17, 16 bytes): stores the AH address (u32 IPv4 + port) and logs 'AH IP resolution successful'. |
| `0x59a780` | matchmaking_configuration_request |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`59a780_matchmaking_configuration_request.c`](decompiled/59a780_matchmaking_configuration_request.c) | Matchmaking configuration request (42): protobuf {1 kind, 2, 3 nonce, 11 {activity hash, content hash}}. |
| `0x59b0e0` | matchmaking_configuration_response_check |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`59b0e0_matchmaking_configuration_response_check.c`](decompiled/59b0e0_matchmaking_configuration_response_check.c) | Matchmaking configuration response: needs field 4 (configuration) present and the nonce echoed. |
| `0xadec40` | network_config_snapshot |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`adec40_network_config_snapshot.c`](decompiled/adec40_network_config_snapshot.c) | Per-frame copy of Engine Configuration (0x3330-byte block at *0x2693DF8) sub-blocks via ~25 getters 0x34E330..0x34E5F0 into networking-config mirror 0x27BD1D0..0x27BE57F; mirror read only by networking/session/matchmaking code (0xAE3000..0xBBC000). |
| `0xadf6c0` | network_config_frame_update |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`adf6c0_network_config_frame_update.c`](decompiled/adf6c0_network_config_frame_update.c) | Calls 0xADEC40, derives 1000/config[+0x5A0+0x18] frame-time limit, resets stale 28-byte entries at mirror+0x6F8. |
| `0xb49210` | voice_port_lookup |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`b49210_voice_port_lookup.c`](decompiled/b49210_voice_port_lookup.c) | Finds a voice port record by the id sceVoiceCreatePort returned; callers dereference the result unchecked. |
| `0x1018800` | activity_client_on_entity_indices |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`1018800_activity_client_on_entity_indices.c`](decompiled/1018800_activity_client_on_entity_indices.c) | Host message 0: ORs a 384-word entity-index bitmask into the client's set (+0x5EA8) and sets +0x64AA (indices received). |
| `0x1018990` | activity_client_on_instance_state |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`1018990_activity_client_on_instance_state.c`](decompiled/1018990_activity_client_on_instance_state.c) | Host message 1: decodes the 0x6B0-byte instance state (0x80800E76) and hands it to the simulation (vtable +0x360 -> event 0x17); sets +0x130 bit 6. |
| `0x1018e30` | activity_client_on_join_result |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`1018e30_activity_client_on_join_result.c`](decompiled/1018e30_activity_client_on_join_result.c) | Host message 4: decodes 0x80800A58 (join result) and calls 0x29C710. |
| `0x10193e0` | activity_client_on_sync_token |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`10193e0_activity_client_on_sync_token.c`](decompiled/10193e0_activity_client_on_sync_token.c) | Host message 27: stores an i32 token at +0x64AC; the client echoes it in its message 28 (0x29D960). |

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
