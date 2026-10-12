/* render_context_reset @ 0x822270  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Sets ctx+0x15C0/0x15C8; when resetting clears extern table (0x288), arena (0x1004), undo list (0xFF x 384) and state at +0x13D8..+0x15D4.
 */


long long sub_822270(long long idx, long long a1, unsigned long a2, char a3)
{
    long long v2;  // rax
    long long v3;  // rax
    long long v0;  // [bp-0x18]

    v0 = v2;
    *(unsigned long *)(idx + 5576) = a2;
    *(long long *)(idx + 5568) = a1;
    if (!a1)
    {
        return v2;
    }
    else if (!(a3 ^ 1))
    {
        sub_12aa980(idx + 4104, 0, 648);
        sub_12aa980(idx, 0, 0x1004);
        sub_12aa980(idx + 5160, 0xff, 384);
        *(unsigned long long *)(idx + 5544) = 0;
        v3 = idx + 5552;
        *(unsigned int *)(v3 + 8) = 0;
        *(unsigned long long *)v3 = 0;
        *(unsigned int *)(idx + 5080) = 0;
        *(unsigned long long *)(idx + 5088) = 0;
        *(unsigned int *)(idx + 5584) = 0;
        *(unsigned int *)(idx + 5588) = 0;
        *(unsigned int *)(idx + 5096) = 0;
        *(unsigned long long *)(idx + 5104) = 0;
        return v3;
    }
    else
    {
        return v2;
    }
}
