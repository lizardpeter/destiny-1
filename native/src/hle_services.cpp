// libSceLibcInternal subset (used by libSceFios2.prx) and system/user services.
#include <atomic>
#include <cstdarg>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>

#include "hle.h"
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
static int li_vsnprintf(char* b, size_t n, const char* f, va_list ap) { return std::vsnprintf(b, n, f, ap); }
HLE("vsnprintf", li_vsnprintf)
static int li_vprintf(const char* f, va_list ap) { return std::vfprintf(stderr, f, ap); }
HLE("vprintf", li_vprintf)
static int li_printf(const char* f, ...) {
    va_list ap;
    va_start(ap, f);
    int r = std::vfprintf(stderr, f, ap);
    va_end(ap);
    return r;
}
HLE("printf", li_printf)
static int li_fflush(void*) { std::fflush(stderr); return 0; }
HLE("fflush", li_fflush)
static int64_t li_time(int64_t* t) { int64_t v = std::time(nullptr); if (t) *t = v; return v; }
HLE("time", li_time)
static struct tm* li_gmtime(const int64_t* t) { time_t v = *t; return std::gmtime(&v); }
HLE("gmtime", li_gmtime)
static int li_gmtime_s(struct tm* out, const int64_t* t) { time_t v = *t; return gmtime_r(&v, out) ? 0 : 22; }
HLE("gmtime_s", li_gmtime_s)
static struct tm* li_localtime(const int64_t* t) { time_t v = *t; return std::localtime(&v); }
HLE("localtime", li_localtime)
static int64_t li_mktime(struct tm* t) { return std::mktime(t); }
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
    std::snprintf(buf, n, "%s", "Guardian");
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
struct SystemServiceStatus { int32_t event_num; bool system_ui, overlay, cpu_mode7, bg_media; uint8_t reserved[128]; };
static int32_t sceSystemServiceGetStatus(SystemServiceStatus* s) { std::memset(s, 0, sizeof *s); return SCE_OK; }
HLE("sceSystemServiceGetStatus", sceSystemServiceGetStatus)
static int32_t sceSystemServiceHideSplashScreen() { log("sceSystemServiceHideSplashScreen: game finished its boot splash"); return SCE_OK; }
HLE("sceSystemServiceHideSplashScreen", sceSystemServiceHideSplashScreen)
static int32_t sceSystemServiceReceiveEvent(void*) { return int32_t(0x80A10003); }  // no event
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
}  // namespace d1
