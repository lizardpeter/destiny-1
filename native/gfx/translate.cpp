// GCN (gfx7) -> SPIR-V translation. See translate.h for the execution model.
#include "translate.h"

#include <algorithm>
#include <cmath>
#include <array>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <set>

#include "gcn.h"
#include "spirv.h"

namespace d1::gcn {
namespace {

using namespace spv;

// Where a scalar register's value came from (for resolving descriptors).
struct Origin {
    enum Kind : uint8_t { None, User, Table } kind = None;
    uint32_t reg = 0;      // User: user-data register index (0..15 SGPRs, 16+ extended user data)
    uint8_t table = 0;     // Table: usage type of the table pointer
    uint8_t table_api = 0; // Table: API slot of the table pointer
    uint32_t dword = 0;    // Table: dword index inside the table
};

struct ResRef {
    bool ok = false;
    uint8_t api = 0;
};

class Translator {
public:
    Translator(const ShaderDesc& d, Result& r) : d_(d), r_(r) {}
    void run();

private:
    // ---------------------------------------------------------------- setup
    void problem(const std::string& s) {
        if (problems_seen_.insert(s).second) r_.problems.push_back(s);
    }
    void types() {
        tvoid_ = m_.t_void(), tbool_ = m_.t_bool(), tu_ = m_.t_u32(), ti_ = m_.t_i32(), tf_ = m_.t_f32();
        tv2f_ = m_.t_vec(tf_, 2), tv3f_ = m_.t_vec(tf_, 3), tv4f_ = m_.t_vec(tf_, 4);
        tv2u_ = m_.t_vec(tu_, 2), tv3u_ = m_.t_vec(tu_, 3), tv4u_ = m_.t_vec(tu_, 4);
        tv2i_ = m_.t_vec(ti_, 2), tv3i_ = m_.t_vec(ti_, 3);
        tpu_ = m_.t_ptr(SCPrivate, tu_);
    }
    Id global(Id ptr_type, StorageClass sc, Id init = 0) {
        const Id v = m_.variable(ptr_type, sc, init);
        interface_.push_back(v);
        return v;
    }
    Id sreg(uint32_t i) {
        auto& v = sregs_[i];
        if (!v) {
            v = global(tpu_, SCPrivate, m_.c_u32(i == 126 ? 1u : 0u));  // EXEC starts with this lane on
            char b[16];
            std::snprintf(b, sizeof b, "s%u", i);
            m_.name(v, b);
        }
        return v;
    }
    Id vreg(uint32_t i) {
        auto& v = vregs_[i];
        if (!v) {
            v = global(tpu_, SCPrivate, m_.c_u32(0));
            char b[16];
            std::snprintf(b, sizeof b, "v%u", i);
            m_.name(v, b);
        }
        return v;
    }
    Id spill_var(uint32_t vgpr, uint32_t lane) {
        Id& v = spills_[vgpr * 64 + (lane & 63)];
        if (!v) v = global(tpu_, SCPrivate, m_.c_u32(0));
        return v;
    }
    Id scc() {
        if (!scc_) {
            scc_ = global(m_.t_ptr(SCPrivate, tbool_), SCPrivate, m_.c_bool(false));
            m_.name(scc_, "scc");
        }
        return scc_;
    }

    // ---------------------------------------------------------------- value helpers
    Id ld(Id var, Id type) { return m_.op_r(OpLoad, type, {var}); }
    void st(Id var, Id val) { m_.op(OpStore, {var, val}); }
    Id u2f(Id u) { return m_.op_r(OpBitcast, tf_, {u}); }
    Id f2u(Id f) { return m_.op_r(OpBitcast, tu_, {f}); }
    Id u2i(Id u) { return m_.op_r(OpBitcast, ti_, {u}); }
    Id i2u(Id i) { return m_.op_r(OpBitcast, tu_, {i}); }
    Id bit0(Id u) {  // lane bit of a mask register value
        return m_.op_r(OpINotEqual, tbool_, {m_.op_r(OpBitwiseAnd, tu_, {u, m_.c_u32(1)}), m_.c_u32(0)});
    }
    Id b2u(Id b) { return m_.op_r(OpSelect, tu_, {b, m_.c_u32(1), m_.c_u32(0)}); }
    Id exec_bit() { return bit0(ld(sreg(126), tu_)); }

    // Raw 32-bit read of an operand.
    Id read_u(const Operand& o, const Inst& in) {
        const uint16_t c = o.code;
        if (c < 104 || c == 106 || c == 107 || c == 124 || c == 126 || c == 127) return ld(sreg(c), tu_);
        if (c >= 256) return ld(vreg(c - 256), tu_);
        if (o.is_inline_const()) return m_.c_u32(inline_constant(c));
        if (c == 255) return m_.c_u32(in.literal);
        if (c == 251) return b2u(m_.op_r(OpLogicalNot, tbool_, {bit0(ld(sreg(106), tu_))}));  // VCCZ
        if (c == 252) return b2u(m_.op_r(OpLogicalNot, tbool_, {exec_bit()}));               // EXECZ
        if (c == 253) return b2u(ld(scc(), tbool_));
        char b[64];
        std::snprintf(b, sizeof b, "unsupported operand %u", c);
        problem(b);
        return m_.c_u32(0);
    }
    Id read_f(const Operand& o, const Inst& in) {
        Id v = u2f(read_u(o, in));
        if (o.abs) v = m_.ext(tf_, GlslFAbs, {v});
        if (o.neg) v = m_.op_r(OpFNegate, tf_, {v});
        return v;
    }
    Id read_i(const Operand& o, const Inst& in) { return u2i(read_u(o, in)); }

    // Vector destination write, predicated by the lane's EXEC bit when the program changes it.
    void write_v(uint32_t vgpr, Id u) {
        if (exec_changes_) {
            const Id old = ld(vreg(vgpr), tu_);
            u = m_.op_r(OpSelect, tu_, {exec_bit(), u, old});
        }
        st(vreg(vgpr), u);
    }
    void write_vf(const Inst& in, Id f) {
        if (in.enc == Enc::VOP3) {
            if (in.omod == 1) f = m_.op_r(OpFMul, tf_, {f, m_.c_f32(2.0f)});
            else if (in.omod == 2) f = m_.op_r(OpFMul, tf_, {f, m_.c_f32(4.0f)});
            else if (in.omod == 3) f = m_.op_r(OpFMul, tf_, {f, m_.c_f32(0.5f)});
            if (in.clamp) f = m_.ext(tf_, GlslNClamp, {f, m_.c_f32(0.0f), m_.c_f32(1.0f)});
        }
        write_v(uint32_t(in.dst.vgpr()), f2u(f));
    }
    void write_s(uint32_t s, Id u) {
        if (s < 104 || s == 106 || s == 107 || s == 124 || s == 126 || s == 127) st(sreg(s), u);
        else {
            char b[64];
            std::snprintf(b, sizeof b, "unsupported scalar destination %u", s);
            problem(b);
        }
    }
    // A lane-mask destination (compare results): lane bit in the low register, high = 0.
    void write_mask(uint32_t s, Id b) {
        write_s(s, b2u(b));
        write_s(s + 1, m_.c_u32(0));
    }

    // ---------------------------------------------------------------- resources
    void analyse_origins(const Program& p);
    ResRef resolve(uint32_t first_sgpr, size_t inst_index, uint8_t want_type);
    Id texture_var(uint8_t api);
    Id sampler_var(uint8_t api);
    Id cbuffer_var(uint8_t api);

    // ---------------------------------------------------------------- translation
    void prologue();
    void emit(const Inst& in, size_t index);
    void emit_vop(const Inst& in);
    void emit_cmp(const Inst& in);
    void emit_scalar(const Inst& in);
    void emit_smrd(const Inst& in, size_t index);
    void emit_mimg(const Inst& in, size_t index);
    void emit_exp(const Inst& in);
    void emit_interp(const Inst& in);
    void emit_fetch_call();
    void emit_buffer_load(const Inst& in, size_t index);

    const ShaderDesc& d_;
    Result& r_;
    Module m_;
    Program prog_, fetch_;
    std::set<std::string> problems_seen_;
    Id tvoid_{}, tbool_{}, tu_{}, ti_{}, tf_{}, tv2f_{}, tv3f_{}, tv4f_{}, tv2u_{}, tv3u_{}, tv4u_{}, tv2i_{}, tv3i_{};
    Id tpu_{};
    Id sregs_[128] = {}, vregs_[256] = {}, scc_ = 0;
    std::vector<Id> interface_;
    bool exec_changes_ = false;
    // origins of the SGPRs each memory instruction uses, by instruction index
    std::map<size_t, std::vector<Origin>> origins_;
    std::map<uint8_t, Id> tex_vars_, samp_vars_, cb_vars_;
    std::map<uint32_t, Id> ps_inputs_, ps_flat_inputs_, outputs_;
    Id frag_coord_ = 0, front_facing_ = 0, position_out_ = 0, frag_depth_ = 0;
    Id vertex_index_ = 0, instance_index_ = 0;
    std::vector<Id> attrib_vars_;
    std::map<uint32_t, Id> spills_;
};

// ---------------------------------------------------------------------------- origins
void Translator::analyse_origins(const Program& p) {
    std::vector<Origin> cur(104);
    std::map<uint32_t, Origin> spilled;  // (VGPR * 64 + lane) -> origin of the spilled SGPR
    for (uint32_t i = 0; i < 16 && i < 104; ++i) cur[i] = {Origin::User, i, 0, 0, 0};
    auto slot_at = [&](uint32_t reg) -> const UsageSlot* {
        for (const auto& s : d_.slots)
            if (s.start_reg == reg) return &s;
        return nullptr;
    };
    for (size_t k = 0; k < p.insts.size(); ++k) {
        const Inst& in = p.insts[k];
        if (in.enc == Enc::MIMG || in.enc == Enc::MUBUF || in.enc == Enc::MTBUF ||
            (in.enc == Enc::SMRD && in.opnum >= 8))
            origins_[k] = cur;
        if (in.enc == Enc::SMRD && in.opnum < 8) {  // S_LOAD_DWORDxN through a pointer
            const uint32_t n = in.op == Op::S_LOAD_DWORD ? 1 : in.op == Op::S_LOAD_DWORDX2 ? 2
                             : in.op == Op::S_LOAD_DWORDX4 ? 4 : in.op == Op::S_LOAD_DWORDX8 ? 8 : 16;
            const Origin base = cur[in.sbase];
            const uint32_t off = in.smrd_imm ? in.smrd_offset : 0;  // dwords
            for (uint32_t i = 0; i < n && in.dst.code + i < 104; ++i) {
                Origin o{};
                if (base.kind == Origin::User) {
                    const UsageSlot* s = slot_at(base.reg);
                    if (s && s->type == kUsagePtrExtendedUserData) o = {Origin::User, 16 + off + i, 0, 0, 0};
                    else if (s) o = {Origin::Table, 0, s->type, s->api_slot, off + i};
                }
                cur[in.dst.code + i] = o;
            }
        } else if (in.op == Op::V_WRITELANE_B32 && in.src[0].code < 104 && in.src[1].is_inline_const()) {
            spilled[uint32_t(in.dst.vgpr()) * 64 + (inline_constant(in.src[1].code) & 63)] = cur[in.src[0].code];
        } else if (in.op == Op::V_READLANE_B32 && in.dst.code < 104) {
            const bool ok = in.src[1].is_inline_const() && in.src[0].is_vgpr();
            cur[in.dst.code] = ok ? spilled[uint32_t(in.src[0].vgpr()) * 64 + (inline_constant(in.src[1].code) & 63)] : Origin{};
        } else if (in.op == Op::S_MOV_B32 && in.dst.code < 104 && in.src[0].code < 104) {
            cur[in.dst.code] = cur[in.src[0].code];
        } else if (in.op == Op::S_MOV_B64 && in.dst.code < 103 && in.src[0].code < 103) {
            cur[in.dst.code] = cur[in.src[0].code];
            cur[in.dst.code + 1] = cur[in.src[0].code + 1];
        } else if (in.enc == Enc::SMRD) {
            const uint32_t nb = in.op == Op::S_BUFFER_LOAD_DWORD ? 1 : in.op == Op::S_BUFFER_LOAD_DWORDX2 ? 2
                              : in.op == Op::S_BUFFER_LOAD_DWORDX4 ? 4 : in.op == Op::S_BUFFER_LOAD_DWORDX8 ? 8 : 16;
            for (uint32_t i = 0; i < nb && in.dst.code + i < 104; ++i) cur[in.dst.code + i] = {};
        } else if ((in.enc == Enc::SOP1 || in.enc == Enc::SOP2 || in.enc == Enc::SOPK ||
                    (in.enc == Enc::VOP3 && in.opnum < 0x100) || in.op == Op::V_READFIRSTLANE_B32 ||
                    in.op == Op::V_READLANE_B32) &&
                   in.dst.code < 104) {
            cur[in.dst.code] = {};
            if (in.op == Op::S_MOV_B64 || in.enc == Enc::VOP3) cur[std::min<uint32_t>(in.dst.code + 1, 103)] = {};
        }
    }
}

ResRef Translator::resolve(uint32_t first_sgpr, size_t index, uint8_t want) {
    auto it = origins_.find(index);
    if (it == origins_.end() || first_sgpr >= 104) return {};
    const Origin& o = it->second[first_sgpr];
    if (o.kind == Origin::User) {
        for (const auto& s : d_.slots)
            if (s.start_reg == o.reg && s.type == want) return {true, s.api_slot};
    } else if (o.kind == Origin::Table) {
        // tables hold 8-dword T#s, or 4-dword S#s / V#s
        if (o.table == kUsagePtrResourceTable && want == kUsageImmResource) return {true, uint8_t(o.table_api + o.dword / 8)};
        if (o.table == kUsagePtrSamplerTable && want == kUsageImmSampler) return {true, uint8_t(o.table_api + o.dword / 4)};
        if (o.table == kUsagePtrConstBufferTable && want == kUsageImmConstBuffer)
            return {true, uint8_t(o.table_api + o.dword / 4)};
    }
    return {};
}

Id Translator::texture_var(uint8_t api) {
    auto& v = tex_vars_[api];
    if (!v) {
        const TexDim td = api < 16 ? d_.tex_dims[api] : TexDim::Tex2D;
        const Dim dim = td == TexDim::Tex3D ? Dim3D : td == TexDim::Cube ? DimCube : Dim2D;
        const Id img = m_.t_image(tf_, dim, false, td == TexDim::Tex2DArray, false, 1);
        v = global(m_.t_ptr(SCUniformConstant, img), SCUniformConstant);
        m_.decorate(v, DecDescriptorSet, {d_.stage == Stage::Vertex ? 0u : 1u});
        m_.decorate(v, DecBinding, {api});
        r_.bindings.push_back({Binding::Texture, api, api});
    }
    return v;
}
Id Translator::sampler_var(uint8_t api) {
    auto& v = samp_vars_[api];
    if (!v) {
        v = global(m_.t_ptr(SCUniformConstant, m_.t_sampler()), SCUniformConstant);
        m_.decorate(v, DecDescriptorSet, {d_.stage == Stage::Vertex ? 0u : 1u});
        m_.decorate(v, DecBinding, {16u + api});
        r_.bindings.push_back({Binding::Sampler, api, 16u + api});
    }
    return v;
}
Id Translator::cbuffer_var(uint8_t api) {
    auto& v = cb_vars_[api];
    if (!v) {
        const Id arr = m_.t_runtime_array(tu_);
        m_.decorate(arr, DecArrayStride, {4});
        const Id st = m_.t_struct({arr});
        m_.decorate(st, DecBlock);
        m_.member_decorate(st, 0, DecOffset, {0});
        m_.member_decorate(st, 0, DecNonWritable);
        v = global(m_.t_ptr(SCStorageBuffer, st), SCStorageBuffer);
        m_.decorate(v, DecDescriptorSet, {d_.stage == Stage::Vertex ? 0u : 1u});
        m_.decorate(v, DecBinding, {32u + api});
        r_.bindings.push_back({Binding::ConstBuffer, api, 32u + api});
    }
    return v;
}

// ---------------------------------------------------------------------------- prologue
void Translator::prologue() {
    if (d_.stage == Stage::Pixel) {
        // input VGPRs in SPI_PS_INPUT_ADDR order
        static const uint8_t counts[16] = {2, 2, 2, 3, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1};
        uint32_t v = 0;
        for (uint32_t bit = 0; bit < 16; ++bit) {
            if (!(d_.ps_input_addr >> bit & 1)) continue;
            if (bit >= 8 && bit <= 11) {  // POS_X/Y/Z/W_FLOAT
                if (!frag_coord_) {
                    frag_coord_ = global(m_.t_ptr(SCInput, tv4f_), SCInput);
                    m_.decorate(frag_coord_, DecBuiltIn, {BuiltInFragCoord});
                }
                const Id fc = ld(frag_coord_, tv4f_);
                st(vreg(v), f2u(m_.op_r(OpCompositeExtract, tf_, {fc, bit - 8})));
            } else if (bit == 12) {  // FRONT_FACE
                front_facing_ = global(m_.t_ptr(SCInput, tbool_), SCInput);
                m_.decorate(front_facing_, DecBuiltIn, {BuiltInFrontFacing});
                st(vreg(v), b2u(ld(front_facing_, tbool_)));
            }
            v += counts[bit];
        }
    } else {
        // vertex: v0 = vertex index, v3 = instance index (relative id / primitive id are zero)
        vertex_index_ = global(m_.t_ptr(SCInput, ti_), SCInput);
        m_.decorate(vertex_index_, DecBuiltIn, {BuiltInVertexIndex});
        instance_index_ = global(m_.t_ptr(SCInput, ti_), SCInput);
        m_.decorate(instance_index_, DecBuiltIn, {BuiltInInstanceIndex});
        st(vreg(0), i2u(ld(vertex_index_, ti_)));
        st(vreg(3), i2u(ld(instance_index_, ti_)));
    }
}

// The fetch shader (vertex) loads each attribute with a typed buffer load into VGPRs; here
// each load becomes a vertex input attribute written into the same VGPRs.
void Translator::emit_fetch_call() {
    if (!d_.fetch) {
        problem("fetch shader call without a fetch shader");
        return;
    }
    fetch_ = decode(d_.fetch, d_.fetch_size);
    // the VB table pointer: usage slot PtrVertexBufferTable; loads through it give V#s
    std::vector<Origin> cur(104);
    uint8_t vb_reg = 0xFF;
    for (const auto& s : d_.slots)
        if (s.type == kUsagePtrVertexBufferTable) vb_reg = s.start_reg;
    uint32_t loc = 0;
    for (const Inst& in : fetch_.insts) {
        if (in.enc == Enc::SMRD && in.opnum < 8) {
            const uint32_t n = in.op == Op::S_LOAD_DWORDX4 ? 4 : in.op == Op::S_LOAD_DWORDX8 ? 8 : in.op == Op::S_LOAD_DWORDX16 ? 16 : 1;
            for (uint32_t i = 0; i < n && in.dst.code + i < 104; ++i)
                cur[in.dst.code + i] = in.sbase == vb_reg ? Origin{Origin::Table, 0, kUsagePtrVertexBufferTable, 0,
                                                                    (in.smrd_imm ? in.smrd_offset : 0) + i}
                                                          : Origin{};
        } else if (in.enc == Enc::MTBUF || (in.enc == Enc::MUBUF && in.opnum <= 3)) {
            const Origin& o = cur[in.srsrc];
            VertexAttrib a{};
            a.location = loc++;
            a.vb_slot = o.kind == Origin::Table ? o.dword / 4 : 0;
            a.offset = in.mem_offset;
            a.dfmt = in.dfmt, a.nfmt = in.nfmt;
            a.components = uint8_t(in.enc == Enc::MTBUF ? in.opnum + 1 : in.opnum + 1);
            a.vgpr = in.vdata;
            if (o.kind != Origin::Table) problem("fetch shader load from an unknown vertex buffer");
            if (in.enc == Enc::MUBUF) a.dfmt = a.nfmt = 0xFF;  // format comes from the V# at draw time
            r_.attribs.push_back(a);
            // integer formats stay integers; everything else arrives as float
            const bool is_int = in.nfmt == 4 || in.nfmt == 5;  // UINT / SINT
            const Id vt = is_int ? tv4u_ : tv4f_;
            const Id var = global(m_.t_ptr(SCInput, vt), SCInput);
            m_.decorate(var, DecLocation, {a.location});
            const Id val = ld(var, vt);
            for (uint32_t c = 0; c < a.components; ++c) {
                Id comp = m_.op_r(OpCompositeExtract, is_int ? tu_ : tf_, {val, c});
                st(vreg(a.vgpr + c), is_int ? comp : f2u(comp));
            }
        } else if (in.op == Op::S_SETPC_B64 || in.op == Op::S_WAITCNT || in.op == Op::S_MOV_B32 ||
                   in.op == Op::S_MOV_B64 || in.op == Op::S_NOP) {
        } else {
            problem(std::string("fetch shader instruction ") + op_name(in.op));
        }
    }
}

// ---------------------------------------------------------------------------- emission
void Translator::emit_scalar(const Inst& in) {
    auto s0 = [&] { return read_u(in.src[0], in); };
    auto s1 = [&] { return read_u(in.src[1], in); };
    auto hi = [&](const Operand& o) {
        Operand h = o;
        if (o.code < 104 || o.code == 106 || o.code == 126) h.code = uint16_t(o.code + 1);
        else if (o.is_inline_const() || o.is_literal()) return m_.c_u32(o.is_inline_const() && int32_t(inline_constant(o.code)) < 0 ? 0xFFFFFFFFu : 0u);
        return read_u(h, in);
    };
    const uint32_t dst = in.dst.code;
    switch (in.op) {
    case Op::S_MOV_B32: write_s(dst, s0()); return;
    case Op::S_MOV_B64: {
        const Id lo = s0(), h = hi(in.src[0]);
        write_s(dst, lo);
        write_s(dst + 1, h);
        return;
    }
    case Op::S_MOVK_I32: write_s(dst, m_.c_u32(uint32_t(int32_t(in.simm16)))); return;
    case Op::S_ADDK_I32: {
        const Id v = m_.op_r(OpIAdd, tu_, {ld(sreg(dst), tu_), m_.c_u32(uint32_t(int32_t(in.simm16)))});
        write_s(dst, v);
        return;
    }
    case Op::S_ADD_U32: case Op::S_ADD_I32: {
        const Id a = s0(), b = s1(), v = m_.op_r(OpIAdd, tu_, {a, b});
        write_s(dst, v);
        st(scc(), m_.op_r(OpULessThan, tbool_, {v, a}));  // carry (unsigned add)
        return;
    }
    case Op::S_SUB_I32: write_s(dst, m_.op_r(OpISub, tu_, {s0(), s1()})); return;
    case Op::S_MUL_I32: write_s(dst, m_.op_r(OpIMul, tu_, {s0(), s1()})); return;
    case Op::S_AND_B32: case Op::S_OR_B32: case Op::S_LSHL_B32: case Op::S_LSHR_B32: {
        Id v;
        if (in.op == Op::S_AND_B32) v = m_.op_r(OpBitwiseAnd, tu_, {s0(), s1()});
        else if (in.op == Op::S_OR_B32) v = m_.op_r(OpBitwiseOr, tu_, {s0(), s1()});
        else if (in.op == Op::S_LSHL_B32)
            v = m_.op_r(OpShiftLeftLogical, tu_, {s0(), m_.op_r(OpBitwiseAnd, tu_, {s1(), m_.c_u32(31)})});
        else v = m_.op_r(OpShiftRightLogical, tu_, {s0(), m_.op_r(OpBitwiseAnd, tu_, {s1(), m_.c_u32(31)})});
        write_s(dst, v);
        st(scc(), m_.op_r(OpINotEqual, tbool_, {v, m_.c_u32(0)}));
        return;
    }
    // 64-bit logic: lane-mask semantics on the low register's bit 0
    case Op::S_AND_B64: case Op::S_OR_B64: case Op::S_XOR_B64: case Op::S_ANDN2_B64: case Op::S_NAND_B64: {
        const Id a = bit0(s0()), b = bit0(s1());
        Id v;
        if (in.op == Op::S_AND_B64) v = m_.op_r(OpLogicalAnd, tbool_, {a, b});
        else if (in.op == Op::S_OR_B64) v = m_.op_r(OpLogicalOr, tbool_, {a, b});
        else if (in.op == Op::S_XOR_B64) v = m_.op_r(OpLogicalNotEqual, tbool_, {a, b});
        else if (in.op == Op::S_ANDN2_B64) v = m_.op_r(OpLogicalAnd, tbool_, {a, m_.op_r(OpLogicalNot, tbool_, {b})});
        else v = m_.op_r(OpLogicalNot, tbool_, {m_.op_r(OpLogicalAnd, tbool_, {a, b})});
        write_mask(dst, v);
        st(scc(), v);
        return;
    }
    case Op::S_WQM_B64: {  // whole-quad mode: this lane's own bit (helpers already run)
        const Id v = bit0(s0());
        write_mask(dst, v);
        st(scc(), v);
        return;
    }
    case Op::S_AND_SAVEEXEC_B64: {
        const Id old = ld(sreg(126), tu_);
        const Id v = m_.op_r(OpLogicalAnd, tbool_, {bit0(s0()), bit0(old)});
        write_s(dst, old);
        write_s(dst + 1, m_.c_u32(0));
        write_mask(126, v);
        st(scc(), v);
        return;
    }
    case Op::S_CMP_EQ_U32: case Op::S_CMP_EQ_I32: st(scc(), m_.op_r(OpIEqual, tbool_, {s0(), s1()})); return;
    case Op::S_CMP_LG_U32: case Op::S_CMP_LG_I32: st(scc(), m_.op_r(OpINotEqual, tbool_, {s0(), s1()})); return;
    case Op::S_CMP_GT_I32: st(scc(), m_.op_r(OpSGreaterThan, tbool_, {u2i(s0()), u2i(s1())})); return;
    case Op::S_CMP_GE_I32: st(scc(), m_.op_r(OpSGreaterThanEqual, tbool_, {u2i(s0()), u2i(s1())})); return;
    case Op::S_CMP_LT_I32: st(scc(), m_.op_r(OpSLessThan, tbool_, {u2i(s0()), u2i(s1())})); return;
    case Op::S_CMP_LE_I32: st(scc(), m_.op_r(OpSLessThanEqual, tbool_, {u2i(s0()), u2i(s1())})); return;
    case Op::S_CMP_GT_U32: st(scc(), m_.op_r(OpUGreaterThan, tbool_, {s0(), s1()})); return;
    case Op::S_CMP_GE_U32: st(scc(), m_.op_r(OpUGreaterThanEqual, tbool_, {s0(), s1()})); return;
    case Op::S_CMP_LT_U32: st(scc(), m_.op_r(OpULessThan, tbool_, {s0(), s1()})); return;
    case Op::S_CMP_LE_U32: st(scc(), m_.op_r(OpULessThanEqual, tbool_, {s0(), s1()})); return;
    default:
        problem(std::string("scalar instruction ") + op_name(in.op));
    }
}

void Translator::emit_smrd(const Inst& in, size_t index) {
    if (in.opnum < 8) return;  // descriptor loads through user-data pointers: resolved statically
    const uint32_t n = in.op == Op::S_BUFFER_LOAD_DWORD ? 1 : in.op == Op::S_BUFFER_LOAD_DWORDX2 ? 2
                     : in.op == Op::S_BUFFER_LOAD_DWORDX4 ? 4 : in.op == Op::S_BUFFER_LOAD_DWORDX8 ? 8 : 16;
    const ResRef cb = resolve(in.sbase, index, kUsageImmConstBuffer);
    if (!cb.ok) {
        problem("s_buffer_load from an unresolved constant buffer");
        for (uint32_t i = 0; i < n; ++i) write_s(in.dst.code + i, m_.c_u32(0));
        return;
    }
    const Id var = cbuffer_var(cb.api);
    Id base;  // dword index
    if (in.smrd_imm) base = m_.c_u32(in.smrd_offset);
    else {
        Operand o;
        o.code = uint16_t(in.smrd_offset);
        base = m_.op_r(OpShiftRightLogical, tu_, {in.smrd_offset == 255 ? m_.c_u32(in.literal) : read_u(o, in), m_.c_u32(2)});
    }
    const Id pu = m_.t_ptr(SCStorageBuffer, tu_);
    for (uint32_t i = 0; i < n; ++i) {
        const Id idx = m_.op_r(OpIAdd, tu_, {base, m_.c_u32(i)});
        const Id p = m_.op_r(OpAccessChain, pu, {var, m_.c_u32(0), idx});
        write_s(in.dst.code + i, ld(p, tu_));
    }
}

void Translator::emit_cmp(const Inst& in) {
    const Id a = read_f(in.src[0], in), b = read_f(in.src[1], in);
    auto ia = [&] { return read_i(in.src[0], in); };
    auto ib = [&] { return read_i(in.src[1], in); };
    auto ua = [&] { return read_u(in.src[0], in); };
    auto ub = [&] { return read_u(in.src[1], in); };
    Id c = 0;
    switch (in.op) {
    case Op::V_CMP_F_F32: c = m_.c_bool(false); break;
    case Op::V_CMP_TRU_F32: c = m_.c_bool(true); break;
    case Op::V_CMP_LT_F32: c = m_.op_r(OpFOrdLessThan, tbool_, {a, b}); break;
    case Op::V_CMP_EQ_F32: c = m_.op_r(OpFOrdEqual, tbool_, {a, b}); break;
    case Op::V_CMP_LE_F32: c = m_.op_r(OpFOrdLessThanEqual, tbool_, {a, b}); break;
    case Op::V_CMP_GT_F32: c = m_.op_r(OpFOrdGreaterThan, tbool_, {a, b}); break;
    case Op::V_CMP_LG_F32: c = m_.op_r(OpFOrdNotEqual, tbool_, {a, b}); break;
    case Op::V_CMP_GE_F32: c = m_.op_r(OpFOrdGreaterThanEqual, tbool_, {a, b}); break;
    case Op::V_CMP_O_F32:
        c = m_.op_r(OpLogicalAnd, tbool_, {m_.op_r(OpLogicalNot, tbool_, {m_.op_r(OpIsNan, tbool_, {a})}),
                                           m_.op_r(OpLogicalNot, tbool_, {m_.op_r(OpIsNan, tbool_, {b})})});
        break;
    case Op::V_CMP_U_F32:
        c = m_.op_r(OpLogicalOr, tbool_, {m_.op_r(OpIsNan, tbool_, {a}), m_.op_r(OpIsNan, tbool_, {b})});
        break;
    case Op::V_CMP_NGE_F32: c = m_.op_r(OpFUnordLessThan, tbool_, {a, b}); break;
    case Op::V_CMP_NLG_F32: c = m_.op_r(OpFUnordEqual, tbool_, {a, b}); break;
    case Op::V_CMP_NGT_F32: c = m_.op_r(OpFUnordLessThanEqual, tbool_, {a, b}); break;
    case Op::V_CMP_NLE_F32: c = m_.op_r(OpFUnordGreaterThan, tbool_, {a, b}); break;
    case Op::V_CMP_NEQ_F32: c = m_.op_r(OpFUnordNotEqual, tbool_, {a, b}); break;
    case Op::V_CMP_NLT_F32: c = m_.op_r(OpFUnordGreaterThanEqual, tbool_, {a, b}); break;
    case Op::V_CMP_LT_I32: c = m_.op_r(OpSLessThan, tbool_, {ia(), ib()}); break;
    case Op::V_CMP_EQ_I32: case Op::V_CMPX_EQ_I32: case Op::V_CMP_EQ_U32: c = m_.op_r(OpIEqual, tbool_, {ua(), ub()}); break;
    case Op::V_CMP_LE_I32: c = m_.op_r(OpSLessThanEqual, tbool_, {ia(), ib()}); break;
    case Op::V_CMP_GT_I32: c = m_.op_r(OpSGreaterThan, tbool_, {ia(), ib()}); break;
    case Op::V_CMP_NE_I32: case Op::V_CMP_NE_U32: c = m_.op_r(OpINotEqual, tbool_, {ua(), ub()}); break;
    case Op::V_CMP_GE_I32: c = m_.op_r(OpSGreaterThanEqual, tbool_, {ia(), ib()}); break;
    case Op::V_CMP_LT_U32: case Op::V_CMPX_LT_U32: c = m_.op_r(OpULessThan, tbool_, {ua(), ub()}); break;
    case Op::V_CMP_LE_U32: c = m_.op_r(OpULessThanEqual, tbool_, {ua(), ub()}); break;
    case Op::V_CMP_GT_U32: c = m_.op_r(OpUGreaterThan, tbool_, {ua(), ub()}); break;
    case Op::V_CMP_GE_U32: c = m_.op_r(OpUGreaterThanEqual, tbool_, {ua(), ub()}); break;
    case Op::V_CMP_CLASS_F32: {
        // class mask bits: 0 sNaN, 1 qNaN, 2 -inf, 3 -normal, 4 -denormal, 5 -0, 6 +0, 7 +denormal,
        // 8 +normal, 9 +inf
        const Id mask = ub();
        const Id x = u2f(ua());
        auto has = [&](uint32_t bit) {
            return m_.op_r(OpINotEqual, tbool_, {m_.op_r(OpBitwiseAnd, tu_, {mask, m_.c_u32(1u << bit)}), m_.c_u32(0)});
        };
        auto both = [&](Id p, Id q) { return m_.op_r(OpLogicalAnd, tbool_, {p, q}); };
        auto any = [&](Id p, Id q) { return m_.op_r(OpLogicalOr, tbool_, {p, q}); };
        const Id nan = m_.op_r(OpIsNan, tbool_, {x}), inf = m_.op_r(OpIsInf, tbool_, {x});
        const Id neg = m_.op_r(OpSLessThan, tbool_, {u2i(ua()), m_.c_i32(0)});
        const Id pos = m_.op_r(OpLogicalNot, tbool_, {neg});
        const Id ax = m_.ext(tf_, GlslFAbs, {x});
        const Id zero = m_.op_r(OpFOrdEqual, tbool_, {ax, m_.c_f32(0.0f)});
        const Id denorm = both(m_.op_r(OpFOrdLessThan, tbool_, {ax, m_.c_f32(1.17549435e-38f)}),
                               m_.op_r(OpLogicalNot, tbool_, {zero}));
        const Id normal = both(m_.op_r(OpLogicalNot, tbool_, {any(any(nan, inf), any(zero, denorm))}), m_.c_bool(true));
        Id r = both(nan, any(has(0), has(1)));
        r = any(r, both(both(inf, neg), has(2)));
        r = any(r, both(both(normal, neg), has(3)));
        r = any(r, both(both(denorm, neg), has(4)));
        r = any(r, both(both(zero, neg), has(5)));
        r = any(r, both(both(zero, pos), has(6)));
        r = any(r, both(both(denorm, pos), has(7)));
        r = any(r, both(both(normal, pos), has(8)));
        r = any(r, both(both(inf, pos), has(9)));
        c = r;
        break;
    }
    default:
        problem(std::string("compare ") + op_name(in.op));
        c = m_.c_bool(false);
    }
    // inactive lanes write 0
    if (exec_changes_) c = m_.op_r(OpLogicalAnd, tbool_, {c, exec_bit()});
    const uint32_t dst = in.enc == Enc::VOP3 ? in.dst.code : 106;
    write_mask(dst, c);
    if (in.op == Op::V_CMPX_EQ_I32 || in.op == Op::V_CMPX_LT_U32) write_mask(126, c);
}

void Translator::emit_vop(const Inst& in) {
    auto f = [&](int i) { return read_f(in.src[i], in); };
    auto u = [&](int i) { return read_u(in.src[i], in); };
    auto si = [&](int i) { return read_i(in.src[i], in); };
    auto wf = [&](Id v) { write_vf(in, v); };
    auto wu = [&](Id v) { write_v(uint32_t(in.dst.vgpr()), v); };
    auto legacy_mul = [&](Id a, Id b) {  // 0 * anything = 0 (D3D9 rules)
        const Id z = m_.op_r(OpLogicalOr, tbool_, {m_.op_r(OpFOrdEqual, tbool_, {a, m_.c_f32(0.0f)}),
                                                     m_.op_r(OpFOrdEqual, tbool_, {b, m_.c_f32(0.0f)})});
        return m_.op_r(OpSelect, tf_, {z, m_.c_f32(0.0f), m_.op_r(OpFMul, tf_, {a, b})});
    };
    auto dstf = [&] { return u2f(ld(vreg(uint32_t(in.dst.vgpr())), tu_)); };
    auto i24 = [&](Id x) {  // sign-extend the low 24 bits
        return m_.op_r(OpShiftRightArithmetic, ti_, {m_.op_r(OpShiftLeftLogical, ti_, {x, m_.c_u32(8)}), m_.c_u32(8)});
    };
    auto u24 = [&](Id x) { return m_.op_r(OpBitwiseAnd, tu_, {x, m_.c_u32(0xFFFFFF)}); };
    switch (in.op) {
    case Op::V_MOV_B32: wu(u(0)); return;
    case Op::V_READFIRSTLANE_B32: write_s(in.dst.code - 256, u(0)); return;  // own lane (uniform in practice)
    case Op::V_ADD_F32: wf(m_.op_r(OpFAdd, tf_, {f(0), f(1)})); return;
    case Op::V_SUB_F32: wf(m_.op_r(OpFSub, tf_, {f(0), f(1)})); return;
    case Op::V_SUBREV_F32: wf(m_.op_r(OpFSub, tf_, {f(1), f(0)})); return;
    case Op::V_MUL_F32: wf(m_.op_r(OpFMul, tf_, {f(0), f(1)})); return;
    case Op::V_MUL_LEGACY_F32: wf(legacy_mul(f(0), f(1))); return;
    case Op::V_MAC_F32: wf(m_.op_r(OpFAdd, tf_, {m_.op_r(OpFMul, tf_, {f(0), f(1)}), dstf()})); return;
    case Op::V_MAC_LEGACY_F32: wf(m_.op_r(OpFAdd, tf_, {legacy_mul(f(0), f(1)), dstf()})); return;
    case Op::V_MAD_F32: wf(m_.op_r(OpFAdd, tf_, {m_.op_r(OpFMul, tf_, {f(0), f(1)}), f(2)})); return;
    case Op::V_FMA_F32: wf(m_.ext(tf_, GlslFma, {f(0), f(1), f(2)})); return;
    case Op::V_MAD_LEGACY_F32: wf(m_.op_r(OpFAdd, tf_, {legacy_mul(f(0), f(1)), f(2)})); return;
    case Op::V_MADMK_F32:  // src0 * K + vsrc1
        wf(m_.op_r(OpFAdd, tf_, {m_.op_r(OpFMul, tf_, {f(0), u2f(m_.c_u32(in.literal))}), f(1)}));
        return;
    case Op::V_MADAK_F32:  // src0 * vsrc1 + K
        wf(m_.op_r(OpFAdd, tf_, {m_.op_r(OpFMul, tf_, {f(0), f(1)}), u2f(m_.c_u32(in.literal))}));
        return;
    case Op::V_MIN_F32: case Op::V_MIN_LEGACY_F32: wf(m_.ext(tf_, GlslNMin, {f(0), f(1)})); return;
    case Op::V_MAX_F32: case Op::V_MAX_LEGACY_F32: wf(m_.ext(tf_, GlslNMax, {f(0), f(1)})); return;
    case Op::V_MIN3_F32: wf(m_.ext(tf_, GlslNMin, {m_.ext(tf_, GlslNMin, {f(0), f(1)}), f(2)})); return;
    case Op::V_MAX3_F32: wf(m_.ext(tf_, GlslNMax, {m_.ext(tf_, GlslNMax, {f(0), f(1)}), f(2)})); return;
    case Op::V_MED3_F32: {
        const Id a = f(0), b = f(1), c = f(2);
        wf(m_.ext(tf_, GlslNMax, {m_.ext(tf_, GlslNMin, {a, b}), m_.ext(tf_, GlslNMin, {m_.ext(tf_, GlslNMax, {a, b}), c})}));
        return;
    }
    case Op::V_MIN_I32: wu(i2u(m_.ext(ti_, GlslSMin, {si(0), si(1)}))); return;
    case Op::V_MAX_I32: wu(i2u(m_.ext(ti_, GlslSMax, {si(0), si(1)}))); return;
    case Op::V_FRACT_F32: wf(m_.ext(tf_, GlslFract, {f(0)})); return;
    case Op::V_TRUNC_F32: wf(m_.ext(tf_, GlslTrunc, {f(0)})); return;
    case Op::V_CEIL_F32: wf(m_.ext(tf_, GlslCeil, {f(0)})); return;
    case Op::V_RNDNE_F32: wf(m_.ext(tf_, GlslRoundEven, {f(0)})); return;
    case Op::V_FLOOR_F32: wf(m_.ext(tf_, GlslFloor, {f(0)})); return;
    case Op::V_EXP_F32: wf(m_.ext(tf_, GlslExp2, {f(0)})); return;
    case Op::V_LOG_F32: wf(m_.ext(tf_, GlslLog2, {f(0)})); return;
    case Op::V_RCP_F32: wf(m_.op_r(OpFDiv, tf_, {m_.c_f32(1.0f), f(0)})); return;
    case Op::V_RSQ_F32: wf(m_.ext(tf_, GlslInverseSqrt, {f(0)})); return;
    case Op::V_RSQ_CLAMP_F32:
        wf(m_.ext(tf_, GlslNClamp, {m_.ext(tf_, GlslInverseSqrt, {f(0)}), m_.c_f32(-3.40282347e38f), m_.c_f32(3.40282347e38f)}));
        return;
    case Op::V_SQRT_F32: wf(m_.ext(tf_, GlslSqrt, {f(0)})); return;
    case Op::V_SIN_F32: wf(m_.ext(tf_, GlslSin, {m_.op_r(OpFMul, tf_, {f(0), m_.c_f32(6.28318530718f)})})); return;
    case Op::V_COS_F32: wf(m_.ext(tf_, GlslCos, {m_.op_r(OpFMul, tf_, {f(0), m_.c_f32(6.28318530718f)})})); return;
    case Op::V_CVT_F32_I32: wf(m_.op_r(OpConvertSToF, tf_, {si(0)})); return;
    case Op::V_CVT_F32_U32: wf(m_.op_r(OpConvertUToF, tf_, {u(0)})); return;
    case Op::V_CVT_I32_F32: wu(i2u(m_.op_r(OpConvertFToS, ti_, {f(0)}))); return;
    case Op::V_CVT_U32_F32: wu(m_.op_r(OpConvertFToU, tu_, {m_.ext(tf_, GlslFMax, {f(0), m_.c_f32(0.0f)})})); return;
    case Op::V_CVT_PKRTZ_F16_F32:
        wu(m_.ext(tu_, GlslPackHalf2x16, {m_.op_r(OpCompositeConstruct, tv2f_, {f(0), f(1)})}));
        return;
    case Op::V_CVT_PKNORM_U16_F32:
        wu(m_.ext(tu_, GlslPackUnorm2x16, {m_.op_r(OpCompositeConstruct, tv2f_, {f(0), f(1)})}));
        return;
    case Op::V_CNDMASK_B32: {
        const Id mask = in.enc == Enc::VOP3 ? bit0(u(2)) : bit0(ld(sreg(106), tu_));
        wu(m_.op_r(OpSelect, tu_, {mask, u(1), u(0)}));
        return;
    }
    case Op::V_ADD_I32: case Op::V_SUB_I32: {
        const Id a = u(0), b = u(1);
        const Id v = m_.op_r(in.op == Op::V_ADD_I32 ? OpIAdd : OpISub, tu_, {a, b});
        wu(v);
        const Id carry = in.op == Op::V_ADD_I32 ? m_.op_r(OpULessThan, tbool_, {v, a}) : m_.op_r(OpULessThan, tbool_, {a, b});
        write_mask(in.enc == Enc::VOP3 ? in.sdst.code : 106, carry);
        return;
    }
    case Op::V_MUL_I32_I24: wu(i2u(m_.op_r(OpIMul, ti_, {i24(si(0)), i24(si(1))}))); return;
    case Op::V_MAD_I32_I24: wu(i2u(m_.op_r(OpIAdd, ti_, {m_.op_r(OpIMul, ti_, {i24(si(0)), i24(si(1))}), si(2)}))); return;
    case Op::V_MAD_U32_U24: wu(m_.op_r(OpIAdd, tu_, {m_.op_r(OpIMul, tu_, {u24(u(0)), u24(u(1))}), u(2)})); return;
    case Op::V_MUL_LO_U32: case Op::V_MUL_LO_I32: wu(m_.op_r(OpIMul, tu_, {u(0), u(1)})); return;
    case Op::V_MUL_HI_U32: {
        const Id st2 = m_.t_struct({tu_, tu_});
        const Id r = m_.op_r(OpUMulExtended, st2, {u(0), u(1)});
        wu(m_.op_r(OpCompositeExtract, tu_, {r, 1}));
        return;
    }
    case Op::V_LSHLREV_B32: wu(m_.op_r(OpShiftLeftLogical, tu_, {u(1), m_.op_r(OpBitwiseAnd, tu_, {u(0), m_.c_u32(31)})})); return;
    case Op::V_LSHRREV_B32: wu(m_.op_r(OpShiftRightLogical, tu_, {u(1), m_.op_r(OpBitwiseAnd, tu_, {u(0), m_.c_u32(31)})})); return;
    case Op::V_AND_B32: wu(m_.op_r(OpBitwiseAnd, tu_, {u(0), u(1)})); return;
    case Op::V_OR_B32: wu(m_.op_r(OpBitwiseOr, tu_, {u(0), u(1)})); return;
    case Op::V_XOR_B32: wu(m_.op_r(OpBitwiseXor, tu_, {u(0), u(1)})); return;
    case Op::V_NOT_B32: wu(m_.op_r(OpNot, tu_, {u(0)})); return;
    case Op::V_BFE_U32:
        wu(m_.op_r(OpBitFieldUExtract, tu_, {u(0), m_.op_r(OpBitwiseAnd, tu_, {u(1), m_.c_u32(31)}),
                                             m_.op_r(OpBitwiseAnd, tu_, {u(2), m_.c_u32(31)})}));
        return;
    case Op::V_LSHL_B64: {  // v[d:d+1] = v[s:s+1] << n (n < 64)
        const Id lo = u(0);
        Operand h = in.src[0];
        h.code = uint16_t(h.code + 1);
        const Id hiv = read_u(h, in);
        const Id n = m_.op_r(OpBitwiseAnd, tu_, {u(1), m_.c_u32(63)});
        const Id big = m_.op_r(OpUGreaterThanEqual, tbool_, {n, m_.c_u32(32)});
        const Id n32 = m_.op_r(OpBitwiseAnd, tu_, {n, m_.c_u32(31)});
        const Id lo_s = m_.op_r(OpShiftLeftLogical, tu_, {lo, n32});
        const Id carry = m_.op_r(OpSelect, tu_, {m_.op_r(OpIEqual, tbool_, {n32, m_.c_u32(0)}), m_.c_u32(0),
                                                 m_.op_r(OpShiftRightLogical, tu_, {lo, m_.op_r(OpISub, tu_, {m_.c_u32(32), n32})})});
        const Id hi_s = m_.op_r(OpBitwiseOr, tu_, {m_.op_r(OpShiftLeftLogical, tu_, {hiv, n32}), carry});
        write_v(uint32_t(in.dst.vgpr()), m_.op_r(OpSelect, tu_, {big, m_.c_u32(0), lo_s}));
        write_v(uint32_t(in.dst.vgpr()) + 1, m_.op_r(OpSelect, tu_, {big, lo_s, hi_s}));
        return;
    }
    case Op::V_CUBEID_F32: case Op::V_CUBESC_F32: case Op::V_CUBETC_F32: case Op::V_CUBEMA_F32: {
        const Id x = f(0), y = f(1), z = f(2);
        const Id ax = m_.ext(tf_, GlslFAbs, {x}), ay = m_.ext(tf_, GlslFAbs, {y}), az = m_.ext(tf_, GlslFAbs, {z});
        const Id zmaj = m_.op_r(OpLogicalAnd, tbool_, {m_.op_r(OpFOrdGreaterThanEqual, tbool_, {az, ax}),
                                                        m_.op_r(OpFOrdGreaterThanEqual, tbool_, {az, ay})});
        const Id ymaj = m_.op_r(OpLogicalAnd, tbool_, {m_.op_r(OpLogicalNot, tbool_, {zmaj}),
                                                        m_.op_r(OpFOrdGreaterThanEqual, tbool_, {ay, ax})});
        auto sel = [&](Id c, Id a, Id b) { return m_.op_r(OpSelect, tf_, {c, a, b}); };
        auto neg = [&](Id a) { return m_.op_r(OpFNegate, tf_, {a}); };
        auto lt0 = [&](Id a) { return m_.op_r(OpFOrdLessThan, tbool_, {a, m_.c_f32(0.0f)}); };
        Id r;
        if (in.op == Op::V_CUBEID_F32) {
            r = sel(zmaj, sel(lt0(z), m_.c_f32(5.0f), m_.c_f32(4.0f)),
                    sel(ymaj, sel(lt0(y), m_.c_f32(3.0f), m_.c_f32(2.0f)), sel(lt0(x), m_.c_f32(1.0f), m_.c_f32(0.0f))));
        } else if (in.op == Op::V_CUBESC_F32) {
            r = sel(zmaj, sel(lt0(z), neg(x), x), sel(ymaj, x, sel(lt0(x), z, neg(z))));
        } else if (in.op == Op::V_CUBETC_F32) {
            r = sel(zmaj, neg(y), sel(ymaj, sel(lt0(y), neg(z), z), neg(y)));
        } else {
            r = m_.op_r(OpFMul, tf_, {m_.c_f32(2.0f), sel(zmaj, z, sel(ymaj, y, x))});
            r = m_.ext(tf_, GlslFAbs, {r});
        }
        wf(r);
        return;
    }
    // SGPR spills into VGPR lanes: lane-select is a constant, values are uniform; each
    // (VGPR, lane) becomes its own private variable
    case Op::V_WRITELANE_B32: {
        if (!in.src[1].is_inline_const()) { problem("v_writelane with a register lane select"); return; }
        st(spill_var(uint32_t(in.dst.vgpr()), inline_constant(in.src[1].code)), u(0));
        return;
    }
    case Op::V_READLANE_B32: {
        if (!in.src[1].is_inline_const() || !in.src[0].is_vgpr()) { write_s(in.dst.code, u(0)); return; }
        write_s(in.dst.code, ld(spill_var(uint32_t(in.src[0].vgpr()), inline_constant(in.src[1].code)), tu_));
        return;
    }
    default:
        if (in.enc == Enc::VOPC || (in.enc == Enc::VOP3 && in.opnum < 0x100)) return emit_cmp(in);
        problem(std::string("vector instruction ") + op_name(in.op));
    }
}

void Translator::emit_interp(const Inst& in) {
    const uint32_t attr = in.attr, chan = in.chan;
    if (in.op == Op::V_INTERP_P1_F32) return;  // the second half (p2) produces the value
    const bool flat = in.op == Op::V_INTERP_MOV_F32;
    auto& map = flat ? ps_flat_inputs_ : ps_inputs_;
    const uint32_t loc = d_.remap_inputs ? d_.input_location[attr & 31] : attr;
    if (loc == 0xFF) {  // the vertex shader does not export this semantic
        write_v(uint32_t(in.dst.vgpr()), m_.c_u32(0));
        return;
    }
    Id& var = map[attr];
    if (!var) {
        var = global(m_.t_ptr(SCInput, tv4f_), SCInput);
        m_.decorate(var, DecLocation, {loc});
        if (flat) m_.decorate(var, DecFlat);
        (flat ? r_.ps_flat_inputs : r_.ps_inputs) |= 1u << attr;
        if ((r_.ps_flat_inputs & r_.ps_inputs) >> attr & 1) problem("attribute read both flat and interpolated");
    }
    const Id v = ld(var, tv4f_);
    write_v(uint32_t(in.dst.vgpr()), f2u(m_.op_r(OpCompositeExtract, tf_, {v, chan})));
}

void Translator::emit_exp(const Inst& in) {
    const uint32_t t = in.exp_target;
    auto src_f = [&](int k) { return u2f(ld(vreg(in.exp_src[k]), tu_)); };
    auto vec4 = [&]() {
        if (in.exp_compr) {  // two packed half2 registers
            const Id a = m_.op_r(OpExtInst, tv2f_, {m_.glsl(), 62 /*UnpackHalf2x16*/, ld(vreg(in.exp_src[0]), tu_)});
            const Id b = m_.op_r(OpExtInst, tv2f_, {m_.glsl(), 62, ld(vreg(in.exp_src[1]), tu_)});
            return m_.op_r(OpVectorShuffle, tv4f_, {a, b, 0, 1, 2, 3});
        }
        Id c[4];
        for (int k = 0; k < 4; ++k) c[k] = (in.exp_en >> k & 1) ? src_f(k) : m_.c_f32(0.0f);
        return m_.op_r(OpCompositeConstruct, tv4f_, {c[0], c[1], c[2], c[3]});
    };
    if (d_.stage == Stage::Vertex) {
        if (t == 12) {  // POS0
            if (!position_out_) {
                position_out_ = global(m_.t_ptr(SCOutput, tv4f_), SCOutput);
                m_.decorate(position_out_, DecBuiltIn, {BuiltInPosition});
            }
            st(position_out_, vec4());
        } else if (t >= 32 && t < 64) {
            Id& var = outputs_[t - 32];
            if (!var) {
                var = global(m_.t_ptr(SCOutput, tv4f_), SCOutput);
                m_.decorate(var, DecLocation, {t - 32});
                r_.param_exports |= 1u << (t - 32);
            }
            st(var, vec4());
        } else if (t >= 13 && t <= 15) {
            // POS1..3 (point size, clip distances): not used by the native pipelines yet
        } else problem("vertex export target " + std::to_string(t));
        return;
    }
    // pixel
    if (in.exp_done && exec_changes_) {
        // a lane killed by EXEC (v_cmpx / exec masking) writes nothing: discard it
        const Id l_kill = m_.label(), l_cont = m_.label();
        const Id alive = exec_bit();
        m_.op(OpSelectionMerge, {l_cont, 0});
        m_.op(OpBranchConditional, {alive, l_cont, l_kill});
        m_.place_label(l_kill);
        m_.op(OpDemoteToHelperInvocation, {});
        m_.op(OpBranch, {l_cont});
        m_.place_label(l_cont);
        r_.discards = true;
        m_.capability(CapDemoteToHelperInvocation);
    }
    if (t < 8) {
        Id& var = outputs_[t];
        if (!var) {
            var = global(m_.t_ptr(SCOutput, tv4f_), SCOutput);
            m_.decorate(var, DecLocation, {t});
            r_.color_outputs |= 1u << t;
        }
        st(var, vec4());
    } else if (t == 8) {  // MRTZ: depth in x
        if (!frag_depth_) {
            frag_depth_ = global(m_.t_ptr(SCOutput, tf_), SCOutput);
            m_.decorate(frag_depth_, DecBuiltIn, {BuiltInFragDepth});
            r_.writes_depth = true;
        }
        if (in.exp_en & 1) st(frag_depth_, src_f(0));
    } else if (t == 9) {  // NULL export
    } else problem("pixel export target " + std::to_string(t));
}

void Translator::emit_mimg(const Inst& in, size_t index) {
    const ResRef tex = resolve(in.srsrc, index, kUsageImmResource);
    const bool sampling = in.op != Op::IMAGE_LOAD && in.op != Op::IMAGE_LOAD_MIP && in.op != Op::IMAGE_GET_RESINFO;
    ResRef smp{};
    if (sampling) smp = resolve(in.ssamp, index, kUsageImmSampler);
    if (!tex.ok || (sampling && !smp.ok)) {
        char at[32];
        std::snprintf(at, sizeof at, getenv("D1_TRANSLATE_VERBOSE") ? " (at %#x)" : "", in.pc);
        problem(std::string(op_name(in.op)) + " with an unresolved " + (!tex.ok ? "T#" : "S#") + at);
        return;
    }
    const TexDim td = tex.api < 16 ? d_.tex_dims[tex.api] : TexDim::Tex2D;
    const uint32_t ncoord = td == TexDim::Tex2D ? 2 : 3;  // 2D array / 3D / cube: 3 address VGPRs
    const Dim dim = td == TexDim::Tex3D ? Dim3D : td == TexDim::Cube ? DimCube : Dim2D;
    const Id img_t = m_.t_image(tf_, dim, false, td == TexDim::Tex2DArray, false, 1);
    const Id image = ld(texture_var(tex.api), img_t);
    uint32_t a = in.vaddr;
    auto af = [&](uint32_t k) { return u2f(ld(vreg(k), tu_)); };
    auto au = [&](uint32_t k) { return ld(vreg(k), tu_); };
    // address order: {offset}{bias}{z-compare}{derivatives}{coords}{lod}
    Id offset = 0, bias = 0, dref = 0;
    if (in.op == Op::IMAGE_SAMPLE_LZ_O || in.op == Op::IMAGE_GATHER4_LZ_O) {
        const Id packed = au(a++);
        auto field6 = [&](uint32_t shift) {
            return m_.op_r(OpBitFieldSExtract, ti_, {u2i(packed), m_.c_u32(shift), m_.c_u32(6)});
        };
        offset = m_.op_r(OpCompositeConstruct, tv2i_, {field6(0), field6(8)});
        m_.capability(CapImageGatherExtended);  // offsets come from a register
    }
    if (in.op == Op::IMAGE_SAMPLE_B) bias = af(a++);
    if (in.op == Op::IMAGE_SAMPLE_C || in.op == Op::IMAGE_SAMPLE_C_LZ) dref = af(a++);
    Id ddx = 0, ddy = 0;
    if (in.op == Op::IMAGE_SAMPLE_D) {
        const uint32_t nd = td == TexDim::Tex3D || td == TexDim::Cube ? 3 : 2;
        Id dx[3], dy[3];
        for (uint32_t k = 0; k < nd; ++k) dx[k] = af(a++);
        for (uint32_t k = 0; k < nd; ++k) dy[k] = af(a++);
        ddx = nd == 2 ? m_.op_r(OpCompositeConstruct, tv2f_, {dx[0], dx[1]}) : m_.op_r(OpCompositeConstruct, tv3f_, {dx[0], dx[1], dx[2]});
        ddy = nd == 2 ? m_.op_r(OpCompositeConstruct, tv2f_, {dy[0], dy[1]}) : m_.op_r(OpCompositeConstruct, tv3f_, {dy[0], dy[1], dy[2]});
    }
    if (td == TexDim::Cube) problem("cube map sampling (face coordinates) not translated exactly yet");
    auto write_result = [&](Id vec4, bool is_uint) {
        uint32_t out = in.vdata;
        const uint32_t mask = (in.op == Op::IMAGE_GATHER4_LZ || in.op == Op::IMAGE_GATHER4_LZ_O) ? 0xF : in.dmask;
        for (uint32_t c = 0; c < 4; ++c) {
            if (!(mask >> c & 1)) continue;
            const Id comp = m_.op_r(OpCompositeExtract, is_uint ? tu_ : tf_, {vec4, c});
            write_v(out++, is_uint ? comp : f2u(comp));
        }
    };
    if (in.op == Op::IMAGE_GET_RESINFO) {
        m_.capability(CapImageQuery);
        const Id lod = u2i(au(a));
        const Id sz = m_.op_r(OpImageQuerySizeLod, td == TexDim::Tex2D ? tv2i_ : tv3i_, {image, lod});
        const Id levels = m_.op_r(OpImageQueryLevels, ti_, {image});
        Id w = m_.op_r(OpCompositeExtract, ti_, {sz, 0}), h = m_.op_r(OpCompositeExtract, ti_, {sz, 1});
        Id dd = td == TexDim::Tex2D ? m_.c_i32(1) : m_.op_r(OpCompositeExtract, ti_, {sz, 2});
        const Id v = m_.op_r(OpCompositeConstruct, tv4u_, {i2u(w), i2u(h), i2u(dd), i2u(levels)});
        write_result(v, true);
        return;
    }
    if (in.op == Op::IMAGE_LOAD || in.op == Op::IMAGE_LOAD_MIP) {
        Id c[3];
        for (uint32_t k = 0; k < ncoord; ++k) c[k] = u2i(au(a++));
        const Id coord = ncoord == 2 ? m_.op_r(OpCompositeConstruct, tv2i_, {c[0], c[1]}) : m_.op_r(OpCompositeConstruct, tv3i_, {c[0], c[1], c[2]});
        const Id lod = in.op == Op::IMAGE_LOAD_MIP ? u2i(au(a++)) : m_.c_i32(0);
        const Id v = m_.op_rv(OpImageFetch, tv4f_, {image, coord, 2 /*Lod*/, lod});
        write_result(v, false);
        return;
    }
    Id c[3];
    for (uint32_t k = 0; k < ncoord; ++k) c[k] = af(a++);
    if (in.unorm) problem("unnormalized texture coordinates");
    const Id coord = ncoord == 2 ? m_.op_r(OpCompositeConstruct, tv2f_, {c[0], c[1]}) : m_.op_r(OpCompositeConstruct, tv3f_, {c[0], c[1], c[2]});
    const Id sampler = ld(sampler_var(smp.api), m_.t_sampler());
    const Id si = m_.op_r(OpSampledImage, m_.t_sampled_image(img_t), {image, sampler});
    Id v = 0;
    switch (in.op) {
    case Op::IMAGE_SAMPLE:
        v = d_.stage == Stage::Pixel ? m_.op_r(OpImageSampleImplicitLod, tv4f_, {si, coord})
                                     : m_.op_rv(OpImageSampleExplicitLod, tv4f_, {si, coord, 2, m_.c_f32(0.0f)});
        break;
    case Op::IMAGE_SAMPLE_B:
        v = d_.stage == Stage::Pixel ? m_.op_rv(OpImageSampleImplicitLod, tv4f_, {si, coord, 1 /*Bias*/, bias})
                                     : m_.op_rv(OpImageSampleExplicitLod, tv4f_, {si, coord, 2, m_.c_f32(0.0f)});
        break;
    case Op::IMAGE_SAMPLE_L: v = m_.op_rv(OpImageSampleExplicitLod, tv4f_, {si, coord, 2, af(a)}); break;
    case Op::IMAGE_SAMPLE_LZ: v = m_.op_rv(OpImageSampleExplicitLod, tv4f_, {si, coord, 2, m_.c_f32(0.0f)}); break;
    case Op::IMAGE_SAMPLE_LZ_O: {
        // Vulkan allows register offsets only on gathers: apply the texel offset to the
        // coordinates (exact at LOD 0)
        m_.capability(CapImageQuery);
        const Id size = m_.op_r(OpImageQuerySizeLod, td == TexDim::Tex2D ? tv2i_ : tv3i_, {image, m_.c_i32(0)});
        const Id sx = m_.op_r(OpConvertSToF, tf_, {m_.op_r(OpCompositeExtract, ti_, {size, 0})});
        const Id sy = m_.op_r(OpConvertSToF, tf_, {m_.op_r(OpCompositeExtract, ti_, {size, 1})});
        const Id ox = m_.op_r(OpConvertSToF, tf_, {m_.op_r(OpCompositeExtract, ti_, {offset, 0})});
        const Id oy = m_.op_r(OpConvertSToF, tf_, {m_.op_r(OpCompositeExtract, ti_, {offset, 1})});
        Id cc[3] = {m_.op_r(OpFAdd, tf_, {c[0], m_.op_r(OpFDiv, tf_, {ox, sx})}),
                    m_.op_r(OpFAdd, tf_, {c[1], m_.op_r(OpFDiv, tf_, {oy, sy})}), ncoord > 2 ? c[2] : 0};
        const Id oc = ncoord == 2 ? m_.op_r(OpCompositeConstruct, tv2f_, {cc[0], cc[1]})
                                  : m_.op_r(OpCompositeConstruct, tv3f_, {cc[0], cc[1], cc[2]});
        v = m_.op_rv(OpImageSampleExplicitLod, tv4f_, {si, oc, 2, m_.c_f32(0.0f)});
        break;
    }
    case Op::IMAGE_SAMPLE_D: v = m_.op_rv(OpImageSampleExplicitLod, tv4f_, {si, coord, 4 /*Grad*/, ddx, ddy}); break;
    case Op::IMAGE_SAMPLE_C: case Op::IMAGE_SAMPLE_C_LZ: {
        // depth comparison: sampled through a non-depth image; compare in the shader
        const Id s = m_.op_rv(OpImageSampleExplicitLod, tv4f_, {si, coord, 2, m_.c_f32(0.0f)});
        const Id d = m_.op_r(OpCompositeExtract, tf_, {s, 0});
        const Id r = m_.op_r(OpSelect, tf_, {m_.op_r(OpFOrdLessThanEqual, tbool_, {dref, d}), m_.c_f32(1.0f), m_.c_f32(0.0f)});
        v = m_.op_r(OpCompositeConstruct, tv4f_, {r, r, r, r});
        problem("depth-compare sampling done as a point comparison");
        break;
    }
    case Op::IMAGE_GATHER4_LZ: case Op::IMAGE_GATHER4_LZ_O: {
        uint32_t comp = 0;
        while (comp < 3 && !(in.dmask >> comp & 1)) ++comp;
        if (offset) v = m_.op_rv(OpImageGather, tv4f_, {si, coord, m_.c_u32(comp), 0x10, offset});
        else v = m_.op_r(OpImageGather, tv4f_, {si, coord, m_.c_u32(comp)});
        break;
    }
    case Op::IMAGE_GET_LOD: {
        m_.capability(CapImageQuery);
        const Id l = m_.op_r(OpImageQueryLod, tv2f_, {si, coord});
        v = m_.op_r(OpVectorShuffle, tv4f_, {l, l, 0, 1, 0, 1});
        break;
    }
    default:
        problem(std::string("image instruction ") + op_name(in.op));
        return;
    }
    write_result(v, false);
}

// Typed / untyped buffer loads outside the fetch shader (skinning matrices and the like): the
// engine binds these as constant buffers (V# stride 16), so they read the same storage buffer.
void Translator::emit_buffer_load(const Inst& in, size_t index) {
    const ResRef cb = resolve(in.srsrc, index, kUsageImmConstBuffer);
    if (!cb.ok) {
        problem(std::string(op_name(in.op)) + " from an unresolved buffer");
        return;
    }
    uint32_t n = 0;
    if (in.enc == Enc::MTBUF) {
        // 32-bit formats only (copied as raw dwords; float/uint/sint all keep their bits)
        static const uint8_t dwords[16] = {0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 2, 0, 3, 4, 0};
        if (!dwords[in.dfmt] || (in.nfmt != 4 && in.nfmt != 5 && in.nfmt != 7)) {
            problem("typed buffer load format " + std::to_string(in.dfmt) + "/" + std::to_string(in.nfmt));
            return;
        }
        n = std::min<uint32_t>(dwords[in.dfmt], in.opnum + 1);
    } else if (in.op == Op::BUFFER_LOAD_DWORD) {
        n = 1;
    } else {
        problem(std::string(op_name(in.op)) + " outside a fetch shader");
        return;
    }
    Id addr = m_.c_u32(in.mem_offset);
    uint32_t va = in.vaddr;
    if (in.idxen) addr = m_.op_r(OpIAdd, tu_, {addr, m_.op_r(OpIMul, tu_, {ld(vreg(va++), tu_), m_.c_u32(16)})});
    if (in.offen) addr = m_.op_r(OpIAdd, tu_, {addr, ld(vreg(va++), tu_)});
    addr = m_.op_r(OpIAdd, tu_, {addr, read_u(in.soffset, in)});
    const Id base = m_.op_r(OpShiftRightLogical, tu_, {addr, m_.c_u32(2)});
    const Id var = cbuffer_var(cb.api);
    const Id pu = m_.t_ptr(SCStorageBuffer, tu_);
    for (uint32_t i = 0; i < n; ++i) {
        const Id p = m_.op_r(OpAccessChain, pu, {var, m_.c_u32(0), m_.op_r(OpIAdd, tu_, {base, m_.c_u32(i)})});
        write_v(in.vdata + i, ld(p, tu_));
    }
}

void Translator::emit(const Inst& in, size_t index) {
    switch (in.enc) {
    case Enc::SOP1: case Enc::SOP2: case Enc::SOPK: case Enc::SOPC:
        if (in.op == Op::S_SWAPPC_B64) return emit_fetch_call();
        return emit_scalar(in);
    case Enc::SOPP: return;  // control flow is handled by the caller; waits / nops vanish
    case Enc::SMRD: return emit_smrd(in, index);
    case Enc::VOP1: case Enc::VOP2: case Enc::VOPC: case Enc::VOP3: return emit_vop(in);
    case Enc::VINTRP: return emit_interp(in);
    case Enc::MIMG: return emit_mimg(in, index);
    case Enc::EXP: return emit_exp(in);
    case Enc::MTBUF: case Enc::MUBUF: return emit_buffer_load(in, index);
    case Enc::DS:
        if (in.op == Op::DS_SWIZZLE_B32) {
            // quad-permute mode (offset bit 15) with one source lane for the whole quad: the
            // manual derivative pattern; a quad broadcast does exactly that
            const uint32_t off = uint32_t(in.ds_offset1) << 8 | in.ds_offset0;
            const uint32_t sel = off & 3;
            const bool uniform = ((off >> 2) & 3) == sel && ((off >> 4) & 3) == sel && ((off >> 6) & 3) == sel;
            if ((off & 0x8000) && uniform) {
                m_.capability(CapGroupNonUniform);
                m_.capability(CapGroupNonUniformQuad);
                const Id v = m_.op_r(OpGroupNonUniformQuadBroadcast, tu_,
                                     {m_.c_u32(3 /*Subgroup*/), ld(vreg(uint32_t(in.src[0].vgpr())), tu_), m_.c_u32(sel)});
                write_v(uint32_t(in.dst.vgpr()), v);
                return;
            }
            problem("ds_swizzle pattern " + std::to_string(off));
            return;
        }
        problem(std::string("instruction ") + op_name(in.op));
        return;
    default:
        problem(std::string("instruction ") + op_name(in.op));
    }
}

void Translator::run() {
    types();
    prog_ = decode(d_.code, d_.code_size);
    for (auto& p : prog_.problems) problem("decode: " + p);
    if (!prog_.ended) problem("program has no end");
    for (const Inst& in : prog_.insts)
        if ((in.enc == Enc::SOP1 || in.enc == Enc::SOP2) && in.dst.code == 126) exec_changes_ = true;
        else if (in.op == Op::V_CMPX_EQ_I32 || in.op == Op::V_CMPX_LT_U32) exec_changes_ = true;
    analyse_origins(prog_);

    m_.capability(CapShader);
    const Id fn = m_.begin_function(tvoid_, m_.t_func(tvoid_));
    prologue();

    // Blocks: split at branch targets and after branches. Skip branches on EXEC are dropped.
    auto is_branch = [](Op op) {
        return op == Op::S_BRANCH || op == Op::S_CBRANCH_SCC0 || op == Op::S_CBRANCH_SCC1 ||
               op == Op::S_CBRANCH_VCCZ || op == Op::S_CBRANCH_VCCNZ;
    };
    std::set<uint32_t> starts{0};
    for (const Inst& in : prog_.insts)
        if (is_branch(in.op)) {
            starts.insert(uint32_t(int64_t(in.pc) + 4 + int64_t(in.simm16) * 4));
            starts.insert(in.pc + in.size);
        }
    const size_t n = prog_.insts.size();
    if (starts.size() == 1) {
        for (size_t k = 0; k < n; ++k) emit(prog_.insts[k], k);
        m_.op(OpReturn, {});
    } else {
        r_.uses_branches = true;
        // pc-dispatch loop: header -> switch on the block index -> block -> continue -> header
        std::map<uint32_t, uint32_t> block_of;  // start pc -> block index
        for (uint32_t s : starts) block_of[s] = uint32_t(block_of.size());
        const uint32_t end_block = uint32_t(block_of.size());
        const Id pc = global(tpu_, SCPrivate, m_.c_u32(0));
        m_.name(pc, "block");
        const Id l_header = m_.label(), l_switch = m_.label(), l_merge = m_.label(), l_cont = m_.label(),
                 l_sw_merge = m_.label();
        m_.op(OpBranch, {l_header});
        m_.place_label(l_header);
        m_.op(OpLoopMerge, {l_merge, l_cont, 0});
        m_.op(OpBranch, {l_switch});
        m_.place_label(l_switch);
        std::vector<Id> labels;
        std::vector<uint32_t> sw{ld(pc, tu_), l_sw_merge};
        for (uint32_t b = 0; b < end_block; ++b) {
            labels.push_back(m_.label());
            sw.push_back(b);
            sw.push_back(labels.back());
        }
        m_.op(OpSelectionMerge, {l_sw_merge, 0});
        m_.op_v(OpSwitch, sw);
        // blocks
        std::vector<uint32_t> bstart(block_of.size());
        for (auto& [spc, bi] : block_of) bstart[bi] = spc;
        size_t k = 0;
        for (uint32_t b = 0; b < end_block; ++b) {
            m_.place_label(labels[b]);
            const uint32_t next_start = b + 1 < end_block ? bstart[b + 1] : 0xFFFFFFFFu;
            while (k < n && prog_.insts[k].pc < bstart[b]) ++k;  // unreachable gap (should not happen)
            Id next = m_.c_u32(b + 1 < end_block ? b + 1 : end_block);
            bool ended = false;
            while (k < n && prog_.insts[k].pc < next_start) {
                const Inst& in = prog_.insts[k];
                if (is_branch(in.op)) {
                    const uint32_t tpc = uint32_t(int64_t(in.pc) + 4 + int64_t(in.simm16) * 4);
                    const uint32_t tb = block_of.count(tpc) ? block_of[tpc] : end_block;
                    if (in.op == Op::S_BRANCH) next = m_.c_u32(tb);
                    else {
                        Id cond;
                        if (in.op == Op::S_CBRANCH_SCC0) cond = m_.op_r(OpLogicalNot, tbool_, {ld(scc(), tbool_)});
                        else if (in.op == Op::S_CBRANCH_SCC1) cond = ld(scc(), tbool_);
                        else if (in.op == Op::S_CBRANCH_VCCZ) cond = m_.op_r(OpLogicalNot, tbool_, {bit0(ld(sreg(106), tu_))});
                        else cond = bit0(ld(sreg(106), tu_));
                        next = m_.op_r(OpSelect, tu_, {cond, m_.c_u32(tb), next});
                    }
                } else if (in.op == Op::S_ENDPGM) {
                    ended = true;
                } else {
                    emit(in, k);
                }
                ++k;
            }
            st(pc, ended ? m_.c_u32(end_block) : next);
            m_.op(OpBranch, {l_sw_merge});
        }
        m_.place_label(l_sw_merge);
        m_.op(OpBranch, {l_cont});
        m_.place_label(l_cont);
        const Id done = m_.op_r(OpUGreaterThanEqual, tbool_, {ld(pc, tu_), m_.c_u32(end_block)});
        m_.op(OpBranchConditional, {done, l_merge, l_header});
        m_.place_label(l_merge);
        m_.op(OpReturn, {});
    }
    m_.end_function();
    std::vector<Id> iface = interface_;
    if (d_.stage == Stage::Pixel) {
        m_.entry_point(ExecFragment, fn, "main", iface);
        m_.execution_mode(fn, ModeOriginUpperLeft);
        if (r_.writes_depth) m_.execution_mode(fn, ModeDepthReplacing);
    } else {
        m_.entry_point(ExecVertex, fn, "main", iface);
    }
    r_.spirv = m_.binary();
}

}  // namespace

Result translate(const ShaderDesc& d) {
    Result r;
    Translator t(d, r);
    t.run();
    return r;
}

}  // namespace d1::gcn

namespace d1::gcn {
std::vector<uint32_t> rect_list_gs(uint32_t param_exports) {
    using namespace d1::spv;
    Module m;
    m.capability(CapShader);
    m.capability(Capability(2));  // Geometry
    const Id tvoid = m.t_void(), tf = m.t_f32(), tv4 = m.t_vec(tf, 4), tu = m.t_u32();
    const Id arr = m.t_array(tv4, 3);
    const Id p_in = m.t_ptr(SCInput, arr), p_in_v = m.t_ptr(SCInput, tv4), p_out = m.t_ptr(SCOutput, tv4);
    (void)tu;
    std::vector<Id> iface;
    struct Var { Id in, out; };
    std::vector<Var> vars;
    {
        Var v{m.variable(p_in, SCInput), m.variable(p_out, SCOutput)};
        m.decorate(v.in, DecBuiltIn, {BuiltInPosition});
        m.decorate(v.out, DecBuiltIn, {BuiltInPosition});
        vars.push_back(v);
    }
    for (uint32_t l = 0; l < 32; ++l)
        if (param_exports >> l & 1) {
            Var v{m.variable(p_in, SCInput), m.variable(p_out, SCOutput)};
            m.decorate(v.in, DecLocation, {l});
            m.decorate(v.out, DecLocation, {l});
            vars.push_back(v);
        }
    for (auto& v : vars) iface.push_back(v.in), iface.push_back(v.out);
    const Id fn = m.begin_function(tvoid, m.t_func(tvoid));
    std::vector<std::array<Id, 4>> vals;
    for (auto& v : vars) {
        std::array<Id, 4> x{};
        for (uint32_t k = 0; k < 3; ++k)
            x[k] = m.op_r(OpLoad, tv4, {m.op_r(OpAccessChain, p_in_v, {v.in, m.c_u32(k)})});
        x[3] = m.op_r(OpFSub, tv4, {m.op_r(OpFAdd, tv4, {x[1], x[2]}), x[0]});
        vals.push_back(x);
    }
    for (uint32_t k = 0; k < 4; ++k) {
        for (size_t i = 0; i < vars.size(); ++i) m.op(OpStore, {vars[i].out, vals[i][k]});
        m.op(Opcode(218), {});  // OpEmitVertex
    }
    m.op(Opcode(219), {});  // OpEndPrimitive
    m.op(OpReturn, {});
    m.end_function();
    m.entry_point(ExecutionModel(3), fn, "main", iface);  // Geometry
    m.execution_mode(fn, ExecutionMode(22));               // Triangles
    m.execution_mode(fn, ExecutionMode(29));               // OutputTriangleStrip
    m.execution_mode(fn, ExecutionMode(26), {4});          // OutputVertices
    m.execution_mode(fn, ExecutionMode(0), {1});           // Invocations
    return m.binary();
}
}  // namespace d1::gcn
