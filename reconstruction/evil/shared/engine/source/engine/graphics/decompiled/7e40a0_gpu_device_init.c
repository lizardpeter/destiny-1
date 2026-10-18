
/* WARNING: Removing unreachable block (ram,0x007e413a) */
/* WARNING: Removing unreachable block (ram,0x007e415a) */
/* WARNING: Removing unreachable block (ram,0x007e417a) */
/* WARNING: Removing unreachable block (ram,0x007e4198) */
/* WARNING: Removing unreachable block (ram,0x007e41b8) */
/* WARNING: Removing unreachable block (ram,0x007e41d8) */
/* WARNING: Removing unreachable block (ram,0x007e41f8) */
/* WARNING: Removing unreachable block (ram,0x007e4218) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_007e40a0(long *param_1,long param_2)

{
  long *plVar1;
  long *plVar2;
  int iVar3;
  undefined2 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  ulong uVar10;
  long lVar11;
  long lVar12;
  long lVar13;
  uint uVar14;
  ulong uVar15;
  undefined4 uVar16;
  uint6 local_d8;
  undefined1 local_d0 [4];
  undefined4 local_cc;
  undefined1 local_c8 [40];
  uint *local_a0;
  undefined8 local_98;
  undefined4 local_90;
  ulong local_78;
  ulong local_70;
  ulong local_68;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  DAT_026e2e88 = param_1;
  *(undefined4 *)(param_1 + 0x51f) = 0x780;
  *(undefined4 *)((long)param_1 + 0x28fc) = 0x438;
  *param_1 = param_2;
  *(undefined4 *)(param_1 + 5) = 0;
  if (DAT_026e2cdc == 0) {
    thunk_FUN_012aa986(&DAT_026e2c08,0,0xd8);
    _DAT_026e2cb8 = 10;
    LOCK();
    DAT_026e2c08 = 0;
    UNLOCK();
    LOCK();
    DAT_026e2c10 = 0;
    UNLOCK();
    LOCK();
    DAT_026e2c18 = 0;
    UNLOCK();
    LOCK();
    DAT_026e2c20 = 0;
    UNLOCK();
    LOCK();
    DAT_026e2cd0 = 0;
    UNLOCK();
    LOCK();
    DAT_026e2cd4 = 0;
    UNLOCK();
    LOCK();
    DAT_026e2cd8 = 0;
    UNLOCK();
    LOCK();
    DAT_026e2cdc = 1;
    UNLOCK();
  }
  *(undefined8 *)((long)param_1 + 0x25ac) = 0x100000003;
  uVar5 = FUN_00f7d5a0(3);
  uVar6 = FUN_00f8a990();
  uVar8 = FUN_000b48f0(uVar6,0xe);
  uVar9 = FUN_000b48f0(uVar6,0xe);
  *(undefined4 *)(*param_1 + 0x132e0) = 0;
  *(undefined4 *)(*param_1 + 0x132e4) = 0;
  *(undefined4 *)(*param_1 + 0x132e8) = 0;
  *(undefined4 *)(*param_1 + 0xb8) = 0;
  *(undefined4 *)(*param_1 + 0xbc) = 0;
  lVar12 = *param_1;
  uVar6 = thunk_FUN_000f6b70(&PTR_s_cs_async_command_buffer_flush_01947f08);
  *(undefined4 *)(lVar12 + 0x2d4) = uVar6;
  *(undefined4 *)(*param_1 + 0x2cc) = 0;
  *(undefined4 *)(*param_1 + 0x2c8) = 0;
  *(undefined4 *)(*param_1 + 0x2d0) = 0;
  thunk_FUN_012aa986(*param_1 + 200,0,0x200);
  FUN_000f6550();
  lVar13 = 0;
  FUN_00f8eba0(param_1 + 0xc,uVar8,*(undefined8 *)(param_2 + 8),*(undefined4 *)(param_2 + 0x18),0,0,
               0,0);
  uVar15 = 0;
  FUN_00f8eba0(param_1 + 0x1d8,uVar9,*(undefined8 *)(param_2 + 0x10),*(undefined4 *)(param_2 + 0x18)
               ,0,0,0,0);
  FUN_00f859b0(&local_cc,1,0xf2e00a,1);
  FUN_00f859b0(local_d0,4,uVar5,1);
  iVar7 = *(int *)((long)param_1 + 0x28fc);
  uVar14 = *(uint *)(param_1 + 0x51f);
  FUN_007ed1c0(&local_d8);
  uVar14 = uVar14 & 0xffff | iVar7 << 0x10;
  FUN_008180f0(param_1,(ulong)local_d8,uVar14,uVar14);
  plVar1 = param_1 + 0x50c;
  uVar15 = uVar15 & 0xffffffff00000000;
  uVar5 = FUN_00f81f80(plVar1,(int)param_1[0x51f],*(undefined4 *)((long)param_1 + 0x28fc),1,0xf2e00a
                       ,local_cc,uVar15,0,0,0);
  uVar10 = FUN_000b4a60(uVar5,0xe);
  local_78 = uVar10;
  thunk_FUN_012aa986(uVar10,0xff,uVar5);
  FUN_00c2e290(plVar1,uVar10 >> 8 & 0xffffffff);
  FUN_00f82aa0(plVar1,0);
  FUN_00417af0(plVar1,0);
  lVar12 = (long)param_1 + 0x288c;
  uVar15 = uVar15 & 0xffffffff00000000;
  uVar5 = FUN_00f81f80(lVar12,(int)param_1[0x51f],*(undefined4 *)((long)param_1 + 0x28fc),1,0xf2e00a
                       ,local_cc,uVar15,0,0,0);
  uVar10 = FUN_000b4a60(uVar5,0xe);
  local_70 = uVar10;
  thunk_FUN_012aa986(uVar10,0xff,uVar5);
  FUN_00c2e290(lVar12,uVar10 >> 8 & 0xffffffff);
  FUN_00f82aa0(lVar12,0);
  FUN_00417af0(lVar12,0);
  plVar2 = param_1 + 0x517;
  uVar15 = uVar15 & 0xffffffff00000000;
  uVar5 = FUN_00f81f80(plVar2,(int)param_1[0x51f],*(undefined4 *)((long)param_1 + 0x28fc),1,0xf2e00a
                       ,local_cc,uVar15,0,0,0);
  uVar6 = (undefined4)(uVar15 >> 0x20);
  uVar10 = FUN_000b4a60(uVar5,0xe);
  local_68 = uVar10;
  thunk_FUN_012aa986(uVar10,0xff,uVar5);
  FUN_00c2e290(plVar2,uVar10 >> 8 & 0xffffffff);
  FUN_00f82aa0(plVar2,0);
  FUN_00417af0(plVar2,0);
  *(undefined4 *)(*param_1 + 0xb0) = 0;
  *(undefined1 *)((long)param_1 + 0x28e4) = 0;
  uVar5 = thunk_FUN_012aba96(0xff,0,0,0);
  *(undefined4 *)(*param_1 + 0x80) = uVar5;
  if (*(int *)(*param_1 + 0x80) < 0) {
    if (DAT_01a231f0 == (code *)0x0) {
      FUN_0005c750(s_ORBIS__failed_to_open_a_valid_co_0165ff1a,*(int *)(*param_1 + 0x80));
      s__libexec_ld_elf_so_1_00000000[1] = '*';
      s__libexec_ld_elf_so_1_00000000[2] = '\0';
      s__libexec_ld_elf_so_1_00000000[3] = '\0';
      s__libexec_ld_elf_so_1_00000000[4] = '\0';
    }
    else {
      (*DAT_01a231f0)(0,s_ORBIS__failed_to_open_a_valid_co_0165ff1a);
    }
  }
  thunk_FUN_012abaa6(*param_1 + 0xa0,s_eq_to_wait_flip_0165ff59);
  thunk_FUN_012ac616(*(undefined8 *)(*param_1 + 0xa0),0x40,0);
  thunk_FUN_012abab6(*(undefined8 *)(*param_1 + 0xa0),*(undefined4 *)(*param_1 + 0x80),0);
  *(undefined4 *)(*param_1 + 0x94) = 0;
  *(undefined4 *)(*param_1 + 0x98) = 3;
  *(undefined4 *)(*param_1 + 0xa8) = 1;
  uVar8 = CONCAT44(uVar6,(int)param_1[0x51f]);
  thunk_FUN_012abac6(&local_a0,0x80000000,0,0,(int)param_1[0x51f],
                     *(undefined4 *)((long)param_1 + 0x28fc),uVar8);
  uVar16 = (undefined4)((ulong)uVar8 >> 0x20);
  thunk_FUN_012aba66(*(undefined4 *)(*param_1 + 0x80),1);
  uVar5 = FUN_00263ef0(plVar1);
  uVar6 = FUN_00f82690(plVar1);
  iVar7 = FUN_00f82ad0(plVar1);
  thunk_FUN_012abac6(local_c8,0x80000000,0,0,uVar5,uVar6,CONCAT44(uVar16,iVar7 * 8 + 8));
  thunk_FUN_012abad6(*(undefined4 *)(*param_1 + 0x80),0,&local_78,3,local_c8);
  uVar8 = FUN_000b4a60(0x20000,0xe);
  *(undefined8 *)*param_1 = uVar8;
  do {
    *(short *)(*(long *)*param_1 + lVar13 * 2) = (short)lVar13;
    lVar13 = lVar13 + 1;
  } while ((int)lVar13 != 0x10000);
  uVar4 = FUN_000b0730(1,0x94,0xa0,0xe,s_ORBIS_vertex_stream_layouts_0165ff69);
  *(undefined2 *)((long)param_1 + 0x28e6) = uVar4;
  param_1[8] = 0;
  param_1[9] = 0;
  *(undefined4 *)(param_1 + 4) = 0x3f800000;
  *(undefined1 *)((long)param_1 + 0x24) = 1;
  *(undefined1 *)((long)param_1 + 0x25) = 0;
  *(undefined8 *)((long)param_1 + 0x2c) = 0xffffffffffffffff;
  uVar8 = FUN_007e4fd0(&LAB_018e0fb8);
  *(undefined8 *)(*param_1 + 0x20) = uVar8;
  FUN_00f8e910(&local_a0,&DAT_018e10c4);
  uVar14 = (uint)(byte)local_a0[0xe] * 2 + 0x3f + (*local_a0 >> 0x18) * 4 & 0xfffffffc;
  lVar13 = FUN_000b49b0(uVar14,0xe);
  uVar5 = local_90;
  lVar12 = lVar13;
  if (lVar13 != 0) {
    lVar11 = FUN_000b4a60(local_90,0xe);
    lVar12 = 0;
    if (lVar11 != 0) {
      thunk_FUN_012aa986(lVar13,0,uVar14);
      thunk_FUN_012aa7c6(lVar13,local_a0,uVar14);
      thunk_FUN_012aa986(lVar11,0,uVar5);
      thunk_FUN_012aa7c6(lVar11,local_98,local_90);
      *(int *)(lVar13 + 8) = (int)((ulong)lVar11 >> 8);
      *(uint *)(lVar13 + 0xc) = (uint)((ulong)lVar11 >> 0x28);
      lVar12 = lVar13;
    }
  }
  *(long *)(*param_1 + 0x28) = lVar12;
  FUN_00f8e910(&local_a0,&DAT_018e1248);
  uVar14 = (uint)(byte)local_a0[0xe] * 2 + 0x3f + (*local_a0 >> 0x18) * 4 & 0xfffffffc;
  lVar13 = FUN_000b49b0(uVar14,0xe);
  uVar5 = local_90;
  lVar12 = lVar13;
  if (lVar13 != 0) {
    lVar11 = FUN_000b4a60(local_90,0xe);
    lVar12 = 0;
    if (lVar11 != 0) {
      thunk_FUN_012aa986(lVar13,0,uVar14);
      thunk_FUN_012aa7c6(lVar13,local_a0,uVar14);
      thunk_FUN_012aa986(lVar11,0,uVar5);
      thunk_FUN_012aa7c6(lVar11,local_98,local_90);
      *(int *)(lVar13 + 8) = (int)((ulong)lVar11 >> 8);
      *(uint *)(lVar13 + 0xc) = (uint)((ulong)lVar11 >> 0x28);
      lVar12 = lVar13;
    }
  }
  *(long *)(*param_1 + 0x30) = lVar12;
  FUN_00f8e910(&local_a0,&DAT_018e1410);
  uVar14 = (uint)(byte)local_a0[0xe] * 2 + 0x3f + (*local_a0 >> 0x18) * 4 & 0xfffffffc;
  lVar13 = FUN_000b49b0(uVar14,0xe);
  uVar5 = local_90;
  lVar12 = lVar13;
  if (lVar13 != 0) {
    lVar11 = FUN_000b4a60(local_90,0xe);
    lVar12 = 0;
    if (lVar11 != 0) {
      thunk_FUN_012aa986(lVar13,0,uVar14);
      thunk_FUN_012aa7c6(lVar13,local_a0,uVar14);
      thunk_FUN_012aa986(lVar11,0,uVar5);
      thunk_FUN_012aa7c6(lVar11,local_98,local_90);
      *(int *)(lVar13 + 8) = (int)((ulong)lVar11 >> 8);
      *(uint *)(lVar13 + 0xc) = (uint)((ulong)lVar11 >> 0x28);
      lVar12 = lVar13;
    }
  }
  *(long *)(*param_1 + 0x38) = lVar12;
  FUN_00f8e910(&local_a0,&DAT_018e1614);
  uVar14 = (uint)(byte)local_a0[0xe] * 2 + 0x3f + (*local_a0 >> 0x18) * 4 & 0xfffffffc;
  lVar13 = FUN_000b49b0(uVar14,0xe);
  uVar5 = local_90;
  lVar12 = lVar13;
  if (lVar13 != 0) {
    lVar11 = FUN_000b4a60(local_90,0xe);
    lVar12 = 0;
    if (lVar11 != 0) {
      thunk_FUN_012aa986(lVar13,0,uVar14);
      thunk_FUN_012aa7c6(lVar13,local_a0,uVar14);
      thunk_FUN_012aa986(lVar11,0,uVar5);
      thunk_FUN_012aa7c6(lVar11,local_98,local_90);
      *(int *)(lVar13 + 8) = (int)((ulong)lVar11 >> 8);
      *(uint *)(lVar13 + 0xc) = (uint)((ulong)lVar11 >> 0x28);
      lVar12 = lVar13;
    }
  }
  *(long *)(*param_1 + 0x40) = lVar12;
  uVar8 = FUN_007e4fd0(&LAB_018e185c);
  *(undefined8 *)(*param_1 + 0x48) = uVar8;
  FUN_00f8e910(&local_a0,&DAT_018e1968);
  uVar14 = (uint)(byte)local_a0[0xe] * 2 + 0x3f + (*local_a0 >> 0x18) * 4 & 0xfffffffc;
  lVar13 = FUN_000b49b0(uVar14,0xe);
  uVar5 = local_90;
  lVar12 = lVar13;
  if (lVar13 != 0) {
    lVar11 = FUN_000b4a60(local_90,0xe);
    lVar12 = 0;
    if (lVar11 != 0) {
      thunk_FUN_012aa986(lVar13,0,uVar14);
      thunk_FUN_012aa7c6(lVar13,local_a0,uVar14);
      thunk_FUN_012aa986(lVar11,0,uVar5);
      thunk_FUN_012aa7c6(lVar11,local_98,local_90);
      *(int *)(lVar13 + 8) = (int)((ulong)lVar11 >> 8);
      *(uint *)(lVar13 + 0xc) = (uint)((ulong)lVar11 >> 0x28);
      lVar12 = lVar13;
    }
  }
  *(long *)(*param_1 + 0x50) = lVar12;
  FUN_00f8e910(&local_a0,&DAT_018e1aa4);
  uVar14 = (uint)(byte)local_a0[0xe] * 2 + 0x3f + (*local_a0 >> 0x18) * 4 & 0xfffffffc;
  lVar13 = FUN_000b49b0(uVar14,0xe);
  uVar5 = local_90;
  lVar12 = lVar13;
  if (lVar13 != 0) {
    lVar11 = FUN_000b4a60(local_90,0xe);
    lVar12 = 0;
    if (lVar11 != 0) {
      thunk_FUN_012aa986(lVar13,0,uVar14);
      thunk_FUN_012aa7c6(lVar13,local_a0,uVar14);
      thunk_FUN_012aa986(lVar11,0,uVar5);
      thunk_FUN_012aa7c6(lVar11,local_98,local_90);
      *(int *)(lVar13 + 8) = (int)((ulong)lVar11 >> 8);
      *(uint *)(lVar13 + 0xc) = (uint)((ulong)lVar11 >> 0x28);
      lVar12 = lVar13;
    }
  }
  *(long *)(*param_1 + 0x60) = lVar12;
  FUN_00f8e910(&local_a0,&DAT_018e1be0);
  uVar14 = (uint)(byte)local_a0[0xe] * 2 + 0x3f + (*local_a0 >> 0x18) * 4 & 0xfffffffc;
  lVar13 = FUN_000b49b0(uVar14,0xe);
  uVar5 = local_90;
  lVar12 = lVar13;
  if (lVar13 != 0) {
    lVar11 = FUN_000b4a60(local_90,0xe);
    lVar12 = 0;
    if (lVar11 != 0) {
      thunk_FUN_012aa986(lVar13,0,uVar14);
      thunk_FUN_012aa7c6(lVar13,local_a0,uVar14);
      thunk_FUN_012aa986(lVar11,0,uVar5);
      thunk_FUN_012aa7c6(lVar11,local_98,local_90);
      *(int *)(lVar13 + 8) = (int)((ulong)lVar11 >> 8);
      *(uint *)(lVar13 + 0xc) = (uint)((ulong)lVar11 >> 0x28);
      lVar12 = lVar13;
    }
  }
  *(long *)(*param_1 + 0x58) = lVar12;
  FUN_00f8e910(&local_a0,&DAT_018e1d1c);
  uVar14 = (uint)(byte)local_a0[0xe] * 2 + 0x3f + (*local_a0 >> 0x18) * 4 & 0xfffffffc;
  lVar13 = FUN_000b49b0(uVar14,0xe);
  uVar5 = local_90;
  lVar12 = lVar13;
  if (lVar13 != 0) {
    lVar11 = FUN_000b4a60(local_90,0xe);
    lVar12 = 0;
    if (lVar11 != 0) {
      thunk_FUN_012aa986(lVar13,0,uVar14);
      thunk_FUN_012aa7c6(lVar13,local_a0,uVar14);
      thunk_FUN_012aa986(lVar11,0,uVar5);
      thunk_FUN_012aa7c6(lVar11,local_98,local_90);
      *(int *)(lVar13 + 8) = (int)((ulong)lVar11 >> 8);
      *(uint *)(lVar13 + 0xc) = (uint)((ulong)lVar11 >> 0x28);
      lVar12 = lVar13;
    }
  }
  *(long *)(*param_1 + 0x68) = lVar12;
  FUN_00f8e910(&local_a0,&DAT_018e21fc);
  uVar14 = (uint)(byte)local_a0[0xe] * 2 + 0x3f + (*local_a0 >> 0x18) * 4 & 0xfffffffc;
  lVar13 = FUN_000b49b0(uVar14,0xe);
  uVar5 = local_90;
  lVar12 = lVar13;
  if (lVar13 != 0) {
    lVar11 = FUN_000b4a60(local_90,0xe);
    lVar12 = 0;
    if (lVar11 != 0) {
      thunk_FUN_012aa986(lVar13,0,uVar14);
      thunk_FUN_012aa7c6(lVar13,local_a0,uVar14);
      thunk_FUN_012aa986(lVar11,0,uVar5);
      thunk_FUN_012aa7c6(lVar11,local_98,local_90);
      *(int *)(lVar13 + 8) = (int)((ulong)lVar11 >> 8);
      *(uint *)(lVar13 + 0xc) = (uint)((ulong)lVar11 >> 0x28);
      lVar12 = lVar13;
    }
  }
  *(long *)(*param_1 + 0x78) = lVar12;
  FUN_00f8e910(&local_a0,&DAT_018e1fcc);
  uVar14 = (uint)(byte)local_a0[0xe] * 2 + 0x3f + (*local_a0 >> 0x18) * 4 & 0xfffffffc;
  lVar13 = FUN_000b49b0(uVar14,0xe);
  uVar5 = local_90;
  lVar12 = lVar13;
  if (lVar13 != 0) {
    lVar11 = FUN_000b4a60(local_90,0xe);
    lVar12 = 0;
    if (lVar11 != 0) {
      thunk_FUN_012aa986(lVar13,0,uVar14);
      thunk_FUN_012aa7c6(lVar13,local_a0,uVar14);
      thunk_FUN_012aa986(lVar11,0,uVar5);
      thunk_FUN_012aa7c6(lVar11,local_98,local_90);
      *(int *)(lVar13 + 8) = (int)((ulong)lVar11 >> 8);
      *(uint *)(lVar13 + 0xc) = (uint)((ulong)lVar11 >> 0x28);
      lVar12 = lVar13;
    }
  }
  *(long *)(*param_1 + 0x70) = lVar12;
  FUN_007e5220(param_1);
  plVar1 = param_1 + 2;
  do {
    iVar3 = (int)*plVar1;
    LOCK();
    iVar7 = (int)*plVar1;
    if (iVar3 == iVar7) {
      *(int *)plVar1 = 1;
      iVar7 = iVar3;
    }
    UNLOCK();
  } while (iVar3 != iVar7);
  FUN_007dc7b0(param_1);
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),1);
  }
  uVar8 = thunk_FUN_012aa7f6();
  return uVar8;
}

