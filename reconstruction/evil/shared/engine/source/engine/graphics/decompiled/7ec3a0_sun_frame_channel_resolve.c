/* sun_frame_channel_resolve @ 0x7ec3a0  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Resolves channel index g_18dcc54 = find_global_channel(0xE6AEB9EC).
 */
typedef struct st_7ec3a0_0 {
    unsigned long long field_0;
} st_7ec3a0_0;

extern unsigned int g_18dcc54;
extern st_7ec3a0_0 *g_1a1f100;
extern unsigned int g_26e4330;

long long sub_7ec3a0(void)
{
    unsigned int v0;  // [bp-0x20]
    unsigned long v1;  // [bp-0x18]

    v1 = *(long long *)g_1a1f100;
    v0 = g_26e4330;
    g_18dcc54 = sub_816240(&v0);
    if (*(long long *)g_1a1f100 != v1)
        return sub_12aa7f0();
    return *(long long *)g_1a1f100;
}
