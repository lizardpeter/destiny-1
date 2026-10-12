/* auto_exposure_history_shift @ 0x844170  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Frame-delayed history: G+0x10<-G+0xC, G+0x14<-G+0x10, int ring G+0/4/8; uses 1/a1[55]*0.0625.
 */

typedef struct st_844170_0 {
    unsigned int field_0;
    unsigned int field_4;
    unsigned int field_8;
    unsigned int field_c;
    unsigned int field_10;
    unsigned int field_14;
} st_844170_0;

typedef struct st_844170_1 {
    unsigned long long field_0;
} st_844170_1;

extern st_844170_1 *g_1a1f100;
extern int g_2709d70;

float sub_844170(st_844170_0 *idx, unsigned int *a1, unsigned int a2, long long a3)
{
    float v19;  // zmm1
    float v20;  // ecx
    long long v29;  // rax
    unsigned long v30;  // rdi
    unsigned int v31;  // zmm0
    unsigned long long v32;  // rax
    unsigned long long v33;  // rcx
    float v21;  // zmm0
    unsigned short *v22;  // rax
    uint128_t v23;  // xmm0
    unsigned int v24;  // zmm3
    uint128_t v25;  // xmm4
    uint128_t v27;  // xmm4
    uint128_t v28;  // xmm1
    uint128_t v0;  // [bp-0x170]
    float v1;  // [bp-0x170]
    uint128_t v2;  // [bp-0x160]
    uint128_t v3;  // [bp-0x150]
    float v4;  // [bp-0x140]
    unsigned long v5;  // [bp-0x140]
    float v6;  // [bp-0x120]
    uint128_t v7;  // [bp-0x110]
    float v8;  // [bp-0x100]
    float v9;  // [bp-0xe0]
    uint128_t v10;  // [bp-0xd0]
    float v11;  // [bp-0xc0]
    float v12;  // [bp-0xa0]
    float v13;  // [bp-0x80]
    float v14;  // [bp-0x60]
    float v15;  // [bp-0x40]
    float v16;  // [bp-0x38]
    unsigned long v17;  // [bp-0x30]

    v17 = *(long long *)g_1a1f100;
    idx->field_0 = g_2709d70 + 2;
    v19 = 0;
    if (2 <= g_2709d70)
        v20 = 0;
    else
        v20 = __int_as_float(g_2709d70 + 1);
    *(float *)&g_2709d70 = v20;
    v21 = *(float *)&a1[55];
    if (v21 != 0.0f)
        v19 = 1.0f / v21 * 0.0625f;
    v1 = v19;
    v3 = a1[111];
    v2 = a1[112];
    v14 = (float)0;
    v13 = (float)0;
    v12 = (float)0;
    v11 = (float)0;
    v9 = (float)0;
    v8 = (float)0;
    v6 = (float)0;
    v4 = (float)0;
    v16 = (float)0;
    v15 = (float)0;
    v5 = sub_818d90(a2);
    v0 = CONCAT((unsigned long long)(0 >> 64), CONCAT((unsigned int)(0 >> 32), *(unsigned int *)&v1));
    v3 = CONCAT(CONCAT((unsigned int)((unsigned long long)v2 >> 32), (unsigned int)((unsigned long long)v3 >> 32)), CONCAT((unsigned int)v2, (unsigned int)v3));
    v22 = sub_818dd0(a2);
    v23 = CONCAT(*(unsigned long long *)&*(unsigned long long *)(void*)&v0, *(unsigned long long *)&*(unsigned long long *)(void*)&v3);
    v24 = v22[1];
    v25 = _INSERT(0, 0, *v22);
    v27 = _INSERT(_INSERT(v25, 4, *(unsigned int *)((void*)&v23 + 4)), 8, *(unsigned long long *)((void*)&v23 + 8));
    v28 = CONCAT(CONCAT((unsigned int)(CONCAT((unsigned long long)(v27 >> 64), CONCAT(v24, (unsigned int)v27)) >> 96), 1.0f / (unsigned int)v27), CONCAT(v24, (unsigned int)v27));
    v7 = CONCAT(CONCAT(__float_as_int(1.0f / __int_as_float(v24)), (unsigned int)(v28 >> 64)), (unsigned long long)v28);
    v10 = v23;
    v29 = sub_82cc20(227);
    sub_898440(a3, v29, idx->field_0, 0, &v5);
    v30 = idx->field_0;
    sub_818a90(v30, v30 & 0xffffffff, 0, 0, 0);
    idx->field_8 = idx->field_4;
    idx->field_14 = idx->field_10;
    idx->field_4 = idx->field_0;
    v31 = idx->field_c;
    idx->field_10 = v31;
    if (*(long long *)g_1a1f100 == v17)
        return v31;
    v32 = sub_12aa7f0();
    do
    {
        *(unsigned int *)(v32 + v33 * 4 + 32) = v31;
        v33 += 1;
    } while ((unsigned int)v33 != 60);
    return v31;
}
