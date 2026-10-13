// The few POSIX calls MinGW's C runtime lacks, for the Windows build.
#pragma once
#ifndef NOMINMAX
#define NOMINMAX
#endif
#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <windows.h>
#include <direct.h>
#include <io.h>

#include <algorithm>
#include <cerrno>
#include <cstdint>

// Positional reads and writes through the file's Windows handle.
inline ssize_t pread(int fd, void* b, size_t n, int64_t off) {
    OVERLAPPED o{};
    o.Offset = DWORD(off);
    o.OffsetHigh = DWORD(uint64_t(off) >> 32);
    DWORD got = 0;
    if (!ReadFile(reinterpret_cast<HANDLE>(_get_osfhandle(fd)), b, DWORD(std::min<size_t>(n, 0x7FFFF000)), &got, &o)) {
        const DWORD e = GetLastError();
        if (e == ERROR_HANDLE_EOF) return 0;
        errno = e == ERROR_NOACCESS ? EFAULT : e == ERROR_INVALID_HANDLE ? EBADF : EIO;
        return -1;
    }
    return ssize_t(got);
}
inline ssize_t pwrite(int fd, const void* b, size_t n, int64_t off) {
    OVERLAPPED o{};
    o.Offset = DWORD(off);
    o.OffsetHigh = DWORD(uint64_t(off) >> 32);
    DWORD put = 0;
    if (!WriteFile(reinterpret_cast<HANDLE>(_get_osfhandle(fd)), b, DWORD(std::min<size_t>(n, 0x7FFFF000)), &put, &o)) {
        errno = EIO;
        return -1;
    }
    return ssize_t(put);
}
inline int fsync(int fd) { return _commit(fd); }
inline int mkdir(const char* p, int) { return _mkdir(p); }
