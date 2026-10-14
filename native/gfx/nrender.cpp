// Native renderer, Vulkan side. See nrender.h.
//
// Model (milestone "mirror"): each submission's draws are executed synchronously on one
// command buffer. Every image stays in VK_IMAGE_LAYOUT_GENERAL; a full memory barrier sits
// between render passes. Transient data the draws read from guest memory (vertices,
// indices, constants) is copied into a host-visible ring that is reset per submission.
// Textures are detiled and uploaded once per distinct T#; render targets are our own images
// keyed by (address, format, size), and a T# that points at one samples it directly.
#include "nrender.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
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

uint64_t hash_bytes(const void* p, size_t n, uint64_t h = 0xcbf29ce484222325ull) {
    const uint8_t* b = static_cast<const uint8_t*>(p);
    for (size_t i = 0; i < n; ++i) h = (h ^ b[i]) * 0x100000001b3ull;
    return h;
}
uint64_t mix(uint64_t h, uint64_t v) { return hash_bytes(&v, 8, h); }

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
    case 2: case 3: case 4: return VK_STENCIL_OP_REPLACE;
    case 5: return VK_STENCIL_OP_INCREMENT_AND_CLAMP;
    case 6: return VK_STENCIL_OP_DECREMENT_AND_CLAMP;
    case 7: return VK_STENCIL_OP_INVERT;
    case 8: return VK_STENCIL_OP_INCREMENT_AND_WRAP;
    case 9: return VK_STENCIL_OP_DECREMENT_AND_WRAP;
    default: return VK_STENCIL_OP_KEEP;
    }
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
struct Image {
    VkImage image = VK_NULL_HANDLE;
    VkDeviceMemory mem = VK_NULL_HANDLE;
    VkFormat format = VK_FORMAT_UNDEFINED;
    uint32_t w = 1, h = 1, d = 1, layers = 1, levels = 1;
    bool depth = false, stencil = false, cube = false, is3d = false;
    uint32_t swap = 0;  // render target COMP_SWAP
    uint64_t base = 0;
    VkImageView attachment = VK_NULL_HANDLE;
    std::unordered_map<uint64_t, VkImageView> views;
    uint64_t last_used = 0;
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
             shaders = 0, bad_shaders = 0, ring_peak = 0;
    std::unordered_map<std::string, uint64_t> skip;
};

struct Renderer {
    Options opt;
    Context ctx;
    VkCommandPool pool = VK_NULL_HANDLE;
    VkCommandBuffer cmd = VK_NULL_HANDLE;
    VkFence fence = VK_NULL_HANDLE;
    Buffer ring;
    uint64_t ring_pos = 0;
    std::vector<Buffer> staging;  // freed after the submission completes
    std::unordered_map<uint64_t, std::unique_ptr<Image>> targets;   // (base, format, size)
    std::unordered_map<uint64_t, Image*> target_by_base;            // newest target at an address
    std::unordered_map<uint64_t, std::unique_ptr<Image>> textures;  // T# hash
    std::unordered_map<uint64_t, VkSampler> samplers;
    std::unordered_map<uint64_t, std::unique_ptr<Shader>> shaders;
    std::unordered_map<uint64_t, std::unique_ptr<Pipeline>> pipelines;
    std::unique_ptr<Image> dummy[4];  // per TexDim
    VkSampler dummy_sampler = VK_NULL_HANDLE;
    uint64_t submit_no = 0;
    Stats st;

    // per-submission recording state
    bool in_pass = false;
    uint64_t pass_key = 0;
    Image* pass_color[8] = {};
    Image* pass_depth = nullptr;
    uint32_t pass_w = 0, pass_h = 0;

    bool init(const Options& o);
    Buffer make_buffer(uint64_t size, VkBufferUsageFlags usage, bool host);
    void free_buffer(Buffer& b);
    VkDeviceMemory alloc(VkMemoryRequirements req, VkMemoryPropertyFlags want);
    std::unique_ptr<Image> make_image(VkFormat f, uint32_t w, uint32_t h, uint32_t d, uint32_t layers, uint32_t levels,
                                      bool cube, bool is3d, bool depth, bool stencil);
    VkImageView view(Image* img, VkImageViewType type, VkComponentMapping comp, uint32_t base_level, bool depth_aspect);
    uint64_t ring_alloc(uint64_t size, uint64_t align = 256);
    uint64_t ring_copy(const void* src, uint64_t size);
    void barrier();
    Image* color_target(const uint32_t* c);
    Image* depth_target(const uint32_t* d);
    VkImageView texture_view(const uint32_t* t, gcn::TexDim dim);
    Image* upload_texture(const uint32_t* t);
    VkSampler sampler(const uint32_t* s);
    Shader* shader(const Draw& dr, bool vs, const gcn::TexDim* dims);
    Pipeline* pipeline(const Draw& dr, Image* const* colors, Image* depth);
    void begin_pass(Image* const* colors, Image* depth);
    void end_pass();
    void skip(const char* why) {
        ++st.skipped;
        ++st.skip[why];
    }
    void draw(const Draw& dr);
    void clear(const Draw& dr);
    void execute(const std::vector<Draw*>& draws);
    void dump(uint64_t addr, uint32_t w, uint32_t h, uint64_t frame);
    bool save_image(Image* img, const char* path);
    uint64_t frame_first_submit = 0;
};

Renderer* g = nullptr;

bool Renderer::init(const Options& o) {
    opt = o;
    char err[512];
    int gpu = -1;
    if (const char* v = std::getenv("D1_GPU")) gpu = std::atoi(v);
    if (!create_context(ctx, gpu, nullptr, 0, err, sizeof err)) {
        log("native renderer: %s", err);
        return false;
    }
    VkCommandPoolCreateInfo pci{VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO};
    pci.flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;
    pci.queueFamilyIndex = ctx.queue_family;
    vkCreateCommandPool(ctx.device, &pci, nullptr, &pool);
    VkCommandBufferAllocateInfo cai{VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};
    cai.commandPool = pool;
    cai.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
    cai.commandBufferCount = 1;
    vkAllocateCommandBuffers(ctx.device, &cai, &cmd);
    VkFenceCreateInfo fci{VK_STRUCTURE_TYPE_FENCE_CREATE_INFO};
    vkCreateFence(ctx.device, &fci, nullptr, &fence);
    uint64_t ring_mb = 512;
    if (const char* v = std::getenv("D1_NG_RING_MB")) ring_mb = std::strtoull(v, nullptr, 10);
    ring = make_buffer(ring_mb << 20, VK_BUFFER_USAGE_VERTEX_BUFFER_BIT | VK_BUFFER_USAGE_INDEX_BUFFER_BIT |
                                          VK_BUFFER_USAGE_STORAGE_BUFFER_BIT | VK_BUFFER_USAGE_TRANSFER_SRC_BIT |
                                          VK_BUFFER_USAGE_TRANSFER_DST_BIT, true);
    if (!ring.map) {
        log("native renderer: no host-visible memory for the %llu MiB upload ring", (unsigned long long)ring_mb);
        return false;
    }
    // placeholder textures for unbound slots (black, alpha 0)
    vkResetCommandBuffer(cmd, 0);
    VkCommandBufferBeginInfo bi{VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
    vkBeginCommandBuffer(cmd, &bi);
    for (int k = 0; k < 4; ++k) {
        const auto dim = gcn::TexDim(k);
        dummy[k] = make_image(VK_FORMAT_R8G8B8A8_UNORM, 1, 1, 1, dim == gcn::TexDim::Cube ? 6 : 1, 1,
                              dim == gcn::TexDim::Cube, dim == gcn::TexDim::Tex3D, false, false);
        VkClearColorValue zero{};
        VkImageSubresourceRange r{VK_IMAGE_ASPECT_COLOR_BIT, 0, 1, 0, VK_REMAINING_ARRAY_LAYERS};
        vkCmdClearColorImage(cmd, dummy[k]->image, VK_IMAGE_LAYOUT_GENERAL, &zero, 1, &r);
    }
    vkEndCommandBuffer(cmd);
    VkCommandBufferSubmitInfo cbi{VK_STRUCTURE_TYPE_COMMAND_BUFFER_SUBMIT_INFO};
    cbi.commandBuffer = cmd;
    VkSubmitInfo2 si{VK_STRUCTURE_TYPE_SUBMIT_INFO_2};
    si.commandBufferInfoCount = 1;
    si.pCommandBufferInfos = &cbi;
    vkQueueSubmit2(ctx.queue, 1, &si, fence);
    vkWaitForFences(ctx.device, 1, &fence, VK_TRUE, UINT64_MAX);
    vkResetFences(ctx.device, 1, &fence);
    VkSamplerCreateInfo sci{VK_STRUCTURE_TYPE_SAMPLER_CREATE_INFO};
    vkCreateSampler(ctx.device, &sci, nullptr, &dummy_sampler);
    log("native renderer: %s, Vulkan %u.%u, %llu MiB upload ring%s", ctx.name, VK_API_VERSION_MAJOR(ctx.api_version),
        VK_API_VERSION_MINOR(ctx.api_version), (unsigned long long)ring_mb,
        opt.frames_dir ? ", writing frames" : "");
    return true;
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

Buffer Renderer::make_buffer(uint64_t size, VkBufferUsageFlags usage, bool host) {
    Buffer b;
    b.size = size;
    VkBufferCreateInfo bci{VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
    bci.size = size;
    bci.usage = usage;
    if (vkCreateBuffer(ctx.device, &bci, nullptr, &b.buf) != VK_SUCCESS) return Buffer{};
    VkMemoryRequirements req;
    vkGetBufferMemoryRequirements(ctx.device, b.buf, &req);
    b.mem = alloc(req, host ? VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT
                            : VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
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
    ici.flags = (cube ? VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT : 0) | VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT;
    ici.imageType = is3d ? VK_IMAGE_TYPE_3D : VK_IMAGE_TYPE_2D;
    ici.format = f;
    ici.extent = {w, h, is3d ? d : 1};
    ici.mipLevels = levels;
    ici.arrayLayers = is3d ? 1 : layers;
    ici.samples = VK_SAMPLE_COUNT_1_BIT;
    ici.tiling = VK_IMAGE_TILING_OPTIMAL;
    ici.usage = VK_IMAGE_USAGE_SAMPLED_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT | VK_IMAGE_USAGE_TRANSFER_SRC_BIT;
    const bool bc = f >= VK_FORMAT_BC1_RGB_UNORM_BLOCK && f <= VK_FORMAT_BC7_SRGB_BLOCK;
    if (depth) ici.usage |= VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT;
    else if (!bc) ici.usage |= VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT;
    ici.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
    if (vkCreateImage(ctx.device, &ici, nullptr, &img->image) != VK_SUCCESS) return nullptr;
    VkMemoryRequirements req;
    vkGetImageMemoryRequirements(ctx.device, img->image, &req);
    img->mem = alloc(req, VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
    if (!img->mem) {
        vkDestroyImage(ctx.device, img->image, nullptr);
        return nullptr;
    }
    vkBindImageMemory(ctx.device, img->image, img->mem, 0);
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
    vkCmdPipelineBarrier2(cmd, &di);
    if (!bc) {
        VkImageViewCreateInfo vci{VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};
        vci.image = img->image;
        vci.viewType = VK_IMAGE_VIEW_TYPE_2D;
        vci.format = f;
        vci.subresourceRange = {b.subresourceRange.aspectMask, 0, 1, 0, 1};
        if (!is3d) vkCreateImageView(ctx.device, &vci, nullptr, &img->attachment);
    }
    return img;
}

VkImageView Renderer::view(Image* img, VkImageViewType type, VkComponentMapping comp, uint32_t base_level,
                           bool depth_aspect) {
    if (img->is3d) type = VK_IMAGE_VIEW_TYPE_3D;
    if (type == VK_IMAGE_VIEW_TYPE_CUBE && (!img->cube || img->layers < 6)) type = VK_IMAGE_VIEW_TYPE_2D_ARRAY;
    if (type == VK_IMAGE_VIEW_TYPE_3D && !img->is3d) type = VK_IMAGE_VIEW_TYPE_2D_ARRAY;
    const uint64_t key = mix(mix(mix(type, uint64_t(comp.r) | uint64_t(comp.g) << 8 | uint64_t(comp.b) << 16 |
                                               uint64_t(comp.a) << 24),
                                 base_level),
                             depth_aspect);
    auto it = img->views.find(key);
    if (it != img->views.end()) return it->second;
    VkImageViewCreateInfo vci{VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};
    vci.image = img->image;
    vci.viewType = type;
    vci.format = img->format;
    vci.components = img->depth ? VkComponentMapping{} : comp;
    const uint32_t lvl = std::min(base_level, img->levels - 1);
    vci.subresourceRange = {img->depth ? VkImageAspectFlags(VK_IMAGE_ASPECT_DEPTH_BIT) : VkImageAspectFlags(VK_IMAGE_ASPECT_COLOR_BIT),
                            lvl, img->levels - lvl, 0,
                            type == VK_IMAGE_VIEW_TYPE_CUBE ? 6u
                            : type == VK_IMAGE_VIEW_TYPE_2D || type == VK_IMAGE_VIEW_TYPE_3D ? 1u
                                                                                            : img->layers};
    VkImageView v = VK_NULL_HANDLE;
    vkCreateImageView(ctx.device, &vci, nullptr, &v);
    img->views[key] = v;
    return v;
}

uint64_t Renderer::ring_alloc(uint64_t size, uint64_t align) {
    uint64_t p = (ring_pos + align - 1) & ~(align - 1);
    if (p + size > ring.size) return UINT64_MAX;
    ring_pos = p + size;
    st.ring_peak = std::max(st.ring_peak, ring_pos);
    return p;
}

uint64_t Renderer::ring_copy(const void* src, uint64_t size) {
    const uint64_t p = ring_alloc(std::max<uint64_t>(size, 16));
    if (p == UINT64_MAX) return p;
    std::memcpy(ring.map + p, src, size);
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
    vkCmdPipelineBarrier2(cmd, &di);
}

// Gnm RenderTarget: CB_COLOR_BASE, PITCH, SLICE, VIEW, INFO, ATTRIB, packed size, CMASK...
Image* Renderer::color_target(const uint32_t* c) {
    const uint64_t base = uint64_t(c[0]) << 8;
    const uint32_t format = (c[4] >> 2) & 0x1F, number = (c[4] >> 8) & 7, swap = (c[4] >> 11) & 3;
    if (!base || !format) return nullptr;
    const uint32_t w = c[6] & 0xFFFF, h = c[6] >> 16;
    if (!w || !h) return nullptr;
    VkFormat f = fmt::vk_format(fmt::color_to_data_format(format), cb_number_to_nfmt(number));
    if (f == VK_FORMAT_UNDEFINED) return nullptr;
    const uint64_t key = mix(mix(mix(base, f), w), h);
    auto it = targets.find(key);
    Image* img;
    if (it != targets.end()) img = it->second.get();
    else {
        auto n = make_image(f, w, h, 1, 1, 1, false, false, false, false);
        if (!n) return nullptr;
        n->base = base, n->swap = swap;
        img = n.get();
        targets[key] = std::move(n);
        ++st.targets;
    }
    target_by_base[base] = img;
    img->last_used = submit_no;
    return img;
}

// Gnm DepthRenderTarget: Z_INFO, STENCIL_INFO, Z_READ_BASE, STENCIL_READ_BASE, Z_WRITE_BASE,
// STENCIL_WRITE_BASE, DEPTH_SIZE, DEPTH_SLICE, DEPTH_VIEW, HTILE_DATA_BASE, HTILE_SURFACE,
// DEPTH_INFO, packed size
Image* Renderer::depth_target(const uint32_t* d) {
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
        n->base = base;
        img = n.get();
        targets[key] = std::move(n);
        ++st.targets;
    }
    target_by_base[base] = img;
    target_by_base[uint64_t(d[2]) << 8] = img;  // Z_READ_BASE
    img->last_used = submit_no;
    return img;
}

Image* Renderer::upload_texture(const uint32_t* t) {
    const uint64_t key = hash_bytes(t, 32);
    auto it = textures.find(key);
    if (it != textures.end()) return it->second.get();
    const auto ts = fmt::decode_tsharp(t);
    const auto fi = fmt::data_format(ts.dfmt);
    const VkFormat f = fmt::vk_format(ts.dfmt, ts.nfmt);
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
            textures[key] = nullptr;
            return nullptr;
        }
        auto img = make_image(f, ts.width, ts.height, sf.depth, sf.layers, sf.levels, cube, is3d, false, false);
        if (img) {
            uint64_t total = 0;
            std::vector<uint64_t> sizes(sf.levels);
            for (uint32_t lv = 0; lv < sf.levels; ++lv) {
                const uint32_t mw = std::max(1u, ts.width >> lv), mh = std::max(1u, ts.height >> lv);
                const uint32_t ew = fi.block ? (mw + 3) / 4 : mw, eh = fi.block ? (mh + 3) / 4 : mh;
                sizes[lv] = uint64_t(ew) * eh * (fi.bpp / 8) * std::max(1u, is3d ? std::max(1u, sf.depth >> lv) : sf.layers);
                total += (sizes[lv] + 15) & ~15ull;
            }
            Buffer sb = make_buffer(std::max<uint64_t>(total, 16), VK_BUFFER_USAGE_TRANSFER_SRC_BIT, true);
            if (sb.map) {
                std::vector<VkBufferImageCopy> regions;
                uint64_t off = 0;
                for (uint32_t lv = 0; lv < sf.levels; ++lv) {
                    tiling::detile(sf, lv, reinterpret_cast<const uint8_t*>(ts.base), sb.map + off);
                    VkBufferImageCopy r{};
                    r.bufferOffset = off;
                    r.imageSubresource = {VK_IMAGE_ASPECT_COLOR_BIT, lv, 0, is3d ? 1u : sf.layers};
                    r.imageExtent = {std::max(1u, ts.width >> lv), std::max(1u, ts.height >> lv),
                                     is3d ? std::max(1u, sf.depth >> lv) : 1u};
                    regions.push_back(r);
                    off += (sizes[lv] + 15) & ~15ull;
                }
                vkCmdCopyBufferToImage(cmd, sb.buf, img->image, VK_IMAGE_LAYOUT_GENERAL, uint32_t(regions.size()),
                                       regions.data());
                staging.push_back(sb);
                out = img.get();
                ++st.textures;
            }
            textures[key] = std::move(img);
            if (!out) textures.erase(key);
        }
    }
    if (!out) textures[key] = nullptr;
    return out;
}

VkImageView Renderer::texture_view(const uint32_t* t, gcn::TexDim dim) {
    const auto vt = view_type(dim);
    if (!t) return view(dummy[int(dim)].get(), vt, {}, 0, false);
    const auto ts = fmt::decode_tsharp(t);
    VkComponentMapping comp{swz(ts.dst_sel & 7), swz(ts.dst_sel >> 3 & 7), swz(ts.dst_sel >> 6 & 7),
                            swz(ts.dst_sel >> 9 & 7)};
    auto rt = target_by_base.find(ts.base);
    if (rt != target_by_base.end()) {
        Image* img = rt->second;
        if (img->depth) return view(img, VK_IMAGE_VIEW_TYPE_2D, {}, 0, true);
        // the render target stored shader component k in memory channel swap(k); our image
        // holds shader components, so map the T#'s memory channels back
        if (img->swap == 1) {
            auto back = [](VkComponentSwizzle s) {
                return s == VK_COMPONENT_SWIZZLE_R ? VK_COMPONENT_SWIZZLE_B : s == VK_COMPONENT_SWIZZLE_B ? VK_COMPONENT_SWIZZLE_R : s;
            };
            comp = {back(comp.r), back(comp.g), back(comp.b), back(comp.a)};
        }
        return view(img, VK_IMAGE_VIEW_TYPE_2D, comp, 0, false);
    }
    auto it = textures.find(hash_bytes(t, 32));
    Image* img = it != textures.end() ? it->second.get() : nullptr;
    if (!img) return view(dummy[int(dim)].get(), vt, {}, 0, false);
    return view(img, vt, comp, ts.base_level, false);
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

Shader* Renderer::shader(const Draw& dr, bool vs, const gcn::TexDim* dims) {
    const uint8_t* obj = vs ? dr.vs : dr.ps;
    uint64_t key = mix(mix(uint64_t(obj), vs), hash_bytes(dims, 16));
    if (!vs) key = mix(key, uint64_t(dr.vs));  // the input mapping depends on the VS
    auto it = shaders.find(key);
    if (it != shaders.end()) return it->second.get();
    auto sh = std::make_unique<Shader>();
    const GnmShader g = parse_shader(obj, vs);
    gcn::ShaderDesc d;
    d.stage = vs ? gcn::Stage::Vertex : gcn::Stage::Pixel;
    d.code = g.code, d.code_size = g.code_size, d.slots = g.slots, d.user_sgprs = g.user_sgprs;
    d.ps_input_addr = g.ps_input_addr, d.fetch = g.fetch, d.fetch_size = g.fetch_size;
    for (int i = 0; i < 16; ++i) d.tex_dims[i] = dims[i];
    if (!vs) {
        const GnmShader v = parse_shader(dr.vs, true);
        d.remap_inputs = true;
        std::memset(d.input_location, 0xFF, sizeof d.input_location);
        for (size_t i = 0; i < g.semantics.size() && i < 32; ++i)
            for (uint16_t e : v.semantics)
                if ((e & 0xFF) == (g.semantics[i] & 0xFF)) d.input_location[i] = uint8_t(e >> 8 & 0x1F);
    }
    if (g.code && g.code_size) {
        sh->res = gcn::translate(d);
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

Pipeline* Renderer::pipeline(const Draw& dr, Image* const* colors, Image* depth) {
    gcn::TexDim dims[2][16];
    for (int s = 0; s < 2; ++s)
        for (int i = 0; i < 16; ++i) {
            dims[s][i] = slot_dim(dr.tex[s][i]);
            // a T# on a render target samples our 2D target image
            if (dr.tex[s][i] && target_by_base.count(fmt::decode_tsharp(dr.tex[s][i]).base)) dims[s][i] = gcn::TexDim::Tex2D;
        }
    Shader* vs = shader(dr, true, dims[0]);
    Shader* ps = dr.ps ? shader(dr, false, dims[1]) : nullptr;  // no pixel shader: depth-only
    if (!vs->ok || (ps && !ps->ok)) return nullptr;
    VkPrimitiveTopology topo;
    if (!topology_of(dr.prim, topo)) return nullptr;
    // key
    uint64_t key = mix(mix(uint64_t(vs), uint64_t(ps)), topo);
    for (const auto& a : vs->res.attribs) {
        const uint32_t* v = dr.vb[a.vb_slot & 15];
        key = mix(key, (v[1] >> 16 & 0x3FFF) | uint64_t(v[3] >> 12 & 0x7F) << 16);
    }
    key = mix(key, dr.blend), key = mix(key, dr.target_mask), key = mix(key, dr.su_sc_mode);
    key = mix(key, dr.depth_ctl), key = mix(key, dr.stencil_ctl);
    for (int i = 0; i < 8; ++i) key = mix(key, colors[i] ? colors[i]->format : 0);
    key = mix(key, depth ? depth->format : 0);
    auto it = pipelines.find(key);
    if (it != pipelines.end()) return it->second.get();

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
        dci.flags = VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT;
        dci.bindingCount = uint32_t(b.size());
        dci.pBindings = b.data();
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
        VkFormat f = vertex_format(dfmt, nfmt);
        if (f == VK_FORMAT_UNDEFINED) f = VK_FORMAT_R32G32B32A32_SFLOAT;
        if (std::none_of(vbind.begin(), vbind.end(), [&](auto& x) { return x.binding == a.vb_slot; }))
            vbind.push_back({a.vb_slot, stride, VK_VERTEX_INPUT_RATE_VERTEX});
        vattr.push_back({a.location, a.vb_slot, f, a.offset});
    }
    VkPipelineVertexInputStateCreateInfo vi{VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO};
    vi.vertexBindingDescriptionCount = uint32_t(vbind.size());
    vi.pVertexBindingDescriptions = vbind.data();
    vi.vertexAttributeDescriptionCount = uint32_t(vattr.size());
    vi.pVertexAttributeDescriptions = vattr.data();
    VkPipelineInputAssemblyStateCreateInfo ia{VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO};
    ia.topology = topo;
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
    if (vkCreateGraphicsPipelines(ctx.device, VK_NULL_HANDLE, 1, &gci, nullptr, &p->pipeline) != VK_SUCCESS)
        p->pipeline = VK_NULL_HANDLE;
    ++st.pipelines;
    Pipeline* out = p.get();
    pipelines[key] = std::move(p);
    return out->pipeline ? out : nullptr;
}

void Renderer::end_pass() {
    if (!in_pass) return;
    vkCmdEndRendering(cmd);
    in_pass = false;
    barrier();
}

void Renderer::begin_pass(Image* const* colors, Image* depth) {
    uint64_t key = uint64_t(depth);
    for (int i = 0; i < 8; ++i) key = mix(key, uint64_t(colors[i]));
    if (in_pass && key == pass_key) return;
    end_pass();
    VkRenderingAttachmentInfo ca[8]{};
    uint32_t n = 0, w = UINT32_MAX, h = UINT32_MAX;
    for (uint32_t i = 0; i < 8; ++i) {
        ca[i] = {VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO};
        if (colors[i]) {
            n = i + 1;
            ca[i].imageView = colors[i]->attachment;
            ca[i].imageLayout = VK_IMAGE_LAYOUT_GENERAL;
            ca[i].loadOp = VK_ATTACHMENT_LOAD_OP_LOAD;
            ca[i].storeOp = VK_ATTACHMENT_STORE_OP_STORE;
            w = std::min(w, colors[i]->w), h = std::min(h, colors[i]->h);
        }
        pass_color[i] = colors[i];
    }
    VkRenderingAttachmentInfo da{VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO};
    if (depth) {
        da.imageView = depth->attachment;
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
    vkCmdBeginRendering(cmd, &ri);
    in_pass = true;
    pass_key = key, pass_depth = depth, pass_w = w, pass_h = h;
}

void Renderer::clear(const Draw& dr) {
    Image* colors[8] = {};
    for (int i = 0; i < 5; ++i) colors[i] = color_target(dr.color[i]);
    Image* depth = depth_target(dr.depth);
    begin_pass(colors, depth);
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
    if ((dr.clear_flags & 0x80) && depth && depth->stencil) da |= VK_IMAGE_ASPECT_STENCIL_BIT;
    if (da) {
        att[n] = {da, 0, {}};
        att[n].clearValue.depthStencil = {dr.clear_depth, dr.clear_stencil};
        ++n;
    }
    if (!n) return;
    int32_t x = std::max(0, dr.vp[0]), y = std::max(0, dr.vp[1]);
    uint32_t w = dr.vp[2] > 0 ? uint32_t(dr.vp[2]) : pass_w, h = dr.vp[3] > 0 ? uint32_t(dr.vp[3]) : pass_h;
    w = std::min(w, pass_w - std::min<uint32_t>(pass_w, uint32_t(x)));
    h = std::min(h, pass_h - std::min<uint32_t>(pass_h, uint32_t(y)));
    if (!w || !h) return;
    VkClearRect r{{{x, y}, {w, h}}, 0, 1};
    vkCmdClearAttachments(cmd, n, att, 1, &r);
    ++st.clears;
}

void Renderer::draw(const Draw& dr) {
    if (!dr.vs || uint64_t(dr.vs) < 0x10000 || (dr.ps && uint64_t(dr.ps) < 0x10000)) {
        static std::unordered_set<uint64_t> seen;
        if (seen.insert(dr.caller).second && seen.size() < 20)
            log("native renderer: draw without shaders (vs %p ps %p) from eboot+%#llx", (const void*)dr.vs,
                (const void*)dr.ps, (unsigned long long)dr.caller);
        return skip("no shader");
    }
    Image* colors[8] = {};
    for (int i = 0; i < 5; ++i) colors[i] = color_target(dr.color[i]);
    Image* depth = depth_target(dr.depth);
    if (!depth && std::none_of(colors, colors + 8, [](Image* x) { return x != nullptr; })) return skip("no target");
    Pipeline* p = pipeline(dr, colors, depth);
    if (!p) return skip("pipeline");
    // geometry into the ring
    VkBuffer vbufs[16];
    VkDeviceSize voffs[16], vsizes[16];
    uint32_t vmask = 0;
    // vertices the draw can reference: [first, last] from the indices
    uint32_t vfirst = 0, vlast = dr.count ? dr.count - 1 : 0;
    if (dr.kind == Draw::Indexed && dr.index_addr >= 0x10000 && dr.count) {
        vfirst = UINT32_MAX, vlast = 0;
        if (dr.index32) {
            const uint32_t* ix = reinterpret_cast<const uint32_t*>(dr.index_addr);
            for (uint32_t i = 0; i < dr.count; ++i) vfirst = std::min(vfirst, ix[i]), vlast = std::max(vlast, ix[i]);
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
        const uint32_t first = stride ? vfirst : 0, last = stride ? std::min(vlast, records - 1) : 0;
        if (first >= records && stride) {  // every fetch is out of range: reads 0, as on GCN
            const uint64_t off = ring_alloc(16);
            if (off == UINT64_MAX) return skip("ring full");
            std::memset(ring.map + off, 0, 16);
            vbufs[slot] = ring.buf, voffs[slot] = off, vsizes[slot] = 16;
            vmask |= 1u << slot;
            continue;
        }
        uint64_t size = stride ? uint64_t(last - first + 1) * stride : 16;
        uint64_t src = base + uint64_t(first) * stride;
        if (!dr.inline_vertices.empty()) {  // V# base is an offset into the inline data
            if (src >= dr.inline_vertices.size()) return skip("inline vertex offset");
            size = std::min<uint64_t>(size, dr.inline_vertices.size() - src);
            src += uint64_t(dr.inline_vertices.data());
        } else if (base < 0x10000) return skip("null vertex buffer");
        size = std::min<uint64_t>(size, 64ull << 20);
        const uint64_t off = ring_alloc(std::max<uint64_t>(size, 16), 256);
        if (off == UINT64_MAX) return skip("ring full");
        std::memcpy(ring.map + off, reinterpret_cast<const void*>(src), size);
        if (size < 16) std::memset(ring.map + off + size, 0, 16 - size);
        // the binding starts at vertex `vfirst`; a stride-0 stream is one record for every vertex
        vbufs[slot] = ring.buf, voffs[slot] = off, vsizes[slot] = std::max<uint64_t>(size, 16);
        vmask |= 1u << slot;
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
                images[s][nw[s]] = {VK_NULL_HANDLE, texture_view(dr.tex[s][slot], slot_dim(dr.tex[s][slot])),
                                    VK_IMAGE_LAYOUT_GENERAL};
                if (dr.tex[s][slot] && target_by_base.count(fmt::decode_tsharp(dr.tex[s][slot]).base))
                    images[s][nw[s]].imageView = texture_view(dr.tex[s][slot], gcn::TexDim::Tex2D);
                w.pImageInfo = &images[s][nw[s]];
            } else if (b.kind == gcn::Binding::Sampler) {
                w.descriptorType = VK_DESCRIPTOR_TYPE_SAMPLER;
                images[s][nw[s]] = {sampler(dr.smp[s][slot]), VK_NULL_HANDLE, VK_IMAGE_LAYOUT_GENERAL};
                w.pImageInfo = &images[s][nw[s]];
            } else {
                w.descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
                const auto& c = dr.cb[s][slot];
                uint64_t off;
                uint32_t size = std::max(16u, (c.size + 15) & ~15u);
                if (c.addr >= 0x10000) off = ring_copy(reinterpret_cast<const void*>(c.addr), c.size);
                else off = ring_alloc(size), std::memset(ring.map + (off == UINT64_MAX ? 0 : off), 0, size);
                if (off == UINT64_MAX) return skip("ring full");
                bufs[s][nw[s]] = {ring.buf, off, size};
                w.pBufferInfo = &bufs[s][nw[s]];
            }
            ++nw[s];
        }
    }
    // indices
    uint32_t count = dr.count;
    uint64_t ioff = 0;
    bool indexed = dr.kind == Draw::Indexed;
    VkIndexType itype = dr.index32 ? VK_INDEX_TYPE_UINT32 : VK_INDEX_TYPE_UINT16;
    if (dr.prim == 0x13 && indexed && dr.index_addr < 0x10000) return skip("null index buffer");
    if (dr.prim == 0x13) {  // quad list -> two triangles per quad
        const uint32_t quads = count / 4;
        const uint64_t o = ring_alloc(uint64_t(quads) * 6 * 4, 4);
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
    } else if (indexed) {
        if (dr.index_addr < 0x10000) return skip("null index buffer");
        ioff = ring_copy(reinterpret_cast<const void*>(dr.index_addr), uint64_t(count) * (dr.index32 ? 4 : 2));
        if (ioff == UINT64_MAX) return skip("ring full");
    }
    if (!count) return;

    begin_pass(colors, depth);
    vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, p->pipeline);
    for (int s = 0; s < 2; ++s)
        if (nw[s]) vkCmdPushDescriptorSet(cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, p->layout, uint32_t(s), nw[s], writes[s]);
    for (uint32_t slot = 0; slot < 16; ++slot)
        if (vmask >> slot & 1) vkCmdBindVertexBuffers2(cmd, slot, 1, &vbufs[slot], &voffs[slot], &vsizes[slot], nullptr);
    // viewport (GCN y points down the screen: flip with a negative height)
    VkViewport vp{};
    vp.x = float(dr.vp[0]), vp.width = float(dr.vp[2] > 0 ? dr.vp[2] : int32_t(pass_w));
    vp.y = float(dr.vp[1] + (dr.vp[3] > 0 ? dr.vp[3] : int32_t(pass_h)));
    vp.height = -float(dr.vp[3] > 0 ? dr.vp[3] : int32_t(pass_h));
    const float range = dr.zfar - dr.znear;
    float zmin = range != 0 ? dr.znear / range : 0.0f, zmax = range != 0 ? zmin + dr.zk / range : 1.0f;
    vp.minDepth = std::clamp(zmin, 0.0f, 1.0f), vp.maxDepth = std::clamp(zmax, 0.0f, 1.0f);
    vkCmdSetViewport(cmd, 0, 1, &vp);
    const int32_t sx = std::max(0, dr.vp[0]), sy = std::max(0, dr.vp[1]);
    VkRect2D sc{{sx, sy},
                {std::min<uint32_t>(pass_w - std::min<uint32_t>(pass_w, sx), uint32_t(std::max(1.0f, vp.width))),
                 std::min<uint32_t>(pass_h - std::min<uint32_t>(pass_h, sy), uint32_t(std::max(1.0f, -vp.height)))}};
    vkCmdSetScissor(cmd, 0, 1, &sc);
    vkCmdSetStencilReference(cmd, VK_STENCIL_FACE_FRONT_AND_BACK, dr.stencil_ref & 0xFF);
    vkCmdSetStencilCompareMask(cmd, VK_STENCIL_FACE_FRONT_AND_BACK, dr.stencil_ref >> 8 & 0xFF);
    vkCmdSetStencilWriteMask(cmd, VK_STENCIL_FACE_FRONT_AND_BACK, dr.stencil_ref >> 16 & 0xFF);
    vkCmdSetDepthBias(cmd, dr.poly_offset, 0.0f, dr.poly_scale);
    if (indexed) {
        vkCmdBindIndexBuffer(cmd, ring.buf, ioff, itype);
        vkCmdDrawIndexed(cmd, count, std::max(1u, dr.instances), 0, -int32_t(vfirst), 0);
    } else {
        vkCmdDraw(cmd, count, std::max(1u, dr.instances), 0, 0);
    }
    ++st.draws;
}

void Renderer::execute(const std::vector<Draw*>& draws) {
    ++submit_no;
    ++st.submits;
    ring_pos = 0;
    vkResetCommandBuffer(cmd, 0);
    VkCommandBufferBeginInfo bi{VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
    bi.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
    vkBeginCommandBuffer(cmd, &bi);
    // resources first (copies cannot run inside a render pass): targets, then textures
    for (Draw* d : draws) {
        for (int i = 0; i < 5; ++i) color_target(d->color[i]);
        depth_target(d->depth);
    }
    for (Draw* d : draws)
        for (int s = 0; s < 2; ++s)
            for (int i = 0; i < 16; ++i)
                if (const uint32_t* t = d->tex[s][i]; t && !target_by_base.count(fmt::decode_tsharp(t).base))
                    upload_texture(t);
    barrier();
    for (Draw* d : draws) {
        if (d->kind == Draw::Clear) clear(*d);
        else draw(*d);
    }
    end_pass();
    vkEndCommandBuffer(cmd);
    VkCommandBufferSubmitInfo cbi{VK_STRUCTURE_TYPE_COMMAND_BUFFER_SUBMIT_INFO};
    cbi.commandBuffer = cmd;
    VkSubmitInfo2 si{VK_STRUCTURE_TYPE_SUBMIT_INFO_2};
    si.commandBufferInfoCount = 1;
    si.pCommandBufferInfos = &cbi;
    vkQueueSubmit2(ctx.queue, 1, &si, fence);
    vkWaitForFences(ctx.device, 1, &fence, VK_TRUE, UINT64_MAX);
    vkResetFences(ctx.device, 1, &fence);
    for (auto& b : staging) free_buffer(b);
    staging.clear();
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
    vkResetCommandBuffer(cmd, 0);
    VkCommandBufferBeginInfo bi{VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
    vkBeginCommandBuffer(cmd, &bi);
    barrier();
    VkBufferImageCopy r{};
    r.imageSubresource = {img->depth ? VkImageAspectFlags(VK_IMAGE_ASPECT_DEPTH_BIT) : VkImageAspectFlags(VK_IMAGE_ASPECT_COLOR_BIT), 0, 0, 1};
    r.imageExtent = {w, h, 1};
    vkCmdCopyImageToBuffer(cmd, img->image, VK_IMAGE_LAYOUT_GENERAL, rb.buf, 1, &r);
    vkEndCommandBuffer(cmd);
    VkCommandBufferSubmitInfo cbi{VK_STRUCTURE_TYPE_COMMAND_BUFFER_SUBMIT_INFO};
    cbi.commandBuffer = cmd;
    VkSubmitInfo2 si{VK_STRUCTURE_TYPE_SUBMIT_INFO_2};
    si.commandBufferInfoCount = 1;
    si.pCommandBufferInfos = &cbi;
    vkQueueSubmit2(ctx.queue, 1, &si, fence);
    vkWaitForFences(ctx.device, 1, &fence, VK_TRUE, UINT64_MAX);
    vkResetFences(ctx.device, 1, &fence);
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
        for (auto& [k, img] : targets)
            if (img && img->last_used > frame_first_submit) {
                std::snprintf(path, sizeof path, "%s/f%06llu_rt%02d_%llx_%ux%u_f%d.ppm", opt.frames_dir,
                              (unsigned long long)frame, n++, (unsigned long long)img->base, img->w, img->h,
                              int(img->format));
                save_image(img.get(), path);
            }
    }
    frame_first_submit = submit_no;
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
    if (g) g->execute(draws);
}
void flip(uint64_t addr, uint32_t w, uint32_t h, uint64_t frame) {
    if (!g) return;
    ++g->st.frames;
    if (addr) g->dump(addr, w, h, frame);
    else g->frame_first_submit = g->submit_no;
}
void print_stats() {
    if (!g) return;
    auto& s = g->st;
    log("native renderer: %llu frames, %llu submissions | %llu draws, %llu clears, %llu skipped | %llu pipelines, "
        "%llu shaders (%llu failed), %llu textures, %llu targets | ring peak %.1f MiB",
        (unsigned long long)s.frames, (unsigned long long)s.submits, (unsigned long long)s.draws,
        (unsigned long long)s.clears, (unsigned long long)s.skipped, (unsigned long long)s.pipelines,
        (unsigned long long)s.shaders, (unsigned long long)s.bad_shaders, (unsigned long long)s.textures,
        (unsigned long long)s.targets, double(s.ring_peak) / 1048576.0);
    std::string why;
    for (auto& [k, v] : s.skip) why += " " + k + "=" + std::to_string(v);
    if (!why.empty()) log("native renderer: skipped:%s", why.c_str());
}

}  // namespace d1::ng
