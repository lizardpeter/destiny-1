// Window, input and audio for builds with the native renderer (no shadPS4): an SDL2 window
// owned by the main thread. The render_bridge.h window/input/audio entry points
// (window_active, read_pad, take_mouse_motion, audio_*, run_window_loop) are implemented by
// frontend_sdl.cpp in those builds.
#pragma once
#include <cstdint>

namespace d1::frontend {

// Native handles of the window for a Vulkan surface.
struct Handles {
    enum Type { kNone, kWin32, kXlib } type = kNone;
    void* display = nullptr;   // Win32: HINSTANCE; Xlib: Display*
    uint64_t window = 0;       // Win32: HWND; Xlib: Window
};

// Opens the game window (main thread). False when D1_WINDOW=0, there is no display, or SDL
// fails; the game then runs without a window.
bool open(int width, int height, bool fullscreen);
bool handles(Handles& out);
// Drawable size in pixels (0 x 0 while minimised).
void drawable_size(uint32_t& w, uint32_t& h);
// Shown in the title bar (frames per second and the like); any thread.
void set_status(const char* text);

}  // namespace d1::frontend
