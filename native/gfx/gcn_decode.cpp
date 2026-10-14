// GCN (gfx7) instruction decoder. See gcn.h.
#include <cctype>
#include <cstdio>
#include <cstring>

#include "gcn.h"

namespace d1::gcn {

const char* op_name(Op op) {
    static const char* names[] = {
        "UNKNOWN",
#define X(n) #n,
        D1_GCN_OPS(X)
#undef X
    };
    return names[size_t(op)];
}

uint32_t inline_constant(uint16_t c) {
    if (c == 128) return 0;
    if (c >= 129 && c <= 192) return c - 128;
    if (c >= 193 && c <= 208) return uint32_t(-int32_t(c - 192));
    switch (c) {
    case 240: return 0x3F000000;  // 0.5
    case 241: return 0xBF000000;  // -0.5
    case 242: return 0x3F800000;  // 1.0
    case 243: return 0xBF800000;  // -1.0
    case 244: return 0x40000000;  // 2.0
    case 245: return 0xC0000000;  // -2.0
    case 246: return 0x40800000;  // 4.0
    case 247: return 0xC0800000;  // -4.0
    }
    return 0;
}

namespace {

struct Entry { Enc enc; uint16_t num; Op op; };
// Sea Islands (gfx7) opcode numbers. VOP3 numbers are the 9-bit VOP3 space: VOPC 0x000-0x0FF,
// VOP2 0x100-0x13F, VOP3-only 0x140-0x17F, VOP1 0x180-0x1FF; VOP1/VOP2/VOPC entries are
// mirrored into it automatically.
const Entry kTable[] = {
    {Enc::SOP2, 0x00, Op::S_ADD_U32}, {Enc::SOP2, 0x02, Op::S_ADD_I32}, {Enc::SOP2, 0x03, Op::S_SUB_I32},
    {Enc::SOP2, 0x0E, Op::S_AND_B32}, {Enc::SOP2, 0x0F, Op::S_AND_B64}, {Enc::SOP2, 0x10, Op::S_OR_B32},
    {Enc::SOP2, 0x11, Op::S_OR_B64}, {Enc::SOP2, 0x13, Op::S_XOR_B64}, {Enc::SOP2, 0x15, Op::S_ANDN2_B64},
    {Enc::SOP2, 0x19, Op::S_NAND_B64}, {Enc::SOP2, 0x1E, Op::S_LSHL_B32}, {Enc::SOP2, 0x20, Op::S_LSHR_B32},
    {Enc::SOP2, 0x26, Op::S_MUL_I32},
    {Enc::SOPK, 0x00, Op::S_MOVK_I32}, {Enc::SOPK, 0x0F, Op::S_ADDK_I32},
    {Enc::SOP1, 0x03, Op::S_MOV_B32}, {Enc::SOP1, 0x04, Op::S_MOV_B64}, {Enc::SOP1, 0x0A, Op::S_WQM_B64},
    {Enc::SOP1, 0x20, Op::S_SETPC_B64}, {Enc::SOP1, 0x21, Op::S_SWAPPC_B64}, {Enc::SOP1, 0x24, Op::S_AND_SAVEEXEC_B64},
    {Enc::SOPC, 0x00, Op::S_CMP_EQ_I32}, {Enc::SOPC, 0x01, Op::S_CMP_LG_I32}, {Enc::SOPC, 0x02, Op::S_CMP_GT_I32},
    {Enc::SOPC, 0x03, Op::S_CMP_GE_I32}, {Enc::SOPC, 0x04, Op::S_CMP_LT_I32}, {Enc::SOPC, 0x05, Op::S_CMP_LE_I32},
    {Enc::SOPC, 0x06, Op::S_CMP_EQ_U32}, {Enc::SOPC, 0x07, Op::S_CMP_LG_U32}, {Enc::SOPC, 0x08, Op::S_CMP_GT_U32},
    {Enc::SOPC, 0x09, Op::S_CMP_GE_U32}, {Enc::SOPC, 0x0A, Op::S_CMP_LT_U32}, {Enc::SOPC, 0x0B, Op::S_CMP_LE_U32},
    {Enc::SOPP, 0x00, Op::S_NOP}, {Enc::SOPP, 0x01, Op::S_ENDPGM}, {Enc::SOPP, 0x02, Op::S_BRANCH},
    {Enc::SOPP, 0x04, Op::S_CBRANCH_SCC0}, {Enc::SOPP, 0x05, Op::S_CBRANCH_SCC1}, {Enc::SOPP, 0x06, Op::S_CBRANCH_VCCZ},
    {Enc::SOPP, 0x07, Op::S_CBRANCH_VCCNZ}, {Enc::SOPP, 0x08, Op::S_CBRANCH_EXECZ}, {Enc::SOPP, 0x09, Op::S_CBRANCH_EXECNZ},
    {Enc::SOPP, 0x0A, Op::S_BARRIER}, {Enc::SOPP, 0x0C, Op::S_WAITCNT}, {Enc::SOPP, 0x10, Op::S_SENDMSG},
    {Enc::SMRD, 0x00, Op::S_LOAD_DWORD}, {Enc::SMRD, 0x01, Op::S_LOAD_DWORDX2}, {Enc::SMRD, 0x02, Op::S_LOAD_DWORDX4},
    {Enc::SMRD, 0x03, Op::S_LOAD_DWORDX8}, {Enc::SMRD, 0x04, Op::S_LOAD_DWORDX16},
    {Enc::SMRD, 0x08, Op::S_BUFFER_LOAD_DWORD}, {Enc::SMRD, 0x09, Op::S_BUFFER_LOAD_DWORDX2},
    {Enc::SMRD, 0x0A, Op::S_BUFFER_LOAD_DWORDX4}, {Enc::SMRD, 0x0B, Op::S_BUFFER_LOAD_DWORDX8},
    {Enc::SMRD, 0x0C, Op::S_BUFFER_LOAD_DWORDX16},
    {Enc::VOP2, 0x00, Op::V_CNDMASK_B32}, {Enc::VOP2, 0x01, Op::V_READLANE_B32}, {Enc::VOP2, 0x02, Op::V_WRITELANE_B32},
    {Enc::VOP2, 0x03, Op::V_ADD_F32}, {Enc::VOP2, 0x04, Op::V_SUB_F32}, {Enc::VOP2, 0x05, Op::V_SUBREV_F32},
    {Enc::VOP2, 0x06, Op::V_MAC_LEGACY_F32}, {Enc::VOP2, 0x07, Op::V_MUL_LEGACY_F32}, {Enc::VOP2, 0x08, Op::V_MUL_F32},
    {Enc::VOP2, 0x09, Op::V_MUL_I32_I24}, {Enc::VOP2, 0x0D, Op::V_MIN_LEGACY_F32}, {Enc::VOP2, 0x0E, Op::V_MAX_LEGACY_F32},
    {Enc::VOP2, 0x0F, Op::V_MIN_F32}, {Enc::VOP2, 0x10, Op::V_MAX_F32}, {Enc::VOP2, 0x11, Op::V_MIN_I32},
    {Enc::VOP2, 0x12, Op::V_MAX_I32}, {Enc::VOP2, 0x16, Op::V_LSHRREV_B32}, {Enc::VOP2, 0x1A, Op::V_LSHLREV_B32},
    {Enc::VOP2, 0x1B, Op::V_AND_B32}, {Enc::VOP2, 0x1C, Op::V_OR_B32}, {Enc::VOP2, 0x1D, Op::V_XOR_B32},
    {Enc::VOP2, 0x1F, Op::V_MAC_F32}, {Enc::VOP2, 0x20, Op::V_MADMK_F32}, {Enc::VOP2, 0x21, Op::V_MADAK_F32},
    {Enc::VOP2, 0x25, Op::V_ADD_I32}, {Enc::VOP2, 0x26, Op::V_SUB_I32}, {Enc::VOP2, 0x2E, Op::V_CVT_PKNORM_U16_F32},
    {Enc::VOP2, 0x2F, Op::V_CVT_PKRTZ_F16_F32},
    {Enc::VOP1, 0x01, Op::V_MOV_B32}, {Enc::VOP1, 0x02, Op::V_READFIRSTLANE_B32}, {Enc::VOP1, 0x05, Op::V_CVT_F32_I32},
    {Enc::VOP1, 0x06, Op::V_CVT_F32_U32}, {Enc::VOP1, 0x07, Op::V_CVT_U32_F32}, {Enc::VOP1, 0x08, Op::V_CVT_I32_F32},
    {Enc::VOP1, 0x20, Op::V_FRACT_F32}, {Enc::VOP1, 0x21, Op::V_TRUNC_F32}, {Enc::VOP1, 0x22, Op::V_CEIL_F32},
    {Enc::VOP1, 0x23, Op::V_RNDNE_F32}, {Enc::VOP1, 0x24, Op::V_FLOOR_F32}, {Enc::VOP1, 0x25, Op::V_EXP_F32},
    {Enc::VOP1, 0x27, Op::V_LOG_F32}, {Enc::VOP1, 0x2A, Op::V_RCP_F32}, {Enc::VOP1, 0x2C, Op::V_RSQ_CLAMP_F32},
    {Enc::VOP1, 0x2E, Op::V_RSQ_F32}, {Enc::VOP1, 0x33, Op::V_SQRT_F32}, {Enc::VOP1, 0x35, Op::V_SIN_F32},
    {Enc::VOP1, 0x36, Op::V_COS_F32}, {Enc::VOP1, 0x37, Op::V_NOT_B32}, {Enc::VOP1, 0x43, Op::V_MOVRELS_B32},
    {Enc::VOPC, 0x00, Op::V_CMP_F_F32}, {Enc::VOPC, 0x01, Op::V_CMP_LT_F32}, {Enc::VOPC, 0x02, Op::V_CMP_EQ_F32},
    {Enc::VOPC, 0x03, Op::V_CMP_LE_F32}, {Enc::VOPC, 0x04, Op::V_CMP_GT_F32}, {Enc::VOPC, 0x05, Op::V_CMP_LG_F32},
    {Enc::VOPC, 0x06, Op::V_CMP_GE_F32}, {Enc::VOPC, 0x07, Op::V_CMP_O_F32}, {Enc::VOPC, 0x08, Op::V_CMP_U_F32},
    {Enc::VOPC, 0x09, Op::V_CMP_NGE_F32}, {Enc::VOPC, 0x0A, Op::V_CMP_NLG_F32}, {Enc::VOPC, 0x0B, Op::V_CMP_NGT_F32},
    {Enc::VOPC, 0x0C, Op::V_CMP_NLE_F32}, {Enc::VOPC, 0x0D, Op::V_CMP_NEQ_F32}, {Enc::VOPC, 0x0E, Op::V_CMP_NLT_F32},
    {Enc::VOPC, 0x0F, Op::V_CMP_TRU_F32},
    {Enc::VOPC, 0x81, Op::V_CMP_LT_I32}, {Enc::VOPC, 0x82, Op::V_CMP_EQ_I32}, {Enc::VOPC, 0x83, Op::V_CMP_LE_I32},
    {Enc::VOPC, 0x84, Op::V_CMP_GT_I32}, {Enc::VOPC, 0x85, Op::V_CMP_NE_I32}, {Enc::VOPC, 0x86, Op::V_CMP_GE_I32},
    {Enc::VOPC, 0x88, Op::V_CMP_CLASS_F32}, {Enc::VOPC, 0x92, Op::V_CMPX_EQ_I32},
    {Enc::VOPC, 0xC1, Op::V_CMP_LT_U32}, {Enc::VOPC, 0xC2, Op::V_CMP_EQ_U32}, {Enc::VOPC, 0xC3, Op::V_CMP_LE_U32},
    {Enc::VOPC, 0xC4, Op::V_CMP_GT_U32}, {Enc::VOPC, 0xC5, Op::V_CMP_NE_U32}, {Enc::VOPC, 0xC6, Op::V_CMP_GE_U32},
    {Enc::VOPC, 0xD1, Op::V_CMPX_LT_U32},
    {Enc::VOP3, 0x140, Op::V_MAD_LEGACY_F32}, {Enc::VOP3, 0x141, Op::V_MAD_F32}, {Enc::VOP3, 0x142, Op::V_MAD_I32_I24},
    {Enc::VOP3, 0x143, Op::V_MAD_U32_U24}, {Enc::VOP3, 0x144, Op::V_CUBEID_F32}, {Enc::VOP3, 0x145, Op::V_CUBESC_F32},
    {Enc::VOP3, 0x146, Op::V_CUBETC_F32}, {Enc::VOP3, 0x147, Op::V_CUBEMA_F32}, {Enc::VOP3, 0x148, Op::V_BFE_U32},
    {Enc::VOP3, 0x14B, Op::V_FMA_F32}, {Enc::VOP3, 0x151, Op::V_MIN3_F32}, {Enc::VOP3, 0x154, Op::V_MAX3_F32},
    {Enc::VOP3, 0x157, Op::V_MED3_F32}, {Enc::VOP3, 0x161, Op::V_LSHL_B64}, {Enc::VOP3, 0x169, Op::V_MUL_LO_U32},
    {Enc::VOP3, 0x16A, Op::V_MUL_HI_U32}, {Enc::VOP3, 0x16B, Op::V_MUL_LO_I32},
    {Enc::VINTRP, 0, Op::V_INTERP_P1_F32}, {Enc::VINTRP, 1, Op::V_INTERP_P2_F32}, {Enc::VINTRP, 2, Op::V_INTERP_MOV_F32},
    {Enc::DS, 0x0D, Op::DS_WRITE_B32}, {Enc::DS, 0x0E, Op::DS_WRITE2_B32}, {Enc::DS, 0x35, Op::DS_SWIZZLE_B32},
    {Enc::DS, 0x36, Op::DS_READ_B32}, {Enc::DS, 0x37, Op::DS_READ2_B32},
    {Enc::MUBUF, 0x00, Op::BUFFER_LOAD_FORMAT_X}, {Enc::MUBUF, 0x01, Op::BUFFER_LOAD_FORMAT_XY},
    {Enc::MUBUF, 0x02, Op::BUFFER_LOAD_FORMAT_XYZ}, {Enc::MUBUF, 0x03, Op::BUFFER_LOAD_FORMAT_XYZW},
    {Enc::MUBUF, 0x0C, Op::BUFFER_LOAD_DWORD}, {Enc::MUBUF, 0x1C, Op::BUFFER_STORE_DWORD},
    {Enc::MTBUF, 0x00, Op::TBUFFER_LOAD_FORMAT_X}, {Enc::MTBUF, 0x01, Op::TBUFFER_LOAD_FORMAT_XY},
    {Enc::MTBUF, 0x02, Op::TBUFFER_LOAD_FORMAT_XYZ}, {Enc::MTBUF, 0x03, Op::TBUFFER_LOAD_FORMAT_XYZW},
    {Enc::MIMG, 0x00, Op::IMAGE_LOAD}, {Enc::MIMG, 0x01, Op::IMAGE_LOAD_MIP}, {Enc::MIMG, 0x0E, Op::IMAGE_GET_RESINFO},
    {Enc::MIMG, 0x20, Op::IMAGE_SAMPLE}, {Enc::MIMG, 0x22, Op::IMAGE_SAMPLE_D}, {Enc::MIMG, 0x24, Op::IMAGE_SAMPLE_L},
    {Enc::MIMG, 0x25, Op::IMAGE_SAMPLE_B}, {Enc::MIMG, 0x27, Op::IMAGE_SAMPLE_LZ}, {Enc::MIMG, 0x28, Op::IMAGE_SAMPLE_C},
    {Enc::MIMG, 0x2F, Op::IMAGE_SAMPLE_C_LZ}, {Enc::MIMG, 0x37, Op::IMAGE_SAMPLE_LZ_O},
    {Enc::MIMG, 0x47, Op::IMAGE_GATHER4_LZ}, {Enc::MIMG, 0x57, Op::IMAGE_GATHER4_LZ_O}, {Enc::MIMG, 0x60, Op::IMAGE_GET_LOD},
    {Enc::EXP, 0, Op::EXP},
};

struct Tables {
    Op t[16][512] = {};
    Tables() {
        for (const Entry& e : kTable) {
            t[size_t(e.enc)][e.num] = e.op;
            if (e.enc == Enc::VOPC) t[size_t(Enc::VOP3)][e.num] = e.op;
            if (e.enc == Enc::VOP2) t[size_t(Enc::VOP3)][0x100 + e.num] = e.op;
            if (e.enc == Enc::VOP1) t[size_t(Enc::VOP3)][0x180 + e.num] = e.op;
        }
    }
};
const Tables& tables() {
    static const Tables t;
    return t;
}

const char* enc_name(Enc e) {
    static const char* n[] = {"SOP2", "SOPK", "SOP1", "SOPC", "SOPP", "SMRD", "VOP2", "VOP1",
                              "VOPC", "VOP3", "VINTRP", "DS", "MUBUF", "MTBUF", "MIMG", "EXP"};
    return n[size_t(e)];
}

Operand opnd(uint32_t code) {
    Operand o;
    o.code = uint16_t(code);
    return o;
}

}  // namespace

Program decode(const uint8_t* code, uint32_t max_bytes) {
    Program p;
    uint32_t i = 0;
    auto word = [&](uint32_t at, uint32_t& out) {
        if (at + 4 > max_bytes) return false;
        std::memcpy(&out, code + at, 4);
        return true;
    };
    const auto& T = tables();
    while (i < max_bytes) {
        uint32_t w;
        if (!word(i, w)) break;
        Inst in;
        in.pc = i;
        uint32_t w1 = 0;
        bool need_w1 = false, may_literal = false;
        const uint32_t top9 = w >> 23;
        if (top9 == 0x17D) {
            in.enc = Enc::SOP1, in.opnum = (w >> 8) & 0xFF;
            in.dst = opnd((w >> 16) & 0x7F), in.src[0] = opnd(w & 0xFF), in.num_src = 1;
            may_literal = true;
        } else if (top9 == 0x17E) {
            in.enc = Enc::SOPC, in.opnum = (w >> 16) & 0x7F;
            in.src[0] = opnd(w & 0xFF), in.src[1] = opnd((w >> 8) & 0xFF), in.num_src = 2;
            may_literal = true;
        } else if (top9 == 0x17F) {
            in.enc = Enc::SOPP, in.opnum = (w >> 16) & 0x7F, in.simm16 = int16_t(w & 0xFFFF);
        } else if ((w >> 28) == 0xB) {
            in.enc = Enc::SOPK, in.opnum = (w >> 23) & 0x1F;
            in.dst = opnd((w >> 16) & 0x7F), in.simm16 = int16_t(w & 0xFFFF);
        } else if ((w >> 30) == 0x2) {
            in.enc = Enc::SOP2, in.opnum = (w >> 23) & 0x7F;
            in.dst = opnd((w >> 16) & 0x7F), in.src[0] = opnd(w & 0xFF), in.src[1] = opnd((w >> 8) & 0xFF);
            in.num_src = 2, may_literal = true;
        } else if ((w >> 27) == 0x18) {
            in.enc = Enc::SMRD, in.opnum = (w >> 22) & 0x1F;
            in.dst = opnd((w >> 15) & 0x7F), in.sbase = uint8_t(((w >> 9) & 0x3F) * 2);
            in.smrd_imm = (w >> 8) & 1, in.smrd_offset = w & 0xFF;
            if (!in.smrd_imm && in.smrd_offset == 255) {  // literal offset
                need_w1 = true;
            }
        } else if ((w >> 25) == 0x3F) {
            in.enc = Enc::VOP1, in.opnum = (w >> 9) & 0xFF;
            in.dst = opnd(256 + ((w >> 17) & 0xFF)), in.src[0] = opnd(w & 0x1FF), in.num_src = 1;
            may_literal = true;
        } else if ((w >> 25) == 0x3E) {
            in.enc = Enc::VOPC, in.opnum = (w >> 17) & 0xFF;
            in.dst = opnd(106);  // VCC
            in.src[0] = opnd(w & 0x1FF), in.src[1] = opnd(256 + ((w >> 9) & 0xFF)), in.num_src = 2;
            may_literal = true;
        } else if ((w >> 31) == 0) {
            in.enc = Enc::VOP2, in.opnum = (w >> 25) & 0x3F;
            in.dst = opnd(256 + ((w >> 17) & 0xFF)), in.src[0] = opnd(w & 0x1FF);
            in.src[1] = opnd(256 + ((w >> 9) & 0xFF)), in.num_src = 2;
            may_literal = true;
        } else {
            switch (w >> 26) {
            case 0x34: {  // VOP3
                in.enc = Enc::VOP3, in.opnum = (w >> 17) & 0x1FF, need_w1 = true;
                break;
            }
            case 0x32:
                in.enc = Enc::VINTRP, in.opnum = (w >> 16) & 3;
                in.dst = opnd(256 + ((w >> 18) & 0xFF)), in.src[0] = opnd(256 + (w & 0xFF)), in.num_src = 1;
                in.attr = (w >> 10) & 0x3F, in.chan = (w >> 8) & 3;
                break;
            case 0x36:
                in.enc = Enc::DS, in.opnum = (w >> 18) & 0xFF, need_w1 = true;
                in.ds_offset0 = w & 0xFF, in.ds_offset1 = (w >> 8) & 0xFF;
                break;
            case 0x38:
                in.enc = Enc::MUBUF, in.opnum = (w >> 18) & 0x7F, need_w1 = true;
                in.mem_offset = w & 0xFFF, in.offen = (w >> 12) & 1, in.idxen = (w >> 13) & 1;
                in.glc = (w >> 14) & 1, in.addr64 = (w >> 15) & 1, in.lds = (w >> 16) & 1;
                break;
            case 0x3A:
                in.enc = Enc::MTBUF, in.opnum = (w >> 16) & 7, need_w1 = true;
                in.mem_offset = w & 0xFFF, in.offen = (w >> 12) & 1, in.idxen = (w >> 13) & 1;
                in.glc = (w >> 14) & 1, in.addr64 = (w >> 15) & 1;
                in.dfmt = (w >> 19) & 0xF, in.nfmt = (w >> 23) & 7;
                break;
            case 0x3C:
                in.enc = Enc::MIMG, in.opnum = (w >> 18) & 0x7F, need_w1 = true;
                in.dmask = (w >> 8) & 0xF, in.unorm = (w >> 12) & 1, in.glc = (w >> 13) & 1;
                in.da = (w >> 14) & 1, in.r128 = (w >> 15) & 1, in.tfe = (w >> 16) & 1, in.lwe = (w >> 17) & 1;
                in.slc = (w >> 25) & 1;
                break;
            case 0x3E:
                in.enc = Enc::EXP, in.opnum = 0, need_w1 = true;
                in.exp_en = w & 0xF, in.exp_target = (w >> 4) & 0x3F, in.exp_compr = (w >> 10) & 1;
                in.exp_done = (w >> 11) & 1, in.exp_vm = (w >> 12) & 1;
                break;
            default: {
                char b[96];
                std::snprintf(b, sizeof b, "unknown encoding %08x at %#x", w, i);
                p.problems.push_back(b);
                return p;
            }
            }
        }
        if (need_w1) {
            if (!word(i + 4, w1)) {
                p.problems.push_back("truncated instruction");
                return p;
            }
            in.size = 8;
            switch (in.enc) {
            case Enc::SMRD:
                in.smrd_offset = w1;
                break;
            case Enc::VOP3: {
                // VOP3b: v_add/sub/subrev/addc/subb/subbrev_i32 carry out, v_div_scale
                const bool vop3b = (in.opnum >= 0x125 && in.opnum <= 0x12A) || in.opnum == 0x16D || in.opnum == 0x16E;
                const bool cmp = in.opnum < 0x100;
                in.dst = cmp ? opnd(w & 0xFF) : opnd(256 + (w & 0xFF));
                if (vop3b) in.sdst = opnd((w >> 8) & 0x7F);
                else {
                    in.src[0].abs = (w >> 8) & 1, in.src[1].abs = (w >> 9) & 1, in.src[2].abs = (w >> 10) & 1;
                    in.clamp = (w >> 11) & 1;
                }
                in.src[0].code = uint16_t(w1 & 0x1FF), in.src[1].code = uint16_t((w1 >> 9) & 0x1FF);
                in.src[2].code = uint16_t((w1 >> 18) & 0x1FF);
                in.omod = (w1 >> 27) & 3;
                in.src[0].neg = (w1 >> 29) & 1, in.src[1].neg = (w1 >> 30) & 1, in.src[2].neg = (w1 >> 31) & 1;
                in.num_src = 3;
                break;
            }
            case Enc::DS:
                in.src[0] = opnd(256 + (w1 & 0xFF));           // address
                in.src[1] = opnd(256 + ((w1 >> 8) & 0xFF));    // data0
                in.src[2] = opnd(256 + ((w1 >> 16) & 0xFF));   // data1
                in.dst = opnd(256 + ((w1 >> 24) & 0xFF));
                in.num_src = 3;
                break;
            case Enc::MUBUF:
            case Enc::MTBUF:
                in.vaddr = w1 & 0xFF, in.vdata = (w1 >> 8) & 0xFF, in.srsrc = uint8_t(((w1 >> 16) & 0x1F) * 4);
                in.slc = (w1 >> 22) & 1, in.tfe = (w1 >> 23) & 1, in.soffset = opnd((w1 >> 24) & 0xFF);
                break;
            case Enc::MIMG:
                in.vaddr = w1 & 0xFF, in.vdata = (w1 >> 8) & 0xFF, in.srsrc = uint8_t(((w1 >> 16) & 0x1F) * 4);
                in.ssamp = uint8_t(((w1 >> 21) & 0x1F) * 4);
                break;
            case Enc::EXP:
                for (int k = 0; k < 4; ++k) in.exp_src[k] = uint8_t(w1 >> (8 * k));
                break;
            default:
                break;
            }
        }
        // literal constant (32-bit word after the instruction)
        bool lit = false;
        if (may_literal)
            for (int k = 0; k < in.num_src; ++k)
                if (in.src[k].code == 255) lit = true;
        in.op = T.t[size_t(in.enc)][in.opnum];
        if (in.op == Op::V_MADMK_F32 || in.op == Op::V_MADAK_F32) lit = true;
        if (lit) {
            if (!word(i + in.size, in.literal)) {
                p.problems.push_back("truncated literal");
                return p;
            }
            in.size += 4;
        }
        if (in.op == Op::Unknown) {
            char b[96];
            std::snprintf(b, sizeof b, "unknown %s opcode %#x at %#x", enc_name(in.enc), in.opnum, i);
            p.problems.push_back(b);
        }
        p.insts.push_back(in);
        i += in.size;
        if (in.op == Op::S_ENDPGM || in.op == Op::S_SETPC_B64) {
            p.ended = true;
            break;
        }
    }
    return p;
}

namespace {
std::string operand_str(const Operand& o, uint32_t literal) {
    char b[48];
    const uint16_t c = o.code;
    if (c < 104) std::snprintf(b, sizeof b, "s%u", c);
    else if (c == 106) std::snprintf(b, sizeof b, "vcc_lo");
    else if (c == 107) std::snprintf(b, sizeof b, "vcc_hi");
    else if (c == 124) std::snprintf(b, sizeof b, "m0");
    else if (c == 126) std::snprintf(b, sizeof b, "exec_lo");
    else if (c == 127) std::snprintf(b, sizeof b, "exec_hi");
    else if (c >= 128 && c <= 208) std::snprintf(b, sizeof b, "%d", int32_t(inline_constant(c)));
    else if (c >= 240 && c <= 247) {
        const uint32_t v = inline_constant(c);
        float f;
        std::memcpy(&f, &v, 4);
        std::snprintf(b, sizeof b, "%g", f);
    } else if (c == 251) std::snprintf(b, sizeof b, "vccz");
    else if (c == 252) std::snprintf(b, sizeof b, "execz");
    else if (c == 253) std::snprintf(b, sizeof b, "scc");
    else if (c == 255) std::snprintf(b, sizeof b, "0x%x", literal);
    else if (c >= 256) std::snprintf(b, sizeof b, "v%u", c - 256);
    else std::snprintf(b, sizeof b, "?%u", c);
    std::string s = b;
    if (o.abs) s = "|" + s + "|";
    if (o.neg) s = "-" + s;
    return s;
}
}  // namespace

std::string disassemble(const Inst& in) {
    char b[256];
    std::string s = op_name(in.op);
    if (in.op == Op::Unknown) {
        std::snprintf(b, sizeof b, "%s_%#x", enc_name(in.enc), in.opnum);
        s = b;
    }
    for (auto& c : s) c = char(std::tolower(c));
    switch (in.enc) {
    case Enc::SOPP:
        std::snprintf(b, sizeof b, " %d", in.simm16);
        return s + b;
    case Enc::SOPK:
        std::snprintf(b, sizeof b, " s%u, %d", in.dst.code, in.simm16);
        return s + b;
    case Enc::SMRD:
        std::snprintf(b, sizeof b, " s%u, s[%u:%u], %s0x%x", in.dst.code, in.sbase, in.sbase + 1, in.smrd_imm ? "" : "s",
                      in.smrd_offset);
        return s + b;
    case Enc::VINTRP:
        std::snprintf(b, sizeof b, " v%u, v%u, attr%u.%c", in.dst.code - 256, in.src[0].code - 256, in.attr, "xyzw"[in.chan]);
        return s + b;
    case Enc::MUBUF:
    case Enc::MTBUF:
        std::snprintf(b, sizeof b, " v%u, v%u, s[%u:%u], %s offset:%u%s%s fmt:%u/%u", in.vdata, in.vaddr, in.srsrc,
                      in.srsrc + 3, operand_str(in.soffset, 0).c_str(), in.mem_offset, in.idxen ? " idxen" : "",
                      in.offen ? " offen" : "", in.dfmt, in.nfmt);
        return s + b;
    case Enc::MIMG:
        std::snprintf(b, sizeof b, " v%u, v%u, s[%u:%u], s[%u:%u] dmask:%x%s", in.vdata, in.vaddr, in.srsrc,
                      in.srsrc + 7, in.ssamp, in.ssamp + 3, in.dmask, in.da ? " da" : "");
        return s + b;
    case Enc::EXP:
        std::snprintf(b, sizeof b, " tgt%u en:%x v%u v%u v%u v%u%s%s%s", in.exp_target, in.exp_en, in.exp_src[0],
                      in.exp_src[1], in.exp_src[2], in.exp_src[3], in.exp_compr ? " compr" : "",
                      in.exp_done ? " done" : "", in.exp_vm ? " vm" : "");
        return s + b;
    case Enc::DS:
        std::snprintf(b, sizeof b, " v%u, v%u, v%u, v%u off:%u,%u", in.dst.code - 256, in.src[0].code - 256,
                      in.src[1].code - 256, in.src[2].code - 256, in.ds_offset0, in.ds_offset1);
        return s + b;
    default:
        break;
    }
    s += " " + operand_str(in.dst, 0);
    if (in.sdst.code) s += ", " + operand_str(in.sdst, 0);
    for (int k = 0; k < in.num_src; ++k) s += ", " + operand_str(in.src[k], in.literal);
    if (in.op == Op::V_MADMK_F32 || in.op == Op::V_MADAK_F32) {
        std::snprintf(b, sizeof b, ", k=0x%x", in.literal);
        s += b;
    }
    if (in.clamp) s += " clamp";
    if (in.omod) s += " omod";
    return s;
}

}  // namespace d1::gcn
