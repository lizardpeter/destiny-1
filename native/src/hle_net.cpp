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
#include <arpa/inet.h>
#include <fcntl.h>
#include <netdb.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <unistd.h>

#include <atomic>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <map>
#include <string>

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

static int32_t sceNetSocket(const char* name, int family, int type, int proto) {
    if (!net_link()) {
        log("net: socket(%s) refused: no network link (D1_NET=link to allow)", name ? name : "?");
        return net_fail(ENETDOWN);
    }
    int ht = (type == 1 || type == 10) ? SOCK_STREAM : SOCK_DGRAM;  // 6/10 = P2P variants
    int fd = socket(AF_INET, ht, 0);
    if (fd < 0) return net_fail(errno);
    log("net: socket(%s, %s) -> %d", name ? name : "?", ht == SOCK_STREAM ? "tcp" : "udp", fd);
    return fd;
}
HLE("sceNetSocket", sceNetSocket)
static int32_t sceNetSocketClose(int fd) { return close(fd) == 0 ? SCE_OK : net_fail(errno); }
HLE("sceNetSocketClose", sceNetSocketClose)
static int32_t sceNetBind(int fd, const void* a, uint32_t) {
    sockaddr_in h = to_host(a);
    return bind(fd, reinterpret_cast<sockaddr*>(&h), sizeof h) == 0 ? SCE_OK : net_fail(errno);
}
HLE("sceNetBind", sceNetBind)
static int32_t sceNetConnect(int fd, const void* a, uint32_t) {
    sockaddr_in h = to_host(a);
    char ip[32];
    inet_ntop(AF_INET, &h.sin_addr, ip, sizeof ip);
    log("net: connect(%d, %s:%u)", fd, ip, ntohs(h.sin_port));
    return connect(fd, reinterpret_cast<sockaddr*>(&h), sizeof h) == 0 ? SCE_OK : net_fail(errno);
}
HLE("sceNetConnect", sceNetConnect)
static int32_t sceNetListen(int fd, int backlog) { return listen(fd, backlog) == 0 ? SCE_OK : net_fail(errno); }
HLE("sceNetListen", sceNetListen)
static int32_t sceNetAccept(int fd, void* a, uint32_t* len) {
    sockaddr_in h{};
    socklen_t l = sizeof h;
    int r = accept(fd, reinterpret_cast<sockaddr*>(&h), &l);
    if (r < 0) return net_fail(errno);
    to_guest(h, a, len);
    return r;
}
HLE("sceNetAccept", sceNetAccept)
static int32_t sceNetSend(int fd, const void* b, uint64_t n, int flags) {
    ssize_t r = send(fd, b, n, MSG_NOSIGNAL);
    return r < 0 ? net_fail(errno) : int32_t(r);
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
            log("net: first udp send to %s:%u (%lu bytes)", ip, ntohs(h.sin_port), n);
        }
    }
    ssize_t r = sendto(fd, b, n, MSG_NOSIGNAL, a ? reinterpret_cast<sockaddr*>(&h) : nullptr, a ? sizeof h : 0);
    return r < 0 ? net_fail(errno) : int32_t(r);
}
HLE("sceNetSendto", sceNetSendto)
static int32_t sceNetSendmsg(int, const void*, int) { return net_fail(EOPNOTSUPP); }
HLE("sceNetSendmsg", sceNetSendmsg)
static int32_t sceNetRecv(int fd, void* b, uint64_t n, int flags) {
    ssize_t r = recv(fd, b, n, (flags & 0x80) ? MSG_DONTWAIT : 0);
    return r < 0 ? net_fail(errno) : int32_t(r);
}
HLE("sceNetRecv", sceNetRecv)
static int32_t sceNetRecvfrom(int fd, void* b, uint64_t n, int flags, void* a, uint32_t* len) {
    sockaddr_in h{};
    socklen_t l = sizeof h;
    ssize_t r = recvfrom(fd, b, n, (flags & 0x80) ? MSG_DONTWAIT : 0, reinterpret_cast<sockaddr*>(&h), &l);
    if (r < 0) return net_fail(errno);
    to_guest(h, a, len);
    return int32_t(r);
}
HLE("sceNetRecvfrom", sceNetRecvfrom)

static int32_t sceNetSetsockopt(int fd, int level, int opt, const void* val, uint32_t len) {
    if (level == 0xFFFF) {
        int v = (val && len >= 4) ? *static_cast<const int*>(val) : 0;
        switch (opt) {
        case 0x0004: return setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &v, 4) == 0 ? SCE_OK : net_fail(errno);
        case 0x0200: return setsockopt(fd, SOL_SOCKET, SO_REUSEPORT, &v, 4) == 0 ? SCE_OK : net_fail(errno);
        case 0x0020: return setsockopt(fd, SOL_SOCKET, SO_BROADCAST, &v, 4) == 0 ? SCE_OK : net_fail(errno);
        case 0x1001: return setsockopt(fd, SOL_SOCKET, SO_SNDBUF, &v, 4) == 0 ? SCE_OK : net_fail(errno);
        case 0x1002: return setsockopt(fd, SOL_SOCKET, SO_RCVBUF, &v, 4) == 0 ? SCE_OK : net_fail(errno);
        case 0x1200: {  // SO_NBIO
            int fl = fcntl(fd, F_GETFL);
            fcntl(fd, F_SETFL, v ? (fl | O_NONBLOCK) : (fl & ~O_NONBLOCK));
            return SCE_OK;
        }
        default: return SCE_OK;  // console-only options (P2P, crypto, policy)
        }
    }
    if (level == 6 && opt == 1) return setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, val, len) == 0 ? SCE_OK : net_fail(errno);
    return SCE_OK;
}
HLE("sceNetSetsockopt", sceNetSetsockopt)
static int32_t sceNetGetsockopt(int fd, int level, int opt, void* val, uint32_t* len) {
    if (level == 0xFFFF && opt == 0x1007) {  // SO_ERROR
        int e = 0;
        socklen_t l = sizeof e;
        getsockopt(fd, SOL_SOCKET, SO_ERROR, &e, &l);
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
    if (getsockname(fd, reinterpret_cast<sockaddr*>(&h), &l) != 0) return net_fail(errno);
    to_guest(h, a, len);
    return SCE_OK;
}
HLE("sceNetGetsockname", sceNetGetsockname)
static int32_t sceNetGetSockInfo(int, void*, int, int) { return net_fail(EOPNOTSUPP); }
HLE("sceNetGetSockInfo", sceNetGetSockInfo)

// epoll: SCE event bits IN 0x1, OUT 0x2, ERR 0x8, HUP 0x10
struct NetEpollEvent { uint32_t events, reserved; uint64_t ident; uint64_t data; };
static uint32_t ep_to_host(uint32_t e) { return (e & 1 ? EPOLLIN : 0) | (e & 2 ? EPOLLOUT : 0) | (e & 8 ? EPOLLERR : 0) | (e & 0x10 ? EPOLLHUP : 0); }
static uint32_t ep_to_guest(uint32_t e) { return (e & EPOLLIN ? 1 : 0) | (e & EPOLLOUT ? 2 : 0) | (e & EPOLLERR ? 8 : 0) | (e & EPOLLHUP ? 0x10 : 0); }
static int32_t sceNetEpollCreate(const char*, int) { int r = epoll_create1(0); return r < 0 ? net_fail(errno) : r; }
HLE("sceNetEpollCreate", sceNetEpollCreate)
static int32_t sceNetEpollDestroy(int ep) { close(ep); return SCE_OK; }
HLE("sceNetEpollDestroy", sceNetEpollDestroy)
static int32_t sceNetEpollControl(int ep, int op, int fd, NetEpollEvent* ev) {
    epoll_event h{};
    if (ev) { h.events = ep_to_host(ev->events); h.data.u64 = ev->data; }
    int hop = op == 1 ? EPOLL_CTL_ADD : op == 2 ? EPOLL_CTL_MOD : EPOLL_CTL_DEL;
    if (hop != EPOLL_CTL_DEL) h.data.u64 = (uint64_t(uint32_t(fd)) << 32) ^ (ev ? (ev->data & 0xFFFFFFFF) : 0);
    static std::mutex mu;
    static std::map<int64_t, uint64_t>* data = new std::map<int64_t, uint64_t>();
    { std::lock_guard lk(mu); if (ev) (*data)[(int64_t(ep) << 32) | uint32_t(fd)] = ev->data; }
    h.data.fd = fd;
    return epoll_ctl(ep, hop, fd, &h) == 0 ? SCE_OK : net_fail(errno);
}
HLE("sceNetEpollControl", sceNetEpollControl)
static int32_t sceNetEpollWait(int ep, NetEpollEvent* evs, int max, int timeout_us) {
    epoll_event h[64];
    int n = epoll_wait(ep, h, std::min(max, 64), timeout_us < 0 ? -1 : timeout_us / 1000);
    if (n < 0) return net_fail(errno);
    for (int i = 0; i < n; ++i) {
        evs[i] = {};
        evs[i].events = ep_to_guest(h[i].events);
        evs[i].ident = uint64_t(h[i].data.fd);
    }
    return n;
}
HLE("sceNetEpollWait", sceNetEpollWait)

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

using NpStateCallback = void (*)(int32_t user, int32_t state, void* userdata);
static NpStateCallback g_np_cb = nullptr;
static void* g_np_cb_data = nullptr;
static std::atomic<bool> g_np_cb_pending{false};
static int32_t sceNpRegisterStateCallback(NpStateCallback cb, void* ud) {
    g_np_cb = cb;
    g_np_cb_data = ud;
    g_np_cb_pending = true;
    return 1;
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
