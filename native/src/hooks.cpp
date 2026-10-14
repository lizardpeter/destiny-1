// Game-specific hooks into Destiny 1 (CUSA00219 01.33 eboot) code.
//
// A hook overwrites the first 14 bytes of a guest function with `jmp [rip+0]; dq host_fn`,
// so calls go straight to a host function with the same System V signature (declared
// D1_SYSV, which matters on Windows). Addresses are
// eboot offsets documented in findings/LOG.md; they are only valid for the 01.33 build.
#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "hle.h"
#include "render_bridge.h"
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
    // 1 = still waiting: log which prerequisite a state is stuck on (once per change)
    // (no thread_local here: game threads run with the guest's TLS)
    static std::atomic<uint32_t> last_waiting{~0u};
    if (r == 1 && last_waiting.exchange(prereq) != prereq) log("prerequisite %u waiting", prereq);
    if (r == 2) {
        static int logged[64];
        if (prereq < 64 && logged[prereq]++ < 3)
            log("bypass: prerequisite %u failed (reason %d) -> forced satisfied", prereq, reason ? *reason : -1);
        if (reason) *reason = -1;
        return 0;
    }
    return r;
}

// ---- initial slice-set loading task 9 (eboot+0x7965A0): waits for the local player's unit
// and the current activity-mode reference (resource 0x10, byte +0x1AC). Returns 1 while
// waiting, 2 when done. D1_BYPASS=spawn (research) completes it once the local player
// exists (local player table DAT_0273EB80 +0xC0 = player datum). The player's unit
// (+0xC4) is never spawned yet, so the game director shows the dead camera (black screen).
using TaskFn = D1_SYSV uint32_t (*)(void*);
static TaskFn g_task9_orig = nullptr;
static D1_SYSV uint32_t task9_bypass(void* h) {
    uint32_t r = g_task9_orig(h);
    if (r == 1) {
        const Module& exe = rt().modules[0];
        auto* players = *reinterpret_cast<uint8_t**>(exe.base + 0x273EB80);
        if (players && *reinterpret_cast<int32_t*>(players + 0xC0) != -1) {
            static bool logged = false;
            if (!logged) { logged = true; log("bypass: slice-set loading task 9 forced complete (player exists, unit %d)",
                                    *reinterpret_cast<int32_t*>(players + 0xC4)); }
            return 2;
        }
    }
    return r;
}

// ---- native mouse look (eboot+0x91B500, the per-player control update)
// void player_control_update(float dt, float, int slot, uint player, input_state* s,
//                            control* c, float* action)
// The game turns the right stick into this frame's look: stick -> deadzones (input
// abstraction 0x926910) -> response curves and turn-speed acceleration (0x928670: yaw rate =
// s[+0x2CC] * 120 deg/s, pitch rate = s[+0x2D4] * 60 deg/s) -> aim assist, zoom scaling ->
// action[5] = yaw_rate * dt, action[6] = pitch_rate * dt (radians; +yaw turns left, +pitch
// looks up). The hook runs after all of that and adds raw mouse counts straight into those
// two deltas: no stick quantization, curve, acceleration, deadzone or aim assist, and the
// counts are at most ~1 ms old (window event loop). A controller keeps working alongside.
using PlayerControlFn = D1_SYSV void (*)(float, float, int32_t, uint32_t, void*, int32_t*, float*);
using GuestBoolFn = D1_SYSV bool (*)();
using ZoomMagFn = D1_SYSV float (*)(int32_t unit, int32_t zoom);
using ZoomAxesFn = D1_SYSV void (*)(int32_t unit, float* yaw, float* pitch);
static PlayerControlFn g_pc_orig = nullptr;
static void trace_cameras();
static int32_t g_mouse_test_dx = 0, g_mouse_test_dy = 0;  // D1_MOUSE_TEST=dx,dy (headless)
static D1_SYSV void player_control_hook(float dt, float f2, int32_t slot, uint32_t player, void* state,
                                        int32_t* control, float* action) {
    g_pc_orig(dt, f2, slot, player, state, control, action);
    if (player != 0 || !action) return;
    trace_cameras();
    if (getenv("D1_TRACE_CINE")) {  // research: why loading cinematics are suppressed
        static int n = 0;
        if (n++ == 0) {
            const uint64_t b = rt().modules[0].base;
            const uint8_t* sel = *reinterpret_cast<uint8_t**>(b + 0x26BC068);
            const bool act = reinterpret_cast<GuestBoolFn>(b + 0x78C710)();
            log("cine: activity selection byte0 %d (+0x12C %d), activity condition %d", sel ? sel[0] : -1,
                sel ? sel[0x12C] : -1, act);
            using PtrFn = D1_SYSV uint8_t* (*)(int32_t);
            const uint8_t* a = reinterpret_cast<PtrFn>(b + 0x775770)(0);
            if (a) {
                log("cine: activity %p: A valid %d dest %#x, B valid %d B+0xE8 short %d, cached dest %#x", (const void*)a,
                    a[0x4B8 + 0xE0] & 1, *reinterpret_cast<const uint32_t*>(a + 0x59C), a[0x9B8 + 0xE0] & 1,
                    *reinterpret_cast<const int16_t*>(a + 0x9B8 + 0xE8 + 2), *reinterpret_cast<const uint32_t*>(b + 0x26CF2B0));
                for (int off : {0x4B8, 0x9B8}) {
                    for (int row = 0; row < 0x110; row += 32) {
                        char hex[3 * 32 + 1] = {};
                        for (int i = 0; i < 32; ++i) std::snprintf(hex + 3 * i, 4, "%02x ", a[off + row + i]);
                        log("cine: +%#x %s", off + row, hex);
                    }
                }
            }
        }
    }
    int32_t dx = 0, dy = 0;
    bool have = render::take_mouse_motion(dx, dy);
    if (!have && (g_mouse_test_dx || g_mouse_test_dy)) dx = g_mouse_test_dx, dy = g_mouse_test_dy, have = true;
    // counts gathered while the game was not running player control (loading, menus) are stale
    static auto last = std::chrono::steady_clock::now();
    const auto now = std::chrono::steady_clock::now();
    const bool stale = now - last > std::chrono::milliseconds(250);
    last = now;
    if (!have || stale || (dx == 0 && dy == 0)) return;
    const Module& exe = rt().modules[0];
    auto* globals = *reinterpret_cast<uint8_t**>(exe.base + 0x273EB28);  // player_control_globals
    // the game zeroes the look deltas while look is locked (+0xC bit 0) or the game is paused
    if (!globals || (globals[0xC] & 1) || reinterpret_cast<GuestBoolFn>(exe.base + 0x591B30)()) return;
    const Settings& cfg = settings();
    double yaw_scale = 1.0, pitch_scale = 1.0;
    if (slot >= 0 && slot < 4 && cfg.mouse_zoom_scale > 0) {
        const int32_t unit = *reinterpret_cast<int32_t*>(globals + 0x20 + slot * 0x1A0);
        const int16_t zoom = *reinterpret_cast<int16_t*>(globals + 0x6E + slot * 0x1A0);
        if (unit != -1 && zoom != -1) {  // the same slowdown the game applies to the stick when zoomed
            const float mag = reinterpret_cast<ZoomMagFn>(exe.base + 0xBD3740)(unit, zoom);
            float y = 1.0f, p = 1.0f;
            reinterpret_cast<ZoomAxesFn>(exe.base + 0xBD3A50)(unit, &y, &p);
            if (mag > 0.01f) {
                yaw_scale = std::pow(std::clamp(double(y / mag), 0.02, 1.0), cfg.mouse_zoom_scale);
                pitch_scale = std::pow(std::clamp(double(p / mag), 0.02, 1.0), cfg.mouse_zoom_scale);
            }
        }
    }
    const double rad_per_count = cfg.mouse_sensitivity * 0.022 * 3.14159265358979 / 180.0;
    const float yaw = float(-dx * rad_per_count * yaw_scale);
    const float pitch = float((cfg.mouse_invert ? dy : -dy) * rad_per_count * pitch_scale);
    static int traced = 0;
    if (getenv("D1_MOUSE_TRACE") && traced < 40) {
        ++traced;
        const float* facing = reinterpret_cast<const float*>(globals + 0x20 + slot * 0x1A0 + 0x18);
        log("mouse: dt %.4f counts %d,%d game look %.5f,%.5f + mouse %.5f,%.5f (zoom %.3f,%.3f) facing %.4f,%.4f",
            dt, dx, dy, action[5], action[6], yaw, pitch, yaw_scale, pitch_scale, facing[0], facing[1]);
    }
    action[5] += yaw;
    action[6] += pitch;
    static bool announced = false;
    if (!announced) { announced = true; log("input: mouse look active (%.2f sensitivity)", cfg.mouse_sensitivity); }
}

// ---- loading-cinematic suppression (eboot+0x766750): investment activity selection
// (*0x26BC068) byte 0 == 1, or the face-to-face join check (0x78C710). D1_TRACE_CINE logs
// every change of the result with the selection's first bytes (research).
using CineFn = D1_SYSV bool (*)();
static CineFn g_cine_orig = nullptr;
static D1_SYSV bool cine_suppressed_hook() {
    const bool r = g_cine_orig();
    static std::atomic<int> last{-1};
    if (last.exchange(r) != int(r)) {
        const uint8_t* sel = *reinterpret_cast<uint8_t**>(rt().modules[0].base + 0x26BC068);
        char hex[3 * 24 + 1] = {};
        for (int i = 0; sel && i < 24; ++i) std::snprintf(hex + 3 * i, 4, "%02x ", sel[i]);
        log("cine: loading cinematics %s (selection %s; state %s)", r ? "suppressed" : "allowed", hex, game_state());
    }
    return r;
}

// ---- camera trace (D1_TRACE_CAMERA, research): director camera switches (0x8E4EE0
// set_camera(director, type, force, float blend); the camera lives inline at director +0x10,
// its vtable slot 0 returns the type) and, in-world, each seen director's current camera.
using SetCameraFn = D1_SYSV uint64_t (*)(uint8_t*, int32_t, uint32_t, float);
static SetCameraFn g_set_camera_orig = nullptr;
static std::atomic<uint8_t*> g_directors[4];
static int32_t camera_type(uint8_t* director) {
    auto* cam = director + 0x10;
    auto** vt = *reinterpret_cast<void***>(cam);
    return reinterpret_cast<D1_SYSV int32_t (*)(void*)>(vt[0])(cam);
}
static D1_SYSV uint64_t set_camera_hook(uint8_t* director, int32_t type, uint32_t force, float blend) {
    const int32_t before = camera_type(director);
    const uint64_t r = g_set_camera_orig(director, type, force, blend);
    for (auto& d : g_directors) {
        uint8_t* expect = nullptr;
        if (d.load() == director || d.compare_exchange_strong(expect, director)) break;
    }
    log("camera: director %p (vtable +%#llx) type %d -> %d (requested %d%s, state %s)", (void*)director,
        (unsigned long long)(*reinterpret_cast<uint64_t*>(director) - rt().modules[0].base), before,
        camera_type(director), type, (force & 0xFF) ? ", forced" : "", game_state());
    return r;
}
static void trace_cameras() {
    static auto last = std::chrono::steady_clock::now();
    if (!g_set_camera_orig || std::chrono::steady_clock::now() - last < std::chrono::seconds(5)) return;
    last = std::chrono::steady_clock::now();
    for (auto& d : g_directors)
        if (uint8_t* p = d.load())
            log("camera: director %p current type %d (camera vtable +%#llx)", (void*)p, camera_type(p),
                (unsigned long long)(*reinterpret_cast<uint64_t*>(p + 0x10) - rt().modules[0].base));
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
// +0x38 integer target fps. The main loop (0x594460) waits until last frame + period
// (`add rcx, [rsi+8]` at 0x594A3B), and the game-time update (0x591710, given the real
// elapsed seconds) runs elapsed / period simulation ticks of one period each (0x593890
// seconds, 0x5938B0 fps), so game time stays wall-clock correct and the tick rate equals
// the target. `fps = N` sets the target. `fps = 0` (unlimited, the default) removes the wait
// and, every frame, sets the period to that frame's real duration (1-33.4 ms) just before
// the tick math: one simulation tick per rendered frame with dt = the frame time; below
// 30 fps it falls back to several 33 ms ticks.
using TimeInitFn = D1_SYSV void (*)(void*);
using GameTimeFn = D1_SYSV void (*)(float, float*, int32_t*, float*, int32_t*);
static TimeInitFn g_time_init_orig = nullptr;
static GameTimeFn g_game_time_orig = nullptr;
static D1_SYSV void time_init_hook(void* cfg) {
    g_time_init_orig(cfg);
    static const int fps = settings().fps;
    auto* tc = *reinterpret_cast<uint8_t**>(rt().modules[0].base + 0x26BCD08);
    if (!tc || fps <= 0) return;
    *reinterpret_cast<int64_t*>(tc + 0x08) = 1000000 / fps;
    *reinterpret_cast<int32_t*>(tc + 0x38) = fps;
    log("hooks: frame rate target %d fps (period %d us)", fps, 1000000 / fps);
}
static D1_SYSV void game_time_hook(float elapsed, float* dt, int32_t* ticks, float* dt2, int32_t* ticks2) {
    if (auto* tc = *reinterpret_cast<uint8_t**>(rt().modules[0].base + 0x26BCD08); tc && elapsed > 0.0f) {
        const int64_t period = std::clamp<int64_t>(int64_t(double(elapsed) * 1e6 + 0.5), 1000, 33366);
        *reinterpret_cast<int64_t*>(tc + 0x08) = period;
        *reinterpret_cast<int32_t*>(tc + 0x38) = int32_t(1000000 / period);
    }
    g_game_time_orig(elapsed, dt, ticks, dt2, ticks2);
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

// investment_signin (eboot+0x79DA10): step at +0x30, sub-step at +0x34 (done at 7/3)
static HandlerUpdateFn g_invest_update_orig = nullptr;
static D1_SYSV void invest_update_hook(void* h) {
    auto* step = reinterpret_cast<int32_t*>(static_cast<uint8_t*>(h) + 0x30);
    const int32_t a = step[0], b = step[1];
    g_invest_update_orig(h);
    if (step[0] != a || step[1] != b) log("bootflow: investment_signin step %d.%d -> %d.%d", a, b, step[0], step[1]);
}

// profile_setup (eboot+0x7A01C0): step at +0x38 (0 brightness, 2 screen bounds, 4 ..., 7 done)
static HandlerUpdateFn g_profile_update_orig = nullptr;
// Screens: 0 brightness (UI 0x16), 2 screen bounds (0x15), 4 (0x17); each finishes with a
// "completed" event (0x7A02E0: 0x23/0x22/0x24) moving 1->2, 3->4, 5->6. D1_BYPASS=profile
// completes them at once (headless testing).
static bool g_profile_bypass = false;
static D1_SYSV void profile_update_hook(void* h) {
    auto* step = reinterpret_cast<int32_t*>(static_cast<uint8_t*>(h) + 0x38);
    if (g_profile_bypass && (*step == 1 || *step == 3 || *step == 5)) ++*step;
    const int32_t a = *step;
    g_profile_update_orig(h);
    if (*step != a) log("bootflow: profile_setup step %d -> %d", a, *step);
}

// Further bootflow handlers: update function, name, offset of a pair of int step fields.
struct StepTrace { uint64_t off; const char* name; uint32_t field; HandlerUpdateFn orig; };
static StepTrace g_step_traces[] = {
    {0x79FDE0, "prepare_for_orbit", 0x30, nullptr},
    {0x7A1AF0, "character_signin", 0x40, nullptr},
    {0x7A1470, "character_prologue", 0x30, nullptr},
    // activity:initial_slice_set_loading (update 0x7969A0): completed-task mask at +0x1A8,
    // done when it equals the required mask at +0x198 (0x7FF, 11 tasks set up by 0x7958C0)
    {0x7969A0, "initial_slice_set_loading", 0x1A8, nullptr},
};
template <int I>
static D1_SYSV void step_trace_hook(void* h) {
    StepTrace& t = g_step_traces[I];
    auto* f = reinterpret_cast<int32_t*>(static_cast<uint8_t*>(h) + t.field);
    const int32_t a = f[0], b = f[1];
    // character:prologue (0x7A1470) step 2 plays the intro cinematic on the player object at
    // 0x295C0A0 (started by 0x33E0D0, playing while 0x33E140). The game stops it itself
    // (0x33E110) on Square/Triangle once world controller +0x2E39 allows skipping;
    // skip_intro stops it right away.
    if (t.off == 0x7A1470 && a == 2 && settings().skip_intro) {
        static bool done = false;
        if (!done) {
            done = true;
            const uint64_t base = rt().modules[0].base;
            reinterpret_cast<D1_SYSV void (*)(void*)>(base + 0x33E110)(reinterpret_cast<void*>(base + 0x295C0A0));
            log("hooks: intro cinematic skipped (skip_intro)");
        }
    }
    t.orig(h);
    if (f[0] != a || f[1] != b) log("bootflow: %s step %d.%d -> %d.%d", t.name, a, b, f[0], f[1]);
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
    if (const char* b = getenv("D1_BYPASS"); b && std::strstr(b, "spawn")) {
        g_task9_orig = reinterpret_cast<TaskFn>(hook_function(exe.base + 0x7965A0, reinterpret_cast<const void*>(&task9_bypass)));
        log("hooks: slice-set loading task 9 bypass %s", g_task9_orig ? "on" : "FAILED");
    }
    // BLOCK_DETECT thread (entry 0x92A3D0, thread table 0x194C3A8): halts the game with
    // "hitch detected ... stalled" when the main loop stops progressing. D1_NO_BLOCK_DETECT
    // (slow software-rendered test runs) makes the thread exit at once.
    if (getenv("D1_NO_BLOCK_DETECT")) {
        const uint8_t ret0[3] = {0x31, 0xC0, 0xC3};
        std::memcpy(reinterpret_cast<void*>(exe.base + 0x92A3D0), ret0, 3);
        log("hooks: BLOCK_DETECT hitch watchdog off");
    }
    if (getenv("D1_TRACE_CAMERA"))
        g_set_camera_orig = reinterpret_cast<SetCameraFn>(hook_function(exe.base + 0x8E4EE0, reinterpret_cast<const void*>(&set_camera_hook)));
    if (getenv("D1_TRACE_CINE"))
        g_cine_orig = reinterpret_cast<CineFn>(hook_function(exe.base + 0x766750, reinterpret_cast<const void*>(&cine_suppressed_hook)));
    if (const char* b = getenv("D1_BYPASS"); b && std::strstr(b, "transport")) {
        replace_function(exe.base + 0x2EB340, reinterpret_cast<const void*>(&transport_started));
        replace_function(exe.base + 0x2EBD40, reinterpret_cast<const void*>(&transport_failed));
        log("hooks: DemonWare transport reported as started");
    }
    g_pc_orig = reinterpret_cast<PlayerControlFn>(hook_function(exe.base + 0x91B500, reinterpret_cast<const void*>(&player_control_hook)));
    if (!g_pc_orig) log("hooks: mouse look hook FAILED");
    if (const char* t = getenv("D1_MOUSE_TEST")) std::sscanf(t, "%d,%d", &g_mouse_test_dx, &g_mouse_test_dy);
    g_state_step_orig = reinterpret_cast<StateStepFn>(hook_function(exe.base + 0x783AC0, reinterpret_cast<const void*>(&state_step_hook)));
    if (settings().fps > 0) {
        g_time_init_orig = reinterpret_cast<TimeInitFn>(hook_function(exe.base + 0x593F00, reinterpret_cast<const void*>(&time_init_hook)));
        if (!g_time_init_orig) log("hooks: frame-rate hook FAILED");
    } else {  // unlimited: no limiter wait, one simulation tick per rendered frame
        auto* wait = reinterpret_cast<uint8_t*>(exe.base + 0x594A3B);
        const uint8_t expect[4] = {0x48, 0x03, 0x4E, 0x08}, nop4[4] = {0x0F, 0x1F, 0x40, 0x00};
        g_game_time_orig = reinterpret_cast<GameTimeFn>(hook_function(exe.base + 0x591710, reinterpret_cast<const void*>(&game_time_hook)));
        if (g_game_time_orig && std::memcmp(wait, expect, 4) == 0) {
            std::memcpy(wait, nop4, 4);
            log("hooks: frame rate unlimited (one game tick per frame)");
        } else {
            log("hooks: unlimited frame rate hook FAILED");
        }
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
        g_invest_update_orig = reinterpret_cast<HandlerUpdateFn>(
            hook_function(exe.base + 0x79DA10, reinterpret_cast<const void*>(&invest_update_hook)));
        if (const char* b = getenv("D1_BYPASS"); b && std::strstr(b, "profile")) g_profile_bypass = true;
        const void* step_hooks[] = {reinterpret_cast<const void*>(&step_trace_hook<0>),
                                    reinterpret_cast<const void*>(&step_trace_hook<1>),
                                    reinterpret_cast<const void*>(&step_trace_hook<2>),
                                    reinterpret_cast<const void*>(&step_trace_hook<3>)};
        static_assert(sizeof(step_hooks) / sizeof(step_hooks[0]) == sizeof(g_step_traces) / sizeof(g_step_traces[0]));
        for (size_t i = 0; i < sizeof(g_step_traces) / sizeof(g_step_traces[0]); ++i)
            g_step_traces[i].orig = reinterpret_cast<HandlerUpdateFn>(hook_function(exe.base + g_step_traces[i].off, step_hooks[i]));
        g_profile_update_orig = reinterpret_cast<HandlerUpdateFn>(
            hook_function(exe.base + 0x7A01C0, reinterpret_cast<const void*>(&profile_update_hook)));
        log("hooks: bootflow trace %s",
            g_bap_update_orig && g_invest_update_orig && g_profile_update_orig ? "on" : "FAILED");
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
