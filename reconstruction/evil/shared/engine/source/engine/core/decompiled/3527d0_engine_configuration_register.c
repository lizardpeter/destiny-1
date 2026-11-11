/* engine_configuration_register @ 0x3527d0  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Registers named global block 'Engine Configuration' (0x3330 bytes, align 4) via sub_23e010 into g_2693DF8.
 */

extern unsigned long long g_100c8c0;
extern long long g_2693df8;

int sub_3527d0(void)
{
    unsigned int v0;  // [bp-0x28]
    unsigned int v1;  // [bp-0x20]
    unsigned long long v2;  // [bp-0x18]

    v2 = &g_100c8c0;
    v1 = 25;
    v0 = 0;
    return sub_23e010(&g_2693df8, "Engine Configuration", 0x3330, 4);
}
