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
#include "runtime.h"
#include "tiling.h"

#ifndef _WIN32
#include <sys/syscall.h>
#include <unistd.h>
#endif

namespace d1 {

void* hook_eboot_function(uint64_t off, const void* host);  // hooks.cpp
uint64_t guest_region_extent(uint64_t addr);                // hle_kernel.cpp
uint64_t gpu_flip_count();                                  // hle_gpu.cpp

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
std::vector<ng::Draw*> g_pending;
uint32_t g_seq = 0;
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
std::vector<CbEvent> g_cb_pending;
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

// Common state of every draw, read from the device object.
ng::Draw* capture(uint64_t dev, uint32_t engine_prim, uint64_t caller = 0) {
    auto* d = new ng::Draw;
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
        }
    }
    for (int s = 0; s < 2; ++s) {
        const uint32_t gnm = s ? 1 : 2;
        for (int i = 0; i < 16; ++i) {
            if (const uint64_t t = field<uint64_t>(dev, 0x1E78 + gnm * 0x80 + i * 8); t >= 0x10000) {
                std::memcpy(d->tex[s][i], reinterpret_cast<const void*>(t), 32);
                d->tex_mask[s] |= uint16_t(1u << i);
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
    return d;
}

void push(ng::Draw* d) {
    std::lock_guard lk(g_m);
    d->seq = g_seq++;
    d->frame = uint32_t(gpu_flip_count());
    g_pending.push_back(d);
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

thread_local uint32_t t_instances = 1;  // set by the instanced draw around its draw_indexed call
D1_SYSV void r_draw_indexed(uint64_t dev, uint64_t prim, uint64_t a, int32_t first, uint32_t count) {
    if (field<uint8_t>(dev, 0x26)) {
        ng::Draw* d = nr::capture(dev, uint32_t(prim), uint64_t(__builtin_return_address(0)));
        d->kind = ng::Draw::Indexed;
        const uint64_t ib = field<uint64_t>(dev, 0x1D70);
        const uint32_t isz = ib ? field<uint32_t>(ib, 0x38) : 0;
        d->index32 = isz != 0;
        d->index_addr = ib ? field<uint64_t>(ib, 0x30) + uint64_t(uint32_t((isz * 2 + 2) * first)) : 0;
        d->count = count;
        d->instances = t_instances;
        nr::push(d);
    }
    o_draw_indexed(dev, prim, a, first, count);
}
D1_SYSV void r_draw(uint64_t dev, uint64_t prim, uint32_t count) {
    if (field<uint8_t>(dev, 0x26)) {
        ng::Draw* d = nr::capture(dev, uint32_t(prim), uint64_t(__builtin_return_address(0)));
        d->kind = ng::Draw::Auto;
        d->count = count;
        nr::push(d);
    }
    o_draw(dev, prim, count);
}
D1_SYSV void r_draw_instanced(uint64_t dev, uint32_t prim, uint32_t count, uint64_t a, uint32_t instances) {
    if (field<uint8_t>(dev, 0x26)) {
        ng::Draw* d = nr::capture(dev, prim, uint64_t(__builtin_return_address(0)));
        d->kind = ng::Draw::Auto;
        d->count = count, d->instances = instances;
        nr::push(d);
    }
    o_draw_instanced(dev, prim, count, a, instances);
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
    o_draw_quads(dev, prim, first, prims);
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
    o_draw_inline(dev, prim, prims, data, stride);
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
    std::lock_guard lk(nr::g_m);
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
            nr::g_cb_pending.push_back({order, nr::g_seq++, uint8_t(s), uint8_t(first + k), cb});
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
std::unordered_map<uint64_t, VCached> g_vcache;
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

bool native_gfx_on_fault(void* addr) { return nr::g_base && ng::active() && wt::on_fault(uint64_t(addr)); }
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
        ok &= hook(0xF8B500, &r_set_cbs, o_set_cbs, "set_constant_buffers");
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
    {
        std::lock_guard lk(nr::g_m);
        auto& pend = nr::g_pending;
        size_t keep = 0;
        for (ng::Draw* d : pend) {
            // position in the submission: (range in traversal order, offset inside it)
            int64_t rng = -1;
            for (size_t r = 0; r < ranges.size(); ++r)
                if (d->order >= ranges[r].first && d->order < ranges[r].second) {
                    rng = int64_t(r);
                    break;
                }
            if (rng >= 0) mine.push_back({uint64_t(rng) << 40 | ((d->order - ranges[size_t(rng)].first) & 0xFFFFFFFFFFull), d});
            else if (nr::g_seq - d->seq < 200000) pend[keep++] = d;
            else {  // never submitted
                ++nr::g_dropped;
                static const bool log_drop = getenv("D1_NG_LOG_DROPS") != nullptr;
                static int n = 0;
                if (log_drop && n++ < 100) {
                    // the nearest range, to see where the draw's recorded position went
                    int64_t best = -1;
                    uint64_t dist = ~0ull;
                    for (size_t r = 0; r < ranges.size(); ++r) {
                        const uint64_t dd = d->order < ranges[r].first ? ranges[r].first - d->order : d->order >= ranges[r].second ? d->order - ranges[r].second : 0;
                        if (dd < dist) dist = dd, best = int64_t(r);
                    }
                    log("ng drop: draw ps %p from %#llx recorded at %#llx (flip %u), nearest range %lld [%#llx, %#llx) off by %llu",
                        (const void*)d->ps, (unsigned long long)d->caller, (unsigned long long)d->order, d->frame, (long long)best,
                        best >= 0 ? (unsigned long long)ranges[size_t(best)].first : 0ull,
                        best >= 0 ? (unsigned long long)ranges[size_t(best)].second : 0ull, (unsigned long long)dist);
                }
                delete d;
            }
        }
        pend.resize(keep);
        for (auto& [pos, e] : events) {
            if (!queries && (e->kind == ng::Draw::ZPass || e->kind == ng::Draw::PredOn || e->kind == ng::Draw::PredOff)) {
                delete e;
                continue;
            }
            e->seq = nr::g_seq++;
            int64_t rng = -1;
            for (size_t r = 0; r < ranges.size(); ++r)
                if (pos >= ranges[r].first && pos < ranges[r].second) {
                    rng = int64_t(r);
                    break;
                }
            if (rng >= 0) mine.push_back({uint64_t(rng) << 40 | ((pos - ranges[size_t(rng)].first) & 0xFFFFFFFFFFull), e});
            else delete e;
        }
        // constant buffer bindings recorded in this submission's command buffers, merged in order
        if (nr::g_ce_order) {
            std::vector<std::pair<std::pair<uint64_t, uint32_t>, const nr::CbEvent*>> evs;
            auto& cp = nr::g_cb_pending;
            std::vector<nr::CbEvent> mine_ev;
            size_t kept = 0;
            for (const auto& e : cp) {
                int64_t rng = -1;
                for (size_t r = 0; r < ranges.size(); ++r)
                    if (e.order >= ranges[r].first && e.order < ranges[r].second) {
                        rng = int64_t(r);
                        break;
                    }
                if (rng >= 0) {
                    mine_ev.push_back(e);
                    mine_ev.back().order = uint64_t(rng) << 40 | ((e.order - ranges[size_t(rng)].first) & 0xFFFFFFFFFFull);
                } else if (nr::g_seq - e.seq < 2000000) cp[kept++] = e;
            }
            cp.resize(kept);
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
    // D1_NG_EVERY_WORLD=<secs>: (testing) draw every frame from <secs> after reaching the world
    static const double every_world = getenv("D1_NG_EVERY_WORLD") ? std::atof(getenv("D1_NG_EVERY_WORLD")) : -1;
    if (every_world >= 0 && nr::g_every > 1) {
        static std::chrono::steady_clock::time_point t_world{};
        const char* gs = game_state();
        if (gs && std::strcmp(gs, "activity:in_world") == 0) {
            if (t_world == std::chrono::steady_clock::time_point{}) t_world = std::chrono::steady_clock::now();
            else if (std::chrono::duration<double>(std::chrono::steady_clock::now() - t_world).count() > every_world) {
                nr::g_every = 1;
                log("native gfx: now drawing every frame (D1_NG_EVERY_WORLD)");
                if (getenv("D1_NG_PASSLOG_N")) ng::request_passlog(uint32_t(std::atoi(getenv("D1_NG_PASSLOG_N"))));
            }
        }
    }
    const bool run = (gpu_flip_count() % uint64_t(nr::g_every)) == 0;
    if (run && !mine.empty()) {
        std::vector<ng::Draw*> draws;
        for (auto& [k, d] : mine) draws.push_back(d);
        const auto t0 = std::chrono::steady_clock::now();
        ng::execute(draws);
        nr::g_exec_ns += uint64_t(std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now() - t0).count());
        nr::g_frame_executed = true;
    }
    for (auto& [k, d] : mine) delete d;
    return run && !mine.empty() && queries;  // (the renderer answered the occlusion dumps)
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
void native_gfx_flip(void* addr, uint32_t width, uint32_t height) {
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
        nr::g_flip_ns += uint64_t(std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now() - f0).count());
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
                dropped0 = nr::g_dropped, late0 = nr::g_late;
                faults0 = faults;
                ng::print_stats();
                if (wt::g_log_faults) wt::print_census();
            }
            t0 = now, n0 = n;
            nr::g_exec_ns = nr::g_flip_ns = 0;
        }
    }
    nr::g_frame_executed = false;
}

}  // namespace d1
