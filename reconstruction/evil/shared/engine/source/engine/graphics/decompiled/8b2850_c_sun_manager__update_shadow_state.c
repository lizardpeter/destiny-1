/* c_sun_manager::update_shadow_state @ 0x8b2850  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Picks sun shadow mode renderer+0x18920 (0..3) from sun_intensity/sun_shadow_intensity; zeroes sun_intensity, sun_shadow_intensity and channel 0xBEBDF937 when disabled.
 */
typedef struct st_8b2850_0 {
    unsigned long long field_0;
} st_8b2850_0;

extern st_8b2850_0 *g_1a1f100;

long long sub_8b2850(unsigned int *a0, unsigned long idx)
{
    unsigned int v9;  // eax
    float v0;  // [bp-0x78]
    float v1;  // [bp-0x68]
    float v2;  // [bp-0x58]
    char v3;  // [bp-0x48]
    char v5;  // [bp-0x38]
    unsigned long v7;  // [bp-0x28]

    v7 = *(long long *)g_1a1f100;
    sub_816100(a0[8], &v5);
    sub_816100(a0[9], &v3);
    if (0.0f < v5)
    {
        if (*(char *)(idx + 100645))
        {
            *(unsigned int *)(idx + 100640) = 1;
            v9 = 1;
        }
        else if (0.0f < v3)
        {
            *(unsigned int *)(idx + 100640) = 3;
            v9 = 3;
        }
        else
        {
            *(unsigned int *)(idx + 100640) = 2;
            v9 = 2;
        }
        *(char *)(idx + 100646) = 1;
        *(unsigned int *)(idx + 100652) = 2;
    }
    else
    {
        *(unsigned int *)(idx + 100640) = 0;
        *(char *)(idx + 100646) = 1;
        *(unsigned int *)(idx + 100652) = 2;
        v2 = (float)0;
        sub_816170(a0[8], &v2);
        v9 = *(int *)(idx + 100640);
    }
    if (v9 != 3)
    {
        v1 = (float)0;
        sub_816170(a0[9], &v1);
    }
    if (*(char *)(idx + 111440))
    {
        v0 = (float)0;
        sub_816170(a0[10], &v0);
    }
    if (*(long long *)g_1a1f100 != v7)
    {
        sub_12aa7f0();
        return sub_816100();
    }
    return *(long long *)g_1a1f100;
}
