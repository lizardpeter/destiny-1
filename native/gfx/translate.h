// GCN (gfx7) -> SPIR-V shader translation for the native renderer.
//
// d1-native's own translator. The model is one SPIR-V invocation per GCN lane:
// - Scalar registers are per-invocation copies (all lanes compute the same values).
// - The 64-bit lane masks (EXEC, VCC, compare results) become this lane's bit, stored as
//   0/1 in the low half.
// - Vector writes are predicated by the lane's EXEC bit.
// - Skip branches on an empty EXEC (s_cbranch_execz/execnz) are dropped: predication already
//   makes them no-ops. Other branches run through a per-invocation program-counter loop,
//   which keeps the SPIR-V structured for any control flow.
//
// Resources are resolved statically: user SGPRs and extended user data (Gnm input usage
// slots), resource tables and the SMRD loads that read them map every T#, S# and V# the
// shader uses to an engine API slot. Each slot becomes a descriptor binding:
//   set = stage (0 vertex, 1 pixel); binding = texture slot, 16 + sampler slot,
//   32 + constant buffer slot.
#pragma once
#include <cstdint>
#include <string>
#include <vector>

namespace d1::gcn {

enum class Stage : uint8_t { Vertex, Pixel };

struct UsageSlot {
    uint8_t type, api_slot, start_reg, flags;
};
// Gnm input usage types used by Destiny 1's shaders
enum : uint8_t {
    kUsageImmResource = 0x00, kUsageImmSampler = 0x01, kUsageImmConstBuffer = 0x02, kUsageImmVertexBuffer = 0x03,
    kUsageSubPtrFetchShader = 0x12, kUsagePtrResourceTable = 0x13, kUsagePtrSamplerTable = 0x15,
    kUsagePtrConstBufferTable = 0x16, kUsagePtrVertexBufferTable = 0x17, kUsagePtrExtendedUserData = 0x1B,
};

enum class TexDim : uint8_t { Tex2D, Tex2DArray, Tex3D, Cube };

struct ShaderDesc {
    Stage stage = Stage::Pixel;
    const uint8_t* code = nullptr;
    uint32_t code_size = 0;
    std::vector<UsageSlot> slots;
    uint32_t user_sgprs = 0;
    uint32_t ps_input_addr = 0;     // pixel: SPI_PS_INPUT_ADDR (VGPR layout of the inputs)
    const uint8_t* fetch = nullptr;  // vertex: fetch shader
    uint32_t fetch_size = 0;
    TexDim tex_dims[16] = {};        // per texture API slot (from the bound T#s)
};

struct Binding {
    enum Kind : uint8_t { Texture, Sampler, ConstBuffer } kind;
    uint8_t api_slot;
    uint32_t binding;
};

// One vertex attribute read by the fetch shader: becomes a Vulkan vertex input.
struct VertexAttrib {
    uint32_t location;
    uint32_t vb_slot;      // vertex buffer index in the vertex buffer table
    uint32_t offset;       // byte offset inside the element
    uint8_t dfmt, nfmt;    // buffer data / number format (MTBUF); 0xFF: from the V# at draw time
    uint8_t components;    // VGPRs written
    uint8_t vgpr;          // first destination VGPR
};

struct Result {
    std::vector<uint32_t> spirv;
    std::vector<Binding> bindings;
    std::vector<VertexAttrib> attribs;  // vertex
    uint32_t param_exports = 0;         // vertex: mask of parameter outputs (locations)
    uint32_t ps_inputs = 0;             // pixel: mask of interpolated attributes read
    uint32_t ps_flat_inputs = 0;        // pixel: attributes read flat (v_interp_mov)
    uint32_t color_outputs = 0;         // pixel: MRT mask
    bool writes_depth = false, discards = false, uses_branches = false;
    std::vector<std::string> problems;  // anything not translated exactly
};

Result translate(const ShaderDesc& d);

}  // namespace d1::gcn
