// ELF-SCE (PS4) module loader: maps a decrypted eboot.bin / .prx at a chosen base.
#pragma once
#include <cstdint>
#include <map>
#include <string>
#include <vector>

namespace d1 {

struct Module {
    struct Sym {
        std::string name;  // "NID#L#M" for SCE symbols
        uint8_t info;
        uint16_t shndx;
        uint64_t value;
    };
    struct Rela {
        uint64_t offset;
        uint32_t type;
        uint32_t sym;
        int64_t addend;
    };

    std::string name;
    std::string path;
    uint16_t elf_type = 0;
    uint64_t base = 0, size = 0;
    uint64_t entry = 0;          // e_entry (exec) — absolute after load
    uint64_t init = 0, fini = 0; // DT_INIT / DT_FINI — absolute (module_start for prx)
    uint64_t proc_param = 0, proc_param_size = 0;
    uint64_t text_lo = 0, text_hi = 0;
    uint64_t eh_frame_hdr = 0;
    // TLS image
    int tls_modid = 0;
    uint64_t tls_init = 0, tls_filesz = 0, tls_memsz = 0, tls_align = 1;
    // SCE dynamic tables
    std::map<int, std::string> needed_modules, import_libs, export_libs;
    std::vector<Sym> syms;
    std::vector<Rela> relas;

    bool contains(uint64_t a) const { return a >= base && a < base + size; }
};

// Map the module at `base` (bytes copied, memory RWX). Throws std::runtime_error.
Module load_module(const std::string& path, uint64_t base);

// Decode the Base64-ish id in "NID#L#M".
int decode_sce_id(const std::string& s);

}  // namespace d1
