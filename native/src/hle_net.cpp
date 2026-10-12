// libSceNet / libSceNetCtl: report "no network" honestly instead of fake success,
// and log what the game tries to reach.
#include <arpa/inet.h>

#include <cstring>

#include "hle.h"

namespace d1 {

static constexpr int32_t kNetErrBase = int32_t(0x80410100);
static int32_t net_err(int e) { return kNetErrBase | e; }

static int32_t sceNetInit() { return SCE_OK; }
HLE("sceNetInit", sceNetInit)
static int32_t sceNetPoolCreate(const char*, int, int) { static int id = 0; return ++id; }
HLE("sceNetPoolCreate", sceNetPoolCreate)
static int32_t sceNetPoolDestroy(int) { return SCE_OK; }
HLE("sceNetPoolDestroy", sceNetPoolDestroy)
static int32_t sceNetCtlInit() { return SCE_OK; }
HLE("sceNetCtlInit", sceNetCtlInit)
static int32_t sceNetCtlGetState(int* s) { *s = 0; return SCE_OK; }  // disconnected
HLE("sceNetCtlGetState", sceNetCtlGetState)
static int32_t sceNetCtlGetInfo(int code, void*) { return int32_t(0x80412104); }  // not connected
HLE("sceNetCtlGetInfo", sceNetCtlGetInfo)
static int32_t sceNetCtlGetResult(int, int* r) { if (r) *r = int(0x80412104); return SCE_OK; }
HLE("sceNetCtlGetResult", sceNetCtlGetResult)
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
static uint32_t sceNetHtonl(uint32_t v) { return htonl(v); }
HLE("sceNetHtonl", sceNetHtonl)
static uint32_t sceNetNtohl(uint32_t v) { return ntohl(v); }
HLE("sceNetNtohl", sceNetNtohl)
static int sceNetInetPton(int af, const char* src, void* dst) { return inet_pton(af == 2 ? AF_INET : AF_INET6, src, dst); }
HLE("sceNetInetPton", sceNetInetPton)

static int32_t sceNetSocket(const char* name, int family, int type, int proto) {
    log("net: socket(%s, family %d, type %d) refused: no network in the prototype", name ? name : "?", family, type);
    return net_err(50);  // ENETDOWN
}
HLE("sceNetSocket", sceNetSocket)
static int32_t sceNetSocketClose(int) { return SCE_OK; }
HLE("sceNetSocketClose", sceNetSocketClose)

static int32_t sceNetResolverCreate(const char*, int, int) { return 1; }
HLE("sceNetResolverCreate", sceNetResolverCreate)
static int32_t sceNetResolverDestroy(int) { return SCE_OK; }
HLE("sceNetResolverDestroy", sceNetResolverDestroy)
static int32_t sceNetResolverStartNtoa(int, const char* host, void*, int, int, int) {
    static int logged = 0;
    if (logged++ < 20) log("net: DNS lookup of '%s' refused: no network in the prototype", host ? host : "?");
    return int32_t(0x804101E1);  // resolver: no DNS server
}
HLE("sceNetResolverStartNtoa", sceNetResolverStartNtoa)

}  // namespace d1
