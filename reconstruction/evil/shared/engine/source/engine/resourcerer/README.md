# resourcerer/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `engine.resourcerer`  
**Folder path evidence:** `HYPOTHESIS` (folder name is a proposal from RTTI/log-channel clustering, not a recovered path)  
**Role:** resource loading, contexts, defrag (log 'resourcerer:*')

## Source files named in the binary

_None recovered (retail build stripped most asserts)._

## Decompiled functions

| VA | name | class | evidence | pseudo-C | role |
|---|---|---|---|---|---|
| `0x106bf0` | client_reference_manager_create |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`106bf0_client_reference_manager_create.c`](decompiled/106bf0_client_reference_manager_create.c) | Allocates the client_reference_manager (0x2BE20 bytes). |
| `0x1072c0` | client_reference_lookup |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`1072c0_client_reference_lookup.c`](decompiled/1072c0_client_reference_lookup.c) | Looks up a client reference (type, index) in the client reference manager (types at +0x2BD1C, slots +0x2A51C, entries +0x520). |
| `0x10c500` | activity_mode_value |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-13); names are HYPOTHESIS | [`10c500_activity_mode_value.c`](decompiled/10c500_activity_mode_value.c) | Byte +0x1AC of client reference type 0x10 (the current activity mode tag); false when missing or -1. |

## Classes (24)

Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. Placement in this folder is `HYPOTHESIS` (name-token rule).

| class | typeinfo | vtable | virtual slots | bases |
|---|---|---|---|---|
| `c_bslib_unshippable_allocator` | `0x1907b40` | `0x1907ac0` | 3 | c_allocation_interface |
| `c_crash_report_timer_files` | `0x1905ce0` | `0x1905ca0` | 7 | i_crash_report_files |
| `c_demonware_http_upload_client::c_upload_stream_callback` | `0x1904cb0` | `0x1904ca0` | 1 | c_http_upload_stream_callback |
| `c_dynamic_hi_mip_streaming_game_interface` | `0x1947dd0` | `0x1947da0` | 8 | c_game_system_interface |
| `c_file_async_thread_implementation` | `0x194c440` | `0x194c410` | 5 | c_file_async_thread_interface |
| `c_file_async_thread_interface` | `0x194c458` |  |  |  |
| `c_json_allocator` | `0x1911c80` | `0x1911c60` | 6 | sce::Json::MemAllocator |
| `c_large_block_overflow_allocator` | `0x1909ac0` | `0x19099a0` | 22 | hkLargeBlockAllocator |
| `c_parcel_upload_stream` | `0x1904d30` | `0x1904cf0` | 6 | c_upload_stream |
| `c_resourcerer_context_package_files` | `0x1905ef0` | `0x1905eb0` | 7 | i_crash_report_files |
| `c_retail_datamine_crash_report_uploader` | `0x1945130` | `0x19450f0` | 7 | i_crash_report_files |
| `c_runtime_blueprint_allocator` | `0x19147b0` | `0x19146c0` | 29 | c_schema_record_allocation_interface |
| `c_runtime_memory_interface` | `0x19089d0` | `0x1908970` | 14 | c_physics_memory_interface |
| `c_runtime_memory_system` | `0x19089f0` | `0x1908880` | 27 | hkMemorySystem |
| `c_simple_file` | `0x1904c38` |  |  |  |
| `c_simple_file_buffered` | `0x1904c10` | `0x1904bb0` | 11 | c_simple_file @+0x8 |
| `c_simple_file_buffered_static<4096u>` | `0x1914010` | `0x1913fb0` | 11 | c_simple_file_buffered |
| `c_static_hi_mip_streaming_game_interface` | `0x1947e40` | `0x1947e10` | 8 | c_game_system_interface |
| `c_strict_lifo_allocator` | `0x1909d60` | `0x1909cf0` | 13 | hkLifoAllocator |
| `c_unpacker_open_current_file` | `0x1908230` | `0x1908200` | 8 | c_dlc_async_task |
| `c_unpacker_open_zip_file` | `0x1908130` | `0x1908100` | 8 | c_dlc_async_task |
| `c_unpacker_read_current_file` | `0x1908190` | `0x1908160` | 8 | c_dlc_async_task |
| `c_upload_stream` | `0x1904d10` |  |  |  |
| `i_crash_report_files` | `0x1904db8` |  |  |  |

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
