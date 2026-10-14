// Minimal SPIR-V module builder (d1-native's own; no third-party SPIR-V libraries).
//
// Enough of SPIR-V 1.6 for translated GCN shaders: scalar/vector types, images and samplers,
// interface variables, structured control flow and GLSL.std.450 extended instructions.
// Types and constants are de-duplicated. Instructions are written straight into word
// streams per module section and assembled by binary().
#pragma once
#include <cstdint>
#include <initializer_list>
#include <map>
#include <string>
#include <vector>

namespace d1::spv {

using Id = uint32_t;

// Opcodes (SPIR-V specification, section 3.52).
enum Opcode : uint16_t {
    OpNop = 0, OpName = 5, OpMemberName = 6, OpExtension = 10, OpExtInstImport = 11, OpExtInst = 12,
    OpMemoryModel = 14, OpEntryPoint = 15, OpExecutionMode = 16, OpCapability = 17,
    OpTypeVoid = 19, OpTypeBool = 20, OpTypeInt = 21, OpTypeFloat = 22, OpTypeVector = 23, OpTypeImage = 25,
    OpTypeSampler = 26, OpTypeSampledImage = 27, OpTypeArray = 28, OpTypeRuntimeArray = 29, OpTypeStruct = 30,
    OpTypePointer = 32, OpTypeFunction = 33,
    OpConstantTrue = 41, OpConstantFalse = 42, OpConstant = 43, OpConstantComposite = 44, OpConstantNull = 46,
    OpFunction = 54, OpFunctionParameter = 55, OpFunctionEnd = 56, OpFunctionCall = 57, OpVariable = 59,
    OpLoad = 61, OpStore = 62, OpAccessChain = 65, OpDecorate = 71, OpMemberDecorate = 72,
    OpVectorShuffle = 79, OpCompositeConstruct = 80, OpCompositeExtract = 81, OpCompositeInsert = 82,
    OpSampledImage = 86, OpImageSampleImplicitLod = 87, OpImageSampleExplicitLod = 88,
    OpImageSampleDrefImplicitLod = 89, OpImageSampleDrefExplicitLod = 90, OpImageFetch = 95, OpImageGather = 96,
    OpImage = 100, OpImageQuerySizeLod = 103, OpImageQueryLod = 105, OpImageQueryLevels = 106,
    OpConvertFToU = 109, OpConvertFToS = 110, OpConvertSToF = 111, OpConvertUToF = 112, OpBitcast = 124,
    OpSNegate = 126, OpFNegate = 127, OpIAdd = 128, OpFAdd = 129, OpISub = 130, OpFSub = 131, OpIMul = 132,
    OpFMul = 133, OpUDiv = 134, OpFDiv = 136, OpUMod = 137, OpUMulExtended = 151,
    OpIsNan = 156, OpIsInf = 157, OpLogicalEqual = 164, OpLogicalNotEqual = 165, OpLogicalOr = 166,
    OpLogicalAnd = 167, OpLogicalNot = 168, OpSelect = 169, OpIEqual = 170, OpINotEqual = 171,
    OpUGreaterThan = 172, OpSGreaterThan = 173, OpUGreaterThanEqual = 174, OpSGreaterThanEqual = 175,
    OpULessThan = 176, OpSLessThan = 177, OpULessThanEqual = 178, OpSLessThanEqual = 179,
    OpFOrdEqual = 180, OpFUnordEqual = 181, OpFOrdNotEqual = 182, OpFUnordNotEqual = 183, OpFOrdLessThan = 184,
    OpFUnordLessThan = 185, OpFOrdGreaterThan = 186, OpFUnordGreaterThan = 187, OpFOrdLessThanEqual = 188,
    OpFUnordLessThanEqual = 189, OpFOrdGreaterThanEqual = 190, OpFUnordGreaterThanEqual = 191,
    OpShiftRightLogical = 194, OpShiftRightArithmetic = 195, OpShiftLeftLogical = 196, OpBitwiseOr = 197,
    OpBitwiseXor = 198, OpBitwiseAnd = 199, OpNot = 200, OpBitFieldSExtract = 202, OpBitFieldUExtract = 203,
    OpDPdx = 207, OpDPdy = 208, OpLoopMerge = 246, OpSelectionMerge = 247, OpLabel = 248, OpBranch = 249,
    OpBranchConditional = 250, OpSwitch = 251, OpKill = 252, OpReturn = 253, OpUnreachable = 255,
    OpGroupNonUniformShuffle = 345, OpDemoteToHelperInvocation = 5380,
};

// GLSL.std.450 extended instructions.
enum Glsl : uint32_t {
    GlslRoundEven = 2, GlslTrunc = 3, GlslFAbs = 4, GlslFloor = 8, GlslCeil = 9, GlslFract = 10, GlslSin = 13,
    GlslCos = 14, GlslExp2 = 29, GlslLog2 = 30, GlslSqrt = 31, GlslInverseSqrt = 32, GlslFMin = 37, GlslUMin = 38,
    GlslSMin = 39, GlslFMax = 40, GlslUMax = 41, GlslSMax = 42, GlslFClamp = 43, GlslFma = 50,
    GlslPackUnorm2x16 = 57, GlslPackHalf2x16 = 58, GlslNMin = 79, GlslNMax = 80, GlslNClamp = 81,
};

enum StorageClass : uint32_t {
    SCUniformConstant = 0, SCInput = 1, SCUniform = 2, SCOutput = 3, SCWorkgroup = 4, SCPrivate = 6,
    SCFunction = 7, SCPushConstant = 9, SCStorageBuffer = 12,
};
enum Decoration : uint32_t {
    DecBlock = 2, DecArrayStride = 6, DecBuiltIn = 11, DecFlat = 14, DecNoPerspective = 13, DecNonWritable = 24,
    DecLocation = 30, DecComponent = 31, DecIndex = 32, DecBinding = 33, DecDescriptorSet = 34, DecOffset = 35,
};
enum BuiltIn : uint32_t {
    BuiltInPosition = 0, BuiltInPointSize = 1, BuiltInFragCoord = 15, BuiltInFrontFacing = 17,
    BuiltInFragDepth = 22, BuiltInVertexIndex = 42, BuiltInInstanceIndex = 43, BuiltInSampleId = 18,
};
enum ExecutionModel : uint32_t { ExecVertex = 0, ExecFragment = 4, ExecGLCompute = 5 };
enum ExecutionMode : uint32_t { ModeOriginUpperLeft = 7, ModeDepthReplacing = 12, ModeLocalSize = 17 };
enum Capability : uint32_t {
    CapShader = 1, CapImageGatherExtended = 25, CapImageQuery = 50, CapDerivativeControl = 51, CapGroupNonUniform = 61,
    CapGroupNonUniformShuffle = 66, CapDemoteToHelperInvocation = 5379,
};
enum Dim : uint32_t { Dim1D = 0, Dim2D = 1, Dim3D = 2, DimCube = 3, DimBuffer = 5 };

class Module {
public:
    Module();
    Id id() { return next_++; }

    // ---- types (de-duplicated)
    Id t_void();
    Id t_bool();
    Id t_u32();
    Id t_i32();
    Id t_f32();
    Id t_vec(Id comp, uint32_t n);
    Id t_ptr(StorageClass sc, Id type);
    Id t_func(Id ret, std::initializer_list<Id> params = {});
    Id t_array(Id elem, uint32_t n);
    Id t_runtime_array(Id elem);
    Id t_struct(std::initializer_list<Id> members);  // not de-duplicated (decorations differ)
    Id t_image(Id sampled, Dim dim, bool depth, bool arrayed, bool ms, uint32_t sampled_mode);
    Id t_sampler();
    Id t_sampled_image(Id image);

    // ---- constants (de-duplicated)
    Id c_u32(uint32_t v);
    Id c_i32(int32_t v);
    Id c_f32(float v);
    Id c_bool(bool v);
    Id c_composite(Id type, std::initializer_list<Id> parts);
    Id c_null(Id type);

    // ---- module-level
    void capability(Capability c);
    void extension(const char* name);
    Id glsl();  // GLSL.std.450 import
    Id variable(Id ptr_type, StorageClass sc, Id init = 0);  // global
    void decorate(Id target, Decoration d, std::initializer_list<uint32_t> args = {});
    void member_decorate(Id type, uint32_t member, Decoration d, std::initializer_list<uint32_t> args = {});
    void name(Id target, const std::string& n);
    void entry_point(ExecutionModel model, Id fn, const char* name, const std::vector<Id>& interface);
    void execution_mode(Id fn, ExecutionMode mode, std::initializer_list<uint32_t> args = {});

    // ---- functions: instructions go to the current function body
    Id begin_function(Id ret_type, Id fn_type);
    Id function_variable(Id ptr_type);  // goes into the entry block's variable list
    void end_function();
    Id label();                                   // new block label id (not yet emitted)
    void place_label(Id l);                       // start a block
    void op(Opcode o, std::initializer_list<uint32_t> words);  // no result
    void op_v(Opcode o, const std::vector<uint32_t>& words);   // no result, variable length
    Id op_r(Opcode o, Id type, std::initializer_list<uint32_t> operands);  // with result type and id
    Id op_rv(Opcode o, Id type, const std::vector<uint32_t>& operands);
    Id ext(Id type, Glsl inst, std::initializer_list<Id> args);

    std::vector<uint32_t> binary() const;

private:
    static void put(std::vector<uint32_t>& s, Opcode o, std::initializer_list<uint32_t> w);
    static void put(std::vector<uint32_t>& s, Opcode o, const std::vector<uint32_t>& w);
    static std::vector<uint32_t> str(const char* s);
    Id typed(std::vector<uint32_t> key, Opcode o);

    Id next_ = 1;
    Id glsl_ = 0;
    std::vector<uint32_t> caps_, exts_, imports_, entry_, modes_, debug_, annot_, types_, body_, fn_vars_;
    std::map<std::vector<uint32_t>, Id> type_cache_, const_cache_;
    std::map<uint32_t, bool> caps_seen_;
    size_t fn_entry_pos_ = 0;  // where the entry block's variables are inserted into body_
};

}  // namespace d1::spv
