// GCN formats. See formats.h.
#include "formats.h"

namespace d1::fmt {

FormatInfo data_format(uint32_t d) {
    switch (d) {
    case 1: return {8, false, 1};
    case 2: return {16, false, 1};
    case 3: return {16, false, 2};
    case 4: return {32, false, 1};
    case 5: return {32, false, 2};
    case 6: case 7: return {32, false, 3};
    case 8: case 9: case 10: return {32, false, 4};
    case 11: return {64, false, 2};
    case 12: return {64, false, 4};
    case 13: return {96, false, 3};
    case 14: return {128, false, 4};
    case 16: return {16, false, 3};
    case 17: case 18: case 19: return {16, false, 4};
    case 20: case 21: return {32, false, 2};
    case 22: return {64, false, 2};
    case 35: return {64, true, 4};   // BC1
    case 36: return {128, true, 4};  // BC2
    case 37: return {128, true, 4};  // BC3
    case 38: return {64, true, 1};   // BC4
    case 39: return {128, true, 2};  // BC5
    case 40: return {128, true, 3};  // BC6H
    case 41: return {128, true, 4};  // BC7
    default: return {};
    }
}

VkFormat vk_format(uint32_t d, uint32_t n) {
    const bool unorm = n == 0, snorm = n == 1, uint = n == 4, sint = n == 5, flt = n == 7, srgb = n == 9;
    switch (d) {
    case 1:
        return unorm ? VK_FORMAT_R8_UNORM : snorm ? VK_FORMAT_R8_SNORM : uint ? VK_FORMAT_R8_UINT : sint ? VK_FORMAT_R8_SINT
             : srgb ? VK_FORMAT_R8_SRGB : VK_FORMAT_UNDEFINED;
    case 2:
        return unorm ? VK_FORMAT_R16_UNORM : snorm ? VK_FORMAT_R16_SNORM : uint ? VK_FORMAT_R16_UINT : sint ? VK_FORMAT_R16_SINT
             : flt ? VK_FORMAT_R16_SFLOAT : VK_FORMAT_UNDEFINED;
    case 3:
        return unorm ? VK_FORMAT_R8G8_UNORM : snorm ? VK_FORMAT_R8G8_SNORM : uint ? VK_FORMAT_R8G8_UINT : sint ? VK_FORMAT_R8G8_SINT
             : srgb ? VK_FORMAT_R8G8_SRGB : VK_FORMAT_UNDEFINED;
    case 4:
        return uint ? VK_FORMAT_R32_UINT : sint ? VK_FORMAT_R32_SINT : flt ? VK_FORMAT_R32_SFLOAT : VK_FORMAT_UNDEFINED;
    case 5:
        return unorm ? VK_FORMAT_R16G16_UNORM : snorm ? VK_FORMAT_R16G16_SNORM : uint ? VK_FORMAT_R16G16_UINT
             : sint ? VK_FORMAT_R16G16_SINT : flt ? VK_FORMAT_R16G16_SFLOAT : VK_FORMAT_UNDEFINED;
    case 6: case 7: return flt ? VK_FORMAT_B10G11R11_UFLOAT_PACK32 : VK_FORMAT_UNDEFINED;
    case 9: return unorm ? VK_FORMAT_A2B10G10R10_UNORM_PACK32 : uint ? VK_FORMAT_A2B10G10R10_UINT_PACK32 : VK_FORMAT_UNDEFINED;
    case 10:
        return unorm ? VK_FORMAT_R8G8B8A8_UNORM : snorm ? VK_FORMAT_R8G8B8A8_SNORM : uint ? VK_FORMAT_R8G8B8A8_UINT
             : sint ? VK_FORMAT_R8G8B8A8_SINT : srgb ? VK_FORMAT_R8G8B8A8_SRGB : VK_FORMAT_UNDEFINED;
    case 11:
        return uint ? VK_FORMAT_R32G32_UINT : sint ? VK_FORMAT_R32G32_SINT : flt ? VK_FORMAT_R32G32_SFLOAT : VK_FORMAT_UNDEFINED;
    case 12:
        return unorm ? VK_FORMAT_R16G16B16A16_UNORM : snorm ? VK_FORMAT_R16G16B16A16_SNORM : uint ? VK_FORMAT_R16G16B16A16_UINT
             : sint ? VK_FORMAT_R16G16B16A16_SINT : flt ? VK_FORMAT_R16G16B16A16_SFLOAT : VK_FORMAT_UNDEFINED;
    case 14:
        return uint ? VK_FORMAT_R32G32B32A32_UINT : sint ? VK_FORMAT_R32G32B32A32_SINT : flt ? VK_FORMAT_R32G32B32A32_SFLOAT
             : VK_FORMAT_UNDEFINED;
    case 16: return unorm ? VK_FORMAT_R5G6B5_UNORM_PACK16 : VK_FORMAT_UNDEFINED;
    case 17: return unorm ? VK_FORMAT_A1R5G5B5_UNORM_PACK16 : VK_FORMAT_UNDEFINED;
    case 18: return unorm ? VK_FORMAT_R5G5B5A1_UNORM_PACK16 : VK_FORMAT_UNDEFINED;
    case 19: return unorm ? VK_FORMAT_R4G4B4A4_UNORM_PACK16 : VK_FORMAT_UNDEFINED;
    case 35: return srgb ? VK_FORMAT_BC1_RGBA_SRGB_BLOCK : VK_FORMAT_BC1_RGBA_UNORM_BLOCK;
    case 36: return srgb ? VK_FORMAT_BC2_SRGB_BLOCK : VK_FORMAT_BC2_UNORM_BLOCK;
    case 37: return srgb ? VK_FORMAT_BC3_SRGB_BLOCK : VK_FORMAT_BC3_UNORM_BLOCK;
    case 38: return snorm ? VK_FORMAT_BC4_SNORM_BLOCK : VK_FORMAT_BC4_UNORM_BLOCK;
    case 39: return snorm ? VK_FORMAT_BC5_SNORM_BLOCK : VK_FORMAT_BC5_UNORM_BLOCK;
    case 40: return snorm ? VK_FORMAT_BC6H_SFLOAT_BLOCK : VK_FORMAT_BC6H_UFLOAT_BLOCK;
    case 41: return srgb ? VK_FORMAT_BC7_SRGB_BLOCK : VK_FORMAT_BC7_UNORM_BLOCK;
    default: return VK_FORMAT_UNDEFINED;
    }
}

uint32_t color_to_data_format(uint32_t c) {
    // COLOR_* numbering matches IMG_DATA_FORMAT_* for the formats render targets use
    return c;
}

TSharp decode_tsharp(const uint32_t t[8]) {
    TSharp s{};
    s.base = (uint64_t(t[0]) | uint64_t(t[1] & 0xFF) << 32) << 8;
    s.dfmt = (t[1] >> 20) & 0x3F;
    s.nfmt = (t[1] >> 26) & 0xF;
    s.min_lod = (t[1] >> 8) & 0xFFF;
    s.width = (t[2] & 0x3FFF) + 1;
    s.height = ((t[2] >> 14) & 0x3FFF) + 1;
    s.dst_sel = t[3] & 0xFFF;
    s.base_level = (t[3] >> 12) & 0xF;
    s.last_level = (t[3] >> 16) & 0xF;
    s.tiling = (t[3] >> 20) & 0x1F;
    s.pow2 = (t[3] >> 25) & 1;
    s.type = (t[3] >> 28) & 0xF;
    s.depth = (t[4] & 0x1FFF) + 1;
    s.pitch = ((t[4] >> 13) & 0x3FFF) + 1;
    s.base_array = t[5] & 0x1FFF;
    s.last_array = (t[5] >> 13) & 0x1FFF;
    return s;
}

}  // namespace d1::fmt
