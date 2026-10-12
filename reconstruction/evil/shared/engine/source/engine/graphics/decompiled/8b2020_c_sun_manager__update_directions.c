/* c_sun_manager::update_directions @ 0x8b2020  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Reads the sun tag (handle this+0x2c) or override vectors; writes sun_light_direction, sun_atmosphere_direction, channel 0x7C61F53B, and sun_ambient_direction = scale(channel 0x38D8C873) * -light_dir.xy.
 */
typedef struct st_8b2020_1 {
    char padding_0[12];
    unsigned int field_c;
} st_8b2020_1;

typedef struct st_8b2020_2 {
    struct st_8b2020_3 *field_0;
} st_8b2020_2;

typedef struct st_8b2020_3 {
    struct st_8b2020_2 *field_0;
} st_8b2020_3;

typedef struct st_8b2020_0 {
    unsigned long long field_0;
} st_8b2020_0;

extern st_8b2020_0 *g_1a1f100;
extern st_8b2020_3 *g_1a238a0;

float sub_8b2020(void* idx, st_8b2020_3 **a1)
{
    st_8b2020_3 **idx1;  // r12
    unsigned int v56;  // eax
    unsigned long v65;  // r15
    unsigned long long v66;  // r15
    int v67;  // eax
    unsigned int v68;  // eax
    unsigned long long v69;  // rcx
    unsigned long v70;  // rax
    unsigned long long v71;  // rdx
    unsigned long long v72;  // rcx
    unsigned long v73;  // rax
    unsigned long long v74;  // rdx
    unsigned long long v57;  // rcx
    int v75;  // eax
    int v76;  // ecx
    unsigned long long v77;  // rax
    unsigned long v78;  // rcx
    unsigned long long v79;  // rdx
    unsigned long long v80;  // rdi
    unsigned long long v81;  // rcx
    unsigned long v82;  // rax
    float v83;  // xmm0
    st_8b2020_3 **v58;  // rbx
    unsigned long v59;  // rsi
    unsigned long v60;  // r13
    unsigned long v61;  // rax
    unsigned long long v62;  // rdx
    st_8b2020_1 *index;  // r13
    char v64;  // al
    float v0;  // [bp-0x298]
    float v1;  // [bp-0x290]
    float v2;  // [bp-0x280]
    float v3;  // [bp-0x278]
    float v4;  // [bp-0x268]
    float v5;  // [bp-0x260]
    float v6;  // [bp-0x250]
    float v7;  // [bp-0x248]
    float v8;  // [bp-0x238]
    float v9;  // [bp-0x230]
    float v10;  // [bp-0x220]
    float v11;  // [bp-0x218]
    float v12;  // [bp-0x208]
    float v13;  // [bp-0x200]
    float v14;  // [bp-0x1f0]
    float v15;  // [bp-0x1e8]
    float v16;  // [bp-0x1d8]
    float v17;  // [bp-0x1d0]
    float v18;  // [bp-0x1c0]
    float v19;  // [bp-0x1b8]
    float v20;  // [bp-0x1a8]
    float v21;  // [bp-0x1a0]
    float v22;  // [bp-0x190]
    float v23;  // [bp-0x188]
    float v24;  // [bp-0x178]
    float v25;  // [bp-0x170]
    float v26;  // [bp-0x160]
    float v27;  // [bp-0x158]
    float v28;  // [bp-0x148]
    float v29;  // [bp-0x140]
    float v30;  // [bp-0x130]
    float v31;  // [bp-0x128]
    float v32;  // [bp-0x120]
    unsigned long v33;  // [bp-0x118]
    st_8b2020_3 **v34;  // [bp-0x110]
    st_8b2020_3 **v35;  // [bp-0x108]
    void* v36;  // [bp-0x100]
    unsigned long long v37;  // [bp-0xf8]
    char *v38;  // [bp-0xf0]
    unsigned int v39;  // [bp-0xdc]
    __m128 v40;  // [bp-0xd8]
    char v41;  // [bp-0xc8]
    float v42;  // [bp-0xc8]
    char v43;  // [bp-0xb8]
    float v44;  // [bp-0xb8]
    float v45;  // [bp-0xa8]
    uint128_t v46;  // [bp-0x98]
    float v47;  // [bp-0x88]
    uint128_t v48;  // [bp-0x78]
    float v49;  // [bp-0x68]
    float v50;  // [bp-0x58]
    float v51;  // [bp-0x48]
    unsigned long v52;  // [bp-0x38]
    char v53;  // [bp-0x8]

    idx1 = a1;
    v52 = *(long long *)g_1a1f100;
    v51 = (float)0;
    v50 = (float)0;
    v49 = (float)0;
    if ((char)idx[49])
    {
        v51 = (float)(int128_t)idx[64];
        v50 = (float)(int128_t)idx[80];
        v49 = (float)(int128_t)idx[64];
    }
    else
    {
        v56 = (int)idx[44];
        if (v56 != 0xffffffff)
        {
            v57 = (((int)(v56) >> 13 >> 18 | 0x3ff) & (int)(v56) >> 13) * 64;
            v58 = &g_1a238a0;
            v39 = *(int *)((char *)&idx1[12591] + 4);
            v59 = *(long long *)g_1a238a0;
            v60 = *(long long *)(v59 + v57 + 16);
            v61 = *(int *)(v59 + v57 + 48) * (v56 & 0x1fff);
            v62 = *(int *)(v59 + v57 + 52) & *(long long *)(v60 + v61 + 8);
            *(int *)&idx[52] = *(int *)((char *)&idx1[12591] + 4);
            index = v60 + v61 - v62;
            v64 = sub_8b3280(index, v59, v62, v57);
            v66 = _INSERT(v65, 0, v64);
            *((char *)&idx1[12580] + 4) = v64;
            v67 = *(int *)&index->padding_0[8];
            if (v67 == 0xffffffff)
            {
                v68 = index->field_c;
                if (v68 == 0xffffffff)
                    goto LABEL_8b21ea;
            }
            else
            {
                v69 = (((unsigned int)(v67 >> 13) >> 18 | 0x3ff) & v67 >> 13) * 64;
                v58 = *(long long *)g_1a238a0;
                v70 = *(int *)((char *)v58 + v69 + 48) * (v67 & 0x1fff);
                v71 = *(int *)((char *)v58 + v69 + 52) & *(long long *)(*(long long *)((char *)v58 + v69 + 16) + v70 + 8);
                sub_1c5e60(*(long long *)((char *)v58 + v69 + 16) + v70 - v71, &v49, v71, v69);
                *(char *)&idx[50] = 1;
                v68 = index->field_c;
            }
            if (!(v68 == 0xffffffff || v64 ^ 1))
            {
                v72 = (((int)(v68) >> 13 >> 18 | 0x3ff) & (int)(v68) >> 13) * 64;
                v58 = *(long long *)g_1a238a0;
                v73 = *(int *)((char *)v58 + v72 + 48) * (v68 & 0x1fff);
                v74 = *(int *)((char *)v58 + v72 + 52) & *(long long *)(*(long long *)((char *)v58 + v72 + 16) + v73 + 8);
                sub_1c5e60(*(long long *)((char *)v58 + v72 + 16) + v73 - v74, &v51, v74, v72);
                *(char *)&idx[50] = 1;
            }
            else if (*(int *)&index->padding_0[8] != 0xffffffff)
            {
                memcpy(&v51, &v49, 16);
            }
            idx1 = &g_1a238a0;
LABEL_8b21ea:
            memcpy(&v50, &v51, 16);
            v75 = *(int *)&index[1].padding_0[0];
            v76 = *(int *)&index[1].padding_0[4];
            if (v75 != 0xffffffff || v76 != 0xffffffff)
            {
                if (v76 == 0xffffffff || !(v66 ^= 1, !(v64 ^ 1)))
                {
                    if (v75 == -0x1)
                        goto LABEL_8b22aa;
                    v81 = (((unsigned int)(v75 >> 13) >> 18 | 0x3ff) & v75 >> 13) * 64;
                    v58 = *(long long *)g_1a238a0;
                    v82 = *(int *)((char *)v58 + v81 + 48) * (v75 & 0x1fff);
                    v79 = *(int *)((char *)v58 + v81 + 52) & *(long long *)(*(long long *)((char *)v58 + v81 + 16) + v82 + 8);
                    v80 = *(long long *)((char *)v58 + v81 + 16) + v82;
                }
                else
                {
                    v77 = (((unsigned int)(v76 >> 13) >> 18 | 0x3ff) & v76 >> 13) * 64;
                    v58 = *(long long *)g_1a238a0;
                    v78 = *(int *)((char *)v58 + v77 + 48) * (v76 & 0x1fff);
                    v79 = *(int *)((char *)v58 + v77 + 52) & *(long long *)(*(long long *)((char *)v58 + v77 + 16) + v78 + 8);
                    v80 = *(long long *)((char *)v58 + v77 + 16) + v78;
                }
                sub_1c5e60(v80 - v79);
            }
        }
    }
LABEL_8b22aa:
    v48 = 0xffffffffffffffff & v51;
    v47 = (float)0;
    sub_99f80(&v48, &v47);
    v51 = (float)0;
    v46 = 0xffffffffffffffff & v50;
    v45 = (float)0;
    sub_99f80(&v46, &v45);
    v50 = (float)0;
    sub_816170((int)idx[8], &v51);
    sub_816170((int)idx[12], &v50);
    sub_816170((int)idx[20], &v49);
    if (!(char)sub_816100((int)idx[24], &v43))
        v44 = (float)0;
    if ((char)sub_816100((int)idx[8], &v41))
    {
        v83 = (float)_mm_add_ps(v41, _mm_castsi128_ps(_mm_set_epi32(0, 0, 0x80000000, 0x80000000)));
    }
    else
    {
        v42 = (float)0;
        v83 = (float)0;
    }
    v40 = _mm_add_ps(_mm_mul_ps(CONCAT(CONCAT((int)v44, (int)v44), CONCAT((int)v44, (int)v44)), v83), _mm_setzero_ps());
    sub_816170((int)idx[16], &v40);
    if (*(long long *)g_1a1f100 == v52)
        return (int)v44 * v83 + 0.0f;
    sub_12aa7f0();
    v38 = &v53;
    v37 = v66;
    v36 = idx;
    v35 = idx1;
    v34 = v58;
    v33 = *(long long *)g_1a1f100;
    v1 = (float)0;
    v0 = (float)0;
    v3 = (float)0;
    v2 = (float)0;
    v5 = (float)0;
    v4 = (float)0;
    v7 = (float)0;
    v6 = (float)0;
    v9 = (float)0;
    v8 = (float)0;
    v11 = (float)0;
    v10 = (float)0;
    v13 = (float)0;
    v12 = (float)0;
    v15 = (float)0;
    v14 = (float)0;
    v17 = (float)0;
    v16 = (float)0;
    v19 = (float)0;
    v18 = (float)0;
    v21 = (float)0;
    v20 = (float)0;
    v23 = (float)0;
    v22 = (float)0;
    v25 = (float)0;
    v24 = (float)0;
    v27 = (float)0;
    v26 = (float)0;
    v29 = (float)0;
    v28 = (float)0;
    v32 = (float)0;
    v31 = (float)0;
    v30 = (float)0;
}
