# platform/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `omaha.platform`  
**Folder path evidence:** `HYPOTHESIS` (folder name is a proposal from RTTI/log-channel clustering, not a recovered path)  
**Role:** orbis/NP platform services, DLC, SKU, trophies

## Source files named in the binary

_None recovered (retail build stripped most asserts)._

## Decompiled functions

| VA | name | class | evidence | pseudo-C | role |
|---|---|---|---|---|---|
| `0x8a040` | boot_button_check |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`8a040_boot_button_check.c`](decompiled/8a040_boot_button_check.c) | Startup: opens pad 0, reads one ScePadData and checks Cross+Triangle (0x4010) held at boot; then mounts /download0. |
| `0xacef0` | input_globals_init |  | Static decompilation of the 01.33 eboot input and UI text paths plus d1-native headless traces (D1_TRACE_GLYPHS / D1_TRACE_PROMPTS / D1_TRACE_WEAPON), 2026-10-17; names are HYPOTHESIS | [`acef0_input_globals_init.c`](decompiled/acef0_input_globals_init.c) | Clears the input globals block 0x1AD40D0 (0xD30 bytes), creates the 'keyboard buffer' (handle 0x1AD4DF8), opens the pads (0xADA40: scePadOpen, controller info into 0x1AD4ED8 rows of 0x18) and runs a first update (0xACF80). |
| `0xacf80` | input_globals_update |  | Static decompilation of the 01.33 eboot input and UI text paths plus d1-native headless traces (D1_TRACE_GLYPHS / D1_TRACE_PROMPTS / D1_TRACE_WEAPON), 2026-10-17; names are HYPOTHESIS | [`acf80_input_globals_update.c`](decompiled/acf80_input_globals_update.c) | Per-frame input update on the double-buffered state (0x1AD40E0 + 0x3B0 * buffer index 0x1AD4840): frame time in ms (clamped 0..100) -> gamepad_poll_all 0xAE1E0 for 4 pads into +0x10, light bar / vibration (0xAE260 with 0x1AD40D2\|0x1AD40D1 = suppressed, 0xAE390). |
| `0xad160` | input_globals_reset |  | Static decompilation of the 01.33 eboot input and UI text paths plus d1-native headless traces (D1_TRACE_GLYPHS / D1_TRACE_PROMPTS / D1_TRACE_WEAPON), 2026-10-17; names are HYPOTHESIS | [`ad160_input_globals_reset.c`](decompiled/ad160_input_globals_reset.c) | Zeroes both pad state buffers and the developer keyboard/mouse block 0x1AD4860..0x1AD4A18. |
| `0xad300` | keyboard_key_down_count |  | Static decompilation of the 01.33 eboot input and UI text paths plus d1-native headless traces (D1_TRACE_GLYPHS / D1_TRACE_PROMPTS / D1_TRACE_WEAPON), 2026-10-17; names are HYPOTHESIS | [`ad300_keyboard_key_down_count.c`](decompiled/ad300_keyboard_key_down_count.c) | Developer keyboard: frames key k has been down (byte at 0x1AD487A + k*4; 0 while 0x1AD40D1 is set). Keys use Bungie's key enum (0 Esc, 1-12 F1-F12, 17-26 digits 1-0, 31 Q, 32 W ... 45 A, 46 S, 47 D, 57 left shift, 68 right shift, 69 left ctrl, 71 left alt, 72 space, 77-80 up/down/left/right); 0x69-0x6C are either-side shift / ctrl / win / alt (max of both keys). Nothing on the PS4 build fills the table. |
| `0xad3a0` | keyboard_key_held_time |  | Static decompilation of the 01.33 eboot input and UI text paths plus d1-native headless traces (D1_TRACE_GLYPHS / D1_TRACE_PROMPTS / D1_TRACE_WEAPON), 2026-10-17; names are HYPOTHESIS | [`ad3a0_keyboard_key_held_time.c`](decompiled/ad3a0_keyboard_key_held_time.c) | Developer keyboard: u16 held time of key k (0x1AD4878 + k*4), with the same combined modifier codes 0x69-0x6C as 0xAD300. |
| `0xad490` | gamepad_state_get |  | Static decompilation of the 01.33 eboot input and UI text paths plus d1-native headless traces (D1_TRACE_GLYPHS / D1_TRACE_PROMPTS / D1_TRACE_WEAPON), 2026-10-17; names are HYPOTHESIS | [`ad490_gamepad_state_get.c`](decompiled/ad490_gamepad_state_get.c) | Pad n's 0xC0-byte engine state in the current buffer (0x1AD40D0 + 0x20 + n*0xC0 + buffer*0x3B0) when connected (+0x10 + n); 0x1AD4E00 while 0x1AD40D1. |
| `0xad670` | mouse_state_get |  | Static decompilation of the 01.33 eboot input and UI text paths plus d1-native headless traces (D1_TRACE_GLYPHS / D1_TRACE_PROMPTS / D1_TRACE_WEAPON), 2026-10-17; names are HYPOTHESIS | [`ad670_mouse_state_get.c`](decompiled/ad670_mouse_state_get.c) | Developer mouse: when 0x1AD40D3 (mouse present) is set, returns the mouse block (0x1AD4860: i32 dx, i32 dy, ...; 0x1AD4EC0 while 0x1AD40D1), else null. |
| `0xad6a0` | mouse_button_down_count |  | Static decompilation of the 01.33 eboot input and UI text paths plus d1-native headless traces (D1_TRACE_GLYPHS / D1_TRACE_PROMPTS / D1_TRACE_WEAPON), 2026-10-17; names are HYPOTHESIS | [`ad6a0_mouse_button_down_count.c`](decompiled/ad6a0_mouse_button_down_count.c) | Developer mouse button n down count (merged with keys in input_abstraction_update: button 0 with key 0x51, 1 with key 0x3E, 2 with key 0x55). |
| `0xad6c0` | mouse_button_held_time |  | Static decompilation of the 01.33 eboot input and UI text paths plus d1-native headless traces (D1_TRACE_GLYPHS / D1_TRACE_PROMPTS / D1_TRACE_WEAPON), 2026-10-17; names are HYPOTHESIS | [`ad6c0_mouse_button_held_time.c`](decompiled/ad6c0_mouse_button_held_time.c) | Developer mouse button n held time. |
| `0xadc00` | gamepad_state_update |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`adc00_gamepad_state_update.c`](decompiled/adc00_gamepad_state_update.c) | ScePadData -> engine gamepad state (0xC0): triggers +0/+1 with press counters, 15 buttons held-frames/ms counters (bit table 0x15B5AB0), sticks s16 at +0x44 lx, +0x46 ly (up +), +0x48 rx, +0x4A ry (up +), motion +0xB0.., two touch points +0x50/+0x80. |
| `0xae0c0` | gamepad_poll |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`ae0c0_gamepad_poll.c`](decompiled/ae0c0_gamepad_poll.c) | One pad: scePadReadState; on a new connection refreshes scePadGetControllerInformation (touch pad size, dead zone); then gamepad_state_update. |
| `0xae1e0` | gamepad_poll_all |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`ae1e0_gamepad_poll_all.c`](decompiled/ae1e0_gamepad_poll_all.c) | Polls every pad slot: gamepad_poll(i) into state[i] (stride 0xC0), stores the connected flag per slot. Pad 0 state is the global 0x1AD40F0. |
| `0xbbe60` | addcont_list_query |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`bbe60_addcont_list_query.c`](decompiled/bbe60_addcont_list_query.c) | Queries installed add-on content (sceAppContentGetAddcontInfoList count-then-fill). |
| `0x295460` | system_event_session_invitation |  | Static decompilation plus d1-native research traces (D1_TRACE_* / D1_BYPASS runs: co-op joining, replication, Director, unlock flags, gear), 2026-10-15/16; names are HYPOTHESIS | [`295460_system_event_session_invitation.c`](decompiled/295460_system_event_session_invitation.c) | System service event 0x10000002 (session invitation; param 0x8C bytes: session id char[45] @0, invitation id @0x30, flags @0x70 bit 0 = from an invitation): copies it to 0x26535D4 and raises internal event 0x24. |
| `0x2b4270` | psn_join_session_invitation |  | Static decompilation plus d1-native research traces (D1_TRACE_* / D1_BYPASS runs: co-op joining, replication, Director, unlock flags, gear), 2026-10-15/16; names are HYPOTHESIS | [`2b4270_psn_join_session_invitation.c`](decompiled/2b4270_psn_join_session_invitation.c) | Handles internal event 0x24 (session invitation) and starts reading the PSN session (0x2B4600). |
| `0x2b4600` | psn_session_read |  | Static decompilation plus d1-native research traces (D1_TRACE_* / D1_BYPASS runs: co-op joining, replication, Director, unlock flags, gear), 2026-10-15/16; names are HYPOTHESIS | [`2b4600_psn_session_read.c`](decompiled/2b4600_psn_session_read.c) | Reads the PSN session (GET sessionInvitation/v1/sessions/<id>?fields=@default,members and .../sessionData), then 0x2B4AF0 checks it -> event 0x25 -> join store 0x266D5E8 -> join manager 0x57A260. |
| `0x2b4af0` | psn_session_check |  | Static decompilation plus d1-native research traces (D1_TRACE_* / D1_BYPASS runs: co-op joining, replication, Director, unlock flags, gear), 2026-10-15/16; names are HYPOTHESIS | [`2b4af0_psn_session_check.c`](decompiled/2b4af0_psn_session_check.c) | Checks the read PSN session before raising event 0x25 (join store 0x266D5E8). |
| `0x2bcc70` | psn_session_info_parse |  | Static decompilation plus d1-native research traces (D1_TRACE_* / D1_BYPASS runs: co-op joining, replication, Director, unlock flags, gear), 2026-10-15/16; names are HYPOTHESIS | [`2bcc70_psn_session_info_parse.c`](decompiled/2bcc70_psn_session_info_parse.c) | PSN session-info parser: requires sessionPrivacy, sessionMaxUser, sessionName, sessionStatus, sessionCreateTimestamp, sessionCreator and members[{onlineId, platform}]. |
| `0x2e94f0` | session_data_copy |  | Static decompilation plus d1-native research traces (D1_TRACE_* / D1_BYPASS runs: co-op joining, replication, Director, unlock flags, gear), 2026-10-15/16; names are HYPOTHESIS | [`2e94f0_session_data_copy.c`](decompiled/2e94f0_session_data_copy.c) | Copies the fireteam session data (host address, id, security key) only when it is exactly 0x4E bytes. |
| `0x2e9a70` | psn_session_id_format |  | Static decompilation plus d1-native research traces (D1_TRACE_* / D1_BYPASS runs: co-op joining, replication, Director, unlock flags, gear), 2026-10-15/16; names are HYPOTHESIS | [`2e9a70_psn_session_id_format.c`](decompiled/2e9a70_psn_session_id_format.c) | Formats a PSN session id (inverse of 0x2E9B10). |
| `0x2e9b10` | psn_session_id_parse |  | Static decompilation plus d1-native research traces (D1_TRACE_* / D1_BYPASS runs: co-op joining, replication, Director, unlock flags, gear), 2026-10-15/16; names are HYPOTHESIS | [`2e9b10_psn_session_id_parse.c`](decompiled/2e9b10_psn_session_id_parse.c) | Parses a PSN session id of the form XXX-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX (hex); other formats parse as zero. |

## Classes (59)

Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. Placement in this folder is `HYPOTHESIS` (name-token rule).

| class | typeinfo | vtable | virtual slots | bases |
|---|---|---|---|---|
| `c_dlc_async_task` | `0x1905640` | `0x1905610` | 8 | c_dlc_task |
| `c_dlc_cacher` | `0x1907cf0` | `0x1907cc0` | 8 | c_dlc_installer_object |
| `c_dlc_category_installer` | `0x1907d80` | `0x1907d20` | 11 | i_dlc_category_installer |
| `c_dlc_download_interceptor` | `0x1907f80` | `0x1907f70` | 1 | c_http_download_stream_callback |
| `c_dlc_downloader` | `0x1907f00` | `0x1907ed0` | 8 | c_dlc_installer_object |
| `c_dlc_enumerate_directories_task` | `0x19056d0` | `0x19056a0` | 8 | c_dlc_async_task |
| `c_dlc_enumerate_entitlements_task` | `0x19057f0` | `0x19057c0` | 8 | c_dlc_async_task |
| `c_dlc_enumerate_marketplace_task` | `0x1905790` | `0x1905760` | 8 | c_dlc_async_task |
| `c_dlc_installer_object` | `0x1907ff0` | `0x1907fc0` | 16 |  |
| `c_dlc_installer_progress` | `0x1908070` | `0x1908050` | 6 | i_dlc_installer_progress |
| `c_dlc_mount_task` | `0x1905850` | `0x1905820` | 8 | c_dlc_async_task |
| `c_dlc_task` | `0x19059c8` | `0x19059a0` | 7 |  |
| `c_dlc_uninstall_directory_task` | `0x1905730` | `0x1905700` | 8 | c_dlc_async_task |
| `c_dlc_uninstall_task` | `0x19058b0` | `0x1905880` | 8 | c_dlc_async_task |
| `c_dlc_unpacker` | `0x19080d0` | `0x19080a0` | 8 | c_dlc_installer_object |
| `c_dlc_vender` | `0x1908290` | `0x1908260` | 8 | c_dlc_installer_object |
| `c_orbis_binary_invitation_async_request_base` | `0x1911c20` | `0x1911bf0` | 8 | c_orbis_invitation_async_request_base |
| `c_orbis_broadcast_invitation_async_request` | `0x1912290` | `0x1912260` | 8 | c_orbis_json_invitation_async_request_base |
| `c_orbis_check_plus_async_np_task` | `0x1909dc0` | `0x1909da0` | 6 | c_platform_async_np_task<SceNpCheckPlusResult> |
| `c_orbis_get_invitation_async_request` | `0x1911680` | `0x1911650` | 8 | c_orbis_json_invitation_async_request_base |
| `c_orbis_get_invitation_data_async_request` | `0x19123b0` | `0x1912380` | 8 | c_orbis_binary_invitation_async_request_base |
| `c_orbis_get_invitation_list_async_request` | `0x1912350` | `0x1912320` | 8 | c_orbis_json_invitation_async_request_base |
| `c_orbis_get_parental_controls_async_np_task` | `0x1909e10` | `0x1909df0` | 6 | c_platform_async_np_task<s_orbis_parental_controls> |
| `c_orbis_get_psn_availability_async_np_task` | `0x1909e60` | `0x1909e40` | 6 | c_platform_async_np_task<int> |
| `c_orbis_invitation_async_request_base` | `0x1911c38` |  |  |  |
| `c_orbis_json_invitation_async_request_base` | `0x1911bc0` | `0x1911b90` | 8 | c_orbis_invitation_async_request_base |
| `c_orbis_mark_invitation_used_async_request` | `0x19122f0` | `0x19122c0` | 8 | c_orbis_json_invitation_async_request_base |
| `c_platform_async_np_future_task<sce::Toolkit::NP::NpUser>` | `0x1911d10` | `0x1911d40` | 4 | c_platform_async_task_base |
| `c_platform_async_np_future_task<sce::Toolkit::NP::ProductInfoDetailed>` | `0x19117c0` | `0x19117f0` | 4 | c_platform_async_task_base |
| `c_platform_async_np_future_task<std::vector<sce::Toolkit::NP::NpUser, std::allocator<sce::Toolkit::NP::NpUser> > >` | `0x1911af0` | `0x1911b20` | 4 | c_platform_async_task_base |
| `c_platform_async_np_task<SceNpCheckPlusResult>` | `0x1909e80` | `0x1909ef0` | 4 | c_platform_async_task_base |
| `c_platform_async_np_task<int>` | `0x1909ec0` | `0x1909f50` | 4 | c_platform_async_task_base |
| `c_platform_async_np_task<s_orbis_parental_controls>` | `0x1909ea0` | `0x1909f20` | 4 | c_platform_async_task_base |
| `c_platform_async_task` | `0x19095d8` | `0x19095b0` | 7 |  |
| `c_platform_async_task_base` | `0x1909590` | `0x1909580` | 4 |  |
| `c_platform_buffered_webapi_request` | `0x1912070` | `0x1912010` | 8 | detail::c_platform_webapi_request_task |
| `c_platform_events_game_system` | `0x1941760` | `0x1941730` | 8 | c_game_system_interface |
| `c_platform_friends_platform_async_task` | `0x1911ad0` | `0x1911a70` | 6 | c_platform_async_np_future_task<std::vector<sce::Toolkit::NP::NpUser, std::allocator<sce::Toolkit::NP::NpUser> > > |
| `c_platform_friends_platform_query_friends_task_director` | `0x1911ac0` | `0x1911ab0` | 6 |  |
| `c_platform_json_webapi_request` | `0x19120e0` | `0x19120b0` | 8 | detail::c_platform_webapi_request_task |
| `c_platform_keyboard` | `0x1910398` | `0x19103c0` | 5 |  |
| `c_platform_keyboard_game_system` | `0x19416a0` | `0x1941670` | 8 | c_game_system_interface |
| `c_platform_keyboard_orbis` | `0x1910380` | `0x1910350` | 5 | c_platform_keyboard |
| `c_platform_player_properties_platform_profile_async_task` | `0x1911cf0` | `0x1911cc0` | 8 | c_platform_async_np_future_task<sce::Toolkit::NP::NpUser> |
| `c_platform_properties_game_system` | `0x19412c0` | `0x1941290` | 8 | c_game_system_interface |
| `c_platform_security_client_state_handler_base` | `0x1910b08` |  |  |  |
| `c_platform_security_client_state_handler_checking_cache` | `0x1910a50` | `0x1910a30` | 3 | c_platform_security_client_state_handler_base |
| `c_platform_security_client_state_handler_complete` | `0x1910a00` | `0x19109e0` | 3 | c_platform_security_client_state_handler_base |
| `c_platform_security_client_state_handler_initializing` | `0x19109b0` | `0x1910990` | 3 | c_platform_security_client_state_handler_base |
| `c_platform_security_client_state_handler_sending_request` | `0x1910af0` | `0x1910ad0` | 3 | c_platform_security_client_state_handler_base |
| `c_platform_security_client_state_handler_updating_cache` | `0x1910aa0` | `0x1910a80` | 3 | c_platform_security_client_state_handler_base |
| `c_platform_user_game_system` | `0x1941700` | `0x19416d0` | 8 | c_game_system_interface |
| `c_trophy_enumeration_task` | `0x1914470` | `0x1914440` | 5 | c_platform_async_task |
| `c_trophy_registration_task` | `0x19143b0` | `0x1914380` | 5 | c_platform_async_task |
| `c_trophy_reporting_task` | `0x1914410` | `0x19143e0` | 5 | c_platform_async_task |
| `c_trophy_unlock_task` | `0x19144d0` | `0x19144a0` | 5 | c_platform_async_task |
| `detail::c_platform_webapi_request_task` | `0x1912040` | `0x1911fd0` | 6 | c_platform_async_task |
| `i_dlc_category_installer` | `0x1907d98` |  |  |  |
| `i_dlc_installer_progress` | `0x1907ea8` |  |  |  |

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
