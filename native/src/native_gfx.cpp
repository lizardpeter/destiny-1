// Native renderer for Destiny 1 (work in progress).
//
// The engine draws through one "GPU device" object (eboot 0x7D8000-0x7E4000) over the
// statically linked Gnm library; see notes/D1_NATIVE_RENDERER_DEVICE_LAYER_2026-10-14.md.
// The native renderer hooks that device API and will implement it in Vulkan.
//
// Milestone 0 (D1_NATIVE_GFX=observe): every hooked call still runs the original (the
// shadPS4 / null GPU path draws as before) and the native side only records what a frame
// uses: device instances, threads, draws, shaders, vertex declarations, state combinations
// (future Vulkan pipelines), textures and buffers. The numbers size the native design.
#include <deque>
#include <map>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <algorithm>
#include <cstring>
#include <filesystem>
#include <string>
#include <mutex>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#include "formats.h"
#include "nrender.h"
#include "settings.h"
#ifdef D1_FRONTEND_SDL
#include "frontend.h"
#endif
#include "hle.h"
#include "os.h"
#include "render_bridge.h"
#include "runtime.h"
#include "tiling.h"

#ifndef _WIN32
#include <sys/syscall.h>
#include <ucontext.h>
#include <dlfcn.h>
#include <unistd.h>
#endif

namespace d1 {

void* hook_eboot_function(uint64_t off, const void* host);  // hooks.cpp
bool replace_eboot_function(uint64_t off, const void* host);  // hooks.cpp
uint64_t guest_region_extent(uint64_t addr);                // hle_kernel.cpp
uint64_t gpu_flip_count();                                  // hle_gpu.cpp
uint64_t gpu_queue_wait_ns();                               // hle_gpu.cpp

namespace {

// ---- device object fields (eboot 01.33)
constexpr uint64_t kVsShader = 0x1D28, kPsShader = 0x1D30, kVertexDecl = 0x1D60;
constexpr uint64_t kBlendIndex = 0x25B4, kRasterIndex = 0x25BC, kDepthIndex = 0x25C0, kStencil = 0x25E8;
constexpr uint64_t kColorTarget0 = 0x26E4;

template <class T>
T field(uint64_t dev, uint64_t off) {
    T v;
    std::memcpy(&v, reinterpret_cast<const void*>(dev + off), sizeof v);
    return v;
}

uint64_t thread_id() {
#ifdef _WIN32
    return 0;
#else
    return uint64_t(syscall(SYS_gettid));
#endif
}

uint64_t mix(uint64_t h, uint64_t v) {
    h ^= v + 0x9E3779B97F4A7C15ull + (h << 6) + (h >> 2);
    return h;
}

// ---- observer
struct Observer {
    std::mutex m;
    uint64_t draws = 0, binds_tex = 0, binds_vb = 0, const_allocs = 0, const_bytes = 0, rt_sets = 0;
    std::unordered_set<uint64_t> devices, threads, vs, ps, programs, decls, pipelines, textures, vbufs, ibufs,
        targets;
    uint64_t frames0 = 0;
    void reset() {
        draws = binds_tex = binds_vb = const_allocs = const_bytes = rt_sets = 0;
        for (auto* s : {&devices, &threads, &vs, &ps, &programs, &decls, &pipelines, &textures, &vbufs, &ibufs,
                        &targets})
            s->clear();
    }
    void maybe_report() {
        const uint64_t f = gpu_flip_count();
        if (f - frames0 < 600) return;
        const double n = double(f - frames0);
        log("native gfx (observe, per frame over %.0f frames): %.0f draws | %.0f texture binds, %.0f vertex buffer binds, "
            "%.0f constant allocations (%.1f KB) | %.1f render-target sets",
            n, draws / n, binds_tex / n, binds_vb / n, const_allocs / n, const_bytes / n / 1024.0, rt_sets / n);
        log("native gfx (observe, distinct over those frames): %zu devices on %zu threads | %zu vertex + %zu pixel shaders, "
            "%zu programs, %zu vertex declarations, %zu pipeline states | %zu textures, %zu vertex buffers, %zu index "
            "buffers, %zu color targets",
            devices.size(), threads.size(), vs.size(), ps.size(), programs.size(), decls.size(), pipelines.size(),
            textures.size(), vbufs.size(), ibufs.size(), targets.size());
        frames0 = f;
        reset();
    }
};
Observer* g_obs = nullptr;

void note_device(uint64_t dev) {
    g_obs->devices.insert(dev);
    g_obs->threads.insert(thread_id());
}

// ---- hooked device API (System V signatures as decompiled)
using DrawIndexedFn = D1_SYSV void (*)(uint64_t, uint64_t, uint64_t, int32_t, uint32_t);
using DrawFn = D1_SYSV void (*)(uint64_t, uint64_t, uint32_t);
using SetTextureFn = D1_SYSV void (*)(uint64_t, uint32_t, uint64_t, void*);
using SetVertexBufferFn = D1_SYSV void (*)(uint64_t, uint32_t, uint32_t, uint32_t, int32_t);
using AllocConstantsFn = D1_SYSV uint64_t (*)(uint64_t, uint32_t, uint32_t, uint32_t);
using SetIndexBufferFn = D1_SYSV void (*)(uint64_t, uint32_t);
using ApplyTargetsFn = D1_SYSV void (*)(uint64_t);

DrawIndexedFn o_draw_indexed;
DrawFn o_draw;
SetTextureFn o_set_texture;
SetVertexBufferFn o_set_vertex_buffer;
AllocConstantsFn o_alloc_constants;
SetIndexBufferFn o_set_index_buffer;
ApplyTargetsFn o_apply_targets;

// D1_NATIVE_GFX_DUMP=<dir>: write each distinct shader object (first 512 bytes) once, for
// working out the shader object layout offline. Research aid; not shipped data.
void dump_shader_object(const char* kind, uint64_t obj) {
    static const char* dir = getenv("D1_NATIVE_GFX_DUMP");
    if (!dir || obj < 0x10000) return;
    char path[512];
    std::snprintf(path, sizeof path, "%s/%s_%llx.obj", dir, kind, (unsigned long long)obj);
    if (FILE* f = std::fopen(path, "wb")) {
        std::fwrite(reinterpret_cast<const void*>(obj), 1, 512, f);
        std::fclose(f);
    }
    // the Gnm shader starts at +0x14 of a vertex shader object (after the fetch shader size
    // and address) and at +0 of a pixel shader object: common data (code size in bits 0..22),
    // then SPI_SHADER_PGM_LO/HI (code address >> 8)
    const uint64_t gnm = obj + (kind[0] == 'v' ? 0x14 : 0);
    const uint32_t size = field<uint32_t>(gnm, 0) & 0x7FFFFF;
    const uint64_t code = (uint64_t(field<uint32_t>(gnm, 8)) << 8) | (uint64_t(field<uint32_t>(gnm, 12)) << 40);
    if (size && size < 0x40000 && code) {
        std::snprintf(path, sizeof path, "%s/%s_%llx.code", dir, kind, (unsigned long long)obj);
        if (FILE* f = std::fopen(path, "wb")) {
            std::fwrite(reinterpret_cast<const void*>(code), 1, size + 256, f);
            std::fclose(f);
        }
    }
    if (kind[0] == 'v') {  // fetch shader
        const uint32_t fsize = field<uint32_t>(obj, 0) & 0x7FFFFF;  // high bits: flags
        const uint64_t fcode = field<uint64_t>(obj, 8);
        if (fsize && fsize < 0x10000 && fcode) {
            std::snprintf(path, sizeof path, "%s/%s_%llx.fetch", dir, kind, (unsigned long long)obj);
            if (FILE* f = std::fopen(path, "wb")) {
                std::fwrite(reinterpret_cast<const void*>(fcode), 1, fsize, f);
                std::fclose(f);
            }
        }
    }
}

void note_draw(uint64_t dev, uint64_t prim) {
    std::lock_guard lk(g_obs->m);
    note_device(dev);
    ++g_obs->draws;
    const uint64_t vs = field<uint64_t>(dev, kVsShader), ps = field<uint64_t>(dev, kPsShader);
    const uint64_t decl = field<uint64_t>(dev, kVertexDecl);
    if (g_obs->vs.insert(vs).second) dump_shader_object("vs", vs);
    if (g_obs->ps.insert(ps).second) dump_shader_object("ps", ps);
    g_obs->decls.insert(decl);
    g_obs->programs.insert(mix(vs, ps));
    uint64_t key = mix(mix(mix(vs, ps), decl), prim & 0xFF);
    key = mix(key, field<uint32_t>(dev, kBlendIndex));
    key = mix(key, field<uint32_t>(dev, kRasterIndex));
    key = mix(key, field<uint32_t>(dev, kDepthIndex));
    key = mix(key, field<uint32_t>(dev, kStencil));
    key = mix(key, field<uint64_t>(dev, kColorTarget0 + 0x28));  // target format word (approximate)
    g_obs->pipelines.insert(key);
    g_obs->maybe_report();
}

D1_SYSV void h_draw_indexed(uint64_t dev, uint64_t prim, uint64_t a, int32_t first, uint32_t count) {
    if (field<uint8_t>(dev, 0x26)) note_draw(dev, prim);
    o_draw_indexed(dev, prim, a, first, count);
}
D1_SYSV void h_draw(uint64_t dev, uint64_t prim, uint32_t count) {
    if (field<uint8_t>(dev, 0x26)) note_draw(dev, prim);
    o_draw(dev, prim, count);
}
// D1_NATIVE_GFX_DUMP: also each distinct texture once (T# + its memory) for detiling tests.
void dump_texture(uint64_t tsharp) {
    static const char* dir = getenv("D1_NATIVE_GFX_DUMP");
    static int count = 0;
    if (!dir || tsharp < 0x10000 || count >= 400) return;
    const uint32_t* t = reinterpret_cast<const uint32_t*>(tsharp);
    const uint64_t base = (uint64_t(t[0]) | uint64_t(t[1] & 0xFF) << 32) << 8;
    const uint32_t w = (t[2] & 0x3FFF) + 1, h = ((t[2] >> 14) & 0x3FFF) + 1;
    const uint32_t levels = ((t[3] >> 16) & 0xF) + 1;
    if (!base || w * h > 4096u * 4096u) return;
    // exact guest footprint from the T# (all mips and slices)
    const auto ts = fmt::decode_tsharp(t);
    const auto fi = fmt::data_format(ts.dfmt);
    if (!fi.bpp || fi.bpp == 96) return;
    tiling::Surface sf;
    sf.tile_mode = ts.tiling, sf.bpp = fi.bpp, sf.block = fi.block, sf.pow2 = ts.pow2;
    sf.width = ts.width, sf.height = ts.height, sf.pitch = ts.pitch;
    sf.depth = ts.type == 10 ? ts.depth : 1;
    sf.layers = (ts.type == 13 || ts.type == 11) ? ts.last_array + 1 : 1;
    sf.levels = ts.last_level + 1;
    tiling::layout(sf);
    const uint64_t bytes = std::min<uint64_t>(sf.total_size, 16ull << 20);
    const uint64_t extent = guest_region_extent(base);
    char path[512];
    std::snprintf(path, sizeof path, "%s/tex_%llx.tsharp", dir, (unsigned long long)tsharp);
    if (FILE* f = std::fopen(path, "wb")) {
        std::fwrite(t, 4, 8, f);
        std::fclose(f);
    }
    std::snprintf(path, sizeof path, "%s/tex_%llx.mem", dir, (unsigned long long)tsharp);
    if (FILE* f = std::fopen(path, "wb")) {
        std::fwrite(reinterpret_cast<const void*>(base), 1, extent ? std::min(bytes, extent) : bytes, f);
        std::fclose(f);
    }
    (void)levels;
    ++count;
}

D1_SYSV void h_set_texture(uint64_t dev, uint32_t stage, uint64_t slot, void* tsharp) {
    {
        std::lock_guard lk(g_obs->m);
        ++g_obs->binds_tex;
        if (g_obs->textures.insert(reinterpret_cast<uint64_t>(tsharp)).second) dump_texture(reinterpret_cast<uint64_t>(tsharp));
    }
    o_set_texture(dev, stage, slot, tsharp);
}
D1_SYSV void h_set_vertex_buffer(uint64_t dev, uint32_t handle, uint32_t stream, uint32_t offset, int32_t count) {
    {
        std::lock_guard lk(g_obs->m);
        ++g_obs->binds_vb;
        if (handle != 0xFFFFFFFFu) g_obs->vbufs.insert(handle);
    }
    o_set_vertex_buffer(dev, handle, stream, offset, count);
}
D1_SYSV uint64_t h_alloc_constants(uint64_t dev, uint32_t stage, uint32_t slot, uint32_t bytes) {
    {
        std::lock_guard lk(g_obs->m);
        ++g_obs->const_allocs;
        g_obs->const_bytes += bytes;
    }
    return o_alloc_constants(dev, stage, slot, bytes);
}
D1_SYSV void h_set_index_buffer(uint64_t dev, uint32_t handle) {
    {
        std::lock_guard lk(g_obs->m);
        g_obs->ibufs.insert(handle);
    }
    o_set_index_buffer(dev, handle);
}
D1_SYSV void h_apply_targets(uint64_t dev) {
    {
        std::lock_guard lk(g_obs->m);
        ++g_obs->rt_sets;
        const bool fresh = g_obs->targets.insert(field<uint64_t>(dev, kColorTarget0)).second;
        // D1_NATIVE_GFX_RT=1: log the raw target descriptors of each new combination (research)
        static const bool log_rt = getenv("D1_NATIVE_GFX_RT") != nullptr;
        static int logged = 0;
        if (log_rt && fresh && logged < 60) {
            ++logged;
            auto hexrow = [&](uint64_t off, int dwords) {
                std::string s;
                char b[12];
                for (int i = 0; i < dwords; ++i) {
                    std::snprintf(b, sizeof b, " %08x", field<uint32_t>(dev, off + 4 * i));
                    s += b;
                }
                return s;
            };
            log("native gfx rt: depth%s", hexrow(0x26B0, 13).c_str());
            for (int i = 0; i < 5; ++i) log("native gfx rt: color%d%s", i, hexrow(kColorTarget0 + 0x2C * i, 11).c_str());
        }
    }
    o_apply_targets(dev);
}


// ---------------------------------------------------------------------------- native rendering
// D1_NATIVE_GFX=render: the device API calls are captured into ng::Draw records (registers,
// descriptors and shader objects as the engine's device object holds them), matched to the
// command buffers the game submits (by their DCB write position) and executed by our own
// Vulkan renderer (gfx/nrender.cpp). The original functions still run, so the null GPU keeps
// the game's fences and flips going.
bool nd_push(uint64_t dev, ng::Draw* d);  // native device layer: into the context's command list

namespace nr {

uint64_t g_base = 0;  // eboot base
template <class T>
T eb(uint64_t off) {
    T v;
    std::memcpy(&v, reinterpret_cast<const void*>(g_base + off), sizeof v);
    return v;
}

using BuildVsharpFn = D1_SYSV void (*)(void*, uint64_t, uint32_t, uint32_t, uint32_t);
using SetMemTypeFn = D1_SYSV void (*)(void*, uint32_t);
BuildVsharpFn build_vsharp;
SetMemTypeFn set_mem_type;

struct DevState {
    ng::Draw::Cb cb[ng::kStages][16] = {};
    uint32_t vb_count[32] = {};
};

std::mutex g_m;
std::unordered_map<uint64_t, DevState*> g_devs;
// draws waiting for the submission that holds their command-buffer position, by position: a
// submission takes the draws inside its ranges with a few lookups (a frame's later draws are
// all waiting while its earlier submissions run: ~10k, scanned in full per submission before)
// sorted by command-buffer position (equal positions keep their recording order)
std::vector<std::pair<uint64_t, ng::Draw*>> g_pending;
std::atomic<uint32_t> g_seq{0};
int g_every = 1;            // execute every Nth frame
int g_dump_every = 0;       // write every Nth executed frame (0: none)
uint64_t g_executed_frames = 0;
bool g_frame_executed = false;
uint64_t g_exec_ns = 0, g_flip_ns = 0;  // time in ng::execute / ng::flip (CPU side, incl. waits)

// Constant buffers as the engine binds them on a context's constant update engine
// (eboot+0xF8B500, setConstantBuffers(cue, stage, first slot, count, V#s)): alloc_constants
// goes through it, and so do the passes that bind a buffer of their own (fullscreen-pass
// viewport constants at 0x7E2C3D / 0x7E2E03, dispatch constants). Keyed by the CUE.
// Constant buffer bindings as events in command-buffer order. The constant update engine
// keeps its bindings in CE RAM, which every context's command buffer shares: a deferred
// context that never binds a slot itself sees what the main context bound before calling it
// (per-view constants are bound once on the main context). Replayed in submission order at
// execute time, they give each draw the bindings the GPU would see.
struct CbEvent {
    uint64_t order;
    uint32_t seq;
    uint8_t stage, slot;
    ng::Draw::Cb cb;
};
std::vector<CbEvent> g_cb_pending;  // by position, as the draws (stage 0xFF: taken)
ng::Draw::Cb g_ce[ng::kStages][16] = {};  // bindings as of the end of the last submission
bool g_ce_order = true;                   // D1_NG_CE_ORDER=0: per-context bindings only (old behaviour)
bool g_cbs_armed = false;
uint64_t g_dropped = 0;  // draws recorded but never found in a submission
uint64_t g_late = 0;     // draws found in a submission of a later frame than they were recorded in  // D1_NG_LOG_CBS: the debugged pixel shader has been drawn
struct CueState {
    ng::Draw::Cb cb[ng::kStages][16] = {};
};
std::unordered_map<uint64_t, CueState*> g_cues;
CueState* cue_state(uint64_t cue, bool create) {
    thread_local uint64_t last_cue = 0;
    thread_local CueState* last = nullptr;
    if (cue == last_cue && last) return last;
    std::lock_guard lk(g_m);
    auto it = g_cues.find(cue);
    CueState* c = it != g_cues.end() ? it->second : nullptr;
    if (!c && create) g_cues[cue] = c = new CueState;
    if (c) last_cue = cue, last = c;
    return c;
}

DevState* dev_state(uint64_t dev) {
    thread_local uint64_t last_dev = 0;
    thread_local DevState* last = nullptr;
    if (dev == last_dev) return last;
    std::lock_guard lk(g_m);
    auto& d = g_devs[dev];
    if (!d) d = new DevState;
    last_dev = dev, last = d;
    return d;
}

// engine resource handle -> buffer object (pool table at *0x1A238A0)
uint64_t resolve_handle(uint32_t h) {
    const uint64_t tbl = *reinterpret_cast<const uint64_t*>(eb<uint64_t>(0x1A238A0));
    const int32_t hs = int32_t(h) >> 13;  // as the engine computes it (handles with bit 31 use more pool bits)
    const uint64_t pool = tbl + uint64_t(((uint32_t(hs) >> 18) | 0x3FF) & uint32_t(hs)) * 0x40;
    const uint64_t pbase = field<uint64_t>(pool, 0x10);
    const uint64_t off = uint64_t(h & 0x1FFF) * field<uint32_t>(pool, 0x30);
    const uint64_t mask = uint64_t(int64_t(field<int32_t>(pool, 0x34)));
    return (pbase + off) - (mask & field<uint64_t>(pbase + off, 8));
}
// the same for a handle that may name an unloaded pool (0 then)
uint64_t resolve_handle_safe(uint32_t h) {
    const uint64_t tbl = *reinterpret_cast<const uint64_t*>(eb<uint64_t>(0x1A238A0));
    const int32_t hs = int32_t(h) >> 13;
    const uint64_t pool = tbl + uint64_t(((uint32_t(hs) >> 18) | 0x3FF) & uint32_t(hs)) * 0x40;
    const uint64_t pbase = field<uint64_t>(pool, 0x10);
    const uint32_t esz = field<uint32_t>(pool, 0x30);
    if (!pbase || !esz || (h & 0x1FFF) * uint64_t(esz) >= field<uint64_t>(pool, 0x20) - pbase) return 0;
    const uint64_t off = uint64_t(h & 0x1FFF) * esz;
    const uint64_t mask = uint64_t(int64_t(field<int32_t>(pool, 0x34)));
    return (pbase + off) - (mask & field<uint64_t>(pbase + off, 8));
}

int gnm_stage_index(uint32_t gnm_stage) { return gnm_stage == 1 ? 1 : gnm_stage == 2 ? 0 : -1; }

uint32_t vertex_count(uint32_t prim, uint32_t n) {
    switch (prim) {
    case 0: return n;
    case 1: return n * 2;
    case 2: return n + 1;
    case 3: case 6: return n * 3;
    case 4: case 5: return n + 2;
    case 7: return n * 4;
    default: return 0;
    }
}

// ---------------------------------------------------------------------------- resource registry
// The engine's GPU resources as the engine itself manages them (findings/gpu_resources.md):
// every bind / re-point / release / move / mip change of a texture (types 1-3: the object is
// the T#), vertex buffer (4) or index buffer (6) bumps the object's epoch. The renderer keeps
// its copy of a registered resource while the epoch is unchanged - no write tracking, no
// version checks - and compares contents once when it changes (a move usually keeps them).
// Reads are lock-free (draw capture, every texture slot of every draw).
namespace resreg {
constexpr uint32_t kBits = 18;
constexpr size_t kSlots = size_t(1) << kBits, kProbe = 64;
struct Slot { std::atomic<uint64_t> key{0}, val{0}; };
Slot* g_slots = nullptr;
std::mutex g_wm;
uint32_t g_next_id = 0;
size_t g_used = 0;
std::atomic<uint64_t> g_events{0};
bool g_on = false;
inline size_t home(uint64_t k) { return size_t((k * 0x9E3779B97F4A7C15ull) >> (64 - kBits)); }
// id << 32 | epoch, or 0 when the object is not a registered resource
inline uint64_t get(uint64_t key) {
    if (!g_slots || key < 0x10000) return 0;
    const size_t h = home(key);
    for (size_t i = 0; i < kProbe; ++i) {
        Slot& sl = g_slots[(h + i) & (kSlots - 1)];
        const uint64_t k = sl.key.load(std::memory_order_acquire);
        if (k == key) return sl.val.load(std::memory_order_acquire);
        if (!k) return 0;
    }
    return 0;
}
// an event on the object: a new epoch (insert = false: only if it is registered already)
void touch(uint64_t key, bool insert) {
    if (!g_slots || key < 0x10000) return;
    std::lock_guard lk(g_wm);
    const size_t h = home(key);
    for (size_t i = 0; i < kProbe; ++i) {
        Slot& sl = g_slots[(h + i) & (kSlots - 1)];
        const uint64_t k = sl.key.load(std::memory_order_relaxed);
        if (k == key) {
            const uint64_t v = sl.val.load(std::memory_order_relaxed);
            sl.val.store((v & ~0xFFFFFFFFull) | ((v + 1) & 0xFFFFFFFFull), std::memory_order_release);
            ++g_events;
            return;
        }
        if (!k) {
            if (!insert || g_used * 10 > kSlots * 7) return;  // (full: unregistered, write-tracked as before)
            sl.val.store(uint64_t(++g_next_id) << 32 | 1, std::memory_order_relaxed);
            sl.key.store(key, std::memory_order_release);
            ++g_used, ++g_events;
            return;
        }
    }
}
// the resource object a (type, handle) names, 0 for the types the renderer does not track
uint64_t object_of(uint32_t type, uint32_t handle) {
    if (handle == 0xFFFFFFFFu || (!(type >= 1 && type <= 4) && type != 6)) return 0;
    const uint64_t o = resolve_handle_safe(handle);
    return o >= 0x10000 ? o : 0;
}
// the renderer prepares the resource's GPU copy now (its loader thread)
void prefetch(uint32_t type, uint64_t o) {
    if (!o || !ng::active()) return;
    const uint64_t res = get(o);
    if (!res) return;
    if (type >= 1 && type <= 3) ng::prefetch_texture(reinterpret_cast<const uint32_t*>(o), res, o);
    else if (type == 4) ng::prefetch_buffer(field<uint64_t>(o, 0x28), field<uint32_t>(o, 0), res, o);
}
void event(uint32_t type, uint32_t handle, bool insert) {
    if (const uint64_t o = object_of(type, handle)) touch(o, insert), prefetch(type, o);
}
// a handle of unknown type (moves): whichever object it names, if registered
void event_any(uint32_t handle) {
    if (handle == 0xFFFFFFFFu) return;
    if (const uint64_t o = resolve_handle_safe(handle)) touch(o, false);
}
void init() {
    if (g_slots) return;
    g_slots = new Slot[kSlots];
    g_on = true;
}
}  // namespace resreg

ng::Draw* alloc_draw();
void resev_check_draw(uint64_t dev);  // (below)

// D1_ND_RES_STATS=1: (research) which handle pools the draws' vertex / index buffers and
// textures come from, logged every 600 flips with each pool's descriptor once
namespace resstats {
std::mutex m;
struct Pool { uint64_t vb = 0, ib = 0, tex = 0; std::unordered_set<uint32_t> handles; bool dumped = false; };
std::map<uint32_t, Pool> pools;
uint64_t tex_other = 0, tex_total = 0, vb_total = 0, ib_noobj = 0, last_flip = 0, draws = 0, no_decl = 0, decl_no_handle = 0, decl_zero = 0;
std::map<uint64_t, uint64_t> tex_other_regions;  // T# pointer >> 24 -> count
uint32_t pool_of(uint32_t h) {
    const int32_t hs = int32_t(h) >> 13;
    return ((uint32_t(hs) >> 18) | 0x3FF) & uint32_t(hs);
}
// the pool whose element array holds `p` (UINT32_MAX: none)
uint32_t pool_holding(uint64_t p) {
    const uint64_t tbl = *reinterpret_cast<const uint64_t*>(eb<uint64_t>(0x1A238A0));
    for (uint32_t i = 0; i < 1024; ++i) {
        const uint64_t d = tbl + uint64_t(i) * 0x40;
        const uint64_t base = field<uint64_t>(d, 0x10);
        const uint32_t esz = field<uint32_t>(d, 0x30);
        if (!base || !esz) continue;
        if (p >= base && p < base + uint64_t(esz) * 0x2000) return i;
    }
    return UINT32_MAX;
}
void dump_pool(uint32_t i) {
    const uint64_t tbl = *reinterpret_cast<const uint64_t*>(eb<uint64_t>(0x1A238A0));
    const uint64_t* q = reinterpret_cast<const uint64_t*>(tbl + uint64_t(i) * 0x40);
    std::string t;
    for (int k = 0; k < 8; ++k) {
        char b[24];
        std::snprintf(b, sizeof b, " %016llx", (unsigned long long)q[k]);
        t += b;
    }
    // a name string at one of the fields?
    for (int k = 0; k < 8; ++k)
        if (q[k] >= 0x10000 && guest_region_extent(q[k]) >= 4) {
            const char* c = reinterpret_cast<const char*>(q[k]);
            bool txt = true;
            for (int j = 0; j < 4; ++j) txt &= c[j] >= 0x20 && c[j] < 0x7F;
            if (txt) { t += " | +"; t += std::to_string(k * 8); t += " \""; t.append(c, strnlen(c, 40)); t += "\""; }
        }
    log("nd res pool %u:%s", i, t.c_str());
}
void note(uint64_t dev, const ng::Draw* d) {
    std::lock_guard lk(m);
    for (int st = 0; st < 2; ++st)
        for (int i = 0; i < 16; ++i)
            if (d->tex_mask[st] >> i & 1) {
                ++tex_total;
                const uint64_t t = field<uint64_t>(dev, 0x1E78 + (st ? 1 : 2) * 0x80 + i * 8);
                const uint32_t pl = pool_holding(t);
                if (pl == UINT32_MAX) ++tex_other, ++tex_other_regions[t >> 28];
                else ++pools[pl].tex;
            }
    ++draws;
    if (!field<uint64_t>(dev, 0x1D60)) ++no_decl;
    else if (!field<uint32_t>(field<uint64_t>(dev, 0x1D60), 0)) ++decl_zero;
    if (const uint64_t decl = field<uint64_t>(dev, 0x1D60)) {
        const uint32_t n = std::min(field<uint32_t>(decl, 0), 16u);
        uint32_t seen = 0;
        bool any = false;
        for (uint32_t i = 0; i < n; ++i)
            any |= field<uint32_t>(dev, 0x1D78 + 4 * (field<uint8_t>(decl, 0x19 + 8 * i) & 31)) != 0xFFFFFFFFu;
        if (n && !any) ++decl_no_handle;
        for (uint32_t i = 0; i < n; ++i) {
            const uint32_t stream = field<uint8_t>(decl, 0x19 + 8 * i) & 31;
            const uint32_t h = field<uint32_t>(dev, 0x1D78 + 4 * stream);
            if (h == 0xFFFFFFFFu || (seen >> stream & 1)) continue;
            seen |= 1u << stream;
            Pool& p = pools[pool_of(h)];
            ++p.vb, ++vb_total;
            p.handles.insert(h);
        }
    }
    {  // (the kind is set after the capture: the bound index buffer)
        const uint32_t h = field<uint32_t>(dev, 0x1D68);
        if (!field<uint64_t>(dev, 0x1D70) || h == 0xFFFFFFFFu) ++ib_noobj;
        else {
            Pool& p = pools[pool_of(h)];
            ++p.ib;
            p.handles.insert(h);
        }
    }
    if (gpu_flip_count() >= last_flip + 600) {
        last_flip = gpu_flip_count();
        std::string t;
        for (auto& [i, p] : pools) {
            char b[160];
            std::snprintf(b, sizeof b, " [pool %u: vb %llu ib %llu tex %llu, %zu handles]", i, (unsigned long long)p.vb,
                          (unsigned long long)p.ib, (unsigned long long)p.tex, p.handles.size());
            t += b;
            if (!p.dumped) p.dumped = true, dump_pool(i);
        }
        std::string r;
        for (auto& [k, v] : tex_other_regions) {
            char b[48];
            std::snprintf(b, sizeof b, " %llx0000000:%llu", (unsigned long long)k, (unsigned long long)v);
            r += b;
        }
        log("nd res: %llu draws (%llu without a vertex declaration, %llu with an empty one, %llu with no stream handle)",
            (unsigned long long)draws, (unsigned long long)no_decl, (unsigned long long)decl_zero, (unsigned long long)decl_no_handle);
        draws = no_decl = decl_zero = decl_no_handle = 0;
        log("nd res: %llu vb binds, %llu ib without object, %llu textures (%llu outside pools:%s) |%s", (unsigned long long)vb_total,
            (unsigned long long)ib_noobj, (unsigned long long)tex_total, (unsigned long long)tex_other, r.c_str(), t.c_str());
        pools.clear(), tex_other_regions.clear(), tex_other = tex_total = vb_total = ib_noobj = 0;
    }
}
}  // namespace resstats

// Common state of every draw, read from the device object.
thread_local uint64_t t_capture_dev = 0;  // (the device context of the last capture: push() files it there)
ng::Draw* capture(uint64_t dev, uint32_t engine_prim, uint64_t caller = 0) {
    t_capture_dev = dev;
    auto* d = alloc_draw();
    d->caller = caller ? caller - g_base : 0;
    d->prim = uint8_t(eb<uint32_t>(0x15D13C0 + uint64_t(engine_prim) * 4));
    d->vs = reinterpret_cast<const uint8_t*>(field<uint64_t>(dev, kVsShader));
    d->ps = reinterpret_cast<const uint8_t*>(field<uint64_t>(dev, kPsShader));
    const uint64_t ctx = field<uint64_t>(dev, 0x50);
    d->order = ctx ? field<uint64_t>(ctx, 0x10) : 0;
    DevState* ds = dev_state(dev);
    CueState* cs = ctx ? cue_state(ctx + 0xC0, false) : nullptr;
    // vertex buffers: one V# per declaration element, as set_vertex_buffer builds them
    if (const uint64_t decl = field<uint64_t>(dev, kVertexDecl)) {
        const uint32_t n = std::min(field<uint32_t>(decl, 0), 16u);
        d->num_vb = n;
        for (uint32_t i = 0; i < n; ++i) {
            const uint32_t fmt = field<uint32_t>(decl, 0x14 + 8 * i);
            const uint32_t off = field<uint8_t>(decl, 0x18 + 8 * i), stream = field<uint8_t>(decl, 0x19 + 8 * i) & 31;
            const uint32_t stride = field<uint32_t>(decl, 4 + 4 * (stream & 3));
            const uint32_t h = field<uint32_t>(dev, 0x1D78 + 4 * stream);
            if (h == 0xFFFFFFFFu || !stride) continue;
            const uint64_t obj = resolve_handle(h);
            const uint64_t base = field<uint64_t>(obj, 0x28) + off + field<uint32_t>(dev, 0x1DF8 + 4 * stream);
            build_vsharp(d->vb[i], base, fmt, stride, ds->vb_count[stream]);
            if (resreg::g_on) {
                d->vres[i] = {resreg::get(obj), field<uint64_t>(obj, 0x28), field<uint32_t>(obj, 0)};
                // D1_ND_LOG_UNREG: (research) vertex buffers that are no engine resource
                static const bool log_unreg = getenv("D1_ND_LOG_UNREG") != nullptr;
                if (log_unreg && !d->vres[i].id) {
                    static std::mutex lm;
                    static std::unordered_map<uint32_t, int> seen;
                    std::lock_guard lk(lm);
                    if (seen.size() < 40 && !seen[h]++) {
                        const uint32_t* q = reinterpret_cast<const uint32_t*>(obj);
                        log("nd unregistered vertex buffer: handle %#x pool %u obj %#llx | %08x %08x %08x %08x %08x %08x %08x %08x %08x %08x %08x %08x %08x %08x | caller %#llx",
                            h, ((uint32_t(int32_t(h) >> 13) >> 18) | 0x3FF) & uint32_t(int32_t(h) >> 13), (unsigned long long)obj, q[0], q[1], q[2], q[3],
                            q[4], q[5], q[6], q[7], q[8], q[9], q[10], q[11], q[12], q[13], (unsigned long long)(caller ? caller - g_base : 0));
                    }
                }
            }
        }
    }
    for (int s = 0; s < 2; ++s) {
        const uint32_t gnm = s ? 1 : 2;
        for (int i = 0; i < 16; ++i) {
            if (const uint64_t t = field<uint64_t>(dev, 0x1E78 + gnm * 0x80 + i * 8); t >= 0x10000) {
                std::memcpy(d->tex[s][i], reinterpret_cast<const void*>(t), 32);
                d->tex_mask[s] |= uint16_t(1u << i);
                d->tex_res[s][i] = resreg::g_on ? resreg::get(t) : 0;
            }
            if (const uint64_t p = field<uint64_t>(dev, (s ? 0x2278 : 0x22F8) + i * 8); p >= 0x10000) {
                std::memcpy(d->smp[s][i], reinterpret_cast<const void*>(p), 16);
                d->smp_mask[s] |= uint16_t(1u << i);
            }
            d->cb[s][i] = ds->cb[s][i];
            if (cs) d->cb[s][i] = cs->cb[s][i];
        }
    }
    static const uint64_t log_ps = [] { const char* v = getenv("D1_NG_DEBUG_PS"); return v ? strtoull(v, nullptr, 16) : 0ull; }();
    if (log_ps && uint64_t(d->ps) == log_ps && getenv("D1_NG_LOG_CBS") && (g_cbs_armed = true))
        log("ng cbs: draw ps %#llx dev %#llx cue %#llx cb13 %#llx flip %llu", (unsigned long long)log_ps, (unsigned long long)dev,
            (unsigned long long)(ctx + 0xC0), (unsigned long long)d->cb[1][13].addr, (unsigned long long)gpu_flip_count());
    d->clip = field<uint32_t>(dev, 0x25D0);
    d->su_sc_mode = field<uint32_t>(dev, 0x25D4);
    d->blend = field<uint32_t>(dev, 0x25D8);
    d->depth_ctl = field<uint32_t>(dev, 0x25DC);
    d->stencil_ctl = field<uint32_t>(dev, 0x25E0);
    d->stencil_ref = field<uint32_t>(dev, 0x25E4);
    d->target_mask = eb<uint32_t>(0x15D16E0 + uint64_t(field<uint32_t>(dev, kBlendIndex)) * 0x24);
    const uint64_t rast = 0x15D2424 + uint64_t(field<uint32_t>(dev, kRasterIndex)) * 0xC;
    d->poly_offset = eb<float>(rast) * 2.0f;
    d->poly_scale = eb<float>(rast + 4) * eb<float>(0x165FE78);
    for (int i = 0; i < 4; ++i) d->vp[i] = field<int32_t>(dev, 0x2578 + 4 * i);
    d->znear = field<float>(dev, 0x2588), d->zfar = field<float>(dev, 0x258C), d->zk = eb<float>(0x165FEA0);
    for (int i = 0; i < 5; ++i) std::memcpy(d->color[i], reinterpret_cast<const void*>(dev + kColorTarget0 + 0x2C * i), 44);
    std::memcpy(d->depth, reinterpret_cast<const void*>(dev + 0x26B0), 52);
    static const bool res_stats = getenv("D1_ND_RES_STATS") != nullptr;
    if (res_stats) resstats::note(dev, d);
    static const bool res_events = getenv("D1_ND_RES_EVENTS") != nullptr;
    if (res_events) resev_check_draw(dev);
    return d;
}

// Draw records are recycled (a few thousand a frame, ~5 KB each): recording threads take
// them in batches from a shared free list, the submitting thread gives them back.
std::mutex g_free_m;
std::vector<ng::Draw*> g_free;
ng::Draw* alloc_draw() {
    thread_local std::vector<ng::Draw*> cache;
    if (cache.empty()) {
        std::lock_guard lk(g_free_m);
        const size_t n = std::min<size_t>(g_free.size(), 128);
        cache.assign(g_free.end() - n, g_free.end());
        g_free.resize(g_free.size() - n);
    }
    if (cache.empty()) return new ng::Draw;
    ng::Draw* d = cache.back();
    cache.pop_back();
    // back to the defaults capture() relies on (it writes the shader resources it marks in
    // tex_mask / smp_mask, every constant buffer slot, the registers and the targets itself)
    d->kind = ng::Draw::Auto, d->prim = 4, d->index32 = 0, d->clear_flags = 0;
    d->count = 0, d->instances = 1, d->index_addr = 0, d->order = 0, d->seq = 0, d->frame = 0, d->caller = 0;
    d->vs = d->ps = nullptr, d->num_vb = 0;
    std::memset(d->vb, 0, sizeof d->vb);
    for (auto& r : d->vres) r = {};
    d->ires = {};
    d->tex_mask[0] = d->tex_mask[1] = d->smp_mask[0] = d->smp_mask[1] = 0;
    d->clear_color[0] = d->clear_color[1] = d->clear_color[2] = d->clear_color[3] = 0;
    d->clear_depth = 1, d->clear_stencil = 0;
    d->inline_vertices.clear();
    return d;
}
void release_draws(std::vector<ng::Draw*>& ds) {
    std::lock_guard lk(g_free_m);
    for (ng::Draw* d : ds) {
        if (g_free.size() >= 65536) delete d;
        else {
            if (d->inline_vertices.capacity() > 65536) d->inline_vertices = {};
            g_free.push_back(d);
        }
    }
    ds.clear();
}
void release_draw(ng::Draw* d) {
    std::vector<ng::Draw*> v{d};
    release_draws(v);
}

// Each recording thread (the engine's render jobs record on up to 7 device contexts at once)
// queues its draws and constant-buffer events in its own inbox; the submitting thread drains
// every inbox into the pending maps. (One lock shared by all of them made the recording
// threads wait on each other for every draw.)
struct Inbox {
    std::mutex m;
    std::vector<ng::Draw*> draws;
    std::vector<CbEvent> cbs;
};
std::vector<Inbox*> g_inboxes;  // (under g_m; never freed: one per thread that ever recorded)
Inbox& inbox() {
    thread_local Inbox* ib = nullptr;
    if (!ib) {
        ib = new Inbox;
        std::lock_guard lk(g_m);
        g_inboxes.push_back(ib);
    }
    return *ib;
}
void push(ng::Draw* d) {
    if (nd_push(t_capture_dev, d)) return;
    d->seq = g_seq.fetch_add(1, std::memory_order_relaxed);
    d->frame = uint32_t(gpu_flip_count());
    Inbox& ib = inbox();
    std::lock_guard lk(ib.m);
    ib.draws.push_back(d);
}
// (g_m held) everything recorded so far into g_pending / g_cb_pending
void drain_inboxes() {
    std::vector<ng::Draw*> ds;
    std::vector<CbEvent> cs;
    const size_t old_d = g_pending.size(), old_c = g_cb_pending.size();
    for (Inbox* ib : g_inboxes) {
        {
            std::lock_guard lk(ib->m);
            ds.swap(ib->draws);
            cs.swap(ib->cbs);
        }
        for (ng::Draw* d : ds) g_pending.push_back({d->order, d});
        g_cb_pending.insert(g_cb_pending.end(), cs.begin(), cs.end());
        ds.clear(), cs.clear();
    }
    // stable: each thread's records with equal positions stay in the order they were made
    auto by_pos = [](const auto& a, const auto& b) { return a.first < b.first; };
    std::stable_sort(g_pending.begin() + ptrdiff_t(old_d), g_pending.end(), by_pos);
    std::inplace_merge(g_pending.begin(), g_pending.begin() + ptrdiff_t(old_d), g_pending.end(), by_pos);
    auto ev_pos = [](const CbEvent& a, const CbEvent& b) { return a.order < b.order; };
    std::stable_sort(g_cb_pending.begin() + ptrdiff_t(old_c), g_cb_pending.end(), ev_pos);
    std::inplace_merge(g_cb_pending.begin(), g_cb_pending.begin() + ptrdiff_t(old_c), g_cb_pending.end(), ev_pos);
}

// Occlusion counter dumps and predication packets of the submission being collected, as
// pseudo-draws at their command-buffer positions (dcb_ranges fills it while set).
std::vector<std::pair<uint64_t, ng::Draw*>>* g_dcb_events = nullptr;

// Collect the DCB ranges of a submission, following INDIRECT_BUFFER packets.
int g_wait_phase = 0;  // diagnostics: 1 = after the null GPU ran the command buffers
// The ranges come out in execution order: a buffer is split at each INDIRECT_BUFFER packet,
// with the called buffer's ranges between the two halves, so recording positions in different
// buffers (a deferred context called from the main one) sort as the GPU runs them.
void dcb_ranges(const uint32_t* p, uint32_t dwords, int depth, std::vector<std::pair<uint64_t, uint64_t>>& out) {
    const uint64_t end = uint64_t(p) + uint64_t(dwords) * 4;
    if (depth >= 4) {
        out.push_back({uint64_t(p), end});
        return;
    }
    uint64_t cursor = uint64_t(p);
    for (uint32_t i = 0; i < dwords;) {
        const uint32_t h = p[i];
        const uint32_t type = h >> 30;
        if (type == 3) {
            const uint32_t op = (h >> 8) & 0xFF, count = (h >> 16) & 0x3FFF;
            // D1_NG_LOG_WAITS: WAIT_REG_MEM on memory that is not satisfied at submit time
            static const bool log_waits = getenv("D1_NG_LOG_WAITS") != nullptr;
            if (log_waits && g_wait_phase == 1 && op == 0x3C && i + 6 < dwords && (p[i + 1] >> 4 & 1)) {
                const uint32_t fn = p[i + 1] & 7, ref = p[i + 4], mask = p[i + 5];
                const uint64_t a = (uint64_t(p[i + 2]) | uint64_t(p[i + 3]) << 32) & ~3ull;
                const uint32_t v = a >= 0x10000 ? *reinterpret_cast<const volatile uint32_t*>(a) & mask : 0;
                const bool ok = fn == 0 || (fn == 1 && v < ref) || (fn == 2 && v <= ref) || (fn == 3 && v == ref) ||
                                (fn == 4 && v != ref) || (fn == 5 && v >= ref) || (fn == 6 && v > ref);
                static std::atomic<uint64_t> total{0}, bad{0};
                ++total;
                if (!ok) {
                    static std::unordered_map<uint64_t, int> seen;
                    if (++bad <= 200 || seen[a]++ < 3)
                        log("ng wait: unsatisfied at submit: [%#llx] & %#x %s %#x (now %#x), %llu of %llu waits",
                            (unsigned long long)a, mask, fn == 3 ? "==" : fn == 4 ? "!=" : fn == 5 ? ">=" : fn == 6 ? ">" : "<",
                            ref, v, (unsigned long long)bad.load(), (unsigned long long)total.load());
                }
            }
            if (g_dcb_events && i + 2 < dwords) {
                const uint32_t* b = p + i + 1;
                if (op == 0x46 && ((b[0] >> 8) & 0xF) == 1 && ((b[0] & 0x3F) == 0x39 || (b[0] & 0x3F) == 0x15) && count >= 2) {
                    auto* e = new ng::Draw;
                    e->kind = ng::Draw::ZPass;
                    e->index_addr = uint64_t(b[1] & ~7u) | (uint64_t(b[2] & 0xFFFF) << 32);
                    g_dcb_events->push_back({uint64_t(p + i), e});
                } else if (op == 0x50 && count >= 5) {  // DMA_DATA
                    const uint32_t src_sel = (b[0] >> 29) & 3, dst_sel = (b[0] >> 20) & 3;
                    if ((dst_sel == 0 || dst_sel == 3) && (src_sel == 0 || src_sel == 2 || src_sel == 3)) {
                        auto* e = new ng::Draw;
                        e->kind = ng::Draw::Dma;
                        e->index_addr = b[1] | (uint64_t(b[2]) << 32);
                        e->caller = b[3] | (uint64_t(b[4]) << 32);
                        e->count = b[5] & 0x1FFFFF;
                        e->prim = uint8_t(src_sel), e->index32 = uint8_t(dst_sel), e->instances = b[1];
                        g_dcb_events->push_back({uint64_t(p + i), e});
                    }
                } else if (op == 0x37 && count >= 3) {  // WRITE_DATA to memory
                    const uint32_t dst_sel = (b[0] >> 8) & 0xF;
                    if (dst_sel == 2 || dst_sel == 5) {
                        auto* e = new ng::Draw;
                        e->kind = ng::Draw::WriteData;
                        e->caller = b[1] | (uint64_t(b[2]) << 32);
                        e->inline_vertices.assign(reinterpret_cast<const uint8_t*>(b + 3), reinterpret_cast<const uint8_t*>(b + 3) + (count - 2) * 4);
                        g_dcb_events->push_back({uint64_t(p + i), e});
                    }
                } else if (op == 0x20 && count >= 1) {
                    auto* e = new ng::Draw;
                    const uint32_t pred_op = (b[1] >> 16) & 7;
                    e->kind = pred_op ? ng::Draw::PredOn : ng::Draw::PredOff;
                    e->index_addr = uint64_t(b[0] & ~15u) | (uint64_t(b[1] & 0xFF) << 32);
                    e->count = (b[1] >> 8) & 1;  // draw if visible
                    g_dcb_events->push_back({uint64_t(p + i), e});
                }
            }
            if ((op == 0x3F || op == 0x33) && i + 3 < dwords) {
                const uint64_t a = uint64_t(p[i + 1]) | (uint64_t(p[i + 2] & 0xFFFF) << 32);
                if (a) {
                    const uint64_t after = uint64_t(p + std::min(i + count + 2, dwords));
                    out.push_back({cursor, after});
                    cursor = after;
                    dcb_ranges(reinterpret_cast<const uint32_t*>(a), p[i + 3] & 0xFFFFF, depth + 1, out);
                }
            }
            i += count + 2;
        } else if (type == 2) {
            i += 1;
        } else {
            i += ((h >> 16) & 0x3FFF) + 2;
        }
    }
    if (cursor < end) out.push_back({cursor, end});
}

}  // namespace nr

using DrawInstancedFn = D1_SYSV void (*)(uint64_t, uint32_t, uint32_t, uint64_t, uint32_t);
using DrawQuadsFn = D1_SYSV void (*)(uint64_t, uint32_t, uint64_t, int32_t);
using DrawInlineFn = D1_SYSV void (*)(uint64_t, uint32_t, int32_t, const void*, int32_t);
using ClearFn = D1_SYSV void (*)(uint64_t, uint32_t);
DrawInstancedFn o_draw_instanced;
using DrawIndexedInstancedFn = D1_SYSV void (*)(uint64_t, uint32_t, uint32_t, uint64_t, uint32_t, uint64_t, uint32_t);
DrawIndexedInstancedFn o_draw_indexed_instanced;
DrawQuadsFn o_draw_quads;
DrawInlineFn o_draw_inline;
ClearFn o_clear;

// Draws are only captured: the engine's Gnm draw code (constant update engine preDraw /
// postDraw, draw packets) does not run, so the command buffers carry state and events only
// (the null GPU still answers fences and labels from them). D1_NG_GNM_DRAWS=1 runs it too.
bool gnm_draws() {
    static const bool on = [] { const char* v = getenv("D1_NG_GNM_DRAWS"); return v && atoi(v) != 0; }();
    return on;
}
thread_local uint32_t t_instances = 1;  // set by the instanced draw around its draw_indexed call
D1_SYSV void r_draw_indexed(uint64_t dev, uint64_t prim, uint64_t a, int32_t first, uint32_t count) {
    if (field<uint8_t>(dev, 0x26)) {
        ng::Draw* d = nr::capture(dev, uint32_t(prim), uint64_t(__builtin_return_address(0)));
        d->kind = ng::Draw::Indexed;
        const uint64_t ib = field<uint64_t>(dev, 0x1D70);
        const uint32_t isz = ib ? field<uint32_t>(ib, 0x38) : 0;
        d->index32 = isz != 0;
        d->index_addr = ib ? field<uint64_t>(ib, 0x30) + uint64_t(uint32_t((isz * 2 + 2) * first)) : 0;
        if (ib && nr::resreg::g_on) d->ires = {nr::resreg::get(ib), field<uint64_t>(ib, 0x30), uint64_t(field<uint32_t>(ib, 0x3C)) * (isz ? 4 : 2)};
        d->count = count;
        d->instances = t_instances;
        nr::push(d);
    }
    if (gnm_draws()) o_draw_indexed(dev, prim, a, first, count);
}
D1_SYSV void r_draw(uint64_t dev, uint64_t prim, uint32_t count) {
    if (field<uint8_t>(dev, 0x26)) {
        ng::Draw* d = nr::capture(dev, uint32_t(prim), uint64_t(__builtin_return_address(0)));
        d->kind = ng::Draw::Auto;
        d->count = count;
        nr::push(d);
    }
    if (gnm_draws()) o_draw(dev, prim, count);
}
D1_SYSV void r_draw_instanced(uint64_t dev, uint32_t prim, uint32_t count, uint64_t a, uint32_t instances) {
    if (field<uint8_t>(dev, 0x26)) {
        ng::Draw* d = nr::capture(dev, prim, uint64_t(__builtin_return_address(0)));
        d->kind = ng::Draw::Auto;
        d->count = count, d->instances = instances;
        nr::push(d);
    }
    if (gnm_draws()) o_draw_instanced(dev, prim, count, a, instances);
}
// draw_indexed_instanced(prim, count, ?, instances, ?, first): NUM_INSTANCES around draw_indexed
D1_SYSV void r_draw_indexed_instanced(uint64_t dev, uint32_t prim, uint32_t count, uint64_t a, uint32_t instances,
                                      uint64_t b, uint32_t first) {
    t_instances = instances ? instances : 1;
    o_draw_indexed_instanced(dev, prim, count, a, instances, b, first);
    t_instances = 1;
}
// indexed from the engine's shared 16-bit index buffer (*device->manager)
D1_SYSV void r_draw_quads(uint64_t dev, uint32_t prim, uint64_t first, int32_t prims) {
    ng::Draw* d = nr::capture(dev, prim, uint64_t(__builtin_return_address(0)));
    d->kind = ng::Draw::Indexed;
    d->index_addr = field<uint64_t>(field<uint64_t>(dev, 0), 0) + (first & 0xFFFFFFFF) * 2;
    d->count = nr::vertex_count(prim, uint32_t(prims));
    nr::push(d);
    if (gnm_draws()) o_draw_quads(dev, prim, first, prims);
}
D1_SYSV void r_draw_inline(uint64_t dev, uint32_t prim, int32_t prims, const void* data, int32_t stride) {
    const uint64_t decl = field<uint64_t>(dev, kVertexDecl);
    if (decl && data) {
        ng::Draw* d = nr::capture(dev, prim, uint64_t(__builtin_return_address(0)));
        d->kind = ng::Draw::Auto;
        d->count = nr::vertex_count(prim, uint32_t(prims));
        d->inline_vertices.assign(static_cast<const uint8_t*>(data),
                                  static_cast<const uint8_t*>(data) + size_t(d->count) * uint32_t(stride));
        std::memset(d->vb, 0, sizeof d->vb);
        const uint32_t n = std::min(field<uint32_t>(decl, 0), 16u);
        d->num_vb = n;
        for (uint32_t i = 0; i < n; ++i)
            nr::build_vsharp(d->vb[i], field<uint8_t>(decl, 0x18 + 8 * i),  // offset into inline_vertices
                             field<uint32_t>(decl, 0x14 + 8 * i), uint32_t(stride), d->count);
        nr::push(d);
    }
    if (gnm_draws()) o_draw_inline(dev, prim, prims, data, stride);
}
// clear(flags): bits 2..5 color MRT 0..3 with the color at +0x40, 0x40 depth (+0x20, stored
// reversed unless +0x24), 0x80 stencil (+0x25)
D1_SYSV void r_clear(uint64_t dev, uint32_t flags) {
    if (flags & 0xFC) {
        ng::Draw* d = nr::capture(dev, 0);
        d->kind = ng::Draw::Clear;
        d->clear_flags = uint8_t(flags);
        std::memcpy(d->clear_color, reinterpret_cast<const void*>(dev + 0x40), 16);
        const float z = field<float>(dev, 0x20);
        d->clear_depth = field<uint8_t>(dev, 0x24) ? z : nr::eb<float>(0x165FEB4) - z;
        d->clear_stencil = field<uint8_t>(dev, 0x25);
        // the engine clears stencil with a draw whose write mask is the byte at +0x25EC (0x7E2819)
        d->stencil_ref = (d->stencil_ref & 0xFF00FFFFu) | uint32_t(field<uint8_t>(dev, 0x25EC)) << 16;
        nr::push(d);
    }
    o_clear(dev, flags);
}
D1_SYSV uint64_t r_alloc_constants(uint64_t dev, uint32_t stage, uint32_t slot, uint32_t bytes) {
    const uint64_t p = o_alloc_constants(dev, stage, slot, bytes);
    const int s = nr::gnm_stage_index(stage);
    if (s >= 0 && slot < 16) nr::dev_state(dev)->cb[s][slot] = {p, bytes};
    return p;
}
D1_SYSV void r_set_vertex_buffer(uint64_t dev, uint32_t handle, uint32_t stream, uint32_t offset, int32_t count) {
    const uint64_t decl = field<uint64_t>(dev, kVertexDecl);
    const uint32_t s = stream & 0xFFFF;
    const uint32_t stride = decl && s < 32 ? field<uint32_t>(decl, 4 + 4 * (s & 3)) : 0;
    if (handle != 0xFFFFFFFFu && s < 32 && stride) {  // the cases the engine resolves the handle in
        uint32_t n = field<uint32_t>(nr::resolve_handle(handle), 0x30);
        if (offset != 0) n = count ? uint32_t(count) : n - (stride ? offset / stride : 0);
        nr::dev_state(dev)->vb_count[s] = n;
    }
    o_set_vertex_buffer(dev, handle, stream, offset, count);
}

using SetCbsFn = D1_SYSV void (*)(uint64_t, uint32_t, uint32_t, uint32_t, const uint32_t*);
SetCbsFn o_set_cbs;
D1_SYSV void r_set_cbs(uint64_t cue, uint32_t stage, uint32_t first, uint32_t count, const uint32_t* vs) {
    o_set_cbs(cue, stage, first, count, vs);
    const int s = nr::gnm_stage_index(stage);
    if (s < 0) return;
    nr::CueState* c = nr::cue_state(cue, true);
    // D1_NG_LOG_CBS=<slot>: who binds this pixel-shader constant buffer slot
    static const int log_slot = [] { const char* v = getenv("D1_NG_LOG_CBS"); return v ? atoi(v) : -1; }();
    if (log_slot >= 0 && s == 1 && uint32_t(log_slot) >= first && uint32_t(log_slot) < first + count) {
        static std::mutex lm;
        static std::map<std::pair<uint64_t, uint64_t>, int> seen;
        const uint64_t ra = uint64_t(__builtin_return_address(0)) - nr::g_base;
        bool show;
        {
            std::lock_guard lk(lm);
            static int total = 0;
            show = nr::g_cbs_armed && total++ < 3000;
            (void)seen;
        }
        if (show) {
            const uint32_t* v = vs ? vs + 4 * (log_slot - first) : nullptr;
            log("ng cbs: cue %#llx ps slot %d = %#llx from %#llx flip %llu", (unsigned long long)cue, log_slot,
                v ? (unsigned long long)(uint64_t(v[0]) | uint64_t(v[1] & 0xFFF) << 32) : 0ull,
                (unsigned long long)(uint64_t(__builtin_return_address(0)) - nr::g_base), (unsigned long long)gpu_flip_count());
        }
    }
    const uint64_t order = field<uint64_t>(cue - 0xC0, 0x10);
    nr::Inbox& ib = nr::inbox();
    std::lock_guard lk(ib.m);
    for (uint32_t k = 0; k < count && first + k < 16; ++k) {
        ng::Draw::Cb& cb = c->cb[s][first + k];
        if (!vs) {
            cb = {};
        } else {
            const uint32_t* v = vs + 4 * k;
            const uint64_t base = uint64_t(v[0]) | uint64_t(v[1] & 0xFFF) << 32;
            const uint32_t stride = v[1] >> 16 & 0x3FFF, records = v[2];
            const uint64_t bytes = stride ? uint64_t(stride) * records : records;
            cb = {base, uint32_t(std::min<uint64_t>(bytes, 1u << 20))};
        }
        if (nr::g_ce_order && order)
            ib.cbs.push_back(nr::CbEvent{order, nr::g_seq.fetch_add(1, std::memory_order_relaxed), uint8_t(s), uint8_t(first + k), cb});
    }
}

// engine dispatch(dev, cs object, x, y, z, flag): compute work on the graphics ring
using DispatchFn = D1_SYSV void (*)(uint64_t, uint64_t, uint32_t, uint32_t, uint32_t, int32_t);
DispatchFn o_dispatch;
D1_SYSV void r_dispatch(uint64_t dev, uint64_t cs, uint32_t x, uint32_t y, uint32_t z, int32_t flag) {
    static const bool census = getenv("D1_NG_LOG_DISPATCH") != nullptr;
    if (census) {
        // caller chain (frame pointers): who asks for compute
        uint64_t chain[4] = {};
        uint64_t* fp = static_cast<uint64_t*>(__builtin_frame_address(0));
        for (int i = 0; i < 4 && fp; ++i) {
            chain[i] = fp[1] - nr::g_base;
            uint64_t* nfp = reinterpret_cast<uint64_t*>(fp[0]);
            if (nfp <= fp) break;
            fp = nfp;
        }
        static std::mutex m;
        static std::unordered_map<uint64_t, uint64_t> seen;
        std::lock_guard lk(m);
        const uint64_t key = chain[1] ^ (chain[2] << 20) ^ (chain[3] << 40) ^ cs;
        if (seen[key]++ < 2) {
            log("ng dispatch: cs %#llx groups %u x %u x %u flag %d | from %#llx < %#llx < %#llx < %#llx", (unsigned long long)cs,
                x, y, z, flag, (unsigned long long)chain[0], (unsigned long long)chain[1], (unsigned long long)chain[2],
                (unsigned long long)chain[3]);
            const uint32_t* w = reinterpret_cast<const uint32_t*>(cs);
            std::string hex;
            for (int i = 0; i < 32; ++i) {
                char b[12];
                std::snprintf(b, sizeof b, " %08x", w[i]);
                hex += b;
            }
            log("ng dispatch: cs object%s", hex.c_str());
            if (const char* dir = getenv("D1_NG_DUMP_GCN")) {
                char path[512];
                std::snprintf(path, sizeof path, "%s/cs_%#llx.code", dir, (unsigned long long)cs);
                if (FILE* f = std::fopen(path, "wb")) {
                    std::fwrite(reinterpret_cast<const void*>(uint64_t(w[2]) << 8 | uint64_t(w[3]) << 40), 1, w[0] & 0x7FFFFF, f);
                    std::fclose(f);
                }
            }
        }
    }
    const uint64_t ctx = field<uint64_t>(dev, 0x50);
    const uint64_t before = ctx ? field<uint64_t>(ctx, 0x10) : 0;
    o_dispatch(dev, cs, x, y, z, flag);
    const uint64_t after = ctx ? field<uint64_t>(ctx, 0x10) : 0;
    if (census && before && after > before && after - before < 4096) {
        // the user data the engine wrote for this dispatch (SET_SH_REG COMPUTE_USER_DATA_*)
        uint32_t ud[16] = {};
        const uint32_t* p = reinterpret_cast<const uint32_t*>(before);
        const uint32_t n = uint32_t((after - before) / 4);
        for (uint32_t i = 0; i < n;) {
            const uint32_t h = p[i], type = h >> 30, count = (h >> 16) & 0x3FFF;
            if (type == 3 && ((h >> 8) & 0xFF) == 0x76 && i + 1 < n) {
                const uint32_t reg = p[i + 1] & 0xFFFF;
                for (uint32_t k = 0; k < count && i + 2 + k < n; ++k)
                    if (reg + k >= 0x240 && reg + k < 0x250) ud[reg + k - 0x240] = p[i + 2 + k];
            }
            i += type == 2 ? 1 : count + 2;
        }
        static int logged = 0;
        if (logged++ < 6) {
            const auto src = fmt::decode_tsharp(ud + 4);
            const uint32_t* dt = reinterpret_cast<const uint32_t*>(uint64_t(ud[2]) | uint64_t(ud[3]) << 32);
            const uint64_t cbb = uint64_t(ud[12]) | uint64_t(ud[13] & 0xFFF) << 32;
            const uint32_t* cb = reinterpret_cast<const uint32_t*>(cbb);
            if (dt && cb) {
                const auto dst = fmt::decode_tsharp(dt);
                log("ng dispatch: src %llx %ux%u f%u.%u tile %u | dst %llx %ux%u f%u.%u tile %u | cb %u %u %u %u %u %u",
                    (unsigned long long)src.base, src.width, src.height, src.dfmt, src.nfmt, src.tiling,
                    (unsigned long long)dst.base, dst.width, dst.height, dst.dfmt, dst.nfmt, dst.tiling, cb[0], cb[1], cb[2],
                    cb[3], cb[4], cb[5]);
            }
        }
    }
}


template <class F>
bool hook(uint64_t off, F host, F& orig, const char* name) {
    orig = reinterpret_cast<F>(hook_eboot_function(off, reinterpret_cast<const void*>(host)));
    if (!orig) log("native gfx: hooking %s (eboot+%#llx) failed", name, (unsigned long long)off);
    return orig != nullptr;
}


// ---------------------------------------------------------------------------- resource events (research)
// D1_ND_RES_EVENTS=1: the engine's core resource manager drives the platform graphics layer
// through a callback table (registered by 0x7D3400 into 0x254EE30..0x254EEA0): bind memory to
// a resource by type (0x7D2E80), re-point it after a move (0x7D3160), release (0x7D2FE0), GPU
// copy for a move (0x7D3560), commit a move (0x7D37B0), rebuild a texture for its resident
// mips (0x7D4480). This counts the events, registers every bound buffer / texture with a hash
// of its contents, and checks at draws whether what is drawn was bound by an event and is
// unchanged since.
namespace resev {
std::mutex m;
struct Res { uint32_t type, handle; uint64_t obj, size, hash; uint64_t flip; bool drawn = false; };
std::map<uint64_t, Res> by_base;  // base address -> resource
std::map<std::pair<int, uint32_t>, uint64_t> counts;  // (callback, type) -> events
uint64_t draw_reg = 0, draw_unreg = 0, draw_same = 0, draw_changed = 0, tex_reg = 0, tex_unreg = 0, tex_same = 0, tex_changed = 0;
uint64_t sample_same = 0, sample_changed = 0, overlaps = 0, tex_by_type[32] = {}, rebind_same = 0, rebind_diff = 0;
uint64_t hash_full(uint64_t a, uint64_t n);
// (sampled: the first, middle and last 4 KiB)
uint64_t hash(uint64_t a, uint64_t n) {
    if (n <= 12288) return hash_full(a, n);
    return hash_full(a, 4096) ^ hash_full(a + (n / 2 & ~4095ull), 4096) * 3 ^ hash_full(a + n - 4096, 4096) * 7 ^ n;
}
uint64_t hash_full(uint64_t a, uint64_t n) {
    if (a < 0x10000 || !n || guest_region_extent(a) < n) return 0;
    const uint8_t* p = reinterpret_cast<const uint8_t*>(a);
    uint64_t h = 0xcbf29ce484222325ull;
    uint64_t i = 0;
    for (; i + 8 <= n; i += 8) {
        uint64_t v;
        std::memcpy(&v, p + i, 8);
        h = (h ^ v) * 0x100000001b3ull;
    }
    for (; i < n; ++i) h = (h ^ p[i]) * 0x100000001b3ull;
    return h | 1;
}
uint64_t tex_size(const uint32_t* t) {
    const auto ts = fmt::decode_tsharp(t);
    const auto fi = fmt::data_format(ts.dfmt);
    if (!fi.bpp || fi.bpp == 96 || !ts.width) return 0;
    tiling::Surface sf;
    sf.tile_mode = ts.tiling, sf.bpp = fi.bpp, sf.block = fi.block, sf.pow2 = ts.pow2;
    sf.width = ts.width, sf.height = ts.height, sf.pitch = ts.pitch;
    sf.depth = ts.type == 10 ? ts.depth : 1;
    sf.layers = (ts.type == 13 || ts.type == 11) ? ts.last_array + 1 : 1;
    sf.levels = std::min(ts.last_level + 1, tiling::kMaxMips);
    tiling::layout(sf);
    return std::min<uint64_t>(sf.total_size, 256ull << 20);
}
uint64_t tex_base(const uint32_t* t) { return (uint64_t(t[0]) | uint64_t(t[1] & 0xFF) << 32) << 8; }
// the resource's memory after a bind event
void reg(int cb, uint32_t type, uint32_t handle) {
    if (handle == 0xFFFFFFFFu) return;
    const uint64_t obj = nr::resolve_handle(handle);
    if (obj < 0x10000) return;
    uint64_t base = 0, size = 0;
    switch (type) {
    case 1: case 2: case 3: base = tex_base(reinterpret_cast<const uint32_t*>(obj)), size = tex_size(reinterpret_cast<const uint32_t*>(obj)); break;
    case 4: base = field<uint64_t>(obj, 0x28), size = field<uint32_t>(obj, 0); break;
    case 6: base = field<uint64_t>(obj, 0x30), size = field<uint64_t>(obj, 8); break;
    case 8: base = tex_base(reinterpret_cast<const uint32_t*>(obj + 8)), size = tex_size(reinterpret_cast<const uint32_t*>(obj + 8)); break;
    default: return;
    }
    if (!base || !size) return;
    const uint64_t h = hash(base, size);
    // anything registered in this range before is gone (its memory is reused)
    auto it = by_base.lower_bound(base > (256ull << 20) ? base - (256ull << 20) : 0);
    while (it != by_base.end() && it->first < base + size) {
        if (it->first + it->second.size > base && it->first != base) ++overlaps, it = by_base.erase(it);
        else ++it;
    }
    by_base[base] = {type, handle, obj, size, h, gpu_flip_count()};
    // a re-point: is the content the same as at the handle's last registration?
    static std::unordered_map<uint32_t, std::pair<uint64_t, uint64_t>> last;  // handle -> (hash, size)
    auto& prev = last[handle];
    if (cb == 1 && prev.first) {
        if (prev.first == h && prev.second == size) ++rebind_same;
        else {
            ++rebind_diff;
            static int told = 0;
            if (told++ < 12) log("nd res events: re-point with different content: type %u handle %#x size %llu (was %llu)", type, handle,
                                 (unsigned long long)size, (unsigned long long)prev.second);
        }
    }
    prev = {h, size};
}
using SetFn = D1_SYSV uint64_t (*)(uint32_t, uint32_t, uint64_t);
SetFn o_bind, o_rebind;
bool g_research = false;
D1_SYSV uint64_t h_bind(uint32_t type, uint32_t handle, uint64_t addr) {
    const uint64_t r = o_bind(type, handle, addr);
    nr::resreg::event(type, handle, true);
    if (!g_research) return r;
    std::lock_guard lk(m);
    ++counts[{0, type}];
    reg(0, type, handle);
    return r;
}
D1_SYSV uint64_t h_rebind(uint32_t type, uint32_t handle, uint64_t addr) {
    const uint64_t r = o_rebind(type, handle, addr);
    nr::resreg::event(type, handle, true);
    if (!g_research) return r;
    std::lock_guard lk(m);
    ++counts[{1, type}];
    reg(1, type, handle);
    return r;
}
using RelFn = D1_SYSV void (*)(uint32_t, uint32_t);
RelFn o_release;
D1_SYSV void h_release(uint32_t type, uint32_t handle) {
    o_release(type, handle);
    nr::resreg::event(type, handle, false);
    if (!g_research) return;
    std::lock_guard lk(m);
    ++counts[{2, type}];
    if (type >= 1 && type <= 3) reg(2, type, handle);  // (textures: the descriptor now names fewer mips)
}
using Two = D1_SYSV void (*)(uint64_t, uint64_t);
Two o_copy, o_swap;
D1_SYSV void h_copy(uint64_t a, uint64_t b) {
    o_copy(a, b);
    nr::resreg::event_any(uint32_t(a)), nr::resreg::event_any(uint32_t(b));
    if (!g_research) return;
    std::lock_guard lk(m);
    ++counts[{3, 0}];
}
D1_SYSV void h_swap(uint64_t a, uint64_t b) {
    o_swap(a, b);
    nr::resreg::event_any(uint32_t(a)), nr::resreg::event_any(uint32_t(b));
    if (!g_research) return;
    std::lock_guard lk(m);
    ++counts[{4, 0}];
}
using MipFn = D1_SYSV void (*)(uint32_t, uint64_t, uint64_t);
MipFn o_mips;
D1_SYSV void h_mips(uint32_t handle, uint64_t base, uint64_t lo) {
    o_mips(handle, base, lo);
    nr::resreg::event(1, handle, false);  // (a texture: its descriptor names other mips now)
    if (!g_research) return;
    std::lock_guard lk(m);
    ++counts[{5, 0}];
    reg(5, 1, handle);
}
// The engine's dynamic textures (a table of 0xE0-byte slots at 0x26F23B0, also used for render
// targets) are written by the CPU between lock (0x818F80) and unlock (0x818FA0), like a PC
// engine's Map / Unmap: the unlock is the event that the slot's memory changed.
// (replaced, not hooked: the engine's unlock only clears the slot's locked bit, 0x81A640)
D1_SYSV void h_unlock(uint64_t idx) {
    const uint64_t e = nr::g_base + 0x26F23B0 + (idx & 0xFFFFFFFFull) * 0xE0;
    const uint64_t ptr = field<uint64_t>(e, (field<uint32_t>(e, 0) & 8) ? 0x48 : 0x40);
    *reinterpret_cast<uint8_t*>(e + 2) &= 0xFB;
    static const bool log_unlock = getenv("D1_ND_LOG_UNLOCK") != nullptr;
    if (log_unlock) {
        static std::atomic<int> told{0};
        if (told++ < 40) {
            const auto ts = fmt::decode_tsharp(reinterpret_cast<const uint32_t*>(e + 4));
            log("nd texture unlock: slot %llu memory %#llx pitch %u | T# at +4: base %#llx %ux%u fmt %u.%u tile %u type %u",
                (unsigned long long)(idx & 0xFFFFFFFFull), (unsigned long long)ptr, field<uint32_t>(e, 0xD8),
                (unsigned long long)ts.base, ts.width, ts.height, ts.dfmt, ts.nfmt, ts.tiling, ts.type);
        }
    }
    ng::cpu_wrote(ptr, 0);
}

// the callbacks are called through the table (0x254EE38 bind, 0x254EE40 re-point, 0x254EE48
// release): our wrappers go into it once the graphics layer has registered it (0xCFCC0)
using RegFn = D1_SYSV void (*)(uint64_t, uint64_t, uint64_t, uint64_t, uint64_t, uint64_t, uint64_t, uint64_t, uint64_t, uint64_t,
                               uint64_t, uint64_t, uint64_t, uint64_t, uint64_t, uint64_t);
RegFn o_register;
void patch_table() {
    auto slot = [](uint64_t off) { return reinterpret_cast<uint64_t*>(nr::g_base + off); };
    if (*slot(0x254EE38) && *slot(0x254EE38) != uint64_t(&h_bind)) o_bind = reinterpret_cast<SetFn>(*slot(0x254EE38)), *slot(0x254EE38) = uint64_t(&h_bind);
    if (*slot(0x254EE40) && *slot(0x254EE40) != uint64_t(&h_rebind)) o_rebind = reinterpret_cast<SetFn>(*slot(0x254EE40)), *slot(0x254EE40) = uint64_t(&h_rebind);
    if (*slot(0x254EE48) && *slot(0x254EE48) != uint64_t(&h_release)) o_release = reinterpret_cast<RelFn>(*slot(0x254EE48)), *slot(0x254EE48) = uint64_t(&h_release);
}
D1_SYSV void h_register(uint64_t a, uint64_t b, uint64_t c, uint64_t d, uint64_t e, uint64_t f, uint64_t g, uint64_t h, uint64_t i,
                        uint64_t j, uint64_t k, uint64_t l, uint64_t mm, uint64_t n, uint64_t o, uint64_t p) {
    o_register(a, b, c, d, e, f, g, h, i, j, k, l, mm, n, o, p);
    patch_table();
    log("nd: engine resource callbacks registered: bind / re-point / release wrapped");
}
void install() {
    bool ok = true;
    nr::resreg::init();
    g_research = getenv("D1_ND_RES_EVENTS") != nullptr;
    ok &= hook(0xCFCC0, &h_register, o_register, "resource_callbacks_register");
    if (!replace_eboot_function(0x818FA0, reinterpret_cast<const void*>(&h_unlock))) ok = false, log("nd: replacing texture_unlock failed");
    patch_table();  // (already registered)
    ok &= hook(0x7D3560, &h_copy, o_copy, "resource_move_copy");
    ok &= hook(0x7D37B0, &h_swap, o_swap, "resource_move_commit");
    ok &= hook(0x7D4480, &h_mips, o_mips, "texture_mips");
    log("nd: engine resource events %s (D1_ND_RES=0 turns them off)", ok ? "hooked" : "NOT HOOKED - resources stay write-tracked");
    if (!ok) nr::resreg::g_on = false;
}
// at a draw: the stream buffers and textures it uses
void check_draw(uint64_t dev) {
    std::lock_guard lk(m);
    auto check = [&](uint64_t base, bool tex, uint64_t size = 0, uint32_t handle = 0) {
        auto it = by_base.find(base);
        if (it == by_base.end() && size && base >= 0x10000) {  // first use: registered here
            by_base[base] = {tex ? 1u : 4u, handle, 0, size, hash(base, size), gpu_flip_count(), true};
            ++(tex ? tex_unreg : draw_unreg);
            return;
        }
        if (it == by_base.end()) { ++(tex ? tex_unreg : draw_unreg); return; }
        ++(tex ? tex_reg : draw_reg);
        if (tex) ++tex_by_type[it->second.type & 31];
        if (!it->second.drawn) {
            it->second.drawn = true;
            if (hash(base, it->second.size) == it->second.hash) ++(tex ? tex_same : draw_same);
            else ++(tex ? tex_changed : draw_changed);
        }
    };
    if (const uint64_t decl = field<uint64_t>(dev, 0x1D60)) {
        const uint32_t n = std::min(field<uint32_t>(decl, 0), 16u);
        uint32_t seen = 0;
        for (uint32_t i = 0; i < n; ++i) {
            const uint32_t stream = field<uint8_t>(decl, 0x19 + 8 * i) & 31;
            const uint32_t h = field<uint32_t>(dev, 0x1D78 + 4 * stream);
            if (h == 0xFFFFFFFFu || (seen >> stream & 1)) continue;
            seen |= 1u << stream;
            const uint64_t obj = nr::resolve_handle(h);
            if (obj >= 0x10000) check(field<uint64_t>(obj, 0x28), false, field<uint32_t>(obj, 0), h);
        }
    }
    if (const uint64_t ib = field<uint64_t>(dev, 0x1D70))
        check(field<uint64_t>(ib, 0x30), false, uint64_t(field<uint32_t>(ib, 0x3C)) * (field<uint32_t>(ib, 0x38) ? 4 : 2), field<uint32_t>(dev, 0x1D68));
    for (int st = 1; st <= 2; ++st)
        for (int i = 0; i < 16; ++i)
            if (const uint64_t t = field<uint64_t>(dev, 0x1E78 + st * 0x80 + i * 8); t >= 0x10000)
                check(tex_base(reinterpret_cast<const uint32_t*>(t)), true, tex_size(reinterpret_cast<const uint32_t*>(t)));
    static uint64_t last = 0;
    if (gpu_flip_count() >= last + 600) {
        last = gpu_flip_count();
        // a sample of registered resources: still what was bound?
        uint32_t k = 0;
        uint64_t bs = 0, bc = 0, ts = 0, tc = 0, bc_pool = 0;
        for (auto& [b, r] : by_base) {
            if (++k % 5) continue;
            const bool same = hash(b, r.size) == r.hash;
            if (!same && r.type != 4 && r.type != 6) {
                static int told = 0;
                if (told++ < 30) {
                    const uint64_t o = r.handle ? nr::resolve_handle_safe(r.handle) : 0;
                    const uint32_t* t = o ? reinterpret_cast<const uint32_t*>(o + (r.type == 8 ? 8 : 0)) : nullptr;
                    const auto ts = t ? fmt::decode_tsharp(t) : fmt::TSharp{};
                    log("nd res events: texture changed without an event: type %u handle %#x base %#llx size %llu bound flip %llu | now %ux%u fmt %u.%u tile %u levels %u-%u base %#llx",
                        r.type, r.handle, (unsigned long long)b, (unsigned long long)r.size, (unsigned long long)r.flip, ts.width, ts.height,
                        ts.dfmt, ts.nfmt, ts.tiling, ts.base_level, ts.last_level, (unsigned long long)ts.base);
                }
            }
            if (r.type == 4) {
                ++(same ? bs : bc);
                // changed: does the handle still resolve to a buffer at this address (pool still loaded)?
                if (!same && r.handle) {
                    const uint64_t o = nr::resolve_handle_safe(r.handle);
                    if (o < 0x10000 || field<uint64_t>(o, 0x28) != b) ++bc_pool;
                }
            } else ++(same ? ts : tc);
            r.hash = hash(b, r.size);
        }
        log("nd res events: sample of buffers %llu unchanged, %llu changed (%llu of them no longer named by their handle) | textures %llu unchanged, %llu changed",
            (unsigned long long)bs, (unsigned long long)bc, (unsigned long long)bc_pool, (unsigned long long)ts, (unsigned long long)tc);
        std::string t;
        static const char* names[] = {"bind", "rebind", "release", "move-copy", "move-commit", "mips"};
        for (auto& [k2, v] : counts) {
            char b[64];
            std::snprintf(b, sizeof b, " %s/%u:%llu", names[k2.first], k2.second, (unsigned long long)v);
            t += b;
        }
        log("nd res events:%s | registered %zu (%llu overlaps replaced) | re-points with the same content %llu, different %llu", t.c_str(),
            by_base.size(), (unsigned long long)overlaps, (unsigned long long)rebind_same, (unsigned long long)rebind_diff);
        log("nd res events: buffer uses %llu registered / %llu not (first use: %llu as bound, %llu changed) | textures %llu / %llu "
            "(%llu as bound, %llu changed) | sample: %llu unchanged, %llu changed since bound",
            (unsigned long long)draw_reg, (unsigned long long)draw_unreg, (unsigned long long)draw_same, (unsigned long long)draw_changed,
            (unsigned long long)tex_reg, (unsigned long long)tex_unreg, (unsigned long long)tex_same, (unsigned long long)tex_changed,
            (unsigned long long)sample_same, (unsigned long long)sample_changed);
        {
            std::string u;
            for (int i = 0; i < 32; ++i)
                if (tex_by_type[i]) u += " type" + std::to_string(i) + ":" + std::to_string(tex_by_type[i]), tex_by_type[i] = 0;
            log("nd res events: draw textures by resource type:%s", u.c_str());
        }
        draw_reg = draw_unreg = tex_reg = tex_unreg = 0;
    }
}
}  // namespace resev
namespace nr { void resev_check_draw(uint64_t dev) { resev::check_draw(dev); } }

// ---------------------------------------------------------------------------- native device layer
// D1_ND=1: no Sony graphics code and no emulated GPU. The engine's device layer
// (findings/gpu_device_layer.md) still runs - it is the game's code - but every Gnm / Gnmx
// function it calls that would build PS4 command buffers is replaced: they do nothing, or
// record what they mean into the calling context's command list (constant buffer bindings,
// end-of-list labels, end-of-pipe events, occlusion dumps, predication, GPU copies). Each
// device context's list (cmdlist_begin .. cmdlist_end) gets a token in its command buffer so
// the engine's own bookkeeping submits it in its order; at submission the lists named by
// the tokens are executed by the Vulkan renderer and their labels written
// (findings/gpu_device_sync_contract.md). Nothing parses PS4 packets.

namespace nd {
bool g_on = false;
constexpr uint32_t kMagic = 0x4E44544Bu;  // token: NOP {magic, id lo, id hi}
struct Item {
    ng::Draw* d = nullptr;  // null: a constant buffer binding
    nr::CbEvent cb{};
};
struct List {
    uint64_t id = 0, dev = 0;
    std::vector<Item> items;
    std::vector<uint8_t*> chunks;  // command-buffer allocations (constants, inline data), arena chunks
    size_t used = 0;
    bool eop = false;
    uint64_t made = 0;  // flip count when begun (cleanup of lists never submitted)
    // recorded on the thread that ended it (ng::record_list): its submission slot, the
    // constant buffers it inherits (filled at submission) and what they fall back to
    bool recorded = false;
    uint32_t handle = 0;
    std::vector<ng::LateCb> late;
    ng::Draw::Cb dflt[ng::kStages][16] = {};
};
std::mutex g_lists_m;
std::unordered_map<uint64_t, List*> g_lists;  // ended, waiting for their submission
std::atomic<uint64_t> g_next{1};
// device contexts as they appear (the main one and the render jobs' workers)
constexpr int kMaxCtx = 16;
std::atomic<uint64_t> g_devs[kMaxCtx];
std::atomic<int> g_ndevs{0};
std::mutex g_devs_m;
struct Ctx { std::atomic<List*> cur{nullptr}; };
Ctx g_ctx[kMaxCtx];
std::atomic<uint64_t> g_lists_made{0}, g_lists_run{0}, g_orphans{0};

uint64_t dev_addr(int i) { return g_devs[i].load(std::memory_order_acquire); }
int ctx_of_dev(uint64_t dev) {
    if (!dev) return -1;
    const int n = g_ndevs.load(std::memory_order_acquire);
    for (int i = 0; i < n; ++i)
        if (g_devs[i].load(std::memory_order_relaxed) == dev) return i;
    std::lock_guard lk(g_devs_m);
    const int m = g_ndevs.load(std::memory_order_relaxed);
    for (int i = n; i < m; ++i)
        if (g_devs[i].load(std::memory_order_relaxed) == dev) return i;
    if (m >= kMaxCtx) return -1;
    g_devs[m].store(dev, std::memory_order_relaxed);
    g_ndevs.store(m + 1, std::memory_order_release);
    log("nd: device context %d at %#llx", m, (unsigned long long)dev);
    return m;
}
int ctx_of_cb(uint64_t cb) {  // a GfxContext (its draw command buffer is at +0): D+0x60 or D+0xEC0
    const int n = g_ndevs.load(std::memory_order_acquire);
    for (int i = 0; i < n; ++i) {
        const uint64_t d = g_devs[i].load(std::memory_order_relaxed);
        if (cb == d + 0x60 || cb == d + 0xEC0) return i;
    }
    return -1;
}
List* list_of(int c) {
    if (c < 0) return nullptr;
    List* l = g_ctx[c].cur.load(std::memory_order_relaxed);
    if (!l) {  // recorded outside a begin .. end (should not happen): an implicit list
        l = new List;
        l->id = g_next++, l->dev = dev_addr(c), l->made = gpu_flip_count();
        g_ctx[c].cur.store(l, std::memory_order_relaxed);
        static std::atomic<int> told{0};
        if (told++ < 5) log("nd: context %d recorded outside a command list", c);
    }
    return l;
}
void begin_list(uint64_t dev) {
    const int c = ctx_of_dev(dev);
    if (c < 0) return;
    if (List* old = g_ctx[c].cur.exchange(nullptr)) {  // begun again without an end: keep it for its token
        std::lock_guard lk(g_lists_m);
        g_lists[old->id] = old;
    }
    auto* l = new List;
    l->id = g_next++, l->dev = dev, l->made = gpu_flip_count();
    g_ctx[c].cur.store(l, std::memory_order_relaxed);
    ++g_lists_made;
}
// The token, written where the list's command buffer ends, so the engine sees a non-empty
// list and submits it (Gnm's own reserve callback grows the buffer when needed).
void write_token(uint64_t cb, uint64_t id) {
    using ReserveFn = D1_SYSV bool (*)(uint64_t, uint32_t, uint64_t);
    uint32_t* p = field<uint32_t*>(cb, 0x10);
    if (uint64_t(field<uint64_t>(cb, 8) - uint64_t(p)) / 4 < 4) {
        if (!reinterpret_cast<ReserveFn>(field<uint64_t>(cb, 0x18))(cb, 4, field<uint64_t>(cb, 0x20))) return;
        p = field<uint32_t*>(cb, 0x10);
    }
    p[0] = 0xC0021000u;  // type 3 NOP, 4 dwords
    p[1] = kMagic, p[2] = uint32_t(id), p[3] = uint32_t(id >> 32);
    *reinterpret_cast<uint32_t**>(cb + 0x10) = p + 4;
}
// Records the list on this thread (the engine's), when the renderer records lists as they end.
// A draw's constant buffers are the list's own bindings before it; a slot the list has not
// bound is inherited from the lists submitted before this one, known only at submission.
void record(List* l) {
    if (!ng::list_recording() || l->items.empty()) return;
    if (gpu_flip_count() % uint64_t(nr::g_every) != 0) return;  // (not drawn this frame)
    ng::Draw::Cb local[ng::kStages][16] = {};
    bool bound[ng::kStages][16] = {};  // (an unbinding counts: the draw then keeps what it captured)
    std::vector<ng::Draw*> items;
    items.reserve(l->items.size());
    for (Item& it : l->items) {
        if (!it.d) {
            local[it.cb.stage][it.cb.slot] = it.cb.cb;
            bound[it.cb.stage][it.cb.slot] = true;
            continue;
        }
        ng::Draw* d = it.d;
        if (d->kind <= ng::Draw::Clear)
            for (int st = 0; st < ng::kStages; ++st)
                for (int sl = 0; sl < 16; ++sl) {
                    ng::Draw::Cb& c = d->cb[st][sl];
                    if (bound[st][sl]) {
                        if (local[st][sl].addr) c = local[st][sl];
                    } else {
                        if (!l->dflt[st][sl].addr && c.addr) l->dflt[st][sl] = c;
                        c = {ng::kLateCb | uint64_t(st) << 4 | uint64_t(sl), c.size};
                    }
                }
        items.push_back(d);
    }
    l->recorded = ng::record_list(items, l->handle, l->late);
}
// end of a list: file it, mark its command buffer
List* end_list(uint64_t dev) {
    const int c = ctx_of_dev(dev);
    {
        static std::atomic<int> told{0};
        if (getenv("D1_ND_LOG") && told++ < 60) log("nd: end of a list on context %d (dev %#llx)", c, (unsigned long long)dev);
    }
    if (c < 0) return nullptr;
    List* l = list_of(c);
    record(l);
    {
        std::lock_guard lk(g_lists_m);
        g_lists[l->id] = l;
    }
    if (const uint64_t gfx = field<uint64_t>(dev, 0x50)) write_token(gfx, l->id);
    return l;
}
void add(int c, ng::Draw* d) {
    if (List* l = list_of(c)) l->items.push_back({d, {}});
    else nr::release_draw(d);
}

// ---- the engine's device functions around lists
using Dev1Fn = D1_SYSV void (*)(uint64_t);
using Dev3Fn = D1_SYSV void (*)(uint64_t, uint64_t, uint64_t);
using Dev4Fn = D1_SYSV void (*)(uint64_t, uint64_t, uint64_t, uint64_t);
Dev1Fn o_begin, o_end_submit;
Dev3Fn o_end;
Dev4Fn o_begin_inherit;
D1_SYSV void h_begin(uint64_t dev) {
    o_begin(dev);
    begin_list(dev);
}
D1_SYSV void h_begin_inherit(uint64_t dev, uint64_t rec, uint64_t a, uint64_t saved) {
    o_begin_inherit(dev, rec, a, saved);
    begin_list(dev);
}
D1_SYSV void h_end(uint64_t dev, uint64_t rec, uint64_t kind) {
    end_list(dev);
    o_end(dev, rec, kind);  // (its end-of-list label lands in the list: still current)
    if (const int c = ctx_of_dev(dev); c >= 0) g_ctx[c].cur.store(nullptr, std::memory_order_relaxed);
}
D1_SYSV void h_end_submit(uint64_t dev) {
    end_list(dev);
    const int c = ctx_of_dev(dev);
    // the label is recorded inside, before the submission it may start: detach the list first
    // only after the call (the submission reads the filed list, not the context)
    o_end_submit(dev);
    if (c >= 0) g_ctx[c].cur.store(nullptr, std::memory_order_relaxed);
}

// ---- Gnm / Gnmx replacements
D1_SYSV uint64_t s_noop() { return 0; }
// Command-buffer allocations hold data the GPU reads through V#s (40-bit addresses): they
// come from a region in the guest's address range, in 256 KiB chunks a list owns until it
// has been executed.
constexpr uint64_t kArenaChunk = 256 << 10, kArenaSize = 1ull << 30;
std::mutex g_arena_m;
uint8_t* g_arena = nullptr;
std::vector<uint32_t> g_arena_free;
uint8_t* arena_chunk() {
    std::lock_guard lk(g_arena_m);
    if (!g_arena) {
        // near the top of the guest address range (Windows keeps guest mappings in
        // 0x2_0000_0000..0x10_0000_0000), exactly there
        for (uint64_t at : {0xF80000000ull, 0xF00000000ull, 0xE80000000ull, 0xE00000000ull, 0xD00000000ull}) {
            void* p = os::alloc(at, kArenaSize, os::kRead | os::kWrite, true);
            if (p == reinterpret_cast<void*>(at)) { g_arena = static_cast<uint8_t*>(p); break; }
            if (p) os::release(p, kArenaSize);
        }
        if (!g_arena) { log("nd: no command-buffer arena below 1 TiB"); return nullptr; }
        for (uint32_t i = uint32_t(kArenaSize / kArenaChunk); i-- > 0;) g_arena_free.push_back(i);
        log("nd: command-buffer arena at %p (%llu MiB)", (void*)g_arena, (unsigned long long)(kArenaSize >> 20));
    }
    if (g_arena_free.empty()) {
        static int told = 0;
        if (told++ < 5) log("nd: command-buffer arena full");
        return nullptr;
    }
    const uint32_t i = g_arena_free.back();
    g_arena_free.pop_back();
    return g_arena + uint64_t(i) * kArenaChunk;
}
void arena_free(uint8_t* p) {
    std::lock_guard lk(g_arena_m);
    g_arena_free.push_back(uint32_t(uint64_t(p - g_arena) / kArenaChunk));
}
std::mutex g_global_alloc_m;
std::vector<uint8_t*> g_global_alloc;
// allocateFromCommandBuffer(cb, bytes, log2 align): constants and inline data, valid until the
// list has been executed
D1_SYSV void* s_alloc(uint64_t cb, uint32_t bytes, uint32_t align_log2) {
    const uint64_t align = uint64_t(1) << std::min(align_log2, 12u);
    const int c = ctx_of_cb(cb);
    List* l = list_of(c);
    const size_t need = size_t(bytes) + align;
    if (need > kArenaChunk) {
        static int told = 0;
        if (told++ < 5) log("nd: command-buffer allocation of %u bytes", bytes);
        return nullptr;
    }
    if (!l) {  // outside any list (initialisation): kept
        std::lock_guard lk(g_global_alloc_m);
        static uint8_t* cur = nullptr;
        static size_t used = 0;
        if (!cur || used + need > kArenaChunk) {
            g_global_alloc_m.unlock();
            uint8_t* c = arena_chunk();
            g_global_alloc_m.lock();
            if (!c) return nullptr;
            g_global_alloc.push_back(c), cur = c, used = 0;
        }
        const uint64_t p = (uint64_t(cur) + used + align - 1) & ~(align - 1);
        used = size_t(p - uint64_t(cur)) + bytes;
        return reinterpret_cast<void*>(p);
    }
    if (l->chunks.empty() || l->used + need > kArenaChunk) {
        uint8_t* c = arena_chunk();
        if (!c) return nullptr;
        l->chunks.push_back(c);
        l->used = 0;
    }
    const uint64_t base = uint64_t(l->chunks.back());
    const uint64_t p = (base + l->used + align - 1) & ~(align - 1);
    l->used = size_t(p - base) + bytes;
    return reinterpret_cast<void*>(p);
}
// EVENT_WRITE_EOP: (cb, event, cache bits, address, data_sel, data, ?, int_sel)
D1_SYSV void s_eop_label(uint64_t cb, uint32_t, uint32_t, uint64_t addr, uint32_t data_sel, uint64_t data, uint32_t,
                         uint32_t int_sel) {
    List* l = list_of(ctx_of_cb(cb));
    if (!l) return;
    if (addr >= 0x10000 && (data_sel == 1 || data_sel == 2)) {
        ng::Draw* d = nr::alloc_draw();
        d->kind = ng::Draw::WriteData;
        d->caller = addr;
        d->inline_vertices.resize(data_sel == 1 ? 4 : 8);
        std::memcpy(d->inline_vertices.data(), &data, d->inline_vertices.size());
        l->items.push_back({d, {}});
    }
    if (int_sel) l->eop = true;
}
D1_SYSV void s_eop_interrupt(uint64_t cb) {
    if (List* l = list_of(ctx_of_cb(cb))) l->eop = true;
}
// occlusion counter dump: (cb, end, results)
D1_SYSV void s_zpass(uint64_t cb, uint32_t end, uint64_t results) {
    const int c = ctx_of_cb(cb);
    if (c < 0 || results < 0x10000) return;
    ng::Draw* d = nr::alloc_draw();
    d->kind = ng::Draw::ZPass;
    d->index_addr = end == 1 ? results + 8 : results;
    add(c, d);
}
// SET_PREDICATION on: (cb, address, ?, draw if visible) / off: (cb)
D1_SYSV void s_pred_on(uint64_t cb, uint64_t addr, uint32_t, uint32_t visible) {
    *reinterpret_cast<uint8_t*>(cb + 0x28) |= 1;
    const int c = ctx_of_cb(cb);
    if (c < 0) return;
    ng::Draw* d = nr::alloc_draw();
    d->kind = ng::Draw::PredOn;
    d->index_addr = addr & ~15ull, d->count = visible & 1;
    add(c, d);
}
D1_SYSV void s_pred_off(uint64_t cb) {
    *reinterpret_cast<uint8_t*>(cb + 0x28) &= ~1;
    const int c = ctx_of_cb(cb);
    if (c < 0) return;
    ng::Draw* d = nr::alloc_draw();
    d->kind = ng::Draw::PredOff;
    add(c, d);
}
// GPU memory copy (the engine's copy queue: streaming, relocation): (cb, dst, src, bytes, last)
D1_SYSV void s_dma(uint64_t cb, uint64_t dst, uint64_t src, uint32_t bytes) {
    const int c = ctx_of_cb(cb);
    if (c < 0 || !bytes) return;
    ng::Draw* d = nr::alloc_draw();
    d->kind = ng::Draw::Dma;
    d->index_addr = src, d->caller = dst, d->count = bytes, d->prim = 0, d->index32 = 0;
    add(c, d);
}
// ConstantUpdateEngine::setConstantBuffers(cue, stage, first, count, V#s): the bindings, in order
D1_SYSV void s_set_cbs(uint64_t cue, uint32_t stage, uint32_t first, uint32_t count, const uint32_t* vs) {
    const int s = nr::gnm_stage_index(stage);
    if (s < 0) return;
    nr::CueState* cst = nr::cue_state(cue, true);
    List* l = list_of(ctx_of_cb(cue - 0xC0));
    for (uint32_t k = 0; k < count && first + k < 16; ++k) {
        ng::Draw::Cb& cbv = cst->cb[s][first + k];
        if (!vs) {
            cbv = {};
        } else {
            const uint32_t* v = vs + 4 * k;
            const uint64_t base = uint64_t(v[0]) | uint64_t(v[1] & 0xFFF) << 32;
            const uint32_t stride = v[1] >> 16 & 0x3FFF, records = v[2];
            const uint64_t bytes = stride ? uint64_t(stride) * records : records;
            cbv = {base, uint32_t(std::min<uint64_t>(bytes, 1u << 20))};
        }
        if (l && nr::g_ce_order) l->items.push_back({nullptr, nr::CbEvent{0, 0, uint8_t(s), uint8_t(first + k), cbv}});
    }
}

// Chunks outlive their list by a few frames: constant buffers bound on the main context are
// read by the render jobs' lists submitted after it (the constant update engine shares
// bindings between contexts), as on the console, where command-buffer memory stays until
// the GPU is past it.
std::mutex g_retired_m;
std::deque<std::pair<uint64_t, std::vector<uint8_t*>>> g_retired;
void retire_chunks(std::vector<uint8_t*>&& cs) {
    const uint64_t now = gpu_flip_count();
    std::lock_guard lk(g_retired_m);
    while (!g_retired.empty() && g_retired.front().first + 3 <= now) {
        for (uint8_t* c : g_retired.front().second) arena_free(c);
        g_retired.pop_front();
    }
    if (!cs.empty()) g_retired.emplace_back(now, std::move(cs));
}
void free_list(List* l) {
    retire_chunks(std::move(l->chunks));
    std::vector<ng::Draw*> ds;
    for (Item& it : l->items)
        if (it.d) ds.push_back(it.d);
    nr::release_draws(ds);
    delete l;
}

// Occlusion dumps of lists that were not drawn: every query reads "visible".
void answer_zpass(uint64_t dest, bool end) {
    if (guest_region_extent(dest) < 0x80) return;
    auto* q = reinterpret_cast<uint64_t*>(dest);
    for (int db = 0; db < 8; ++db) q[db * 2 + (end ? 1 : 0)] = (end ? 1000ull : 0ull) | (1ull << 63);
}

void install(uint64_t) {
    if (const char* v = getenv("D1_ND_RES"); !v || atoi(v) != 0) resev::install();
    g_on = true;
    bool ok = true;
    auto rep = [&](uint64_t off, const void* fn) {
        if (!replace_eboot_function(off, fn)) ok = false, log("nd: replacing eboot+%#llx failed", (unsigned long long)off);
    };
    // Gnm / Gnmx functions the device layer calls per frame that write command buffers
    static const uint32_t kNoops[] = {
        0xF7E740, 0xF7E7C0, 0xF7E840, 0xF7E8D0, 0xF7E950, 0xF7E9B0, 0xF7EA20, 0xF7EA80, 0xF7EAF0, 0xF7EB50, 0xF7EBB0,
        0xF7EC30, 0xF7ED40, 0xF7EEC0, 0xF7F1E0, 0xF7F260, 0xF7F320, 0xF7F4A0, 0xF7F790, 0xF7F7E0, 0xF7F840, 0xF7F890,
        0xF7FA90, 0xF7FCD0, 0xF7FD40, 0xF7FE20, 0xF80340, 0xF80440, 0xF804F0, 0xF80550, 0xF805C0, 0xF80640, 0xF806D0,
        0xF80730, 0xF80790, 0xF80830, 0xF808A0, 0xF80910, 0xF80E00, 0xF80F10, 0xF81090, 0xF81220,
        0xF7E5E0, 0xF84DB0, 0xF811C0,  // default hardware state, InsertWaitFlipDone (imports writing packets)
        0xF8AFD0, 0xF8B0C0, 0xF8B1F0, 0xF8B2E0, 0xF8B410, 0xF8B600, 0xF8B790, 0xF8B8C0, 0xF8B980, 0xF8DF60, 0xF8E680,
        0xF8E880, 0xF8F0E0, 0xF8F4B0};
    for (uint32_t off : kNoops) rep(off, reinterpret_cast<const void*>(&s_noop));
    rep(0xF7FEB0, reinterpret_cast<const void*>(&s_alloc));
    rep(0xF80C90, reinterpret_cast<const void*>(&s_eop_label));
    rep(0xF80D70, reinterpret_cast<const void*>(&s_eop_interrupt));
    rep(0xF80AE0, reinterpret_cast<const void*>(&s_zpass));
    rep(0xF809F0, reinterpret_cast<const void*>(&s_pred_on));
    rep(0xF80A80, reinterpret_cast<const void*>(&s_pred_off));
    rep(0xF8F3A0, reinterpret_cast<const void*>(&s_dma));
    rep(0xF8B500, reinterpret_cast<const void*>(&s_set_cbs));
    ok &= hook(0x7DCCE0, &h_begin, o_begin, "cmdlist_begin");
    ok &= hook(0x7DD6A0, &h_begin_inherit, o_begin_inherit, "cmdlist_begin_inherit");
    ok &= hook(0x7DCEC0, &h_end, o_end, "cmdlist_end");
    ok &= hook(0x7DE950, &h_end_submit, o_end_submit, "cmdlist_end_and_submit");
    log("nd: native device layer: no Gnm command buffers, no emulated GPU (%zu Gnm functions replaced)%s",
        sizeof kNoops / sizeof kNoops[0] + 8, ok ? "" : " - SOME REPLACEMENTS FAILED");
}
}  // namespace nd

bool nd_push(uint64_t dev, ng::Draw* d) {
    if (!nd::g_on) return false;
    d->frame = uint32_t(gpu_flip_count());
    nd::add(nd::ctx_of_dev(dev), d);
    return true;
}

}  // namespace

// ---------------------------------------------------------------------------- write tracking
// The renderer keeps copies of guest memory on the GPU (vertex and index buffers, textures).
// To know when the game changes them, the pages are write-protected while a copy exists;
// the first write faults, bumps the page's generation and unprotects the page. A range's
// version is the sum of its pages' generations, so it changes exactly when a write happened.
namespace wt {
constexpr uint64_t kPage = 4096, kChunkBits = 30, kPagesPerChunk = 1ull << (kChunkBits - 12), kChunks = 128;
constexpr uint64_t kBlockPages = 16;  // a fault opens the protected pages of its 64 KiB block
constexpr uint64_t kCoarsePages = 256;  // 1 MiB: a generation per block too, for quick checks
enum : uint8_t { kOff = 0, kProtected = 1, kUnprotecting = 2 };
struct Chunk {
    std::atomic<uint32_t> gen[kPagesPerChunk];
    std::atomic<uint32_t> coarse[kPagesPerChunk / kCoarsePages];  // bumped with any page's gen
    std::atomic<uint8_t> state[kPagesPerChunk];
    std::atomic<uint8_t> watched[kPagesPerChunk];  // ever protected by us
};
std::atomic<Chunk*> g_chunks[kChunks];
std::mutex g_alloc_m;
std::atomic<uint64_t> g_faults{0};
const bool g_log_faults = getenv("D1_NG_LOG_FAULTS") != nullptr;
std::mutex g_census_m;
std::unordered_map<uint64_t, uint64_t> g_census;
void print_census() {
    std::vector<std::pair<uint64_t, uint64_t>> v;
    {
        std::lock_guard lk(g_census_m);
        v.assign(g_census.begin(), g_census.end());
        g_census.clear();
    }
    std::sort(v.begin(), v.end(), [](auto& a, auto& b) { return a.second > b.second; });
    std::string out;
    for (size_t i = 0; i < v.size() && i < 16; ++i) {
        char b[48];
        std::snprintf(b, sizeof b, " %llx:%llu", (unsigned long long)(v[i].first << 16), (unsigned long long)v[i].second);
        out += b;
    }
    log("native gfx: write faults by 64 KiB region (%zu regions):%s", v.size(), out.c_str());
}

Chunk* chunk(uint64_t page, bool create) {
    const uint64_t c = page >> (kChunkBits - 12);
    if (c >= kChunks) return nullptr;
    Chunk* ch = g_chunks[c].load(std::memory_order_acquire);
    if (ch || !create) return ch;
    std::lock_guard lk(g_alloc_m);
    ch = g_chunks[c].load(std::memory_order_acquire);
    if (!ch) {
        ch = new Chunk();  // value-initialised: zero
        g_chunks[c].store(ch, std::memory_order_release);
    }
    return ch;
}

uint64_t fine_version(uint64_t addr, uint64_t size) {
    uint64_t v = 0;
    for (uint64_t pg = addr / kPage, end = (addr + size + kPage - 1) / kPage; pg < end; ++pg) {
        Chunk* ch = chunk(pg, false);
        if (!ch) return ~0ull;  // never watched
        const uint64_t i = pg & (kPagesPerChunk - 1);
        // an unprotected page may change without notice: such a range has no stable version
        if (ch->state[i].load(std::memory_order_acquire) != kProtected) return ~0ull;
        v += ch->gen[i].load(std::memory_order_relaxed);
    }
    return v;
}

// The sum of the 1 MiB block generations over a range (~0: never watched).
uint64_t coarse_sum(uint64_t addr, uint64_t size) {
    uint64_t v = 0;
    const uint64_t first = addr / kPage, end = (addr + size + kPage - 1) / kPage;
    for (uint64_t pg = first & ~(kCoarsePages - 1); pg < end; pg += kCoarsePages) {
        Chunk* ch = chunk(pg, false);
        if (!ch) return ~0ull;
        v += ch->coarse[(pg & (kPagesPerChunk - 1)) / kCoarsePages].load(std::memory_order_acquire);
    }
    return v;
}

// A range's version, remembered with the 1 MiB block generations it was computed under: while
// none of those changed, no page in the range was written or unprotected, so a big buffer is
// checked with a few loads instead of one per page. Only the renderer thread calls this.
struct VCached { uint64_t addr, size, coarse, version; };
thread_local std::unordered_map<uint64_t, VCached> g_vcache;  // (per thread: the renderer's recording threads ask concurrently)
uint64_t version(uint64_t addr, uint64_t size) {
    const uint64_t c = coarse_sum(addr, size);  // before the pages: see on_fault
    if (c == ~0ull) return ~0ull;
    const uint64_t key = (addr * 0x9E3779B97F4A7C15ull) ^ size;
    auto it = g_vcache.find(key);
    if (it != g_vcache.end() && it->second.addr == addr && it->second.size == size && it->second.coarse == c)
        return it->second.version;
    const uint64_t v = fine_version(addr, size);
    if (v == ~0ull) {
        if (it != g_vcache.end()) g_vcache.erase(it);
        return v;
    }
    if (g_vcache.size() > (1u << 20)) g_vcache.clear();
    g_vcache[key] = {addr, size, c, v};
    return v;
}

// (diagnostics) a page's tracking state, generation and the host's protection of it
void describe(uint64_t addr, char* out, size_t n) {
    const uint64_t pg = addr / kPage;
    Chunk* ch = chunk(pg, false);
    std::string prot = "?";
#if !defined(_WIN32)
    if (FILE* f = std::fopen("/proc/self/maps", "r")) {
        char line[512];
        while (std::fgets(line, sizeof line, f)) {
            unsigned long long lo, hi;
            char perms[8];
            if (std::sscanf(line, "%llx-%llx %7s", &lo, &hi, perms) == 3 && addr >= lo && addr < hi) {
                prot = std::string(perms) + " " + std::to_string((hi - lo) >> 10) + "K";
                break;
            }
        }
        std::fclose(f);
    }
#endif
    if (!ch) {
        std::snprintf(out, n, "no chunk, host %s", prot.c_str());
        return;
    }
    const uint64_t i = pg & (kPagesPerChunk - 1);
    std::snprintf(out, n, "state %u gen %llu watched %u, host %s", unsigned(ch->state[i].load()),
                  (unsigned long long)ch->gen[i].load(), unsigned(ch->watched[i].load()), prot.c_str());
}

// Protect [addr, addr+size) (whole pages) and return its version.
uint64_t watch(uint64_t addr, uint64_t size) {
    const uint64_t first = addr / kPage, end = (addr + size + kPage - 1) / kPage;
    uint64_t run = 0, run_len = 0;
    auto flush = [&] {
        if (run_len) os::protect(reinterpret_cast<void*>(run * kPage), run_len * kPage, os::kRead);
        run_len = 0;
    };
    for (uint64_t pg = first; pg < end; ++pg) {
        Chunk* ch = chunk(pg, true);
        if (!ch) return ~0ull;
        const uint64_t i = pg & (kPagesPerChunk - 1);
        uint8_t expect = kOff;
        if (ch->state[i].compare_exchange_strong(expect, kProtected)) {
            ch->watched[i].store(1, std::memory_order_relaxed);
            if (run_len && run + run_len == pg) ++run_len;
            else flush(), run = pg, run_len = 1;
        } else if (expect == kUnprotecting) {
            flush();
            return ~0ull;  // being written right now: try again later
        }
    }
    flush();
    return version(addr, size);
}

// A page we no longer know the contents of (unmapped / remapped).
void forget(uint64_t addr, uint64_t size) {
    for (uint64_t pg = addr / kPage, end = (addr + size + kPage - 1) / kPage; pg < end; ++pg) {
        Chunk* ch = chunk(pg, false);
        if (!ch) {
            pg |= kPagesPerChunk - 1;  // skip the rest of this chunk
            continue;
        }
        const uint64_t i = pg & (kPagesPerChunk - 1);
        ch->gen[i].fetch_add(1, std::memory_order_relaxed);
        ch->coarse[i / kCoarsePages].fetch_add(1, std::memory_order_release);
        ch->state[i].store(kOff, std::memory_order_release);
    }
}

// Fault handler (any thread): true if the fault was one of our write-protected pages.
bool on_fault(uint64_t addr) {
    const uint64_t pg = addr / kPage;
    Chunk* ch = chunk(pg, false);
    if (!ch) return false;
    const uint64_t i = pg & (kPagesPerChunk - 1);
    uint8_t expect = kProtected;
    if (ch->state[i].compare_exchange_strong(expect, kUnprotecting)) {
        // the game writes whole buffers / textures front to back: open the rest of this 64 KiB
        // block too (the protected pages of it), so a streamed write costs one fault, not 16
        const uint64_t blk = i & ~uint64_t(kBlockPages - 1);
        uint32_t taken = 1u << (i - blk);
        for (uint64_t k = 0; k < kBlockPages; ++k) {
            if (blk + k == i) continue;
            uint8_t e = kProtected;
            if (ch->state[blk + k].compare_exchange_strong(e, kUnprotecting)) taken |= 1u << k;
        }
        for (uint64_t k = 0; k < kBlockPages; ++k)
            if (taken >> k & 1) ch->gen[blk + k].fetch_add(1, std::memory_order_relaxed);
        // after the page generations (version() reads the block generation first)
        ch->coarse[blk / kCoarsePages].fetch_add(1, std::memory_order_release);
        for (uint64_t k = 0; k < kBlockPages;) {  // one protect call per run of taken pages
            if (!(taken >> k & 1)) {
                ++k;
                continue;
            }
            uint64_t e = k;
            while (e < kBlockPages && (taken >> e & 1)) ++e;
            const uint64_t first = (pg & ~(kPagesPerChunk - 1)) + blk + k;
            os::protect(reinterpret_cast<void*>(first * kPage), (e - k) * kPage, os::kRead | os::kWrite);
            k = e;
        }
        for (uint64_t k = 0; k < kBlockPages; ++k)
            if (taken >> k & 1) ch->state[blk + k].store(kOff, std::memory_order_release);
        g_faults.fetch_add(1, std::memory_order_relaxed);
        if (g_log_faults) {  // D1_NG_LOG_FAULTS: which 64 KiB regions keep faulting
            std::lock_guard lk(g_census_m);
            ++g_census[pg >> 4];
        }
        return true;
    }
    // another thread is unprotecting it (or just did): retry the access
    if (expect == kUnprotecting) {
        while (ch->state[i].load(std::memory_order_acquire) == kUnprotecting) {}
        return true;
    }
    return ch->watched[i].load(std::memory_order_relaxed) != 0;
}
}  // namespace wt

// D1_NG_LOG_FAULTS: per writing code address, the faults and a sample address (what the
// renderer keeps there is named in the periodic census)
namespace faultlog {
std::mutex m;
struct Site { uint64_t n = 0, sample = 0; };
std::unordered_map<uint64_t, Site> sites;
void note(void* uc, uint64_t addr) {
    uint64_t rip = 0;
#if defined(__linux__)
    rip = uint64_t(static_cast<ucontext_t*>(uc)->uc_mcontext.gregs[REG_RIP]);
#else
    (void)uc;
#endif
    std::lock_guard lk(m);
    Site& s = sites[rip >= nr::g_base && rip < nr::g_base + 0x4000000 ? rip - nr::g_base : rip | 1ull << 63];
    if (!s.n++) s.sample = addr;
}
void print() {
    std::vector<std::pair<uint64_t, Site>> v;
    {
        std::lock_guard lk(m);
        v.assign(sites.begin(), sites.end());
        sites.clear();
    }
    std::sort(v.begin(), v.end(), [](auto& a, auto& b) { return a.second.n > b.second.n; });
    for (size_t i = 0; i < v.size() && i < 24; ++i) {
        char owner[160] = "";
        ng::describe_owner(v[i].second.sample, owner, sizeof owner);
        char where[200] = "";
#if defined(__linux__)
        if (v[i].first >> 63) {
            Dl_info di{};
            const uint64_t a = v[i].first & ~(1ull << 63);
            if (dladdr(reinterpret_cast<void*>(a), &di) && di.dli_fname)
                std::snprintf(where, sizeof where, " [%s+%#llx %s]", di.dli_fname, (unsigned long long)(a - uint64_t(di.dli_fbase)),
                              di.dli_sname ? di.dli_sname : "");
        }
#endif
        log("native gfx: write faults from %s%#llx%s: %llu (e.g. %#llx: %s)", v[i].first >> 63 ? "host " : "eboot+",
            (unsigned long long)(v[i].first & ~(1ull << 63)), where, (unsigned long long)v[i].second.n, (unsigned long long)v[i].second.sample, owner);
    }
}
}  // namespace faultlog
bool native_gfx_on_fault(void* uc, void* addr) {
    if (!nr::g_base || !ng::active() || !wt::on_fault(uint64_t(addr))) return false;
    if (wt::g_log_faults) faultlog::note(uc, uint64_t(addr));
    return true;
}
bool native_gfx_active() { return nr::g_base && ng::active(); }
void native_gfx_on_unmap(uint64_t addr, uint64_t size) {
    if (native_gfx_active()) wt::forget(addr, size);
}

// Called once the eboot is loaded and relocated (with the other game hooks).
void native_gfx_install() {
    const char* mode = getenv("D1_NATIVE_GFX");
#ifndef D1_RENDERER_SHADPS4
    if (!mode) mode = "render";  // the native renderer is this build's renderer
#endif
    if (!mode) return;
    if (std::strcmp(mode, "render") == 0) {
        nr::g_base = rt().modules[0].base;
        nr::build_vsharp = reinterpret_cast<nr::BuildVsharpFn>(nr::g_base + 0xF7CF90);
        if (const char* v = getenv("D1_NG_EVERY")) nr::g_every = std::max(1, std::atoi(v));
        if (const char* v = getenv("D1_NG_CE_ORDER")) nr::g_ce_order = std::atoi(v) != 0;
        if (const char* v = getenv("D1_NG_DUMP_EVERY")) nr::g_dump_every = std::max(0, std::atoi(v));
        ng::Options opt;
        opt.frames_dir = getenv("D1_NG_FRAMES");
        opt.no_cull = getenv("D1_NG_NOCULL") != nullptr;
        opt.dump_targets = getenv("D1_NG_TARGETS") != nullptr;
        const Settings& st = settings();
        opt.present_mode = st.vsync == "on" ? "Fifo" : st.vsync == "off-tearing" ? "Immediate" : "Mailbox";
        static std::string cache_file;
        cache_file = rt().data_root + "/shader_cache";
        {
            std::error_code ec;
            std::filesystem::create_directories(cache_file, ec);
        }
        cache_file += "/native_pipelines.bin";
        opt.pipeline_cache = cache_file.c_str();
        if (!getenv("D1_NG_NOCACHE")) {
            opt.watch = [](uint64_t a, uint64_t n) { return wt::watch(a, n); };
            opt.version = [](uint64_t a, uint64_t n) { return wt::version(a, n); };
            // (engine resource events: the native device layer with D1_ND_RES on, as nd::install decides)
            const char* nd_v = getenv("D1_ND");
            const char* res_v = getenv("D1_ND_RES");
            if ((!nd_v || atoi(nd_v) != 0) && (!res_v || atoi(res_v) != 0))
                opt.res_current = [](uint64_t obj) { return nr::resreg::get(obj); };
            opt.describe = [](uint64_t a, char* out, size_t n) { wt::describe(a, out, n); };
        }
        if (const char* v = getenv("D1_NG_FRAMES_IN_FLIGHT")) opt.frames_in_flight = uint32_t(std::max(1, std::atoi(v)));
#ifdef D1_FRONTEND_SDL
        // the game window (main thread, before the game starts)
        if (frontend::open(st.window_width, st.window_height, st.fullscreen)) {
            opt.window_handles = [](ng::WindowHandles& out) {
                frontend::Handles h;
                if (!frontend::handles(h)) return false;
                out.type = h.type == frontend::Handles::kWin32 ? ng::WindowHandles::kWin32 : ng::WindowHandles::kXlib;
                out.display = h.display;
                out.window = h.window;
                return true;
            };
            opt.window_size = [](uint32_t& w, uint32_t& h) { frontend::drawable_size(w, h); };
        }
#endif
        if (!ng::init(opt)) {
            log("native gfx: renderer unavailable; not capturing");
#ifndef D1_RENDERER_SHADPS4
            if (opt.window_handles)  // a window that would stay black: say why
                os::error_box("The renderer could not start, so nothing can be drawn.\n\nIt needs a GPU driver with "
                              "Vulkan 1.4 (update the graphics driver). Details are in d1-native.log.");
#endif
            return;
        }
        bool ok = true;
        ok &= hook(0x7E15D0, &r_draw_indexed, o_draw_indexed, "draw_indexed");
        ok &= hook(0x7E17C0, &r_draw, o_draw, "draw");
        ok &= hook(0x7E1710, &r_draw_instanced, o_draw_instanced, "draw_instanced");
        ok &= hook(0x7E16A0, &r_draw_indexed_instanced, o_draw_indexed_instanced, "draw_indexed_instanced");
        ok &= hook(0x7E1840, &r_draw_quads, o_draw_quads, "draw_shared_indices");
        ok &= hook(0x7E1960, &r_draw_inline, o_draw_inline, "draw_inline");
        ok &= hook(0x7E2A00, &r_clear, o_clear, "clear");
        ok &= hook(0x7DF630, &r_alloc_constants, o_alloc_constants, "alloc_constants");
        ok &= hook(0x7DEC20, &r_set_vertex_buffer, o_set_vertex_buffer, "set_vertex_buffer");
        ok &= hook(0x7E0780, &r_dispatch, o_dispatch, "dispatch");
        // the native device layer is the default; D1_ND=0: Gnm command buffers and the emulated GPU as before
        if (const char* v = getenv("D1_ND"); !v || std::atoi(v) != 0) nd::install(0);
        else ok &= hook(0xF8B500, &r_set_cbs, o_set_cbs, "set_constant_buffers");
        log("native gfx: rendering natively (every %d frame%s)%s", nr::g_every, nr::g_every == 1 ? "" : "s",
            ok ? "" : " (some hooks failed)");
        return;
    }
    if (std::strcmp(mode, "observe") != 0) return;
    g_obs = new Observer;
    bool ok = true;
    ok &= hook(0x7E15D0, &h_draw_indexed, o_draw_indexed, "draw_indexed");
    ok &= hook(0x7E17C0, &h_draw, o_draw, "draw");
    ok &= hook(0x7DE8C0, &h_set_texture, o_set_texture, "set_texture");
    ok &= hook(0x7DEC20, &h_set_vertex_buffer, o_set_vertex_buffer, "set_vertex_buffer");
    ok &= hook(0x7DF630, &h_alloc_constants, o_alloc_constants, "alloc_constants");
    ok &= hook(0x7DEE30, &h_set_index_buffer, o_set_index_buffer, "set_index_buffer");
    ok &= hook(0x7E0430, &h_apply_targets, o_apply_targets, "apply_render_targets");
    log("native gfx: observing the engine GPU device layer%s", ok ? "" : " (some hooks failed)");
}

// hle_gpu.cpp: the game submitted command buffers. Execute the captured draws that belong to
// them, in submission order.
static void nr_every_world() {
    // D1_NG_EVERY_WORLD=<secs>: (testing) draw every frame from <secs> after reaching the world
    // (or the state named by D1_NG_EVERY_STATE, a prefix, e.g. setup:orbit). With a large
    // D1_NG_EVERY (e.g. 100000) nothing is drawn before that: a rendered check of a late
    // screen at about headless speed.
    static const double every_world = getenv("D1_NG_EVERY_WORLD") ? std::atof(getenv("D1_NG_EVERY_WORLD")) : -1;
    static const char* every_state = getenv("D1_NG_EVERY_STATE") ? getenv("D1_NG_EVERY_STATE") : "activity:in_world";
    if (every_world >= 0 && nr::g_every > 1) {
        static std::chrono::steady_clock::time_point t_world{};
        const char* gs = game_state();
        if (gs && std::strncmp(gs, every_state, std::strlen(every_state)) == 0) {
            if (t_world == std::chrono::steady_clock::time_point{}) t_world = std::chrono::steady_clock::now();
            else if (std::chrono::duration<double>(std::chrono::steady_clock::now() - t_world).count() > every_world) {
                nr::g_every = 1;
                log("native gfx: now drawing every frame (D1_NG_EVERY_WORLD)");
                if (getenv("D1_NG_PASSLOG_N")) ng::request_passlog(uint32_t(std::atoi(getenv("D1_NG_PASSLOG_N"))));
            }
        }
    }
}

bool native_gfx_submit(uint32_t count, uint32_t* const* dcbs, const uint32_t* sizes) {
    if (!nr::g_base || !ng::active()) return false;
    std::vector<std::pair<uint64_t, uint64_t>> ranges;
    std::vector<std::pair<uint64_t, ng::Draw*>> events;
    static const bool queries_cfg = !getenv("D1_NG_QUERIES") || atoi(getenv("D1_NG_QUERIES")) != 0;
    const bool queries = queries_cfg && !(ng::debug_toggles() & 1);
    nr::g_dcb_events = &events;
    for (uint32_t k = 0; k < count; ++k)
        if (dcbs[k] && sizes[k]) nr::dcb_ranges(dcbs[k], sizes[k] / 4, 0, ranges);
    nr::g_dcb_events = nullptr;
    std::vector<std::pair<uint64_t, ng::Draw*>> mine;
    // the range (in traversal order) holding a command-buffer position: binary search over
    // the ranges sorted by start (the first range in traversal order wins where they overlap,
    // as the linear search did); thousands of draws and constant events are placed per frame
    std::vector<std::pair<uint64_t, uint32_t>> by_start;
    by_start.reserve(ranges.size());
    for (size_t r = 0; r < ranges.size(); ++r) by_start.push_back({ranges[r].first, uint32_t(r)});
    std::sort(by_start.begin(), by_start.end());
    bool overlap = false;
    for (size_t i = 1; i < by_start.size(); ++i)
        if (by_start[i].first < ranges[by_start[i - 1].second].second) overlap = true;
    auto find_range = [&](uint64_t x) -> int64_t {
        if (overlap) {
            for (size_t r = 0; r < ranges.size(); ++r)
                if (x >= ranges[r].first && x < ranges[r].second) return int64_t(r);
            return -1;
        }
        auto it = std::upper_bound(by_start.begin(), by_start.end(), std::make_pair(x, UINT32_MAX));
        if (it == by_start.begin()) return -1;
        --it;
        return x < ranges[it->second].second ? int64_t(it->second) : -1;
    };
    {
        std::lock_guard lk(nr::g_m);
        nr::drain_inboxes();
        auto& pend = nr::g_pending;
        // the draws inside each range (in traversal order: where ranges overlap, the first wins)
        for (size_t r = 0; r < ranges.size(); ++r) {
            auto it = std::lower_bound(pend.begin(), pend.end(), ranges[r].first,
                                       [](const auto& a, uint64_t x) { return a.first < x; });
            for (; it != pend.end() && it->first < ranges[r].second; ++it) {
                ng::Draw* d = it->second;
                if (!d) continue;
                mine.push_back({uint64_t(r) << 40 | ((d->order - ranges[r].first) & 0xFFFFFFFFFFull), d});
                it->second = nullptr;
            }
        }
        // draws whose submission never came
        static uint32_t sweep = 0;
        if (++sweep % 64 == 0)
            for (auto& [pos, d] : pend) {
                if (!d || nr::g_seq - d->seq < 200000) continue;
                ++nr::g_dropped;
                static const bool log_drop = getenv("D1_NG_LOG_DROPS") != nullptr;
                static int n = 0;
                if (log_drop && n++ < 100)
                    log("ng drop: draw ps %p from %#llx recorded at %#llx (flip %u) never submitted", (const void*)d->ps,
                        (unsigned long long)d->caller, (unsigned long long)d->order, d->frame);
                nr::release_draw(d);
                d = nullptr;
            }
        pend.erase(std::remove_if(pend.begin(), pend.end(), [](const auto& e) { return !e.second; }), pend.end());
        if (static const bool st = getenv("D1_NG_PENDING_STATS") != nullptr; st) {
            static uint64_t n = 0;
            if (++n % 500 == 0)
                log("ng pending: %zu draws, %zu constant events kept after a submission of %zu ranges (%zu matched)",
                    pend.size(), nr::g_cb_pending.size(), ranges.size(), mine.size());
        }
        for (auto& [pos, e] : events) {
            if (!queries && (e->kind == ng::Draw::ZPass || e->kind == ng::Draw::PredOn || e->kind == ng::Draw::PredOff)) {
                nr::release_draw(e);
                continue;
            }
            e->seq = nr::g_seq++;
            const int64_t rng = find_range(pos);
            if (rng >= 0) mine.push_back({uint64_t(rng) << 40 | ((pos - ranges[size_t(rng)].first) & 0xFFFFFFFFFFull), e});
            else nr::release_draw(e);
        }
        // constant buffer bindings recorded in this submission's command buffers, merged in order
        if (nr::g_ce_order) {
            std::vector<std::pair<std::pair<uint64_t, uint32_t>, const nr::CbEvent*>> evs;
            auto& cp = nr::g_cb_pending;
            std::vector<nr::CbEvent> mine_ev;
            for (size_t r = 0; r < ranges.size(); ++r) {
                auto it = std::lower_bound(cp.begin(), cp.end(), ranges[r].first,
                                           [](const nr::CbEvent& a, uint64_t x) { return a.order < x; });
                for (; it != cp.end() && it->order < ranges[r].second; ++it) {
                    if (it->stage == 0xFF) continue;
                    mine_ev.push_back(*it);
                    mine_ev.back().order = uint64_t(r) << 40 | ((it->order - ranges[r].first) & 0xFFFFFFFFFFull);
                    it->stage = 0xFF;
                }
            }
            static uint32_t sweep_ev = 0;
            const bool sweep_now = ++sweep_ev % 64 == 0;
            cp.erase(std::remove_if(cp.begin(), cp.end(),
                                    [&](const nr::CbEvent& e) { return e.stage == 0xFF || (sweep_now && nr::g_seq - e.seq >= 2000000); }),
                     cp.end());
            std::vector<std::pair<std::pair<uint64_t, uint32_t>, int64_t>> seq;  // (pos, seq) -> draw index or ~event
            for (size_t i = 0; i < mine.size(); ++i) seq.push_back({{mine[i].first, mine[i].second->seq}, int64_t(i)});
            for (size_t i = 0; i < mine_ev.size(); ++i) seq.push_back({{mine_ev[i].order, mine_ev[i].seq}, ~int64_t(i)});
            std::sort(seq.begin(), seq.end(), [](auto& a, auto& b) { return a.first < b.first; });
            for (auto& [key, idx] : seq) {
                if (idx < 0) {
                    const auto& e = mine_ev[size_t(~idx)];
                    nr::g_ce[e.stage][e.slot] = e.cb;
                } else {
                    ng::Draw* d = mine[size_t(idx)].second;
                    for (int st = 0; st < 2; ++st)
                        for (int sl = 0; sl < 16; ++sl)
                            if (nr::g_ce[st][sl].addr) d->cb[st][sl] = nr::g_ce[st][sl];
                }
            }
        }
    }
    {
        uint32_t newest = 0;
        for (auto& [k, d] : mine) newest = std::max(newest, d->frame);
        for (auto& [k, d] : mine)
            if (d->kind <= ng::Draw::Clear && d->frame + 1 < newest) ++nr::g_late;
    }
    std::stable_sort(mine.begin(), mine.end(), [](auto& a, auto& b) { return a.first < b.first; });
    // D1_NG_LOG_STALE=1: draws matched to this submission that were recorded frames ago
    static const bool log_stale = getenv("D1_NG_LOG_STALE") != nullptr;
    if (log_stale && !mine.empty()) {
        uint32_t newest = 0;
        for (auto& [k, d] : mine) newest = std::max(newest, d->frame);
        uint32_t stale = 0, oldest = newest;
        for (auto& [k, d] : mine)
            if (d->frame + 1 < newest) ++stale, oldest = std::min(oldest, d->frame);
        static int logged = 0;
        if (stale && logged++ < 200)
            log("ng stale: %u of %zu draws in this submission were recorded %u+ frames before the newest (flip %u)", stale,
                mine.size(), newest - oldest, newest);
    }
    nr_every_world();
    const bool run = (gpu_flip_count() % uint64_t(nr::g_every)) == 0;
    if (run && !mine.empty()) {
        std::vector<ng::Draw*> draws;
        for (auto& [k, d] : mine) draws.push_back(d);
        const auto t0 = std::chrono::steady_clock::now();
        ng::execute(draws);
        nr::g_exec_ns += uint64_t(std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now() - t0).count());
        nr::g_frame_executed = true;
    }
    {
        std::vector<ng::Draw*> done;
        done.reserve(mine.size());
        for (auto& [k, d] : mine) done.push_back(d);
        nr::release_draws(done);
    }
    return run && !mine.empty() && queries;  // (the renderer answered the occlusion dumps)
}

// ---- native device layer: a submission names its command lists by their tokens
bool native_device_active() { return nd::g_on; }
void gnm_signal_eop();  // hle_gpu.cpp
void native_device_submit(uint32_t count, uint32_t* const* dcbs, const uint32_t* sizes) {
    std::vector<nd::List*> lists;
    {
        std::lock_guard lk(nd::g_lists_m);
        for (uint32_t k = 0; k < count; ++k) {
            const uint32_t* p = dcbs[k];
            const uint32_t n = p ? sizes[k] / 4 : 0;
            for (uint32_t i = 0; i < n;) {
                const uint32_t h = p[i], type = h >> 30;
                if (type == 3) {
                    const uint32_t cnt = (h >> 16) & 0x3FFF;
                    if (((h >> 8) & 0xFF) == 0x10 && cnt == 2 && i + 3 < n && p[i + 1] == nd::kMagic) {
                        const uint64_t id = p[i + 2] | uint64_t(p[i + 3]) << 32;
                        if (auto it = nd::g_lists.find(id); it != nd::g_lists.end()) lists.push_back(it->second), nd::g_lists.erase(it);
                    }
                    i += cnt + 2;
                } else if (type == 2) {
                    i += 1;
                } else {
                    i += ((h >> 16) & 0x3FFF) + 2;
                }
            }
        }
        // lists whose submission never came (a few hundred frames old): dropped
        static uint64_t sweep = 0;
        if (++sweep % 256 == 0)
            for (auto it = nd::g_lists.begin(); it != nd::g_lists.end();)
                if (it->second->made + 300 < gpu_flip_count()) {
                    if (it->second->recorded) ng::discard_recorded(it->second->handle);
                    ++nd::g_orphans, nd::free_list(it->second), it = nd::g_lists.erase(it);
                }
                else ++it;
    }
    // the draws and events in order; constant buffer bindings replayed as the constant update
    // engine shares them between contexts (in submission order)
    std::vector<ng::Draw*> draws;
    std::vector<uint32_t> recorded;
    std::vector<ng::Draw*> cpu_events;  // of recorded lists: memory writes the CPU sees, after their submission
    bool eop = false;
    // D1_ND_CB_CHECK: would the list's own bindings (over what the draw captured) give the
    // same constant buffers as the replay across lists?
    static const bool cb_check = getenv("D1_ND_CB_CHECK") != nullptr;
    static uint64_t cbc_draws[nd::kMaxCtx] = {}, cbc_diff[nd::kMaxCtx] = {}, cbc_inh[nd::kMaxCtx] = {}, cbc_cap[nd::kMaxCtx] = {}, cbc_n = 0;
    for (nd::List* l : lists) {
        eop |= l->eop;
        if (l->recorded) {
            // its inherited constant buffers: the bindings as the lists before it left them
            for (const ng::LateCb& lc : l->late) {
                const ng::Draw::Cb& c = nr::g_ce[lc.stage][lc.slot].addr ? nr::g_ce[lc.stage][lc.slot] : l->dflt[lc.stage][lc.slot];
                ng::fill_late(lc, c.addr, c.size);
            }
            recorded.push_back(l->handle);
            for (nd::Item& it : l->items) {
                if (!it.d) nr::g_ce[it.cb.stage][it.cb.slot] = it.cb.cb;
                else if (it.d->kind == ng::Draw::Dma || it.d->kind == ng::Draw::WriteData) cpu_events.push_back(it.d);
            }
            continue;
        }
        ng::Draw::Cb local[ng::kStages][16] = {};
        const int lc = cb_check && !l->recorded ? nd::ctx_of_dev(l->dev) : -1;
        for (nd::Item& it : l->items) {
            if (cb_check && lc >= 0) {
                if (!it.d) local[it.cb.stage][it.cb.slot] = it.cb.cb;
                else if (it.d->kind <= ng::Draw::Clear) {
                    bool diff = false, inh = false, cap = false;
                    for (int st = 0; st < 2; ++st)
                        for (int sl = 0; sl < 16; ++sl) {
                            const ng::Draw::Cb own = local[st][sl].addr ? local[st][sl] : it.d->cb[st][sl];
                            const ng::Draw::Cb full = nr::g_ce[st][sl].addr ? nr::g_ce[st][sl] : it.d->cb[st][sl];
                            if (own.addr && full.addr && own.addr != full.addr) {
                                if (local[st][sl].addr) diff = true; else cap = true;
                            }
                            inh |= !own.addr && full.addr;
                        }
                    ++cbc_draws[lc], cbc_diff[lc] += diff, cbc_inh[lc] += inh, cbc_cap[lc] += cap;
                }
            }
            if (!it.d) {
                nr::g_ce[it.cb.stage][it.cb.slot] = it.cb.cb;
                continue;
            }
            ng::Draw* d = it.d;
            if (nr::g_ce_order && d->kind <= ng::Draw::Clear)
                for (int st = 0; st < 2; ++st)
                    for (int sl = 0; sl < 16; ++sl)
                        if (nr::g_ce[st][sl].addr) d->cb[st][sl] = nr::g_ce[st][sl];
            draws.push_back(d);
        }
    }
    if (cb_check && ++cbc_n % 3000 == 0) {
        std::string t;
        for (int c = 0; c < nd::g_ndevs.load(); ++c) {
            char b[128];
            std::snprintf(b, sizeof b, " ctx%d %llu: local-conflict %llu captured-conflict %llu inherited %llu |", c, (unsigned long long)cbc_draws[c],
                          (unsigned long long)cbc_diff[c], (unsigned long long)cbc_cap[c], (unsigned long long)cbc_inh[c]);
            t += b;
        }
        log("nd cb check: draws whose constant buffers depend on earlier lists:%s", t.c_str());
    }
    nr_every_world();
    const bool run = (gpu_flip_count() % uint64_t(nr::g_every)) == 0 && ng::active();
    if (!recorded.empty()) {
        const auto t0 = std::chrono::steady_clock::now();
        ng::submit_recorded(recorded);
        nr::g_exec_ns += uint64_t(std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now() - t0).count());
        nr::g_frame_executed = true;
        for (ng::Draw* d : cpu_events) {
            ng::cpu_wrote(d->caller, d->kind == ng::Draw::Dma ? d->count : d->inline_vertices.size());
            if (d->kind == ng::Draw::Dma) {
                if (d->caller < 0x10000 || guest_region_extent(d->caller) < d->count) continue;
                if (d->prim == 2) {
                    auto* w = reinterpret_cast<uint32_t*>(d->caller);
                    for (uint32_t k = 0; k < d->count / 4; ++k) w[k] = d->instances;
                } else if (d->index_addr >= 0x10000 && guest_region_extent(d->index_addr) >= d->count) {
                    std::memmove(reinterpret_cast<void*>(d->caller), reinterpret_cast<const void*>(d->index_addr), d->count);
                }
            } else if (d->caller >= 0x10000 && guest_region_extent(d->caller) >= d->inline_vertices.size()) {
                std::memcpy(reinterpret_cast<void*>(d->caller), d->inline_vertices.data(), d->inline_vertices.size());
            }
        }
    }
    if (run && !draws.empty()) {
        const auto t0 = std::chrono::steady_clock::now();
        ng::execute(draws);
        nr::g_exec_ns += uint64_t(std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now() - t0).count());
        nr::g_frame_executed = true;
    } else {
        // not drawn: the memory effects still happen, in order, and occlusion reads "visible"
        for (ng::Draw* d : draws) {
            switch (d->kind) {
            case ng::Draw::Dma:
                if (d->caller >= 0x10000 && d->index_addr >= 0x10000 && guest_region_extent(d->caller) >= d->count &&
                    guest_region_extent(d->index_addr) >= d->count)
                    std::memmove(reinterpret_cast<void*>(d->caller), reinterpret_cast<const void*>(d->index_addr), d->count);
                break;
            case ng::Draw::WriteData:
                if (d->caller >= 0x10000 && guest_region_extent(d->caller) >= d->inline_vertices.size())
                    std::memcpy(reinterpret_cast<void*>(d->caller), d->inline_vertices.data(), d->inline_vertices.size());
                break;
            case ng::Draw::ZPass: nd::answer_zpass(d->index_addr & ~0xFull, (d->index_addr & 0xF) != 0); break;
            default: break;
            }
        }
    }
    nd::g_lists_run += lists.size();
    if (static const bool st = getenv("D1_ND_LIST_STATS") != nullptr; st) {  // draws per context per frame
        static uint64_t per_ctx[nd::kMaxCtx] = {}, lists_ctx[nd::kMaxCtx] = {}, last_flip = 0, frames = 0;
        for (nd::List* l : lists) {
            const int c = nd::ctx_of_dev(l->dev);
            if (c < 0) continue;
            ++lists_ctx[c];
            for (auto& it : l->items) per_ctx[c] += it.d && it.d->kind <= ng::Draw::Auto;
        }
        if (gpu_flip_count() != last_flip) {
            last_flip = gpu_flip_count();
            if (++frames % 300 == 0) {
                std::string t;
                for (int c = 0; c < nd::g_ndevs.load(); ++c) {
                    char b[64];
                    std::snprintf(b, sizeof b, " ctx%d %.0f draws/%.1f lists", c, per_ctx[c] / 300.0, lists_ctx[c] / 300.0);
                    t += b;
                    per_ctx[c] = lists_ctx[c] = 0;
                }
                log("nd: per frame:%s", t.c_str());
            }
        }
    }
    {
        static std::atomic<int> told{0};
        if (getenv("D1_ND_LOG") && told++ < 60)
            log("nd: submission of %u buffers: %zu lists, %zu items, eop %d, run %d", count, lists.size(), draws.size(), int(eop), int(run));
    }
    for (nd::List* l : lists) nd::free_list(l);
    if (eop) gnm_signal_eop();
}

// Diagnostics (D1_NG_LOG_WAITS): memory waits still unsatisfied after the null GPU ran the
// command buffers (so the CPU, not the GPU, is meant to release them).
void native_gfx_check_waits(uint32_t count, uint32_t* const* dcbs, const uint32_t* sizes) {
    static const bool on = getenv("D1_NG_LOG_WAITS") != nullptr;
    if (!on) return;
    std::vector<std::pair<uint64_t, uint64_t>> ranges;
    nr::g_wait_phase = 1;
    for (uint32_t k = 0; k < count; ++k)
        if (dcbs[k] && sizes[k]) nr::dcb_ranges(dcbs[k], sizes[k] / 4, 0, ranges);
    nr::g_wait_phase = 0;
}

// hle_gpu.cpp: the frame in video-out buffer `addr` is being flipped.
// ---- D1_ND_POOL_WATCH=1: (research) who writes the engine's handle-pool table (*0x1A238A0):
// the table is write-protected; each write faults, is logged with the writing code address
// and the descriptor field, and the page is protected again on the next flip.
namespace poolwatch {
std::atomic<uint64_t> lo{0}, hi{0};
std::mutex m;
struct Site { uint64_t n = 0; uint32_t first_pool = 0; };
std::map<std::pair<uint64_t, uint32_t>, Site> sites;  // (code offset, field) -> count
std::atomic<bool> dirty{false};
void protect() {
    if (!lo) return;
    os::protect(reinterpret_cast<void*>(lo.load()), hi - lo, os::kRead);
}
void start() {
    const uint64_t tbl = *reinterpret_cast<const uint64_t*>(nr::eb<uint64_t>(0x1A238A0));
    if (!tbl) return;
    lo = tbl & ~0xFFFull;
    hi = (tbl + 16384ull * 0x40 + 0xFFF) & ~0xFFFull;
    protect();
    log("nd pool watch: table %#llx write-protected", (unsigned long long)tbl);
}
void tick() {
    static const bool on = getenv("D1_ND_POOL_WATCH") != nullptr;
    if (!on || !nr::g_base) return;
    if (!lo) {
        if (gpu_flip_count() > 30) start();
        return;
    }
    if (dirty.exchange(false)) protect();
    static uint64_t last = 0;
    if (gpu_flip_count() >= last + 300) {
        last = gpu_flip_count();
        std::lock_guard lk(m);
        std::string t;
        for (auto& [k, v] : sites) {
            char b[96];
            std::snprintf(b, sizeof b, " [eboot+%#llx field +%#x: %llu, pool %u]", (unsigned long long)k.first, k.second,
                          (unsigned long long)v.n, v.first_pool);
            t += b;
        }
        log("nd pool watch:%s", t.c_str());
    }
}
}  // namespace poolwatch

bool native_gfx_research_fault(void* uc, void* addr) {
    const uint64_t a = uint64_t(addr);
    if (!poolwatch::lo || a < poolwatch::lo || a >= poolwatch::hi) return false;
    uint64_t rip = 0;
#if defined(__linux__)
    rip = uint64_t(static_cast<ucontext_t*>(uc)->uc_mcontext.gregs[REG_RIP]);
#else
    (void)uc;  // (Windows: the research log has no code address)
#endif
    const uint64_t tbl = *reinterpret_cast<const uint64_t*>(nr::eb<uint64_t>(0x1A238A0));
    {
        std::lock_guard lk(poolwatch::m);
        auto& site = poolwatch::sites[{rip - nr::g_base, uint32_t((a - tbl) % 0x40)}];
        if (!site.n++) site.first_pool = uint32_t((a - tbl) / 0x40);
    }
    os::protect(reinterpret_cast<void*>(a & ~0xFFFull), 0x1000, os::kRead | os::kWrite);
    poolwatch::dirty = true;
    return true;
}

void native_gfx_flip(void* addr, uint32_t width, uint32_t height) {
    poolwatch::tick();
    if (!nr::g_base || !ng::active()) return;
    if (nr::g_frame_executed) {
        ++nr::g_executed_frames;
        bool dump = nr::g_dump_every && nr::g_executed_frames % uint64_t(nr::g_dump_every) == 0;
        // D1_NG_SNAP=<state prefix>:<secs>: (testing) <secs> after the game enters that state,
        // log the next frame's passes and dump it (with D1_NG_FRAMES / D1_NG_TARGETS)
        static const char* snap = getenv("D1_NG_SNAP");
        static int snap_phase = 0;  // 0 waiting, 1 armed (passlog requested), 2 done
        static int snap_more = 0;
        if (snap_phase == 2 && snap_more > 0) dump = true, --snap_more;
        if (snap && snap_phase < 2) {
            static std::chrono::steady_clock::time_point t_in{};
            const char* colon = std::strrchr(snap, ':');
            const size_t n = colon ? size_t(colon - snap) : std::strlen(snap);
            const char* gs = game_state();
            if (snap_phase == 1) {
                dump = true, snap_phase = 2;
                log("native gfx: snapshot at state '%s'", gs ? gs : "?");
                // D1_NG_SNAP_FRAMES=<n>: and the n frames after it (flicker hunting)
                if (const char* v = getenv("D1_NG_SNAP_FRAMES")) snap_more = std::atoi(v);
            } else if (gs && std::strncmp(gs, snap, n) == 0) {
                if (t_in == std::chrono::steady_clock::time_point{}) t_in = std::chrono::steady_clock::now();
                else if (std::chrono::duration<double>(std::chrono::steady_clock::now() - t_in).count() > (colon ? std::atof(colon + 1) : 0)) {
                    nr::g_every = 1;
                    ng::request_passlog(getenv("D1_NG_PASSLOG_N") ? uint32_t(std::max(1, std::atoi(getenv("D1_NG_PASSLOG_N")))) : 1u);
                    snap_phase = 1;
                }
            }
        }
        static const bool log_reloads = getenv("D1_NG_LOG_RELOADS") != nullptr;
        if (log_reloads) log("ng flip %llu", (unsigned long long)gpu_flip_count());
        const auto f0 = std::chrono::steady_clock::now();
        ng::flip(uint64_t(addr), width, height, gpu_flip_count(), dump);
        const uint64_t flip_ns = uint64_t(std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now() - f0).count());
        nr::g_flip_ns += flip_ns;
        {  // frames that take more than 40 ms (hitches): what they did
            static auto last = std::chrono::steady_clock::now();
            static uint64_t exec0 = 0, faults0 = 0;
            static ng::Counters c0 = ng::counters();
            const auto now = std::chrono::steady_clock::now();
            const double ms = std::chrono::duration<double, std::milli>(now - last).count();
            const ng::Counters c = ng::counters();
            const uint64_t faults = wt::g_faults.load();
            static int told = 0;
            if (ms > 40.0 && told < 300) {
                ++told;
                const char* gs = game_state();
                log("slow frame: %.1f ms | recording %.1f ms, present %.1f ms | new pipelines %llu, shaders %llu, textures %llu "
                    "(%.1f MiB) | %llu draws, %llu write faults (%s)",
                    ms, double(nr::g_exec_ns >= exec0 ? nr::g_exec_ns - exec0 : nr::g_exec_ns) / 1e6, double(flip_ns) / 1e6,
                    (unsigned long long)(c.pipelines - c0.pipelines), (unsigned long long)(c.shaders - c0.shaders),
                    (unsigned long long)(c.textures - c0.textures), double(c.tex_bytes - c0.tex_bytes) / 1048576.0,
                    (unsigned long long)(c.draws - c0.draws), (unsigned long long)(faults - faults0), gs ? gs : "?");
            }
            last = now, exec0 = nr::g_exec_ns, faults0 = faults, c0 = c;
        }
        // title bar: frames per second over the last second; log stats every minute or so
        static auto t0 = std::chrono::steady_clock::now();
        static uint64_t n0 = 0;
        const auto now = std::chrono::steady_clock::now();
        const double secs = std::chrono::duration<double>(now - t0).count();
        if (secs >= 1.0) {
            const uint64_t n = nr::g_executed_frames;
            const double fps = double(n - n0) / secs;
#ifdef D1_FRONTEND_SDL
            char title[256];
            std::snprintf(title, sizeof title, "Destiny (d1-native) - %.0f fps (%.1f ms) - %s%s", fps,
                          fps > 0 ? 1000.0 / fps : 0.0, ng::gpu_name(), ng::debug_toggle_text());
            frontend::set_status(title);
#endif
            static int report = 0;
            if (++report % (getenv("D1_NG_STATS") ? 5 : 15) == 1) {
                const double frames = double(std::max<uint64_t>(1, n - n0));
                static uint64_t faults0 = 0, fault_frames0 = 0;
                const uint64_t faults = wt::g_faults.load();
                const double fault_frames = double(std::max<uint64_t>(1, n - fault_frames0));
                fault_frames0 = n;
                static uint64_t dropped0 = 0, late0 = 0;
                log("native gfx: %.1f fps | per frame: record %.1f ms, present+wait %.1f ms, %.0f write faults | "
                    "%llu draws never submitted, %llu run in a later frame", fps,
                    double(nr::g_exec_ns) / 1e6 / frames, double(nr::g_flip_ns) / 1e6 / frames,
                    double(faults - faults0) / fault_frames, (unsigned long long)(nr::g_dropped - dropped0),
                    (unsigned long long)(nr::g_late - late0));
                // the game's side: its frame (submit to submit), the part blocked on GPU events, the
                // part blocked on a full GPU queue (it is ahead of the renderer)
                auto& gp = render::perf();
                static uint64_t gf0 = 0, gn0 = 0, gw0 = 0, qw0 = 0;
                const uint64_t gf = gp.guest_frames, gn = gp.guest_ns, gw = gp.guest_wait_ns, qw = gpu_queue_wait_ns();
                const double gfr = double(std::max<uint64_t>(1, gf - gf0));
                log("native gfx: game frame %.1f ms (waiting for GPU events %.1f ms, for the GPU queue %.1f ms)",
                    double(gn - gn0) / 1e6 / gfr, double(gw - gw0) / 1e6 / gfr, double(qw - qw0) / 1e6 / gfr);
                gf0 = gf, gn0 = gn, gw0 = gw, qw0 = qw;
                dropped0 = nr::g_dropped, late0 = nr::g_late;
                faults0 = faults;
                ng::print_stats();
                if (wt::g_log_faults) wt::print_census(), faultlog::print();
            }
            t0 = now, n0 = n;
            nr::g_exec_ns = nr::g_flip_ns = 0;
        }
    }
    nr::g_frame_executed = false;
}

}  // namespace d1
