// D1_PROFILE_GPU=<file> (Linux): a sampling profiler for the renderer's command-processor
// thread (shadPS4:GpuComm). Every millisecond of that thread's CPU time, a signal records its
// call stack; at exit the stacks are written as "<count> <offset>;<offset>;..." with offsets
// relative to the executable's load address (symbolize with addr2line -f -C -e d1-native).
// Used to find where the per-draw CPU cost goes.
#ifdef __linux__
#include <atomic>
#include <csignal>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <dirent.h>
#include <dlfcn.h>
#include <execinfo.h>
#include <link.h>
#include <map>
#include <string>
#include <sys/syscall.h>
#include <unistd.h>
#include <vector>

namespace d1 {
void log(const char* fmt, ...);
}

namespace {
constexpr int kDepth = 24;
constexpr size_t kMax = 1 << 18;
struct Sample {
    uint8_t n;
    void* pc[kDepth];
};
Sample* g_samples;
std::atomic<size_t> g_count{0};
uintptr_t g_base;
std::string g_path;

void on_prof(int, siginfo_t*, void*) {
    const size_t i = g_count.fetch_add(1, std::memory_order_relaxed);
    if (i >= kMax) return;
    Sample& s = g_samples[i];
    s.n = uint8_t(backtrace(s.pc, kDepth));
}

void dump() {
    const size_t n = std::min(g_count.load(), kMax);
    std::map<std::string, size_t> agg;
    for (size_t i = 0; i < n; ++i) {
        std::string key;
        for (int k = 2; k < g_samples[i].n; ++k) {  // skip the handler and the signal frame
            const uintptr_t pc = uintptr_t(g_samples[i].pc[k]);
            char b[256];
            Dl_info di{};
            if (dladdr(g_samples[i].pc[k], &di) && di.dli_fname && uintptr_t(di.dli_fbase) != g_base) {
                const char* base = std::strrchr(di.dli_fname, '/');
                std::snprintf(b, sizeof b, "%s:%s+%lx;", base ? base + 1 : di.dli_fname, di.dli_sname ? di.dli_sname : "",
                              (unsigned long)(pc - uintptr_t(di.dli_fbase)));
            } else {
                std::snprintf(b, sizeof b, "%lx;", (unsigned long)(pc - g_base));
            }
            key += b;
        }
        ++agg[key];
    }
    if (FILE* f = std::fopen(g_path.c_str(), "w")) {
        for (auto& [k, c] : agg) std::fprintf(f, "%zu %s\n", c, k.c_str());
        std::fclose(f);
    }
    d1::log("gpu profiler: %zu samples written to %s", n, g_path.c_str());
}

pid_t find_thread(const char* name) {
    DIR* d = opendir("/proc/self/task");
    if (!d) return 0;
    pid_t found = 0;
    while (dirent* e = readdir(d)) {
        if (e->d_name[0] == '.') continue;
        std::string p = std::string("/proc/self/task/") + e->d_name + "/comm";
        if (FILE* f = std::fopen(p.c_str(), "r")) {
            char c[64] = {};
            if (std::fgets(c, sizeof c, f) && std::strncmp(c, name, std::strlen(name)) == 0) found = std::atoi(e->d_name);
            std::fclose(f);
        }
        if (found) break;
    }
    closedir(d);
    return found;
}
}  // namespace

namespace d1::render {
void gpu_profiler_dump() {
    if (g_samples) dump();
}
void start_gpu_profiler() {
    const char* path = std::getenv("D1_PROFILE_GPU");
    if (!path || !*path) return;
    const pid_t tid = find_thread("shadPS4:GpuComm");
    if (!tid) {
        d1::log("gpu profiler: GPU thread not found");
        return;
    }
    g_path = path;
    g_samples = static_cast<Sample*>(std::calloc(kMax, sizeof(Sample)));
    dl_iterate_phdr([](dl_phdr_info* info, size_t, void*) -> int {
        if (!info->dlpi_name || !info->dlpi_name[0]) {  // the executable
            g_base = info->dlpi_addr;
            return 1;
        }
        return 0;
    }, nullptr);
    void* warm[4];
    backtrace(warm, 4);  // load libgcc's unwinder before the first signal
    struct sigaction sa{};
    sa.sa_sigaction = on_prof;
    sa.sa_flags = SA_SIGINFO | SA_RESTART;
    sigaction(SIGPROF, &sa, nullptr);
    clockid_t clk = clockid_t((~unsigned(tid) << 3) | 6);  // CPUCLOCK_SCHED for that thread
    sigevent ev{};
    ev.sigev_notify = SIGEV_THREAD_ID;
    ev.sigev_signo = SIGPROF;
    ev._sigev_un._tid = tid;
    timer_t timer;
    if (timer_create(clk, &ev, &timer) != 0) {
        d1::log("gpu profiler: timer_create failed (%s)", std::strerror(errno));
        return;
    }
    itimerspec its{};
    its.it_interval.tv_nsec = its.it_value.tv_nsec = 1000000;
    timer_settime(timer, 0, &its, nullptr);
    std::atexit(dump);
    d1::log("gpu profiler: sampling thread %d every 1 ms of its CPU time", tid);
}
}  // namespace d1::render
#else
namespace d1::render {
void start_gpu_profiler() {}
void gpu_profiler_dump() {}
}  // namespace d1::render
#endif
