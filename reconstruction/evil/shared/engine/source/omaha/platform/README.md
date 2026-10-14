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
| `0xadc00` | gamepad_state_update |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`adc00_gamepad_state_update.c`](decompiled/adc00_gamepad_state_update.c) | ScePadData -> engine gamepad state (0xC0): triggers +0/+1 with press counters, 15 buttons held-frames/ms counters (bit table 0x15B5AB0), sticks s16 at +0x44 lx, +0x46 ly (up +), +0x48 rx, +0x4A ry (up +), motion +0xB0.., two touch points +0x50/+0x80. |
| `0xae0c0` | gamepad_poll |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`ae0c0_gamepad_poll.c`](decompiled/ae0c0_gamepad_poll.c) | One pad: scePadReadState; on a new connection refreshes scePadGetControllerInformation (touch pad size, dead zone); then gamepad_state_update. |
| `0xae1e0` | gamepad_poll_all |  | Static decompilation of the 01.33 eboot input path (pad -> input abstraction -> player control), 2026-10-13 | [`ae1e0_gamepad_poll_all.c`](decompiled/ae1e0_gamepad_poll_all.c) | Polls every pad slot: gamepad_poll(i) into state[i] (stride 0xC0), stores the connected flag per slot. Pad 0 state is the global 0x1AD40F0. |
| `0xbbe60` | addcont_list_query |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`bbe60_addcont_list_query.c`](decompiled/bbe60_addcont_list_query.c) | Queries installed add-on content (sceAppContentGetAddcontInfoList count-then-fill). |

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
