// BSD sockets on Linux and Winsock on Windows behind one small interface. Socket handles
// are passed to the game as ints on both systems.
#pragma once
#include "os.h"

#if D1_WINDOWS
#ifndef NOMINMAX
#define NOMINMAX
#endif
#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <ws2tcpip.h>
#include <cerrno>
#ifndef MSG_NOSIGNAL
#define MSG_NOSIGNAL 0
#endif
using socklen_t = int;
namespace d1::net {
using sock = SOCKET;  // host socket handle
constexpr sock kInvalid = INVALID_SOCKET;
inline int close(sock s) { return closesocket(s); }
// Last socket error as a POSIX errno value.
inline int error() {
    switch (WSAGetLastError()) {
    case WSAEWOULDBLOCK: return EAGAIN;
    case WSAEINPROGRESS: return EINPROGRESS;
    case WSAEALREADY: return EALREADY;
    case WSAECONNREFUSED: return ECONNREFUSED;
    case WSAECONNRESET: return ECONNRESET;
    case WSAECONNABORTED: return ECONNABORTED;
    case WSAETIMEDOUT: return ETIMEDOUT;
    case WSAENOTCONN: return ENOTCONN;
    case WSAEISCONN: return EISCONN;
    case WSAEADDRINUSE: return EADDRINUSE;
    case WSAEADDRNOTAVAIL: return EADDRNOTAVAIL;
    case WSAENETDOWN: return ENETDOWN;
    case WSAENETUNREACH: return ENETUNREACH;
    case WSAEHOSTUNREACH: return EHOSTUNREACH;
    case WSAEMSGSIZE: return EMSGSIZE;
    case WSAENOTSOCK: return ENOTSOCK;
    case WSAEINVAL: return EINVAL;
    case WSAEINTR: return EINTR;
    default: return EIO;
    }
}
inline bool set_nonblocking(sock s, bool on) {
    u_long v = on;
    return ioctlsocket(s, FIONBIO, &v) == 0;
}
inline void set_timeouts(sock s, int seconds) {
    DWORD ms = DWORD(seconds) * 1000;
    setsockopt(s, SOL_SOCKET, SO_RCVTIMEO, reinterpret_cast<const char*>(&ms), sizeof ms);
    setsockopt(s, SOL_SOCKET, SO_SNDTIMEO, reinterpret_cast<const char*>(&ms), sizeof ms);
}
inline int poll(pollfd* fds, unsigned n, int timeout_ms) { return WSAPoll(fds, n, timeout_ms); }
}  // namespace d1::net
#else
#include <arpa/inet.h>
#include <fcntl.h>
#include <netdb.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <poll.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h>

#include <cerrno>
namespace d1::net {
using sock = int;  // host socket handle
constexpr sock kInvalid = -1;
inline int close(sock s) { return ::close(s); }
inline int error() { return errno; }
inline bool set_nonblocking(int s, bool on) {
    int fl = fcntl(s, F_GETFL);
    return fcntl(s, F_SETFL, on ? (fl | O_NONBLOCK) : (fl & ~O_NONBLOCK)) == 0;
}
inline void set_timeouts(int s, int seconds) {
    timeval tv{seconds, 0};
    setsockopt(s, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof tv);
    setsockopt(s, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof tv);
}
inline int poll(pollfd* fds, unsigned n, int timeout_ms) { return ::poll(fds, n, timeout_ms); }
}  // namespace d1::net
#endif
