// Checks tiling::detile's fast paths against the element-by-element reference: every tile
// mode, element size, a range of sizes (odd, non-multiple-of-tile), layers and mip levels.
#include <cstdio>
#include <cstring>
#include <random>
#include <vector>

#include "../tiling.h"

using namespace d1;

int main() {
    std::mt19937 rng(1);
    int checked = 0, failed = 0;
    const uint32_t sizes[][2] = {{1, 1}, {7, 5}, {8, 8}, {33, 17}, {64, 64}, {100, 60}, {256, 128}, {300, 300}, {1024, 16}};
    for (uint32_t mode = 0; mode < 32; ++mode)  // (linear modes are a plain copy in both)
        if (mode != 8 && mode < 27)
        for (uint32_t bpp : {8u, 16u, 32u, 64u, 128u})
            for (const auto& wh : sizes)
                for (uint32_t layers : {1u, 3u})
                    for (bool block : {false, true}) {
                        if (block && bpp < 64) continue;
                        tiling::Surface s;
                        s.tile_mode = mode, s.bpp = bpp, s.width = wh[0], s.height = wh[1], s.layers = layers;
                        s.block = block, s.levels = 4;
                        tiling::layout(s);
                        if (!s.total_size || s.total_size > (256u << 20)) continue;
                        std::vector<uint8_t> src(s.total_size + 4096);
                        for (auto& b : src) b = uint8_t(rng());
                        for (uint32_t lv = 0; lv < s.levels; ++lv) {
                            uint32_t w = std::max(1u, s.width >> lv), h = std::max(1u, s.height >> lv);
                            if (block) w = (w + 3) / 4, h = (h + 3) / 4;
                            const size_t n = size_t(w) * h * layers * (bpp / 8);
                            std::vector<uint8_t> a(n), b(n);
                            tiling::detile(s, lv, src.data(), a.data());
                            tiling::detile_reference(s, lv, src.data(), b.data());
                            ++checked;
                            if (a != b) {
                                if (failed++ < 20)
                                    std::printf("MISMATCH mode %u bpp %u %ux%u layers %u block %d level %u\n", mode, bpp, wh[0], wh[1],
                                                layers, int(block), lv);
                            }
                        }
                    }
    std::printf("%d checked, %d failed\n", checked, failed);
    return failed ? 1 : 0;
}
