/* network_config_frame_update @ 0xadf6c0  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Calls 0xADEC40, derives 1000/config[+0x5A0+0x18] frame-time limit, resets stale 28-byte entries at mirror+0x6F8.
 */

extern char g_27bd1d0;

float sub_adf6c0(void)
{
    float v2;  // zmm0
    long long v3;  // rdi
    long long v4;  // rsi
    unsigned long v5;  // rax
    float v0;  // [bp-0xc]

    sub_adec40();
    sub_34e3b0();
    sub_afa990();
    *(unsigned int *)&v0 = 1000 / *(int *)(sub_34e3b0() + 24);
    v2 = *(float *)&*(int *)((unsigned long long)sub_34e3b0() + 176);
    if (v2 > v0)
    {
        sub_34e3b0();
        sub_2e41a0(1, 0);
    }
    sub_2e41a0(1, 0);
    sub_34e3b0(v3, v4);
    v5 = 0;
    do
    {
        if (*(int *)&(&g_27bd1d0)[1784 + v5] != 0xffffffff && (unsigned int)*(int *)&(&g_27bd1d0)[1784 + v5] >= 10)
            *(unsigned int *)&(&g_27bd1d0)[1784 + v5] = 0xffffffff;
    } while ((v5 += 28, (unsigned int)v5 != 560));
    return v2;
}
