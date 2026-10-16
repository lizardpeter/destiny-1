// libSceLibcInternal subset (used by libSceFios2.prx) and system/user services.
#include <atomic>
#include <cstdarg>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <string>
#include <algorithm>
#include <deque>
#include <mutex>
#include <vector>

#include "hle.h"
#include "settings.h"
#include "runtime.h"

namespace d1 {

// ------------------------------------------------------------------ libSceLibcInternal
static void* li_malloc(size_t n) { return std::malloc(n); }
HLE("malloc", li_malloc)
static void li_free(void* p) { std::free(p); }
HLE("free", li_free)
static void* li_memcpy(void* d, const void* s, size_t n) { return std::memcpy(d, s, n); }
HLE("memcpy", li_memcpy)
static void* li_memset(void* d, int c, size_t n) { return std::memset(d, c, n); }
HLE("memset", li_memset)
// printf family. The game's va_list is the System V one (a pointer to this structure),
// which the Windows C library cannot read, so arguments are pulled out here and each
// conversion is formatted on its own.
struct SysvVaList { uint32_t gp_offset, fp_offset; uint8_t* overflow; uint8_t* reg_save; };
static uint64_t va_gp(SysvVaList* ap) {
    uint64_t v;
    if (ap->gp_offset < 48) { std::memcpy(&v, ap->reg_save + ap->gp_offset, 8); ap->gp_offset += 8; }
    else { std::memcpy(&v, ap->overflow, 8); ap->overflow += 8; }
    return v;
}
static double va_fp(SysvVaList* ap) {
    double v;
    if (ap->fp_offset < 176) { std::memcpy(&v, ap->reg_save + ap->fp_offset, 8); ap->fp_offset += 16; }
    else { std::memcpy(&v, ap->overflow, 8); ap->overflow += 8; }
    return v;
}
static std::string format_sysv(const char* f, SysvVaList* ap) {
    std::string out;
    char tmp[512];
    while (*f) {
        if (*f != '%') { out += *f++; continue; }
        if (f[1] == '%') { out += '%'; f += 2; continue; }
        std::string spec = "%";
        ++f;
        while (*f && std::strchr("-+ #0", *f)) spec += *f++;
        auto number = [&] {
            if (*f == '*') { spec += std::to_string(int(va_gp(ap))); ++f; }
            else while (*f >= '0' && *f <= '9') spec += *f++;
        };
        number();
        if (*f == '.') { spec += *f++; number(); }
        int len = 0;  // 0 int, 1 64-bit, -1 short/char
        while (*f && std::strchr("hlLqjzt", *f)) {
            if (*f == 'h') len = -1; else len = 1;
            ++f;
        }
        const char c = *f ? *f++ : 0;
        if (!c) break;
        if (std::strchr("diouxXc", c)) {
            const uint64_t v = va_gp(ap);
            if (c == 'c') { spec += 'c'; std::snprintf(tmp, sizeof tmp, spec.c_str(), int(v)); }
            else if (len == 1) { spec += "ll"; spec += c; std::snprintf(tmp, sizeof tmp, spec.c_str(), (long long)v); }
            else { spec += c; std::snprintf(tmp, sizeof tmp, spec.c_str(), int(v)); }
        } else if (std::strchr("eEfFgGaA", c)) {
            spec += c;
            std::snprintf(tmp, sizeof tmp, spec.c_str(), va_fp(ap));
        } else if (c == 's') {
            const char* str = reinterpret_cast<const char*>(va_gp(ap));
            spec += 's';
            std::snprintf(tmp, sizeof tmp, spec.c_str(), str ? str : "(null)");
        } else if (c == 'p') {
            std::snprintf(tmp, sizeof tmp, "0x%llx", (unsigned long long)va_gp(ap));
        } else if (c == 'n') {
            va_gp(ap);
            tmp[0] = 0;
        } else {
            tmp[0] = 0;
        }
        out += tmp;
    }
    return out;
}
static int li_vsnprintf(char* b, size_t n, const char* f, SysvVaList* ap) {
    std::string s = format_sysv(f, ap);
    if (n) {
        size_t k = std::min(n - 1, s.size());
        std::memcpy(b, s.data(), k);
        b[k] = 0;
    }
    return int(s.size());
}
HLE("vsnprintf", li_vsnprintf)
static int li_vprintf(const char* f, SysvVaList* ap) {
    std::string s = format_sysv(f, ap);
    std::fputs(s.c_str(), stderr);
    return int(s.size());
}
HLE("vprintf", li_vprintf)
// Variadic: declared with every register a System V caller can use, then read as a va_list.
static D1_SYSV int li_printf(const char* f, uint64_t a1, uint64_t a2, uint64_t a3, uint64_t a4, uint64_t a5,
                             double x0, double x1, double x2, double x3, double x4, double x5, double x6, double x7) {
    uint64_t save[22] = {reinterpret_cast<uint64_t>(f), a1, a2, a3, a4, a5};
    const double xs[8] = {x0, x1, x2, x3, x4, x5, x6, x7};
    for (int i = 0; i < 8; ++i) std::memcpy(&save[6 + 2 * i], &xs[i], 8);
    SysvVaList ap{8, 48, static_cast<uint8_t*>(__builtin_frame_address(0)) + 16, reinterpret_cast<uint8_t*>(save)};
    return li_vprintf(f, &ap);
}
HLE_SYSV("printf", li_printf)
static int li_fflush(void*) { std::fflush(stderr); return 0; }
HLE("fflush", li_fflush)
static int64_t li_time(int64_t* t) { int64_t v = std::time(nullptr); if (t) *t = v; return v; }
HLE("time", li_time)
// FreeBSD struct tm: nine ints, then tm_gmtoff (long) and tm_zone (char*).
struct GuestTm { int32_t sec, min, hour, mday, mon, year, wday, yday, isdst, pad; int64_t gmtoff; const char* zone; };
static void to_guest_tm(const struct tm& h, GuestTm* g) {
    *g = {h.tm_sec, h.tm_min, h.tm_hour, h.tm_mday, h.tm_mon, h.tm_year, h.tm_wday, h.tm_yday, h.tm_isdst, 0, 0, "UTC"};
}
static struct tm from_guest_tm(const GuestTm* g) {
    struct tm h{};
    h.tm_sec = g->sec; h.tm_min = g->min; h.tm_hour = g->hour; h.tm_mday = g->mday; h.tm_mon = g->mon;
    h.tm_year = g->year; h.tm_wday = g->wday; h.tm_yday = g->yday; h.tm_isdst = g->isdst;
    return h;
}
static thread_local GuestTm t_tm;
static int li_gmtime_s(GuestTm* out, const int64_t* t) {
    time_t v = time_t(*t);
    struct tm h;
#if D1_WINDOWS
    if (gmtime_s(&h, &v) != 0) return 22;
#else
    if (!gmtime_r(&v, &h)) return 22;
#endif
    to_guest_tm(h, out);
    return 0;
}
HLE("gmtime_s", li_gmtime_s)
static GuestTm* li_gmtime(const int64_t* t) { return li_gmtime_s(&t_tm, t) == 0 ? &t_tm : nullptr; }
HLE("gmtime", li_gmtime)
static GuestTm* li_localtime(const int64_t* t) {
    time_t v = time_t(*t);
    struct tm h;
#if D1_WINDOWS
    if (localtime_s(&h, &v) != 0) return nullptr;
#else
    if (!localtime_r(&v, &h)) return nullptr;
#endif
    to_guest_tm(h, &t_tm);
    return &t_tm;
}
HLE("localtime", li_localtime)
static int64_t li_mktime(GuestTm* t) {
    struct tm h = from_guest_tm(t);
    int64_t r = std::mktime(&h);
    to_guest_tm(h, t);
    return r;
}
HLE("mktime", li_mktime)
static void li_cxa_finalize(void*) {}
HLE("__cxa_finalize", li_cxa_finalize)
static void* g_stdout_obj[32] = {};
HLE_OBJ("_Stdout", g_stdout_obj)
static int g_need_libc_internal = 1;
HLE_OBJ("Need_sceLibcInternal", g_need_libc_internal)

// ------------------------------------------------------------------ libSceSysmodule
static int32_t sceSysmoduleLoadModule(uint16_t id) { log("sceSysmoduleLoadModule(%#x)", id); return SCE_OK; }
HLE("sceSysmoduleLoadModule", sceSysmoduleLoadModule)
static int32_t sceSysmoduleUnloadModule(uint16_t) { return SCE_OK; }
HLE("sceSysmoduleUnloadModule", sceSysmoduleUnloadModule)
static int32_t sceSysmoduleIsLoaded(uint16_t) { return SCE_OK; }
HLE("sceSysmoduleIsLoaded", sceSysmoduleIsLoaded)

// ------------------------------------------------------------------ libSceUserService
static constexpr int32_t kUser = 0x10000001;
static int32_t sceUserServiceInitialize(void*) { return SCE_OK; }
HLE("sceUserServiceInitialize", sceUserServiceInitialize)
static int32_t sceUserServiceTerminate() { return SCE_OK; }
HLE("sceUserServiceTerminate", sceUserServiceTerminate)
static int32_t sceUserServiceGetInitialUser(int32_t* u) { *u = kUser; return SCE_OK; }
HLE("sceUserServiceGetInitialUser", sceUserServiceGetInitialUser)
static int32_t sceUserServiceGetLoginUserIdList(int32_t* l) {
    l[0] = kUser; l[1] = l[2] = l[3] = -1;
    return SCE_OK;
}
HLE("sceUserServiceGetLoginUserIdList", sceUserServiceGetLoginUserIdList)
static int32_t sceUserServiceGetUserName(int32_t, char* buf, size_t n) {
    std::snprintf(buf, n, "%s", settings().name.c_str());
    return SCE_OK;
}
HLE("sceUserServiceGetUserName", sceUserServiceGetUserName)

// ------------------------------------------------------------------ libSceSystemService
static int32_t sceSystemServiceParamGetInt(int id, int32_t* v) {
    switch (id) {
    case 1: *v = 1; break;      // language: English (US)
    case 2: *v = 2; break;      // date format: MM/DD/YYYY
    case 3: *v = 0; break;      // time format: 12h
    case 4: *v = -300; break;   // time zone (minutes from UTC)
    case 5: *v = 1; break;      // summer time
    case 1000: *v = 9; break;   // game parental level
    case 1001: *v = 1; break;   // enter button: cross
    default: *v = 0; break;
    }
    return SCE_OK;
}
HLE("sceSystemServiceParamGetInt", sceSystemServiceParamGetInt)
// System events (what the PS4 system software tells the game, e.g. 0x10000002 session
// invitation: the player chose "Join" on a friend or accepted an invitation). Queued by
// push_system_event; the game polls sceSystemServiceGetStatus().event_num, then receives them.
struct SystemServiceEvent { int32_t type; uint8_t data[8192]; };
static std::mutex g_event_mutex;
static std::deque<std::pair<int32_t, std::vector<uint8_t>>> g_events;
void push_system_event(int32_t type, const void* data, size_t size) {
    std::lock_guard lk(g_event_mutex);
    const auto* p = static_cast<const uint8_t*>(data);
    g_events.emplace_back(type, std::vector<uint8_t>(p, p + std::min<size_t>(size, 8192)));
    log("system service: event %#x queued (%zu bytes)", type, size);
}
struct SystemServiceStatus { int32_t event_num; bool system_ui, overlay, cpu_mode7, bg_media; uint8_t reserved[128]; };
static int32_t sceSystemServiceGetStatus(SystemServiceStatus* s) {
    std::memset(s, 0, sizeof *s);
    std::lock_guard lk(g_event_mutex);
    s->event_num = int32_t(g_events.size());
    return SCE_OK;
}
HLE("sceSystemServiceGetStatus", sceSystemServiceGetStatus)
static int32_t sceSystemServiceHideSplashScreen() { log("sceSystemServiceHideSplashScreen: game finished its boot splash"); return SCE_OK; }
HLE("sceSystemServiceHideSplashScreen", sceSystemServiceHideSplashScreen)
static int32_t sceSystemServiceReceiveEvent(SystemServiceEvent* e) {
    std::lock_guard lk(g_event_mutex);
    if (g_events.empty() || !e) return int32_t(0x80A10003);  // no event
    std::memset(e, 0, sizeof *e);
    e->type = g_events.front().first;
    std::memcpy(e->data, g_events.front().second.data(), g_events.front().second.size());
    g_events.pop_front();
    log("system service: event %#x delivered", e->type);
    return SCE_OK;
}
HLE("sceSystemServiceReceiveEvent", sceSystemServiceReceiveEvent)

}  // namespace d1

// ------------------------------------------------------------------ message dialogs
// libSceMsgDialog: the message is logged; user messages are answered at once with the
// first button, progress bars stay open until the game closes them.
namespace d1 {
struct MsgDialogResult { uint32_t mode; int32_t result; uint32_t button_id; uint8_t reserved[32]; };
static std::atomic<int32_t> g_msg_status{0};  // 0 none, 1 initialized, 2 running, 3 finished
static uint32_t g_msg_mode = 0;
static int32_t sceMsgDialogInitialize() { g_msg_status = 1; return SCE_OK; }
HLE("sceMsgDialogInitialize", sceMsgDialogInitialize)
static int32_t sceMsgDialogOpen(const uint8_t* param) {
    if (!param) return int32_t(0x80B80006);
    g_msg_mode = *reinterpret_cast<const uint32_t*>(param + 56);
    const char* text = nullptr;
    if (g_msg_mode == 1) {
        if (auto* user = *reinterpret_cast<const uint8_t* const*>(param + 64)) text = *reinterpret_cast<const char* const*>(user + 8);
    } else if (g_msg_mode == 2) {
        if (auto* bar = *reinterpret_cast<const uint8_t* const*>(param + 72)) text = *reinterpret_cast<const char* const*>(bar + 8);
    } else if (g_msg_mode == 3) {
        if (auto* sys = *reinterpret_cast<const uint8_t* const*>(param + 80))
            log("message dialog (system message %u)", *reinterpret_cast<const uint32_t*>(sys));
    }
    if (text) log("message dialog (mode %u): %s", g_msg_mode, text);
    g_msg_status = g_msg_mode == 2 ? 2 : 3;
    return SCE_OK;
}
HLE("sceMsgDialogOpen", sceMsgDialogOpen)
static int32_t sceMsgDialogUpdateStatus() { return g_msg_status; }
HLE("sceMsgDialogUpdateStatus", sceMsgDialogUpdateStatus)
static int32_t sceMsgDialogGetStatus() { return g_msg_status; }
HLE("sceMsgDialogGetStatus", sceMsgDialogGetStatus)
static int32_t sceMsgDialogGetResult(MsgDialogResult* r) {
    if (r) { std::memset(r, 0, sizeof *r); r->mode = g_msg_mode; r->result = 0; r->button_id = 1; }
    return SCE_OK;
}
HLE("sceMsgDialogGetResult", sceMsgDialogGetResult)
static int32_t sceMsgDialogClose() { g_msg_status = 3; return SCE_OK; }
HLE("sceMsgDialogClose", sceMsgDialogClose)
static int32_t sceMsgDialogTerminate() { g_msg_status = 0; return SCE_OK; }
HLE("sceMsgDialogTerminate", sceMsgDialogTerminate)
static int32_t sceMsgDialogProgressBarSetValue(int32_t, uint32_t) { return SCE_OK; }
HLE("sceMsgDialogProgressBarSetValue", sceMsgDialogProgressBarSetValue)
static int32_t sceMsgDialogProgressBarSetMsg(int32_t, const char* m) { if (m) log("message dialog progress: %s", m); return SCE_OK; }
HLE("sceMsgDialogProgressBarSetMsg", sceMsgDialogProgressBarSetMsg)

// ------------------------------------------------------------------ libSceAppContent / PlayGo / DiscMap
// These write results through pointers. Left as logging stubs they returned "OK" without
// writing, and the game used stack garbage: GetAddcontInfoList's count once came back as
// ~860 million add-ons, a 19 GB allocation and an ENGINE OOM halt in content_check.
static int32_t sceAppContentInitialize(const void*, void*) { return SCE_OK; }
HLE("sceAppContentInitialize", sceAppContentInitialize)
// No add-on content installed for now (the expansions live in the main packages list).
static int32_t sceAppContentGetAddcontInfoList(uint32_t, void* list, uint32_t num, uint32_t* hit) {
    (void)list;
    (void)num;
    if (hit) *hit = 0;
    return SCE_OK;
}
HLE("sceAppContentGetAddcontInfoList", sceAppContentGetAddcontInfoList)
// Param 0 is the SKU flag: 1 = trial, 3 = full game. The game reads anything but 3 as the
// trial (0x296990): "TRIAL MODE" banner, Earth only, no "full sku" offer 0xE0000001.
// Params 1-4 are the title's USER_DEFINED_PARAM values (0 for this title).
static int32_t sceAppContentAppParamGetInt(uint32_t id, int32_t* value) {
    if (value) *value = id == 0 ? 3 : 0;
    return SCE_OK;
}
HLE("sceAppContentAppParamGetInt", sceAppContentAppParamGetInt)
static int32_t sceAppContentDownloadDataGetAvailableSpaceKb(const char*, uint64_t* kb) {
    if (kb) *kb = 64ull << 20;  // 64 GiB
    return SCE_OK;
}
HLE("sceAppContentDownloadDataGetAvailableSpaceKb", sceAppContentDownloadDataGetAvailableSpaceKb)
HLE("sceAppContentTemporaryDataGetAvailableSpaceKb", sceAppContentDownloadDataGetAvailableSpaceKb)
// The temporary-data mount is the /temp0 tree in the data folder (SceAppContentMountPoint: 16 chars).
static int32_t sceAppContentTemporaryDataMount(char* mount_point) {
    if (mount_point) std::strcpy(mount_point, "/temp0");
    return SCE_OK;
}
HLE("sceAppContentTemporaryDataMount", sceAppContentTemporaryDataMount)
static int32_t sceAppContentTemporaryDataMount2(uint32_t, char* mount_point) { return sceAppContentTemporaryDataMount(mount_point); }
HLE("sceAppContentTemporaryDataMount2", sceAppContentTemporaryDataMount2)
static int32_t sceAppContentTemporaryDataUnmount(const char*) { return SCE_OK; }
HLE("sceAppContentTemporaryDataUnmount", sceAppContentTemporaryDataUnmount)

// PlayGo (streaming install): everything is installed, nothing left to do.
static int32_t scePlayGoInitialize(const void*) { return SCE_OK; }
HLE("scePlayGoInitialize", scePlayGoInitialize)
static int32_t scePlayGoOpen(int32_t* handle, const void*) { if (handle) *handle = 1; return SCE_OK; }
HLE("scePlayGoOpen", scePlayGoOpen)
static int32_t scePlayGoClose(int32_t) { return SCE_OK; }
HLE("scePlayGoClose", scePlayGoClose)
static int32_t scePlayGoSetLanguageMask(int32_t, uint64_t) { return SCE_OK; }
HLE("scePlayGoSetLanguageMask", scePlayGoSetLanguageMask)
static int32_t scePlayGoGetToDoList(int32_t, void*, uint32_t, uint32_t* entries) {
    if (entries) *entries = 0;
    return SCE_OK;
}
HLE("scePlayGoGetToDoList", scePlayGoGetToDoList)

// Disc map: no disc layout information; the caller reads from the installed files.
static int32_t sceDiscMapIsRequestOnHDD(const char*, uint64_t, uint64_t, int32_t* on_hdd) {
    if (on_hdd) *on_hdd = 1;
    return SCE_OK;
}
HLE("sceDiscMapIsRequestOnHDD", sceDiscMapIsRequestOnHDD)

}  // namespace d1
