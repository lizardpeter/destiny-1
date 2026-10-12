/* lighting_frame_update @ 0x7ebfc0  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Per-frame lighting-globals driver: global channel update passes, sets channel g_18dcc54 (hash 0xE6AEB9EC, name unknown) from a virtual getter, then runs c_sun_manager update_directions / update_intensity / update_shadow.
 */
typedef struct st_7ebfc0_5 {
    char padding_0[1248];
    unsigned int field_4e0;
} st_7ebfc0_5;

typedef struct st_7ebfc0_2 {
    char padding_0[32];
    struct st_7ebfc0_0 *field_20;
} st_7ebfc0_2;

typedef struct st_7ebfc0_0 {
    unsigned long long field_0;
} st_7ebfc0_0;

typedef struct st_7ebfc0_4 {
    struct st_7ebfc0_2 *field_0;
} st_7ebfc0_4;

extern unsigned int g_18dcc54;
extern char g_1949560;
extern st_7ebfc0_0 *g_1a1f100;
extern unsigned int g_26e3d90;
extern unsigned long long g_29600a0;
extern st_7ebfc0_4 *g_2960100;

float sub_7ebfc0(st_7ebfc0_0 **a0)
{
    long long *v13;  // r14
    unsigned int v14;  // ebx
    long long v15;  // rdi
    st_7ebfc0_2 **v16;  // rax
    long long v17;  // rsi
    st_7ebfc0_5 *v18;  // rbx
    char v0;  // [bp-0x518]
    st_7ebfc0_2 **v1;  // [bp-0x504]
    unsigned long v2;  // [bp-0x4e8]
    st_7ebfc0_5 *v3;  // [bp-0x4d8]
    long long *v4;  // [bp-0x4d0]
    char *v5;  // [bp-0x4c8]
    char *v6;  // [bp-0x4c0]
    uint128_t v7;  // [bp-0x4b8]
    char v8;  // [bp-0x4a8]
    char v9;  // [bp-0x478]
    unsigned long v10;  // [bp-0x28]
    char v11;  // [bp-0x8]

    v10 = *(long long *)g_1a1f100;
    v13 = *a0;
    sub_88fb20((char *)&v13[12893] + 4, (char *)&v13[12894] + 4);
    if (!(char)g_2960100 && sub_12aa7d0(&g_2960100))
    {
        g_29600a0 = &g_1949560;
        sub_12aa7e0(&g_2960100);
    }
    sub_815600();
    sub_815f40(v13);
    sub_815790(v13);
    v14 = g_26e3d90;
    v16 = sub_25a3b0(v15);
    if (v16)
        v14 = *v16->field_20(v16);
    g_26e3d90 = v14;
    v7 = CONCAT(CONCAT(__float_as_int((float)(double)(unsigned long long)v14), __float_as_int((float)(double)(unsigned long long)v14)), CONCAT(__float_as_int((float)(double)(unsigned long long)v14), __float_as_int((float)(double)(unsigned long long)v14)));
    sub_816170(g_18dcc54, &v7);
    sub_8b2020(&g_29600a0, v13);
    sub_8b23f0(&g_29600a0, v13);
    sub_8b2850(&g_29600a0, v13);
    sub_802e50(v15, v17);
    sub_7ca8b0();
    sub_80e630(&v9);
    sub_810bc0(&v8);
    v18 = v13[16266];
    sub_810c80(&v8, &v18->padding_0[16]);
    if (v18->field_4e0 != 7)
        sub_88c400(&v8, v13, v18);
    sub_88ca60(v13, *v13);
    sub_8b5010(v13);
    if (*(long long *)g_1a1f100 == v10)
        return (float)(double)v14;
    sub_12aa7f0();
    v6 = &v11;
    v5 = &v8;
    v4 = v13;
    v3 = v18;
    v2 = *(long long *)g_1a1f100;
    v1 = (st_7ebfc0_2 **)0;
    sub_8326e0(&v0, &v1);
}
