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
    bool IsPipelineCacheEnabled() const { return false; }
    bool IsDumpShaders() const { return Env("D1_DUMP_SHADERS"); }
    bool IsShaderCollect() const { return false; }
    bool IsRenderdocEnabled() const { return false; }
    bool IsNullGPU() const { return false; }
    bool IsHdrAllowed() const { return false; }
    bool IsDirectMemoryAccessEnabled() const { return false; }
    u32 GetReadbacksMode() const { return GpuReadbacksMode::Disabled; }
    std::string GetPresentMode() const { return "Fifo"; }
    bool IsVkValidationSyncEnabled() const { return false; }
    bool IsVkValidationGpuEnabled() const { return false; }
    bool IsVkValidationEnabled() const { return Env("D1_VK_VALIDATION"); }
    bool IsVkValidationCoreEnabled() const { return Env("D1_VK_VALIDATION"); }
    bool IsVkCrashDiagnosticEnabled() const { return false; }
    bool IsUserfaultfdTracking() const { return false; }
    bool IsReadbackLinearImagesEnabled() const { return false; }
    bool IsRcasEnabled() const { return false; }
    bool IsPatchShaders() const { return false; }
    bool IsInlineFetchShader() const { return true; }
    bool IsFsrEnabled() const { return false; }
    bool IsCopyGpuBuffers() const { return false; }
    float GetRcasAttenuation() const { return 0.25f; }
    int GetGpuId() const { return -1; }
};

#define EmulatorSettings (*EmulatorSettingsImpl::GetInstance())
