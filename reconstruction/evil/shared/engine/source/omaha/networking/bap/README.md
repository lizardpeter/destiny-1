# bap/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `omaha.networking.bap`  
**Folder path evidence:** `HYPOTHESIS` (folder name is a proposal from RTTI/log-channel clustering, not a recovered path)  
**Role:** BAP connection/message queues, investment BAP messages

## Source files named in the binary

_None recovered (retail build stripped most asserts)._

## Decompiled functions

_None yet._

## Classes (137)

Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. Placement in this folder is `HYPOTHESIS` (name-token rule).

| class | typeinfo | vtable | virtual slots | bases |
|---|---|---|---|---|
| `c_activity_client_messaging_interface_bap` | `0x1941c20` | `0x1941b40` | 12 | i_activity_client_messaging_interface |
| `c_activity_client_messaging_interface_bap::c_bap_host_manager_response_handler` | `0x1941c00` | `0x1941bb0` | 1 | i_investment_bap_message_queue_callbacks |
| `c_bap_message_client_activity_request_header` | `0x193b460` | `0x193b0d0` | 18 | c_bap_message_header_base |
| `c_bap_message_client_notification_header` | `0x193b480` | `0x193b170` | 18 | c_bap_message_header_base |
| `c_bap_message_client_request_header` | `0x193b420` | `0x193af90` | 18 | c_bap_message_header_base |
| `c_bap_message_client_response_header` | `0x193b440` | `0x193b030` | 18 | c_bap_message_header_base |
| `c_bap_message_header` | `0x193b400` | `0x193aef0` | 18 | c_bap_message_header_base |
| `c_bap_message_header_base` | `0x193b3e0` |  |  | i_investment_bap_message_header_interface |
| `c_bap_message_response_header` | `0x193b4e0` | `0x193b350` | 20 | c_bap_message_header_base |
| `c_bap_message_service_activity_request_header` | `0x193b4c0` | `0x193b2b0` | 18 | c_bap_message_header_base |
| `c_bap_message_service_request_header` | `0x193b4a0` | `0x193b210` | 18 | c_bap_message_header_base |
| `c_bap_status_for_crash_report` | `0x196bf00` | `0x196bec0` | 7 | i_crash_report_files |
| `c_investment_bap_message_activity_host_to_client_log_notification` | `0x193bb20` | `0x193bae0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_activity_host_to_client_notification` | `0x193b880` | `0x193b840` | 10 | i_investment_bap_message_interface |
| `c_investment_bap_message_activity_host_to_world_server_response` | `0x193e420` | `0x193e3e0` | 10 | i_investment_bap_message_interface |
| `c_investment_bap_message_bap_to_activity_host_manager_request` | `0x193a8a0` | `0x193a860` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_bap_to_activity_host_manager_response` | `0x193a910` | `0x193a8d0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_bap_to_activity_host_notification` | `0x193ba40` | `0x193ba00` | 10 | i_investment_bap_message_interface |
| `c_investment_bap_message_bap_to_activity_host_request` | `0x193a6e0` | `0x193a6a0` | 10 | c_investment_bap_protobuf_message_base |
| `c_investment_bap_message_bap_to_activity_host_response` | `0x193a750` | `0x193a710` | 10 | c_investment_bap_protobuf_message_base |
| `c_investment_bap_message_bap_to_activity_host_socket_handoff_request` | `0x193a980` | `0x193a940` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_bap_to_client_log_notification` | `0x193b960` | `0x193b920` | 10 | i_investment_bap_message_interface |
| `c_investment_bap_message_bap_to_client_nat_punch_relay_intro_notification` | `0x193b810` | `0x193b7d0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_bap_to_client_notification` | `0x193b8f0` | `0x193b8b0` | 10 | i_investment_bap_message_interface |
| `c_investment_bap_message_bap_to_client_request_relay_connection_notification` | `0x193d860` | `0x193d820` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_bap_to_client_server_shutdown_notification` | `0x193b9d0` | `0x193b990` | 10 | i_investment_bap_message_interface |
| `c_investment_bap_message_bap_to_client_user_message_request` | `0x193e1f0` | `0x193e1b0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_bap_to_client_user_message_response` | `0x193e260` | `0x193e220` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_base` | `0x193a580` |  |  | i_investment_bap_message_interface |
| `c_investment_bap_message_client_to_activity_host_manager_request` | `0x193a7c0` | `0x193a780` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_activity_host_manager_response` | `0x193a830` | `0x193a7f0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_activity_host_notification` | `0x193bab0` | `0x193ba70` | 10 | i_investment_bap_message_interface |
| `c_investment_bap_message_client_to_bap_account_id_translation_request` | `0x193a600` | `0x193a5c0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_account_id_translation_response` | `0x193a670` | `0x193a630` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_channel_startup_request` | `0x193d400` | `0x193d3c0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_channel_startup_response` | `0x193d470` | `0x193d430` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_check_party_invite_request` | `0x193ae50` | `0x193ae10` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_check_party_invite_response` | `0x193aec0` | `0x193ae80` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_clan_request` | `0x193a9f0` | `0x193a9b0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_clan_response` | `0x193aa60` | `0x193aa20` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_client_config_request` | `0x193aad0` | `0x193aa90` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_client_config_response` | `0x193ab40` | `0x193ab00` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_echo_request` | `0x193d320` | `0x193d2e0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_echo_response` | `0x193d390` | `0x193d350` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_friends_generic_response` | `0x193ad00` | `0x193acc0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_friends_update_request` | `0x193ac90` | `0x193ac50` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_get_activity_host_proxy_request` | `0x193d9b0` | `0x193d970` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_get_activity_host_proxy_response` | `0x193da20` | `0x193d9e0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_initiate_relay_connection_notification` | `0x193d7f0` | `0x193d7b0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_nat_punch_request` | `0x193b7a0` | `0x193b760` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_party_invite_request` | `0x193ad70` | `0x193ad30` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_party_invite_response` | `0x193ade0` | `0x193ada0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_queuez_register_request` | `0x193d550` | `0x193d510` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_queuez_register_response` | `0x193d5c0` | `0x193d580` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_register_relay_client_request` | `0x193d8d0` | `0x193d890` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_register_relay_client_response` | `0x193d940` | `0x193d900` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_secure_hello_request` | `0x193d1b0` | `0x193d170` | 10 | c_investment_bap_protobuf_message_base |
| `c_investment_bap_message_client_to_bap_secure_hello_response` | `0x193d4e0` | `0x193d4a0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_subscription_request` | `0x193d630` | `0x193d5f0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_subscription_response` | `0x193d6a0` | `0x193d660` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_unsubscribe_request` | `0x193d710` | `0x193d6d0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_unsubscribe_response` | `0x193d780` | `0x193d740` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_update_matchmaking_core_request` | `0x193b5e0` | `0x193b5a0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_update_matchmaking_core_response` | `0x193b650` | `0x193b610` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_update_matchmaking_skill_request` | `0x193b6c0` | `0x193b680` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_update_matchmaking_skill_response` | `0x193b730` | `0x193b6f0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_update_purchased_offers_request` | `0x193abb0` | `0x193ab70` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_bap_update_purchased_offers_response` | `0x193ac20` | `0x193abe0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_client_to_world_server_request` | `0x193e2d0` | `0x193e290` | 10 | i_investment_bap_message_interface |
| `c_investment_bap_message_client_to_world_server_response` | `0x193e340` | `0x193e300` | 10 | i_investment_bap_message_interface |
| `c_investment_bap_message_policy_activity_host_to_client_log_notification` | `0x193c1d0` | `0x193c170` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_activity_host_to_client_notification` | `0x193c140` | `0x193c0e0` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_bap_to_activity_host_manager_request` | `0x193c410` | `0x193c3b0` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_bap_to_activity_host_notification` | `0x193c380` | `0x193c320` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_bap_to_activity_host_request` | `0x193c020` | `0x193bfc0` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_bap_to_activity_host_response` | `0x193c0b0` | `0x193c050` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_bap_to_client_log_notification` | `0x193cd10` | `0x193ccb0` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_bap_to_client_notification` | `0x193c260` | `0x193c200` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_bap_to_client_server_shutdown_notification` | `0x193c890` | `0x193c830` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_bap_to_client_user_message` | `0x193cec0` | `0x193ce60` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_base` | `0x193be60` |  |  | i_investment_bap_message_policy_interface |
| `c_investment_bap_message_policy_client_to_activity_host_manager_request` | `0x193bf00` | `0x193bea0` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_client_to_activity_host_manager_response` | `0x193bf90` | `0x193bf30` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_client_to_activity_host_notification` | `0x193c2f0` | `0x193c290` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_client_to_bap_account_id_translation_request` | `0x193c5c0` | `0x193c560` | 14 | i_investment_bap_message_policy_interface |
| `c_investment_bap_message_policy_client_to_bap_challenge_response` | `0x193c530` | `0x193c4d0` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_client_to_bap_clan_request` | `0x193c9b0` | `0x193c950` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_client_to_bap_client_config_request` | `0x193ca40` | `0x193c9e0` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_client_to_bap_friends_check_party_invite_request` | `0x193cc80` | `0x193cc20` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_client_to_bap_friends_party_invite_request` | `0x193cbf0` | `0x193cb90` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_client_to_bap_friends_update_request` | `0x193cb60` | `0x193cb00` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_client_to_bap_get_activity_host_proxy_request` | `0x193c4a0` | `0x193c440` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_client_to_bap_initiate_relay_connection_notification` | `0x193c770` | `0x193c710` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_client_to_bap_matchmaking_core_request` | `0x193cda0` | `0x193cd40` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_client_to_bap_matchmaking_skill_request` | `0x193ce30` | `0x193cdd0` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_client_to_bap_nat_punch_intro_request` | `0x193c920` | `0x193c8c0` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_client_to_bap_register_relay_client_request` | `0x193c800` | `0x193c7a0` | 14 | i_investment_bap_message_policy_interface |
| `c_investment_bap_message_policy_client_to_bap_subscription_request` | `0x193c650` | `0x193c5f0` | 14 | i_investment_bap_message_policy_interface |
| `c_investment_bap_message_policy_client_to_bap_unsubscribe_request` | `0x193c6e0` | `0x193c680` | 14 | i_investment_bap_message_policy_interface |
| `c_investment_bap_message_policy_client_to_bap_update_purchased_offers_request` | `0x193cad0` | `0x193ca70` | 14 | c_investment_bap_message_policy_base |
| `c_investment_bap_message_policy_client_to_world_server_deterministic_request` | `0x193d000` | `0x193cfa0` | 14 | c_investment_bap_message_policy_client_to_world_server_request_base |
| `c_investment_bap_message_policy_client_to_world_server_nondeterministic_request` | `0x193cf70` | `0x193cf10` | 14 | c_investment_bap_message_policy_client_to_world_server_request_base |
| `c_investment_bap_message_policy_client_to_world_server_request_base` | `0x193cee0` |  |  | i_investment_bap_message_policy_interface |
| `c_investment_bap_message_policy_service_to_world_server_request` | `0x193d090` | `0x193d030` | 14 | c_investment_bap_message_policy_client_to_world_server_request_base |
| `c_investment_bap_message_push_handler` | `0x193da90` | `0x193da50` | 7 | i_network_server_bap_connection_push_handler_interface |
| `c_investment_bap_message_push_policy_activity_host_to_client_notification` | `0x193de80` | `0x193de50` | 8 | i_investment_bap_message_push_policy_interface |
| `c_investment_bap_message_push_policy_bap_client_to_activity_host_manager_request` | `0x193dd60` | `0x193dd30` | 8 | i_investment_bap_message_push_policy_interface |
| `c_investment_bap_message_push_policy_bap_client_to_activity_host_notification` | `0x193dc40` | `0x193dc10` | 8 | i_investment_bap_message_push_policy_interface |
| `c_investment_bap_message_push_policy_bap_to_activity_host_notification` | `0x193dca0` | `0x193dc70` | 8 | i_investment_bap_message_push_policy_interface |
| `c_investment_bap_message_push_policy_bap_to_activity_host_request` | `0x193dd00` | `0x193dcd0` | 8 | i_investment_bap_message_push_policy_interface |
| `c_investment_bap_message_push_policy_bap_to_client_challenge_request` | `0x1937e90` | `0x1937e60` | 8 | i_investment_bap_message_push_policy_interface |
| `c_investment_bap_message_push_policy_bap_to_client_log_notification` | `0x193ddc0` | `0x193dd90` | 8 | i_investment_bap_message_push_policy_interface |
| `c_investment_bap_message_push_policy_bap_to_client_nat_punch_relay_intro_notification` | `0x193de20` | `0x193ddf0` | 8 | i_investment_bap_message_push_policy_interface |
| `c_investment_bap_message_push_policy_bap_to_client_notification` | `0x193dbe0` | `0x193dbb0` | 8 | i_investment_bap_message_push_policy_interface |
| `c_investment_bap_message_push_policy_bap_to_client_request_relay_connection_notification` | `0x193dfa0` | `0x193df70` | 8 | i_investment_bap_message_push_policy_interface |
| `c_investment_bap_message_push_policy_bap_to_client_server_shutdown_notification` | `0x193e000` | `0x193dfd0` | 8 | i_investment_bap_message_push_policy_interface |
| `c_investment_bap_message_push_policy_queuez_to_client_subscription_lost_notification` | `0x193df40` | `0x193df10` | 8 | i_investment_bap_message_push_policy_interface |
| `c_investment_bap_message_push_policy_queuez_to_client_update_notification` | `0x193dee0` | `0x193deb0` | 8 | i_investment_bap_message_push_policy_interface |
| `c_investment_bap_message_queue` | `0x193e080` | `0x193e030` | 12 | i_network_server_bap_connection_message_source_interface |
| `c_investment_bap_message_queuez_to_client_subscription_lost_notification` | `0x193e170` | `0x193e130` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_queuez_to_client_update_notification` | `0x193e100` | `0x193e0c0` | 10 | c_investment_bap_message_base |
| `c_investment_bap_message_server_challenge_request` | `0x193d240` | `0x193d200` | 10 | c_investment_bap_message_wrapper_message_base |
| `c_investment_bap_message_server_challenge_response` | `0x193d2b0` | `0x193d270` | 10 | c_investment_bap_message_wrapper_message_base |
| `c_investment_bap_message_service_to_world_server_request` | `0x193e3b0` | `0x193e370` | 10 | i_investment_bap_message_interface |
| `c_investment_bap_message_wrapper_message_base` | `0x193d1d0` |  |  | c_investment_bap_protobuf_message_base |
| `c_investment_bap_protobuf_message_base` | `0x193d140` |  |  | c_investment_bap_message_base |
| `c_network_server_bap_connection` | `0x196be70` | `0x196be50` | 6 | i_network_server_bap_connection_consumer_interface |
| `c_network_server_bap_connection_protocol_request_source` | `0x196bf80` | `0x196bf30` | 12 | i_network_server_bap_connection_message_source_interface |
| `c_world_controller_state_bootflow_bap_signin_handler` | `0x1945de0` | `0x1945d90` | 12 | c_world_controller_tiger_base_state_handler |
| `i_investment_bap_message_header_interface` | `0x193b580` |  |  |  |
| `i_investment_bap_message_interface` | `0x193a598` |  |  |  |
| `i_investment_bap_message_policy_interface` | `0x193be78` |  |  |  |
| `i_investment_bap_message_push_policy_interface` | `0x1937ea8` |  |  |  |
| `i_investment_bap_message_queue_callbacks` | `0x193a128` |  |  |  |
| `i_network_server_bap_connection_consumer_interface` | `0x196be88` |  |  |  |
| `i_network_server_bap_connection_message_source_interface` | `0x193e098` |  |  |  |
| `i_network_server_bap_connection_push_handler_interface` | `0x193daa8` |  |  |  |

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
