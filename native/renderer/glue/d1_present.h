// Window presentation for d1-native: our own swapchain (replacing shadPS4's, which rebuilt
// itself on every "suboptimal" result, a black frame each time) and the stats overlay.
#pragma once
#include <array>
#include <string>
#include <vector>

#include "video_core/renderer_vulkan/vk_common.h"

namespace Vulkan {
class Instance;
}
namespace Frontend {
class WindowSDL;
}

namespace d1::render {

class Presenter {
public:
    Presenter(const Vulkan::Instance& instance, const Frontend::WindowSDL& window, const std::string& mode);
    ~Presenter();

    // Acquire the next image for a window of ww x wh pixels. False: nothing to present now
    // (minimised, or the swapchain is being rebuilt).
    bool Acquire(uint32_t ww, uint32_t wh);
    vk::Image Image() const { return images_[image_]; }
    vk::Extent2D Extent() const { return extent_; }
    vk::Semaphore AcquiredSemaphore() const { return acquired_[frame_]; }
    vk::Semaphore ReadySemaphore() const { return ready_[image_]; }
    void Present();  // after a submission that waits on AcquiredSemaphore and signals ReadySemaphore

    // Record a copy of text (one string per line) into the top-left of the acquired image.
    void RecordOverlay(vk::CommandBuffer cmd, const std::vector<std::string>& lines);

    const char* ModeName() const;
    uint32_t Rebuilds() const { return rebuilds_; }
    uint64_t presented_ = 0, suboptimal_ = 0, failed_ = 0;  // diagnostics

private:
    void Create(uint32_t w, uint32_t h);
    void Destroy();

    const Vulkan::Instance& instance_;
    vk::SurfaceKHR surface_{};
    vk::SwapchainKHR chain_{};
    vk::SurfaceFormatKHR format_{};
    vk::PresentModeKHR mode_{vk::PresentModeKHR::eFifo};
    vk::Extent2D extent_{};
    std::vector<vk::Image> images_;
    std::vector<vk::Semaphore> acquired_, ready_;
    uint32_t frame_ = 0, image_ = 0, rebuilds_ = 0;
    uint32_t want_w_ = 0, want_h_ = 0;
    bool out_of_date_ = false;
    // overlay: one host-visible staging buffer per frame in flight
    struct Staging {
        vk::Buffer buffer{};
        vk::DeviceMemory memory{};
        uint8_t* data = nullptr;
    };
    static constexpr uint32_t kOverlayW = 640, kOverlayH = 16 * 8 + 8;
    std::vector<Staging> staging_;
};

}  // namespace d1::render
