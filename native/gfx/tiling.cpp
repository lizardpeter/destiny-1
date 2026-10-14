// GCN surface tiling. See tiling.h.
#include "tiling.h"

#include <algorithm>
#include <bit>
#include <cstring>

namespace d1::tiling {
namespace {

enum Array : uint32_t {
    LinearGeneral = 0, LinearAligned = 1, Tiled1DThin1 = 2, Tiled1DThick = 3, Tiled2DThin1 = 4, PrtThin1 = 5,
    Prt2DThin1 = 6, Tiled2DThick = 7, Tiled2DXThick = 8, PrtThick = 9, Prt2DThick = 10, Prt3DThin1 = 11,
    Tiled3DThin1 = 12, Tiled3DThick = 13, Tiled3DXThick = 14, Prt3DThick = 15,
};
enum Micro : uint32_t { Display = 0, Thin = 1, Depth = 2, Rotated = 3, Thick = 4 };
enum Pipes : uint32_t { P2, P8_32x32_8x16, P8_32x32_16x16 };

// GB_TILE_MODE table of the PS4 (index -> array mode, micro mode, pipe config, sample split,
// depth tile split bytes)
struct ModeInfo {
    Array array;
    Micro micro;
    Pipes pipes;
    uint8_t sample_split;
    uint16_t tile_split_hw;
    const char* name;
};
constexpr ModeInfo kModes[32] = {
    {Tiled2DThin1, Depth, P8_32x32_16x16, 1, 64, "Depth2DThin64"},
    {Tiled2DThin1, Depth, P8_32x32_16x16, 1, 128, "Depth2DThin128"},
    {Tiled2DThin1, Depth, P8_32x32_16x16, 1, 256, "Depth2DThin256"},
    {Tiled2DThin1, Depth, P8_32x32_16x16, 1, 512, "Depth2DThin512"},
    {Tiled2DThin1, Depth, P8_32x32_16x16, 1, 1024, "Depth2DThin1K"},
    {Tiled1DThin1, Depth, P8_32x32_16x16, 1, 64, "Depth1DThin"},
    {Prt2DThin1, Depth, P8_32x32_16x16, 1, 256, "Depth2DThinPrt256"},
    {Prt2DThin1, Depth, P8_32x32_16x16, 1, 1024, "Depth2DThinPrt1K"},
    {LinearAligned, Display, P8_32x32_16x16, 1, 64, "DisplayLinearAligned"},
    {Tiled1DThin1, Display, P8_32x32_16x16, 1, 64, "Display1DThin"},
    {Tiled2DThin1, Display, P8_32x32_16x16, 2, 64, "Display2DThin"},
    {PrtThin1, Display, P8_32x32_8x16, 2, 64, "DisplayThinPrt"},
    {Prt2DThin1, Display, P8_32x32_16x16, 2, 64, "Display2DThinPrt"},
    {Tiled1DThin1, Thin, P8_32x32_16x16, 1, 64, "Thin1DThin"},
    {Tiled2DThin1, Thin, P8_32x32_16x16, 2, 64, "Thin2DThin"},
    {Tiled3DThin1, Thin, P8_32x32_8x16, 2, 64, "Thin3DThin"},
    {PrtThin1, Thin, P8_32x32_8x16, 2, 64, "ThinThinPrt"},
    {Prt2DThin1, Thin, P8_32x32_16x16, 2, 64, "Thin2DThinPrt"},
    {Prt3DThin1, Thin, P8_32x32_16x16, 2, 64, "Thin3DThinPrt"},
    {Tiled1DThick, Thick, P8_32x32_16x16, 1, 64, "Thick1DThick"},
    {Tiled2DThick, Thick, P8_32x32_16x16, 1, 64, "Thick2DThick"},
    {Tiled3DThick, Thick, P8_32x32_8x16, 1, 64, "Thick3DThick"},
    {PrtThick, Thick, P8_32x32_8x16, 1, 64, "ThickThickPrt"},
    {Prt2DThick, Thick, P8_32x32_16x16, 1, 64, "Thick2DThickPrt"},
    {Prt3DThick, Thick, P8_32x32_8x16, 1, 64, "Thick3DThickPrt"},
    {Tiled2DXThick, Thick, P8_32x32_16x16, 1, 64, "Thick2DXThick"},
    {Tiled3DXThick, Thick, P8_32x32_8x16, 1, 64, "Thick3DXThick"},
    {LinearGeneral, Display, P2, 1, 64, "?"}, {LinearGeneral, Display, P2, 1, 64, "?"},
    {LinearGeneral, Display, P2, 1, 64, "?"}, {LinearGeneral, Display, P2, 1, 64, "?"},
    {LinearGeneral, Display, P2, 1, 64, "DisplayLinearGeneral"},
};

uint32_t thickness(Array a) {
    switch (a) {
    case Tiled1DThick: case Tiled2DThick: case Tiled3DThick: case PrtThick: case Prt2DThick: case Prt3DThick: return 4;
    case Tiled2DXThick: case Tiled3DXThick: return 8;
    default: return 1;
    }
}
bool macro_tiled(Array a) { return a >= Tiled2DThin1; }
bool prt(Array a) { return a == PrtThin1 || a == Prt2DThin1 || a == PrtThick || a == Prt2DThick || a == Prt3DThin1 || a == Prt3DThick; }
uint32_t num_pipes(Pipes p) { return p == P2 ? 2 : 8; }

// macro tile mode parameters (bank height, number of banks, macro tile aspect); bank width is 1
struct MacroMode { uint32_t bank_h, banks, aspect; };
MacroMode macro_mode(uint32_t idx) {
    static const MacroMode m[16] = {
        {4, 16, 4}, {2, 16, 2}, {1, 16, 2}, {1, 16, 2}, {1, 8, 1}, {1, 4, 1}, {1, 2, 1}, {1, 2, 1},  // 1x4_16 .. 1x1_2_Dup
        {8, 16, 4}, {4, 16, 4}, {2, 16, 2}, {1, 16, 2}, {1, 8, 1}, {1, 4, 1}, {1, 2, 1}, {1, 2, 1},  // PRT variants
    };
    return m[idx & 15];
}

struct Macro {
    uint32_t pipes, banks, bank_w, bank_h, aspect, tile_split, width, height;
};
Macro macro_params(uint32_t tile_mode, uint32_t bpp, uint32_t samples) {
    const ModeInfo& mi = kModes[tile_mode & 31];
    const uint32_t thick = thickness(mi.array);
    const uint32_t tile_bytes_1x = bpp * 64 * thick / 8;
    uint32_t split = mi.micro == Depth ? mi.tile_split_hw : std::max(256u, mi.sample_split * tile_bytes_1x);
    split = std::min(1024u, split);
    const uint32_t tile_bytes = std::min(split, samples * tile_bytes_1x);
    uint32_t idx = uint32_t(std::bit_width(std::max(1u, tile_bytes / 64))) - 1;
    if (prt(mi.array)) idx += 8;
    const MacroMode mm = macro_mode(idx);
    Macro m{};
    m.pipes = num_pipes(mi.pipes);
    m.banks = mm.banks;
    m.bank_w = 1;
    m.bank_h = mm.bank_h;
    m.aspect = mm.aspect;
    m.tile_split = split;
    m.width = 8 * m.bank_w * m.pipes * m.aspect;
    m.height = 8 * m.bank_h * m.banks / m.aspect;
    return m;
}

uint32_t bit(uint32_t v, uint32_t b) { return (v >> b) & 1; }

uint32_t pixel_index(Micro mode, uint32_t bpp, uint32_t x, uint32_t y, uint32_t z, uint32_t thick) {
    const uint32_t x0 = bit(x, 0), x1 = bit(x, 1), x2 = bit(x, 2), y0 = bit(y, 0), y1 = bit(y, 1), y2 = bit(y, 2);
    const uint32_t z0 = bit(z, 0), z1 = bit(z, 1), z2 = bit(z, 2);
    uint32_t p[9] = {};
    if (mode == Display) {
        switch (bpp) {
        case 8: p[0] = x0, p[1] = x1, p[2] = x2, p[3] = y1, p[4] = y0, p[5] = y2; break;
        case 16: p[0] = x0, p[1] = x1, p[2] = x2, p[3] = y0, p[4] = y1, p[5] = y2; break;
        case 32: p[0] = x0, p[1] = x1, p[2] = y0, p[3] = x2, p[4] = y1, p[5] = y2; break;
        case 64: p[0] = x0, p[1] = y0, p[2] = x1, p[3] = x2, p[4] = y1, p[5] = y2; break;
        default: p[0] = x0, p[1] = y0, p[2] = x1, p[3] = y1, p[4] = x2, p[5] = y2; break;
        }
    } else if (mode == Thin || mode == Depth) {
        p[0] = x0, p[1] = y0, p[2] = x1, p[3] = y1, p[4] = x2, p[5] = y2;
    } else {  // thick
        if (bpp <= 16) p[0] = x0, p[1] = y0, p[2] = x1, p[3] = y1, p[4] = z0, p[5] = z1;
        else if (bpp == 32) p[0] = x0, p[1] = y0, p[2] = x1, p[3] = z0, p[4] = y1, p[5] = z1;
        else p[0] = x0, p[1] = y0, p[2] = z0, p[3] = x1, p[4] = y1, p[5] = z1;
        p[6] = x2, p[7] = y2;
        if (thick == 8) p[8] = z2;
    }
    uint32_t r = 0;
    for (uint32_t i = 0; i < 9; ++i) r |= p[i] << i;
    return r;
}

uint64_t addr_micro(Micro mode, uint32_t bpp, uint32_t samples, uint32_t x, uint32_t y, uint32_t z, uint32_t pitch,
                    uint32_t height, uint32_t thick) {
    const uint64_t micro_bytes = 64ull * thick * bpp * samples / 8;
    const uint64_t slice_bytes = (uint64_t(pitch) * height * thick * bpp * samples + 7) / 8;
    const uint64_t tile = uint64_t(y / 8) * (pitch / 8) + x / 8;
    const uint32_t pix = pixel_index(mode, bpp, x, y, z, thick);
    return (z / thick) * slice_bytes + tile * micro_bytes + uint64_t(pix) * bpp / 8;
}

uint64_t addr_macro(const ModeInfo& mi, const Macro& m, uint32_t bpp, uint32_t samples, uint32_t x, uint32_t y,
                    uint32_t z, uint32_t pitch, uint32_t height) {
    const uint32_t thick = thickness(mi.array);
    const uint32_t pix = pixel_index(mi.micro, bpp, x, y, z, thick);
    uint64_t elem = uint64_t(pix) * bpp / 8;  // sample 0
    uint64_t micro_bytes = 64ull * thick * bpp * samples / 8;
    uint32_t slices_per_tile = 1, split_slice = 0;
    if (micro_bytes > m.tile_split && thick == 1) {
        slices_per_tile = uint32_t(micro_bytes / m.tile_split);
        split_slice = uint32_t(elem / m.tile_split);
        elem %= m.tile_split;
        micro_bytes = m.tile_split;
    }
    const uint64_t macro_bytes = micro_bytes * (m.width / 8) * (m.height / 8) / (m.pipes * m.banks);
    const uint32_t per_row = pitch / m.width;
    const uint64_t macro_off = (uint64_t(y / m.height) * per_row + x / m.width) * macro_bytes;
    const uint64_t slice_bytes = uint64_t(per_row) * (height / m.height) * macro_bytes;
    const uint64_t slice_off = slice_bytes * (split_slice + uint64_t(slices_per_tile) * (z / thick));
    const uint32_t tile_row = (y / 8) % m.bank_h, tile_col = ((x / 8) / m.pipes) % m.bank_w;
    const uint64_t tile_off = uint64_t(tile_row * m.bank_w + tile_col) * micro_bytes;
    const uint64_t total = slice_off + macro_off + elem + tile_off;
    if (prt(mi.array)) x %= m.width, y %= m.height;
    // pipe
    const uint32_t tx = x / 8, ty = y / 8;
    uint32_t pipe;
    if (mi.pipes == P2) pipe = bit(tx, 0) ^ bit(ty, 0);
    else if (mi.pipes == P8_32x32_8x16)
        pipe = (bit(tx, 1) ^ bit(ty, 0) ^ bit(tx, 2)) | (bit(tx, 0) ^ bit(ty, 1)) << 1 | (bit(tx, 2) ^ bit(ty, 2)) << 2;
    else pipe = (bit(tx, 0) ^ bit(ty, 0) ^ bit(tx, 1)) | (bit(tx, 1) ^ bit(ty, 1)) << 1 | (bit(tx, 2) ^ bit(ty, 2)) << 2;
    const bool is3d = mi.array == Tiled3DThin1 || mi.array == Tiled3DThick || mi.array == Tiled3DXThick;
    if (is3d) pipe ^= (std::max(1u, m.pipes / 2 - 1) * (z / thick)) & (m.pipes - 1);
    // bank
    const uint32_t bx = x / 8 / (m.bank_w * m.pipes), by = y / 8 / m.bank_h;
    uint32_t bank = 0;
    switch (m.banks) {
    case 16:
        bank = (bit(bx, 0) ^ bit(by, 3)) | (bit(bx, 1) ^ bit(by, 2) ^ bit(by, 3)) << 1 | (bit(bx, 2) ^ bit(by, 1)) << 2 |
               (bit(bx, 3) ^ bit(by, 0)) << 3;
        break;
    case 8: bank = (bit(bx, 0) ^ bit(by, 2)) | (bit(bx, 1) ^ bit(by, 1) ^ bit(by, 2)) << 1 | (bit(bx, 2) ^ bit(by, 0)) << 2; break;
    case 4: bank = (bit(bx, 0) ^ bit(by, 1)) | (bit(bx, 1) ^ bit(by, 0)) << 1; break;
    default: bank = bit(bx, 0) ^ bit(by, 0); break;
    }
    uint32_t slice_rot = 0, split_rot = 0;
    if (mi.array == Tiled2DThin1 || mi.array == Tiled2DThick || mi.array == Tiled2DXThick)
        slice_rot = (m.banks / 2 - 1) * (z / thick);
    else if (is3d) slice_rot = std::max(1u, m.pipes / 2 - 1) * (z / thick) / m.pipes;
    if (mi.array == Tiled2DThin1 || mi.array == Tiled3DThin1 || mi.array == Prt2DThin1 || mi.array == Prt3DThin1)
        split_rot = (m.banks / 2 + 1) * split_slice;
    bank = ((bank ^ slice_rot) ^ split_rot) & (m.banks - 1);
    const uint32_t pipe_bits = uint32_t(std::bit_width(m.pipes)) - 1, bank_bits = uint32_t(std::bit_width(m.banks)) - 1;
    return (total & 0xFF) | uint64_t(pipe) << 8 | uint64_t(bank) << (8 + pipe_bits) | (total >> 8) << (8 + pipe_bits + bank_bits);
}

}  // namespace

const char* tile_mode_name(uint32_t tile_mode) { return kModes[tile_mode & 31].name; }

void layout(Surface& s) {
    const ModeInfo& mi = kModes[s.tile_mode & 31];
    const uint32_t thick = thickness(mi.array);
    const bool macro = macro_tiled(mi.array);
    s.total_size = 0;
    const Macro m = macro ? macro_params(s.tile_mode, s.bpp, s.samples) : Macro{};
    for (uint32_t lv = 0; lv < s.levels && lv < kMaxMips; ++lv) {
        uint32_t w = std::max(1u, (lv == 0 && s.pitch ? s.pitch : s.width) >> lv);
        if (lv > 0 && s.pitch) w = std::max(1u, s.width >> lv);
        uint32_t h = std::max(1u, s.height >> lv);
        if (s.block) w = (w + 3) / 4, h = (h + 3) / 4;
        w = std::max(w, 1u), h = std::max(h, 1u);
        uint32_t d = std::max(1u, s.depth >> lv);
        if (s.pow2) w = std::bit_ceil(w), h = std::bit_ceil(h), d = std::bit_ceil(d);
        MipLayout& ml = s.mips[lv];
        ml.thickness = 1;
        ml.micro = false;
        uint64_t size;
        if (mi.array == LinearAligned || mi.array == LinearGeneral) {
            const uint32_t bytes = std::max(1u, (s.bpp + 7) / 8);
            const uint32_t pitch_align = std::max(8u, 64u / bytes);
            uint32_t p = (w + pitch_align - 1) & ~(pitch_align - 1);
            const uint32_t slice_align = std::max(64u, 256u / bytes);
            while ((uint64_t(p) * h * s.samples) % slice_align) p += pitch_align;
            ml.pitch = p, ml.height = h;
            size = (uint64_t(p) * h * s.samples * s.bpp + 7) / 8;
        } else if (macro && (lv == 0 || (w >= m.width && h >= m.height))) {
            ml.thickness = thick;
            ml.pitch = (w + m.width - 1) / m.width * m.width;
            ml.height = (h + m.height - 1) / m.height * m.height;
            size = (uint64_t(ml.pitch) * ml.height * s.samples * s.bpp + 7) / 8;
        } else {
            ml.thickness = std::min(thick, 4u);
            ml.micro = macro;
            uint32_t p = (w + 7) & ~7u;
            const uint32_t hh = (h + 7) & ~7u;
            size = (uint64_t(p) * hh * s.bpp * s.samples + 7) / 8;
            while ((size * ml.thickness) % 256) {
                p += 8;
                size = (uint64_t(p) * hh * s.bpp * s.samples + 7) / 8;
            }
            ml.pitch = p, ml.height = hh;
        }
        uint32_t slices = d * s.layers;
        slices += (0u - slices) & (ml.thickness - 1);
        ml.size = size * slices;
        ml.offset = s.total_size;
        s.total_size += ml.size;
    }
}

void detile(const Surface& s, uint32_t lv, const uint8_t* tiled, uint8_t* linear) {
    const ModeInfo& mi = kModes[s.tile_mode & 31];
    const MipLayout& ml = s.mips[lv];
    const uint32_t bytes = s.bpp / 8;
    uint32_t w = std::max(1u, s.width >> lv), h = std::max(1u, s.height >> lv);
    if (s.block) w = (w + 3) / 4, h = (h + 3) / 4;
    const uint32_t slices = std::max(1u, s.depth >> lv) * s.layers;
    const uint8_t* base = tiled + ml.offset;
    if (mi.array == LinearAligned || mi.array == LinearGeneral) {
        for (uint32_t z = 0; z < slices; ++z)
            for (uint32_t y = 0; y < h; ++y)
                std::memcpy(linear + ((uint64_t(z) * h + y) * w) * bytes,
                            base + ((uint64_t(z) * ml.height + y) * ml.pitch) * bytes, uint64_t(w) * bytes);
        return;
    }
    const bool micro = ml.micro || !macro_tiled(mi.array);
    const Macro m = micro ? Macro{} : macro_params(s.tile_mode, s.bpp, s.samples);
    for (uint32_t z = 0; z < slices; ++z)
        for (uint32_t y = 0; y < h; ++y) {
            uint8_t* out = linear + ((uint64_t(z) * h + y) * w) * bytes;
            for (uint32_t x = 0; x < w; ++x) {
                const uint64_t a = micro ? addr_micro(mi.micro, s.bpp, s.samples, x, y, z, ml.pitch, ml.height, ml.thickness)
                                         : addr_macro(mi, m, s.bpp, s.samples, x, y, z, ml.pitch, ml.height);
                std::memcpy(out + uint64_t(x) * bytes, base + a, bytes);
            }
        }
}

}  // namespace d1::tiling
