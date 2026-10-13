// Linux implementation of os.h.
#include "os.h"

#include <fcntl.h>
#include <limits.h>
#include <pthread.h>
#include <signal.h>
#include <sys/mman.h>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#include <cerrno>
#include <cstring>

namespace d1::os {

void init() {}

static int host_prot(int p) {
    return (p & kRead ? PROT_READ : 0) | (p & kWrite ? PROT_WRITE : 0) | (p & kExec ? PROT_EXEC : 0);
}

void* alloc(uint64_t addr, uint64_t size, int prot, bool exact) {
    int fl = MAP_PRIVATE | MAP_ANONYMOUS | (exact ? MAP_FIXED : addr ? MAP_FIXED_NOREPLACE : 0);
    void* p = mmap(reinterpret_cast<void*>(addr), size, host_prot(prot), fl, -1, 0);
    if (p == MAP_FAILED && !exact && addr)
        p = mmap(nullptr, size, host_prot(prot), MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    return p == MAP_FAILED ? nullptr : p;
}

void* reserve(uint64_t addr, uint64_t size, bool exact) {
    int fl = MAP_PRIVATE | MAP_ANONYMOUS | MAP_NORESERVE | (exact ? MAP_FIXED : addr ? MAP_FIXED_NOREPLACE : 0);
    void* p = mmap(reinterpret_cast<void*>(addr), size, PROT_NONE, fl, -1, 0);
    return p == MAP_FAILED ? nullptr : p;
}

bool release(void* addr, uint64_t size) { return munmap(addr, size) == 0; }
bool protect(void* addr, uint64_t size, int prot) { return mprotect(addr, size, host_prot(prot)) == 0; }

static int g_phys_fd = -1;
bool phys_create(uint64_t size) {
    if (g_phys_fd >= 0) return true;
    g_phys_fd = memfd_create("d1-direct-memory", 0);
    return g_phys_fd >= 0 && ftruncate(g_phys_fd, off_t(size)) == 0;
}

void* phys_map(uint64_t addr, uint64_t size, uint64_t offset, int prot, bool exact) {
    int fl = MAP_SHARED | (exact ? MAP_FIXED : addr ? MAP_FIXED_NOREPLACE : 0);
    void* p = mmap(reinterpret_cast<void*>(addr), size, host_prot(prot), fl, g_phys_fd, off_t(offset));
    if (p == MAP_FAILED && !exact && addr)
        p = mmap(nullptr, size, host_prot(prot), MAP_SHARED, g_phys_fd, off_t(offset));
    return p == MAP_FAILED ? nullptr : p;
}

// /proc/self/mem ignores page protection.
bool write_backing(void* addr, const void* data, uint64_t size) {
    static int fd = open("/proc/self/mem", O_RDWR | O_CLOEXEC);
    if (fd < 0) return false;
    return pwrite(fd, data, size, reinterpret_cast<off_t>(addr)) == static_cast<ssize_t>(size);
}

uint64_t granularity() { return 0x4000; }

uint32_t thread_id() { return uint32_t(syscall(SYS_gettid)); }

void sleep_us(uint64_t us) {
    timespec ts{time_t(us / 1000000), long((us % 1000000) * 1000)};
    while (nanosleep(&ts, &ts) != 0 && errno == EINTR) {}
}

void set_thread_name(const char* name) {
    char n[16];
    std::strncpy(n, name, 15);
    n[15] = 0;
    pthread_setname_np(pthread_self(), n);
}

std::string exe_dir() {
    char b[PATH_MAX];
    ssize_t n = readlink("/proc/self/exe", b, sizeof b - 1);
    if (n <= 0) return ".";
    b[n] = 0;
    std::string s = b;
    auto slash = s.find_last_of('/');
    return slash == std::string::npos ? "." : s.substr(0, slash);
}

bool is_dir(const std::string& path) {
    struct stat s;
    return stat(path.c_str(), &s) == 0 && S_ISDIR(s.st_mode);
}

void make_dirs(const std::string& path) {
    for (size_t i = 1; i <= path.size(); ++i)
        if (i == path.size() || path[i] == '/') mkdir(path.substr(0, i).c_str(), 0755);
}

void error_box(const std::string&) {}  // the terminal shows the log

bool spawn_child(const std::string& exe, const std::string& args, const std::string& log_file) {
    pid_t pid = fork();
    if (pid < 0) return false;
    if (pid == 0) {
        prctl(PR_SET_PDEATHSIG, SIGTERM);  // the backend goes away with the game
        int fd = open(log_file.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0644);
        if (fd >= 0) { dup2(fd, 1); dup2(fd, 2); close(fd); }
        execl("/bin/sh", "sh", "-c", ("exec \"" + exe + "\" " + args).c_str(), nullptr);
        _exit(127);
    }
    return true;
}

}  // namespace d1::os
