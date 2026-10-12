/* auto_exposure_update @ 0x8439e0  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Writes G+0xC (EV). Disabled: hold. Fast mode: lerp to target at 0.85 when |d|<0.2 else tweak 0x18DEEB4. Windowed: min/max of last N targets (N=settings+0x19504 clamped 1..60, ring G+0x20); adapt only outside window at min(|d|*settings+0x1950C, settings+0x19508). Clamp [settings+0x194F4, +0x194F8]; output ring G+0x110; index G+0x200 mod 60.
 */

typedef struct st_8439e0_0 {
    unsigned long long field_0;
} st_8439e0_0;

extern char g_7fe000;
extern char g_800000;
extern unsigned int g_18deeb4;
extern st_8439e0_0 *g_1a1f100;

long long sub_8439e0(void* idx, unsigned long long index, unsigned long a2, unsigned long a3)
{
    unsigned long long v15;  // r15
    unsigned long long v16;  // r14
    char v25;  // r15
    unsigned int v26;  // eax
    char v27;  // edx
    char v28;  // ebx
    unsigned long long v29;  // rsi
    char v30;  // cc_dep1
    char v31;  // ebx
    char v32;  // r12d
    char v33;  // edi
    unsigned int v34;  // r12d
    unsigned long long v17;  // r13
    unsigned int v35;  // edi
    char v36;  // edx
    char v37;  // ecx
    char v38;  // cc_dep1
    char v39;  // ecx
    char v40;  // eax
    char v41;  // ebx
    unsigned int v42;  // eax
    unsigned int v43;  // esi
    char v44;  // edx
    unsigned long long v18;  // r12
    char v45;  // edi
    char v46;  // cc_dep1
    char v47;  // edi
    char v48;  // eax
    char v49;  // ecx
    unsigned int v50;  // eax
    float v51;  // zmm1
    long long v52;  // rdi
    float v53;  // zmm0
    float v54;  // zmm4
    unsigned long long v19;  // rbx
    float v55;  // zmm0
    float v56;  // zmm4
    float v57;  // zmm3
    float v58;  // zmm1
    float v59;  // zmm0
    float v60;  // zmm4
    float v61;  // zmm2
    float v62;  // zmm3
    float v63;  // zmm1
    float v64;  // zmm2
    float v20;  // zmm6
    char v65;  // ecx
    char v66;  // eax
    uint128_t v67;  // xmm3
    char v68;  // edi
    int v69;  // edi
    char v70;  // edx
    char i;  // edx
    unsigned int v72;  // ebx
    char v73;  // edx
    int v74;  // edi
    char v21;  // ebx
    uint128_t v75;  // xmm5
    float v76;  // zmm3
    char v77;  // edx
    int v78;  // edx
    char v79;  // ecx
    char j;  // ecx
    unsigned int v81;  // edx
    char v82;  // ecx
    int v83;  // eax
    float v84;  // zmm3
    char v22;  // r8d
    float v85;  // zmm1
    char v86;  // ecx
    char v87;  // eax
    float v23;  // zmm2
    char v24;  // r14
    float v0;  // [bp-0x60]
    char v1;  // [bp-0x5c]
    float v2;  // [bp-0x5c]
    unsigned long long v3;  // [bp-0x58]
    float v4;  // [bp-0x4c]
    float v5;  // [bp-0x48]
    char v6;  // [bp-0x44]
    char v7;  // [bp-0x40]
    unsigned long v8;  // [bp-0x38]
    unsigned long long v9;  // [bp-0x30]
    unsigned long long v10;  // [bp-0x28]
    unsigned long long v11;  // [bp-0x20]
    unsigned long long v12;  // [bp-0x18]
    unsigned long long v13;  // [bp-0x10]

    v13 = v15;
    v12 = v16;
    v11 = v17;
    v10 = v18;
    v9 = v19;
    v8 = *(long long *)g_1a1f100;
    if (*(char *)(index + 103657))
    {
        v7 = 0;
        v6 = 0;
        v20 = __int_as_float((int)idx[20]);
        v21 = (int)idx[8];
        if (v21)
        {
            v5 = v20;
            v20 = v5;
            if ((char)sub_818f80(v21, 0, &v7, &v6))
            {
                v3 = index;
                v1 = v21;
                v22 = *(short *)sub_818dd0(v21);
                v5 = 0;
                v4 = 0;
                v23 = 0;
                if (v22)
                {
                    v5 = 0;
                    v24 = 0;
                    v25 = v7;
                    v4 = 0;
                    v23 = 0;
                    do
                    {
                        v26 = *(short *)(v25 + v24 * 8);
                        v27 = v26 & 0xffff & 0x3ff;
                        v28 = v26 * 0x20000 >> 27;
                        v29 = v24 * 8;
                        if (v28 == 31)
                        {
                            v30 = v27;
                            if (!v27)
                            {
                                v31 = 142;
                                if (v30)
                                    goto LABEL_843af5;
                            }
                            else
                            {
                                v31 = 0;
                                if (v30)
                                {
LABEL_843af5:
                                    v32 = 0;
LABEL_843af7:
                                    goto LABEL_843b49;
                                }
                            }
                            v32 = (char)&g_7fe000;
                            goto LABEL_843af7;
                        }
                        else
                        {
                            if (!v28)
                            {
                                v33 = 113;
                                v32 = 0;
                                v31 = 0;
                                if (v27)
                                {
                                    do
                                    {
                                        v34 = v27;
                                        v33 -= 1;
                                        v27 = v34 * 2;
                                    } while (!((char)(v27 >> 8) & 4));
                                    v32 = v34 * 0x4000 & 0xff7fc000;
                                    v31 = v33;
                                }
                            }
                            else
                            {
                                v31 = v28 + 112;
                                v32 = v27 * 0x2000;
                            }
LABEL_843b49:
                            v35 = *(short *)(v25 + (v29 | 2));
                            v5 += __int_as_float(v31 * &g_800000 | (v26 >> 15) * 0x80000000 | v32);
                            v36 = v35 & 0xffff & 0x3ff;
                            v37 = v35 * 0x20000 >> 27;
                            if (v37 == 31)
                            {
                                v38 = v36;
                                if (!v36)
                                {
                                    v39 = 142;
                                    if (v38)
                                        goto LABEL_843b99;
                                }
                                else
                                {
                                    v39 = 0;
                                    if (v38)
                                    {
LABEL_843b99:
                                        v40 = 0;
LABEL_843b9b:
                                        goto LABEL_843be8;
                                    }
                                }
                                v40 = (char)&g_7fe000;
                                goto LABEL_843b9b;
                            }
                            else
                            {
                                if (!v37)
                                {
                                    v41 = 113;
                                    v40 = 0;
                                    v39 = 0;
                                    if (v36)
                                    {
                                        do
                                        {
                                            v42 = v36;
                                            v41 -= 1;
                                            v36 = v42 * 2;
                                        } while (!((char)(v36 >> 8) & 4));
                                        v40 = v42 * 0x4000 & 0xff7fc000;
                                        v39 = v41;
                                    }
                                }
                                else
                                {
                                    v39 = v37 + 112;
                                    v40 = v36 * 0x2000;
                                }
LABEL_843be8:
                                v43 = *(short *)(v25 + (v29 | 4));
                                v4 += __int_as_float(v39 * &g_800000 | (v35 >> 15) * 0x80000000 | v40);
                                v44 = v43 & 0xffff & 0x3ff;
                                v45 = v43 * 0x20000 >> 27;
                                if (v45 == 31)
                                {
                                    v46 = v44;
                                    if (!v44)
                                    {
                                        v47 = 142;
                                        if (v46)
                                            goto LABEL_843c34;
                                    }
                                    else
                                    {
                                        v47 = 0;
                                        if (v46)
                                        {
LABEL_843c34:
                                            v48 = 0;
LABEL_843c36:
                                            continue;
                                        }
                                    }
                                    v48 = (char)&g_7fe000;
                                    goto LABEL_843c36;
                                }
                                else if (!v45)
                                {
                                    v49 = 113;
                                    v48 = 0;
                                    v47 = 0;
                                    if (v44)
                                    {
                                        do
                                        {
                                            v50 = v44;
                                            v49 -= 1;
                                            v44 = v50 * 2;
                                        } while (!((char)(v44 >> 8) & 4));
                                        v48 = v50 * 0x4000 & 0xff7fc000;
                                        v47 = v49;
                                    }
                                }
                                else
                                {
                                    v47 = v45 + 112;
                                    v48 = v44 * 0x2000;
                                }
                            }
                        }
                    } while ((v23 += __int_as_float(v47 * &g_800000 | (v43 >> 15) * 0x80000000 | v48), v24 = (char)(v24 + 1), (unsigned int)v24 != v22));
                }
                v0 = v23;
                sub_818fa0(v1);
                v51 = v0;
                v5 /= v51;
                sub_12aaf70(0);
                v2 = v5 * 0.5f;
                v4 = (v4 / v51 + 9.999999747378752e-06f) * 1.4426950216293335f * 0.5f;
                v5 = v2 + v4;
                sub_12ab9b0(v52);
                sub_915e0();
                *(int *)&idx[516] = (int)idx[516];
                sub_12ab9b0();
                sub_915e0();
                *(int *)&idx[520] = (int)idx[520];
                sub_12ab9b0();
                sub_915e0();
                *(int *)&idx[524] = (int)idx[524];
                index = v3;
                v53 = *(int *)(index + 103660) - v5;
                v54 = 0;
                if ((__float_as_int(v53) & 0x7f800000) != 0x7f800000)
                {
                    v54 = (float)0x40e00000;
                    if (v53 + 7.0f < 0.0f)
                        v53 = -7.0;
                    if (v53 + -7.0f < 0.0f)
                        v54 = v53;
                }
                v20 = __int_as_float(v54 + (int)idx[20]);
            }
        }
        v55 = 1.0;
        v56 = __int_as_float(1.0f - *(int *)(index + 103664));
        v57 = *(float *)&*(int *)(index + 103668);
        v58 = *(float *)&*(int *)(index + 103672);
        *(float *)&idx[24] = v57;
        if (v56 < 0.0f)
            v56 = 0;
        if (v56 + -1.0f < 0.0f)
            v55 = v56;
        v59 = v20 * v55;
        *(int *)&idx[28] = *(int *)(index + 103672);
        v60 = v59;
        if (v60 - v57 < 0.0f)
            v60 = v57;
        if (v60 - v58 < 0.0f)
            v58 = v60;
        if (*(char *)(index + 103656))
        {
            v61 = __int_as_float((int)idx[12]);
            if (*(char *)(index + 103658))
            {
                if (0.20000000298023224f > (__float_as_int(v61 - v58) & 0x7fffffff))
                {
                    g_18deeb4 = 1062836634;
                    v61 = __int_as_float((int)idx[12]);
                    v62 = 0.85;
                }
                else
                {
                    v62 = *(float *)&g_18deeb4;
                }
                v63 = v58 * v62;
                v64 = (1.0f - v62) * v61;
            }
            else
            {
                v65 = *(int *)(index + 103684);
                if (v65 > 0)
                    v66 = v65;
                else
                    v66 = 1;
                if (60 < v66)
                    v66 = 60;
                v67 = *(int *)(index + 103672);
                if (v66 > 0)
                {
                    if (v65 > 0)
                        v68 = v65;
                    else
                        v68 = 1;
                    v69 = ~v68;
                    if (-0x3e < v69)
                        v70 = v69;
                    else
                        v70 = 0xffffffc3;
                    i = ~v70;
                    v72 = (unsigned int)(60 - v66) + (int)idx[0x200];
                    do
                    {
                        v73 = i;
                        if ((int)v72 <= 59)
                            v74 = v72;
                        else
                            v74 = v72 - 60;
                        v75 = *(int *)((char *)idx + 4 * v74 + 32);
                        if (*(unsigned int *)&v67 - *(unsigned int *)&v75 < 0.0f)
                            v75 = v67;
                        i = v73 - 1;
                        v67 = v75;
                        v72 = v74 + 1;
                    } while (i);
                }
                else
                {
                    v75 = v67;
                }
                if (*(unsigned int *)&v75 < v61)
                {
                    v76 = *(float *)&*(int *)(index + 103668);
                    if (v66 > 0)
                    {
                        if (v65 > 0)
                            v77 = v65;
                        else
                            v77 = 1;
                        v78 = ~v77;
                        if (-0x3e < v78)
                            v79 = v78;
                        else
                            v79 = 0xffffffc3;
                        j = ~v79;
                        v81 = (unsigned int)(60 - v66) + (int)idx[0x200];
                        do
                        {
                            v82 = j;
                            if ((int)v81 <= 59)
                                v83 = v81;
                            else
                                v83 = v81 - 60;
                            if (v76 - *(int *)((char *)idx + 4 * v83 + 32) < 0.0f)
                                v76 = *(float *)&*(int *)((char *)idx + 4 * v83 + 32);
                            j = v82 - 1;
                            v81 = v83 + 1;
                        } while (j);
                    }
                    if (v61 < v76)
                        goto LABEL_84403b;
                }
                v84 = __int_as_float((__float_as_int(v61 - v58) & 0x7fffffff) * *(int *)(index + 103692));
                if (*(int *)(index + 103688) - v84 < 0.0f)
                    v84 = *(float *)&*(int *)(index + 103688);
                v63 = v58 * v84;
                v64 = v61 * (1.0f - v84);
            }
            v61 = v63 + v64;
            *(float *)&idx[12] = v61;
LABEL_84403b:
            v85 = *(float *)&*(int *)(index + 103672);
            if (v61 - *(int *)(index + 103668) < 0.0f)
                v61 = *(float *)&*(int *)(index + 103668);
            if (v61 - *(int *)(index + 103672) < 0.0f)
                v85 = v61;
            *(float *)&idx[12] = v85;
        }
        else
        {
            v85 = __int_as_float((int)idx[12]);
        }
        *(float *)((char *)idx + 4 * idx[0x200] + 32) = v59;
        *(float *)((char *)idx + 4 * idx[0x200] + 272) = v85;
        if (59 <= (int)idx[0x200])
            v86 = 0;
        else
            v86 = (int)idx[0x200] + 1;
        *(unsigned int *)&idx[0x200] = v86;
    }
    if (*(long long *)g_1a1f100 == v8)
        return *(long long *)g_1a1f100;
    v87 = sub_12aa7f0();
    if (v87 == 1)
        return v87 - 1;
    return v87 - 1;
}
