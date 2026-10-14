// d1-native replacements for shadPS4 emulator-core pieces the renderer links against:
// logging backend, assert handlers and the (disabled) pipeline-cache storage.
#include <condition_variable>
#include <atomic>
#include <cstdio>
#include <deque>
#include <filesystem>
#include <fstream>
#include <thread>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <stdexcept>
#include <string>
#include <string_view>
#include <unordered_map>

#include <fmt/format.h>

#include "common/assert.h"
#include "common/logging/log.h"
#include "video_core/cache_storage.h"

#include "../../src/render_bridge.h"

namespace d1 {
void log(const char* fmt, ...);
}
std::atomic<u64> d1_gpu_busy_ns{0};  // patch 0006: GPU-thread busy time
std::atomic<u64> d1_gpu_wait_ns{0};  // patch 0006: time blocked on device execution

namespace Common::Log {

static Level initial_level() {
    const char* v = std::getenv("D1_GPU_LOG");
    if (!v) return Level::Warning;
    switch (v[0]) {
    case 't': return Level::Trace;
    case 'd': return Level::Debug;
    case 'i': return Level::Info;
    case 'e': return Level::Error;
    default: return Level::Warning;
    }
}
static const Level g_user_level = initial_level();
std::array<Level, NUM_LOG_CLASSES> g_class_levels = [] {
    std::array<Level, NUM_LOG_CLASSES> a{};
    a.fill(g_user_level);
    // pipeline compilations are logged at Info: always let them through to be counted
    auto& v = a[size_t(Class::Render_Vulkan)];
    if (v > Level::Info) v = Level::Info;
    return a;
}();

void VLog(Class log_class, Level level, const char* file, int line, const char* func,
          fmt::string_view format, fmt::format_args args) {
    if (level == Level::Info && log_class == Class::Render_Vulkan &&
        std::string_view(format.data(), format.size()).starts_with("Compiling")) {
        ++d1::render::perf().compiles;
        if (level < g_user_level) return;
    } else if (level < g_user_level) {
        return;
    }
    if (level >= Level::Warning) {
        ++d1::render::perf().gpu_messages;
        // A message repeated every draw floods the console and costs frames: print each call
        // site's first 20, then one in 10000.
        static std::mutex cm;
        static std::unordered_map<const void*, u64> seen;
        u64 n;
        {
            std::lock_guard lk(cm);
            n = ++seen[format.data()];
        }
        if (n > 20 && n % 10000 != 0) return;
        if (n == 20) d1::log("[gpu] (the next message repeats; further copies are suppressed)");
    }
    static const char* names[] = {"T", "D", "I", "W", "E", "C", "-"};
    std::string msg = fmt::vformat(format, args);
    const char* base = file ? (std::strrchr(file, '/') ? std::strrchr(file, '/') + 1 : file) : "?";
    if (const char* b2 = std::strrchr(base, '\\')) base = b2 + 1;
    // into d1-native.log (stderr is not kept on Windows)
    d1::log("[gpu %s] %s:%d %s: %s", names[int(level)], base, line, func ? func : "", msg.c_str());
}
void Setup(std::string_view) {}
void Switch(std::string_view, bool) {}
void Shutdown() {}
void Flush() { std::fflush(stderr); }
void Terminate() {}
void UpdateSinks() {}
void UpdateLogLevels(std::string_view) {}
void UpdateLogFlushLevel(std::string_view) {}

}  // namespace Common::Log

// A failed renderer assertion throws: during start-up (no usable Vulkan 1.3 device, ...)
// render::init catches it and the game falls back to the null GPU with a clear message.
void assert_fail_impl() {
    std::fflush(stderr);
    throw std::runtime_error("renderer assertion failed (see the line above)");
}
[[noreturn]] void unreachable_impl() {
    assert_fail_impl();
    std::abort();
}
void assert_fail_debug_msg(const char* msg) {
    std::fprintf(stderr, "[gpu C] assertion failed: %s\n", msg);
    assert_fail_impl();
}

// Pipeline cache storage: one file per blob under the d1-native data folder
// (<data>/shader_cache/<name>.<meta|spv|key|bin>), written by a background thread through
// a temporary file + rename so an interrupted run never leaves a torn blob behind. With it,
// shaders and pipelines compiled in one session load at start-up in the next (no stutter
// the second time through an area).
namespace d1_cache {
std::filesystem::path g_dir;
std::mutex g_mu;
std::condition_variable g_cv;
std::deque<std::pair<std::filesystem::path, std::vector<u8>>> g_queue;
bool g_stop = false;
std::thread g_worker;

const char* ext(Storage::BlobType t) {
    switch (t) {
    case Storage::BlobType::ShaderMeta: return ".meta";
    case Storage::BlobType::ShaderBinary: return ".spv";
    case Storage::BlobType::PipelineKey: return ".key";
    default: return ".bin";
    }
}
void worker() {
    for (;;) {
        std::pair<std::filesystem::path, std::vector<u8>> job;
        {
            std::unique_lock lk(g_mu);
            g_cv.wait(lk, [] { return g_stop || !g_queue.empty(); });
            if (g_queue.empty()) return;
            job = std::move(g_queue.front());
            g_queue.pop_front();
        }
        auto tmp = job.first;
        tmp += ".tmp";
        {
            std::ofstream f(tmp, std::ios::binary | std::ios::trunc);
            f.write(reinterpret_cast<const char*>(job.second.data()), std::streamsize(job.second.size()));
            if (!f) continue;
        }
        std::error_code ec;
        std::filesystem::rename(tmp, job.first, ec);
    }
}
bool read(const std::filesystem::path& p, std::vector<u8>& out) {
    std::ifstream f(p, std::ios::binary | std::ios::ate);
    if (!f) return false;
    out.resize(size_t(f.tellg()));
    f.seekg(0);
    f.read(reinterpret_cast<char*>(out.data()), std::streamsize(out.size()));
    return bool(f);
}
}  // namespace d1_cache

void d1_set_pipeline_cache_dir(const char* dir) {
    d1_cache::g_dir = dir ? std::filesystem::path(dir) : std::filesystem::path{};
}

namespace Storage {
void DataBase::Open() {
    if (opened || d1_cache::g_dir.empty()) return;
    std::error_code ec;
    std::filesystem::create_directories(d1_cache::g_dir, ec);
    if (ec) return;
    cache_path = d1_cache::g_dir;
    d1_cache::g_stop = false;
    d1_cache::g_worker = std::thread(d1_cache::worker);
    opened = true;
}
void DataBase::Close() {
    if (!opened) return;
    {
        std::lock_guard lk(d1_cache::g_mu);
        d1_cache::g_stop = true;
    }
    d1_cache::g_cv.notify_all();
    if (d1_cache::g_worker.joinable()) d1_cache::g_worker.join();
    opened = false;
}
void DataBase::FinishPreload() {}
static bool save_bytes(const std::filesystem::path& dir, BlobType t, const std::string& name, std::vector<u8>&& v) {
    auto p = dir / name;
    p += d1_cache::ext(t);
    {
        std::lock_guard lk(d1_cache::g_mu);
        d1_cache::g_queue.emplace_back(std::move(p), std::move(v));
    }
    d1_cache::g_cv.notify_one();
    return true;
}
bool DataBase::Save(BlobType t, const std::string& name, std::vector<u8>&& data) {
    return opened && save_bytes(cache_path, t, name, std::move(data));
}
bool DataBase::Save(BlobType t, const std::string& name, std::vector<u32>&& data) {
    if (!opened) return false;
    std::vector<u8> b(data.size() * 4);
    std::memcpy(b.data(), data.data(), b.size());
    return save_bytes(cache_path, t, name, std::move(b));
}
void DataBase::Load(BlobType t, const std::string& name, std::vector<u8>& data) {
    if (!opened) return;
    auto p = cache_path / name;
    p += d1_cache::ext(t);
    if (!d1_cache::read(p, data)) data.clear();
}
void DataBase::Load(BlobType t, const std::string& name, std::vector<u32>& data) {
    if (!opened) return;
    auto p = cache_path / name;
    p += d1_cache::ext(t);
    std::vector<u8> b;
    if (!d1_cache::read(p, b)) { data.clear(); return; }
    data.resize(b.size() / 4);
    std::memcpy(data.data(), b.data(), data.size() * 4);
}
void DataBase::ForEachBlob(BlobType t, const std::function<void(std::vector<u8>&&)>& func) {
    if (!opened) return;
    const std::string e = d1_cache::ext(t);
    std::error_code ec;
    for (const auto& ent : std::filesystem::directory_iterator(cache_path, ec)) {
        if (ent.path().extension() != e) continue;
        std::vector<u8> data;
        if (d1_cache::read(ent.path(), data)) func(std::move(data));
    }
}
}  // namespace Storage
