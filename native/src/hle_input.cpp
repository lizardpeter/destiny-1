// libScePad: one always-connected DualShock 4 with neutral input (host input comes later).
#include <time.h>

#include <cstdlib>
#include <cstring>

#include "hle.h"

namespace d1 {

struct PadTouch { uint16_t x, y; uint8_t id, reserve[3]; };
struct PadData {
    uint32_t buttons;
    uint8_t lx, ly, rx, ry;
    uint8_t l2, r2, pad_[2];
    float orientation[4];
    float acceleration[3];
    float angular_velocity[3];
    struct { uint8_t num, reserve[3]; uint32_t held_time; PadTouch touch[2]; } touch;
    bool connected;
    uint64_t timestamp;
    struct { uint32_t id; uint8_t reserve, len, data[10]; } ext;
    uint8_t connected_count;
    uint8_t reserve[2];
    uint8_t unique_len;
    uint8_t unique[12];
};
static_assert(sizeof(PadData) == 0x78, "ScePadData layout");

struct PadInfo {
    float pixel_density;
    uint16_t res_x, res_y;
    uint8_t dead_left, dead_right;
    uint8_t connection_type, connected_count;
    bool connected;
    int32_t device_class;
    uint8_t reserve[8];
};

static constexpr int32_t kPadHandle = 1;

// D1_AUTOPRESS=<seconds>: tap Cross (0x4000) for 100 ms every N seconds (headless testing).
static uint32_t scripted_buttons(uint64_t now_us) {
    static const char* env = getenv("D1_AUTOPRESS");
    if (!env) return 0;
    uint64_t period = uint64_t(atof(env) * 1e6);
    return period && (now_us % period) < 100000 ? 0x4000u : 0u;
}

static void fill(PadData* d) {
    std::memset(d, 0, sizeof *d);
    d->lx = d->ly = d->rx = d->ry = 0x80;
    d->orientation[3] = 1.0f;
    d->connected = true;
    d->connected_count = 1;
    timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    d->timestamp = uint64_t(ts.tv_sec) * 1000000 + ts.tv_nsec / 1000;
    d->buttons = scripted_buttons(d->timestamp);
}

static int32_t scePadInit() { return SCE_OK; }
HLE("scePadInit", scePadInit)
static int32_t scePadOpen(int32_t user, int32_t type, int32_t index, const void*) { return kPadHandle; }
HLE("scePadOpen", scePadOpen)
static int32_t scePadClose(int32_t) { return SCE_OK; }
HLE("scePadClose", scePadClose)
static int32_t scePadRead(int32_t, PadData* d, int32_t num) {
    if (num < 1) return 0;
    fill(d);
    return 1;
}
HLE("scePadRead", scePadRead)
static int32_t scePadReadState(int32_t, PadData* d) { fill(d); return SCE_OK; }
HLE("scePadReadState", scePadReadState)
static int32_t scePadGetControllerInformation(int32_t, PadInfo* i) {
    std::memset(i, 0, sizeof *i);
    i->pixel_density = 44.86f;
    i->res_x = 1920;
    i->res_y = 943;
    i->dead_left = i->dead_right = 13;
    i->connected_count = 1;
    i->connected = true;
    return SCE_OK;
}
HLE("scePadGetControllerInformation", scePadGetControllerInformation)
static int32_t scePadSetVibration(int32_t, const void*) { return SCE_OK; }
HLE("scePadSetVibration", scePadSetVibration)
static int32_t scePadSetLightBar(int32_t, const void*) { return SCE_OK; }
HLE("scePadSetLightBar", scePadSetLightBar)

}  // namespace d1
