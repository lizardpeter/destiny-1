// SDL2 window, event loop, input and audio for builds with the native renderer (no
// shadPS4). Controls are PC key bindings (Destiny 2 defaults, bind_* in d1-native.cfg; the
// table is kActions below) turned into the DualShock 4 input the game reads, plus raw
// mouse look fed straight into the game's aim (hooks.cpp) and direct weapon selection.
// Clicking in the window captures the mouse; F2 or losing focus releases it. F11 or
// Alt+Enter toggles borderless fullscreen. Controllers use SDL's game-controller mapping.
#include <SDL.h>
#include <SDL_syswm.h>

#include <algorithm>
#include <atomic>
#include <cstdlib>
#include <mutex>
#include <cctype>
#include <cstring>
#include <string>
#include <vector>

#include "frontend.h"
#include "settings.h"
#include "render_bridge.h"
#include "../gfx/nrender.h"

namespace d1 {
void log(const char* fmt, ...);
void hooks_request_launch();
void hooks_request_join();
}

namespace d1::render {

namespace {
enum : uint32_t {
    kL3 = 0x2, kR3 = 0x4, kOptions = 0x8, kUp = 0x10, kRight = 0x20, kDown = 0x40, kLeft = 0x80,
    kL2 = 0x100, kR2 = 0x200, kL1 = 0x400, kR1 = 0x800, kTriangle = 0x1000, kCircle = 0x2000,
    kCross = 0x4000, kSquare = 0x8000, kTouchPad = 0x100000,
};

SDL_Window* g_window = nullptr;
std::atomic<uint32_t> g_w{0}, g_h{0};
std::mutex g_title_m;
std::string g_status;
bool g_status_dirty = false;
SDL_GameController* g_pad = nullptr;
std::mutex g_pad_mutex;
PadState g_state{0, 0x80, 0x80, 0x80, 0x80, 0, 0};
// Mouse: motion is accumulated by the event loop (1 ms cadence) and drained by the game's
// aim hook, so a count reaches the game at most ~1 ms after SDL sees it.
std::atomic<bool> g_captured{false};
std::atomic<int32_t> g_mouse_dx{0}, g_mouse_dy{0};

void set_capture(bool on) {
    if (on == g_captured.load()) return;
    SDL_SetRelativeMouseMode(on ? SDL_TRUE : SDL_FALSE);
    g_mouse_dx = 0, g_mouse_dy = 0;
    g_captured = on;
    d1::log("input: mouse %s", on ? "captured (F2 releases)" : "released");
}

uint8_t axis(int v) {  // SDL -32768..32767 -> 0..255
    return uint8_t((v + 32768) >> 8);
}

void update_drawable_size() {
    int w = 0, h = 0;
    SDL_GetWindowSizeInPixels(g_window, &w, &h);
    if (SDL_GetWindowFlags(g_window) & SDL_WINDOW_MINIMIZED) w = h = 0;
    g_w = uint32_t(std::max(w, 0)), g_h = uint32_t(std::max(h, 0));
}

// ---- key bindings (PC defaults as in Destiny 2; bind_<action> lines in d1-native.cfg)
// Each action turns into the DualShock 4 input the game reads: a held button, a short tap
// (reload is Square tapped, interact Square held), a stick direction, or a direct weapon
// selection (weapon_1..3, see select_weapon in hooks.cpp).
enum class Kind { hold, tap, stick, weapon };
enum Stick { kLeftX, kLeftY };
struct Action {
    const char* name;
    const char* defaults;
    Kind kind;
    uint32_t buttons;  // hold / tap: button bits; stick: axis (kLeftX / kLeftY) and sign; weapon: index
    int sign;
};
constexpr Action kActions[] = {
    {"move_forward", "W", Kind::stick, kLeftY, -1},
    {"move_back", "S", Kind::stick, kLeftY, +1},
    {"move_left", "A", Kind::stick, kLeftX, -1},
    {"move_right", "D", Kind::stick, kLeftX, +1},
    {"jump", "Space", Kind::hold, kCross, 0},
    {"crouch", "Left Ctrl", Kind::hold, kCircle, 0},
    {"sprint", "Left Shift", Kind::hold, kL3, 0},
    {"fire", "Mouse1", Kind::hold, kR2, 0},
    {"aim", "Mouse2", Kind::hold, kL2, 0},
    {"reload", "R", Kind::tap, kSquare, 0},
    {"interact", "E", Kind::hold, kSquare, 0},
    {"melee", "C", Kind::hold, kR1, 0},
    {"grenade", "Q", Kind::hold, kL1, 0},
    {"super", "F", Kind::hold, kL1 | kR1, 0},
    {"weapon_1", "1", Kind::weapon, 0, 0},
    {"weapon_2", "2", Kind::weapon, 1, 0},
    {"weapon_3", "3", Kind::weapon, 2, 0},
    {"swap_weapon", "`", Kind::tap, kTriangle, 0},
    {"next_weapon", "WheelUp", Kind::tap, kTriangle, 0},
    {"prev_weapon", "WheelDown", Kind::tap, kTriangle, 0},
    {"ghost", "Tab", Kind::hold, kTouchPad, 0},
    {"director", "M", Kind::tap, kTouchPad, 0},
    {"character", "I", Kind::tap, kOptions, 0},
    {"menu", "Escape", Kind::hold, kOptions, 0},
    {"back", "Backspace", Kind::hold, kCircle, 0},
    {"confirm", "Return", Kind::hold, kCross, 0},
    {"emote_up", "Up", Kind::hold, kUp, 0},
    {"emote_down", "Down", Kind::hold, kDown, 0},
    {"emote_left", "Left", Kind::hold, kLeft, 0},
    {"emote_right", "Right", Kind::hold, kRight, 0},
    {"pad_cross", "", Kind::hold, kCross, 0},
    {"pad_circle", "", Kind::hold, kCircle, 0},
    {"pad_square", "", Kind::hold, kSquare, 0},
    {"pad_triangle", "", Kind::hold, kTriangle, 0},
    {"pad_l1", "", Kind::hold, kL1, 0},
    {"pad_r1", "", Kind::hold, kR1, 0},
    {"pad_l2", "", Kind::hold, kL2, 0},
    {"pad_r2", "", Kind::hold, kR2, 0},
    {"pad_l3", "", Kind::hold, kL3, 0},
    {"pad_r3", "", Kind::hold, kR3, 0},
    {"pad_options", "", Kind::hold, kOptions, 0},
    {"pad_touchpad", "", Kind::hold, kTouchPad, 0},
    {"pad_up", "", Kind::hold, kUp, 0},
    {"pad_down", "", Kind::hold, kDown, 0},
    {"pad_left", "", Kind::hold, kLeft, 0},
    {"pad_right", "", Kind::hold, kRight, 0},
};
constexpr int kActionCount = int(sizeof kActions / sizeof kActions[0]);
constexpr uint32_t kTapMs = 120;  // long enough for the game to see a press, short of a hold

// An input: a keyboard scancode, a mouse button (1-5) or a wheel direction.
struct Input {
    enum { key, mouse, wheel_up, wheel_down } type;
    int code;
};
std::vector<Input> g_binds[kActionCount];
std::atomic<uint32_t> g_wheel_up_until{0}, g_wheel_down_until{0};
std::atomic<int> g_weapon_request{-1};

bool parse_input(std::string name, Input& out) {
    name.erase(0, name.find_first_not_of(" \t"));
    name.erase(name.find_last_not_of(" \t") + 1);
    if (name.empty()) return false;
    std::string lower;
    for (char c : name) lower += char(std::tolower(static_cast<unsigned char>(c)));
    if (lower == "wheelup") return out = {Input::wheel_up, 0}, true;
    if (lower == "wheeldown") return out = {Input::wheel_down, 0}, true;
    if (lower.size() == 6 && lower.rfind("mouse", 0) == 0 && lower[5] >= '1' && lower[5] <= '5')
        return out = {Input::mouse, lower[5] - '0'}, true;
    const SDL_Scancode sc = SDL_GetScancodeFromName(name.c_str());
    if (sc == SDL_SCANCODE_UNKNOWN) return false;
    return out = {Input::key, int(sc)}, true;
}

std::once_flag g_binds_once;
void load_binds_once() {
    const auto& user = d1::settings().binds;
    for (int a = 0; a < kActionCount; ++a) {
        std::string spec = kActions[a].defaults;
        for (const auto& [name, keys] : user)
            if (name == kActions[a].name) spec = keys;
        std::string lower;
        for (char c : spec) lower += char(std::tolower(static_cast<unsigned char>(c)));
        if (lower == "none") continue;
        size_t pos = 0;
        while (pos <= spec.size()) {
            size_t comma = spec.find(',', pos);
            if (comma == std::string::npos) comma = spec.size();
            const std::string one = spec.substr(pos, comma - pos);
            Input in;
            if (parse_input(one, in)) g_binds[a].push_back(in);
            else if (one.find_first_not_of(" \t") != std::string::npos)
                d1::log("input: bind_%s: unknown key '%s'", kActions[a].name, one.c_str());
            pos = comma + 1;
        }
    }
    for (const auto& [name, keys] : user) {
        bool known = false;
        for (const auto& a : kActions) known |= name == a.name;
        if (!known) d1::log("input: unknown action bind_%s", name.c_str());
    }
}

// Last input device: key names in prompts while the keyboard and mouse are in use, button
// glyphs once a controller is (settings "prompts": auto, keyboard or controller).
std::atomic<bool> g_kbm_last{true};

std::string input_name(const Input& in) {
    switch (in.type) {
    case Input::mouse: {
        static const char* names[] = {"", "LMB", "RMB", "MMB", "Mouse 4", "Mouse 5"};
        return names[in.code];
    }
    case Input::wheel_up:
        return "Wheel Up";
    case Input::wheel_down:
        return "Wheel Down";
    case Input::key:
        break;
    }
    std::string n = SDL_GetScancodeName(SDL_Scancode(in.code));
    for (const char* side : {"Left ", "Right "})
        if (n.rfind(side, 0) == 0 && n.size() > std::strlen(side) + 1) n = n.substr(std::strlen(side));
    if (n == "Escape") n = "Esc";
    if (n == "Return") n = "Enter";
    if (n == "Backspace") n = "Bksp";
    return n;
}

// The action a DualShock 4 glyph stands for in prompts (what the player presses on PC).
const char* glyph_action(uint32_t glyph) {
    switch (glyph) {
    case 0xE000: return "jump";         // Cross
    case 0xE001: return "crouch";       // Circle
    case 0xE002: return "interact";     // Square (prompts are mostly "hold to interact")
    case 0xE003: return "swap_weapon";  // Triangle
    case 0xE005: return "director";     // touch pad
    case 0xE006: return "fire";         // R2
    case 0xE007: return "aim";          // L2
    case 0xE008: return "grenade";      // L1
    case 0xE009: return "melee";        // R1
    case 0xE010: return "mouse_look";   // R3 / right stick (the glyph is the stick)
    case 0xE012: return "movement";     // L3 / left stick ("use the left stick to move ...")
    case 0xE013: return "emote_up";     // D-pad
    case 0xE014: return "emote_right";
    case 0xE015: return "emote_down";
    case 0xE016: return "emote_left";
    case 0xE017: return "character";    // Options
    }
    return nullptr;
}

void poll_input() {
    std::call_once(g_binds_once, load_binds_once);
    PadState s{0, 0x80, 0x80, 0x80, 0x80, 0, 0};
    const uint8_t* k = SDL_GetKeyboardState(nullptr);
    const uint32_t now = SDL_GetTicks();
    const uint32_t mouse = g_captured ? SDL_GetMouseState(nullptr, nullptr) : 0;
    const bool alt = k[SDL_SCANCODE_LALT] || k[SDL_SCANCODE_RALT];  // Alt+Enter is the fullscreen toggle
    auto down = [&](const Input& in) {
        switch (in.type) {
        case Input::key:
            return k[in.code] != 0 && !(alt && in.code == SDL_SCANCODE_RETURN);
        case Input::mouse:
            return (mouse & SDL_BUTTON(in.code)) != 0;
        case Input::wheel_up:
            return g_captured && int32_t(g_wheel_up_until.load() - now) > 0;
        case Input::wheel_down:
            return g_captured && int32_t(g_wheel_down_until.load() - now) > 0;
        }
        return false;
    };
    static bool was[kActionCount] = {};
    static uint32_t tap_until[kActionCount] = {};
    int lx = 0, ly = 0;
    for (int a = 0; a < kActionCount; ++a) {
        bool on = false;
        for (const Input& in : g_binds[a]) on |= down(in);
        const bool pressed = on && !was[a];
        was[a] = on;
        const Action& act = kActions[a];
        switch (act.kind) {
        case Kind::hold:
            if (on) s.buttons |= act.buttons;
            break;
        case Kind::tap:
            if (pressed) tap_until[a] = now + kTapMs;
            if (int32_t(tap_until[a] - now) > 0) s.buttons |= act.buttons;
            break;
        case Kind::stick:
            if (on) (act.buttons == kLeftX ? lx : ly) += act.sign;
            break;
        case Kind::weapon:
            if (pressed) g_weapon_request = int(act.buttons);
            break;
        }
    }
    s.lx = lx < 0 ? 0x00 : lx > 0 ? 0xFF : 0x80;
    s.ly = ly < 0 ? 0x00 : ly > 0 ? 0xFF : 0x80;
    if (s.buttons & kL2) s.l2 = 0xFF;
    if (s.buttons & kR2) s.r2 = 0xFF;

    if (g_pad) {
        struct { SDL_GameControllerButton b; uint32_t bit; } btns[] = {
            {SDL_CONTROLLER_BUTTON_A, kCross},          {SDL_CONTROLLER_BUTTON_B, kCircle},
            {SDL_CONTROLLER_BUTTON_X, kSquare},         {SDL_CONTROLLER_BUTTON_Y, kTriangle},
            {SDL_CONTROLLER_BUTTON_LEFTSHOULDER, kL1},  {SDL_CONTROLLER_BUTTON_RIGHTSHOULDER, kR1},
            {SDL_CONTROLLER_BUTTON_LEFTSTICK, kL3},     {SDL_CONTROLLER_BUTTON_RIGHTSTICK, kR3},
            {SDL_CONTROLLER_BUTTON_START, kOptions},    {SDL_CONTROLLER_BUTTON_TOUCHPAD, kTouchPad},
            {SDL_CONTROLLER_BUTTON_BACK, kTouchPad},    {SDL_CONTROLLER_BUTTON_DPAD_UP, kUp},
            {SDL_CONTROLLER_BUTTON_DPAD_DOWN, kDown},   {SDL_CONTROLLER_BUTTON_DPAD_LEFT, kLeft},
            {SDL_CONTROLLER_BUTTON_DPAD_RIGHT, kRight},
        };
        for (auto& [b, bit] : btns)
            if (SDL_GameControllerGetButton(g_pad, b)) s.buttons |= bit;
        auto merge = [](uint8_t key, uint8_t pad) { return key != 0x80 ? key : pad; };
        s.lx = merge(s.lx, axis(SDL_GameControllerGetAxis(g_pad, SDL_CONTROLLER_AXIS_LEFTX)));
        s.ly = merge(s.ly, axis(SDL_GameControllerGetAxis(g_pad, SDL_CONTROLLER_AXIS_LEFTY)));
        s.rx = merge(s.rx, axis(SDL_GameControllerGetAxis(g_pad, SDL_CONTROLLER_AXIS_RIGHTX)));
        s.ry = merge(s.ry, axis(SDL_GameControllerGetAxis(g_pad, SDL_CONTROLLER_AXIS_RIGHTY)));
        const int l2 = SDL_GameControllerGetAxis(g_pad, SDL_CONTROLLER_AXIS_TRIGGERLEFT);
        const int r2 = SDL_GameControllerGetAxis(g_pad, SDL_CONTROLLER_AXIS_TRIGGERRIGHT);
        if (l2 > 0) s.l2 = std::max<uint8_t>(s.l2, uint8_t(l2 >> 7));
        if (r2 > 0) s.r2 = std::max<uint8_t>(s.r2, uint8_t(r2 >> 7));
        if (s.l2 > 0x20) s.buttons |= kL2;
        if (s.r2 > 0x20) s.buttons |= kR2;
    }
    std::lock_guard lk(g_pad_mutex);
    g_state = s;
}

void open_first_controller() {
    if (g_pad) return;
    for (int i = 0; i < SDL_NumJoysticks(); ++i)
        if (SDL_IsGameController(i) && (g_pad = SDL_GameControllerOpen(i))) {
            d1::log("input: controller \"%s\"", SDL_GameControllerName(g_pad));
            return;
        }
}
}  // namespace

bool window_active() {
    return g_window != nullptr;
}

int take_weapon_request() {
    return g_weapon_request.exchange(-1, std::memory_order_relaxed);
}

bool keyboard_prompts() {
    const std::string& mode = d1::settings().prompts;
    if (mode == "controller") return false;
    if (mode == "keyboard") return true;
    return g_kbm_last.load(std::memory_order_relaxed);
}

int prompt_label(uint32_t glyph, char16_t* out, int max) {
    const char* action = glyph_action(glyph);
    if (!action) return 0;
    std::call_once(g_binds_once, load_binds_once);
    auto put = [&](const std::string& text) {
        int n = 0;
        for (char c : text)
            if (n < max - 1) out[n++] = char16_t(static_cast<unsigned char>(c));
        out[n] = 0;
        return n;
    };
    if (!std::strcmp(action, "mouse_look")) return put("Mouse");
    if (!std::strcmp(action, "movement")) {  // the four move keys, e.g. "WASD"
        std::string keys;
        for (const char* m : {"move_forward", "move_left", "move_back", "move_right"})
            for (int a = 0; a < kActionCount; ++a)
                if (!std::strcmp(kActions[a].name, m) && !g_binds[a].empty()) keys += input_name(g_binds[a][0]);
        return keys.size() == 4 ? put(keys) : put("Move keys");
    }
    for (int a = 0; a < kActionCount; ++a) {
        if (std::strcmp(kActions[a].name, action) != 0 || g_binds[a].empty()) continue;
        return put(input_name(g_binds[a][0]));
    }
    return 0;
}

bool take_mouse_motion(int32_t& dx, int32_t& dy) {
    if (!g_window || !g_captured.load(std::memory_order_relaxed)) return false;
    dx = g_mouse_dx.exchange(0, std::memory_order_relaxed);
    dy = g_mouse_dy.exchange(0, std::memory_order_relaxed);
    return true;
}

static SDL_AudioDeviceID g_audio = 0;
static uint32_t g_audio_bytes = 0;  // one buffer
bool audio_open(uint32_t freq, uint32_t frames) {
    if (!g_window || g_audio) return g_audio != 0;
    if (const char* v = std::getenv("D1_AUDIO"); v && v[0] == '0') return false;
    if (SDL_InitSubSystem(SDL_INIT_AUDIO) != 0) {
        d1::log("audio: SDL audio init failed: %s", SDL_GetError());
        return false;
    }
    SDL_AudioSpec want{}, have{};
    want.freq = int(freq);
    want.format = AUDIO_F32SYS;
    want.channels = 8;
    want.samples = Uint16(std::min<uint32_t>(frames, 4096));
    // no allowed changes: SDL converts (and downmixes 7.1) to whatever the device uses
    g_audio = SDL_OpenAudioDevice(nullptr, 0, &want, &have, 0);
    if (!g_audio) {
        d1::log("audio: no output device: %s", SDL_GetError());
        return false;
    }
    g_audio_bytes = frames * 8 * sizeof(float);
    SDL_PauseAudioDevice(g_audio, 0);
    d1::log("audio: %s, %d Hz, 7.1 float in (%d-frame device buffer)",
            SDL_GetCurrentAudioDriver() ? SDL_GetCurrentAudioDriver() : "?", freq, int(have.samples));
    return true;
}
void audio_output(const float* frames8, uint32_t frames) {
    if (!g_audio) return;
    // keep ~3 buffers (64 ms at 1024 frames) queued: enough to ride out a slow frame
    for (int i = 0; i < 200 && SDL_GetQueuedAudioSize(g_audio) > 2 * g_audio_bytes; ++i) SDL_Delay(1);
    SDL_QueueAudio(g_audio, frames8, frames * 8 * sizeof(float));
}

bool read_pad(PadState& out) {
    if (!g_window) return false;
    std::lock_guard lk(g_pad_mutex);
    out = g_state;
    return true;
}

void run_window_loop() {
    if (!g_window) return;
    for (;;) {
        SDL_Event e;
        while (SDL_PollEvent(&e)) {
            switch (e.type) {
            case SDL_QUIT:
                return;
            case SDL_WINDOWEVENT:
                if (e.window.event == SDL_WINDOWEVENT_SIZE_CHANGED || e.window.event == SDL_WINDOWEVENT_MINIMIZED ||
                    e.window.event == SDL_WINDOWEVENT_RESTORED || e.window.event == SDL_WINDOWEVENT_MAXIMIZED)
                    update_drawable_size();
                if (e.window.event == SDL_WINDOWEVENT_FOCUS_LOST) set_capture(false);
                break;
            case SDL_CONTROLLERBUTTONDOWN:
                g_kbm_last = false;
                break;
            case SDL_CONTROLLERAXISMOTION:
                if (std::abs(int(e.caxis.value)) > 16000) g_kbm_last = false;
                break;
            case SDL_MOUSEMOTION:
                if (g_captured && (std::abs(e.motion.xrel) > 2 || std::abs(e.motion.yrel) > 2)) g_kbm_last = true;
                if (g_captured) {
                    g_mouse_dx.fetch_add(e.motion.xrel, std::memory_order_relaxed);
                    g_mouse_dy.fetch_add(e.motion.yrel, std::memory_order_relaxed);
                }
                break;
            case SDL_MOUSEBUTTONDOWN:
                if (!g_captured && e.button.button == SDL_BUTTON_LEFT) set_capture(true);
                break;
            case SDL_MOUSEWHEEL:  // a notch reads as a press for 80 ms (bindings see its edge)
                if (g_captured && e.wheel.y > 0) g_wheel_up_until = SDL_GetTicks() + 80;
                if (g_captured && e.wheel.y < 0) g_wheel_down_until = SDL_GetTicks() + 80;
                break;
            case SDL_KEYDOWN:
                g_kbm_last = true;
                if (!e.key.repeat && e.key.keysym.sym == SDLK_F2) set_capture(!g_captured);
                if (!e.key.repeat && e.key.keysym.sym == SDLK_F9) d1::hooks_request_launch();   // co-op test keys
                if (!e.key.repeat && e.key.keysym.sym == SDLK_F10) d1::hooks_request_join();
                if (!e.key.repeat && e.key.keysym.sym >= SDLK_F5 && e.key.keysym.sym <= SDLK_F8)  // renderer test switches
                    d1::ng::flip_debug_toggle(int(e.key.keysym.sym - SDLK_F5));
                if (!e.key.repeat && (e.key.keysym.sym == SDLK_F11 ||
                                      (e.key.keysym.sym == SDLK_RETURN && (e.key.keysym.mod & KMOD_ALT)))) {
                    const bool fs = SDL_GetWindowFlags(g_window) & SDL_WINDOW_FULLSCREEN_DESKTOP;
                    SDL_SetWindowFullscreen(g_window, fs ? 0 : SDL_WINDOW_FULLSCREEN_DESKTOP);
                    update_drawable_size();
                    d1::log("window: %s, %ux%u", fs ? "windowed" : "fullscreen", g_w.load(), g_h.load());
                }
                break;
            case SDL_CONTROLLERDEVICEADDED:
                open_first_controller();
                break;
            case SDL_CONTROLLERDEVICEREMOVED:
                if (g_pad && e.cdevice.which == SDL_JoystickInstanceID(SDL_GameControllerGetJoystick(g_pad))) {
                    SDL_GameControllerClose(g_pad);
                    g_pad = nullptr;
                    open_first_controller();
                }
                break;
            default:
                break;
            }
        }
        poll_input();
        {
            std::lock_guard lk(g_title_m);
            if (g_status_dirty) {
                g_status_dirty = false;
                SDL_SetWindowTitle(g_window, g_status.c_str());
            }
        }
        SDL_Delay(1);  // input is at most ~1 ms old when the game reads the pad
    }
}

}  // namespace d1::render

namespace d1::frontend {
using namespace d1::render;

bool open(int width, int height, bool fullscreen) {
    if (const char* v = std::getenv("D1_WINDOW"); v && v[0] == '0') return false;
#ifndef _WIN32
    if (!std::getenv("DISPLAY")) return false;  // Xlib surfaces only
    SDL_SetHint(SDL_HINT_VIDEODRIVER, "x11");
#endif
    SDL_SetHint(SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS, "1");
    // Relative mode from raw input (WM_INPUT on Windows) without warping the cursor and
    // without the OS pointer-acceleration curve: the aim hook gets device counts.
    SDL_SetHint(SDL_HINT_MOUSE_RELATIVE_MODE_WARP, "0");
    SDL_SetHint(SDL_HINT_MOUSE_RELATIVE_SYSTEM_SCALE, "0");
    SDL_SetHint(SDL_HINT_MOUSE_RELATIVE_SPEED_SCALE, "1.0");
    SDL_SetHint(SDL_HINT_WINDOWS_DPI_AWARENESS, "permonitorv2");
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER) != 0) {
        d1::log("window: SDL_Init failed: %s", SDL_GetError());
        return false;
    }
    g_window = SDL_CreateWindow("Destiny (d1-native)", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                                width > 0 ? width : 1280, height > 0 ? height : 720,
                                SDL_WINDOW_RESIZABLE | SDL_WINDOW_ALLOW_HIGHDPI |
                                    (fullscreen ? SDL_WINDOW_FULLSCREEN_DESKTOP : 0));
    if (!g_window) {
        d1::log("window: SDL_CreateWindow failed: %s", SDL_GetError());
        return false;
    }
    Handles h;
    if (!handles(h)) {
        d1::log("window: unsupported window system");
        SDL_DestroyWindow(g_window);
        g_window = nullptr;
        return false;
    }
    update_drawable_size();
    open_first_controller();
    d1::log("window: %s, %ux%u", h.type == Handles::kWin32 ? "Windows" : "X11", g_w.load(), g_h.load());
    return true;
}

bool handles(Handles& out) {
    if (!g_window) return false;
    SDL_SysWMinfo wm;
    SDL_VERSION(&wm.version);
    if (!SDL_GetWindowWMInfo(g_window, &wm)) return false;
    switch (wm.subsystem) {
#ifdef SDL_VIDEO_DRIVER_WINDOWS
    case SDL_SYSWM_WINDOWS:
        out.type = Handles::kWin32;
        out.display = wm.info.win.hinstance;
        out.window = uint64_t(wm.info.win.window);
        return true;
#endif
#ifdef SDL_VIDEO_DRIVER_X11
    case SDL_SYSWM_X11:
        out.type = Handles::kXlib;
        out.display = wm.info.x11.display;
        out.window = uint64_t(wm.info.x11.window);
        return true;
#endif
    default:
        return false;
    }
}

void drawable_size(uint32_t& w, uint32_t& h) {
    w = g_w.load(std::memory_order_relaxed);
    h = g_h.load(std::memory_order_relaxed);
}

void set_status(const char* text) {
    std::lock_guard lk(g_title_m);
    g_status = text;
    g_status_dirty = true;
}

}  // namespace d1::frontend
