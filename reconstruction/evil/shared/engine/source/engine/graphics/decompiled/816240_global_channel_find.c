/* global_channel_find @ 0x816240  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: find_global_channel(const u32* name_hash) -> index: linear search of the definition tag's hash array; -1 if absent. Name hash is FNV-1 32 (verified by preimages, e.g. 'sun_color' = 0x90745795).
 */
typedef struct st_816240_0 {
    unsigned long long field_0;
} st_816240_0;

extern st_816240_0 *g_1a238a0;
extern int g_26f1ff0;

unsigned int sub_816240(unsigned int *a0)
{
    int v1;  // eax
    unsigned long long v2;  // rcx
    unsigned long long v3;  // r10
    unsigned long v4;  // rax
    unsigned long v5;  // rsi
    void* v6;  // rdx
    unsigned long v7;  // rax

    if (g_26f1ff0 == -0x1)
        return 0xffffffff;
    v1 = g_26f1ff0 >> 13;
    v2 = (((unsigned int)(v1) >> 18 | 0x3ff) & v1) * 64;
    v3 = *(long long *)g_1a238a0;
    v4 = 0;
    v5 = *(int *)(v3 + v2 + 48) * (g_26f1ff0 & 0x1fff);
    v6 = *(long long *)(v3 + v2 + 16) + v5 - (*(int *)(v3 + v2 + 52) & *(long long *)(*(long long *)(v3 + v2 + 16) + v5 + 8));
    while (1)
    {
        v7 = v4;
        if ((long long)v7 >= (long long)v6[8])
            return 0xffffffff;
        v4 = v7 + 1;
        if (*a0 == *(int *)(v6[16] + (char *)v6 + 4 * v7 + 32))
            return (unsigned int)v7 - 0;
    }
}
