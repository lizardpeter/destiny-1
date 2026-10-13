// libSceNet / libSceNetCtl over host sockets, and libSceNpManager / libSceNpAuth as a
// local "signed in" user.
//
// D1_NET=offline (default) reports no network link, which stops the bootflow at
// platform_signin. D1_NET=link reports a connected interface and gives the game real
// host sockets, so later sign-in stages run and show what they need.
//
// D1_BACKEND=<host or IP> names a replacement backend server (same machine for now,
// another machine later) and implies D1_NET=link. Hostnames of Bungie's, DemonWare's and
// Sony's services resolve to that server; every other name is refused. Without
// D1_BACKEND all lookups are refused. Nothing ever reaches the real services.
#include "net_compat.h"

#include <algorithm>
#include <atomic>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <map>
#include <set>
#include <string>
#include <vector>

#include "os.h"

#include "hle.h"

namespace d1 {

static bool net_link() {
    static const bool link = [] {
        const char* v = getenv("D1_NET");
        return (v && std::strcmp(v, "link") == 0) || getenv("D1_BACKEND") != nullptr;
    }();
    return link;
}

// ------------------------------------------------------------------ backend routing
static const char* const kBackendDomains[] = {
    "deadorbit.net", "gravityshavings.net", "bungie.net", "bungie.com",   // Bungie
    "demonware.net",                                                     // DemonWare (STUN)
    "playstation.net", "sonyentertainmentnetwork.com",                   // PSN auth
};

static bool is_backend_name(const std::string& host) {
    for (const char* d : kBackendDomains) {
        const size_t n = std::strlen(d);
        if (host.size() >= n && host.compare(host.size() - n, n, d) == 0 &&
            (host.size() == n || host[host.size() - n - 1] == '.'))
            return true;
    }
    return false;
}

const char* backend_host() {
    static const char* h = getenv("D1_BACKEND");
    return h && *h ? h : nullptr;
}

// IPv4 address of the D1_BACKEND server (network byte order), resolved once.
static bool backend_addr(uint32_t* out) {
    static const uint32_t addr = []() -> uint32_t {
        const char* h = backend_host();
        if (!h) return 0;
        addrinfo hints{}, *res = nullptr;
        hints.ai_family = AF_INET;
        if (getaddrinfo(h, nullptr, &hints, &res) != 0 || !res) {
            log("net: cannot resolve D1_BACKEND '%s'", h);
            return 0;
        }
        uint32_t a = reinterpret_cast<sockaddr_in*>(res->ai_addr)->sin_addr.s_addr;
        freeaddrinfo(res);
        char ip[32];
        inet_ntop(AF_INET, &a, ip, sizeof ip);
        log("net: backend server %s (%s)", h, ip);
        return a;
    }();
    if (!addr) return false;
    *out = addr;
    return true;
}

bool backend_route(const char* host, uint32_t* addr_be) {
    if (!host || !is_backend_name(host)) return false;
    return backend_addr(addr_be);
}

// ------------------------------------------------------------------ errors
static thread_local int t_net_errno = 0;
static int* sceNetErrnoLoc() { return &t_net_errno; }
HLE("sceNetErrnoLoc", sceNetErrnoLoc)
static int32_t net_fail(int linux_errno) {
    t_net_errno = to_ps4_errno(linux_errno);
    return int32_t(0x80410100u | uint32_t(t_net_errno));
}

// ------------------------------------------------------------------ init / control
static int32_t sceNetInit() { return SCE_OK; }
HLE("sceNetInit", sceNetInit)
static int32_t sceNetTerm() { return SCE_OK; }
HLE("sceNetTerm", sceNetTerm)
static int32_t sceNetPoolCreate(const char*, int, int) { static std::atomic<int> id{0}; return ++id; }
HLE("sceNetPoolCreate", sceNetPoolCreate)
static int32_t sceNetPoolDestroy(int) { return SCE_OK; }
HLE("sceNetPoolDestroy", sceNetPoolDestroy)
static int32_t sceNetCtlInit() { return SCE_OK; }
HLE("sceNetCtlInit", sceNetCtlInit)
static int32_t sceNetCtlTerm() { return SCE_OK; }
HLE("sceNetCtlTerm", sceNetCtlTerm)
static int32_t sceNetCtlGetState(int* s) { *s = net_link() ? 3 : 0; return SCE_OK; }  // 3 = IP obtained
HLE("sceNetCtlGetState", sceNetCtlGetState)
static int32_t sceNetCtlGetInfo(int code, uint8_t* info) {
    if (!net_link()) return int32_t(0x80412104);
    std::memset(info, 0, 256);
    auto str = [&](const char* s) { std::strcpy(reinterpret_cast<char*>(info), s); };
    switch (code) {
    case 1: break;                                   // device: wired
    case 2: { const uint8_t m[6] = {0x02, 0xD1, 0, 0, 0, 1}; std::memcpy(info, m, 6); break; }
    case 3: { uint32_t mtu = 1500; std::memcpy(info, &mtu, 4); break; }
    case 4: info[0] = 1; break;                      // link up
    case 11: break;                                  // ip config: DHCP
    case 14: str("10.0.2.15"); break;                // ip address
    case 15: str("255.255.255.0"); break;            // netmask
    case 16: str("10.0.2.2"); break;                 // default route
    case 17: case 18: str("10.0.2.3"); break;        // DNS
    default: break;
    }
    return SCE_OK;
}
HLE("sceNetCtlGetInfo", sceNetCtlGetInfo)
struct NatInfo { uint32_t size; int32_t stun_status, nat_type; uint32_t mapped_addr; };
static int32_t sceNetCtlGetNatInfo(NatInfo* n) {
    if (!net_link()) return int32_t(0x80412104);
    n->stun_status = 1;
    n->nat_type = 2;
    n->mapped_addr = inet_addr("10.0.2.15");
    return SCE_OK;
}
HLE("sceNetCtlGetNatInfo", sceNetCtlGetNatInfo)
static int32_t sceNetCtlGetResult(int, int* r) { if (r) *r = net_link() ? 0 : int(0x80412104); return SCE_OK; }
HLE("sceNetCtlGetResult", sceNetCtlGetResult)
static int32_t sceNetCtlRegisterCallback(void*, void*, int* id) { if (id) *id = 1; return SCE_OK; }
HLE("sceNetCtlRegisterCallback", sceNetCtlRegisterCallback)
static int32_t sceNetCtlUnregisterCallback(int) { return SCE_OK; }
HLE("sceNetCtlUnregisterCallback", sceNetCtlUnregisterCallback)
static int32_t sceNetCtlCheckCallback() { return SCE_OK; }
HLE("sceNetCtlCheckCallback", sceNetCtlCheckCallback)
static int32_t sceNetGetMacAddress(uint8_t* mac, int) {
    static const uint8_t m[6] = {0x02, 0xD1, 0x00, 0x00, 0x00, 0x01};
    std::memcpy(mac, m, 6);
    return SCE_OK;
}
HLE("sceNetGetMacAddress", sceNetGetMacAddress)

static uint16_t sceNetHtons(uint16_t v) { return htons(v); }
HLE("sceNetHtons", sceNetHtons)
static uint16_t sceNetNtohs(uint16_t v) { return ntohs(v); }
HLE("sceNetNtohs", sceNetNtohs)
static int sceNetInetPton(int af, const char* src, void* dst) { return inet_pton(af == 2 ? AF_INET : AF_INET6, src, dst); }
HLE("sceNetInetPton", sceNetInetPton)
static const char* sceNetInetNtop(int af, const void* src, char* dst, uint32_t size) {
    return inet_ntop(af == 2 ? AF_INET : AF_INET6, src, dst, size);
}
HLE("sceNetInetNtop", sceNetInetNtop)

// ------------------------------------------------------------------ sockets
// FreeBSD sockaddr_in: u8 len, u8 family, u16 port, u32 addr, u8 zero[8]
struct Ps4SockaddrIn { uint8_t len, family; uint16_t port; uint32_t addr; uint8_t zero[8]; };

static sockaddr_in to_host(const void* a) {
    sockaddr_in h{};
    auto* p = static_cast<const Ps4SockaddrIn*>(a);
    h.sin_family = AF_INET;
    h.sin_port = p->port;
    h.sin_addr.s_addr = p->addr;
    return h;
}
static void to_guest(const sockaddr_in& h, void* a, uint32_t* len) {
    if (!a) return;
    auto* p = static_cast<Ps4SockaddrIn*>(a);
    std::memset(p, 0, sizeof *p);
    p->len = sizeof *p;
    p->family = 2;
    p->port = h.sin_port;
    p->addr = h.sin_addr.s_addr;
    if (len) *len = sizeof *p;
}

// Sockets handed to the game. The game sees small descriptors in [kSockBase, kSockEnd) mapped
// to host sockets: Winsock handles are large values, and the game's own FD_SET macros write
// into 1024-bit sets on its stack (a handle such as 1528 smashed it). The range also keeps
// sockets apart from file descriptors, so `close` (shared with files) knows what it closes.
constexpr int kSockBase = 768, kSockEnd = 1024;
static std::mutex g_sock_mutex;
static std::map<int, net::sock> g_sockets;
static int g_next_sock = kSockBase;
// Guest descriptor for a new host socket (-1 if the range is exhausted).
static int adopt(net::sock s) {
    std::lock_guard lk(g_sock_mutex);
    for (int i = 0; i < kSockEnd - kSockBase; ++i) {
        const int id = kSockBase + (g_next_sock - kSockBase + i) % (kSockEnd - kSockBase);
        if (!g_sockets.count(id)) {
            g_sockets[id] = s;
            g_next_sock = id + 1;
            return id;
        }
    }
    return -1;
}
// Host socket for a guest descriptor (kInvalid if it is not one of ours).
static net::sock H(int fd) {
    std::lock_guard lk(g_sock_mutex);
    auto it = g_sockets.find(fd);
    return it == g_sockets.end() ? net::kInvalid : it->second;
}
bool net_set_nonblocking(int fd, bool on) { return net::set_nonblocking(H(fd), on); }
bool net_is_socket(int fd) {
    std::lock_guard lk(g_sock_mutex);
    return g_sockets.count(fd) != 0;
}
int net_close_socket(int fd) {
    net::sock s;
    {
        std::lock_guard lk(g_sock_mutex);
        auto it = g_sockets.find(fd);
        if (it == g_sockets.end()) return -1;
        s = it->second;
        g_sockets.erase(it);
    }
    return net::close(s);
}

static int32_t sceNetSocket(const char* name, int family, int type, int proto) {
    if (!net_link()) {
        log("net: socket(%s) refused: no network link (D1_NET=link to allow)", name ? name : "?");
        return net_fail(ENETDOWN);
    }
    int ht = (type == 1 || type == 10) ? SOCK_STREAM : SOCK_DGRAM;  // 6/10 = P2P variants
    const net::sock hs = socket(AF_INET, ht, 0);
    if (hs == net::kInvalid) return net_fail(net::error());
    const int fd = adopt(hs);
    if (fd < 0) { net::close(hs); return net_fail(EMFILE); }
    log("net: socket(%s, %s) -> %d", name ? name : "?", ht == SOCK_STREAM ? "tcp" : "udp", fd);
    return fd;
}
HLE("sceNetSocket", sceNetSocket)
static int32_t sceNetSocketClose(int fd) { return net_close_socket(fd) == 0 ? SCE_OK : net_fail(net::error()); }
HLE("sceNetSocketClose", sceNetSocketClose)
static int32_t sceNetBind(int fd, const void* a, uint32_t) {
    sockaddr_in h = to_host(a);
    return bind(H(fd), reinterpret_cast<sockaddr*>(&h), sizeof h) == 0 ? SCE_OK : net_fail(net::error());
}
HLE("sceNetBind", sceNetBind)
static int32_t sceNetConnect(int fd, const void* a, uint32_t) {
    sockaddr_in h = to_host(a);
    char ip[32];
    inet_ntop(AF_INET, &h.sin_addr, ip, sizeof ip);
    log("net: connect(%d, %s:%u)", fd, ip, ntohs(h.sin_port));
    if (connect(H(fd), reinterpret_cast<sockaddr*>(&h), sizeof h) == 0) return SCE_OK;
    int e = net::error();
    return net_fail(e == EAGAIN ? EINPROGRESS : e);  // Winsock reports a pending connect as "would block"
}
HLE("sceNetConnect", sceNetConnect)
static int32_t sceNetListen(int fd, int backlog) { return listen(H(fd), backlog) == 0 ? SCE_OK : net_fail(net::error()); }
HLE("sceNetListen", sceNetListen)
static int32_t sceNetAccept(int fd, void* a, uint32_t* len) {
    sockaddr_in h{};
    socklen_t l = sizeof h;
    const net::sock hs = accept(H(fd), reinterpret_cast<sockaddr*>(&h), &l);
    if (hs == net::kInvalid) return net_fail(net::error());
    const int r = adopt(hs);
    if (r < 0) { net::close(hs); return net_fail(EMFILE); }
    to_guest(h, a, len);
    return r;
}
HLE("sceNetAccept", sceNetAccept)
static int32_t sceNetSend(int fd, const void* b, uint64_t n, int flags) {
    auto r = send(H(fd), static_cast<const char*>(b), int(n), MSG_NOSIGNAL);
    return r < 0 ? net_fail(net::error()) : int32_t(r);
}
HLE("sceNetSend", sceNetSend)
static int32_t sceNetSendto(int fd, const void* b, uint64_t n, int flags, const void* a, uint32_t) {
    sockaddr_in h = to_host(a);
    if (a) {  // log each new UDP destination once (protocol discovery)
        static std::mutex m;
        static std::map<uint64_t, int> seen;
        std::lock_guard lk(m);
        if (seen[(uint64_t(h.sin_addr.s_addr) << 16) | h.sin_port]++ == 0) {
            char ip[32];
            inet_ntop(AF_INET, &h.sin_addr, ip, sizeof ip);
            log("net: first udp send to %s:%u (%llu bytes)", ip, ntohs(h.sin_port), (unsigned long long)n);
        }
    }
    auto r = sendto(H(fd), static_cast<const char*>(b), int(n), MSG_NOSIGNAL, a ? reinterpret_cast<sockaddr*>(&h) : nullptr,
                    a ? sizeof h : 0);
    return r < 0 ? net_fail(net::error()) : int32_t(r);
}
HLE("sceNetSendto", sceNetSendto)
// MSG_DONTWAIT (0x80): fail with EAGAIN instead of blocking (Winsock has no such flag).
static bool would_block(int fd, int flags) {
    if (!(flags & 0x80)) return false;
    pollfd p{H(fd), POLLIN, 0};
    return net::poll(&p, 1, 0) == 0;
}
static bool would_block_write(int fd, int flags) {
    if (!(flags & 0x80)) return false;
    pollfd p{H(fd), POLLOUT, 0};
    return net::poll(&p, 1, 0) == 0;
}
static int32_t sceNetRecv(int fd, void* b, uint64_t n, int flags) {
    if (would_block(fd, flags)) return net_fail(EAGAIN);
    auto r = recv(H(fd), static_cast<char*>(b), int(n), 0);
    return r < 0 ? net_fail(net::error()) : int32_t(r);
}
HLE("sceNetRecv", sceNetRecv)
static int32_t sceNetRecvfrom(int fd, void* b, uint64_t n, int flags, void* a, uint32_t* len) {
    sockaddr_in h{};
    socklen_t l = sizeof h;
    if (would_block(fd, flags)) return net_fail(EAGAIN);
    auto r = recvfrom(H(fd), static_cast<char*>(b), int(n), 0, reinterpret_cast<sockaddr*>(&h), &l);
    if (r < 0) return net_fail(net::error());
    to_guest(h, a, len);
    return int32_t(r);
}
HLE("sceNetRecvfrom", sceNetRecvfrom)

static int32_t sceNetSetsockopt(int fd, int level, int opt, const void* val, uint32_t len) {
    auto set = [&](int lvl, int o, int v) {
        return setsockopt(H(fd), lvl, o, reinterpret_cast<const char*>(&v), sizeof v) == 0 ? SCE_OK : net_fail(net::error());
    };
    if (level == 0xFFFF) {
        int v = (val && len >= 4) ? *static_cast<const int*>(val) : 0;
        switch (opt) {
        case 0x0004: return set(SOL_SOCKET, SO_REUSEADDR, v);
#ifdef SO_REUSEPORT
        case 0x0200: return set(SOL_SOCKET, SO_REUSEPORT, v);
#endif
        case 0x0020: return set(SOL_SOCKET, SO_BROADCAST, v);
        case 0x1001: return set(SOL_SOCKET, SO_SNDBUF, v);
        case 0x1002: return set(SOL_SOCKET, SO_RCVBUF, v);
        case 0x1200: net::set_nonblocking(H(fd), v); return SCE_OK;  // SO_NBIO
        default: return SCE_OK;  // console-only options (P2P, crypto, policy)
        }
    }
    if (level == 6 && opt == 1 && val && len >= 4) return set(IPPROTO_TCP, TCP_NODELAY, *static_cast<const int*>(val));
    return SCE_OK;
}
HLE("sceNetSetsockopt", sceNetSetsockopt)
static int32_t sceNetGetsockopt(int fd, int level, int opt, void* val, uint32_t* len) {
    if (level == 0xFFFF && opt == 0x1007) {  // SO_ERROR
        int e = 0;
        socklen_t l = sizeof e;
        getsockopt(H(fd), SOL_SOCKET, SO_ERROR, reinterpret_cast<char*>(&e), &l);
#if D1_WINDOWS
        WSASetLastError(e);
        e = e ? net::error() : 0;
#endif
        *static_cast<int*>(val) = to_ps4_errno(e);
        if (len) *len = 4;
        return SCE_OK;
    }
    if (val && len && *len >= 4) *static_cast<int*>(val) = 0;
    return SCE_OK;
}
HLE("sceNetGetsockopt", sceNetGetsockopt)
static int32_t sceNetGetsockname(int fd, void* a, uint32_t* len) {
    sockaddr_in h{};
    socklen_t l = sizeof h;
    if (getsockname(H(fd), reinterpret_cast<sockaddr*>(&h), &l) != 0) return net_fail(net::error());
    to_guest(h, a, len);
    return SCE_OK;
}
HLE("sceNetGetsockname", sceNetGetsockname)
static int32_t sceNetGetSockInfo(int, void*, int, int) { return net_fail(EOPNOTSUPP); }
HLE("sceNetGetSockInfo", sceNetGetSockInfo)

// epoll, implemented with poll() on both systems: an "epoll" is a set of watched sockets.
// SCE event bits: IN 0x1, OUT 0x2, ERR 0x8, HUP 0x10.
struct NetEpollEvent { uint32_t events, reserved; uint64_t ident; uint64_t data; };
struct Epoll { std::map<int, NetEpollEvent> watched; };
static std::mutex g_ep_mutex;
static std::map<int, Epoll> g_eps;
static int g_next_ep = 0x30000000;
static int32_t sceNetEpollCreate(const char*, int) {
    std::lock_guard lk(g_ep_mutex);
    int id = g_next_ep++;
    g_eps[id];
    return id;
}
HLE("sceNetEpollCreate", sceNetEpollCreate)
static int32_t sceNetEpollDestroy(int ep) {
    std::lock_guard lk(g_ep_mutex);
    g_eps.erase(ep);
    return SCE_OK;
}
HLE("sceNetEpollDestroy", sceNetEpollDestroy)
static int32_t sceNetEpollControl(int ep, int op, int fd, NetEpollEvent* ev) {
    std::lock_guard lk(g_ep_mutex);
    auto it = g_eps.find(ep);
    if (it == g_eps.end()) return net_fail(EBADF);
    if (op == 3) it->second.watched.erase(fd);  // DEL
    else if (ev) it->second.watched[fd] = *ev;
    return SCE_OK;
}
HLE("sceNetEpollControl", sceNetEpollControl)
static int32_t sceNetEpollWait(int ep, NetEpollEvent* evs, int max, int timeout_us) {
    std::vector<pollfd> fds;
    std::vector<uint64_t> data;
    std::vector<int> guest;
    {
        std::lock_guard lk(g_ep_mutex);
        auto it = g_eps.find(ep);
        if (it == g_eps.end()) return net_fail(EBADF);
        for (auto& [fd, e] : it->second.watched) {
            short want = short((e.events & 1 ? POLLIN : 0) | (e.events & 2 ? POLLOUT : 0));
            fds.push_back({H(fd), want, 0});
            data.push_back(e.data);
            guest.push_back(fd);
        }
    }
    if (fds.empty()) {
        if (timeout_us > 0) os::sleep_us(uint64_t(timeout_us));
        return 0;
    }
    int n = net::poll(fds.data(), unsigned(fds.size()), timeout_us < 0 ? -1 : (timeout_us + 999) / 1000);
    if (n < 0) return net_fail(net::error());
    int out = 0;
    for (size_t i = 0; i < fds.size() && out < max; ++i) {
        const short r = fds[i].revents;
        if (!r) continue;
        evs[out] = {};
        evs[out].events = (r & POLLIN ? 1 : 0) | (r & POLLOUT ? 2 : 0) | (r & POLLERR ? 8 : 0) | (r & POLLHUP ? 0x10 : 0);
        evs[out].ident = uint64_t(guest[i]);
        evs[out].data = data[i];
        ++out;
    }
    return out;
}
HLE("sceNetEpollWait", sceNetEpollWait)

// ------------------------------------------------------------------ POSIX sockets (libkernel)
// The BAP connection and DemonWare use these rather than sceNet*: return -1 and set errno
// (FreeBSD numbering) on failure. FreeBSD constants: SOCK_STREAM 1, SOCK_DGRAM 2;
// SOL_SOCKET 0xFFFF; MSG_DONTWAIT 0x80; F_GETFL 3, F_SETFL 4, O_NONBLOCK 4; FIONBIO 0x8004667E.
static int px_fail(int e) {
    errno = to_ps4_errno(e);
    return -1;
}
static int px_socket(int domain, int type, int proto) {
    if (!net_link()) return px_fail(ENETDOWN);
    if (domain != 2) return px_fail(EAFNOSUPPORT);
    const int t = type & 0xF;
    const net::sock hs = socket(AF_INET, t == 1 ? SOCK_STREAM : SOCK_DGRAM, 0);
    const int fd = hs == net::kInvalid ? -1 : adopt(hs);
    if (fd < 0) return px_fail(hs == net::kInvalid ? net::error() : EMFILE);
    if (type & 0x20000000) net::set_nonblocking(hs, true);  // SOCK_NONBLOCK
    log("net: socket(posix, %s) -> %d", t == 1 ? "tcp" : "udp", fd);
    return fd;
}
HLE("socket", px_socket)
static int px_bind(int fd, const void* a, uint32_t) {
    sockaddr_in h = to_host(a);
    return bind(H(fd), reinterpret_cast<sockaddr*>(&h), sizeof h) == 0 ? 0 : px_fail(net::error());
}
HLE("bind", px_bind)
static int px_connect(int fd, const void* a, uint32_t) {
    sockaddr_in h = to_host(a);
    char ip[32];
    inet_ntop(AF_INET, &h.sin_addr, ip, sizeof ip);
    log("net: connect(posix %d, %s:%u)", fd, ip, ntohs(h.sin_port));
    if (connect(H(fd), reinterpret_cast<sockaddr*>(&h), sizeof h) == 0) return 0;
    const int e = net::error();
    return px_fail(e == EAGAIN ? EINPROGRESS : e);
}
HLE("connect", px_connect)
static int px_listen(int fd, int backlog) { return listen(H(fd), backlog) == 0 ? 0 : px_fail(net::error()); }
HLE("listen", px_listen)
static int px_accept(int fd, void* a, uint32_t* len) {
    sockaddr_in h{};
    socklen_t l = sizeof h;
    const net::sock hs = accept(H(fd), reinterpret_cast<sockaddr*>(&h), &l);
    if (hs == net::kInvalid) return px_fail(net::error());
    const int r = adopt(hs);
    if (r < 0) { net::close(hs); return px_fail(EMFILE); }
    to_guest(h, a, len);
    return r;
}
HLE("accept", px_accept)
static int64_t px_send(int fd, const void* b, uint64_t n, int flags) {
    if (would_block_write(fd, flags)) return px_fail(EAGAIN);
    auto r = send(H(fd), static_cast<const char*>(b), int(n), MSG_NOSIGNAL);
    return r < 0 ? px_fail(net::error()) : int64_t(r);
}
HLE("send", px_send)
static int64_t px_sendto(int fd, const void* b, uint64_t n, int flags, const void* a, uint32_t alen) {
    if (!a) return px_send(fd, b, n, flags);
    sockaddr_in h = to_host(a);
    auto r = sendto(H(fd), static_cast<const char*>(b), int(n), MSG_NOSIGNAL, reinterpret_cast<sockaddr*>(&h), sizeof h);
    return r < 0 ? px_fail(net::error()) : int64_t(r);
}
HLE("sendto", px_sendto)
static int64_t px_recv(int fd, void* b, uint64_t n, int flags) {
    if (would_block(fd, flags)) return px_fail(EAGAIN);
    auto r = recv(H(fd), static_cast<char*>(b), int(n), 0);
    return r < 0 ? px_fail(net::error()) : int64_t(r);
}
HLE("recv", px_recv)
static int64_t px_recvfrom(int fd, void* b, uint64_t n, int flags, void* a, uint32_t* len) {
    if (would_block(fd, flags)) return px_fail(EAGAIN);
    sockaddr_in h{};
    socklen_t l = sizeof h;
    auto r = recvfrom(H(fd), static_cast<char*>(b), int(n), 0, reinterpret_cast<sockaddr*>(&h), &l);
    if (r < 0) return px_fail(net::error());
    to_guest(h, a, len);
    return int64_t(r);
}
HLE("recvfrom", px_recvfrom)
// FreeBSD struct msghdr / iovec (amd64): name, namelen, iov, iovlen, control, controllen, flags.
struct GuestIovec { uint8_t* base; uint64_t len; };
struct GuestMsghdr {
    void* name;
    uint32_t namelen, pad0;
    GuestIovec* iov;
    int32_t iovlen, pad1;
    void* control;
    uint32_t controllen;
    int32_t flags;
};
static int64_t px_sendmsg(int fd, const GuestMsghdr* m, int flags) {
    std::string buf;
    for (int i = 0; i < m->iovlen; ++i) buf.append(reinterpret_cast<const char*>(m->iov[i].base), m->iov[i].len);
    if (m->name) return px_sendto(fd, buf.data(), buf.size(), flags, m->name, m->namelen);
    return px_send(fd, buf.data(), buf.size(), flags);
}
HLE("sendmsg", px_sendmsg)
static int64_t px_recvmsg(int fd, GuestMsghdr* m, int flags) {
    uint64_t total = 0;
    for (int i = 0; i < m->iovlen; ++i) total += m->iov[i].len;
    std::string buf(total, '\0');
    uint32_t alen = m->namelen;
    const int64_t r = m->name ? px_recvfrom(fd, buf.data(), total, flags, m->name, &alen) : px_recv(fd, buf.data(), total, flags);
    if (r <= 0) return r;
    uint64_t off = 0;
    for (int i = 0; i < m->iovlen && off < uint64_t(r); ++i) {
        const uint64_t n = std::min<uint64_t>(m->iov[i].len, uint64_t(r) - off);
        std::memcpy(m->iov[i].base, buf.data() + off, n);
        off += n;
    }
    if (m->name) m->namelen = alen;
    m->controllen = 0;
    m->flags = 0;
    return r;
}
HLE("recvmsg", px_recvmsg)
// sceNet flavours (the BAP endpoint flushes with sceNetSendmsg): SCE error codes.
static int32_t sceNetSendmsg(int fd, const GuestMsghdr* m, int flags) {
    const int64_t r = px_sendmsg(fd, m, flags);
    return r < 0 ? net_fail(errno == 35 ? EAGAIN : EIO) : int32_t(r);
}
HLE("sceNetSendmsg", sceNetSendmsg)
static int32_t sceNetRecvmsg(int fd, GuestMsghdr* m, int flags) {
    const int64_t r = px_recvmsg(fd, m, flags);
    return r < 0 ? net_fail(errno == 35 ? EAGAIN : EIO) : int32_t(r);
}
HLE("sceNetRecvmsg", sceNetRecvmsg)
static int px_setsockopt(int fd, int level, int opt, const void* val, uint32_t len) {
    const int32_t r = sceNetSetsockopt(fd, level, opt, val, len);
    if (r == SCE_OK) return 0;
    errno = int(uint32_t(r) & 0xFF);
    return -1;
}
HLE("setsockopt", px_setsockopt)
static int px_getsockopt(int fd, int level, int opt, void* val, uint32_t* len) {
    sceNetGetsockopt(fd, level, opt, val, len);
    return 0;
}
HLE("getsockopt", px_getsockopt)
static int px_getsockname(int fd, void* a, uint32_t* len) {
    sockaddr_in h{};
    socklen_t l = sizeof h;
    if (getsockname(H(fd), reinterpret_cast<sockaddr*>(&h), &l) != 0) return px_fail(net::error());
    to_guest(h, a, len);
    return 0;
}
HLE("getsockname", px_getsockname)
static int px_getpeername(int fd, void* a, uint32_t* len) {
    sockaddr_in h{};
    socklen_t l = sizeof h;
    if (getpeername(H(fd), reinterpret_cast<sockaddr*>(&h), &l) != 0) return px_fail(net::error());
    to_guest(h, a, len);
    return 0;
}
HLE("getpeername", px_getpeername)
static int px_shutdown(int fd, int how) { return shutdown(H(fd), how) == 0 ? 0 : px_fail(net::error()); }
HLE("shutdown", px_shutdown)

// select(): FreeBSD fd_set is a bit array of 64-bit words; the timeout a 64-bit timeval.
static int px_select(int nfds, uint64_t* rd, uint64_t* wr, uint64_t* ex, const GuestTimeval* tv) {
    std::vector<pollfd> fds;
    std::vector<int> guest;
    auto bit = [](const uint64_t* set, int fd) { return set && (set[fd / 64] >> (fd % 64) & 1); };
    for (int fd = 0; fd < nfds; ++fd) {
        short ev = short((bit(rd, fd) ? POLLIN : 0) | (bit(wr, fd) ? POLLOUT : 0));
        if (ev || bit(ex, fd)) {
            fds.push_back({H(fd), ev, 0});
            guest.push_back(fd);
        }
    }
    const int ms = tv ? int(tv->tv_sec * 1000 + (tv->tv_usec + 999) / 1000) : -1;
    if (fds.empty()) {
        if (ms > 0) os::sleep_us(uint64_t(ms) * 1000);
        return 0;
    }
    int n = net::poll(fds.data(), unsigned(fds.size()), ms);
    if (n < 0) return px_fail(net::error());
    const size_t words = (size_t(nfds) + 63) / 64;
    if (rd) std::memset(rd, 0, words * 8);
    if (wr) std::memset(wr, 0, words * 8);
    if (ex) std::memset(ex, 0, words * 8);
    int ready = 0;
    for (size_t i = 0; i < fds.size(); ++i) {
        const pollfd& p = fds[i];
        const int fd = guest[i];
        bool any = false;
        if (rd && (p.revents & (POLLIN | POLLHUP | POLLERR))) rd[fd / 64] |= 1ull << (fd % 64), any = true;
        if (wr && (p.revents & (POLLOUT | POLLERR | POLLHUP))) wr[fd / 64] |= 1ull << (fd % 64), any = true;
        if (ex && (p.revents & POLLERR)) ex[fd / 64] |= 1ull << (fd % 64), any = true;
        ready += any;
    }
    return ready;
}
HLE("select", px_select)
// FreeBSD struct pollfd (int fd; short events; short revents); the host one holds the host
// socket (64-bit on Winsock), so convert.
struct GuestPollfd { int32_t fd; int16_t events, revents; };
static int px_poll(GuestPollfd* g, uint32_t n, int timeout_ms) {
    std::vector<pollfd> fds(n);
    for (uint32_t i = 0; i < n; ++i)
        fds[i] = {H(g[i].fd), short(g[i].events & (POLLIN | POLLOUT)), 0};
    int r = net::poll(fds.data(), n, timeout_ms);
    if (r < 0) return px_fail(net::error());
    for (uint32_t i = 0; i < n; ++i) g[i].revents = int16_t(fds[i].revents);
    return r;
}
HLE("poll", px_poll)
static int px_ioctl(int fd, uint64_t req, int* arg) {
    if (req == 0x8004667E && arg) {  // FIONBIO
        net::set_nonblocking(H(fd), *arg != 0);
        return 0;
    }
    return px_fail(ENOTTY);
}
HLE("ioctl", px_ioctl)

// ------------------------------------------------------------------ DNS: backend names only
static int32_t sceNetResolverCreate(const char*, int, int) { return 1; }
HLE("sceNetResolverCreate", sceNetResolverCreate)
static int32_t sceNetResolverDestroy(int) { return SCE_OK; }
HLE("sceNetResolverDestroy", sceNetResolverDestroy)
static int32_t sceNetResolverAbort(int, int) { return SCE_OK; }
HLE("sceNetResolverAbort", sceNetResolverAbort)
static int32_t sceNetResolverStartNtoa(int, const char* host, uint32_t* addr, int, int, int) {
    uint32_t a;
    if (backend_route(host, &a)) {
        static std::mutex m;
        static std::map<std::string, int> seen;
        std::lock_guard lk(m);
        if (seen[host]++ == 0) log("net: %s -> backend", host);
        if (addr) *addr = a;
        return SCE_OK;
    }
    static std::atomic<int> logged{0};
    if (logged++ < 20) log("net: DNS lookup of '%s' refused (not a backend name, or no D1_BACKEND)", host ? host : "?");
    return int32_t(0x804101E1);
}
HLE("sceNetResolverStartNtoa", sceNetResolverStartNtoa)

// ------------------------------------------------------------------ PSN: local signed-in user
struct NpOnlineId { char data[16]; int8_t term; int8_t dummy[3]; };
struct NpId { NpOnlineId handle; uint8_t opt[8]; uint8_t reserved[8]; };
static const char* kOnlineId = "D1NativeGuardian";

static int32_t sceNpGetState(int32_t, int32_t* state) { *state = net_link() ? 2 : 1; return SCE_OK; }
HLE("sceNpGetState", sceNpGetState)
static int32_t sceNpGetOnlineId(int32_t, NpOnlineId* id) {
    std::memset(id, 0, sizeof *id);
    std::strncpy(id->data, kOnlineId, 16);
    return SCE_OK;
}
HLE("sceNpGetOnlineId", sceNpGetOnlineId)
static int32_t sceNpGetNpId(int32_t u, NpId* id) {
    std::memset(id, 0, sizeof *id);
    return sceNpGetOnlineId(u, &id->handle);
}
HLE("sceNpGetNpId", sceNpGetNpId)
static int32_t sceNpGetAccountCountry(const NpOnlineId*, char* cc) { cc[0] = 'u'; cc[1] = 's'; cc[2] = 0; return SCE_OK; }
HLE("sceNpGetAccountCountry", sceNpGetAccountCountry)
static int32_t sceNpGetParentalControlInfo(int32_t, const NpOnlineId*, int8_t* age, uint8_t* info) {
    *age = 30;
    info[0] = info[1] = info[2] = 0;
    return SCE_OK;
}
HLE("sceNpGetParentalControlInfo", sceNpGetParentalControlInfo)
static std::atomic<int32_t> g_np_req{0x10000};
static int32_t np_create_request() { return ++g_np_req; }
HLE("sceNpCreateRequest", np_create_request)
HLE("sceNpCreateAsyncRequest", np_create_request)
HLE("sceNpAuthCreateRequest", np_create_request)
HLE("sceNpAuthCreateAsyncRequest", np_create_request)
static int32_t np_ok() { return SCE_OK; }
HLE("sceNpDeleteRequest", np_ok)
HLE("sceNpAbortRequest", np_ok)
HLE("sceNpAuthDeleteRequest", np_ok)
HLE("sceNpSetNpTitleId", np_ok)
HLE("sceNpSetContentRestriction", np_ok)
HLE("sceNpNotifyPlusFeature", np_ok)
HLE("sceNpRegisterPlusEventCallback", np_ok)
HLE("sceNpUnregisterPlusEventCallback", np_ok)
HLE("sceNpRegisterGamePresenceCallback", np_ok)
HLE("sceNpUnregisterStateCallback", np_ok)
static int32_t sceNpCheckNpAvailability(int32_t, const NpOnlineId*) {
    return net_link() ? SCE_OK : int32_t(0x80550003);  // signed out
}
HLE("sceNpCheckNpAvailability", sceNpCheckNpAvailability)
static int32_t np_poll(int32_t, int32_t* result) { if (result) *result = 0; return SCE_OK; }  // finished, success
HLE("sceNpPollAsync", np_poll)
HLE("sceNpAuthPollAsync", np_poll)
struct CheckPlusResult { bool authorized; uint8_t reserved[32]; };
static int32_t sceNpCheckPlus(int32_t, const void*, CheckPlusResult* r) { std::memset(r, 0, sizeof *r); r->authorized = true; return SCE_OK; }
HLE("sceNpCheckPlus", sceNpCheckPlus)
static int32_t sceNpGetGamePresenceStatus(const NpOnlineId*, int32_t* status) { *status = 1; return SCE_OK; }
HLE("sceNpGetGamePresenceStatus", sceNpGetGamePresenceStatus)

using NpStateCallback = D1_SYSV void (*)(int32_t user, int32_t state, void* userdata);  // game code
static NpStateCallback g_np_cb = nullptr;
static void* g_np_cb_data = nullptr;
static std::atomic<bool> g_np_cb_pending{false};
// Returns 0: the game's NP toolkit (eboot+0xFA7E10) treats anything else as failure, and its
// thread then quits before the main thread waits for it (the intermittent start-up hang).
static int32_t sceNpRegisterStateCallback(NpStateCallback cb, void* ud) {
    g_np_cb = cb;
    g_np_cb_data = ud;
    g_np_cb_pending = true;
    return SCE_OK;
}
HLE("sceNpRegisterStateCallback", sceNpRegisterStateCallback)
static int32_t sceNpCheckCallback() {
    if (g_np_cb && g_np_cb_pending.exchange(false)) g_np_cb(0x10000001, net_link() ? 2 : 1, g_np_cb_data);
    return SCE_OK;
}
HLE("sceNpCheckCallback", sceNpCheckCallback)

struct NpAuthorizationCode { char code[129]; uint8_t padding[7]; };
static int32_t sceNpAuthGetAuthorizationCode(int32_t, const void*, NpAuthorizationCode* code, int32_t* issuer) {
    log("np: authorization code requested — returning a placeholder; real Bungie/Sony servers would reject it");
    std::memset(code, 0, sizeof *code);
    std::strcpy(code->code, "D1NATIVE-PLACEHOLDER");
    if (issuer) *issuer = 1;
    return SCE_OK;
}
HLE("sceNpAuthGetAuthorizationCode", sceNpAuthGetAuthorizationCode)

}  // namespace d1
