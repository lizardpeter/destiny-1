// Windows implementation of os.h.
//
// Guest memory lives in one big address-space reservation made of "placeholders"
// (VirtualAlloc2 / MapViewOfFile3, Windows 10 1803+), so mappings can be placed at exact
// addresses inside it and replaced later, the way mmap(MAP_FIXED) works on Linux. Direct
// memory is a pagefile-backed section mapped as views, so two views of the same offset
// alias like the console's CPU and GPU mappings.
#include "os.h"

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <winsock2.h>
#include <timeapi.h>

#include <algorithm>
#include <cstdio>
#include <iterator>
#include <map>
#include <mutex>
#include <vector>

#include "hle.h"

namespace d1::os {

// ------------------------------------------------------------------ placeholder API
// Resolved at run time: older SDK import libraries do not have them.
using VirtualAlloc2Fn = PVOID(WINAPI*)(HANDLE, PVOID, SIZE_T, ULONG, ULONG, MEM_EXTENDED_PARAMETER*, ULONG);
using MapViewOfFile3Fn = PVOID(WINAPI*)(HANDLE, HANDLE, PVOID, ULONG64, SIZE_T, ULONG, ULONG, MEM_EXTENDED_PARAMETER*, ULONG);
using UnmapViewOfFile2Fn = BOOL(WINAPI*)(HANDLE, PVOID, ULONG);
static VirtualAlloc2Fn pVirtualAlloc2;
static MapViewOfFile3Fn pMapViewOfFile3;
static UnmapViewOfFile2Fn pUnmapViewOfFile2;

#ifndef MEM_RESERVE_PLACEHOLDER
#define MEM_RESERVE_PLACEHOLDER 0x00040000
#define MEM_REPLACE_PLACEHOLDER 0x00004000
#define MEM_PRESERVE_PLACEHOLDER 0x00000002
#define MEM_COALESCE_PLACEHOLDERS 0x00000001
#endif

// Guest address space: [kPoolBase, kPoolEnd). PS4 user mappings, the eboot (0x8_0000_0000)
// and the game modules (0x9_0000_0000+) are all placed in here; the host never is.
static constexpr uint64_t kPoolBase = 0x200000000ull;
static constexpr uint64_t kPoolEnd = 0x1000000000ull;

enum class Kind { Free, Reserved, Anon, View };
struct Seg { uint64_t size; Kind kind; };
static std::map<uint64_t, Seg> g_segs;  // start -> segment, covers the pool exactly
static std::recursive_mutex g_mem;
static HANDLE g_section = nullptr;
static bool g_pool = false;

static DWORD win_prot(int p) {
    const bool r = p & kRead, w = p & kWrite, x = p & kExec;
    if (x) return w ? PAGE_EXECUTE_READWRITE : r ? PAGE_EXECUTE_READ : PAGE_EXECUTE;
    if (w) return PAGE_READWRITE;
    return r ? PAGE_READONLY : PAGE_NOACCESS;
}

static void pool_init() {
    HMODULE kb = GetModuleHandleW(L"kernelbase.dll");
    pVirtualAlloc2 = reinterpret_cast<VirtualAlloc2Fn>(GetProcAddress(kb, "VirtualAlloc2"));
    pMapViewOfFile3 = reinterpret_cast<MapViewOfFile3Fn>(GetProcAddress(kb, "MapViewOfFile3"));
    pUnmapViewOfFile2 = reinterpret_cast<UnmapViewOfFile2Fn>(GetProcAddress(kb, "UnmapViewOfFile2"));
    if (!pVirtualAlloc2 || !pMapViewOfFile3 || !pUnmapViewOfFile2) {
        log("memory: Windows 10 version 1803 or newer is required (VirtualAlloc2 missing)");
        return;
    }
    void* p = pVirtualAlloc2(GetCurrentProcess(), reinterpret_cast<void*>(kPoolBase), kPoolEnd - kPoolBase,
                             MEM_RESERVE | MEM_RESERVE_PLACEHOLDER, PAGE_NOACCESS, nullptr, 0);
    if (p != reinterpret_cast<void*>(kPoolBase)) {
        log("memory: cannot reserve the guest address range %#llx-%#llx (error %lu)", kPoolBase, kPoolEnd,
            GetLastError());
        return;
    }
    g_segs[kPoolBase] = {kPoolEnd - kPoolBase, Kind::Free};
    g_pool = true;
}

static bool in_pool(uint64_t a, uint64_t n) { return g_pool && a >= kPoolBase && a + n <= kPoolEnd && a + n > a; }

static std::map<uint64_t, Seg>::iterator seg_at(uint64_t a) {
    auto it = g_segs.upper_bound(a);
    return --it;  // the pool is covered exactly, so a segment always contains a
}

// Turn an allocation or view back into a free placeholder.
static void to_placeholder(std::map<uint64_t, Seg>::iterator it) {
    void* p = reinterpret_cast<void*>(it->first);
    if (it->second.kind == Kind::Anon) VirtualFree(p, 0, MEM_RELEASE | MEM_PRESERVE_PLACEHOLDER);
    else if (it->second.kind == Kind::View) pUnmapViewOfFile2(GetCurrentProcess(), p, MEM_PRESERVE_PLACEHOLDER);
    it->second.kind = Kind::Free;
}

// Merge a free segment with free neighbours (Windows only places a mapping inside one
// placeholder, so large free ranges must stay whole).
static void coalesce(std::map<uint64_t, Seg>::iterator it) {
    if (it->second.kind != Kind::Free) return;
    if (it != g_segs.begin()) {
        auto prev = std::prev(it);
        if (prev->second.kind == Kind::Free) {
            VirtualFree(reinterpret_cast<void*>(prev->first), prev->second.size + it->second.size,
                        MEM_RELEASE | MEM_COALESCE_PLACEHOLDERS);
            prev->second.size += it->second.size;
            g_segs.erase(it);
            it = prev;
        }
    }
    auto next = std::next(it);
    if (next != g_segs.end() && next->second.kind == Kind::Free) {
        VirtualFree(reinterpret_cast<void*>(it->first), it->second.size + next->second.size,
                    MEM_RELEASE | MEM_COALESCE_PLACEHOLDERS);
        it->second.size += next->second.size;
        g_segs.erase(next);
    }
}

// Make [a, a+n) exactly one placeholder segment. Mappings in the way are removed when
// replace is set (MAP_FIXED semantics) and must lie entirely inside the range.
static bool carve(uint64_t a, uint64_t n, bool replace) {
    for (auto it = seg_at(a); it != g_segs.end() && it->first < a + n;) {
        Kind k = it->second.kind;
        if (k == Kind::Anon || k == Kind::View) {
            if (!replace || it->first < a || it->first + it->second.size > a + n) return false;
            to_placeholder(it);
        }
        ++it;
    }
    // Free/reserved pieces in the range: merge into one placeholder, then split it out.
    auto first = seg_at(a);
    Kind keep = first->second.kind == Kind::Reserved ? Kind::Reserved : Kind::Free;
    uint64_t lo = first->first, hi = a + n;
    for (auto it = first; it != g_segs.end() && it->first < a + n; ++it) hi = std::max(hi, it->first + it->second.size);
    if (std::next(first) != g_segs.end() && std::next(first)->first < hi) {
        VirtualFree(reinterpret_cast<void*>(lo), hi - lo, MEM_RELEASE | MEM_COALESCE_PLACEHOLDERS);
        g_segs.erase(std::next(first), g_segs.lower_bound(hi));
        first->second.size = hi - lo;
    }
    if (lo != a || hi != a + n) {
        if (!VirtualFree(reinterpret_cast<void*>(a), n, MEM_RELEASE | MEM_PRESERVE_PLACEHOLDER)) return false;
        if (lo < a) g_segs[lo] = {a - lo, keep};
        if (hi > a + n) g_segs[a + n] = {hi - a - n, keep};
    }
    g_segs[a] = {n, keep};
    return true;
}

static uint64_t round_up(uint64_t v) { return (v + 0xFFFF) & ~uint64_t(0xFFFF); }

void* alloc(uint64_t addr, uint64_t size, int prot, bool exact) {
    size = round_up(size);
    std::lock_guard lk(g_mem);
    if (addr && in_pool(addr, size) && carve(addr, size, exact)) {
        void* p = pVirtualAlloc2(GetCurrentProcess(), reinterpret_cast<void*>(addr), size,
                                 MEM_RESERVE | MEM_COMMIT | MEM_REPLACE_PLACEHOLDER, win_prot(prot), nullptr, 0);
        if (p) {
            g_segs[addr].kind = Kind::Anon;
            return p;
        }
        log("memory: VirtualAlloc2 at %#llx (+%#llx) failed: %lu", addr, size, GetLastError());
        coalesce(g_segs.find(addr));
        return nullptr;
    }
    if (exact) return nullptr;
    return VirtualAlloc(nullptr, size, MEM_RESERVE | MEM_COMMIT, win_prot(prot));
}

void* reserve(uint64_t addr, uint64_t size, bool exact) {
    size = round_up(size);
    std::lock_guard lk(g_mem);
    if (addr && in_pool(addr, size) && carve(addr, size, exact)) {
        g_segs[addr].kind = Kind::Reserved;
        return reinterpret_cast<void*>(addr);
    }
    if (exact) return nullptr;
    return VirtualAlloc(nullptr, size, MEM_RESERVE, PAGE_NOACCESS);
}

bool release(void* p, uint64_t size) {
    const uint64_t a = reinterpret_cast<uint64_t>(p);
    std::lock_guard lk(g_mem);
    if (!in_pool(a, 1)) return VirtualFree(p, 0, MEM_RELEASE);
    size = round_up(size);
    bool ok = true;
    for (auto it = seg_at(a); it != g_segs.end() && it->first < a + size;) {
        if (it->first >= a && it->first + it->second.size <= a + size) {
            if (it->second.kind != Kind::Free) to_placeholder(it);
            it->second.kind = Kind::Free;
        } else if (it->second.kind == Kind::Anon) {
            // Part of a private allocation: drop its pages, keep the allocation.
            uint64_t lo = std::max(a, it->first), hi = std::min(a + size, it->first + it->second.size);
            VirtualFree(reinterpret_cast<void*>(lo), hi - lo, MEM_DECOMMIT);
            VirtualAlloc(reinterpret_cast<void*>(lo), hi - lo, MEM_COMMIT, PAGE_NOACCESS);
        } else if (it->second.kind == Kind::View) {
            ok = false;  // part of a view cannot be unmapped on Windows; leave it
        }
        ++it;
    }
    // Merge neighbouring free placeholders around the released range.
    auto it = seg_at(a);
    if (it != g_segs.begin()) --it;
    while (it != g_segs.end() && it->first <= a + size) {
        auto next = std::next(it);
        if (next != g_segs.end() && it->second.kind == Kind::Free && next->second.kind == Kind::Free) {
            VirtualFree(reinterpret_cast<void*>(it->first), it->second.size + next->second.size,
                        MEM_RELEASE | MEM_COALESCE_PLACEHOLDERS);
            it->second.size += next->second.size;
            g_segs.erase(next);
        } else {
            it = next;
        }
    }
    return ok;
}

bool protect(void* p, uint64_t size, int prot) {
    // VirtualProtect cannot span two allocations: go one mapping at a time.
    const uint64_t a = reinterpret_cast<uint64_t>(p);
    DWORD old;
    if (!in_pool(a, size)) return VirtualProtect(p, size, win_prot(prot), &old);
    std::lock_guard lk(g_mem);
    bool ok = true;
    for (auto it = seg_at(a); it != g_segs.end() && it->first < a + size; ++it) {
        if (it->second.kind != Kind::Anon && it->second.kind != Kind::View) continue;
        uint64_t lo = std::max(a, it->first), hi = std::min(a + size, it->first + it->second.size);
        ok &= VirtualProtect(reinterpret_cast<void*>(lo), hi - lo, win_prot(prot), &old) != 0;
    }
    return ok;
}

bool phys_create(uint64_t size) {
    if (g_section) return true;
    g_section = CreateFileMappingW(INVALID_HANDLE_VALUE, nullptr, PAGE_EXECUTE_READWRITE, DWORD(size >> 32),
                                   DWORD(size), nullptr);
    if (!g_section) log("memory: cannot create %llu MiB of direct memory (error %lu); is the page file too small?",
                        size >> 20, GetLastError());
    return g_section != nullptr;
}

void* phys_map(uint64_t addr, uint64_t size, uint64_t offset, int prot, bool exact) {
    std::lock_guard lk(g_mem);
    const DWORD wp = win_prot(prot | kRead);
    if (!addr && g_pool) {
        log("memory: direct memory mapping without an address");
        return nullptr;
    }
    if (in_pool(addr, size) && (addr & 0xFFFF) == 0 && carve(addr, round_up(size), exact)) {
        void* p = pMapViewOfFile3(g_section, GetCurrentProcess(), reinterpret_cast<void*>(addr), offset,
                                  round_up(size), MEM_REPLACE_PLACEHOLDER, wp, nullptr, 0);
        if (p) {
            g_segs[addr].kind = Kind::View;
            return p;
        }
        log("memory: MapViewOfFile3 at %#llx (+%#llx, offset %#llx) failed: %lu", addr, size, offset, GetLastError());
        coalesce(g_segs.find(addr));
        return nullptr;
    }
    if (exact) return nullptr;
    return MapViewOfFileEx(g_section, FILE_MAP_ALL_ACCESS | FILE_MAP_EXECUTE, DWORD(offset >> 32), DWORD(offset),
                           size, nullptr);
}

bool write_backing(void* addr, const void* data, uint64_t size) {
    SIZE_T done = 0;
    return WriteProcessMemory(GetCurrentProcess(), addr, data, size, &done) && done == size;
}

uint64_t granularity() { return 0x10000; }

// ------------------------------------------------------------------ threads and time
uint32_t thread_id() { return GetCurrentThreadId(); }

// A high-resolution waitable timer sleeps with ~0.5 ms accuracy instead of the 1-15.6 ms
// of Sleep(); the remainder is spun.
void sleep_us(uint64_t us) {
    if (us == 0) { SwitchToThread(); return; }
    LARGE_INTEGER f, t0, t;
    QueryPerformanceFrequency(&f);
    QueryPerformanceCounter(&t0);
    const int64_t end = t0.QuadPart + int64_t(us) * f.QuadPart / 1000000;
    if (us > 600) {
        static thread_local HANDLE timer = CreateWaitableTimerExW(
            nullptr, nullptr, 0x00000002 /*CREATE_WAITABLE_TIMER_HIGH_RESOLUTION*/, TIMER_ALL_ACCESS);
        LARGE_INTEGER due;
        due.QuadPart = -int64_t(us - 500) * 10;  // 100 ns units, relative
        if (timer && SetWaitableTimer(timer, &due, 0, nullptr, nullptr, FALSE)) WaitForSingleObject(timer, INFINITE);
        else Sleep(DWORD((us - 500) / 1000));
    }
    do {
        YieldProcessor();
        QueryPerformanceCounter(&t);
    } while (t.QuadPart < end);
}

void set_thread_name(const char* name) {
    using SetDescFn = HRESULT(WINAPI*)(HANDLE, PCWSTR);
    static auto fn = reinterpret_cast<SetDescFn>(GetProcAddress(GetModuleHandleW(L"kernelbase.dll"), "SetThreadDescription"));
    if (!fn || !name) return;
    wchar_t w[64];
    MultiByteToWideChar(CP_UTF8, 0, name, -1, w, 64);
    fn(GetCurrentThread(), w);
}

// ------------------------------------------------------------------ files
static std::wstring widen(const std::string& s) {
    std::wstring w(MultiByteToWideChar(CP_UTF8, 0, s.c_str(), -1, nullptr, 0), 0);
    MultiByteToWideChar(CP_UTF8, 0, s.c_str(), -1, w.data(), int(w.size()));
    if (!w.empty()) w.pop_back();
    return w;
}

std::string exe_dir() {
    wchar_t w[MAX_PATH * 4];
    DWORD n = GetModuleFileNameW(nullptr, w, DWORD(std::size(w)));
    std::string s(WideCharToMultiByte(CP_UTF8, 0, w, int(n), nullptr, 0, nullptr, nullptr), 0);
    WideCharToMultiByte(CP_UTF8, 0, w, int(n), s.data(), int(s.size()), nullptr, nullptr);
    for (auto& c : s)
        if (c == '\\') c = '/';
    auto slash = s.find_last_of('/');
    return slash == std::string::npos ? "." : s.substr(0, slash);
}

bool is_dir(const std::string& path) {
    DWORD a = GetFileAttributesW(widen(path).c_str());
    return a != INVALID_FILE_ATTRIBUTES && (a & FILE_ATTRIBUTE_DIRECTORY);
}

void make_dirs(const std::string& path) {
    for (size_t i = 1; i <= path.size(); ++i)
        if (i == path.size() || path[i] == '/' || path[i] == '\\')
            CreateDirectoryW(widen(path.substr(0, i)).c_str(), nullptr);
}

void error_box(const std::string& text) {
    MessageBoxW(nullptr, widen(text).c_str(), L"Destiny (d1-native)", MB_OK | MB_ICONERROR);
}

// ------------------------------------------------------------------ processes
// The child joins a job object that is closed (killing it) when this process exits.
bool spawn_child(const std::string& exe, const std::string& args, const std::string& log_file) {
    static HANDLE job = [] {
        HANDLE j = CreateJobObjectW(nullptr, nullptr);
        JOBOBJECT_EXTENDED_LIMIT_INFORMATION li{};
        li.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
        SetInformationJobObject(j, JobObjectExtendedLimitInformation, &li, sizeof li);
        return j;
    }();
    SECURITY_ATTRIBUTES sa{sizeof sa, nullptr, TRUE};
    HANDLE out = CreateFileW(widen(log_file).c_str(), GENERIC_WRITE, FILE_SHARE_READ, &sa, CREATE_ALWAYS,
                             FILE_ATTRIBUTE_NORMAL, nullptr);
    STARTUPINFOW si{};
    si.cb = sizeof si;
    si.dwFlags = STARTF_USESTDHANDLES;
    si.hStdOutput = si.hStdError = out;
    si.hStdInput = GetStdHandle(STD_INPUT_HANDLE);
    std::wstring cmd = L"\"" + widen(exe) + L"\" " + widen(args);
    PROCESS_INFORMATION pi{};
    BOOL ok = CreateProcessW(nullptr, cmd.data(), nullptr, nullptr, TRUE, CREATE_NO_WINDOW | CREATE_SUSPENDED,
                             nullptr, nullptr, &si, &pi);
    if (out != INVALID_HANDLE_VALUE) CloseHandle(out);
    if (!ok) return false;
    AssignProcessToJobObject(job, pi.hProcess);
    ResumeThread(pi.hThread);
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    return true;
}

// ------------------------------------------------------------------ init
void init() {
    timeBeginPeriod(1);
    SetConsoleOutputCP(CP_UTF8);
    WSADATA wsa;
    WSAStartup(MAKEWORD(2, 2), &wsa);
    pool_init();
}

}  // namespace d1::os
