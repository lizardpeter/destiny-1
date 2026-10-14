// Minimal SPIR-V module builder. See spirv.h.
#include "spirv.h"

#include <cstring>

namespace d1::spv {

Module::Module() = default;

void Module::put(std::vector<uint32_t>& s, Opcode o, std::initializer_list<uint32_t> w) {
    s.push_back(uint32_t(w.size() + 1) << 16 | o);
    s.insert(s.end(), w.begin(), w.end());
}
void Module::put(std::vector<uint32_t>& s, Opcode o, const std::vector<uint32_t>& w) {
    s.push_back(uint32_t(w.size() + 1) << 16 | o);
    s.insert(s.end(), w.begin(), w.end());
}
std::vector<uint32_t> Module::str(const char* s) {
    std::vector<uint32_t> w((std::strlen(s) + 4) / 4, 0);
    std::memcpy(w.data(), s, std::strlen(s));
    return w;
}

Id Module::typed(std::vector<uint32_t> key, Opcode o) {
    key.insert(key.begin(), o);
    auto it = type_cache_.find(key);
    if (it != type_cache_.end()) return it->second;
    const Id r = id();
    std::vector<uint32_t> w{r};
    w.insert(w.end(), key.begin() + 1, key.end());
    put(types_, o, w);
    type_cache_[key] = r;
    return r;
}

Id Module::t_void() { return typed({}, OpTypeVoid); }
Id Module::t_bool() { return typed({}, OpTypeBool); }
Id Module::t_u32() { return typed({32, 0}, OpTypeInt); }
Id Module::t_i32() { return typed({32, 1}, OpTypeInt); }
Id Module::t_f32() { return typed({32}, OpTypeFloat); }
Id Module::t_vec(Id comp, uint32_t n) { return typed({comp, n}, OpTypeVector); }
Id Module::t_ptr(StorageClass sc, Id type) { return typed({sc, type}, OpTypePointer); }
Id Module::t_func(Id ret, std::initializer_list<Id> params) {
    std::vector<uint32_t> k{ret};
    k.insert(k.end(), params.begin(), params.end());
    return typed(k, OpTypeFunction);
}
Id Module::t_array(Id elem, uint32_t n) { return typed({elem, c_u32(n)}, OpTypeArray); }
Id Module::t_runtime_array(Id elem) {
    const Id r = id();  // not de-duplicated: carries its own ArrayStride decoration
    put(types_, OpTypeRuntimeArray, {r, elem});
    return r;
}
Id Module::t_struct(std::initializer_list<Id> members) {
    const Id r = id();
    std::vector<uint32_t> w{r};
    w.insert(w.end(), members.begin(), members.end());
    put(types_, OpTypeStruct, w);
    return r;
}
Id Module::t_image(Id sampled, Dim dim, bool depth, bool arrayed, bool ms, uint32_t sampled_mode) {
    return typed({sampled, dim, depth ? 1u : 0u, arrayed ? 1u : 0u, ms ? 1u : 0u, sampled_mode, 0 /*Unknown*/},
                 OpTypeImage);
}
Id Module::t_sampler() { return typed({}, OpTypeSampler); }
Id Module::t_sampled_image(Id image) { return typed({image}, OpTypeSampledImage); }

Id Module::c_u32(uint32_t v) {
    const Id t = t_u32();
    std::vector<uint32_t> k{OpConstant, t, v};
    auto it = const_cache_.find(k);
    if (it != const_cache_.end()) return it->second;
    const Id r = id();
    put(types_, OpConstant, {t, r, v});
    return const_cache_[k] = r;
}
Id Module::c_i32(int32_t v) {
    const Id t = t_i32();
    std::vector<uint32_t> k{OpConstant, t, uint32_t(v)};
    auto it = const_cache_.find(k);
    if (it != const_cache_.end()) return it->second;
    const Id r = id();
    put(types_, OpConstant, {t, r, uint32_t(v)});
    return const_cache_[k] = r;
}
Id Module::c_f32(float v) {
    const Id t = t_f32();
    uint32_t bits;
    std::memcpy(&bits, &v, 4);
    std::vector<uint32_t> k{OpConstant, t, bits};
    auto it = const_cache_.find(k);
    if (it != const_cache_.end()) return it->second;
    const Id r = id();
    put(types_, OpConstant, {t, r, bits});
    return const_cache_[k] = r;
}
Id Module::c_bool(bool v) {
    const Id t = t_bool();
    std::vector<uint32_t> k{uint32_t(v ? OpConstantTrue : OpConstantFalse), t};
    auto it = const_cache_.find(k);
    if (it != const_cache_.end()) return it->second;
    const Id r = id();
    put(types_, v ? OpConstantTrue : OpConstantFalse, {t, r});
    return const_cache_[k] = r;
}
Id Module::c_composite(Id type, std::initializer_list<Id> parts) {
    std::vector<uint32_t> k{OpConstantComposite, type};
    k.insert(k.end(), parts.begin(), parts.end());
    auto it = const_cache_.find(k);
    if (it != const_cache_.end()) return it->second;
    const Id r = id();
    std::vector<uint32_t> w{type, r};
    w.insert(w.end(), parts.begin(), parts.end());
    put(types_, OpConstantComposite, w);
    return const_cache_[k] = r;
}
Id Module::c_null(Id type) {
    std::vector<uint32_t> k{OpConstantNull, type};
    auto it = const_cache_.find(k);
    if (it != const_cache_.end()) return it->second;
    const Id r = id();
    put(types_, OpConstantNull, {type, r});
    return const_cache_[k] = r;
}

void Module::capability(Capability c) {
    if (caps_seen_[c]) return;
    caps_seen_[c] = true;
    put(caps_, OpCapability, {c});
}
void Module::extension(const char* name) { put(exts_, OpExtension, str(name)); }
Id Module::glsl() {
    if (!glsl_) {
        glsl_ = id();
        std::vector<uint32_t> w{glsl_};
        auto s = str("GLSL.std.450");
        w.insert(w.end(), s.begin(), s.end());
        put(imports_, OpExtInstImport, w);
    }
    return glsl_;
}
Id Module::variable(Id ptr_type, StorageClass sc, Id init) {
    const Id r = id();
    if (init) put(types_, OpVariable, {ptr_type, r, sc, init});
    else put(types_, OpVariable, {ptr_type, r, sc});
    return r;
}
void Module::decorate(Id target, Decoration d, std::initializer_list<uint32_t> args) {
    std::vector<uint32_t> w{target, d};
    w.insert(w.end(), args.begin(), args.end());
    put(annot_, OpDecorate, w);
}
void Module::member_decorate(Id type, uint32_t member, Decoration d, std::initializer_list<uint32_t> args) {
    std::vector<uint32_t> w{type, member, d};
    w.insert(w.end(), args.begin(), args.end());
    put(annot_, OpMemberDecorate, w);
}
void Module::name(Id target, const std::string& n) {
    std::vector<uint32_t> w{target};
    auto s = str(n.c_str());
    w.insert(w.end(), s.begin(), s.end());
    put(debug_, OpName, w);
}
void Module::entry_point(ExecutionModel model, Id fn, const char* name, const std::vector<Id>& interface) {
    std::vector<uint32_t> w{model, fn};
    auto s = str(name);
    w.insert(w.end(), s.begin(), s.end());
    w.insert(w.end(), interface.begin(), interface.end());
    put(entry_, OpEntryPoint, w);
}
void Module::execution_mode(Id fn, ExecutionMode mode, std::initializer_list<uint32_t> args) {
    std::vector<uint32_t> w{fn, mode};
    w.insert(w.end(), args.begin(), args.end());
    put(modes_, OpExecutionMode, w);
}

Id Module::begin_function(Id ret_type, Id fn_type) {
    const Id f = id();
    put(body_, OpFunction, {ret_type, f, 0, fn_type});
    const Id entry = id();
    put(body_, OpLabel, {entry});
    fn_entry_pos_ = body_.size();
    fn_vars_.clear();
    return f;
}
Id Module::function_variable(Id ptr_type) {
    const Id r = id();
    put(fn_vars_, OpVariable, {ptr_type, r, SCFunction});
    return r;
}
void Module::end_function() {
    body_.insert(body_.begin() + long(fn_entry_pos_), fn_vars_.begin(), fn_vars_.end());
    fn_vars_.clear();
    put(body_, OpFunctionEnd, {});
}
Id Module::label() { return id(); }
void Module::place_label(Id l) { put(body_, OpLabel, {l}); }
void Module::op(Opcode o, std::initializer_list<uint32_t> words) { put(body_, o, words); }
void Module::op_v(Opcode o, const std::vector<uint32_t>& words) { put(body_, o, words); }
Id Module::op_r(Opcode o, Id type, std::initializer_list<uint32_t> operands) {
    const Id r = id();
    std::vector<uint32_t> w{type, r};
    w.insert(w.end(), operands.begin(), operands.end());
    put(body_, o, w);
    return r;
}
Id Module::op_rv(Opcode o, Id type, const std::vector<uint32_t>& operands) {
    const Id r = id();
    std::vector<uint32_t> w{type, r};
    w.insert(w.end(), operands.begin(), operands.end());
    put(body_, o, w);
    return r;
}
Id Module::ext(Id type, Glsl inst, std::initializer_list<Id> args) {
    const Id r = id();
    std::vector<uint32_t> w{type, r, glsl(), inst};
    w.insert(w.end(), args.begin(), args.end());
    put(body_, OpExtInst, w);
    return r;
}

std::vector<uint32_t> Module::binary() const {
    std::vector<uint32_t> out{0x07230203, 0x00010600 /*1.6*/, 0x44310000 /*generator: d1*/, next_, 0};
    std::vector<uint32_t> mm;
    put(mm, OpMemoryModel, {0 /*Logical*/, 1 /*GLSL450*/});
    for (const std::vector<uint32_t>* s : std::initializer_list<const std::vector<uint32_t>*>{&caps_, &exts_, &imports_, &mm, &entry_, &modes_, &debug_, &annot_, &types_, &body_})
        out.insert(out.end(), s->begin(), s->end());
    return out;
}

}  // namespace d1::spv
