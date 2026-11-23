// The native renderer's Vulkan side: executes the draws the engine recorded through its GPU
// device layer (src/native_gfx.cpp captures them) with our own translated shaders, our own
// images and our own pipelines. No PM4, no emulated GPU.
#pragma once
#include <functional>
#include <cstdint>
#include <vector>

namespace d1::ng {

constexpr int kStages = 2;  // 0 = vertex, 1 = pixel
constexpr uint8_t kTexIsTarget = 1u << 5;

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
    uint64_t order = 0;         // DCB write position when recorded
    uint32_t seq = 0;
    uint32_t frame = 0;         // video-out flip count when recorded
    uint64_t caller = 0;        // engine call site (diagnostics)
    const uint8_t* vs = nullptr;  // engine vertex shader object (fetch shader size/address, Gnm VsShader at +0x14)
    const uint8_t* ps = nullptr;  // Gnm PsShader
    uint32_t num_vb = 0;
    uint32_t vb[16][4] = {};    // V# per vertex buffer API slot (vertex declaration element)
    uint32_t tex[kStages][16][8] = {};
    uint32_t smp[kStages][16][4] = {};
    uint16_t tex_mask[kStages] = {}, smp_mask[kStages] = {};
    const uint32_t* T(int s, uint32_t i) const { return (tex_mask[s] >> (i & 15) & 1) ? tex[s][i & 15] : nullptr; }
    const uint32_t* S(int s, uint32_t i) const { return (smp_mask[s] >> (i & 15) & 1) ? smp[s][i & 15] : nullptr; }
    struct Cb { uint64_t addr; uint32_t size; } cb[kStages][16] = {};
    // Engine resources: identity id << 32 | epoch, 0 when not a registered resource.
    uint64_t tex_res[kStages][16] = {};
    uint64_t tex_obj[kStages][16] = {};
    struct Res { uint64_t id = 0, base = 0, size = 0; } vres[16], ires;
    // Resolved bindless descriptor table indices and pipeline signature words (populated once before draw):
    uint16_t tex_view[kStages][16] = {};  // bindless view_id in global descriptor table
    uint8_t tex_dk[kStages][16] = {};     // bits 0..1: TexDim, bits 2..3: tex_kind, bit 4: filterable, bit 5: kTexIsTarget
    uint16_t tex_filter_mask[kStages] = {};  // bit i = 1 if texture slot i supports linear filtering
    uint16_t smp_lin[kStages][16] = {};   // bindless sampler_id (default/linear)
    uint16_t smp_near[kStages][16] = {};  // bindless sampler_id (forced nearest for non-filterable textures)
    uint64_t tex_sig[kStages] = {};       // 4 bits per slot: (dim | kind << 2) << (slot * 4)
    uint64_t vb_sig = 0;                  // pre-mixed hash of vertex buffer strides & formats
    bool samples_target = false;          // true if any active texture slot references a render target
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
    bool (*window_handles)(WindowHandles& out) = nullptr;
    void (*window_size)(uint32_t& w, uint32_t& h) = nullptr;
    const char* present_mode = "Immediate";  // "Fifo", "Mailbox" or "Immediate"
    uint32_t frames_in_flight = 2;           // frames the CPU may record ahead of the GPU
    const char* pipeline_cache = nullptr;    // file for the Vulkan pipeline cache (kept between runs)
    uint64_t (*watch)(uint64_t addr, uint64_t size) = nullptr;
    uint64_t (*version)(uint64_t addr, uint64_t size) = nullptr;
    void (*describe)(uint64_t addr, char* out, size_t n) = nullptr;
    uint64_t (*res_current)(uint64_t obj) = nullptr;
};

bool init(const Options& opt);
bool active();
void execute(const std::vector<Draw*>& draws);

constexpr uint64_t kLateCb = 1ull << 62;
constexpr uint8_t kEopLabel = 0xE0;  // Draw::prim of a WriteData that is an end-of-pipe label
struct LateCb { uint8_t stage, slot; uint32_t size; uint64_t off; };
bool list_recording();
bool record_list(const std::vector<Draw*>& items, uint32_t& handle, std::vector<LateCb>& late);
void fill_late(const LateCb& l, uint64_t src, uint32_t size);
void submit_recorded(const std::vector<uint32_t>& handles);
void prefetch_texture(const uint32_t* tsharp, uint64_t res, uint64_t obj);
void notify_texture_mips(const uint32_t* tsharp, uint64_t res, uint64_t obj, uint64_t low_base, uint64_t hi_base);
void prefetch_buffer(uint64_t base, uint64_t size, uint64_t res, uint64_t obj);
void prefetch_shader(const uint8_t* obj, bool is_vs, uint64_t res = 0, uint64_t tag = 0);
void prefetch_shader_pair(const uint8_t* vs_obj, const uint8_t* ps_obj);
void cpu_wrote(uint64_t addr, uint64_t size);
void discard_recorded(uint32_t handle);
void after_gpu(std::function<void()> fn);
void flip(uint64_t addr, uint32_t width, uint32_t height, uint64_t frame, bool dump);
void print_stats();
void describe_owner(uint64_t addr, char* out, size_t n);
void request_passlog(uint32_t frames);
uint64_t presented_frames();
struct Counters { uint64_t pipelines, shaders, textures, tex_bytes, draws; };
Counters counters();
const char* gpu_name();

uint32_t debug_toggles();
void flip_debug_toggle(int bit);
const char* debug_toggle_text();

}  // namespace d1::ng
