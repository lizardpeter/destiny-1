/* global_channels_load_defaults @ 0x8154e0  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Loads defaults from the global-channel definition tag g_26f1ff0 (activity tag field_34): parallel arrays of 100 FNV-1 name hashes (+0x8) and vec4 defaults (+0x18) into g_26f1fc0; count -> g_26f1fc8.
 */
typedef struct st_8154e0_0 {
    char padding_0[8];
    unsigned long long field_8;
    char padding_10[16];
    unsigned long long field_20;
    char padding_28[12];
    unsigned int field_34;
} st_8154e0_0;

typedef struct st_8154e0_2 {
    unsigned int field_0;
} st_8154e0_2;

typedef struct st_8154e0_1 {
    unsigned long long field_0;
} st_8154e0_1;

extern st_8154e0_1 *g_1a238a0;
extern st_8154e0_2 *g_26f1fc0;
extern unsigned int g_26f1fc8;
extern unsigned int g_26f1ff0;

st_8154e0_0 * sub_8154e0(void)
{
    st_8154e0_0 *v1;  // rax
    unsigned int v2;  // ecx
    char v11;  // rdx
    char idx;  // rcx
    unsigned long long v3;  // rdx
    unsigned long long v4;  // rsi
    unsigned long v5;  // rcx
    st_8154e0_0 *v6;  // rax
    unsigned int *v7;  // rdi
    unsigned long long v8;  // rdx
    st_8154e0_0 *v9;  // rax
    unsigned long v10;  // rsi

    v1 = sub_7ea940();
    if (!v1)
        return v1;
    v2 = v1->field_34;
    if (v2 == 0xffffffff)
        return v1;
    g_26f1ff0 = v2;
    v3 = (((int)(v2) >> 13 >> 18 | 0x3ff) & (int)(v2) >> 13) * 64;
    v4 = *(long long *)g_1a238a0;
    v5 = *(int *)(v4 + v3 + 48) * (v2 & 0x1fff);
    v6 = *(long long *)(v4 + v3 + 16) + v5 - (*(int *)(v4 + v3 + 52) & *(long long *)(*(long long *)(v4 + v3 + 16) + v5 + 8));
    g_26f1fc8 = v6->field_8;
    if ((int)g_26f1fc8 <= 0)
        return v6;
    v7 = g_26f1fc0;
    v8 = g_26f1fc8 * 16;
    if ((long long)v8 >= 101)
        return sub_12aa7c0();
    v9 = &v6->field_20;
    if (!(g_26f1fc0 & 0x3))
    {
        v10 = (unsigned long)v9->padding_0;
        if (!((v9->padding_0 & 3) + (v9 & 0x3)))
        {
            v11 = (long long)(v8) >> 2;
            if (!v11)
                return v9;
            idx = 0;
            while (1)
            {
                v7[idx] = *(int *)&v9->padding_10[4 * idx + v10];
                if (v11 - 1 == idx)
                    break;
                idx += 1;
                v7 = g_26f1fc0;
                v10 = (unsigned long)v9->padding_0;
            }
            return v9;
        }
    }
    return sub_12aa7c0();
}
