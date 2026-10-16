// libScePad: one always-connected DualShock 4. Input comes from the renderer's window
// (keyboard / controller) when there is one, plus D1_AUTOPRESS for headless tests.
#include <time.h>

#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "hle.h"
#include "render_bridge.h"

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

// D1_AUTOPRESS=<seconds>[:<buttons>]: hold a button for a third of every N-second period
// (headless testing; long enough to be seen at the low frame rates of software rendering).
// Buttons cycle through the letters given (x Cross, o Circle, t Triangle, s Square, p touch
// pad); the
// default is Cross only.
static uint32_t scripted_buttons(uint64_t now_us) {
    static const char* env = getenv("D1_AUTOPRESS");
    if (!env) return 0;
    // D1_AUTOPRESS_UNTIL=<state prefix>: stop pressing once the game reaches that state
    static const char* until = getenv("D1_AUTOPRESS_UNTIL");
    static bool stopped = false;
    if (until && !stopped)
        if (const char* gs = game_state(); gs && std::strncmp(gs, until, std::strlen(until)) == 0) stopped = true;
    if (stopped) return 0;
    const uint64_t period = uint64_t(atof(env) * 1e6);
    if (!period || (now_us % period) >= period / 3) return 0;
    const char* seq = strchr(env, ':');
    seq = seq && seq[1] ? seq + 1 : "x";
    const char c = seq[(now_us / period) % strlen(seq)];
    switch (c) {
        case 'o': return 0x2000u;
        case 't': return 0x1000u;
        case 's': return 0x8000u;
        case 'p': return 0x100000u;  // touch pad (the director)
        default: return 0x4000u;
    }
}

// D1_STATE_PRESS=<state>:<letter>@<secs>,<letter>@<secs>,... (headless testing): once
// the game reaches that state, press each button (letters as for D1_AUTOPRESS) for half a
// second at the given time, once. E.g. setup:orbit:o@5,p@10 dismisses a screen in orbit, then
// opens the director.
static uint32_t state_buttons(uint64_t now_us) {
    static const char* env = getenv("D1_STATE_PRESS");
    if (!env) return 0;
    static std::string prefix;
    static std::vector<std::pair<char, uint64_t>> presses;
    static bool parsed = false;
    static uint64_t since = 0;
    if (!parsed) {
        parsed = true;
        const std::string spec = env;
        const size_t colon = spec.rfind(':', spec.find('@'));
        prefix = spec.substr(0, colon);
        std::string rest = spec.substr(colon + 1);
        size_t pos = 0;
        while (pos < rest.size()) {
            size_t comma = rest.find(',', pos);
            const std::string item = rest.substr(pos, comma == std::string::npos ? std::string::npos : comma - pos);
            if (item.size() > 2 && item[1] == '@') presses.push_back({item[0], uint64_t(atof(item.c_str() + 2) * 1e6)});
            if (comma == std::string::npos) break;
            pos = comma + 1;
        }
    }
    if (!since) {
        if (const char* gs = game_state(); gs && prefix == gs) since = now_us;  // exact: setup:orbit is not setup:orbit_loading
        return 0;
    }
    uint32_t b = 0;
    for (auto& [c, at] : presses)
        if (now_us - since >= at && now_us - since < at + 500000)
            b |= c == 'o' ? 0x2000u : c == 't' ? 0x1000u : c == 's' ? 0x8000u : c == 'p' ? 0x100000u : 0x4000u;
    return b;
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
    d->buttons = scripted_buttons(d->timestamp) | state_buttons(d->timestamp);
    render::PadState p;
    if (render::read_pad(p)) {  // window input (renderer build)
        d->buttons |= p.buttons;
        d->lx = p.lx, d->ly = p.ly, d->rx = p.rx, d->ry = p.ry;
        d->l2 = p.l2, d->r2 = p.r2;
    }
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
