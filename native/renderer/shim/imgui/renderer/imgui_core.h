// d1-native shim: no overlay.
#pragma once
#include "video_core/renderer_vulkan/vk_common.h"
namespace ImGui::Core {
inline void Shutdown(vk::Device) {}
}
