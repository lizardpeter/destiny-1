/* global_channels_alloc @ 0x815420  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Allocates the 0x1000-byte global channel vec4 array g_26f1fc0 (heap tag 'Extracted global channel data'); clears handle g_26f1fec.
 */
extern unsigned long long g_26f1fc0;
extern long long g_26f1fec;

void sub_815420(void)
{
    char v0;  // [bp+0x0]

    g_26f1fc0 = sub_af600(0xffff, 1, 0x1000, 14, "Extracted global channel data", &g_26f1fec, &v0);
    return;
}
