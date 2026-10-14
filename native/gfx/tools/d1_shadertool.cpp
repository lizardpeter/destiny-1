// d1-shadertool: development tool for d1-native's own shader translator.
//
//   d1-shadertool decode <file>...     decode GCN programs, report problems and statistics
//   d1-shadertool dis <file>           disassemble one program
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
    if (argc < 3) {
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
