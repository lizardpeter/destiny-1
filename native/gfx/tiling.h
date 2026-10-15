// GCN (PS4 "Liverpool") surface tiling: layouts and detiling, d1-native's own implementation
// of AMD's published Southern/Sea Islands addressing (micro tiles of 8x8 elements, macro tiles
// interleaved across 8 pipes and up to 16 banks).
#pragma once
#include <cstdint>
#include <vector>

namespace d1::tiling {

constexpr uint32_t kMaxMips = 16;

struct MipLayout {
    uint32_t pitch = 0, height = 0;  // in elements (texels, or 4x4 blocks for BCn)
    uint64_t offset = 0, size = 0;   // bytes; size covers every slice of this mip
    bool micro = false;              // stored micro-tiled (small mips of a macro-tiled surface)
    uint32_t thickness = 1;
};

struct Surface {
    uint32_t tile_mode = 0;      // GB_TILE_MODE index (T# TILING_INDEX / CB ATTRIB TILE_MODE_INDEX)
    uint32_t bpp = 32;           // bits per element (texel or block)
    uint32_t width = 1, height = 1, depth = 1;  // texels
    uint32_t layers = 1, levels = 1, samples = 1;
    bool block = false;          // 4x4 block compressed
    bool pow2 = false;           // T# POW2_PAD: mips padded to powers of two
    uint32_t pitch = 0;          // texels; 0 = from width
    // computed by layout()
    MipLayout mips[kMaxMips];
    uint64_t total_size = 0;
};

// Fills `mips` and `total_size` (the guest memory footprint).
void layout(Surface& s);

// Copies mip `level` (all slices) from tiled guest memory into a tightly packed buffer
// (rows of mip width elements, slices one after another). `tiled` points at the surface base.
void detile(const Surface& s, uint32_t level, const uint8_t* tiled, uint8_t* linear);

// The inverse: writes mip `level` from a tightly packed buffer into tiled guest memory.
void tile(const Surface& s, uint32_t level, const uint8_t* linear, uint8_t* tiled);

const char* tile_mode_name(uint32_t tile_mode);

}  // namespace d1::tiling
