/* frame_setup @ 0x80aa80  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Calls frame_extern_build with E=G+0xC (G=0x2709B28 exposure controller), 0.33*E, G+0x204/208/20C; allocates three 'light_sample_result' readbacks.
 */

typedef struct st_80aa80_0 {
    unsigned long long field_0;
} st_80aa80_0;

extern unsigned int g_fac70c;
extern st_80aa80_0 *g_1a1f100;
extern long long g_2709b28;
extern unsigned int g_2709b34;

long long sub_80aa80(void* idx)
{
    unsigned long long v16;  // r15
    unsigned long long v17;  // r14
    unsigned short *v18;  // rax
    unsigned long long index;  // rax
    long long v20;  // rdx
    long long v21;  // rcx
    void* v22;  // r14
    unsigned long v0;  // [bp-0x70]
    unsigned long v1;  // [bp-0x68]
    unsigned short *v2;  // [bp-0x60]
    unsigned int v3;  // [bp-0x5c]
    unsigned short *v4;  // [bp-0x58]
    unsigned short *v5;  // [bp-0x56]
    long long v6;  // [bp-0x52]
    unsigned int v7;  // [bp-0x50]
    unsigned int v8;  // [bp-0x4c]
    unsigned short *v9;  // [bp-0x48]
    unsigned short v10[4];  // [bp-0x40]
    long long v11;  // [bp-0x38]
    unsigned long v12;  // [bp-0x30]
    unsigned long long v13;  // [bp-0x18]
    unsigned long long v14;  // [bp-0x10]

    v14 = v16;
    v13 = v17;
    v12 = *(long long *)g_1a1f100;
    sub_802e50();
    *(unsigned int *)((char *)&v0 + 4) = g_2709b34;
    sub_844100(&g_2709b28);
    v18 = sub_807750(idx);
    *(unsigned short **)&idx[440] = v18;
    if (v18)
    {
        index = (long long)idx[8];
        v20 = *(long long *)(*(long long *)idx + 100688);
        v21 = *(long long *)(*(long long *)idx + 100696);
        *(long long *)(index + 5104) = v21;
        *(long long *)(index + 5096) = v20;
        sub_802e50(*(long long *)((long long)idx[8] + 5568), 1, v20, v21);
        v22 = idx + 496;
        sub_8408d0(v22, *(long long *)idx + 100688, *(long long *)idx + 102904, 208 + (long long)idx[24]);
        sub_8076a0(idx, v22);
        *(unsigned int *)v10 = 0;
        v11 = 1;
        wcsncpy(&v10[2], L"  ", 2);
        v1 = "light_sample_result";
        v2 = (unsigned short *)0;
        v5 = (unsigned short *)0;
        v6 = 1;
        v4 = (unsigned short *)0;
        v3 = 10;
        v7 = (unsigned int)&g_fac70c;
        v8 = (unsigned int)&g_fac70c;
        v9 = (unsigned short *)0;
        *(unsigned int *)&idx[292] = sub_818490(&v1);
        *(unsigned int *)v10 = 0;
        v11 = 1;
        wcsncpy(&v10[2], L"  ", 2);
        v1 = "light_sample_result";
        v2 = (unsigned short *)0;
        v5 = (unsigned short *)0;
        v6 = 1;
        v4 = (unsigned short *)0;
        v3 = 10;
        v7 = (unsigned int)&g_fac70c;
        v8 = (unsigned int)&g_fac70c;
        v9 = (unsigned short *)0;
        *(unsigned int *)&idx[296] = sub_818490(&v1);
        *(unsigned int *)v10 = 0;
        v11 = 1;
        wcsncpy(&v10[2], L"  ", 2);
        v1 = "light_sample_result";
        v2 = (unsigned short *)0;
        v5 = (unsigned short *)0;
        v6 = 1;
        v4 = (unsigned short *)0;
        v3 = 10;
        v7 = (unsigned int)&g_fac70c;
        v8 = (unsigned int)&g_fac70c;
        v9 = (unsigned short *)0;
        *(unsigned int *)&idx[300] = sub_818490(&v1);
        sub_80af40(idx, (long long)idx[440]);
        sub_80b070(idx); /* do not return */
    }
    else if (*(long long *)g_1a1f100 == v12)
    {
        return _INSERT(*(long long *)g_1a1f100, 0, 0);
    }
    else
    {
        return sub_12aa7f0();
    }
}
