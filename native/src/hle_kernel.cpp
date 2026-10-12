// libkernel: memory, time, files, process/module information.
#include <dirent.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>
#include <x86intrin.h>

#include <atomic>
#include <cstring>
#include <map>
#include <set>
#include <mutex>

#include "hle.h"
#include "render_bridge.h"
#include "runtime.h"

namespace d1 {

int to_ps4_errno(int e) {
    switch (e) {  // FreeBSD numbering where it differs from Linux
    case EAGAIN: return 35;
    case EDEADLK: return 11;
    case ENOSYS: return 78;
    case ETIMEDOUT: return 60;
    case ENOTSUP: return 45;
    case EINPROGRESS: return 36;
    case EALREADY: return 37;
    case ENOTEMPTY: return 66;
    case ENAMETOOLONG: return 63;
    case ELOOP: return 62;
    case EBUSY: return 16;
    default: return e;  // 1..34 match
    }
}

std::string host_path(const char* guest) {
    std::string g = guest ? guest : "";
    auto& r = rt();
    if (g.rfind("/app0", 0) == 0) return r.app0 + g.substr(5);
    for (const char* mount : {"/temp0", "/temp", "/download0", "/data", "/savedata0", "/hostapp"})
        if (g.rfind(mount, 0) == 0) {
            std::string dir = r.data_root + mount;
            mkdir(dir.c_str(), 0755);
            return dir + g.substr(strlen(mount));
        }
    return r.data_root + "/unmapped" + g;
}

// ------------------------------------------------------------------ memory
// Direct memory is backed by one sparse memfd so that two mappings of the same
// "physical" range alias, as on the console (CPU and GPU views of one buffer).
static std::mutex g_mem_mutex;
static int g_dmem_fd = -1;
static constexpr uint64_t kDirectMemSize = 0x150000000ull;  // 5.25 GiB, retail game budget
static uint64_t g_dmem_next = 0;
struct Region { uint64_t size; int prot; bool direct; uint64_t phys; char name[32]; };
static std::map<uint64_t, Region> g_regions;  // start -> region
static constexpr uint64_t kUserVaBase = 0x200000000ull;
static uint64_t g_va_next = 0x400000000ull;

static int host_prot(int p) {
    int h = 0;
    if (p & 1) h |= PROT_READ;
    if (p & 2) h |= PROT_WRITE;
    if (p & 4) h |= PROT_EXEC;
    if (p & 0x30) h |= PROT_READ | PROT_WRITE;  // GPU read/write: CPU view must stay accessible
    return h;
}

static void dmem_init() {
    if (g_dmem_fd >= 0) return;
    g_dmem_fd = memfd_create("d1-direct-memory", 0);
    ftruncate(g_dmem_fd, kDirectMemSize);
}

static uint64_t pick_va(uint64_t want, uint64_t len, uint64_t align) {
    if (want) return want;
    align = std::max<uint64_t>(align, 0x4000);
    uint64_t a = (g_va_next + align - 1) & ~(align - 1);
    g_va_next = a + ((len + 0xFFFF) & ~uint64_t(0xFFFF));
    return a;
}

static void* do_map(uint64_t want, uint64_t len, int prot, bool fixed, int fd, uint64_t off, uint64_t align) {
    uint64_t va = pick_va(want, len, align);
    int fl = (fd >= 0 ? MAP_SHARED : MAP_PRIVATE | MAP_ANONYMOUS);
    fl |= fixed ? MAP_FIXED : MAP_FIXED_NOREPLACE;
    void* p = mmap(reinterpret_cast<void*>(va), len, host_prot(prot), fl, fd, off);
    if (p == MAP_FAILED && !fixed) {  // hint taken: let the host choose
        p = mmap(nullptr, len, host_prot(prot), (fd >= 0 ? MAP_SHARED : MAP_PRIVATE | MAP_ANONYMOUS), fd, off);
    }
    return p == MAP_FAILED ? nullptr : p;
}

static uint64_t sceKernelGetDirectMemorySize() { return kDirectMemSize; }
HLE("sceKernelGetDirectMemorySize", sceKernelGetDirectMemorySize)

static int32_t sceKernelAllocateDirectMemory(int64_t start, int64_t end, uint64_t len, uint64_t align, int type,
                                             int64_t* phys) {
    std::lock_guard lk(g_mem_mutex);
    dmem_init();
    align = std::max<uint64_t>(align, 0x10000);
    uint64_t a = (std::max<uint64_t>(g_dmem_next, start) + align - 1) & ~(align - 1);
    if (a + len > kDirectMemSize || (end && a + len > uint64_t(end))) return sce_err(12);
    g_dmem_next = a + len;
    *phys = int64_t(a);
    return SCE_OK;
}
HLE("sceKernelAllocateDirectMemory", sceKernelAllocateDirectMemory)

static int32_t sceKernelReleaseDirectMemory(int64_t, uint64_t) { return SCE_OK; }
HLE("sceKernelReleaseDirectMemory", sceKernelReleaseDirectMemory)

static int32_t sceKernelMapDirectMemory(void** addr, uint64_t len, int prot, int flags, int64_t phys, uint64_t align) {
    std::lock_guard lk(g_mem_mutex);
    dmem_init();
    bool fixed = flags & 0x10;
    void* p = do_map(reinterpret_cast<uint64_t>(*addr), len, prot, fixed, g_dmem_fd, uint64_t(phys), align);
    if (!p) return sce_err(12);
    *addr = p;
    Region r{len, prot, true, uint64_t(phys), {}};
    g_regions[reinterpret_cast<uint64_t>(p)] = r;
    gpu_on_map(reinterpret_cast<uint64_t>(p), len);
    return SCE_OK;
}
HLE("sceKernelMapDirectMemory", sceKernelMapDirectMemory)

static int32_t sceKernelMapNamedDirectMemory(void** addr, uint64_t len, int prot, int flags, int64_t phys,
                                             uint64_t align, const char* name) {
    int32_t r = sceKernelMapDirectMemory(addr, len, prot, flags, phys, align);
    if (r == SCE_OK && name) {
        std::lock_guard lk(g_mem_mutex);
        std::strncpy(g_regions[reinterpret_cast<uint64_t>(*addr)].name, name, 31);
    }
    return r;
}
HLE("sceKernelMapNamedDirectMemory", sceKernelMapNamedDirectMemory)

static int32_t sceKernelMapNamedFlexibleMemory(void** addr, uint64_t len, int prot, int flags, const char* name) {
    std::lock_guard lk(g_mem_mutex);
    void* p = do_map(reinterpret_cast<uint64_t>(*addr), len, prot, flags & 0x10, -1, 0, 0x4000);
    if (!p) return sce_err(12);
    *addr = p;
    Region r{len, prot, false, 0, {}};
    if (name) std::strncpy(r.name, name, 31);
    g_regions[reinterpret_cast<uint64_t>(p)] = r;
    gpu_on_map(reinterpret_cast<uint64_t>(p), len);
    return SCE_OK;
}
HLE("sceKernelMapNamedFlexibleMemory", sceKernelMapNamedFlexibleMemory)

static int32_t sceKernelMapFlexibleMemory(void** addr, uint64_t len, int prot, int flags) {
    return sceKernelMapNamedFlexibleMemory(addr, len, prot, flags, nullptr);
}
HLE("sceKernelMapFlexibleMemory", sceKernelMapFlexibleMemory)

static int32_t sceKernelReserveVirtualRange(void** addr, uint64_t len, int flags, uint64_t align) {
    std::lock_guard lk(g_mem_mutex);
    uint64_t va = pick_va(reinterpret_cast<uint64_t>(*addr), len, align);
    void* p = mmap(reinterpret_cast<void*>(va), len, PROT_NONE,
                   MAP_PRIVATE | MAP_ANONYMOUS | MAP_NORESERVE | ((flags & 0x10) ? MAP_FIXED : MAP_FIXED_NOREPLACE), -1, 0);
    if (p == MAP_FAILED) return sce_err(12);
    *addr = p;
    return SCE_OK;
}
HLE("sceKernelReserveVirtualRange", sceKernelReserveVirtualRange)

static int32_t sceKernelMunmap(void* addr, uint64_t len) {
    gpu_on_unmap(reinterpret_cast<uint64_t>(addr), len);
    std::lock_guard lk(g_mem_mutex);
    g_regions.erase(reinterpret_cast<uint64_t>(addr));
    return munmap(addr, len) == 0 ? SCE_OK : sce_err(to_ps4_errno(errno));
}
HLE("sceKernelMunmap", sceKernelMunmap)

static int32_t sceKernelMprotect(void* addr, uint64_t len, int prot) {
    return mprotect(addr, len, host_prot(prot)) == 0 ? SCE_OK : sce_err(to_ps4_errno(errno));
}
HLE("sceKernelMprotect", sceKernelMprotect)

static int32_t sceKernelMlock(const void*, uint64_t) { return SCE_OK; }
HLE("sceKernelMlock", sceKernelMlock)

static int32_t sceKernelSetVirtualRangeName(void*, uint64_t, const char*) { return SCE_OK; }
HLE("sceKernelSetVirtualRangeName", sceKernelSetVirtualRangeName)

static const std::pair<const uint64_t, Region>* region_of(uint64_t a) {
    auto it = g_regions.upper_bound(a);
    if (it == g_regions.begin()) return nullptr;
    --it;
    return a < it->first + it->second.size ? &*it : nullptr;
}

uint64_t guest_region_extent(uint64_t addr) {
    std::lock_guard lk(g_mem_mutex);
    auto* r = region_of(addr);
    return r ? r->first + r->second.size - addr : 0;
}

static int32_t sceKernelQueryMemoryProtection(void* addr, void** start, void** end, int* prot) {
    std::lock_guard lk(g_mem_mutex);
    uint64_t a = reinterpret_cast<uint64_t>(addr);
    if (auto* r = region_of(a)) {
        if (start) *start = reinterpret_cast<void*>(r->first);
        if (end) *end = reinterpret_cast<void*>(r->first + r->second.size - 1);
        if (prot) *prot = r->second.prot;
        return SCE_OK;
    }
    for (auto& m : rt().modules)
        if (m.contains(a)) {
            if (start) *start = reinterpret_cast<void*>(m.base);
            if (end) *end = reinterpret_cast<void*>(m.base + m.size - 1);
            if (prot) *prot = 7;
            return SCE_OK;
        }
    return sce_err(22);
}
HLE("sceKernelQueryMemoryProtection", sceKernelQueryMemoryProtection)

struct VirtualQueryInfo {
    uint64_t start, end, offset;
    int32_t prot, memory_type;
    uint8_t is_flexible : 1, is_direct : 1, is_stack : 1, is_pooled : 1, is_committed : 1;
    char name[32];
};
static int32_t sceKernelVirtualQuery(const void* addr, int flags, VirtualQueryInfo* info, uint64_t infosz) {
    std::lock_guard lk(g_mem_mutex);
    uint64_t a = reinterpret_cast<uint64_t>(addr);
    auto it = g_regions.upper_bound(a);
    const std::pair<const uint64_t, Region>* r = region_of(a);
    if (!r && (flags & 1) && it != g_regions.end()) r = &*it;  // "find next"
    if (!r) return sce_err(13);
    std::memset(info, 0, std::min<uint64_t>(infosz, sizeof *info));
    info->start = r->first;
    info->end = r->first + r->second.size;
    info->offset = r->second.phys;
    info->prot = r->second.prot;
    info->is_direct = r->second.direct;
    info->is_flexible = !r->second.direct;
    info->is_committed = 1;
    std::memcpy(info->name, r->second.name, 32);
    return SCE_OK;
}
HLE("sceKernelVirtualQuery", sceKernelVirtualQuery)

// FreeBSD mmap flags -> Linux
static void* ps4_mmap(void* addr, uint64_t len, int prot, int flags, int fd, int64_t off) {
    int hf = 0;
    if (flags & 0x1) hf |= MAP_SHARED;
    if (flags & 0x2) hf |= MAP_PRIVATE;
    if (flags & 0x10) hf |= MAP_FIXED;
    if (flags & 0x1000) hf |= MAP_ANONYMOUS;
    if (!(hf & (MAP_SHARED | MAP_PRIVATE))) hf |= MAP_PRIVATE;
    void* p = mmap(addr, len, host_prot(prot), hf, (flags & 0x1000) ? -1 : fd, off);
    if (p == MAP_FAILED) errno = to_ps4_errno(errno);
    return p;
}
HLE("mmap", ps4_mmap)
static int ps4_munmap(void* a, uint64_t l) { return munmap(a, l); }
HLE("munmap", ps4_munmap)
static int ps4_msync(void* a, uint64_t l, int f) { return 0; }
HLE("msync", ps4_msync)
static int ps4_getpagesize() { return 0x4000; }
HLE("getpagesize", ps4_getpagesize)

// ------------------------------------------------------------------ time
static uint64_t g_tsc_freq = 0;
static uint64_t sceKernelGetTscFrequency() {
    if (!g_tsc_freq) {
        timespec a, b;
        clock_gettime(CLOCK_MONOTONIC, &a);
        uint64_t t0 = __rdtsc();
        timespec d{0, 50'000'000};
        nanosleep(&d, nullptr);
        uint64_t t1 = __rdtsc();
        clock_gettime(CLOCK_MONOTONIC, &b);
        double s = (b.tv_sec - a.tv_sec) + (b.tv_nsec - a.tv_nsec) * 1e-9;
        g_tsc_freq = uint64_t((t1 - t0) / s);
    }
    return g_tsc_freq;
}
HLE("sceKernelGetTscFrequency", sceKernelGetTscFrequency)
static uint64_t sceKernelReadTsc() { return __rdtsc(); }
HLE("sceKernelReadTsc", sceKernelReadTsc)

static clockid_t host_clock(int id) {
    switch (id) {  // FreeBSD clock ids
    case 0: return CLOCK_REALTIME;
    case 4: return CLOCK_MONOTONIC;
    case 11: case 13: return CLOCK_MONOTONIC;  // UPTIME_FAST / MONOTONIC_FAST
    case 12: return CLOCK_REALTIME;            // REALTIME_FAST
    case 15: return CLOCK_PROCESS_CPUTIME_ID;
    case 14: return CLOCK_THREAD_CPUTIME_ID;
    default: return CLOCK_MONOTONIC;
    }
}
static int32_t sceKernelClockGettime(int id, timespec* ts) {
    return clock_gettime(host_clock(id), ts) == 0 ? SCE_OK : sce_err(22);
}
HLE("sceKernelClockGettime", sceKernelClockGettime)
static int ps4_clock_gettime(int id, timespec* ts) { return clock_gettime(host_clock(id), ts); }
HLE("clock_gettime", ps4_clock_gettime)

static timespec g_start = [] { timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t; }();
static uint64_t sceKernelGetProcessTime() {
    timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return uint64_t((t.tv_sec - g_start.tv_sec) * 1000000ll + (t.tv_nsec - g_start.tv_nsec) / 1000);
}
HLE("sceKernelGetProcessTime", sceKernelGetProcessTime)
static int32_t sceKernelGettimeofday(timeval* tv) { gettimeofday(tv, nullptr); return SCE_OK; }
HLE("sceKernelGettimeofday", sceKernelGettimeofday)
static int ps4_gettimeofday(timeval* tv, void*) { return gettimeofday(tv, nullptr); }
HLE("gettimeofday", ps4_gettimeofday)
static int32_t sceKernelGettimezone(int32_t* tz) { if (tz) tz[0] = tz[1] = 0; return SCE_OK; }
HLE("sceKernelGettimezone", sceKernelGettimezone)
static int32_t sceKernelUsleep(uint32_t us) { usleep(us); return SCE_OK; }
HLE("sceKernelUsleep", sceKernelUsleep)
static int ps4_usleep(uint32_t us) { return usleep(us); }
HLE("usleep", ps4_usleep)
static int32_t sceKernelSleep(uint32_t s) { sleep(s); return SCE_OK; }
HLE("sceKernelSleep", sceKernelSleep)
static int ps4_nanosleep(const timespec* a, timespec* b) { return nanosleep(a, b); }
HLE("nanosleep", ps4_nanosleep)

// ------------------------------------------------------------------ files
static int host_oflags(int f) {
    int h = f & 3;  // O_RDONLY/O_WRONLY/O_RDWR
    if (f & 0x4) h |= O_NONBLOCK;
    if (f & 0x8) h |= O_APPEND;
    if (f & 0x80) h |= O_SYNC;
    if (f & 0x200) h |= O_CREAT;
    if (f & 0x400) h |= O_TRUNC;
    if (f & 0x800) h |= O_EXCL;
    if (f & 0x20000) h |= O_DIRECTORY;
    return h;
}

static bool file_log() {
    static const bool on = getenv("D1_FILE_LOG") != nullptr;
    return on;
}
// D1_FILE_LOG=2 also logs reads: the first read of each 1 MiB window of each file.
static int file_log_level() {
    static const int lv = getenv("D1_FILE_LOG") ? atoi(getenv("D1_FILE_LOG")) : 0;
    return lv;
}
static std::mutex g_fdpath_mutex;
static std::map<int, std::pair<std::string, std::set<uint64_t>>> g_fdpath;
static void note_open(int fd, const char* path) {
    if (file_log_level() < 2 || fd < 0) return;
    std::lock_guard lk(g_fdpath_mutex);
    g_fdpath[fd] = {path, {}};
}
static void note_read(int fd, int64_t off, uint64_t n) {
    if (file_log_level() < 2) return;
    std::lock_guard lk(g_fdpath_mutex);
    auto it = g_fdpath.find(fd);
    if (it == g_fdpath.end()) return;
    for (uint64_t w = uint64_t(off) >> 20; w <= (uint64_t(off) + (n ? n - 1 : 0)) >> 20; ++w)
        if (it->second.second.insert(w).second)
            log("read %s @%#lx +%#lx", it->second.first.c_str(), off, n);
}
static int32_t sceKernelOpen(const char* path, int flags, uint16_t mode) {
    std::string hp = host_path(path);
    int fd = open(hp.c_str(), host_oflags(flags), mode ? mode : 0644);
    if (file_log()) log("open %s (flags %#x) -> %d", path, flags, fd);
    note_open(fd, path);
    if (fd < 0) {
        log("sceKernelOpen(%s -> %s) failed: %s", path, hp.c_str(), strerror(errno));
        return sce_err(to_ps4_errno(errno));
    }
    return fd;
}
HLE("sceKernelOpen", sceKernelOpen)
static int32_t sceKernelClose(int fd) { return close(fd) == 0 ? SCE_OK : sce_err(to_ps4_errno(errno)); }
HLE("sceKernelClose", sceKernelClose)
// A kernel read into a page the GPU has write-protected (to notice CPU writes) fails with
// EFAULT instead of faulting. Touch the destination so the fault handler unprotects it,
// then retry.
static void touch_for_write(void* b, uint64_t n) {
    auto* p = static_cast<volatile uint8_t*>(b);
    for (uint64_t off = 0; off < n; off += 0x1000) p[off] = p[off];
    if (n) p[n - 1] = p[n - 1];
}
template <class F>
static ssize_t retry_efault(void* b, uint64_t n, F&& io) {
    ssize_t r = io();
    for (int i = 0; i < 4 && r < 0 && errno == EFAULT; ++i) {
        touch_for_write(b, n);
        r = io();
    }
    return r;
}
static int64_t sceKernelRead(int fd, void* b, uint64_t n) {
    if (file_log_level() >= 2) note_read(fd, lseek(fd, 0, SEEK_CUR), n);
    // read() can copy part of the data before it hits a protected page and then return a
    // short count, so unprotect the whole destination first.
    if (gpu_active()) touch_for_write(b, n);
    ssize_t r = retry_efault(b, n, [&] { return read(fd, b, n); });
    return r < 0 ? sce_err(to_ps4_errno(errno)) : r;
}
HLE("sceKernelRead", sceKernelRead)
static int64_t sceKernelWrite(int fd, const void* b, uint64_t n) {
    ssize_t r = write(fd, b, n);
    return r < 0 ? sce_err(to_ps4_errno(errno)) : r;
}
HLE("sceKernelWrite", sceKernelWrite)
static int64_t sceKernelPread(int fd, void* b, uint64_t n, int64_t off) {
    note_read(fd, off, n);
    if (gpu_active()) touch_for_write(b, n);
    ssize_t r = retry_efault(b, n, [&] { return pread(fd, b, n, off); });
    return r < 0 ? sce_err(to_ps4_errno(errno)) : r;
}
HLE("sceKernelPread", sceKernelPread)
static int64_t sceKernelPwrite(int fd, const void* b, uint64_t n, int64_t off) {
    ssize_t r = pwrite(fd, b, n, off);
    return r < 0 ? sce_err(to_ps4_errno(errno)) : r;
}
HLE("sceKernelPwrite", sceKernelPwrite)
static int64_t sceKernelLseek(int fd, int64_t off, int whence) {
    off_t r = lseek(fd, off, whence);
    return r < 0 ? sce_err(to_ps4_errno(errno)) : r;
}
HLE("sceKernelLseek", sceKernelLseek)
static int32_t sceKernelFsync(int fd) { fsync(fd); return SCE_OK; }
HLE("sceKernelFsync", sceKernelFsync)
static int32_t sceKernelFtruncate(int fd, int64_t l) { return ftruncate(fd, l) == 0 ? SCE_OK : sce_err(to_ps4_errno(errno)); }
HLE("sceKernelFtruncate", sceKernelFtruncate)
static int32_t sceKernelTruncate(const char* p, int64_t l) {
    return truncate(host_path(p).c_str(), l) == 0 ? SCE_OK : sce_err(to_ps4_errno(errno));
}
HLE("sceKernelTruncate", sceKernelTruncate)

// FreeBSD 9 amd64 struct stat as seen by PS4 code
struct Ps4Stat {
    uint32_t dev, ino;
    uint16_t mode, nlink;
    uint32_t uid, gid, rdev;
    timespec atim, mtim, ctim;
    int64_t size, blocks;
    uint32_t blksize, flags, gen;
    int32_t lspare;
    timespec birthtim;
};
static void fill_stat(const struct stat& s, Ps4Stat* o) {
    std::memset(o, 0, sizeof *o);
    o->dev = uint32_t(s.st_dev);
    o->ino = uint32_t(s.st_ino);
    o->mode = uint16_t(s.st_mode);
    o->nlink = uint16_t(s.st_nlink);
    o->size = s.st_size;
    o->blocks = s.st_blocks;
    o->blksize = 0x10000;
    o->atim = s.st_atim; o->mtim = s.st_mtim; o->ctim = s.st_ctim; o->birthtim = s.st_mtim;
}
static int32_t sceKernelStat(const char* p, Ps4Stat* o) {
    if (file_log()) log("stat %s", p);
    struct stat s;
    if (stat(host_path(p).c_str(), &s) != 0) return sce_err(to_ps4_errno(errno));
    fill_stat(s, o);
    return SCE_OK;
}
HLE("sceKernelStat", sceKernelStat)
static int32_t sceKernelFstat(int fd, Ps4Stat* o) {
    struct stat s;
    if (fstat(fd, &s) != 0) return sce_err(to_ps4_errno(errno));
    fill_stat(s, o);
    return SCE_OK;
}
HLE("sceKernelFstat", sceKernelFstat)
static int ps4_fstat(int fd, Ps4Stat* o) {
    struct stat s;
    if (fstat(fd, &s) != 0) return -1;
    fill_stat(s, o);
    return 0;
}
HLE("fstat", ps4_fstat)
static int32_t sceKernelMkdir(const char* p, uint16_t mode) {
    return mkdir(host_path(p).c_str(), mode ? mode : 0755) == 0 ? SCE_OK : sce_err(to_ps4_errno(errno));
}
HLE("sceKernelMkdir", sceKernelMkdir)
static int32_t sceKernelRmdir(const char* p) { return rmdir(host_path(p).c_str()) == 0 ? SCE_OK : sce_err(to_ps4_errno(errno)); }
HLE("sceKernelRmdir", sceKernelRmdir)
static int32_t sceKernelUnlink(const char* p) { return unlink(host_path(p).c_str()) == 0 ? SCE_OK : sce_err(to_ps4_errno(errno)); }
HLE("sceKernelUnlink", sceKernelUnlink)
static int32_t sceKernelRename(const char* a, const char* b) {
    return rename(host_path(a).c_str(), host_path(b).c_str()) == 0 ? SCE_OK : sce_err(to_ps4_errno(errno));
}
HLE("sceKernelRename", sceKernelRename)
static int32_t sceKernelChmod(const char* p, uint16_t m) { chmod(host_path(p).c_str(), m); return SCE_OK; }
HLE("sceKernelChmod", sceKernelChmod)
static int32_t sceKernelUtimes(const char*, const void*) { return SCE_OK; }
HLE("sceKernelUtimes", sceKernelUtimes)

// FreeBSD struct dirent: u32 fileno, u16 reclen, u8 type, u8 namlen, char name[256]
static int32_t sceKernelGetdirentries(int fd, char* buf, int nbytes, int64_t* basep) {
    static std::mutex mu;
    static std::map<int, DIR*> dirs;
    std::lock_guard lk(mu);
    DIR*& d = dirs[fd];
    if (!d) {
        d = fdopendir(dup(fd));
        if (!d) return sce_err(to_ps4_errno(errno));
    }
    int used = 0;
    while (true) {
        long pos = telldir(d);
        dirent* e = readdir(d);
        if (!e) break;
        size_t nl = strlen(e->d_name);
        uint16_t reclen = uint16_t((8 + nl + 1 + 3) & ~size_t(3));
        if (used + reclen > nbytes) { seekdir(d, pos); break; }
        char* o = buf + used;
        uint32_t ino = uint32_t(e->d_ino);
        std::memcpy(o, &ino, 4);
        std::memcpy(o + 4, &reclen, 2);
        o[6] = char(e->d_type);
        o[7] = char(nl);
        std::memcpy(o + 8, e->d_name, nl + 1);
        used += reclen;
    }
    if (basep) *basep = used;
    return used;
}
HLE("sceKernelGetdirentries", sceKernelGetdirentries)
static int32_t sceKernelGetdents(int fd, char* buf, int nbytes) { return sceKernelGetdirentries(fd, buf, nbytes, nullptr); }
HLE("sceKernelGetdents", sceKernelGetdents)

// ------------------------------------------------------------------ process / modules / misc
static int* ps4_error() { return &errno; }
HLE("__error", ps4_error)
static int ps4_getpid() { return 1; }
HLE("getpid", ps4_getpid)
static void* sceKernelGetProcParam() { return reinterpret_cast<void*>(rt().modules[0].proc_param); }
HLE("sceKernelGetProcParam", sceKernelGetProcParam)

static uint64_t g_stack_chk_guard = 0x2B992DDFA23249D6ull;
HLE_OBJ("__stack_chk_guard", g_stack_chk_guard)
static const char* g_progname = "eboot.bin";
HLE_OBJ("__progname", g_progname)

[[noreturn]] static void ps4_stack_chk_fail() {
    log("__stack_chk_fail called from guest: stack corruption");
    _exit(134);
}
HLE("__stack_chk_fail", ps4_stack_chk_fail)
[[noreturn]] static void ps4_exit(int code) {
    log("guest _exit(%d)", code);
    _exit(code);
}
HLE("_exit", ps4_exit)

static int32_t sceKernelDebugRaiseException(uint32_t code, uint32_t arg) {
    log("sceKernelDebugRaiseException(%#x, %#x)", code, arg);
    return SCE_OK;
}
HLE("sceKernelDebugRaiseException", sceKernelDebugRaiseException)
HLE("sceKernelDebugRaiseExceptionOnReleaseMode", sceKernelDebugRaiseException)

static int ps4_getrusage(int who, rusage* r) { return getrusage(who, r); }
HLE("getrusage", ps4_getrusage)

// sceKernelRtldSetApplicationHeapAPI: libc hands its allocator table to libkernel.
static void* g_heap_api = nullptr;
static int32_t rtld_set_heap_api(void* api) { g_heap_api = api; return SCE_OK; }
HLE("_sceKernelRtldSetApplicationHeapAPI", rtld_set_heap_api)

// Module information
struct ModuleSegment { uint64_t address; uint32_t size; int32_t prot; };
struct ModuleInfo {
    uint64_t size;
    char name[256];
    ModuleSegment segments[4];
    uint32_t segment_count;
    uint8_t fingerprint[20];
};
struct ModuleInfoEx {
    uint64_t size;
    char name[256];
    int32_t handle;
    uint32_t tls_index;
    uint64_t tls_init_addr;
    uint32_t tls_init_size, tls_size, tls_offset, tls_align;
    uint64_t init_proc_addr, fini_proc_addr, reserved1, reserved2;
    uint64_t eh_frame_hdr_addr, eh_frame_addr;
    uint32_t eh_frame_hdr_size, eh_frame_size;
    ModuleSegment segments[4];
    uint32_t segment_count, ref_count;
};
static void fill_info(const Module& m, ModuleInfo* o) {
    std::memset(o, 0, sizeof *o);
    o->size = sizeof *o;
    std::strncpy(o->name, m.name.c_str(), 255);
    o->segments[0] = {m.text_lo, uint32_t(m.text_hi - m.text_lo), 5};
    o->segments[1] = {m.text_hi, uint32_t(m.base + m.size - m.text_hi), 3};
    o->segment_count = 2;
}
static int32_t sceKernelGetModuleList(int32_t* handles, uint64_t num, uint64_t* actual) {
    auto& ms = rt().modules;
    uint64_t n = std::min<uint64_t>(num, ms.size());
    for (uint64_t i = 0; i < n; ++i) handles[i] = int32_t(i);
    if (actual) *actual = ms.size();
    return SCE_OK;
}
HLE("sceKernelGetModuleList", sceKernelGetModuleList)
static int32_t sceKernelGetModuleInfo(int32_t h, ModuleInfo* o) {
    if (h < 0 || size_t(h) >= rt().modules.size()) return sce_err(3);
    fill_info(rt().modules[h], o);
    return SCE_OK;
}
HLE("sceKernelGetModuleInfo", sceKernelGetModuleInfo)
static int32_t sceKernelGetModuleInfoFromAddr(uint64_t addr, int flags, ModuleInfoEx* o) {
    for (size_t i = 0; i < rt().modules.size(); ++i) {
        const Module& m = rt().modules[i];
        if (!m.contains(addr)) continue;
        std::memset(o, 0, sizeof *o);
        o->size = sizeof *o;
        std::strncpy(o->name, m.name.c_str(), 255);
        o->handle = int32_t(i);
        o->tls_index = m.tls_modid;
        o->tls_init_addr = m.tls_init;
        o->tls_init_size = uint32_t(m.tls_filesz);
        o->tls_size = uint32_t(m.tls_memsz);
        o->tls_align = uint32_t(m.tls_align);
        o->init_proc_addr = m.init;
        o->fini_proc_addr = m.fini;
        o->eh_frame_hdr_addr = m.eh_frame_hdr;
        o->segments[0] = {m.text_lo, uint32_t(m.text_hi - m.text_lo), 5};
        o->segments[1] = {m.text_hi, uint32_t(m.base + m.size - m.text_hi), 3};
        o->segment_count = 2;
        o->ref_count = 1;
        return SCE_OK;
    }
    return sce_err(3);
}
HLE("sceKernelGetModuleInfoFromAddr", sceKernelGetModuleInfoFromAddr)

}  // namespace d1
