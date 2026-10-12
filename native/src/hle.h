// Registry for host implementations of PS4 firmware functions ("HLE").
//
// PS4 user code uses the System V AMD64 ABI, the same as Linux, so a firmware
// function is an ordinary host function with the matching signature. Register it
// by its PS4 symbol name; the linker computes the NID and resolves imports to it.
#pragma once
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

namespace d1 {

struct HleEntry {
    const char* name;
    void* addr;
    bool object;  // data symbol (address of a host object) rather than a function
};

std::vector<HleEntry>& hle_registry();

struct HleReg {
    HleReg(const char* n, void* a, bool obj = false) { hle_registry().push_back({n, a, obj}); }
};

#define D1_CAT2(a, b) a##b
#define D1_CAT(a, b) D1_CAT2(a, b)
#define HLE(name, fn) static ::d1::HleReg D1_CAT(_hle_, __LINE__){name, reinterpret_cast<void*>(&fn)};
#define HLE_OBJ(name, obj) static ::d1::HleReg D1_CAT(_hleo_, __LINE__){name, reinterpret_cast<void*>(&obj), true};

void log(const char* fmt, ...) __attribute__((format(printf, 1, 2)));

// PS4 kernel error codes (subset). Kernel functions return 0x8002xxxx = 0x80020000 | errno.
constexpr int32_t SCE_OK = 0;
inline int32_t sce_err(int posix_errno) { return int32_t(0x80020000u | uint32_t(posix_errno)); }

// FreeBSD errno values the game sees (Linux values differ for some).
int to_ps4_errno(int linux_errno);

// GPU hooks (hle_gpu.cpp): guest memory the GPU can see, and write faults on pages it caches.
void gpu_init();
bool gpu_active();  // the real renderer is running
void gpu_on_map(uint64_t addr, uint64_t size);
void gpu_on_unmap(uint64_t addr, uint64_t size);
bool gpu_on_fault(void* ucontext, void* addr);

// Guest paths (/app0/..., /temp0/...) -> host paths.
std::string host_path(const char* guest);

}  // namespace d1
