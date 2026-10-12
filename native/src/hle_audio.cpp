// libSceAudioOut (paced silent sink) and libSceAjm (codec jobs that "decode" to silence).
#include <time.h>

#include <chrono>
#include <cstring>
#include <map>
#include <mutex>
#include <thread>
#include <vector>

#include "hle.h"

namespace d1 {

// ------------------------------------------------------------------ audio out
struct AudioPort { uint32_t samples = 256, freq = 48000; std::chrono::steady_clock::time_point next{}; };
static std::mutex g_ao_mutex;
static std::map<int32_t, AudioPort> g_ports;
static int32_t g_next_port = 1;

static int32_t sceAudioOutInit() { return SCE_OK; }
HLE("sceAudioOutInit", sceAudioOutInit)
static int32_t sceAudioOutOpen(int32_t user, int32_t type, int32_t index, uint32_t len, uint32_t freq, uint32_t param) {
    std::lock_guard lk(g_ao_mutex);
    int32_t h = g_next_port++;
    g_ports[h] = {len ? len : 256, freq ? freq : 48000, std::chrono::steady_clock::now()};
    log("audio out: port %d type %d, %u samples @ %u Hz, param %#x", h, type, len, freq, param);
    return h;
}
HLE("sceAudioOutOpen", sceAudioOutOpen)
static int32_t sceAudioOutClose(int32_t h) { std::lock_guard lk(g_ao_mutex); g_ports.erase(h); return SCE_OK; }
HLE("sceAudioOutClose", sceAudioOutClose)
static int32_t sceAudioOutOutput(int32_t h, const void*) {
    std::chrono::steady_clock::time_point wake;
    {
        std::lock_guard lk(g_ao_mutex);
        auto it = g_ports.find(h);
        if (it == g_ports.end()) return SCE_OK;
        auto& p = it->second;
        auto now = std::chrono::steady_clock::now();
        if (p.next < now) p.next = now;
        p.next += std::chrono::microseconds(uint64_t(p.samples) * 1000000 / p.freq);
        wake = p.next;
    }
    std::this_thread::sleep_until(wake);  // the console blocks until the previous buffer is consumed
    return SCE_OK;
}
HLE("sceAudioOutOutput", sceAudioOutOutput)
struct AudioOutParam { int32_t handle; const void* ptr; };
static int32_t sceAudioOutOutputs(const AudioOutParam* p, uint32_t num) {
    if (num) sceAudioOutOutput(p[0].handle, p[0].ptr);
    return SCE_OK;
}
HLE("sceAudioOutOutputs", sceAudioOutOutputs)
static int32_t sceAudioOutSetVolume(int32_t, int32_t, const int32_t*) { return SCE_OK; }
HLE("sceAudioOutSetVolume", sceAudioOutSetVolume)

// ------------------------------------------------------------------ AJM
// Jobs are recorded host-side; the batch buffer only needs distinct addresses per job.
struct AjmBuffer { uint8_t* p; uint64_t size; };
struct AjmJob {
    bool run;
    uint64_t flags;
    std::vector<AjmBuffer> in, out;
    uint8_t* sideband_out;
    uint64_t sideband_out_size;
};
static std::mutex g_ajm_mutex;
static std::map<uintptr_t, AjmJob> g_jobs;
static uint32_t g_next_batch = 1, g_next_instance = 1;
static constexpr uint64_t kJobSize = 64;

static int32_t sceAjmInitialize(int64_t, uint32_t* ctx) { *ctx = 1; return SCE_OK; }
HLE("sceAjmInitialize", sceAjmInitialize)
static int32_t sceAjmFinalize(uint32_t) { return SCE_OK; }
HLE("sceAjmFinalize", sceAjmFinalize)
static int32_t sceAjmModuleRegister(uint32_t, uint32_t, int64_t) { return SCE_OK; }
HLE("sceAjmModuleRegister", sceAjmModuleRegister)
static int32_t sceAjmModuleUnregister(uint32_t, uint32_t) { return SCE_OK; }
HLE("sceAjmModuleUnregister", sceAjmModuleUnregister)
static int32_t sceAjmInstanceCreate(uint32_t, uint32_t codec, uint64_t flags, uint32_t* inst) {
    std::lock_guard lk(g_ajm_mutex);
    *inst = (codec << 14) | g_next_instance++;
    return SCE_OK;
}
HLE("sceAjmInstanceCreate", sceAjmInstanceCreate)
static int32_t sceAjmInstanceDestroy(uint32_t, uint32_t) { return SCE_OK; }
HLE("sceAjmInstanceDestroy", sceAjmInstanceDestroy)

static void* sceAjmBatchJobControlBufferRa(void* buf, uint32_t, uint64_t flags, void*, uint64_t, void* sb_out,
                                           uint64_t sb_out_size, void*) {
    std::lock_guard lk(g_ajm_mutex);
    g_jobs[reinterpret_cast<uintptr_t>(buf)] = {false, flags, {}, {}, static_cast<uint8_t*>(sb_out), sb_out_size};
    std::memset(buf, 0, kJobSize);
    return static_cast<uint8_t*>(buf) + kJobSize;
}
HLE("sceAjmBatchJobControlBufferRa", sceAjmBatchJobControlBufferRa)
static void* sceAjmBatchJobRunSplitBufferRa(void* buf, uint32_t, uint64_t flags, const AjmBuffer* in, uint64_t nin,
                                            const AjmBuffer* out, uint64_t nout, void* sb_out, uint64_t sb_out_size,
                                            void*) {
    std::lock_guard lk(g_ajm_mutex);
    AjmJob j{true, flags, {in, in + nin}, {out, out + nout}, static_cast<uint8_t*>(sb_out), sb_out_size};
    g_jobs[reinterpret_cast<uintptr_t>(buf)] = std::move(j);
    std::memset(buf, 0, kJobSize);
    return static_cast<uint8_t*>(buf) + kJobSize;
}
HLE("sceAjmBatchJobRunSplitBufferRa", sceAjmBatchJobRunSplitBufferRa)

static int32_t sceAjmBatchStartBuffer(uint32_t, uint8_t* batch, uint32_t size, int, void* err, uint32_t* id) {
    std::lock_guard lk(g_ajm_mutex);
    auto lo = g_jobs.lower_bound(reinterpret_cast<uintptr_t>(batch));
    auto hi = g_jobs.lower_bound(reinterpret_cast<uintptr_t>(batch) + size);
    for (auto it = lo; it != hi; ++it) {
        AjmJob& j = it->second;
        if (j.sideband_out && j.sideband_out_size) std::memset(j.sideband_out, 0, j.sideband_out_size);  // result = OK
        if (j.run) {
            int64_t consumed = 0, written = 0;
            for (auto& b : j.in) consumed += b.size;
            for (auto& b : j.out) { std::memset(b.p, 0, b.size); written += b.size; }
            if (j.sideband_out_size >= 24) {  // AjmSidebandResult + AjmSidebandStream
                int32_t c = int32_t(consumed), w = int32_t(written);
                std::memcpy(j.sideband_out + 8, &c, 4);
                std::memcpy(j.sideband_out + 12, &w, 4);
                uint64_t samples = uint64_t(written) / 4;
                std::memcpy(j.sideband_out + 16, &samples, 8);
            }
        }
    }
    g_jobs.erase(lo, hi);
    *id = g_next_batch++;
    return SCE_OK;
}
HLE("sceAjmBatchStartBuffer", sceAjmBatchStartBuffer)
static int32_t sceAjmBatchWait(uint32_t, uint32_t, uint32_t, void*) { return SCE_OK; }
HLE("sceAjmBatchWait", sceAjmBatchWait)
static int32_t sceAjmBatchErrorDump(const void*, int32_t) { return SCE_OK; }
HLE("sceAjmBatchErrorDump", sceAjmBatchErrorDump)

}  // namespace d1
