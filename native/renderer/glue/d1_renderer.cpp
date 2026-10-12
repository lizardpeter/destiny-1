// d1-native side of the temporary renderer: owns shadPS4's command processor (Liverpool)
// and Vulkan rasterizer, feeds them the game's command buffers, turns flip packets into
// video-out flips, and (optionally) saves displayed frames as PNG files.
//
// The Gnm command builders below follow shadPS4's libSceGnmDriver (GPL-2.0-or-later).
#include <png.h>
#include <sys/stat.h>

#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <mutex>
#include <string>

#include "common/elf_info.h"
#include "core/libraries/gnmdriver/gnmdriver_init.h"
#include "core/emulator_settings.h"
#include "core/libraries/videoout/buffer.h"
#include "core/memory.h"
#include "core/platform.h"
#include "core/signals.h"
#include "sdl_window.h"
#include "video_core/amdgpu/liverpool.h"
#include "video_core/amdgpu/pm4_cmds.h"
#include "video_core/buffer_cache/buffer.h"
#include "video_core/renderer_vulkan/vk_instance.h"
#include "video_core/renderer_vulkan/vk_rasterizer.h"
#include "video_core/renderer_vulkan/vk_runtime.h"
#include "video_core/renderer_vulkan/vk_scheduler.h"
#include "video_core/renderer_vulkan/vk_swapchain.h"
#include "video_core/texture_cache/texture_cache.h"

#include "../../src/render_bridge.h"
#include "d1_window.h"

namespace d1 {
void log(const char* fmt, ...);
}

namespace d1::render {

using namespace AmdGpu;
using Libraries::VideoOut::BufferAttributeGroup;

namespace {

struct State {
    Callbacks cb{};
    u32 sdk_version{};
    std::unique_ptr<Liverpool> liverpool;
    std::unique_ptr<Vulkan::Instance> instance;
    std::unique_ptr<Vulkan::Scheduler> scheduler;
    std::unique_ptr<Vulkan::Runtime> runtime;
    std::unique_ptr<Vulkan::Rasterizer> rasterizer;
    Frontend::WindowSDL* window{};  // null: offscreen only
    std::unique_ptr<Vulkan::Swapchain> swapchain;
    std::mutex submit_mutex;
    bool send_init_packet{true};
    BufferAttributeGroup group{};
    VAddr vo_buffers[16]{};
    // frame capture
    std::string frames_dir;
    u64 frame_every{60};
    std::atomic<u64> flips{0};
    std::atomic<u64> submits{0};
    std::atomic<u64> saved{0};
};
State* g = nullptr;

// ------------------------------------------------------------- frame capture
void write_png(const std::string& path, const u8* rgba, u32 w, u32 h, vk::Format fmt) {
    FILE* f = std::fopen(path.c_str(), "wb");
    if (!f) return;
    png_structp png = png_create_write_struct(PNG_LIBPNG_VER_STRING, nullptr, nullptr, nullptr);
    png_infop info = png_create_info_struct(png);
    if (setjmp(png_jmpbuf(png))) {
        png_destroy_write_struct(&png, &info);
        std::fclose(f);
        return;
    }
    png_init_io(png, f);
    png_set_compression_level(png, 3);
    png_set_IHDR(png, info, w, h, 8, PNG_COLOR_TYPE_RGB, PNG_INTERLACE_NONE, PNG_COMPRESSION_TYPE_DEFAULT,
                 PNG_FILTER_TYPE_DEFAULT);
    png_write_info(png, info);
    std::vector<u8> row(w * 3);
    for (u32 y = 0; y < h; ++y) {
        const u8* s = rgba + size_t(y) * w * 4;
        for (u32 x = 0; x < w; ++x, s += 4) {
            u8 r, gch, b;
            switch (fmt) {
            case vk::Format::eB8G8R8A8Srgb:
            case vk::Format::eB8G8R8A8Unorm:
                r = s[2], gch = s[1], b = s[0];
                break;
            case vk::Format::eA2R10G10B10UnormPack32:
            case vk::Format::eA2B10G10R10UnormPack32: {
                const u32 v = s[0] | (s[1] << 8) | (s[2] << 16) | (u32(s[3]) << 24);
                const u8 lo = u8((v >> 2) & 0xFF), mid = u8((v >> 12) & 0xFF), hi = u8((v >> 22) & 0xFF);
                if (fmt == vk::Format::eA2R10G10B10UnormPack32) r = hi, gch = mid, b = lo;
                else r = lo, gch = mid, b = hi;
                break;
            }
            default:
                r = s[0], gch = s[1], b = s[2];
                break;
            }
            row[x * 3] = r, row[x * 3 + 1] = gch, row[x * 3 + 2] = b;
        }
        png_write_row(png, row.data());
    }
    png_write_end(png, nullptr);
    png_destroy_write_struct(&png, &info);
    std::fclose(f);
}

// Runs on the GPU thread, in order with the command stream.
void capture(s32 index) {
    if (g->frames_dir.empty() || index < 0 || !g->vo_buffers[index]) return;
    const u64 n = g->flips.load();
    if (n != 1 && n % g->frame_every != 0) return;
    auto& tc = g->rasterizer->GetTextureCache();
    auto desc = VideoCore::TextureCache::ImageDesc{g->group, g->vo_buffers[index]};
    const auto id = tc.FindImage(desc);
    tc.UpdateImage(id);
    auto& image = tc.GetImage(id);
    const u32 w = image.info.size.width, h = image.info.size.height;
    VideoCore::Buffer buf{*g->instance, 0, u64(w) * h * 4, VideoCore::MemoryType::HostCached};
    const vk::BufferImageCopy region{
        .bufferOffset = 0,
        .bufferRowLength = 0,
        .bufferImageHeight = 0,
        .imageSubresource{.aspectMask = vk::ImageAspectFlagBits::eColor, .mipLevel = 0, .baseArrayLayer = 0, .layerCount = 1},
        .imageOffset = {0, 0, 0},
        .imageExtent = {w, h, 1},
    };
    g->runtime->DownloadImage(&image, &buf, std::span{&region, 1});
    g->scheduler->Finish();
    char name[64];
    std::snprintf(name, sizeof name, "/frame_%06lu.png", n);
    write_png(g->frames_dir + name, buf.mapped_data.data(), w, h, image.info.pixel_format);
    ++g->saved;
    d1::log("renderer: saved %s%s (%ux%u, %s)", g->frames_dir.c_str(), name, w, h,
            vk::to_string(image.info.pixel_format).c_str());
}

// Blit the displayed buffer into the window, letterboxed. Runs on the GPU thread.
void present(s32 index) {
    if (!g->swapchain || index < 0 || !g->vo_buffers[index]) return;
    auto& sc = *g->swapchain;
    const u32 ww = u32(g->window->GetWidth()), wh = u32(g->window->GetHeight());
    if (ww == 0 || wh == 0) return;
    if (ww != sc.GetWidth() || wh != sc.GetHeight()) sc.Recreate(ww, wh);
    if (!sc.AcquireNextImage()) {
        sc.Recreate(ww, wh);
        if (!sc.AcquireNextImage()) return;
    }
    auto& tc = g->rasterizer->GetTextureCache();
    auto desc = VideoCore::TextureCache::ImageDesc{g->group, g->vo_buffers[index]};
    const auto id = tc.FindImage(desc);
    tc.UpdateImage(id);
    auto& image = tc.GetImage(id);
    const s32 iw = s32(image.info.size.width), ih = s32(image.info.size.height);

    g->scheduler->EndRendering();
    g->runtime->Transit(&image, vk::ImageLayout::eTransferSrcOptimal, vk::PipelineStageFlagBits2::eBlit,
                        vk::AccessFlagBits2::eTransferRead);
    g->runtime->FlushBarriers();
    const auto cmdbuf = g->scheduler->CommandBuffer();
    const vk::ImageSubresourceRange range{vk::ImageAspectFlagBits::eColor, 0, 1, 0, 1};
    const vk::ImageMemoryBarrier2 to_dst{
        .srcStageMask = vk::PipelineStageFlagBits2::eAllCommands,
        .srcAccessMask = vk::AccessFlagBits2::eNone,
        .dstStageMask = vk::PipelineStageFlagBits2::eAllTransfer,
        .dstAccessMask = vk::AccessFlagBits2::eTransferWrite,
        .oldLayout = vk::ImageLayout::eUndefined,
        .newLayout = vk::ImageLayout::eTransferDstOptimal,
        .image = sc.Image(),
        .subresourceRange = range,
    };
    cmdbuf.pipelineBarrier2(vk::DependencyInfo{.imageMemoryBarrierCount = 1, .pImageMemoryBarriers = &to_dst});
    const vk::ClearColorValue black{std::array<float, 4>{0.f, 0.f, 0.f, 1.f}};
    cmdbuf.clearColorImage(sc.Image(), vk::ImageLayout::eTransferDstOptimal, black, range);
    // fit the game image into the window, keeping its aspect ratio
    s32 dw = s32(ww), dh = s32(int64_t(ww) * ih / iw);
    if (dh > s32(wh)) dh = s32(wh), dw = s32(int64_t(wh) * iw / ih);
    const s32 dx = (s32(ww) - dw) / 2, dy = (s32(wh) - dh) / 2;
    const vk::ImageBlit blit{
        .srcSubresource = {vk::ImageAspectFlagBits::eColor, 0, 0, 1},
        .srcOffsets = std::array{vk::Offset3D{0, 0, 0}, vk::Offset3D{iw, ih, 1}},
        .dstSubresource = {vk::ImageAspectFlagBits::eColor, 0, 0, 1},
        .dstOffsets = std::array{vk::Offset3D{dx, dy, 0}, vk::Offset3D{dx + dw, dy + dh, 1}},
    };
    const vk::MemoryBarrier2 clear_done{
        .srcStageMask = vk::PipelineStageFlagBits2::eAllTransfer,
        .srcAccessMask = vk::AccessFlagBits2::eTransferWrite,
        .dstStageMask = vk::PipelineStageFlagBits2::eAllTransfer,
        .dstAccessMask = vk::AccessFlagBits2::eTransferWrite,
    };
    cmdbuf.pipelineBarrier2(vk::DependencyInfo{.memoryBarrierCount = 1, .pMemoryBarriers = &clear_done});
    cmdbuf.blitImage(image.GetImage(), vk::ImageLayout::eTransferSrcOptimal, sc.Image(),
                     vk::ImageLayout::eTransferDstOptimal, blit, vk::Filter::eLinear);
    const vk::ImageMemoryBarrier2 to_present{
        .srcStageMask = vk::PipelineStageFlagBits2::eAllTransfer,
        .srcAccessMask = vk::AccessFlagBits2::eTransferWrite,
        .dstStageMask = vk::PipelineStageFlagBits2::eAllCommands,
        .dstAccessMask = vk::AccessFlagBits2::eNone,
        .oldLayout = vk::ImageLayout::eTransferDstOptimal,
        .newLayout = vk::ImageLayout::ePresentSrcKHR,
        .image = sc.Image(),
        .subresourceRange = range,
    };
    cmdbuf.pipelineBarrier2(vk::DependencyInfo{.imageMemoryBarrierCount = 1, .pImageMemoryBarriers = &to_present});
    Vulkan::SubmitInfo info{};
    info.AddWait(sc.GetImageAcquiredSemaphore());
    info.AddSignal(sc.GetPresentReadySemaphore());
    g->scheduler->Flush(info);
    sc.Present();
}

void flip_on_gpu(s32 index, s64 arg) {
    ++g->flips;
    capture(index);
    present(index);
    g->cb.flip(index, arg);
}

// ------------------------------------------------------------- PM4 helpers
inline u32* WriteNop(u32* cmdbuf, u32 data_block_size) {
    auto* nop = reinterpret_cast<PM4CmdNop*>(cmdbuf);
    nop->header = PM4Type3Header{PM4ItOpcode::Nop, data_block_size - 1};
    nop->data_block[0] = 0u;
    return cmdbuf + data_block_size + 1;
}
template <u32 N>
inline u32* WriteNop(u32* cmdbuf) {
    return WriteNop(cmdbuf, N);
}
inline u32* ClearContextState(u32* cmdbuf) {
    static constexpr std::array ClearStateSequence{
        0xc0012800u, 0x80000000u, 0x80000000u, 0xc0001200u, 0u, 0xc0055800u,
        0x2ec47fc0u, 0xffffffffu, 0u,          0u,          0u, 10u,
    };
    std::memcpy(cmdbuf, ClearStateSequence.data(), ClearStateSequence.size() * 4);
    return cmdbuf + ClearStateSequence.size();
}

void send_init_sequence() {
    if (!g->send_init_packet) return;
    using Common::ElfInfo;
    if (g->sdk_version < ElfInfo::FW_200) g->liverpool->SubmitGfx(Libraries::GnmDriver::InitSequence, {});
    else if (g->sdk_version < ElfInfo::FW_400) g->liverpool->SubmitGfx(Libraries::GnmDriver::InitSequence200, {});
    else g->liverpool->SubmitGfx(Libraries::GnmDriver::InitSequence350, {});
    g->send_init_packet = false;
}

void perform_submit(u32 count, u32* const* dcbs, const u32* dcb_sizes, u32* const* ccbs, const u32* ccb_sizes) {
    send_init_sequence();
    for (u32 i = 0; i < count; ++i) {
        const u32* ccb = ccbs ? ccbs[i] : nullptr;
        const u32 ccb_bytes = (ccb_sizes && ccb) ? ccb_sizes[i] : 0;
        g->liverpool->SubmitGfx(std::span<const u32>{dcbs[i], dcb_sizes[i] / 4}, std::span<const u32>{ccb, ccb_bytes / 4});
    }
    ++g->submits;
}

// The game ends a frame's last DCB with a 64-dword `prepareFlip` NOP; the driver rewrites
// it into a label write plus a flip marker that the command processor turns into GfxFlip.
bool patch_flip_request(u32* cmdbuf, u32 size_dw, u32 buf_idx) {
    cmdbuf += size_dw - 64;
    if (cmdbuf[0] != 0xc03e1000) return false;
    std::array<u32, 7> backup{};
    std::memcpy(backup.data(), cmdbuf, sizeof backup);

    auto* write_lock = reinterpret_cast<PM4CmdWriteData*>(cmdbuf);
    write_lock->header = PM4Type3Header{PM4ItOpcode::WriteData, 3};
    write_lock->raw = 0x500u;
    write_lock->Address<uintptr_t>(reinterpret_cast<uintptr_t>(&g->cb.labels[buf_idx]) & ~0x3ull);
    write_lock->data[0] = 1;

    auto* nop = reinterpret_cast<PM4CmdNop*>(cmdbuf + 5);
    if (backup[1] == PM4CmdNop::PayloadType::PrepareFlip) {
        nop->header = PM4Type3Header{PM4ItOpcode::Nop, 0x39};
        nop->data_block[0] = PM4CmdNop::PayloadType::PatchedFlip;
    } else if (backup[1] == PM4CmdNop::PayloadType::PrepareFlipLabel) {
        nop->header = PM4Type3Header{PM4ItOpcode::Nop, 0x34};
        nop->data_block[0] = PM4CmdNop::PayloadType::PatchedFlip;
        auto* write_label = reinterpret_cast<PM4CmdWriteData*>(cmdbuf + 0x3b);
        write_label->header = PM4Type3Header{PM4ItOpcode::WriteData, 3};
        write_label->raw = 0x500u;
        write_label->dst_addr_lo = backup[2] & 0xffff'fffcu;
        write_label->dst_addr_hi = backup[3];
        write_label->data[0] = backup[4];
    } else if (backup[1] == PM4CmdNop::PayloadType::PrepareFlipInterruptLabel) {
        nop->header = PM4Type3Header{PM4ItOpcode::Nop, 0x33};
        nop->data_block[0] = PM4CmdNop::PayloadType::PatchedFlip;
        auto* write_eop = reinterpret_cast<PM4CmdEventWriteEop*>(cmdbuf + 0x3a);
        write_eop->header = PM4Type3Header{PM4ItOpcode::EventWriteEop, 4};
        write_eop->event_control = (backup[5] & 0x3f) + 0x500u + (backup[6] & 0x3f) * 0x1000;
        write_eop->address_lo = backup[2] & 0xffff'fffcu;
        write_eop->data_control = (backup[3] & 0xffffu) | 0x2200'0000u;
        write_eop->data_lo = backup[4];
        write_eop->data_hi = 0u;
    } else if (backup[1] == PM4CmdNop::PayloadType::PrepareFlipInterrupt) {
        nop->header = PM4Type3Header{PM4ItOpcode::Nop, 0x33};
        nop->data_block[0] = PM4CmdNop::PayloadType::PatchedFlip;
        auto* write_eop = reinterpret_cast<PM4CmdEventWriteEop*>(cmdbuf + 0x3a);
        write_eop->header = PM4Type3Header{PM4ItOpcode::EventWriteEop, 4};
        write_eop->event_control = (backup[5] & 0x3f) + 0x500u + (backup[6] & 0x3f) * 0x1000;
        write_eop->address_lo = 0u;
        write_eop->data_control = 0x100'0000u;
        write_eop->data_lo = 0u;
        write_eop->data_hi = 0u;
    }
    return true;
}

}  // namespace

// ------------------------------------------------------------- lifecycle
bool init(const Callbacks& cb) {
    if (const char* v = std::getenv("D1_RENDERER"); v && v[0] == '0') return false;
    g = new State;
    g->cb = cb;
    g->sdk_version = cb.sdk_version;
    if (const char* d = std::getenv("D1_FRAMES")) {
        g->frames_dir = d;
        mkdir(d, 0755);
    }
    if (const char* e = std::getenv("D1_FRAME_EVERY")) g->frame_every = std::max(1L, std::atol(e));
    try {
        g->liverpool = std::make_unique<Liverpool>();
        static Frontend::WindowSDL headless;  // window system "Headless": no surface, offscreen only
        if (cb.present_mode) EmulatorSettings.present_mode = cb.present_mode;
        g->window = window::open(cb.window_width, cb.window_height, cb.fullscreen);
        g->instance = std::make_unique<Vulkan::Instance>(g->window ? *g->window : headless, EmulatorSettings.GetGpuId(),
                                                         EmulatorSettings.IsVkValidationEnabled(), false);
        g->scheduler = std::make_unique<Vulkan::Scheduler>(*g->instance);
        g->runtime = std::make_unique<Vulkan::Runtime>(*g->instance, *g->scheduler);
        g->rasterizer = std::make_unique<Vulkan::Rasterizer>(*g->instance, *g->scheduler, *g->runtime, g->liverpool.get());
        if (g->window) {
            g->swapchain = std::make_unique<Vulkan::Swapchain>(*g->instance, *g->window);
            d1::log("renderer: present mode %s", EmulatorSettings.GetPresentMode().c_str());
        }
    } catch (const std::exception& e) {
        d1::log("renderer: Vulkan initialisation failed (%s); using the null GPU", e.what());
        delete g;
        g = nullptr;
        return false;
    }
    Core::Memory::Instance()->SetRasterizer(g->rasterizer.get());

    static int irq_uid;
    Platform::IrqC::Instance()->Register(Platform::InterruptId::GfxEop, [](Platform::InterruptId) { g->cb.eop(); },
                                         &irq_uid);
    d1::log("renderer: shadPS4 video_core on %s (Vulkan %u.%u)",
            g->instance->GetPhysicalDevice().getProperties().deviceName.data(),
            VK_API_VERSION_MAJOR(g->instance->ApiVersion()), VK_API_VERSION_MINOR(g->instance->ApiVersion()));
    return true;
}

bool active() {
    return g != nullptr;
}

void register_buffers(s32 start, void* const* addrs, s32 num, const VoAttr& attr) {
    if (!g) return;
    g->group.is_occupied = true;
    std::memcpy(&g->group.attrib, &attr, sizeof attr);
    for (s32 i = 0; i < num && start + i < 16; ++i) {
        const VAddr a = reinterpret_cast<VAddr>(addrs[i]);
        g->vo_buffers[start + i] = a;
        auto desc = VideoCore::TextureCache::ImageDesc{g->group, a};
        auto& tc = g->rasterizer->GetTextureCache();
        auto& image = tc.GetImage(tc.FindImage(desc));
        image.usage.vo_surface = 1u;
    }
}

void submit(u32 count, u32* const* dcbs, const u32* dcb_sizes, u32* const* ccbs, const u32* ccb_sizes) {
    std::scoped_lock lk{g->submit_mutex};
    perform_submit(count, dcbs, dcb_sizes, ccbs, ccb_sizes);
}

s32 submit_and_flip(u32 count, u32* const* dcbs, const u32* dcb_sizes, u32* const* ccbs, const u32* ccb_sizes,
                    u32 buf, s64 arg) {
    std::scoped_lock lk{g->submit_mutex};
    if (count && patch_flip_request(dcbs[count - 1], dcb_sizes[count - 1] / 4, buf)) {
        Platform::IrqC::Instance()->RegisterOnce(Platform::InterruptId::GfxFlip,
                                                 [buf, arg](Platform::InterruptId) { flip_on_gpu(s32(buf), arg); });
        perform_submit(count, dcbs, dcb_sizes, ccbs, ccb_sizes);
    } else {
        static bool warned;
        if (!warned) {
            warned = true;
            d1::log("renderer: no prepareFlip packet at the end of the DCB; flipping after the submit");
        }
        perform_submit(count, dcbs, dcb_sizes, ccbs, ccb_sizes);
        g->liverpool->SendCommand([buf, arg] { flip_on_gpu(s32(buf), arg); });
    }
    return 0;
}

void cpu_flip(s32 index, s64 arg) {
    g->liverpool->SendCommand([index, arg] { flip_on_gpu(index, arg); });
}

void submit_done() {
    std::scoped_lock lk{g->submit_mutex};
    g->liverpool->SubmitDone();
    g->send_init_packet = true;
}

void on_map(u64 addr, u64 size) {
    if (!g || addr + size >= 0x10000000000ull) return;
    g->rasterizer->MapMemory(addr, size);
    g->rasterizer->RegisterMemory(addr, size);
}

void on_unmap(u64 addr, u64 size) {
    if (!g || addr + size >= 0x10000000000ull) return;
    g->rasterizer->UnmapMemory(addr, size);
}

bool on_fault(void* ucontext, void* addr) {
    if (!g) return false;
    return Core::Signals::Instance()->DispatchAccessViolation(ucontext, addr);
}

void print_summary() {
    if (!g) return;
    d1::log("renderer: %lu submits, %lu flips, %lu frames saved", g->submits.load(), g->flips.load(), g->saved.load());
}

// ------------------------------------------------------------- Gnm command builders
u32 draw_init_default_hw_state(u32* cmdbuf, u32 size) {
    using Libraries::GnmDriver::HwInitPacketSize;
    using Libraries::GnmDriver::InitSequence;
    if (size < HwInitPacketSize) return 0;
    const auto* end = cmdbuf + HwInitPacketSize;
    cmdbuf = ClearContextState(cmdbuf);
    std::memcpy(cmdbuf, &InitSequence[2], (InitSequence.size() - 2) * 4);
    cmdbuf += InitSequence.size() - 2;
    WriteNop(cmdbuf, u32(end - cmdbuf - 1));
    return HwInitPacketSize;
}

u32 dispatch_init_default_hw_state(u32* cmdbuf, u32 size) {
    using Libraries::GnmDriver::HwInitPacketSize;
    if (size < HwInitPacketSize) return 0;
    cmdbuf = PM4CmdSetData::SetShReg<PM4ShaderType::ShaderCompute>(cmdbuf, 0x216u, 0xffffffffu);
    cmdbuf = PM4CmdSetData::SetShReg<PM4ShaderType::ShaderCompute>(cmdbuf, 0x217u, 0xffffffffu);
    cmdbuf = PM4CmdSetData::SetShReg<PM4ShaderType::ShaderCompute>(cmdbuf, 0x215u, 0x170u);
    cmdbuf = WriteHeader<PM4ItOpcode::AcquireMem>(cmdbuf, 6);
    cmdbuf = WriteBody(cmdbuf, 0x28000000u, 0u, 0u, 0u, 0u, 0xau);
    cmdbuf = WriteHeader<PM4ItOpcode::Nop>(cmdbuf, 0xef);
    cmdbuf = WriteBody(cmdbuf, 0u);
    return HwInitPacketSize;
}

s32 insert_wait_flip_done(u32* cmdbuf, u32 size, u32 buf_idx) {
    if (size != 7) return -1;
    auto* w = reinterpret_cast<PM4CmdWaitRegMem*>(cmdbuf);
    w->header = PM4Type3Header{PM4ItOpcode::WaitRegMem, 5};
    w->raw = 0x13u;
    *reinterpret_cast<uintptr_t*>(&w->poll_addr_lo) = reinterpret_cast<uintptr_t>(&g->cb.labels[buf_idx]) & ~0x3ull;
    w->ref = 0u;
    w->mask = 0xffff'ffffu;
    w->poll_interval = 10u;
    return 0;
}

s32 set_cs_shader(u32* cmdbuf, u32 size, const u32* r) {
    if (!cmdbuf || size <= 0x18 || !r || r[1] != 0) return -1;
    cmdbuf = PM4CmdSetData::SetShReg(cmdbuf, 0x20cu, r[0], 0u);
    cmdbuf = PM4CmdSetData::SetShReg(cmdbuf, 0x212u, r[2], r[3]);
    cmdbuf = PM4CmdSetData::SetShReg(cmdbuf, 0x207u, r[4], r[5], r[6]);
    WriteNop<11>(cmdbuf);
    return 0;
}

s32 set_es_shader(u32* cmdbuf, u32 size, const u32* r, u32 mod) {
    if (!cmdbuf || size < 0x14 || !r || (mod & 0xfcfffc3f) || r[1] != 0) return -1;
    const u32 var = mod == 0 ? r[2] : ((r[2] & 0xfcfffc3f) | mod);
    cmdbuf = PM4CmdSetData::SetShReg(cmdbuf, 0xc8u, r[0], 0u);
    cmdbuf = PM4CmdSetData::SetShReg(cmdbuf, 0xcau, var, r[3]);
    WriteNop<11>(cmdbuf);
    return 0;
}

s32 set_gs_shader(u32* cmdbuf, u32 size, const u32* r) {
    if (!cmdbuf || size < 0x1d || !r || r[1] != 0) return -1;
    cmdbuf = PM4CmdSetData::SetShReg(cmdbuf, 0x88u, r[0], 0u);
    cmdbuf = PM4CmdSetData::SetShReg(cmdbuf, 0x8au, r[2], r[3]);
    cmdbuf = PM4CmdSetData::SetContextReg(cmdbuf, 0x2e5u, r[4]);
    cmdbuf = PM4CmdSetData::SetContextReg(cmdbuf, 0x29bu, r[5]);
    cmdbuf = PM4CmdSetData::SetContextReg(cmdbuf, 0x2e4u, r[6]);
    WriteNop<11>(cmdbuf);
    return 0;
}

s32 set_hs_shader(u32* cmdbuf, u32 size, const u32* r, u32 param4) {
    if (!cmdbuf || size < 0x1E || !r || r[1] != 0) return -1;
    cmdbuf = PM4CmdSetData::SetShReg(cmdbuf, 0x108u, r[0], 0u);
    cmdbuf = PM4CmdSetData::SetShReg(cmdbuf, 0x10au, r[2], r[3]);
    cmdbuf = PM4CmdSetData::SetContextReg(cmdbuf, 0x286u, r[5], r[6]);
    cmdbuf = PM4CmdSetData::SetContextReg(cmdbuf, 0x2dbu, r[4]);
    cmdbuf = PM4CmdSetData::SetContextReg(cmdbuf, 0x2d6u, param4);
    WriteNop<11>(cmdbuf);
    return 0;
}

s32 set_ls_shader(u32* cmdbuf, u32 size, const u32* r, u32 mod) {
    if (!cmdbuf || size < 0x17 || !r) return -1;
    const u32 mask = ((mod & 0xfffffc3f) == 0) ? 0xfffffc3f : 0xfcfffc3f;
    if ((mod & mask) || r[1] != 0) return -1;
    const u32 var = mod == 0 ? r[2] : ((r[2] & mask) | mod);
    cmdbuf = PM4CmdSetData::SetShReg(cmdbuf, 0x148u, r[0], 0u);
    cmdbuf = PM4CmdSetData::SetShReg(cmdbuf, 0x14bu, r[3]);
    cmdbuf = PM4CmdSetData::SetShReg(cmdbuf, 0x14au, var, r[3]);
    WriteNop<11>(cmdbuf);
    return 0;
}

s32 set_ps_shader(u32* cmdbuf, u32 size, const u32* r) {
    if (!cmdbuf || size <= 0x27) return -1;
    if (!r) {
        cmdbuf = PM4CmdSetData::SetShReg(cmdbuf, 8u, 0u, 0u);
        cmdbuf = PM4CmdSetData::SetContextReg(cmdbuf, 0x203u, 0u);
        WriteNop<0x20>(cmdbuf);
        return 0;
    }
    if (r[1] != 0) return -1;
    cmdbuf = PM4CmdSetData::SetShReg(cmdbuf, 8u, r[0], 0u);
    cmdbuf = PM4CmdSetData::SetShReg(cmdbuf, 10u, r[2], r[3]);
    cmdbuf = PM4CmdSetData::SetContextReg(cmdbuf, 0x1c4u, r[4], r[5]);
    cmdbuf = PM4CmdSetData::SetContextReg(cmdbuf, 0x1b3u, r[6], r[7]);
    cmdbuf = PM4CmdSetData::SetContextReg(cmdbuf, 0x1b6u, r[8]);
    cmdbuf = PM4CmdSetData::SetContextReg(cmdbuf, 0x1b8u, r[9]);
    cmdbuf = PM4CmdSetData::SetContextReg(cmdbuf, 0x203u, r[10]);
    cmdbuf = PM4CmdSetData::SetContextReg(cmdbuf, 0x8fu, r[11]);
    WriteNop<11>(cmdbuf);
    return 0;
}

s32 set_vs_shader(u32* cmdbuf, u32 size, const u32* r, u32 mod) {
    if (!cmdbuf || size <= 0x1c || !r || (mod & 0xfcfffc3f) || r[1] != 0) return -1;
    const u32 var = mod == 0 ? r[2] : (r[2] & 0xfcfffc3f) | mod;
    cmdbuf = PM4CmdSetData::SetShReg(cmdbuf, 0x48u, r[0], 0u);
    cmdbuf = PM4CmdSetData::SetShReg(cmdbuf, 0x4au, var, r[3]);
    cmdbuf = PM4CmdSetData::SetContextReg(cmdbuf, 0x207u, r[6]);
    cmdbuf = PM4CmdSetData::SetContextReg(cmdbuf, 0x1b1u, r[4]);
    cmdbuf = PM4CmdSetData::SetContextReg(cmdbuf, 0x1c3u, r[5]);
    WriteNop<11>(cmdbuf);
    return 0;
}

}  // namespace d1::render
