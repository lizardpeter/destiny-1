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
    enum Kind : uint8_t { Indexed, Auto, Clear, ZPass, PredOn, PredOff, Dma, WriteData, Eop };
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
    // Engine resources (the engine's own bookkeeping, see native_gfx.cpp resreg): identity
    // id << 32 | epoch, 0 when not a registered resource (then write-tracked). A resource's
    // contents only change when its epoch does: per T# slot, per vertex declaration element
    // (with the whole buffer's memory), and the index buffer.
    uint64_t tex_res[kStages][16] = {};
    struct Res { uint64_t id = 0, base = 0, size = 0; } vres[16], ires;
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
    // engine resources: the current id << 32 | epoch of a resource object (0: not one)
    uint64_t (*res_current)(uint64_t obj) = nullptr;
};

bool init(const Options& opt);
bool active();
// Records and submits draws (already in GPU order). The GPU runs them asynchronously; data
// they read from guest memory is copied while recording.
void execute(const std::vector<Draw*>& draws);
// ---- recording on the engine's own threads (native device layer)
// A command list is recorded into its own Vulkan command buffer by the thread that ends it;
// the GPU queue thread only submits the recorded lists, in the engine's submission order.
// Constant buffers a list inherits from earlier lists (the constant engine's bindings carry
// across command buffers) are only known at submission: such a Draw::Cb has
// addr = kLateCb | stage << 4 | slot, and the list's draws read one ring region per slot,
// filled at submission (fill_late) from the bindings in effect when the list starts.
constexpr uint64_t kLateCb = 1ull << 62;
struct LateCb { uint8_t stage, slot; uint32_t size; uint64_t off; };
bool list_recording();  // on (D1_ND_RECORD, default on) and no per-draw diagnostics running
// false: not recorded (the caller executes the list's draws at submission instead)
bool record_list(const std::vector<Draw*>& items, uint32_t& handle, std::vector<LateCb>& late);
void fill_late(const LateCb& l, uint64_t src, uint32_t size);
void submit_recorded(const std::vector<uint32_t>& handles);  // in this order
// An engine resource was bound, moved or changed (its epoch is `res`): its GPU copy is made on
// the renderer's loader thread now, as a PC engine uploads at load, not at the first draw.
// `obj` is the resource object (to drop the work if it changes again meanwhile).
void prefetch_texture(const uint32_t* tsharp, uint64_t res, uint64_t obj);
void prefetch_buffer(uint64_t base, uint64_t size, uint64_t res, uint64_t obj);
// The CPU wrote [addr, addr + size) of memory that is no engine resource (a dynamic texture's
// unlock, a copy-queue write; size 0: the resource starting at addr): copies of it are stale.
void cpu_wrote(uint64_t addr, uint64_t size);
void discard_recorded(uint32_t handle);                       // never submitted
// The video-out buffer at `addr` was flipped: present it to the window (if any), dump it when
// frames are being written (dump = true), and limit how far the CPU runs ahead.
void flip(uint64_t addr, uint32_t width, uint32_t height, uint64_t frame, bool dump);
void print_stats();
// (diagnostics) what the renderer keeps a copy of at a guest address
void describe_owner(uint64_t addr, char* out, size_t n);
// Log the passes of the next `frames` frames (diagnostics).
void request_passlog(uint32_t frames);
// Frame timing for the title bar: presented frames and the GPU name.
uint64_t presented_frames();
// running totals: pipelines and shaders created, textures uploaded, texture bytes copied
struct Counters { uint64_t pipelines, shaders, textures, tex_bytes, draws; };
Counters counters();
const char* gpu_name();

// Testing switches flipped at run time (F5..F8 in the window), to narrow down rendering
// problems while playing: bit 0 occlusion queries off (every query visible, no predication),
// bit 1 readbacks not waited for, bit 2 no readbacks, bit 3 no geometry cache.
uint32_t debug_toggles();
void flip_debug_toggle(int bit);
const char* debug_toggle_text();  // e.g. " [F5 queries off]" (empty when none is on)

}  // namespace d1::ng
