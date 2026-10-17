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

#include <map>
#include <set>
#include <mutex>
#include "hle.h"
#include "os.h"
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

// Exported for other subsystems (native_gfx.cpp): hook an eboot function by offset.
void* hook_eboot_function(uint64_t off, const void* host) {
    return hook_function(rt().modules[0].base + off, host);
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
            if (!logged) {
                logged = true;
                log("bypass: slice-set loading task 9 forced complete (player exists, unit %d)",
                    *reinterpret_cast<int32_t*>(players + 0xC4));
            }
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
static void trace_references();
static void roster_tick();
static std::atomic<int32_t> g_spawn_entity{-1};
static int client_references(uint64_t b, int type, uint8_t** out, int max);
static int32_t g_mouse_test_dx = 0, g_mouse_test_dy = 0;  // D1_MOUSE_TEST=dx,dy (headless)

// ---- direct weapon selection (PC keys 1 / 2 / 3)
// The console has no "weapon n" button: Triangle tapped toggles primary and special, held
// draws the heavy weapon. The player control record (*0x273EB28, one local player) keeps the
// unit at +0x20, and 0xBD5AA0(unit) gives the unit's current weapon index (0 primary,
// 1 special, 2 heavy; 0xBD5340(unit, index) != -1 when it has one there). The record's
// +0x64/+0x68 (current / desired index, copied into the unit action) are not a way in:
// 0x91EE90 resets +0x68 from the unit (0xBD5B80) every update, so writing it changes nothing.
// A weapon key therefore drives Triangle the way a player would - a tap, or a hold for the
// heavy weapon - until the unit holds the wanted weapon (or 6 s pass), reading the result
// every update from the post-0x91B500 hook; the pad read (hle_input.cpp) adds the presses.
// D1_WEAPON_TEST=<index>@<secs>,... (headless): request weapons at those times after the
// first player control update; D1_TRACE_WEAPON logs the state every 2 s.
using UnitWeaponFn = D1_SYSV int32_t (*)(int32_t unit, int16_t index);
using UnitCurrentWeaponFn = D1_SYSV int32_t (*)(int32_t unit);
static std::atomic<uint32_t> g_injected_buttons{0};
uint32_t hooks_injected_buttons() { return g_injected_buttons.load(std::memory_order_relaxed); }
static void select_weapon() {
    using clock = std::chrono::steady_clock;
    const uint64_t b = rt().modules[0].base;
    auto* pc = *reinterpret_cast<uint8_t**>(b + 0x273EB28);
    if (!pc) return;
    const int32_t unit = *reinterpret_cast<int32_t*>(pc + 0x20);
    if (unit == -1) { g_injected_buttons = 0; return; }
    int want = render::take_weapon_request();
    static const char* test = getenv("D1_WEAPON_TEST");
    static const auto t0 = clock::now();
    const auto now = clock::now();
    if (test && want < 0) {
        static size_t done = 0;
        const double secs = std::chrono::duration<double>(now - t0).count();
        size_t n = 0;
        for (const char* q = test; *q; ++n) {
            int idx = 0;
            double at = 0;
            std::sscanf(q, "%d@%lf", &idx, &at);
            if (n == done && secs >= at) want = idx, ++done;
            while (*q && *q != ',') ++q;
            if (*q) ++q;
        }
    }
    const int32_t current = reinterpret_cast<UnitCurrentWeaponFn>(b + 0xBD5AA0)(unit);
    static int target = -1, phase = 0, pressed_from = -1;
    static clock::time_point phase_until, deadline;
    constexpr uint32_t kTriangle = 0x1000;
    if (want >= 0 && want < 3) {
        const bool has = reinterpret_cast<UnitWeaponFn>(b + 0xBD5340)(unit, int16_t(want)) != -1;
        log("input: weapon %d requested (current %d%s)", want, current, has ? "" : ", none in that slot");
        if (has && want != current) target = want, phase = 0, deadline = now + std::chrono::seconds(6);
    }
    if (target >= 0) {
        if (current == target || now >= deadline) {
            if (current != target) log("input: weapon %d not reached (still %d)", target, current);
            target = -1, g_injected_buttons = 0;
        } else if (phase == 0) {  // press: a tap toggles primary / special, a hold draws the heavy
            g_injected_buttons = kTriangle;
            phase_until = now + std::chrono::milliseconds(target == 2 ? 1000 : 200);
            phase = 1;
        } else if (phase == 1 && now >= phase_until) {  // release, give the switch time to start
            g_injected_buttons = 0;
            phase_until = now + std::chrono::milliseconds(2500);  // the switch reports when done
            pressed_from = current;
            phase = 2;
        } else if (phase == 2 && (now >= phase_until || current != pressed_from)) {
            phase = 0;  // not there yet (e.g. heavy -> special goes via primary): press again
        }
    }
    if (getenv("D1_TRACE_WEAPON")) {
        static auto next = clock::now();
        if (now >= next) {
            next = now + std::chrono::milliseconds(500);
            int32_t w[4];
            for (int i = 0; i < 4; ++i) w[i] = reinterpret_cast<UnitWeaponFn>(b + 0xBD5340)(unit, int16_t(i));
            log("weapon: unit %#x current %d target %d phase %d; slots %d %d %d %d", unit, current, target, phase,
                w[0] != -1, w[1] != -1, w[2] != -1, w[3] != -1);
        }
    }
}

static D1_SYSV void player_control_hook(float dt, float f2, int32_t slot, uint32_t player, void* state,
                                        int32_t* control, float* action) {
    g_pc_orig(dt, f2, slot, player, state, control, action);
    if (player != 0 || !action) return;
    trace_cameras();
    trace_references();
    select_weapon();
    if (getenv("D1_TRACE_SPAWN")) {  // research: why the local player gets no unit
        static auto next = std::chrono::steady_clock::now();
        if (std::chrono::steady_clock::now() >= next) {
            next = std::chrono::steady_clock::now() + std::chrono::seconds(10);
            const uint64_t b = rt().modules[0].base;
            // tag handle -> data (same arithmetic as the engine's tag lookups)
            auto tag = [b](uint32_t h) -> const uint8_t* {
                if (h == 0xFFFFFFFFu) return nullptr;
                const int32_t hi = int32_t(h) >> 13;
                const uint64_t slot = uint64_t((((uint32_t(hi) >> 18) | 0x3FF) & uint32_t(hi))) * 0x40;
                const uint8_t* tbl = *reinterpret_cast<uint8_t**>(*reinterpret_cast<uint64_t*>(b + 0x1A238A0));
                const uint8_t* p = *reinterpret_cast<uint8_t* const*>(tbl + 0x10 + slot);
                const uint64_t off = uint64_t((h & 0x1FFF) * *reinterpret_cast<const int32_t*>(tbl + 0x30 + slot));
                const uint64_t mask = uint64_t(int64_t(*reinterpret_cast<const int32_t*>(tbl + 0x34 + slot))) &
                                      *reinterpret_cast<const uint64_t*>(p + 8 + off);
                return p + off - mask;
            };
            using U32Fn = D1_SYSV uint32_t (*)();
            const uint32_t t840 = reinterpret_cast<U32Fn>(b + 0x240840)();
            const uint32_t t880 = reinterpret_cast<U32Fn>(b + 0x240880)();
            const uint8_t* p840 = tag(t840);
            const uint8_t* p880 = tag(t880);
            int32_t mode = -2;
            const bool have_mode = reinterpret_cast<D1_SYSV bool (*)(int32_t*)>(b + 0x10C500)(&mode);
            auto* players = *reinterpret_cast<uint8_t**>(b + 0x273EB80);
            const int32_t datum = players ? *reinterpret_cast<int32_t*>(players + 0xC0) : -1;
            const int32_t unit = players ? *reinterpret_cast<int32_t*>(players + 0xC4) : -1;
            const bool can = datum != -1 && reinterpret_cast<D1_SYSV bool (*)(int32_t)>(b + 0x415700)(datum);
            log("spawn: player %#x unit %d can_spawn %d | mode ref %s %d | tag840 %#x (+0x1C %d) tag880 %#x (+0x1C %d)",
                datum, unit, can, have_mode ? "set" : "unset", mode, t840, p840 ? p840[0x1C] : -1, t880,
                p880 ? p880[0x1C] : -1);
            using PtrU32Fn = D1_SYSV uint64_t (*)(uint32_t);
            const bool blocked = reinterpret_cast<D1_SYSV bool (*)()>(b + 0x3D5F30)();
            const int32_t ent = g_spawn_entity.load();
            const uint64_t pinfo = ent != -1 ? reinterpret_cast<PtrU32Fn>(b + 0x1192B0)(ent) : 0;
            const uint64_t pa = ent != -1 ? reinterpret_cast<PtrU32Fn>(b + 0x3F3CE0)(ent) : 0;
            const uint64_t pb = ent != -1 ? reinterpret_cast<PtrU32Fn>(b + 0x3F3DE0)(ent) : 0;
            // first gate of 0x415700: slice-set state (0x3430B0 -> 0x3455E0 / 0x345610 -> 0x12D730)
            using U64Fn = D1_SYSV uint64_t (*)();
            using BoolU64Fn = D1_SYSV bool (*)(uint64_t);
            const uint64_t ss = reinterpret_cast<U64Fn>(b + 0x3430B0)();
            const bool ss_ok = reinterpret_cast<BoolU64Fn>(b + 0x3455E0)(ss);
            bool ss_gate = false;
            if (ss_ok) {
                const uint64_t v = reinterpret_cast<D1_SYSV uint64_t (*)(uint64_t)>(b + 0x345610)(ss);
                uint64_t tmp = v;
                ss_gate = reinterpret_cast<D1_SYSV bool (*)(uint64_t*)>(b + 0x12D730)(&tmp);
            }
            log("spawn: entity %#x slice gate %d/%d", ent, ss_ok, ss_gate);
            if (ent != -1) {
                const uint64_t arr = *reinterpret_cast<uint64_t*>(b + 0x2689588);
                const uint64_t stride = *reinterpret_cast<uint32_t*>(b + 0x2689590);
                const uint8_t* e = reinterpret_cast<const uint8_t*>(arr + (uint32_t(ent) & 0x1FFF) * stride);
                const uint32_t def = *reinterpret_cast<const uint32_t*>(e + 0x50);
                const uint8_t* d = tag(def);
                log("spawn: entity data %p +0x4C player %d +0x50 definition %#x -> %p: +0x1F8 %#x +0x208 %#x +0x318 %#x",
                    (const void*)e, *reinterpret_cast<const int32_t*>(e + 0x4C), def, (const void*)d,
                    d ? *reinterpret_cast<const uint32_t*>(d + 0x1F8) : 0, d ? *reinterpret_cast<const uint32_t*>(d + 0x208) : 0,
                    d ? *reinterpret_cast<const uint32_t*>(d + 0x318) : 0);
                {
                    // player configuration (0x912240 -> 0x73DAC0 -> player data +0x1660): needs
                    // 0x52B090, 0x549510 and player +0x613 bit 1; body tag = player +0x85C
                    const uint8_t* pl = *reinterpret_cast<uint8_t* const*>(*reinterpret_cast<uint64_t*>(b + 0x273EA80) + 8) +
                                        (*reinterpret_cast<const uint32_t*>(e + 0x4C) & 0xFFFF) * 0x2AF0;
                    const bool g1 = reinterpret_cast<D1_SYSV bool (*)()>(b + 0x52B090)();
                    const bool g2 = reinterpret_cast<D1_SYSV bool (*)()>(b + 0x549510)();
                    char hex[3 * 16 + 1] = {};
                    for (int k = 0; k < 16; ++k) std::snprintf(hex + 3 * k, 4, "%02x ", pl[0x850 + k]);
                    log("spawn: player config gates %d %d +0x613 %#x | +0x850 %s| +0x1660 %d configured %d | character %#llx", g1, g2, pl[0x613], hex,
                        *reinterpret_cast<const int32_t*>(pl + 0x1660), pl[0x2840],
                        (unsigned long long)*reinterpret_cast<const uint64_t*>(pl + 0x710));
                    {
                        // producer of the peer subscription state (0x58B570): runs unless 0x906F70;
                        // members of the investment object id from 0x587520 (*0x26BC510 entries 0x30, kind 3)
                        const bool cli = reinterpret_cast<D1_SYSV bool (*)()>(b + 0x906F70)();
                        const uint64_t grp = reinterpret_cast<D1_SYSV uint64_t (*)()>(b + 0x587520)();
                        const uint8_t* reg = *reinterpret_cast<uint8_t* const*>(b + 0x26BC510);
                        if (const uint8_t* pm = *reinterpret_cast<uint8_t* const*>(b + 0x26BC448)) {
                            char hx[3 * 0x68 + 1] = {};
                            for (int k = 0; k < 0x68; ++k) std::snprintf(hx + 3 * k, 4, "%02x ", pm[0x28 + k]);
                            log("spawn: peer members %p group %#llx count %d flags %#x | m0 %s", (const void*)pm,
                                (unsigned long long)*reinterpret_cast<const uint64_t*>(pm + 0x14),
                                *reinterpret_cast<const int32_t*>(pm + 0x20), *reinterpret_cast<const uint16_t*>(pm + 0x8a), hx);
                        }
                        log("spawn: peer subscription producer client %d group %#llx registry %p kind0 %d id0 %#llx",
                            cli, (unsigned long long)grp, (const void*)reg, reg ? reg[0] : -1,
                            reg ? (unsigned long long)*reinterpret_cast<const uint64_t*>(reg + 1) : 0ULL);
                    }
                    // roster the character data cache (0x58D940) follows: *0x26BC3C0 +0x10, 16 bytes each
                    if (const uint8_t* ro = *reinterpret_cast<uint8_t* const*>(b + 0x26BC3C0)) {
                        for (int k = 0; k < 4; ++k)
                            log("spawn: roster[%d] %#llx %#x", k, (unsigned long long)*reinterpret_cast<const uint64_t*>(ro + 0x10 + k * 16),
                                *reinterpret_cast<const uint16_t*>(ro + 0x18 + k * 16));
                    }
                }
                {
                    uint8_t* lr[4];
                    const int nl = client_references(b, 0x10, lr, 4);
                    for (int k = 0; k < nl; ++k) {
                        char hx[3 * 32 + 1] = {};
                        for (int row = 0x100; row < 0x1C0; row += 32) {
                            for (int q = 0; q < 32; ++q) std::snprintf(hx + 3 * q, 4, "%02x ", lr[k][row + q]);
                            log("spawn: lifetime ref %d %p +%#x %s", k, (void*)lr[k], row, hx);
                        }
                    }
                }
                if (d) {
                    // authority state (0x4098E0): @0x299 spawn-ready needs @0x298, published
                    // @0x250 == @0x2C8 (player byte +0x738) and 0x77B920 (state 0x7680F0 == 4)
                    const bool st4 = reinterpret_cast<D1_SYSV bool (*)()>(b + 0x77B920)();
                    log("spawn: fireteam @0x250 %d @0x2C8 %d @0x290 %#x @0x298 %d @0x299 %d state4 %d", *reinterpret_cast<const int32_t*>(d + 0x250),
                        *reinterpret_cast<const int32_t*>(d + 0x2C8), *reinterpret_cast<const uint32_t*>(d + 0x290), d[0x298], d[0x299], st4);
                }
            }
            const uint16_t ctx = *reinterpret_cast<uint16_t*>(b + 0x25D6FF8);
            int16_t refs0c = -1;
            if (ctx) {
                const uint64_t pool = *reinterpret_cast<uint64_t*>(b + 0x1AD5000);
                const uint64_t stride = *reinterpret_cast<uint32_t*>(b + 0x1AD5010);
                const uint8_t* mgr = *reinterpret_cast<uint8_t**>(b + 0x1AD5030 + ctx * stride + pool);
                if (mgr) refs0c = *reinterpret_cast<const int16_t*>(mgr + 0x2BD1E + 0xC * 4);
                // 0x1195F0 binds entity +0x50 to the type-0xC reference whose owner id (first 8
                // bytes of the object at [ref +0x208] + [ref +0x210]) equals entity +0x18
                struct Iter { const uint8_t* mgr; int16_t idx; int16_t pad; int32_t type; bool valid; uint8_t p2[7]; };
                struct Out { uint32_t handle; uint32_t pad; int64_t off; };
                using IterFn = D1_SYSV bool (*)(Iter*, Out*);
                if (mgr) {  // groups: count @+0xC, start @+0x10, key @+0x14 (stride 0x14, count @+8)
                    const int32_t ng = *reinterpret_cast<const int32_t*>(mgr + 8);
                    for (int32_t g = 0; g < ng && g < 64; ++g) {
                        const int32_t* gr = reinterpret_cast<const int32_t*>(mgr + 0xC + g * 0x14);
                        log("spawn: ref group %d count %d start %d key %#x %#x %#x", g, gr[0], gr[1], gr[2], gr[3], gr[4]);
                    }
                    const int16_t st = *reinterpret_cast<const int16_t*>(mgr + 0x2BD1C + 0xC * 4);
                    for (int16_t i = 0; i < refs0c && i < 32; ++i)
                        log("spawn: ref0c[%d] entry %d", i, *reinterpret_cast<const int16_t*>(mgr + 0x2A51C + (st + i) * 2));
                }
                for (int16_t i = 0; mgr && i < refs0c && i < 32; ++i) {
                    Iter it{mgr, i, 0, 0xC, true, {}};
                    Out o{0xFFFFFFFFu, 0, 0};
                    if (!reinterpret_cast<IterFn>(b + 0x100CB80)(&it, &o)) { log("spawn: ref0c[%d] -", i); continue; }
                    const uint8_t* obj = tag(o.handle);
                    const uint8_t* r = obj ? obj + o.off : nullptr;
                    const uint32_t inner = r ? *reinterpret_cast<const uint32_t*>(r + 0x208) : 0xFFFFFFFFu;
                    const uint8_t* io = tag(inner);
                    const uint64_t key = io ? *reinterpret_cast<const uint64_t*>(io + *reinterpret_cast<const int64_t*>(r + 0x210)) : 0;
                    if (r && i == 0) {
                        char hex[3 * 64 + 1] = {};
                        for (int row = 0x100; row < 0x2A0; row += 32) {
                            for (int k = 0; k < 32; ++k) std::snprintf(hex + 3 * k, 4, "%02x ", r[row + k]);
                            log("spawn: ref0c[0] +%#x %s", row, hex);
                        }
                    }
                    log("spawn: ref0c[%d] handle %#x off %#llx inner %#x owner field +%#llx = %#llx", i, o.handle,
                        (long long)o.off, inner, r ? (long long)*reinterpret_cast<const int64_t*>(r + 0x210) : -1LL,
                        (unsigned long long)key);
                }
            }
            if (ent != -1) {
                const uint64_t arr = *reinterpret_cast<uint64_t*>(b + 0x2689588);
                const uint64_t stride = *reinterpret_cast<uint32_t*>(b + 0x2689590);
                const uint64_t* e = reinterpret_cast<const uint64_t*>(arr + (uint32_t(ent) & 0x1FFF) * stride);
                log("spawn: entity +8 %#llx +0x10 %#llx +0x18 %#llx +0x20 %#llx +0x28 %#llx +0x30 %#llx +0x38 %#llx",
                    (unsigned long long)e[1], (unsigned long long)e[2], (unsigned long long)e[3], (unsigned long long)e[4],
                    (unsigned long long)e[5], (unsigned long long)e[6], (unsigned long long)e[7]);
            }
            log("spawn: activity/membership block %d | player info %#llx (+9 %d) data3f3ce0 %#llx data3f3de0 %#llx | type-0xC refs %d",
                blocked, (unsigned long long)pinfo, pinfo ? reinterpret_cast<const uint8_t*>(pinfo)[9] : -1,
                (unsigned long long)pa, (unsigned long long)pb, refs0c);
        }
    }
    if (getenv("D1_TRACE_FADE")) {  // research: find a held screen-fade block {count, .., mode @0x14, alpha @0x18}
        static auto next = std::chrono::steady_clock::now();
        if (std::chrono::steady_clock::now() >= next) {
            next = std::chrono::steady_clock::now() + std::chrono::seconds(10);
            const uint64_t b = rt().modules[0].base;
            int found = 0;
            for (uint64_t g = 0x2600000; g < 0x2980000 && found < 16; g += 8) {
                const uint64_t p = *reinterpret_cast<const uint64_t*>(b + g);
                if (p < 0x200000000ull || p > 0x7FFFFFFFFFFull || (p & 3)) continue;
                if (guest_region_extent(p) < 0x20) continue;
                const uint32_t* w = reinterpret_cast<const uint32_t*>(p);
                const float alpha = *reinterpret_cast<const float*>(p + 0x18);
                if (w[0] >= 1 && w[0] <= 4 && w[5] >= 1 && w[5] <= 4 && alpha > 0.0f && alpha <= 1.0f) {
                    ++found;
                    log("fade: [%#llx] -> %#llx: +0 %u +4 %#x +8 %#x +0xC %#x +0x10 %#x +0x14 %u +0x18 %.3f +0x1C %#x",
                        (unsigned long long)g, (unsigned long long)p, w[0], w[1], w[2], w[3], w[4], w[5], alpha, w[7]);
                }
            }
        }
    }
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
    const double rad_per_count = cfg.mouse_sensitivity * 0.0066 * 3.14159265358979 / 180.0;  // Destiny 2 scale
    const float yaw = float(-dx * rad_per_count * yaw_scale);
    const float pitch = float((cfg.mouse_invert ? -dy : dy) * rad_per_count * pitch_scale);  // + pitch: down (screen y)
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
    static const bool allow = getenv("D1_ALLOW_LOADING_CINE") != nullptr;  // research
    const bool r = allow ? false : g_cine_orig();
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

// ---- activity lifetime state (eboot+0x10C500): byte +0x1AC of the object behind client
// reference type 0x10 (0x1072C0). Player spawning (0x415700) only proceeds in states 3/6
// and loading task 9 (0x7965A0) waits for it. The object (class handlers 0x4044B0 bind,
// 0x4044F0 receive: +0x1AC = published byte, 0x404550 publish: authoritative byte +0x1AD)
// never gets a value: nothing in the client writes +0x1AD, so the state comes from the
// activity's script owner (the activity host). Until that is served, the spawn bypass
// reports state 3 while the game has none; D1_FORCE_LIFETIME=<n> picks another value.
using LifetimeFn = D1_SYSV bool (*)(int32_t*);
static LifetimeFn g_lifetime_orig = nullptr;
static int32_t g_force_lifetime = -1;
static D1_SYSV bool lifetime_hook(int32_t* out) {
    if (g_lifetime_orig(out)) return true;
    static bool logged = false;
    if (!logged) { logged = true; log("hooks: activity lifetime state unset; reporting %d", g_force_lifetime); }
    *out = g_force_lifetime;
    return true;
}

// ---- player spawn check (eboot+0x415700, called per player simulation entity by the
// spawning update 0x412800). D1_TRACE_SPAWN logs its calls (throttled).
using CanSpawnFn = D1_SYSV bool (*)(int32_t);
static CanSpawnFn g_can_spawn_orig = nullptr;
static bool g_trace_spawn = false;
static bool g_publish_fireteam = false;

// ---- fireteam publish (stand-in for the unidentified source of fireteam data)
// A player simulation entity's definition (+0x50) is the fireteam client reference (type 0xC,
// 16 of them, objects of content type 0x80802236) whose fireteam id (object +0x258) equals
// the fireteam id the entity was created with (+0x18, from the player's membership
// properties @0xA0; with one player it is the character id); 0x1195F0 does the binding. The fireteam data (0x808022A5, 0x78 bytes
// at object +0x218, id at +0x40) reaches the object through a content-declared data binding
// whose handler is 0x409710 (copy, rebind players, refresh); nothing in the retail
// client publishes it, and the activity host's client-reference message (7) does not reach
// these objects (no message delegate at +0x108). Until the publisher is found, the first
// free fireteam reference gets the player's fireteam id through that same handler.
static const uint8_t* tag_data(uint64_t b, uint32_t h) {
    if (h == 0xFFFFFFFFu) return nullptr;
    const int32_t hi = int32_t(h) >> 13;
    const uint64_t slot = uint64_t((((uint32_t(hi) >> 18) | 0x3FF) & uint32_t(hi))) * 0x40;
    const uint8_t* tbl = *reinterpret_cast<uint8_t**>(*reinterpret_cast<uint64_t*>(b + 0x1A238A0));
    const uint8_t* p = *reinterpret_cast<uint8_t* const*>(tbl + 0x10 + slot);
    const uint64_t off = uint64_t((h & 0x1FFF) * *reinterpret_cast<const int32_t*>(tbl + 0x30 + slot));
    const uint64_t mask = uint64_t(int64_t(*reinterpret_cast<const int32_t*>(tbl + 0x34 + slot))) &
                          *reinterpret_cast<const uint64_t*>(p + 8 + off);
    return p + off - mask;
}
// client references of a type (manager per context: registry {start, count} @+0x2BD1C per
// type, index list @+0x2A51C, entries @+0x520 x 0x38 = {u32 handle, u32, i64 offset, ...})
static int client_references(uint64_t b, int type, uint8_t** out, int max) {
    const uint16_t ctx = *reinterpret_cast<uint16_t*>(b + 0x25D6FF8);
    if (!ctx) return 0;
    const uint64_t pool = *reinterpret_cast<uint64_t*>(b + 0x1AD5000);
    const uint64_t stride = *reinterpret_cast<uint32_t*>(b + 0x1AD5010);
    const uint8_t* mgr = *reinterpret_cast<uint8_t**>(b + 0x1AD5030 + ctx * stride + pool);
    if (!mgr) return 0;
    const int16_t start = *reinterpret_cast<const int16_t*>(mgr + 0x2BD1C + type * 4);
    const int16_t count = *reinterpret_cast<const int16_t*>(mgr + 0x2BD1E + type * 4);
    int n = 0;
    for (int16_t i = 0; i < count && n < max; ++i) {
        const int16_t e = *reinterpret_cast<const int16_t*>(mgr + 0x2A51C + (start + i) * 2);
        if (e < 0) continue;
        const uint8_t* ent = mgr + 0x520 + e * 0x38;
        const uint32_t h = *reinterpret_cast<const uint32_t*>(ent);
        const uint8_t* obj = tag_data(b, h);
        if (obj) out[n++] = const_cast<uint8_t*>(obj + *reinterpret_cast<const int64_t*>(ent + 8));
    }
    return n;
}
// D1_TRACE_REFS=<secs> (research): once, <secs> after player control starts, log every client
// reference type's count and its first entries (tag handle, object offset, first bytes).
static void trace_references() {
    static const char* v = getenv("D1_TRACE_REFS");
    static bool done = false;
    if (!v || done) return;
    static const auto start = std::chrono::steady_clock::now();
    if (std::chrono::steady_clock::now() - start < std::chrono::seconds(atoi(v))) return;
    done = true;
    const uint64_t b = rt().modules[0].base;
    // registered world cinematics (*0x26AFEF0: count @+0x1350, entries @+0x1320 + 0x38 i;
    // 0x4E3D50 matches a play request's id against 0x354400(entry))
    if (!*reinterpret_cast<uint8_t* const*>(b + 0x26AFEF0)) log("cinematics: no table");
    if (const uint8_t* cb = *reinterpret_cast<uint8_t* const*>(b + 0x26AFEF0)) {
        const int32_t n = *reinterpret_cast<const int32_t*>(cb + 0x1350);
        log("cinematics: table %p count %d", (const void*)cb, n);
        using IdFn = D1_SYSV void (*)(int32_t*, const uint64_t*);
        const auto id_of = reinterpret_cast<IdFn>(b + 0x354400);
        for (int32_t i = 0; i < n && i < 64; ++i) {
            const uint8_t* e = cb + 0x1320 + 0x38 * i;
            const uint32_t h50 = *reinterpret_cast<const uint32_t*>(e + 0x50);
            const uint32_t h58 = *reinterpret_cast<const uint32_t*>(e + 0x58);
            uint64_t arg[5] = {};
            arg[0] = reinterpret_cast<uint64_t>(tag_data(b, h50));
            const uint8_t* t58 = tag_data(b, h58);
            arg[1] = t58 ? reinterpret_cast<uint64_t>(t58) + *reinterpret_cast<const uint64_t*>(e + 0x60) : 0;
            arg[2] = *reinterpret_cast<const uint64_t*>(e + 0x58);
            arg[3] = *reinterpret_cast<const uint64_t*>(e + 0x60);
            arg[4] = *reinterpret_cast<const uint32_t*>(e + 0x68);
            int32_t id[2] = {-1, -1};
            if (arg[0] && arg[1]) id_of(id, arg);
            log("cinematics: [%d] id %08x tag %08x obj %08x+%llx", i, id[0], h50, h58,
                (unsigned long long)*reinterpret_cast<const uint64_t*>(e + 0x60));
        }
    }
    // simulation queue element definitions (*0x2689508)[type]: vtable of each (research)
    if (const uint64_t* defs = *reinterpret_cast<uint64_t* const*>(b + 0x2689508)) {
        for (int t = 0; t < 0x80; ++t) {
            const uint64_t d = defs[t];
            if (d && d > b && d < b + 0x4000000)
                log("simq: element %#x def +%#llx vtable +%#llx", t, (unsigned long long)(d - b),
                    (unsigned long long)(*reinterpret_cast<const uint64_t*>(d) - b));
            else if (d) log("simq: element %#x def %#llx", t, (unsigned long long)d);
        }
    }
    const uint16_t ctx = *reinterpret_cast<uint16_t*>(b + 0x25D6FF8);
    if (!ctx) { log("refs: no context"); return; }
    const uint64_t pool = *reinterpret_cast<uint64_t*>(b + 0x1AD5000);
    const uint64_t stride = *reinterpret_cast<uint32_t*>(b + 0x1AD5010);
    const uint8_t* mgr = *reinterpret_cast<uint8_t**>(b + 0x1AD5030 + ctx * stride + pool);
    if (!mgr) { log("refs: no manager"); return; }
    // groups (0x1071D0): count at int [2], records of 5 ints from int [5]: key at [0], start at [4]
    const int32_t* gi = reinterpret_cast<const int32_t*>(mgr);
    for (int g = 0; g < gi[2] && g < 64; ++g) {
        const int32_t* r = gi + 5 + g * 5;
        log("refs: group %d key %08x %08x %08x %08x start %d", g, r[0], r[1], r[2], r[3], r[4]);
    }
    for (int type = 0; type < 64; ++type) {
        const int16_t start_i = *reinterpret_cast<const int16_t*>(mgr + 0x2BD1C + type * 4);
        const int16_t count = *reinterpret_cast<const int16_t*>(mgr + 0x2BD1E + type * 4);
        if (count <= 0) continue;
        char line[1024];
        int n = std::snprintf(line, sizeof line, "refs: type %#x count %d:", type, count);
        for (int16_t i = 0; i < count && n < 900; ++i) {
            const int16_t e = *reinterpret_cast<const int16_t*>(mgr + 0x2A51C + (start_i + i) * 2);
            if (e < 0) continue;
            const uint8_t* ent = mgr + 0x520 + e * 0x38;
            n += std::snprintf(line + n, sizeof line - n, " [%d]%08x", e, *reinterpret_cast<const uint32_t*>(ent));
        }
        log("%s", line);
        // first bound entry: the object's message delegate block at +0x108 (0x29D7E0 / 0x353340)
        for (int16_t i = 0; i < count; ++i) {
            const int16_t e = *reinterpret_cast<const int16_t*>(mgr + 0x2A51C + (start_i + i) * 2);
            if (e < 0) continue;
            const uint8_t* ent = mgr + 0x520 + e * 0x38;
            const uint32_t h = *reinterpret_cast<const uint32_t*>(ent);
            if (h == 0xFFFFFFFFu) continue;
            const uint8_t* obj = tag_data(b, h);
            if (!obj) break;
            obj += *reinterpret_cast<const int64_t*>(ent + 8);
            const uint32_t* d = reinterpret_cast<const uint32_t*>(obj + 0x108);
            log("refs:   type %#x [%d] obj %p delegate %08x %08x %08x %08x %08x %08x %08x %08x", type, e, (const void*)obj,
                d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7]);
            break;
        }
    }
}

// "Join" on a friend, as the PS4 system software does it: read the sessions the friend is in
// (PSN sessionInvitation GET /v1/users/<id>/sessions) and send the game a session invitation
// event (0x10000002; parameter: session id char[45] @0, invitation id @0x30, flags @0x70 with
// bit 0 = from an invitation, online id @0x78). The game (0x295460 -> event 0x24 -> 0x2B4270
// -> 0x2B4600) then reads the session's data from PSN and joins through the join manager.
static bool join_friend(const std::string& friend_id) {
    BackendReply rep;
    const std::vector<std::pair<std::string, std::string>> headers = {
        {"Authorization", "Bearer d1b-D1NATIVE-" + settings().name}};
    if (!backend_http("GET", "sessionInvitation.np.playstation.net",
                      "/npwebapi/sessionInvitation/v1/users/" + friend_id + "/sessions", headers, nullptr, 0, rep) ||
        rep.status != 200) {
        log("join: cannot read %s's sessions (status %d)", friend_id.c_str(), rep.status);
        return false;
    }
    const auto k = rep.body.find("\"sessionId\":\"");
    if (k == std::string::npos) {
        log("join: %s is not in a session", friend_id.c_str());
        return false;
    }
    const auto v = k + 13;
    const std::string sid = rep.body.substr(v, rep.body.find('"', v) - v);
    uint8_t param[0x8C] = {};
    std::memcpy(param, sid.data(), std::min<size_t>(sid.size(), 44));
    std::memcpy(param + 0x78, friend_id.data(), std::min<size_t>(friend_id.size(), 16));
    log("join: joining %s's session %s", friend_id.c_str(), sid.c_str());
    push_system_event(0x10000002, param, sizeof param);
    return true;
}

// Called once per game frame (the game polls sceSystemServiceGetStatus every frame, in every
// state: boot, orbit, world).
static void dump_activity_vtables() {
    static const bool on = getenv("D1_DUMP_ACTIVITIES") != nullptr;
    static bool done = false;
    if (!on || done) return;
    const uint64_t b = rt().modules[0].base;
    const uint64_t g = *reinterpret_cast<const uint64_t*>(b + 0x26527E8);  // content globals
    const uint64_t a = *reinterpret_cast<const uint64_t*>(b + 0x26527E0);
    if (!g || !a) return;
    done = true;
    const uint64_t* gv = *reinterpret_cast<uint64_t* const*>(g);
    const uint64_t* av = *reinterpret_cast<uint64_t* const*>(a);
    log("activities: content globals %#llx vtable +0x320 %s +0x328 %s", (unsigned long long)g,
        describe_addr(gv[0x320 / 8]).c_str(), describe_addr(gv[0x328 / 8]).c_str());
    log("activities: 0x26527E0 %#llx vtable +0x28 %s +0x68 %s", (unsigned long long)a, describe_addr(av[0x28 / 8]).c_str(),
        describe_addr(av[0x68 / 8]).c_str());
    // activity definitions (0x25A6E0): block = vtable +0x38 (count @0, relptr @8 -> 16-byte
    // entries, relptr @+8 -> definition)
    using BlockFn = D1_SYSV const uint8_t* (*)(uint64_t);
    const uint8_t* blk = reinterpret_cast<BlockFn>(gv[0x38 / 8])(g);
    const int64_t count = *reinterpret_cast<const int64_t*>(blk);
    log("activities: %lld definitions (block %p)", (long long)count, blk);
    const char* want = getenv("D1_DUMP_ACTIVITIES");
    const int dump_idx = atoi(want);
    for (int64_t i = 0; i < count; ++i) {
        const uint8_t* arr = blk + 0x18 + *reinterpret_cast<const int64_t*>(blk + 8);
        const uint8_t* e = arr + i * 0x10;
        const int64_t rel = *reinterpret_cast<const int64_t*>(e + 8);
        if (!rel) continue;
        const uint8_t* d = e + 8 + rel;
        if (i == dump_idx) {
            for (int o = 0; o < 0x200; o += 32) {
                char line[200];
                int k = std::snprintf(line, sizeof line, "activities: [%lld] +%03x", (long long)i, o);
                for (int w = 0; w < 32; w += 4) k += std::snprintf(line + k, sizeof line - k, " %08x", *reinterpret_cast<const uint32_t*>(d + o + w));
                log("%s", line);
            }
        }
        // relative fields: string candidates
        std::string names;
        for (int o : {0x20, 0x28, 0x48, 0x50, 0x58, 0x98}) {
            const int64_t r = *reinterpret_cast<const int64_t*>(d + o);
            if (r <= 0 || r > 0x1000000) continue;
            const char* str = reinterpret_cast<const char*>(d + o + r);
            int n = 0;
            while (n < 64 && str[n] >= 0x20 && str[n] < 0x7f) ++n;
            if (n >= 3 && str[n] == 0) names += " +" + std::to_string(o) + "='" + std::string(str, n) + "'";
        }
        log("activities: [%lld] hash %08x tag %08x mm %08x%s", (long long)i, *reinterpret_cast<const uint32_t*>(d),
            *reinterpret_cast<const uint32_t*>(d + 0x88), *reinterpret_cast<const uint32_t*>(d + 0xa4), names.c_str());
    }
}

// D1_LAUNCH_ACTIVITY=<index>[:<secs>] (research): from orbit, launch an activity the way the
// game's own handlers do (the prologue handler 0x7A1470 case 4): write the activity selection
// {u8 1, i16 activity index @2, u8 tier @4 (0xFF), ...} into the activity-selection manager
// (0x574DC0(*0x26BC068, &selection)) and request world-controller state 0x19 (cleanup,
// 0x783ED0), which moves on to activity session creation. World-controller states are indices
// into the name table at 0x165AA27 (0x1B setup:orbit, 0x24 activity:in_world); the current one
// is *(*0x26CA078 + 0x1B0).
static std::atomic<bool> g_launch_key{false}, g_join_key{false};
void hooks_request_launch() {
    g_launch_key = true;
    log("keys: F9, launch requested (runs once in orbit)");
}
void hooks_request_join() {
    g_join_key = true;
    log("keys: F10, join requested (runs once a friend is listed and we are in orbit or the world)");
}

// D1_DUMP_PREREQS=1 (research): once in orbit, run the world transition's purchase
// prerequisite check (0x5505C0(activity index) -> -1 or the failing requirement) for every
// activity and log the ones that fail; with D1_TRACE_UNLOCK the expressions show up too.
// Activity permission (0x2648D0(provider, activity, &a, &b, &c); 0x547EF0 needs a and b, or
// c when b alone is not enough). a is the activity's availability (0x2680A0: definition +0x8C
// through the availability provider *0x26527D8, vtable +0x40; 7 = unavailable), b and c its
// requirement lists (0x267BC0 / 0x2679E0). The Director's lock state and the world transition
// both use it. D1_BYPASS=activities (research / test characters) passes every activity;
// D1_TRACE_PERMISSION=1 logs each check.
using PermFn = D1_SYSV void (*)(void*, uint32_t, uint8_t*, uint8_t*, uint8_t*);
static PermFn g_perm_orig = nullptr;
static bool g_perm_bypass = false;
static D1_SYSV void perm_hook(void* prov, uint32_t act, uint8_t* a, uint8_t* b, uint8_t* c) {
    g_perm_orig(prov, act, a, b, c);
    static const bool trace = getenv("D1_TRACE_PERMISSION") != nullptr;
    if (trace) log("permission: activity %u -> %d %d %d%s", act, *a, *b, *c, g_perm_bypass ? " (bypassed)" : "");
    if (g_perm_bypass) *a = *b = *c = 1;
}

// Matchmaking composition check (0xB0C6D0(settings, session properties) -> 0x12 success, else
// a reason: 0xB too many parties, 0xC "big-party-count-exceeds-teams" when properties +0x14
// exceed settings +0xC4, ...). D1_TRACE_COMPOSITION=1 (research) logs each failure.
using CompFn = D1_SYSV int32_t (*)(const uint8_t*, const uint8_t*);
static CompFn g_comp_orig = nullptr;
static bool g_comp_bypass = false;  // D1_BYPASS=activities: 0xC (settings +0xC4 unset, e.g. the Tower) passes
static D1_SYSV int32_t comp_hook(const uint8_t* st, const uint8_t* pr) {
    int32_t r = g_comp_orig(st, pr);
    if (g_comp_bypass && r == 0xC) r = 0x12;
    static const bool trace = getenv("D1_TRACE_COMPOSITION") != nullptr;
    if (trace && r != 0x12 && st && pr)
        log("composition: %d (settings +0x9C %d +0xA0 %d +0xC4 %d; properties +0x14 %d +0x28 %d +0x16C %d)", r,
            *reinterpret_cast<const int32_t*>(st + 0x9C), *reinterpret_cast<const int32_t*>(st + 0xA0),
            *reinterpret_cast<const int32_t*>(st + 0xC4), *reinterpret_cast<const int32_t*>(pr + 0x14),
            *reinterpret_cast<const int32_t*>(pr + 0x28), *reinterpret_cast<const int32_t*>(pr + 0x16C));
    return r;
}

// Investment object lookup (0x56DC00(manager, context, type, &id) -> object or 0; replaced,
// same logic): per (context, type) a table at manager +0x4FD90 + context*0x60 + type*0x10
// {u32 storage offset, i16 count, i32 stride} into manager +0x40A0. D1_TRACE_LOOKUP=<type>
// (research) logs lookups of that type (3 = inventory item) once per (context, id).
static int g_trace_lookup_type = -1;
static D1_SYSV const uint8_t* lookup_replacement(uint8_t* mgr, int32_t ctx, int32_t type, const int64_t* id) {
    const uint8_t* t = mgr + int64_t(ctx) * 0x60 + int64_t(type) * 0x10 + 0x4FD90;
    const uint32_t off = *reinterpret_cast<const uint32_t*>(t);
    const uint8_t* found = nullptr;
    int16_t count = 0;
    if (off != 0xFFFFFFFF) {
        count = *reinterpret_cast<const int16_t*>(t + 4);
        const int32_t stride = *reinterpret_cast<const int32_t*>(t + 8);
        const uint8_t* p = mgr + 0x40A0 + off;
        for (int i = 0; i < count; ++i, p += stride)
            if (*reinterpret_cast<const int64_t*>(p) == *id) { found = p; break; }
    }
    if (type == g_trace_lookup_type) {
        static std::mutex m;
        static std::set<std::pair<int, int64_t>> seen;
        std::lock_guard lk(m);
        if (seen.insert({ctx, *id}).second)
            log("lookup: type %d context %d id %llx -> %s (table %s, %d objects) <- %s", type, ctx, (long long)*id,
                found ? "found" : "missing", off == 0xFFFFFFFF ? "none" : "set", count,
                describe_addr(reinterpret_cast<uint64_t>(__builtin_return_address(0))).c_str());
    }
    return found;
}

// Can-equip check (0x269A50(flags, values, equipped ids, item provider, item, &why) -> bool):
// needs the item's definition loaded (definitions vtable +0x410), its equipment slot open and
// its requirements met; `why` collects reasons (1 no definition/slot, 0x20/0x40 unlock lists,
// 8 values, 2 slot conflict, 4 final unlock). D1_TRACE_EQUIP=1 (research) logs each item.
using EquipFn = D1_SYSV bool (*)(void*, void*, void*, void*, const uint8_t*, uint8_t*);
static EquipFn g_equip_orig = nullptr;
static D1_SYSV bool equip_hook(void* a, void* b, void* c, void* d, const uint8_t* item, uint8_t* why) {
    uint8_t local = 0;
    const bool r = g_equip_orig(a, b, c, d, item, why ? why : &local);
    static std::mutex m;
    static std::map<std::pair<int64_t, int>, int> seen;
    std::lock_guard lk(m);
    const int64_t id = item ? *reinterpret_cast<const int64_t*>(item) : 0;
    const int index = item ? *reinterpret_cast<const int16_t*>(item + 0x24) : -1;
    const int w = why ? *why : local;
    auto [it, fresh] = seen.try_emplace({id, r}, w);
    if (fresh) log("equip: item %llx (index %d) -> %d, reasons %#x", (long long)id, index, int(r), w);
    return r;
}

static std::atomic<int> g_prereq_activity{-1};  // set while prereq_dump runs a check
static void prereq_dump(uint64_t b) {
    static bool done = false;
    if (done || !getenv("D1_DUMP_PREREQS")) return;
    done = true;
    using PrereqFn = D1_SYSV int32_t (*)(int32_t);
    auto check = reinterpret_cast<PrereqFn>(b + 0x5505C0);
    int fails = 0;
    std::string line;
    for (int i = 0; i < 653; ++i) {
        g_prereq_activity = i;
        const int32_t r = check(i);
        g_prereq_activity = -1;
        if (r == -1) continue;
        ++fails;
        char buf[32];
        std::snprintf(buf, sizeof buf, " %d:%x", i, r);
        line += buf;
    }
    log("prereq: %d of 653 activities fail their purchase prerequisites:%s", fails, line.c_str());
}

static void launch_tick() {
    static const char* spec = getenv("D1_LAUNCH_ACTIVITY");
    static bool done = false;
    static std::chrono::steady_clock::time_point since{};
    const bool key = g_launch_key.load();
    if ((!spec || done) && !key && !getenv("D1_DUMP_PREREQS")) return;
    const uint64_t b = rt().modules[0].base;
    const uint64_t st = *reinterpret_cast<const uint64_t*>(b + 0x26CA078);
    if (!st || *reinterpret_cast<const int32_t*>(st + 0x1B0) != 0x1B) {
        since = {};
        return;
    }
    prereq_dump(b);
    if ((!spec || done) && !key) return;
    int index;
    if (key) {  // F9: now (Earth patrol unless D1_KEY_ACTIVITY names another index)
        g_launch_key = false;
        const char* k = getenv("D1_KEY_ACTIVITY");
        index = k ? atoi(k) : 93;
    } else {
        const auto now = std::chrono::steady_clock::now();
        if (since == std::chrono::steady_clock::time_point{}) since = now;
        const char* colon = strchr(spec, ':');
        const int wait = colon ? atoi(colon + 1) : 5;
        if (now - since < std::chrono::seconds(wait)) return;
        done = true;
        index = atoi(spec);
    }
    alignas(8) uint8_t sel[0x8C] = {};
    sel[0] = 1;
    *reinterpret_cast<int16_t*>(sel + 2) = int16_t(index);
    sel[4] = 0xFF;
    using SelFn = D1_SYSV void (*)(void*, const void*);
    using MgrFn = D1_SYSV void* (*)();
    using StateFn = D1_SYSV void (*)(int32_t);
    void* mgr = reinterpret_cast<MgrFn>(b + 0x574EF0)();
    log("launch: activity index %d from orbit (selection manager %p)", index, mgr);
    reinterpret_cast<SelFn>(b + 0x574DC0)(mgr, sel);
    reinterpret_cast<StateFn>(b + 0x783ED0)(0x19);
}

// D1_TRACE_PLAYERS (research): every 15 s, the machine ids (02:D1:..) found in the game's
// player records (*(*0x273EA80 + 8), 0x2AF0 each), i.e. which players this client simulates.
static void trace_players() {
    static const bool on = getenv("D1_TRACE_PLAYERS") != nullptr;
    if (!on) return;
    static auto next = std::chrono::steady_clock::now();
    const auto now = std::chrono::steady_clock::now();
    if (now < next) return;
    next = now + std::chrono::seconds(15);
    const uint64_t b = rt().modules[0].base;
    const uint64_t pm = *reinterpret_cast<const uint64_t*>(b + 0x273EA80);
    if (!pm) return;
    const uint8_t* players = *reinterpret_cast<uint8_t* const*>(pm + 8);
    if (!players) return;
    std::string out;
    for (int i = 0; i < 16; ++i) {
        const uint8_t* r = players + size_t(i) * 0x2AF0;
        for (int o = 0; o + 8 <= 0x2AF0; o += 8) {
            if (r[o] == 0x02 && r[o + 1] == 0xD1 && r[o + 6] == 0 && r[o + 7] == 0 && (r[o + 2] | r[o + 3] | r[o + 4] | r[o + 5])) {
                char buf[64];
                std::snprintf(buf, sizeof buf, " [%d]+%#x=%02x%02x%02x%02x", i, o, r[o + 2], r[o + 3], r[o + 4], r[o + 5]);
                out += buf;
                break;
            }
        }
    }
    log("players:%s", out.empty() ? " none" : out.c_str());
    // handle-looking fields of each record (u32, low 16 bits 0x2000..0x2FFF, high 16 not 0
    // or 0xFFFF): where a player record points at its entities (unit, ...)
    for (int i = 0; i < 4; ++i) {
        const uint8_t* r = players + size_t(i) * 0x2AF0;
        std::string h;
        for (int o = 0; o + 4 <= 0x2AF0; o += 4) {
            const uint32_t v = *reinterpret_cast<const uint32_t*>(r + o);
            if ((v & 0xF000) == 0x2000 && (v >> 16) != 0 && (v >> 16) != 0xFFFF) {
                char buf[32]; std::snprintf(buf, sizeof buf, " +%#x=%08x", o, v); h += buf;
            }
        }
        if (!h.empty()) {
            // +0x850: configuration (race, gender, class, ..., body tag @+0x85C); +0x1660 the
            // resolved configuration (-1 = none: the player cannot spawn)
            char cfg[64] = {};
            for (int k = 0; k < 16; ++k) std::snprintf(cfg + 3 * k, 4, "%02x ", r[0x850 + k]);
            log("players: record %d handles%s | config %s| +0x1660 %d", i, h.c_str(), cfg, *reinterpret_cast<const int32_t*>(r + 0x1660));
        }
    }

    // Player updates (0xBB6080 → 0xBA6760): the simulation (*0x2801518, role @+8; 1 = client)
    // diffs its tracked players (P = *sim: mask @+0x10, generation @+0xC) against the activity
    // session's membership (session = 0x75F130(*(Q + 0x12A78 + i*0x18258 + 0x10)), Q = *P,
    // i = *(Q + 0x5B180); state @+0x8C48 must be 4..9; generation @+0x6330; membership @+0x620,
    // simulated mask @+0x1C54, identity @+0x1C5C + slot*0xE8).
    const uint64_t sim = *reinterpret_cast<const uint64_t*>(b + 0x2801518);
    if (!sim) return;
    const uint64_t P = *reinterpret_cast<const uint64_t*>(sim);
    const uint64_t Q = P ? *reinterpret_cast<const uint64_t*>(P) : 0;
    const int role = *reinterpret_cast<const int*>(sim + 8);
    // 0xB9FAC0 only produces player updates while *0x28A5410 and 0x906E00() (object *0x273DCD0:
    // +0x2B48 set, +0 clear → +1) hold.
    // Simulation peers: the session's list (*0x273DCD0: mask @+0x20, 20 ids @+0x24), copied by
    // 0x906750 → 0x913A90 into the global list (*0x273EA90: mask @+4, ids @+8), which a
    // simulation tracker reset (0xBA6470) snapshots into its known peers.
    if (const uint8_t* g = *reinterpret_cast<uint8_t* const*>(b + 0x273DCD0)) {
        std::string peers;
        auto list = [&](const char* name, const uint8_t* at, uint32_t mask) {
            peers += name;
            for (int k = 0; k < 20; ++k)
                if (mask >> k & 1) {
                    char buf[24];
                    uint64_t v; std::memcpy(&v, at + k * 8, 8);
                    std::snprintf(buf, sizeof buf, " %llx", (unsigned long long)v);
                    peers += buf;
                }
        };
        uint32_t m1; std::memcpy(&m1, g + 0x20, 4);
        list(" session:", g + 0x24, m1);
        if (const uint8_t* gl = *reinterpret_cast<uint8_t* const*>(b + 0x273EA90)) {
            uint32_t m2; std::memcpy(&m2, gl + 4, 4);
            list(" global:", gl + 8, m2);
        }
        log("players: producer gate %d, sim object [0]=%d [1]=%d [0x2b48]=%d;%s", *reinterpret_cast<const uint8_t*>(b + 0x28A5410), g[0], g[1], g[0x2B48], peers.c_str());
    }
    if (!Q) { log("players: sim role %d, no tracker", role); return; }
    const int idx = *reinterpret_cast<const int*>(Q + 0x5B180);
    uint64_t sess = 0;
    if (idx != -1) {
        // the simulation session entry's peer list (mask @+0x4C, ids @+0x5C, dirty @+0xFC):
        // what 0xBA6510 publishes as simulation message 0xD
        const uint64_t e = Q + 0x12A78 + uint64_t(idx) * 0x18258;
        std::string el;
        const uint32_t em = *reinterpret_cast<const uint32_t*>(e + 0x4C);
        for (int k = 0; k < 20; ++k)
            if (em >> k & 1) {
                char buf[24];
                std::snprintf(buf, sizeof buf, " %llx", (unsigned long long)*reinterpret_cast<const uint64_t*>(e + 0x5C + k * 8));
                el += buf;
            }
        log("players: sim entry peers%s dirty %d; tracker host list mask %#x", el.c_str(), *reinterpret_cast<const uint8_t*>(e + 0xFC),
            *reinterpret_cast<const uint32_t*>(P + 0x12DC));
        // Simulation views, one per remote machine (list *(e + 0x38), 19 slots @+0x118; view:
        // alive @+0x44, machine @+0x54, peer @+0x5C, channel @+0x68 (set once the channel is
        // connected, 0xBB31D0), error @+0x70, local state @+0x74 / id @+0x78, remote state
        // @+0x84, replicating @+0xA4 (0xBB3280), @+0xB2)
        if (const uint64_t L = *reinterpret_cast<const uint64_t*>(e + 0x38)) {
            std::string vs;
            for (int k = 0; k < 19; ++k) {
                const uint8_t* v = *reinterpret_cast<uint8_t* const*>(L + 0x118 + k * 8);
                if (!v || !v[0x44]) continue;
                char buf[160];
                std::snprintf(buf, sizeof buf, " [%llx peer %d ch %d err %d state %d/%d remote %d repl %d/%d b2 %d]",
                              (unsigned long long)*reinterpret_cast<const uint64_t*>(v + 0x54), *reinterpret_cast<const int*>(v + 0x5C),
                              *reinterpret_cast<const uint64_t*>(v + 0x68) != 0, *reinterpret_cast<const int*>(v + 0x70),
                              *reinterpret_cast<const int*>(v + 0x74), *reinterpret_cast<const int*>(v + 0x78),
                              *reinterpret_cast<const int*>(v + 0x84), v[0xA4], v[0xA5], v[0xB2]);
                vs += buf;
            }
            log("players: views%s", vs.empty() ? " none" : vs.c_str());
        }
        // Entity database (e + 0x1B0, 0xB53BB0 / 0xB5A220): per index i a 6-byte record @+0xB4
        // (i16 entity record, u8 counters @+0xB6/+0xB7, u8 state @+0xB8), locally owned mask
        // @+0x120B8. Count live entities per 256-index slice of the client range
        // (8192..12287), '*' marking owned slices.
        {
            const uint64_t db = e + 0x1B0;
            std::string cs;
            // an index's entity: i16 @+0xB4 (record in the entity table at 0x28832D8, -1 none)
            auto live = [db](int i) { const int16_t r = *reinterpret_cast<const int16_t*>(db + 0xB4 + uint64_t(i) * 6); return r > 0; };
            for (int s = 0; s < 16; ++s) {
                int used = 0;
                for (int i = 8192 + s * 256; i < 8192 + (s + 1) * 256; ++i)
                    if (live(i)) ++used;
                const uint32_t own = *reinterpret_cast<const uint32_t*>(db + 0x120B8 + uint64_t((8192 + s * 256) >> 5) * 4);
                if (used || own) { char buf[24]; std::snprintf(buf, sizeof buf, " %d:%d%s", s, used, own ? "*" : ""); cs += buf; }
            }
            int low = 0;
            for (int i = 0; i < 8192; ++i)
                if (live(i)) ++low;
            // entities held for other machines (not owned): index, and the start of their
            // record in the replication entity table (0x28832D8, 0x80 each: +0 view, +1 state,
            // +4 type?, +8 handle)
            std::string remote;
            for (int i = 8192; i < 12288; ++i) {
                if (!live(i)) continue;
                const uint32_t own = *reinterpret_cast<const uint32_t*>(db + 0x120B8 + uint64_t(i >> 5) * 4);
                if (own >> (i & 31) & 1) continue;
                const int16_t r = *reinterpret_cast<const int16_t*>(db + 0xB4 + uint64_t(i) * 6);
                const uint8_t* rec = reinterpret_cast<const uint8_t*>(b + 0x28832D8 + uint64_t(r) * 0x80);
                char buf[96];
                std::snprintf(buf, sizeof buf, " %d:[%02x %02x %08x %08x %08x]", i, rec[0], rec[1], *reinterpret_cast<const uint32_t*>(rec + 4),
                              *reinterpret_cast<const uint32_t*>(rec + 8), *reinterpret_cast<const uint32_t*>(rec + 12));
                remote += buf;
            }
            if (!remote.empty()) log("players: remote entities%s", remote.c_str());
            // per-view replication objects the database feeds (0xB5A220 -> 0xB5EBA0: view index
            // @+0xC, database @+0x10, entities queued for creation @+0x28)
            std::string dv;
            for (int k = 0; k < 19; ++k)
                if (const uint8_t* rv = *reinterpret_cast<uint8_t* const*>(db + 0x18 + k * 8)) {
                    char buf[96];  // the writer (0xB5C530) only runs with +9 and +0xA set
                    std::snprintf(buf, sizeof buf, " %d:(view %d flags %d/%d/%d queued %d/%d/%d/%d)", k, *reinterpret_cast<const int*>(rv + 0xC),
                                  rv[8], rv[9], rv[10], *reinterpret_cast<const int*>(rv + 0x28), *reinterpret_cast<const int*>(rv + 0x2C),
                                  *reinterpret_cast<const int*>(rv + 0x30), *reinterpret_cast<const int*>(rv + 0x34));
                    dv += buf;
                }
            log("players: entities host range %d, client slices%s; database views%s", low, cs.c_str(), dv.empty() ? " none" : dv.c_str());
        }
        using SessFn = D1_SYSV uint64_t (*)(uint64_t);
        sess = reinterpret_cast<SessFn>(b + 0x75F130)(*reinterpret_cast<const uint64_t*>(Q + 0x12A78 + uint64_t(idx) * 0x18258 + 0x10));
    }
    const uint32_t tmask = *reinterpret_cast<const uint32_t*>(P + 0x10);
    const int tgen = *reinterpret_cast<const int*>(P + 0xC);
    if (!sess) { log("players: sim role %d idx %d, no session; tracked mask %#x gen %d", role, idx, tmask, tgen); return; }
    const uint64_t m = sess + 0x620;
    std::string ids;
    const uint32_t smask = *reinterpret_cast<const uint32_t*>(m + 0x1C54);
    for (int i = 0; i < 20; ++i)
        if (smask >> i & 1) {
            const uint64_t s = m + uint64_t(i) * 0xE8;  // +0x1CE0 account soid, +0x1CE8 character
            // 0x75F210 (fireteam_from_player): the fireteam session's member entry for this
            // identity, value @+0xA0 of its data; the diff needs it found and not 0/-1.
            using FtFn = D1_SYSV bool (*)(const void*, int64_t*);
            int64_t ft = -2;
            const bool found = reinterpret_cast<FtFn>(b + 0x75F210)(reinterpret_cast<const void*>(s + 0x1C5C), &ft);
            char buf[128];
            std::snprintf(buf, sizeof buf, " %d:%016llx soid %llx char %llx ft %d/%lld", i, (unsigned long long)*reinterpret_cast<const uint64_t*>(s + 0x1C5C),
                          (unsigned long long)*reinterpret_cast<const uint64_t*>(s + 0x1CE0), (unsigned long long)*reinterpret_cast<const uint64_t*>(s + 0x1CE8),
                          found, (long long)ft);
            ids += buf;
        }
    // slot peer index @+0x1C64, @+0x1C74 (must not be -1); peers (mask @+0x2C, state @+0x5C +
    // p*0x168, id @+0x54 + p*0x168); the tracker's known peers: 20 u64 @P+0x123C
    for (int i = 0; i < 20; ++i)
        if (smask >> i & 1) {
            const uint64_t s = m + uint64_t(i) * 0xE8;
            char buf[64];
            std::snprintf(buf, sizeof buf, " s%d:peer %d x %d", i, *reinterpret_cast<const int*>(s + 0x1C64), *reinterpret_cast<const int*>(s + 0x1C74));
            ids += buf;
        }
    const uint32_t pmask = *reinterpret_cast<const uint32_t*>(m + 0x2C);
    for (int p = 0; p < 20; ++p)
        if (pmask >> p & 1) {
            char buf[64];
            std::snprintf(buf, sizeof buf, " p%d:%llx st %d", p, (unsigned long long)*reinterpret_cast<const uint64_t*>(m + 0x54 + uint64_t(p) * 0x168),
                          *reinterpret_cast<const int*>(m + 0x5C + uint64_t(p) * 0x168));
            ids += buf;
        }
    ids += " known:";
    for (int k = 0; k < 20; ++k) {
        const uint64_t v = *reinterpret_cast<const uint64_t*>(P + 0x123C + uint64_t(k) * 8);
        if (v) { char buf[24]; std::snprintf(buf, sizeof buf, " %llx", (unsigned long long)v); ids += buf; }
    }
    for (int i = 0; i < 20; ++i)
        if (tmask >> i & 1) {  // tracker slot: id @+0x18, pending flag @+0x20, @+0x28, @+0x34
            const uint64_t t = P + uint64_t(i) * 0xE8;
            char buf[96];
            std::snprintf(buf, sizeof buf, " t%d:%016llx flag %d %llx %d", i, (unsigned long long)*reinterpret_cast<const uint64_t*>(t + 0x18),
                          *reinterpret_cast<const uint8_t*>(t + 0x20), (unsigned long long)*reinterpret_cast<const uint64_t*>(t + 0x28),
                          *reinterpret_cast<const int*>(t + 0x34));
            ids += buf;
        }
    {
        using IntFn = D1_SYSV int (*)();
        using PtrFn = D1_SYSV uint64_t (*)();
        const uint64_t ftsess = reinterpret_cast<PtrFn>(b + 0x75D330)();
        log("players: mode %d fireteam slot %d session %#llx established %d", reinterpret_cast<IntFn>(b + 0x78F6B0)(),
            reinterpret_cast<IntFn>(b + 0x75D200)(), (unsigned long long)ftsess,
            ftsess ? *reinterpret_cast<const uint8_t*>(ftsess + 0x131) & 1 : -1);
    }
    log("players: sim role %d idx %d session state %u gen %d members %#x simulated %#x%s; tracked mask %#x gen %d",
        role, idx, *reinterpret_cast<const uint32_t*>(sess + 0x8C48), *reinterpret_cast<const int*>(sess + 0x6330),
        *reinterpret_cast<const uint32_t*>(m + 0x2C), smask, ids.c_str(), tmask, tgen);
}

void hooks_system_tick() {
    roster_tick();
    trace_players();
    launch_tick();
    dump_activity_vtables();
}

// Investment roster (*0x26BC448: count @+0x20, 0x68-byte records from +0x30; a record starts
// with the player's 0x30-byte roster identity, compared by 0x2B82D0). D1_TRACE_ROSTER (research)
// dumps it every 10 s in the world; D1_JOIN_TEST=<secs> joins the first record that is not the
// local player, <secs> after player control: as the system software's "Join" (join_friend), or
// with D1_JOIN_VIA=roster as the in-game roster's join command (0x579EA0, which the contact
// widget's join action 0xA2DC20 uses).
static void roster_tick() {
    static const bool trace = getenv("D1_TRACE_ROSTER") != nullptr;
    static const int env_join_after = getenv("D1_JOIN_TEST") ? atoi(getenv("D1_JOIN_TEST")) : -1;
    static bool key_pending = false;  // F10: join as soon as possible (again, if need be)
    if (g_join_key.exchange(false)) key_pending = true;
    const int join_after = key_pending ? 0 : env_join_after;
    if (!trace && join_after < 0) return;
    static auto next = std::chrono::steady_clock::now();
    static std::chrono::steady_clock::time_point start{};  // the friend first in the roster
    static bool joined = false;
    const auto now = std::chrono::steady_clock::now();
    const uint64_t b = rt().modules[0].base;
    const uint8_t* r = *reinterpret_cast<uint8_t* const*>(b + 0x26BC448);
    if (!r) return;
    const int32_t n = *reinterpret_cast<const int32_t*>(r + 0x20);
    // the timer starts once the friend is listed and we are in orbit (0x1B) or in the world
    // (0x24): a join that arrives while loading is dropped (0x57A260, message 0x26BC328)
    const uint64_t wc = *reinterpret_cast<const uint64_t*>(b + 0x26CA078);
    const int32_t wstate = wc ? *reinterpret_cast<const int32_t*>(wc + 0x1B0) : -1;
    if (n > 1 && (wstate == 0x1B || wstate == 0x24) && start == std::chrono::steady_clock::time_point{}) start = now;
    if (trace && now >= next) {
        next = now + std::chrono::seconds(10);
        using JoinMgrFn = D1_SYSV uint64_t (*)();
        const uint32_t* jm = reinterpret_cast<const uint32_t*>(reinterpret_cast<JoinMgrFn>(b + 0x57A220)());
        if (jm) log("join manager: state %u flags %08x target soid %08x%08x | %08x %08x %08x %08x", jm[0], jm[1], jm[3], jm[2],
                    jm[0x24], jm[0x25], jm[0x26], jm[0x27]);
        // platform join (*0x266D6A0: +0x27D done, +0x27E joinable, +0x27F busy, +0x312 request;
        // join store 0x266D5E9 pending)
        if (const uint8_t* ps = *reinterpret_cast<uint8_t* const*>(b + 0x266D6A0))
            log("platform join: done %d joinable %d busy %d request %d | store pending %d", ps[0x27D], ps[0x27E], ps[0x27F],
                ps[0x312], *reinterpret_cast<const uint8_t*>(b + 0x266D5E9));
        log("roster: %d records", n);
        for (int32_t i = 0; i < n && i < 16; ++i) {
            const uint32_t* q = reinterpret_cast<const uint32_t*>(r + 0x30 + 0x68 * i);
            char line[400];
            int k = std::snprintf(line, sizeof line, "roster: [%d]", i);
            for (int w = 0; w < 26 && k < 380; ++w) k += std::snprintf(line + k, sizeof line - k, " %08x", q[w]);
            log("%s", line);
        }
    }
    if (join_after >= 0 && (!joined || key_pending) && n > 1 && start != std::chrono::steady_clock::time_point{} &&
        now - start > std::chrono::seconds(join_after)) {
        joined = true;
        key_pending = false;
        // the first record whose name (record +0, up to '@') is not ours
        const std::string me = settings().name;
        for (int32_t i = 0; i < n; ++i) {
            const char* name = reinterpret_cast<const char*>(r + 0x30 + 0x68 * i);
            std::string nm(name, strnlen(name, 32));
            nm = nm.substr(0, nm.find('@'));
            if (nm == me) continue;
            if (const char* via = getenv("D1_JOIN_VIA"); via && !strcmp(via, "roster")) {
                // the in-game roster's join (0x579EA0): element 0x24 {identity[0x30], u8 1,
                // u8 0, u64 0}, payload type *0x2918220. From inside an activity the join
                // check refuses it (bit 0x100000) unless the join came from the system.
                log("join test: joining roster record %d (%s) via the roster", i, nm.c_str());
                alignas(16) uint8_t el[0x40] = {};
                std::memcpy(el, r + 0x30 + 0x68 * i, 0x30);
                el[0x30] = 1;
                using InsertFn = D1_SYSV bool (*)(int32_t, uint32_t, const void*);
                const uint32_t ty = *reinterpret_cast<const uint32_t*>(b + 0x2918220);
                const bool ok = reinterpret_cast<InsertFn>(b + 0x300230)(0x24, ty, el);
                log("join test: queue insert (type %#x) -> %d", ty, ok);
            } else {
                join_friend(nm);
            }
            break;
        }
    }
}

// Join manager "target not joinable" report (0x57B160(manager, &reason bits)): log the bits
// the joinability check (0x955EF0) returned (research, with D1_JOIN_TEST).
using JoinReasonFn = D1_SYSV void (*)(void*, const uint32_t*);
static JoinReasonFn g_join_reason_orig = nullptr;
static D1_SYSV void join_reason_hook(void* mgr, const uint32_t* bits) {
    const uint64_t b = rt().modules[0].base;
    // Local inputs of the checks: 0x8000 = *(*0x26BC068 + 300); 0x80000/0x100000 =
    // *(*0x26CA078 + 0x1B0) in 0x1C..0x23 / >= 0x24 unless (*0x281D300)[0] or [1].
    const uint64_t jm = *reinterpret_cast<const uint64_t*>(b + 0x26BC068);
    const uint64_t st = *reinterpret_cast<const uint64_t*>(b + 0x26CA078);
    const uint64_t fl = *reinterpret_cast<const uint64_t*>(b + 0x281D300);
    log("join: target not joinable, reason bits %#x (local: +300 %d, state %d, flags %d %d)", bits ? *bits : 0,
        jm ? *reinterpret_cast<const uint8_t*>(jm + 300) : -1, st ? *reinterpret_cast<const int32_t*>(st + 0x1B0) : -1,
        fl ? *reinterpret_cast<const uint8_t*>(fl) : -1, fl ? *reinterpret_cast<const uint8_t*>(fl + 1) : -1);
    g_join_reason_orig(mgr, bits);
}

// Character progression state check (0x28CFB0(component, index) = table[index] == 2, the
// table from 0x2601F0); the activity-selection component's "no joining" flag (+300 of
// *0x26BC068, from 0x546F20) uses the index at game globals +0x192. Logged per (index, result)
// change with D1_JOIN_TEST.
using ProgressFn = D1_SYSV bool (*)(void*, uint16_t);
static ProgressFn g_progress_orig = nullptr;
static D1_SYSV bool progress_hook(void* c, uint16_t idx) {
    const bool r = g_progress_orig(c, idx);
    static std::mutex m;
    static std::map<uint16_t, int> seen;
    std::lock_guard lk(m);
    auto [it, fresh] = seen.try_emplace(idx, r);
    if (fresh || it->second != int(r)) {
        it->second = r;
        log("progress: state[%u] == 2 -> %d (component %p) <- %s", idx, r, c,
            describe_addr(reinterpret_cast<uint64_t>(__builtin_return_address(0))).c_str());
    }
    return r;
}

// Unlock expressions (0x28E590(component, expression) -> bool): a stack program over ops
// {u8 kind, u32 operand @+4}, 8 bytes each, at expression+8 + *(expression+8) + 0x10, count
// at expression+0: 1 push flag (0x28CFE0), 10 push unlock value (0x28D160 on component
// +0x2000), 11 push constant, 2 not, 0x15 negate, 3.. binary ops. D1_TRACE_UNLOCK=1
// (research) logs each distinct expression's ops and every change of its result.
using UnlockFn = D1_SYSV uint64_t (*)(void*, const int64_t*);
static UnlockFn g_unlock_orig = nullptr;
static D1_SYSV uint64_t unlock_hook(void* c, const int64_t* expr) {
    const uint64_t r = g_unlock_orig(c, expr);
    if (const int a = g_prereq_activity.load(); a >= 0 && !(r & 1)) {
        std::string ops;
        const int64_t n = expr[0];
        const uint8_t* base = reinterpret_cast<const uint8_t*>(expr + 1) + expr[1] + 0x10;
        for (int64_t i = 0; i < n && i < 24; ++i) {
            char buf[32];
            std::snprintf(buf, sizeof buf, " %u:%u", base[i * 8], *reinterpret_cast<const uint32_t*>(base + i * 8 + 4));
            ops += buf;
        }
        log("prereq: activity %d fails [%s ]", a, ops.c_str());
    }
    static std::mutex m;
    static std::map<const void*, int> seen;
    std::lock_guard lk(m);
    auto [it, fresh] = seen.try_emplace(expr, int(r & 1));
    if (fresh || it->second != int(r & 1)) {
        it->second = int(r & 1);
        std::string ops;
        const int64_t n = expr[0];
        const uint8_t* base = reinterpret_cast<const uint8_t*>(expr + 1) + expr[1] + 0x10;
        for (int64_t i = 0; i < n && i < 24; ++i) {
            char buf[32];
            std::snprintf(buf, sizeof buf, " %u:%u", base[i * 8], *reinterpret_cast<const uint32_t*>(base + i * 8 + 4));
            ops += buf;
        }
        // callers: the guest keeps frame pointers, so walk a few frames up from ours
        std::string callers = describe_addr(reinterpret_cast<uint64_t>(__builtin_return_address(0)));
        const uint64_t* fp = static_cast<const uint64_t*>(__builtin_frame_address(0));
        for (int k = 0; k < 4 && fp; ++k) {
            const uint64_t* next = reinterpret_cast<const uint64_t*>(fp[0]);
            // a frame chain only goes up the same stack: stop at anything else
            if (next <= fp || reinterpret_cast<uint64_t>(next) - reinterpret_cast<uint64_t>(fp) > (1u << 20)) break;
            fp = next;
            callers += " < " + describe_addr(fp[1]);
        }
        log("unlock: expr %p ->%d [%s ] <- %s", (const void*)expr, int(r & 1), ops.c_str(), callers.c_str());
    }
    return r;
}

// Director activity state (0x264360(component, activity unlock list) -> state): the list is
// {i64 count @+0x18, relative array @+0x20} of 0x18-byte entries {i8 state @+0, unlock
// expression @+8}; scanned from the last entry, the first true expression gives the state
// (none: 0). The director (0x58FD40) shows a node at state 3 and up (4: newly available).
// D1_TRACE_DIRECTOR=1 (research) logs each list, its entries and every change of its state.
static std::string expr_ops(const int64_t* expr) {
    std::string ops;
    const int64_t n = expr[0];
    const uint8_t* base = reinterpret_cast<const uint8_t*>(expr + 1) + expr[1] + 0x10;
    for (int64_t i = 0; i < n && i < 24; ++i) {
        char buf[32];
        std::snprintf(buf, sizeof buf, " %u:%u", base[i * 8], *reinterpret_cast<const uint32_t*>(base + i * 8 + 4));
        ops += buf;
    }
    return ops;
}
using ActivityStateFn = D1_SYSV int32_t (*)(void*, const uint8_t*);
static ActivityStateFn g_activity_state_orig = nullptr;
// Where each unlock flag is stored (research, D1_TRACE_DIRECTOR): the definitions manager
// (0x25A550) lists, per storage scope, the master flag index of each stored slot. Vtable +0x290:
// profile flags (scope 4, profile +0x383C, 3100), +0x298: more profile flags (scope 3, +0x5430), +0x2A0: character flags (scope 7, slot i = character +0x53C0 + i),
// both {i32 count, i64 relative array @+8} of 8-byte entries {.. i16 master index @+0x14}
// (as read by 0x28BC60). Logged once as "flagscope: <scope> <slot> <master>".
static void dump_flag_scopes() {
    using GetFn = D1_SYSV void* (*)();
    using ListFn = D1_SYSV const int32_t* (*)(void*);
    void* defs = reinterpret_cast<GetFn>(rt().modules[0].base + 0x25A550)();
    if (!defs) return;
    const auto vt = *reinterpret_cast<const uint64_t* const*>(defs);
    log("flagscope: definitions manager %p vtable %s", defs, describe_addr(reinterpret_cast<uint64_t>(vt)).c_str());
    for (auto [scope, off] : {std::pair{4, 0x290}, std::pair{3, 0x298}, std::pair{7, 0x2A0}}) {
        const int32_t* lst = reinterpret_cast<ListFn>(vt[off / 8])(defs);
        if (!lst) continue;
        const auto* base = reinterpret_cast<const uint8_t*>(lst) + 8 + *reinterpret_cast<const int64_t*>(lst + 2);
        std::string line;
        for (int32_t i = 0; i < lst[0]; ++i) {
            line += " " + std::to_string(*reinterpret_cast<const int16_t*>(base + i * 8 + 0x14));
            if (line.size() > 900 || i + 1 == lst[0]) {
                log("flagscope: %d up to slot %d:%s", scope, i, line.c_str());
                line.clear();
            }
        }
    }
    // inventory item definitions (0x549570: {i32 count, i64 relative array @+8} of 16-byte
    // rows; 0x54D110 reads the u32 at +8 as the item's gear resource): "items: <index> <row>"
    using TableFn = D1_SYSV const int32_t* (*)();
    if (const int32_t* it = reinterpret_cast<TableFn>(rt().modules[0].base + 0x549570)()) {
        const auto* rows = reinterpret_cast<const uint8_t*>(it) + 8 + *reinterpret_cast<const int64_t*>(it + 2) + 0x10;
        log("items: %d definitions", it[0]);
        std::string line;
        for (int32_t i = 0; i < it[0]; ++i) {
            char buf[64];
            const auto* r = reinterpret_cast<const uint32_t*>(rows + i * 16);
            std::snprintf(buf, sizeof buf, " %d:%08x.%08x.%08x.%08x", i, r[0], r[1], r[2], r[3]);
            line += buf;
            if (line.size() > 900 || i + 1 == it[0]) {
                log("items:%s", line.c_str());
                line.clear();
            }
        }
    }
    // equipment slots (vtable +0x100: {i32 count, i64 relative array}): the character's
    // equipped item ids (member 5, +0x2B80) are in this order
    {
        using ListFn = D1_SYSV const int32_t* (*)(void*);
        if (const int32_t* e = reinterpret_cast<ListFn>(vt[0x100 / 8])(defs)) {
            const auto* a = reinterpret_cast<const uint8_t*>(e) + 8 + *reinterpret_cast<const int64_t*>(e + 2) + 0x10;
            // rows of 0x38: {u32 bucket hash, u8, u8 item slot code @+5 (definition +0x88), ...}
            std::string codes;
            for (int k = 0; k < e[0]; ++k) {
                char buf[24];
                std::snprintf(buf, sizeof buf, " %d:%08x/%u", k, *reinterpret_cast<const uint32_t*>(a + k * 0x38), a[k * 0x38 + 5]);
                codes += buf;
            }
            log("equipment: %d slots (index:bucket/item slot code):%s", e[0], codes.c_str());
        }
    }
    // item definitions by index (vtable +0x410): D1_ITEM_PEEK=<i>,<j>,... logs the first 64 bytes
    if (const char* pk = getenv("D1_ITEM_PEEK")) {
        using DefFn = D1_SYSV const uint8_t* (*)(void*, uint32_t);
        for (const char* p = pk; *p;) {
            const int i = atoi(p);
            const uint8_t* d = reinterpret_cast<DefFn>(vt[0x410 / 8])(defs, uint32_t(i));
            std::string hex;
            for (int k = 0; d && k < 64; k += 4) {
                char buf[16];
                std::snprintf(buf, sizeof buf, " %08x", *reinterpret_cast<const uint32_t*>(d + k));
                hex += buf;
            }
            using TblFn = D1_SYSV const int32_t* (*)(void*);
            const int32_t* t = reinterpret_cast<TblFn>(vt[0x168 / 8])(defs);
            const auto* row = t && i < t[0] ? reinterpret_cast<const uint32_t*>(reinterpret_cast<const uint8_t*>(t) + 8 +
                                                 *reinterpret_cast<const int64_t*>(t + 2) + 0x10 + i * 0x18) : nullptr;
            log("items: definition %d at %p:%s (map row: hash %08x file %08x)", i, (const void*)d, hex.c_str(),
                row ? row[0] : 0, row ? row[4] : 0);
            while (*p && *p != ',') ++p;
            if (*p) ++p;
        }
    }
    // scope 12: {i64 count, i64 relative array @+8} of 16-byte {i16 flag, i16 state, i64
    // threshold @+8}: flag = state once the character's value reaches the threshold
    using List64Fn = D1_SYSV const int64_t* (*)(void*);
    if (const int64_t* t = reinterpret_cast<List64Fn>(vt[0x2B0 / 8])(defs)) {
        const auto* e = reinterpret_cast<const uint8_t*>(t + 1) + t[1] + 0x10;
        std::string line;
        for (int64_t i = 0; i < t[0]; ++i) {
            char buf[48];
            std::snprintf(buf, sizeof buf, " %d=%d@%lld", *reinterpret_cast<const int16_t*>(e + i * 16),
                          *reinterpret_cast<const int16_t*>(e + i * 16 + 2), (long long)*reinterpret_cast<const int64_t*>(e + i * 16 + 8));
            line += buf;
            if (line.size() > 900 || i + 1 == t[0]) {
                log("flagscope: 12 up to entry %lld:%s", (long long)i, line.c_str());
                line.clear();
            }
        }
    }
}

// The time the scheduled flags (scope 12) are compared against (0x265100(context, character)
// -> character +0x3E88 when +0x3E80 is set, else context +8; replaced, same logic). Logged
// on change.
static D1_SYSV const int64_t* flag_time_hook(const uint8_t* ctx, const uint8_t* ch) {
    const auto* r = reinterpret_cast<const int64_t*>(ch && ch[0x3E80] ? ch + 0x3E88 : ctx + 8);  // the original
    static std::atomic<int64_t> last{-1};
    if (r && last.exchange(*r) != *r)
        log("flagtime: %lld from %s (context %p vtable %s, +0x10 %llx, character %p)", (long long)*r,
            ch && ch[0x3E80] ? "character +0x3E88" : "context +8", (const void*)ctx,
            describe_addr(*reinterpret_cast<const uint64_t*>(ctx)).c_str(),
            (unsigned long long)*reinterpret_cast<const uint64_t*>(ctx + 0x10), (const void*)ch);
    return r;
}

// Unlock flag sources (0x28BC60(..., scope @arg10, owner @arg11, flags @arg12, ok @arg13)):
// the client fills three arrays (scopes 12/11, scope 10, scopes 9..0) and merges them,
// first non-zero wins (0x28E0C0). D1_WATCH_FLAGS=<i>,<j>,... (research) logs which scope
// writes each watched flag and the value.
using FlagApplyFn = D1_SYSV void (*)(void*, void*, void*, void*, void*, void*, void*, void*, void*, int32_t,
                                     char, uint8_t*, uint8_t*);
static FlagApplyFn g_flag_apply_orig = nullptr;
static std::vector<int> g_watch_flags;
static D1_SYSV void flag_apply_hook(void* a1, void* a2, void* a3, void* a4, void* a5, void* a6, void* a7, void* a8,
                                    void* a9, int32_t scope, char owner, uint8_t* flags, uint8_t* ok) {
    uint8_t before[16] = {};
    for (size_t i = 0; i < g_watch_flags.size() && i < 16; ++i) before[i] = flags[g_watch_flags[i]];
    g_flag_apply_orig(a1, a2, a3, a4, a5, a6, a7, a8, a9, scope, owner, flags, ok);
    static std::mutex m;
    static std::map<std::pair<int, int>, int> seen;
    std::lock_guard lk(m);
    for (size_t i = 0; i < g_watch_flags.size() && i < 16; ++i) {
        const int f = g_watch_flags[i], v = flags[f];
        if (v == before[i]) continue;
        auto [it, fresh] = seen.try_emplace({f, scope}, v);
        if (fresh || it->second != v) {
            it->second = v;
            log("flagsource: flag %d = %d by scope %d (owner %d)", f, v, scope, int(owner));
        }
    }
}

static bool g_director_unlock = false;  // D1_BYPASS=activities: locked nodes (2) show as available (3)
static D1_SYSV int32_t activity_state_hook(void* c, const uint8_t* list) {
    static const bool trace = getenv("D1_TRACE_DIRECTOR") != nullptr;
    if (trace) {
        static std::once_flag scopes;
        std::call_once(scopes, dump_flag_scopes);
    }
    int32_t r = g_activity_state_orig(c, list);
    if (g_director_unlock && r == 2) r = 3;
    if (!trace) return r;
    static std::mutex m;
    static std::map<const void*, int> seen;
    std::lock_guard lk(m);
    auto [it, fresh] = seen.try_emplace(list, r);
    if (fresh || it->second != r) {
        it->second = r;
        std::string entries;
        const int64_t n = *reinterpret_cast<const int64_t*>(list + 0x18);
        const uint8_t* arr = list + 0x20 + *reinterpret_cast<const int64_t*>(list + 0x20) + 0x10;
        for (int64_t i = 0; i < n && i < 12; ++i) {
            const uint8_t* e = arr + i * 0x18;
            const auto* expr = reinterpret_cast<const int64_t*>(e + 8);
            entries += " {" + std::to_string(int(int8_t(e[0]))) + ":" + expr_ops(expr) + "}";
        }
        log("director: activity %p state %d (%lld entries)%s <- %s", (const void*)list, r, (long long)n, entries.c_str(),
            describe_addr(reinterpret_cast<uint64_t>(__builtin_return_address(0))).c_str());
    }
    return r;
}

// UI error / notification (0x950620(ui, &message id, ?, ?)): the join manager reports
// failures this way (message ids DAT_026BC300..0x26BC31C). Logged with D1_JOIN_TEST.
using UiNotifyFn = D1_SYSV void (*)(void*, const uint32_t*, uint32_t, uint32_t);
static UiNotifyFn g_ui_notify_orig = nullptr;
static D1_SYSV void ui_notify_hook(void* ui, const uint32_t* msg, uint32_t a, uint32_t c) {
    const uint64_t b = rt().modules[0].base;
    int which = -1;
    for (int i = 0; i <= 0x3C; i += 4)
        if (msg && *msg == *reinterpret_cast<const uint32_t*>(b + 0x26BC300 + i)) which = 0x26BC300 + i;
    log("ui notify: message %08x (%s%x) %u %u <- %s", msg ? *msg : 0, which >= 0 ? "join manager DAT_" : "",
        which >= 0 ? which : 0, a, c, describe_addr(reinterpret_cast<uint64_t>(__builtin_return_address(0))).c_str());
    g_ui_notify_orig(ui, msg, a, c);
}

static void publish_fireteam(int32_t entity) {
    const uint64_t b = rt().modules[0].base;
    const uint64_t arr = *reinterpret_cast<uint64_t*>(b + 0x2689588);
    const uint64_t stride = *reinterpret_cast<uint32_t*>(b + 0x2689590);
    const uint8_t* e = reinterpret_cast<const uint8_t*>(arr + (uint32_t(entity) & 0x1FFF) * stride);
    if (*reinterpret_cast<const int32_t*>(e + 0x50) != -1) return;
    const uint64_t id = *reinterpret_cast<const uint64_t*>(e + 0x18);
    if (!id) return;
    uint8_t* refs[32];
    const int n = client_references(b, 0xC, refs, 32);
    uint8_t* free_ref = nullptr;
    for (int i = 0; i < n; ++i) {
        const uint64_t owner = *reinterpret_cast<const uint64_t*>(refs[i] + 0x258);
        if (owner == id) return;  // published; binding happens in the handler
        if (!owner && !free_ref) free_ref = refs[i];
    }
    if (!free_ref) return;
    alignas(16) uint8_t data[0x78] = {};
    // @0 0x80800540 {i32, u32, bool, bool @9, bool, i8, i8}: the spawn check (0x415700)
    // requires @9 (read through the binding at object +0x1F8)
    data[9] = 1;
    // @0x10 0x80802619, its i32 @0x28: the authority state (0x4098E0) only becomes
    // spawn-ready while it equals the player's byte at player data +0x738 (players at
    // *(0x273EA80)+8, 0x2AF0 each; entity +0x4C low 16 bits = player index)
    const uint8_t* players = *reinterpret_cast<uint8_t* const*>(*reinterpret_cast<uint64_t*>(b + 0x273EA80) + 8);
    const int32_t team = int8_t(players[0x738 + (*reinterpret_cast<const uint32_t*>(e + 0x4C) & 0xFFFF) * 0x2AF0]);
    std::memcpy(data + 0x38, &team, 4);
    std::memcpy(data + 0x40, &id, 8);
    struct Typed { uint32_t type; uint32_t pad; const void* data; } v{
        **reinterpret_cast<uint32_t**>(b + 0x19B2AD8), 0, data};  // 0x808022A5
    reinterpret_cast<D1_SYSV void (*)(uint8_t*, Typed*)>(b + 0x409710)(free_ref, &v);
    log("hooks: fireteam %#llx published to fireteam reference %p; player entity %#x definition now %#x",
        (unsigned long long)id, (void*)free_ref, entity, *reinterpret_cast<const int32_t*>(e + 0x50));
}

static D1_SYSV bool can_spawn_hook(int32_t entity) {
    g_spawn_entity = entity;
    if (g_publish_fireteam) publish_fireteam(entity);
    const bool r = g_can_spawn_orig(entity);
    if (g_trace_spawn) {  // each entity's first check and every change of its result
        static std::mutex m;
        static std::map<int32_t, bool> last;
        std::lock_guard<std::mutex> lock(m);
        const auto it = last.find(entity);
        if (it == last.end() || it->second != r) {
            last[entity] = r;
            log("spawn: check entity %#x -> %d", entity, r);
        }
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

// D1_TRACE_GLYPHS=1 (research): 20 s into activity:in_world, log how button prompts resolve.
// Text variables naming a button ({f2:<hash>} parts of a localized string) go through
// 0x94B0F0(&hash, &out): variable -> action -> the controller layout's button (0x748FE0,
// 0x745650) -> one of 21 glyph name hashes (0x2744880..0x27448DC, set by 0x94C350) -> an
// entry of the glyph table tag (0xAC5E40, global 0x279D158) for the current language
// (0x8D5220(tag, &hash, 0x752A40())). out = {u32 variable, u32, entry pointer @+8}.
static void hexdump(const char* what, const void* p, int n) {
    if (!p) { log("glyph: %s: null", what); return; }
    std::string hex;
    for (int i = 0; i < n; ++i) {
        char buf[4];
        std::snprintf(buf, sizeof buf, "%02x ", static_cast<const uint8_t*>(p)[i]);
        hex += buf;
    }
    log("glyph: %s @%p: %s", what, p, hex.c_str());
}
static void trace_glyphs(int st) {
    static const bool on = getenv("D1_TRACE_GLYPHS") != nullptr;
    static std::chrono::steady_clock::time_point since{};
    static bool done = false;
    if (!on || done) return;
    if (st != 0x24) { since = {}; return; }
    const auto now = std::chrono::steady_clock::now();
    if (since == std::chrono::steady_clock::time_point{}) since = now;
    if (now - since < std::chrono::seconds(20)) return;
    done = true;
    const uint64_t b = rt().modules[0].base;
    using TagFn = D1_SYSV const uint8_t* (*)();
    const uint8_t* tag = reinterpret_cast<TagFn>(b + 0xAC5E40)();
    hexdump("glyph table tag", tag, 0x60);
    const int lang = reinterpret_cast<D1_SYSV int (*)()>(b + 0x752A40)();
    log("glyph: language %d", lang);
    using FindFn = D1_SYSV const uint8_t* (*)(const uint8_t*, const uint32_t*, int);
    for (int i = 0; tag && i < 26; ++i) {
        const uint32_t h = *reinterpret_cast<const uint32_t*>(b + 0x2744880 + 4 * i);
        const uint8_t* e = reinterpret_cast<FindFn>(b + 0x8D5220)(tag, &h, lang);
        char what[64];
        std::snprintf(what, sizeof what, "glyph %#x (hash %08x)", 0x2744880 + 4 * i, h);
        hexdump(what, e, 0x30);
    }
    using ResolveFn = D1_SYSV bool (*)(const uint32_t*, uint32_t*);
    for (uint32_t v : {0xEABFE990u, 0xBE22697Bu, 0xCED69A4Eu, 0xCC517DBEu, 0x8FEB4850u, 0x9CD0EF5Eu, 0x6FEBE322u}) {
        alignas(8) uint32_t out[4] = {};
        const bool ok = reinterpret_cast<ResolveFn>(b + 0x94B0F0)(&v, out);
        char what[64];
        std::snprintf(what, sizeof what, "variable %08x -> %d", v, int(ok));
        hexdump(what, ok ? reinterpret_cast<const void*>(*reinterpret_cast<uint64_t*>(out + 2)) : nullptr, 0x30);
    }
}

// ---- PC button prompts: key names in place of the controller's button glyphs
// Every piece of UI text is built from localized string parts (0x20 bytes: +0x08 relative
// pointer to the bytes, +0x14 u16 byte count, +0x16 u16 character count, +0x18 u16 cipher
// shift added to every character, +0x1B flags: bit 2 = UTF-8 source, bits 0-1 = part kind,
// 2 = variable). A string's parts become text runs (0x8DA9D0): 0x8DA760(chars) allocates a
// run (0x50 bytes: +0x30 pool, +0x38 UTF-16 buffer of chars + 1, +0x40 i32 length) and
// 0x8D5530(part, buffer, chars + 1) decodes the part into it. Button glyphs are private-use
// characters U+E000..U+E021 the UI font draws as DualShock 4 buttons, each in a part of its
// own (one cipher shift per part): inline in the text, or substituted for a button variable
// (0x94B0F0 above: the 21 glyph strings of tag 0x80AA949E / English 0x80AB0EE2). Cross is
// U+E020 U+E000 (a backdrop glyph, then the button), circle E001, square E002, triangle
// E003, touch pad E021 E005, R2 E006, L2 E007, L1 E008, R1 E009, R3 E010, L3 E012, D-pad
// up E013 / right E014 / down E015 / left E016, Options E017.
// d1-native reimplements 0x8D5530 (same decode) and, while the keyboard and mouse are in
// use, replaces a glyph-only part with the bound key's name ("E"), growing the run it was
// allocated for (0x8DA760 hook remembers the last run per thread); backdrop glyphs become a
// space (never an empty run).
using RunAllocFn = D1_SYSV uint8_t* (*)(int64_t chars);
static RunAllocFn g_run_alloc_orig = nullptr;
static thread_local uint8_t* t_last_run = nullptr;
static D1_SYSV uint8_t* run_alloc_hook(int64_t chars) {
    uint8_t* run = g_run_alloc_orig(chars);
    t_last_run = run;
    return run;
}
static bool is_glyph(uint16_t c) { return c >= 0xE000 && c <= 0xE021; }
static bool is_backdrop(uint16_t c) { return c == 0xE020 || c == 0xE021; }
static D1_SYSV void string_part_decode(const uint8_t* part, uint16_t* out, int64_t cap) {
    uint16_t* const start = out;
    const int64_t rel = *reinterpret_cast<const int64_t*>(part + 8);
    const uint8_t* src = rel ? part + 8 + rel : nullptr;
    const uint16_t bytes = *reinterpret_cast<const uint16_t*>(part + 0x14);
    const uint16_t shift = *reinterpret_cast<const uint16_t*>(part + 0x18);
    if (!(part[0x1B] & 4)) {  // UTF-16 source: `bytes` units, at most cap - 1
        for (int64_t i = 0; bytes && cap != 1 && i < bytes && i < cap - 1; ++i)
            *out++ = uint16_t(shift + reinterpret_cast<const uint16_t*>(src)[i]);
    } else if (bytes && cap != 1) {  // UTF-8 source (as the game decodes it: 16-bit result)
        uint16_t* const last = start + cap - 1;
        const uint8_t* end = src + bytes;
        do {
            const uint8_t b = *src;
            uint16_t c = b;
            int n = 1;
            if (b & 0x80) {
                if ((b & 0xE0) == 0xC0) c = b & 0x1F, n = 2;
                else if ((b & 0xF0) == 0xE0) c = b & 0x0F, n = 3;
                else if ((b & 0xF8) == 0xF0) c = b & 7, n = 4;
                else c = 0, n = 0;  // a stray continuation byte: the game writes 0 and stays put
                for (int k = 1; k < n; ++k) c = uint16_t(c << 6 | (src[k] & 0x3F));
            }
            *out++ = uint16_t(c + shift);
            src += n;
        } while (src != end && out != last);
    }
    *out = 0;
    // glyph-only part?
    const int64_t len = out - start;
    static const bool trace = getenv("D1_TRACE_PROMPTS") != nullptr;
    if (trace) {  // research: every part with a private-use character
        static std::atomic<int> traced{0};
        bool any = false;
        for (int64_t i = 0; i < len; ++i) any |= start[i] >= 0xE000 && start[i] < 0xF900;
        if (any && traced.fetch_add(1) < 80) {
            std::string hex;
            for (int64_t i = 0; i < len && i < 24; ++i) {
                char buf[8];
                std::snprintf(buf, sizeof buf, start[i] < 0x80 && start[i] >= 0x20 ? "%c" : "<%04x>", start[i]);
                hex += buf;
            }
            log("prompt: part shift %04x flags %02x: %s", shift, part[0x1B], hex.c_str());
        }
    }
    if (len == 0 || !render::keyboard_prompts()) return;
    uint32_t button = 0;
    for (int64_t i = 0; i < len; ++i) {
        if (!is_glyph(start[i])) return;
        if (!is_backdrop(start[i]) && !button) button = start[i];
    }
    if (!button) {
        // a backdrop part (U+E020 / U+E021 drawn under Cross..Triangle / the touch pad): a
        // space in place. An empty run is not an option: a text with an empty run is dropped
        // whole (the title's "press to start", the orbit bar, 2026-10-17 test-12).
        for (int64_t i = 0; i < len; ++i) start[i] = u' ';
        return;
    }
    char16_t label[32];
    const int n = render::prompt_label(button, label, 32);
    if (n <= 0) return;  // a button with no key bound: keep the glyph
    uint8_t* run = t_last_run;
    static std::atomic<int> traced{0};
    if (trace && traced.fetch_add(1) < 60) {
        std::string l;
        for (int i = 0; i < n; ++i) l += char(label[i]);
        log("prompt: glyph %04x (%lld chars) -> '%s'%s", button, (long long)len, l.c_str(),
            run && *reinterpret_cast<uint16_t**>(run + 0x38) == start ? " (run resized)" : "");
    }
    static const bool noresize = getenv("D1_PROMPT_NORESIZE") != nullptr;  // research
    if (!noresize && run && *reinterpret_cast<uint16_t**>(run + 0x38) == start) {
        const uint64_t b = rt().modules[0].base;
        using PoolAllocFn = D1_SYSV uint16_t* (*)(void* pool, int64_t size, int64_t align);
        using PoolFreeFn = D1_SYSV void (*)(void* const* pool, void* ptr);  // 0x8DD4C0: frees ptr (if any) from *pool
        uint16_t* buf = start;
        if (n > *reinterpret_cast<int32_t*>(run + 0x40)) {
            void* pool = *reinterpret_cast<void**>(run + 0x30);
            buf = reinterpret_cast<PoolAllocFn>(b + 0x8D9820)(pool, int64_t(n) * 2 + 2, 2);
            if (!buf) return;
            *reinterpret_cast<uint16_t**>(run + 0x38) = buf;
            reinterpret_cast<PoolFreeFn>(b + 0x8DD4C0)(&pool, start);
        }
        for (int i = 0; i < n; ++i) buf[i] = uint16_t(label[i]);
        buf[n] = 0;
        *reinterpret_cast<int32_t*>(run + 0x40) = n;
        t_last_run = nullptr;
    } else if (n <= len) {
        for (int i = 0; i < n; ++i) start[i] = uint16_t(label[i]);
        start[n] = 0;
    }
}

// D1_TRACE_RESOURCES=1 (research): 0x349C10(?, handle) is the "is this tag loaded" query
// (0xE2280(loaded set 0x2693C10, *(u16*)0x2693C0C, handle) * 2: 2 = loaded). Reimplemented to
// log each (handle, caller) once while in the world, with whether it was loaded, and again
// when it becomes loaded.
static D1_SYSV int resource_status_hook(void*, uint32_t handle) {
    const uint64_t b = rt().modules[0].base;
    using BitFn = D1_SYSV uint8_t (*)(void*, uint32_t, uint32_t);
    const int r = reinterpret_cast<BitFn>(b + 0xE2280)(reinterpret_cast<void*>(b + 0x2693C10),
                                                    *reinterpret_cast<const uint16_t*>(b + 0x2693C0C), handle) * 2;
    if (g_state.load(std::memory_order_relaxed) == 0x24) {
        static std::mutex m;
        static std::map<std::pair<uint32_t, uint64_t>, int> seen;
        const uint64_t caller = reinterpret_cast<uint64_t>(__builtin_return_address(0));
        std::lock_guard lk(m);
        auto [it, fresh] = seen.try_emplace({handle, caller}, r);
        if ((fresh || it->second != r) && seen.size() < 4000) {
            it->second = r;
            log("resource: %08x %s <- %s", handle, r == 2 ? "loaded" : "NOT loaded", describe_addr(caller).c_str());
        }
    }
    return r;
}

// D1_TRACE_VEHICLE=1 (research): 0x7420F0(player?, ...) is the vehicle (sparrow) summon path
// that crashed without a sparrow item; log each call and its result.
using VehicleFn = D1_SYSV uint64_t (*)(void*, void*, float*);
static VehicleFn g_vehicle_orig = nullptr;
static D1_SYSV uint64_t vehicle_hook(void* a, void* b, float* c) {
    log("vehicle: 0x7420F0(%p, %p, %p) <- %s", a, b, (void*)c, describe_addr(reinterpret_cast<uint64_t>(__builtin_return_address(0))).c_str());
    const uint64_t r = g_vehicle_orig(a, b, c);
    log("vehicle: -> %#llx", (unsigned long long)r);
    return r;
}

static D1_SYSV void state_step_hook(void* sm) {
    g_state_step_orig(sm);
    const int32_t st = *reinterpret_cast<const int32_t*>(static_cast<uint8_t*>(sm) + 0x1B0);
    g_state.store(st, std::memory_order_relaxed);
    // D1_TRACE_GEAR=1 (research): 20 s into activity:in_world (0x24), log the local player's
    // configuration (player data +0x1660, built by 0x912240): body tag, and per weapon
    // config (+0x368 / +0x688 / +0x9A8) its gear id (-1: none) and item index (@+0x22)
    trace_glyphs(st);
    static const bool trace = getenv("D1_TRACE_GEAR") != nullptr;
    static std::chrono::steady_clock::time_point since{};
    static bool done = false;
    if (trace && !done) {
        if (st != 0x24) { since = {}; return; }
        const auto now = std::chrono::steady_clock::now();
        if (since == std::chrono::steady_clock::time_point{}) since = now;
        if (now - since < std::chrono::seconds(20)) return;
        done = true;
        const uint64_t b = rt().modules[0].base;
        const uint64_t pd = *reinterpret_cast<const uint64_t*>(*reinterpret_cast<const uint64_t*>(b + 0x273EA80) + 8);
        const auto* cfg = reinterpret_cast<const uint8_t*>(pd + 0x1660);
        auto i32 = [&](int o) { return *reinterpret_cast<const int32_t*>(cfg + o); };
        auto i16 = [&](int o) { return int(*reinterpret_cast<const int16_t*>(cfg + o)); };
        log("gear: player config body %08x; weapons gear %d %d %d, items %d %d %d, slots %d %d %d", uint32_t(i32(0)),
            i32(0x368), i32(0x688), i32(0x9A8), i16(0x368 + 0x22), i16(0x688 + 0x22), i16(0x9A8 + 0x22),
            cfg[0x368 + 0x20], cfg[0x688 + 0x20], cfg[0x9A8 + 0x20]);
        // per weapon config: the stat-derived value at +0x318 (0x910C60: 0x282210 of one stat)
        // and the 20 stat curve slots from +0x58 (8 bytes each)
        for (int w : {0x368, 0x688, 0x9A8}) {
            std::string v;
            for (int k = 0; k < 20; ++k) {
                char buf[24];
                std::snprintf(buf, sizeof buf, " %.3g", *reinterpret_cast<const float*>(cfg + w + 0x58 + k * 0x20));
                v += buf;
            }
            log("gear: weapon config +%#x: +0x318 = %d; stat slots:%s", w, i32(w + 0x318), v.c_str());
        }
        // the gear table 0x54C7B0 indexes (0x54C7F0: {i32 count, i64 rel}, 0x20 rows) and the
        // loaded definitions of D1_GEAR_ITEMS=<i>,... (definitions vtable +0x410)
        using TblFn = D1_SYSV const int32_t* (*)();
        if (const int32_t* t = reinterpret_cast<TblFn>(b + 0x54C7F0)()) {
            const auto* r = reinterpret_cast<const uint8_t*>(t) + 8 + *reinterpret_cast<const int64_t*>(t + 2) + 0x10;
            log("gear: table 0x54C7F0 has %d rows; row 0: %08x %08x %08x %08x", t[0], *reinterpret_cast<const uint32_t*>(r),
                *reinterpret_cast<const uint32_t*>(r + 4), *reinterpret_cast<const uint32_t*>(r + 8), *reinterpret_cast<const uint32_t*>(r + 12));
        }
        if (const char* gi = getenv("D1_GEAR_ITEMS")) {
            void* defs = reinterpret_cast<void* (*)()>(b + 0x25A550)();
            const auto vt = *reinterpret_cast<const uint64_t* const*>(defs);
            using DefFn = D1_SYSV const uint8_t* (*)(void*, uint32_t);
            for (const char* q = gi; *q;) {
                const int i = atoi(q);
                const uint8_t* d = reinterpret_cast<DefFn>(vt[0x410 / 8])(defs, uint32_t(i));
                std::string hex;
                for (int k = 0; d && k < 0x2B8; k += 2) {
                    char buf[8];
                    std::snprintf(buf, sizeof buf, " %04x", *reinterpret_cast<const uint16_t*>(d + k));
                    hex += buf;
                }
                log("gear: definition %d at %p:%s", i, (const void*)d, hex.c_str());
                while (*q && *q != ',') ++q;
                if (*q) ++q;
            }
        }
    }
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

// bootflow:bootload steps (0x79A730, step at handler+0x30: 1 open the unpatchable package
// async, 2 wait for the open, 3/4 async read, 5/6 startup package sets, 0x10 done). Logged on
// change, so a stalled boot names its step.
static HandlerUpdateFn g_bootload_step_orig = nullptr;
static D1_SYSV void bootload_step_hook(void* h) {
    auto* step = reinterpret_cast<int32_t*>(static_cast<uint8_t*>(h) + 0x30);
    const int32_t before = *step;
    g_bootload_step_orig(h);
    if (*step != before) log("bootflow: bootload step %d -> %d", before, *step);
}

// bootflow:intro_screen_display (handler update 0x79D840, enter 0x79D800): on entering, the
// handler registers its "continue" listener (0x78E950(handler + 0x30)) only if the UI mode
// (*0x26CF430, 0x752150) is already 3, which game init sets (0x52C020 -> 0x751EE0). When the
// state is entered first (thread timing), nothing is registered, the flag at +0x38 never gets
// set and the game stays on the intro screen. Registration only stores the pointer, so the
// update re-registers while the flag is clear and the mode is 3.
static HandlerUpdateFn g_intro_update_orig = nullptr;
static D1_SYSV void intro_update_hook(void* h) {
    const uint64_t b = rt().modules[0].base;
    static bool logged = false;
    if (!logged) {
        logged = true;
        log("intro: first update, UI mode %d, listener flag %d", *reinterpret_cast<const int32_t*>(b + 0x26CF430),
            *(static_cast<uint8_t*>(h) + 0x38));
    }
    if (!*(static_cast<uint8_t*>(h) + 0x38) && *reinterpret_cast<const int32_t*>(b + 0x26CF430) == 3) {
        using RegFn = D1_SYSV void (*)(void*);
        reinterpret_cast<RegFn>(b + 0x78E950)(static_cast<uint8_t*>(h) + 0x30);
    }
    // Headless tests (D1_AUTOPRESS): occasionally the title screen's UI never delivers the
    // accept (the listener is registered, the UI-side caller 0x9CE1D0 never calls it). After
    // 20 s do what the listener's callback (0x79D860) does.
    static const bool autopress = getenv("D1_AUTOPRESS") != nullptr;
    static auto since = std::chrono::steady_clock::now();
    if (autopress && !*(static_cast<uint8_t*>(h) + 0x38) &&
        std::chrono::steady_clock::now() - since > std::chrono::seconds(20)) {
        log("intro: no accept from the title screen after 20 s, continuing (D1_AUTOPRESS)");
        *(static_cast<uint8_t*>(h) + 0x38) = 1;
    }
    g_intro_update_orig(h);
}

// investment_signin (eboot+0x79DA10): step at +0x30, sub-step at +0x34 (done at 7/3)
static HandlerUpdateFn g_invest_update_orig = nullptr;
static D1_SYSV void invest_update_hook(void* h) {
    auto* step = reinterpret_cast<int32_t*>(static_cast<uint8_t*>(h) + 0x30);
    const int32_t a = step[0], b = step[1];
    g_invest_update_orig(h);
    if (step[0] != a || step[1] != b) log("bootflow: investment_signin step %d.%d -> %d.%d", a, b, step[0], step[1]);
}

// profile_setup (eboot+0x7A01C0): step at +0x38 (7 done). Screens: 0 screen bounds (UI 0x16),
// 2 UI 0x15, 4 UI 0x17; each finishes with a "completed" event (0x7A02E0: 0x23/0x22/0x24)
// moving 1->2, 3->4, 5->6. On a new account UI 0x15 and 0x17 never come up (a spinner over
// the background) and so never send 0x22 / 0x24: D1_BYPASS=profile (on by default) completes
// those two steps (the screen bounds screen still runs).
static HandlerUpdateFn g_profile_update_orig = nullptr;
static bool g_profile_bypass = false;
static D1_SYSV void profile_update_hook(void* h) {
    auto* step = reinterpret_cast<int32_t*>(static_cast<uint8_t*>(h) + 0x38);
    // screens 2 and 3 (UI 0x15, 0x17) never come up on a new account (a spinner instead) and
    // so never send their events: complete those; the screen bounds screen is played
    // normally. D1_BYPASS=profile_all completes all three (headless testing).
    static const bool all = [] { const char* b = getenv("D1_BYPASS"); return b && std::strstr(b, "profile_all"); }();
    if (g_profile_bypass && (*step == 3 || *step == 5 || (all && *step == 1))) ++*step;
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
// Per-frame rates since the last call (null GPU statistics, every 300 flips): non-zero only.
void print_call_rates(uint64_t frames) {
    static std::vector<uint64_t> prev;
    prev.resize(g_counters.size());
    std::string line;
    for (size_t i = 0; i < g_counters.size(); ++i) {
        const uint64_t c = *g_counters[i].count;
        if (c != prev[i]) {
            char b[64];
            std::snprintf(b, sizeof b, " %llx=%.1f", (unsigned long long)g_counters[i].off, double(c - prev[i]) / double(frames));
            line += b;
        }
        prev[i] = c;
    }
    if (!line.empty()) log("calls per frame:%s", line.c_str());
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
    g_trace_spawn = getenv("D1_TRACE_SPAWN") != nullptr;
    g_publish_fireteam = getenv("D1_BYPASS") && std::strstr(getenv("D1_BYPASS"), "spawn");
    if (g_trace_spawn || g_publish_fireteam)
        g_can_spawn_orig = reinterpret_cast<CanSpawnFn>(hook_function(exe.base + 0x415700, reinterpret_cast<const void*>(&can_spawn_hook)));
    if (const char* v = getenv("D1_FORCE_LIFETIME"); v || (getenv("D1_BYPASS") && std::strstr(getenv("D1_BYPASS"), "spawn"))) {
        g_force_lifetime = v ? std::atoi(v) : 3;
        g_lifetime_orig = reinterpret_cast<LifetimeFn>(hook_function(exe.base + 0x10C500, reinterpret_cast<const void*>(&lifetime_hook)));
    }
    if (getenv("D1_TRACE_CAMERA"))
        g_set_camera_orig = reinterpret_cast<SetCameraFn>(hook_function(exe.base + 0x8E4EE0, reinterpret_cast<const void*>(&set_camera_hook)));
    if (getenv("D1_JOIN_TEST"))
        g_ui_notify_orig = reinterpret_cast<UiNotifyFn>(hook_function(exe.base + 0x950620, reinterpret_cast<const void*>(&ui_notify_hook)));
    g_perm_bypass = getenv("D1_BYPASS") && std::strstr(getenv("D1_BYPASS"), "activities");
    if (getenv("D1_TRACE_PERMISSION") || g_perm_bypass)
        g_perm_orig = reinterpret_cast<PermFn>(hook_function(exe.base + 0x2648D0, reinterpret_cast<const void*>(&perm_hook)));
    g_comp_bypass = getenv("D1_BYPASS") && std::strstr(getenv("D1_BYPASS"), "activities");
    if (getenv("D1_TRACE_COMPOSITION") || g_comp_bypass)
        g_comp_orig = reinterpret_cast<CompFn>(hook_function(exe.base + 0xB0C6D0, reinterpret_cast<const void*>(&comp_hook)));
    if (getenv("D1_TRACE_EQUIP"))
        g_equip_orig = reinterpret_cast<EquipFn>(hook_function(exe.base + 0x269A50, reinterpret_cast<const void*>(&equip_hook)));
    if (getenv("D1_TRACE_VEHICLE"))
        g_vehicle_orig = reinterpret_cast<VehicleFn>(hook_function(exe.base + 0x7420F0, reinterpret_cast<const void*>(&vehicle_hook)));
    if (getenv("D1_TRACE_RESOURCES")) replace_function(exe.base + 0x349C10, reinterpret_cast<const void*>(&resource_status_hook));
    if (const char* t = getenv("D1_TRACE_LOOKUP")) {
        g_trace_lookup_type = atoi(t);
        replace_function(exe.base + 0x56DC00, reinterpret_cast<const void*>(&lookup_replacement));
    }
    if (const char* w = getenv("D1_WATCH_FLAGS")) {
        for (const char* p = w; *p;) {
            g_watch_flags.push_back(atoi(p));
            while (*p && *p != ',') ++p;
            if (*p) ++p;
        }
        g_flag_apply_orig = reinterpret_cast<FlagApplyFn>(hook_function(exe.base + 0x28BC60, reinterpret_cast<const void*>(&flag_apply_hook)));
    }
    if (getenv("D1_TRACE_DIRECTOR"))
        replace_function(exe.base + 0x265100, reinterpret_cast<const void*>(&flag_time_hook));
    g_director_unlock = getenv("D1_BYPASS") && std::strstr(getenv("D1_BYPASS"), "activities");
    if (getenv("D1_TRACE_DIRECTOR") || g_director_unlock)
        g_activity_state_orig = reinterpret_cast<ActivityStateFn>(hook_function(exe.base + 0x264360, reinterpret_cast<const void*>(&activity_state_hook)));
    if (getenv("D1_TRACE_UNLOCK"))
        g_unlock_orig = reinterpret_cast<UnlockFn>(hook_function(exe.base + 0x28E590, reinterpret_cast<const void*>(&unlock_hook)));
    if (getenv("D1_JOIN_TEST"))
        g_progress_orig = reinterpret_cast<ProgressFn>(hook_function(exe.base + 0x28CFB0, reinterpret_cast<const void*>(&progress_hook)));
    if (getenv("D1_JOIN_TEST"))
        g_join_reason_orig = reinterpret_cast<JoinReasonFn>(hook_function(exe.base + 0x57B160, reinterpret_cast<const void*>(&join_reason_hook)));
    if (getenv("D1_TRACE_CINE") || getenv("D1_ALLOW_LOADING_CINE"))
        g_cine_orig = reinterpret_cast<CineFn>(hook_function(exe.base + 0x766750, reinterpret_cast<const void*>(&cine_suppressed_hook)));
    if (const char* b = getenv("D1_BYPASS"); b && std::strstr(b, "transport")) {
        replace_function(exe.base + 0x2EB340, reinterpret_cast<const void*>(&transport_started));
        replace_function(exe.base + 0x2EBD40, reinterpret_cast<const void*>(&transport_failed));
        log("hooks: DemonWare transport reported as started");
    }
    // Internal render resolution: the GPU device init (0x7E40A0) stores the display size as
    // immediates (`mov [r13+0x28F8], 1920` / `mov [r13+0x28FC], 1080`) and sizes the display
    // buffers and render targets from them.
    if (settings().render_width != 1920 || settings().render_height != 1080) {
        auto* w = reinterpret_cast<uint8_t*>(exe.base + 0x7E40D6);
        auto* h = reinterpret_cast<uint8_t*>(exe.base + 0x7E40E1);
        uint32_t ow, oh;
        std::memcpy(&ow, w, 4), std::memcpy(&oh, h, 4);
        if (ow == 1920 && oh == 1080) {
            const uint32_t nw = uint32_t(settings().render_width), nh = uint32_t(settings().render_height);
            std::memcpy(w, &nw, 4), std::memcpy(h, &nh, 4);
            log("hooks: internal render resolution %ux%u", nw, nh);
        } else {
            log("hooks: render resolution patch FAILED (unexpected bytes)");
        }
    }
    g_pc_orig = reinterpret_cast<PlayerControlFn>(hook_function(exe.base + 0x91B500, reinterpret_cast<const void*>(&player_control_hook)));
    if (!g_pc_orig) log("hooks: mouse look hook FAILED");
    // PC button prompts (key names instead of DualShock 4 glyphs while on keyboard and mouse)
    g_run_alloc_orig = reinterpret_cast<RunAllocFn>(hook_function(exe.base + 0x8DA760, reinterpret_cast<const void*>(&run_alloc_hook)));
    if (g_run_alloc_orig) replace_function(exe.base + 0x8D5530, reinterpret_cast<const void*>(&string_part_decode));
    else log("hooks: text run hook FAILED (controller prompts stay)");
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
        g_bootload_step_orig = reinterpret_cast<HandlerUpdateFn>(
            hook_function(exe.base + 0x79A730, reinterpret_cast<const void*>(&bootload_step_hook)));
        // its first instruction is a short branch (no room for a jump patch): replace the
        // handler's vtable slot (0x1946528 + 0x40) instead
        {
            auto* slot = reinterpret_cast<uint64_t*>(exe.base + 0x1946528 + 0x40);
            if (*slot == exe.base + 0x79D840) {
                g_intro_update_orig = reinterpret_cast<HandlerUpdateFn>(exe.base + 0x79D840);
                const uint64_t f = reinterpret_cast<uint64_t>(&intro_update_hook);
                os::write_backing(slot, &f, sizeof f);
                log("hooks: intro screen listener registration retried while the UI mode settles");
            } else {
                log("hooks: intro handler vtable slot is %#llx, not hooked", (unsigned long long)*slot);
            }
        }
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
