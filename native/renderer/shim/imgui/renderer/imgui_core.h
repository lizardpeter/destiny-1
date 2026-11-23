// d1-native shim: no overlay.
#pragma once
#include "video_core/renderer_vulkan/vk_common.h"
namespace Vulkan {
class Instance;
}
namespace Frontend {
class WindowSDL;
}
namespace ImGui::Core {
inline void Initialize(const Vulkan::Instance&, const Frontend::WindowSDL&, unsigned, vk::Format) {}
inline void OnSurfaceFormatChange(vk::Format) {}
inline void Shutdown(vk::Device) {}
}  // namespace ImGui::Core
