// Window owned by the temporary renderer (SDL2): created on the main thread before the
// Vulkan instance, whose surface extensions depend on the window system.
#pragma once
#include "sdl_window.h"

namespace d1::render::window {
// Opens the game window unless D1_WINDOW=0 or no display is available. F11 or Alt+Enter
// toggles borderless fullscreen.
Frontend::WindowSDL* open(int width, int height, bool fullscreen);
}  // namespace d1::render::window
