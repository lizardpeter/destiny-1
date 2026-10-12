// Event queues, video out and a "null GPU" for libSceGnmDriver.
//
// The null GPU walks submitted PM4 command buffers and performs only their memory side
// effects — end-of-pipe/end-of-shader fence writes, WRITE_DATA, DMA_DATA fills/copies —
// and raises the end-of-pipe interrupt. Nothing is drawn. This lets the game's frame
// pacing (which waits on GPU fences and flip events) run headless until a real renderer
// replaces it.
#include <sys/mman.h>
#include <time.h>
#include <x86intrin.h>

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstring>
#include <mutex>
#include <thread>
#include <vector>

#include "hle.h"
#include "runtime.h"

namespace d1 {

// ------------------------------------------------------------------ kernel event queues
struct KEvent {
    uint64_t ident;
    int16_t filter;
    uint16_t flags;
    uint32_t fflags;
    uint64_t data;
    void* udata;
};
static_assert(sizeof(KEvent) == 32);

constexpr int16_t kFilterUser = -11, kFilterVideoOut = -13, kFilterGraphics = -14;

struct Equeue {
    std::mutex m;
    std::condition_variable cv;
    struct Entry { KEvent ev; bool triggered; };
    std::vector<Entry> events;
    std::string name;

    void add(const KEvent& e) {
        std::lock_guard lk(m);
        for (auto& x : events)
            if (x.ev.ident == e.ident && x.ev.filter == e.filter) { x.ev = e; return; }
        events.push_back({e, false});
    }
    bool trigger(uint64_t ident, int16_t filter, uint64_t data, bool display = false) {
        bool found = false;
        {
            std::lock_guard lk(m);
            for (auto& x : events)
                if (x.ev.ident == ident && x.ev.filter == filter) {
                    if (display) {
                        uint64_t counter = (x.ev.data >> 12) & 0xF;
                        if (counter != 0xF) ++counter;
                        x.ev.data = (__rdtsc() & 0xFFF) | (counter << 12) | (data & 0xFFFFFFFFFFFF0000ull);
                    } else {
                        x.ev.data = data;
                    }
                    x.triggered = true;
                    found = true;
                }
        }
        cv.notify_all();
        return found;
    }
};

static std::mutex g_eq_mutex;
static std::vector<Equeue*> g_equeues;

static int32_t sceKernelCreateEqueue(Equeue** out, const char* name) {
    auto* q = new Equeue;
    if (name) q->name = name;
    { std::lock_guard lk(g_eq_mutex); g_equeues.push_back(q); }
    *out = q;
    return SCE_OK;
}
HLE("sceKernelCreateEqueue", sceKernelCreateEqueue)
static int32_t sceKernelDeleteEqueue(Equeue* q) { return SCE_OK; }
HLE("sceKernelDeleteEqueue", sceKernelDeleteEqueue)

static int32_t sceKernelWaitEqueue(Equeue* q, KEvent* ev, int num, int* out, uint32_t* timeout_us) {
    std::unique_lock lk(q->m);
    auto any = [&] { for (auto& x : q->events) if (x.triggered) return true; return false; };
    if (timeout_us) {
        if (!q->cv.wait_for(lk, std::chrono::microseconds(*timeout_us), any)) {
            if (out) *out = 0;
            return sce_err(60);
        }
    } else {
        q->cv.wait(lk, any);
    }
    int n = 0;
    for (auto& x : q->events)
        if (x.triggered && n < num) {
            ev[n++] = x.ev;
            x.triggered = false;
        }
    if (out) *out = n;
    return SCE_OK;
}
HLE("sceKernelWaitEqueue", sceKernelWaitEqueue)

static uint64_t sceKernelGetEventData(const KEvent* e) { return e->data; }
HLE("sceKernelGetEventData", sceKernelGetEventData)
static uint64_t sceKernelGetEventId(const KEvent* e) { return e->ident; }
HLE("sceKernelGetEventId", sceKernelGetEventId)
static int sceKernelGetEventFilter(const KEvent* e) { return e->filter; }
HLE("sceKernelGetEventFilter", sceKernelGetEventFilter)
static void* sceKernelGetEventUserData(const KEvent* e) { return e->udata; }
HLE("sceKernelGetEventUserData", sceKernelGetEventUserData)

static int32_t sceKernelAddUserEvent(Equeue* q, int id) {
    q->add({uint64_t(id), kFilterUser, 1, 0, 0, nullptr});
    return SCE_OK;
}
HLE("sceKernelAddUserEvent", sceKernelAddUserEvent)
HLE("sceKernelAddUserEventEdge", sceKernelAddUserEvent)
static int32_t sceKernelTriggerUserEvent(Equeue* q, int id, void* udata) {
    {
        std::lock_guard lk(q->m);
        for (auto& x : q->events)
            if (x.ev.ident == uint64_t(id) && x.ev.filter == kFilterUser) { x.ev.udata = udata; x.triggered = true; }
    }
    q->cv.notify_all();
    return SCE_OK;
}
HLE("sceKernelTriggerUserEvent", sceKernelTriggerUserEvent)
static int32_t sceKernelAddGpuExceptionEvent(Equeue* q, void* udata) {
    q->add({0x8000, kFilterGraphics, 1, 0, 0, udata});  // never triggered: the null GPU does not fault
    return SCE_OK;
}
HLE("sceKernelAddGpuExceptionEvent", sceKernelAddGpuExceptionEvent)

// ------------------------------------------------------------------ video out
struct FlipStatus {
    uint64_t count, process_time, tsc;
    int64_t flip_arg;
    uint64_t submit_tsc, reserved0;
    int32_t gc_queue_num, flip_pending_num, current_buffer;
    uint32_t reserved1;
};
struct BufferAttribute {
    uint32_t pixel_format, tiling_mode, aspect_ratio, width, height, pitch_in_pixel;
    uint64_t option;
    uint32_t reserved0;
    uint64_t reserved1;
};
static struct VideoOutPort {
    std::mutex m;
    FlipStatus status{0, 0, 0, -1, 0, 0, 0, 0, -1, 0};
    void* buffers[16] = {};
    BufferAttribute attr{};
    int registered = 0;
    alignas(64) uint64_t labels[16] = {};
    std::vector<Equeue*> flip_eqs, vblank_eqs;
    std::atomic<uint64_t> vblank_count{0};
    int prev_index = -1;
} g_vo;
static constexpr int32_t kVoHandle = 1;

static int32_t sceVideoOutOpen(int32_t, int32_t, int32_t, const void*) { return kVoHandle; }
HLE("sceVideoOutOpen", sceVideoOutOpen)
static int32_t sceVideoOutClose(int32_t) { return SCE_OK; }
HLE("sceVideoOutClose", sceVideoOutClose)
static void sceVideoOutSetBufferAttribute(BufferAttribute* a, uint32_t fmt, uint32_t tiling, uint32_t aspect,
                                          uint32_t w, uint32_t h, uint32_t pitch) {
    std::memset(a, 0, sizeof *a);
    *a = {fmt, tiling, aspect, w, h, pitch, 0, 0, 0};
}
HLE("sceVideoOutSetBufferAttribute", sceVideoOutSetBufferAttribute)
static int32_t sceVideoOutRegisterBuffers(int32_t, int32_t start, void* const* addrs, int32_t num,
                                          const BufferAttribute* attr) {
    std::lock_guard lk(g_vo.m);
    for (int i = 0; i < num && start + i < 16; ++i) g_vo.buffers[start + i] = addrs[i];
    if (attr) g_vo.attr = *attr;
    g_vo.registered = std::max(g_vo.registered, start + num);
    log("video out: %d buffers registered, %ux%u pitch %u format %#x tiling %u", num, g_vo.attr.width,
        g_vo.attr.height, g_vo.attr.pitch_in_pixel, g_vo.attr.pixel_format, g_vo.attr.tiling_mode);
    return 0;  // buffer set index
}
HLE("sceVideoOutRegisterBuffers", sceVideoOutRegisterBuffers)
static int32_t sceVideoOutSetFlipRate(int32_t, int32_t) { return SCE_OK; }
HLE("sceVideoOutSetFlipRate", sceVideoOutSetFlipRate)
static int32_t sceVideoOutGetFlipStatus(int32_t, FlipStatus* s) {
    std::lock_guard lk(g_vo.m);
    *s = g_vo.status;
    return SCE_OK;
}
HLE("sceVideoOutGetFlipStatus", sceVideoOutGetFlipStatus)
static int32_t sceVideoOutIsFlipPending(int32_t) { return 0; }
HLE("sceVideoOutIsFlipPending", sceVideoOutIsFlipPending)
static int32_t sceVideoOutGetBufferLabelAddress(int32_t, uintptr_t* out) {
    *out = reinterpret_cast<uintptr_t>(g_vo.labels);
    return 16;
}
HLE("sceVideoOutGetBufferLabelAddress", sceVideoOutGetBufferLabelAddress)
static int32_t sceVideoOutAddFlipEvent(Equeue* q, int32_t, void* udata) {
    q->add({6, kFilterVideoOut, 1, 0, 0, udata});
    std::lock_guard lk(g_vo.m);
    g_vo.flip_eqs.push_back(q);
    return SCE_OK;
}
HLE("sceVideoOutAddFlipEvent", sceVideoOutAddFlipEvent)

static void vblank_thread() {
    using namespace std::chrono;
    auto next = steady_clock::now();
    while (true) {
        next += microseconds(16667);
        std::this_thread::sleep_until(next);
        uint64_t c = ++g_vo.vblank_count;
        std::vector<Equeue*> qs;
        { std::lock_guard lk(g_vo.m); qs = g_vo.vblank_eqs; }
        for (auto* q : qs) q->trigger(7, kFilterVideoOut, 7 | (c << 16), true);
    }
}
static int32_t sceVideoOutAddVblankEvent(Equeue* q, int32_t, void* udata) {
    q->add({7, kFilterVideoOut, 1, 0, 0, udata});
    static std::once_flag once;
    std::call_once(once, [] { std::thread(vblank_thread).detach(); });
    std::lock_guard lk(g_vo.m);
    g_vo.vblank_eqs.push_back(q);
    return SCE_OK;
}
HLE("sceVideoOutAddVblankEvent", sceVideoOutAddVblankEvent)

struct ResolutionStatus { int32_t full_w, full_h, pane_w, pane_h; uint64_t refresh; float screen_size; uint16_t flags; uint16_t reserved0; uint32_t reserved1[3]; };
static int32_t sceVideoOutGetResolutionStatus(int32_t, ResolutionStatus* r) {
    std::memset(r, 0, sizeof *r);
    r->full_w = r->pane_w = 1920;
    r->full_h = r->pane_h = 1080;
    r->refresh = 3;  // 59.94 Hz
    r->screen_size = 50.0f;
    return SCE_OK;
}
HLE("sceVideoOutGetResolutionStatus", sceVideoOutGetResolutionStatus)
static int32_t vo_noop() { return SCE_OK; }
HLE("sceVideoOutColorSettingsSetGamma_", vo_noop)
HLE("sceVideoOutAdjustColor_", vo_noop)

static std::atomic<uint64_t> g_frames{0};
static void do_flip(int32_t index, int64_t arg) {
    std::vector<Equeue*> qs;
    {
        std::lock_guard lk(g_vo.m);
        auto& s = g_vo.status;
        ++s.count;
        timespec t;
        clock_gettime(CLOCK_MONOTONIC, &t);
        s.process_time = uint64_t(t.tv_sec) * 1000000 + t.tv_nsec / 1000;
        s.tsc = __rdtsc();
        s.flip_arg = arg;
        s.current_buffer = index;
        if (g_vo.prev_index >= 0) g_vo.labels[g_vo.prev_index] = 0;
        g_vo.prev_index = index;
        qs = g_vo.flip_eqs;
    }
    for (auto* q : qs) q->trigger(6, kFilterVideoOut, 6 | (uint64_t(arg) << 16), true);
    uint64_t n = ++g_frames;
    if (n == 1 || n == 10 || n == 100 || n % 1000 == 0) log("flip #%lu (buffer %d, arg %ld)", n, index, arg);
}
static int32_t sceVideoOutSubmitFlip(int32_t, int32_t index, int32_t mode, int64_t arg) {
    do_flip(index, arg);
    return SCE_OK;
}
HLE("sceVideoOutSubmitFlip", sceVideoOutSubmitFlip)

// ------------------------------------------------------------------ null GPU command processor
static std::mutex g_gnm_mutex;
static std::vector<Equeue*> g_eop_eqs;
static std::atomic<uint64_t> g_packets{0};
static uint64_t g_op_counts[256];

static void signal_eop() {
    std::vector<Equeue*> qs;
    { std::lock_guard lk(g_gnm_mutex); qs = g_eop_eqs; }
    for (auto* q : qs) q->trigger(0x40, kFilterGraphics, 0x40);
}

static uint64_t gpu_clock() {
    timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return uint64_t(t.tv_sec) * 100000000ull + uint64_t(t.tv_nsec) / 10;  // 100 MHz
}

static void run_dcb(const uint32_t* p, uint64_t dwords, int depth) {
    uint64_t i = 0;
    bool eop = false;
    while (i < dwords) {
        uint32_t h = p[i];
        uint32_t type = h >> 30;
        if (type == 2) { ++i; continue; }
        uint32_t count = ((h >> 16) & 0x3FFF) + 1;  // body dwords
        if (type == 0) { i += 1 + count; continue; }
        if (type != 3) { log("null GPU: bad PM4 header %#x at dword %lu", h, i); return; }
        uint32_t op = (h >> 8) & 0xFF;
        const uint32_t* b = p + i + 1;
        ++g_op_counts[op];
        ++g_packets;
        switch (op) {
        case 0x47: {  // EVENT_WRITE_EOP
            uint64_t addr = b[1] | (uint64_t(b[2] & 0xFFFF) << 32);
            uint32_t data_sel = b[2] >> 29, int_sel = (b[2] >> 24) & 3;
            if (data_sel == 1) *reinterpret_cast<volatile uint32_t*>(addr) = b[3];
            else if (data_sel == 2) *reinterpret_cast<volatile uint64_t*>(addr) = b[3] | (uint64_t(b[4]) << 32);
            else if (data_sel == 3 || data_sel == 4) *reinterpret_cast<volatile uint64_t*>(addr) = gpu_clock();
            if (int_sel) eop = true;
            break;
        }
        case 0x48: {  // EVENT_WRITE_EOS
            uint64_t addr = b[1] | (uint64_t(b[2] & 0xFFFF) << 32);
            if ((b[2] >> 29) == 2) *reinterpret_cast<volatile uint32_t*>(addr) = b[3];
            break;
        }
        case 0x49: {  // RELEASE_MEM (compute)
            uint64_t addr = b[2] | (uint64_t(b[3] & 0xFFFF) << 32);
            uint32_t data_sel = b[1] >> 29;
            if (data_sel == 1) *reinterpret_cast<volatile uint32_t*>(addr) = b[4];
            else if (data_sel == 2) *reinterpret_cast<volatile uint64_t*>(addr) = b[4] | (uint64_t(b[5]) << 32);
            else if (data_sel == 3) *reinterpret_cast<volatile uint64_t*>(addr) = gpu_clock();
            break;
        }
        case 0x37: {  // WRITE_DATA
            uint64_t addr = b[1] | (uint64_t(b[2]) << 32);
            uint32_t n = count - 3;
            uint32_t dst_sel = (b[0] >> 8) & 0xF;
            if (dst_sel == 2 || dst_sel == 5) std::memcpy(reinterpret_cast<void*>(addr), b + 3, n * 4);
            break;
        }
        case 0x50: {  // DMA_DATA
            uint32_t src_sel = (b[0] >> 29) & 3, dst_sel = (b[0] >> 20) & 3;
            uint64_t src = b[1] | (uint64_t(b[2]) << 32), dst = b[3] | (uint64_t(b[4]) << 32);
            uint32_t bytes = b[5] & 0x1FFFFF;
            if (dst_sel == 0 || dst_sel == 3) {
                if (src_sel == 2) {
                    auto* d = reinterpret_cast<uint32_t*>(dst);
                    for (uint32_t k = 0; k < bytes / 4; ++k) d[k] = b[1];
                } else if (src_sel == 0 || src_sel == 3) {
                    std::memmove(reinterpret_cast<void*>(dst), reinterpret_cast<void*>(src), bytes);
                }
            }
            break;
        }
        case 0x3F:  // INDIRECT_BUFFER
            if (depth < 4) run_dcb(reinterpret_cast<const uint32_t*>(b[0] | (uint64_t(b[1] & 0xFFFF) << 32)),
                                   b[2] & 0xFFFFF, depth + 1);
            break;
        default:
            break;
        }
        i += 1 + count;
    }
    if (eop) signal_eop();
}

static int32_t submit(uint32_t count, uint32_t* const* dcbs, const uint32_t* dcb_sizes) {
    for (uint32_t k = 0; k < count; ++k)
        if (dcbs[k] && dcb_sizes[k]) run_dcb(dcbs[k], dcb_sizes[k] / 4, 0);
    return SCE_OK;
}

static int32_t sceGnmSubmitCommandBuffers(uint32_t count, uint32_t* const* dcbs, const uint32_t* dcb_sizes,
                                          uint32_t* const*, const uint32_t*) {
    return submit(count, dcbs, dcb_sizes);
}
HLE("sceGnmSubmitCommandBuffers", sceGnmSubmitCommandBuffers)
static int32_t sceGnmSubmitAndFlipCommandBuffers(uint32_t count, uint32_t* const* dcbs, const uint32_t* dcb_sizes,
                                                 uint32_t* const*, const uint32_t*, uint32_t, uint32_t buf,
                                                 uint32_t mode, int64_t arg) {
    submit(count, dcbs, dcb_sizes);
    do_flip(int32_t(buf), arg);
    return SCE_OK;
}
HLE("sceGnmSubmitAndFlipCommandBuffers", sceGnmSubmitAndFlipCommandBuffers)
static int32_t sceGnmSubmitDone() { return SCE_OK; }
HLE("sceGnmSubmitDone", sceGnmSubmitDone)
static int32_t sceGnmAddEqEvent(Equeue* q, uint64_t id, void* udata) {
    q->add({id, kFilterGraphics, 1, 0, 0, udata});
    if (id == 0x40) { std::lock_guard lk(g_gnm_mutex); g_eop_eqs.push_back(q); }
    return SCE_OK;
}
HLE("sceGnmAddEqEvent", sceGnmAddEqEvent)
static int32_t sceGnmIsUserPaEnabled() { return 0; }
HLE("sceGnmIsUserPaEnabled", sceGnmIsUserPaEnabled)

// Command-writing helpers: emit one NOP covering the space the game reserved.
static void write_nop(uint32_t* p, uint32_t n) {
    if (!n) return;
    if (n == 1) { p[0] = 0x80000000u; return; }  // type-2 filler
    p[0] = 0xC0001000u | ((n - 2) << 16);
    std::memset(p + 1, 0, (n - 1) * 4);
}
static uint32_t sceGnmDrawInitDefaultHardwareState(uint32_t* cmd, uint32_t size) {
    if (size < 0x100) return 0;
    write_nop(cmd, 0x100);
    return 0x100;
}
HLE("sceGnmDrawInitDefaultHardwareState", sceGnmDrawInitDefaultHardwareState)
HLE("sceGnmDispatchInitDefaultHardwareState", sceGnmDrawInitDefaultHardwareState)
static int32_t gnm_set_shader(uint32_t* cmd, uint32_t size, const uint32_t*, uint32_t) {
    if (!cmd) return -1;
    write_nop(cmd, size);
    return SCE_OK;
}
HLE("sceGnmSetPsShader", gnm_set_shader)
HLE("sceGnmSetVsShader", gnm_set_shader)
HLE("sceGnmSetCsShader", gnm_set_shader)
HLE("sceGnmSetEsShader", gnm_set_shader)
HLE("sceGnmSetGsShader", gnm_set_shader)
HLE("sceGnmSetHsShader", gnm_set_shader)
HLE("sceGnmSetLsShader", gnm_set_shader)
static int32_t sceGnmInsertWaitFlipDone(uint32_t* cmd, uint32_t size, int32_t, uint32_t) {
    write_nop(cmd, size);
    return SCE_OK;
}
HLE("sceGnmInsertWaitFlipDone", sceGnmInsertWaitFlipDone)

void print_gpu_summary() {
    log("null GPU: %lu packets, %lu flips", g_packets.load(), g_frames.load());
    for (int op = 0; op < 256; ++op)
        if (g_op_counts[op]) log("  PM4 op %#04x x%lu", op, g_op_counts[op]);
}

}  // namespace d1
