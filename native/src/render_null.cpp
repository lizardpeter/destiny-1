// Build without the renderer: every entry point reports "not available" and the null GPU
// in hle_gpu.cpp handles command buffers.
#include "render_bridge.h"
#include "settings.h"
#include <cstdio>

namespace d1::render {
bool init(const Callbacks&) { return false; }
bool overlay_enabled() { return false; }
void set_overlay(bool) {}
bool active() { return false; }
bool idle() { return true; }
void wait_idle() {}
void register_buffers(int32_t, void* const*, int32_t, const VoAttr&) {}
void submit(uint32_t, uint32_t* const*, const uint32_t*, uint32_t* const*, const uint32_t*) {}
int32_t submit_and_flip(uint32_t, uint32_t* const*, const uint32_t*, uint32_t* const*, const uint32_t*, uint32_t,
                        int64_t) { return 0; }
void cpu_flip(int32_t, int64_t) {}
void submit_done() {}
void on_map(uint64_t, uint64_t) {}
void on_unmap(uint64_t, uint64_t) {}
bool on_fault(void*, void*) { return false; }
uint32_t draw_init_default_hw_state(uint32_t*, uint32_t) { return 0; }
uint32_t dispatch_init_default_hw_state(uint32_t*, uint32_t) { return 0; }
int32_t insert_wait_flip_done(uint32_t*, uint32_t, uint32_t) { return -1; }
int32_t set_ps_shader(uint32_t*, uint32_t, const uint32_t*) { return -1; }
int32_t set_vs_shader(uint32_t*, uint32_t, const uint32_t*, uint32_t) { return -1; }
int32_t set_cs_shader(uint32_t*, uint32_t, const uint32_t*) { return -1; }
int32_t set_es_shader(uint32_t*, uint32_t, const uint32_t*, uint32_t) { return -1; }
int32_t set_gs_shader(uint32_t*, uint32_t, const uint32_t*) { return -1; }
int32_t set_hs_shader(uint32_t*, uint32_t, const uint32_t*, uint32_t) { return -1; }
int32_t set_ls_shader(uint32_t*, uint32_t, const uint32_t*, uint32_t) { return -1; }
void print_summary() {}
#ifndef D1_FRONTEND_SDL  // else frontend_sdl.cpp: window, input and audio for the native renderer
bool window_active() { return false; }
bool read_pad(PadState&) { return false; }
bool take_mouse_motion(int32_t&, int32_t&) { return false; }
int take_weapon_request() { return -1; }
// headless testing: D1_PROMPTS=keyboard labels every glyph "[#<code>]"
bool keyboard_prompts() { return d1::settings().prompts == "keyboard"; }
int prompt_label(uint32_t glyph, char16_t* out, int max) {
    char text[16];
    const int n = std::snprintf(text, sizeof text, "[#%X]", unsigned(glyph));
    int k = 0;
    for (; k < n && k < max - 1; ++k) out[k] = char16_t(text[k]);
    out[k] = 0;
    return k;
}
bool audio_open(uint32_t, uint32_t) { return false; }
void audio_output(const float*, uint32_t) {}
void run_window_loop() {}
#endif
}  // namespace d1::render
