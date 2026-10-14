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
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <unordered_set>

#include "hle.h"
#include "runtime.h"

#ifndef _WIN32
#include <sys/syscall.h>
#include <unistd.h>
#endif

namespace d1 {

void* hook_eboot_function(uint64_t off, const void* host);  // hooks.cpp
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

void note_draw(uint64_t dev, uint64_t prim) {
    std::lock_guard lk(g_obs->m);
    note_device(dev);
    ++g_obs->draws;
    const uint64_t vs = field<uint64_t>(dev, kVsShader), ps = field<uint64_t>(dev, kPsShader);
    const uint64_t decl = field<uint64_t>(dev, kVertexDecl);
    g_obs->vs.insert(vs);
    g_obs->ps.insert(ps);
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
D1_SYSV void h_set_texture(uint64_t dev, uint32_t stage, uint64_t slot, void* tsharp) {
    {
        std::lock_guard lk(g_obs->m);
        ++g_obs->binds_tex;
        g_obs->textures.insert(reinterpret_cast<uint64_t>(tsharp));
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
        g_obs->targets.insert(field<uint64_t>(dev, kColorTarget0));
    }
    o_apply_targets(dev);
}

template <class F>
bool hook(uint64_t off, F host, F& orig, const char* name) {
    orig = reinterpret_cast<F>(hook_eboot_function(off, reinterpret_cast<const void*>(host)));
    if (!orig) log("native gfx: hooking %s (eboot+%#llx) failed", name, (unsigned long long)off);
    return orig != nullptr;
}

}  // namespace

// Called once the eboot is loaded and relocated (with the other game hooks).
void native_gfx_install() {
    const char* mode = getenv("D1_NATIVE_GFX");
    if (!mode || std::strcmp(mode, "observe") != 0) return;
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

}  // namespace d1
