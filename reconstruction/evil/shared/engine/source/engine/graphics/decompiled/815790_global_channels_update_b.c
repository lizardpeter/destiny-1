/* global_channels_update_b @ 0x815790  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Per-frame global channel update, second pass; honours override bit flags g_26f1fcc[4].
 */
typedef struct st_815790_5 {
    struct st_815790_6 *field_0;
    struct st_815790_3 *field_8;
    struct st_815790_4 *field_10;
} st_815790_5;

typedef struct st_815790_4 {
    char padding_0[8];
    unsigned int field_8;
    char padding_c[4];
    long long field_10;
    char field_18;
} st_815790_4;

typedef struct st_815790_6 {
    unsigned int field_0;
} st_815790_6;

typedef struct st_815790_3 {
    char padding_0[8];
    char field_8;
    char padding_9[7];
    unsigned long long field_10;
    char padding_18[16];
    unsigned long long field_28;
} st_815790_3;

typedef struct st_815790_2 {
    char padding_0[104];
    unsigned int field_68;
} st_815790_2;

typedef struct st_815790_0 {
    unsigned long long field_0;
} st_815790_0;

extern unsigned int g_815f30[4];
extern st_815790_0 *g_1a1f100;
extern st_815790_0 *g_1a238a0;
extern unsigned long long g_26f1fc0;
extern unsigned int g_26f1fcc[4];
extern int g_26f1ff0;

float sub_815790(unsigned long a0)
{
    int v53;  // edx
    unsigned long long v54;  // rcx
    char v63;  // rsi
    char *v64;  // rdx
    char v65;  // r9
    char v66;  // r8d
    unsigned long long v67;  // rax
    unsigned int v68;  // r12d
    unsigned long v69;  // r11
    unsigned long node;  // r13
    unsigned int v71;  // r12d
    unsigned long long v72;  // rax
    unsigned long v55;  // rsi
    unsigned long long index;  // r15
    unsigned int v74;  // ebx
    unsigned long v75;  // rax
    char v76;  // r14
    unsigned long long v77;  // rdx
    unsigned long v78;  // rbx
    unsigned long v79;  // rdi
    char v80;  // r13
    long long v81;  // r14d
    st_815790_5 *iter;  // r15
    char v56;  // xmm0
    st_815790_3 *v83;  // rdi
    st_815790_4 *v84;  // rax
    char v85;  // r12d
    char v86;  // rdx
    float v87;  // zmm0
    unsigned int v88;  // edx
    float v89;  // zmm2
    char v90;  // xmm4
    uint128_t *v91;  // rbx
    char v92;  // zmm0
    st_815790_2 **v57;  // rbx
    __m128 v93;  // xmm1
    char v94;  // xmm2
    unsigned long v58;  // rax
    char v59;  // xmm1
    unsigned long long v60;  // rax
    char idx;  // rcx
    unsigned long long v62;  // rax
    unsigned int v0;  // [bp-0xa68]
    char *v1;  // [bp-0x938]
    unsigned long v2;  // [bp-0x930]
    unsigned long v3;  // [bp-0x928]
    char v4;  // [bp-0x91c]
    char v5;  // [bp-0x91c]
    char v6;  // [bp-0x918]
    char v7;  // [bp-0x908]
    char v8;  // [bp-0x8f8]
    char v9;  // [bp-0x8e8]
    char v10;  // [bp-0x8d8]
    uint128_t v11;  // [bp-0x8c8]
    char v12;  // [bp-0x8b8]
    char v13;  // [bp-0x8a8]
    char v14;  // [bp-0x890]
    char v15;  // [bp-0x850]
    char v16;  // [bp-0x850]
    st_815790_2 *v17;  // [bp-0x848]
    char v18;  // [bp-0x818]
    char v19;  // [bp-0x810]
    char v20;  // [bp-0x7f8]
    char v21;  // [bp-0x7f0]
    char v22;  // [bp-0x7d8]
    char v23;  // [bp-0x7d0]
    char v24;  // [bp-0x7b8]
    char v25;  // [bp-0x7b0]
    char v26;  // [bp-0x798]
    char v27;  // [bp-0x790]
    char v28;  // [bp-0x778]
    char v29;  // [bp-0x770]
    char v30;  // [bp-0x758]
    char v31;  // [bp-0x750]
    char v32;  // [bp-0x738]
    char v33;  // [bp-0x730]
    char v34;  // [bp-0x718]
    char v35;  // [bp-0x710]
    char v36;  // [bp-0x6f8]
    char v37;  // [bp-0x6f0]
    char v38;  // [bp-0x6d8]
    char v39;  // [bp-0x6d0]
    char v40;  // [bp-0x6b8]
    char v41;  // [bp-0x6b0]
    char v42;  // [bp-0x698]
    char v43;  // [bp-0x690]
    char v44;  // [bp-0x678]
    char v45;  // [bp-0x670]
    char v46;  // [bp-0x658]
    char v47;  // [bp-0x650]
    char v48;  // [bp-0x648]
    unsigned int *v49;  // [bp-0x640]
    char v50;  // [bp-0x40]
    unsigned long v51;  // [bp-0x38]

    v51 = *(long long *)g_1a1f100;
    if (g_26f1ff0 == -0x1)
    {
LABEL_815f08:
        if (*(long long *)g_1a1f100 == v51)
            return *(unsigned int *)&v56;
        sub_12aa7f0();
    }
    v53 = g_26f1ff0 >> 13;
    v54 = (((unsigned int)(v53) >> 18 | 0x3ff) & v53) * 64;
    v55 = *(long long *)g_1a238a0;
    v56 = *(int *)(a0 + 100732);
    v7 = v56;
    v2 = g_26f1fc0;
    v57 = &v17;
    v58 = *(int *)(v55 + v54 + 48) * (g_26f1ff0 & 0x1fff);
    v3 = *(long long *)(*(long long *)(v55 + v54 + 16) + v58 - (*(int *)(v55 + v54 + 52) & *(long long *)(*(long long *)(v55 + v54 + 16) + v58 + 8)) + 8);
    (&v17)[3] = 0;
    (&v17)[2] = 0;
    v19 = 0;
    v18 = 0;
    v21 = 0;
    v20 = 0;
    v23 = 0;
    v22 = 0;
    v25 = 0;
    v24 = 0;
    v27 = 0;
    v26 = 0;
    v29 = 0;
    v28 = 0;
    v31 = 0;
    v30 = 0;
    v33 = 0;
    v32 = 0;
    v35 = 0;
    v34 = 0;
    v37 = 0;
    v36 = 0;
    v39 = 0;
    v38 = 0;
    v41 = 0;
    v40 = 0;
    v43 = 0;
    v42 = 0;
    v45 = 0;
    v44 = 0;
    v48 = 0;
    v47 = 0;
    v46 = 0;
    sub_7cc8a0(1, 3, &v17);
    v59 = v7;
    v15 = 0;
    if (!v48)
        goto LABEL_815f08;
    v60 = v48 * 32;
    idx = 0;
    do
    {
        v62 = v60;
        v63 = 16;
        if (idx != 16)
        {
            v16 = idx + 1;
            *(unsigned int *)&(&v14)[4 * idx] = *v57->field_68;
            v15 = v16;
            v63 = v16;
        }
    } while ((idx = v63, v57 += 32, v60 = v62 - 32, v62 != 32));
    if (idx > 0)
    {
        sub_6a2f0(&v14);
        v59 = v7;
        idx = v15;
    }
    if (!idx)
        goto LABEL_815f08;
    v56 = CONCAT(CONCAT(v59, v59), CONCAT(v59, v59));
    v6 = v56;
    v4 = 0;
    v64 = &v14;
    while (1)
    {
        v1 = v64;
        v5 = *(int *)v64;
        if (v64 == &v14 || v5 != v4)
            break;
LABEL_815eec:
        v64 = v1 + 4;
        v4 = v5;
        if (v64 == &(&v14)[4 * idx])
            goto LABEL_815f08;
    }
    v50 = 0;
    v65 = 0;
    v66 = *(unsigned int *)&v48;
    if (v66 > 0)
    {
        do
        {
            v67 = v65 * 32;
            if (*(int *)(*(long long *)((char *)&v17 + v67) + 104) == v5)
            {
                v68 = *(long long *)((char *)&v17 + v67 + 16);
                if ((int)v68 > 0)
                {
                    v69 = *(long long *)((char *)&v17 + v67 + 8);
                    node = *(long long *)((char *)&v17 + v67 + 24) + 4;
                    do
                    {
                        v71 = v68;
                        v72 = v50;
                        v50 = v72 + 1;
                        index = v72 * 3;
                        (&v49)[index] = v69;
                        v74 = *(int *)node;
                        v75 = *(long long *)g_1a238a0;
                        v76 = 0;
                        v77 = (((int)(v74) >> 13 >> 18 | 0x3ff) & (int)(v74) >> 13) * 64;
                        v78 = *(int *)(v75 + v77 + 48) * (v74 & 0x1fff);
                        v79 = *(long long *)(v75 + v77 + 16) + v78 - (*(int *)(v75 + v77 + 52) & *(long long *)(*(long long *)(v75 + v77 + 16) + v78 + 8));
                        (&v49)[1 + index] = v79;
                        if (*(long long *)(v79 + 24))
                            v76 = v79 + 24 + *(long long *)(v79 + 24) + 16;
                    } while (((&v49)[2 + index] = (unsigned int *)(unsigned long long)v76, node += 8, v68 = v71 - 1, v71 != 1));
                }
            }
        } while ((v65 = (char)(v65 + 1), (unsigned int)v65 != v66));
    }
    v80 = 0;
    if ((int)v3 <= 0)
        goto LABEL_815eec;
    while (1)
    {
        if (v50 <= 0)
            continue;
        v9 = 0;
        v81 = 5;
        v8 = 0;
        iter = &v49;
        do
        {
            v83 = iter->field_8;
            v84 = iter->field_10;
            v85 = 0;
            while (1)
            {
                v86 = 0;
                if (*(long long *)&v83->padding_18[0])
                    v86 = (char)(struct st_815790_3 *)&v83->padding_18[*(long long *)&v83->padding_18[0] + 16];
                if (v84 == v86 + v83->field_10 * 24 || *(int *)&v84->padding_0[0] > v80 || v85 > 9999)
                    break;
                if (*(int *)&v84->padding_0[0] == v80 && *(unsigned int *)&v59 >= *(int *)&v84->padding_0[4] && *(int *)&v84->padding_0[4] + *(float *)&v84->field_8 > *(unsigned int *)&v59)
                {
                    if (v84->field_10 < *(long long *)&v83->padding_18[8])
                    {
                        memcpy(&v13, &v6, 16);
                        v12 = 0;
                        sub_237710(48 * v84->field_10 + (char *)&iter->field_8->field_28 + iter->field_8->field_28 + 16, &v13, 0, &v12);
                        v59 = v7;
                        v83 = iter->field_8;
                        v87 = *(float *)&*(int *)iter->field_0;
                        v8 = *(unsigned int *)&v8 + v87;
                        v9 = (char)_mm_add_ps(v9, _mm_mul_ps(CONCAT(CONCAT(__float_as_int(v87), __float_as_int(v87)), CONCAT(__float_as_int(v87), __float_as_int(v87))), v12));
                        v84 = iter->field_10;
                    }
                    v88 = v83->field_8;
                    if (v88 != (char)v81 & v81 == 5)
                        v81 = v88;
                }
                v84 = &v84->field_18;
                iter->field_10 = v84;
                v85 += 1;
            }
            iter += 1;
        } while (iter != &(&v49)[3 * v50]);
        v89 = __int_as_float((unsigned int)v8);
        if (v89 > 9.999999747378752e-05f)
        {
            v90 = v59;
            v9 = (char)_mm_mul_ps(v9, CONCAT(CONCAT(__float_as_int(1.0f / v89), __float_as_int(1.0f / v89)), CONCAT(__float_as_int(1.0f / v89), __float_as_int(1.0f / v89))));
        }
        else
        {
            v90 = v59;
        }
        if (v89 < 0.0f)
            v89 = 0;
        v91 = v80 * 16 + v2;
        if (v89 + -1.0f < 0.0f)
            v92 = (char)v89;
        else
            v92 = 0x3f800000;
        if (v81 - 1 <= 3)
            break;
        v93 = *v91;
        v94 = v9;
        v56 = (char)_mm_add_ps(v93, _mm_mul_ps(CONCAT(CONCAT(v92, v92), CONCAT(v92, v92)), _mm_sub_ps(v94, v93)));
        *v91 = v56;
        v0 = g_26f1fcc[(char)(v80) >> 5];
        v59 = v90;
        if ((char)(*((char *)&v0 + ((int)(v80 & 31) >> 3))) >> (v80 & 31 & 7) & 1)
        {
            v11 = v56 & 0xffffffffffffffff;
            v56 = 0;
            v10 = 0;
            sub_99f80(&v11, &v10);
            v59 = v7;
            *v91 = 0;
        }
        v80 += 1;
        if (v80 == (unsigned int)v3)
        {
            idx = v15;
            goto LABEL_815eec;
        }
    }
    goto *((void *)((long long)(*(int *)((char *)&g_815f30[v81] - 4) + (char *)&g_815f30[0])));
}
