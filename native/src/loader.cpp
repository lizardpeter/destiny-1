#include "loader.h"

#include <sys/mman.h>

#include <cstring>
#include <fstream>
#include <stdexcept>

namespace d1 {

namespace {
constexpr uint32_t PT_LOAD = 1, PT_DYNAMIC = 2, PT_TLS = 7;
constexpr uint32_t PT_SCE_DYNLIBDATA = 0x61000000, PT_SCE_PROCPARAM = 0x61000001;
constexpr uint32_t PT_GNU_EH_FRAME = 0x6474E550;
constexpr int64_t DT_INIT = 0x0C, DT_FINI = 0x0D;
constexpr int64_t DT_SCE_NEEDED_MODULE = 0x6100000F, DT_SCE_IMPORT_LIB = 0x61000015,
                  DT_SCE_EXPORT_LIB = 0x61000013, DT_SCE_JMPREL = 0x61000029,
                  DT_SCE_PLTRELSZ = 0x6100002D, DT_SCE_RELA = 0x6100002F,
                  DT_SCE_RELASZ = 0x61000031, DT_SCE_STRTAB = 0x61000035,
                  DT_SCE_SYMTAB = 0x61000039, DT_SCE_SYMTABSZ = 0x6100003F;

template <class T>
T rd(const std::vector<uint8_t>& b, size_t o) {
    if (o + sizeof(T) > b.size()) throw std::runtime_error("read out of bounds");
    T v;
    std::memcpy(&v, b.data() + o, sizeof(T));
    return v;
}

std::string cstr(const std::vector<uint8_t>& b, size_t o) {
    std::string s;
    while (o < b.size() && b[o]) s.push_back(char(b[o++]));
    return s;
}
}  // namespace

int decode_sce_id(const std::string& s) {
    static const std::string A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-";
    int v = 0;
    for (char c : s) v = v * 64 + int(A.find(c));
    return v;
}

Module load_module(const std::string& path, uint64_t base) {
    std::ifstream f(path, std::ios::binary);
    if (!f) throw std::runtime_error("cannot open " + path);
    std::vector<uint8_t> d((std::istreambuf_iterator<char>(f)), {});
    if (d.size() < 64 || std::memcmp(d.data(), "\x7f" "ELF", 4) != 0)
        throw std::runtime_error(path + ": not a decrypted ELF");

    Module m;
    m.path = path;
    m.name = path.substr(path.find_last_of('/') + 1);
    m.elf_type = rd<uint16_t>(d, 0x10);
    m.base = base;
    const uint64_t e_entry = rd<uint64_t>(d, 0x18);
    const uint64_t phoff = rd<uint64_t>(d, 0x20);
    const uint16_t phnum = rd<uint16_t>(d, 0x38);

    struct Ph { uint32_t type, flags; uint64_t off, va, fs, ms, align; };
    std::vector<Ph> ph;
    for (int i = 0; i < phnum; ++i) {
        size_t o = phoff + size_t(i) * 56;
        ph.push_back({rd<uint32_t>(d, o), rd<uint32_t>(d, o + 4), rd<uint64_t>(d, o + 8),
                      rd<uint64_t>(d, o + 16), rd<uint64_t>(d, o + 32), rd<uint64_t>(d, o + 40),
                      rd<uint64_t>(d, o + 48)});
    }
    uint64_t top = 0;
    for (auto& p : ph)
        if (p.type == PT_LOAD) top = std::max(top, p.va + p.ms);
    m.size = (top + 0xFFFF) & ~uint64_t(0xFFFF);

    void* want = reinterpret_cast<void*>(base);
    void* got = mmap(want, m.size, PROT_READ | PROT_WRITE | PROT_EXEC,
                     MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED_NOREPLACE, -1, 0);
    if (got != want) throw std::runtime_error(m.name + ": cannot map at requested base");

    size_t dyn_off = 0, dyn_size = 0, dlib = 0;
    bool text_set = false;
    for (auto& p : ph) {
        if (p.type == PT_LOAD) {
            std::memcpy(reinterpret_cast<void*>(base + p.va), d.data() + p.off, p.fs);
            if ((p.flags & 1) && !text_set) {
                m.text_lo = base + p.va;
                m.text_hi = base + p.va + p.ms;
                text_set = true;
            }
        } else if (p.type == PT_DYNAMIC) {
            dyn_off = p.off; dyn_size = p.fs;
        } else if (p.type == PT_SCE_DYNLIBDATA) {
            dlib = p.off;
        } else if (p.type == PT_TLS) {
            m.tls_init = base + p.va; m.tls_filesz = p.fs; m.tls_memsz = p.ms;
            m.tls_align = p.align ? p.align : 1;
        } else if (p.type == PT_SCE_PROCPARAM) {
            m.proc_param = base + p.va; m.proc_param_size = p.fs;
        } else if (p.type == PT_GNU_EH_FRAME) {
            m.eh_frame_hdr = base + p.va;
        }
    }
    if (!dyn_size || !dlib) throw std::runtime_error(m.name + ": missing dynamic data");

    std::multimap<int64_t, uint64_t> tags;
    for (size_t o = dyn_off; o + 16 <= dyn_off + dyn_size; o += 16) {
        int64_t tag = rd<int64_t>(d, o);
        if (tag == 0) break;
        tags.emplace(tag, rd<uint64_t>(d, o + 8));
    }
    auto tag1 = [&](int64_t t) -> uint64_t {
        auto it = tags.find(t);
        return it == tags.end() ? 0 : it->second;
    };
    const size_t strtab = dlib + tag1(DT_SCE_STRTAB);
    auto s = [&](uint64_t off) { return cstr(d, strtab + off); };
    for (auto [it, end] = tags.equal_range(DT_SCE_NEEDED_MODULE); it != end; ++it)
        m.needed_modules[int(it->second >> 48)] = s(it->second & 0xFFFFFFFF);
    for (auto [it, end] = tags.equal_range(DT_SCE_IMPORT_LIB); it != end; ++it)
        m.import_libs[int(it->second >> 48)] = s(it->second & 0xFFFFFFFF);
    for (auto [it, end] = tags.equal_range(DT_SCE_EXPORT_LIB); it != end; ++it)
        m.export_libs[int(it->second >> 48)] = s(it->second & 0xFFFFFFFF);

    const size_t symtab = dlib + tag1(DT_SCE_SYMTAB);
    for (uint64_t o = 0; o + 24 <= tag1(DT_SCE_SYMTABSZ); o += 24) {
        Module::Sym sym;
        sym.name = s(rd<uint32_t>(d, symtab + o));
        sym.info = d[symtab + o + 4];
        sym.shndx = rd<uint16_t>(d, symtab + o + 6);
        sym.value = rd<uint64_t>(d, symtab + o + 8);
        m.syms.push_back(std::move(sym));
    }
    auto relocs = [&](int64_t at, int64_t sz) {
        const size_t start = dlib + tag1(at);
        for (uint64_t o = 0; o + 24 <= tag1(sz); o += 24) {
            uint64_t info = rd<uint64_t>(d, start + o + 8);
            m.relas.push_back({rd<uint64_t>(d, start + o), uint32_t(info), uint32_t(info >> 32),
                               rd<int64_t>(d, start + o + 16)});
        }
    };
    relocs(DT_SCE_RELA, DT_SCE_RELASZ);
    relocs(DT_SCE_JMPREL, DT_SCE_PLTRELSZ);

    m.entry = e_entry ? base + e_entry : 0;
    if (tags.count(DT_INIT)) m.init = base + tag1(DT_INIT);
    if (tags.count(DT_FINI)) m.fini = base + tag1(DT_FINI);
    return m;
}

}  // namespace d1
