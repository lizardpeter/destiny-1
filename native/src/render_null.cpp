// Build without the renderer: every entry point reports "not available" and the null GPU
// in hle_gpu.cpp handles command buffers.
#include "render_bridge.h"

namespace d1::render {
bool init(const Callbacks&) { return false; }
bool overlay_enabled() { return false; }
void set_overlay(bool) {}
bool active() { return false; }
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
bool window_active() { return false; }
bool read_pad(PadState&) { return false; }
void run_window_loop() {}
}  // namespace d1::render
