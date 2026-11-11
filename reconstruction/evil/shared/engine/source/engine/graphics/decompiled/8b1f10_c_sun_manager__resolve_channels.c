/* c_sun_manager::resolve_channels @ 0x8b1f10  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Resolves 8 channel indices by FNV-1 hash: +0x8 sun_light_direction, +0xC sun_atmosphere_direction, +0x10 sun_ambient_direction, +0x14 0x7C61F53B, +0x18 0x38D8C873, +0x20 sun_intensity, +0x24 sun_shadow_intensity, +0x28 0xBEBDF937.
 */
typedef struct st_8b1f10_1 {
    char padding_0[44];
    unsigned int field_2c;
} st_8b1f10_1;

typedef struct st_8b1f10_0 {
    unsigned long long field_0;
} st_8b1f10_0;

extern st_8b1f10_0 *g_1a1f100;
extern unsigned int g_2736c34;
extern unsigned int g_2736c38;
extern unsigned int g_2736c3c;
extern unsigned int g_2736c40;
extern unsigned int g_2736c44;
extern unsigned int g_2736c48;
extern unsigned int g_2736c4c;
extern unsigned int g_2736c50;

unsigned long long sub_8b1f10(unsigned int *idx)
{
    unsigned long long v10;  // rax
    st_8b1f10_1 *index;  // rdi
    unsigned int v0;  // [bp-0x60]
    unsigned int v1;  // [bp-0x58]
    unsigned int v2;  // [bp-0x50]
    unsigned int v3;  // [bp-0x48]
    unsigned int v4;  // [bp-0x40]
    unsigned int v5;  // [bp-0x38]
    unsigned int v6;  // [bp-0x30]
    unsigned int v7;  // [bp-0x28]
    unsigned long v8;  // [bp-0x20]

    v8 = *(long long *)g_1a1f100;
    v7 = g_2736c34;
    idx[2] = sub_816240(&v7);
    v6 = g_2736c38;
    idx[3] = sub_816240(&v6);
    v5 = g_2736c3c;
    idx[4] = sub_816240(&v5);
    v4 = g_2736c44;
    idx[5] = sub_816240(&v4);
    v3 = g_2736c50;
    idx[10] = sub_816240(&v3);
    v2 = g_2736c40;
    idx[6] = sub_816240(&v2);
    v1 = g_2736c48;
    idx[8] = sub_816240(&v1);
    v0 = g_2736c4c;
    idx[9] = sub_816240(&v0);
    *(char *)&idx[12] = 1;
    *((char *)&idx[12] + 1) = 0;
    *((char *)&idx[12] + 2) = 0;
    idx[13] = 0;
    if (*(long long *)g_1a1f100 != v8)
    {
        v10 = sub_12aa7f0();
        index->field_2c = 0xffffffff;
        index[1].padding_0[0] = 0;
        index[1].padding_0[2] = 0;
        *(unsigned int *)&index[1].padding_0[4] = 0;
        return v10;
    }
    return *(long long *)g_1a1f100;
}
