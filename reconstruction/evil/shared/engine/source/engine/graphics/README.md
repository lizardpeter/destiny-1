# graphics/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `engine.graphics`  
**Folder path evidence:** `CONFIRMED_BINARY`  
**Role:** renderer; mostly non-virtual, so nearly invisible to RTTI (seen via heaps 'Render Prepare/Submit * State', 'GPU Main Resources'); TFX VM and render context live here

## Sub-folders

- [`cloth/`](features/cloth/README.md) — Havok Cloth integration

## Source files named in the binary

_None recovered (retail build stripped most asserts)._

## Decompiled functions

| VA | name | class | evidence | pseudo-C | role |
|---|---|---|---|---|---|
| `0x7ebfc0` | lighting_frame_update |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`7ebfc0_lighting_frame_update.c`](decompiled/7ebfc0_lighting_frame_update.c) | Per-frame lighting-globals driver: global channel update passes, sets channel g_18dcc54 (hash 0xE6AEB9EC, name unknown) from a virtual getter, then runs c_sun_manager update_directions / update_intensity / update_shadow. |
| `0x7ec3a0` | sun_frame_channel_resolve |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`7ec3a0_sun_frame_channel_resolve.c`](decompiled/7ec3a0_sun_frame_channel_resolve.c) | Resolves channel index g_18dcc54 = find_global_channel(0xE6AEB9EC). |
| `0x7ecbc0` | renderer_frame_prepare |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`7ecbc0_renderer_frame_prepare.c`](decompiled/7ecbc0_renderer_frame_prepare.c) | Renderer per-frame prepare; runs exposure controller update sub_843500(&G, renderer) among other per-frame updates. |
| `0x807750` | frame_extern_build |  | CONFIRMED_BINARY (disassembly) | [`807750_frame_extern_build.c`](decompiled/807750_frame_extern_build.c) | Builds TFX extern 1 (Frame, 0x170 bytes). [0]=renderer+0x1896C, [1..4]=+0x18978/+0x18974/+0x18970/+0x1897C, +0x14=1/30, +0x18=1/60, +0x1C=exp2f(E), +0x20=E, +0x24=exp2f(0.33E), +0x28=exp2f(0.33E)/exp2f(E), +0x160..0x168=G+0x204..0x20C, rest via 0x820D30. |
| `0x80aa80` | frame_setup |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`80aa80_frame_setup.c`](decompiled/80aa80_frame_setup.c) | Calls frame_extern_build with E=G+0xC (G=0x2709B28 exposure controller), 0.33*E, G+0x204/208/20C; allocates three 'light_sample_result' readbacks. Also points render-context ctx+0x13F0 at renderer+0x18958 (global channel copy) and ctx+0x13E8 at renderer+0x18950. |
| `0x815420` | global_channels_alloc |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`815420_global_channels_alloc.c`](decompiled/815420_global_channels_alloc.c) | Allocates the 0x1000-byte global channel vec4 array g_26f1fc0 (heap tag 'Extracted global channel data'); clears handle g_26f1fec. |
| `0x815460` | global_channels_free |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`815460_global_channels_free.c`](decompiled/815460_global_channels_free.c) | Releases g_26f1fc0 and resets count g_26f1fc8 / handle g_26f1fec. |
| `0x8154e0` | global_channels_load_defaults |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`8154e0_global_channels_load_defaults.c`](decompiled/8154e0_global_channels_load_defaults.c) | Loads defaults from the global-channel definition tag g_26f1ff0 (activity tag field_34): parallel arrays of 100 FNV-1 name hashes (+0x8) and vec4 defaults (+0x18) into g_26f1fc0; count -> g_26f1fc8. |
| `0x815600` | global_channels_update_a |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`815600_global_channels_update_a.c`](decompiled/815600_global_channels_update_a.c) | Per-frame global channel update, first pass (called from lighting_frame_update 0x7ebfc0). |
| `0x815790` | global_channels_update_b |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`815790_global_channels_update_b.c`](decompiled/815790_global_channels_update_b.c) | Per-frame global channel update, second pass; honours override bit flags g_26f1fcc[4]. |
| `0x816100` | global_channel_get |  | CONFIRMED_BINARY (decompiled data flow) | [`816100_global_channel_get.c`](decompiled/816100_global_channel_get.c) | get_global_channel(int index, vec4* out): bounds-checked read of g_26f1fc0[index]; returns false when out of range. |
| `0x816170` | global_channel_set |  | CONFIRMED_BINARY (decompiled data flow) | [`816170_global_channel_set.c`](decompiled/816170_global_channel_set.c) | set_global_channel(int index, const vec4* v): stores into g_26f1fc0[index] unless the bit in g_26f1fcc is set (then routes through 0x99f80 and zeroes). |
| `0x816240` | global_channel_find |  | CONFIRMED_BINARY (decompiled data flow) | [`816240_global_channel_find.c`](decompiled/816240_global_channel_find.c) | find_global_channel(const u32* name_hash) -> index: linear search of the definition tag's hash array; -1 if absent. Name hash is FNV-1 32 (verified by preimages, e.g. 'sun_color' = 0x90745795). |
| `0x8162d0` | global_channels_copy_to_renderer |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`8162d0_global_channels_copy_to_renderer.c`](decompiled/8162d0_global_channels_copy_to_renderer.c) | Per-frame copy of g_26f1fc0 into renderer+0x18958 (the array render-context ctx+0x13F0 points at, read by TFX opcode 0x4B). Called from renderer_frame_prepare. |
| `0x822270` | render_context_reset |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`822270_render_context_reset.c`](decompiled/822270_render_context_reset.c) | Sets ctx+0x15C0/0x15C8; when resetting clears extern table (0x288), arena (0x1004), undo list (0xFF x 384) and state at +0x13D8..+0x15D4. |
| `0x822350` | render_context_capture_externs |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`822350_render_context_capture_externs.c`](decompiled/822350_render_context_capture_externs.c) | Clones a source context: deep-copies each pending extern block into own arena and repoints slots; copies +0x13D8/+0x13E8/+0x15AC/+0x15B0/+0x15D0/+0x15D4. |
| `0x829300` | tfx_vm_execute |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS |  | TFX expression VM: opcode=byte[pc], dispatch opcode-1 over 0x50 handlers (jump table 0x82B288). 0x3C/0x3D/0x3E read extern block ptr ctx[0x1008+id*8], element*4 (Float) or *16 (Vec4/Mat4). 0x4B k: push vec4 channels[k] from ptr ctx+0x13F0 (zero if null). |
| `0x82b940` | tfx_extern_alloc |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`82b940_tfx_extern_alloc.c`](decompiled/82b940_tfx_extern_alloc.c) | void* (ctx, uint id, size): bump-allocate 16-aligned block in ctx arena (cursor ctx+0x1000), slot[id]=ctx+0x1008+id*8, size ctx+0x1290+id*4, push undo {id,prev_ptr,prev_size} at ctx+0x1428 (count ctx+0x15A8), zero-fill, set dirty bit ctx+0x15B0. 131 callers. |
| `0x82bd10` | tfx_bind_stage |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`82bd10_tfx_bind_stage.c`](decompiled/82bd10_tfx_bind_stage.c) | Per shader stage: copy constants into cbuffer from ctx+0x15C0 allocator, run tfx_vm_execute when bytecode size>0, then 0x82BE10 resource bind. ~110 callers in render features (VS/PS pairs). |
| `0x8439e0` | auto_exposure_update |  | CONFIRMED_BINARY (disassembly) | [`8439e0_auto_exposure_update.c`](decompiled/8439e0_auto_exposure_update.c) | Writes G+0xC (EV). Disabled: hold. Fast mode: lerp to target at 0.85 when \|d\|<0.2 else tweak 0x18DEEB4. Windowed: min/max of last N targets (N=settings+0x19504 clamped 1..60, ring G+0x20); adapt only outside window at min(\|d\|*settings+0x1950C, settings+0x19508). Clamp [settings+0x194F4, +0x194F8]; output ring G+0x110; index G+0x200 mod 60. |
| `0x844100` | auto_exposure_scaled |  | CONFIRMED_BINARY (disassembly) | [`844100_auto_exposure_scaled.c`](decompiled/844100_auto_exposure_scaled.c) | returns *(float*)0x18DEEB0 (=0.33, writable) * G[+0xC]. |
| `0x844170` | auto_exposure_history_shift |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`844170_auto_exposure_history_shift.c`](decompiled/844170_auto_exposure_history_shift.c) | Frame-delayed history: G+0x10<-G+0xC, G+0x14<-G+0x10, int ring G+0/4/8; uses 1/a1[55]*0.0625. |
| `0x844380` | auto_exposure_static_init |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`844380_auto_exposure_static_init.c`](decompiled/844380_auto_exposure_static_init.c) | C++ static ctor for G=0x2709B28: E=0, history=-3.0, config 1,1,0,-3.0,0.25,-1.0,1.0,0.01,0.9,6,0.05,0.05. |
| `0x876400` | tfx_vm_execute_alt |  | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS |  | Second TFX VM variant: opcodes 0x01..0x48 (jump table 0x8782E8); single caller 0x8763A0. |
| `0x8b1f10` | c_sun_manager::resolve_channels | c_sun_manager | CONFIRMED_BINARY (vtable 0x1949560 slot 2) | [`8b1f10_c_sun_manager__resolve_channels.c`](decompiled/8b1f10_c_sun_manager__resolve_channels.c) | Resolves 8 channel indices by FNV-1 hash: +0x8 sun_light_direction, +0xC sun_atmosphere_direction, +0x10 sun_ambient_direction, +0x14 0x7C61F53B, +0x18 0x38D8C873, +0x20 sun_intensity, +0x24 sun_shadow_intensity, +0x28 0xBEBDF937. |
| `0x8b2000` | c_sun_manager::vslot3 | c_sun_manager | CONFIRMED_BINARY (vtable 0x1949560 slot 3) | [`8b2000_c_sun_manager__vslot3.c`](decompiled/8b2000_c_sun_manager__vslot3.c) | Clears sun tag handle and state bytes/word at this+0x30..0x34. |
| `0x8b2020` | c_sun_manager::update_directions | c_sun_manager | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`8b2020_c_sun_manager__update_directions.c`](decompiled/8b2020_c_sun_manager__update_directions.c) | Reads the sun tag (handle this+0x2c) or override vectors; writes sun_light_direction, sun_atmosphere_direction, channel 0x7C61F53B, and sun_ambient_direction = scale(channel 0x38D8C873) * -light_dir.xy. |
| `0x8b23f0` | c_sun_manager::update_intensity | c_sun_manager | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`8b23f0_c_sun_manager__update_intensity.c`](decompiled/8b23f0_c_sun_manager__update_intensity.c) | Scales sun_intensity by (1 - max fade) over volumes of kind 2 at renderer+0x18988; sets renderer+0x18925 when kind-13 volumes reach full weight. |
| `0x8b2850` | c_sun_manager::update_shadow_state | c_sun_manager | CONFIRMED_BINARY (decompiled data flow); names are HYPOTHESIS | [`8b2850_c_sun_manager__update_shadow_state.c`](decompiled/8b2850_c_sun_manager__update_shadow_state.c) | Picks sun shadow mode renderer+0x18920 (0..3) from sun_intensity/sun_shadow_intensity; zeroes sun_intensity, sun_shadow_intensity and channel 0xBEBDF937 when disabled. |
| `0x8b29a0` | c_sun_manager::vslot1 | c_sun_manager | CONFIRMED_BINARY (vtable 0x1949560 slot 1) | [`8b29a0_c_sun_manager__vslot1.c`](decompiled/8b29a0_c_sun_manager__vslot1.c) | Clears sun tag handle (this+0x2c = -1) and flag byte this+0x30. |

## Classes (6)

Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. Placement in this folder is `HYPOTHESIS` (name-token rule).

| class | typeinfo | vtable | virtual slots | bases |
|---|---|---|---|---|
| `c_bitmap_widget` | `0x194d3f0` | `0x194d2e0` | 26 | c_bitmap_widget_base |
| `c_bitmap_widget_base` | `0x194d410` | `0x194d440` | 26 | c_cui_widget |
| `c_debug_render_game_interface` | `0x1938678` |  |  |  |
| `c_sun_manager` | `0x1949590` | `0x1949560` | 8 | c_game_system_interface |
| `c_video_system` | `0x1914b90` | `0x1914b60` | 8 | c_game_system_interface |
| `c_wrapping_bitmap_widget` | `0x196aec0` | `0x196adb0` | 26 | c_bitmap_widget |

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
