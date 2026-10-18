// Native renderer, Vulkan side. See nrender.h.
//
// Model: each submission's draws are recorded into their own command buffer and submitted
// without waiting; the CPU runs at most `frames_in_flight` frames ahead of the GPU. Every
// image stays in VK_IMAGE_LAYOUT_GENERAL; a full memory barrier sits between render passes
// and at the start of each command buffer. Transient data the draws read from guest memory
// (vertices, indices, constants, texture uploads) is copied into a host-visible circular
// ring while recording; space is reused once the submissions that read it have completed.
// Textures are detiled and uploaded once per distinct T# (and dropped when unused for a
// while); render targets are our own images keyed by (address, format, size), and a T# that
// points at one samples it directly. Device memory for images is suballocated from large
// blocks. Flips blit the video-out target into the window's swapchain.
#include "nrender.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <condition_variable>
#include <functional>
#include <thread>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <deque>
#include <atomic>
#include <map>
#include <set>
#include <memory>
#include <mutex>
#include <string>
#include <unordered_map>
#include <unordered_set>

#include "formats.h"
#include "tiling.h"
#include "translate.h"
#include "vk/vk.h"

namespace d1 {
void log(const char* fmt, ...);
uint64_t guest_region_extent(uint64_t addr);  // bytes from addr to the end of its guest mapping
}

namespace d1::ng {
using namespace d1::vk;

namespace {

// 8 bytes at a time (descriptors and keys are hashed for every draw)
// (h * K1 + v, not h ^ v: with h ^ v, two keys collide whenever their first two values XOR to
// the same thing - (address, size) pairs of vertex ranges, (vs, ps) shader pairs - and a cache
// then hands back another buffer's geometry or another draw's pipeline)
inline uint64_t mix(uint64_t h, uint64_t v) {
    h = (h * 0xC2B2AE3D27D4EB4Full + v) * 0x9E3779B97F4A7C15ull;
    return h ^ (h >> 31);
}
uint64_t hash_bytes(const void* p, size_t n, uint64_t h = 0xcbf29ce484222325ull) {
    const uint8_t* b = static_cast<const uint8_t*>(p);
    size_t i = 0;
    for (; i + 8 <= n; i += 8) {
        uint64_t v;
        std::memcpy(&v, b + i, 8);
        h = mix(h, v);
    }
    if (i < n) {
        uint64_t v = 0;
        std::memcpy(&v, b + i, n - i);
        h = mix(h, v ^ (uint64_t(n) << 56));
    }
    return h;
}
inline uint64_t now_ns() {
    return uint64_t(std::chrono::duration_cast<std::chrono::nanoseconds>(
                        std::chrono::steady_clock::now().time_since_epoch()).count());
}

// ---------------------------------------------------------------------------- Gnm shaders
struct GnmShader {
    const uint8_t* code = nullptr;
    uint32_t code_size = 0;
    std::vector<gcn::UsageSlot> slots;
    uint32_t user_sgprs = 0, ps_input_addr = 0;
    const uint8_t* fetch = nullptr;
    uint32_t fetch_size = 0;
    std::vector<uint16_t> semantics;  // VS: export semantics; PS: input semantics
};

uint32_t rd32(const uint8_t* p) {
    uint32_t v;
    std::memcpy(&v, p, 4);
    return v;
}

// vs: engine vertex shader object (fetch shader size, fetch address, Gnm VsShader at +0x14)
GnmShader parse_shader(const uint8_t* obj, bool vs) {
    GnmShader s;
    const uint8_t* g = obj + (vs ? 0x14 : 0);
    const uint32_t common = rd32(g), nslots = common >> 24;
    const uint32_t regs = vs ? 0x1C : 0x30;
    s.code_size = common & 0x7FFFFF;
    s.code = reinterpret_cast<const uint8_t*>((uint64_t(rd32(g + 8)) << 8) | (uint64_t(rd32(g + 12)) << 40));
    s.user_sgprs = (rd32(g + 8 + 12) >> 1) & 0x1F;
    if (!vs) s.ps_input_addr = rd32(g + 8 + 0x1C);
    const uint8_t* counts = g + 8 + regs;
    const uint8_t* p = counts + 4;
    for (uint32_t k = 0; k < nslots; ++k, p += 4) s.slots.push_back({p[0], p[1], p[2], p[3]});
    if (vs) {
        p += 4u * counts[0];  // input semantics
        for (uint32_t k = 0; k < counts[1]; ++k, p += 2) s.semantics.push_back(uint16_t(p[0] | p[1] << 8));
        s.fetch_size = rd32(obj) & 0x7FFFFF;
        uint64_t f;
        std::memcpy(&f, obj + 8, 8);
        s.fetch = reinterpret_cast<const uint8_t*>(f);
        if (!s.fetch_size) s.fetch = nullptr;
    } else {
        for (uint32_t k = 0; k < counts[0]; ++k, p += 2) s.semantics.push_back(uint16_t(p[0] | p[1] << 8));
    }
    return s;
}

// ---------------------------------------------------------------------------- formats
VkFormat vertex_format(uint32_t d, uint32_t n) {
    struct F { VkFormat un, sn, us, ss, ui, si, fl; };
    static const F t[15] = {
        {},
        {VK_FORMAT_R8_UNORM, VK_FORMAT_R8_SNORM, VK_FORMAT_R8_USCALED, VK_FORMAT_R8_SSCALED, VK_FORMAT_R8_UINT, VK_FORMAT_R8_SINT, {}},
        {VK_FORMAT_R16_UNORM, VK_FORMAT_R16_SNORM, VK_FORMAT_R16_USCALED, VK_FORMAT_R16_SSCALED, VK_FORMAT_R16_UINT, VK_FORMAT_R16_SINT, VK_FORMAT_R16_SFLOAT},
        {VK_FORMAT_R8G8_UNORM, VK_FORMAT_R8G8_SNORM, VK_FORMAT_R8G8_USCALED, VK_FORMAT_R8G8_SSCALED, VK_FORMAT_R8G8_UINT, VK_FORMAT_R8G8_SINT, {}},
        {{}, {}, {}, {}, VK_FORMAT_R32_UINT, VK_FORMAT_R32_SINT, VK_FORMAT_R32_SFLOAT},
        {VK_FORMAT_R16G16_UNORM, VK_FORMAT_R16G16_SNORM, VK_FORMAT_R16G16_USCALED, VK_FORMAT_R16G16_SSCALED, VK_FORMAT_R16G16_UINT, VK_FORMAT_R16G16_SINT, VK_FORMAT_R16G16_SFLOAT},
        {{}, {}, {}, {}, {}, {}, VK_FORMAT_B10G11R11_UFLOAT_PACK32},
        {{}, {}, {}, {}, {}, {}, VK_FORMAT_B10G11R11_UFLOAT_PACK32},
        {VK_FORMAT_A2B10G10R10_UNORM_PACK32, VK_FORMAT_A2B10G10R10_SNORM_PACK32, VK_FORMAT_A2B10G10R10_USCALED_PACK32, VK_FORMAT_A2B10G10R10_SSCALED_PACK32, VK_FORMAT_A2B10G10R10_UINT_PACK32, VK_FORMAT_A2B10G10R10_SINT_PACK32, {}},
        {VK_FORMAT_A2B10G10R10_UNORM_PACK32, VK_FORMAT_A2B10G10R10_SNORM_PACK32, VK_FORMAT_A2B10G10R10_USCALED_PACK32, VK_FORMAT_A2B10G10R10_SSCALED_PACK32, VK_FORMAT_A2B10G10R10_UINT_PACK32, VK_FORMAT_A2B10G10R10_SINT_PACK32, {}},
        {VK_FORMAT_R8G8B8A8_UNORM, VK_FORMAT_R8G8B8A8_SNORM, VK_FORMAT_R8G8B8A8_USCALED, VK_FORMAT_R8G8B8A8_SSCALED, VK_FORMAT_R8G8B8A8_UINT, VK_FORMAT_R8G8B8A8_SINT, {}},
        {{}, {}, {}, {}, VK_FORMAT_R32G32_UINT, VK_FORMAT_R32G32_SINT, VK_FORMAT_R32G32_SFLOAT},
        {VK_FORMAT_R16G16B16A16_UNORM, VK_FORMAT_R16G16B16A16_SNORM, VK_FORMAT_R16G16B16A16_USCALED, VK_FORMAT_R16G16B16A16_SSCALED, VK_FORMAT_R16G16B16A16_UINT, VK_FORMAT_R16G16B16A16_SINT, VK_FORMAT_R16G16B16A16_SFLOAT},
        {{}, {}, {}, {}, VK_FORMAT_R32G32B32_UINT, VK_FORMAT_R32G32B32_SINT, VK_FORMAT_R32G32B32_SFLOAT},
        {{}, {}, {}, {}, VK_FORMAT_R32G32B32A32_UINT, VK_FORMAT_R32G32B32A32_SINT, VK_FORMAT_R32G32B32A32_SFLOAT},
    };
    if (d == 0 || d > 14) return VK_FORMAT_UNDEFINED;
    const F& f = t[d];
    switch (n) {
    case 0: return f.un;
    case 1: return f.sn;
    case 2: return f.us;
    case 3: return f.ss;
    case 4: return f.ui;
    case 5: return f.si;
    case 7: return f.fl;
    default: return VK_FORMAT_UNDEFINED;
    }
}

bool is_sint_format(VkFormat f) {
    switch (f) {
    case VK_FORMAT_R8_SINT: case VK_FORMAT_R16_SINT: case VK_FORMAT_R32_SINT: case VK_FORMAT_R8G8_SINT:
    case VK_FORMAT_R16G16_SINT: case VK_FORMAT_R32G32_SINT: case VK_FORMAT_R8G8B8A8_SINT:
    case VK_FORMAT_R16G16B16A16_SINT: case VK_FORMAT_R32G32B32A32_SINT: case VK_FORMAT_A2B10G10R10_SINT_PACK32:
        return true;
    default:
        return false;
    }
}

bool is_int_format(VkFormat f) {
    switch (f) {
    case VK_FORMAT_R8_UINT: case VK_FORMAT_R8_SINT: case VK_FORMAT_R16_UINT: case VK_FORMAT_R16_SINT:
    case VK_FORMAT_R32_UINT: case VK_FORMAT_R32_SINT: case VK_FORMAT_R8G8_UINT: case VK_FORMAT_R8G8_SINT:
    case VK_FORMAT_R16G16_UINT: case VK_FORMAT_R16G16_SINT: case VK_FORMAT_R32G32_UINT: case VK_FORMAT_R32G32_SINT:
    case VK_FORMAT_R8G8B8A8_UINT: case VK_FORMAT_R8G8B8A8_SINT: case VK_FORMAT_R16G16B16A16_UINT:
    case VK_FORMAT_R16G16B16A16_SINT: case VK_FORMAT_R32G32B32A32_UINT: case VK_FORMAT_R32G32B32A32_SINT:
    case VK_FORMAT_A2B10G10R10_UINT_PACK32:
        return true;
    default:
        return false;
    }
}

// CB_COLOR_INFO NUMBER_TYPE -> image NUM_FORMAT numbering
uint32_t cb_number_to_nfmt(uint32_t n) { return n == 6 ? 9u : n; }

VkComponentSwizzle swz(uint32_t sel) {
    switch (sel) {
    case 0: return VK_COMPONENT_SWIZZLE_ZERO;
    case 1: return VK_COMPONENT_SWIZZLE_ONE;
    case 4: return VK_COMPONENT_SWIZZLE_R;
    case 5: return VK_COMPONENT_SWIZZLE_G;
    case 6: return VK_COMPONENT_SWIZZLE_B;
    case 7: return VK_COMPONENT_SWIZZLE_A;
    default: return VK_COMPONENT_SWIZZLE_ZERO;
    }
}

gcn::TexDim tex_dim(uint32_t type) {
    switch (type) {
    case 10: return gcn::TexDim::Tex3D;
    case 11: return gcn::TexDim::Cube;
    case 12: case 13: return gcn::TexDim::Tex2DArray;
    default: return gcn::TexDim::Tex2D;
    }
}
VkImageViewType view_type(gcn::TexDim d) {
    switch (d) {
    case gcn::TexDim::Tex3D: return VK_IMAGE_VIEW_TYPE_3D;
    case gcn::TexDim::Cube: return VK_IMAGE_VIEW_TYPE_CUBE;
    case gcn::TexDim::Tex2DArray: return VK_IMAGE_VIEW_TYPE_2D_ARRAY;
    default: return VK_IMAGE_VIEW_TYPE_2D;
    }
}

VkBlendFactor blend_factor(uint32_t f) {
    switch (f) {
    case 0: return VK_BLEND_FACTOR_ZERO;
    case 1: return VK_BLEND_FACTOR_ONE;
    case 2: return VK_BLEND_FACTOR_SRC_COLOR;
    case 3: return VK_BLEND_FACTOR_ONE_MINUS_SRC_COLOR;
    case 4: return VK_BLEND_FACTOR_SRC_ALPHA;
    case 5: return VK_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA;
    case 6: return VK_BLEND_FACTOR_DST_ALPHA;
    case 7: return VK_BLEND_FACTOR_ONE_MINUS_DST_ALPHA;
    case 8: return VK_BLEND_FACTOR_DST_COLOR;
    case 9: return VK_BLEND_FACTOR_ONE_MINUS_DST_COLOR;
    case 10: return VK_BLEND_FACTOR_SRC_ALPHA_SATURATE;
    case 13: return VK_BLEND_FACTOR_CONSTANT_COLOR;
    case 14: return VK_BLEND_FACTOR_ONE_MINUS_CONSTANT_COLOR;
    case 15: return VK_BLEND_FACTOR_SRC1_COLOR;
    case 16: return VK_BLEND_FACTOR_ONE_MINUS_SRC1_COLOR;
    case 17: return VK_BLEND_FACTOR_SRC1_ALPHA;
    case 18: return VK_BLEND_FACTOR_ONE_MINUS_SRC1_ALPHA;
    case 19: return VK_BLEND_FACTOR_CONSTANT_ALPHA;
    case 20: return VK_BLEND_FACTOR_ONE_MINUS_CONSTANT_ALPHA;
    default: return VK_BLEND_FACTOR_ONE;
    }
}
VkBlendOp blend_op(uint32_t f) {
    switch (f) {
    case 1: return VK_BLEND_OP_SUBTRACT;
    case 2: return VK_BLEND_OP_MIN;
    case 3: return VK_BLEND_OP_MAX;
    case 4: return VK_BLEND_OP_REVERSE_SUBTRACT;
    default: return VK_BLEND_OP_ADD;
    }
}
VkStencilOp stencil_op(uint32_t o) {
    switch (o) {
    case 1: return VK_STENCIL_OP_ZERO;
    // 2 ONES, 3 REPLACE_TEST, 4 REPLACE_OP: a replace with the value set per draw (stencil_dynamic)
    case 2: case 3: case 4: return VK_STENCIL_OP_REPLACE;
    case 5: return VK_STENCIL_OP_INCREMENT_AND_CLAMP;
    case 6: return VK_STENCIL_OP_DECREMENT_AND_CLAMP;
    case 7: return VK_STENCIL_OP_INVERT;
    case 8: return VK_STENCIL_OP_INCREMENT_AND_WRAP;
    case 9: return VK_STENCIL_OP_DECREMENT_AND_WRAP;
    // AND / OR with STENCILOPVAL: replace with 0 / 0xFF through a write mask of the bits
    // concerned; XOR: invert those bits (stencil_dynamic)
    case 10: case 11: return VK_STENCIL_OP_REPLACE;
    case 12: return VK_STENCIL_OP_INVERT;
    default: return VK_STENCIL_OP_KEEP;
    }
}
// Reference and write mask for a draw's stencil ops (DB_STENCILREFMASK: test value, test mask,
// write mask, op value). Vulkan has one reference for the test and REPLACE, and no
// AND/OR/XOR: the op that writes (z-pass, else z-fail, else fail) picks the value and mask.
void stencil_dynamic(uint32_t stencil_ctl, uint32_t depth_ctl, uint32_t refmask, uint32_t& ref, uint32_t& write_mask) {
    ref = refmask & 0xFF, write_mask = refmask >> 16 & 0xFF;
    const uint32_t opval = refmask >> 24 & 0xFF;
    uint32_t op = stencil_ctl >> 4 & 0xF;
    if (!op) op = stencil_ctl >> 8 & 0xF;
    if (!op) op = stencil_ctl & 0xF;
    int value = -1;
    switch (op) {
    case 2: value = 0xFF; break;
    case 4: value = int(opval); break;
    case 10: value = 0, write_mask &= ~opval & 0xFF; break;
    case 11: value = 0xFF, write_mask &= opval; break;
    case 12: write_mask &= opval; break;
    default: break;
    }
    const uint32_t func = depth_ctl >> 8 & 7;
    if (value >= 0 && (func == 0 || func == 7 || !(depth_ctl & 1))) ref = uint32_t(value);
}

VkSamplerAddressMode address_mode(uint32_t c) {
    switch (c) {
    case 0: return VK_SAMPLER_ADDRESS_MODE_REPEAT;
    case 1: return VK_SAMPLER_ADDRESS_MODE_MIRRORED_REPEAT;
    case 2: return VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
    case 3: case 5: case 7: return VK_SAMPLER_ADDRESS_MODE_MIRROR_CLAMP_TO_EDGE;
    default: return VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_BORDER;
    }
}

// ---------------------------------------------------------------------------- resources
// device memory suballocation (see Heap)
struct Alloc {
    VkDeviceMemory mem = VK_NULL_HANDLE;
    uint64_t offset = 0, size = 0;
    int block = -1;  // -1: dedicated allocation
};

struct Image {
    VkImage image = VK_NULL_HANDLE;
    Alloc mem;
    VkFormat format = VK_FORMAT_UNDEFINED;
    uint32_t w = 1, h = 1, d = 1, layers = 1, levels = 1;
    bool depth = false, stencil = false, cube = false, is3d = false;
    uint32_t swap = 0;  // render target COMP_SWAP
    uint64_t base = 0;
    VkImageView attachment = VK_NULL_HANDLE;
    VkImageAspectFlags att_aspect = 0;  // attachment view made when first rendered to (0: none)
    std::unordered_map<uint64_t, VkImageView> views;
    uint64_t last_used = 0;
    uint32_t bind_slice = 0;  // layered target: the slice the current pass renders
    // textures: the guest memory they were copied from, and its version then (write tracking)
    uint64_t src_addr = 0, src_size = 0, version = ~0ull, checked = 0;
    uint32_t torn = 0;  // reloads in a row that were rewritten while being copied
    // render targets: guest layout (for readback) and whether any draw samples it
    uint32_t tile_mode = 0, pitch = 0, bpp = 0;
    bool sampled = false;
    // small render targets: the memory's version when the GPU last rendered it (write
    // tracking); a CPU write since then makes the memory, not the image, the current contents
    uint64_t tv_version = ~0ull, tv_size = 0, tv_frame = 0;
    // textures of engine resources: the resource's id << 32 | epoch when copied, and a hash of
    // the guest memory then (a new epoch with the same contents - a move - keeps the image)
    uint64_t res_val = 0, content = 0;
    bool stale = false;  // its memory was written by a copy command: reload at the next use
    uint64_t bound_serial = 0;  // render targets: when last bound for drawing
};

struct Shader {
    VkShaderModule module = VK_NULL_HANDLE;
    VkShaderModule rect_gs = VK_NULL_HANDLE;  // vertex: rect-list expansion for this shader's outputs
    gcn::Result res;
    bool ok = false;
};

struct Pipeline {
    VkPipeline pipeline = VK_NULL_HANDLE;
    VkPipelineLayout layout = VK_NULL_HANDLE;
    VkDescriptorSetLayout sets[2] = {};
    bool push_ps = false;  // the pixel shader's set is a push descriptor set
    Shader* vs = nullptr;
    Shader* ps = nullptr;
};

struct Buffer {
    VkBuffer buf = VK_NULL_HANDLE;
    VkDeviceMemory mem = VK_NULL_HANDLE;
    uint8_t* map = nullptr;
    uint64_t size = 0;
};

struct Stats {
    uint64_t frames = 0, submits = 0, draws = 0, clears = 0, skipped = 0, pipelines = 0, textures = 0, targets = 0,
             shaders = 0, bad_shaders = 0, ring_peak = 0, evicted = 0;
    uint64_t bytes_vtx = 0, bytes_idx = 0, bytes_cb = 0, bytes_tex = 0;  // copied into the ring
    uint64_t bytes_geo = 0, geo_hits = 0, tex_reloads = 0, tex_torn = 0, geo_torn = 0, readbacks = 0, target_writes = 0, mips_filled = 0, tex_inplace = 0;                 // geometry cache uploads
    // CPU time per phase (ns): targets+textures pre-pass, then per draw: targets+pipeline,
    // geometry, descriptors, commands; frames counted for averages
    uint64_t geo_stale = 0, predicated = 0, zpass_dumps = 0, t_bind = 0, t_view = 0, t_vkimg = 0, t_heap = 0, heap_scans = 0, heap_blocks_new = 0, t_detile = 0, t_fill = 0, t_watch = 0, t_mkimg = 0, t_tgt = 0, t_tex_hit = 0, t_tex_load = 0, tex_checks = 0, tex_unwatched = 0, t_pre = 0, t_pipe = 0, t_geo = 0, t_desc = 0, t_cmd = 0, t_frames = 0, t_draws = 0, memo_hits = 0, memo_misses = 0, memo_gen = 0;
    uint64_t t_wait = 0, t_submit = 0;  // waiting for the GPU (fences), vkQueueSubmit2
    // engine resources: uses with an unchanged epoch, moves with the same contents, real changes
    uint64_t res_hits = 0, res_moves = 0, res_changed = 0, geo_res_hits = 0, geo_res_moves = 0, geo_res_changed = 0;
    uint64_t res_verify_ok = 0, res_verify_missed = 0;
    // (census) memory still write-tracked: textures by key -> bytes, geometry lookups
    std::unordered_map<uint64_t, uint64_t> unreg_tex;
    uint64_t unreg_geo = 0, unreg_geo_bytes = 0;
    uint64_t why_vb_noid = 0, why_vb_range = 0, why_ib_noid = 0, why_ib_range = 0, why_inline = 0;
    std::unordered_map<std::string, uint64_t> skip;
};

// Device-local memory for images: 256 MiB blocks per memory type, first fit with a free
// list per block (drivers limit the number of allocations; Windows drivers often to 4096).
struct Heap {
    struct Block {
        VkDeviceMemory mem = VK_NULL_HANDLE;
        uint32_t type = 0;
        uint64_t size = 0;
        std::map<uint64_t, uint64_t> free;           // offset -> size
        std::multimap<uint64_t, uint64_t> by_size;  // size -> offset (the same ranges, for best fit)
        void add(uint64_t off, uint64_t size) {
            free[off] = size;
            by_size.emplace(size, off);
        }
        void remove(uint64_t off, uint64_t size) {
            free.erase(off);
            for (auto [i, e] = by_size.equal_range(size); i != e; ++i)
                if (i->second == off) {
                    by_size.erase(i);
                    break;
                }
        }
    };
    std::vector<Block> blocks;
    uint64_t used = 0, reserved = 0;
};

// One submitted (or recording) command buffer and what must outlive it.
struct Sub {
    VkCommandPool cpool = VK_NULL_HANDLE;  // its own (lists are recorded on several threads at once)
    VkCommandBuffer cmd = VK_NULL_HANDLE;
    VkFence fence = VK_NULL_HANDLE;
    uint64_t serial = 0;
    enum State : uint8_t { Idle, Recording, Recorded, Inflight } state = Idle;
    uint64_t submit_no = 0;   // the first recording that used it (what it may reference)
    uint64_t ring_begin = 0;  // ring position (absolute) when recording started
    std::vector<Buffer> staging;
    std::vector<VkDescriptorPool> pools;            // descriptor sets of this submission's draws
    size_t pool = 0;                                // the pool being allocated from
    // small render targets the CPU reads: copied to the ring, written to guest memory when done
    struct Readback { uint64_t base; tiling::Surface sf; uint64_t off; };
    std::vector<Readback> readbacks;
    Buffer rb;             // their copies, in host-cached memory (the ring may be write-combined VRAM)
    uint64_t rb_used = 0;
    // secondary command buffers recorded by the worker threads (one pool per worker)
    struct Secondaries { VkCommandPool pool = VK_NULL_HANDLE; std::vector<VkCommandBuffer> cbs; size_t used = 0; };
    std::vector<Secondaries> sec;
    // occlusion counting (ZPASS_DONE dumps): one query per stretch of draws between two dumps
    // (and render pass boundaries); a dump's counter is the sum of the stretches before it
    VkQueryPool qpool = VK_NULL_HANDLE;
    uint32_t q_used = 0;
    struct ZRec { uint64_t dest; uint32_t boundary; };
    std::vector<ZRec> zrecs;
    std::vector<std::array<uint64_t, 4>> copies;  // (D1_NG_VERIFY_LATE) kind, address, size, hash when recorded
};

// Copies of guest vertex / index buffers kept on the GPU while the game does not write them.
struct GeoEntry {
    int block = -1;
    uint64_t off = 0, size = 0;
    uint64_t version = ~0ull, checked = 0, checked_frame = 0, last_used = 0, uploaded = 0, volatile_until = 0;
    uint32_t misses = 0;
    uint32_t vfirst = 0, vlast = 0;  // index buffers: the vertex range they reference
    bool valid = false;
    uint64_t hash = 0;  // of the guest bytes when copied (engine resources; D1_NG_GEO_VERIFY)
    uint64_t res = 0;   // engine resource: id << 32 | epoch when copied
};
struct GeoBlock {
    Buffer buf;
    std::map<uint64_t, uint64_t> free;  // offset -> size
};

// Window presentation.
struct Swapchain {
    VkSurfaceKHR surface = VK_NULL_HANDLE;
    VkSwapchainKHR chain = VK_NULL_HANDLE;
    VkSurfaceFormatKHR format{};
    VkPresentModeKHR mode = VK_PRESENT_MODE_FIFO_KHR;
    VkExtent2D extent{};
    std::vector<VkImage> images;
    std::vector<VkSemaphore> acquired;  // per frame slot
    std::vector<VkSemaphore> ready;     // per swapchain image
    uint32_t slot = 0;
    bool failed = false;     // no surface / no swapchain support: stop trying
    bool stale = false;      // out of date or resized: rebuild before the next acquire
    uint32_t want_w = 0, want_h = 0;
    std::unique_ptr<Image> raw;  // UNORM copy of an sRGB video-out image (blit without decoding)
    uint64_t presented = 0;
};

struct Renderer {
    Options opt;
    Context ctx;
    std::mutex m;
    VkCommandPool pool = VK_NULL_HANDLE;
    Buffer ring;
    uint64_t ring_head = 0;                 // absolute position of the next ring allocation
    std::vector<Sub> subs;
    std::deque<uint32_t> inflight;          // submitted, in order
    std::vector<uint32_t> idle_subs;
    uint64_t serial_next = 1, serial_done = 0;
    std::deque<uint64_t> frame_ends;        // last submission serial of each recent frame
    Heap heap;
    Swapchain sc;
    VkPipelineCache pcache = VK_NULL_HANDLE;
    std::vector<GeoBlock> geo_blocks;  // (reserved up front: never reallocated, read without a lock)
    // the entries in 64 shards by address, each with its own lock (the recording threads look
    // up every draw's buffers); blocks, their free lists and geo_bytes under geo_block_m
    struct GeoShard {
        std::mutex m;
        std::unordered_map<uint64_t, GeoEntry> map;
    };
    GeoShard geo_shards[64];
    std::mutex geo_block_m;
    uint64_t geo_bytes = 0;
    struct GeoHit {
        VkBuffer buf = VK_NULL_HANDLE;
        uint64_t off = 0, size = 0;
        uint32_t vfirst = 0, vlast = 0;
    };
    bool geo_alloc(uint64_t size, int& block, uint64_t& off);
    void geo_free_now(int block, uint64_t off, uint64_t size);
    void geo_free_later(int block, uint64_t off, uint64_t size);
    // res / rbase: an engine resource (id << 32 | epoch) and its memory's start: kept by
    // identity and epoch instead of write tracking
    bool geo_get(uint64_t addr, uint64_t size, int index_size, uint32_t index_count, GeoHit& hit, uint64_t res = 0, uint64_t rbase = 0);
    GeoEntry* geo_lookup(uint64_t addr, uint64_t size, int index_size, uint32_t index_count, uint64_t res, uint64_t rbase);
    static thread_local GeoHit geo_hit_out;  // (geo_lookup's result, copied while its shard is locked)
    GeoEntry* geo_lookup_res(uint64_t addr, uint64_t size, int index_size, uint32_t index_count, uint64_t res, uint64_t rbase);
    void evict_geo();
    uint64_t pcache_saved_pipelines = 0;
    void save_pipeline_cache();
    std::unordered_map<uint64_t, std::unique_ptr<Image>> targets;   // (base, format, size)
    std::unordered_map<uint64_t, Image*> target_by_base;            // newest target at an address
    std::vector<std::unique_ptr<Image>> retired;                    // replaced targets (still referenced)
    std::unordered_map<uint64_t, std::unique_ptr<Image>> textures;  // T# hash
    std::unordered_map<uint64_t, VkSampler> samplers;
    std::unordered_map<uint64_t, std::unique_ptr<Shader>> shaders;
    std::unordered_map<uint64_t, std::unique_ptr<Pipeline>> pipelines;
    std::unique_ptr<Image> dummy[4];  // per TexDim
    VkSampler dummy_sampler = VK_NULL_HANDLE;
    Stats st;

    // per-submission recording state

    bool init(const Options& o);
    Buffer make_buffer(uint64_t size, VkBufferUsageFlags usage, bool host, bool prefer_device = false);
    void free_buffer(Buffer& b);
    VkDeviceMemory alloc(VkMemoryRequirements req, VkMemoryPropertyFlags want);
    Alloc heap_alloc(VkMemoryRequirements req);
    void heap_free(Alloc& a);
    std::unique_ptr<Image> make_image(VkFormat f, uint32_t w, uint32_t h, uint32_t d, uint32_t layers, uint32_t levels,
                                      bool cube, bool is3d, bool depth, bool stencil);
    void destroy_image(Image* img);
    VkImageView view(Image* img, VkImageViewType type, VkComponentMapping comp, uint32_t base_level, bool depth_aspect, bool stencil_aspect = false);
    uint64_t ring_alloc(uint64_t size, uint64_t align = 256);
    Buffer make_readback_buffer(uint64_t size);
    // bumped whenever a render target appears or the image bound at an address changes: what
    // T#s on render targets resolve to (pipeline memo below)
    std::atomic<uint64_t> targets_gen{1};
    uint64_t gen_why[8] = {};  // (diagnostics: which bump)
    std::vector<uint64_t> ambiguous_bases;  // sorted
    // the same, append-only, read without a lock by the recording threads' pipeline caches
    static constexpr uint32_t kAmbMax = 1024;
    uint64_t amb_arr[kAmbMax] = {};
    std::atomic<uint32_t> amb_n{0};
    void publish_ambiguous(uint64_t base) {
        const uint32_t n = amb_n.load(std::memory_order_relaxed);
        if (n < kAmbMax) amb_arr[n] = base;
        amb_n.store(n + 1, std::memory_order_release);  // (past kAmbMax: every T# counts as ambiguous)
    }
    // pipeline() key without the parts that need the shared maps; ambiguous = a T# names an
    // address whose sampled image changes kind (then only pipeline() under the lock decides)
    uint64_t pipe_key(const Draw& dr, Image* const* colors, Image* depth, bool& ambiguous) const;
    // what a pipeline sees of a render target sampled as a texture: dimensionality and kind
    static uint32_t target_attrs(const Image* i) {
        if (!i) return 0;
        return 1u | uint32_t(i->is3d) << 1 | uint32_t(i->depth) << 2 |
               (i->depth ? 0u : is_int_format(i->format) ? (is_sint_format(i->format) ? 16u : 8u) : 0u);
    }
    template <class M> void set_base(M& m, uint64_t base, Image* img) {
        auto [it, added] = m.try_emplace(base, img);
        if (added || it->second != img) {
            if (added) (++targets_gen, ++gen_why[0]);
            else if (target_attrs(it->second) != target_attrs(img) &&
                     !std::binary_search(ambiguous_bases.begin(), ambiguous_bases.end(), base)) {  // (see below)
                ambiguous_bases.insert(std::upper_bound(ambiguous_bases.begin(), ambiguous_bases.end(), base), base);
                publish_ambiguous(base);
                (++targets_gen, ++gen_why[0]);
            }
            it->second = img, ++views_gen;
        } else if (auto ib = images_by_base.find(base); ib != images_by_base.end() && ib->second.size() > 1) {
            // (target_for picks the most recently bound of same-size images at one address)
            bool same_size = false, other_attrs = false;
            for (Image* c : ib->second)
                if (c != img && c->w == img->w && c->h == img->h) same_size = true, other_attrs |= target_attrs(c) != target_attrs(img);
            if (same_size) ++views_gen;
            // an address whose sampled image alternates between kinds: pipeline() keys draws
            // that sample it by what it resolves to (instead of invalidating every pipeline)
            if (other_attrs && !std::binary_search(ambiguous_bases.begin(), ambiguous_bases.end(), base)) {
                ambiguous_bases.insert(std::upper_bound(ambiguous_bases.begin(), ambiguous_bases.end(), base), base);
                publish_ambiguous(base);
                (++targets_gen, ++gen_why[1]);
            }
        }
    }
    // bumped whenever what a T# resolves to may change (textures uploaded or dropped, render
    // targets bound): the recording threads' view caches are valid for one value
    std::atomic<uint64_t> views_gen{1};
    // what draw() last set in the current command buffer (invalid: set everything)
    struct DrawState {
        bool valid = false;
        VkPipeline pipe = VK_NULL_HANDLE;
        uint32_t vmask = 0;
        VkBuffer vb[16]{};
        VkDeviceSize voff[16]{}, vsize[16]{};
        VkViewport vp{};
        VkRect2D sc{};
        uint32_t sref = 0, cmask = 0, wmask = 0;
        float bias[2]{};
        VkBuffer ib = VK_NULL_HANDLE;
        VkDeviceSize ioff = 0;
        VkIndexType itype = VK_INDEX_TYPE_UINT16;
    };
    // What one recording (a submission's command buffer) is in the middle of: the main
    // recorder serves the submitting thread; others record lists on the engine's threads.
    struct Recorder {
        VkCommandBuffer cmd = VK_NULL_HANDLE;  // the command buffer being recorded
        uint32_t cur = UINT32_MAX;              // its submission slot (subs)
        uint64_t submit_no = 0;                 // its submission number
        bool in_pass = false;
        uint64_t pass_key = 0;
        Image* pass_color[8] = {};
        Image* pass_depth = nullptr;
        uint32_t pass_w = 0, pass_h = 0;
        bool pass_secondary = false;  // the current pass's contents are secondary command buffers
        DrawState dstate;
        bool q_on = false;      // this submission dumps occlusion counters
        int32_t q_active = -1;  // the query counting now (in the current pass)
        int32_t pred_cur = -1;  // the slot predicating draws now (-1: none)
        bool pred_invert = false;
        // recording a list on an engine thread: shared state is taken under the renderer's
        // lock (m) instead of the finer locks the worker threads use while it is held
        bool lr = false;
        struct Late { uint64_t off = 0; uint32_t size = 0; };
        Late late[kStages][16];
        std::vector<LateCb> late_list;
        // D1_NG_VERIFY_LATE: what was copied while recording, compared again at submission
        struct Copy { uint8_t kind; uint64_t addr, size, hash; };
        std::vector<Copy> copies;
        // attachments the current pass's draws sample: read from a copy made before the pass
        std::vector<std::pair<Image*, Image*>> snaps;  // (attachment, snapshot)
        // snapshots that still equal their attachment at this point of this command buffer (no
        // command recorded here since the copy writes it): a later pass samples them uncopied.
        // Per command buffer: lists are recorded in any order but run in submission order.
        struct Fresh { Image* img; Image* sn; uint8_t valid; };  // valid: 1 color / depth, 2 stencil
        std::vector<Fresh> fresh;
        // this render pass instance: attachments sampled in place (read-only so far: valid in
        // Vulkan as long as no command of the instance writes them) and what it has written
        std::vector<std::pair<Image*, uint8_t>> pass_live, pass_written;
        uint64_t snap_key = 0;                          // the attachments they were made for
    };
    // per attachment image, its snapshot image (feedback: a draw sampling what it renders into)
    std::unordered_map<Image*, std::unique_ptr<Image>> snap_img;
    uint64_t snap_copies = 0;
    static uint64_t pass_key_of(Image* const* colors, Image* depth) {
        uint64_t key = uint64_t(depth);
        for (int i = 0; i < 8; ++i) key = mix(mix(key, uint64_t(colors[i])), colors[i] ? colors[i]->bind_slice : 0);
        return key;
    }
    // (new_pass: the run gets a render pass instance of its own)
    void feedback_snapshots(const Draw* const* run, size_t n, Image* const* colors, Image* depth, bool new_pass = false);
    // what these draws may write: bit i color target i, bit 8 depth, bit 9 stencil
    static uint32_t run_writes(const Draw* const* run, size_t n);
    void wrote_target(Image* img, uint8_t aspects = 3) {
        auto& f = rc().fresh;
        for (size_t i = 0; i < f.size();)
            if (f[i].img == img && !(f[i].valid &= uint8_t(~aspects))) f[i] = f.back(), f.pop_back();
            else ++i;
    }
    uint64_t snap_reused = 0;
    VkImageView target_view(Image* img, const Image* like, const uint32_t* t);
    static bool verify_late() { static const bool v = std::getenv("D1_NG_VERIFY_LATE") != nullptr; return v; }
    void note_copy(uint8_t kind, uint64_t addr, uint64_t size) {
        if (verify_late() && rc().lr && size && size <= (1u << 20)) rc().copies.push_back({kind, addr, size, hash_bytes(reinterpret_cast<const void*>(addr), size)});
    }
    uint64_t late_checked[3] = {}, late_changed[3] = {};
    Recorder up_rec;  // uploads and target set-up for lists recorded on engine threads
    // the loader thread: engine resources prepared when the engine binds or moves them
    struct LoadJob { bool tex; uint32_t t[8]; uint64_t base, size, res, obj; };
    std::mutex load_m;
    std::condition_variable load_cv;
    std::deque<LoadJob> load_q;
    std::thread loader;
    bool load_on = false;
    std::atomic<uint64_t> ld_tex{0}, ld_moves{0}, ld_buf{0}, ld_stale{0}, ld_skipped{0}, ld_dropped{0}, ld_ns{0};
    void start_loader();
    void load_texture(const LoadJob& j);
    void load_buffer(const LoadJob& j);
    void prefetch(const LoadJob& j) {
        if (!load_on) return;
        {
            std::lock_guard lk(load_m);
            if (load_q.size() >= 20000) load_q.pop_front(), ++ld_dropped;  // (the draws upload what is dropped)
            load_q.push_back(j);
        }
        load_cv.notify_one();
    }
    std::atomic<uint32_t> late_hint[kStages][16] = {};  // largest inherited constant buffer seen per slot
    bool list_rec = false;
    bool dynamic_copy = false;  // engine resource events on: memory that is no resource is copied per draw, never write-tracked
    // Dynamic memory without write tracking: the CPU writes the engine announces (dynamic
    // texture unlocks, copy-queue writes) bump a generation per tracked range (dynamic textures,
    // small render targets the CPU may rewrite); a copy is current while its generation is.
    std::mutex dyn_m;
    std::vector<std::pair<uint64_t, uint64_t>> dyn_q;              // (address, size) written, not applied yet
    std::map<uint64_t, std::pair<uint64_t, uint64_t>> dyn_mem;     // base -> (size, generation)   [under m]
    std::unordered_set<uint64_t> dyn_targets;                       // (bases of render targets among them)
    uint64_t dyn_target_bumps = 0;
    uint64_t dyn_events = 0, dyn_bumps = 0, dyn_verify_hits = 0, dyn_verify_missed = 0;
    // The list's copy commands (DMA_DATA), done before its textures are prepared (the engine
    // copies first, e.g. streamed mips or new glyphs, then draws with the result); the textures
    // whose memory they write are marked stale.
    uint64_t dma_stale = 0;
    void run_copies(const std::vector<Draw*>& items) {
        for (Draw* d : items) {
            if (d->kind != Draw::Dma || d->caller < 0x10000 || guest_region_extent(d->caller) < d->count) continue;
            if (d->prim == 2) {
                auto* w = reinterpret_cast<uint32_t*>(d->caller);
                for (uint32_t k = 0; k < d->count / 4; ++k) w[k] = d->instances;
            } else if (d->index_addr >= 0x10000 && guest_region_extent(d->index_addr) >= d->count) {
                std::memmove(reinterpret_cast<void*>(d->caller), reinterpret_cast<const void*>(d->index_addr), d->count);
            } else continue;
            if (dynamic_copy) {
                std::lock_guard dl(dyn_m);
                dyn_q.push_back({d->caller, d->count});
            }
            const uint64_t a = d->caller, e = d->caller + d->count;
            for (auto& [k, img] : textures)
                if (img && img->src_size && a < img->src_addr + img->src_size && e > img->src_addr && !img->stale) img->stale = true, ++dma_stale;
            dma_texture_check(d->caller, d->count);
        }
    }
    // D1_NG_LOG_DMA_TEX: (diagnostics) copy-queue writes into memory a texture copy was made from
    void dma_texture_check(uint64_t dst, uint64_t n) {
        static const bool on = std::getenv("D1_NG_LOG_DMA_TEX") != nullptr;
        if (!on) return;
        static int told = 0;
        for (auto& [k, img] : textures)
            if (img && img->src_size && dst < img->src_addr + img->src_size && dst + n > img->src_addr) {
                ++dma_tex_hits;
                if (told++ < 40)
                    log("native renderer: copy-queue write %#llx +%llu into texture %#llx %ux%u fmt %d (%s)", (unsigned long long)dst,
                        (unsigned long long)n, (unsigned long long)img->src_addr, img->w, img->h, int(img->format),
                        img->res_val ? "engine resource" : "dynamic");
            }
    }
    uint64_t dma_tex_hits = 0, feedback_draws = 0;
    void apply_cpu_writes() {
        std::vector<std::pair<uint64_t, uint64_t>> q;
        {
            std::lock_guard lk(dyn_m);
            q.swap(dyn_q);
        }
        for (auto [a, n] : q) {
            ++dyn_events;
            const uint64_t end = a + std::max<uint64_t>(n, 1);
            auto it = dyn_mem.upper_bound(a);
            if (it != dyn_mem.begin()) --it;
            for (; it != dyn_mem.end() && it->first < end; ++it)
                if (it->first + std::max<uint64_t>(it->second.first, 1) > a) {
                    ++it->second.second, ++dyn_bumps;
                    if (dyn_targets.count(it->first)) {
                        ++dyn_target_bumps;
                        static const bool log_t = std::getenv("D1_NG_LOG_DYN") != nullptr;
                        static int told = 0;
                        if (log_t && told++ < 60)
                            log("native renderer: CPU write %#llx +%llu marks render target %#llx (+%llu) rewritten", (unsigned long long)a,
                                (unsigned long long)n, (unsigned long long)it->first, (unsigned long long)it->second.first);
                    }
                }
        }
    }
    // write tracking, or (dynamic_copy) the generation of the range
    uint64_t mem_watch(uint64_t base, uint64_t size) {
        if (!dynamic_copy) return opt.watch ? opt.watch(base, size) : ~0ull;
        auto& e = dyn_mem[base];
        e.first = std::max(e.first, size);
        return e.second + 1;
    }
    uint64_t mem_version(uint64_t base, uint64_t size) {
        if (!dynamic_copy) return opt.version ? opt.version(base, size) : ~0ull;
        auto it = dyn_mem.find(base);
        return it == dyn_mem.end() ? ~0ull : it->second.second + 1;
    }
    std::atomic<uint64_t> lr_lists{0}, lr_ns{0}, lr_wait_ns{0}, lr_sub_ns{0};  // (statistics)
    bool record_list(const std::vector<Draw*>& items, uint32_t& handle, std::vector<LateCb>& late);
    void pre_pass(const std::vector<Draw*>& draws);
    void submit_recorded(const std::vector<uint32_t>& handles);
    void discard_recorded(uint32_t handle);
    Recorder main_rec;
    static thread_local Recorder* tr;  // this thread's recorder (null: the main one)
    Recorder& rc() { return tr ? *tr : main_rec; }
    std::atomic<uint64_t> submit_seq{0};
    // pipeline() results by a hash of everything they depend on, valid for one targets_gen
    struct PipeMemo { uint64_t key = 0, gen = 0; Pipeline* p = nullptr; };
    std::vector<PipeMemo> pipe_memo = std::vector<PipeMemo>(1u << 14);
    uint64_t ring_copy(const void* src, uint64_t size);
    // submissions
    void begin_record();
    void submit(const VkSemaphoreSubmitInfo* wait = nullptr, const VkSemaphoreSubmitInfo* signal = nullptr);
    void submit_sub(uint32_t i, const VkSemaphoreSubmitInfo* wait = nullptr, const VkSemaphoreSubmitInfo* signal = nullptr);
    uint64_t min_live_submit() const;
    uint64_t oldest_ring() const;
    uint64_t ring_oldest = 0;  // a lower bound of oldest_ring()
    VkSemaphore timeline = VK_NULL_HANDLE;  // value = serial of the last completed submission
    // images and geometry regions dropped while recordings that may use them are in progress
    struct Dead { uint64_t tag; std::unique_ptr<Image> img; std::array<uint64_t, 3> geo; };
    std::mutex grave_m;
    std::vector<Dead> grave;
    void bury(std::unique_ptr<Image> img);
    void reap();
    void retire_one();
    void retire_completed();
    void wait_serial(uint64_t serial);
    void wait_idle() { wait_serial(serial_next - 1); }
    void submit_and_wait() {
        submit();
        wait_idle();
    }
    VkDescriptorSet alloc_set(VkDescriptorSetLayout layout);
    // push descriptors (Vulkan 1.4 core): the pixel shader's bindings are written straight into
    // the command buffer instead of allocating and updating a descriptor set per draw
    PFN_vkCmdPushDescriptorSetKHR push_fn = nullptr;
    uint32_t max_push = 0;
    void barrier();
    // bind = false (the pre-pass): create the image, but leave which image an address names
    // to the draws themselves, in order (a draw that reads last frame's contents of an
    // address must not see an image a later draw in this submission renders to)
    Image* color_target(const uint32_t* c, bool bind = true);
    VkImageView attachment_view(Image* img);
    Image* depth_target(const uint32_t* d, bool bind = true);
    std::unordered_set<uint64_t> target_bases;  // every address ever rendered to
    std::unordered_set<uint64_t> sampled_bases;  // render target addresses some draw sampled
    std::unordered_set<uint64_t> tsharp_bases;   // every address a draw's T# named
    bool reload_all = false;
    // stencil clears that keep some bits (the engine clears stencil with a draw that honours the
    // write mask; vkCmdClearAttachments cannot)
    VkShaderModule fullscreen_vs = VK_NULL_HANDLE;
    VkPipelineLayout empty_layout = VK_NULL_HANDLE;
    std::unordered_map<uint64_t, VkPipeline> stencil_clear_pipes;
    void masked_stencil_clear(Image* depth, uint32_t value, uint32_t write_mask, const VkRect2D& rect);
    // occlusion queries and predication (GCN ZPASS_DONE / SET_PREDICATION)
    static constexpr uint32_t kQueries = 2048, kPredSlots = 4096;
    Buffer pred_buf;             // 32-bit predicates for conditional rendering, one slot per query address
    std::unordered_map<uint64_t, uint32_t> pred_slots;
    uint64_t zcount_base = 0;    // occlusion counter value before the oldest unwritten submission
    void q_begin();
    void q_end();
    uint32_t pred_slot(uint64_t base);
    void zpass(uint64_t dest);
    void predicate(uint64_t base, bool draw_if_visible);
    void store_query_predicates();
    void write_zpass_results(Sub& sb);
    struct TraceRec { uint64_t ps, vs, caller, off; uint32_t bytes, w, blend, count; };
    std::vector<TraceRec> traces;  // D1_NG_TRACE
    std::unordered_map<uint64_t, uint32_t> base_targets;  // render target images made per address
    std::unordered_map<uint64_t, Image*> stencil_by_base;  // separate stencil planes of depth targets (DB_STENCIL_*_BASE)
    std::unordered_map<uint64_t, std::vector<Image*>> images_by_base;  // every render target image per address
    uint64_t bind_serial = 0;
    Image* target_for(const fmt::TSharp& ts);
    VkImageView texture_view(const uint32_t* t, gcn::TexDim dim, uint64_t res = 0);
    Image* upload_texture(const uint32_t* t, uint64_t res = 0);
    // the textures map key: the T#, or for an engine resource its identity and the T# without
    // its base address (a resource the engine moves keeps its key)
    static uint64_t tex_key(const uint32_t* t, uint64_t res) {
        if (!res) return hash_bytes(t, 32);
        uint32_t c[8];
        std::memcpy(c, t, 32);
        c[0] = 0, c[1] &= ~0xFFu;
        return hash_bytes(c, 32, (res >> 32) * 0x9E3779B97F4A7C15ull) | 1;
    }
    void evict_textures();
    VkSampler sampler(const uint32_t* s);
    Shader* shader(const Draw& dr, bool vs, const gcn::TexDim* dims, const uint8_t* kinds, uint32_t uint_in = 0,
                   uint32_t sint_in = 0, uint32_t scaled_in = 0);
    // what this GPU supports per format (cached): vertex buffers, sampling, rendering
    std::mutex fmt_m;
    std::unordered_map<uint32_t, VkFormatProperties> fmt_props;
    VkFormatProperties format_props(VkFormat f) {
        std::lock_guard lk(fmt_m);
        auto it = fmt_props.find(uint32_t(f));
        if (it != fmt_props.end()) return it->second;
        VkFormatProperties p{};
        vkGetPhysicalDeviceFormatProperties(ctx.gpu, f, &p);
        fmt_props[uint32_t(f)] = p;
        return p;
    }
    bool vertex_ok(VkFormat f) {
        // D1_NG_NO_SCALED=1: (testing) as on a GPU without SCALED vertex formats
        static const bool no_scaled = std::getenv("D1_NG_NO_SCALED") != nullptr;
        if (no_scaled) {
            switch (f) {
            case VK_FORMAT_R8_USCALED: case VK_FORMAT_R8_SSCALED: case VK_FORMAT_R8G8_USCALED: case VK_FORMAT_R8G8_SSCALED:
            case VK_FORMAT_R16_USCALED: case VK_FORMAT_R16_SSCALED: case VK_FORMAT_R16G16_USCALED: case VK_FORMAT_R16G16_SSCALED:
            case VK_FORMAT_R8G8B8A8_USCALED: case VK_FORMAT_R8G8B8A8_SSCALED: case VK_FORMAT_R16G16B16A16_USCALED:
            case VK_FORMAT_R16G16B16A16_SSCALED: case VK_FORMAT_A2B10G10R10_USCALED_PACK32: case VK_FORMAT_A2B10G10R10_SSCALED_PACK32:
                return false;
            default: break;
            }
        }
        return (format_props(f).bufferFeatures & VK_FORMAT_FEATURE_VERTEX_BUFFER_BIT) != 0;
    }
    // a vertex attribute's format on this GPU: SCALED formats it cannot read are fetched as
    // integers and converted in the shader (scaled_u / scaled_s)
    VkFormat vertex_format_here(uint32_t dfmt, uint32_t nfmt, bool& scaled_u, bool& scaled_s) {
        scaled_u = scaled_s = false;
        VkFormat f = vertex_format(dfmt, nfmt);
        if (f == VK_FORMAT_UNDEFINED) return VK_FORMAT_R32G32B32A32_SFLOAT;
        if (vertex_ok(f)) return f;
        if (nfmt == 2 || nfmt == 3) {
            const VkFormat i = vertex_format(dfmt, nfmt == 2 ? 4 : 5);
            if (i != VK_FORMAT_UNDEFINED && vertex_ok(i)) {
                (nfmt == 2 ? scaled_u : scaled_s) = true;
                static std::atomic<int> told{0};
                if (told++ < 8) log("native renderer: vertex format %d is not supported by this GPU: read as %d and converted in the shader", int(f), int(i));
                return i;
            }
        }
        static std::mutex lm;
        static std::unordered_set<int> told;
        std::lock_guard lk(lm);
        if (told.insert(int(f)).second) log("native renderer: vertex format %d (data format %u, number format %u) is NOT supported by this GPU", int(f), dfmt, nfmt);
        return f;
    }
    Pipeline* pipeline(const Draw& dr, Image* const* colors, Image* depth);
    Pipeline* pipeline_resolve(const Draw& dr, Image* const* colors, Image* depth);
    void begin_pass(Image* const* colors, Image* depth, bool secondaries = false);
    // parallel recording of runs of plain draws (secondary command buffers, worker threads)
    struct Workers {
        std::vector<std::thread> threads;
        std::mutex m;
        std::condition_variable cv, done_cv;
        std::vector<std::function<void()>> jobs;
        size_t pending = 0;
        bool quit = false;
    } wk;
    uint32_t rec_threads = 0;   // worker threads (0: everything on the submitting thread)
    uint32_t rec_min_run = 64;  // fewest draws in a pass worth splitting
    uint64_t par_runs = 0, par_draws = 0;
    void start_workers();
    void run_parallel(Draw* const* run, size_t n);
    VkCommandBuffer secondary(uint32_t worker);
    void end_pass();
    void queue_readbacks();
    bool target_current(uint64_t base);
    uint32_t first_missing_mip(const fmt::TSharp& ts, const fmt::FormatInfo& fi, const tiling::Surface& sf, bool is3d);
    void fill_missing_mips(uint32_t first, uint8_t* staging, const std::vector<uint64_t>& off, const std::vector<uint64_t>& sizes,
                           const fmt::TSharp& ts, const fmt::FormatInfo& fi, const tiling::Surface& sf, bool is3d);
    void skip(const char* why) {
        ++st.skipped;
        ++st.skip[why];
    }
    // a recording context for draw(): the command buffer, its state filter, and what it adds to
    // the statistics (merged after the run)
    struct Rec {
        VkCommandBuffer cmd = VK_NULL_HANDLE;
        DrawState* ds = nullptr;
        bool parallel = false;
        uint64_t t_pipe = 0, t_geo = 0, t_desc = 0, t_cmd = 0, draws = 0, bytes_vtx = 0, bytes_idx = 0, bytes_cb = 0, predicated = 0, memo_tl = 0;
        uint64_t chunk_pos = 0, chunk_end = 0;  // (parallel) this worker's slice of the ring
    };
    std::mutex pipe_m, geo_m, tex_m, set_m, ring_m, skip_m;
    uint64_t rec_ring(Rec& r, uint64_t size, uint64_t align = 256);
    uint64_t rec_copy(Rec& r, const void* src, uint64_t size) {
        const uint64_t p = rec_ring(r, std::max<uint64_t>(size, 16));
        if (p != UINT64_MAX) std::memcpy(ring.map + p, src, size);
        return p;
    }
    void merge(const Rec& r) {
        st.t_pipe += r.t_pipe, st.t_geo += r.t_geo, st.t_desc += r.t_desc, st.t_cmd += r.t_cmd, st.draws += r.draws;
        st.bytes_vtx += r.bytes_vtx, st.bytes_idx += r.bytes_idx, st.bytes_cb += r.bytes_cb, st.predicated += r.predicated;
        st.memo_hits += r.memo_tl;
    }
    void draw(const Draw& dr, Rec& r, Image* const* run_colors, Image* run_depth);
    void draw(const Draw& dr) {
        Rec r;
        r.cmd = rc().cmd, r.ds = &rc().dstate;
        draw(dr, r, nullptr, nullptr);
        merge(r);
    }
    void clear(const Draw& dr);
    void execute(const std::vector<Draw*>& draws);
    // presentation
    bool make_swapchain(uint32_t w, uint32_t h);
    void destroy_swapchain(bool keep_surface);
    void present(uint64_t addr);
    void end_frame();
    void dump(uint64_t addr, uint32_t w, uint32_t h, uint64_t frame);
    bool save_image(Image* img, const char* path);
    uint64_t frame_first_submit = 0;
    struct PassLog { uint64_t c[5], d; uint32_t draws, clears; uint64_t first_vs, first_ps, caller; std::string tex; };
    std::vector<PassLog> passlog;
    std::map<uint64_t, std::pair<uint64_t, uint64_t>> frame_draws;  // D1_NG_DRAWSTATS
    uint64_t passlog_frame = UINT64_MAX;  // D1_NG_PASSLOG=<executed frame>: list that frame's passes
    uint32_t passlog_count = 1;           // D1_NG_PASSLOG_N: that many consecutive frames
    bool debug = false;
    uint64_t debug_from = 0;  // D1_NG_DEBUG=<executed frame>: log draws and clears from that frame
    int debug_lines = 0;
};

Renderer* g = nullptr;

bool Renderer::init(const Options& o) {
    opt = o;
    if (const char* v = std::getenv("D1_NG_DEBUG")) debug = true, debug_from = std::strtoull(v, nullptr, 10);
    if (const char* v = std::getenv("D1_NG_PASSLOG_N")) passlog_count = uint32_t(std::max(1, std::atoi(v)));
    if (const char* v = std::getenv("D1_NG_PASSLOG"))
        passlog_frame = std::strcmp(v, "world") == 0 ? UINT64_MAX - 1 : std::strtoull(v, nullptr, 10);
    char err[512];
    int gpu = -1;
    if (const char* v = std::getenv("D1_GPU")) gpu = std::atoi(v);
    // window surface extensions when there is a window to present to
    WindowHandles wh;
    const char* inst_exts[2];
    uint32_t n_inst = 0;
    if (opt.window_handles && opt.window_handles(wh))
        n_inst = surface_instance_extensions(wh.type == WindowHandles::kWin32 ? WindowSystem::Win32 : WindowSystem::Xlib,
                                             inst_exts);
    else sc.failed = true;
    if (!sc.failed && !n_inst) {
        log("native renderer: the Vulkan loader has no window surface support; not presenting");
        sc.failed = true;
    }
    if (!create_context(ctx, gpu, inst_exts, n_inst, err, sizeof err)) {
        log("native renderer: %s", err);
        return false;
    }
    VkCommandPoolCreateInfo pci{VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO};
    pci.flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;
    pci.queueFamilyIndex = ctx.queue_family;
    vkCreateCommandPool(ctx.device, &pci, nullptr, &pool);
    // command buffers: enough for a few frames of several submissions each
    subs.resize(256);  // ~30 submissions a frame, a few frames in flight
    for (uint32_t i = 0; i < subs.size(); ++i) {
        VkCommandPoolCreateInfo pci{VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO};
        pci.flags = VK_COMMAND_POOL_CREATE_TRANSIENT_BIT;
        pci.queueFamilyIndex = ctx.queue_family;
        vkCreateCommandPool(ctx.device, &pci, nullptr, &subs[i].cpool);
        VkCommandBufferAllocateInfo cai{VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};
        cai.commandPool = subs[i].cpool;
        cai.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
        cai.commandBufferCount = 1;
        vkAllocateCommandBuffers(ctx.device, &cai, &subs[i].cmd);
        VkFenceCreateInfo fci{VK_STRUCTURE_TYPE_FENCE_CREATE_INFO};
        vkCreateFence(ctx.device, &fci, nullptr, &subs[i].fence);
        idle_subs.push_back(uint32_t(subs.size() - 1 - i));
    }
    {
        VkSemaphoreTypeCreateInfo tci{VK_STRUCTURE_TYPE_SEMAPHORE_TYPE_CREATE_INFO};
        tci.semaphoreType = VK_SEMAPHORE_TYPE_TIMELINE;
        VkSemaphoreCreateInfo sci{VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO, &tci};
        if (vkCreateSemaphore(ctx.device, &sci, nullptr, &timeline) != VK_SUCCESS) timeline = VK_NULL_HANDLE;
    }
    uint64_t ring_mb = 256;
    if (const char* v = std::getenv("D1_NG_RING_MB")) ring_mb = std::max<uint64_t>(64, std::strtoull(v, nullptr, 10));
    ring = make_buffer(ring_mb << 20, VK_BUFFER_USAGE_VERTEX_BUFFER_BIT | VK_BUFFER_USAGE_INDEX_BUFFER_BIT |
                                          VK_BUFFER_USAGE_STORAGE_BUFFER_BIT | VK_BUFFER_USAGE_TRANSFER_SRC_BIT |
                                          VK_BUFFER_USAGE_TRANSFER_DST_BIT, true, std::getenv("D1_NG_RING_SYSMEM") == nullptr);
    if (!ring.map) {
        log("native renderer: no host-visible memory for the %llu MiB upload ring", (unsigned long long)ring_mb);
        return false;
    }
    // placeholder textures for unbound slots (black, alpha 0)
    begin_record();
    for (int k = 0; k < 4; ++k) {
        const auto dim = gcn::TexDim(k);
        dummy[k] = make_image(VK_FORMAT_R8G8B8A8_UNORM, 1, 1, 1, dim == gcn::TexDim::Cube ? 6 : 1, 1,
                              dim == gcn::TexDim::Cube, dim == gcn::TexDim::Tex3D, false, false);
        VkClearColorValue zero{};
        VkImageSubresourceRange r{VK_IMAGE_ASPECT_COLOR_BIT, 0, 1, 0, VK_REMAINING_ARRAY_LAYERS};
        vkCmdClearColorImage(rc().cmd, dummy[k]->image, VK_IMAGE_LAYOUT_GENERAL, &zero, 1, &r);
    }
    submit_and_wait();
    VkSamplerCreateInfo sci{VK_STRUCTURE_TYPE_SAMPLER_CREATE_INFO};
    vkCreateSampler(ctx.device, &sci, nullptr, &dummy_sampler);
    // pipeline cache from the last run (the driver checks it matches this GPU and driver)
    {
        std::vector<char> data;
        if (opt.pipeline_cache)
            if (FILE* f = std::fopen(opt.pipeline_cache, "rb")) {
                std::fseek(f, 0, SEEK_END);
                const long n = std::ftell(f);
                std::fseek(f, 0, SEEK_SET);
                if (n > 0) {
                    data.resize(size_t(n));
                    if (std::fread(data.data(), 1, data.size(), f) != data.size()) data.clear();
                }
                std::fclose(f);
            }
        VkPipelineCacheCreateInfo cci{VK_STRUCTURE_TYPE_PIPELINE_CACHE_CREATE_INFO};
        cci.initialDataSize = data.size();
        cci.pInitialData = data.empty() ? nullptr : data.data();
        if (vkCreatePipelineCache(ctx.device, &cci, nullptr, &pcache) != VK_SUCCESS) {
            cci.initialDataSize = 0, cci.pInitialData = nullptr;
            vkCreatePipelineCache(ctx.device, &cci, nullptr, &pcache);
        }
        if (!data.empty()) log("native renderer: pipeline cache %.1f MiB from the last run", double(data.size()) / 1048576.0);
    }
    {
        const char* v = std::getenv("D1_NG_PUSH_DESCRIPTORS");
        if (!v || std::atoi(v) != 0) {
            push_fn = reinterpret_cast<PFN_vkCmdPushDescriptorSetKHR>(vkGetDeviceProcAddr(ctx.device, "vkCmdPushDescriptorSet"));
            if (!push_fn) push_fn = reinterpret_cast<PFN_vkCmdPushDescriptorSetKHR>(vkGetDeviceProcAddr(ctx.device, "vkCmdPushDescriptorSetKHR"));
            VkPhysicalDevicePushDescriptorPropertiesKHR pp{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PUSH_DESCRIPTOR_PROPERTIES_KHR};
            VkPhysicalDeviceProperties2 p2{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2, &pp};
            vkGetPhysicalDeviceProperties2(ctx.gpu, &p2);
            max_push = push_fn ? pp.maxPushDescriptors : 0;
            log("native renderer: push descriptors %s (up to %u)", push_fn && max_push ? "on" : "unavailable", max_push);
        }
    }
    opt.frames_in_flight = std::clamp(opt.frames_in_flight, 1u, 4u);
    log("native renderer: %s, Vulkan %u.%u, %llu MiB upload ring, %u frame%s in flight%s%s", ctx.name,
        VK_API_VERSION_MAJOR(ctx.api_version), VK_API_VERSION_MINOR(ctx.api_version), (unsigned long long)ring_mb,
        opt.frames_in_flight, opt.frames_in_flight == 1 ? "" : "s", sc.failed ? "" : ", presenting to the window",
        opt.frames_dir ? ", writing frames" : "");
    // D1_NG_RECORD_THREADS=<n>: worker threads recording runs of draws in parallel (default:
    // up to 6, leaving four hardware threads for the game; 0 = all on one thread)
    // D1_NG_RECORD_RUN=<n>: fewest draws in one render pass that are split (default 64)
    {
        const uint32_t hw = std::max(1u, std::thread::hardware_concurrency());
        rec_threads = hw >= 6 ? std::min(6u, hw - 4) : 0;
        if (const char* v = std::getenv("D1_NG_RECORD_THREADS")) rec_threads = uint32_t(std::clamp(std::atoi(v), 0, 15));
        if (const char* v = std::getenv("D1_NG_RECORD_RUN")) rec_min_run = uint32_t(std::max(2, std::atoi(v)));
        if (rec_threads) start_workers();
        log("native renderer: recording on %u thread%s (runs of %u+ draws in one pass split)", rec_threads + 1,
            rec_threads ? "s" : "", rec_min_run);
    }
    // D1_ND_RECORD=0: lists are recorded on the GPU queue thread at submission (as before)
    {
        const char* v = std::getenv("D1_ND_RECORD");
        list_rec = (!v || std::atoi(v) != 0) && !debug && passlog_frame == UINT64_MAX && !std::getenv("D1_NG_TRACE") &&
                   !std::getenv("D1_NG_DRAWSTATS");
        log("native renderer: command lists recorded %s", list_rec ? "on the engine's threads as they end" : "at submission");
    }
    start_loader();
    {
        const char* v = std::getenv("D1_NG_DYNAMIC_COPY");
        dynamic_copy = opt.res_current && (!v || std::atoi(v) != 0);
    }
    return true;
}

// ---------------------------------------------------------------------------- submissions
void Renderer::begin_record() {
    if (rc().cur != UINT32_MAX) return;
    if (idle_subs.empty()) retire_one();
    if (idle_subs.empty()) return;  // (every submission slot recorded and not yet submitted)
    rc().cur = idle_subs.back();
    idle_subs.pop_back();
    Sub& sb = subs[rc().cur];
    sb.ring_begin = ring_head;
    sb.state = Sub::Recording;
    sb.submit_no = rc().submit_no;
    for (VkDescriptorPool p : sb.pools) vkResetDescriptorPool(ctx.device, p, 0);
    sb.pool = 0;
    vkResetFences(ctx.device, 1, &sb.fence);
    vkResetCommandPool(ctx.device, sb.cpool, 0);
    for (auto& w : sb.sec)
        if (w.used) vkResetCommandPool(ctx.device, w.pool, 0), w.used = 0;
    VkCommandBufferBeginInfo bi{VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
    bi.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
    vkBeginCommandBuffer(sb.cmd, &bi);
    rc().dstate.valid = false;
    rc().cmd = sb.cmd;
    rc().snaps.clear(), rc().snap_key = 0, rc().fresh.clear(), rc().pass_live.clear(), rc().pass_written.clear();
    barrier();  // earlier submissions' writes before anything here
}

void Renderer::submit(const VkSemaphoreSubmitInfo* wait, const VkSemaphoreSubmitInfo* signal) {
    if (rc().cur == UINT32_MAX) return;
    vkEndCommandBuffer(subs[rc().cur].cmd);
    submit_sub(rc().cur, wait, signal);
    rc().cur = UINT32_MAX;
    rc().cmd = VK_NULL_HANDLE;
}

void Renderer::submit_sub(uint32_t i, const VkSemaphoreSubmitInfo* wait, const VkSemaphoreSubmitInfo* signal) {
    Sub& sb = subs[i];
    VkCommandBufferSubmitInfo cbi{VK_STRUCTURE_TYPE_COMMAND_BUFFER_SUBMIT_INFO};
    cbi.commandBuffer = sb.cmd;
    VkSubmitInfo2 si{VK_STRUCTURE_TYPE_SUBMIT_INFO_2};
    si.commandBufferInfoCount = 1;
    si.pCommandBufferInfos = &cbi;
    si.waitSemaphoreInfoCount = wait ? 1 : 0;
    si.pWaitSemaphoreInfos = wait;
    // the timeline semaphore counts completed submissions (waited for without the lock)
    VkSemaphoreSubmitInfo sig[2]{};
    uint32_t nsig = 0;
    if (signal) sig[nsig++] = *signal;
    if (timeline) {
        sig[nsig] = {VK_STRUCTURE_TYPE_SEMAPHORE_SUBMIT_INFO};
        sig[nsig].semaphore = timeline, sig[nsig].value = serial_next, sig[nsig].stageMask = VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT;
        ++nsig;
    }
    si.signalSemaphoreInfoCount = nsig;
    si.pSignalSemaphoreInfos = sig;
    const uint64_t ts0 = now_ns();
    const VkResult r = vkQueueSubmit2(ctx.queue, 1, &si, sb.fence);
    st.t_submit += now_ns() - ts0;
    if (r != VK_SUCCESS) {
        static int logged = 0;
        if (logged++ < 5) log("native renderer: vkQueueSubmit2 failed (%d)%s", int(r),
                              r == VK_ERROR_DEVICE_LOST ? ": the GPU device was lost" : "");
        if (r == VK_ERROR_DEVICE_LOST) {
            log("native renderer: cannot continue after a lost device");
            std::_Exit(1);
        }
    }
    sb.serial = serial_next++;
    sb.state = Sub::Inflight;
    inflight.push_back(i);
}

// Descriptor sets come from pools owned by the recording submission, reset when it is reused.
VkDescriptorSet Renderer::alloc_set(VkDescriptorSetLayout layout) {
    Sub& sb = subs[rc().cur];
    for (;;) {
        if (sb.pool == sb.pools.size()) {
            const VkDescriptorPoolSize sizes[] = {{VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE, 16384},
                                                  {VK_DESCRIPTOR_TYPE_SAMPLER, 16384},
                                                  {VK_DESCRIPTOR_TYPE_STORAGE_BUFFER, 8192}};
            VkDescriptorPoolCreateInfo pci{VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO};
            pci.maxSets = 4096;
            pci.poolSizeCount = 3;
            pci.pPoolSizes = sizes;
            VkDescriptorPool p = VK_NULL_HANDLE;
            if (vkCreateDescriptorPool(ctx.device, &pci, nullptr, &p) != VK_SUCCESS) return VK_NULL_HANDLE;
            sb.pools.push_back(p);
        }
        VkDescriptorSetAllocateInfo ai{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO};
        ai.descriptorPool = sb.pools[sb.pool];
        ai.descriptorSetCount = 1;
        ai.pSetLayouts = &layout;
        VkDescriptorSet set = VK_NULL_HANDLE;
        if (vkAllocateDescriptorSets(ctx.device, &ai, &set) == VK_SUCCESS) return set;
        ++sb.pool;  // full: the next pool
    }
}

void Renderer::retire_one() {
    if (inflight.empty()) return;
    const uint32_t i = inflight.front();
    inflight.pop_front();
    Sub& sb = subs[i];
    const uint64_t tw = now_ns();
    vkWaitForFences(ctx.device, 1, &sb.fence, VK_TRUE, UINT64_MAX);
    st.t_wait += now_ns() - tw;
    write_zpass_results(sb);
    for (const auto& rb : sb.readbacks)  // the GPU's results where the game reads them
        if (sb.rb.map && guest_region_extent(rb.base) >= rb.sf.total_size)
            tiling::tile(rb.sf, 0, sb.rb.map + rb.off, reinterpret_cast<uint8_t*>(rb.base));
    st.readbacks += sb.readbacks.size();
    sb.readbacks.clear();
    sb.rb_used = 0;
    for (auto& b : sb.staging) free_buffer(b);
    sb.staging.clear();
    serial_done = std::max(serial_done, sb.serial);
    sb.state = Sub::Idle;
    idle_subs.push_back(i);
    reap();
}

// The oldest recording any submission slot in use (recording, recorded or in flight) made:
// what was dropped before it can be freed.
uint64_t Renderer::min_live_submit() const {
    uint64_t m = UINT64_MAX;
    for (const Sub& sb : subs)
        if (sb.state != Sub::Idle) m = std::min(m, sb.submit_no);
    return m;
}

uint64_t Renderer::oldest_ring() const {
    uint64_t m = ring_head;
    for (const Sub& sb : subs)
        if (sb.state != Sub::Idle) m = std::min(m, sb.ring_begin);
    return m;
}

void Renderer::bury(std::unique_ptr<Image> img) {
    if (!img) return;
    std::lock_guard lk(grave_m);
    grave.push_back({submit_seq.load(), std::move(img), {}});
}

void Renderer::reap() {
    const uint64_t live = min_live_submit();
    std::vector<Dead> now;
    {
        std::lock_guard lk(grave_m);
        auto keep = std::stable_partition(grave.begin(), grave.end(), [&](const Dead& d) { return d.tag >= live; });
        std::move(keep, grave.end(), std::back_inserter(now));
        grave.erase(keep, grave.end());
    }
    for (Dead& d : now) {
        if (d.img) destroy_image(d.img.get());
        else geo_free_now(int(d.geo[0]), d.geo[1], d.geo[2]);
    }
}

void Renderer::retire_completed() {
    while (!inflight.empty() && vkGetFenceStatus(ctx.device, subs[inflight.front()].fence) == VK_SUCCESS) retire_one();
}

void Renderer::wait_serial(uint64_t serial) {
    while (serial_done < serial && !inflight.empty()) retire_one();
}

VkDeviceMemory Renderer::alloc(VkMemoryRequirements req, VkMemoryPropertyFlags want) {
    VkMemoryAllocateInfo ai{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
    ai.allocationSize = req.size;
    ai.memoryTypeIndex = find_memory_type(ctx, req.memoryTypeBits, want);
    if (ai.memoryTypeIndex == UINT32_MAX) ai.memoryTypeIndex = find_memory_type(ctx, req.memoryTypeBits, 0);
    VkDeviceMemory m = VK_NULL_HANDLE;
    if (vkAllocateMemory(ctx.device, &ai, nullptr, &m) != VK_SUCCESS) return VK_NULL_HANDLE;
    return m;
}

Buffer Renderer::make_buffer(uint64_t size, VkBufferUsageFlags usage, bool host, bool prefer_device) {
    Buffer b;
    b.size = size;
    VkBufferCreateInfo bci{VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
    bci.size = size;
    bci.usage = usage;
    if (vkCreateBuffer(ctx.device, &bci, nullptr, &b.buf) != VK_SUCCESS) return Buffer{};
    VkMemoryRequirements req;
    vkGetBufferMemoryRequirements(ctx.device, b.buf, &req);
    const VkMemoryPropertyFlags hv = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT;
    // host-visible memory in VRAM (resizable BAR) where the GPU offers it: what shaders read
    // from it every frame (constants, streamed vertices) then stays on the card instead of
    // crossing PCIe on every access
    if (host && prefer_device) {
        const uint32_t t = find_memory_type(ctx, req.memoryTypeBits, hv | VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
        if (t != UINT32_MAX) {
            VkMemoryAllocateInfo ai{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
            ai.allocationSize = req.size;
            ai.memoryTypeIndex = t;
            if (vkAllocateMemory(ctx.device, &ai, nullptr, &b.mem) != VK_SUCCESS) b.mem = VK_NULL_HANDLE;
            else log("native renderer: %llu MiB buffer in device-local host-visible memory", (unsigned long long)(size >> 20));
        }
    }
    if (!b.mem)
        b.mem = alloc(req, host ? hv : VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
    if (!b.mem) {
        vkDestroyBuffer(ctx.device, b.buf, nullptr);
        return Buffer{};
    }
    vkBindBufferMemory(ctx.device, b.buf, b.mem, 0);
    if (host) {
        void* p = nullptr;
        vkMapMemory(ctx.device, b.mem, 0, VK_WHOLE_SIZE, 0, &p);
        b.map = static_cast<uint8_t*>(p);
    }
    return b;
}

// Memory the CPU reads after the GPU wrote it: host-cached where offered (reading uncached or
// write-combined memory is very slow), plain host-visible otherwise.
Buffer Renderer::make_readback_buffer(uint64_t size) {
    Buffer b;
    b.size = size;
    VkBufferCreateInfo bci{VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
    bci.size = size;
    bci.usage = VK_BUFFER_USAGE_TRANSFER_DST_BIT;
    if (vkCreateBuffer(ctx.device, &bci, nullptr, &b.buf) != VK_SUCCESS) return Buffer{};
    VkMemoryRequirements req;
    vkGetBufferMemoryRequirements(ctx.device, b.buf, &req);
    const VkMemoryPropertyFlags hv = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT;
    uint32_t t = find_memory_type(ctx, req.memoryTypeBits, hv | VK_MEMORY_PROPERTY_HOST_CACHED_BIT);
    if (t == UINT32_MAX) t = find_memory_type(ctx, req.memoryTypeBits, hv);
    VkMemoryAllocateInfo ai{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
    ai.allocationSize = req.size;
    ai.memoryTypeIndex = t;
    if (t == UINT32_MAX || vkAllocateMemory(ctx.device, &ai, nullptr, &b.mem) != VK_SUCCESS) {
        vkDestroyBuffer(ctx.device, b.buf, nullptr);
        return Buffer{};
    }
    vkBindBufferMemory(ctx.device, b.buf, b.mem, 0);
    void* p = nullptr;
    vkMapMemory(ctx.device, b.mem, 0, VK_WHOLE_SIZE, 0, &p);
    b.map = static_cast<uint8_t*>(p);
    return b;
}

Alloc Renderer::heap_alloc(VkMemoryRequirements req) {
    Alloc a;
    uint32_t type = find_memory_type(ctx, req.memoryTypeBits, VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
    if (type == UINT32_MAX) type = find_memory_type(ctx, req.memoryTypeBits, 0);
    if (type == UINT32_MAX) return a;
    const uint64_t align = std::max<uint64_t>({req.alignment, ctx.props.limits.bufferImageGranularity, 256});
    auto dedicated = [&] {
        VkMemoryAllocateInfo ai{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
        ai.allocationSize = req.size;
        ai.memoryTypeIndex = type;
        if (vkAllocateMemory(ctx.device, &ai, nullptr, &a.mem) != VK_SUCCESS) a.mem = VK_NULL_HANDLE;
        a.size = req.size, a.offset = 0, a.block = -1;
        if (a.mem) heap.used += req.size;
        return a;
    };
    if (req.size >= (64ull << 20)) return dedicated();
    for (int pass = 0; pass < 2; ++pass) {
        for (size_t bi = 0; bi < heap.blocks.size(); ++bi) {
            auto& b = heap.blocks[bi];
            if (b.type != type) continue;
            // best fit: the smallest free ranges that can hold the size, until one does once aligned
            for (auto it = b.by_size.lower_bound(req.size); it != b.by_size.end(); ++it) {
                ++st.heap_scans;
                const uint64_t fo = it->second, fs = it->first;
                const uint64_t start = (fo + align - 1) & ~(align - 1);
                if (start + req.size > fo + fs) continue;
                b.remove(fo, fs);
                if (start > fo) b.add(fo, start - fo);
                if (start + req.size < fo + fs) b.add(start + req.size, fo + fs - (start + req.size));
                a.mem = b.mem, a.offset = start, a.size = req.size, a.block = int(bi);
                heap.used += req.size;
                return a;
            }
        }
        if (pass) break;
        // a new block
        Heap::Block nb;
        nb.type = type;
        for (uint64_t sz : {256ull << 20, 64ull << 20}) {
            VkMemoryAllocateInfo ai{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
            ai.allocationSize = sz;
            ai.memoryTypeIndex = type;
            if (vkAllocateMemory(ctx.device, &ai, nullptr, &nb.mem) == VK_SUCCESS) {
                nb.size = sz;
                break;
            }
            nb.mem = VK_NULL_HANDLE;
        }
        if (!nb.mem) break;
        ++st.heap_blocks_new;
        nb.add(0, nb.size);
        heap.reserved += nb.size;
        heap.blocks.push_back(std::move(nb));
    }
    return dedicated();
}

void Renderer::heap_free(Alloc& a) {
    if (!a.mem) return;
    heap.used -= a.size;
    if (a.block < 0) {
        vkFreeMemory(ctx.device, a.mem, nullptr);
    } else {
        auto& blk = heap.blocks[size_t(a.block)];
        auto& fr = blk.free;
        uint64_t off = a.offset, size = a.size;
        auto next = fr.lower_bound(off);
        if (next != fr.end() && next->first == off + size) {  // merge with the following range
            const uint64_t no = next->first, ns = next->second;
            size += ns;
            blk.remove(no, ns);
        }
        next = fr.lower_bound(off);
        if (next != fr.begin()) {  // and the preceding one
            auto prev = std::prev(next);
            if (prev->first + prev->second == off) {
                const uint64_t po = prev->first, ps = prev->second;
                off = po, size += ps;
                blk.remove(po, ps);
            }
        }
        blk.add(off, size);
    }
    a = Alloc{};
}

void Renderer::destroy_image(Image* img) {
    if (!img) return;
    for (auto& [k, v] : img->views) vkDestroyImageView(ctx.device, v, nullptr);
    img->views.clear();
    if (img->attachment) vkDestroyImageView(ctx.device, img->attachment, nullptr);
    img->attachment = VK_NULL_HANDLE;
    if (img->image) vkDestroyImage(ctx.device, img->image, nullptr);
    img->image = VK_NULL_HANDLE;
    heap_free(img->mem);
}

void Renderer::free_buffer(Buffer& b) {
    if (b.buf) vkDestroyBuffer(ctx.device, b.buf, nullptr);
    if (b.mem) vkFreeMemory(ctx.device, b.mem, nullptr);
    b = Buffer{};
}

std::unique_ptr<Image> Renderer::make_image(VkFormat f, uint32_t w, uint32_t h, uint32_t d, uint32_t layers,
                                            uint32_t levels, bool cube, bool is3d, bool depth, bool stencil) {
    auto img = std::make_unique<Image>();
    img->format = f, img->w = w, img->h = h, img->d = d, img->layers = layers, img->levels = levels;
    img->cube = cube, img->is3d = is3d, img->depth = depth, img->stencil = stencil;
    VkImageCreateInfo ici{VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO};
    ici.flags = (cube ? VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT : 0) | VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT |
                (is3d ? VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT : 0);
    ici.imageType = is3d ? VK_IMAGE_TYPE_3D : VK_IMAGE_TYPE_2D;
    ici.format = f;
    ici.extent = {w, h, is3d ? d : 1};
    ici.mipLevels = levels;
    ici.arrayLayers = is3d ? 1 : layers;
    ici.samples = VK_SAMPLE_COUNT_1_BIT;
    ici.tiling = VK_IMAGE_TILING_OPTIMAL;
    ici.usage = VK_IMAGE_USAGE_SAMPLED_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT | VK_IMAGE_USAGE_TRANSFER_SRC_BIT;
    const bool bc = f >= VK_FORMAT_BC1_RGB_UNORM_BLOCK && f <= VK_FORMAT_BC7_SRGB_BLOCK;
    // only what this GPU supports for the format (asking for more is invalid: drivers may
    // then produce garbage)
    const VkFormatFeatureFlags ff = format_props(f).optimalTilingFeatures;
    if (depth) ici.usage |= VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT;
    else if (!bc && (ff & VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT)) ici.usage |= VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT;
    {
        static std::mutex lm;
        static std::unordered_set<int> told;
        const char* why = !(ff & VK_FORMAT_FEATURE_SAMPLED_IMAGE_BIT) ? "cannot be sampled"
                        : depth && !(ff & VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT) ? "cannot be a depth target"
                        : !(ff & VK_FORMAT_FEATURE_TRANSFER_DST_BIT) ? "cannot be copied to"
                        : nullptr;
        std::lock_guard lk(lm);
        if (why && told.insert(int(f)).second) log("native renderer: image format %d %s on this GPU", int(f), why);
        if (!depth && !bc && !(ff & VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT) && told.insert(int(f) | 1 << 30).second)
            log("native renderer: image format %d cannot be rendered to on this GPU (textures only)", int(f));
    }
    ici.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
    const uint64_t t0 = now_ns();
    if (const VkResult r = vkCreateImage(ctx.device, &ici, nullptr, &img->image); r != VK_SUCCESS) {
        static std::atomic<int> told{0};
        if (told++ < 20) log("native renderer: vkCreateImage failed (%d): format %d %ux%ux%u, %u levels, %u layers", int(r), int(f), w, h, d, levels, layers);
        return nullptr;
    }
    VkMemoryRequirements req;
    vkGetImageMemoryRequirements(ctx.device, img->image, &req);
    const uint64_t t1 = now_ns();
    st.t_vkimg += t1 - t0;
    img->mem = heap_alloc(req);
    st.t_heap += now_ns() - t1;
    if (!img->mem.mem) {
        static int logged = 0;
        if (logged++ < 5) log("native renderer: out of GPU memory for a %ux%u image (%.0f MiB in use)", w, h,
                              double(heap.used) / 1048576.0);
        vkDestroyImage(ctx.device, img->image, nullptr);
        return nullptr;
    }
    const uint64_t tb = now_ns();
    vkBindImageMemory(ctx.device, img->image, img->mem.mem, img->mem.offset);
    st.t_bind += now_ns() - tb;
    // straight to GENERAL, where every image lives
    VkImageMemoryBarrier2 b{VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER_2};
    b.srcStageMask = VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT;
    b.dstStageMask = VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT;
    b.dstAccessMask = VK_ACCESS_2_MEMORY_READ_BIT | VK_ACCESS_2_MEMORY_WRITE_BIT;
    b.oldLayout = VK_IMAGE_LAYOUT_UNDEFINED;
    b.newLayout = VK_IMAGE_LAYOUT_GENERAL;
    b.srcQueueFamilyIndex = b.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    b.image = img->image;
    b.subresourceRange = {depth ? VkImageAspectFlags(VK_IMAGE_ASPECT_DEPTH_BIT | (stencil ? VK_IMAGE_ASPECT_STENCIL_BIT : 0))
                                : VkImageAspectFlags(VK_IMAGE_ASPECT_COLOR_BIT),
                          0, VK_REMAINING_MIP_LEVELS, 0, VK_REMAINING_ARRAY_LAYERS};
    VkDependencyInfo di{VK_STRUCTURE_TYPE_DEPENDENCY_INFO};
    di.imageMemoryBarrierCount = 1;
    di.pImageMemoryBarriers = &b;
    vkCmdPipelineBarrier2(rc().cmd, &di);
    // the attachment view waits until the image is rendered to: most images are textures, and
    // making views is slow on some drivers
    if (!bc && !is3d) img->att_aspect = b.subresourceRange.aspectMask;
    return img;
}

VkImageView Renderer::view(Image* img, VkImageViewType type, VkComponentMapping comp, uint32_t base_level,
                           bool depth_aspect, bool stencil_aspect) {
    if (img->is3d) type = VK_IMAGE_VIEW_TYPE_3D;
    if (type == VK_IMAGE_VIEW_TYPE_CUBE && (!img->cube || img->layers < 6)) type = VK_IMAGE_VIEW_TYPE_2D_ARRAY;
    if (type == VK_IMAGE_VIEW_TYPE_3D && !img->is3d) type = VK_IMAGE_VIEW_TYPE_2D_ARRAY;
    const uint64_t key = mix(mix(mix(type, uint64_t(comp.r) | uint64_t(comp.g) << 8 | uint64_t(comp.b) << 16 |
                                               uint64_t(comp.a) << 24),
                                 base_level),
                             uint64_t(depth_aspect) | uint64_t(stencil_aspect) << 1);
    auto it = img->views.find(key);
    if (it != img->views.end()) return it->second;
    VkImageViewCreateInfo vci{VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};
    vci.image = img->image;
    vci.viewType = type;
    vci.format = img->format;
    vci.components = img->depth ? VkComponentMapping{} : comp;
    const uint32_t lvl = std::min(base_level, img->levels - 1);
    vci.subresourceRange = {stencil_aspect ? VkImageAspectFlags(VK_IMAGE_ASPECT_STENCIL_BIT)
                            : img->depth   ? VkImageAspectFlags(VK_IMAGE_ASPECT_DEPTH_BIT)
                                           : VkImageAspectFlags(VK_IMAGE_ASPECT_COLOR_BIT),
                            lvl, img->levels - lvl, 0,
                            type == VK_IMAGE_VIEW_TYPE_CUBE ? 6u
                            : type == VK_IMAGE_VIEW_TYPE_2D || type == VK_IMAGE_VIEW_TYPE_3D ? 1u
                                                                                            : img->layers};
    VkImageView v = VK_NULL_HANDLE;
    vkCreateImageView(ctx.device, &vci, nullptr, &v);
    img->views[key] = v;
    return v;
}

// The ring is circular in absolute positions: an allocation may reuse space once every
// submission recorded before it reached that space has completed.
uint64_t Renderer::ring_alloc(uint64_t size, uint64_t align) {
    const uint64_t R = ring.size;
    if (size > R / 2 || rc().cur == UINT32_MAX) return UINT64_MAX;
    uint64_t off = ring_head % R;
    uint64_t p = (off + align - 1) & ~(align - 1);
    if (p + size > R) {  // wrap to the start
        ring_head += R - off;
        off = 0, p = 0;
    }
    const uint64_t end = ring_head - off + p + size;
    // (the oldest allocation still in use only moves forward: a slot begun later starts at the head)
    while (end > ring_oldest + R) {
        ring_oldest = oldest_ring();
        if (end <= ring_oldest + R) break;
        if (inflight.empty()) return UINT64_MAX;  // the recordings in progress need more than the ring
        retire_one();
    }
    ring_head = end;
    st.ring_peak = std::max(st.ring_peak, ring_head - ring_oldest);
    return p;
}

uint64_t Renderer::ring_copy(const void* src, uint64_t size) {
    const uint64_t p = ring_alloc(std::max<uint64_t>(size, 16));
    if (p == UINT64_MAX) return p;
    std::memcpy(ring.map + p, src, size);
    return p;
}

uint64_t Renderer::rec_ring(Rec& r, uint64_t size, uint64_t align) {
    if (!r.parallel) return ring_alloc(size, align);
    uint64_t p = (r.chunk_pos + align - 1) & ~(align - 1);
    if (p + size > r.chunk_end) {
        constexpr uint64_t kChunk = 1ull << 20;
        const uint64_t want = std::max(kChunk, size + align);
        uint64_t c;
        {
            std::lock_guard lk(rc().lr ? m : ring_m);
            c = ring_alloc(want, 256);
        }
        if (c == UINT64_MAX) return UINT64_MAX;
        r.chunk_pos = c, r.chunk_end = c + want;
        p = (r.chunk_pos + align - 1) & ~(align - 1);
    }
    r.chunk_pos = p + size;
    return p;
}

void Renderer::barrier() {
    VkMemoryBarrier2 mb{VK_STRUCTURE_TYPE_MEMORY_BARRIER_2};
    mb.srcStageMask = mb.dstStageMask = VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT;
    mb.srcAccessMask = VK_ACCESS_2_MEMORY_WRITE_BIT;
    mb.dstAccessMask = VK_ACCESS_2_MEMORY_READ_BIT | VK_ACCESS_2_MEMORY_WRITE_BIT;
    VkDependencyInfo di{VK_STRUCTURE_TYPE_DEPENDENCY_INFO};
    di.memoryBarrierCount = 1;
    di.pMemoryBarriers = &mb;
    vkCmdPipelineBarrier2(rc().cmd, &di);
}

// Gnm RenderTarget: CB_COLOR_BASE, PITCH, SLICE, VIEW, INFO, ATTRIB, packed size, CMASK...
Image* Renderer::color_target(const uint32_t* c, bool bind) {
    const uint64_t base = uint64_t(c[0]) << 8;
    const uint32_t format = (c[4] >> 2) & 0x1F, number = (c[4] >> 8) & 7, swap = (c[4] >> 11) & 3;
    if (!base || !format) return nullptr;
    const uint32_t w = c[6] & 0xFFFF, h = c[6] >> 16;
    if (!w || !h) return nullptr;
    VkFormat f = fmt::vk_format(fmt::color_to_data_format(format), cb_number_to_nfmt(number));
    if (f == VK_FORMAT_UNDEFINED) return nullptr;
    // CB_COLOR_VIEW: a layered target (rendered slice by slice, e.g. the 3D color-grading
    // LUT): each pass names its slice in SLICE_START..SLICE_MAX. The depth is not in the
    // descriptor; the image is made as deep as the slices seen (at least its width, as for a
    // cube LUT) and rebuilt deeper if a later slice needs it.
    const uint32_t slice = c[3] & 0x7FF, slice_max = (c[3] >> 13) & 0x7FF;
    const bool layered = slice_max > 0;
    const uint64_t key = mix(mix(mix(mix(base, f), w), h), layered);
    auto it = targets.find(key);
    Image* img = it != targets.end() ? it->second.get() : nullptr;
    if (!img || (layered && img->d <= slice_max)) {
        const uint32_t depth = layered ? std::max(slice_max + 1, std::min(w, 64u)) : 1;
        auto n = make_image(f, w, h, depth, 1, 1, false, layered, false, false);
        if (!n) return nullptr;
        {  // new images hold undefined data (garbage on most GPUs): start from zero
            VkClearColorValue zero{};
            VkImageSubresourceRange r{VK_IMAGE_ASPECT_COLOR_BIT, 0, 1, 0, 1};
            vkCmdClearColorImage(rc().cmd, n->image, VK_IMAGE_LAYOUT_GENERAL, &zero, 1, &r);
        }
        n->base = base, n->swap = swap;
        if (++base_targets[base] > 1) {  // the same memory as another target (aliasing): diagnostics
            static int told = 0;
            auto prev = target_by_base.find(base);
            if (told++ < 60 && prev != target_by_base.end())
                log("native renderer: target %llx now also %ux%u format %d (was %ux%u format %d)", (unsigned long long)base, w, h,
                    int(f), prev->second->w, prev->second->h, int(prev->second->format));
        }
        img = n.get();
        if (auto old = targets.find(key); old != targets.end()) {
            auto& v = images_by_base[base];
            v.erase(std::remove(v.begin(), v.end(), old->second.get()), v.end());
            retired.push_back(std::move(old->second));
        }
        images_by_base[base].push_back(n.get());
        (++targets_gen, ++gen_why[2]);
        targets[key] = std::move(n);
        ++st.targets;
    }
    target_bases.insert(base);
    if (bind || !target_by_base.count(base)) set_base(target_by_base, base, img), img->bound_serial = ++bind_serial;
    img->last_used = rc().submit_no;
    img->bind_slice = std::min(slice, img->d - 1);
    img->tile_mode = c[5] & 0x1F, img->pitch = ((c[1] & 0x7FF) + 1) * 8;
    img->bpp = fmt::data_format(fmt::color_to_data_format(format)).bpp;
    // rendered to (once a frame): remember the memory's version (see target_current)
    if (bind && (opt.watch || dynamic_copy) && !layered && img->tv_frame != st.frames + 1 && uint64_t(w) * h <= 512 * 512 && img->bpp) {
        img->tv_frame = st.frames + 1;
        if (!img->tv_size) {
            tiling::Surface sf;
            sf.tile_mode = img->tile_mode, sf.bpp = img->bpp, sf.width = w, sf.height = h, sf.pitch = img->pitch;
            tiling::layout(sf);
            img->tv_size = sf.total_size;
        }
        img->tv_version = guest_region_extent(base) >= img->tv_size ? mem_watch(base, img->tv_size) : ~0ull;
        if (dynamic_copy) dyn_targets.insert(base);
    }
    return img;
}

VkImageView Renderer::attachment_view(Image* img) {
    if (!img->is3d) {
        if (!img->attachment && img->att_aspect) {
            VkImageViewCreateInfo vci{VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};
            vci.image = img->image;
            vci.viewType = VK_IMAGE_VIEW_TYPE_2D;
            vci.format = img->format;
            vci.subresourceRange = {img->att_aspect, 0, 1, 0, 1};
            const uint64_t tv = now_ns();
            vkCreateImageView(ctx.device, &vci, nullptr, &img->attachment);
            st.t_view += now_ns() - tv;
        }
        return img->attachment;
    }
    const uint64_t key = 0xA77AC4ull << 32 | img->bind_slice;
    auto it = img->views.find(key);
    if (it != img->views.end()) return it->second;
    VkImageViewCreateInfo vci{VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};
    vci.image = img->image;
    vci.viewType = VK_IMAGE_VIEW_TYPE_2D;
    vci.format = img->format;
    vci.subresourceRange = {VK_IMAGE_ASPECT_COLOR_BIT, 0, 1, img->bind_slice, 1};
    VkImageView v = VK_NULL_HANDLE;
    vkCreateImageView(ctx.device, &vci, nullptr, &v);
    img->views[key] = v;
    return v;
}

// Gnm DepthRenderTarget: Z_INFO, STENCIL_INFO, Z_READ_BASE, STENCIL_READ_BASE, Z_WRITE_BASE,
// STENCIL_WRITE_BASE, DEPTH_SIZE, DEPTH_SLICE, DEPTH_VIEW, HTILE_DATA_BASE, HTILE_SURFACE,
// DEPTH_INFO, packed size
Image* Renderer::depth_target(const uint32_t* d, bool bind) {
    const uint32_t zfmt = d[0] & 3, sfmt = d[1] & 1;
    const uint64_t base = uint64_t(d[4]) << 8;
    if (!zfmt || !base) return nullptr;
    const uint32_t w = d[12] & 0xFFFF, h = d[12] >> 16;
    if (!w || !h) return nullptr;
    const VkFormat f = sfmt ? VK_FORMAT_D32_SFLOAT_S8_UINT : zfmt == 1 ? VK_FORMAT_D16_UNORM : VK_FORMAT_D32_SFLOAT;
    const uint64_t key = mix(mix(mix(base, f), w), h);
    auto it = targets.find(key);
    Image* img;
    if (it != targets.end()) img = it->second.get();
    else {
        auto n = make_image(f, w, h, 1, 1, 1, false, false, true, sfmt != 0);
        if (!n) return nullptr;
        {
            VkClearDepthStencilValue z{0.0f, 0};
            VkImageSubresourceRange r{VkImageAspectFlags(VK_IMAGE_ASPECT_DEPTH_BIT | (sfmt ? VK_IMAGE_ASPECT_STENCIL_BIT : 0)), 0, 1, 0, 1};
            vkCmdClearDepthStencilImage(rc().cmd, n->image, VK_IMAGE_LAYOUT_GENERAL, &z, 1, &r);
        }
        n->base = base;
        img = n.get();
        images_by_base[base].push_back(img);
        (++targets_gen, ++gen_why[3]);
        targets[key] = std::move(n);
        ++st.targets;
    }
    const uint64_t read_base = uint64_t(d[2]) << 8;  // Z_READ_BASE
    if (bind) img->bound_serial = ++bind_serial;
    target_bases.insert(base), target_bases.insert(read_base);
    if (bind || !target_by_base.count(base)) set_base(target_by_base, base, img);
    if (bind || !target_by_base.count(read_base)) set_base(target_by_base, read_base, img);
    if (sfmt)  // the stencil plane lives at its own address; shaders read it as an 8-bit texture
        for (const uint64_t sb : {uint64_t(d[3]) << 8, uint64_t(d[5]) << 8})
            if (sb && sb != base) {
                target_bases.insert(sb);
                if (bind || !stencil_by_base.count(sb)) set_base(stencil_by_base, sb, img);
                static std::unordered_set<uint64_t> told;
                if (told.size() < 32 && told.insert(sb).second)
                    log("native renderer: depth target %llx %ux%u has its stencil at %llx", (unsigned long long)base, w, h,
                        (unsigned long long)sb);
            }
    img->last_used = rc().submit_no;
    return img;
}

Image* Renderer::upload_texture(const uint32_t* t, uint64_t res) {
    const uint64_t t_in = now_ns();
    struct LoadTimer {
        Renderer* r;
        uint64_t t0;
        ~LoadTimer() { r->st.t_tex_load += now_ns() - t0; }
    };
    const uint64_t key = tex_key(t, res);
    ++st.tex_checks;
    std::unique_ptr<Image> prev;
    auto it = textures.find(key);
    bool found = it != textures.end();
    if (found && it->second && it->second->stale) {  // written by a copy command: copied again
        prev = std::move(it->second);
        prev->stale = false;
        textures.erase(it), found = false; ++views_gen;
        ++st.tex_reloads;
    }
    if (found) {
        Image* img = it->second.get();
        if (!img) return nullptr;
        img->last_used = rc().submit_no;
        if (res && img->res_val) {
            // an engine resource: unchanged while its epoch is; after an event (a move, most
            // often) the same contents at the new address keep the image
            if (img->res_val == res) {
                ++st.res_hits;
                // D1_NG_VERIFY_RES=1: (testing) unchanged really? (a write the engine did not announce)
                static const bool verify_res = std::getenv("D1_NG_VERIFY_RES") != nullptr;
                if (verify_res && img->src_size && guest_region_extent(img->src_addr) >= img->src_size) {
                    const uint64_t h = hash_bytes(reinterpret_cast<const void*>(img->src_addr), img->src_size);
                    if (h != img->content) {
                        ++st.res_verify_missed;
                        static int told = 0;
                        if (told++ < 40) {
                            const auto tv = fmt::decode_tsharp(t);
                            log("native renderer: engine texture changed without an event: %#llx %ux%u fmt %u.%u type %u levels %u-%u (%llu bytes) res %#llx",
                                (unsigned long long)img->src_addr, tv.width, tv.height, tv.dfmt, tv.nfmt, tv.type, tv.base_level, tv.last_level,
                                (unsigned long long)img->src_size, (unsigned long long)res);
                        }
                        img->content = h;
                    } else ++st.res_verify_ok;
                }
                st.t_tex_hit += now_ns() - t_in;
                return img;
            }
            const auto ts0 = fmt::decode_tsharp(t);
            if (img->src_size && guest_region_extent(ts0.base) >= img->src_size &&
                hash_bytes(reinterpret_cast<const void*>(ts0.base), img->src_size) == img->content) {
                img->res_val = res, img->src_addr = ts0.base;
                ++st.res_moves;
                st.t_tex_hit += now_ns() - t_in;
                return img;
            }
            ++st.res_changed;
            prev = std::move(it->second);
            textures.erase(it), found = false; ++views_gen;
            ++st.tex_reloads;
        }
    }
    if (found) {
        Image* img = it->second.get();
        if (!res && st.unreg_tex.size() < 100000) st.unreg_tex[key] = uint64_t(img->w) * img->h * std::max(1u, img->bpp / 8);
        // rewritten textures are noticed at the next submission that uses them: the game may rewrite
        // a texture between two submissions of one frame (the null GPU finishes work at once)
        if (img->checked == rc().submit_no || !img->src_size || (!opt.version && !dynamic_copy)) {
            st.t_tex_hit += now_ns() - t_in;
            return img;
        }
        const uint64_t v = mem_version(img->src_addr, img->src_size);
        if (v == img->version) {
            // D1_NG_VERIFY_DYN=1: (testing) is it really unchanged? (a CPU write without an event)
            static const bool verify = std::getenv("D1_NG_VERIFY_DYN") != nullptr;
            if (verify && dynamic_copy && img->content) {
                if (guest_region_extent(img->src_addr) >= img->src_size &&
                    hash_bytes(reinterpret_cast<const void*>(img->src_addr), img->src_size) != img->content) {
                    ++dyn_verify_missed;
                    static int told = 0;
                    if (told++ < 30)
                        log("native renderer: dynamic texture %#llx (%llu bytes, %ux%u fmt %d) changed without an event", (unsigned long long)img->src_addr,
                            (unsigned long long)img->src_size, img->w, img->h, int(img->format));
                    img->content = hash_bytes(reinterpret_cast<const void*>(img->src_addr), img->src_size);
                } else ++dyn_verify_hits;
            }
            img->checked = rc().submit_no;
            st.t_tex_hit += now_ns() - t_in;
            return img;
        }
        if (v == ~0ull) ++st.tex_unwatched;
        // the game rewrote the texture's memory (streaming): copy it again (keeping the old
        // copy until the new one is known to be complete)
        prev = std::move(it->second);
        textures.erase(it); ++views_gen;
        ++st.tex_reloads;
    }
    LoadTimer load_timer{this, t_in};
    const auto ts = fmt::decode_tsharp(t);
    if (!res && st.unreg_tex.size() < 100000) st.unreg_tex[key] = uint64_t(ts.width) * ts.height;
    const auto fi = fmt::data_format(ts.dfmt);
    const VkFormat f = fmt::vk_format(ts.dfmt, ts.nfmt);
    tsharp_bases.insert(ts.base);  // memory read as a texture: never a readback target
    Image* out = nullptr;
    if (f != VK_FORMAT_UNDEFINED && fi.bpp && fi.bpp != 96 && ts.base && ts.width <= 16384 && ts.height <= 16384) {
        tiling::Surface sf;
        sf.tile_mode = ts.tiling, sf.bpp = fi.bpp, sf.block = fi.block, sf.pow2 = ts.pow2;
        sf.width = ts.width, sf.height = ts.height, sf.pitch = ts.pitch;
        const bool is3d = ts.type == 10, cube = ts.type == 11;
        sf.depth = is3d ? ts.depth : 1;
        sf.layers = (ts.type == 13 || ts.type == 12 || cube) ? ts.last_array + 1 : 1;
        if (cube) sf.layers = std::max(6u, sf.layers - sf.layers % 6);
        sf.levels = std::min(ts.last_level + 1, tiling::kMaxMips);
        tiling::layout(sf);
        if (const uint64_t ext = guest_region_extent(ts.base); ext && ext < sf.total_size) {
            static int told = 0;
            if (told++ < 20)
                log("native renderer: texture %llx %ux%u f%u type %u mips %u layers %u needs %llu bytes, mapping has %llu: not drawn",
                    (unsigned long long)ts.base, ts.width, ts.height, ts.dfmt, ts.type, sf.levels, sf.layers,
                    (unsigned long long)sf.total_size, (unsigned long long)ext);
            textures[key] = nullptr; ++views_gen;
            return nullptr;
        }
        // a rewrite of the same texture (per-frame tables, streaming into the same slot): copy
        // into the existing image - earlier submissions read it before this one's copies run
        // (the barrier at the start of every command buffer) - instead of making a new one
        std::unique_ptr<Image> img;
        if (prev && prev->format == f && prev->w == ts.width && prev->h == ts.height && prev->d == sf.depth &&
            prev->layers == sf.layers && prev->levels == sf.levels && prev->cube == cube && prev->is3d == is3d) {
            img = std::move(prev);
            img->torn = 0, img->res_val = 0;
            ++st.tex_inplace;
        } else {
            const uint64_t tm = now_ns();
            img = make_image(f, ts.width, ts.height, sf.depth, sf.layers, sf.levels, cube, is3d, false, false);
            st.t_mkimg += now_ns() - tm;
        }
        if (img && res) {  // an engine resource: its events say when it changes (no write tracking)
            img->res_val = res, img->src_addr = ts.base, img->src_size = sf.total_size, img->version = ~0ull;
            img->content = hash_bytes(reinterpret_cast<const void*>(ts.base), sf.total_size);
        } else if (img && (opt.watch || dynamic_copy)) {  // protect first, then copy: a later write shows up as a new version
            const uint64_t tw = now_ns();
            img->version = mem_watch(ts.base, sf.total_size);
            if (dynamic_copy && std::getenv("D1_NG_VERIFY_DYN")) img->content = hash_bytes(reinterpret_cast<const void*>(ts.base), sf.total_size);
            st.t_watch += now_ns() - tw;
            if (img->version != ~0ull) img->src_addr = ts.base, img->src_size = sf.total_size, img->checked = rc().submit_no;
        }
        if (img) {
            uint64_t total = 0;
            std::vector<uint64_t> sizes(sf.levels);
            for (uint32_t lv = 0; lv < sf.levels; ++lv) {
                const uint32_t mw = std::max(1u, ts.width >> lv), mh = std::max(1u, ts.height >> lv);
                const uint32_t ew = fi.block ? (mw + 3) / 4 : mw, eh = fi.block ? (mh + 3) / 4 : mh;
                sizes[lv] = uint64_t(ew) * eh * (fi.bpp / 8) * std::max(1u, is3d ? std::max(1u, sf.depth >> lv) : sf.layers);
                total += (sizes[lv] + 15) & ~15ull;
            }
            // staging: the ring (large textures get their own buffer, freed with the submission)
            Buffer sb;
            uint64_t base_off = ring_alloc(std::max<uint64_t>(total, 16), 256);
            bool own = base_off == UINT64_MAX;
            if (!own) sb = ring, sb.map = ring.map + base_off;
            else sb = make_buffer(std::max<uint64_t>(total, 16), VK_BUFFER_USAGE_TRANSFER_SRC_BIT, true), base_off = 0;
            if (sb.map) {
                std::vector<VkBufferImageCopy> regions;
                uint64_t off = 0;
                std::vector<uint64_t> level_off(sf.levels);
                {
                    uint64_t o = 0;
                    for (uint32_t lv = 0; lv < sf.levels; ++lv) level_off[lv] = o, o += (sizes[lv] + 15) & ~15ull;
                }
                // the staging memory may be the GPU's (write-combined): only ever written here.
                // Mips to rebuild are made in cached memory from the level above, then copied.
                const uint64_t tf0 = now_ns();
                const uint32_t missing = first_missing_mip(ts, fi, sf, is3d);
                const uint64_t td = now_ns();
                st.t_fill += td - tf0;
                if (missing < sf.levels) {
                    static thread_local std::vector<uint8_t> scratch;
                    scratch.resize(total);
                    for (uint32_t lv = 0; lv < missing; ++lv)
                        tiling::detile(sf, lv, reinterpret_cast<const uint8_t*>(ts.base), scratch.data() + level_off[lv]);
                    const uint64_t tf = now_ns();
                    st.t_detile += tf - td;
                    fill_missing_mips(missing, scratch.data(), level_off, sizes, ts, fi, sf, is3d);
                    std::memcpy(sb.map, scratch.data(), total);
                    st.t_fill += now_ns() - tf;
                } else {
                    for (uint32_t lv = 0; lv < sf.levels; ++lv)
                        tiling::detile(sf, lv, reinterpret_cast<const uint8_t*>(ts.base), sb.map + level_off[lv]);
                    st.t_detile += now_ns() - td;
                }
                for (uint32_t lv = 0; lv < sf.levels; ++lv) {
                    VkBufferImageCopy r{};
                    r.bufferOffset = base_off + off;
                    r.imageSubresource = {VK_IMAGE_ASPECT_COLOR_BIT, lv, 0, is3d ? 1u : sf.layers};
                    r.imageExtent = {std::max(1u, ts.width >> lv), std::max(1u, ts.height >> lv),
                                     is3d ? std::max(1u, sf.depth >> lv) : 1u};
                    regions.push_back(r);
                    off += (sizes[lv] + 15) & ~15ull;
                }
                vkCmdCopyBufferToImage(rc().cmd, sb.buf, img->image, VK_IMAGE_LAYOUT_GENERAL, uint32_t(regions.size()),
                                       regions.data());
                if (own) subs[rc().cur].staging.push_back(sb);
                out = img.get();
                out->last_used = rc().submit_no;
                st.bytes_tex += total;
                ++st.textures;
            }
            // D1_NG_LOG_RELOADS: small reloaded textures with their first values (diagnostics)
            static const bool log_reloads = std::getenv("D1_NG_LOG_RELOADS") != nullptr;
            if (log_reloads && out && prev && ts.width * ts.height <= 64 * 64) {
                const float* fv = reinterpret_cast<const float*>(ts.base);
                log("ng reload frame %llu sub %llu: %llx %ux%u fmt %u.%u | %g %g %g %g %g %g %g %g",
                    (unsigned long long)st.frames, (unsigned long long)rc().submit_no, (unsigned long long)ts.base, ts.width,
                    ts.height, ts.dfmt, ts.nfmt, fv[0], fv[1], fv[2], fv[3], fv[4], fv[5], fv[6], fv[7]);
            }
            // written while we copied (another thread is filling it): the copy may be torn
            if (out && !res && img->src_size && !dynamic_copy && opt.version(img->src_addr, img->src_size) != img->version) {
                ++st.tex_torn;
                if (prev && prev->torn < 2) {  // show the previous contents one more frame
                    prev->torn++, prev->checked = rc().submit_no, prev->last_used = rc().submit_no;
                    bury(std::move(img));
                    Image* keep = prev.get();
                    textures[key] = std::move(prev); ++views_gen;
                    return keep;
                }
                img->version = ~0ull;  // copy it again next frame
            }
            textures[key] = std::move(img); ++views_gen;
            if (!out) textures.erase(key);
        }
    }
    if (prev) bury(std::move(prev));
    if (!out) textures[key] = nullptr; ++views_gen;
    return out;
}

// Mip levels the game never wrote (all zero) while level 0 has data: the console fills them on
// the GPU (the 256x256 environment cube maps have only level 0 in memory), so sampling a
// coarser level here read black - the speckled snow, whose sparkle cube is blended by LOD.
// Rebuild them from the level above: 2x2 averages for 8-bit RGBA, every other block for BCn
// (point-sampled, but the right colours), every other texel otherwise.
// The first mip level the game never wrote (all zero) while level 0 has data, or sf.levels.
// Read from guest memory (the tiled bytes): a few spread samples per level decide quickly that
// a level has data; only levels whose samples are all zero are scanned in full (small ones) or
// taken as unwritten (large ones).
uint32_t Renderer::first_missing_mip(const fmt::TSharp& ts, const fmt::FormatInfo& fi, const tiling::Surface& sf, bool is3d) {
    if (sf.levels < 2 || is3d || !fi.bpp || fi.bpp % 8) return sf.levels;
    auto zero = [](const uint8_t* p, uint64_t n) {
        uint64_t acc = 0, i = 0;
        for (; i + 8 <= n; i += 8) {
            uint64_t v;
            std::memcpy(&v, p + i, 8);
            acc |= v;
        }
        for (; i < n; ++i) acc |= p[i];
        return acc == 0;
    };
    auto level_zero = [&](const uint8_t* p, uint64_t n) {
        if (n <= 4096) return zero(p, n);
        constexpr uint64_t kSamples = 32, kSpan = 64;
        for (uint64_t k = 0; k < kSamples; ++k) {
            const uint64_t at = (n - kSpan) * k / (kSamples - 1);
            if (!zero(p + at, kSpan)) return false;
        }
        return n > (256u << 10) || zero(p, n);
    };
    const uint8_t* guest = reinterpret_cast<const uint8_t*>(ts.base);
    if (level_zero(guest + sf.mips[0].offset, sf.mips[0].size)) return sf.levels;
    for (uint32_t lv = 1; lv < sf.levels; ++lv)
        if (level_zero(guest + sf.mips[lv].offset, sf.mips[lv].size)) return lv;
    return sf.levels;
}

// Mip levels the game never wrote (all zero) while level 0 has data: the console fills them on
// the GPU (the 256x256 environment cube maps have only level 0 in memory), so sampling a
// coarser level here read black - the speckled snow, whose sparkle cube is blended by LOD.
// Rebuild levels first.. from the level above (in cached memory): 2x2 averages for 8-bit RGBA,
// every other block for BCn (point-sampled, but the right colours), every other texel otherwise.
void Renderer::fill_missing_mips(uint32_t first, uint8_t* staging, const std::vector<uint64_t>& off, const std::vector<uint64_t>& sizes,
                                 const fmt::TSharp& ts, const fmt::FormatInfo& fi, const tiling::Surface& sf, bool is3d) {
    if (first < 1 || first >= sf.levels) return;
    const uint32_t bs = fi.bpp / 8;
    const bool rgba8 = !fi.block && fi.bpp == 32;
    for (uint32_t lv = first; lv < sf.levels; ++lv) {
        const uint32_t sw = std::max(1u, ts.width >> (lv - 1)), sh = std::max(1u, ts.height >> (lv - 1));
        const uint32_t dw = std::max(1u, ts.width >> lv), dh = std::max(1u, ts.height >> lv);
        const uint32_t sew = fi.block ? (sw + 3) / 4 : sw, seh = fi.block ? (sh + 3) / 4 : sh;
        const uint32_t dew = fi.block ? (dw + 3) / 4 : dw, deh = fi.block ? (dh + 3) / 4 : dh;
        for (uint32_t layer = 0; layer < sf.layers; ++layer) {
            const uint8_t* src = staging + off[lv - 1] + uint64_t(layer) * sew * seh * bs;
            uint8_t* dst = staging + off[lv] + uint64_t(layer) * dew * deh * bs;
            for (uint32_t y = 0; y < deh; ++y)
                for (uint32_t x = 0; x < dew; ++x) {
                    const uint32_t x0 = std::min(2 * x, sew - 1), y0 = std::min(2 * y, seh - 1);
                    uint8_t* d = dst + (uint64_t(y) * dew + x) * bs;
                    if (rgba8) {
                        const uint32_t x1 = std::min(x0 + 1, sew - 1), y1 = std::min(y0 + 1, seh - 1);
                        const uint8_t* a = src + (uint64_t(y0) * sew + x0) * 4;
                        const uint8_t* b = src + (uint64_t(y0) * sew + x1) * 4;
                        const uint8_t* c = src + (uint64_t(y1) * sew + x0) * 4;
                        const uint8_t* e = src + (uint64_t(y1) * sew + x1) * 4;
                        for (int k = 0; k < 4; ++k) d[k] = uint8_t((a[k] + b[k] + c[k] + e[k] + 2) / 4);
                    } else {
                        std::memcpy(d, src + (uint64_t(y0) * sew + x0) * bs, bs);
                    }
                }
        }
    }
    ++st.mips_filled;
}

// ---------------------------------------------------------------------------- geometry cache
bool Renderer::geo_alloc(uint64_t size, int& block, uint64_t& off) {
    std::lock_guard lk(geo_block_m);
    size = (size + 255) & ~255ull;
    for (int pass = 0; pass < 2; ++pass) {
        for (size_t b = 0; b < geo_blocks.size(); ++b)
            for (auto it = geo_blocks[b].free.begin(); it != geo_blocks[b].free.end(); ++it)
                if (it->second >= size) {
                    block = int(b), off = it->first;
                    const uint64_t rest = it->second - size;
                    geo_blocks[b].free.erase(it);
                    if (rest) geo_blocks[b].free[off + size] = rest;
                    geo_bytes += size;
                    return true;
                }
        static const size_t max_blocks = [] {
            const char* v = std::getenv("D1_NG_GEO_MB");  // geometry cache budget (default 1 GiB)
            return size_t(std::max<long long>(1, (v ? std::atoll(v) : 1024) / 64));
        }();
        if (geo_blocks.capacity() < max_blocks) geo_blocks.reserve(max_blocks);  // (first call, before any reader)
        if (pass || geo_blocks.size() >= max_blocks) return false;
        // a new 64 MiB block: host-visible (device-local too where the GPU offers it)
        GeoBlock nb;
        nb.buf.size = 64ull << 20;
        VkBufferCreateInfo bci{VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
        bci.size = nb.buf.size;
        bci.usage = VK_BUFFER_USAGE_VERTEX_BUFFER_BIT | VK_BUFFER_USAGE_INDEX_BUFFER_BIT;
        if (vkCreateBuffer(ctx.device, &bci, nullptr, &nb.buf.buf) != VK_SUCCESS) return false;
        VkMemoryRequirements req;
        vkGetBufferMemoryRequirements(ctx.device, nb.buf.buf, &req);
        const VkMemoryPropertyFlags host = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT;
        nb.buf.mem = alloc(req, host | VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
        if (!nb.buf.mem) {
            VkMemoryAllocateInfo ai{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
            ai.allocationSize = req.size;
            ai.memoryTypeIndex = find_memory_type(ctx, req.memoryTypeBits, host);
            if (ai.memoryTypeIndex == UINT32_MAX || vkAllocateMemory(ctx.device, &ai, nullptr, &nb.buf.mem) != VK_SUCCESS)
                nb.buf.mem = VK_NULL_HANDLE;
        }
        // alloc() falls back to any memory type: make sure this one can be mapped
        void* map = nullptr;
        if (!nb.buf.mem || vkBindBufferMemory(ctx.device, nb.buf.buf, nb.buf.mem, 0) != VK_SUCCESS ||
            vkMapMemory(ctx.device, nb.buf.mem, 0, VK_WHOLE_SIZE, 0, &map) != VK_SUCCESS) {
            free_buffer(nb.buf);
            return false;
        }
        nb.buf.map = static_cast<uint8_t*>(map);
        nb.free[0] = nb.buf.size;
        geo_blocks.push_back(std::move(nb));
    }
    return false;
}

void Renderer::geo_free_now(int block, uint64_t off, uint64_t size) {
    std::lock_guard lk(geo_block_m);
    size = (size + 255) & ~255ull;
    geo_bytes -= size;
    auto& fr = geo_blocks[size_t(block)].free;
    auto next = fr.lower_bound(off);
    if (next != fr.end() && next->first == off + size) {
        size += next->second;
        next = fr.erase(next);
    }
    if (next != fr.begin()) {
        auto prev = std::prev(next);
        if (prev->first + prev->second == off) {
            off = prev->first, size += prev->second;
            fr.erase(prev);
        }
    }
    fr[off] = size;
}

// After the submissions that may read the region have completed.
void Renderer::geo_free_later(int block, uint64_t off, uint64_t size) {
    std::lock_guard lk(grave_m);
    grave.push_back({submit_seq.load(), nullptr, {uint64_t(block), off, size}});
}

// A GPU copy of guest memory [addr, addr+size), valid for this submission, or null (then the
// caller copies into the ring). Buffers the game keeps rewriting are not cached for a while.
bool Renderer::geo_get(uint64_t addr, uint64_t size, int index_size, uint32_t index_count, GeoHit& hit, uint64_t res, uint64_t rbase) {
    GeoEntry* ep = geo_lookup(addr, size, index_size, index_count, res, rbase);
    return ep != nullptr && (hit = geo_hit_out, true);
}

// An engine resource's bytes [addr, addr + size): kept while the resource's epoch is unchanged
// (the engine only changes them with an event: bind, move, release), compared once after an
// event (a move keeps the contents), never write-tracked. Keyed by the resource and the offset
// in it, so a move does not make a new entry.
GeoEntry* Renderer::geo_lookup_res(uint64_t addr, uint64_t size, int index_size, uint32_t index_count, uint64_t res, uint64_t rbase) {
    const uint64_t key = (mix(mix(res >> 32, addr - rbase), size) | 1ull << 63);
    GeoShard& sh = geo_shards[(key * 0x9E3779B97F4A7C15ull) >> 58];
    std::unique_lock shard_lock(sh.m);
    GeoEntry& e = sh.map[key];
    e.last_used = submit_seq.load(std::memory_order_relaxed);
    const uint64_t ext = guest_region_extent(addr);
    if (!ext || ext < size) return nullptr;
    if (e.valid) {
        if (e.res == res) {
            __atomic_fetch_add(&st.geo_hits, 1, __ATOMIC_RELAXED);
            __atomic_fetch_add(&st.geo_res_hits, 1, __ATOMIC_RELAXED);
            geo_hit_out = {geo_blocks[size_t(e.block)].buf.buf, e.off, e.size, e.vfirst, e.vlast};
            return &e;
        }
        if (e.size == size && hash_bytes(reinterpret_cast<const void*>(addr), size) == e.hash) {  // moved
            e.res = res;
            __atomic_fetch_add(&st.geo_res_moves, 1, __ATOMIC_RELAXED);
            geo_hit_out = {geo_blocks[size_t(e.block)].buf.buf, e.off, e.size, e.vfirst, e.vlast};
            return &e;
        }
        __atomic_fetch_add(&st.geo_res_changed, 1, __ATOMIC_RELAXED);
        geo_free_later(e.block, e.off, e.size);
        e.valid = false;
    }
    if (!geo_alloc(size, e.block, e.off)) return nullptr;
    e.size = size;
    uint8_t* dst = geo_blocks[size_t(e.block)].buf.map + e.off;
    std::memcpy(dst, reinterpret_cast<const void*>(addr), size);
    __atomic_fetch_add(&st.bytes_geo, size, __ATOMIC_RELAXED);
    e.hash = hash_bytes(reinterpret_cast<const void*>(addr), size);  // (of guest memory: compared after a move)
    if (index_size) {  // the vertex range the indices reference
        uint32_t lo = UINT32_MAX, hi = 0;
        if (index_size == 4) {
            const uint32_t* ix = reinterpret_cast<const uint32_t*>(dst);
            for (uint32_t i = 0; i < index_count; ++i)
                if (ix[i] != 0xFFFFFFFFu) lo = std::min(lo, ix[i]), hi = std::max(hi, ix[i]);
        } else {
            const uint16_t* ix = reinterpret_cast<const uint16_t*>(dst);
            for (uint32_t i = 0; i < index_count; ++i)
                if (ix[i] != 0xFFFF) lo = std::min<uint32_t>(lo, ix[i]), hi = std::max<uint32_t>(hi, ix[i]);
        }
        if (lo > hi) lo = hi = 0;
        e.vfirst = lo, e.vlast = hi;
    }
    e.res = res, e.uploaded = e.last_used, e.valid = true;
    geo_hit_out = {geo_blocks[size_t(e.block)].buf.buf, e.off, e.size, e.vfirst, e.vlast};
    return &e;
}

GeoEntry* Renderer::geo_lookup(uint64_t addr, uint64_t size, int index_size, uint32_t index_count, uint64_t res, uint64_t rbase) {
    if (addr < 0x10000 || !size || size >= (64ull << 20) || (debug_toggles() & 8)) return nullptr;
    if (res && addr >= rbase) return geo_lookup_res(addr, size, index_size, index_count, res, rbase);
    if (!opt.watch || !opt.version || size >= (16ull << 20)) return nullptr;
    __atomic_fetch_add(&st.unreg_geo, 1, __ATOMIC_RELAXED);
    __atomic_fetch_add(&st.unreg_geo_bytes, size, __ATOMIC_RELAXED);
    const uint64_t key = addr | size << 40;  // exact: addr < 2^40, size <= 16 MiB
    GeoShard& sh = geo_shards[(key * 0x9E3779B97F4A7C15ull) >> 58];
    std::unique_lock shard_lock(sh.m);
    GeoEntry& e = sh.map[key];
    e.last_used = rc().submit_no;
    if (e.volatile_until > rc().submit_no) return nullptr;
    // D1_NG_GEO_VERIFY: (diagnostics) compare every cache hit with guest memory, log differences
    static const bool verify = std::getenv("D1_NG_GEO_VERIFY") != nullptr;
    auto verified = [&](const char* how) {
        if (verify && std::memcmp(geo_blocks[size_t(e.block)].buf.map + e.off, reinterpret_cast<const void*>(addr), size) != 0) {
            __atomic_fetch_add(&st.geo_stale, 1, __ATOMIC_RELAXED);
            static int n = 0;
            if (n++ < 200) {
                const uint8_t* a = geo_blocks[size_t(e.block)].buf.map + e.off;
                const uint8_t* b = reinterpret_cast<const uint8_t*>(addr);
                uint64_t first = 0, diff = 0;
                for (uint64_t i = 0; i < size; ++i)
                    if (a[i] != b[i]) first = diff++ ? first : i;
                const uint64_t hg = hash_bytes(b, size), hc = hash_bytes(a, size);
                if (n < 6) {
                    std::string ga, ca;
                    for (uint64_t i = 0; i < std::min<uint64_t>(size, 32); ++i) {
                        char t[4];
                        std::snprintf(t, sizeof t, "%02x", b[i]);
                        ga += t;
                        std::snprintf(t, sizeof t, "%02x", a[i]);
                        ca += t;
                    }
                    char ds[256] = "";
                    if (opt.describe) opt.describe(addr, ds, sizeof ds);
                    log("ng geo stale bytes: guest %s | copy %s | hashes guest %llx copy %llx stored %llx, block %d off %llx | page: %s",
                        ga.c_str(), ca.c_str(), (unsigned long long)hg, (unsigned long long)hc, (unsigned long long)e.hash, e.block,
                        (unsigned long long)e.off, ds);
                }
                log("ng geo stale (%s, %s): %llx +%llu, %llu bytes differ from +%llu; version now %llx, cached %llx, uploaded at submission %llu, now %llu",
                    how, hg == e.hash ? "OUR COPY CHANGED" : hc == e.hash ? "guest changed" : "both changed", (unsigned long long)addr, (unsigned long long)size, (unsigned long long)diff, (unsigned long long)first,
                    (unsigned long long)opt.version(addr, size), (unsigned long long)e.version, (unsigned long long)e.uploaded,
                    (unsigned long long)rc().submit_no);
            }
        }
        __atomic_fetch_add(&st.geo_hits, 1, __ATOMIC_RELAXED);
        geo_hit_out = {geo_blocks[size_t(e.block)].buf.buf, e.off, e.size, e.vfirst, e.vlast};
        return &e;
    };
    if (e.valid) {
        // buffers that never changed are checked once per frame, the others every submission
        if (e.checked == rc().submit_no) return verified("checked this submission");
        if (e.misses == 0 && e.checked_frame == st.frames + 1) return verified("checked this frame");
        if (opt.version(addr, size) == e.version) {
            e.checked = rc().submit_no, e.checked_frame = st.frames + 1;
            return verified("same version");
        }
        // written since the copy: drop it; rewritten soon after every upload = dynamic data
        geo_free_later(e.block, e.off, e.size);
        e.valid = false;
        e.misses = rc().submit_no - e.uploaded < 400 ? e.misses + 1 : 0;
        if (e.misses >= 3) {
            e.volatile_until = rc().submit_no + 4000, e.misses = 0;
            return nullptr;
        }
    }
    const uint64_t ext = guest_region_extent(addr);
    if (!ext || ext < size) return nullptr;
    const uint64_t ver = opt.watch(addr, size);
    if (ver == ~0ull) return nullptr;
    if (!geo_alloc(size, e.block, e.off)) return nullptr;
    e.size = size;
    uint8_t* dst = geo_blocks[size_t(e.block)].buf.map + e.off;
    std::memcpy(dst, reinterpret_cast<const void*>(addr), size);
    __atomic_fetch_add(&st.bytes_geo, size, __ATOMIC_RELAXED);
    if (opt.version(addr, size) != ver) {  // written while copying: use the ring this time
        __atomic_fetch_add(&st.geo_torn, 1, __ATOMIC_RELAXED);
        geo_free_later(e.block, e.off, size);
        e.valid = false, ++e.misses, e.uploaded = rc().submit_no;
        return nullptr;
    }
    if (index_size) {  // the vertex range the indices reference
        uint32_t lo = UINT32_MAX, hi = 0;
        if (index_size == 4) {
            const uint32_t* ix = reinterpret_cast<const uint32_t*>(dst);
            for (uint32_t i = 0; i < index_count; ++i)
                if (ix[i] != 0xFFFFFFFFu) lo = std::min(lo, ix[i]), hi = std::max(hi, ix[i]);
        } else {
            const uint16_t* ix = reinterpret_cast<const uint16_t*>(dst);
            for (uint32_t i = 0; i < index_count; ++i)
                if (ix[i] != 0xFFFF) lo = std::min<uint32_t>(lo, ix[i]), hi = std::max<uint32_t>(hi, ix[i]);
        }
        if (lo > hi) lo = hi = 0;
        e.vfirst = lo, e.vlast = hi;
    }
    if (verify) e.hash = hash_bytes(dst, size);
    e.version = ver, e.checked = rc().submit_no, e.checked_frame = st.frames + 1, e.uploaded = rc().submit_no, e.valid = true;
    geo_hit_out = {geo_blocks[size_t(e.block)].buf.buf, e.off, e.size, e.vfirst, e.vlast};
    return &e;
}

thread_local Renderer::GeoHit Renderer::geo_hit_out;
thread_local Renderer::Recorder* Renderer::tr = nullptr;

void Renderer::evict_geo() {
    const uint64_t horizon = 3000, now = submit_seq.load();
    if (now < horizon) return;
    for (GeoShard& sh : geo_shards) {
        std::lock_guard lk(sh.m);
        for (auto it = sh.map.begin(); it != sh.map.end();) {
            if (it->second.last_used + horizon < now) {
                if (it->second.valid) geo_free_later(it->second.block, it->second.off, it->second.size);
                it = sh.map.erase(it);
            } else {
                ++it;
            }
        }
    }
}

// Textures unused for a while are dropped (re-uploaded if the game uses them again): the
// game streams, and an address range can hold many textures over a session. The image is
// destroyed once the submissions that may still read it have completed.
void Renderer::evict_textures() {
    const uint64_t horizon = 2000, now = submit_seq.load();  // recordings (several per frame)
    if (now < horizon) return;
    std::vector<uint64_t> drop;
    for (auto& [k, img] : textures)
        if (img && img->last_used + horizon < now) drop.push_back(k);
    for (uint64_t k : drop) {
        auto it = textures.find(k);
        bury(std::move(it->second));  // (freed once every recording that may use it has completed)
        textures.erase(it); ++views_gen;
    }
    if (!drop.empty()) st.evicted += drop.size();
}

// The render target a T# reads: the image last drawn into at that address, unless another
// image there has the T#'s size (the game reuses transient memory for targets of different
// sizes within a frame; a T# made for one of them must not see another).
Image* Renderer::target_for(const fmt::TSharp& ts) {
    auto rt = target_by_base.find(ts.base);
    if (rt == target_by_base.end()) return nullptr;
    Image* img = rt->second;
    if (img->w == ts.width && img->h == ts.height) return img;
    Image* best = nullptr;
    if (auto it = images_by_base.find(ts.base); it != images_by_base.end())
        for (Image* c : it->second)
            if (c->w == ts.width && c->h == ts.height && (!best || c->bound_serial > best->bound_serial)) best = c;
    return best ? best : img;
}

thread_local Image* tv_texture = nullptr;  // (texture_view: the uploaded texture it returned a view of, if any)
VkImageView Renderer::texture_view(const uint32_t* t, gcn::TexDim dim, uint64_t res) {
    tv_texture = nullptr;
    const auto vt = view_type(dim);
    if (!t) return view(dummy[int(dim)].get(), vt, {}, 0, false);
    const auto ts = fmt::decode_tsharp(t);
    VkComponentMapping comp{swz(ts.dst_sel & 7), swz(ts.dst_sel >> 3 & 7), swz(ts.dst_sel >> 6 & 7),
                            swz(ts.dst_sel >> 9 & 7)};
    if (auto sit = stencil_by_base.find(ts.base); sit != stencil_by_base.end() && sit->second->stencil) {
        sit->second->sampled = true;
        sampled_bases.insert(ts.base);
        static std::unordered_set<uint64_t> told;
        if (told.size() < 32 && told.insert(ts.base).second)
            log("native renderer: texture %llx is the stencil of depth target %llx", (unsigned long long)ts.base,
                (unsigned long long)sit->second->base);
        return view(sit->second, VK_IMAGE_VIEW_TYPE_2D, {}, 0, true, true);
    }
    if (Image* img = target_for(ts)) {
        img->sampled = true;
        sampled_bases.insert(ts.base);
        if (img->depth) return view(img, VK_IMAGE_VIEW_TYPE_2D, {}, 0, true);
        // the render target stored shader component k in memory channel swap(k); our image
        // holds shader components, so map the T#'s memory channels back
        if (img->swap == 1) {
            auto back = [](VkComponentSwizzle s) {
                return s == VK_COMPONENT_SWIZZLE_R ? VK_COMPONENT_SWIZZLE_B : s == VK_COMPONENT_SWIZZLE_B ? VK_COMPONENT_SWIZZLE_R : s;
            };
            comp = {back(comp.r), back(comp.g), back(comp.b), back(comp.a)};
        }
        return view(img, img->is3d ? VK_IMAGE_VIEW_TYPE_3D : VK_IMAGE_VIEW_TYPE_2D, comp, 0, false);
    }
    auto it = textures.find(tex_key(t, res));
    Image* img = it != textures.end() ? it->second.get() : nullptr;
    if (!img) return view(dummy[int(dim)].get(), vt, {}, 0, false);
    img->last_used = rc().submit_no;
    tv_texture = img;
    // MIN_LOD: the streaming system has not loaded the finer mips yet (their memory is still
    // zero): start the view at the first mip it allows
    const uint32_t first = std::min(std::max(ts.base_level, (ts.min_lod + 255) >> 8), std::max(ts.last_level, ts.base_level));
    return view(img, vt, comp, first, false);
}

VkSampler Renderer::sampler(const uint32_t* s) {
    if (!s) return dummy_sampler;
    const uint64_t key = hash_bytes(s, 16);
    auto it = samplers.find(key);
    if (it != samplers.end()) return it->second;
    VkSamplerCreateInfo sci{VK_STRUCTURE_TYPE_SAMPLER_CREATE_INFO};
    sci.addressModeU = address_mode(s[0] & 7);
    sci.addressModeV = address_mode(s[0] >> 3 & 7);
    sci.addressModeW = address_mode(s[0] >> 6 & 7);
    const uint32_t aniso = s[0] >> 9 & 7, cmp = s[0] >> 12 & 7;
    sci.unnormalizedCoordinates = VK_FALSE;
    sci.minLod = float(s[1] & 0xFFF) / 256.0f;
    sci.maxLod = float(s[1] >> 12 & 0xFFF) / 256.0f;
    int32_t bias = int32_t(s[2] & 0x3FFF);
    if (bias & 0x2000) bias -= 0x4000;
    sci.mipLodBias = float(bias) / 256.0f;
    const uint32_t mag = s[2] >> 20 & 3, min = s[2] >> 22 & 3, mip = s[2] >> 26 & 3;
    sci.magFilter = mag == 0 ? VK_FILTER_NEAREST : VK_FILTER_LINEAR;
    sci.minFilter = min == 0 ? VK_FILTER_NEAREST : VK_FILTER_LINEAR;
    sci.mipmapMode = mip == 2 ? VK_SAMPLER_MIPMAP_MODE_LINEAR : VK_SAMPLER_MIPMAP_MODE_NEAREST;
    if (mip == 0) sci.maxLod = sci.minLod;  // no mipmapping
    if (sci.maxLod < sci.minLod) sci.maxLod = sci.minLod;
    if (cmp) {
        sci.compareEnable = VK_TRUE;
        sci.compareOp = VkCompareOp(cmp);
    }
    (void)aniso;
    const uint32_t border = s[3] >> 30;
    sci.borderColor = border == 1 ? VK_BORDER_COLOR_FLOAT_OPAQUE_BLACK
                    : border == 2 ? VK_BORDER_COLOR_FLOAT_OPAQUE_WHITE
                                  : VK_BORDER_COLOR_FLOAT_TRANSPARENT_BLACK;
    VkSampler smp = VK_NULL_HANDLE;
    vkCreateSampler(ctx.device, &sci, nullptr, &smp);
    samplers[key] = smp;
    return smp;
}

Shader* Renderer::shader(const Draw& dr, bool vs, const gcn::TexDim* dims, const uint8_t* kinds, uint32_t uint_in,
                         uint32_t sint_in, uint32_t scaled_in) {
    const uint8_t* obj = vs ? dr.vs : dr.ps;
    uint64_t key = mix(mix(uint64_t(obj), vs), hash_bytes(dims, 16 * sizeof(gcn::TexDim)));
    key = mix(mix(key, hash_bytes(kinds, 16)), uint64_t(uint_in) | uint64_t(sint_in) << 32);
    if (scaled_in) key = mix(key, scaled_in);
    if (!vs) key = mix(key, uint64_t(dr.vs));  // the input mapping depends on the VS
    auto it = shaders.find(key);
    if (it != shaders.end()) return it->second.get();
    auto sh = std::make_unique<Shader>();
    const GnmShader g = parse_shader(obj, vs);
    gcn::ShaderDesc d;
    d.stage = vs ? gcn::Stage::Vertex : gcn::Stage::Pixel;
    d.id = uint64_t(obj);
    d.code = g.code, d.code_size = g.code_size, d.slots = g.slots, d.user_sgprs = g.user_sgprs;
    d.ps_input_addr = g.ps_input_addr, d.fetch = g.fetch, d.fetch_size = g.fetch_size;
    for (int i = 0; i < 16; ++i) d.tex_dims[i] = dims[i], d.tex_kind[i] = kinds[i];
    d.uint_inputs = uint_in, d.sint_inputs = sint_in, d.scaled_inputs = scaled_in;
    if (!vs) {
        const GnmShader v = parse_shader(dr.vs, true);
        d.remap_inputs = true;
        std::memset(d.input_location, 0xFF, sizeof d.input_location);
        for (size_t i = 0; i < g.semantics.size() && i < 32; ++i)
            for (uint16_t e : v.semantics)
                if ((e & 0xFF) == (g.semantics[i] & 0xFF)) d.input_location[i] = uint8_t(e >> 8 & 0x1F);
    }
    if (const char* dir = std::getenv("D1_NG_DUMP_GCN"); dir && g.code && g.code_size) {  // for d1-shadertool dis
        char path[512];
        std::snprintf(path, sizeof path, "%s/%s_%p.code", dir, vs ? "vs" : "ps", (const void*)obj);
        if (FILE* f = std::fopen(path, "wb")) std::fwrite(g.code, 1, g.code_size, f), std::fclose(f);
        if (g.fetch && g.fetch_size) {
            std::snprintf(path, sizeof path, "%s/%s_%p.fetch", dir, vs ? "vs" : "ps", (const void*)obj);
            if (FILE* f = std::fopen(path, "wb")) std::fwrite(g.fetch, 1, g.fetch_size, f), std::fclose(f);
        }
    }
    if (g.code && g.code_size) {
        sh->res = gcn::translate(d);
        if (const char* dir = std::getenv("D1_NG_DUMP_SPV")) {  // every translated shader, for spirv-val
            static int n = 0;
            char path[512];
            std::snprintf(path, sizeof path, "%s/%04d_%s_%p.spv", dir, n++, vs ? "vs" : "ps", (const void*)obj);
            if (FILE* f = std::fopen(path, "wb")) {
                std::fwrite(sh->res.spirv.data(), 4, sh->res.spirv.size(), f);
                std::fclose(f);
            }
        }
        VkShaderModuleCreateInfo mci{VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};
        mci.codeSize = sh->res.spirv.size() * 4;
        mci.pCode = sh->res.spirv.data();
        sh->ok = !sh->res.spirv.empty() && vkCreateShaderModule(ctx.device, &mci, nullptr, &sh->module) == VK_SUCCESS;
        if (!sh->res.problems.empty() && sh->ok) {
            static int logged = 0;
            if (logged++ < 20)
                log("native renderer: %s shader %p: %s", vs ? "vertex" : "pixel", (const void*)obj,
                    sh->res.problems[0].c_str());
        }
    }
    ++st.shaders;
    if (!sh->ok) ++st.bad_shaders;
    Shader* out = sh.get();
    shaders[key] = std::move(sh);
    return out;
}

uint32_t topology_of(uint32_t prim, VkPrimitiveTopology& t) {
    switch (prim) {
    case 1: t = VK_PRIMITIVE_TOPOLOGY_POINT_LIST; return 1;
    case 2: t = VK_PRIMITIVE_TOPOLOGY_LINE_LIST; return 1;
    case 3: t = VK_PRIMITIVE_TOPOLOGY_LINE_STRIP; return 1;
    case 4: t = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST; return 1;
    case 5: t = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_FAN; return 1;
    case 6: t = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP; return 1;
    case 0x11: t = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST; return 3;  // rect list: geometry shader
    case 0x13: t = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST; return 2;  // quad list: indices rebuilt
    default: return 0;
    }
}

gcn::TexDim slot_dim(const uint32_t* t) {
    return t ? tex_dim(fmt::decode_tsharp(t).type) : gcn::TexDim::Tex2D;
}

// Memoized: a draw's pipeline depends only on its shaders, primitive, render state, vertex
// formats, target formats and its T#s' type / format / address (and what render target an
// address is) - hashed here in far less time than resolving them again for every draw.
uint64_t Renderer::pipe_key(const Draw& dr, Image* const* colors, Image* depth, bool& ambiguous) const {
    uint64_t k = mix(mix(uint64_t(dr.vs), uint64_t(dr.ps)), uint64_t(dr.prim) | uint64_t(dr.tex_mask[0]) << 8 | uint64_t(dr.tex_mask[1]) << 24);
    k = mix(mix(k, uint64_t(dr.blend) | uint64_t(dr.target_mask) << 32), uint64_t(dr.su_sc_mode) | uint64_t(dr.depth_ctl) << 32);
    k = mix(k, dr.stencil_ctl);
    for (int i = 0; i < 8; ++i) k = mix(k, uint64_t(colors[i]));
    k = mix(k, uint64_t(depth));
    for (int i = 0; i < 16; ++i) k = mix(k, uint64_t(dr.vb[i][1] >> 16) | uint64_t(dr.vb[i][3]) << 32);
    const uint32_t na = amb_n.load(std::memory_order_acquire);
    ambiguous = na > kAmbMax;
    for (int s = 0; s < 2; ++s)
        for (uint32_t m = dr.tex_mask[s]; m; m &= m - 1) {
            const uint32_t* t = dr.tex[s][__builtin_ctz(m)];
            k = mix(mix(k, uint64_t(t[0]) | uint64_t(t[1]) << 32), uint64_t(t[2]) | uint64_t(t[3]) << 32);
            if (na && !ambiguous) {
                const uint64_t base = (uint64_t(t[0]) | uint64_t(t[1] & 0xFF) << 32) << 8;
                for (uint32_t i = 0; i < na; ++i)
                    if (amb_arr[i] == base) { ambiguous = true; break; }
            }
        }
    return k;
}

Pipeline* Renderer::pipeline(const Draw& dr, Image* const* colors, Image* depth) {
    uint64_t k = mix(mix(uint64_t(dr.vs), uint64_t(dr.ps)), uint64_t(dr.prim) | uint64_t(dr.tex_mask[0]) << 8 | uint64_t(dr.tex_mask[1]) << 24);
    k = mix(mix(k, uint64_t(dr.blend) | uint64_t(dr.target_mask) << 32), uint64_t(dr.su_sc_mode) | uint64_t(dr.depth_ctl) << 32);
    k = mix(k, dr.stencil_ctl);
    for (int i = 0; i < 8; ++i) k = mix(k, uint64_t(colors[i]));
    k = mix(k, uint64_t(depth));
    for (int i = 0; i < 16; ++i) k = mix(k, uint64_t(dr.vb[i][1] >> 16) | uint64_t(dr.vb[i][3]) << 32);
    for (int s = 0; s < 2; ++s)
        for (uint32_t m = dr.tex_mask[s]; m; m &= m - 1) {
            const uint32_t* t = dr.tex[s][__builtin_ctz(m)];
            k = mix(mix(k, uint64_t(t[0]) | uint64_t(t[1]) << 32), uint64_t(t[2]) | uint64_t(t[3]) << 32);
            if (!ambiguous_bases.empty()) {
                const uint64_t base = (uint64_t(t[0]) | uint64_t(t[1] & 0xFF) << 32) << 8;
                if (std::binary_search(ambiguous_bases.begin(), ambiguous_bases.end(), base))
                    k = mix(k, target_attrs(target_for(fmt::decode_tsharp(t))));
            }
        }
    PipeMemo& e = pipe_memo[k & (pipe_memo.size() - 1)];
    if (e.key == k && e.gen == targets_gen) return ++st.memo_hits, e.p;
    ++st.memo_misses;
    if (e.key == k) ++st.memo_gen;
    Pipeline* p = pipeline_resolve(dr, colors, depth);
    e = {k, targets_gen, p};
    return p;
}

Pipeline* Renderer::pipeline_resolve(const Draw& dr, Image* const* colors, Image* depth) {
    // per texture slot: the image dimensionality (a T# on a render target samples our 2D
    // target image) and whether it is sampled with integer types
    gcn::TexDim dims[2][16];
    uint8_t kinds[2][16] = {};
    for (int s = 0; s < 2; ++s)
        for (int i = 0; i < 16; ++i) {
            const uint32_t* t = dr.T(s, i);
            dims[s][i] = slot_dim(t);
            if (!t) continue;
            const auto ts = fmt::decode_tsharp(t);
            if (ts.type == 11) {  // cube maps: what they are (diagnostics, once per address)
                static std::unordered_set<uint64_t> seen;
                if (seen.size() < 32 && seen.insert(ts.base).second) {
                    auto rt = target_by_base.find(ts.base);
                    log("native renderer: cube T# %llx %ux%u f%u.%u mips %u-%u arrays %u-%u tile %u%s",
                        (unsigned long long)ts.base, ts.width, ts.height, ts.dfmt, ts.nfmt, ts.base_level, ts.last_level,
                        ts.base_array, ts.last_array, ts.tiling, rt != target_by_base.end() ? " (a render target)" : "");
                    if (const char* dir = std::getenv("D1_NG_DUMP_TEX")) {
                        const auto fi0 = fmt::data_format(ts.dfmt);
                        tiling::Surface sf0;
                        sf0.tile_mode = ts.tiling, sf0.bpp = fi0.bpp, sf0.block = fi0.block, sf0.pow2 = ts.pow2;
                        sf0.width = ts.width, sf0.height = ts.height, sf0.pitch = ts.pitch, sf0.layers = 6;
                        sf0.levels = std::min(ts.last_level + 1, tiling::kMaxMips);
                        tiling::layout(sf0);
                        char path[512];
                        std::snprintf(path, sizeof path, "%s/cube_%llx.bin", dir, (unsigned long long)ts.base);
                        if (guest_region_extent(ts.base) >= sf0.total_size)
                            if (FILE* f = std::fopen(path, "wb")) {
                                std::fwrite(t, 4, 8, f);
                                std::fwrite(reinterpret_cast<const void*>(ts.base), 1, sf0.total_size, f);
                                std::fclose(f);
                            }
                    }
                }
            }
            if (Image* ri = target_for(ts)) {
                dims[s][i] = ri->is3d ? gcn::TexDim::Tex3D : gcn::TexDim::Tex2D;
                const VkFormat f = ri->format;
                kinds[s][i] = ri->depth || !is_int_format(f) ? 0 : is_sint_format(f) ? 2 : 1;
            } else {
                kinds[s][i] = ts.nfmt == 4 ? 1 : ts.nfmt == 5 ? 2 : 0;
            }
        }
    Shader* vs = shader(dr, true, dims[0], kinds[0]);
    // vertex inputs whose format comes from the V#: integer formats need integer inputs
    uint32_t uin = 0, sin = 0;
    for (const auto& a : vs->res.attribs)
        if (a.dfmt == 0xFF && a.location < 32) {
            const uint32_t nf = dr.vb[a.vb_slot & 15][3] >> 12 & 7;
            if (nf == 4) uin |= 1u << a.location;
            if (nf == 5) sin |= 1u << a.location;
        }
    // SCALED formats this GPU cannot read as vertex attributes: integer fetch + conversion
    uint32_t scl = 0;
    for (const auto& a : vs->res.attribs) {
        if (a.location >= 32) continue;
        const uint32_t* v = dr.vb[a.vb_slot & 15];
        const uint32_t df = a.dfmt == 0xFF ? (v[3] >> 15 & 0xF) : a.dfmt, nf = a.dfmt == 0xFF ? (v[3] >> 12 & 7) : a.nfmt;
        bool su, ss;
        vertex_format_here(df, nf, su, ss);
        if (su) uin |= 1u << a.location, scl |= 1u << a.location;
        if (ss) sin |= 1u << a.location, scl |= 1u << a.location;
    }
    if (uin | sin | scl) vs = shader(dr, true, dims[0], kinds[0], uin, sin, scl);
    Shader* ps = dr.ps ? shader(dr, false, dims[1], kinds[1]) : nullptr;  // no pixel shader: depth-only
    if (!vs->ok || (ps && !ps->ok)) return nullptr;
    VkPrimitiveTopology topo;
    if (!topology_of(dr.prim, topo)) return nullptr;
    // key
    uint64_t key = mix(mix(uint64_t(vs), uint64_t(ps)), topo);
    for (const auto& a : vs->res.attribs) {
        const uint32_t* v = dr.vb[a.vb_slot & 15];
        key = mix(key, (v[1] >> 16 & 0x3FFF) | uint64_t(v[3] >> 12 & 0x7F) << 16 | uint64_t(a.index_vgpr) << 24);
    }
    key = mix(key, dr.blend), key = mix(key, dr.target_mask), key = mix(key, dr.su_sc_mode);
    key = mix(key, dr.depth_ctl), key = mix(key, dr.stencil_ctl);
    for (int i = 0; i < 8; ++i) key = mix(key, colors[i] ? colors[i]->format : 0);
    key = mix(key, depth ? depth->format : 0);
    auto it = pipelines.find(key);
    if (it != pipelines.end()) return it->second->pipeline ? it->second.get() : nullptr;  // failed before

    auto p = std::make_unique<Pipeline>();
    p->vs = vs, p->ps = ps;
    // descriptor set layouts (push descriptors): set 0 vertex, set 1 pixel
    for (int s = 0; s < 2; ++s) {
        const Shader* sh = s ? ps : vs;
        std::vector<VkDescriptorSetLayoutBinding> b;
        if (sh) for (const auto& x : sh->res.bindings) {
            VkDescriptorSetLayoutBinding lb{};
            lb.binding = x.binding;
            lb.descriptorType = x.kind == gcn::Binding::Texture ? VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE
                              : x.kind == gcn::Binding::Sampler ? VK_DESCRIPTOR_TYPE_SAMPLER
                                                                : VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
            lb.descriptorCount = 1;
            lb.stageFlags = s ? VK_SHADER_STAGE_FRAGMENT_BIT : VK_SHADER_STAGE_VERTEX_BIT;
            b.push_back(lb);
        }
        VkDescriptorSetLayoutCreateInfo dci{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO};
        dci.bindingCount = uint32_t(b.size());
        dci.pBindings = b.data();
        // one push descriptor set per pipeline layout is allowed: the pixel shader's (the most
        // textures and samplers)
        if (s == 1 && push_fn && !b.empty() && b.size() <= max_push && b.size() <= 48) {
            dci.flags = VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR;
            p->push_ps = true;
        }
        vkCreateDescriptorSetLayout(ctx.device, &dci, nullptr, &p->sets[s]);
    }
    VkPipelineLayoutCreateInfo lci{VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO};
    lci.setLayoutCount = 2;
    lci.pSetLayouts = p->sets;
    vkCreatePipelineLayout(ctx.device, &lci, nullptr, &p->layout);

    VkPipelineShaderStageCreateInfo stages[3]{{VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO},
                                              {VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO},
                                              {VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO}};
    stages[0].stage = VK_SHADER_STAGE_VERTEX_BIT, stages[0].module = vs->module, stages[0].pName = "main";
    uint32_t nstages = 1;
    if (ps) {
        stages[1].stage = VK_SHADER_STAGE_FRAGMENT_BIT, stages[1].module = ps->module, stages[1].pName = "main";
        nstages = 2;
    }
    if (dr.prim == 0x11) {
        if (!vs->rect_gs) {
            const auto words = gcn::rect_list_gs(vs->res.param_exports);
            VkShaderModuleCreateInfo mci{VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};
            mci.codeSize = words.size() * 4;
            mci.pCode = words.data();
            vkCreateShaderModule(ctx.device, &mci, nullptr, &vs->rect_gs);
        }
        stages[nstages].stage = VK_SHADER_STAGE_GEOMETRY_BIT, stages[nstages].module = vs->rect_gs;
        stages[nstages].pName = "main";
        ++nstages;
    }

    std::vector<VkVertexInputBindingDescription> vbind;
    std::vector<VkVertexInputAttributeDescription> vattr;
    for (const auto& a : vs->res.attribs) {
        const uint32_t* v = dr.vb[a.vb_slot & 15];
        const uint32_t stride = v[1] >> 16 & 0x3FFF;
        uint32_t dfmt = a.dfmt, nfmt = a.nfmt;
        if (dfmt == 0xFF) dfmt = v[3] >> 15 & 0xF, nfmt = v[3] >> 12 & 7;
        bool su, ss;
        const VkFormat f = vertex_format_here(dfmt, nfmt, su, ss);
        if (std::none_of(vbind.begin(), vbind.end(), [&](auto& x) { return x.binding == a.vb_slot; }))
            vbind.push_back({a.vb_slot, stride, a.index_vgpr == 0 ? VK_VERTEX_INPUT_RATE_VERTEX : VK_VERTEX_INPUT_RATE_INSTANCE});
        vattr.push_back({a.location, a.vb_slot, f, a.offset});
    }
    VkPipelineVertexInputStateCreateInfo vi{VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO};
    vi.vertexBindingDescriptionCount = uint32_t(vbind.size());
    vi.pVertexBindingDescriptions = vbind.data();
    vi.vertexAttributeDescriptionCount = uint32_t(vattr.size());
    vi.pVertexAttributeDescriptions = vattr.data();
    VkPipelineInputAssemblyStateCreateInfo ia{VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO};
    ia.topology = topo;
    // strips are cut with the reset index (0xFFFF / 0xFFFFFFFF), as the engine sets up
    // VGT_MULTI_PRIM_IB_RESET_EN: without it the cut is drawn as a vertex far away (streaks)
    ia.primitiveRestartEnable = topo == VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP || topo == VK_PRIMITIVE_TOPOLOGY_LINE_STRIP ||
                                topo == VK_PRIMITIVE_TOPOLOGY_TRIANGLE_FAN;
    VkPipelineViewportStateCreateInfo vp{VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO};
    vp.viewportCount = vp.scissorCount = 1;
    VkPipelineRasterizationStateCreateInfo rs{VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO};
    rs.polygonMode = VK_POLYGON_MODE_FILL;
    rs.cullMode = opt.no_cull ? VK_CULL_MODE_NONE
                              : VkCullModeFlags((dr.su_sc_mode & 1 ? VK_CULL_MODE_FRONT_BIT : 0) |
                                                (dr.su_sc_mode & 2 ? VK_CULL_MODE_BACK_BIT : 0));
    rs.frontFace = (dr.su_sc_mode & 4) ? VK_FRONT_FACE_CLOCKWISE : VK_FRONT_FACE_COUNTER_CLOCKWISE;
    rs.depthBiasEnable = (dr.su_sc_mode >> 11 & 3) != 0;
    rs.lineWidth = 1.0f;
    VkPipelineMultisampleStateCreateInfo ms{VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO};
    ms.rasterizationSamples = VK_SAMPLE_COUNT_1_BIT;
    VkPipelineDepthStencilStateCreateInfo ds{VK_STRUCTURE_TYPE_PIPELINE_DEPTH_STENCIL_STATE_CREATE_INFO};
    if (depth) {
        ds.depthTestEnable = (dr.depth_ctl >> 1) & 1;
        ds.depthWriteEnable = (dr.depth_ctl >> 2) & 1;
        ds.depthCompareOp = VkCompareOp(dr.depth_ctl >> 4 & 7);
        ds.stencilTestEnable = depth->stencil && (dr.depth_ctl & 1);
        auto face = [&](uint32_t func, uint32_t ops) {
            VkStencilOpState s{};
            s.failOp = stencil_op(ops & 0xF);
            s.passOp = stencil_op(ops >> 4 & 0xF);
            s.depthFailOp = stencil_op(ops >> 8 & 0xF);
            s.compareOp = VkCompareOp(func & 7);
            s.compareMask = s.writeMask = 0xFF;
            return s;
        };
        ds.front = face(dr.depth_ctl >> 8, dr.stencil_ctl);
        ds.back = (dr.depth_ctl >> 7 & 1) ? face(dr.depth_ctl >> 20, dr.stencil_ctl >> 12) : ds.front;
    }
    VkPipelineColorBlendAttachmentState cb[8]{};
    VkFormat cfmt[8]{};
    uint32_t ncolor = 0;
    for (uint32_t i = 0; i < 8; ++i) {
        if (colors[i]) ncolor = i + 1;
        cfmt[i] = colors[i] ? colors[i]->format : VK_FORMAT_UNDEFINED;
        auto& a = cb[i];
        a.colorWriteMask = (dr.target_mask >> (4 * i)) & 0xF;
        if (i < 4 && (dr.blend >> 30 & 1) && colors[i] && !is_int_format(colors[i]->format)) {
            a.blendEnable = VK_TRUE;
            a.srcColorBlendFactor = blend_factor(dr.blend & 0x1F);
            a.colorBlendOp = blend_op(dr.blend >> 5 & 7);
            a.dstColorBlendFactor = blend_factor(dr.blend >> 8 & 0x1F);
            if (dr.blend >> 29 & 1) {
                a.srcAlphaBlendFactor = blend_factor(dr.blend >> 16 & 0x1F);
                a.alphaBlendOp = blend_op(dr.blend >> 21 & 7);
                a.dstAlphaBlendFactor = blend_factor(dr.blend >> 24 & 0x1F);
            } else {
                a.srcAlphaBlendFactor = a.srcColorBlendFactor;
                a.alphaBlendOp = a.colorBlendOp;
                a.dstAlphaBlendFactor = a.dstColorBlendFactor;
            }
        }
    }
    VkPipelineColorBlendStateCreateInfo cbs{VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO};
    cbs.attachmentCount = ncolor;
    cbs.pAttachments = cb;
    const VkDynamicState dyn[] = {VK_DYNAMIC_STATE_VIEWPORT, VK_DYNAMIC_STATE_SCISSOR, VK_DYNAMIC_STATE_STENCIL_REFERENCE,
                                  VK_DYNAMIC_STATE_STENCIL_COMPARE_MASK, VK_DYNAMIC_STATE_STENCIL_WRITE_MASK,
                                  VK_DYNAMIC_STATE_DEPTH_BIAS};
    VkPipelineDynamicStateCreateInfo dy{VK_STRUCTURE_TYPE_PIPELINE_DYNAMIC_STATE_CREATE_INFO};
    dy.dynamicStateCount = 6;
    dy.pDynamicStates = dyn;
    VkPipelineRenderingCreateInfo rci{VK_STRUCTURE_TYPE_PIPELINE_RENDERING_CREATE_INFO};
    rci.colorAttachmentCount = ncolor;
    rci.pColorAttachmentFormats = cfmt;
    rci.depthAttachmentFormat = depth ? depth->format : VK_FORMAT_UNDEFINED;
    rci.stencilAttachmentFormat = depth && depth->stencil ? depth->format : VK_FORMAT_UNDEFINED;
    VkGraphicsPipelineCreateInfo gci{VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO, &rci};
    gci.stageCount = nstages;
    gci.pStages = stages;
    gci.pVertexInputState = &vi;
    gci.pInputAssemblyState = &ia;
    gci.pViewportState = &vp;
    gci.pRasterizationState = &rs;
    gci.pMultisampleState = &ms;
    gci.pDepthStencilState = &ds;
    gci.pColorBlendState = &cbs;
    gci.pDynamicState = &dy;
    gci.layout = p->layout;
    if (const VkResult r = vkCreateGraphicsPipelines(ctx.device, pcache, 1, &gci, nullptr, &p->pipeline); r != VK_SUCCESS) {
        p->pipeline = VK_NULL_HANDLE;
        static int logged = 0;
        if (logged++ < 20)
            log("native renderer: pipeline creation failed (%d): vs %p ps %p prim %u, %zu vertex inputs, %u colour targets",
                int(r), (const void*)dr.vs, (const void*)dr.ps, dr.prim, vattr.size(), ncolor);
        if (const char* dir = std::getenv("D1_NG_DUMP_FAILED")) {  // the SPIR-V, for spirv-val
            char path[512];
            for (int k = 0; k < 2; ++k) {
                const Shader* sh = k ? ps : vs;
                if (!sh) continue;
                std::snprintf(path, sizeof path, "%s/%s_%p.spv", dir, k ? "ps" : "vs", (const void*)(k ? dr.ps : dr.vs));
                if (FILE* f = std::fopen(path, "wb")) {
                    std::fwrite(sh->res.spirv.data(), 4, sh->res.spirv.size(), f);
                    std::fclose(f);
                }
            }
        }
    }
    ++st.pipelines;
    Pipeline* out = p.get();
    pipelines[key] = std::move(p);
    return out->pipeline ? out : nullptr;
}

void Renderer::end_pass() {
    if (!rc().in_pass) return;
    if (rc().pass_secondary) {  // its query was begun outside the pass
        vkCmdEndRendering(rc().cmd);
        q_end();
    } else {
        q_end();
        vkCmdEndRendering(rc().cmd);
    }
    rc().in_pass = false, rc().pass_secondary = false;
    barrier();
}

// ---------------------------------------------------------------------------- parallel recording
void Renderer::start_workers() {
    for (uint32_t i = 0; i < rec_threads; ++i)
        wk.threads.emplace_back([this] {
            for (;;) {
                std::function<void()> job;
                {
                    std::unique_lock lk(wk.m);
                    wk.cv.wait(lk, [&] { return wk.quit || !wk.jobs.empty(); });
                    if (wk.quit) return;
                    job = std::move(wk.jobs.back());
                    wk.jobs.pop_back();
                }
                job();
                std::lock_guard lk(wk.m);
                if (--wk.pending == 0) wk.done_cv.notify_all();
            }
        });
}

// A secondary command buffer from worker slot `w`'s pool for the current submission (pools
// are per worker slot: command pools are not thread-safe; reset when the submission is reused).
VkCommandBuffer Renderer::secondary(uint32_t w) {
    Sub& sb = subs[rc().cur];
    auto& sc = sb.sec[w];
    if (!sc.pool) {
        VkCommandPoolCreateInfo pci{VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO};
        pci.queueFamilyIndex = ctx.queue_family;
        if (vkCreateCommandPool(ctx.device, &pci, nullptr, &sc.pool) != VK_SUCCESS) return VK_NULL_HANDLE;
    }
    if (sc.used == sc.cbs.size()) {
        VkCommandBufferAllocateInfo cai{VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};
        cai.commandPool = sc.pool;
        cai.level = VK_COMMAND_BUFFER_LEVEL_SECONDARY;
        cai.commandBufferCount = 1;
        VkCommandBuffer cb = VK_NULL_HANDLE;
        if (vkAllocateCommandBuffers(ctx.device, &cai, &cb) != VK_SUCCESS) return VK_NULL_HANDLE;
        sc.cbs.push_back(cb);
    }
    return sc.cbs[sc.used++];
}

// n plain draws with the same render targets: one render pass whose contents are secondary
// command buffers, each recorded by a thread (the workers and this one) from a contiguous
// slice, executed in order.
void Renderer::run_parallel(Draw* const* run, size_t n) {
    Image* colors[8] = {};
    for (int i = 0; i < 5; ++i) colors[i] = color_target(run[0]->color[i]);
    Image* depth = depth_target(run[0]->depth);
    if (!depth && std::none_of(colors, colors + 8, [](Image* x) { return x != nullptr; })) {
        for (size_t i = 0; i < n; ++i) skip("no target");
        return;
    }
    const uint32_t T = rec_threads + 1;
    Sub& sb = subs[rc().cur];
    if (sb.sec.size() < T) sb.sec.resize(T);
    // slices and their command buffers (allocated here: the pools belong to this thread's use)
    std::vector<VkCommandBuffer> cbs(T);
    for (uint32_t t = 0; t < T; ++t)
        if (!(cbs[t] = secondary(t))) {
            for (size_t i = 0; i < n; ++i) draw(*run[i]);
            return;
        }
    feedback_snapshots(run, n, colors, depth, true);
    begin_pass(colors, depth, true);
    rc().pass_secondary = true;
    VkFormat cfmt[8]{};
    uint32_t ncolor = 0;
    for (uint32_t i = 0; i < 8; ++i)
        if (colors[i]) cfmt[i] = colors[i]->format, ncolor = i + 1;
    VkCommandBufferInheritanceRenderingInfo iri{VK_STRUCTURE_TYPE_COMMAND_BUFFER_INHERITANCE_RENDERING_INFO};
    iri.colorAttachmentCount = ncolor;
    iri.pColorAttachmentFormats = cfmt;
    iri.depthAttachmentFormat = depth ? depth->format : VK_FORMAT_UNDEFINED;
    iri.stencilAttachmentFormat = depth && depth->stencil ? depth->format : VK_FORMAT_UNDEFINED;
    iri.rasterizationSamples = VK_SAMPLE_COUNT_1_BIT;
    VkCommandBufferInheritanceInfo ii{VK_STRUCTURE_TYPE_COMMAND_BUFFER_INHERITANCE_INFO, &iri};
    ii.occlusionQueryEnable = rc().q_active >= 0;
    ii.queryFlags = rc().q_active >= 0 && ctx.occlusion_precise ? VK_QUERY_CONTROL_PRECISE_BIT : 0;
    std::vector<Rec> recs(T);
    std::vector<DrawState> states(T);
    auto slice = [&](uint32_t t) {
        const size_t b = n * t / T, e = n * (t + 1) / T;
        Rec& r = recs[t];
        r.cmd = cbs[t], r.ds = &states[t], r.parallel = true;
        VkCommandBufferBeginInfo bi{VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
        bi.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT | VK_COMMAND_BUFFER_USAGE_RENDER_PASS_CONTINUE_BIT;
        bi.pInheritanceInfo = &ii;
        vkBeginCommandBuffer(r.cmd, &bi);
        for (size_t i = b; i < e; ++i) draw(*run[i], r, colors, depth);
        vkEndCommandBuffer(r.cmd);
    };
    {
        std::lock_guard lk(wk.m);
        for (uint32_t t = 1; t < T; ++t) wk.jobs.push_back([&slice, t] { slice(t); });
        wk.pending += T - 1;
    }
    wk.cv.notify_all();
    slice(0);
    {
        std::unique_lock lk(wk.m);
        wk.done_cv.wait(lk, [&] { return wk.pending == 0; });
    }
    vkCmdExecuteCommands(rc().cmd, T, cbs.data());
    for (const Rec& r : recs) merge(r);
    rc().dstate.valid = false;  // (the primary's bindings and dynamic state are undefined after secondaries)
    end_pass();
    ++par_runs, par_draws += n;
}

// GCN reads a render target that the same pass renders into from memory, as it was before the
// pass (the color / depth caches are not coherent with texture reads; the engine relies on
// it: decals and lighting sample the G-buffer and depth they draw into). In Vulkan that is a
// feedback loop with undefined results - garbage that changes every frame on real GPUs
// (Intel's compressed depth and color most of all). Such attachments are copied before the
// pass and the draws sample the copy.
// Each run of draws into the same targets passes here before it is recorded. A sampled
// attachment the run does not write is read in place (Vulkan allows reading an attachment
// that no command of the render pass instance writes; the pass is split when a later run
// writes it, or when an earlier one did). One the run writes too is copied first, and the
// draws read the copy.
void Renderer::feedback_snapshots(const Draw* const* run, size_t n, Image* const* colors, Image* depth, bool new_pass) {
    static const bool off = [] { const char* v = std::getenv("D1_NG_FEEDBACK_COPY"); return v && std::atoi(v) == 0; }();
    if (off) return;
    const uint32_t w = run_writes(run, n);
    auto writes = [&](Image* img) -> uint8_t {  // aspects (1 color / depth, 2 stencil) the run writes
        if (img && img == depth) return uint8_t((w >> 8 & 1) | (w >> 9 & 1) << 1);
        uint8_t r = 0;
        for (int i = 0; i < 8; ++i)
            if (img && colors[i] == img && (w >> i & 1)) r = 3;
        return r;
    };
    auto find = [](std::vector<std::pair<Image*, uint8_t>>& v, Image* img) -> uint8_t {
        for (auto& x : v)
            if (x.first == img) return x.second;
        return 0;
    };
    auto put = [](std::vector<std::pair<Image*, uint8_t>>& v, Image* img, uint8_t a) {
        if (!a) return;
        for (auto& x : v)
            if (x.first == img) { x.second |= a; return; }
        v.push_back({img, a});
    };
    struct Need { Image* img; uint8_t asp; };  // asp: 1 color / depth, 2 stencil
    std::vector<Need> need;
    auto add = [&](Image* img, uint8_t asp) {
        for (auto& x : need)
            if (x.img == img) { x.asp |= asp; return; }
        need.push_back({img, asp});
    };
    for (size_t k = 0; k < n; ++k) {
        const Draw& dr = *run[k];
        for (int st2 = 0; st2 < 2; ++st2)
            for (uint32_t msk = dr.tex_mask[st2]; msk; msk &= msk - 1) {
                const uint32_t* t = dr.tex[st2][__builtin_ctz(msk)];
                const auto ts = fmt::decode_tsharp(t);
                if (depth && depth->stencil)
                    if (auto sit = stencil_by_base.find(ts.base); sit != stencil_by_base.end() && sit->second == depth) {
                        add(depth, 2);
                        continue;
                    }
                Image* ri = target_for(ts);
                if (!ri || ri->is3d || ri->layers > 1) continue;
                bool attached = ri == depth;
                for (int i = 0; i < 8; ++i) attached |= ri == colors[i];
                if (attached) add(ri, 1);
            }
    }
    const uint64_t key = pass_key_of(colors, depth);
    if (rc().in_pass && (new_pass || rc().pass_key != key)) end_pass();  // (begin_pass would; the new instance's tracking starts here)
    const bool same_pass = rc().in_pass;
    // (cleared only here: an instance begun elsewhere - e.g. after an upload ended the pass -
    // keeps what the last one tracked, which can only split more often)
    if (!same_pass) rc().pass_live.clear(), rc().pass_written.clear();
    // the open instance continues with this run: it must not write what was read in place, nor
    // read in place what it wrote
    if (same_pass) {
        bool split = false;
        for (auto& [img, a] : rc().pass_live) split |= (writes(img) & a) != 0;
        for (const Need& x : need)
            if (!(writes(x.img) & x.asp) && (find(rc().pass_written, x.img) & x.asp)) {
                const bool snapped = rc().snap_key == key &&
                                     std::any_of(rc().snaps.begin(), rc().snaps.end(), [&](auto& p) { return p.first == x.img; });
                if (!snapped) split = true;
            }
        if (split) end_pass();
    }
    // what is copied: what the run reads and writes, and what the pass already reads from a copy
    std::vector<Need> snap_need;
    const bool keep = rc().snap_key == key;
    for (const Need& x : need) {
        const bool copied = keep && std::any_of(rc().snaps.begin(), rc().snaps.end(), [&](auto& p) { return p.first == x.img; });
        if (copied || (writes(x.img) & x.asp)) snap_need.push_back(x);
        else put(rc().pass_live, x.img, x.asp);
    }
    auto done = [&] {
        for (Image* img : {colors[0], colors[1], colors[2], colors[3], colors[4], colors[5], colors[6], colors[7], depth})
            if (img) {
                const uint8_t a = writes(img);
                put(rc().pass_written, img, a);
                if (a) wrote_target(img, a);
            }
    };
    if (snap_need.empty()) {
        if (!keep) rc().snaps.clear(), rc().snap_key = 0;
        return done();
    }
    if (keep && std::all_of(snap_need.begin(), snap_need.end(), [&](const Need& x) {
            return std::any_of(rc().snaps.begin(), rc().snaps.end(), [&](auto& p) { return p.first == x.img; });
        }))
        return done();  // (copied for this pass already: the draws read the pass's starting contents)
    if (keep)
        for (auto& p : rc().snaps)
            if (std::none_of(snap_need.begin(), snap_need.end(), [&](const Need& x) { return x.img == p.first; }))
                snap_need.push_back({p.first, 0});  // (earlier draws of the pass sample these too)
    // snapshots still current in this command buffer need no copy (and no break in the pass)
    std::vector<Image*> copy;
    std::vector<std::pair<Image*, Image*>> snaps;
    for (const Need& x : snap_need) {
        auto f = std::find_if(rc().fresh.begin(), rc().fresh.end(), [&](auto& p) { return p.img == x.img; });
        auto si = snap_img.find(x.img);
        const uint8_t want = x.asp ? x.asp : 3;
        if (f != rc().fresh.end() && si != snap_img.end() && si->second.get() == f->sn && (f->valid & want) == want)
            snaps.push_back({x.img, f->sn}), ++snap_reused;
        else copy.push_back(x.img);
    }
    if (!copy.empty()) {
        end_pass();  // (copies run outside render passes; the next draw begins the pass again)
        for (Image* img : copy) {
            auto& sn = snap_img[img];
            if (!sn || sn->w != img->w || sn->h != img->h || sn->format != img->format) {
                if (sn) bury(std::move(sn));
                sn = make_image(img->format, img->w, img->h, 1, 1, 1, false, false, img->depth, img->stencil);
                if (!sn) continue;
                sn->base = img->base, sn->swap = img->swap;
            }
            VkImageCopy c{};
            const VkImageAspectFlags asp = img->depth ? VkImageAspectFlags(VK_IMAGE_ASPECT_DEPTH_BIT | (img->stencil ? VK_IMAGE_ASPECT_STENCIL_BIT : 0))
                                                      : VK_IMAGE_ASPECT_COLOR_BIT;
            c.srcSubresource = c.dstSubresource = {asp, 0, 0, 1};
            c.extent = {img->w, img->h, 1};
            vkCmdCopyImage(rc().cmd, img->image, VK_IMAGE_LAYOUT_GENERAL, sn->image, VK_IMAGE_LAYOUT_GENERAL, 1, &c);
            snaps.push_back({img, sn.get()});
            wrote_target(img);
            rc().fresh.push_back({img, sn.get(), 3});
            ++snap_copies;
            if (static const bool lg = std::getenv("D1_NG_LOG_SNAPS"); lg)
                if (static uint64_t tot = 0; ++tot >= 1000 && tot < 1080)
                    log("native renderer: snapshot %ux%u fmt %d of %s, run of %zu from ps %#llx, writes %#x", img->w, img->h, int(img->format),
                        img == depth ? "the depth target" : "a color target", n, (unsigned long long)run[0]->ps, w);
        }
        barrier();
    }
    rc().snaps = std::move(snaps);
    rc().snap_key = key;
    done();
}

uint32_t Renderer::run_writes(const Draw* const* run, size_t n) {
    uint32_t w = 0;
    for (size_t k = 0; k < n; ++k) {
        const Draw& dr = *run[k];
        for (int i = 0; i < 8; ++i)
            if (dr.target_mask >> (4 * i) & 0xF) w |= 1u << i;
        if (dr.depth_ctl & 4) w |= 1u << 8;  // (z write; conservatively even without the z test)
        if (dr.depth_ctl & 1) {              // stencil test: written unless every op keeps or nothing is writable
            uint32_t ref, wm;
            stencil_dynamic(dr.stencil_ctl, dr.depth_ctl, dr.stencil_ref, ref, wm);
            if (wm && (dr.stencil_ctl & 0xFFFFFF)) w |= 1u << 9;
        }
        if (dr.kind == Draw::Clear || dr.clear_flags) w = 0x3FF;
    }
    return w;
}

// A render target sampled as a texture (as texture_view does it), from `img` - the target
// itself or its snapshot - with the channel order of `like`.
VkImageView Renderer::target_view(Image* img, const Image* like, const uint32_t* t) {
    if (img->depth) return view(img, VK_IMAGE_VIEW_TYPE_2D, {}, 0, true);
    const auto ts = fmt::decode_tsharp(t);
    VkComponentMapping comp{swz(ts.dst_sel & 7), swz(ts.dst_sel >> 3 & 7), swz(ts.dst_sel >> 6 & 7), swz(ts.dst_sel >> 9 & 7)};
    if (like->swap == 1) {
        auto back = [](VkComponentSwizzle s) {
            return s == VK_COMPONENT_SWIZZLE_R ? VK_COMPONENT_SWIZZLE_B : s == VK_COMPONENT_SWIZZLE_B ? VK_COMPONENT_SWIZZLE_R : s;
        };
        comp = {back(comp.r), back(comp.g), back(comp.b), back(comp.a)};
    }
    return view(img, VK_IMAGE_VIEW_TYPE_2D, comp, 0, false);
}

void Renderer::begin_pass(Image* const* colors, Image* depth, bool secondaries) {
    const uint64_t key = pass_key_of(colors, depth);
    if (!secondaries && rc().in_pass && key == rc().pass_key) return;
    if (key != rc().snap_key) rc().snaps.clear(), rc().snap_key = 0;
    end_pass();
    VkRenderingAttachmentInfo ca[8]{};
    uint32_t n = 0, w = UINT32_MAX, h = UINT32_MAX;
    for (uint32_t i = 0; i < 8; ++i) {
        ca[i] = {VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO};
        if (colors[i]) {
            n = i + 1;
            ca[i].imageView = attachment_view(colors[i]);
            ca[i].imageLayout = VK_IMAGE_LAYOUT_GENERAL;
            ca[i].loadOp = VK_ATTACHMENT_LOAD_OP_LOAD;
            ca[i].storeOp = VK_ATTACHMENT_STORE_OP_STORE;
            w = std::min(w, colors[i]->w), h = std::min(h, colors[i]->h);
        }
        rc().pass_color[i] = colors[i];
    }
    VkRenderingAttachmentInfo da{VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO};
    if (depth) {
        da.imageView = attachment_view(depth);
        da.imageLayout = VK_IMAGE_LAYOUT_GENERAL;
        da.loadOp = VK_ATTACHMENT_LOAD_OP_LOAD;
        da.storeOp = VK_ATTACHMENT_STORE_OP_STORE;
        w = std::min(w, depth->w), h = std::min(h, depth->h);
    }
    if (w == UINT32_MAX) w = h = 1;
    VkRenderingInfo ri{VK_STRUCTURE_TYPE_RENDERING_INFO};
    ri.renderArea = {{0, 0}, {w, h}};
    ri.layerCount = 1;
    ri.colorAttachmentCount = n;
    ri.pColorAttachments = ca;
    ri.pDepthAttachment = depth ? &da : nullptr;
    ri.pStencilAttachment = depth && depth->stencil ? &da : nullptr;
    if (secondaries) {
        // (contents only through vkCmdExecuteCommands; an occlusion query spans the pass from
        // outside, begun before it)
        ri.flags = VK_RENDERING_CONTENTS_SECONDARY_COMMAND_BUFFERS_BIT;
        if (rc().q_on && rc().q_active < 0 && subs[rc().cur].q_used < kQueries) {
            Sub& sb = subs[rc().cur];
            vkCmdBeginQuery(rc().cmd, sb.qpool, sb.q_used, ctx.occlusion_precise ? VK_QUERY_CONTROL_PRECISE_BIT : 0);
            rc().q_active = int32_t(sb.q_used++);
        }
    }
    vkCmdBeginRendering(rc().cmd, &ri);
    rc().in_pass = true;
    if (!secondaries) q_begin();
    if (st.frames == passlog_frame) {
        PassLog pl{};
        for (int i = 0; i < 5; ++i) pl.c[i] = colors[i] ? colors[i]->base + colors[i]->bind_slice : 0;
        pl.d = depth ? depth->base : 0;
        passlog.push_back(pl);
    }
    rc().pass_key = key, rc().pass_depth = depth, rc().pass_w = w, rc().pass_h = h;
}

void Renderer::clear(const Draw& dr) {
    if (debug && st.frames >= debug_from && debug_lines < 600) {
        ++debug_lines;
        log("ng clear flags %#x color %g %g %g %g depth %g stencil %u | c0 %llx d %llx", dr.clear_flags,
            dr.clear_color[0], dr.clear_color[1], dr.clear_color[2], dr.clear_color[3], dr.clear_depth,
            dr.clear_stencil, (unsigned long long)dr.color[0][0] << 8, (unsigned long long)dr.depth[4] << 8);
    }
    static const std::vector<uint64_t> skip_ps = [] {  // D1_NG_SKIP_PS=<hex>,..: (testing) leave these out
        std::vector<uint64_t> v;
        if (const char* e = std::getenv("D1_NG_SKIP_PS"))
            for (const char* p = e; *p;) {
                char* end;
                v.push_back(std::strtoull(p, &end, 16));
                p = *end ? end + 1 : end;
            }
        return v;
    }();
    if (!skip_ps.empty() && std::find(skip_ps.begin(), skip_ps.end(), uint64_t(dr.ps)) != skip_ps.end()) return;
    Image* colors[8] = {};
    for (int i = 0; i < 5; ++i) colors[i] = color_target(dr.color[i]);
    Image* depth = depth_target(dr.depth);
    if (rc().in_pass && rc().pass_key == pass_key_of(colors, depth) && !rc().pass_live.empty()) end_pass();  // (it writes what the pass reads in place)
    begin_pass(colors, depth);
    for (Image* x : colors)
        if (x) wrote_target(x), rc().pass_written.push_back({x, 3});
    if (depth) wrote_target(depth), rc().pass_written.push_back({depth, 3});
    VkClearAttachment att[6];
    uint32_t n = 0;
    for (uint32_t i = 0; i < 4; ++i)
        if ((dr.clear_flags >> (2 + i) & 1) && colors[i]) {
            att[n] = {VK_IMAGE_ASPECT_COLOR_BIT, i, {}};
            std::memcpy(att[n].clearValue.color.float32, dr.clear_color, 16);
            ++n;
        }
    VkImageAspectFlags da = 0;
    if ((dr.clear_flags & 0x40) && depth) da |= VK_IMAGE_ASPECT_DEPTH_BIT;
    const uint32_t stencil_wm = dr.stencil_ref >> 16 & 0xFF;
    const bool masked_stencil = (dr.clear_flags & 0x80) && depth && depth->stencil && stencil_wm != 0xFF;
    if ((dr.clear_flags & 0x80) && depth && depth->stencil && !masked_stencil) da |= VK_IMAGE_ASPECT_STENCIL_BIT;
    if (da) {
        att[n] = {da, 0, {}};
        att[n].clearValue.depthStencil = {dr.clear_depth, dr.clear_stencil};
        ++n;
    }
    if (!n && !masked_stencil) return;
    int32_t x = std::max(0, dr.vp[0]), y = std::max(0, dr.vp[1]);
    uint32_t w = dr.vp[2] > 0 ? uint32_t(dr.vp[2]) : rc().pass_w, h = dr.vp[3] > 0 ? uint32_t(dr.vp[3]) : rc().pass_h;
    w = std::min(w, rc().pass_w - std::min<uint32_t>(rc().pass_w, uint32_t(x)));
    h = std::min(h, rc().pass_h - std::min<uint32_t>(rc().pass_h, uint32_t(y)));
    if (!w || !h) return;
    if (st.frames == passlog_frame && !passlog.empty()) ++passlog.back().clears;
    VkClearRect r{{{x, y}, {w, h}}, 0, 1};
    if (n) vkCmdClearAttachments(rc().cmd, n, att, 1, &r);
    if (masked_stencil && stencil_wm) masked_stencil_clear(depth, dr.clear_stencil, stencil_wm, r.rect);
    ++st.clears;
}

// Inside the current pass: stencil = (stencil & ~write_mask) | (value & write_mask) over rect.
void Renderer::masked_stencil_clear(Image* depth, uint32_t value, uint32_t write_mask, const VkRect2D& rect) {
    static const uint32_t kVs[] = {
#include "fullscreen_vs.inc"
    };
    if (!fullscreen_vs) {
        VkShaderModuleCreateInfo smi{VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};
        smi.codeSize = sizeof kVs;
        smi.pCode = kVs;
        vkCreateShaderModule(ctx.device, &smi, nullptr, &fullscreen_vs);
        VkPipelineLayoutCreateInfo pli{VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO};
        vkCreatePipelineLayout(ctx.device, &pli, nullptr, &empty_layout);
    }
    VkFormat cfmt[8]{};
    uint32_t ncolor = 0;
    for (uint32_t i = 0; i < 8; ++i)
        if (rc().pass_color[i]) cfmt[i] = rc().pass_color[i]->format, ncolor = i + 1;
    uint64_t key = depth->format;
    for (uint32_t i = 0; i < ncolor; ++i) key = mix(key, cfmt[i] + 1);
    VkPipeline& pipe = stencil_clear_pipes[key];
    if (!pipe) {
        VkPipelineShaderStageCreateInfo stage{VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO};
        stage.stage = VK_SHADER_STAGE_VERTEX_BIT;
        stage.module = fullscreen_vs;
        stage.pName = "main";
        VkPipelineVertexInputStateCreateInfo vi{VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO};
        VkPipelineInputAssemblyStateCreateInfo ia{VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO};
        ia.topology = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST;
        VkPipelineViewportStateCreateInfo vp{VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO};
        vp.viewportCount = vp.scissorCount = 1;
        VkPipelineRasterizationStateCreateInfo rs{VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO};
        rs.polygonMode = VK_POLYGON_MODE_FILL;
        rs.cullMode = VK_CULL_MODE_NONE;
        rs.lineWidth = 1.0f;
        VkPipelineMultisampleStateCreateInfo ms{VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO};
        ms.rasterizationSamples = VK_SAMPLE_COUNT_1_BIT;
        VkPipelineDepthStencilStateCreateInfo ds{VK_STRUCTURE_TYPE_PIPELINE_DEPTH_STENCIL_STATE_CREATE_INFO};
        ds.stencilTestEnable = VK_TRUE;
        ds.front = {VK_STENCIL_OP_REPLACE, VK_STENCIL_OP_REPLACE, VK_STENCIL_OP_REPLACE, VK_COMPARE_OP_ALWAYS, 0xFF, 0xFF, 0};
        ds.back = ds.front;
        VkPipelineColorBlendAttachmentState cb[8]{};
        VkPipelineColorBlendStateCreateInfo cbs{VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO};
        cbs.attachmentCount = ncolor;
        cbs.pAttachments = cb;
        const VkDynamicState dyn[] = {VK_DYNAMIC_STATE_VIEWPORT, VK_DYNAMIC_STATE_SCISSOR, VK_DYNAMIC_STATE_STENCIL_REFERENCE,
                                      VK_DYNAMIC_STATE_STENCIL_WRITE_MASK};
        VkPipelineDynamicStateCreateInfo dy{VK_STRUCTURE_TYPE_PIPELINE_DYNAMIC_STATE_CREATE_INFO};
        dy.dynamicStateCount = 4;
        dy.pDynamicStates = dyn;
        VkPipelineRenderingCreateInfo rci{VK_STRUCTURE_TYPE_PIPELINE_RENDERING_CREATE_INFO};
        rci.colorAttachmentCount = ncolor;
        rci.pColorAttachmentFormats = cfmt;
        rci.depthAttachmentFormat = depth->format;
        rci.stencilAttachmentFormat = depth->format;
        VkGraphicsPipelineCreateInfo gci{VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO, &rci};
        gci.stageCount = 1;
        gci.pStages = &stage;
        gci.pVertexInputState = &vi;
        gci.pInputAssemblyState = &ia;
        gci.pViewportState = &vp;
        gci.pRasterizationState = &rs;
        gci.pMultisampleState = &ms;
        gci.pDepthStencilState = &ds;
        gci.pColorBlendState = &cbs;
        gci.pDynamicState = &dy;
        gci.layout = empty_layout;
        if (vkCreateGraphicsPipelines(ctx.device, pcache, 1, &gci, nullptr, &pipe) != VK_SUCCESS) pipe = VK_NULL_HANDLE;
    }
    if (!pipe) return;
    rc().dstate.valid = false;  // (its own pipeline and dynamic state)
    vkCmdBindPipeline(rc().cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, pipe);
    const VkViewport v{0, 0, float(rc().pass_w), float(rc().pass_h), 0, 1};
    vkCmdSetViewport(rc().cmd, 0, 1, &v);
    vkCmdSetScissor(rc().cmd, 0, 1, &rect);
    vkCmdSetStencilReference(rc().cmd, VK_STENCIL_FACE_FRONT_AND_BACK, value & 0xFF);
    vkCmdSetStencilWriteMask(rc().cmd, VK_STENCIL_FACE_FRONT_AND_BACK, write_mask);
    vkCmdDraw(rc().cmd, 3, 1, 0, 0);
}

// One draw into a recording context: the main command buffer (serially, as the submission is
// executed) or, for runs of plain draws inside one render pass, a worker's secondary command
// buffer (parallel: the shared caches are taken under their locks, constants and streamed
// vertices go to the worker's own slice of the ring, statistics to the context).
void Renderer::draw(const Draw& dr, Rec& r, Image* const* run_colors, Image* run_depth) {
    const bool lr = rc().lr;
    auto guard = [&](std::mutex& mx) {
        return r.parallel ? std::unique_lock<std::mutex>(lr && &mx != &skip_m ? m : mx) : std::unique_lock<std::mutex>();
    };
    auto skip = [&](const char* why) {
        auto lk = guard(skip_m);
        this->skip(why);
    };
    VkCommandBuffer cmd = r.cmd;
    uint64_t t0 = now_ns();
    auto lap = [&](uint64_t& acc) {
        const uint64_t t = now_ns();
        acc += t - t0;
        t0 = t;
    };
    if (!dr.vs || uint64_t(dr.vs) < 0x10000 || (dr.ps && uint64_t(dr.ps) < 0x10000)) {
        auto lk = guard(skip_m);
        static std::unordered_set<uint64_t> seen;
        if (seen.insert(dr.caller).second && seen.size() < 20)
            log("native renderer: draw without shaders (vs %p ps %p) from eboot+%#llx", (const void*)dr.vs,
                (const void*)dr.ps, (unsigned long long)dr.caller);
        return skip("no shader");
    }
    Image* colors[8] = {};
    Image* depth = nullptr;
    if (run_colors) {
        std::copy(run_colors, run_colors + 8, colors), depth = run_depth;
    } else {
        for (int i = 0; i < 5; ++i) colors[i] = color_target(dr.color[i]);
        depth = depth_target(dr.depth);
    }
    if (!depth && std::none_of(colors, colors + 8, [](Image* x) { return x != nullptr; })) return skip("no target");
    Pipeline* p = nullptr;
    if (lr && r.parallel) {
        // this thread's cache of pipeline() results (the shared memo needs the lock)
        struct TlMemo { uint64_t key = 0, gen = 0; Pipeline* p = nullptr; };
        static thread_local TlMemo tlm[4096];
        bool amb;
        const uint64_t k = pipe_key(dr, colors, depth, amb);
        const uint64_t gen = targets_gen.load(std::memory_order_acquire);
        TlMemo& e = tlm[k & 4095];
        if (!amb && e.key == k && e.gen == gen && e.p) {
            p = e.p;
            ++r.memo_tl;
        } else {
            auto lk = guard(pipe_m);
            p = pipeline(dr, colors, depth);
            if (!amb) e = {k, gen, p};
        }
    } else {
        auto lk = guard(pipe_m);
        p = pipeline(dr, colors, depth);
    }
    if (!p) return skip("pipeline");
    lap(r.t_pipe);
    // geometry into the ring
    VkBuffer vbufs[16];
    VkDeviceSize voffs[16], vsizes[16];
    uint32_t vmask = 0;
    // vertices the draw can reference: [first, last] from the indices
    uint32_t vfirst = 0, vlast = dr.count ? dr.count - 1 : 0;
    bool ige = false;  // cached index buffer
    const bool dyn_copy = dynamic_copy;
    VkBuffer ige_buf = VK_NULL_HANDLE;
    uint64_t ige_off = 0;
    if (dr.kind == Draw::Indexed && dr.index_addr >= 0x10000 && dr.count && dr.prim != 0x13) {
        GeoHit h;
        const uint64_t ibytes = uint64_t(dr.count) * (dr.index32 ? 4 : 2);
        const bool ires = dr.ires.id && dr.index_addr >= dr.ires.base && dr.index_addr + ibytes <= dr.ires.base + dr.ires.size;
        if (!dr.ires.id) __atomic_fetch_add(&st.why_ib_noid, 1, __ATOMIC_RELAXED);
        else if (!ires) __atomic_fetch_add(&st.why_ib_range, 1, __ATOMIC_RELAXED);
        // (memory that is no engine resource is dynamic data: copied for the draw, not cached)
        if ((ires || !dyn_copy) && geo_get(dr.index_addr, ibytes, dr.index32 ? 4 : 2, dr.count, h, ires ? dr.ires.id : 0, dr.ires.base))
            ige = true, ige_buf = h.buf, ige_off = h.off, vfirst = h.vfirst, vlast = h.vlast;
    }
    if (!ige && dr.kind == Draw::Indexed && dr.index_addr >= 0x10000 && dr.count) {
        vfirst = UINT32_MAX, vlast = 0;
        if (dr.index32) {
            const uint32_t* ix = reinterpret_cast<const uint32_t*>(dr.index_addr);
            for (uint32_t i = 0; i < dr.count; ++i)
                if (ix[i] != 0xFFFFFFFFu) vfirst = std::min(vfirst, ix[i]), vlast = std::max(vlast, ix[i]);
        } else {
            const uint16_t* ix = reinterpret_cast<const uint16_t*>(dr.index_addr);
            for (uint32_t i = 0; i < dr.count; ++i)
                if (ix[i] != 0xFFFF) vfirst = std::min<uint32_t>(vfirst, ix[i]), vlast = std::max<uint32_t>(vlast, ix[i]);
        }
        if (vfirst > vlast) vfirst = vlast = 0;
    }
    for (const auto& a : p->vs->res.attribs) {
        const uint32_t slot = a.vb_slot & 15;
        if (vmask >> slot & 1) continue;
        const uint32_t* v = dr.vb[slot];
        uint64_t base = uint64_t(v[0]) | uint64_t(v[1] & 0xFFF) << 32;
        const uint32_t stride = v[1] >> 16 & 0x3FFF;
        // copy only vertices [vfirst, vlast] (bounded by the V#'s record count); vertexOffset
        // in the draw shifts the indices back
        const uint32_t records = std::max(v[2], 1u);
        // per-instance streams (fetched with the instance id) start at record 0
        const bool per_instance = a.index_vgpr != 0;
        const uint32_t lo = per_instance ? 0 : vfirst, hi = per_instance ? std::max(dr.instances, 1u) - 1 : vlast;
        const uint32_t first = stride ? lo : 0, last = stride ? std::min(hi, records - 1) : 0;
        if (first >= records && stride) {  // every fetch is out of range: reads 0, as on GCN
            const uint64_t off = rec_ring(r, 16);
            if (off == UINT64_MAX) return skip("ring full");
            std::memset(ring.map + off, 0, 16);
            vbufs[slot] = ring.buf, voffs[slot] = off, vsizes[slot] = 16;
            vmask |= 1u << slot;
            continue;
        }
        uint64_t size = stride ? uint64_t(last - first + 1) * stride : 16;
        uint64_t src = base + uint64_t(first) * stride;
        // an engine resource: the whole buffer, by its identity
        {
            const Draw::Res& R = dr.vres[slot];
            if (!dr.inline_vertices.empty()) __atomic_fetch_add(&st.why_inline, 1, __ATOMIC_RELAXED);
            else if (!R.id) __atomic_fetch_add(&st.why_vb_noid, 1, __ATOMIC_RELAXED);
            else if (!(stride && base >= R.base && src < R.base + R.size)) {
                __atomic_fetch_add(&st.why_vb_range, 1, __ATOMIC_RELAXED);
                static std::atomic<int> told{0};
                if (told++ < 10)
                    log("ng geo: vertex range outside its buffer: base %#llx src %#llx size %llu stride %u records %u first %u | buffer %#llx +%llu",
                        (unsigned long long)base, (unsigned long long)src, (unsigned long long)size, stride, records, first,
                        (unsigned long long)R.base, (unsigned long long)R.size);
            }
        }
        // (the last record may end past the buffer by its element's offset in the stride: the
        // binding ends with the buffer, no fetch reads past it)
        if (const Draw::Res& R = dr.vres[slot]; R.id && dr.inline_vertices.empty() && stride && base >= R.base &&
                                                 src < R.base + R.size) {
            GeoHit h;
            if (geo_get(R.base, R.size, 0, 0, h, R.id, R.base)) {
                vbufs[slot] = h.buf, voffs[slot] = h.off + (src - R.base);
                vsizes[slot] = std::min<uint64_t>(size, R.size - (src - R.base));
                vmask |= 1u << slot;
                continue;
            }
        }
        // the whole buffer from the geometry cache (write-tracked; not with engine resource events:
        // what is not an engine resource is dynamic data, copied below for the draw)
        if (dr.inline_vertices.empty() && stride && base >= 0x10000 && !dyn_copy) {
            GeoHit h;
            if (geo_get(base, uint64_t(records) * stride, 0, 0, h)) {
                vbufs[slot] = h.buf, voffs[slot] = h.off + uint64_t(first) * stride;
                vsizes[slot] = std::min<uint64_t>(size, h.size - uint64_t(first) * stride);
                vmask |= 1u << slot;
                continue;
            }
        }
        if (!dr.inline_vertices.empty()) {  // V# base is an offset into the inline data
            if (src >= dr.inline_vertices.size()) return skip("inline vertex offset");
            size = std::min<uint64_t>(size, dr.inline_vertices.size() - src);
            src += uint64_t(dr.inline_vertices.data());
        } else if (base < 0x10000) return skip("null vertex buffer");
        size = std::min<uint64_t>(size, 64ull << 20);
        const uint64_t off = rec_ring(r, std::max<uint64_t>(size, 16), 256);
        if (off == UINT64_MAX) return skip("ring full");
        std::memcpy(ring.map + off, reinterpret_cast<const void*>(src), size);
        if (dr.inline_vertices.empty()) note_copy(1, src, size);
        r.bytes_vtx += size;
        if (size < 16) std::memset(ring.map + off + size, 0, 16 - size);
        // the binding starts at vertex `vfirst`; a stride-0 stream is one record for every vertex
        vbufs[slot] = ring.buf, voffs[slot] = off, vsizes[slot] = std::max<uint64_t>(size, 16);
        vmask |= 1u << slot;
    }
    lap(r.t_geo);
    if (!r.parallel) {
        const Draw* one = &dr;
        feedback_snapshots(&one, 1, colors, depth);
    }
    // descriptors (copied constants, image views, samplers)
    VkWriteDescriptorSet writes[2][48];
    VkDescriptorImageInfo images[2][48];
    VkDescriptorBufferInfo bufs[2][48];
    uint32_t nw[2] = {};
    for (int s = 0; s < 2; ++s) {
        const Shader* sh = s ? p->ps : p->vs;
        if (!sh) continue;
        for (const auto& b : sh->res.bindings) {
            if (nw[s] >= 48) break;
            auto& w = writes[s][nw[s]];
            w = {VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};
            w.dstBinding = b.binding;
            w.descriptorCount = 1;
            const uint32_t slot = b.api_slot & 15;
            if (b.kind == gcn::Binding::Texture) {
                w.descriptorType = VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE;
                // per-thread cache of resolved views (valid while views_gen is unchanged: the
                // shared maps are only taken on a miss)
                struct TvEntry { uint64_t key = 0, gen = 0; VkImageView view = VK_NULL_HANDLE; Image* tex = nullptr; };
                static thread_local TvEntry tvc[2048];
                const uint32_t* T = dr.T(s, slot);
                const gcn::TexDim dim = slot_dim(T);
                const uint64_t tres = T ? dr.tex_res[s][slot & 15] : 0;
                const uint64_t key = (T ? hash_bytes(T, 32) ^ tres * 0xC2B2AE3D27D4EB4Full : 0x5A5A) ^ (uint64_t(dim) + 1) * 0x9E3779B97F4A7C15ull;
                const uint64_t gen = views_gen.load(std::memory_order_acquire);
                TvEntry& e = tvc[key & 2047];
                VkImageView v = VK_NULL_HANDLE;
                if (!rc().snaps.empty() && T) {  // an attachment of this pass: its snapshot
                    auto lk = guard(tex_m);
                    const auto ts = fmt::decode_tsharp(T);
                    auto sit = stencil_by_base.find(ts.base);
                    if (sit != stencil_by_base.end() && sit->second->stencil) {  // (as texture_view: the stencil of a depth target)
                        for (auto& [att, sn] : rc().snaps)
                            if (att == sit->second) { v = view(sn, VK_IMAGE_VIEW_TYPE_2D, {}, 0, true, true); break; }
                    } else if (Image* ri = target_for(ts))
                        for (auto& [att, sn] : rc().snaps)
                            if (att == ri) { v = target_view(sn, ri, T); break; }
                }
                if (v) {
                } else if (e.key == key && e.gen == gen && e.view) {
                    v = e.view;
                    if (e.tex) e.tex->last_used = rc().submit_no;  // (keeps it from being dropped as unused)
                } else {
                    auto lk = guard(tex_m);
                    v = texture_view(T, dim, tres);
                    Image* tex = tv_texture;
                    if (T)
                        if (Image* ri = target_for(fmt::decode_tsharp(T)))
                            v = texture_view(T, ri->is3d ? gcn::TexDim::Tex3D : gcn::TexDim::Tex2D, tres), tex = nullptr;
                    e = {key, gen, v, tex};
                }
                images[s][nw[s]] = {VK_NULL_HANDLE, v, VK_IMAGE_LAYOUT_GENERAL};
                // D1_NG_LOG_FEEDBACK: (diagnostics) a draw sampling an image it renders into
                static const bool log_fb = std::getenv("D1_NG_LOG_FEEDBACK") != nullptr;
                if (log_fb && T) {
                    auto lk = guard(tex_m);
                    if (Image* ri = target_for(fmt::decode_tsharp(T))) {
                        bool hit = ri == depth;
                        for (int k = 0; k < 8; ++k) hit |= ri == colors[k];
                        if (hit) {
                            ++feedback_draws;
                            static std::mutex fm;
                            static std::set<std::pair<uint64_t, uint64_t>> seen;
                            std::lock_guard fl(fm);
                            if (seen.insert({uint64_t(dr.ps), uint64_t(ri)}).second && seen.size() < 60)
                                log("native renderer: feedback: ps %#llx samples %s %ux%u fmt %d it renders into (t%u) | depth ctl %#x (z write %u), target mask %#x, blend %#x, from %#llx",
                                    (unsigned long long)dr.ps, ri->depth ? "depth target" : "color target", ri->w, ri->h, int(ri->format), slot,
                                    dr.depth_ctl, dr.depth_ctl >> 2 & 1, dr.target_mask, dr.blend, (unsigned long long)dr.caller);
                        }
                    }
                }
                w.pImageInfo = &images[s][nw[s]];
            } else if (b.kind == gcn::Binding::Sampler) {
                w.descriptorType = VK_DESCRIPTOR_TYPE_SAMPLER;
                struct SmpEntry { uint64_t key = 0; VkSampler smp = VK_NULL_HANDLE; };
                static thread_local SmpEntry smc[512];
                const uint32_t* S = dr.S(s, slot);
                const uint64_t key = S ? hash_bytes(S, 16) | 1 : 0;
                SmpEntry& e = smc[key & 511];
                VkSampler smp;
                if (key && e.key == key) {
                    smp = e.smp;
                } else {
                    auto lk = guard(tex_m);
                    smp = sampler(S);
                    if (key) e = {key, smp};
                }
                images[s][nw[s]] = {smp, VK_NULL_HANDLE, VK_IMAGE_LAYOUT_GENERAL};
                w.pImageInfo = &images[s][nw[s]];
            } else {
                w.descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
                const auto& c = dr.cb[s][slot];
                uint64_t off;
                uint32_t size = std::max(16u, (c.size + 15) & ~15u);
                if ((c.addr & kLateCb) && rc().lr) {  // inherited from earlier lists: the list's region for the slot, filled at submission
                    Recorder::Late& L = rc().late[s][slot];
                    if (!L.size) {
                        const uint32_t want = std::min<uint32_t>(65536, std::max({256u, (c.size + 255) & ~255u, late_hint[s][slot].load()}));
                        L.off = rec_ring(r, want);
                        if (L.off == UINT64_MAX) return skip("ring full");
                        L.size = want;
                        rc().late_list.push_back({uint8_t(s), uint8_t(slot), want, L.off});
                    }
                    off = L.off, size = L.size;
                } else if (c.addr >= 0x10000 && !(c.addr & kLateCb)) off = rec_copy(r, reinterpret_cast<const void*>(c.addr), c.size), r.bytes_cb += c.size, note_copy(0, c.addr, c.size);
                else off = rec_ring(r, size), std::memset(ring.map + (off == UINT64_MAX ? 0 : off), 0, size);
                if (off == UINT64_MAX) return skip("ring full");
                bufs[s][nw[s]] = {ring.buf, off, size};
                w.pBufferInfo = &bufs[s][nw[s]];
            }
            ++nw[s];
        }
    }
    lap(r.t_desc);
    // indices
    uint32_t count = dr.count;
    uint64_t ioff = 0;
    VkBuffer index_buf = ring.buf;
    bool indexed = dr.kind == Draw::Indexed;
    VkIndexType itype = dr.index32 ? VK_INDEX_TYPE_UINT32 : VK_INDEX_TYPE_UINT16;
    if (dr.prim == 0x13 && indexed && dr.index_addr < 0x10000) return skip("null index buffer");
    if (dr.prim == 0x13) {  // quad list -> two triangles per quad
        const uint32_t quads = count / 4;
        const uint64_t o = rec_ring(r, uint64_t(quads) * 6 * 4, 4);
        if (o == UINT64_MAX) return skip("ring full");
        uint32_t* out = reinterpret_cast<uint32_t*>(ring.map + o);
        for (uint32_t q = 0; q < quads; ++q) {
            uint32_t v[4];
            for (int k = 0; k < 4; ++k) {
                const uint32_t i = q * 4 + k;
                v[k] = !indexed ? i
                     : dr.index32 ? reinterpret_cast<const uint32_t*>(dr.index_addr)[i]
                                  : reinterpret_cast<const uint16_t*>(dr.index_addr)[i];
            }
            const uint32_t t[6] = {v[0], v[1], v[2], v[0], v[2], v[3]};
            std::memcpy(out + q * 6, t, sizeof t);
        }
        ioff = o, count = quads * 6, indexed = true, itype = VK_INDEX_TYPE_UINT32;
    } else if (indexed && ige) {
        index_buf = ige_buf, ioff = ige_off;
    } else if (indexed) {
        if (dr.index_addr < 0x10000) return skip("null index buffer");
        ioff = rec_copy(r, reinterpret_cast<const void*>(dr.index_addr), uint64_t(count) * (dr.index32 ? 4 : 2));
        note_copy(2, dr.index_addr, uint64_t(count) * (dr.index32 ? 4 : 2));
        r.bytes_idx += uint64_t(count) * (dr.index32 ? 4 : 2);
        if (ioff == UINT64_MAX) return skip("ring full");
    }
    if (!count) return;

    if (!r.parallel) begin_pass(colors, depth);
    // D1_NG_DEBUG_PS=<hex>: only log draws using this pixel shader, with its constant buffers in full
    static const uint64_t debug_ps = [] {
        const char* v = std::getenv("D1_NG_DEBUG_PS");
        return v ? std::strtoull(v, nullptr, 16) : 0ull;
    }();
    if (!r.parallel && debug && st.frames >= debug_from && debug_lines < 600 && (!debug_ps || uint64_t(dr.ps) == debug_ps)) {
        ++debug_lines;
        log("ng draw %s prim %u count %u inst %u | vs %p ps %p | c0 %llx d %llx | depth %#x stencil %#x/%#x blend %#x mask %#x "
            "su %#x | vp %d %d %d %d z %g..%g | vb %u range %u..%u | from %#llx",
            dr.kind == Draw::Indexed ? "idx" : "auto", dr.prim, dr.count, dr.instances, (const void*)dr.vs,
            (const void*)dr.ps, (unsigned long long)dr.color[0][0] << 8, (unsigned long long)dr.depth[4] << 8,
            dr.depth_ctl, dr.stencil_ctl, dr.stencil_ref, dr.blend, dr.target_mask, dr.su_sc_mode, dr.vp[0], dr.vp[1],
            dr.vp[2], dr.vp[3], dr.znear, dr.zfar, dr.num_vb, vfirst, vlast, (unsigned long long)dr.caller);
        std::string vbs;
        for (const auto& a : p->vs->res.attribs) {
            const uint32_t* v = dr.vb[a.vb_slot & 15];
            char b[160];
            std::snprintf(b, sizeof b, " [%u: %llx stride %u n %u dfmt %u nfmt %u inst %u]", a.vb_slot,
                          (unsigned long long)(uint64_t(v[0]) | uint64_t(v[1] & 0xFFF) << 32), v[1] >> 16 & 0x3FFF, v[2],
                          v[3] >> 15 & 0xF, v[3] >> 12 & 7, a.index_vgpr);
            vbs += b;
        }
        for (const auto& b : p->vs->res.bindings)
            if (b.kind == gcn::Binding::ConstBuffer) {
                char t[96];
                std::snprintf(t, sizeof t, " cb%u=%llx/%u", b.api_slot, (unsigned long long)dr.cb[0][b.api_slot & 15].addr,
                              dr.cb[0][b.api_slot & 15].size);
                vbs += t;
            }
        if (!p->vs->res.attribs.empty()) {  // packed bone index in position.w (16_16_16_16 snorm)
            const uint32_t* v = dr.vb[p->vs->res.attribs[0].vb_slot & 15];
            const uint64_t base = uint64_t(v[0]) | uint64_t(v[1] & 0xFFF) << 32;
            const uint32_t stride = v[1] >> 16 & 0x3FFF;
            if ((v[3] >> 15 & 0xF) == 12 && (v[3] >> 12 & 7) == 1 && base >= 0x10000 && stride) {
                int mx = -1;
                for (uint32_t i = vfirst; i <= vlast && i < v[2]; ++i)
                    mx = std::max<int>(mx, reinterpret_cast<const int16_t*>(base + uint64_t(i) * stride)[3]);
                char t[48];
                std::snprintf(t, sizeof t, " maxw %d", mx);
                vbs += t;
            }
        }
        log("ng   attribs:%s", vbs.c_str());
        if (p->ps) {
            std::string ts;
            for (const auto& b : p->ps->res.bindings) {
                char t[256];
                if (b.kind == gcn::Binding::Texture) {
                    const uint32_t* T = dr.T(1, b.api_slot);
                    if (!T) continue;
                    const auto d = fmt::decode_tsharp(T);
                    // D1_NG_DUMP_TEX=<dir>: (testing) the T# and its guest memory, for offline decoding
                    if (const char* dir = std::getenv("D1_NG_DUMP_TEX")) {
                        static std::unordered_set<uint64_t> dumped;
                        tiling::Surface sf0;
                        const auto fi0 = fmt::data_format(d.dfmt);
                        sf0.tile_mode = d.tiling, sf0.bpp = fi0.bpp, sf0.block = fi0.block, sf0.pow2 = d.pow2;
                        sf0.width = d.width, sf0.height = d.height, sf0.pitch = d.pitch;
                        sf0.levels = std::min(d.last_level + 1, tiling::kMaxMips);
                        tiling::layout(sf0);
                        if (fi0.bpp && dumped.size() < 200 && dumped.insert(d.base).second &&
                            guest_region_extent(d.base) >= sf0.total_size) {
                            char path[512];
                            std::snprintf(path, sizeof path, "%s/tex_%llx.bin", dir, (unsigned long long)d.base);
                            if (FILE* f = std::fopen(path, "wb")) {
                                std::fwrite(dr.T(1, b.api_slot), 4, 8, f);
                                std::fwrite(reinterpret_cast<const void*>(d.base), 1, sf0.total_size, f);
                                std::fclose(f);
                            }
                        }
                    }
                    // zero blocks per mip (streaming not done / never loaded)
                    std::string zs;
                    const auto fi = fmt::data_format(d.dfmt);
                    if (fi.block && fi.bpp) {
                        tiling::Surface sf;
                        sf.tile_mode = d.tiling, sf.bpp = fi.bpp, sf.block = true, sf.pow2 = d.pow2;
                        sf.width = d.width, sf.height = d.height, sf.pitch = d.pitch;
                        sf.levels = std::min(d.last_level + 1, tiling::kMaxMips);
                        tiling::layout(sf);
                        if (guest_region_extent(d.base) >= sf.total_size)
                            for (uint32_t lv = 0; lv < sf.levels && lv < 4; ++lv) {
                                const uint8_t* m = reinterpret_cast<const uint8_t*>(d.base) + sf.mips[lv].offset;
                                const uint32_t bs = fi.bpp / 8;
                                uint64_t zero = 0, n = sf.mips[lv].size / bs;
                                for (uint64_t q = 0; q < n; ++q) {
                                    uint64_t acc = 0;
                                    for (uint32_t z = 0; z < bs; z += 8) acc |= *reinterpret_cast<const uint64_t*>(m + q * bs + z);
                                    zero += acc == 0;
                                }
                                char zb[24];
                                std::snprintf(zb, sizeof zb, "%s%llu%%", lv ? "," : "/z", (unsigned long long)(n ? zero * 100 / n : 0));
                                zs += zb;
                            }
                    }
                    std::snprintf(t, sizeof t, " t%u:%llx/%ux%u/f%u.%u/mips%u-%u/minlod%.2f/sel%03o%s", b.api_slot,
                                  (unsigned long long)d.base, d.width, d.height, d.dfmt, d.nfmt, d.base_level,
                                  d.last_level, d.min_lod / 256.0, d.dst_sel, zs.c_str());
                } else if (b.kind == gcn::Binding::Sampler) {
                    const uint32_t* S = dr.S(1, b.api_slot);
                    if (!S) continue;
                    std::snprintf(t, sizeof t, " s%u:%08x.%08x.%08x.%08x", b.api_slot, S[0], S[1], S[2], S[3]);
                } else {
                    const auto& c = dr.cb[1][b.api_slot & 15];
                    const float* fv = c.addr >= 0x10000 ? reinterpret_cast<const float*>(c.addr) : nullptr;
                    if (fv && c.size >= 32)
                        std::snprintf(t, sizeof t, " cb%u:%llx/%u[%g %g %g %g %g %g %g %g]", b.api_slot, (unsigned long long)c.addr,
                                      c.size, fv[0], fv[1], fv[2], fv[3], fv[4], fv[5], fv[6], fv[7]);
                    else
                        std::snprintf(t, sizeof t, " cb%u:%llx/%u", b.api_slot, (unsigned long long)c.addr, c.size);
                }
                ts += t;
            }
            log("ng   ps textures:%s", ts.c_str());
            if (debug_ps)
                for (const auto& b : p->ps->res.bindings) {
                    if (b.kind != gcn::Binding::ConstBuffer) continue;
                    const auto& c = dr.cb[1][b.api_slot & 15];
                    if (c.addr < 0x10000) continue;
                    const float* fv = reinterpret_cast<const float*>(c.addr);
                    std::string cs;
                    for (uint32_t i = 0; i < std::min<uint32_t>(c.size / 4, 128); ++i) {
                        char t[24];
                        std::snprintf(t, sizeof t, " %g", fv[i]);
                        cs += t;
                    }
                    log("ng   ps cb%u:%s", b.api_slot, cs.c_str());
                }
        }
    }
    if (!r.parallel && st.frames == passlog_frame && !passlog.empty()) {
        auto& pl = passlog.back();
        if (!pl.draws++) {
            pl.first_vs = uint64_t(dr.vs), pl.first_ps = uint64_t(dr.ps), pl.caller = dr.caller;
            if (p->ps)
                for (const auto& b : p->ps->res.bindings) {
                    if (b.kind != gcn::Binding::Texture) continue;
                    const uint32_t* t = dr.T(1, b.api_slot);
                    char buf[96];
                    if (!t) std::snprintf(buf, sizeof buf, " t%u:none", b.api_slot);
                    else {
                        const auto ts = fmt::decode_tsharp(t);
                        const bool rt = target_by_base.count(ts.base) != 0;
                        auto it = textures.find(hash_bytes(t, 32));
                        std::snprintf(buf, sizeof buf, " t%u:%s%llx/%ux%u/f%u.%u", b.api_slot,
                                      rt ? "RT" : (it != textures.end() && it->second) ? "tex" : "MISSING",
                                      (unsigned long long)ts.base, ts.width, ts.height, ts.dfmt, ts.nfmt);
                    }
                    pl.tex += buf;
                }
            if (p->ps && !p->ps->res.problems.empty()) pl.tex += " [" + p->ps->res.problems[0] + "]";
        }
    }
    // state the previous draw in this command buffer already set is not set again (bindings
    // and dynamic state last for the whole command buffer)
    DrawState& ds = *r.ds;
    if (!ds.valid || ds.pipe != p->pipeline) vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, p->pipeline), ds.pipe = p->pipeline;
    for (int s = 0; s < 2; ++s)
        if (nw[s] && s == 1 && p->push_ps) {
            push_fn(cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, p->layout, 1, nw[s], writes[s]);
        } else if (nw[s]) {
            VkDescriptorSet set;
            {
                auto lk = guard(set_m);
                set = alloc_set(p->sets[s]);
            }
            if (!set) return skip("descriptor pool");
            for (uint32_t k = 0; k < nw[s]; ++k) writes[s][k].dstSet = set;
            vkUpdateDescriptorSets(ctx.device, nw[s], writes[s], 0, nullptr);
            vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, p->layout, uint32_t(s), 1, &set, 0, nullptr);
        }
    if (!ds.valid) ds.vmask = 0;
    for (uint32_t slot = 0; slot < 16;) {  // runs of changed bindings, one call each
        auto same = [&](uint32_t k) {
            return !(vmask >> k & 1) || ((ds.vmask >> k & 1) && ds.vb[k] == vbufs[k] && ds.voff[k] == voffs[k] && ds.vsize[k] == vsizes[k]);
        };
        if (same(slot)) { ++slot; continue; }
        uint32_t end = slot + 1;
        while (end < 16 && (vmask >> end & 1) && !same(end)) ++end;
        vkCmdBindVertexBuffers2(cmd, slot, end - slot, &vbufs[slot], &voffs[slot], &vsizes[slot], nullptr);
        for (uint32_t k = slot; k < end; ++k) ds.vb[k] = vbufs[k], ds.voff[k] = voffs[k], ds.vsize[k] = vsizes[k], ds.vmask |= 1u << k;
        slot = end;
    }
    // viewport (GCN y points down the screen: flip with a negative height)
    VkViewport vp{};
    vp.x = float(dr.vp[0]), vp.width = float(dr.vp[2] > 0 ? dr.vp[2] : int32_t(rc().pass_w));
    vp.y = float(dr.vp[1] + (dr.vp[3] > 0 ? dr.vp[3] : int32_t(rc().pass_h)));
    vp.height = -float(dr.vp[3] > 0 ? dr.vp[3] : int32_t(rc().pass_h));
    const float range = dr.zfar - dr.znear;
    float zmin = range != 0 ? dr.znear / range : 0.0f, zmax = range != 0 ? zmin + dr.zk / range : 1.0f;
    vp.minDepth = std::clamp(zmin, 0.0f, 1.0f), vp.maxDepth = std::clamp(zmax, 0.0f, 1.0f);
    if (!ds.valid || std::memcmp(&ds.vp, &vp, sizeof vp) != 0) vkCmdSetViewport(cmd, 0, 1, &vp), ds.vp = vp;
    const int32_t sx = std::max(0, dr.vp[0]), sy = std::max(0, dr.vp[1]);
    VkRect2D sc{{sx, sy},
                {std::min<uint32_t>(rc().pass_w - std::min<uint32_t>(rc().pass_w, sx), uint32_t(std::max(1.0f, vp.width))),
                 std::min<uint32_t>(rc().pass_h - std::min<uint32_t>(rc().pass_h, sy), uint32_t(std::max(1.0f, -vp.height)))}};
    if (!ds.valid || std::memcmp(&ds.sc, &sc, sizeof sc) != 0) vkCmdSetScissor(cmd, 0, 1, &sc), ds.sc = sc;
    {
        uint32_t sref, swm;
        stencil_dynamic(dr.stencil_ctl, dr.depth_ctl, dr.stencil_ref, sref, swm);
        const uint32_t cmask = dr.stencil_ref >> 8 & 0xFF;
        if (!ds.valid || ds.sref != sref) vkCmdSetStencilReference(cmd, VK_STENCIL_FACE_FRONT_AND_BACK, sref), ds.sref = sref;
        if (!ds.valid || ds.cmask != cmask) vkCmdSetStencilCompareMask(cmd, VK_STENCIL_FACE_FRONT_AND_BACK, cmask), ds.cmask = cmask;
        if (!ds.valid || ds.wmask != swm) vkCmdSetStencilWriteMask(cmd, VK_STENCIL_FACE_FRONT_AND_BACK, swm), ds.wmask = swm;
    }
    if (!ds.valid || ds.bias[0] != dr.poly_offset || ds.bias[1] != dr.poly_scale)
        vkCmdSetDepthBias(cmd, dr.poly_offset, 0.0f, dr.poly_scale), ds.bias[0] = dr.poly_offset, ds.bias[1] = dr.poly_scale;
    if (!ds.valid) ds.ib = VK_NULL_HANDLE;
    ds.valid = true;
    const bool predicated = rc().pred_cur >= 0 && ctx.conditional_rendering && pred_buf.buf;
    if (predicated) {
        VkConditionalRenderingBeginInfoEXT cr{VK_STRUCTURE_TYPE_CONDITIONAL_RENDERING_BEGIN_INFO_EXT};
        cr.buffer = pred_buf.buf;
        cr.offset = uint64_t(rc().pred_cur) * 4;
        cr.flags = rc().pred_invert ? VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT : 0;
        vkCmdBeginConditionalRenderingEXT(cmd, &cr);
        ++r.predicated;
    }
    if (indexed) {
        if (ds.ib != index_buf || ds.ioff != ioff || ds.itype != itype)
            vkCmdBindIndexBuffer(cmd, index_buf, ioff, itype), ds.ib = index_buf, ds.ioff = ioff, ds.itype = itype;
        vkCmdDrawIndexed(cmd, count, std::max(1u, dr.instances), 0, -int32_t(vfirst), 0);
    } else {
        vkCmdDraw(cmd, count, std::max(1u, dr.instances), 0, 0);
    }
    if (predicated) vkCmdEndConditionalRenderingEXT(cmd);
    ++r.draws;
    // D1_NG_DRAWSTATS: (diagnostics) per logged frame, draws and instances per shader pair
    static const bool drawstats = std::getenv("D1_NG_DRAWSTATS") != nullptr;
    if (!r.parallel && drawstats && st.frames == passlog_frame) {
        auto& e = frame_draws[uint64_t(dr.ps) ^ uint64_t(dr.vs) << 20];
        e.first += 1, e.second += std::max(1u, dr.instances) * uint64_t(count);
    }
    // D1_NG_TRACE=<target base hex>,<x>,<y>,<w>: (testing) in the logged frame, a row of that
    // target's pixels after every draw into it, to find which draw writes what
    static const struct Trace { uint64_t base = 0; uint32_t x = 0, y = 0, w = 0, h = 1; } trace = [] {
        Trace t;
        if (const char* e = std::getenv("D1_NG_TRACE"))
            std::sscanf(e, "%llx,%u,%u,%u,%u", reinterpret_cast<unsigned long long*>(&t.base), &t.x, &t.y, &t.w, &t.h);
        return t;
    }();
    if (!r.parallel && trace.base && st.frames == passlog_frame)
        for (int i = 0; i < 8; ++i)
            if (colors[i] && colors[i]->base == trace.base && trace.x + trace.w <= colors[i]->w && trace.y + trace.h <= colors[i]->h &&
                colors[i]->bpp && traces.size() < 4000) {
                end_pass();
                const uint32_t bytes = colors[i]->bpp / 8;
                const uint64_t off = ring_alloc(uint64_t(trace.w) * trace.h * bytes, 16);
                if (off == UINT64_MAX) break;
                VkBufferImageCopy r{};
                r.bufferOffset = off;
                r.imageSubresource = {VK_IMAGE_ASPECT_COLOR_BIT, 0, 0, 1};
                r.imageOffset = {int32_t(trace.x), int32_t(trace.y), 0};
                r.imageExtent = {trace.w, trace.h, 1};
                vkCmdCopyImageToBuffer(cmd, colors[i]->image, VK_IMAGE_LAYOUT_GENERAL, ring.buf, 1, &r);
                barrier();
                traces.push_back({uint64_t(dr.ps), uint64_t(dr.vs), dr.caller, off, bytes, trace.w * trace.h, dr.blend, dr.count});
                break;
            }
    lap(r.t_cmd);
}

// Resources first (copies cannot run inside a render pass): targets, then textures (each
// distinct target set and T# once per recording: thousands of draws share a few).
void Renderer::pre_pass(const std::vector<Draw*>& draws) {
    const uint64_t tp = now_ns();
    apply_cpu_writes();
    if (reload_all) {
        reload_all = false;
        for (auto& [k, img] : textures)
            bury(std::move(img));
        textures.clear(); ++views_gen;
        log("native renderer: dropped every texture (D1_NG_SNAP_RELOAD)");
    }
    // resources first (copies cannot run inside a render pass): targets, then textures
    // (each distinct target set and T# once per submission: thousands of draws share a few)
    const uint64_t t_tgt0 = now_ns();
    const Draw* prev_d = nullptr;
    for (Draw* d : draws) {
        if (prev_d && std::memcmp(prev_d->color, d->color, sizeof d->color) == 0 &&
            std::memcmp(prev_d->depth, d->depth, sizeof d->depth) == 0)
            continue;
        prev_d = d;
        for (int i = 0; i < 5; ++i) color_target(d->color[i], false);
        depth_target(d->depth, false);
    }
    st.t_tgt += now_ns() - t_tgt0;
    struct Seen { uint64_t key, sub; };
    static std::vector<Seen> seen(1u << 13);
    for (Draw* d : draws)
        for (int s = 0; s < 2; ++s)
            for (int i = 0; i < 16; ++i)
                if (const uint32_t* t = d->T(s, i)) {
                    const uint64_t k = hash_bytes(t, 32) ^ d->tex_res[s][i];
                    Seen& e = seen[k & (seen.size() - 1)];
                    if (e.key == k && e.sub == rc().submit_no) continue;
                    e = {k, rc().submit_no};
                    const uint64_t b = fmt::decode_tsharp(t).base;
                    const bool is_target = target_bases.count(b) != 0;
                    if (is_target) tsharp_bases.insert(b);  // (only render target addresses matter there)
                    if (!is_target || !target_current(b)) upload_texture(t, d->tex_res[s][i]);
                }
    barrier();
    st.t_pre += now_ns() - tp;
}

void Renderer::execute(const std::vector<Draw*>& draws) {
    if (up_rec.cur != UINT32_MAX && !tr) {  // uploads for lists recorded on engine threads go first
        tr = &up_rec;
        submit();
        tr = nullptr;
    }
    // D1_NG_PASSLOG=world: log the frame after the first big (in-world) submission, plus 3
    if (passlog_frame == UINT64_MAX - 1 && draws.size() > 2000) passlog_frame = st.frames + 3;
    rc().submit_no = ++submit_seq;
    ++st.submits;
    retire_completed();
    begin_record();
    run_copies(draws);
    pre_pass(draws);
    rc().q_on = false;
    for (Draw* d : draws) rc().q_on |= d->kind == Draw::ZPass;
    if (rc().q_on) {
        Sub& sb = subs[rc().cur];
        if (!sb.qpool) {
            VkQueryPoolCreateInfo qci{VK_STRUCTURE_TYPE_QUERY_POOL_CREATE_INFO};
            qci.queryType = VK_QUERY_TYPE_OCCLUSION;
            qci.queryCount = kQueries;
            vkCreateQueryPool(ctx.device, &qci, nullptr, &sb.qpool);
        }
        if (sb.qpool) {
            end_pass();  // (resets happen outside render passes)
            vkCmdResetQueryPool(rc().cmd, sb.qpool, 0, kQueries);
        } else rc().q_on = false;
    }
    for (size_t i = 0; i < draws.size(); ++i) {
        Draw* d = draws[i];
        switch (d->kind) {
        case Draw::Clear: clear(*d); break;
        case Draw::ZPass: zpass(d->index_addr); break;
        case Draw::PredOn: predicate(d->index_addr, d->count & 1); break;
        case Draw::PredOff: rc().pred_cur = -1; break;
        case Draw::Dma: break;  // (done before the textures: run_copies)
        case Draw::Eop: break;  // (the device layer raises the event after the submission)
        case Draw::WriteData:
            if (d->caller >= 0x10000 && guest_region_extent(d->caller) >= d->inline_vertices.size())
                std::memcpy(reinterpret_cast<void*>(d->caller), d->inline_vertices.data(), d->inline_vertices.size());
            break;
        default: {
            // a run of plain draws into the same targets: recorded in parallel
            size_t j = i + 1;
            if (rec_threads && !debug && st.frames != passlog_frame) {
                auto plain = [&](const Draw* x) {
                    return (x->kind == Draw::Indexed || x->kind == Draw::Auto) && std::memcmp(x->color, d->color, sizeof d->color) == 0 &&
                           std::memcmp(x->depth, d->depth, sizeof d->depth) == 0;
                };
                while (j < draws.size() && plain(draws[j])) ++j;
            }
            if (j - i >= rec_min_run) {
                run_parallel(draws.data() + i, j - i);
                i = j - 1;
            } else {
                draw(*d);
            }
            break;
        }
        }
    }
    end_pass();
    rc().pred_cur = -1;
    if (rc().q_on) store_query_predicates();
    rc().q_on = false;
    queue_readbacks();
    // Results the game reads back (small targets, occlusion counts) reach guest memory when
    // the work completes, a frame or two later - about what the console's GPU latency is.
    // D1_NG_READBACK_SYNC=1 waits for them here instead (the CPU then waits for the GPU at that
    // point every frame, which costs a lot of frame rate on slower GPUs).
    static const bool rb_sync = [] {
        const char* v = std::getenv("D1_NG_READBACK_SYNC");
        return v && std::atoi(v) != 0;
    }();
    // occlusion counts too: the game reads them back (object visibility), and the null GPU no
    // longer answers for executed submissions
    const bool has_rb = rc().cur != UINT32_MAX && (!subs[rc().cur].readbacks.empty() || !subs[rc().cur].zrecs.empty());
    if (has_rb && std::getenv("D1_NG_LOG_READBACK")) {
        static int n = 0;
        if (n++ < 40)
            log("ng readback sync: submission %llu of the frame, %zu draws, %zu readbacks, %zu counter dumps",
                (unsigned long long)(rc().submit_no - frame_first_submit), draws.size(), subs[rc().cur].readbacks.size(),
                subs[rc().cur].zrecs.size());
    }
    submit();
    if ((rb_sync != bool(debug_toggles() & 2)) && has_rb && !inflight.empty()) wait_serial(subs[inflight.back()].serial);
}

// ---------------------------------------------------------------------------- loader
// Engine resources are prepared when the engine binds or moves them, on this thread: textures
// are detiled without the renderer's lock and committed (image, staging copy in the shared
// upload slot) under it; buffers go to the geometry cache. A job whose resource changed again
// (another epoch) before it was done is dropped. Draws that need a resource first still
// upload it themselves; the loader then finds it done.
void Renderer::start_loader() {
    const char* v = std::getenv("D1_NG_PREFETCH");
    load_on = (!v || std::atoi(v) != 0) && opt.res_current != nullptr;
    if (!load_on) return;
    loader = std::thread([this] {
        for (;;) {
            LoadJob j;
            {
                std::unique_lock lk(load_m);
                load_cv.wait(lk, [&] { return !load_q.empty(); });
                j = load_q.front();
                load_q.pop_front();
            }
            const uint64_t t0 = now_ns();
            if (opt.res_current(j.obj) != j.res) ++ld_stale;
            else if (j.tex) load_texture(j);
            else load_buffer(j);
            ld_ns += now_ns() - t0;
        }
    });
    loader.detach();
    log("native renderer: engine resources are uploaded when the engine loads or moves them (D1_NG_PREFETCH=0: at first use)");
}

void Renderer::load_buffer(const LoadJob& j) {
    if (j.base < 0x10000 || !j.size || j.size >= (64ull << 20) || guest_region_extent(j.base) < j.size) return;
    if (geo_lookup_res(j.base, j.size, 0, 0, j.res, j.base)) ++ld_buf;
}

void Renderer::load_texture(const LoadJob& j) {
    const uint32_t* t = j.t;
    const auto ts = fmt::decode_tsharp(t);
    const auto fi = fmt::data_format(ts.dfmt);
    const VkFormat f = fmt::vk_format(ts.dfmt, ts.nfmt);
    if (f == VK_FORMAT_UNDEFINED || !fi.bpp || fi.bpp == 96 || !ts.base || ts.width > 16384 || ts.height > 16384) return;
    tiling::Surface sf;
    sf.tile_mode = ts.tiling, sf.bpp = fi.bpp, sf.block = fi.block, sf.pow2 = ts.pow2;
    sf.width = ts.width, sf.height = ts.height, sf.pitch = ts.pitch;
    const bool is3d = ts.type == 10, cube = ts.type == 11;
    sf.depth = is3d ? ts.depth : 1;
    sf.layers = (ts.type == 13 || ts.type == 12 || cube) ? ts.last_array + 1 : 1;
    if (cube) sf.layers = std::max(6u, sf.layers - sf.layers % 6);
    sf.levels = std::min(ts.last_level + 1, tiling::kMaxMips);
    tiling::layout(sf);
    if (guest_region_extent(ts.base) < sf.total_size) return;
    const uint64_t key = tex_key(t, j.res);
    const uint64_t content = hash_bytes(reinterpret_cast<const void*>(ts.base), sf.total_size);
    {  // done already, or moved with the same contents
        std::lock_guard lk(m);
        if (target_bases.count(ts.base)) return;  // (render target memory: the draws decide)
        auto it = textures.find(key);
        if (it != textures.end() && it->second) {
            Image* img = it->second.get();
            if (img->res_val == j.res) { ++ld_skipped; return; }
            if (img->content == content && img->src_size == sf.total_size) {
                img->res_val = j.res, img->src_addr = ts.base;
                ++ld_moves;
                return;
            }
        }
    }
    // detiled here, without the lock
    std::vector<uint64_t> sizes(sf.levels), level_off(sf.levels);
    uint64_t total = 0;
    for (uint32_t lv = 0; lv < sf.levels; ++lv) {
        const uint32_t mw = std::max(1u, ts.width >> lv), mh = std::max(1u, ts.height >> lv);
        const uint32_t ew = fi.block ? (mw + 3) / 4 : mw, eh = fi.block ? (mh + 3) / 4 : mh;
        sizes[lv] = uint64_t(ew) * eh * (fi.bpp / 8) * std::max(1u, is3d ? std::max(1u, sf.depth >> lv) : sf.layers);
        level_off[lv] = total;
        total += (sizes[lv] + 15) & ~15ull;
    }
    static thread_local std::vector<uint8_t> scratch;
    scratch.resize(total);
    const uint32_t missing = first_missing_mip(ts, fi, sf, is3d);
    for (uint32_t lv = 0; lv < std::min(missing, sf.levels); ++lv)
        tiling::detile(sf, lv, reinterpret_cast<const uint8_t*>(ts.base), scratch.data() + level_off[lv]);
    if (missing < sf.levels) fill_missing_mips(missing, scratch.data(), level_off, sizes, ts, fi, sf, is3d);
    // changed meanwhile (moved again, or still being written): the next event or the draws redo it
    if (opt.res_current(j.obj) != j.res || hash_bytes(reinterpret_cast<const void*>(ts.base), sf.total_size) != content) {
        ++ld_stale;
        return;
    }
    std::lock_guard lk(m);
    auto it = textures.find(key);
    if (it != textures.end() && it->second && it->second->res_val == j.res) { ++ld_skipped; return; }
    // (into the shared upload slot: the image's layout set-up is recorded too)
    Recorder* const prev_tr = tr;
    struct Restore { Recorder* p; ~Restore() { tr = p; } } restore{prev_tr};
    tr = &up_rec;
    up_rec.lr = true;
    up_rec.submit_no = submit_seq.load();
    begin_record();
    if (up_rec.cur == UINT32_MAX) return;
    auto img = make_image(f, ts.width, ts.height, sf.depth, sf.layers, sf.levels, cube, is3d, false, false);
    if (!img) return;
    Buffer sb;
    uint64_t base_off = ring_alloc(std::max<uint64_t>(total, 16), 256);
    const bool own = base_off == UINT64_MAX;
    if (!own) sb = ring, sb.map = ring.map + base_off;
    else sb = make_buffer(std::max<uint64_t>(total, 16), VK_BUFFER_USAGE_TRANSFER_SRC_BIT, true), base_off = 0;
    if (!sb.map) { destroy_image(img.get()); return; }
    std::memcpy(sb.map, scratch.data(), total);
    std::vector<VkBufferImageCopy> regions;
    for (uint32_t lv = 0; lv < sf.levels; ++lv) {
        VkBufferImageCopy r{};
        r.bufferOffset = base_off + level_off[lv];
        r.imageSubresource = {VK_IMAGE_ASPECT_COLOR_BIT, lv, 0, is3d ? 1u : sf.layers};
        r.imageExtent = {std::max(1u, ts.width >> lv), std::max(1u, ts.height >> lv), is3d ? std::max(1u, sf.depth >> lv) : 1u};
        regions.push_back(r);
    }
    vkCmdCopyBufferToImage(up_rec.cmd, sb.buf, img->image, VK_IMAGE_LAYOUT_GENERAL, uint32_t(regions.size()), regions.data());
    barrier();
    if (own) subs[up_rec.cur].staging.push_back(sb);
    img->res_val = j.res, img->src_addr = ts.base, img->src_size = sf.total_size, img->content = content, img->version = ~0ull;
    img->last_used = submit_seq.load();
    if (it != textures.end()) bury(std::move(it->second));
    textures[key] = std::move(img);
    ++views_gen;
    st.bytes_tex += total;
    ++st.textures;
    ++ld_tex;
}

// ---------------------------------------------------------------------------- lists on engine threads
// A command list recorded on the thread that ended it, into a submission slot of its own. The
// renderer's lock (m) is held for everything that changes shared state - texture uploads and
// target set-up (into the shared upload slot, submitted before any list that follows), pass
// changes, clears, queries, readbacks - and released for runs of plain draws, which take it
// only for cache misses. Recorded slots wait for submit_recorded, in the engine's order.
bool Renderer::record_list(const std::vector<Draw*>& items, uint32_t& handle, std::vector<LateCb>& late) {
    static thread_local Recorder R;
    Recorder* const prev_tr = tr;
    R.lr = true;
    tr = &R;
    struct Restore { Recorder* p; ~Restore() { tr = p; } } restore{prev_tr};
    const uint64_t t_start = now_ns();
    std::unique_lock lk(m, std::defer_lock);
    uint64_t waited = 0;
    auto relock = [&] {
        const uint64_t t = now_ns();
        lk.lock();
        waited += now_ns() - t;
    };
    relock();
    struct Account {
        Renderer* g; const uint64_t& t0; const uint64_t& w;
        ~Account() { g->lr_ns += now_ns() - t0, g->lr_wait_ns += w, ++g->lr_lists; }
    } account{this, t_start, waited};
    R.submit_no = ++submit_seq;
    ++st.submits;
    retire_completed();
    begin_record();
    if (R.cur == UINT32_MAX) return false;  // no free slot: executed at submission instead
    for (auto& row : R.late)
        for (auto& l : row) l = {};
    R.late_list.clear();
    R.copies.clear();
    R.q_on = false;
    R.pred_cur = -1;
    // uploads and new targets into the shared slot
    tr = &up_rec;
    up_rec.lr = true;
    up_rec.submit_no = R.submit_no;
    begin_record();
    run_copies(items);
    if (up_rec.cur != UINT32_MAX) pre_pass(items);
    tr = &R;
    for (const Draw* d : items) R.q_on |= d->kind == Draw::ZPass;
    if (R.q_on) {
        Sub& sb = subs[R.cur];
        if (!sb.qpool) {
            VkQueryPoolCreateInfo qci{VK_STRUCTURE_TYPE_QUERY_POOL_CREATE_INFO};
            qci.queryType = VK_QUERY_TYPE_OCCLUSION;
            qci.queryCount = kQueries;
            vkCreateQueryPool(ctx.device, &qci, nullptr, &sb.qpool);
        }
        if (sb.qpool) vkCmdResetQueryPool(R.cmd, sb.qpool, 0, kQueries);
        else R.q_on = false;
    }
    Rec run_rec;  // (plain draws: one ring chunk stream for the whole list)
    run_rec.cmd = R.cmd, run_rec.ds = &R.dstate, run_rec.parallel = true;
    for (size_t i = 0; i < items.size(); ++i) {
        Draw* d = items[i];
        switch (d->kind) {
        case Draw::Clear: clear(*d); break;
        case Draw::ZPass: zpass(d->index_addr); break;
        case Draw::PredOn: predicate(d->index_addr, d->count & 1); break;
        case Draw::PredOff: R.pred_cur = -1; break;
        case Draw::Dma: break;  // (done before the list's textures: run_copies; repeated at submission)
        case Draw::Eop:
        case Draw::WriteData: break;  // (CPU-visible: done at submission)
        default: {
            // a run of plain draws into the same targets: recorded without the lock
            size_t j = i + 1;
            auto plain = [&](const Draw* x) {
                return (x->kind == Draw::Indexed || x->kind == Draw::Auto) && std::memcmp(x->color, d->color, sizeof d->color) == 0 &&
                       std::memcmp(x->depth, d->depth, sizeof d->depth) == 0;
            };
            while (j < items.size() && plain(items[j])) ++j;
            Image* colors[8] = {};
            for (int k = 0; k < 5; ++k) colors[k] = color_target(d->color[k]);
            Image* depth = depth_target(d->depth);
            if (!depth && std::none_of(colors, colors + 8, [](Image* x) { return x != nullptr; })) {
                for (size_t k = i; k < j; ++k) skip("no target");
                i = j - 1;
                break;
            }
            feedback_snapshots(items.data() + i, j - i, colors, depth);
            begin_pass(colors, depth);
            lk.unlock();
            for (size_t k = i; k < j; ++k) draw(*items[k], run_rec, colors, depth);
            relock();
            i = j - 1;
            break;
        }
        }
    }
    merge(run_rec);
    end_pass();
    R.pred_cur = -1;
    if (R.q_on) store_query_predicates();
    R.q_on = false;
    queue_readbacks();
    vkEndCommandBuffer(R.cmd);
    subs[R.cur].state = Sub::Recorded;
    subs[R.cur].copies.clear();
    for (const auto& c : R.copies) subs[R.cur].copies.push_back({c.kind, c.addr, c.size, c.hash});
    handle = R.cur;
    late = R.late_list;
    R.cur = UINT32_MAX, R.cmd = VK_NULL_HANDLE;
    return true;
}

// The recorded lists of one submission, after the shared upload slot.
void Renderer::submit_recorded(const std::vector<uint32_t>& handles) {
    const uint64_t t0 = now_ns();
    struct Account { Renderer* g; uint64_t t0; ~Account() { g->lr_sub_ns += now_ns() - t0; } } account{this, t0};
    if (up_rec.cur != UINT32_MAX) {
        Recorder* const prev_tr = tr;
        tr = &up_rec;
        submit();
        tr = prev_tr;
    }
    if (verify_late()) {
        static int told = 0;
        for (uint32_t h : handles)
            if (h < subs.size())
                for (const auto& c : subs[h].copies) {
                    const bool same = hash_bytes(reinterpret_cast<const void*>(c[1]), c[2]) == c[3];
                    ++late_checked[c[0]], late_changed[c[0]] += !same;
                    if (!same && told++ < 40)
                        log("native renderer: %s at %#llx (%llu bytes) changed between the list's end and its submission",
                            c[0] == 0 ? "constants" : c[0] == 1 ? "vertices" : "indices", (unsigned long long)c[1], (unsigned long long)c[2]);
                }
        static uint64_t n = 0;
        if (++n % 600 == 0)
            log("native renderer: copies changed between list end and submission: constants %llu of %llu, vertices %llu of %llu, indices %llu of %llu",
                (unsigned long long)late_changed[0], (unsigned long long)late_checked[0], (unsigned long long)late_changed[1],
                (unsigned long long)late_checked[1], (unsigned long long)late_changed[2], (unsigned long long)late_checked[2]);
    }
    for (uint32_t h : handles)
        if (h < subs.size() && subs[h].state == Sub::Recorded) submit_sub(h);
    retire_completed();
}

void Renderer::discard_recorded(uint32_t h) {
    if (h >= subs.size() || subs[h].state != Sub::Recorded) return;
    Sub& sb = subs[h];
    sb.readbacks.clear(), sb.rb_used = 0, sb.zrecs.clear(), sb.q_used = 0;
    for (auto& b : sb.staging) free_buffer(b);
    sb.staging.clear();
    sb.state = Sub::Idle;
    idle_subs.push_back(h);
    reap();
}

// False when the CPU has written a small render target's memory since the GPU rendered it:
// the game reuses the memory for data it writes itself (the 32x32 light tables at
// 0x579214000.. are rendered to some frames and written by the CPU in others), so the T# must
// read the memory again. The address stops counting as a render target until it is rendered.
bool Renderer::target_current(uint64_t base) {
    auto it = target_by_base.find(base);
    if (it == target_by_base.end()) return true;
    Image* img = it->second;
    if (img->depth || img->tv_version == ~0ull || (!opt.version && !dynamic_copy) || mem_version(base, img->tv_size) == img->tv_version)
        return true;
    target_by_base.erase(it);
    (++targets_gen, ++gen_why[4]);
    target_bases.erase(base);
    img->tv_version = ~0ull, img->tv_frame = 0;
    ++st.target_writes;
    return false;
}

// ---------------------------------------------------------------------------- occlusion
// The game counts samples that pass the depth test with ZPASS_DONE dumps (8 DB counters,
// 16 bytes apart: begin at +0, end at +8 of a query's results) and either reads the counts or
// predicates draws on them (SET_PREDICATION: lens flares and light halos behind walls). One
// Vulkan occlusion query counts each stretch of draws between two dumps; at a dump the
// counter is the sum of the stretches so far. Predicates for conditional rendering are copied
// from the query between a begin and an end dump into a slot per query address.
void Renderer::q_begin() {
    if (!rc().q_on || rc().q_active >= 0 || !rc().in_pass) return;
    Sub& sb = subs[rc().cur];
    if (sb.q_used >= kQueries) return;
    vkCmdBeginQuery(rc().cmd, sb.qpool, sb.q_used, ctx.occlusion_precise ? VK_QUERY_CONTROL_PRECISE_BIT : 0);
    rc().q_active = int32_t(sb.q_used++);
}

void Renderer::q_end() {
    if (rc().q_active < 0) return;
    vkCmdEndQuery(rc().cmd, subs[rc().cur].qpool, uint32_t(rc().q_active));
    rc().q_active = -1;
}

void Renderer::zpass(uint64_t dest) {
    if (!rc().q_on) return;
    Sub& sb = subs[rc().cur];
    uint32_t boundary;
    if (rc().q_active >= 0) {
        q_end();
        boundary = sb.q_used;
        q_begin();
    } else {
        boundary = sb.q_used;
    }
    sb.zrecs.push_back({dest, boundary});
    ++st.zpass_dumps;
}

uint32_t Renderer::pred_slot(uint64_t base) {
    auto it = pred_slots.find(base);
    if (it != pred_slots.end()) return it->second;
    if (pred_slots.size() >= kPredSlots) pred_slots.clear();  // (reused from the start)
    const uint32_t slot = uint32_t(pred_slots.size());
    pred_slots[base] = slot;
    return slot;
}

// Copies the predicate for the query at `base` (begin and end dumped in this submission) into
// its slot: the one query between the two dumps, 0 when no draw ran between them, and
// "visible" when the stretch spans several queries (render pass changes).
static bool query_span(const std::vector<Sub::ZRec>& zr, uint64_t base, uint32_t& b0, uint32_t& b1) {
    for (size_t i = zr.size(); i-- > 0;)
        if (zr[i].dest == base + 8) {
            for (size_t j = i; j-- > 0;)
                if (zr[j].dest == base) {
                    b0 = zr[j].boundary, b1 = zr[i].boundary;
                    return true;
                }
            return false;
        }
    return false;
}

void Renderer::predicate(uint64_t base, bool draw_if_visible) {
    rc().pred_cur = -1;
    if (!ctx.conditional_rendering) return;
    if (!pred_buf.buf) {
        pred_buf = make_buffer(kPredSlots * 4, VK_BUFFER_USAGE_TRANSFER_DST_BIT | VK_BUFFER_USAGE_CONDITIONAL_RENDERING_BIT_EXT, false);
        if (!pred_buf.buf) return;
    }
    Sub& sb = subs[rc().cur];
    uint32_t b0 = 0, b1 = 0;
    if (rc().q_on && query_span(sb.zrecs, base, b0, b1)) {
        const uint32_t slot = pred_slot(base);
        end_pass();  // (copies run outside render passes; the next draw starts a new one)
        if (b1 - b0 == 1)
            vkCmdCopyQueryPoolResults(rc().cmd, sb.qpool, b0, 1, pred_buf.buf, uint64_t(slot) * 4, 4, VK_QUERY_RESULT_WAIT_BIT);
        else
            vkCmdFillBuffer(rc().cmd, pred_buf.buf, uint64_t(slot) * 4, 4, b1 == b0 ? 0u : 1u);
        barrier();
        rc().pred_cur = int32_t(slot);
    } else if (auto it = pred_slots.find(base); it != pred_slots.end()) {
        rc().pred_cur = int32_t(it->second);  // from an earlier submission (store_query_predicates)
    } else {
        return;  // never counted: draw
    }
    rc().pred_invert = !draw_if_visible;
    static const bool log_q = std::getenv("D1_NG_LOG_QUERIES") != nullptr;
    static int n = 0;
    if (log_q && n++ < 400) log("ng predicate %llx: draw if %s", (unsigned long long)base, draw_if_visible ? "visible" : "hidden");
}

// At the end of a submission: predicates of the queries it completed, for later submissions.
void Renderer::store_query_predicates() {
    if (!ctx.conditional_rendering) return;
    Sub& sb = subs[rc().cur];
    if (!pred_buf.buf)
        pred_buf = make_buffer(kPredSlots * 4, VK_BUFFER_USAGE_TRANSFER_DST_BIT | VK_BUFFER_USAGE_CONDITIONAL_RENDERING_BIT_EXT, false);
    if (!pred_buf.buf) return;
    bool any = false;
    for (const auto& z : sb.zrecs) {
        if ((z.dest & 15) != 0) continue;  // begins
        uint32_t b0, b1;
        if (!query_span(sb.zrecs, z.dest, b0, b1)) continue;
        const uint32_t slot = pred_slot(z.dest);
        if (b1 - b0 == 1)
            vkCmdCopyQueryPoolResults(rc().cmd, sb.qpool, b0, 1, pred_buf.buf, uint64_t(slot) * 4, 4, VK_QUERY_RESULT_WAIT_BIT);
        else
            vkCmdFillBuffer(rc().cmd, pred_buf.buf, uint64_t(slot) * 4, 4, b1 == b0 ? 0u : 1u);
        any = true;
    }
    if (any) barrier();
}

// When the submission is done: every dump's counter into guest memory (DB 0 carries the count,
// DBs 1-7 zero; bit 63: valid), where the game reads them.
void Renderer::write_zpass_results(Sub& sb) {
    if (sb.zrecs.empty() && !sb.q_used) return;
    std::vector<uint64_t> res(sb.q_used, 0);
    if (sb.q_used)
        vkGetQueryPoolResults(ctx.device, sb.qpool, 0, sb.q_used, res.size() * 8, res.data(), 8,
                              VK_QUERY_RESULT_64_BIT | VK_QUERY_RESULT_WAIT_BIT);
    std::vector<uint64_t> prefix(sb.q_used + 1, 0);
    for (uint32_t i = 0; i < sb.q_used; ++i) prefix[i + 1] = prefix[i] + res[i];
    for (const auto& z : sb.zrecs) {
        if (z.dest < 0x10000 || guest_region_extent(z.dest) < 8 * 16) continue;
        auto* r = reinterpret_cast<volatile uint64_t*>(z.dest);
        const uint64_t v = (zcount_base + prefix[std::min<uint32_t>(z.boundary, sb.q_used)]) & 0x7FFFFFFFFFFFFFFFull;
        for (int k = 0; k < 8; ++k) r[k * 2] = (k == 0 ? v : 0) | 0x8000000000000000ull;
    }
    // D1_NG_LOG_QUERIES: (diagnostics) each query's sample count
    static const bool log_q = std::getenv("D1_NG_LOG_QUERIES") != nullptr;
    if (log_q) {
        static int n = 0;
        for (const auto& z : sb.zrecs) {
            uint32_t b0, b1;
            if ((z.dest & 15) || !query_span(sb.zrecs, z.dest, b0, b1) || n >= 400) continue;
            ++n;
            log("ng query %llx: %llu samples (%u stretches)", (unsigned long long)z.dest,
                (unsigned long long)(prefix[std::min(b1, sb.q_used)] - prefix[std::min(b0, sb.q_used)]), b1 - b0);
        }
    }
    zcount_base += prefix[sb.q_used];
    sb.q_used = 0;
    sb.zrecs.clear();
}

// Small render targets that no draw samples are results the CPU reads back (the depth
// reduction at 0x579200000 that fits the shadow cascades, for one): the game would find them
// in guest memory once the GPU is done, so copy them there when this submission completes.
// D1_NG_READBACK=<max pixels> (default 4096; 0 off).
void Renderer::queue_readbacks() {
    static const uint64_t max_pix = [] {
        const char* v = std::getenv("D1_NG_READBACK");
        return v ? std::strtoull(v, nullptr, 10) : 4096ull;
    }();
    if (!max_pix || (debug_toggles() & 4)) return;
    bool any = false;
    for (auto& [k, up] : targets) {
        Image* img = up.get();
        // only memory used for nothing else: one target there, never sampled or read as a texture
        if (!img || img->last_used != rc().submit_no || img->depth || img->is3d || img->swap || !img->bpp || img->bpp % 8 ||
            uint64_t(img->w) * img->h > max_pix || !img->base)
            continue;
        if (img->sampled || sampled_bases.count(img->base) || base_targets[img->base] != 1 || tsharp_bases.count(img->base)) {
            static std::unordered_set<uint64_t> told;
            if (std::getenv("D1_NG_LOG_READBACK") && told.insert(img->base).second)
                log("native renderer: not reading back %llx %ux%u: sampled %d/%d, targets %u, T# %d", (unsigned long long)img->base,
                    img->w, img->h, int(img->sampled), int(sampled_bases.count(img->base)), base_targets[img->base],
                    int(tsharp_bases.count(img->base)));
            continue;
        }
        tiling::Surface sf;
        sf.tile_mode = img->tile_mode, sf.bpp = img->bpp, sf.width = img->w, sf.height = img->h, sf.pitch = img->pitch;
        tiling::layout(sf);
        const uint64_t bytes = uint64_t(img->w) * img->h * (img->bpp / 8);
        Sub& sb = subs[rc().cur];
        constexpr uint64_t kReadbackBytes = 4ull << 20;
        if (!sb.rb.buf) sb.rb = make_readback_buffer(kReadbackBytes);
        const uint64_t off = (sb.rb_used + 255) & ~255ull;
        if (!sb.rb.map || off + bytes > kReadbackBytes) break;
        sb.rb_used = off + bytes;
        if (!any) barrier(), any = true;
        VkBufferImageCopy r{};
        r.bufferOffset = off;
        r.imageSubresource = {VK_IMAGE_ASPECT_COLOR_BIT, 0, 0, 1};
        r.imageExtent = {img->w, img->h, 1};
        vkCmdCopyImageToBuffer(rc().cmd, img->image, VK_IMAGE_LAYOUT_GENERAL, sb.rb.buf, 1, &r);
        sb.readbacks.push_back({img->base, sf, off});
        static std::unordered_set<uint64_t> seen;
        if (seen.size() < 64 && seen.insert(img->base ^ uint64_t(img->w) << 40 ^ uint64_t(img->h) << 52).second)
            log("native renderer: reading back target %llx %ux%u (format %d, tile mode %u) to guest memory",
                (unsigned long long)img->base, img->w, img->h, int(img->format), img->tile_mode);
    }
    if (any) {
        VkMemoryBarrier2 mb{VK_STRUCTURE_TYPE_MEMORY_BARRIER_2};
        mb.srcStageMask = VK_PIPELINE_STAGE_2_COPY_BIT, mb.srcAccessMask = VK_ACCESS_2_TRANSFER_WRITE_BIT;
        mb.dstStageMask = VK_PIPELINE_STAGE_2_HOST_BIT, mb.dstAccessMask = VK_ACCESS_2_HOST_READ_BIT;
        VkDependencyInfo di{VK_STRUCTURE_TYPE_DEPENDENCY_INFO};
        di.memoryBarrierCount = 1;
        di.pMemoryBarriers = &mb;
        vkCmdPipelineBarrier2(rc().cmd, &di);
    }
}

// ---------------------------------------------------------------------------- presentation
bool Renderer::make_swapchain(uint32_t w, uint32_t h) {
    if (!sc.surface) {
        WindowHandles wh;
        if (!opt.window_handles || !opt.window_handles(wh) ||
            !create_surface(ctx, wh.type == WindowHandles::kWin32 ? WindowSystem::Win32 : WindowSystem::Xlib, wh.display,
                            wh.window, &sc.surface)) {
            log("native renderer: could not create a window surface; not presenting");
            sc.failed = true;
            return false;
        }
        VkBool32 ok = VK_FALSE;
        vkGetPhysicalDeviceSurfaceSupportKHR(ctx.gpu, ctx.queue_family, sc.surface, &ok);
        if (!ok || !vkCreateSwapchainKHR) {
            log("native renderer: %s cannot present to this window", ctx.name);
            sc.failed = true;
            return false;
        }
        // format: 8-bit UNORM (the video-out bytes are already sRGB-encoded; no conversion)
        uint32_t n = 0;
        vkGetPhysicalDeviceSurfaceFormatsKHR(ctx.gpu, sc.surface, &n, nullptr);
        std::vector<VkSurfaceFormatKHR> fmts(n);
        vkGetPhysicalDeviceSurfaceFormatsKHR(ctx.gpu, sc.surface, &n, fmts.data());
        sc.format = fmts.empty() ? VkSurfaceFormatKHR{VK_FORMAT_B8G8R8A8_UNORM, VK_COLOR_SPACE_SRGB_NONLINEAR_KHR} : fmts[0];
        for (auto& f : fmts)
            if ((f.format == VK_FORMAT_B8G8R8A8_UNORM || f.format == VK_FORMAT_R8G8B8A8_UNORM) &&
                f.colorSpace == VK_COLOR_SPACE_SRGB_NONLINEAR_KHR) {
                sc.format = f;
                break;
            }
        // present mode: the requested one if offered, else FIFO (always available)
        vkGetPhysicalDeviceSurfacePresentModesKHR(ctx.gpu, sc.surface, &n, nullptr);
        std::vector<VkPresentModeKHR> modes(n);
        vkGetPhysicalDeviceSurfacePresentModesKHR(ctx.gpu, sc.surface, &n, modes.data());
        const std::string want = opt.present_mode ? opt.present_mode : "Fifo";
        const VkPresentModeKHR wm = want == "Immediate" ? VK_PRESENT_MODE_IMMEDIATE_KHR
                                  : want == "Mailbox"   ? VK_PRESENT_MODE_MAILBOX_KHR
                                                        : VK_PRESENT_MODE_FIFO_KHR;
        sc.mode = VK_PRESENT_MODE_FIFO_KHR;
        for (auto m : modes)
            if (m == wm) sc.mode = wm;
        if (sc.mode != wm && wm == VK_PRESENT_MODE_IMMEDIATE_KHR)  // no tearing mode: the next least latency
            for (auto m : modes)
                if (m == VK_PRESENT_MODE_MAILBOX_KHR) sc.mode = m;
        log("native renderer: presenting %s (%s), format %d", sc.mode == VK_PRESENT_MODE_IMMEDIATE_KHR ? "Immediate"
                                                              : sc.mode == VK_PRESENT_MODE_MAILBOX_KHR ? "Mailbox"
                                                                                                       : "Fifo",
            want.c_str(), int(sc.format.format));
    }
    VkSurfaceCapabilitiesKHR caps{};
    vkGetPhysicalDeviceSurfaceCapabilitiesKHR(ctx.gpu, sc.surface, &caps);
    VkExtent2D ext{w, h};
    if (caps.currentExtent.width != UINT32_MAX) ext = caps.currentExtent;
    ext.width = std::clamp(ext.width, caps.minImageExtent.width, std::max(caps.minImageExtent.width, caps.maxImageExtent.width));
    ext.height = std::clamp(ext.height, caps.minImageExtent.height, std::max(caps.minImageExtent.height, caps.maxImageExtent.height));
    if (!ext.width || !ext.height) return false;  // minimised
    uint32_t count = std::max(caps.minImageCount, sc.mode == VK_PRESENT_MODE_MAILBOX_KHR ? 3u : 2u);
    if (caps.maxImageCount) count = std::min(count, caps.maxImageCount);
    VkSwapchainCreateInfoKHR ci{VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR};
    ci.surface = sc.surface;
    ci.minImageCount = count;
    ci.imageFormat = sc.format.format;
    ci.imageColorSpace = sc.format.colorSpace;
    ci.imageExtent = ext;
    ci.imageArrayLayers = 1;
    ci.imageUsage = VK_IMAGE_USAGE_TRANSFER_DST_BIT | VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT;
    ci.imageSharingMode = VK_SHARING_MODE_EXCLUSIVE;
    ci.preTransform = (caps.supportedTransforms & VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR) ? VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR
                                                                                         : caps.currentTransform;
    ci.compositeAlpha = (caps.supportedCompositeAlpha & VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR)
                            ? VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR
                            : VkCompositeAlphaFlagBitsKHR(caps.supportedCompositeAlpha & -caps.supportedCompositeAlpha);
    ci.presentMode = sc.mode;
    ci.clipped = VK_TRUE;
    ci.oldSwapchain = sc.chain;
    VkSwapchainKHR chain = VK_NULL_HANDLE;
    const VkResult r = vkCreateSwapchainKHR(ctx.device, &ci, nullptr, &chain);
    destroy_swapchain(true);
    if (r != VK_SUCCESS) {
        log("native renderer: vkCreateSwapchainKHR failed (%d)", int(r));
        return false;
    }
    sc.chain = chain;
    sc.extent = ext;
    uint32_t n = 0;
    vkGetSwapchainImagesKHR(ctx.device, chain, &n, nullptr);
    sc.images.resize(n);
    vkGetSwapchainImagesKHR(ctx.device, chain, &n, sc.images.data());
    VkSemaphoreCreateInfo si{VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO};
    sc.ready.resize(n);
    for (auto& x : sc.ready) vkCreateSemaphore(ctx.device, &si, nullptr, &x);
    sc.acquired.resize(opt.frames_in_flight + 2);
    for (auto& x : sc.acquired) vkCreateSemaphore(ctx.device, &si, nullptr, &x);
    sc.want_w = w, sc.want_h = h, sc.stale = false;
    log("native renderer: swapchain %ux%u, %u images", ext.width, ext.height, n);
    return true;
}

void Renderer::destroy_swapchain(bool keep_surface) {
    if (sc.chain || !sc.acquired.empty()) wait_idle(), vkDeviceWaitIdle(ctx.device);
    for (auto x : sc.ready) vkDestroySemaphore(ctx.device, x, nullptr);
    for (auto x : sc.acquired) vkDestroySemaphore(ctx.device, x, nullptr);
    sc.ready.clear(), sc.acquired.clear(), sc.images.clear();
    if (sc.chain) vkDestroySwapchainKHR(ctx.device, sc.chain, nullptr);
    sc.chain = VK_NULL_HANDLE;
    if (!keep_surface && sc.surface) vkDestroySurfaceKHR(ctx.instance, sc.surface, nullptr), sc.surface = VK_NULL_HANDLE;
}

VkFormat unorm_of(VkFormat f) {
    switch (f) {
    case VK_FORMAT_R8G8B8A8_SRGB: return VK_FORMAT_R8G8B8A8_UNORM;
    case VK_FORMAT_B8G8R8A8_SRGB: return VK_FORMAT_B8G8R8A8_UNORM;
    case VK_FORMAT_A8B8G8R8_SRGB_PACK32: return VK_FORMAT_A8B8G8R8_UNORM_PACK32;
    default: return VK_FORMAT_UNDEFINED;
    }
}

// Blit the flipped video-out image into the window, letterboxed to keep its aspect ratio.
void Renderer::present(uint64_t addr) {
    if (sc.failed || !opt.window_size) return;
    auto it = target_by_base.find(addr);
    if (it == target_by_base.end() || !it->second || it->second->depth) return;
    Image* src = it->second;
    uint32_t ww = 0, wh = 0;
    opt.window_size(ww, wh);
    if (!ww || !wh) return;  // minimised
    if (!sc.chain || sc.stale || ww != sc.want_w || wh != sc.want_h)
        if (!make_swapchain(ww, wh)) return;
    const uint32_t slot = sc.slot;
    uint32_t index = 0;
    // (the swapchain and the queue are only used on this thread: the lock is released while
    // presentation may block, so the engine's threads keep recording)
    m.unlock();
    VkResult r = vkAcquireNextImageKHR(ctx.device, sc.chain, UINT64_MAX, sc.acquired[slot], VK_NULL_HANDLE, &index);
    m.lock();
    if (r == VK_ERROR_OUT_OF_DATE_KHR) {
        sc.stale = true;
        return;
    }
    if (r != VK_SUCCESS && r != VK_SUBOPTIMAL_KHR) {
        static int logged = 0;
        if (logged++ < 5) log("native renderer: vkAcquireNextImageKHR failed (%d)", int(r));
        if (r == VK_ERROR_SURFACE_LOST_KHR) destroy_swapchain(false);
        return;
    }
    sc.slot = (slot + 1) % uint32_t(sc.acquired.size());
    begin_record();
    // sRGB-format sources: copy the bytes into a UNORM image first (a blit would decode them)
    Image* from = src;
    if (const VkFormat uf = unorm_of(src->format); uf != VK_FORMAT_UNDEFINED) {
        if (!sc.raw || sc.raw->w != src->w || sc.raw->h != src->h || sc.raw->format != uf) {
            bury(std::move(sc.raw));
            sc.raw = make_image(uf, src->w, src->h, 1, 1, 1, false, false, false, false);
        }
        if (sc.raw) {
            VkImageCopy c{};
            c.srcSubresource = c.dstSubresource = {VK_IMAGE_ASPECT_COLOR_BIT, 0, 0, 1};
            c.extent = {src->w, src->h, 1};
            vkCmdCopyImage(rc().cmd, src->image, VK_IMAGE_LAYOUT_GENERAL, sc.raw->image, VK_IMAGE_LAYOUT_GENERAL, 1, &c);
            barrier();
            from = sc.raw.get();
        }
    }
    VkImage dst = sc.images[index];
    auto transition = [&](VkImageLayout a, VkImageLayout b, VkPipelineStageFlags2 src_stage, VkPipelineStageFlags2 dst_stage) {
        VkImageMemoryBarrier2 ib{VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER_2};
        ib.srcStageMask = src_stage;
        ib.srcAccessMask = a == VK_IMAGE_LAYOUT_UNDEFINED ? 0 : VK_ACCESS_2_TRANSFER_WRITE_BIT;
        ib.dstStageMask = dst_stage;
        ib.dstAccessMask = b == VK_IMAGE_LAYOUT_PRESENT_SRC_KHR ? 0 : VK_ACCESS_2_TRANSFER_WRITE_BIT;
        ib.oldLayout = a, ib.newLayout = b;
        ib.srcQueueFamilyIndex = ib.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
        ib.image = dst;
        ib.subresourceRange = {VK_IMAGE_ASPECT_COLOR_BIT, 0, 1, 0, 1};
        VkDependencyInfo di{VK_STRUCTURE_TYPE_DEPENDENCY_INFO};
        di.imageMemoryBarrierCount = 1;
        di.pImageMemoryBarriers = &ib;
        vkCmdPipelineBarrier2(rc().cmd, &di);
    };
    transition(VK_IMAGE_LAYOUT_UNDEFINED, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT,
               VK_PIPELINE_STAGE_2_ALL_TRANSFER_BIT);
    VkClearColorValue black{};
    VkImageSubresourceRange rr{VK_IMAGE_ASPECT_COLOR_BIT, 0, 1, 0, 1};
    // fit: largest rectangle with the source's aspect ratio
    const double sa = double(from->w) / from->h, da = double(sc.extent.width) / sc.extent.height;
    uint32_t bw = sc.extent.width, bh = sc.extent.height;
    if (sa > da) bh = uint32_t(bw / sa + 0.5);
    else bw = uint32_t(bh * sa + 0.5);
    const int32_t bx = int32_t(sc.extent.width - bw) / 2, by = int32_t(sc.extent.height - bh) / 2;
    if (bw != sc.extent.width || bh != sc.extent.height) {
        vkCmdClearColorImage(rc().cmd, dst, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, &black, 1, &rr);
        transition(VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
                   VK_PIPELINE_STAGE_2_ALL_TRANSFER_BIT, VK_PIPELINE_STAGE_2_ALL_TRANSFER_BIT);
    }
    VkImageBlit b{};
    b.srcSubresource = b.dstSubresource = {VK_IMAGE_ASPECT_COLOR_BIT, 0, 0, 1};
    b.srcOffsets[1] = {int32_t(from->w), int32_t(from->h), 1};
    b.dstOffsets[0] = {bx, by, 0};
    b.dstOffsets[1] = {bx + int32_t(bw), by + int32_t(bh), 1};
    vkCmdBlitImage(rc().cmd, from->image, VK_IMAGE_LAYOUT_GENERAL, dst, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &b,
                   (bw == from->w && bh == from->h) ? VK_FILTER_NEAREST : VK_FILTER_LINEAR);
    transition(VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, VK_IMAGE_LAYOUT_PRESENT_SRC_KHR, VK_PIPELINE_STAGE_2_ALL_TRANSFER_BIT,
               VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT);
    VkSemaphoreSubmitInfo wait{VK_STRUCTURE_TYPE_SEMAPHORE_SUBMIT_INFO};
    wait.semaphore = sc.acquired[slot];
    wait.stageMask = VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT;
    VkSemaphoreSubmitInfo signal{VK_STRUCTURE_TYPE_SEMAPHORE_SUBMIT_INFO};
    signal.semaphore = sc.ready[index];
    signal.stageMask = VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT;
    submit(&wait, &signal);
    VkPresentInfoKHR pi{VK_STRUCTURE_TYPE_PRESENT_INFO_KHR};
    pi.waitSemaphoreCount = 1;
    pi.pWaitSemaphores = &sc.ready[index];
    pi.swapchainCount = 1;
    pi.pSwapchains = &sc.chain;
    pi.pImageIndices = &index;
    m.unlock();
    r = vkQueuePresentKHR(ctx.queue, &pi);
    m.lock();
    if (r == VK_ERROR_OUT_OF_DATE_KHR || r == VK_SUBOPTIMAL_KHR) sc.stale = r == VK_ERROR_OUT_OF_DATE_KHR;
    else if (r != VK_SUCCESS) {
        static int logged = 0;
        if (logged++ < 5) log("native renderer: vkQueuePresentKHR failed (%d)", int(r));
    }
    ++sc.presented;
}

// Written next to the game's data whenever enough new pipelines were built (the process ends
// without a shutdown path, so there is no "on exit").
void Renderer::save_pipeline_cache() {
    if (!opt.pipeline_cache || !pcache || st.pipelines == pcache_saved_pipelines) return;
    pcache_saved_pipelines = st.pipelines;
    size_t n = 0;
    if (vkGetPipelineCacheData(ctx.device, pcache, &n, nullptr) != VK_SUCCESS || !n) return;
    std::vector<char> data(n);
    if (vkGetPipelineCacheData(ctx.device, pcache, &n, data.data()) != VK_SUCCESS) return;
    const std::string tmp = std::string(opt.pipeline_cache) + ".tmp";
    FILE* f = std::fopen(tmp.c_str(), "wb");
    if (!f) return;
    const bool ok = std::fwrite(data.data(), 1, n, f) == n;
    std::fclose(f);
    if (ok) {
        std::remove(opt.pipeline_cache);
        std::rename(tmp.c_str(), opt.pipeline_cache);
    }
}

// End of a frame: limit how far the CPU runs ahead, and housekeeping.
void Renderer::end_frame() {
    frame_ends.push_back(serial_next - 1);
    while (frame_ends.size() > opt.frames_in_flight) {
        // (with m held by the caller: released while waiting, so lists keep being recorded)
        if (timeline && serial_done < frame_ends.front()) {
            VkSemaphoreWaitInfo wi{VK_STRUCTURE_TYPE_SEMAPHORE_WAIT_INFO};
            wi.semaphoreCount = 1, wi.pSemaphores = &timeline, wi.pValues = &frame_ends.front();
            const uint64_t tw = now_ns();
            m.unlock();
            vkWaitSemaphores(ctx.device, &wi, UINT64_MAX);
            m.lock();
            st.t_wait += now_ns() - tw;
        }
        wait_serial(frame_ends.front());
        frame_ends.pop_front();
    }
    retire_completed();
    if (st.frames % 120 == 0) evict_textures(), evict_geo();
    // pipeline cache: shortly after new pipelines appear (a burst while a level loads), at
    // most every ~10 s
    static uint64_t last_save_frame = 0;
    if (st.pipelines != pcache_saved_pipelines && st.frames - last_save_frame > 600) {
        last_save_frame = st.frames;
        save_pipeline_cache();
    }
}

// Reads an image back and writes it as a PPM (8-bit; float formats are clamped to [0, 1],
// depth is shown as gray).
bool Renderer::save_image(Image* img, const char* path) {
    uint32_t bpp = 0;
    switch (img->format) {
    case VK_FORMAT_R8G8B8A8_UNORM: case VK_FORMAT_R8G8B8A8_SRGB: case VK_FORMAT_B8G8R8A8_UNORM:
    case VK_FORMAT_B8G8R8A8_SRGB: case VK_FORMAT_A2B10G10R10_UNORM_PACK32: case VK_FORMAT_B10G11R11_UFLOAT_PACK32:
    case VK_FORMAT_R32_SFLOAT: case VK_FORMAT_R16G16_SFLOAT: case VK_FORMAT_R16G16_UNORM: case VK_FORMAT_D32_SFLOAT:
    case VK_FORMAT_D32_SFLOAT_S8_UINT: case VK_FORMAT_R32_UINT:
        bpp = 4;
        break;
    case VK_FORMAT_R16G16B16A16_SFLOAT: case VK_FORMAT_R32G32_SFLOAT: bpp = 8; break;
    case VK_FORMAT_R8_UNORM: bpp = 1; break;
    case VK_FORMAT_R16_SFLOAT: case VK_FORMAT_R16_UNORM: case VK_FORMAT_R8G8_UNORM: bpp = 2; break;
    case VK_FORMAT_R32G32B32A32_SFLOAT: bpp = 16; break;
    default: return false;
    }
    const uint32_t w = img->w, h = img->h;
    Buffer rb = make_buffer(uint64_t(w) * h * bpp, VK_BUFFER_USAGE_TRANSFER_DST_BIT, true);
    if (!rb.map) return false;
    begin_record();
    VkBufferImageCopy r{};
    r.imageSubresource = {img->depth ? VkImageAspectFlags(VK_IMAGE_ASPECT_DEPTH_BIT) : VkImageAspectFlags(VK_IMAGE_ASPECT_COLOR_BIT), 0, 0, 1};
    r.imageExtent = {w, h, 1};
    vkCmdCopyImageToBuffer(rc().cmd, img->image, VK_IMAGE_LAYOUT_GENERAL, rb.buf, 1, &r);
    submit_and_wait();
    auto half = [](uint16_t hv) {
        const uint32_t e = hv >> 10 & 0x1F, m = hv & 0x3FF;
        float f = e == 0 ? m / 16777216.0f : e == 31 ? 65504.0f : std::ldexp(1.0f + m / 1024.0f, int(e) - 15);
        return (hv & 0x8000) ? -f : f;
    };
    auto u8 = [](float f) { return uint8_t(std::clamp(f, 0.0f, 1.0f) * 255.0f + 0.5f); };
    FILE* f = std::fopen(path, "wb");
    if (!f) {
        free_buffer(rb);
        return false;
    }
    std::fprintf(f, "P6 %u %u 255\n", w, h);
    std::vector<uint8_t> row(size_t(w) * 3);
    for (uint32_t y = 0; y < h; ++y) {
        const uint8_t* src = rb.map + size_t(y) * w * bpp;
        for (uint32_t x = 0; x < w; ++x) {
            const uint8_t* p = src + size_t(x) * bpp;
            uint8_t c[3] = {};
            uint32_t v32;
            std::memcpy(&v32, p, std::min(bpp, 4u));
            switch (img->format) {
            case VK_FORMAT_B8G8R8A8_UNORM: case VK_FORMAT_B8G8R8A8_SRGB: c[0] = p[2], c[1] = p[1], c[2] = p[0]; break;
            case VK_FORMAT_R8G8B8A8_UNORM: case VK_FORMAT_R8G8B8A8_SRGB: c[0] = p[0], c[1] = p[1], c[2] = p[2]; break;
            case VK_FORMAT_R8_UNORM: c[0] = c[1] = c[2] = p[0]; break;
            case VK_FORMAT_R8G8_UNORM: c[0] = p[0], c[1] = p[1]; break;
            case VK_FORMAT_A2B10G10R10_UNORM_PACK32:
                c[0] = uint8_t((v32 & 0x3FF) >> 2), c[1] = uint8_t((v32 >> 10 & 0x3FF) >> 2), c[2] = uint8_t((v32 >> 20 & 0x3FF) >> 2);
                break;
            case VK_FORMAT_B10G11R11_UFLOAT_PACK32: {
                auto f11 = [&](uint32_t v, int mbits) {
                    const uint32_t e = v >> mbits, m = v & ((1u << mbits) - 1);
                    return e == 0 ? 0.0f : std::ldexp(1.0f + float(m) / float(1u << mbits), int(e) - 15);
                };
                c[0] = u8(f11(v32 & 0x7FF, 6)), c[1] = u8(f11(v32 >> 11 & 0x7FF, 6)), c[2] = u8(f11(v32 >> 22 & 0x3FF, 5));
                break;
            }
            case VK_FORMAT_R16G16B16A16_SFLOAT: {
                uint16_t hv[3];
                std::memcpy(hv, p, 6);
                c[0] = u8(half(hv[0])), c[1] = u8(half(hv[1])), c[2] = u8(half(hv[2]));
                break;
            }
            case VK_FORMAT_R16G16_SFLOAT: {
                uint16_t hv[2];
                std::memcpy(hv, p, 4);
                c[0] = u8(half(hv[0])), c[1] = u8(half(hv[1]));
                break;
            }
            case VK_FORMAT_R16_SFLOAT: {
                uint16_t hv;
                std::memcpy(&hv, p, 2);
                c[0] = c[1] = c[2] = u8(half(hv));
                break;
            }
            case VK_FORMAT_R16_UNORM: c[0] = c[1] = c[2] = p[1]; break;
            case VK_FORMAT_R16G16_UNORM: c[0] = p[1], c[1] = p[3]; break;
            case VK_FORMAT_R32_SFLOAT: case VK_FORMAT_D32_SFLOAT: case VK_FORMAT_D32_SFLOAT_S8_UINT: {
                float fv;
                std::memcpy(&fv, p, 4);
                c[0] = c[1] = c[2] = u8(fv);
                break;
            }
            case VK_FORMAT_R32_UINT: c[0] = p[0], c[1] = p[1], c[2] = p[2]; break;
            case VK_FORMAT_R32G32_SFLOAT: {
                float fv[2];
                std::memcpy(fv, p, 8);
                c[0] = u8(fv[0]), c[1] = u8(fv[1]);
                break;
            }
            case VK_FORMAT_R32G32B32A32_SFLOAT: {
                float fv[3];
                std::memcpy(fv, p, 12);
                c[0] = u8(fv[0]), c[1] = u8(fv[1]), c[2] = u8(fv[2]);
                break;
            }
            default: break;
            }
            std::memcpy(&row[size_t(x) * 3], c, 3);
        }
        std::fwrite(row.data(), 1, row.size(), f);
    }
    std::fclose(f);
    free_buffer(rb);
    return true;
}

void Renderer::dump(uint64_t addr, uint32_t, uint32_t, uint64_t frame) {
    if (!opt.frames_dir) return;
    char path[512];
    if (auto it = target_by_base.find(addr); it != target_by_base.end()) {
        std::snprintf(path, sizeof path, "%s/f%06llu.ppm", opt.frames_dir, (unsigned long long)frame);
        save_image(it->second, path);
    }
    // D1_NG_TARGETS: every render target this frame used, in creation order
    if (opt.dump_targets) {
        int n = 0;
        static const uint64_t max_pix = std::getenv("D1_NG_TARGETS_MAXPIX") ? std::strtoull(std::getenv("D1_NG_TARGETS_MAXPIX"), nullptr, 10) : ~0ull;
        static const std::vector<uint64_t> only = [] {  // D1_NG_TARGETS_BASES=<hex>,..: just these
            std::vector<uint64_t> v;
            if (const char* e = std::getenv("D1_NG_TARGETS_BASES"))
                for (const char* p = e; *p;) {
                    char* end;
                    v.push_back(std::strtoull(p, &end, 16));
                    p = *end ? end + 1 : end;
                }
            return v;
        }();
        for (auto& [k, img] : targets)
            if (img && img->last_used > frame_first_submit && uint64_t(img->w) * img->h <= max_pix && !img->is3d &&
                (only.empty() || std::find(only.begin(), only.end(), img->base) != only.end())) {
                std::snprintf(path, sizeof path, "%s/f%06llu_rt%02d_%llx_%ux%u_f%d.ppm", opt.frames_dir,
                              (unsigned long long)frame, n++, (unsigned long long)img->base, img->w, img->h,
                              int(img->format));
                save_image(img.get(), path);
            }
    }
    frame_first_submit = submit_seq.load();
}

}  // namespace

bool init(const Options& opt) {
    g = new Renderer;
    if (!g->init(opt)) {
        delete g;
        g = nullptr;
        return false;
    }
    return true;
}
bool active() { return g != nullptr; }
void execute(const std::vector<Draw*>& draws) {
    if (!g) return;
    std::lock_guard lk(g->m);
    g->execute(draws);
}
bool list_recording() { return g && g->list_rec; }
bool record_list(const std::vector<Draw*>& items, uint32_t& handle, std::vector<LateCb>& late) {
    return g && g->list_rec && g->record_list(items, handle, late);
}
void fill_late(const LateCb& l, uint64_t src, uint32_t size) {
    if (!g) return;
    uint8_t* dst = g->ring.map + l.off;
    const uint32_t n = src >= 0x10000 ? std::min(size, l.size) : 0;
    if (n) std::memcpy(dst, reinterpret_cast<const void*>(src), n);
    if (n < l.size) std::memset(dst + n, 0, l.size - n);
    if (size > l.size) {  // (bigger next time)
        auto& h = g->late_hint[l.stage & 1][l.slot & 15];
        uint32_t cur = h.load();
        const uint32_t want = std::min<uint32_t>(65536, (size + 255) & ~255u);
        while (cur < want && !h.compare_exchange_weak(cur, want)) {}
    }
}
void prefetch_texture(const uint32_t* tsharp, uint64_t res, uint64_t obj) {
    if (!g || !res) return;
    Renderer::LoadJob j{true, {}, 0, 0, res, obj};
    std::memcpy(j.t, tsharp, 32);
    g->prefetch(j);
}
void prefetch_buffer(uint64_t base, uint64_t size, uint64_t res, uint64_t obj) {
    if (!g || !res) return;
    g->prefetch({false, {}, base, size, res, obj});
}
void cpu_wrote(uint64_t addr, uint64_t size) {
    if (!g || !g->dynamic_copy || addr < 0x10000) return;
    std::lock_guard lk(g->dyn_m);
    g->dyn_q.push_back({addr, size});
}
void submit_recorded(const std::vector<uint32_t>& handles) {
    if (!g) return;
    std::lock_guard lk(g->m);
    g->submit_recorded(handles);
}
void discard_recorded(uint32_t handle) {
    if (!g) return;
    std::lock_guard lk(g->m);
    g->discard_recorded(handle);
}
void flip(uint64_t addr, uint32_t w, uint32_t h, uint64_t frame, bool dump) {
    if (!g) return;
    std::lock_guard lk(g->m);
    if (g->st.frames == g->passlog_frame) {
        int i = 0;
        log("ng frame %llu (flip %llu):", (unsigned long long)g->st.frames, (unsigned long long)frame);
        for (auto& pl : g->passlog)
            log("ng pass %3d: c %llx %llx %llx %llx d %llx | %u draws %u clears | vs %llx ps %llx from %#llx |%s", i++,
                (unsigned long long)pl.c[0], (unsigned long long)pl.c[1], (unsigned long long)pl.c[2],
                (unsigned long long)pl.c[3], (unsigned long long)pl.d, pl.draws, pl.clears,
                (unsigned long long)pl.first_vs, (unsigned long long)pl.first_ps, (unsigned long long)pl.caller,
                pl.tex.c_str());
    }
    if (g->st.frames == g->passlog_frame && !g->frame_draws.empty()) {
        std::string line;
        uint64_t total = 0;
        for (auto& [k, v] : g->frame_draws) {
            char b[64];
            std::snprintf(b, sizeof b, " %llx:%llu/%llu", (unsigned long long)k, (unsigned long long)v.first,
                          (unsigned long long)v.second);
            line += b;
            total += v.first;
        }
        log("ng drawstats flip %llu: %llu draws |%s", (unsigned long long)frame, (unsigned long long)total, line.c_str());
        g->frame_draws.clear();
    }
    if (g->st.frames == g->passlog_frame && !g->traces.empty()) {
        vkDeviceWaitIdle(g->ctx.device);
        // <frames dir>/trace.bin: per draw a header (ps, vs, caller, blend, count, bytes) and the pixels
        char path[512];
        std::snprintf(path, sizeof path, "%s/trace_%06llu.bin", g->opt.frames_dir ? g->opt.frames_dir : ".", (unsigned long long)frame);
        if (FILE* f = std::fopen(path, "wb")) {
            for (const auto& t : g->traces) {
                const uint64_t hdr[6] = {t.ps, t.vs, t.caller, t.blend, t.count, uint64_t(t.w) * t.bytes};
                std::fwrite(hdr, 8, 6, f);
                std::fwrite(g->ring.map + t.off, 1, uint64_t(t.w) * t.bytes, f);
            }
            std::fclose(f);
        }
        log("ng trace: %zu draws written to %s", g->traces.size(), path);
        g->traces.clear();
    }
    if (g->st.frames == g->passlog_frame && --g->passlog_count) {
        g->passlog.clear();
        ++g->passlog_frame;
    }
    ++g->st.frames;
    if (addr) g->present(addr);
    if (dump && addr) g->dump(addr, w, h, frame);
    else g->frame_first_submit = g->submit_seq.load();
    g->end_frame();
}
void request_passlog(uint32_t frames) {
    if (!g) return;
    std::lock_guard lk(g->m);
    g->passlog.clear();
    g->passlog_frame = g->st.frames + 1;
    g->passlog_count = frames;
    if (std::getenv("D1_NG_SNAP_DEBUG")) g->debug = true, g->debug_from = g->passlog_frame, g->debug_lines = 0;
    if (std::getenv("D1_NG_SNAP_RELOAD")) g->reload_all = true;  // (testing) copy every texture again
}
Counters counters() {
    if (!g) return {};
    return {g->st.pipelines, g->st.shaders, g->st.textures, g->st.bytes_tex, g->st.draws};
}

uint64_t presented_frames() { return g ? g->sc.presented : 0; }
const char* gpu_name() { return g ? g->ctx.name : ""; }

static std::atomic<uint32_t> g_toggles{0};
uint32_t debug_toggles() { return g_toggles.load(std::memory_order_relaxed); }
void flip_debug_toggle(int bit) {
    const uint32_t v = g_toggles.fetch_xor(1u << bit) ^ (1u << bit);
    static const char* names[] = {"occlusion queries", "waiting for readbacks (inverted: F6 turns waiting ON)", "readbacks", "geometry cache"};
    log("native renderer: %s %s (F%d)", bit < 4 ? names[bit] : "?", (v >> bit & 1) ? "OFF" : "on", 5 + bit);
}
const char* debug_toggle_text() {
    static thread_local char buf[96];
    const uint32_t v = debug_toggles();
    buf[0] = 0;
    if (v & 1) std::strcat(buf, " [F5 queries off]");
    if (v & 2) std::strcat(buf, " [F6 readback wait flipped]");
    if (v & 4) std::strcat(buf, " [F7 readbacks off]");
    if (v & 8) std::strcat(buf, " [F8 geometry cache off]");
    return buf;
}
void describe_owner(uint64_t a, char* out, size_t n) {
    if (!g || !n) return;
    out[0] = 0;
    std::lock_guard lk(g->m);
    for (auto& [k, img] : g->textures)
        if (img && a >= img->src_addr && a < img->src_addr + img->src_size) {
            std::snprintf(out, n, "texture %ux%u fmt %d levels %u at %#llx (+%#llx), %s", img->w, img->h, int(img->format), img->levels,
                          (unsigned long long)img->src_addr, (unsigned long long)(a - img->src_addr),
                          img->res_val ? "engine resource" : "write-tracked");
            return;
        }
    for (auto& [k, up] : g->targets)
        if (up && up->base && a >= up->base && a < up->base + std::max<uint64_t>(up->tv_size, uint64_t(up->w) * up->h * std::max(1u, up->bpp / 8))) {
            std::snprintf(out, n, "render target %ux%u fmt %d at %#llx", up->w, up->h, int(up->format), (unsigned long long)up->base);
            return;
        }
    for (auto& sh : g->geo_shards) {
        std::lock_guard sl(sh.m);
        for (auto& [k, e] : sh.map)
            if (!(k >> 63) && e.valid && a >= (k & 0xFFFFFFFFFFull) && a < (k & 0xFFFFFFFFFFull) + e.size) {
                std::snprintf(out, n, "geometry %#llx +%llu (%s)", (unsigned long long)(k & 0xFFFFFFFFFFull), (unsigned long long)e.size,
                              e.misses ? "rewritten before" : "first write");
                return;
            }
    }
    std::snprintf(out, n, "nothing kept now");
}
void print_stats() {
    if (!g) return;
    std::lock_guard lk(g->m);
    auto& s = g->st;
    log("native renderer: %llu frames, %llu submissions | %llu draws, %llu clears, %llu skipped | %llu pipelines, "
        "%llu shaders (%llu failed), %llu textures (%llu dropped), %llu targets | ring peak %.1f MiB | "
        "image memory %.0f MiB in %zu blocks",
        (unsigned long long)s.frames, (unsigned long long)s.submits, (unsigned long long)s.draws,
        (unsigned long long)s.clears, (unsigned long long)s.skipped, (unsigned long long)s.pipelines,
        (unsigned long long)s.shaders, (unsigned long long)s.bad_shaders, (unsigned long long)s.textures,
        (unsigned long long)s.evicted, (unsigned long long)s.targets, double(s.ring_peak) / 1048576.0,
        double(g->heap.used) / 1048576.0, g->heap.blocks.size());
    const double fr = double(std::max<uint64_t>(1, s.frames));
    log("native renderer: copied per frame (average): vertices %.1f MiB, indices %.1f MiB, constants %.1f MiB, "
        "textures %.1f MiB | geometry cache: %.1f MiB uploaded per frame, %.0f hits per frame, %.0f MiB held | "
        "%llu texture reloads (%llu torn, %llu in place), %llu torn geometry copies, %llu target readbacks, %llu targets rewritten by the CPU, %llu textures with rebuilt mips", double(s.bytes_vtx) / fr / 1048576.0, double(s.bytes_idx) / fr / 1048576.0,
        double(s.bytes_cb) / fr / 1048576.0, double(s.bytes_tex) / fr / 1048576.0, double(s.bytes_geo) / fr / 1048576.0,
        double(s.geo_hits) / fr, double(g->geo_bytes) / 1048576.0, (unsigned long long)s.tex_reloads,
        (unsigned long long)s.tex_torn, (unsigned long long)s.tex_inplace, (unsigned long long)s.geo_torn, (unsigned long long)s.readbacks,
        (unsigned long long)s.target_writes, (unsigned long long)s.mips_filled);
    if (const double f = double(s.frames - s.t_frames); f > 0)
        log("native renderer: CPU per frame: pre-pass %.2f ms, pipelines %.2f ms, geometry %.2f ms, descriptors %.2f ms, "
            "commands %.2f ms, submit %.2f ms, waiting for the GPU %.2f ms", double(s.t_pre) / f / 1e6,
            double(s.t_pipe) / f / 1e6, double(s.t_geo) / f / 1e6, double(s.t_desc) / f / 1e6, double(s.t_cmd) / f / 1e6,
            double(s.t_submit) / f / 1e6, double(s.t_wait) / f / 1e6);
    if (const double n = double(s.draws - s.t_draws); n > 0)
        log("native renderer: per draw (%.0f draws per frame, %.0f%% recorded in parallel): pipeline %.0f ns, geometry %.0f ns, "
            "descriptors %.0f ns, commands %.0f ns (summed over threads) | pipeline memo %llu hits, %llu misses (%llu by target changes)",
            n / std::max(1.0, double(s.frames - s.t_frames)), 100.0 * double(g->par_draws) / n, double(s.t_pipe) / n, double(s.t_geo) / n,
            double(s.t_desc) / n, double(s.t_cmd) / n, (unsigned long long)s.memo_hits, (unsigned long long)s.memo_misses,
            (unsigned long long)s.memo_gen);
    if (std::getenv("D1_NG_LOG_GEN"))
        log("native renderer: target generation bumps: new/changed binding %llu, same-size alias %llu, new color %llu, new depth %llu, CPU rewrite %llu",
            (unsigned long long)g->gen_why[0], (unsigned long long)g->gen_why[1], (unsigned long long)g->gen_why[2],
            (unsigned long long)g->gen_why[3], (unsigned long long)g->gen_why[4]);
    s.memo_hits = s.memo_misses = s.memo_gen = 0, g->par_draws = g->par_runs = 0;
    if (const double f = double(s.frames - s.t_frames); f > 0 && g->list_rec)
        log("native renderer: lists recorded on the engine's threads: %.1f per frame, %.2f ms per frame of their time "
            "(%.2f ms waiting for the renderer lock) | submitting them %.2f ms per frame",
            double(g->lr_lists.exchange(0)) / f, double(g->lr_ns.exchange(0)) / f / 1e6, double(g->lr_wait_ns.exchange(0)) / f / 1e6,
            double(g->lr_sub_ns.exchange(0)) / f / 1e6);
    if (const double f = double(s.frames - s.t_frames); f > 0)
        log("native renderer: pre-pass per frame: targets %.2f ms, texture checks %.2f ms (%.0f, %.0f unwatched), texture loads %.2f ms "
            "(detile %.2f, mip check %.2f, protect %.2f, new images %.2f)",
            double(s.t_tgt) / f / 1e6, double(s.t_tex_hit) / f / 1e6, double(s.tex_checks) / f, double(s.tex_unwatched) / f,
            double(s.t_tex_load) / f / 1e6, double(s.t_detile) / f / 1e6, double(s.t_fill) / f / 1e6,
            double(s.t_watch) / f / 1e6, double(s.t_mkimg) / f / 1e6);
    if (const double f = double(s.frames - s.t_frames); f > 0)
        log("native renderer: new images per frame: vkCreateImage %.2f ms, memory %.2f ms (%.0f free ranges scanned, %llu new blocks), bind %.2f ms, view %.2f ms",
            double(s.t_vkimg) / f / 1e6, double(s.t_heap) / f / 1e6, double(s.heap_scans) / f, (unsigned long long)s.heap_blocks_new, double(s.t_bind) / f / 1e6, double(s.t_view) / f / 1e6);
    s.t_bind = s.t_view = 0;
    if (s.res_hits || s.geo_res_hits || s.res_moves || s.geo_res_moves)
        log("native renderer: engine resources (no write tracking): textures %llu kept, %llu moved with the same contents, %llu changed | "
            "buffers %llu kept, %llu moved with the same contents, %llu changed",
            (unsigned long long)s.res_hits, (unsigned long long)s.res_moves, (unsigned long long)s.res_changed,
            (unsigned long long)s.geo_res_hits, (unsigned long long)s.geo_res_moves, (unsigned long long)s.geo_res_changed);
    if (s.res_verify_ok || s.res_verify_missed)
        log("native renderer: verify engine textures: %llu unchanged, %llu CHANGED WITHOUT AN EVENT", (unsigned long long)s.res_verify_ok,
            (unsigned long long)s.res_verify_missed);
    s.res_verify_ok = s.res_verify_missed = 0;
    s.res_hits = s.res_moves = s.res_changed = s.geo_res_hits = s.geo_res_moves = s.geo_res_changed = 0;
    if (const double f = double(s.frames - s.t_frames); f > 0) {
        uint64_t texels = 0, big = 0;
        for (auto& [k, v] : s.unreg_tex) texels += v, big += v > 65536;
        log("native renderer: memory that is no engine resource: %zu dynamic textures (%.1f KiB, %llu over 64K) | %.0f write-tracked geometry lookups per frame (%.2f MiB per frame)",
            s.unreg_tex.size(), double(texels) / 1024.0, (unsigned long long)big, double(s.unreg_geo) / f,
            double(s.unreg_geo_bytes) / f / 1048576.0);
        log("native renderer: write-tracked geometry because: vertex buffer not an engine resource %.0f, outside its buffer %.0f, inline %.0f | "
            "index buffer not an engine resource %.0f, outside its buffer %.0f (per frame)", double(s.why_vb_noid) / f, double(s.why_vb_range) / f,
            double(s.why_inline) / f, double(s.why_ib_noid) / f, double(s.why_ib_range) / f);
        s.why_vb_noid = s.why_vb_range = s.why_ib_noid = s.why_ib_range = s.why_inline = 0;
        if (g->dynamic_copy)
            log("native renderer: dynamic memory (no write tracking): %llu CPU writes announced, %llu copies made stale (%llu render targets), %zu ranges tracked%s",
                (unsigned long long)g->dyn_events, (unsigned long long)g->dyn_bumps, (unsigned long long)g->dyn_target_bumps, g->dyn_mem.size(),
                std::getenv("D1_NG_VERIFY_DYN") ? (" | verify: " + std::to_string(g->dyn_verify_hits) + " unchanged, " +
                                                   std::to_string(g->dyn_verify_missed) + " CHANGED WITHOUT AN EVENT").c_str() : "");
        g->dyn_events = g->dyn_bumps = g->dyn_verify_hits = g->dyn_verify_missed = g->dyn_target_bumps = 0;
        log("native renderer: feedback loops: %llu target snapshots copied, %llu reused | copy commands: %llu texture copies made stale",
            (unsigned long long)g->snap_copies, (unsigned long long)g->snap_reused, (unsigned long long)g->dma_stale);
        g->snap_copies = g->snap_reused = g->dma_stale = 0;
        s.unreg_tex.clear(), s.unreg_geo = s.unreg_geo_bytes = 0;
    }
    if (g->load_on) {
        size_t q;
        {
            std::lock_guard lk(g->load_m);
            q = g->load_q.size();
        }
        log("native renderer: loader: %llu textures and %llu buffers uploaded ahead of use, %llu moves kept, %llu already done, "
            "%llu dropped as changed again, %llu over the queue limit | %.1f ms of loader time, %zu queued",
            (unsigned long long)g->ld_tex.exchange(0), (unsigned long long)g->ld_buf.exchange(0), (unsigned long long)g->ld_moves.exchange(0),
            (unsigned long long)g->ld_skipped.exchange(0), (unsigned long long)g->ld_stale.exchange(0), (unsigned long long)g->ld_dropped.exchange(0),
            double(g->ld_ns.exchange(0)) / 1e6, q);
    }
    if (s.zpass_dumps || s.predicated)
        log("native renderer: occlusion: %llu counter dumps, %llu predicated draws%s", (unsigned long long)s.zpass_dumps,
            (unsigned long long)s.predicated, g->ctx.conditional_rendering ? "" : " (no conditional rendering: drawn)");
    s.zpass_dumps = s.predicated = 0;
    s.t_vkimg = s.t_heap = s.heap_scans = s.heap_blocks_new = 0;
    s.t_detile = s.t_fill = s.t_watch = s.t_mkimg = 0;
    s.t_tgt = s.t_tex_hit = s.t_tex_load = s.tex_checks = s.tex_unwatched = 0;
    s.t_pre = s.t_pipe = s.t_geo = s.t_desc = s.t_cmd = s.t_submit = s.t_wait = 0, s.t_frames = s.frames, s.t_draws = s.draws;
    std::string why;
    for (auto& [k, v] : s.skip) why += " " + k + "=" + std::to_string(v);
    if (!why.empty()) log("native renderer: skipped:%s", why.c_str());
}

}  // namespace d1::ng
