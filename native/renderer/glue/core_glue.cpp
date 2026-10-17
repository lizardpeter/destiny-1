// d1-native implementations of the shadPS4 emulator-core services that video_core calls:
// guest memory (the guest runs natively, so guest addresses are host addresses), fault
// dispatch, debug-state hooks and a few kernel queries.
#include <x86intrin.h>

#include <chrono>
#include <cstring>
#include <optional>
#include <vector>

#include "common/elf_info.h"
#include "core/address_space.h"
#include "core/debug_state.h"
#include "core/file_sys/ifile.h"
#include "core/libraries/kernel/process.h"
#include "core/libraries/kernel/threads/pthread.h"
#include "core/libraries/kernel/time.h"
#include "core/memory.h"
#include "core/signals.h"
#include "video_core/renderdoc.h"

#include "../../src/os.h"
#include "../../src/render_bridge.h"

// ---------------------------------------------------------------- address space
namespace Core {

struct AddressSpace::Impl {};
AddressSpace::AddressSpace() = default;
AddressSpace::~AddressSpace() = default;

void AddressSpace::Protect(VAddr addr, u64 size, MemoryPermission perms) {
    int prot = 0;
    if (True(perms & MemoryPermission::Read)) prot |= d1::os::kRead;
    if (True(perms & MemoryPermission::Write)) prot |= d1::os::kWrite;
    if (True(perms & MemoryPermission::Execute)) prot |= d1::os::kExec;
    d1::os::protect(reinterpret_cast<void*>(addr), size, prot);
}

boost::icl::interval_set<VAddr> AddressSpace::GetUsableRegions() {
    return {};
}

// ---------------------------------------------------------------- memory manager
MemoryManager::MemoryManager() = default;
MemoryManager::~MemoryManager() = default;

u64 MemoryManager::ClampRangeSize(VAddr addr, u64 size) {
    static constexpr u64 MinSizeToClamp = 1ull << 30;
    if (size < MinSizeToClamp) return size;
    const u64 extent = d1::guest_region_extent(addr);
    return extent ? std::min(size, extent) : size;
}

void MemoryManager::CopySparseMemory(VAddr src, u8* dst, u64 size) {
    std::memcpy(dst, reinterpret_cast<const void*>(src), size);
}

// GPU-side writes into guest memory must not trip the CPU write tracking, so they bypass
// page protection (/proc/self/mem on Linux, WriteProcessMemory on Windows).
bool MemoryManager::TryWriteBacking(void* address, const void* data, u64 size) {
    return d1::os::write_backing(address, data, size);
}

// ---------------------------------------------------------------- signals
SignalDispatch::SignalDispatch() = default;
SignalDispatch::~SignalDispatch() = default;
void SignalDispatch::RemoveHandlers() {}

bool SignalDispatch::DispatchAccessViolation(void* context, void* fault_address) const {
    for (const auto& h : access_violation_handlers)
        if (h.handler(context, fault_address)) return true;
    return false;
}
bool SignalDispatch::DispatchIllegalInstruction(void* context) const {
    for (const auto& h : illegal_instruction_handlers)
        if (h.handler(context)) return true;
    return false;
}

namespace FileSys {
bool IsZArchiveFile(const std::filesystem::path&) {
    return false;
}
std::optional<std::vector<u8>> ReadGameFile(const std::filesystem::path&, std::string_view) {
    return std::nullopt;
}
}  // namespace FileSys

}  // namespace Core

// ---------------------------------------------------------------- debug state (devtools off)
namespace DebugStateType {
void DebugStateImpl::PushRegsDump(uintptr_t, uintptr_t, const AmdGpu::Regs&) {}
void DebugStateImpl::PushRegsDumpCompute(uintptr_t, uintptr_t, const CsState&) {}
}  // namespace DebugStateType
DebugStateType::DebugStateImpl& DebugState = *Common::Singleton<DebugStateType::DebugStateImpl>::Instance();

namespace VideoCore {
void StartCapture() {}
void EndCapture() {}
}  // namespace VideoCore

// ---------------------------------------------------------------- kernel / gnm queries
namespace Libraries::Kernel {
thread_local Pthread* g_curthread = nullptr;

s32 PS4_SYSV_ABI sceKernelIsNeoMode() {
    return 0;  // base PS4
}
u64 PS4_SYSV_ABI sceKernelReadTsc() {
    return __rdtsc();
}
u64 PS4_SYSV_ABI sceKernelGetTscFrequency() {
    static const u64 freq = [] {
        const auto a = std::chrono::steady_clock::now();
        const u64 t0 = __rdtsc();
        d1::os::sleep_us(20000);
        const auto b = std::chrono::steady_clock::now();
        const u64 t1 = __rdtsc();
        const double s = std::chrono::duration<double>(b - a).count();
        return static_cast<u64>((t1 - t0) / s);
    }();
    return freq;
}
}  // namespace Libraries::Kernel

namespace Libraries::GnmDriver {
u32 PS4_SYSV_ABI sceGnmGetGpuCoreClockFrequency() {
    return 800'000'000;  // Liverpool, base PS4
}
}  // namespace Libraries::GnmDriver
