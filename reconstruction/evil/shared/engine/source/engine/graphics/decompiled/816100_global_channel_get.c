/* global_channel_get @ 0x816100  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: get_global_channel(int index, vec4* out): bounds-checked read of g_26f1fc0[index]; returns false when out of range.
 */
typedef struct st_816100_0 {
    uint128_t field_0;
} st_816100_0;

extern st_816100_0 *g_26f1fc0;
extern char g_26f1fc8;

double sub_816100(uint128_t *a0, uint128_t *a1)
{
    uint128_t v1;  // xmm0

    if (g_26f1fc0 && a0 >= 0 && *(int *)&g_26f1fc8 > a0)
    {
        v1 = *(int128_t *)((char *)g_26f1fc0 + 0x10 * a0);
        *a1 = v1;
    }
    return *(unsigned long long *)&v1;
}
