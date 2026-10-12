/* tfx_extern_alloc @ 0x82b940  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: void* (ctx, uint id, size): bump-allocate 16-aligned block in ctx arena (cursor ctx+0x1000), slot[id]=ctx+0x1008+id*8, size ctx+0x1290+id*4, push undo {id,prev_ptr,prev_size} at ctx+0x1428 (count ctx+0x15A8), zero-fill, set dirty bit ctx+0x15B0. 131 callers.
 */


long long sub_82b940(unsigned long idx, unsigned int a1, unsigned long long a2)
{
    unsigned long long v2;  // rax
    unsigned long v3;  // r14
    unsigned int v4;  // ecx
    unsigned long v5;  // rdi
    unsigned int v6;  // eax
    unsigned long long v7;  // rsi
    unsigned long v8;  // r14
    unsigned long long v0;  // [bp-0x28]

    v0 = v2;
    v3 = *(int *)(idx + 0x1000);
    v4 = (unsigned int)a2 + 15 & 0xfffffff0;
    *(unsigned int *)(idx + 0x1000) = (unsigned int)v3 + v4;
    v5 = a1;
    v6 = *(int *)(idx + v5 * 4 + 4752);
    v7 = *(long long *)(idx + v5 * 8 + 4104);
    v8 = v3 + idx;
    *(unsigned long *)(idx + v5 * 8 + 4104) = v8;
    *(unsigned int *)(idx + v5 * 4 + 4752) = v4;
    *(unsigned int *)(idx + *(int *)(idx + 5544) * 24 + 5160) = v5;
    *(unsigned long long *)(idx + *(int *)(idx + 5544) * 24 + 5168) = v7;
    *(unsigned int *)(idx + *(int *)(idx + 5544) * 24 + 5176) = v6;
    *(int *)(idx + 5544) = *(int *)(idx + 5544) + 1;
    if (a2 < 33 && !(v8 & 3) && !(a2 & 3) && a2 <= 3)
    {
        *(unsigned int *)(idx + ((int)(a1) >> 5) * 4 + 5552) = *(int *)(idx + ((int)(a1) >> 5) * 4 + 5552) | (unsigned int)(1 << ((char)a1 & 31));
        return v8;
    }
    sub_12aa980(v8, 0);
    *(unsigned int *)(idx + ((int)(a1) >> 5) * 4 + 5552) = *(int *)(idx + ((int)(a1) >> 5) * 4 + 5552) | (unsigned int)(1 << ((char)a1 & 31));
    return v8;
}
