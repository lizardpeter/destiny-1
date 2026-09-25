#include <windows.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <vector>
#include <string>

using LzhInitFn = int (__fastcall *)(void *decoder, const uint8_t *src, const uint8_t *end, int *consumed);

static std::vector<uint8_t> read_file(const char *path) {
    std::ifstream f(path, std::ios::binary);
    if (!f) return {};
    return std::vector<uint8_t>((std::istreambuf_iterator<char>(f)), {});
}

int main(int argc, char **argv) {
    if (argc != 4) {
        std::fprintf(stderr, "usage: %s oo2core_3_win64.dll block.comp offset\n", argv[0]);
        return 2;
    }
    auto comp = read_file(argv[2]);
    if (comp.empty()) return 3;
    long offset = std::strtol(argv[3], nullptr, 0);
    if (offset < 0 || (size_t)offset >= comp.size()) return 4;

    HMODULE mod = LoadLibraryA(argv[1]);
    if (!mod) {
        std::fprintf(stderr, "LoadLibrary failed: %lu\n", GetLastError());
        return 5;
    }
    auto base = reinterpret_cast<uint8_t*>(mod);
    auto fn = reinterpret_cast<LzhInitFn>(base + 0x5D5E0);

    // Function keeps its Huffman object/work arrays inside caller-owned storage.
    std::vector<uint8_t> decoder(1 << 20);
    int consumed = -1;
    int ok = 0;
    __try {
        ok = fn(decoder.data(), comp.data() + offset, comp.data() + comp.size(), &consumed);
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        std::printf("OFFSET=%ld EXCEPTION=0x%08lx\n", offset, GetExceptionCode());
        FreeLibrary(mod);
        return 10;
    }

    std::printf("OFFSET=%ld OK=%d CONSUMED=%d\n", offset, ok, consumed);
    if (!ok) {
        FreeLibrary(mod);
        return 11;
    }

    auto h = *reinterpret_cast<uint8_t**>(decoder.data() + 0x60);
    if (!h || h < decoder.data() || h >= decoder.data() + decoder.size()) {
        std::printf("HUFFPTR=%p OUTSIDE_DECODER base=%p\n", h, decoder.data());
        FreeLibrary(mod);
        return 12;
    }

    const int numSymbols = *reinterpret_cast<int*>(h + 0x284);
    const int gotNumSymbols = *reinterpret_cast<int*>(h + 0x288);
    const int oneChar = *reinterpret_cast<int*>(h + 0x290);
    const int maxSymbol = *reinterpret_cast<int*>(h + 0x294);
    const int minCodeLen = *reinterpret_cast<int*>(h + 0x298);
    const int maxCodeLen = *reinterpret_cast<int*>(h + 0x29C);
    auto lens = *reinterpret_cast<uint8_t**>(h + 0x2A0);

    std::printf(
        "HUFF num=%d got=%d one=%d maxsym=%d minlen=%d maxlen=%d huff_off=%lld lens_off=%lld\n",
        numSymbols, gotNumSymbols, oneChar, maxSymbol, minCodeLen, maxCodeLen,
        (long long)(h - decoder.data()),
        lens ? (long long)(lens - decoder.data()) : -1LL
    );

    if (numSymbols > 0 && numSymbols <= 4096 && lens) {
        std::printf("LENS=");
        for (int i=0; i<numSymbols; ++i) {
            if (i) std::putchar(',');
            std::printf("%u", (unsigned)lens[i]);
        }
        std::putchar('\n');
    }

    FreeLibrary(mod);
    return 0;
}
