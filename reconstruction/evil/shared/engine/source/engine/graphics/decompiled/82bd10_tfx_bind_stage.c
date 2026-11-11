/* tfx_bind_stage @ 0x82bd10  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Per shader stage: copy constants into cbuffer from ctx+0x15C0 allocator, run tfx_vm_execute when bytecode size>0, then 0x82BE10 resource bind. ~110 callers in render features (VS/PS pairs).
 */

typedef struct st_82bd10_0 {
    char padding_0[24];
    long long field_18;
    char padding_20[40];
    unsigned long long field_48;
    char padding_50[32];
    unsigned int field_70;
} st_82bd10_0;


char sub_82bd10(long long a0, unsigned int a1, st_82bd10_0 *index)
{
    unsigned long long v2;  // rax
    unsigned int v3;  // eax
    long long v4;  // rbx
    unsigned int *v5;  // r13
    char v6;  // rsi
    char v7;  // rbx
    char idx;  // rax
    unsigned long long v0;  // [bp-0x38]

    v0 = v2;
    v3 = sub_7e2c90(a1);
    if ((int)index->field_48 > 0)
    {
        v4 = (long long)(index->field_48 * 0x100000000) >> 28;
        v5 = sub_7df630(*(long long *)(a0 + 5568), v3, index->field_70, v4 & 0xffffffff);
        v6 = 0;
        if (*(long long *)&index->padding_50[0])
            v6 = (char)(struct st_82bd10_0 *)&index->padding_50[*(long long *)&index->padding_50[0] + 16];
        if ((unsigned long long)v4 >= 101 || v5 & 0x3 || v6 & 3)
        {
            sub_12aa7c0(v5);
        }
        else
        {
            v7 = (unsigned long long)(v4) >> 2;
            if (v7)
            {
                idx = 0;
                do
                {
                    v5[idx] = *(int *)(v6 + idx * 4);
                    idx += 1;
                } while (idx < v7);
            }
        }
    }
    if (index->field_18 > 0)
        sub_829300(a0);
    sub_82be10(a0, a1, index);
    return 1;
}
