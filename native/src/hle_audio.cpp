// libSceAudioOut (played through the window's audio device when there is one, else a
// paced silent sink), libSceAjm (codec jobs that "decode" to silence) and
// libSceVoice (ports that exist but carry no audio).
#include <time.h>

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstring>
#include <map>
#include <mutex>
#include <thread>
#include <vector>

#include "hle.h"
#include "render_bridge.h"

namespace d1 {

// ------------------------------------------------------------------ audio out
struct AudioPort {
    uint32_t samples = 256, freq = 48000, format = 1;
    float gain = 1.0f;
    std::chrono::steady_clock::time_point next{};
    std::vector<float> mix;
};
static std::mutex g_ao_mutex;
static std::map<int32_t, AudioPort> g_ports;
static int32_t g_next_port = 1;

static int32_t sceAudioOutInit() { return SCE_OK; }
HLE("sceAudioOutInit", sceAudioOutInit)
static int32_t sceAudioOutOpen(int32_t user, int32_t type, int32_t index, uint32_t len, uint32_t freq, uint32_t param) {
    std::lock_guard lk(g_ao_mutex);
    int32_t h = g_next_port++;
    AudioPort& p = g_ports[h];
    p.samples = len ? len : 256, p.freq = freq ? freq : 48000, p.format = param & 0xFF;
    p.next = std::chrono::steady_clock::now();
    // the main port (type 0) goes to the speakers; others (pad speaker, voice, ...) stay silent
    const bool played = type == 0 && render::audio_open(p.freq, p.samples);
    log("audio out: port %d type %d, %u samples @ %u Hz, format %u%s", h, type, len, freq, p.format,
        played ? " -> audio device" : "");
    if (!played) p.format = ~0u;
    return h;
}
HLE("sceAudioOutOpen", sceAudioOutOpen)
static int32_t sceAudioOutClose(int32_t h) { std::lock_guard lk(g_ao_mutex); g_ports.erase(h); return SCE_OK; }
HLE("sceAudioOutClose", sceAudioOutClose)

// Port formats: 0 s16 mono, 1 s16 stereo, 2 s16 7.1, 3 float mono, 4 float stereo,
// 5 float 7.1, 6 s16 7.1 "std", 7 float 7.1 "std". The 7.1 layouts are L R C LFE then
// back/side (std: side, back); the device side takes SDL's 7.1 order (L R C LFE back side).
static bool to_float8(AudioPort& p, const void* src) {
    static const int kChannels[8] = {1, 2, 8, 1, 2, 8, 8, 8};
    if (p.format > 7) return false;
    const int ch = kChannels[p.format];
    const bool is_float = p.format >= 3 && p.format != 6;
    const bool std_order = p.format >= 6;
    p.mix.assign(size_t(p.samples) * 8, 0.0f);
    for (uint32_t i = 0; i < p.samples; ++i) {
        float in[8] = {};
        for (int c = 0; c < ch; ++c)
            in[c] = is_float ? static_cast<const float*>(src)[i * ch + c]
                             : static_cast<const int16_t*>(src)[i * ch + c] * (1.0f / 32768.0f);
        float* o = &p.mix[size_t(i) * 8];
        if (ch == 1) o[0] = o[1] = in[0];
        else if (ch == 2) o[0] = in[0], o[1] = in[1];
        else if (std_order) o[0] = in[0], o[1] = in[1], o[2] = in[2], o[3] = in[3], o[4] = in[6], o[5] = in[7], o[6] = in[4], o[7] = in[5];
        else for (int c = 0; c < 8; ++c) o[c] = in[c];
        for (int c = 0; c < 8; ++c) o[c] *= p.gain;
    }
    return true;
}

static int32_t sceAudioOutOutput(int32_t h, const void* data) {
    std::chrono::steady_clock::time_point wake;
    {
        std::lock_guard lk(g_ao_mutex);
        auto it = g_ports.find(h);
        if (it == g_ports.end()) return SCE_OK;
        auto& p = it->second;
        if (data && to_float8(p, data)) {
            std::vector<float> buf;
            buf.swap(p.mix);
            const uint32_t frames = p.samples;
            g_ao_mutex.unlock();
            render::audio_output(buf.data(), frames);  // blocks while the device has enough queued
            g_ao_mutex.lock();
            return SCE_OK;
        }
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
// volumes: per channel, 32768 = 0 dB; flag bits select the channels being set
static int32_t sceAudioOutSetVolume(int32_t h, int32_t flag, const int32_t* vol) {
    if (!vol) return SCE_OK;
    std::lock_guard lk(g_ao_mutex);
    auto it = g_ports.find(h);
    if (it == g_ports.end()) return SCE_OK;
    int32_t m = 0;
    for (int c = 0; c < 8; ++c)
        if (flag & (1 << c)) m = std::max(m, vol[c]);
    it->second.gain = std::min(m, 32768) / 32768.0f;
    return SCE_OK;
}
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
    static bool seen[8];
    if (codec < 8 && !seen[codec]) { seen[codec] = true; log("ajm: codec %u instance (0 mp3, 1 atrac9, 2 aac); decoded as silence", codec); }
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

// ------------------------------------------------------------------ voice chat
// Ports must get real ids: the game finds its port records by the id CreatePort returned and
// dereferences the result unchecked (0xB49210). No audio flows through them.
static std::atomic<uint32_t> g_next_voice_port{1};
static int32_t sceVoiceInit(void*, uint32_t) { return SCE_OK; }
HLE("sceVoiceInit", sceVoiceInit)
static int32_t sceVoiceEnd() { return SCE_OK; }
HLE("sceVoiceEnd", sceVoiceEnd)
static int32_t sceVoiceStart(void*) { return SCE_OK; }
HLE("sceVoiceStart", sceVoiceStart)
static int32_t sceVoiceStop() { return SCE_OK; }
HLE("sceVoiceStop", sceVoiceStop)
static int32_t sceVoiceGetResourceInfo(void* info) {
    if (info) std::memset(info, 0, 16);
    return SCE_OK;
}
HLE("sceVoiceGetResourceInfo", sceVoiceGetResourceInfo)
static int32_t sceVoiceCreatePort(uint32_t* port, const void* param) {
    if (!port) return int32_t(0x8023000b);
    *port = g_next_voice_port++;
    log("voice: port %u", *port);
    return SCE_OK;
}
HLE("sceVoiceCreatePort", sceVoiceCreatePort)
static int32_t sceVoiceDeletePort(uint32_t) { return SCE_OK; }
HLE("sceVoiceDeletePort", sceVoiceDeletePort)
static int32_t sceVoiceConnectIPortToOPort(uint32_t, uint32_t) { return SCE_OK; }
HLE("sceVoiceConnectIPortToOPort", sceVoiceConnectIPortToOPort)
static int32_t sceVoiceDisconnectIPortFromOPort(uint32_t, uint32_t) { return SCE_OK; }
HLE("sceVoiceDisconnectIPortFromOPort", sceVoiceDisconnectIPortFromOPort)
static int32_t sceVoiceReadFromOPort(uint32_t, void*, uint32_t* size) {
    if (size) *size = 0;
    return SCE_OK;
}
HLE("sceVoiceReadFromOPort", sceVoiceReadFromOPort)
static int32_t sceVoiceWriteToIPort(uint32_t, const void*, uint32_t*, int16_t) { return SCE_OK; }
HLE("sceVoiceWriteToIPort", sceVoiceWriteToIPort)
static int32_t sceVoiceSetMuteFlag(uint32_t, bool) { return SCE_OK; }
HLE("sceVoiceSetMuteFlag", sceVoiceSetMuteFlag)
static int32_t sceVoiceSetMuteFlagAll(bool) { return SCE_OK; }
HLE("sceVoiceSetMuteFlagAll", sceVoiceSetMuteFlagAll)
static int32_t sceVoiceSetVolume(uint32_t, float) { return SCE_OK; }
HLE("sceVoiceSetVolume", sceVoiceSetVolume)
static int32_t sceVoiceUpdatePort(uint32_t, const void*) { return SCE_OK; }
HLE("sceVoiceUpdatePort", sceVoiceUpdatePort)
static int32_t sceVoiceGetPortInfo(uint32_t, void* info) {
    if (info) std::memset(info, 0, 32);
    return SCE_OK;
}
HLE("sceVoiceGetPortInfo", sceVoiceGetPortInfo)
static int32_t sceVoiceSetBitRate(uint32_t, int32_t) { return SCE_OK; }
HLE("sceVoiceSetBitRate", sceVoiceSetBitRate)
static int32_t sceVoiceGetBitRate(uint32_t, uint32_t* rate) {
    if (rate) *rate = 16000;
    return SCE_OK;
}
HLE("sceVoiceGetBitRate", sceVoiceGetBitRate)

}  // namespace d1
