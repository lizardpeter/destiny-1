/* renderer_frame_prepare @ 0x7ecbc0  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Renderer per-frame prepare; runs exposure controller update sub_843500(&G, renderer) among other per-frame updates.
 */

typedef struct st_7ecbc0_1 {
    unsigned long long field_0;
} st_7ecbc0_1;

typedef struct st_7ecbc0_2 {
    struct st_7ecbc0_1 *field_0;
} st_7ecbc0_2;

typedef struct st_7ecbc0_0 {
    char padding_0[36];
    unsigned int field_24;
} st_7ecbc0_0;

extern long long g_1052240;
extern char g_1949440;
extern long long g_19ee540;
extern st_7ecbc0_0 *g_2647d10;
extern char g_26c6fd8;
extern int g_26c7048;
extern unsigned int g_26e3ab4;
extern char g_2709890;
extern long long g_2709b28;
extern unsigned long long g_295c460;
extern char g_295c468;
extern char g_295c46c;
extern unsigned int g_295c470;
extern unsigned int g_295c474;
extern unsigned int g_295c478;
extern char g_295c47c;
extern char g_295c47d;
extern char g_295c480;
extern long long g_295ff40;
extern char g_2960080;

float sub_7ecbc0(void)
{
    long long *idx;  // rbx
    char v2;  // eax
    char v3;  // r14b
    long long v4;  // rdi
    long long v5;  // rsi
    st_7ecbc0_2 **v6;  // rax
    unsigned int v7;  // zmm0

    idx = sub_7eab70();
    if (!idx)
        return v7;
    *((char *)&idx[16259] + 1) = sub_833cb0();
    *(int *)&idx[12893] = *(int *)&(&g_26c6fd8)[12 + 56 * g_26c7048];
    sub_8162d0(idx + 12586, *idx);
    if (!g_295c480 && sub_12aa7d0(&g_295c480))
    {
        g_295c460 = &g_1949440;
        *(unsigned int *)&g_295c468 = 0;
        *(unsigned int *)&g_295c46c = 0;
        g_295c470 = 0xffffffff;
        g_295c474 = 0xffffffff;
        g_295c478 = 0x3f800000;
        g_295c47c = 0;
        g_295c47d = 0;
        sub_12aa7e0(&g_295c480);
    }
    if (g_295c47c)
        v2 = 0;
    else
        v2 = *(int *)&g_295c468;
    *(unsigned int *)((char *)&idx[13926] + 4) = v2;
    *(unsigned int *)&idx[13929] = g_2647d10->field_24;
    *(unsigned int *)((char *)&idx[13929] + 4) = sub_7da740();
    *((char *)&idx[13930] + 2) = g_26e3ab4 == 1;
    if (!g_2960080 && sub_12aa7d0(&g_2960080))
    {
        sub_1052310(&g_295ff40);
        sub_12aaa50(&g_1052240, &g_295ff40, &g_19ee540);
        sub_12aa7e0(&g_2960080);
    }
    sub_8ce410(&g_295ff40, idx);
    v3 = *(char *)(idx + "H");
    *(char *)&idx[13930] = (char)sub_1dad30(v4, v5) | (g_2709890 & v3) != 0;
    *(char *)(idx + "f") = (g_2709890 & v3) != 0;
    sub_84d4e0(idx);
    if ((char)sub_7cb5a0(v4))
    {
        v6 = sub_7cb590();
        (*(long long *)*v6)(v6);
    }
    sub_8afd10(idx);
    sub_8755b0(idx);
    sub_8a1f20(idx);
    sub_843500(&g_2709b28, idx);
    sub_8cfae0(idx);
    sub_804150(idx);
    sub_7ecad0(idx);
    idx[12539] = sub_7c7a10(*idx);
}
