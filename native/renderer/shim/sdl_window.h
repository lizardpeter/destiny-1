// d1-native shim: headless window description (rendering is offscreen).
#pragma once
#include "common/types.h"
namespace Frontend {
enum class WindowSystemType : u8 { Headless, Windows, X11, Wayland, Metal };
struct WindowSystemInfo {
    void* display_connection = nullptr;
    void* render_surface = nullptr;
    float render_surface_scale = 1.0f;
    WindowSystemType type = WindowSystemType::Headless;
};
class WindowSDL {
public:
    const WindowSystemInfo& GetWindowInfo() const { return info; }
    s32 GetWidth() const { return 1920; }
    s32 GetHeight() const { return 1080; }
    WindowSystemInfo info{};
};
}  // namespace Frontend
