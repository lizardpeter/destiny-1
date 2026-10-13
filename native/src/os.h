// Host operating-system layer: everything d1-native needs from Linux or Windows.
//
// The game's code uses the System V AMD64 calling convention (PS4 = FreeBSD). On Linux
// that is the native convention; on Windows every host function the game calls, and every
// game function the host calls, is declared D1_SYSV so the compiler converts.
#pragma once
#include <cstdint>
#include <string>

#define D1_SYSV __attribute__((sysv_abi))

#if defined(_WIN32)
#define D1_WINDOWS 1
#endif

namespace d1::os {

void init();  // process-wide setup: timer resolution, sockets, console encoding

// ---- virtual memory. prot is a mask of kRead | kWrite | kExec.
enum : int { kRead = 1, kWrite = 2, kExec = 4 };
// Committed, zeroed memory. exact: must start at addr (replacing anything mapped there, like
// MAP_FIXED); otherwise addr is a hint (0 = anywhere) and the host may choose.
void* alloc(uint64_t addr, uint64_t size, int prot, bool exact);
// Address space only (no memory), for later exact mappings inside it.
void* reserve(uint64_t addr, uint64_t size, bool exact);
bool release(void* addr, uint64_t size);
bool protect(void* addr, uint64_t size, int prot);
// "Physical" memory: one backing store that can be mapped at several addresses at once,
// like the console's direct memory (CPU and GPU views of the same pages).
bool phys_create(uint64_t size);
void* phys_map(uint64_t addr, uint64_t size, uint64_t offset, int prot, bool exact);
// Write into memory regardless of its page protection (GPU writes into tracked pages).
bool write_backing(void* addr, const void* data, uint64_t size);
// Allocation granularity for addresses the host picks (16 KiB on Linux, 64 KiB on Windows).
uint64_t granularity();

// ---- threads and time
uint32_t thread_id();
void sleep_us(uint64_t us);  // precise (sub-millisecond) on both systems
void set_thread_name(const char* name);

// ---- files
std::string exe_dir();  // folder of the running executable, no trailing separator
bool is_dir(const std::string& path);
void make_dirs(const std::string& path);

// ---- user-facing errors: a message box on Windows (a console window may close at once)
void error_box(const std::string& text);

// ---- processes: start a helper (the backend) that dies with us
bool spawn_child(const std::string& exe, const std::string& args, const std::string& log_file);

}  // namespace d1::os
