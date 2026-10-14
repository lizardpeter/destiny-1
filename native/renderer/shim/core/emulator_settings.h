// d1-native shim: the subset of shadPS4's EmulatorSettings that video_core reads.
#pragma once
#include <cstdlib>
#include <string>

#include "common/types.h"

enum GpuReadbacksMode : int { Disabled, Relaxed, Precise };

class EmulatorSettingsImpl {
public:
    static EmulatorSettingsImpl* GetInstance() {
        static EmulatorSettingsImpl s;
        return &s;
    }
    static bool Env(const char* n) { return std::getenv(n) != nullptr; }
    bool IsVkHostMarkersEnabled() const { return false; }
    bool IsVkGuestMarkersEnabled() const { return false; }
    bool IsPipelineCacheArchived() const { return false; }
    bool IsPipelineCacheEnabled() const { return pipeline_cache; }
    void SetPipelineCacheEnabled(bool v) { pipeline_cache = v; }
    bool pipeline_cache = false;  // render::init turns it on with a cache folder
    bool IsDumpShaders() const { return Env("D1_DUMP_SHADERS"); }
    bool IsShaderCollect() const { return false; }
    bool IsRenderdocEnabled() const { return false; }
    bool IsNullGPU() const { return false; }
    bool IsHdrAllowed() const { return false; }
    bool IsDirectMemoryAccessEnabled() const { return false; }
    u32 GetReadbacksMode() const { return GpuReadbacksMode::Disabled; }
    // From the vsync setting: Fifo (on) | Mailbox (off, no tearing) | Immediate (off-tearing).
    // D1_PRESENT still overrides with a raw mode name.
    std::string GetPresentMode() const {
        if (const char* v = std::getenv("D1_PRESENT")) return v;
        return present_mode;
    }
    std::string present_mode = "Mailbox";
    bool IsVkValidationSyncEnabled() const { return false; }
    bool IsVkValidationGpuEnabled() const { return false; }
    bool IsVkValidationEnabled() const { return Env("D1_VK_VALIDATION"); }
    bool IsVkValidationCoreEnabled() const { return Env("D1_VK_VALIDATION"); }
    bool IsVkCrashDiagnosticEnabled() const { return false; }
    bool IsUserfaultfdTracking() const { return false; }
    bool IsReadbackLinearImagesEnabled() const { return false; }
    bool IsRcasEnabled() const { return false; }
    bool IsPatchShaders() const { return false; }
    // Stock shadPS4 default (vertex input attributes). D1_INLINE_FETCH=1 translates fetch
    // shaders inline as buffer loads instead (shadPS4's debugging path, slower).
    bool IsInlineFetchShader() const { return Env("D1_INLINE_FETCH"); }
    bool IsFsrEnabled() const { return false; }
    bool IsCopyGpuBuffers() const { return false; }
    float GetRcasAttenuation() const { return 0.25f; }
    // -1 = shadPS4's picker; D1_GPU_ID=<n> picks the n-th Vulkan device.
    int GetGpuId() const {
        const char* v = std::getenv("D1_GPU_ID");
        return v ? std::atoi(v) : -1;
    }
};

#define EmulatorSettings (*EmulatorSettingsImpl::GetInstance())
