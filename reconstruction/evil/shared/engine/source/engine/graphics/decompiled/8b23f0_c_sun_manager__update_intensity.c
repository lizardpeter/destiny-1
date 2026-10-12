/* c_sun_manager::update_intensity @ 0x8b23f0  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Scales sun_intensity by (1 - max fade) over volumes of kind 2 at renderer+0x18988; sets renderer+0x18925 when kind-13 volumes reach full weight.
 */
typedef struct st_8b23f0_3 {
    char padding_0[32];
    unsigned int field_20;
} st_8b23f0_3;

typedef struct st_8b23f0_1 {
    char padding_0[120];
    float field_78;
} st_8b23f0_1;

typedef struct st_8b23f0_0 {
    unsigned long long field_0;
} st_8b23f0_0;

extern st_8b23f0_0 *g_1a1f100;

float sub_8b23f0(st_8b23f0_3 *a0, unsigned long long a1)
{
    unsigned long long v43;  // r15
    st_8b23f0_1 **v44;  // rbx
    float v53;  // zmm3
    unsigned long long v54;  // 4203
    unsigned long long v55;  // 4209
    st_8b23f0_3 *v56;  // rdi
    float v45;  // zmm4
    unsigned long long v46;  // rax
    unsigned long long v47;  // rax
    float v48;  // zmm2
    st_8b23f0_1 **v49;  // rbx
    float v50;  // zmm1
    unsigned long long v51;  // rax
    unsigned long long v52;  // rax
    char v0;  // [bp-0x210]
    unsigned long v1;  // [bp-0x200]
    st_8b23f0_1 **v2;  // [bp-0x1f8]
    unsigned long long v3;  // [bp-0x1f0]
    unsigned long long v4;  // [bp-0x1e8]
    char *v5;  // [bp-0x1e0]
    float v6;  // [bp-0x1cc]
    uint128_t v7;  // [bp-0x1c8]
    void* v8;  // [bp-0x1b8]
    float v9;  // [bp-0x198]
    float v10;  // [bp-0x190]
    float v11;  // [bp-0x180]
    float v12;  // [bp-0x178]
    float v13;  // [bp-0x168]
    float v14;  // [bp-0x160]
    float v15;  // [bp-0x150]
    float v16;  // [bp-0x148]
    float v17;  // [bp-0x138]
    float v18;  // [bp-0x130]
    float v19;  // [bp-0x120]
    float v20;  // [bp-0x118]
    float v21;  // [bp-0x108]
    float v22;  // [bp-0x100]
    float v23;  // [bp-0xf0]
    float v24;  // [bp-0xe8]
    float v25;  // [bp-0xd8]
    float v26;  // [bp-0xd0]
    float v27;  // [bp-0xc0]
    float v28;  // [bp-0xb8]
    float v29;  // [bp-0xa8]
    float v30;  // [bp-0xa0]
    float v31;  // [bp-0x90]
    float v32;  // [bp-0x88]
    float v33;  // [bp-0x78]
    float v34;  // [bp-0x70]
    float v35;  // [bp-0x60]
    float v36;  // [bp-0x58]
    float v37;  // [bp-0x48]
    float v38;  // [bp-0x40]
    float v39;  // [bp-0x38]
    unsigned long v40;  // [bp-0x30]
    char v41;  // [bp-0x8]

    v40 = *(long long *)g_1a1f100;
    (&v8)[2] = 0;
    (&v8)[1] = 0;
    v10 = (float)0;
    v9 = (float)0;
    v12 = (float)0;
    v11 = (float)0;
    v43 = a1 + 100744;
    v44 = &v8;
    v14 = (float)0;
    v13 = (float)0;
    v16 = (float)0;
    v15 = (float)0;
    v18 = (float)0;
    v17 = (float)0;
    v20 = (float)0;
    v19 = (float)0;
    v22 = (float)0;
    v21 = (float)0;
    v24 = (float)0;
    v23 = (float)0;
    v26 = (float)0;
    v25 = (float)0;
    v28 = (float)0;
    v27 = (float)0;
    v30 = (float)0;
    v29 = (float)0;
    v32 = (float)0;
    v31 = (float)0;
    v34 = (float)0;
    v33 = (float)0;
    v36 = (float)0;
    v35 = (float)0;
    v39 = (float)0;
    v38 = (float)0;
    v37 = (float)0;
    sub_7ccc20(v43, 2, &v8);
    v45 = 0;
    if (v39)
    {
        v46 = v39 * 24;
        v45 = 0;
        do
        {
            v47 = v46;
            v48 = *v44->field_78;
            if (v45 - *v44->field_78 < 0.0f)
                v45 = v48;
        } while ((v44 += 24, v46 = v47 - 24, v47 != 24));
    }
    if (v45 < 0.0f)
        v45 = 0;
    if (v45 + -1.0f >= 0.0f)
        v45 = 1.0;
    v6 = v45;
    if (v45 > 0.0f)
    {
        sub_816100(a0->field_20, &v7);
        v7 = _mm_mul_ps(CONCAT(CONCAT(__float_as_int(1.0f - v6), __float_as_int(1.0f - v6)), CONCAT(__float_as_int(1.0f - v6), __float_as_int(1.0f - v6))), v7);
        sub_816170(a0->field_20, &v7);
    }
    (&v8)[2] = 0;
    (&v8)[1] = 0;
    v10 = (float)0;
    v9 = (float)0;
    v12 = (float)0;
    v11 = (float)0;
    v14 = (float)0;
    v13 = (float)0;
    v16 = (float)0;
    v15 = (float)0;
    v18 = (float)0;
    v17 = (float)0;
    v49 = &v8;
    v20 = (float)0;
    v19 = (float)0;
    v22 = (float)0;
    v21 = (float)0;
    v24 = (float)0;
    v23 = (float)0;
    v26 = (float)0;
    v25 = (float)0;
    v28 = (float)0;
    v27 = (float)0;
    v30 = (float)0;
    v29 = (float)0;
    v32 = (float)0;
    v31 = (float)0;
    v34 = (float)0;
    v33 = (float)0;
    v36 = (float)0;
    v35 = (float)0;
    v39 = (float)0;
    v38 = (float)0;
    v37 = (float)0;
    sub_7ccc20(v43, 13, &v8);
    v50 = 0;
    if (v39)
    {
        v51 = v39 * 24;
        v50 = 0;
        do
        {
            v52 = v51;
            v53 = *v49->field_78;
            if (v50 - *v49->field_78 < 0.0f)
                v50 = v53;
        } while ((v49 += 24, v51 = v52 - 24, v52 != 24));
    }
    if (v50 < 0.0f)
        v50 = 0;
    v54 = _ccall(0, CmpF(__double_as_longlong((double)v50), 1.0) & 69, 0, 0);
    v55 = _ccall(0, CmpF(__double_as_longlong((double)(v50 + -1.0f)), 0) & 69, 0, 0);
    *(char *)(a1 + 100645) = -((char)v55 & 1) & -((char)v54 & 1) & 1 ^ 1;
    if (*(long long *)g_1a1f100 == v40)
        return 0;
    sub_12aa7f0();
    v5 = &v41;
    v4 = v43;
    v3 = a1;
    v2 = v49;
    v1 = *(long long *)g_1a1f100;
    sub_816100(v56->field_20, &v0);
}
