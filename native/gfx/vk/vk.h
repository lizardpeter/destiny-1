// Vulkan entry points for the native renderer (d1-native's own loader).
//
// The Vulkan loader (vulkan-1.dll / libvulkan.so.1) is opened at run time; every function the
// native renderer uses is listed once below and resolved through vkGetInstanceProcAddr /
// vkGetDeviceProcAddr. Headers: Khronos Vulkan-Headers (fetched by CMake), VK_NO_PROTOTYPES.
#pragma once
#define VK_NO_PROTOTYPES
#include <vulkan/vulkan.h>

#define D1_VK_GLOBAL_FUNCS(X) \
    X(vkCreateInstance) X(vkEnumerateInstanceVersion) X(vkEnumerateInstanceExtensionProperties) \
    X(vkEnumerateInstanceLayerProperties)

#define D1_VK_INSTANCE_FUNCS(X) \
    X(vkDestroyInstance) X(vkEnumeratePhysicalDevices) X(vkGetPhysicalDeviceProperties2) \
    X(vkGetPhysicalDeviceFeatures2) X(vkGetPhysicalDeviceQueueFamilyProperties) \
    X(vkGetPhysicalDeviceMemoryProperties) X(vkGetPhysicalDeviceFormatProperties) X(vkCreateDevice) \
    X(vkGetDeviceProcAddr) X(vkEnumerateDeviceExtensionProperties) X(vkDestroySurfaceKHR) \
    X(vkGetPhysicalDeviceSurfaceSupportKHR) X(vkGetPhysicalDeviceSurfaceCapabilitiesKHR) \
    X(vkGetPhysicalDeviceSurfaceFormatsKHR) X(vkGetPhysicalDeviceSurfacePresentModesKHR)

#define D1_VK_DEVICE_FUNCS(X) \
    X(vkDestroyDevice) X(vkGetDeviceQueue) X(vkDeviceWaitIdle) X(vkQueueSubmit2) X(vkQueueWaitIdle) \
    X(vkCreateCommandPool) X(vkDestroyCommandPool) X(vkResetCommandPool) X(vkAllocateCommandBuffers) \
    X(vkFreeCommandBuffers) X(vkBeginCommandBuffer) X(vkEndCommandBuffer) X(vkResetCommandBuffer) \
    X(vkCreateFence) X(vkDestroyFence) X(vkWaitForFences) X(vkResetFences) X(vkGetFenceStatus) \
    X(vkCreateSemaphore) X(vkDestroySemaphore) X(vkWaitSemaphores) X(vkGetSemaphoreCounterValue) \
    X(vkSignalSemaphore) \
    X(vkAllocateMemory) X(vkFreeMemory) X(vkMapMemory) X(vkUnmapMemory) X(vkFlushMappedMemoryRanges) \
    X(vkCreateBuffer) X(vkDestroyBuffer) X(vkGetBufferMemoryRequirements) X(vkBindBufferMemory) \
    X(vkCreateImage) X(vkDestroyImage) X(vkGetImageMemoryRequirements) X(vkBindImageMemory) \
    X(vkCreateImageView) X(vkDestroyImageView) X(vkCreateSampler) X(vkDestroySampler) \
    X(vkCreateShaderModule) X(vkDestroyShaderModule) X(vkCreatePipelineLayout) X(vkDestroyPipelineLayout) \
    X(vkCreateDescriptorSetLayout) X(vkDestroyDescriptorSetLayout) X(vkCreateGraphicsPipelines) \
    X(vkCreateComputePipelines) X(vkDestroyPipeline) X(vkCreatePipelineCache) X(vkGetPipelineCacheData) \
    X(vkDestroyPipelineCache) \
    X(vkCmdPipelineBarrier2) X(vkCmdBeginRendering) X(vkCmdEndRendering) X(vkCmdBindPipeline) \
    X(vkCmdBindVertexBuffers) X(vkCmdBindIndexBuffer) X(vkCmdDraw) \
    X(vkCmdDrawIndexed) X(vkCmdDispatch) X(vkCmdSetViewport) X(vkCmdSetScissor) X(vkCmdCopyBuffer) \
    X(vkCmdCopyBufferToImage) X(vkCmdCopyImageToBuffer) X(vkCmdBlitImage) X(vkCmdClearColorImage) \
    X(vkCmdClearDepthStencilImage) X(vkCmdSetStencilReference) X(vkCmdPushConstants) X(vkCmdClearAttachments) \
    X(vkCmdSetDepthBias) X(vkCreateDescriptorPool) X(vkDestroyDescriptorPool) X(vkResetDescriptorPool) \
    X(vkAllocateDescriptorSets) X(vkUpdateDescriptorSets) X(vkCmdBindDescriptorSets) X(vkCmdSetStencilCompareMask) X(vkCmdSetStencilWriteMask) X(vkCmdCopyImage) X(vkCmdBindVertexBuffers2) \
    X(vkCreateSwapchainKHR) X(vkDestroySwapchainKHR) X(vkGetSwapchainImagesKHR) X(vkAcquireNextImageKHR) \
    X(vkQueuePresentKHR)

namespace d1::vk {

#define D1_VK_DECLARE(f) extern PFN_##f f;
D1_VK_GLOBAL_FUNCS(D1_VK_DECLARE)
D1_VK_INSTANCE_FUNCS(D1_VK_DECLARE)
D1_VK_DEVICE_FUNCS(D1_VK_DECLARE)
#undef D1_VK_DECLARE

// The native renderer's Vulkan context.
struct Context {
    VkInstance instance = VK_NULL_HANDLE;
    VkPhysicalDevice gpu = VK_NULL_HANDLE;
    VkDevice device = VK_NULL_HANDLE;
    VkQueue queue = VK_NULL_HANDLE;
    uint32_t queue_family = 0;
    uint32_t api_version = 0;
    VkPhysicalDeviceProperties props{};
    VkPhysicalDeviceMemoryProperties memory{};
    bool host_image_copy = false;     // VK 1.4 hostImageCopy feature
    bool external_memory_host = false;
    char name[256] = {};
};

// Opens the loader, creates a Vulkan 1.4 instance and device with the features the native
// renderer needs (dynamic rendering, synchronization2, push descriptors, maintenance5/6,
// demote-to-helper, quad subgroup operations, gather offsets, timeline semaphores).
// `gpu_index` < 0 picks the first discrete GPU, else integrated, else anything.
// Returns false with `error` set when Vulkan 1.4 or a required feature is missing.
bool create_context(Context& ctx, int gpu_index, const char** instance_extensions, uint32_t num_instance_extensions,
                    char* error, size_t error_size);
void destroy_context(Context& ctx);

uint32_t find_memory_type(const Context& ctx, uint32_t type_bits, VkMemoryPropertyFlags want);

// Window surfaces. The instance must have been created with surface_instance_extensions().
enum class WindowSystem { None, Win32, Xlib };
// VK_KHR_surface plus the platform's surface extension, if the loader offers them (else 0).
uint32_t surface_instance_extensions(WindowSystem ws, const char** out /* 2 entries */);
// display: HINSTANCE (Win32) or Display* (Xlib); window: HWND or X11 Window.
bool create_surface(const Context& ctx, WindowSystem ws, void* display, uint64_t window, VkSurfaceKHR* out);

}  // namespace d1::vk
