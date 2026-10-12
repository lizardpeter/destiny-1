/* global_channels_copy_to_renderer @ 0x8162d0  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Per-frame copy of g_26f1fc0 into renderer+0x18958 (the array render-context ctx+0x13F0 points at, read by TFX opcode 0x4B). Called from renderer_frame_prepare.
 */
typedef struct st_8162d0_1 {
    char field_0;
    char padding_1[7];
    struct st_8162d0_2 *field_8;
} st_8162d0_1;

typedef struct st_8162d0_2 {
    unsigned int field_0;
} st_8162d0_2;

typedef struct st_8162d0_0 {
    unsigned long long field_0;
} st_8162d0_0;

extern st_8162d0_0 *g_1a1f100;
extern st_8162d0_2 *g_26f1fc0;
extern char g_26f1fc8;
extern unsigned int g_295a874;
extern char g_295a878;
extern unsigned int g_295a880;
extern char g_295a888;
extern unsigned int g_295a890;
extern char g_295a898;
extern unsigned int g_295a8a0;
extern char g_295a8a8;
extern unsigned int g_295a8b0;
extern char g_295a8b8;
extern unsigned int g_295a8c0;
extern char g_295a8c8;
extern unsigned int g_295a8d0;
extern char g_295a8d8;
extern char g_295a8e8;

char sub_8162d0(st_8162d0_1 *idx)
{
    char v6;  // r14b
    unsigned long v7;  // rax
    unsigned long long v8;  // rdi
    unsigned int *v9;  // rdi
    unsigned int *v10;  // rsi
    char index;  // rcx
    char v0;  // [bp-0x48]
    char v1;  // [bp-0x40]
    unsigned int v2;  // [bp-0x38]
    unsigned int v3;  // [bp-0x34]
    unsigned long v4;  // [bp-0x28]

    v4 = *(long long *)g_1a1f100;
    *(unsigned int *)&idx->field_0 = 0;
    idx->field_8 = 0;
    v6 = 0;
    if (*(int *)&g_26f1fc8 > 0)
    {
        v0 = 0;
        sub_76040(&v1);
        v7 = v3;
        if (v7 + *(int *)&g_26f1fc8 * 16 + 16 > v2)
        {
            idx->field_8 = 0;
        }
        else
        {
            v8 = v7 + v1 + 15;
            v9 = v8 & 0xfffffffffffffff0;
            idx->field_8 = v9;
            if (v8 & 0xfffffffffffffff0)
            {
                *(int *)&idx->field_0 = *(int *)&g_26f1fc8;
                if ((unsigned long long)(*(int *)&g_26f1fc8 * 16) >= 101)
                {
LABEL_81639a:
                    sub_12aa7c0();
                    v6 = 1;
                }
                else
                {
                    v10 = g_26f1fc0;
                    if ((char)g_26f1fc0 & 3)
                        goto LABEL_81639a;
                    v6 = 1;
                    if (*(int *)&g_26f1fc8)
                    {
                        index = 0;
                        while (1)
                        {
                            v9[index] = v10[index];
                            if ((*(int *)&g_26f1fc8 & 0xfffffffffffffff) * 4 - 1 == index)
                                break;
                            index += 1;
                            v9 = idx->field_8;
                            v10 = g_26f1fc0;
                        }
                    }
                }
            }
        }
    }
    if (*(long long *)g_1a1f100 == v4)
        return v6;
    sub_12aa7f0();
    if (!g_295a878)
    {
        g_295a874 = 1086918619;
        *(unsigned long long *)&g_295a878 = 1;
    }
    if (!g_295a888)
    {
        g_295a880 = 1078530011;
        *(unsigned long long *)&g_295a888 = 1;
    }
    if (!g_295a898)
    {
        g_295a890 = 0x3fc90fdb;
        *(unsigned long long *)&g_295a898 = 1;
    }
    if (!g_295a8a8)
    {
        g_295a8a0 = 1061752795;
        *(unsigned long long *)&g_295a8a8 = 1;
    }
    if (!g_295a8b8)
    {
        g_295a8b0 = 1060439283;
        *(unsigned long long *)&g_295a8b8 = 1;
    }
    if (!g_295a8c8)
    {
        g_295a8c0 = 1060439283;
        *(unsigned long long *)&g_295a8c8 = 1;
    }
    if (g_295a8d8)
        goto LABEL_0x816500;
    g_295a8d0 = 0x3f000000;
    *(unsigned long long *)&g_295a8d8 = 1;
    if (!g_295a8e8)
        goto LABEL_0x81650c;
    else
        goto LABEL_0x816520;
}
