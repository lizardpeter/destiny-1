// Linker, import thunks, call tracing, TLS and crash reporting.
#include "runtime.h"

#include <asm/prctl.h>
#include <pthread.h>
#include <signal.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <ucontext.h>
#include <unistd.h>

#include <algorithm>
#include <atomic>
#include <cstdarg>
#include <cstring>
#include <map>
#include <mutex>
#include <stdexcept>
#include <unordered_map>

#include "hle.h"
#include "nid.h"

namespace d1 {

// ------------------------------------------------------------------ logging
static std::mutex g_log_mutex;
void log(const char* fmt, ...) {
    std::lock_guard lk(g_log_mutex);
    va_list ap;
    va_start(ap, fmt);
    std::vfprintf(stderr, fmt, ap);
    va_end(ap);
    std::fputc('\n', stderr);
}

std::vector<HleEntry>& hle_registry() {
    static std::vector<HleEntry> r;
    return r;
}

Runtime& rt() {
    static Runtime r;
    return r;
}

// Names for NIDs we do not implement (generated from evidence/generated/d1_import_surface.json).
static const std::pair<const char*, const char*> kImportNames[] = {
#include "import_names.inc"
};

std::string describe_addr(uint64_t a) {
    for (auto& m : rt().modules)
        if (m.contains(a)) {
            char b[160];
            std::snprintf(b, sizeof b, "%s+0x%lx", m.name.c_str(), (unsigned long)(a - m.base));
            return b;
        }
    char b[32];
    std::snprintf(b, sizeof b, "0x%lx", (unsigned long)a);
    return b;
}

// ------------------------------------------------------------------ import thunks + tracing
struct ImportInfo {
    std::string name;     // symbol name (or NID when unknown)
    std::string library;  // importing library name
    std::string importer; // module that imports it
    void* target;         // HLE function (traced) or nullptr (unimplemented)
    std::atomic<uint64_t> calls{0};
};
static std::vector<ImportInfo*> g_imports;

static std::atomic<uint64_t> g_seq{0};
struct TraceRec { uint64_t seq; uint32_t idx; uint32_t tid; uint64_t a0, a1, a2; };
static constexpr int kRing = 256;
static TraceRec g_ring[kRing];
static bool g_trace_all = false;
static bool g_abort_on_unimpl = false;

static uint32_t gettid32() { return uint32_t(syscall(SYS_gettid)); }

extern "C" void d1_log_call(uint64_t idx, uint64_t* regs) {
    // regs: rdi, rsi, rdx, rcx, r8, r9
    ImportInfo* ii = g_imports[idx];
    uint64_t n = ii->calls.fetch_add(1);
    uint64_t s = g_seq.fetch_add(1);
    g_ring[s % kRing] = {s, uint32_t(idx), gettid32(), regs[0], regs[1], regs[2]};
    if (g_trace_all || (!ii->target && n < 3))
        log("[%u] %s %s(%#lx, %#lx, %#lx)%s", gettid32(), ii->target ? "call" : "UNIMPL",
            ii->name.c_str(), regs[0], regs[1], regs[2], ii->target ? "" : " -> 0");
    if (!ii->target && g_abort_on_unimpl) {
        log("aborting on first unimplemented import %s (%s)", ii->name.c_str(), ii->library.c_str());
        _exit(3);
    }
}

// Common entry for all import thunks. r11 = import index, r10 = target (0 = unimplemented).
// Saves integer + vector argument registers and AL (vararg count), logs, then tail-jumps.
extern "C" void d1_import_entry();
asm(R"(
    .text
    .globl d1_import_entry
    .type d1_import_entry, @function
d1_import_entry:
    push %rbp
    mov %rsp, %rbp
    and $-16, %rsp
    sub $208, %rsp
    mov %rdi, 0(%rsp)
    mov %rsi, 8(%rsp)
    mov %rdx, 16(%rsp)
    mov %rcx, 24(%rsp)
    mov %r8, 32(%rsp)
    mov %r9, 40(%rsp)
    mov %rax, 48(%rsp)
    mov %r10, 56(%rsp)
    movdqu %xmm0, 64(%rsp)
    movdqu %xmm1, 80(%rsp)
    movdqu %xmm2, 96(%rsp)
    movdqu %xmm3, 112(%rsp)
    movdqu %xmm4, 128(%rsp)
    movdqu %xmm5, 144(%rsp)
    movdqu %xmm6, 160(%rsp)
    movdqu %xmm7, 176(%rsp)
    mov %r11, %rdi
    mov %rsp, %rsi
    call d1_log_call
    mov 0(%rsp), %rdi
    mov 8(%rsp), %rsi
    mov 16(%rsp), %rdx
    mov 24(%rsp), %rcx
    mov 32(%rsp), %r8
    mov 40(%rsp), %r9
    mov 48(%rsp), %rax
    mov 56(%rsp), %r10
    movdqu 64(%rsp), %xmm0
    movdqu 80(%rsp), %xmm1
    movdqu 96(%rsp), %xmm2
    movdqu 112(%rsp), %xmm3
    movdqu 128(%rsp), %xmm4
    movdqu 144(%rsp), %xmm5
    movdqu 160(%rsp), %xmm6
    movdqu 176(%rsp), %xmm7
    mov %rbp, %rsp
    pop %rbp
    test %r10, %r10
    jz 1f
    jmp *%r10
1:
    xor %eax, %eax
    ret
)");

static uint8_t* g_thunk_mem = nullptr;
static size_t g_thunk_used = 0;
static constexpr size_t kThunkArea = 4 << 20;

static void* make_thunk(uint64_t idx, void* target) {
    if (!g_thunk_mem) {
        g_thunk_mem = static_cast<uint8_t*>(mmap(nullptr, kThunkArea, PROT_READ | PROT_WRITE | PROT_EXEC,
                                                 MAP_PRIVATE | MAP_ANONYMOUS, -1, 0));
        if (g_thunk_mem == MAP_FAILED) throw std::runtime_error("thunk mmap failed");
    }
    uint8_t* p = g_thunk_mem + g_thunk_used;
    // mov r11, imm64 ; mov r10, imm64 ; jmp [rip+0] ; dq d1_import_entry
    uint8_t code[] = {0x49, 0xBB, 0, 0, 0, 0, 0, 0, 0, 0, 0x49, 0xBA, 0, 0, 0, 0, 0, 0, 0, 0,
                      0xFF, 0x25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    uint64_t t = reinterpret_cast<uint64_t>(target), e = reinterpret_cast<uint64_t>(&d1_import_entry);
    std::memcpy(code + 2, &idx, 8);
    std::memcpy(code + 12, &t, 8);
    std::memcpy(code + 26, &e, 8);
    std::memcpy(p, code, sizeof code);
    g_thunk_used += 48;
    return p;
}

// ------------------------------------------------------------------ guest calls
// Guest code walks frame-pointer chains (callstack capture for allocation tracking) several
// levels deep. Calls into the guest start from a terminal frame whose saved rbp points to
// itself and whose return address is 0, so any walk ends cleanly instead of running into
// host frames.
asm(R"(
    .data
    .balign 16
    .globl d1_root_frame
d1_root_frame:
    .quad d1_root_frame
    .quad 0
    .text
    .globl d1_call_guest
    .type d1_call_guest, @function
d1_call_guest:
    push %rbp
    push %rbx
    mov %rsp, %rbx
    and $-16, %rsp
    lea d1_root_frame(%rip), %rbp
    mov %rdi, %rax
    mov %rsi, %rdi
    mov %rdx, %rsi
    mov %rcx, %rdx
    call *%rax
    mov %rbx, %rsp
    pop %rbx
    pop %rbp
    ret
)");

// ------------------------------------------------------------------ TLS
// PS4 (FreeBSD amd64, TLS variant II): fs:[0] is the TCB self-pointer and the main
// executable's static TLS block sits immediately below the TCB. Guest code reads the
// TCB with `mov r64, fs:[0]`; the loader rewrites that prefix to GS so glibc keeps FS.
struct Tcb {
    Tcb* self;
    void* dtv;
    uint64_t reserved[30];
};
static uint64_t g_static_tls_size = 0;
static thread_local std::map<int, void*>* t_dtv = nullptr;
static thread_local Tcb* t_tcb = nullptr;

void* tls_create_thread_block() {
    const Module& exe = rt().modules[0];
    const uint64_t align = std::max<uint64_t>(exe.tls_align, 16);
    g_static_tls_size = (exe.tls_memsz + align - 1) & ~(align - 1);
    uint8_t* blk = static_cast<uint8_t*>(aligned_alloc(64, g_static_tls_size + sizeof(Tcb) + 64));
    std::memset(blk, 0, g_static_tls_size + sizeof(Tcb) + 64);
    uint8_t* tls = blk + 64;
    Tcb* tcb = reinterpret_cast<Tcb*>(tls + g_static_tls_size);
    if (exe.tls_filesz) std::memcpy(tls, reinterpret_cast<void*>(exe.tls_init), exe.tls_filesz);
    tcb->self = tcb;
    return tcb;
}

void tls_set_current(void* tcb) {
    if (syscall(SYS_arch_prctl, ARCH_SET_GS, reinterpret_cast<uint64_t>(tcb)) != 0)
        throw std::runtime_error("arch_prctl(ARCH_SET_GS) failed");
    t_tcb = static_cast<Tcb*>(tcb);
}

void tls_destroy_thread_block(void*) { /* leaked deliberately in the prototype */ }

// __tls_get_addr(tls_index*): dynamic TLS for modules loaded after the executable.
struct TlsIndex { uint64_t modid; uint64_t offset; };
static void* tls_get_addr(TlsIndex* ti) {
    if (ti->modid == 1) return reinterpret_cast<uint8_t*>(t_tcb) - g_static_tls_size + ti->offset;
    if (!t_dtv) t_dtv = new std::map<int, void*>();
    auto& slot = (*t_dtv)[int(ti->modid)];
    if (!slot) {
        for (auto& m : rt().modules)
            if (m.tls_modid == int(ti->modid)) {
                slot = aligned_alloc(64, (m.tls_memsz + 63) & ~uint64_t(63));
                std::memset(slot, 0, m.tls_memsz);
                if (m.tls_filesz) std::memcpy(slot, reinterpret_cast<void*>(m.tls_init), m.tls_filesz);
            }
        if (!slot) { log("__tls_get_addr: unknown module id %lu", ti->modid); return nullptr; }
    }
    return static_cast<uint8_t*>(slot) + ti->offset;
}
HLE("__tls_get_addr", tls_get_addr)

static size_t patch_fs_tcb(Module& m) {
    // 64 [48|4C] 8B <modrm mod=00 rm=100> 25 00 00 00 00   mov r64, qword ptr fs:[0]
    size_t n = 0;
    auto* p = reinterpret_cast<uint8_t*>(m.text_lo);
    const size_t len = m.text_hi - m.text_lo;
    for (size_t i = 0; i + 9 <= len; ++i) {
        if (p[i] == 0x64 && (p[i + 1] == 0x48 || p[i + 1] == 0x4C) && p[i + 2] == 0x8B &&
            (p[i + 3] & 0xC7) == 0x04 && p[i + 4] == 0x25 && !p[i + 5] && !p[i + 6] && !p[i + 7] && !p[i + 8]) {
            p[i] = 0x65;  // FS -> GS
            ++n;
        }
    }
    return n;
}

// ------------------------------------------------------------------ linker
void link_all() {
    auto& mods = rt().modules;
    int next_modid = 1;
    for (auto& m : mods)
        if (m.tls_memsz) m.tls_modid = next_modid++;

    // Exports from game-shipped modules: (nid, library) -> address
    std::map<std::pair<std::string, std::string>, uint64_t> exports;
    for (auto& m : mods)
        for (auto& s : m.syms) {
            if (!s.value || !s.shndx) continue;
            auto h1 = s.name.find('#');
            if (h1 == std::string::npos) continue;
            auto h2 = s.name.find('#', h1 + 1);
            int lib = decode_sce_id(s.name.substr(h1 + 1, h2 - h1 - 1));
            auto it = m.export_libs.find(lib);
            if (it == m.export_libs.end()) continue;
            exports[{s.name.substr(0, h1), it->second}] = m.base + s.value;
        }

    std::unordered_map<std::string, const HleEntry*> hle;
    for (auto& e : hle_registry()) hle[nid_of(e.name)] = &e;
    std::unordered_map<std::string, const char*> names;
    for (auto& [nid, name] : kImportNames) names[nid] = name;

    std::map<std::string, void*> thunk_cache;  // key importer|nid|lib
    size_t n_game = 0, n_hle = 0, n_unimpl = 0, n_obj = 0;
    for (auto& m : mods) {
        for (auto& r : m.relas) {
            auto* where = reinterpret_cast<uint64_t*>(m.base + r.offset);
            switch (r.type) {
            case 8:  // R_X86_64_RELATIVE
                *where = m.base + r.addend;
                continue;
            case 16:  // R_X86_64_DTPMOD64
                *where = uint64_t(m.tls_modid);
                continue;
            case 17:  // R_X86_64_DTPOFF64
                *where = m.syms[r.sym].value + r.addend;
                continue;
            case 1: case 6: case 7: break;  // 64, GLOB_DAT, JUMP_SLOT
            default:
                log("%s: unsupported relocation type %u at +%#lx", m.name.c_str(), r.type, r.offset);
                continue;
            }
            const auto& s = m.syms[r.sym];
            uint64_t value = 0;
            if (s.value && s.shndx) {
                value = m.base + s.value;
            } else {
                auto h1 = s.name.find('#');
                std::string nid = s.name.substr(0, h1);
                std::string lib;
                if (h1 != std::string::npos) {
                    auto h2 = s.name.find('#', h1 + 1);
                    lib = m.import_libs[decode_sce_id(s.name.substr(h1 + 1, h2 - h1 - 1))];
                }
                const bool is_object = (s.info & 0xF) == 1;
                std::string key = m.name + "|" + nid + "|" + lib;
                if (auto ex = exports.find({nid, lib}); ex != exports.end()) {
                    value = ex->second;
                    ++n_game;
                } else if (auto h = hle.find(nid); h != hle.end()) {
                    if (h->second->object) {
                        value = reinterpret_cast<uint64_t>(h->second->addr);
                    } else {
                        auto& t = thunk_cache[key];
                        if (!t) {
                            auto* ii = new ImportInfo{h->second->name, lib, m.name, h->second->addr};
                            g_imports.push_back(ii);
                            t = make_thunk(g_imports.size() - 1, h->second->addr);
                        }
                        value = reinterpret_cast<uint64_t>(t);
                    }
                    ++n_hle;
                } else if (is_object) {
                    auto& t = thunk_cache[key];
                    if (!t) {
                        t = calloc(1, 0x1000);
                        auto nm = names.find(nid);
                        log("data import %s (%s) -> zeroed placeholder", nm != names.end() ? nm->second : nid.c_str(),
                            lib.c_str());
                    }
                    value = reinterpret_cast<uint64_t>(t);
                    ++n_obj;
                } else {
                    auto& t = thunk_cache[key];
                    if (!t) {
                        auto nm = names.find(nid);
                        auto* ii = new ImportInfo{nm != names.end() ? nm->second : nid, lib, m.name, nullptr};
                        g_imports.push_back(ii);
                        t = make_thunk(g_imports.size() - 1, nullptr);
                    }
                    value = reinterpret_cast<uint64_t>(t);
                    ++n_unimpl;
                }
            }
            *where = (r.type == 1) ? value + r.addend : value;
        }
    }
    for (auto& m : mods) {
        size_t p = patch_fs_tcb(m);
        log("%-18s base %#lx size %#lx entry %s init %s tls(mod %d, %#lx bytes) fs:[0] patched %zu",
            m.name.c_str(), m.base, m.size, m.entry ? describe_addr(m.entry).c_str() : "-",
            m.init ? describe_addr(m.init).c_str() : "-", m.tls_modid, m.tls_memsz, p);
    }
    log("imports: %zu game-module, %zu HLE, %zu unimplemented (logging stubs), %zu data placeholders", n_game,
        n_hle, n_unimpl, n_obj);
}

// ------------------------------------------------------------------ crash reporting
static void dump_ring() {
    uint64_t s = g_seq.load();
    uint64_t from = s > 48 ? s - 48 : 0;
    log("last %lu import calls:", s - from);
    for (uint64_t i = from; i < s; ++i) {
        auto& r = g_ring[i % kRing];
        if (r.seq != i) continue;
        log("  #%lu [%u] %s%s(%#lx, %#lx, %#lx)", r.seq, r.tid, g_imports[r.idx]->target ? "" : "UNIMPL ",
            g_imports[r.idx]->name.c_str(), r.a0, r.a1, r.a2);
    }
}

static void on_fault(int sig, siginfo_t* si, void* uc_) {
    // Write to a page the renderer protects to track CPU changes: let it invalidate and retry.
    if ((sig == SIGSEGV || sig == SIGBUS) && gpu_on_fault(uc_, si->si_addr)) return;
    auto* uc = static_cast<ucontext_t*>(uc_);
    uint64_t rip = uc->uc_mcontext.gregs[REG_RIP];
    uint64_t rbp = uc->uc_mcontext.gregs[REG_RBP];
    log("\n=== %s at %s (fault address %p) thread %u ===", strsignal(sig), describe_addr(rip).c_str(), si->si_addr,
        gettid32());
    static const char* R[] = {"r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15", "rdi", "rsi", "rbp", "rbx",
                              "rdx", "rax", "rcx", "rsp"};
    for (int i = 0; i < 16; ++i) std::fprintf(stderr, "%s=%#llx%s", R[i], uc->uc_mcontext.gregs[i], i % 4 == 3 ? "\n" : "  ");
    log("guest call stack (frame pointers):");
    for (int d = 0; d < 24 && rbp; ++d) {
        uint64_t* f = reinterpret_cast<uint64_t*>(rbp);
        if (rbp & 7) break;
        uint64_t ret = f[1];
        log("  %s", describe_addr(ret).c_str());
        if (f[0] <= rbp) break;
        rbp = f[0];
    }
    dump_ring();
    _exit(128 + sig);
}

// ------------------------------------------------------------------ hang diagnostics
static std::mutex g_threads_mutex;
static std::vector<std::pair<uint32_t, std::string>> g_threads;

void register_guest_thread(const char* name) {
    std::lock_guard lk(g_threads_mutex);
    g_threads.push_back({gettid32(), name ? name : "?"});
}

static void walk(uint64_t rip, uint64_t rbp) {
    log("  at %s", describe_addr(rip).c_str());
    for (int d = 0; d < 16 && rbp && !(rbp & 7); ++d) {
        uint64_t* f = reinterpret_cast<uint64_t*>(rbp);
        log("  <- %s", describe_addr(f[1]).c_str());
        if (f[0] <= rbp) break;
        rbp = f[0];
    }
}

static void on_dump(int, siginfo_t*, void* uc_) {
    auto* uc = static_cast<ucontext_t*>(uc_);
    log("thread %u:", gettid32());
    walk(uc->uc_mcontext.gregs[REG_RIP], uc->uc_mcontext.gregs[REG_RBP]);
}

void dump_all_threads() {
    std::vector<std::pair<uint32_t, std::string>> ts;
    { std::lock_guard lk(g_threads_mutex); ts = g_threads; }
    for (auto& [tid, name] : ts) {
        log("--- %s (%u)", name.c_str(), tid);
        syscall(SYS_tgkill, getpid(), tid, SIGUSR2);
        usleep(100000);
    }
    dump_ring();
}

void install_crash_handler() {
    {
        struct sigaction sd{};
        sd.sa_sigaction = on_dump;
        sd.sa_flags = SA_SIGINFO | SA_RESTART;
        sigaction(SIGUSR2, &sd, nullptr);
    }
    static uint8_t altstack[1 << 20];
    stack_t ss{};
    ss.ss_sp = altstack;
    ss.ss_size = sizeof altstack;
    sigaltstack(&ss, nullptr);
    struct sigaction sa{};
    sa.sa_sigaction = on_fault;
    sa.sa_flags = SA_SIGINFO | SA_ONSTACK;
    for (int s : {SIGSEGV, SIGILL, SIGBUS, SIGFPE, SIGTRAP}) sigaction(s, &sa, nullptr);
    g_trace_all = getenv("D1_TRACE") != nullptr;
    g_abort_on_unimpl = getenv("D1_ABORT_ON_UNIMPL") != nullptr;
}

void print_import_summary() {
    log("import call counts (top 40):");
    std::vector<ImportInfo*> v(g_imports.begin(), g_imports.end());
    std::sort(v.begin(), v.end(), [](auto* a, auto* b) { return a->calls > b->calls; });
    for (size_t i = 0; i < v.size() && i < 40 && v[i]->calls; ++i)
        log("  %8lu  %s%s", v[i]->calls.load(), v[i]->target ? "" : "UNIMPL ", v[i]->name.c_str());
}

}  // namespace d1
