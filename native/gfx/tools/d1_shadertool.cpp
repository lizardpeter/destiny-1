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
#include <cstring>
#include <map>
#include <string>
#include <vector>

#include "../gcn.h"
#include "../translate.h"
#include "../vk/vk.h"

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
