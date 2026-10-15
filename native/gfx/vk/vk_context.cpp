// Vulkan loader and device creation for the native renderer. See vk.h.
#include "vk.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#ifdef _WIN32
#include <windows.h>
#else
#include <dlfcn.h>
#endif

namespace d1::vk {

#define D1_VK_DEFINE(f) PFN_##f f = nullptr;
D1_VK_GLOBAL_FUNCS(D1_VK_DEFINE)
D1_VK_INSTANCE_FUNCS(D1_VK_DEFINE)
D1_VK_DEVICE_FUNCS(D1_VK_DEFINE)
#undef D1_VK_DEFINE

namespace {

PFN_vkGetInstanceProcAddr g_gipa = nullptr;

bool open_loader() {
    if (g_gipa) return true;
#ifdef _WIN32
    HMODULE lib = LoadLibraryA("vulkan-1.dll");
    if (!lib) return false;
    g_gipa = reinterpret_cast<PFN_vkGetInstanceProcAddr>(reinterpret_cast<void*>(GetProcAddress(lib, "vkGetInstanceProcAddr")));
#else
    void* lib = dlopen("libvulkan.so.1", RTLD_NOW | RTLD_LOCAL);
    if (!lib) lib = dlopen("libvulkan.so", RTLD_NOW | RTLD_LOCAL);
    if (!lib) return false;
    g_gipa = reinterpret_cast<PFN_vkGetInstanceProcAddr>(dlsym(lib, "vkGetInstanceProcAddr"));
#endif
    if (!g_gipa) return false;
#define D1_VK_LOAD(f) f = reinterpret_cast<PFN_##f>(g_gipa(VK_NULL_HANDLE, #f));
    D1_VK_GLOBAL_FUNCS(D1_VK_LOAD)
#undef D1_VK_LOAD
    return vkCreateInstance != nullptr;
}

bool has_extension(const std::vector<VkExtensionProperties>& list, const char* name) {
    for (auto& e : list)
        if (std::strcmp(e.extensionName, name) == 0) return true;
    return false;
}

}  // namespace

uint32_t find_memory_type(const Context& ctx, uint32_t type_bits, VkMemoryPropertyFlags want) {
    for (uint32_t i = 0; i < ctx.memory.memoryTypeCount; ++i)
        if ((type_bits >> i & 1) && (ctx.memory.memoryTypes[i].propertyFlags & want) == want) return i;
    return UINT32_MAX;
}

bool create_context(Context& ctx, int gpu_index, const char** inst_exts, uint32_t num_inst_exts, char* err,
                    size_t err_size) {
    auto fail = [&](const char* fmt, auto... args) {
        std::snprintf(err, err_size, fmt, args...);
        return false;
    };
    if (!open_loader()) return fail("no Vulkan loader (vulkan-1.dll / libvulkan.so.1)");
    uint32_t loader_version = VK_API_VERSION_1_0;
    if (vkEnumerateInstanceVersion) vkEnumerateInstanceVersion(&loader_version);
    // An older loader still passes a 1.4 request through to a 1.4 driver; what matters is
    // the device's version, checked below.
    (void)loader_version;

    VkApplicationInfo app{VK_STRUCTURE_TYPE_APPLICATION_INFO};
    app.pApplicationName = "Destiny (d1-native)";
    app.pEngineName = "d1-native";
    app.apiVersion = VK_API_VERSION_1_4;
    VkInstanceCreateInfo ici{VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO};
    ici.pApplicationInfo = &app;
    ici.enabledExtensionCount = num_inst_exts;
    ici.ppEnabledExtensionNames = inst_exts;
    const char* validation = "VK_LAYER_KHRONOS_validation";
    if (std::getenv("D1_VK_VALIDATION")) {
        ici.enabledLayerCount = 1;
        ici.ppEnabledLayerNames = &validation;
    }
    if (vkCreateInstance(&ici, nullptr, &ctx.instance) != VK_SUCCESS) return fail("vkCreateInstance failed");
#define D1_VK_LOAD(f) f = reinterpret_cast<PFN_##f>(g_gipa(ctx.instance, #f));
    D1_VK_INSTANCE_FUNCS(D1_VK_LOAD)
#undef D1_VK_LOAD

    uint32_t n = 0;
    vkEnumeratePhysicalDevices(ctx.instance, &n, nullptr);
    std::vector<VkPhysicalDevice> gpus(n);
    vkEnumeratePhysicalDevices(ctx.instance, &n, gpus.data());
    if (gpus.empty()) return fail("no Vulkan GPU");
    VkPhysicalDevice pick = VK_NULL_HANDLE;
    if (gpu_index >= 0 && uint32_t(gpu_index) < gpus.size()) pick = gpus[size_t(gpu_index)];
    for (VkPhysicalDeviceType want : {VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU, VK_PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU,
                                      VK_PHYSICAL_DEVICE_TYPE_VIRTUAL_GPU, VK_PHYSICAL_DEVICE_TYPE_CPU})
        for (auto g : gpus) {
            if (pick) break;
            VkPhysicalDeviceProperties2 p{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2};
            vkGetPhysicalDeviceProperties2(g, &p);
            if (p.properties.deviceType == want && p.properties.apiVersion >= VK_API_VERSION_1_4) pick = g;
        }
    if (!pick) return fail("no GPU with Vulkan 1.4 (update the graphics driver)");
    ctx.gpu = pick;

    VkPhysicalDeviceSubgroupProperties subgroup{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SUBGROUP_PROPERTIES};
    VkPhysicalDeviceProperties2 props{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2, &subgroup};
    vkGetPhysicalDeviceProperties2(pick, &props);
    ctx.props = props.properties;
    ctx.api_version = props.properties.apiVersion;
    std::snprintf(ctx.name, sizeof ctx.name, "%s", props.properties.deviceName);
    vkGetPhysicalDeviceMemoryProperties(pick, &ctx.memory);
    if (props.properties.apiVersion < VK_API_VERSION_1_4) return fail("%s supports only Vulkan %u.%u", ctx.name,
                                                                      VK_API_VERSION_MAJOR(ctx.api_version),
                                                                      VK_API_VERSION_MINOR(ctx.api_version));
    if (!(subgroup.supportedOperations & VK_SUBGROUP_FEATURE_QUAD_BIT) ||
        !(subgroup.supportedStages & VK_SHADER_STAGE_FRAGMENT_BIT))
        return fail("%s lacks quad subgroup operations in fragment shaders", ctx.name);

    // features
    VkPhysicalDeviceVulkan14Features f14{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_4_FEATURES};
    VkPhysicalDeviceVulkan13Features f13{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES, &f14};
    VkPhysicalDeviceVulkan12Features f12{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_FEATURES, &f13};
    VkPhysicalDeviceVulkan11Features f11{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_1_FEATURES, &f12};
    VkPhysicalDeviceFeatures2 f{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2, &f11};
    vkGetPhysicalDeviceFeatures2(pick, &f);
    const char* missing = nullptr;
    if (!f13.dynamicRendering) missing = "dynamicRendering";
    else if (!f13.synchronization2) missing = "synchronization2";
    else if (!f13.shaderDemoteToHelperInvocation) missing = "shaderDemoteToHelperInvocation";
    else if (!f13.maintenance4) missing = "maintenance4";
    else if (!f12.timelineSemaphore) missing = "timelineSemaphore";
    else if (!f14.maintenance5) missing = "maintenance5";
    else if (!f.features.shaderImageGatherExtended) missing = "shaderImageGatherExtended";
    if (missing) return fail("%s lacks the Vulkan feature %s", ctx.name, missing);
    ctx.host_image_copy = f14.hostImageCopy;

    // enable exactly what we use
    VkPhysicalDeviceVulkan14Features e14{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_4_FEATURES};
    e14.maintenance5 = VK_TRUE;
    e14.maintenance6 = f14.maintenance6;
    e14.hostImageCopy = f14.hostImageCopy;
    e14.dynamicRenderingLocalRead = f14.dynamicRenderingLocalRead;
    VkPhysicalDeviceVulkan13Features e13{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES, &e14};
    e13.dynamicRendering = VK_TRUE;
    e13.synchronization2 = VK_TRUE;
    e13.shaderDemoteToHelperInvocation = VK_TRUE;
    e13.maintenance4 = VK_TRUE;
    VkPhysicalDeviceVulkan12Features e12{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_FEATURES, &e13};
    e12.timelineSemaphore = VK_TRUE;
    e12.scalarBlockLayout = f12.scalarBlockLayout;
    VkPhysicalDeviceVulkan11Features e11{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_1_FEATURES, &e12};
    VkPhysicalDeviceFeatures2 ef{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2, &e11};
    ef.features.shaderImageGatherExtended = VK_TRUE;
    ef.features.independentBlend = f.features.independentBlend;
    ef.features.samplerAnisotropy = f.features.samplerAnisotropy;
    ef.features.depthClamp = f.features.depthClamp;
    ef.features.geometryShader = f.features.geometryShader;  // GCN rect lists
    ef.features.robustBufferAccess = f.features.robustBufferAccess;  // GCN buffer reads are bounds-checked too
    ef.features.depthBiasClamp = f.features.depthBiasClamp;
    ef.features.fillModeNonSolid = f.features.fillModeNonSolid;
    ef.features.textureCompressionBC = f.features.textureCompressionBC;
    ef.features.fragmentStoresAndAtomics = f.features.fragmentStoresAndAtomics;
    ef.features.vertexPipelineStoresAndAtomics = f.features.vertexPipelineStoresAndAtomics;

    // device extensions
    vkEnumerateDeviceExtensionProperties(pick, nullptr, &n, nullptr);
    std::vector<VkExtensionProperties> exts(n);
    vkEnumerateDeviceExtensionProperties(pick, nullptr, &n, exts.data());
    std::vector<const char*> dev_exts;
    if (num_inst_exts && has_extension(exts, VK_KHR_SWAPCHAIN_EXTENSION_NAME)) dev_exts.push_back(VK_KHR_SWAPCHAIN_EXTENSION_NAME);
    if (has_extension(exts, VK_EXT_EXTERNAL_MEMORY_HOST_EXTENSION_NAME)) {
        dev_exts.push_back(VK_EXT_EXTERNAL_MEMORY_HOST_EXTENSION_NAME);
        ctx.external_memory_host = true;
    }

    // one graphics + compute queue
    vkGetPhysicalDeviceQueueFamilyProperties(pick, &n, nullptr);
    std::vector<VkQueueFamilyProperties> fams(n);
    vkGetPhysicalDeviceQueueFamilyProperties(pick, &n, fams.data());
    ctx.queue_family = UINT32_MAX;
    for (uint32_t i = 0; i < n; ++i)
        if ((fams[i].queueFlags & (VK_QUEUE_GRAPHICS_BIT | VK_QUEUE_COMPUTE_BIT)) == (VK_QUEUE_GRAPHICS_BIT | VK_QUEUE_COMPUTE_BIT)) {
            ctx.queue_family = i;
            break;
        }
    if (ctx.queue_family == UINT32_MAX) return fail("%s has no graphics queue", ctx.name);
    const float prio = 1.0f;
    VkDeviceQueueCreateInfo qci{VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO};
    qci.queueFamilyIndex = ctx.queue_family;
    qci.queueCount = 1;
    qci.pQueuePriorities = &prio;
    VkDeviceCreateInfo dci{VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO, &ef};
    dci.queueCreateInfoCount = 1;
    dci.pQueueCreateInfos = &qci;
    dci.enabledExtensionCount = uint32_t(dev_exts.size());
    dci.ppEnabledExtensionNames = dev_exts.data();
    if (vkCreateDevice(pick, &dci, nullptr, &ctx.device) != VK_SUCCESS) return fail("vkCreateDevice failed on %s", ctx.name);
    // core names first, then the extension names they were promoted from (older loaders and
    // layers, e.g. Wine's, only know vkCmdPushDescriptorSetKHR)
    auto device_fn = [&](const char* name) {
        PFN_vkVoidFunction f = vkGetDeviceProcAddr(ctx.device, name);
        for (const char* suffix : {"KHR", "EXT"}) {
            if (f) break;
            char alt[128];
            std::snprintf(alt, sizeof alt, "%s%s", name, suffix);
            f = vkGetDeviceProcAddr(ctx.device, alt);
        }
        return f;
    };
    std::string missing_fns;
#define D1_VK_LOAD(f)                                            \
    f = reinterpret_cast<PFN_##f>(device_fn(#f));                \
    if (!f && std::strstr(#f, "Swapchain") == nullptr && std::strcmp(#f, "vkAcquireNextImageKHR") != 0 && \
        std::strcmp(#f, "vkQueuePresentKHR") != 0)               \
        missing_fns += std::string(missing_fns.empty() ? "" : ", ") + #f;
    D1_VK_DEVICE_FUNCS(D1_VK_LOAD)
#undef D1_VK_LOAD
    if (!missing_fns.empty()) return fail("%s: the driver lacks %s", ctx.name, missing_fns.c_str());
    vkGetDeviceQueue(ctx.device, ctx.queue_family, 0, &ctx.queue);
    return true;
}

uint32_t surface_instance_extensions(WindowSystem ws, const char** out) {
    if (ws == WindowSystem::None || !open_loader()) return 0;
    uint32_t n = 0;
    vkEnumerateInstanceExtensionProperties(nullptr, &n, nullptr);
    std::vector<VkExtensionProperties> exts(n);
    vkEnumerateInstanceExtensionProperties(nullptr, &n, exts.data());
    const char* platform = ws == WindowSystem::Win32 ? "VK_KHR_win32_surface" : "VK_KHR_xlib_surface";
    if (!has_extension(exts, VK_KHR_SURFACE_EXTENSION_NAME) || !has_extension(exts, platform)) return 0;
    out[0] = VK_KHR_SURFACE_EXTENSION_NAME;
    out[1] = platform;
    return 2;
}

bool create_surface(const Context& ctx, WindowSystem ws, void* display, uint64_t window, VkSurfaceKHR* out) {
    // The platform create-info structs, declared here so no window-system header is needed
    // (layouts as in vulkan_win32.h / vulkan_xlib.h).
    struct Win32Info {
        VkStructureType sType;
        const void* pNext;
        VkFlags flags;
        void* hinstance;
        void* hwnd;
    };
    struct XlibInfo {
        VkStructureType sType;
        const void* pNext;
        VkFlags flags;
        void* dpy;
        unsigned long window;
    };
    using CreateFn = VkResult(VKAPI_PTR*)(VkInstance, const void*, const VkAllocationCallbacks*, VkSurfaceKHR*);
    if (ws == WindowSystem::Win32) {
        auto fn = reinterpret_cast<CreateFn>(g_gipa(ctx.instance, "vkCreateWin32SurfaceKHR"));
        Win32Info ci{VK_STRUCTURE_TYPE_WIN32_SURFACE_CREATE_INFO_KHR, nullptr, 0, display,
                     reinterpret_cast<void*>(uintptr_t(window))};
        return fn && fn(ctx.instance, &ci, nullptr, out) == VK_SUCCESS;
    }
    if (ws == WindowSystem::Xlib) {
        auto fn = reinterpret_cast<CreateFn>(g_gipa(ctx.instance, "vkCreateXlibSurfaceKHR"));
        XlibInfo ci{VK_STRUCTURE_TYPE_XLIB_SURFACE_CREATE_INFO_KHR, nullptr, 0, display, (unsigned long)window};
        return fn && fn(ctx.instance, &ci, nullptr, out) == VK_SUCCESS;
    }
    return false;
}

void destroy_context(Context& ctx) {
    if (ctx.device) vkDestroyDevice(ctx.device, nullptr);
    if (ctx.instance) vkDestroyInstance(ctx.instance, nullptr);
    ctx = Context{};
}

}  // namespace d1::vk
