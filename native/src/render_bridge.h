// Interface between d1-native's firmware layer and the optional renderer
// (native/renderer/, built with -DD1_RENDERER_SHADPS4=ON). Only plain types cross it, so
// the renderer's headers never leak into the rest of the program.
#pragma once
#include <cstdint>

namespace d1::render {

// SceVideoOutBufferAttribute (40 bytes).
struct VoAttr {
    uint32_t pixel_format, tiling_mode;
    int32_t aspect_ratio;
    uint32_t width, height, pitch_in_pixel;
    uint32_t option, reserved0;
    uint64_t reserved1;
};
static_assert(sizeof(VoAttr) == 40);

struct Callbacks {
    void (*eop)();                             // GPU end-of-pipe interrupt
    void (*flip)(int32_t index, int64_t arg);  // a frame left the GPU: update flip status/events
    uint64_t* labels;                          // video out buffer labels (16 x u64)
    uint32_t sdk_version;                      // from the eboot's process parameters
    // display options (settings.h)
    int window_width, window_height;           // initial window size in pixels
    bool fullscreen;                           // borderless fullscreen on the current display
    const char* present_mode;                  // Vulkan present mode: "Fifo", "Mailbox" or "Immediate"
    bool overlay;                              // stats overlay shown at start (F3 toggles)
};

// Creates the Vulkan device, the command processor and the rasterizer. Returns false (and
// logs why) when no Vulkan device is usable; the null GPU stays in charge then.
bool init(const Callbacks& cb);
bool active();

void register_buffers(int32_t start, void* const* addrs, int32_t num, const VoAttr& attr);
void submit(uint32_t count, uint32_t* const* dcbs, const uint32_t* dcb_sizes, uint32_t* const* ccbs,
            const uint32_t* ccb_sizes);
int32_t submit_and_flip(uint32_t count, uint32_t* const* dcbs, const uint32_t* dcb_sizes, uint32_t* const* ccbs,
                        const uint32_t* ccb_sizes, uint32_t buf, int64_t arg);
void cpu_flip(int32_t index, int64_t arg);
void submit_done();

// Guest memory visible to the GPU, and CPU writes to pages the GPU caches.
void on_map(uint64_t addr, uint64_t size);
void on_unmap(uint64_t addr, uint64_t size);
bool on_fault(void* ucontext, void* addr);

// libSceGnmDriver command builders that the game calls (they emit real PM4 packets).
uint32_t draw_init_default_hw_state(uint32_t* cmd, uint32_t size);
uint32_t dispatch_init_default_hw_state(uint32_t* cmd, uint32_t size);
int32_t insert_wait_flip_done(uint32_t* cmd, uint32_t size, uint32_t buf);
int32_t set_ps_shader(uint32_t* cmd, uint32_t size, const uint32_t* regs);
int32_t set_vs_shader(uint32_t* cmd, uint32_t size, const uint32_t* regs, uint32_t modifier);
int32_t set_cs_shader(uint32_t* cmd, uint32_t size, const uint32_t* regs);
int32_t set_es_shader(uint32_t* cmd, uint32_t size, const uint32_t* regs, uint32_t modifier);
int32_t set_gs_shader(uint32_t* cmd, uint32_t size, const uint32_t* regs);
int32_t set_hs_shader(uint32_t* cmd, uint32_t size, const uint32_t* regs, uint32_t param);
int32_t set_ls_shader(uint32_t* cmd, uint32_t size, const uint32_t* regs, uint32_t modifier);

void print_summary();

// Window and input (renderer build with a display). The pad state uses ScePadData's
// button bits and 0..255 stick axes (0x80 = centre).
struct PadState {
    uint32_t buttons;
    uint8_t lx, ly, rx, ry, l2, r2;
};
// Stats overlay (FPS, resolutions, v-sync, GPU, game state); F3 toggles it.
bool overlay_enabled();
void set_overlay(bool on);

bool window_active();
bool read_pad(PadState& out);  // false when there is no window: caller keeps its own input
// Raw mouse motion (device counts, no OS acceleration) accumulated since the last call while
// the window holds the cursor; the counts are consumed. False when the cursor is not captured.
bool take_mouse_motion(int32_t& dx, int32_t& dy);
// Audio (renderer build with a window): open the speakers for 7.1 float frames (SDL order
// L R C LFE back-L back-R side-L side-R; the device downmixes), and queue a buffer. Output
// blocks while about three buffers are queued, which paces the game's mixer like the
// console's audio port.
bool audio_open(uint32_t freq, uint32_t frames);
void audio_output(const float* frames8, uint32_t frames);
void run_window_loop();        // main thread; returns when the window is closed

}  // namespace d1::render

namespace d1 {
// Implemented by hle_kernel.cpp: bytes from addr to the end of its guest mapping (0 if unknown).
uint64_t guest_region_extent(uint64_t addr);
}  // namespace d1
