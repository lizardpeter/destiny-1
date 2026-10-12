/* global_channel_set @ 0x816170  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: set_global_channel(int index, const vec4* v): stores into g_26f1fc0[index] unless the bit in g_26f1fcc is set (then routes through 0x99f80 and zeroes).
 */
typedef struct st_816170_0 {
    unsigned long long field_0;
} st_816170_0;

extern char g_816237;
extern st_816170_0 *g_1a1f100;
extern char g_26f1fc0;
extern char g_26f1fc8;
extern unsigned int g_26f1fcc[4];

unsigned int sub_816170(unsigned int a0, uint128_t *a1)
{
    unsigned int v5;  // eax
    unsigned long v6;  // rbx
    unsigned int v7;  // eax
    char v8;  // dil
    unsigned int v0;  // [bp-0x158]
    uint128_t v1;  // [bp-0x38]
    uint128_t v2;  // [bp-0x28]
    unsigned long v3;  // [bp-0x18]

    v3 = *(long long *)g_1a1f100;
    v5 = _INSERT(0, 0, 0);
    if (*(long long *)&g_26f1fc0 && (int)a0 >= 0 && *(int *)&g_26f1fc8 > (int)a0)
    {
        v6 = *(long long *)&g_26f1fc0 + a0 * 16;
        v0 = g_26f1fcc[(int)(a0) >> 5];
        if ((char)(*((char *)&v0 + ((int)(a0 & 31) >> 3))) >> ((char)a0 & 31 & 7) & 1)
        {
            v2 = *a1 & 0xffffffffffffffff;
            v1 = 0;
            v5 = _INSERT(sub_99f80(&v2, &v1), 0, 1);
            *(uint128_t *)v6 = 0;
        }
        else
        {
            *(uint128_t *)v6 = *a1;
            v5 = _INSERT(v0, 0, 1);
        }
    }
    if (*(long long *)g_1a1f100 != v3)
    {
        v7 = sub_12aa7f0();
        g_816237 = v8;
        return v7;
    }
    return v5;
}
