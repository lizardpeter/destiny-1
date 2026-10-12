# audio/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `engine.audio`  
**Folder path evidence:** `HYPOTHESIS` (folder name is a proposal from RTTI/log-channel clustering, not a recovered path)  
**Role:** tiger_audio / tiger_dialog, CRI and Wwise glue

## Source files named in the binary

_None recovered (retail build stripped most asserts)._

## Decompiled functions

_None yet._

## Classes (24)

Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. Placement in this folder is `HYPOTHESIS` (name-token rule).

| class | typeinfo | vtable | virtual slots | bases |
|---|---|---|---|---|
| `c_audio_interface_callback_handler` | `0x19479c0` | `0x1947990` | 5 | c_audio_system_callback_handler |
| `c_audio_stream_manager` | `0x1947b30` | `0x1947a80` | 11 | AK::StreamMgr::IAkFileLocationResolver, AK::StreamMgr::IAkIOHookDeferred @+0x8 |
| `c_audio_system_callback_handler` | `0x19479d8` |  |  |  |
| `c_close_dialog_component` | `0x194d8d0` | `0x194d7e0` | 22 | c_event_handler_component |
| `c_cri_file_reader` | `0x19149e0` | `0x1914980` | 11 | CriMvFileReaderInterface |
| `c_cri_sound` | `0x1914a80` | `0x1914a20` | 14 | CriMvSoundInterface |
| `c_cri_timer` | `0x1914af0` | `0x1914ac0` | 8 | CriMvSystemTimerInterface |
| `c_dialog_audio` | `0x19478c0` | `0x1947800` | 8 | c_dialog_audio_interface |
| `c_dialog_audio_interface` | `0x1947948` |  |  |  |
| `c_dialog_game_system` | `0x1907c20` | `0x1907bf0` | 8 | c_game_system_interface |
| `c_dialog_pipe_client_component` | `0x194ded0` | `0x194e1f0` | 21 | c_screen_pipe_client_component |
| `c_dialog_pipe_component` | `0x194e3d0` | `0x194e2e0` | 22 | c_screen_pipe_component |
| `c_dialog_pipe_writer_component` | `0x194e520` | `0x194e440` | 21 | c_dialog_pipe_client_component |
| `c_dialog_subtitles` | `0x1969990` | `0x1969970` | 3 | c_dialog_subtitles_interface |
| `c_dialog_subtitles_interface` | `0x1969978` |  |  |  |
| `c_email_confirmation_dialog_handler` | `0x1942660` | `0x1942630` | 2 | i_online_world_controller_ui_dialog_result_handler |
| `c_email_validation_warning_dialog_handler` | `0x1942680` | `0x1942650` | 4 | i_online_world_controller_ui_dialog_result_handler |
| `c_load_dialog_component` | `0x194f500` | `0x194f410` | 22 | c_event_handler_component |
| `c_play_sound_event_component` | `0x194ff20` | `0x194fe40` | 21 | c_cui_object_component |
| `c_tiger_audio_game_system` | `0x19415e0` | `0x19415b0` | 8 | c_game_system_interface |
| `c_tiger_dialog_game_system` | `0x1938490` | `0x1938460` | 8 | c_game_system_interface |
| `c_video_audio` | `0x1947900` | `0x1947880` | 3 | c_video_audio_interface |
| `c_video_audio_interface` | `0x1947968` |  |  |  |
| `c_voice_controller_monitor` | `0x196c420` | `0x196c400` | 3 | c_controller_monitor |

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
