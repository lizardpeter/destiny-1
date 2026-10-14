// SDL2 window, event loop and input for d1-native's temporary renderer.
//
// Keyboard and mouse (a connected controller works alongside them):
//   WASD move · mouse look (raw counts, fed straight into the game's aim; see hooks.cpp)
//   Space/Enter Cross (jump) · Left Ctrl/C Circle (crouch, back) · Esc/Backspace Circle
//   R/E Square (reload, interact) · 1/2/3/mouse wheel Triangle (switch weapon)
//   Q L1 (grenade) · F R1 (melee) · X L1+R1 (super) · Left Shift L3 (sprint) · Z R3
//   left mouse R2 (fire) · right mouse L2 (aim) · middle mouse R3 · mouse 4/5 L1/R1
//   Tab Options · G touch pad (ghost) · arrows D-pad · IJKL right stick (menus)
// Clicking in the window captures the mouse; F2 or losing focus releases it.
// Controllers use SDL's game-controller mapping (PlayStation layout names).
#include <SDL2/SDL.h>
#include <SDL2/SDL_syswm.h>
#include <SDL2/SDL_vulkan.h>

#include <algorithm>
#include <atomic>
#include <cstdlib>
#include <mutex>

#include "../../src/render_bridge.h"
#include "d1_window.h"

namespace d1 {
void log(const char* fmt, ...);
}

namespace d1::render {

namespace {
enum : u32 {
    kL3 = 0x2, kR3 = 0x4, kOptions = 0x8, kUp = 0x10, kRight = 0x20, kDown = 0x40, kLeft = 0x80,
    kL2 = 0x100, kR2 = 0x200, kL1 = 0x400, kR1 = 0x800, kTriangle = 0x1000, kCircle = 0x2000,
    kCross = 0x4000, kSquare = 0x8000, kTouchPad = 0x100000,
};

SDL_Window* g_window = nullptr;
Frontend::WindowSDL g_info;
SDL_GameController* g_pad = nullptr;
std::mutex g_pad_mutex;
PadState g_state{0, 0x80, 0x80, 0x80, 0x80, 0, 0};
// Mouse: motion is accumulated by the event loop (1 ms cadence) and drained by the game's
// aim hook, so a count reaches the game at most ~1 ms after SDL sees it.
std::atomic<bool> g_captured{false};
std::atomic<int32_t> g_mouse_dx{0}, g_mouse_dy{0};
std::atomic<u32> g_wheel_until{0};  // SDL tick until which a wheel notch holds Triangle

void set_capture(bool on) {
    if (on == g_captured.load()) return;
    SDL_SetRelativeMouseMode(on ? SDL_TRUE : SDL_FALSE);
    g_mouse_dx = 0, g_mouse_dy = 0;
    g_captured = on;
    d1::log("input: mouse %s", on ? "captured (F2 releases)" : "released");
}

u8 axis(int v) {  // SDL -32768..32767 -> 0..255
    return u8((v + 32768) >> 8);
}

void update_drawable_size() {
    int w = 0, h = 0;
    SDL_Vulkan_GetDrawableSize(g_window, &w, &h);
    if (w > 0 && h > 0) {
        g_info.width = w;
        g_info.height = h;
    }
}

void poll_input() {
    PadState s{0, 0x80, 0x80, 0x80, 0x80, 0, 0};
    const u8* k = SDL_GetKeyboardState(nullptr);
    struct { SDL_Scancode sc; u32 bit; } keys[] = {
        {SDL_SCANCODE_SPACE, kCross},     {SDL_SCANCODE_RETURN, kCross},    {SDL_SCANCODE_LCTRL, kCircle},
        {SDL_SCANCODE_C, kCircle},        {SDL_SCANCODE_ESCAPE, kCircle},   {SDL_SCANCODE_BACKSPACE, kCircle},
        {SDL_SCANCODE_R, kSquare},        {SDL_SCANCODE_E, kSquare},        {SDL_SCANCODE_1, kTriangle},
        {SDL_SCANCODE_2, kTriangle},      {SDL_SCANCODE_3, kTriangle},      {SDL_SCANCODE_Q, kL1},
        {SDL_SCANCODE_F, kR1},            {SDL_SCANCODE_X, kL1 | kR1},      {SDL_SCANCODE_LSHIFT, kL3},
        {SDL_SCANCODE_Z, kR3},            {SDL_SCANCODE_TAB, kOptions},     {SDL_SCANCODE_G, kTouchPad},
        {SDL_SCANCODE_UP, kUp},           {SDL_SCANCODE_DOWN, kDown},       {SDL_SCANCODE_LEFT, kLeft},
        {SDL_SCANCODE_RIGHT, kRight},
    };
    const bool alt = k[SDL_SCANCODE_LALT] || k[SDL_SCANCODE_RALT];  // Alt+Enter is the fullscreen toggle
    for (auto& [sc, bit] : keys)
        if (k[sc] && !(alt && sc == SDL_SCANCODE_RETURN)) s.buttons |= bit;
    auto stick = [&](SDL_Scancode neg, SDL_Scancode pos) -> u8 {
        return k[neg] && !k[pos] ? 0x00 : k[pos] && !k[neg] ? 0xFF : 0x80;
    };
    s.lx = stick(SDL_SCANCODE_A, SDL_SCANCODE_D);
    s.ly = stick(SDL_SCANCODE_W, SDL_SCANCODE_S);
    s.rx = stick(SDL_SCANCODE_J, SDL_SCANCODE_L);
    s.ry = stick(SDL_SCANCODE_I, SDL_SCANCODE_K);
    if (g_captured) {
        const u32 m = SDL_GetMouseState(nullptr, nullptr);
        if (m & SDL_BUTTON_LMASK) s.buttons |= kR2;
        if (m & SDL_BUTTON_RMASK) s.buttons |= kL2;
        if (m & SDL_BUTTON_MMASK) s.buttons |= kR3;
        if (m & SDL_BUTTON_X1MASK) s.buttons |= kL1;
        if (m & SDL_BUTTON_X2MASK) s.buttons |= kR1;
        if (int32_t(g_wheel_until.load() - SDL_GetTicks()) > 0) s.buttons |= kTriangle;
    }
    if (s.buttons & kL2) s.l2 = 0xFF;
    if (s.buttons & kR2) s.r2 = 0xFF;

    if (g_pad) {
        struct { SDL_GameControllerButton b; u32 bit; } btns[] = {
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
        auto merge = [](u8 key, u8 pad) { return key != 0x80 ? key : pad; };
        s.lx = merge(s.lx, axis(SDL_GameControllerGetAxis(g_pad, SDL_CONTROLLER_AXIS_LEFTX)));
        s.ly = merge(s.ly, axis(SDL_GameControllerGetAxis(g_pad, SDL_CONTROLLER_AXIS_LEFTY)));
        s.rx = merge(s.rx, axis(SDL_GameControllerGetAxis(g_pad, SDL_CONTROLLER_AXIS_RIGHTX)));
        s.ry = merge(s.ry, axis(SDL_GameControllerGetAxis(g_pad, SDL_CONTROLLER_AXIS_RIGHTY)));
        const int l2 = SDL_GameControllerGetAxis(g_pad, SDL_CONTROLLER_AXIS_TRIGGERLEFT);
        const int r2 = SDL_GameControllerGetAxis(g_pad, SDL_CONTROLLER_AXIS_TRIGGERRIGHT);
        if (l2 > 0) s.l2 = std::max<u8>(s.l2, u8(l2 >> 7));
        if (r2 > 0) s.r2 = std::max<u8>(s.r2, u8(r2 >> 7));
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

namespace window {
Frontend::WindowSDL* open(int width, int height, bool fullscreen) {
    if (const char* v = std::getenv("D1_WINDOW"); v && v[0] == '0') return nullptr;
#ifndef _WIN32
    if (!std::getenv("DISPLAY") && !std::getenv("WAYLAND_DISPLAY")) return nullptr;
#endif
    SDL_SetHint(SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS, "1");
    // Relative mode from raw input (WM_INPUT on Windows) without warping the cursor and
    // without the OS pointer-acceleration curve: the aim hook gets device counts.
    SDL_SetHint(SDL_HINT_MOUSE_RELATIVE_MODE_WARP, "0");
    SDL_SetHint(SDL_HINT_MOUSE_RELATIVE_SYSTEM_SCALE, "0");
    SDL_SetHint(SDL_HINT_MOUSE_RELATIVE_SPEED_SCALE, "1.0");
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER) != 0) {
        d1::log("window: SDL_Init failed: %s", SDL_GetError());
        return nullptr;
    }
    g_window = SDL_CreateWindow("Destiny (d1-native)", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                                width > 0 ? width : 1280, height > 0 ? height : 720,
                                SDL_WINDOW_VULKAN | SDL_WINDOW_RESIZABLE | SDL_WINDOW_ALLOW_HIGHDPI |
                                    (fullscreen ? SDL_WINDOW_FULLSCREEN_DESKTOP : 0));
    if (!g_window) {
        d1::log("window: SDL_CreateWindow failed: %s", SDL_GetError());
        return nullptr;
    }
    SDL_SysWMinfo wm;
    SDL_VERSION(&wm.version);
    if (!SDL_GetWindowWMInfo(g_window, &wm)) {
        d1::log("window: no native handles: %s", SDL_GetError());
        return nullptr;
    }
    switch (wm.subsystem) {
#ifdef SDL_VIDEO_DRIVER_X11
    case SDL_SYSWM_X11:
        g_info.info.type = Frontend::WindowSystemType::X11;
        g_info.info.display_connection = wm.info.x11.display;
        g_info.info.render_surface = reinterpret_cast<void*>(wm.info.x11.window);
        break;
#endif
#ifdef SDL_VIDEO_DRIVER_WINDOWS
    case SDL_SYSWM_WINDOWS:
        g_info.info.type = Frontend::WindowSystemType::Windows;
        g_info.info.render_surface = wm.info.win.window;
        break;
#endif
#ifdef SDL_VIDEO_DRIVER_WAYLAND
    case SDL_SYSWM_WAYLAND:
        g_info.info.type = Frontend::WindowSystemType::Wayland;
        g_info.info.display_connection = wm.info.wl.display;
        g_info.info.render_surface = wm.info.wl.surface;
        break;
#endif
    default:
        d1::log("window: unsupported window system %d", int(wm.subsystem));
        return nullptr;
    }
    update_drawable_size();
    open_first_controller();
    d1::log("window: %s, %dx%d",
            g_info.info.type == Frontend::WindowSystemType::Windows ? "Windows"
            : g_info.info.type == Frontend::WindowSystemType::X11   ? "X11"
                                                                    : "Wayland",
            g_info.GetWidth(), g_info.GetHeight());
    return &g_info;
}
}  // namespace window

static std::atomic<bool> g_overlay{false};
bool overlay_enabled() { return g_overlay.load(std::memory_order_relaxed); }
void set_overlay(bool on) { g_overlay = on; }

bool window_active() {
    return g_window != nullptr;
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
                if (e.window.event == SDL_WINDOWEVENT_SIZE_CHANGED) update_drawable_size();
                if (e.window.event == SDL_WINDOWEVENT_FOCUS_LOST) set_capture(false);
                break;
            case SDL_MOUSEMOTION:
                if (g_captured) {
                    g_mouse_dx.fetch_add(e.motion.xrel, std::memory_order_relaxed);
                    g_mouse_dy.fetch_add(e.motion.yrel, std::memory_order_relaxed);
                }
                break;
            case SDL_MOUSEBUTTONDOWN:
                if (!g_captured && e.button.button == SDL_BUTTON_LEFT) set_capture(true);
                break;
            case SDL_MOUSEWHEEL:
                if (g_captured && e.wheel.y != 0) g_wheel_until = SDL_GetTicks() + 80;
                break;
            case SDL_KEYDOWN:
                if (!e.key.repeat && e.key.keysym.sym == SDLK_F2) set_capture(!g_captured);
                if (!e.key.repeat && e.key.keysym.sym == SDLK_F3) set_overlay(!overlay_enabled());
                if (!e.key.repeat && (e.key.keysym.sym == SDLK_F11 ||
                                      (e.key.keysym.sym == SDLK_RETURN && (e.key.keysym.mod & KMOD_ALT)))) {
                    const bool fs = SDL_GetWindowFlags(g_window) & SDL_WINDOW_FULLSCREEN_DESKTOP;
                    SDL_SetWindowFullscreen(g_window, fs ? 0 : SDL_WINDOW_FULLSCREEN_DESKTOP);
                    update_drawable_size();
                    d1::log("window: %s, %dx%d", fs ? "windowed" : "fullscreen", g_info.GetWidth(), g_info.GetHeight());
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
        SDL_Delay(1);  // input is at most ~1 ms old when the game reads the pad
    }
}

}  // namespace d1::render
