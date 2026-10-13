# main/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `omaha.main`  
**Folder path evidence:** `CONFIRMED_BINARY`  
**Role:** entry point and world-controller shim

## Source files named in the binary

Verbatim path strings (`CONFIRMED_BINARY`). Each has a placeholder file here to be filled in.

- `d:\bungie\evil\shared\engine\source\omaha\main\main.cpp` → [`main.cpp`](main.cpp) — not yet reconstructed
- `d:\bungie\evil\shared\engine\source\omaha\main\omaha_world_controller_shim.cpp` → [`omaha_world_controller_shim.cpp`](omaha_world_controller_shim.cpp) — not yet reconstructed

## Decompiled functions

| VA | name | class | evidence | pseudo-C | role |
|---|---|---|---|---|---|
| `0x1cf60` | startup_mode_override_stub |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`1cf60_startup_mode_override_stub.c`](decompiled/1cf60_startup_mode_override_stub.c) | Stripped development override; returns -1 in retail. |
| `0x239b70` | startup_flag_editor_world_controller |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`239b70_startup_flag_editor_world_controller.c`](decompiled/239b70_startup_flag_editor_world_controller.c) | Start-up flag selecting the editor world controller (EWC). |
| `0x52c020` | startup_select_world_controller |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`52c020_startup_select_world_controller.c`](decompiled/52c020_startup_select_world_controller.c) | Start-up mode choice: a stripped override (0x1CF60 -> -1), then EWC if the start-up flag (0x239B70) is set, otherwise OWC. |
| `0x591710` | time_control_apply |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`591710_time_control_apply.c`](decompiled/591710_time_control_apply.c) | Consumes frame time / fps from the time-control config. |
| `0x593890` | time_control_frame_seconds |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`593890_time_control_frame_seconds.c`](decompiled/593890_time_control_frame_seconds.c) | Frame time in seconds from time-control +0x08. |
| `0x5938b0` | time_control_fps |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`5938b0_time_control_fps.c`](decompiled/5938b0_time_control_fps.c) | Frames per second from time-control +0x08. |
| `0x593f00` | time_control_config_build |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`593f00_time_control_config_build.c`](decompiled/593f00_time_control_config_build.c) | Builds the time-control config globals (pointer 0x26BCD08, 0x48 bytes) from float seconds; +0x08 frame period, +0x38 (D1_FPS hook rewrites both). |
| `0x594460` | main_loop |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`594460_main_loop.c`](decompiled/594460_main_loop.c) | Main loop: waits for the next frame period from the time-control config. |
| `0x6e95f0` | console_command_release_stub |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`6e95f0_console_command_release_stub.c`](decompiled/6e95f0_console_command_release_stub.c) | Console command entry in release: does nothing (init files cannot run console commands in this build). |

## Classes (0)

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
