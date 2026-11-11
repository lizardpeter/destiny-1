/* render_context_capture_externs @ 0x822350  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Clones a source context: deep-copies each pending extern block into own arena and repoints slots; copies +0x13D8/+0x13E8/+0x15AC/+0x15B0/+0x15D0/+0x15D4.
 */

typedef struct st_822350_0 {
    uint128_t field_0;
    uint128_t field_10;
    uint128_t field_20;
    uint128_t field_30;
    unsigned long long field_40;
    unsigned long long field_48;
} st_822350_0;


void sub_822350(uint128_t *idx, unsigned long idx1)
{
    unsigned long long v7;  // r15
    unsigned long long v8;  // r14
    unsigned long v17;  // rdx
    uint128_t *iter;  // r8
    int v19;  // r9d
    unsigned long v20;  // rcx
    uint128_t *v21;  // r10
    unsigned long v22;  // r11
    char v23;  // rsi
    uint128_t *v24;  // rcx
    unsigned long long v25;  // rax
    unsigned long long v26;  // rsi
    unsigned long long v9;  // r13
    uint128_t *idx2;  // rbx
    uint128_t *v28;  // rdi
    uint128_t *v29;  // rdi
    unsigned long long v32;  // 4162
    unsigned long long v33;  // rax
    unsigned long long v34;  // rax
    unsigned long long v10;  // r12
    unsigned long long v37;  // 4126
    int v38;  // eax
    unsigned long v39;  // r15
    long long v40;  // r15
    unsigned int v41;  // eax
    unsigned long long v42;  // rcx
    unsigned long v43;  // r15
    long long v44;  // r15
    unsigned int v45;  // eax
    unsigned long long v46;  // rcx
    unsigned long long v11;  // rbx
    unsigned long v47;  // rax
    st_822350_0 *v48;  // rdx
    unsigned int v49;  // ecx
    st_822350_0 *v50;  // rcx
    uint128_t v51;  // xmm0
    uint128_t v52;  // xmm1
    uint128_t v53;  // xmm3
    unsigned long v54;  // r15
    long long v55;  // r15
    unsigned int v56;  // eax
    unsigned long long v12;  // rax
    unsigned long long v57;  // rcx
    unsigned long v58;  // r15
    long long v59;  // rdi
    unsigned int v60;  // eax
    unsigned long long v61;  // rcx
    uint128_t *index;  // rax
    uint128_t v63;  // xmm6
    uint128_t v64;  // xmm4
    uint128_t v65;  // xmm7
    uint128_t v66;  // xmm8
    char v13;  // r15d
    uint128_t v67;  // xmm2
    uint128_t v68;  // xmm5
    uint128_t v69;  // xmm1
    uint128_t v70;  // xmm9
    uint128_t v71;  // xmm3
    uint128_t v72;  // xmm0
    uint128_t v73;  // xmm6
    uint128_t v74;  // xmm7
    unsigned long long v14;  // rax
    char v15;  // r12
    unsigned long long v16;  // rax
    unsigned long long v0;  // [bp-0x38]
    unsigned long long v1;  // [bp-0x30]
    unsigned long long v2;  // [bp-0x28]
    unsigned long long v3;  // [bp-0x20]
    unsigned long long v4;  // [bp-0x18]
    unsigned long long v5;  // [bp-0x10]

    v5 = v7;
    v4 = v8;
    v3 = v9;
    v2 = v10;
    v1 = v11;
    v0 = v12;
    v13 = 0;
    sub_12aa980((char *)&idx[0x100] + 8, 0, 648);
    *(unsigned int *)((char *)&idx[346] + 8) = 0;
    *(unsigned int *)&idx[0x100] = 0;
    v14 = *(long long *)(idx1 + 5080);
    *(long long *)&idx[318] = *(long long *)(idx1 + 5088);
    *(unsigned long long *)((char *)&idx[317] + 8) = v14;
    v15 = 0;
    *(int *)((char *)&idx[346] + 12) = *(int *)(idx1 + 5548);
    *(int *)((char *)&idx[347] + 8) = *(int *)(idx1 + 5560);
    *(long long *)&idx[347] = *(long long *)(idx1 + 5552);
    *(int *)&idx[349] = *(int *)(idx1 + 5584);
    *(int *)((char *)&idx[349] + 4) = *(int *)(idx1 + 5588);
    v16 = *(long long *)(idx1 + 5096);
    *(long long *)&idx[319] = *(long long *)(idx1 + 5104);
    *(unsigned long long *)((char *)&idx[318] + 8) = v16;
    if (*(int *)(idx1 + 5544) > 0)
    {
        while (1)
        {
            v17 = *(int *)(idx1 + v15 * 24 + 5160);
            iter = *(long long *)(idx1 + v17 * 8 + 4104);
            v19 = *(int *)(idx1 + v17 * 4 + 4752);
            v20 = v13;
            v21 = (char *)idx + v20;
            v22 = v19;
            *(unsigned int *)&idx[0x100] = (unsigned int)v20 + v19;
            v23 = v22 >> 6;
            if (!v23)
            {
                v24 = v21;
            }
            else
            {
                v25 = v23 * 64;
                v26 = -v23;
                idx2 = v21;
                v28 = iter;
                do
                {
                    *idx2 = *v28;
                    idx2[1] = v28[1];
                    idx2[2] = v28[2];
                    v29 = v28 + 4;
                    idx2[3] = v28[3];
                    v32 = _ccall(4, 24, v26 + 1, 0, idx2 + 4 < idx2);
                    idx2 += 4;
                    v26 += 1;
                    v28 = v29;
                } while (!(v32 & 1));
                v24 = v20 + v25 + (char *)idx;
                iter = (char *)iter + v25;
            }
            v33 = v22 * 0x400000000000000 >> 62;
            if (v33)
            {
                v34 = -v33;
                do
                {
                    *v24 = *iter;
                    iter += 1;
                    v37 = _ccall(4, 24, v34 + 1, 0, v24 + 1 < v24);
                    v34 += 1;
                    v24 += 1;
                } while (!(v37 & 1));
            }
            *(uint128_t **)((char *)idx + 8 * v17 + 4104) = v21;
            *(int *)((char *)idx + 4 * v17 + 4752) = v19;
            *(unsigned int *)((char *)idx + 24 * *(int *)((char *)&idx[346] + 8) + 5160) = v17;
            v15 += 1;
            *(unsigned int *)((char *)idx + 24 * *(int *)((char *)&idx[346] + 8) + 5176) = 0;
            *(unsigned long long *)((char *)idx + 24 * *(int *)((char *)&idx[346] + 8) + 5168) = 0;
            v38 = *(int *)((char *)&idx[346] + 8) + 1;
            *(int *)((char *)&idx[346] + 8) = v38;
            if (v15 >= *(int *)(idx1 + 5544))
                break;
            v13 = idx[0x100];
        }
        v15 = v38;
    }
    if (*(long long *)(idx1 + 0x1010) && !(long long)idx[0x101])
    {
        v39 = (int)idx[0x100];
        *(unsigned int *)&idx[0x100] = (unsigned int)v39 + 368;
        v40 = v39 + (char *)idx;
        v41 = *(int *)((char *)&idx[297] + 4);
        *(long long *)&idx[0x101] = v40;
        *(unsigned int *)((char *)&idx[297] + 4) = 368;
        *(unsigned int *)((char *)idx + 24 * v15 + 5160) = 1;
        *(unsigned long long *)((char *)idx + 24 * *(int *)((char *)&idx[346] + 8) + 5168) = 0;
        v42 = *(int *)((char *)&idx[346] + 8) * 3;
        *(unsigned int *)((char *)idx + 8 * v42 + 5176) = v41;
        *(int *)((char *)&idx[346] + 8) = *(int *)((char *)&idx[346] + 8) + 1;
        sub_12aa980(v40, 0, 368, v42);
        *(char *)&idx[347] = (char)idx[347] | 2;
        sub_12aa7c0(v40, *(long long *)(idx1 + 0x1010), 368);
    }
    if (*(long long *)(idx1 + 4120) && !*(long long *)((char *)&idx[0x101] + 8))
    {
        v43 = (int)idx[0x100];
        *(unsigned int *)&idx[0x100] = (unsigned int)v43 + 672;
        v44 = v43 + (char *)idx;
        v45 = *(int *)((char *)&idx[297] + 8);
        *(long long *)((char *)&idx[0x101] + 8) = v44;
        *(unsigned int *)((char *)&idx[297] + 8) = 672;
        *(unsigned int *)((char *)idx + 24 * *(int *)((char *)&idx[346] + 8) + 5160) = 2;
        *(unsigned long long *)((char *)idx + 24 * *(int *)((char *)&idx[346] + 8) + 5168) = 0;
        v46 = *(int *)((char *)&idx[346] + 8) * 3;
        *(unsigned int *)((char *)idx + 8 * v46 + 5176) = v45;
        *(int *)((char *)&idx[346] + 8) = *(int *)((char *)&idx[346] + 8) + 1;
        sub_12aa980(v44, 0, 672, v46);
        *(char *)&idx[347] = (char)idx[347] | 4;
        sub_12aa7c0(v44, *(long long *)(idx1 + 4120), 672);
    }
    if (*(long long *)(idx1 + 4128) && !(long long)idx[258])
    {
        v47 = (int)idx[0x100];
        *(unsigned int *)&idx[0x100] = (unsigned int)v47 + 80;
        v48 = (char *)idx + v47;
        v49 = *(int *)((char *)&idx[297] + 12);
        *(st_822350_0 **)&idx[258] = v48;
        *(unsigned int *)((char *)&idx[297] + 12) = 80;
        *(unsigned int *)((char *)idx + 24 * *(int *)((char *)&idx[346] + 8) + 5160) = 3;
        *(unsigned long long *)((char *)idx + 24 * *(int *)((char *)&idx[346] + 8) + 5168) = 0;
        *(unsigned int *)((char *)idx + 24 * *(int *)((char *)&idx[346] + 8) + 5176) = v49;
        *(int *)((char *)&idx[346] + 8) = *(int *)((char *)&idx[346] + 8) + 1;
        memset((char *)idx + v47 + 8, 0, 72);
        *(unsigned long long *)((char *)idx + v47) = 0;
        *(char *)&idx[347] = (char)idx[347] | 8;
        v50 = *(long long *)(idx1 + 4128);
        if (!(v48 & 0x3))
            if (!((char)v50 & 3))
                goto LABEL_0x828225;
            else
                goto LABEL_8227fd;
LABEL_8227fd:
        v51 = v50->field_0;
        v52 = v50->field_20;
        v53 = v50->field_30;
        v48->field_10 = v50->field_10;
        v48->field_0 = v51;
        v48->field_30 = v53;
        v48->field_20 = v52;
        v48->field_48 = v50->field_48;
        v48->field_40 = v50->field_40;
    }
    if (*(long long *)(idx1 + 4136) && !*(long long *)((char *)&idx[258] + 8))
    {
        v54 = (int)idx[0x100];
        *(unsigned int *)&idx[0x100] = (unsigned int)v54 + 288;
        v55 = v54 + (char *)idx;
        v56 = idx[298];
        *(long long *)((char *)&idx[258] + 8) = v55;
        *(unsigned int *)&idx[298] = 288;
        *(unsigned int *)((char *)idx + 24 * *(int *)((char *)&idx[346] + 8) + 5160) = 4;
        *(unsigned long long *)((char *)idx + 24 * *(int *)((char *)&idx[346] + 8) + 5168) = 0;
        v57 = *(int *)((char *)&idx[346] + 8) * 3;
        *(unsigned int *)((char *)idx + 8 * v57 + 5176) = v56;
        *(int *)((char *)&idx[346] + 8) = *(int *)((char *)&idx[346] + 8) + 1;
        sub_12aa980(v55, 0, 288, v57);
        *(char *)&idx[347] = (char)idx[347] | 16;
        sub_12aa7c0(v55, *(long long *)(idx1 + 4136), 288);
    }
    if (!*(long long *)(idx1 + 4144))
        goto LABEL_0x822a94;
    if ((long long)idx[259])
        goto LABEL_0x822a94;
    v58 = (int)idx[0x100];
    *(unsigned int *)&idx[0x100] = (unsigned int)v58 + 0x100;
    v59 = (char *)idx + v58;
    v60 = *(int *)((char *)&idx[298] + 4);
    *(long long *)&idx[259] = v59;
    *(unsigned int *)((char *)&idx[298] + 4) = 0x100;
    *(unsigned int *)((char *)idx + 24 * *(int *)((char *)&idx[346] + 8) + 5160) = 5;
    *(unsigned long long *)((char *)idx + 24 * *(int *)((char *)&idx[346] + 8) + 5168) = 0;
    v61 = *(int *)((char *)&idx[346] + 8) * 3;
    *(unsigned int *)((char *)idx + 8 * v61 + 5176) = v60;
    *(int *)((char *)&idx[346] + 8) = *(int *)((char *)&idx[346] + 8) + 1;
    sub_12aa980(v59, 0, 0x100, v61);
    *(char *)&idx[347] = (char)idx[347] | 32;
    index = *(long long *)(idx1 + 4144);
    v63 = *index;
    v64 = index[2];
    v65 = index[3];
    v66 = index[11];
    v67 = index[9];
    v68 = index[7];
    v69 = index[5];
    v70 = index[13];
    v71 = index[10];
    *(uint128_t *)((char *)idx + v58 + 16) = index[1];
    v72 = index[8];
    *(uint128_t *)((char *)idx + v58) = v63;
    v73 = index[6];
    *(uint128_t *)((char *)idx + v58 + 48) = v65;
    v74 = index[4];
    *(uint128_t *)((char *)idx + v58 + 32) = v64;
    *(uint128_t *)((char *)idx + v58 + 80) = v69;
    *(uint128_t *)((char *)idx + v58 + 64) = v74;
    *(uint128_t *)((char *)idx + v58 + 112) = v68;
    *(uint128_t *)((char *)idx + v58 + 96) = v73;
    *(uint128_t *)((char *)idx + v58 + 144) = v67;
    *(uint128_t *)((char *)idx + v58 + 128) = v72;
    *(uint128_t *)((char *)idx + v58 + 176) = v66;
    *(uint128_t *)((char *)idx + v58 + 160) = v71;
    *(uint128_t *)((char *)idx + v58 + 208) = v70;
    *(uint128_t *)((char *)idx + v58 + 192) = index[12];
    *(uint128_t *)((char *)idx + v58 + 240) = index[15];
    *(uint128_t *)((char *)idx + v58 + 224) = index[14];
    if (!*(long long *)(idx1 + 4152))
        goto LABEL_0x822b54;
    else
        goto LABEL_0x822aa2;
}
