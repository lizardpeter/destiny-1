#pragma once
#include <cstdint>
#include <string>
#include <vector>

#include "loader.h"

namespace d1 {

struct Runtime {
    std::vector<Module> modules;  // [0] = eboot
    std::string app0;             // host directory backing /app0
    std::string data_root;        // host directory for /temp0, /download0, /data, ...
};

Runtime& rt();

// Threads that run guest code need their own PS4 TCB (GS base).
void* tls_create_thread_block();
void tls_set_current(void* tcb);
void tls_destroy_thread_block(void* tcb);

// Call guest code fn(a0, a1, a2) from a terminal frame-pointer frame.
extern "C" uint64_t d1_call_guest(const void* fn, uint64_t a0, uint64_t a1, uint64_t a2);

// Resolve an address to "module+0xoff".
std::string describe_addr(uint64_t a);

// Start a host thread that runs guest code with a PS4 TCB installed.
// `fn` is called with the TCB already set; used for the main thread and scePthreadCreate.
}  // namespace d1
