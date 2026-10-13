// Game-specific hooks into Destiny 1 (CUSA00219 01.33 eboot) code.
//
// A hook overwrites the first 14 bytes of a guest function with `jmp [rip+0]; dq host_fn`,
// so calls go straight to a host function with the same System V signature (declared
// D1_SYSV, which matters on Windows). Addresses are
// eboot offsets documented in findings/LOG.md; they are only valid for the 01.33 build.
#include <atomic>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "hle.h"
#include "runtime.h"
#include "settings.h"

namespace d1 {

static void replace_function(uint64_t guest, const void* host) {
    uint8_t code[14] = {0xFF, 0x25, 0, 0, 0, 0};
    uint64_t h = reinterpret_cast<uint64_t>(host);
    std::memcpy(code + 6, &h, 8);
    std::memcpy(reinterpret_cast<void*>(guest), code, sizeof code);
}

// Hook with a callable original: the first whole instructions (>= 5 bytes) of the guest
// function move to a trampoline that jumps back; the function start becomes `jmp rel32`
// to a stub near the module that jumps to the host function. Only plain prologue
// instructions are relocated (push/mov rbp,rsp/sub rsp,imm), never RIP-relative ones.
static uint8_t* g_near = nullptr;
static size_t g_near_used = 0;
static uint8_t* near_alloc(size_t n) {
    if (!g_near) {
        const Module& exe = rt().modules[0];
        void* want = reinterpret_cast<void*>((exe.base + exe.size + 0x100000 + 0xFFFF) & ~uint64_t(0xFFFF));
        g_near = static_cast<uint8_t*>(os::alloc(reinterpret_cast<uint64_t>(want), 1 << 20,
                                                 os::kRead | os::kWrite | os::kExec, false));
        if (g_near != want) { g_near = nullptr; return nullptr; }
    }
    uint8_t* p = g_near + g_near_used;
    g_near_used += (n + 15) & ~size_t(15);
    return p;
}
static size_t prologue_len(const uint8_t* p) {
    if (p[0] >= 0x50 && p[0] <= 0x57) return 1;                                  // push r64
    if (p[0] == 0x41 && p[1] >= 0x50 && p[1] <= 0x57) return 2;                  // push r8-r15
    if (p[0] == 0x48 && p[1] == 0x89 && p[2] == 0xE5) return 3;                  // mov rbp, rsp
    if (p[0] == 0x48 && p[1] == 0x83 && p[2] == 0xEC) return 4;                  // sub rsp, imm8
    if (p[0] == 0x48 && p[1] == 0x81 && p[2] == 0xEC) return 7;                  // sub rsp, imm32
    return 0;
}
static void* hook_function(uint64_t guest, const void* host) {
    auto* g = reinterpret_cast<uint8_t*>(guest);
    size_t n = 0;
    while (n < 5) {
        size_t l = prologue_len(g + n);
        if (!l) { log("hooks: cannot relocate prologue at %s", describe_addr(guest).c_str()); return nullptr; }
        n += l;
    }
    uint8_t* tramp = near_alloc(n + 14);
    uint8_t* stub = near_alloc(14);
    if (!tramp || !stub) return nullptr;
    std::memcpy(tramp, g, n);
    uint8_t back[14] = {0xFF, 0x25, 0, 0, 0, 0};
    uint64_t ret = guest + n;
    std::memcpy(back + 6, &ret, 8);
    std::memcpy(tramp + n, back, 14);
    uint8_t to_host[14] = {0xFF, 0x25, 0, 0, 0, 0};
    uint64_t h = reinterpret_cast<uint64_t>(host);
    std::memcpy(to_host + 6, &h, 8);
    std::memcpy(stub, to_host, 14);
    int32_t rel = int32_t(reinterpret_cast<int64_t>(stub) - int64_t(guest + 5));
    g[0] = 0xE9;
    std::memcpy(g + 1, &rel, 4);
    for (size_t i = 5; i < n; ++i) g[i] = 0x90;
    return tramp;
}

// ---- bootflow prerequisite bypass (eboot+0x792ED0)
// int check_prerequisite(state*, int prereq, ctx*, int* reason): 0 satisfied, 1 pending, 2 failed.
// With D1_BYPASS=prereq a failed prerequisite is logged and reported as satisfied.
using PrereqFn = D1_SYSV uint32_t (*)(void*, uint32_t, void*, int32_t*);
static PrereqFn g_prereq_orig = nullptr;
static D1_SYSV uint32_t prereq_bypass(void* state, uint32_t prereq, void* ctx, int32_t* reason) {
    uint32_t r = g_prereq_orig(state, prereq, ctx, reason);
    if (r == 2) {
        static int logged[64];
        if (prereq < 64 && logged[prereq]++ < 3)
            log("bypass: prerequisite %u failed (reason %d) -> forced satisfied", prereq, reason ? *reason : -1);
        if (reason) *reason = -1;
        return 0;
    }
    return r;
}

// ---- DemonWare transport status (eboot+0x2EB340 "started", eboot+0x2EBD40 "failed")
// Both wrap the status of the DemonWare network-start object at g_2F66F68 (status 2 = started).
// D1_BYPASS=transport reports the transport as started so platform_signin can proceed.
static D1_SYSV bool transport_started() { return true; }
static D1_SYSV bool transport_failed() { return false; }

// ---- job steal outside the job system (eboot+0xFAAC0)
// Threads that wait for the GPU (Graphics Heartbeat's frame-counter wait at 0x7DD1CA) spin
// through 0xFB860, which tries to run a pending job via 0xFAAC0. That dereferences the
// calling thread's job context (TLS slot read by 0xFC520), which only job-system threads
// have (set by 0xFAD30). On a console the GPU is usually done before the wait starts; with
// a slower GPU the heartbeat crashes there (shadPS4 users see the same 0xFAAF4 fault).
// Without a context, report "no job run" so the caller sleeps and polls again.
using StealFn = D1_SYSV bool (*)();
static StealFn g_steal_orig = nullptr;
using JobContextFn = D1_SYSV void* (*)();
static JobContextFn g_job_context = nullptr;
static D1_SYSV bool steal_guard() {
    if (!g_job_context()) return false;
    return g_steal_orig();
}

// ---- world controller selection (eboot+0x52C020 -> 0x751EE0)
// Modes: 0 SWC, 1 DWC, 2 EWC (c_editor_world_controller), 3 OWC (c_online_world_controller),
// 4 AHWC (activity host; not built into the retail client). Retail picks EWC when the flag
// read by 0x239B70 is set, else OWC. D1_WORLD_CONTROLLER=editor forces that flag
// (research: does the editor controller load a world without online services?).
static D1_SYSV bool flag_true() { return true; }

// ---- frame rate (eboot+0x593F00 builds "time control config globals", pointer at 0x26BCD08)
// Config fields (µs): +0x08 frame period (33366 = 29.97 fps), +0x28 vblank period,
// +0x38 integer target fps. The main loop (0x594460) sleeps until the next period and the
// frame-time getters (0x593890 seconds, 0x5938B0 fps) derive from +0x08, so changing the
// period changes pacing and the per-frame time step together. Title-screen timing is
// wall-clock based at 30 and 60 fps (findings/LOG.md). The `fps` setting (or D1_FPS) sets the target.
using TimeInitFn = D1_SYSV void (*)(void*);
static TimeInitFn g_time_init_orig = nullptr;
static D1_SYSV void time_init_hook(void* cfg) {
    g_time_init_orig(cfg);
    static const int fps = settings().fps;
    auto* tc = *reinterpret_cast<uint8_t**>(rt().modules[0].base + 0x26BCD08);
    if (!tc || fps <= 0) return;
    *reinterpret_cast<int64_t*>(tc + 0x08) = 1000000 / fps;
    *reinterpret_cast<int32_t*>(tc + 0x38) = fps;
    log("hooks: frame rate target %d fps (period %d us)", fps, 1000000 / fps);
}

// ---- current world-controller state (eboot+0x783AC0, the state manager's transition step)
// The state manager keeps its current state index at +0x1B0; names at 0x1945340 (37).
using StateStepFn = D1_SYSV void (*)(void*);
static StateStepFn g_state_step_orig = nullptr;
static std::atomic<int> g_state{-1};
static D1_SYSV void state_step_hook(void* sm) {
    g_state_step_orig(sm);
    g_state.store(*reinterpret_cast<const int32_t*>(static_cast<uint8_t*>(sm) + 0x1B0), std::memory_order_relaxed);
}
const char* game_state() {
    int s = g_state.load(std::memory_order_relaxed);
    if (s < 0 || s >= 37) return nullptr;
    auto* names = reinterpret_cast<const char* const*>(rt().modules[0].base + 0x1945340);
    return names[s];
}

// ---- engine logging (eboot+0xE4D70 gate, eboot+0xE4AA0 emit)
// Release builds keep the log calls but the per-channel threshold table is absent, so every
// message is dropped. With D1_GAME_LOG set, the gate always passes and the emit prints the
// already-formatted text. D1_GAME_LOG=<substring> keeps only matching lines.
static const char* g_log_filter = nullptr;
static D1_SYSV bool game_log_enabled(int channel, int level) { return true; }
static D1_SYSV void game_log_emit(uint32_t, const char* text) {
    if (!text) return;
    if (g_log_filter && *g_log_filter && !std::strstr(text, g_log_filter)) return;
    size_t n = strnlen(text, 320);
    while (n && (text[n - 1] == '\n' || text[n - 1] == '\r')) --n;
    log("[game] %.*s", int(n), text);
}

// ---- engine heap allocation (eboot+0x1009CB0: heap, size, allocation id, halt_on_oom)
// D1_ALLOC_LOG=<MiB>: log allocations of at least that size with the caller chain.
using HeapAllocFn = D1_SYSV void* (*)(void*, uint64_t, uint32_t, char);
static HeapAllocFn g_heap_alloc_orig = nullptr;
static uint64_t g_alloc_log_min = 0;
static D1_SYSV void* heap_alloc_hook(void* heap, uint64_t size, uint32_t id, char halt) {
    if (size >= g_alloc_log_min) {
        // Our caller is game code (we were jumped to from its call); its frames follow the
        // frame-pointer chain from the rbp it left us.
        std::string chain = " <- " + describe_addr(reinterpret_cast<uint64_t>(__builtin_return_address(0)));
        uint64_t rbp;
        asm volatile("mov %%rbp, %0" : "=r"(rbp));
        (void)rbp;
        log("alloc: %llu bytes (id %u) on heap %p%s", (unsigned long long)size, id, heap, chain.c_str());
    }
    return g_heap_alloc_orig(heap, size, id, halt);
}

// ---- bap_signin sub-steps (eboot+0x799A70: handler update; sub-step index at handler+0x30)
// Every sub-step change of the bap_signin handler is logged.
using HandlerUpdateFn = D1_SYSV void (*)(void*);
static HandlerUpdateFn g_bap_update_orig = nullptr;
static D1_SYSV void bap_update_hook(void* h) {
    auto* step = reinterpret_cast<int32_t*>(static_cast<uint8_t*>(h) + 0x30);
    const int32_t before = *step;
    g_bap_update_orig(h);
    if (*step != before) log("bootflow: bap_signin step %d -> %d", before, *step);
}

// ---- call counters (research): D1_COUNT=off,off,... (eboot offsets, hex). Each function
// start jumps to a stub that does `lock inc qword [counter]` and continues in the original.
// Counts are printed by the watchdog (print_call_counts).
struct CallCounter { uint64_t off; uint64_t* count; };
static std::vector<CallCounter> g_counters;
static void install_call_counters(const char* list) {
    const Module& exe = rt().modules[0];
    for (const char* p = list; *p;) {
        char* end;
        const uint64_t off = std::strtoull(p, &end, 16);
        p = *end == ',' ? end + 1 : end;
        if (!off) {
            if (end == p) break;
            continue;
        }
        uint8_t* stub = near_alloc(48);
        if (!stub) break;
        auto* counter = reinterpret_cast<uint64_t*>(stub + 32);
        *counter = 0;
        // lock inc qword ptr [rip + disp]   (disp from the end of this 8-byte instruction)
        const int32_t disp = int32_t(reinterpret_cast<uint8_t*>(counter) - (stub + 8));
        stub[0] = 0xF0; stub[1] = 0x48; stub[2] = 0xFF; stub[3] = 0x05;
        std::memcpy(stub + 4, &disp, 4);
        void* tramp = hook_function(exe.base + off, stub);
        if (!tramp) continue;
        const uint8_t jmp[6] = {0xFF, 0x25, 0, 0, 0, 0};  // jmp [rip+0]; dq tramp
        std::memcpy(stub + 8, jmp, 6);
        const uint64_t t = reinterpret_cast<uint64_t>(tramp);
        std::memcpy(stub + 14, &t, 8);
        g_counters.push_back({off, counter});
    }
    log("hooks: %zu call counters", g_counters.size());
}
void print_call_counts() {
    for (auto& c : g_counters) log("count eboot+%#llx: %llu", (unsigned long long)c.off, (unsigned long long)*c.count);
}

void install_game_hooks() {
    const Module& exe = rt().modules[0];
    g_job_context = reinterpret_cast<JobContextFn>(exe.base + 0xFC520);
    g_steal_orig = reinterpret_cast<StealFn>(hook_function(exe.base + 0xFAAC0, reinterpret_cast<const void*>(&steal_guard)));
    if (!g_steal_orig) log("hooks: job-steal guard FAILED");
    if (const char* b = getenv("D1_BYPASS"); b && std::strstr(b, "prereq")) {
        g_prereq_orig = reinterpret_cast<PrereqFn>(hook_function(exe.base + 0x792ED0, reinterpret_cast<const void*>(&prereq_bypass)));
        log("hooks: bootflow prerequisite bypass %s", g_prereq_orig ? "on" : "FAILED");
    }
    // Global resource loads (eboot+0x34A1D0): with a simulation queue present the request is
    // sent as simulation event 0x4E to the session (bb1a40) and loaded when the session applies
    // it; without one it is loaded locally. Solo play has no session to apply it, so
    // D1_BYPASS=localres takes the local path: `call 0x300be0` (queue exists?) -> xor eax,eax.
    if (const char* b = getenv("D1_BYPASS"); b && std::strstr(b, "localres")) {
        auto* p = reinterpret_cast<uint8_t*>(exe.base + 0x34A278);
        if (p[0] == 0xE8) {
            const uint8_t patch[5] = {0x31, 0xC0, 0x0F, 0x1F, 0x00};  // xor eax,eax; nop3
            std::memcpy(p, patch, 5);
            log("hooks: global resources load locally (localres)");
        }
    }
    if (const char* b = getenv("D1_BYPASS"); b && std::strstr(b, "transport")) {
        replace_function(exe.base + 0x2EB340, reinterpret_cast<const void*>(&transport_started));
        replace_function(exe.base + 0x2EBD40, reinterpret_cast<const void*>(&transport_failed));
        log("hooks: DemonWare transport reported as started");
    }
    g_state_step_orig = reinterpret_cast<StateStepFn>(hook_function(exe.base + 0x783AC0, reinterpret_cast<const void*>(&state_step_hook)));
    if (settings().fps > 0) {
        g_time_init_orig = reinterpret_cast<TimeInitFn>(hook_function(exe.base + 0x593F00, reinterpret_cast<const void*>(&time_init_hook)));
        if (!g_time_init_orig) log("hooks: frame-rate hook FAILED");
    }
    if (const char* w = getenv("D1_WORLD_CONTROLLER"); w && std::strcmp(w, "editor") == 0) {
        replace_function(exe.base + 0x239B70, reinterpret_cast<const void*>(&flag_true));
        log("hooks: editor world controller selected");
    }
    // With a replacement backend: the content manifest is signed with Bungie's key, checked
    // only when the byte at 0x18DC974 is set (0x2B0980). Our backend cannot sign, so clear it.
    if (getenv("D1_BACKEND")) {
        *reinterpret_cast<volatile uint8_t*>(exe.base + 0x18DC974) = 0;
        log("hooks: content manifest signature check off (D1_BACKEND)");
    }
    {  // bap_signin sub-step trace: cheap (logs only on change), always on
        g_bap_update_orig = reinterpret_cast<HandlerUpdateFn>(
            hook_function(exe.base + 0x799A70, reinterpret_cast<const void*>(&bap_update_hook)));
        log("hooks: bootflow trace %s", g_bap_update_orig ? "on" : "FAILED");
    }
    if (const char* c = getenv("D1_COUNT")) install_call_counters(c);
    if (const char* a = getenv("D1_ALLOC_LOG")) {
        g_alloc_log_min = std::strtoull(a, nullptr, 10) << 20;
        g_heap_alloc_orig = reinterpret_cast<HeapAllocFn>(
            hook_function(exe.base + 0x1009CB0, reinterpret_cast<const void*>(&heap_alloc_hook)));
        log("hooks: allocation log (>= %s MiB) %s", a, g_heap_alloc_orig ? "on" : "FAILED");
    }
    if (const char* f = getenv("D1_GAME_LOG")) {
        g_log_filter = (std::strcmp(f, "1") == 0) ? nullptr : f;
        replace_function(exe.base + 0xE4D70, reinterpret_cast<const void*>(&game_log_enabled));
        replace_function(exe.base + 0xE4AA0, reinterpret_cast<const void*>(&game_log_emit));
        log("hooks: engine logging enabled%s%s", g_log_filter ? ", filter " : "", g_log_filter ? g_log_filter : "");
    }
}

}  // namespace d1
