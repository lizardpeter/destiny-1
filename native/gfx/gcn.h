// GCN (gfx7, PS4 "Liverpool") shader instructions: decoding.
//
// Part of d1-native's own shader translator (no third-party shader code). Encodings and
// opcode numbers follow AMD's Sea Islands ISA. Only what Destiny 1's shaders use is named
// (129 distinct opcodes across its ~13,700 shaders, plus fetch shaders); anything else
// decodes as Op::Unknown with its encoding and number kept, so a shader that needs it can
// be reported instead of silently mistranslated.
#pragma once
#include <cstdint>
#include <string>
#include <vector>

namespace d1::gcn {

enum class Enc : uint8_t { SOP2, SOPK, SOP1, SOPC, SOPP, SMRD, VOP2, VOP1, VOPC, VOP3, VINTRP, DS, MUBUF, MTBUF, MIMG, EXP };

#define D1_GCN_OPS(X) \
    /* scalar */ \
    X(S_MOV_B32) X(S_MOV_B64) X(S_MOVK_I32) X(S_ADDK_I32) X(S_AND_B32) X(S_AND_B64) X(S_OR_B64) \
    X(S_XOR_B64) X(S_ANDN2_B64) X(S_NAND_B64) X(S_LSHL_B32) X(S_WQM_B64) X(S_AND_SAVEEXEC_B64) \
    X(S_SWAPPC_B64) X(S_SETPC_B64) X(S_ADD_U32) X(S_ADD_I32) X(S_SUB_I32) X(S_MUL_I32) X(S_LSHR_B32) X(S_OR_B32) \
    X(S_CMP_EQ_U32) X(S_CMP_LG_U32) X(S_CMP_EQ_I32) X(S_CMP_LG_I32) X(S_CMP_GT_I32) X(S_CMP_LT_I32) \
    X(S_CMP_GE_I32) X(S_CMP_LE_I32) X(S_CMP_GT_U32) X(S_CMP_LT_U32) X(S_CMP_GE_U32) X(S_CMP_LE_U32) \
    X(S_NOP) X(S_ENDPGM) X(S_BRANCH) X(S_CBRANCH_SCC0) X(S_CBRANCH_SCC1) X(S_CBRANCH_VCCZ) \
    X(S_CBRANCH_VCCNZ) X(S_CBRANCH_EXECZ) X(S_CBRANCH_EXECNZ) X(S_BARRIER) X(S_WAITCNT) \
    X(S_SENDMSG) X(S_LOAD_DWORD) X(S_LOAD_DWORDX2) X(S_LOAD_DWORDX4) X(S_LOAD_DWORDX8) \
    X(S_LOAD_DWORDX16) X(S_BUFFER_LOAD_DWORD) X(S_BUFFER_LOAD_DWORDX2) X(S_BUFFER_LOAD_DWORDX4) \
    X(S_BUFFER_LOAD_DWORDX8) X(S_BUFFER_LOAD_DWORDX16) \
    /* vector ALU */ \
    X(V_CNDMASK_B32) X(V_READLANE_B32) X(V_WRITELANE_B32) X(V_ADD_F32) X(V_SUB_F32) X(V_SUBREV_F32) \
    X(V_MAC_LEGACY_F32) X(V_MUL_LEGACY_F32) X(V_MUL_F32) X(V_MUL_I32_I24) X(V_MIN_F32) X(V_MAX_F32) \
    X(V_MAX_I32) X(V_LSHRREV_B32) X(V_LSHLREV_B32) X(V_AND_B32) X(V_OR_B32) X(V_MAC_F32) X(V_MADMK_F32) \
    X(V_MADAK_F32) X(V_ADD_I32) X(V_SUB_I32) X(V_CVT_PKNORM_U16_F32) X(V_CVT_PKRTZ_F16_F32) \
    X(V_MIN_I32) X(V_XOR_B32) X(V_MAX_LEGACY_F32) X(V_MIN_LEGACY_F32) \
    X(V_MOV_B32) X(V_READFIRSTLANE_B32) X(V_CVT_F32_I32) X(V_CVT_F32_U32) X(V_CVT_U32_F32) \
    X(V_CVT_I32_F32) X(V_FRACT_F32) X(V_TRUNC_F32) X(V_CEIL_F32) X(V_RNDNE_F32) X(V_FLOOR_F32) \
    X(V_EXP_F32) X(V_LOG_F32) X(V_RCP_F32) X(V_RSQ_CLAMP_F32) X(V_RSQ_F32) X(V_SQRT_F32) X(V_SIN_F32) \
    X(V_COS_F32) X(V_MOVRELS_B32) X(V_NOT_B32) \
    X(V_MAD_LEGACY_F32) X(V_MAD_F32) X(V_MAD_I32_I24) X(V_MAD_U32_U24) X(V_CUBEID_F32) X(V_CUBESC_F32) \
    X(V_CUBETC_F32) X(V_CUBEMA_F32) X(V_BFE_U32) X(V_MIN3_F32) X(V_LSHL_B64) X(V_MUL_LO_U32) \
    X(V_MUL_HI_U32) X(V_MUL_LO_I32) X(V_MAX3_F32) X(V_MED3_F32) X(V_FMA_F32) \
    /* compares: VOPC (or VOP3 with an SGPR pair destination) */ \
    X(V_CMP_F_F32) X(V_CMP_LT_F32) X(V_CMP_EQ_F32) X(V_CMP_LE_F32) X(V_CMP_GT_F32) X(V_CMP_LG_F32) \
    X(V_CMP_GE_F32) X(V_CMP_O_F32) X(V_CMP_U_F32) X(V_CMP_NGE_F32) X(V_CMP_NLG_F32) X(V_CMP_NGT_F32) \
    X(V_CMP_NLE_F32) X(V_CMP_NEQ_F32) X(V_CMP_NLT_F32) X(V_CMP_TRU_F32) \
    X(V_CMP_LT_I32) X(V_CMP_EQ_I32) X(V_CMP_LE_I32) X(V_CMP_GT_I32) X(V_CMP_NE_I32) X(V_CMP_GE_I32) \
    X(V_CMP_LT_U32) X(V_CMP_EQ_U32) X(V_CMP_LE_U32) X(V_CMP_GT_U32) X(V_CMP_NE_U32) X(V_CMP_GE_U32) \
    X(V_CMPX_EQ_I32) X(V_CMPX_LT_U32) X(V_CMP_CLASS_F32) \
    /* interpolation, LDS, memory, export */ \
    X(V_INTERP_P1_F32) X(V_INTERP_P2_F32) X(V_INTERP_MOV_F32) \
    X(DS_WRITE_B32) X(DS_WRITE2_B32) X(DS_SWIZZLE_B32) X(DS_READ_B32) X(DS_READ2_B32) \
    X(BUFFER_LOAD_DWORD) X(BUFFER_LOAD_FORMAT_X) X(BUFFER_LOAD_FORMAT_XY) X(BUFFER_LOAD_FORMAT_XYZ) \
    X(BUFFER_LOAD_FORMAT_XYZW) X(BUFFER_STORE_DWORD) \
    X(TBUFFER_LOAD_FORMAT_X) X(TBUFFER_LOAD_FORMAT_XY) X(TBUFFER_LOAD_FORMAT_XYZ) X(TBUFFER_LOAD_FORMAT_XYZW) \
    X(IMAGE_LOAD) X(IMAGE_LOAD_MIP) X(IMAGE_GET_RESINFO) X(IMAGE_SAMPLE) X(IMAGE_SAMPLE_D) X(IMAGE_SAMPLE_L) \
    X(IMAGE_SAMPLE_B) X(IMAGE_SAMPLE_LZ) X(IMAGE_SAMPLE_C) X(IMAGE_SAMPLE_C_LZ) X(IMAGE_SAMPLE_LZ_O) \
    X(IMAGE_GATHER4_LZ) X(IMAGE_GATHER4_LZ_O) X(IMAGE_GET_LOD) \
    X(EXP)

enum class Op : uint16_t {
    Unknown,
#define X(n) n,
    D1_GCN_OPS(X)
#undef X
    Count
};
const char* op_name(Op op);

// A source/destination operand in the hardware's 9-bit operand space.
struct Operand {
    uint16_t code = 0;  // 0..103 SGPR, 106/107 VCC lo/hi, 124 M0, 126/127 EXEC lo/hi, 128..208 inline
                        // integers, 240..247 inline floats, 251 VCCZ, 252 EXECZ, 253 SCC,
                        // 255 literal, 256..511 VGPR
    bool neg = false, abs = false;
    bool is_sgpr() const { return code < 104; }
    bool is_vgpr() const { return code >= 256; }
    bool is_literal() const { return code == 255; }
    bool is_inline_const() const { return (code >= 128 && code <= 208) || (code >= 240 && code <= 247); }
    int vgpr() const { return code - 256; }
};
uint32_t inline_constant(uint16_t code);  // bit pattern of an inline constant

struct Inst {
    Op op = Op::Unknown;
    Enc enc{};
    uint16_t opnum = 0;    // raw opcode within its encoding (VOP3: 9-bit)
    uint32_t pc = 0;       // byte offset in the program
    uint8_t size = 4;      // bytes, including a literal
    Operand dst, sdst;     // sdst: VOP3b scalar destination (compares, carries)
    Operand src[3];
    uint32_t literal = 0;
    uint8_t num_src = 0;
    // VOP3 modifiers
    bool clamp = false;
    uint8_t omod = 0;
    // SOPP / SOPK
    int16_t simm16 = 0;
    // SMRD
    uint8_t sbase = 0;     // first SGPR of the base pair
    bool smrd_imm = false; // offset is an immediate (dwords) rather than an SGPR
    uint32_t smrd_offset = 0;
    // VINTRP
    uint8_t attr = 0, chan = 0;
    // DS
    uint8_t ds_offset0 = 0, ds_offset1 = 0;
    // MUBUF / MTBUF / MIMG
    uint16_t mem_offset = 0;
    bool offen = false, idxen = false, glc = false, slc = false, addr64 = false, lds = false, tfe = false;
    uint8_t dfmt = 0, nfmt = 0;
    uint8_t vaddr = 0, vdata = 0, srsrc = 0, ssamp = 0;  // srsrc/ssamp: first SGPR (already x4)
    Operand soffset;
    uint8_t dmask = 0;
    bool unorm = false, da = false, r128 = false, lwe = false;
    // EXP
    uint8_t exp_en = 0, exp_target = 0;
    bool exp_compr = false, exp_done = false, exp_vm = false;
    uint8_t exp_src[4] = {};
};

struct Program {
    std::vector<Inst> insts;
    std::vector<std::string> problems;  // unknown encodings or opcodes, truncation
    bool ended = false;                 // reached S_ENDPGM / S_SETPC_B64
};

// Decode a program until S_ENDPGM (or S_SETPC_B64 for fetch shaders) or `max_bytes`.
Program decode(const uint8_t* code, uint32_t max_bytes);
std::string disassemble(const Inst& in);

}  // namespace d1::gcn
