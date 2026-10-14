// The native renderer's Vulkan side: executes the draws the engine recorded through its GPU
// device layer (src/native_gfx.cpp captures them) with our own translated shaders, our own
// images and our own pipelines. No PM4, no emulated GPU.
//
// Everything here is engine-independent GCN / Gnm knowledge: a Draw holds the hardware
// register values and resource descriptors (T#, S#, V#, render-target descriptors) that the
// engine's device object keeps, plus pointers to the Gnm shader objects.
#pragma once
#include <cstdint>
#include <vector>

namespace d1::ng {

constexpr int kStages = 2;  // 0 = vertex, 1 = pixel

struct Draw {
    enum Kind : uint8_t { Indexed, Auto, Clear };
    Kind kind = Auto;
    uint8_t prim = 4;           // VGT_DI_PRIM_TYPE
    uint8_t index32 = 0;
    uint8_t clear_flags = 0;    // Clear: bits 2..5 color MRT 0..3, 0x40 depth, 0x80 stencil
    uint32_t count = 0, instances = 1;
    uint64_t index_addr = 0;    // Indexed: first index
    uint64_t order = 0;         // DCB write position when recorded (orders draws in a submission)
    uint32_t seq = 0;
    uint64_t caller = 0;        // engine call site (diagnostics)
    const uint8_t* vs = nullptr;  // engine vertex shader object (fetch shader size/address, Gnm VsShader at +0x14)
    const uint8_t* ps = nullptr;  // Gnm PsShader
    uint32_t num_vb = 0;
    uint32_t vb[16][4] = {};    // V# per vertex buffer API slot (vertex declaration element)
    const uint32_t* tex[kStages][16] = {};   // T# per stage and slot
    const uint32_t* smp[kStages][16] = {};   // S#
    struct Cb { uint64_t addr; uint32_t size; } cb[kStages][16] = {};
    // registers
    uint32_t blend = 0, target_mask = 0xF, su_sc_mode = 0, clip = 0, depth_ctl = 0, stencil_ctl = 0, stencil_ref = 0;
    float poly_offset = 0, poly_scale = 0;
    int32_t vp[4] = {};         // x, y, w, h
    float znear = 0, zfar = 1, zk = 1;
    uint32_t color[5][11] = {}; // Gnm RenderTarget (CB_COLOR_* registers + packed size)
    uint32_t depth[13] = {};    // Gnm DepthRenderTarget
    float clear_color[4] = {};
    float clear_depth = 1;
    uint8_t clear_stencil = 0;
    std::vector<uint8_t> inline_vertices;  // draw from an inline vertex buffer: V# bases are offsets into it
};

struct Options {
    const char* frames_dir = nullptr;  // write the flipped image as <dir>/f<N>.ppm
    bool no_cull = false;
    bool dump_targets = false;         // with each written frame, every render target the frame used
};

bool init(const Options& opt);
bool active();
// Executes draws (already in GPU order) and waits for them.
void execute(const std::vector<Draw*>& draws);
// The video-out buffer at `addr` was flipped: dump it when frames are being written.
void flip(uint64_t addr, uint32_t width, uint32_t height, uint64_t frame);
void print_stats();

}  // namespace d1::ng
