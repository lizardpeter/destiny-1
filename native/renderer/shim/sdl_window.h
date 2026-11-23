// d1-native shim for shadPS4's window type: just the native handles and current size,
// which the Vulkan instance and swapchain read. The window itself is owned by
// glue/d1_window.cpp (SDL2). "Headless" means offscreen rendering, no swapchain.
#pragma once
#include <atomic>
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
    s32 GetWidth() const { return width.load(); }
    s32 GetHeight() const { return height.load(); }
    WindowSystemInfo info{};
    std::atomic<s32> width{1920};
    std::atomic<s32> height{1080};
};
}  // namespace Frontend
