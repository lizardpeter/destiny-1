/* frame_extern_build @ 0x807750  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Builds TFX extern 1 (Frame, 0x170 bytes). [0]=renderer+0x1896C, [1..4]=+0x18978/+0x18974/+0x18970/+0x1897C, +0x14=1/30, +0x18=1/60, +0x1C=exp2f(E), +0x20=E, +0x24=exp2f(0.33E), +0x28=exp2f(0.33E)/exp2f(E), +0x160..0x168=G+0x204..0x20C, rest via 0x820D30.
 */

typedef struct st_807750_1 {
    unsigned long long field_0;
    long long field_8;
    char padding_10[288];
    struct st_807750_0 *field_130;
} st_807750_1;

typedef struct st_807750_0 {
    char padding_0[48];
    int field_30;
} st_807750_0;

typedef struct st_807750_2 {
    unsigned long long field_0;
} st_807750_2;

extern st_807750_2 *g_1a238a0;

unsigned int * sub_807750(st_807750_1 *index, float a1, float a2, float a3, float a4, float a5)
{
    unsigned int *idx;  // r13
    unsigned long long v12;  // rdx
    unsigned int *v13;  // rbx
    long long idx1;  // r15
    st_807750_0 *v15;  // r12
    st_807750_0 *v16;  // al
    long long v4;  // rdi
    long long v5;  // rsi
    long long v6;  // rdx
    st_807750_0 *v7;  // rax
    unsigned int v8;  // eax
    unsigned long long v9;  // rcx
    unsigned long long v10;  // rsi
    unsigned long v11;  // rax
    unsigned int v0;  // [bp-0x4c]

    idx = sub_82b940(index->field_8, 1, 368);
    *(char *)&index->field_130 = 1;
    sub_12ab9b0(v4, v5, v6);
    v0 = *(int *)(index->field_0 + 100716);
    sub_12ab9b0();
    *idx = v0;
    idx[1] = *(int *)(index->field_0 + 100728);
    idx[2] = *(int *)(index->field_0 + 100724);
    idx[3] = *(int *)(index->field_0 + 100720);
    idx[4] = *(int *)(index->field_0 + 100732);
    idx[5] = 1023969417;
    idx[6] = 1015580809;
    *(float *)&idx[8] = a1;
    *(float *)&idx[7] = a1;
    *(float *)&idx[9] = a2;
    *(float *)&idx[10] = a2 / a1;
    idx[28] = 0;
    idx[88] = a3;
    idx[89] = a4;
    idx[90] = a5;
    sub_820d30(idx);
    *(unsigned long long *)&idx[36] = 0;
    sub_8cf990(index->field_0 + 102800, idx);
    v7 = sub_7ea940(v4, v5);
    if (v7)
    {
        v8 = v7->field_30;
        v9 = (((int)(v8) >> 13 >> 18 | 0x3ff) & (int)(v8) >> 13) * 64;
        v10 = *(long long *)g_1a238a0;
        v11 = *(int *)(v10 + v9 + 48) * (v8 & 0x1fff);
        v12 = *(int *)(v10 + v9 + 52) & *(long long *)(*(long long *)(v10 + v9 + 16) + v11 + 8);
        v13 = *(long long *)(v10 + v9 + 16) + v11 - v12;
        sub_8213f0(idx + 42, v13[2], v12, v9);
        sub_8213f0(idx + 38, v13[3]);
        sub_8213f0(idx + 40, v13[4]);
    }
    idx1 = index->field_8;
    v15 = sub_82cb90(0);
    if (v15)
    {
        v16 = (st_807750_0 *)(char)sub_81fb90(idx1, v15, *(long long *)(idx1 + 5568));
        if (!v16)
        {
            v16 = (st_807750_0 *)0;
            if ((char)sub_82bd10(idx1, 1, &v15->padding_0[32]))
                v16 = (st_807750_0 *)(char)sub_82bd10(idx1, 2, &v15[3].padding_0[20]);
        }
        if (v16)
        {
            *(char *)(idx1 + 5548) = *(char *)(idx1 + 5548) | 1;
            return idx;
        }
    }
    sub_82ba20(index->field_8, 1, 368);
    *(char *)&index->field_130 = 0;
    return 0;
}
