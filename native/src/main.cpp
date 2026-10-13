// d1-native: run Destiny 1's PS4 code natively on an x86-64 Windows or Linux host.
//
// Everything lives in the executable's folder:
//   d1-native(.exe), d1-backend(.exe)   the game runtime and the replacement backend
//   d1-native.cfg                       settings (written with defaults on first run)
//   d1-native.log, backend.log          logs of the last run
//   data/                               everything the game writes (saves, caches, ...)
//   game/                               the installed game, unless game_dir points elsewhere
// Options (all optional): --game <dir> --data <dir> --config <file> --eboot <file> --sce-module <dir>
//
// Loads eboot.bin and the game-shipped modules, links their imports (game modules,
// host implementations, or logging stubs), starts the modules, and jumps to the
// game's entry point on a thread with a PS4 thread control block installed.
#include <pthread.h>
#include <unistd.h>

#include <cctype>
#include <chrono>
#include <climits>
#include <cstdlib>
#include <cstring>
#include <stdexcept>
#include <string>
#include <thread>

#include "os.h"

#include "hle.h"
#include "discord.h"
#include "render_bridge.h"
#include "settings.h"
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

extern "C" D1_SYSV void d1_program_exit() {
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

static std::string join(const std::string& dir, const std::string& p) {
    const bool absolute = !p.empty() && (p[0] == '/' || p[0] == '\\' || (p.size() > 1 && p[1] == ':'));
    return absolute ? p : dir + "/" + p;
}
static void set_env(const char* k, const std::string& v) {
#if D1_WINDOWS
    _putenv_s(k, v.c_str());
#else
    setenv(k, v.c_str(), 1);
#endif
}
static bool file_exists(const std::string& p) { return access(p.c_str(), F_OK) == 0; }

// Lower-cased, '/'-separated full path, for the "data folder inside the game folder" check.
static std::string canonical(std::string p) {
#if D1_WINDOWS
    char b[4096];
    if (_fullpath(b, p.c_str(), sizeof b)) p = b;
    for (auto& c : p) c = c == '\\' ? '/' : char(std::tolower(static_cast<unsigned char>(c)));
#else
    char b[PATH_MAX];
    if (realpath(p.c_str(), b)) p = b;
#endif
    return p + "/";
}

int main(int argc, char** argv) {
    os::init();
    const std::string folder = os::exe_dir();
    std::string eboot, sce_module, app0, data = folder + "/data", config = folder + "/d1-native.cfg";
    for (int i = 1; i + 1 < argc; i += 2) {
        std::string k = argv[i], v = argv[i + 1];
        if (k == "--eboot") eboot = v;
        else if (k == "--sce-module") sce_module = v;
        else if (k == "--game" || k == "--app0") app0 = v;
        else if (k == "--data") data = v;
        else if (k == "--config") config = v;
    }
    log_to_file(folder + "/d1-native.log");
    load_settings(config);
    const Settings& st = settings();
    if (app0.empty()) app0 = join(folder, st.game_dir);
    if (eboot.empty()) eboot = app0 + "/eboot.bin";
    if (sce_module.empty() && file_exists(app0 + "/sce_module")) sce_module = app0 + "/sce_module";
    if (!file_exists(eboot)) {
        const std::string msg = "Game files not found: " + eboot + " is missing.\n\n"
                                "Put the installed game (CUSA00219 version 01.33: eboot.bin, sce_module, "
                                "packages) in\n" + app0 + "\n\nor set game_dir in\n" + settings_path();
        log("%s", msg.c_str());
        os::error_box(msg);
        return 2;
    }
    // The game directory is never written to; the data folder must live outside it.
    os::make_dirs(data);
    if (canonical(data).rfind(canonical(app0), 0) == 0) {
        log("the data folder (%s) must be outside the game folder (%s)", data.c_str(), app0.c_str());
        os::error_box("The data folder (" + data + ") must be outside the game folder (" + app0 + ").");
        return 2;
    }
    rt().app0 = app0;
    rt().data_root = data;

    // Backend: start ours from this folder, use a remote one, or none.
    if (st.backend == "local") {
#if D1_WINDOWS
        const std::string backend_exe = folder + "/d1-backend.exe";
#else
        const std::string backend_exe = folder + "/d1-backend";
#endif
        if (file_exists(backend_exe) &&
            os::spawn_child(backend_exe, "--packages-dir \"" + app0 + "/packages\"", folder + "/backend.log")) {
            log("backend: started %s", backend_exe.c_str());
            set_env("D1_BACKEND", "127.0.0.1");
            os::sleep_us(300000);  // let it open its ports
        } else {
            log("backend: %s not found or not started; playing offline", backend_exe.c_str());
        }
    } else if (st.backend != "off" && !st.backend.empty()) {
        set_env("D1_BACKEND", st.backend);
    }
    if (!getenv("D1_BYPASS") && getenv("D1_BACKEND") && !st.bypass.empty()) set_env("D1_BYPASS", st.bypass);

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
        log("load failed: %s", e.what());
        os::error_box(std::string("Could not load the game: ") + e.what() +
                      "\n\neboot.bin must be the decrypted 01.33 executable. Details are in d1-native.log.");
        return 1;
    }
    install_crash_handler();
    gpu_init();
    discord_start();

    pthread_attr_t a;
    pthread_attr_init(&a);
    pthread_attr_setstacksize(&a, 16 << 20);  // PS4 main thread default is smaller; be generous
    pthread_t t;
    pthread_create(&t, &a, main_thread, nullptr);
    if (const char* w = getenv("D1_WATCHDOG")) {  // seconds: dump every guest thread, then exit
        std::thread([secs = unsigned(atoi(w))] {
            std::this_thread::sleep_for(std::chrono::seconds(secs));
            log("watchdog: dumping guest threads");
            // D1_PEEK=off[,off...]: eboot offsets; "*off" dereferences a pointer first. Dumps 64 bytes.
            if (const char* pk = getenv("D1_PEEK")) {
                std::string list = pk;
                for (size_t p = 0; p < list.size();) {
                    size_t e = list.find(',', p);
                    std::string item = list.substr(p, e == std::string::npos ? std::string::npos : e - p);
                    p = e == std::string::npos ? list.size() : e + 1;
                    bool deref = !item.empty() && item[0] == '*';
                    uint64_t a = rt().modules[0].base + std::strtoull(item.c_str() + (deref ? 1 : 0), nullptr, 16);
                    if (deref) a = *reinterpret_cast<uint64_t*>(a);
                    const auto* q = reinterpret_cast<const uint32_t*>(a);
                    log("peek %s @%#llx: %08x %08x %08x %08x %08x %08x %08x %08x  %08x %08x %08x %08x %08x %08x %08x %08x",
                        item.c_str(), a, q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7], q[8], q[9], q[10], q[11], q[12], q[13], q[14], q[15]);
                }
            }
            dump_all_threads();
            print_import_summary();
            print_gpu_summary();
            _exit(0);
        }).detach();
    }
    // D1_POKE=secs:off+delta=value[;...]: after <secs>, write a 32-bit value at eboot offset
    // (prefix '*' to dereference a pointer at off first). Research aid.
    if (const char* pk = getenv("D1_POKE")) {
        std::thread([spec = std::string(pk)] {
            const char* p = spec.c_str();
            char* end;
            unsigned secs = unsigned(std::strtoul(p, &end, 10));
            std::this_thread::sleep_for(std::chrono::seconds(secs));
            std::string rest = *end == ':' ? end + 1 : "";
            for (size_t q = 0; q < rest.size();) {
                size_t e = rest.find(';', q);
                std::string it = rest.substr(q, e == std::string::npos ? std::string::npos : e - q);
                q = e == std::string::npos ? rest.size() : e + 1;
                bool deref = !it.empty() && it[0] == '*';
                const char* c = it.c_str() + (deref ? 1 : 0);
                uint64_t off = std::strtoull(c, &end, 16), delta = 0;
                if (*end == '+') delta = std::strtoull(end + 1, &end, 16);
                uint32_t val = uint32_t(std::strtoul(*end == '=' ? end + 1 : "0", nullptr, 0));
                uint64_t a = rt().modules[0].base + off;
                if (deref) a = *reinterpret_cast<uint64_t*>(a);
                *reinterpret_cast<volatile uint32_t*>(a + delta) = val;
                log("poke %s: %#llx <- %#x", it.c_str(), a + delta, val);
            }
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
