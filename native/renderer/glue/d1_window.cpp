// SDL2 window, event loop and input for d1-native's temporary renderer.
//
// Keyboard (until a controller is connected, both work together):
//   WASD left stick · IJKL right stick · arrows D-pad
//   Enter/Space Cross · Esc/Backspace Circle · R Square · F Triangle
//   Q L1 · E R1 · Z L2 · X R2 · Left Shift L3 · C R3 · Tab Options · T touch pad
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
        {SDL_SCANCODE_RETURN, kCross},  {SDL_SCANCODE_SPACE, kCross},      {SDL_SCANCODE_ESCAPE, kCircle},
        {SDL_SCANCODE_BACKSPACE, kCircle}, {SDL_SCANCODE_R, kSquare},      {SDL_SCANCODE_F, kTriangle},
        {SDL_SCANCODE_Q, kL1},          {SDL_SCANCODE_E, kR1},             {SDL_SCANCODE_Z, kL2},
        {SDL_SCANCODE_X, kR2},          {SDL_SCANCODE_LSHIFT, kL3},        {SDL_SCANCODE_C, kR3},
        {SDL_SCANCODE_TAB, kOptions},   {SDL_SCANCODE_T, kTouchPad},       {SDL_SCANCODE_UP, kUp},
        {SDL_SCANCODE_DOWN, kDown},     {SDL_SCANCODE_LEFT, kLeft},        {SDL_SCANCODE_RIGHT, kRight},
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

bool window_active() {
    return g_window != nullptr;
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
                break;
            case SDL_KEYDOWN:
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
