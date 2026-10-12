// d1-native replacements for shadPS4 emulator-core pieces the renderer links against:
// logging backend, assert handlers and the (disabled) pipeline-cache storage.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <string>

#include <fmt/format.h>

#include "common/assert.h"
#include "common/logging/log.h"
#include "video_core/cache_storage.h"

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
std::array<Level, NUM_LOG_CLASSES> g_class_levels = [] {
    std::array<Level, NUM_LOG_CLASSES> a{};
    a.fill(initial_level());
    return a;
}();

void VLog(Class log_class, Level level, const char* file, int line, const char* func,
          fmt::string_view format, fmt::format_args args) {
    static std::mutex mu;
    static const char* names[] = {"T", "D", "I", "W", "E", "C", "-"};
    std::string msg = fmt::vformat(format, args);
    std::lock_guard lk(mu);
    std::fprintf(stderr, "[gpu %s] %s:%d %s: %s\n", names[int(level)], file ? std::strrchr(file, '/') ? std::strrchr(file, '/') + 1 : file : "?", line, func ? func : "", msg.c_str());
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

void assert_fail_impl() {
    std::fflush(stderr);
    __asm__ __volatile__("int $3");
}
[[noreturn]] void unreachable_impl() {
    assert_fail_impl();
    std::abort();
}
void assert_fail_debug_msg(const char* msg) {
    std::fprintf(stderr, "[gpu C] assertion failed: %s\n", msg);
    assert_fail_impl();
}

namespace Storage {
void DataBase::Open() { opened = false; }
void DataBase::Close() {}
void DataBase::FinishPreload() {}
bool DataBase::Save(BlobType, const std::string&, std::vector<u8>&&) { return false; }
bool DataBase::Save(BlobType, const std::string&, std::vector<u32>&&) { return false; }
void DataBase::Load(BlobType, const std::string&, std::vector<u8>&) {}
void DataBase::Load(BlobType, const std::string&, std::vector<u32>&) {}
void DataBase::ForEachBlob(BlobType, const std::function<void(std::vector<u8>&&)>&) {}
}  // namespace Storage
