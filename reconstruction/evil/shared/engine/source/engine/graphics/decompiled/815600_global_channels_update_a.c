/* global_channels_update_a @ 0x815600  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Per-frame global channel update, first pass (called from lighting_frame_update 0x7ebfc0).
 */
typedef struct st_815600_0 {
    unsigned long long field_0;
} st_815600_0;

extern char g_18de9ec;
extern st_815600_0 *g_1a1f100;
extern st_815600_0 *g_1a238a0;
extern unsigned long long g_26f1fc0;
extern int g_26f1ff0;

long long sub_815600(void)
{
    int v17;  // edx
    unsigned long long v18;  // rcx
    unsigned long long v26;  // r14
    unsigned long long v19;  // rsi
    unsigned long v20;  // rax
    unsigned long long *v21;  // rdi
    unsigned long long *v22;  // r15
    unsigned long v23;  // r13
    unsigned long long v24;  // r12
    unsigned long i;  // rbx
    unsigned int v0;  // [bp-0x1a8]
    unsigned long v1;  // [bp-0xc0]
    unsigned long long v2;  // [bp-0xb8]
    unsigned long long v3;  // [bp-0xb0]
    unsigned long long v4;  // [bp-0xa8]
    unsigned long long v5;  // [bp-0xa0]
    unsigned long long *v6;  // [bp-0x98]
    char *v7;  // [bp-0x90]
    unsigned long long *v8;  // [bp-0x80]
    unsigned long long *v9;  // [bp-0x78]
    unsigned long long *v10;  // [bp-0x70]
    uint128_t v11;  // [bp-0x68]
    uint128_t v12;  // [bp-0x58]
    unsigned int v13;  // [bp-0x40]
    unsigned long v14;  // [bp-0x38]
    char v15;  // [bp-0x8]

    v14 = *(long long *)g_1a1f100;
    if (g_26f1ff0 != -0x1)
    {
        v17 = g_26f1ff0 >> 13;
        v18 = (((unsigned int)(v17) >> 18 | 0x3ff) & v17) * 64;
        v19 = *(long long *)g_1a238a0;
        v20 = *(int *)(v19 + v18 + 48) * (g_26f1ff0 & 0x1fff);
        v21 = *(long long *)(v19 + v18 + 16) + v20 - (*(int *)(v19 + v18 + 52) & *(long long *)(*(long long *)(v19 + v18 + 16) + v20 + 8));
        if ((long long)v21[1] > 0)
        {
            v10 = v21;
            v8 = v21 + 4;
            v22 = v21 + 6;
            v9 = v21 + 2;
            v23 = 0;
            v24 = &g_26f1fc0;
            i = 0;
            do
            {
                v13 = *(int *)(*v9 + (char *)v9 + 4 * i + 16);
                if (!(char)sub_242190(&v13, *(long long *)v24 + v23) && g_18de9ec)
                    *(int128_t *)(*(long long *)v24 + v23) = *(int128_t *)(v23 + *v8 + (char *)v8 + 16);
                v0 = *(int *)(*v22 + (char *)v22 + 4 * ((int)((unsigned int)i) >> 5) + 16);
                if ((char)(*((char *)&v0 + ((int)((unsigned int)i & 31) >> 3))) >> ((char)i & 31 & 7) & 1)
                {
                    v26 = v24;
                    v12 = 0xffffffffffffffff & *(int128_t *)(*(long long *)v26 + v23);
                    v11 = 0;
                    sub_99f80(&v12, &v11);
                    *(uint128_t *)(*(long long *)v26 + v23) = 0;
                    v24 = v26;
                }
                v23 += 16;
                i += 1;
            } while ((long long)i < (long long)v10[1]);
        }
    }
    if (*(long long *)g_1a1f100 == v14)
        return *(long long *)g_1a1f100;
    sub_12aa7f0();
    v7 = &v15;
    v6 = v22;
    v5 = v26;
    v4 = v23;
    v3 = v24;
    v2 = i;
    v1 = *(long long *)g_1a1f100;
    if (g_26f1ff0 == -0x1)
        goto LABEL_0x815f08;
    else
        goto LABEL_0x8157c4;
}
