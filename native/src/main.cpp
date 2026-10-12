// d1-native: run Destiny 1's PS4 code natively on an x86-64 Linux host.
//
//   d1-native --eboot eboot.bin --sce-module sce_module/ --app0 <game dir> [--data <dir>]
//
// Loads eboot.bin and the game-shipped modules, links their imports (game modules,
// host implementations, or logging stubs), starts the modules, and jumps to the
// game's entry point on a thread with a PS4 thread control block installed.
#include <pthread.h>
#include <sys/stat.h>
#include <unistd.h>

#include <cstring>
#include <stdexcept>
#include <string>
#include <thread>

#include "hle.h"
#include "render_bridge.h"
#include "runtime.h"

namespace d1 {
void link_all();
void install_crash_handler();
void print_import_summary();
void register_guest_thread(const char* name);
void dump_all_threads();
void print_gpu_summary();
void install_game_hooks();
struct Thread;
Thread* ensure_self(const char* name);
}  // namespace d1

using namespace d1;

namespace {

constexpr uint64_t kExeBase = 0x800000000ull;   // same base the PS4 kernel uses for ASLR-less runs
constexpr uint64_t kModBase = 0x900000000ull;

struct EntryParams {
    int argc;
    uint32_t pad;
    const char* argv[33];
};
EntryParams g_params{};

extern "C" void d1_program_exit() {
    log("guest exit function called");
    print_import_summary();
    _exit(0);
}

// Enter the executable like the PS4 kernel: rdi = params, rsi = exit function,
// argc/argv copied to the top of a 16-byte-aligned stack minus 8.
[[noreturn]] void enter_guest(uint64_t entry, EntryParams* p) {
    asm volatile(
        "andq $-16, %%rsp\n"
        "subq $8, %%rsp\n"
        "pushq 8(%1)\n"
        "pushq 0(%1)\n"
        "leaq d1_root_frame(%%rip), %%rbp\n"
        "movq %1, %%rdi\n"
        "movq %2, %%rsi\n"
        "jmp *%0\n"
        :
        : "r"(entry), "r"(p), "r"(&d1_program_exit)
        : "rdi", "rsi", "memory");
    __builtin_unreachable();
}

using ModuleStart = int (*)(uint64_t args, const void* argp, void* param);

void* main_thread(void*) {
    void* tcb = tls_create_thread_block();
    tls_set_current(tcb);
    ensure_self("main");
    register_guest_thread("main");
    auto& mods = rt().modules;
    // Start dependencies before dependents: libSceFios2 (needed by libc), then libc.
    for (const char* name : {"libSceFios2.prx", "libc.prx"})
        for (auto& m : mods)
            if (m.name == name && m.init) {
                log("starting %s at %s", m.name.c_str(), describe_addr(m.init).c_str());
                int r = int(d1_call_guest(reinterpret_cast<const void*>(m.init), 0, 0, 0));
                log("%s module_start returned %d", m.name.c_str(), r);
            }
    g_params.argc = 1;
    g_params.argv[0] = "eboot.bin";
    log("entering eboot at %s", describe_addr(mods[0].entry).c_str());
    enter_guest(mods[0].entry, &g_params);
}

}  // namespace

int main(int argc, char** argv) {
    std::string eboot, sce_module, app0, data = "./d1-data";
    for (int i = 1; i + 1 < argc; i += 2) {
        std::string k = argv[i], v = argv[i + 1];
        if (k == "--eboot") eboot = v;
        else if (k == "--sce-module") sce_module = v;
        else if (k == "--app0") app0 = v;
        else if (k == "--data") data = v;
    }
    if (eboot.empty()) {
        std::fprintf(stderr, "usage: %s --eboot eboot.bin [--sce-module dir] [--app0 dir] [--data dir]\n", argv[0]);
        return 2;
    }
    rt().app0 = app0;
    rt().data_root = data;
    mkdir(data.c_str(), 0755);
    try {
        rt().modules.push_back(load_module(eboot, kExeBase));
        uint64_t base = kModBase;
        for (const char* n : {"libSceFios2.prx", "libc.prx"}) {
            if (sce_module.empty()) break;
            rt().modules.push_back(load_module(sce_module + "/" + n, base));
            base += (rt().modules.back().size + 0xFFFFFFF) & ~uint64_t(0xFFFFFFF);
        }
        link_all();
        install_game_hooks();
    } catch (const std::exception& e) {
        std::fprintf(stderr, "load failed: %s\n", e.what());
        return 1;
    }
    install_crash_handler();
    gpu_init();

    pthread_attr_t a;
    pthread_attr_init(&a);
    pthread_attr_setstacksize(&a, 16 << 20);  // PS4 main thread default is smaller; be generous
    pthread_t t;
    pthread_create(&t, &a, main_thread, nullptr);
    if (const char* w = getenv("D1_WATCHDOG")) {  // seconds: dump every guest thread, then exit
        std::thread([secs = unsigned(atoi(w))] {
            sleep(secs);
            log("watchdog: dumping guest threads");
            dump_all_threads();
            print_import_summary();
            print_gpu_summary();
            _exit(0);
        }).detach();
    }
    if (render::window_active()) {  // the window's event loop owns the main thread
        render::run_window_loop();
        log("window closed");
        print_gpu_summary();
        _exit(0);
    }
    pthread_join(t, nullptr);
    print_import_summary();
    return 0;
}
