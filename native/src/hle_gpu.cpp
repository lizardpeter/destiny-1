// Event queues, video out and a "null GPU" for libSceGnmDriver.
//
// The null GPU walks submitted PM4 command buffers and performs only their memory side
// effects — end-of-pipe/end-of-shader fence writes, WRITE_DATA, DMA_DATA fills/copies —
// and raises the end-of-pipe interrupt. Nothing is drawn. This lets the game's frame
// pacing (which waits on GPU fences and flip events) run headless until a real renderer
// replaces it.
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
#include "render_bridge.h"
#include "runtime.h"
#include "settings.h"

#ifdef D1_RENDERER_SHADPS4
static constexpr bool kHaveRenderer = true;
#else
static constexpr bool kHaveRenderer = false;
#endif

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

namespace render {
Perf& perf() {
    static Perf p;
    return p;
}
}  // namespace render
static thread_local bool t_flip_thread = false;  // the game's thread that submits frames
static uint64_t now_ns() {
    return uint64_t(std::chrono::duration_cast<std::chrono::nanoseconds>(
                        std::chrono::steady_clock::now().time_since_epoch()).count());
}
// Interval between the game's frame submissions (its whole CPU frame, waits included).
static void note_guest_frame() {
    static std::atomic<uint64_t> last{0};
    t_flip_thread = true;
    const uint64_t t = now_ns(), prev = last.exchange(t);
    if (prev && t - prev < 2'000'000'000ull) {
        auto& p = render::perf();
        p.guest_ns += t - prev;
        ++p.guest_frames;
    }
}

static int32_t sceKernelWaitEqueue(Equeue* q, KEvent* ev, int num, int* out, uint32_t* timeout_us) {
    struct WaitTimer {
        uint64_t t0 = t_flip_thread ? now_ns() : 0;
        ~WaitTimer() { if (t0) render::perf().guest_wait_ns += now_ns() - t0; }
    } wait_timer;
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

// True once the real renderer (native/renderer/) is running; otherwise the null GPU below
// handles command buffers.
static bool g_gpu_real = false;
static bool gpu_real() { return kHaveRenderer && g_gpu_real; }
// D1_RENDERER_LATE=<s> (test aid): run on the null GPU until the game has been in
// activity:in_world for <s> seconds, then start the renderer. Lets a slow software Vulkan
// device look at the world without its frame times changing how the game gets there.
// Command buffers use the real packet builders from the start.
static bool g_late = false;
static double g_late_secs = 0;
static render::Callbacks g_late_cb{};
static bool builders_real() { return kHaveRenderer && (g_gpu_real || g_late); }
static void maybe_attach_renderer();

// D1_RENDER_EVERY=N: with the renderer on, draw only every Nth frame; the frames in between go
// through the null GPU (labels, EOP and flips without drawing). For slow GPUs and software
// rendering, so the game keeps its real speed (and its network timeouts) while frames still
// come out. Before a skipped frame the renderer is drained, so the order of GPU work holds;
// D1_RENDER_ASYNC=1 skips without waiting whenever the renderer is still busy instead.
static int g_render_every = 0;
static bool g_render_async = false;
static int g_frame_mode = -1;  // current frame: -1 undecided, 0 null, 1 renderer
static uint64_t g_frame_no = 0;
static bool frame_rendered() {
    if (!gpu_real() || (g_render_every <= 1 && !g_render_async)) return true;
    if (g_frame_mode < 0) {
        bool draw;
        if (g_render_async) draw = render::idle();
        else if (!(draw = g_frame_no % uint64_t(g_render_every) == 0)) render::wait_idle();
        g_frame_mode = draw ? 1 : 0;
    }
    return g_frame_mode == 1;
}
static void frame_end() {
    g_frame_mode = -1;
    ++g_frame_no;
}

bool native_gfx_active();                    // native_gfx.cpp: the native renderer runs
bool native_gfx_on_fault(void* addr);        // a write to a page it watches
void native_gfx_on_unmap(uint64_t addr, uint64_t size);
bool gpu_active() { return gpu_real() || native_gfx_active(); }

void native_gfx_submit(uint32_t count, uint32_t* const* dcbs, const uint32_t* sizes);  // native_gfx.cpp
void native_gfx_flip(void* addr, uint32_t width, uint32_t height);
void native_gfx_check_waits(uint32_t count, uint32_t* const* dcbs, const uint32_t* sizes);

// ------------------------------------------------------------------ video out
struct FlipStatus {
    uint64_t count, process_time, tsc;
    int64_t flip_arg;
    uint64_t submit_tsc, reserved0;
    int32_t gc_queue_num, flip_pending_num, current_buffer;
    uint32_t reserved1;
};
using BufferAttribute = render::VoAttr;  // SceVideoOutBufferAttribute, 40 bytes
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
    *a = {fmt, tiling, int32_t(aspect), w, h, pitch, 0, 0, 0};
}
HLE("sceVideoOutSetBufferAttribute", sceVideoOutSetBufferAttribute)
static int32_t sceVideoOutRegisterBuffers(int32_t, int32_t start, void* const* addrs, int32_t num,
                                          const BufferAttribute* attr) {
    std::lock_guard lk(g_vo.m);
    for (int i = 0; i < num && start + i < 16; ++i) g_vo.buffers[start + i] = addrs[i];
    if (attr) g_vo.attr = *attr;
    g_vo.registered = std::max(g_vo.registered, start + num);
    if (gpu_real() && attr) render::register_buffers(start, addrs, num, *attr);
    log("video out: %d buffers registered, %ux%u pitch %u format %#x tiling %u", num, g_vo.attr.width,
        g_vo.attr.height, g_vo.attr.pitch_in_pixel, g_vo.attr.pixel_format, g_vo.attr.tiling_mode);
    return 0;  // buffer set index
}
HLE("sceVideoOutRegisterBuffers", sceVideoOutRegisterBuffers)
static int32_t sceVideoOutSetFlipRate(int32_t, int32_t rate) {
    static int last = -1;
    if (rate != last) { log("video out: flip rate %d (%s)", rate, rate == 0 ? "60 Hz" : rate == 1 ? "30 Hz" : "20 Hz"); last = rate; }
    return SCE_OK;
}
HLE("sceVideoOutSetFlipRate", sceVideoOutSetFlipRate)
static int32_t sceVideoOutGetFlipStatus(int32_t, FlipStatus* s) {
    std::lock_guard lk(g_vo.m);
    *s = g_vo.status;
    return SCE_OK;
}
HLE("sceVideoOutGetFlipStatus", sceVideoOutGetFlipStatus)
static int32_t sceVideoOutIsFlipPending(int32_t) {
    std::lock_guard lk(g_vo.m);
    return g_vo.status.flip_pending_num;
}
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
    static const int hz = [] { const char* v = getenv("D1_VBLANK_HZ"); return v ? std::max(1, atoi(v)) : 60; }();
    while (true) {
        next += microseconds(1000000 / hz);
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
    // The game ignores this for its render targets (hardcoded 1920x1080 in the GPU device
    // init, patched by hooks.cpp for render_resolution); report the same size anyway.
    r->full_w = r->pane_w = settings().render_width;
    r->full_h = r->pane_h = settings().render_height;
    r->refresh = 3;  // 59.94 Hz
    r->screen_size = 50.0f;
    return SCE_OK;
}
HLE("sceVideoOutGetResolutionStatus", sceVideoOutGetResolutionStatus)
static int32_t vo_noop() { return SCE_OK; }
HLE("sceVideoOutColorSettingsSetGamma_", vo_noop)
HLE("sceVideoOutAdjustColor_", vo_noop)

static std::atomic<uint64_t> g_frames{0};
uint64_t gpu_flip_count() { return g_frames.load(); }
static void gpu_stats(uint64_t frame);
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
        if (s.flip_pending_num > 0) --s.flip_pending_num;
        if (s.gc_queue_num > 0) --s.gc_queue_num;
        if (g_vo.prev_index >= 0) g_vo.labels[g_vo.prev_index] = 0;
        g_vo.prev_index = index;
        qs = g_vo.flip_eqs;
    }
    for (auto* q : qs) q->trigger(6, kFilterVideoOut, 6 | (uint64_t(arg) << 16), true);
    uint64_t n = ++g_frames;
    if (n == 1 || n == 10 || n == 100 || n % 1000 == 0) log("flip #%llu (buffer %d, arg %lld)", n, index, arg);
    gpu_stats(n);
}
static int32_t sceVideoOutSubmitFlip(int32_t, int32_t index, int32_t mode, int64_t arg) {
    note_guest_frame();
    if (gpu_real() && frame_rendered()) {
        frame_end();
        { std::lock_guard lk(g_vo.m); ++g_vo.status.flip_pending_num; }
        render::cpu_flip(index, arg);
        return SCE_OK;
    }
    if (gpu_real()) frame_end();
    if (index >= 0 && index < 16) native_gfx_flip(g_vo.buffers[index], g_vo.attr.width, g_vo.attr.height);
    do_flip(index, arg);
    return SCE_OK;
}
HLE("sceVideoOutSubmitFlip", sceVideoOutSubmitFlip)

// ------------------------------------------------------------------ null GPU command processor
static std::mutex g_gnm_mutex;
static std::vector<Equeue*> g_eop_eqs;
static std::atomic<uint64_t> g_packets{0};
static uint64_t g_op_counts[256];
static bool g_pred_on = false;            // SET_PREDICATION active (null GPU statistics)
static uint64_t g_pred_draws = 0, g_pred_sets = 0;

// D1_GPU_STATS=1 (null GPU): every 300 flips, the average draws / dispatches / packets per
// frame, which shows whether the game is submitting a scene or only UI / fades.
void print_call_rates(uint64_t frames);  // hooks.cpp
static void gpu_stats(uint64_t frame) {
    static const bool on = getenv("D1_GPU_STATS") != nullptr;
    if (!on || frame % 300) return;
    static uint64_t last_draw = 0, last_disp = 0, last_pk = 0;
    const uint64_t draw = g_op_counts[0x27] + g_op_counts[0x2D] + g_op_counts[0x35] + g_op_counts[0x38] + g_op_counts[0x25];
    const uint64_t disp = g_op_counts[0x15] + g_op_counts[0x16];
    const uint64_t pk = g_packets.load();
    static uint64_t last_pd = 0, last_ps = 0;
    log("gpu stats @%llu: %.1f draws (%.1f predicated, %.1f SET_PREDICATION), %.1f dispatches, %.0f packets per frame",
        (unsigned long long)frame, (draw - last_draw) / 300.0, (g_pred_draws - last_pd) / 300.0,
        (g_pred_sets - last_ps) / 300.0, (disp - last_disp) / 300.0, (pk - last_pk) / 300.0);
    last_draw = draw, last_disp = disp, last_pk = pk, last_pd = g_pred_draws, last_ps = g_pred_sets;
    print_call_rates(300);
}

static void signal_eop() {
    std::vector<Equeue*> qs;
    { std::lock_guard lk(g_gnm_mutex); qs = g_eop_eqs; }
    for (auto* q : qs) q->trigger(0x40, kFilterGraphics, 0x40);
}

// GPU timestamps (EOP / RELEASE_MEM "GPU clock 64"): the same clock the renderer's command
// processor writes (shadPS4: high_resolution_clock in ns), so frames that go through the null GPU
// (D1_RENDER_EVERY, D1_RENDERER_LATE) don't make the game's GPU timings jump backwards.
static uint64_t gpu_clock() {
    return uint64_t(std::chrono::duration_cast<std::chrono::nanoseconds>(
                        std::chrono::high_resolution_clock::now().time_since_epoch()).count());
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
        if (type != 3) { log("null GPU: bad PM4 header %#x at dword %llu", h, i); return; }
        uint32_t op = (h >> 8) & 0xFF;
        const uint32_t* b = p + i + 1;
        ++g_op_counts[op];
        ++g_packets;
        if (g_pred_on && (h & 1) && (op == 0x27 || op == 0x2D || op == 0x35 || op == 0x38 || op == 0x25)) ++g_pred_draws;
        switch (op) {
        case 0x20:  // SET_PREDICATION: operation in bits 18:16 of the second dword (0 = off)
            g_pred_on = ((b[1] >> 16) & 7) != 0;
            ++g_pred_sets;
            break;
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
    native_gfx_submit(count, dcbs, dcb_sizes);
    for (uint32_t k = 0; k < count; ++k)
        if (dcbs[k] && dcb_sizes[k]) run_dcb(dcbs[k], dcb_sizes[k] / 4, 0);
    native_gfx_check_waits(count, dcbs, dcb_sizes);
    return SCE_OK;
}

static int32_t sceGnmSubmitCommandBuffers(uint32_t count, uint32_t* const* dcbs, const uint32_t* dcb_sizes,
                                          uint32_t* const* ccbs, const uint32_t* ccb_sizes) {
    if (gpu_real() && frame_rendered()) {
        render::submit(count, dcbs, dcb_sizes, ccbs, ccb_sizes);
        return SCE_OK;
    }
    return submit(count, dcbs, dcb_sizes);
}
HLE("sceGnmSubmitCommandBuffers", sceGnmSubmitCommandBuffers)
static int32_t sceGnmSubmitAndFlipCommandBuffers(uint32_t count, uint32_t* const* dcbs, const uint32_t* dcb_sizes,
                                                 uint32_t* const* ccbs, const uint32_t* ccb_sizes, uint32_t,
                                                 uint32_t buf, uint32_t mode, int64_t arg) {
    note_guest_frame();
    maybe_attach_renderer();
    if (gpu_real() && frame_rendered()) {
        frame_end();
        {
            std::lock_guard lk(g_vo.m);
            ++g_vo.status.flip_pending_num;
            ++g_vo.status.gc_queue_num;
        }
        return render::submit_and_flip(count, dcbs, dcb_sizes, ccbs, ccb_sizes, buf, arg);
    }
    submit(count, dcbs, dcb_sizes);
    if (buf < 16) native_gfx_flip(g_vo.buffers[buf], g_vo.attr.width, g_vo.attr.height);
    if (gpu_real()) {  // a skipped frame: what the patched prepareFlip would have written
        frame_end();
        if (buf < 16) g_vo.labels[buf] = 1;
    }
    do_flip(int32_t(buf), arg);
    return SCE_OK;
}
HLE("sceGnmSubmitAndFlipCommandBuffers", sceGnmSubmitAndFlipCommandBuffers)
static int32_t sceGnmSubmitDone() {
    if (gpu_real()) render::submit_done();
    return SCE_OK;
}
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
    if (builders_real()) return render::draw_init_default_hw_state(cmd, size);
    if (size < 0x100) return 0;
    write_nop(cmd, 0x100);
    return 0x100;
}
HLE("sceGnmDrawInitDefaultHardwareState", sceGnmDrawInitDefaultHardwareState)
static uint32_t sceGnmDispatchInitDefaultHardwareState(uint32_t* cmd, uint32_t size) {
    if (builders_real()) return render::dispatch_init_default_hw_state(cmd, size);
    if (size < 0x100) return 0;
    write_nop(cmd, 0x100);
    return 0x100;
}
HLE("sceGnmDispatchInitDefaultHardwareState", sceGnmDispatchInitDefaultHardwareState)

// Shader-state builders: real register writes with the renderer, a NOP of the reserved size
// for the null GPU.
#define D1_SHADER_SETTER(NAME, CALL, ...)                                   \
    static int32_t NAME(uint32_t* cmd, uint32_t size, const uint32_t* regs __VA_OPT__(, ) __VA_ARGS__) { \
        if (builders_real()) return CALL;                                   \
        if (!cmd) return -1;                                                \
        write_nop(cmd, size);                                               \
        return SCE_OK;                                                      \
    }
D1_SHADER_SETTER(sceGnmSetPsShader, render::set_ps_shader(cmd, size, regs))
D1_SHADER_SETTER(sceGnmSetCsShader, render::set_cs_shader(cmd, size, regs))
D1_SHADER_SETTER(sceGnmSetGsShader, render::set_gs_shader(cmd, size, regs))
D1_SHADER_SETTER(sceGnmSetVsShader, render::set_vs_shader(cmd, size, regs, mod), uint32_t mod)
D1_SHADER_SETTER(sceGnmSetEsShader, render::set_es_shader(cmd, size, regs, mod), uint32_t mod)
D1_SHADER_SETTER(sceGnmSetLsShader, render::set_ls_shader(cmd, size, regs, mod), uint32_t mod)
D1_SHADER_SETTER(sceGnmSetHsShader, render::set_hs_shader(cmd, size, regs, param), uint32_t param)
#undef D1_SHADER_SETTER
HLE("sceGnmSetPsShader", sceGnmSetPsShader)
HLE("sceGnmSetVsShader", sceGnmSetVsShader)
HLE("sceGnmSetCsShader", sceGnmSetCsShader)
HLE("sceGnmSetEsShader", sceGnmSetEsShader)
HLE("sceGnmSetGsShader", sceGnmSetGsShader)
HLE("sceGnmSetHsShader", sceGnmSetHsShader)
HLE("sceGnmSetLsShader", sceGnmSetLsShader)
static int32_t sceGnmInsertWaitFlipDone(uint32_t* cmd, uint32_t size, int32_t, uint32_t buf) {
    if (gpu_real()) return render::insert_wait_flip_done(cmd, size, buf);
    if (builders_real() && size == 7 && buf < 16) {
        // WAIT_REG_MEM (memory, equal) on the video out label: label == 0
        const uint64_t a = reinterpret_cast<uint64_t>(&g_vo.labels[buf]) & ~3ull;
        const uint32_t pkt[7] = {0xC0053C00u, 0x13u, uint32_t(a), uint32_t(a >> 32), 0u, 0xFFFFFFFFu, 10u};
        std::memcpy(cmd, pkt, sizeof pkt);
        return SCE_OK;
    }
    write_nop(cmd, size);
    return SCE_OK;
}
HLE("sceGnmInsertWaitFlipDone", sceGnmInsertWaitFlipDone)

void gpu_init() {
    if (!kHaveRenderer) return;
    render::Callbacks cb{};
    cb.eop = signal_eop;
    cb.flip = do_flip;
    cb.labels = g_vo.labels;
    if (uint64_t pp = rt().modules[0].proc_param) cb.sdk_version = uint32_t(*reinterpret_cast<const uint64_t*>(pp + 0x10));
    const Settings& st = settings();
    cb.window_width = st.window_width;
    cb.window_height = st.window_height;
    cb.fullscreen = st.fullscreen;
    cb.overlay = st.overlay;
    static const std::string cache_dir = rt().data_root + "/shader_cache";
    cb.cache_dir = cache_dir.c_str();
    cb.present_mode = st.vsync == "on" ? "Fifo" : st.vsync == "off-tearing" ? "Immediate" : "Mailbox";
    if (const char* v = getenv("D1_RENDER_EVERY")) g_render_every = std::max(0, std::atoi(v));
    if (const char* v = getenv("D1_RENDER_ASYNC")) g_render_async = v[0] == '1';
    if (g_render_every > 1 || g_render_async)
        log("GPU: drawing %s (the other frames go through the null GPU)",
            g_render_async ? "whenever the renderer is idle" : ("every " + std::to_string(g_render_every) + "th frame").c_str());
    if (const char* v = getenv("D1_RENDERER_LATE")) {
        g_late = true;
        g_late_secs = std::atof(v);
        g_late_cb = cb;
        log("GPU: null GPU until %.0f s into activity:in_world, then the renderer (D1_RENDERER_LATE)", g_late_secs);
        return;
    }
    g_gpu_real = render::init(cb);
    if (!g_gpu_real) log("GPU: null GPU (nothing is drawn)");
}

void for_each_guest_region(void (*fn)(uint64_t addr, uint64_t size));  // hle_kernel.cpp

// Called at each frame submission: start the renderer once the late-attach point is reached.
static void maybe_attach_renderer() {
    if (!g_late || g_gpu_real) return;
    static std::chrono::steady_clock::time_point t_world{};
    const char* st = game_state();
    if (!st || std::strcmp(st, "activity:in_world") != 0) {
        t_world = {};
        return;
    }
    const auto now = std::chrono::steady_clock::now();
    if (t_world == std::chrono::steady_clock::time_point{}) t_world = now;
    if (std::chrono::duration<double>(now - t_world).count() < g_late_secs) return;
    g_late = false;
    if (!render::init(g_late_cb)) {
        log("GPU: late renderer start failed; staying on the null GPU");
        return;
    }
    for_each_guest_region([](uint64_t a, uint64_t n) { render::on_map(a, n); });
    {
        std::lock_guard lk(g_vo.m);
        if (g_vo.registered > 0) {
            void* addrs[16];
            for (int i = 0; i < g_vo.registered && i < 16; ++i) addrs[i] = g_vo.buffers[i];
            render::register_buffers(0, addrs, g_vo.registered, g_vo.attr);
        }
    }
    g_gpu_real = true;
    log("GPU: renderer started (late attach)");
}

void gpu_on_map(uint64_t addr, uint64_t size) {
    native_gfx_on_unmap(addr, size);  // new contents
    if (gpu_real()) render::on_map(addr, size);
}
void gpu_on_unmap(uint64_t addr, uint64_t size) {
    native_gfx_on_unmap(addr, size);
    if (gpu_real()) render::on_unmap(addr, size);
}
bool gpu_on_fault(void* uc, void* addr) {
    if (native_gfx_on_fault(addr)) return true;
    if (!gpu_real()) return false;
    const uint64_t t0 = now_ns();
    if (!render::on_fault(uc, addr)) return false;
    auto& p = render::perf();
    ++p.faults;
    p.fault_ns += now_ns() - t0;
    return true;
}

void print_gpu_summary() {
    if (gpu_real()) {
        render::print_summary();
        return;
    }
    log("null GPU: %llu packets, %llu flips", g_packets.load(), g_frames.load());
    for (int op = 0; op < 256; ++op)
        if (g_op_counts[op]) log("  PM4 op %#04x x%llu", op, g_op_counts[op]);
}

}  // namespace d1
