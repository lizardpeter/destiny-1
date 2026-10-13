// See d1_present.h.
#include "d1_present.h"

#include <algorithm>
#include <cstring>

#include "overlay_font.h"
#include "sdl_window.h"
#include "video_core/renderer_vulkan/vk_instance.h"
#include "video_core/renderer_vulkan/vk_platform.h"

namespace d1 {
void log(const char* fmt, ...);
}

namespace d1::render {

static vk::PresentModeKHR parse_mode(const std::string& m) {
    if (m == "Immediate") return vk::PresentModeKHR::eImmediate;
    if (m == "Mailbox") return vk::PresentModeKHR::eMailbox;
    return vk::PresentModeKHR::eFifo;
}

Presenter::Presenter(const Vulkan::Instance& instance, const Frontend::WindowSDL& window, const std::string& mode)
    : instance_(instance) {
    surface_ = Vulkan::CreateSurface(instance.GetInstance(), window);
    const auto pd = instance.GetPhysicalDevice();
    // Requested mode if the driver has it, else FIFO (always available).
    const auto [mr, modes] = pd.getSurfacePresentModesKHR(surface_);
    // v-sync off prefers Mailbox (no tearing), then Immediate; Intel drivers on Windows
    // usually have only FIFO and Immediate.
    const auto want = parse_mode(mode);
    auto has = [&](vk::PresentModeKHR m) { return std::find(modes.begin(), modes.end(), m) != modes.end(); };
    mode_ = vk::PresentModeKHR::eFifo;
    if (has(want)) mode_ = want;
    else if (want == vk::PresentModeKHR::eMailbox && has(vk::PresentModeKHR::eImmediate)) mode_ = vk::PresentModeKHR::eImmediate;
    std::string avail;
    for (auto m : modes) avail += " " + vk::to_string(m);
    d1::log("present: requested %s, using %s (driver offers:%s)", mode.c_str(), vk::to_string(mode_).c_str(),
            avail.c_str());
    const auto [fr, formats] = pd.getSurfaceFormatsKHR(surface_);
    format_ = formats.empty() ? vk::SurfaceFormatKHR{vk::Format::eB8G8R8A8Unorm, vk::ColorSpaceKHR::eSrgbNonlinear}
                              : formats[0];
    for (const auto& f : formats)
        if (f.format == vk::Format::eB8G8R8A8Unorm || f.format == vk::Format::eR8G8B8A8Unorm) {
            format_ = f;
            break;
        }

    // Overlay staging buffers (host visible, coherent).
    const auto device = instance.GetDevice();
    const auto mem_props = pd.getMemoryProperties();
    staging_.resize(4);
    for (auto& s : staging_) {
        s.buffer = device.createBuffer({.size = kOverlayW * kOverlayH * 4, .usage = vk::BufferUsageFlagBits::eTransferSrc})
                       .value;
        const auto req = device.getBufferMemoryRequirements(s.buffer);
        uint32_t type = 0;
        for (uint32_t i = 0; i < mem_props.memoryTypeCount; ++i)
            if ((req.memoryTypeBits & (1u << i)) &&
                (mem_props.memoryTypes[i].propertyFlags &
                 (vk::MemoryPropertyFlagBits::eHostVisible | vk::MemoryPropertyFlagBits::eHostCoherent)) ==
                    (vk::MemoryPropertyFlagBits::eHostVisible | vk::MemoryPropertyFlagBits::eHostCoherent)) {
                type = i;
                break;
            }
        s.memory = device.allocateMemory({.allocationSize = req.size, .memoryTypeIndex = type}).value;
        (void)device.bindBufferMemory(s.buffer, s.memory, 0);
        s.data = static_cast<uint8_t*>(device.mapMemory(s.memory, 0, req.size).value);
    }
}

Presenter::~Presenter() {
    Destroy();
    const auto device = instance_.GetDevice();
    for (auto& s : staging_) {
        device.destroyBuffer(s.buffer);
        device.freeMemory(s.memory);
    }
    instance_.GetInstance().destroySurfaceKHR(surface_);
}

const char* Presenter::ModeName() const {
    switch (mode_) {
    case vk::PresentModeKHR::eImmediate: return "off-tearing (Immediate)";
    case vk::PresentModeKHR::eMailbox: return "off (Mailbox)";
    default: return "on (FIFO)";
    }
}

void Presenter::Destroy() {
    const auto device = instance_.GetDevice();
    (void)device.waitIdle();
    for (auto s : acquired_) device.destroySemaphore(s);
    for (auto s : ready_) device.destroySemaphore(s);
    acquired_.clear();
    ready_.clear();
    images_.clear();
    if (chain_) device.destroySwapchainKHR(chain_);
    chain_ = nullptr;
}

void Presenter::Create(uint32_t w, uint32_t h) {
    Destroy();
    want_w_ = w;
    want_h_ = h;
    out_of_date_ = false;
    const auto pd = instance_.GetPhysicalDevice();
    const auto device = instance_.GetDevice();
    const auto caps = pd.getSurfaceCapabilitiesKHR(surface_).value;
    extent_ = caps.currentExtent;
    if (extent_.width == UINT32_MAX) {
        extent_.width = std::clamp(w, caps.minImageExtent.width, caps.maxImageExtent.width);
        extent_.height = std::clamp(h, caps.minImageExtent.height, caps.maxImageExtent.height);
    }
    if (extent_.width == 0 || extent_.height == 0) return;  // minimised
    uint32_t count = std::max(caps.minImageCount + 1, 3u);
    if (caps.maxImageCount) count = std::min(count, caps.maxImageCount);
    vk::CompositeAlphaFlagBitsKHR alpha = vk::CompositeAlphaFlagBitsKHR::eOpaque;
    if (!(caps.supportedCompositeAlpha & alpha)) alpha = vk::CompositeAlphaFlagBitsKHR::eInherit;
    const std::array families{instance_.GetGraphicsQueueFamilyIndex(), instance_.GetPresentQueueFamilyIndex()};
    const bool same = families[0] == families[1];
    auto [r, chain] = device.createSwapchainKHR({
        .surface = surface_,
        .minImageCount = count,
        .imageFormat = format_.format,
        .imageColorSpace = format_.colorSpace,
        .imageExtent = extent_,
        .imageArrayLayers = 1,
        .imageUsage = vk::ImageUsageFlagBits::eColorAttachment | vk::ImageUsageFlagBits::eTransferDst,
        .imageSharingMode = same ? vk::SharingMode::eExclusive : vk::SharingMode::eConcurrent,
        .queueFamilyIndexCount = same ? 1u : 2u,
        .pQueueFamilyIndices = families.data(),
        .preTransform = caps.currentTransform,
        .compositeAlpha = alpha,
        .presentMode = mode_,
        .clipped = true,
    });
    if (r != vk::Result::eSuccess) {
        d1::log("present: cannot create the swapchain (%s)", vk::to_string(r).c_str());
        extent_ = vk::Extent2D{};
        return;
    }
    chain_ = chain;
    images_ = device.getSwapchainImagesKHR(chain_).value;
    for (size_t i = 0; i < images_.size(); ++i) {
        acquired_.push_back(device.createSemaphore({}).value);
        ready_.push_back(device.createSemaphore({}).value);
    }
    frame_ = 0;
    if (rebuilds_++ < 20)
        d1::log("present: swapchain %ux%u, %zu images, v-sync %s", extent_.width, extent_.height, images_.size(),
                ModeName());
}

bool Presenter::Acquire(uint32_t ww, uint32_t wh) {
    if (ww == 0 || wh == 0) return false;
    // Rebuild only when the window size changed or the driver says the swapchain is unusable;
    // "suboptimal" images are still presented.
    if (!chain_ || out_of_date_ || ww != want_w_ || wh != want_h_) Create(ww, wh);
    if (!chain_) return false;
    const auto r = instance_.GetDevice().acquireNextImageKHR(chain_, UINT64_MAX, acquired_[frame_], nullptr, &image_);
    if (r == vk::Result::eSuboptimalKHR) ++suboptimal_;
    if (r == vk::Result::eErrorOutOfDateKHR || r == vk::Result::eErrorSurfaceLostKHR) {
        out_of_date_ = true;
        ++failed_;
        return false;
    }
    if (r != vk::Result::eSuccess && r != vk::Result::eSuboptimalKHR) ++failed_;
    return r == vk::Result::eSuccess || r == vk::Result::eSuboptimalKHR;
}

void Presenter::Present() {
    const vk::PresentInfoKHR info{
        .waitSemaphoreCount = 1,
        .pWaitSemaphores = &ready_[image_],
        .swapchainCount = 1,
        .pSwapchains = &chain_,
        .pImageIndices = &image_,
    };
    const auto r = instance_.GetPresentQueue().presentKHR(info);
    if (r == vk::Result::eErrorOutOfDateKHR || r == vk::Result::eErrorSurfaceLostKHR) out_of_date_ = true;
    if (r == vk::Result::eSuboptimalKHR) ++suboptimal_;
    else if (r != vk::Result::eSuccess) ++failed_;
    ++presented_;
    frame_ = (frame_ + 1) % uint32_t(acquired_.size());
}

void Presenter::RecordOverlay(vk::CommandBuffer cmd, const std::vector<std::string>& lines) {
    namespace F = d1::overlay_font;
    size_t cols = 0;
    for (auto& l : lines) cols = std::max(cols, l.size());
    const uint32_t pad = 4;
    const uint32_t w = std::min<uint32_t>(uint32_t(cols) * F::kWidth + 2 * pad, kOverlayW);
    const uint32_t h = std::min<uint32_t>(uint32_t(lines.size()) * F::kHeight + 2 * pad, kOverlayH);
    const uint32_t x0 = 12, y0 = 12;
    if (x0 + w > extent_.width || y0 + h > extent_.height) return;
    const bool bgra = format_.format == vk::Format::eB8G8R8A8Unorm || format_.format == vk::Format::eB8G8R8A8Srgb;
    uint8_t* px = staging_[image_ % staging_.size()].data;
    for (uint32_t y = 0; y < h; ++y)
        for (uint32_t x = 0; x < w; ++x) {
            uint32_t cov = 0;
            const uint32_t line = (y - pad) / F::kHeight, col = (x - pad) / F::kWidth;
            if (y >= pad && x >= pad && line < lines.size() && col < lines[line].size()) {
                const unsigned char c = lines[line][col];
                if (c >= F::kFirst && c <= F::kLast)
                    cov = F::kGlyphs[c - F::kFirst][((y - pad) % F::kHeight) * F::kWidth + (x - pad) % F::kWidth];
            }
            // white text over a dark panel (copied, not blended)
            const uint8_t v = uint8_t(20 + cov * (255 - 20) / 255);
            uint8_t* p = px + (size_t(y) * w + x) * 4;
            const uint8_t g = v, r = cov ? v : 20, b = cov ? v : 24;
            p[0] = bgra ? b : r;
            p[1] = g;
            p[2] = bgra ? r : b;
            p[3] = 255;
        }
    const vk::BufferImageCopy region{
        .bufferOffset = 0,
        .bufferRowLength = w,
        .bufferImageHeight = h,
        .imageSubresource = {vk::ImageAspectFlagBits::eColor, 0, 0, 1},
        .imageOffset = {int32_t(x0), int32_t(y0), 0},
        .imageExtent = {w, h, 1},
    };
    cmd.copyBufferToImage(staging_[image_ % staging_.size()].buffer, Image(), vk::ImageLayout::eTransferDstOptimal,
                          region);
}

}  // namespace d1::render
