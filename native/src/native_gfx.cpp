// Native renderer device layer for Destiny 1.
//
// The engine draws through its "GPU device" object (eboot 0x7D8000-0x7E4000) over the
// statically linked Gnm library; see notes/D1_NATIVE_RENDERER_DEVICE_LAYER_2026-10-14.md.
// Every Gnm / Gnmx function that would build PS4 command buffers is replaced so draws and
// resource events go straight into per-context command lists recorded on the engine's own
// threads and executed by our Vulkan renderer (gfx/nrender.cpp). No PM4, no emulated GPU.
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
#include <tuple>
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
constexpr uint64_t kBlendIndex = 0x25B4, kRasterIndex = 0x25BC;
constexpr uint64_t kColorTarget0 = 0x26E4;

template <class T>
T field(uint64_t dev, uint64_t off) {
    T v;
    std::memcpy(&v, reinterpret_cast<const void*>(dev + off), sizeof v);
    return v;
}

uint64_t mix(uint64_t h, uint64_t v) {
    h ^= v + 0x9E3779B97F4A7C15ull + (h << 6) + (h >> 2);
    return h;
}

// ---- hooked device API (System V signatures as decompiled)
using DrawIndexedFn = D1_SYSV void (*)(uint64_t, uint64_t, uint64_t, int32_t, uint32_t);
using DrawFn = D1_SYSV void (*)(uint64_t, uint64_t, uint32_t);
using SetVertexBufferFn = D1_SYSV void (*)(uint64_t, uint32_t, uint32_t, uint32_t, int32_t);
using AllocConstantsFn = D1_SYSV uint64_t (*)(uint64_t, uint32_t, uint32_t, uint32_t);

DrawIndexedFn o_draw_indexed;
DrawFn o_draw;
SetVertexBufferFn o_set_vertex_buffer;
AllocConstantsFn o_alloc_constants;

bool nd_push(uint64_t dev, ng::Draw* d);

namespace nr {

uint64_t g_base = 0;  // eboot base
template <class T>
T eb(uint64_t off) {
    T v;
    std::memcpy(&v, reinterpret_cast<const void*>(g_base + off), sizeof v);
    return v;
}

using BuildVsharpFn = D1_SYSV void (*)(void*, uint64_t, uint32_t, uint32_t, uint32_t);
BuildVsharpFn build_vsharp;

struct DevState {
    ng::Draw::Cb cb[ng::kStages][16] = {};
    uint32_t vb_count[32] = {};
    uint32_t vb_handle[32] = {
        0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu,
        0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu,
        0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu,
        0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFFu};
    uint32_t vb_offset[32] = {};
    int32_t vb_raw_count[32] = {};
};

std::mutex g_m;
std::unordered_map<uint64_t, DevState*> g_devs;
int g_every = 1;            // execute every Nth frame
int g_dump_every = 0;       // write every Nth executed frame (0: none)
uint64_t g_executed_frames = 0;
bool g_frame_executed = false;
uint64_t g_exec_ns = 0, g_flip_ns = 0;

struct CbEvent {
    uint64_t order;
    uint32_t seq;
    uint8_t stage, slot;
    ng::Draw::Cb cb;
};
ng::Draw::Cb g_ce[ng::kStages][16] = {};  // bindings as of the end of the last submission
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
    const int32_t hs = int32_t(h) >> 13;
    const uint64_t pool = tbl + uint64_t(((uint32_t(hs) >> 18) | 0x3FF) & uint32_t(hs)) * 0x40;
    const uint64_t pbase = field<uint64_t>(pool, 0x10);
    const uint64_t off = uint64_t(h & 0x1FFF) * field<uint32_t>(pool, 0x30);
    const uint64_t mask = uint64_t(int64_t(field<int32_t>(pool, 0x34)));
    return (pbase + off) - (mask & field<uint64_t>(pbase + off, 8));
}
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
// the T#), vertex buffer (4), index buffer (6), pixel shader (8) or vertex shader (9) bumps
// the object's epoch and triggers background GPU preparation.
namespace resreg {
constexpr uint32_t kBits = 18;
constexpr size_t kSlots = size_t(1) << kBits, kProbe = 64;
struct Slot { std::atomic<uint64_t> key{0}, val{0}; std::atomic<uint32_t> handle{0xFFFFFFFFu}; };
Slot* g_slots = nullptr;
std::mutex g_wm;
uint32_t g_next_id = 0;
size_t g_used = 0;
std::atomic<uint64_t> g_events{0};
bool g_on = false;
inline size_t home(uint64_t k) { return size_t((k * 0x9E3779B97F4A7C15ull) >> (64 - kBits)); }
inline uint64_t get(uint64_t key) {
    if (!g_slots || key < 0x10000) return 0;
    const size_t h = home(key);
    for (size_t i = 0; i < kProbe; ++i) {
        Slot& sl = g_slots[(h + i) & (kSlots - 1)];
        const uint64_t k = sl.key.load(std::memory_order_acquire);
        if (k == key) {
            const uint64_t v = sl.val.load(std::memory_order_acquire);
            const uint32_t hd = sl.handle.load(std::memory_order_relaxed);
            if (hd != 0xFFFFFFFFu && resolve_handle_safe(hd) != key) {
                static std::atomic<uint64_t> n{0};
                const uint64_t c = ++n;
                if ((c & (c - 1)) == 0 && c <= (1u << 20))
                    log("nd: stale resource registry entries ignored: %llu (object %#llx, handle %#x now names %#llx)", (unsigned long long)c,
                        (unsigned long long)key, hd, (unsigned long long)resolve_handle_safe(hd));
                return 0;
            }
            return v;
        }
        if (!k) return 0;
    }
    return 0;
}
void touch(uint64_t key, bool insert, uint32_t handle = 0xFFFFFFFFu) {
    if (!g_slots || key < 0x10000) return;
    std::lock_guard lk(g_wm);
    const size_t h = home(key);
    for (size_t i = 0; i < kProbe; ++i) {
        Slot& sl = g_slots[(h + i) & (kSlots - 1)];
        const uint64_t k = sl.key.load(std::memory_order_relaxed);
        if (k == key) {
            const uint64_t v = sl.val.load(std::memory_order_relaxed);
            if (handle != 0xFFFFFFFFu) sl.handle.store(handle, std::memory_order_relaxed);
            sl.val.store((v & ~0xFFFFFFFFull) | ((v + 1) & 0xFFFFFFFFull), std::memory_order_release);
            ++g_events;
            return;
        }
        if (!k) {
            if (!insert || g_used * 10 > kSlots * 7) return;
            sl.handle.store(handle, std::memory_order_relaxed);
            sl.val.store(uint64_t(++g_next_id) << 32 | 1, std::memory_order_relaxed);
            sl.key.store(key, std::memory_order_release);
            ++g_used, ++g_events;
            return;
        }
    }
}
// the resource object a (type, handle) names, 0 for the types the renderer does not track
uint64_t object_of(uint32_t type, uint32_t handle) {
    if (handle == 0xFFFFFFFFu || (!(type >= 1 && type <= 4) && type != 6 && type != 8 && type != 9 && type != 12 && type != 13)) return 0;
    const uint64_t o = resolve_handle_safe(handle);
    return o >= 0x10000 ? (type == 8 ? o + 8 : o) : 0;
}
// the renderer prepares the resource's GPU copy now (its loader thread)
void prefetch(uint32_t type, uint64_t o) {
    if (!o || !ng::active()) return;
    const uint64_t res = get(o);
    if (!res) return;
    if (type == 9 || type == 12 || type == 13) {
        ng::prefetch_shader(reinterpret_cast<const uint8_t*>(o), type == 9, res, o);
        return;
    }
    if ((type >= 1 && type <= 3) || type == 8) {
        const uint64_t tag = type == 8 ? o - 8 : o;
        const uint8_t full_mips = field<uint8_t>(tag, 0x31);
        const uint8_t has_hi = field<uint8_t>(tag, 0x34);
        const uint32_t* t = reinterpret_cast<const uint32_t*>(o);
        const uint32_t t_levels = ((t[3] >> 16) & 0xF) + 1;
        const uint64_t t_base = (uint64_t(t[0]) | uint64_t(t[1] & 0x3F) << 32) << 8;
        if (type != 8 && has_hi && full_mips > 1 && t_levels == uint32_t(full_mips - 1)) {
            ng::notify_texture_mips(t, res, tag, t_base, 0);
        }
        ng::prefetch_texture(t, res, tag);
    } else if (type == 4) ng::prefetch_buffer(field<uint64_t>(o, 0x28), field<uint32_t>(o, 0), res, o);
    else if (type == 6) {
        const uint32_t isz = field<uint32_t>(o, 0x38);
        ng::prefetch_buffer(field<uint64_t>(o, 0x30), uint64_t(field<uint32_t>(o, 0x3C)) * (isz ? 4 : 2), res, o);
    }
}
void event(uint32_t type, uint32_t handle, bool insert) {
    if (const uint64_t o = object_of(type, handle)) touch(o, insert, handle), prefetch(type, o);
}
void event_any(uint32_t handle) {
    if (handle == 0xFFFFFFFFu) return;
    if (const uint64_t o = resolve_handle_safe(handle)) touch(o, false, handle);
}
void init() {
    if (g_slots) return;
    g_slots = new Slot[kSlots];
    g_on = true;
}
}  // namespace resreg

ng::Draw* alloc_draw();

thread_local uint64_t t_capture_dev = 0;
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
    uint64_t vbsig = 0;
    if (const uint64_t decl = field<uint64_t>(dev, kVertexDecl)) {
        const uint32_t n = std::min(field<uint32_t>(decl, 0), 16u);
        d->num_vb = n;
        for (uint32_t i = 0; i < n; ++i) {
            const uint32_t fmt = field<uint32_t>(decl, 0x14 + 8 * i);
            const uint32_t off = field<uint8_t>(decl, 0x18 + 8 * i), stream = field<uint8_t>(decl, 0x19 + 8 * i) & 31;
            const uint32_t stride = field<uint32_t>(decl, 4 + 4 * (stream & 3));
            uint32_t h = field<uint32_t>(dev, 0x1D78 + 4 * stream);
            uint32_t stream_off = field<uint32_t>(dev, 0x1DF8 + 4 * stream);
            uint32_t vcnt = ds->vb_count[stream];
            // 0x7DEB70 (set_vertex_decl) resets dev+0x1D78[0..31] to 0xFFFFFFFF without unbinding
            // the CUE's vertex buffers; submesh loops (0x845DE0) switch vertex declarations between
            // submeshes of the same mesh without re-calling set_vertex_buffer for stream 0/1.
            if (h == 0xFFFFFFFFu && ds->vb_handle[stream] != 0xFFFFFFFFu) {
                h = ds->vb_handle[stream];
                stream_off = ds->vb_offset[stream];
                const uint64_t ro = resolve_handle_safe(h);
                if (ro >= 0x10000) {
                    uint32_t tot = field<uint32_t>(ro, 0x30);
                    if (stream_off != 0) tot = ds->vb_raw_count[stream] ? uint32_t(ds->vb_raw_count[stream]) : (stride ? tot - stream_off / stride : tot);
                    vcnt = tot;
                } else {
                    h = 0xFFFFFFFFu;
                }
            }
            if (h == 0xFFFFFFFFu || !stride) continue;
            const uint64_t obj = resolve_handle(h);
            const uint64_t base = field<uint64_t>(obj, 0x28) + off + stream_off;
            build_vsharp(d->vb[i], base, fmt, stride, vcnt);
            vbsig = mix(vbsig, uint64_t(i) << 48 | uint64_t(d->vb[i][1] >> 16) | uint64_t(d->vb[i][3]) << 32);
            if (resreg::g_on) d->vres[i] = {resreg::get(obj), field<uint64_t>(obj, 0x28), field<uint32_t>(obj, 0)};
        }
    }
    d->vb_sig = vbsig;
    for (int s = 0; s < 2; ++s) {
        const uint32_t gnm = s ? 1 : 2;
        for (int i = 0; i < 16; ++i) {
            if (const uint64_t t = field<uint64_t>(dev, 0x1E78 + gnm * 0x80 + i * 8); t >= 0x10000) {
                std::memcpy(d->tex[s][i], reinterpret_cast<const void*>(t), 32);
                d->tex_mask[s] |= uint16_t(1u << i);
                d->tex_res[s][i] = resreg::g_on ? resreg::get(t) : 0;
                d->tex_obj[s][i] = t;
            }
            if (const uint64_t p = field<uint64_t>(dev, (s ? 0x2278 : 0x22F8) + i * 8); p >= 0x10000) {
                std::memcpy(d->smp[s][i], reinterpret_cast<const void*>(p), 16);
                d->smp_mask[s] |= uint16_t(1u << i);
            }
            d->cb[s][i] = cs ? cs->cb[s][i] : ds->cb[s][i];
        }
    }
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
    d->kind = ng::Draw::Auto, d->prim = 4, d->index32 = 0, d->clear_flags = 0;
    d->count = 0, d->instances = 1, d->index_addr = 0, d->order = 0, d->seq = 0, d->frame = 0, d->caller = 0;
    d->vs = d->ps = nullptr, d->num_vb = 0;
    std::memset(d->vb, 0, sizeof d->vb);
    for (auto& r : d->vres) r = {};
    d->ires = {};
    d->tex_mask[0] = d->tex_mask[1] = d->smp_mask[0] = d->smp_mask[1] = 0;
    d->tex_filter_mask[0] = d->tex_filter_mask[1] = 0;
    d->tex_sig[0] = d->tex_sig[1] = d->vb_sig = 0;
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

void push(ng::Draw* d) {
    if (nd_push(t_capture_dev, d)) return;
    release_draw(d);
}

}  // namespace nr

using DrawInstancedFn = D1_SYSV void (*)(uint64_t, uint32_t, uint32_t, uint64_t, uint32_t);
using DrawQuadsFn = D1_SYSV void (*)(uint64_t, uint32_t, uint64_t, int32_t);
using DrawInlineFn = D1_SYSV void (*)(uint64_t, uint32_t, int32_t, const void*, int32_t);
using ClearFn = D1_SYSV void (*)(uint64_t, uint32_t);
using DispatchFn = D1_SYSV void (*)(uint64_t, uint64_t, uint32_t, uint32_t, uint32_t, int32_t);
DrawInstancedFn o_draw_instanced;
using DrawIndexedInstancedFn = D1_SYSV void (*)(uint64_t, uint32_t, uint32_t, uint64_t, uint32_t, uint64_t, uint32_t);
DrawIndexedInstancedFn o_draw_indexed_instanced;
DrawQuadsFn o_draw_quads;
DrawInlineFn o_draw_inline;
ClearFn o_clear;
DispatchFn o_dispatch;

thread_local uint32_t t_instances = 1;
D1_SYSV void r_draw_indexed(uint64_t dev, uint64_t prim, uint64_t, int32_t first, uint32_t count) {
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
}
D1_SYSV void r_draw(uint64_t dev, uint64_t prim, uint32_t count) {
    if (field<uint8_t>(dev, 0x26)) {
        ng::Draw* d = nr::capture(dev, uint32_t(prim), uint64_t(__builtin_return_address(0)));
        d->kind = ng::Draw::Auto;
        d->count = count;
        nr::push(d);
    }
}
D1_SYSV void r_draw_instanced(uint64_t dev, uint32_t prim, uint32_t count, uint64_t, uint32_t instances) {
    if (field<uint8_t>(dev, 0x26)) {
        ng::Draw* d = nr::capture(dev, prim, uint64_t(__builtin_return_address(0)));
        d->kind = ng::Draw::Auto;
        d->count = count, d->instances = instances;
        nr::push(d);
    }
}
D1_SYSV void r_draw_indexed_instanced(uint64_t dev, uint32_t prim, uint32_t count, uint64_t a, uint32_t instances,
                                      uint64_t b, uint32_t first) {
    t_instances = instances ? instances : 1;
    o_draw_indexed_instanced(dev, prim, count, a, instances, b, first);
    t_instances = 1;
}
D1_SYSV void r_draw_quads(uint64_t dev, uint32_t prim, uint64_t first, int32_t prims) {
    ng::Draw* d = nr::capture(dev, prim, uint64_t(__builtin_return_address(0)));
    d->kind = ng::Draw::Indexed;
    d->index_addr = field<uint64_t>(field<uint64_t>(dev, 0), 0) + (first & 0xFFFFFFFF) * 2;
    d->count = nr::vertex_count(prim, uint32_t(prims));
    nr::push(d);
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
        uint64_t vbsig = 0;
        for (uint32_t i = 0; i < n; ++i) {
            nr::build_vsharp(d->vb[i], field<uint8_t>(decl, 0x18 + 8 * i),
                             field<uint32_t>(decl, 0x14 + 8 * i), uint32_t(stride), d->count);
            vbsig = mix(vbsig, uint64_t(i) << 48 | uint64_t(d->vb[i][1] >> 16) | uint64_t(d->vb[i][3]) << 32);
        }
        d->vb_sig = vbsig;
        nr::push(d);
    }
}
D1_SYSV void r_clear(uint64_t dev, uint32_t flags) {
    if (flags & 0xFC) {
        ng::Draw* d = nr::capture(dev, 0);
        d->kind = ng::Draw::Clear;
        d->clear_flags = uint8_t(flags);
        std::memcpy(d->clear_color, reinterpret_cast<const void*>(dev + 0x40), 16);
        const float z = field<float>(dev, 0x20);
        d->clear_depth = field<uint8_t>(dev, 0x24) ? z : nr::eb<float>(0x165FEB4) - z;
        d->clear_stencil = field<uint8_t>(dev, 0x25);
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
    if (handle != 0xFFFFFFFFu && s < 32) {
        nr::DevState* ds = nr::dev_state(dev);
        ds->vb_handle[s] = handle;
        ds->vb_offset[s] = offset;
        ds->vb_raw_count[s] = count;
        const uint32_t stride = decl ? field<uint32_t>(decl, 4 + 4 * (s & 3)) : 0;
        if (stride) {
            uint32_t n = field<uint32_t>(nr::resolve_handle(handle), 0x30);
            if (offset != 0) n = count ? uint32_t(count) : n - (stride ? offset / stride : 0);
            ds->vb_count[s] = n;
        }
    }
    o_set_vertex_buffer(dev, handle, stream, offset, count);
}
D1_SYSV void r_dispatch(uint64_t dev, uint64_t cs, uint32_t x, uint32_t y, uint32_t z, int32_t flag) {
    o_dispatch(dev, cs, x, y, z, flag);
}

template <class Fn>
bool hook(uint64_t off, Fn host, Fn& orig, const char* name) {
    void* t = hook_eboot_function(off, reinterpret_cast<const void*>(host));
    if (!t) {
        log("native gfx: hooking %s (eboot+%#llx) failed", name, (unsigned long long)off);
        return false;
    }
    orig = reinterpret_cast<Fn>(t);
    return true;
}

// ---------------------------------------------------------------------------- engine resource events
namespace resev {
uint64_t tex_base(const uint32_t* t) { return (uint64_t(t[0]) | uint64_t(t[1] & 0xFF) << 32) << 8; }
using SetFn = D1_SYSV uint64_t (*)(uint32_t, uint32_t, uint64_t);
SetFn o_bind, o_rebind;
D1_SYSV uint64_t h_bind(uint32_t type, uint32_t handle, uint64_t addr) {
    const uint64_t r = o_bind(type, handle, addr);
    nr::resreg::event(type, handle, true);
    return r;
}
D1_SYSV uint64_t h_rebind(uint32_t type, uint32_t handle, uint64_t addr) {
    const uint64_t r = o_rebind(type, handle, addr);
    nr::resreg::event(type, handle, true);
    return r;
}
using RelFn = D1_SYSV void (*)(uint32_t, uint32_t);
RelFn o_release;
D1_SYSV void h_release(uint32_t type, uint32_t handle) {
    o_release(type, handle);
    nr::resreg::event(type, handle, false);
}
using Two = D1_SYSV void (*)(uint64_t, uint64_t);
Two o_copy, o_swap;
D1_SYSV void h_copy(uint64_t a, uint64_t b) {
    o_copy(a, b);
    nr::resreg::event_any(uint32_t(a)), nr::resreg::event_any(uint32_t(b));
}
D1_SYSV void h_swap(uint64_t a, uint64_t b) {
    o_swap(a, b);
    nr::resreg::event_any(uint32_t(a)), nr::resreg::event_any(uint32_t(b));
}
using MipFn = D1_SYSV void (*)(uint32_t, uint64_t, uint64_t);
MipFn o_mips;
D1_SYSV void h_mips(uint32_t handle, uint64_t low_base, uint64_t hi_base) {
    o_mips(handle, low_base, hi_base);
    if (const uint64_t o = nr::resreg::object_of(1, handle)) {
        nr::resreg::touch(o, true, handle);
        const uint64_t res = nr::resreg::get(o);
        if (res && ng::active()) {
            ng::notify_texture_mips(reinterpret_cast<const uint32_t*>(o), res, o, low_base, hi_base);
        }
    }
}
using TechFn = D1_SYSV uint64_t (*)(uint64_t, uint64_t);
using TechVoidFn = D1_SYSV void (*)(uint64_t, uint64_t);
TechFn o_tech_a, o_tech_b;
TechVoidFn o_tech_c;
void note_tfx_technique(uint64_t tech) {
    if (tech < 0x10000 || !ng::active()) return;
    const uint32_t vs_h = field<uint32_t>(tech, 0x28);
    const uint32_t ps_h = field<uint32_t>(tech, 0x2A8);
    const uint64_t vs_o = vs_h != 0xFFFFFFFFu ? nr::resolve_handle_safe(vs_h) : 0;
    const uint64_t ps_o = ps_h != 0xFFFFFFFFu ? nr::resolve_handle_safe(ps_h) : 0;
    if (vs_o >= 0x10000) nr::resreg::touch(vs_o, true, vs_h);
    if (ps_o >= 0x10000) nr::resreg::touch(ps_o, true, ps_h);
    if (vs_o >= 0x10000 || ps_o >= 0x10000) {
        ng::prefetch_shader_pair(vs_o >= 0x10000 ? reinterpret_cast<const uint8_t*>(vs_o) : nullptr,
                                 ps_o >= 0x10000 ? reinterpret_cast<const uint8_t*>(ps_o) : nullptr);
    }
}
D1_SYSV uint64_t h_tech_a(uint64_t ctx, uint64_t tech) {
    note_tfx_technique(tech);
    return o_tech_a(ctx, tech);
}
D1_SYSV uint64_t h_tech_b(uint64_t ctx, uint64_t tech) {
    note_tfx_technique(tech);
    return o_tech_b(ctx, tech);
}
D1_SYSV void h_tech_c(uint64_t ctx, uint64_t tech) {
    note_tfx_technique(tech);
    o_tech_c(ctx, tech);
}
D1_SYSV void h_unlock(uint64_t idx) {
    const uint64_t e = nr::g_base + 0x26F23B0 + (idx & 0xFFFFFFFFull) * 0xE0;
    const uint64_t ptr = field<uint64_t>(e, (field<uint32_t>(e, 0) & 8) ? 0x48 : 0x40);
    *reinterpret_cast<uint8_t*>(e + 2) &= 0xFB;
    ng::cpu_wrote(ptr, 0);
}
using GlyphFn = D1_SYSV void (*)(uint64_t);
GlyphFn o_glyph_upload;
std::atomic<uint64_t> g_glyph_uploads{0}, g_tiled{0};
D1_SYSV void h_glyph_upload(uint64_t self) {
    o_glyph_upload(self);
    const uint64_t c = field<uint64_t>(self, 0);
    if (c < 0x10000) return;
    const int32_t idx = field<int32_t>(c, 0x34);
    if (idx < 0 || idx > 8) return;
    for (int k = 0; k < 2; ++k) {
        const uint64_t t = field<uint64_t>(c, 0x20 + (uint64_t(idx) + k) * 8);
        if (t >= 0x10000) ng::cpu_wrote(tex_base(reinterpret_cast<const uint32_t*>(t)), 0);
    }
    ++g_glyph_uploads;
}
using TileFn = D1_SYSV uint64_t (*)(uint64_t, uint64_t, uint64_t);
TileFn o_tile;
D1_SYSV uint64_t h_tile(uint64_t out, uint64_t in, uint64_t tp) {
    const uint64_t r = o_tile(out, in, tp);
    if (out >= 0x10000) ng::cpu_wrote(out, 1);
    ++g_tiled;
    return r;
}

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
    ok &= hook(0xCFCC0, &h_register, o_register, "resource_callbacks_register");
    if (!replace_eboot_function(0x818FA0, reinterpret_cast<const void*>(&h_unlock))) ok = false, log("nd: replacing texture_unlock failed");
    patch_table();
    ok &= hook(0x7D3560, &h_copy, o_copy, "resource_move_copy");
    ok &= hook(0x7D37B0, &h_swap, o_swap, "resource_move_commit");
    ok &= hook(0x7D4480, &h_mips, o_mips, "texture_mips");
    ok &= hook(0x82B490, &h_tech_a, o_tech_a, "tfx_technique_apply_a");
    ok &= hook(0x82B5C0, &h_tech_b, o_tech_b, "tfx_technique_apply_b");
    ok &= hook(0x82B730, &h_tech_c, o_tech_c, "tfx_technique_apply_c");
    ok &= hook(0x8BE050, &h_glyph_upload, o_glyph_upload, "glyph_cache_upload");
    ok &= hook(0xF8A330, &h_tile, o_tile, "tile_surface");
    log("nd: engine resource events %s", ok ? "hooked" : "NOT HOOKED");
    if (!ok) nr::resreg::g_on = false;
}
}  // namespace resev

// ---------------------------------------------------------------------------- native device layer
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
    std::vector<uint8_t*> chunks;
    size_t used = 0;
    bool eop = false;
    uint64_t made = 0;
    bool recorded = false;
    uint32_t handle = 0;
    std::vector<ng::LateCb> late;
    ng::Draw::Cb dflt[ng::kStages][16] = {};
};
std::mutex g_lists_m;
std::unordered_map<uint64_t, List*> g_lists;
std::atomic<uint64_t> g_next{1};
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
int ctx_of_cb(uint64_t cb) {
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
    if (!l) {
        l = new List;
        l->id = g_next++, l->dev = dev_addr(c), l->made = gpu_flip_count();
        g_ctx[c].cur.store(l, std::memory_order_relaxed);
    }
    return l;
}
void begin_list(uint64_t dev) {
    const int c = ctx_of_dev(dev);
    if (c < 0) return;
    if (List* old = g_ctx[c].cur.exchange(nullptr)) {
        std::lock_guard lk(g_lists_m);
        g_lists[old->id] = old;
    }
    auto* l = new List;
    l->id = g_next++, l->dev = dev, l->made = gpu_flip_count();
    g_ctx[c].cur.store(l, std::memory_order_relaxed);
    ++g_lists_made;
}
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
void record(List* l) {
    if (!ng::list_recording() || l->items.empty()) return;
    if (gpu_flip_count() % uint64_t(nr::g_every) != 0) return;
    ng::Draw::Cb local[ng::kStages][16] = {};
    bool bound[ng::kStages][16] = {};
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
List* end_list(uint64_t dev) {
    const int c = ctx_of_dev(dev);
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
    o_end(dev, rec, kind);
    if (const int c = ctx_of_dev(dev); c >= 0) g_ctx[c].cur.store(nullptr, std::memory_order_relaxed);
}
D1_SYSV void h_end_submit(uint64_t dev) {
    end_list(dev);
    const int c = ctx_of_dev(dev);
    o_end_submit(dev);
    if (c >= 0) g_ctx[c].cur.store(nullptr, std::memory_order_relaxed);
}

D1_SYSV uint64_t s_noop() { return 0; }
constexpr uint64_t kArenaChunk = 256 << 10, kArenaSize = 1ull << 30;
std::mutex g_arena_m;
uint8_t* g_arena = nullptr;
std::vector<uint32_t> g_arena_free;
uint8_t* arena_chunk() {
    std::lock_guard lk(g_arena_m);
    if (!g_arena) {
        for (uint64_t at : {0xF80000000ull, 0xF00000000ull, 0xE80000000ull, 0xE00000000ull, 0xD00000000ull}) {
            void* p = os::alloc(at, kArenaSize, os::kRead | os::kWrite, true);
            if (p == reinterpret_cast<void*>(at)) { g_arena = static_cast<uint8_t*>(p); break; }
            if (p) os::release(p, kArenaSize);
        }
        if (!g_arena) { log("nd: no command-buffer arena below 1 TiB"); return nullptr; }
        for (uint32_t i = uint32_t(kArenaSize / kArenaChunk); i-- > 0;) g_arena_free.push_back(i);
        log("nd: command-buffer arena at %p (%llu MiB)", (void*)g_arena, (unsigned long long)(kArenaSize >> 20));
    }
    if (g_arena_free.empty()) return nullptr;
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
D1_SYSV void* s_alloc(uint64_t cb, uint32_t bytes, uint32_t align_log2) {
    const uint64_t align = uint64_t(1) << std::min(align_log2, 12u);
    const int c = ctx_of_cb(cb);
    List* l = list_of(c);
    const size_t need = size_t(bytes) + align;
    if (need > kArenaChunk) return nullptr;
    if (!l) {
        std::lock_guard lk(g_global_alloc_m);
        static uint8_t* cur = nullptr;
        static size_t used = 0;
        if (!cur || used + need > kArenaChunk) {
            g_global_alloc_m.unlock();
            uint8_t* ch = arena_chunk();
            g_global_alloc_m.lock();
            if (!ch) return nullptr;
            g_global_alloc.push_back(ch), cur = ch, used = 0;
        }
        const uint64_t p = (uint64_t(cur) + used + align - 1) & ~(align - 1);
        used = size_t(p - uint64_t(cur)) + bytes;
        return reinterpret_cast<void*>(p);
    }
    if (l->chunks.empty() || l->used + need > kArenaChunk) {
        uint8_t* ch = arena_chunk();
        if (!ch) return nullptr;
        l->chunks.push_back(ch);
        l->used = 0;
    }
    const uint64_t base = uint64_t(l->chunks.back());
    const uint64_t p = (base + l->used + align - 1) & ~(align - 1);
    l->used = size_t(p - base) + bytes;
    return reinterpret_cast<void*>(p);
}
D1_SYSV void s_eop_label(uint64_t cb, uint32_t, uint32_t, uint64_t addr, uint32_t data_sel, uint64_t data, uint32_t,
                         uint32_t int_sel) {
    List* l = list_of(ctx_of_cb(cb));
    if (!l) return;
    if (addr >= 0x10000 && (data_sel == 1 || data_sel == 2 || data_sel == 3)) {
        ng::Draw* d = nr::alloc_draw();
        d->kind = ng::Draw::WriteData;
        d->prim = ng::kEopLabel;
        d->caller = addr;
        d->inline_vertices.resize(data_sel == 1 ? 4 : 8);
        d->count = data_sel == 3;
        std::memcpy(d->inline_vertices.data(), &data, d->inline_vertices.size());
        l->items.push_back({d, {}});
    }
    if (int_sel) l->eop = true;
}
D1_SYSV void s_eop_interrupt(uint64_t cb) {
    if (List* l = list_of(ctx_of_cb(cb))) l->eop = true;
}
D1_SYSV void s_zpass(uint64_t cb, uint32_t end, uint64_t results) {
    const int c = ctx_of_cb(cb);
    if (c < 0 || results < 0x10000) return;
    ng::Draw* d = nr::alloc_draw();
    d->kind = ng::Draw::ZPass;
    d->index_addr = end == 1 ? results + 8 : results;
    add(c, d);
}
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
D1_SYSV void s_dma(uint64_t cb, uint64_t dst, uint64_t src, uint32_t bytes) {
    const int c = ctx_of_cb(cb);
    if (c < 0 || !bytes) return;
    ng::Draw* d = nr::alloc_draw();
    d->kind = ng::Draw::Dma;
    d->index_addr = src, d->caller = dst, d->count = bytes, d->prim = 0, d->index32 = 0;
    add(c, d);
}
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
        if (l) l->items.push_back({nullptr, nr::CbEvent{0, 0, uint8_t(s), uint8_t(first + k), cbv}});
    }
}

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

void answer_zpass(uint64_t dest, bool end) {
    if (guest_region_extent(dest) < 0x80) return;
    auto* q = reinterpret_cast<uint64_t*>(dest);
    for (int db = 0; db < 8; ++db) q[db * 2 + (end ? 1 : 0)] = (end ? 1000ull : 0ull) | (1ull << 63);
}

void install() {
    resev::install();
    g_on = true;
    bool ok = true;
    auto rep = [&](uint64_t off, const void* fn) {
        if (!replace_eboot_function(off, fn)) ok = false, log("nd: replacing eboot+%#llx failed", (unsigned long long)off);
    };
    static const uint32_t kNoops[] = {
        0xF7E740, 0xF7E7C0, 0xF7E840, 0xF7E8D0, 0xF7E950, 0xF7E9B0, 0xF7EA20, 0xF7EA80, 0xF7EAF0, 0xF7EB50, 0xF7EBB0,
        0xF7EC30, 0xF7ED40, 0xF7EEC0, 0xF7F1E0, 0xF7F260, 0xF7F320, 0xF7F4A0, 0xF7F790, 0xF7F7E0, 0xF7F840, 0xF7F890,
        0xF7FA90, 0xF7FCD0, 0xF7FD40, 0xF7FE20, 0xF80340, 0xF80440, 0xF804F0, 0xF80550, 0xF805C0, 0xF80640, 0xF806D0,
        0xF80730, 0xF80790, 0xF80830, 0xF808A0, 0xF80910, 0xF80E00, 0xF80F10, 0xF81090, 0xF81220,
        0xF7E5E0, 0xF84DB0, 0xF811C0,
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
namespace wt {
constexpr uint64_t kPage = 4096, kChunkBits = 30, kPagesPerChunk = 1ull << (kChunkBits - 12), kChunks = 128;
constexpr uint64_t kBlockPages = 16;
constexpr uint64_t kCoarsePages = 256;
enum : uint8_t { kOff = 0, kProtected = 1, kUnprotecting = 2 };
struct Chunk {
    std::atomic<uint32_t> gen[kPagesPerChunk];
    std::atomic<uint32_t> coarse[kPagesPerChunk / kCoarsePages];
    std::atomic<uint8_t> state[kPagesPerChunk];
    std::atomic<uint8_t> watched[kPagesPerChunk];
};
std::atomic<Chunk*> g_chunks[kChunks];
std::mutex g_alloc_m;
std::atomic<uint64_t> g_faults{0};
const bool g_log_faults = getenv("D1_NG_LOG_FAULTS") != nullptr || getenv("D1_NG_CENSUS") != nullptr;
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
        ch = new Chunk();
        g_chunks[c].store(ch, std::memory_order_release);
    }
    return ch;
}

uint64_t fine_version(uint64_t addr, uint64_t size) {
    uint64_t v = 0;
    for (uint64_t pg = addr / kPage, end = (addr + size + kPage - 1) / kPage; pg < end; ++pg) {
        Chunk* ch = chunk(pg, false);
        if (!ch) return ~0ull;
        const uint64_t i = pg & (kPagesPerChunk - 1);
        if (ch->state[i].load(std::memory_order_acquire) != kProtected) return ~0ull;
        v += ch->gen[i].load(std::memory_order_relaxed);
    }
    return v;
}

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

struct VCached { uint64_t addr, size, coarse, version; };
thread_local std::unordered_map<uint64_t, VCached> g_vcache;
uint64_t version(uint64_t addr, uint64_t size) {
    const uint64_t c = coarse_sum(addr, size);
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

void describe(uint64_t addr, char* out, size_t n) {
    const uint64_t pg = addr / kPage;
    Chunk* ch = chunk(pg, false);
    if (!ch) {
        std::snprintf(out, n, "no chunk");
        return;
    }
    const uint64_t i = pg & (kPagesPerChunk - 1);
    std::snprintf(out, n, "state %u gen %llu watched %u", unsigned(ch->state[i].load()),
                  (unsigned long long)ch->gen[i].load(), unsigned(ch->watched[i].load()));
}

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
            return ~0ull;
        }
    }
    flush();
    return version(addr, size);
}

void forget(uint64_t addr, uint64_t size) {
    for (uint64_t pg = addr / kPage, end = (addr + size + kPage - 1) / kPage; pg < end; ++pg) {
        Chunk* ch = chunk(pg, false);
        if (!ch) {
            pg |= kPagesPerChunk - 1;
            continue;
        }
        const uint64_t i = pg & (kPagesPerChunk - 1);
        ch->gen[i].fetch_add(1, std::memory_order_relaxed);
        ch->coarse[i / kCoarsePages].fetch_add(1, std::memory_order_release);
        ch->state[i].store(kOff, std::memory_order_release);
    }
}

bool on_fault(uint64_t addr) {
    const uint64_t pg = addr / kPage;
    Chunk* ch = chunk(pg, false);
    if (!ch) return false;
    const uint64_t i = pg & (kPagesPerChunk - 1);
    uint8_t expect = kProtected;
    if (ch->state[i].compare_exchange_strong(expect, kUnprotecting)) {
        const uint64_t blk = i & ~uint64_t(kBlockPages - 1);
        uint32_t taken = 1u << (i - blk);
        for (uint64_t k = 0; k < kBlockPages; ++k) {
            if (blk + k == i) continue;
            uint8_t e = kProtected;
            if (ch->state[blk + k].compare_exchange_strong(e, kUnprotecting)) taken |= 1u << k;
        }
        for (uint64_t k = 0; k < kBlockPages; ++k)
            if (taken >> k & 1) ch->gen[blk + k].fetch_add(1, std::memory_order_relaxed);
        ch->coarse[blk / kCoarsePages].fetch_add(1, std::memory_order_release);
        for (uint64_t k = 0; k < kBlockPages;) {
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
struct Site { uint64_t n = 0, sample = 0, lo = ~0ull, hi = 0; };
struct Key {
    uint64_t rip, c1, c2;
    bool operator<(const Key& o) const { return std::tie(rip, c1, c2) < std::tie(o.rip, o.c1, o.c2); }
};
std::map<Key, Site> sites;
// D1_NG_CENSUS=<file>: every writer since the start (not only the last interval's top 24), with
// the two guest callers above it (frame pointers) and the range of addresses it wrote
const char* const g_census = getenv("D1_NG_CENSUS");
static uint64_t rel(uint64_t a) { return a >= nr::g_base && a < nr::g_base + 0x4000000 ? a - nr::g_base : a | 1ull << 63; }
void note(void* uc, uint64_t addr) {
    uint64_t rip = 0, c1 = 0, c2 = 0;
#if defined(__linux__)
    const auto& gr = static_cast<ucontext_t*>(uc)->uc_mcontext.gregs;
    rip = uint64_t(gr[REG_RIP]);
    if (g_census) {  // the guest's frame chain (the engine keeps frame pointers)
        uint64_t bp = uint64_t(gr[REG_RBP]);
        const uint64_t sp = uint64_t(gr[REG_RSP]);
        uint64_t* out[2] = {&c1, &c2};
        // (a frame pointer is trusted while it stays on this thread's stack, above the stack
        // pointer; memcpy keeps none, so the first frame is its caller's)
        for (int k = 0, got = 0; k < 24 && got < 2 && !(bp & 7) && bp >= sp && bp < sp + (4u << 20); ++k) {
            const uint64_t ret = reinterpret_cast<const uint64_t*>(bp)[1];
            const uint64_t next = reinterpret_cast<const uint64_t*>(bp)[0];
            if (ret >= nr::g_base && ret < nr::g_base + 0x4000000) *out[got++] = ret - nr::g_base;
            if (next <= bp) break;
            bp = next;
        }
    }
#else
    (void)uc;
#endif
    std::lock_guard lk(m);
    Site& s = sites[{rel(rip), c1, c2}];
    if (!s.n++) s.sample = addr;
    s.lo = std::min(s.lo, addr), s.hi = std::max(s.hi, addr);
}
void print() {
    std::vector<std::pair<Key, Site>> v;
    {
        std::lock_guard lk(m);
        v.assign(sites.begin(), sites.end());
        if (!g_census) sites.clear();
    }
    std::sort(v.begin(), v.end(), [](auto& a, auto& b) { return a.second.n > b.second.n; });
    FILE* f = g_census ? std::fopen(g_census, "w") : nullptr;
    for (size_t i = 0; i < v.size() && (f || i < 24); ++i) {
        char owner[160] = "";
        ng::describe_owner(v[i].second.sample, owner, sizeof owner);
        char where[200] = "";
        const uint64_t rip = v[i].first.rip;
#if defined(__linux__)
        if (rip >> 63) {
            Dl_info di{};
            const uint64_t a = rip & ~(1ull << 63);
            if (dladdr(reinterpret_cast<void*>(a), &di) && di.dli_fname)
                std::snprintf(where, sizeof where, " [%s+%#llx %s]", di.dli_fname, (unsigned long long)(a - uint64_t(di.dli_fbase)),
                              di.dli_sname ? di.dli_sname : "");
        }
#endif
        if (f)
            std::fprintf(f, "%s%#llx%s <- %#llx <- %#llx | %llu faults | %#llx..%#llx | e.g. %#llx: %s\n", rip >> 63 ? "host " : "eboot+",
                         (unsigned long long)(rip & ~(1ull << 63)), where, (unsigned long long)v[i].first.c1, (unsigned long long)v[i].first.c2,
                         (unsigned long long)v[i].second.n, (unsigned long long)v[i].second.lo, (unsigned long long)v[i].second.hi,
                         (unsigned long long)v[i].second.sample, owner);
        else
            log("native gfx: write faults from %s%#llx%s: %llu (e.g. %#llx: %s)", rip >> 63 ? "host " : "eboot+",
                (unsigned long long)(rip & ~(1ull << 63)), where, (unsigned long long)v[i].second.n, (unsigned long long)v[i].second.sample, owner);
    }
    if (f) std::fclose(f);
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
bool native_gfx_research_fault(void*, void*) { return false; }

void native_gfx_install() {
    const char* mode = getenv("D1_NATIVE_GFX");
#ifndef D1_RENDERER_SHADPS4
    if (!mode) mode = "render";
#endif
    if (!mode || std::strcmp(mode, "render") != 0) return;
    nr::g_base = rt().modules[0].base;
    nr::build_vsharp = reinterpret_cast<nr::BuildVsharpFn>(nr::g_base + 0xF7CF90);
    if (const char* v = getenv("D1_NG_EVERY")) nr::g_every = std::max(1, std::atoi(v));
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
        opt.res_current = [](uint64_t obj) { return nr::resreg::get(obj); };
        opt.describe = [](uint64_t a, char* out, size_t n) { wt::describe(a, out, n); };
    }
    if (const char* v = getenv("D1_NG_FRAMES_IN_FLIGHT")) opt.frames_in_flight = uint32_t(std::max(1, std::atoi(v)));
#ifdef D1_FRONTEND_SDL
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
        if (opt.window_handles)
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
    nd::install();
    log("native gfx: rendering natively (every %d frame%s)%s", nr::g_every, nr::g_every == 1 ? "" : "s",
        ok ? "" : " (some hooks failed)");
}

static void nr_every_world() {
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
        static uint64_t sweep = 0;
        if (++sweep % 256 == 0) {
            for (auto it = nd::g_lists.begin(); it != nd::g_lists.end();) {
                if (it->second->made + 300 < gpu_flip_count()) {
                    if (it->second->recorded) ng::discard_recorded(it->second->handle);
                    ++nd::g_orphans, nd::free_list(it->second), it = nd::g_lists.erase(it);
                } else {
                    ++it;
                }
            }
        }
    }
    std::vector<ng::Draw*> draws;
    std::vector<uint32_t> recorded;
    std::vector<ng::Draw*> cpu_events;
    std::vector<std::pair<uint64_t, std::vector<uint8_t>>> labels;
    bool eop = false;
    for (nd::List* l : lists) {
        eop |= l->eop;
        if (l->recorded) {
            for (const ng::LateCb& lc : l->late) {
                const ng::Draw::Cb& c = nr::g_ce[lc.stage][lc.slot].addr ? nr::g_ce[lc.stage][lc.slot] : l->dflt[lc.stage][lc.slot];
                ng::fill_late(lc, c.addr, c.size);
            }
            recorded.push_back(l->handle);
            for (nd::Item& it : l->items) {
                if (!it.d) nr::g_ce[it.cb.stage][it.cb.slot] = it.cb.cb;
                else if (it.d->kind == ng::Draw::WriteData && it.d->prim == ng::kEopLabel) labels.push_back({it.d->caller | uint64_t(it.d->count) << 63, it.d->inline_vertices});
                else if (it.d->kind == ng::Draw::Dma || it.d->kind == ng::Draw::WriteData) cpu_events.push_back(it.d);
            }
            continue;
        }
        for (nd::Item& it : l->items) {
            if (!it.d) {
                nr::g_ce[it.cb.stage][it.cb.slot] = it.cb.cb;
                continue;
            }
            ng::Draw* d = it.d;
            if (d->kind == ng::Draw::WriteData && d->prim == ng::kEopLabel) {
                labels.push_back({d->caller | uint64_t(d->count) << 63, d->inline_vertices});
                continue;
            }
            if (d->kind <= ng::Draw::Clear)
                for (int st = 0; st < 2; ++st)
                    for (int sl = 0; sl < 16; ++sl)
                        if (nr::g_ce[st][sl].addr) d->cb[st][sl] = nr::g_ce[st][sl];
            draws.push_back(d);
        }
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
    for (nd::List* l : lists) nd::free_list(l);
    if (!labels.empty() || eop)
        ng::after_gpu([labels = std::move(labels), eop] {
            for (auto [tagged, bytes] : labels) {
                const uint64_t addr = tagged & ~(1ull << 63);
                if (tagged >> 63) {
                    const uint64_t t = uint64_t(std::chrono::duration_cast<std::chrono::nanoseconds>(
                                                    std::chrono::high_resolution_clock::now().time_since_epoch()).count());
                    std::memcpy(bytes.data(), &t, 8);
                }
                if (addr >= 0x10000 && guest_region_extent(addr) >= bytes.size()) std::memcpy(reinterpret_cast<void*>(addr), bytes.data(), bytes.size());
            }
            if (eop) gnm_signal_eop();
        });
}

void native_gfx_flip(void* addr, uint32_t width, uint32_t height) {
    if (!nr::g_base || !ng::active()) return;
    if (nr::g_frame_executed) {
        ++nr::g_executed_frames;
        bool dump = nr::g_dump_every && nr::g_executed_frames % uint64_t(nr::g_dump_every) == 0;
        static const char* snap = getenv("D1_NG_SNAP");
        static int snap_phase = 0;
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
        const auto f0 = std::chrono::steady_clock::now();
        ng::flip(uint64_t(addr), width, height, gpu_flip_count(), dump);
        const uint64_t flip_ns = uint64_t(std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now() - f0).count());
        nr::g_flip_ns += flip_ns;
        {
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
                log("native gfx: %.1f fps | per frame: record %.1f ms, present+wait %.1f ms, %.0f write faults",
                    fps, double(nr::g_exec_ns) / 1e6 / frames, double(nr::g_flip_ns) / 1e6 / frames,
                    double(faults - faults0) / fault_frames);
                auto& gp = render::perf();
                static uint64_t gf0 = 0, gn0 = 0, gw0 = 0, qw0 = 0;
                const uint64_t gf = gp.guest_frames, gn = gp.guest_ns, gw = gp.guest_wait_ns, qw = gpu_queue_wait_ns();
                const double gfr = double(std::max<uint64_t>(1, gf - gf0));
                log("native gfx: game frame %.1f ms (waiting for GPU events %.1f ms, for the GPU queue %.1f ms)",
                    double(gn - gn0) / 1e6 / gfr, double(gw - gw0) / 1e6 / gfr, double(qw - qw0) / 1e6 / gfr);
                gf0 = gf, gn0 = gn, gw0 = gw, qw0 = qw;
                faults0 = faults;
                ng::print_stats();
                if (wt::g_log_faults) wt::print_census(), faultlog::print();
                log("nd: texture updates announced at their source: %llu glyph cache uploads, %llu tiled surfaces",
                    (unsigned long long)resev::g_glyph_uploads.exchange(0), (unsigned long long)resev::g_tiled.exchange(0));
            }
            t0 = now, n0 = n;
            nr::g_exec_ns = nr::g_flip_ns = 0;
        }
    }
    nr::g_frame_executed = false;
}

}  // namespace d1
