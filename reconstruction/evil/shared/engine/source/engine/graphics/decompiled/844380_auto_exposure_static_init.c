/* auto_exposure_static_init @ 0x844380  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: C++ static ctor for G=0x2709B28: E=0, history=-3.0, config 1,1,0,-3.0,0.25,-1.0,1.0,0.01,0.9,6,0.05,0.05.
 */

extern unsigned int g_2709b28;
extern unsigned int g_2709b2c;
extern unsigned int g_2709b30;
extern unsigned int g_2709b34;
extern unsigned int g_2709b38;
extern unsigned int g_2709b3c;
extern long long g_2709b48;
extern unsigned int g_2709d28;
extern unsigned int g_2709d2c;
extern unsigned int g_2709d30;
extern unsigned int g_2709d34;
extern char g_2709d40;
extern char g_2709d41;
extern char g_2709d42;
extern unsigned int g_2709d44;
extern unsigned int g_2709d48;
extern unsigned int g_2709d4c;
extern unsigned int g_2709d50;
extern unsigned int g_2709d54;
extern unsigned int g_2709d58;
extern unsigned int g_2709d5c;
extern unsigned int g_2709d60;
extern unsigned int g_2709d64;
extern char g_2709d68;
extern unsigned int g_2709d74;
extern unsigned int g_2709d78;
extern unsigned int g_2709d7c;
extern unsigned int g_2709d80;
extern unsigned int g_295a874;
extern void g_295a878;
extern unsigned int g_295a880;
extern unsigned long long g_295a888;
extern unsigned int g_295a890;
extern unsigned long long g_295a898;
extern unsigned int g_295a8a0;
extern unsigned long long g_295a8a8;
extern unsigned int g_295a8b0;
extern unsigned long long g_295a8b8;
extern unsigned int g_295a8c0;
extern unsigned long long g_295a8c8;
extern unsigned int g_295a8d0;
extern unsigned long long g_295a8d8;
extern unsigned int g_295a8e0;
extern unsigned long long g_295a8e8;
extern unsigned int g_295a8f0;
extern unsigned long long g_295a8f8;
extern unsigned int g_295a900;
extern unsigned long long g_295a908;

int sub_844380(void)
{
    unsigned long long v2;  // rax
    unsigned int v3;  // eax
    unsigned long long v0;  // [bp-0x18]

    v0 = v2;
    if (!g_295a878)
    {
        g_295a874 = 1086918619;
        *(unsigned long long *)&g_295a878 = 1;
    }
    if (!(char)g_295a888)
    {
        g_295a880 = 1078530011;
        g_295a888 = 1;
    }
    if (!(char)g_295a898)
    {
        g_295a890 = 0x3fc90fdb;
        g_295a898 = 1;
    }
    if (!(char)g_295a8a8)
    {
        g_295a8a0 = 1061752795;
        g_295a8a8 = 1;
    }
    if (!(char)g_295a8b8)
    {
        g_295a8b0 = 1060439283;
        g_295a8b8 = 1;
    }
    if (!(char)g_295a8c8)
    {
        g_295a8c0 = 1060439283;
        g_295a8c8 = 1;
    }
    if (!(char)g_295a8d8)
    {
        g_295a8d0 = 0x3f000000;
        g_295a8d8 = 1;
    }
    if (!(char)g_295a8e8)
    {
        g_295a8e0 = 1063105495;
        g_295a8e8 = 1;
    }
    if (!(char)g_295a8f8)
    {
        g_295a8f0 = 0x3fcf1bbd;
        g_295a8f8 = 1;
    }
    if (!(char)g_295a908)
    {
        g_295a900 = 1058944890;
        g_295a908 = 1;
    }
    g_2709d74 = 617897721;
    g_2709d78 = 3968759000;
    g_2709d7c = 2961144874;
    g_2709d80 = 413164828;
    g_2709d40 = 1;
    g_2709d41 = 1;
    g_2709d42 = 0;
    g_2709d44 = 0xc0400000;
    g_2709d48 = 1048576000;
    g_2709d4c = 0xbf800000;
    g_2709d50 = 0x3f800000;
    g_2709d54 = 1008981770;
    g_2709d58 = 1063675494;
    g_2709d5c = 6;
    g_2709d60 = 1028443341;
    g_2709d64 = 1028443341;
    g_2709d68 = 0;
    g_2709d28 = 0;
    g_2709b34 = 0;
    g_2709b38 = 0;
    g_2709b3c = 0;
    v3 = sub_12aa980(&g_2709b48, 0, 240);
    g_2709d2c = 0xc0400000;
    g_2709d30 = 0xc0400000;
    g_2709d34 = 0xc0400000;
    g_2709b28 = 0;
    g_2709b2c = 0;
    g_2709b30 = 0;
    return v3;
}
