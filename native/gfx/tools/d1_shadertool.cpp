// d1-shadertool: development tool for d1-native's own shader translator.
//
//   d1-shadertool decode <file>...     decode GCN programs, report problems and statistics
//   d1-shadertool dis <file>           disassemble one program
//   d1-shadertool translate <obj>...    translate dumped shader objects (vs_*.obj / ps_*.obj with
//                                       their .code / .fetch next to them) to <obj>.spv and
//                                       report what was not translated exactly
//
// Input files are raw shader code (e.g. *.code / *.fetch written by
// D1_NATIVE_GFX=observe D1_NATIVE_GFX_DUMP=<dir>). Shader bytes are game data: keep dumps
// outside the repository.
#include <cstdio>
#include <algorithm>
#include <cstring>
#include <map>
#include <string>
#include <vector>

#include "../gcn.h"
#include "../translate.h"
#include "../vk/vk.h"
#include "../formats.h"
#include "../tiling.h"

using namespace d1::gcn;

static std::vector<uint8_t> read_file(const char* path) {
    std::vector<uint8_t> d;
    if (FILE* f = std::fopen(path, "rb")) {
        uint8_t b[65536];
        size_t n;
        while ((n = std::fread(b, 1, sizeof b, f)) > 0) d.insert(d.end(), b, b + n);
        std::fclose(f);
    }
    return d;
}

int main(int argc, char** argv) {
    if (argc < 3 && !(argc == 2 && std::string(argv[1]) == "vkinfo")) {
        std::fprintf(stderr, "usage: %s decode|dis <file>...\n", argv[0]);
        return 2;
    }
    const std::string cmd = argv[1];
    if (cmd == "dis") {
        auto d = read_file(argv[2]);
        Program p = decode(d.data(), uint32_t(d.size()));
        for (auto& in : p.insts) std::printf("%5x: %s\n", in.pc, disassemble(in).c_str());
        for (auto& e : p.problems) std::printf("PROBLEM: %s\n", e.c_str());
        return p.problems.empty() && p.ended ? 0 : 1;
    }
    if (cmd == "vkinfo") {  // create the native renderer's Vulkan 1.4 context
        d1::vk::Context ctx;
        char err[256] = {};
        if (!d1::vk::create_context(ctx, -1, nullptr, 0, err, sizeof err)) {
            std::printf("Vulkan: %s\n", err);
            return 1;
        }
        std::printf("Vulkan %u.%u.%u on %s (host image copy %s, external host memory %s)\n",
                    VK_API_VERSION_MAJOR(ctx.api_version), VK_API_VERSION_MINOR(ctx.api_version),
                    VK_API_VERSION_PATCH(ctx.api_version), ctx.name, ctx.host_image_copy ? "yes" : "no",
                    ctx.external_memory_host ? "yes" : "no");
        d1::vk::destroy_context(ctx);
        return 0;
    }
    if (cmd == "detile") {  // detile dumped textures (tex_*.tsharp + .mem) to <name>.ppm (mip 0, slice 0)
        for (int i = 2; i < argc; ++i) {
            const std::string tpath = argv[i], base = tpath.substr(0, tpath.size() - 7);
            auto tb = read_file(tpath.c_str());
            auto mem = read_file((base + ".mem").c_str());
            if (tb.size() < 32) continue;
            uint32_t t[8];
            std::memcpy(t, tb.data(), 32);
            const auto ts = d1::fmt::decode_tsharp(t);
            const auto fi = d1::fmt::data_format(ts.dfmt);
            d1::tiling::Surface s;
            s.tile_mode = ts.tiling, s.bpp = fi.bpp, s.block = fi.block, s.pow2 = ts.pow2;
            s.width = ts.width, s.height = ts.height, s.pitch = ts.pitch;
            s.depth = ts.type == 10 ? ts.depth : 1;
            s.layers = (ts.type == 13 || ts.type == 11) ? ts.last_array + 1 : 1;
            s.levels = ts.last_level + 1;
            if (fi.bpp == 0 || fi.bpp == 96) {
                std::printf("%s: format %u unsupported\n", tpath.c_str(), ts.dfmt);
                continue;
            }
            d1::tiling::layout(s);
            std::printf("%s: %ux%u pitch %u fmt %u/%u type %u tile %s levels %u layers %u: %llu bytes (dump %zu)\n",
                        tpath.c_str(), ts.width, ts.height, ts.pitch, ts.dfmt, ts.nfmt, ts.type,
                        d1::tiling::tile_mode_name(ts.tiling), s.levels, s.layers,
                        (unsigned long long)s.total_size, mem.size());
            if (mem.size() < s.mips[0].offset + s.mips[0].size) continue;
            const uint32_t bw = fi.block ? (ts.width + 3) / 4 : ts.width, bh = fi.block ? (ts.height + 3) / 4 : ts.height;
            std::vector<uint8_t> lin(size_t(bw) * bh * s.layers * std::max(1u, s.depth) * (fi.bpp / 8));
            d1::tiling::detile(s, 0, mem.data(), lin.data());
            // preview as RGB
            std::vector<uint8_t> rgb(size_t(ts.width) * ts.height * 3);
            auto put = [&](uint32_t x, uint32_t y, uint8_t r, uint8_t g, uint8_t b) {
                if (x < ts.width && y < ts.height) { auto* p = &rgb[(size_t(y) * ts.width + x) * 3]; p[0] = r, p[1] = g, p[2] = b; }
            };
            auto c565 = [](uint16_t c, uint8_t o[3]) { o[0] = uint8_t((c >> 11) * 255 / 31); o[1] = uint8_t(((c >> 5) & 63) * 255 / 63); o[2] = uint8_t((c & 31) * 255 / 31); };
            if (ts.dfmt == 10) {
                for (uint32_t y = 0; y < bh; ++y) for (uint32_t x = 0; x < bw; ++x) { const uint8_t* p = &lin[(size_t(y) * bw + x) * 4]; put(x, y, p[0], p[1], p[2]); }
            } else if (ts.dfmt == 1 || ts.dfmt == 3) {
                const uint32_t b = ts.dfmt == 1 ? 1 : 2;
                for (uint32_t y = 0; y < bh; ++y) for (uint32_t x = 0; x < bw; ++x) { const uint8_t* p = &lin[(size_t(y) * bw + x) * b]; put(x, y, p[0], b > 1 ? p[1] : p[0], p[0]); }
            } else if (ts.dfmt == 35 || ts.dfmt == 36 || ts.dfmt == 37) {
                const uint32_t bs = fi.bpp / 8, coff = ts.dfmt == 35 ? 0 : 8;
                for (uint32_t by = 0; by < bh; ++by) for (uint32_t bx = 0; bx < bw; ++bx) {
                    const uint8_t* blk = &lin[(size_t(by) * bw + bx) * bs] + coff;
                    uint16_t c0, c1; uint32_t idx; std::memcpy(&c0, blk, 2); std::memcpy(&c1, blk + 2, 2); std::memcpy(&idx, blk + 4, 4);
                    uint8_t c[4][3]; c565(c0, c[0]); c565(c1, c[1]);
                    for (int k = 0; k < 3; ++k) {
                        if (c0 > c1 || coff) { c[2][k] = uint8_t((2 * c[0][k] + c[1][k]) / 3); c[3][k] = uint8_t((c[0][k] + 2 * c[1][k]) / 3); }
                        else { c[2][k] = uint8_t((c[0][k] + c[1][k]) / 2); c[3][k] = 0; }
                    }
                    for (uint32_t py = 0; py < 4; ++py) for (uint32_t px = 0; px < 4; ++px) {
                        const uint32_t s2 = (idx >> (2 * (py * 4 + px))) & 3;
                        put(bx * 4 + px, by * 4 + py, c[s2][0], c[s2][1], c[s2][2]);
                    }
                }
            } else if (ts.dfmt == 38 || ts.dfmt == 39) {
                const uint32_t bs = fi.bpp / 8;
                for (uint32_t by = 0; by < bh; ++by) for (uint32_t bx = 0; bx < bw; ++bx) {
                    const uint8_t* blk = &lin[(size_t(by) * bw + bx) * bs];
                    uint8_t a0 = blk[0], a1 = blk[1]; uint64_t bits = 0; std::memcpy(&bits, blk + 2, 6);
                    uint8_t pal[8] = {a0, a1};
                    for (int k = 2; k < 8; ++k) pal[k] = a0 > a1 ? uint8_t(((8 - k) * a0 + (k - 1) * a1) / 7) : (k < 6 ? uint8_t(((6 - k) * a0 + (k - 1) * a1) / 5) : (k == 6 ? 0 : 255));
                    for (uint32_t pz = 0; pz < 16; ++pz) { const uint8_t v = pal[(bits >> (3 * pz)) & 7]; put(bx * 4 + pz % 4, by * 4 + pz / 4, v, v, v); }
                }
            } else {
                std::printf("  (no preview for format %u)\n", ts.dfmt);
                continue;
            }
            if (FILE* f = std::fopen((base + ".ppm").c_str(), "wb")) {
                std::fprintf(f, "P6 %u %u 255\n", ts.width, ts.height);
                std::fwrite(rgb.data(), 1, rgb.size(), f);
                std::fclose(f);
            }
        }
        return 0;
    }
    if (cmd == "translate") {
        size_t ok = 0, total = 0;
        std::map<std::string, size_t> problems;
        for (int i = 2; i < argc; ++i) {
            const std::string obj_path = argv[i];
            const std::string base = obj_path.substr(0, obj_path.size() - 4);
            const bool vs = obj_path.find("vs_") != std::string::npos;
            auto obj = read_file(obj_path.c_str());
            auto code = read_file((base + ".code").c_str());
            auto fetch = read_file((base + ".fetch").c_str());
            if (obj.size() < 0x80 || code.empty()) continue;
            ++total;
            d1::gcn::ShaderDesc d;
            d.stage = vs ? d1::gcn::Stage::Vertex : d1::gcn::Stage::Pixel;
            const size_t g = vs ? 0x14 : 0;  // Gnm shader inside the object
            auto u32 = [&](size_t off) { uint32_t v; std::memcpy(&v, obj.data() + off, 4); return v; };
            const uint32_t common = u32(g), nslots = common >> 24;
            const size_t regs = vs ? 0x1C : 0x30;
            d.user_sgprs = (u32(g + 8 + 12) >> 1) & 0x1F;
            if (!vs) d.ps_input_addr = u32(g + 8 + 0x1C);
            for (uint32_t k = 0; k < nslots; ++k) {
                const uint8_t* b = obj.data() + g + 8 + regs + 4 + 4 * k;
                d.slots.push_back({b[0], b[1], b[2], b[3]});
            }
            d.code = code.data(), d.code_size = uint32_t(code.size());
            if (!fetch.empty()) d.fetch = fetch.data(), d.fetch_size = uint32_t(fetch.size());
            auto r = d1::gcn::translate(d);
            if (FILE* f = std::fopen((base + ".spv").c_str(), "wb")) {
                std::fwrite(r.spirv.data(), 4, r.spirv.size(), f);
                std::fclose(f);
            }
            if (r.problems.empty()) ++ok;
            for (auto& p : r.problems) ++problems[p];
        }
        std::printf("%zu shaders, %zu translated without remarks\n", total, ok);
        for (auto& [p, c] : problems) std::printf("%6zu  %s\n", c, p.c_str());
        return 0;
    }
    std::map<std::string, size_t> ops;
    size_t files = 0, clean = 0, insts = 0;
    for (int i = 2; i < argc; ++i) {
        auto d = read_file(argv[i]);
        Program p = decode(d.data(), uint32_t(d.size()));
        ++files;
        insts += p.insts.size();
        for (auto& in : p.insts) ++ops[op_name(in.op)];
        if (p.problems.empty() && p.ended) ++clean;
        else {
            std::printf("%s:", argv[i]);
            for (auto& e : p.problems) std::printf(" [%s]", e.c_str());
            if (!p.ended) std::printf(" [no end]");
            std::printf("\n");
        }
    }
    std::printf("%zu programs, %zu clean, %zu instructions, %zu distinct opcodes\n", files, clean, insts, ops.size());
    return clean == files ? 0 : 1;
}
