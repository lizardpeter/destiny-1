// GCN image / buffer formats (T# DATA_FORMAT / NUM_FORMAT, CB_COLOR_INFO) -> sizes and Vulkan
// formats.
#pragma once
#include <cstdint>

#include "vk/vk.h"

namespace d1::fmt {

struct FormatInfo {
    uint32_t bpp = 0;     // bits per element (texel, or 4x4 block)
    bool block = false;   // BCn
    uint8_t comps = 0;
};

// IMG_DATA_FORMAT_* (T# dword1 bits 20..25)
FormatInfo data_format(uint32_t dfmt);
// Vulkan format for a sampled image / render target; VK_FORMAT_UNDEFINED when unsupported.
// nfmt: IMG_NUM_FORMAT_* (0 UNORM, 1 SNORM, 2 USCALED, 3 SSCALED, 4 UINT, 5 SINT, 7 FLOAT, 9 SRGB)
VkFormat vk_format(uint32_t dfmt, uint32_t nfmt);
// CB_COLOR_INFO FORMAT (COLOR_*) / NUMBER_TYPE -> the same data-format numbering
uint32_t color_to_data_format(uint32_t color_format);

// T# fields
struct TSharp {
    uint64_t base;       // byte address
    uint32_t dfmt, nfmt;
    uint32_t width, height, depth;
    uint32_t pitch;      // texels
    uint32_t base_level, last_level, base_array, last_array;
    uint32_t tiling;     // tile mode index
    uint32_t type;       // 8 1D, 9 2D, 10 3D, 11 cube, 12 1D array, 13 2D array, 14/15 MSAA
    uint32_t dst_sel;    // 12 bits: x y z w swizzles (0 zero, 1 one, 4 r, 5 g, 6 b, 7 a)
    uint32_t min_lod;    // u4.8: sampling never uses finer mips (texture streaming: not loaded yet)
    bool pow2;
};
TSharp decode_tsharp(const uint32_t t[8]);

}  // namespace d1::fmt
