// Registry for host implementations of PS4 firmware functions ("HLE").
//
// PS4 user code uses the System V AMD64 ABI. A firmware function is an ordinary host
// function with the matching signature; HLE() registers it by its PS4 symbol name (the
// linker computes the NID) through a System V entry point, which on Windows converts to
// the host calling convention and on Linux is the function itself.
#pragma once
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

#include "os.h"

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

// System V entry point for a host function (Windows: converts the calling convention).
template <auto F> struct GuestEntry;
template <class R, class... A, R (*F)(A...)> struct GuestEntry<F> {
    static D1_SYSV R call(A... a) { return F(a...); }
};
template <auto F> inline void* guest_entry() { return reinterpret_cast<void*>(&GuestEntry<F>::call); }

#define D1_CAT2(a, b) a##b
#define D1_CAT(a, b) D1_CAT2(a, b)
#define HLE(name, fn) static ::d1::HleReg D1_CAT(_hle_, __LINE__){name, ::d1::guest_entry<&fn>()};
// A function already declared D1_SYSV (e.g. variadic ones) registers as itself.
#define HLE_SYSV(name, fn) static ::d1::HleReg D1_CAT(_hle_, __LINE__){name, reinterpret_cast<void*>(&fn)};
#define HLE_OBJ(name, obj) static ::d1::HleReg D1_CAT(_hleo_, __LINE__){name, reinterpret_cast<void*>(&obj), true};

void log(const char* fmt, ...) __attribute__((format(printf, 1, 2)));
void log_to_file(const std::string& path);  // also write the log to this file

// Guest time structures (FreeBSD amd64: 64-bit fields, unlike Windows' timeval/timespec).
struct GuestTimespec { int64_t tv_sec, tv_nsec; };
struct GuestTimeval { int64_t tv_sec, tv_usec; };

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

// Backend routing (hle_net.cpp): D1_BACKEND server, and whether a hostname belongs to the
// services it replaces (then *addr_be is the server's IPv4 address).
const char* backend_host();
bool backend_route(const char* host, uint32_t* addr_be);
struct BackendReply {
    int status = 0;
    std::vector<std::pair<std::string, std::string>> headers;
    std::string body;
};
// A blocking HTTP/1.1 request to the backend's HTTP port (hle_http.cpp).
bool backend_http(const std::string& method, const std::string& host, const std::string& path,
                  const std::vector<std::pair<std::string, std::string>>& headers, const void* data,
                  size_t size, BackendReply& out);

// Queue a system-service event for the game (hle_services.cpp), e.g. 0x10000002 session
// invitation with its 0x8C-byte parameter.
void push_system_event(int32_t type, const void* data, size_t size);
// Per-frame research tick (hooks.cpp), run from sceSystemServiceGetStatus.
void hooks_system_tick();

// Sockets the game opened (hle_net.cpp): `close` routes them to the network layer.
bool net_is_socket(int fd);
int net_close_socket(int fd);

// Current world-controller state name (e.g. "bootflow:start"), or null (hooks.cpp).
const char* game_state();

// Guest paths (/app0/..., /temp0/...) -> host paths.
std::string host_path(const char* guest);

}  // namespace d1
