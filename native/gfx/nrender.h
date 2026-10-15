// The native renderer's Vulkan side: executes the draws the engine recorded through its GPU
// device layer (src/native_gfx.cpp captures them) with our own translated shaders, our own
// images and our own pipelines. No PM4, no emulated GPU.
//
// Everything here is engine-independent GCN / Gnm knowledge: a Draw holds the hardware
// register values and resource descriptors (T#, S#, V#, render-target descriptors) that the
// engine's device object keeps, plus pointers to the Gnm shader objects.
#pragma once
#include <cstdint>
#include <vector>

namespace d1::ng {

constexpr int kStages = 2;  // 0 = vertex, 1 = pixel

struct Draw {
    // ZPass / PredOn / PredOff: command-buffer events at their place among the draws (not draws):
    // an occlusion counter dump to index_addr (ZPASS_DONE), draw predication on the query results
    // at index_addr (count bit 0: draw if visible) and its end (SET_PREDICATION)
    // Dma / WriteData: CP memory writes (DMA_DATA: src index_addr -> dst caller, count bytes,
    // prim = src_sel, index32 = dst_sel, instances = fill value; WRITE_DATA: inline_vertices -> caller),
    // done in order so draws after them read the new data
    enum Kind : uint8_t { Indexed, Auto, Clear, ZPass, PredOn, PredOff, Dma, WriteData };
    Kind kind = Auto;
    uint8_t prim = 4;           // VGT_DI_PRIM_TYPE
    uint8_t index32 = 0;
    uint8_t clear_flags = 0;    // Clear: bits 2..5 color MRT 0..3, 0x40 depth, 0x80 stencil
    uint32_t count = 0, instances = 1;
    uint64_t index_addr = 0;    // Indexed: first index
    uint64_t order = 0;         // DCB write position when recorded (orders draws in a submission)
    uint32_t seq = 0;
    uint32_t frame = 0;         // video-out flip count when recorded (stale-draw diagnostics)
    uint64_t caller = 0;        // engine call site (diagnostics)
    const uint8_t* vs = nullptr;  // engine vertex shader object (fetch shader size/address, Gnm VsShader at +0x14)
    const uint8_t* ps = nullptr;  // Gnm PsShader
    uint32_t num_vb = 0;
    uint32_t vb[16][4] = {};    // V# per vertex buffer API slot (vertex declaration element)
    // T# / S# per stage and slot, copied when the draw is recorded (the engine builds some of
    // them in temporary memory)
    uint32_t tex[kStages][16][8] = {};
    uint32_t smp[kStages][16][4] = {};
    uint16_t tex_mask[kStages] = {}, smp_mask[kStages] = {};
    const uint32_t* T(int s, uint32_t i) const { return (tex_mask[s] >> (i & 15) & 1) ? tex[s][i & 15] : nullptr; }
    const uint32_t* S(int s, uint32_t i) const { return (smp_mask[s] >> (i & 15) & 1) ? smp[s][i & 15] : nullptr; }
    struct Cb { uint64_t addr; uint32_t size; } cb[kStages][16] = {};
    // registers
    uint32_t blend = 0, target_mask = 0xF, su_sc_mode = 0, clip = 0, depth_ctl = 0, stencil_ctl = 0, stencil_ref = 0;
    float poly_offset = 0, poly_scale = 0;
    int32_t vp[4] = {};         // x, y, w, h
    float znear = 0, zfar = 1, zk = 1;
    uint32_t color[5][11] = {}; // Gnm RenderTarget (CB_COLOR_* registers + packed size)
    uint32_t depth[13] = {};    // Gnm DepthRenderTarget
    float clear_color[4] = {};
    float clear_depth = 1;
    uint8_t clear_stencil = 0;
    std::vector<uint8_t> inline_vertices;  // draw from an inline vertex buffer: V# bases are offsets into it
};

// A window to present to (native handles; see vk::create_surface).
struct WindowHandles {
    enum Type { kNone, kWin32, kXlib } type = kNone;
    void* display = nullptr;  // HINSTANCE / Display*
    uint64_t window = 0;      // HWND / X11 Window
};

struct Options {
    const char* frames_dir = nullptr;  // write the flipped image as <dir>/f<N>.ppm
    bool no_cull = false;
    bool dump_targets = false;         // with each written frame, every render target the frame used
    // presentation (optional): the window's handles and its current drawable size
    bool (*window_handles)(WindowHandles& out) = nullptr;
    void (*window_size)(uint32_t& w, uint32_t& h) = nullptr;
    const char* present_mode = "Immediate";  // "Fifo", "Mailbox" or "Immediate"
    uint32_t frames_in_flight = 2;           // frames the CPU may record ahead of the GPU
    const char* pipeline_cache = nullptr;    // file for the Vulkan pipeline cache (kept between runs)
    // write tracking of guest memory (optional): watch() write-protects a range and returns
    // its version; version() is the current one (~0: unknown / not watched). A copy made after
    // watch() stays valid while version() returns the same value.
    uint64_t (*watch)(uint64_t addr, uint64_t size) = nullptr;
    uint64_t (*version)(uint64_t addr, uint64_t size) = nullptr;
    void (*describe)(uint64_t addr, char* out, size_t n) = nullptr;  // (diagnostics) tracking state of a page
};

bool init(const Options& opt);
bool active();
// Records and submits draws (already in GPU order). The GPU runs them asynchronously; data
// they read from guest memory is copied while recording.
void execute(const std::vector<Draw*>& draws);
// The video-out buffer at `addr` was flipped: present it to the window (if any), dump it when
// frames are being written (dump = true), and limit how far the CPU runs ahead.
void flip(uint64_t addr, uint32_t width, uint32_t height, uint64_t frame, bool dump);
void print_stats();
// Log the passes of the next `frames` frames (diagnostics).
void request_passlog(uint32_t frames);
// Frame timing for the title bar: presented frames and the GPU name.
uint64_t presented_frames();
const char* gpu_name();

// Testing switches flipped at run time (F5..F8 in the window), to narrow down rendering
// problems while playing: bit 0 occlusion queries off (every query visible, no predication),
// bit 1 readbacks not waited for, bit 2 no readbacks, bit 3 no geometry cache.
uint32_t debug_toggles();
void flip_debug_toggle(int bit);
const char* debug_toggle_text();  // e.g. " [F5 queries off]" (empty when none is on)

}  // namespace d1::ng
