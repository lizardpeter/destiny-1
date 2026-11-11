/* global_channels_free @ 0x815460  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Releases g_26f1fc0 and resets count g_26f1fc8 / handle g_26f1fec.
 */
extern unsigned long long g_26f1fc0;
extern unsigned int g_26f1fc8;
extern unsigned short g_26f1fec;
extern unsigned int g_26f1ff0;

unsigned int * sub_815460(void)
{
    unsigned long long v2;  // rax
    unsigned long v3;  // rdi
    unsigned long long v0;  // [bp-0x18]

    v0 = v2;
    v3 = _INSERT(0, 0, g_26f1fec);
    if ((unsigned short)v3 != 0xffff)
    {
        sub_af8f0(v3);
        g_26f1fec = 0xffff;
    }
    g_26f1fc0 = 0;
    g_26f1fc8 = 0;
    g_26f1ff0 = 0xffffffff;
    return &g_26f1ff0;
}
