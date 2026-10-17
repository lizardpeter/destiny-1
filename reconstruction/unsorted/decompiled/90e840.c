
void FUN_0090e840(uint param_1,long param_2)

{
  undefined8 *puVar1;
  undefined8 *puVar2;
  undefined8 *puVar3;
  undefined8 *puVar4;
  byte bVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  long lVar9;
  undefined8 uVar10;
  undefined8 uVar11;
  undefined8 uVar12;
  undefined8 uVar13;
  undefined8 uVar14;
  undefined8 uVar15;
  undefined8 uVar16;
  undefined8 uVar17;
  undefined8 uVar18;
  undefined8 uVar19;
  undefined8 uVar20;
  undefined8 uVar21;
  undefined8 uVar22;
  undefined8 uVar23;
  undefined8 uVar24;
  undefined8 uVar25;
  undefined8 uVar26;
  undefined8 uVar27;
  undefined8 uVar28;
  undefined8 uVar29;
  undefined8 uVar30;
  undefined8 uVar31;
  undefined8 uVar32;
  undefined8 uVar33;
  undefined8 uVar34;
  undefined8 uVar35;
  undefined *puVar36;
  long lVar37;
  byte bVar38;
  uint uVar39;
  int iVar40;
  undefined8 uVar41;
  undefined4 *puVar42;
  long lVar43;
  undefined1 local_88 [24];
  undefined8 local_70;
  long local_68;
  long local_60;
  undefined8 local_58;
  long local_50;
  undefined8 local_48;
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar43 = ((ulong)param_1 & 0xffff) * 0x2af0;
  lVar9 = *(long *)(DAT_0273ea80 + 8);
  uVar6 = *(undefined4 *)(lVar9 + 0x270c + lVar43);
  uVar41 = *(undefined8 *)(lVar9 + 0x2700 + lVar43);
  uVar10 = *(undefined8 *)(lVar9 + 0x26f8 + lVar43);
  iVar40 = *(int *)(lVar9 + 0x648 + lVar43);
  uVar11 = *(undefined8 *)(lVar9 + 0x2730 + lVar43);
  uVar12 = *(undefined8 *)(lVar9 + 0x2738 + lVar43);
  uVar13 = *(undefined8 *)(lVar9 + 0x2728 + lVar43);
  uVar14 = *(undefined8 *)(lVar9 + 0x2720 + lVar43);
  uVar15 = *(undefined8 *)(lVar9 + 10000 + lVar43);
  uVar16 = *(undefined8 *)(lVar9 + 0x2718 + lVar43);
  uVar17 = *(undefined8 *)(lVar9 + 0x2760 + lVar43);
  uVar18 = *(undefined8 *)(lVar9 + 0x2768 + lVar43);
  uVar19 = *(undefined8 *)(lVar9 + 0x2758 + lVar43);
  uVar20 = *(undefined8 *)(lVar9 + 0x2750 + lVar43);
  uVar21 = *(undefined8 *)(lVar9 + 0x2740 + lVar43);
  uVar22 = *(undefined8 *)(lVar9 + 0x2748 + lVar43);
  uVar23 = *(undefined8 *)(lVar9 + 0x27e4 + lVar43);
  uVar24 = *(undefined8 *)(lVar9 + 0x2790 + lVar43);
  uVar25 = *(undefined8 *)(lVar9 + 0x2798 + lVar43);
  uVar26 = *(undefined8 *)(lVar9 + 0x2788 + lVar43);
  uVar27 = *(undefined8 *)(lVar9 + 0x2780 + lVar43);
  uVar28 = *(undefined8 *)(lVar9 + 0x2770 + lVar43);
  uVar29 = *(undefined8 *)(lVar9 + 0x2778 + lVar43);
  uVar7 = *(undefined4 *)(lVar9 + 0x27a0 + lVar43);
  uVar30 = *(undefined8 *)(lVar9 + 0x27c0 + lVar43);
  uVar31 = *(undefined8 *)(FUN_000027d0 + lVar43 + lVar9);
  uVar32 = *(undefined8 *)(&DAT_000027c8 + lVar43 + lVar9);
  uVar33 = *(undefined8 *)(lVar9 + 0x27b8 + lVar43);
  uVar34 = *(undefined8 *)(lVar9 + 0x27a8 + lVar43);
  uVar35 = *(undefined8 *)(lVar9 + 0x27b0 + lVar43);
  uVar8 = *(undefined4 *)(lVar9 + 0x27d8 + lVar43);
  bVar5 = *(byte *)(lVar9 + 0x14 + lVar43);
  local_70 = *(undefined8 *)(param_2 + 0xc);
  local_68 = *(long *)(param_2 + 0x28);
  local_58 = *(undefined8 *)(param_2 + 0x98);
  local_50 = *(long *)(param_2 + 0xa0);
  local_48 = *(undefined8 *)(param_2 + 0x20);
  local_40 = *(undefined8 *)(param_2 + 0x18);
  local_60 = local_50;
  if (local_50 == 0) {
    local_60 = local_68;
  }
  FUN_00302bb0(*(undefined4 *)(lVar9 + 4 + lVar43),&local_70);
  FUN_0090f180((ulong)param_1,0,param_2);
  bVar38 = *(byte *)(lVar9 + 0x14 + lVar43);
  if ((bVar5 & 1) == 0) {
    bVar38 = bVar38 & 0xfe;
  }
  else {
    bVar38 = bVar38 | 1;
  }
  *(byte *)(lVar9 + 0x14 + lVar43) = bVar38;
  *DAT_0273ea90 = *DAT_0273ea90 + 1;
  FUN_00b9f2c0(param_1);
  FUN_0090a2c0(param_1);
  if (iVar40 != -1) {
    puVar1 = (undefined8 *)(lVar9 + 0x27a8 + lVar43);
    puVar2 = (undefined8 *)(lVar9 + 0x2770 + lVar43);
    puVar3 = (undefined8 *)(lVar9 + 0x2740 + lVar43);
    puVar4 = (undefined8 *)(lVar9 + 10000 + lVar43);
    uVar39 = FUN_006ed8f0(iVar40);
    FUN_00911c50(param_1,iVar40,0,1);
    *(undefined8 *)(lVar9 + 0x26f8 + lVar43) = uVar10;
    *(undefined8 *)(lVar9 + 0x2700 + lVar43) = uVar41;
    *(undefined4 *)(lVar9 + 0x270c + lVar43) = uVar6;
    puVar4[5] = uVar12;
    puVar4[4] = uVar11;
    puVar4[3] = uVar13;
    puVar4[2] = uVar14;
    puVar4[1] = uVar16;
    puVar36 = PTR_DAT_0191a990;
    *puVar4 = uVar15;
    puVar3[5] = uVar18;
    puVar3[4] = uVar17;
    puVar3[3] = uVar19;
    puVar3[2] = uVar20;
    puVar3[1] = uVar22;
    *puVar3 = uVar21;
    *(undefined8 *)(lVar9 + 0x27e4 + lVar43) = uVar23;
    puVar2[5] = uVar25;
    puVar2[4] = uVar24;
    puVar2[3] = uVar26;
    puVar2[2] = uVar27;
    puVar2[1] = uVar29;
    *puVar2 = uVar28;
    *(undefined4 *)(lVar9 + 0x27a0 + lVar43) = uVar7;
    puVar1[5] = uVar31;
    puVar1[4] = uVar32;
    puVar1[3] = uVar30;
    puVar1[2] = uVar33;
    puVar1[1] = uVar35;
    *puVar1 = uVar34;
    *(undefined4 *)(lVar9 + 0x27d8 + lVar43) = uVar8;
    lVar37 = DAT_02692228;
    uVar39 = (uVar39 & 0x1fff) * DAT_02692230;
    uVar6 = *(undefined4 *)puVar36;
    uVar41 = FUN_00328350(local_88);
    iVar40 = FUN_00327f40(lVar37 + (ulong)uVar39,uVar6,0,0,uVar41);
    if (iVar40 != -1) {
      puVar42 = (undefined4 *)thunk_FUN_00326e00(iVar40);
      *puVar42 = *(undefined4 *)(lVar9 + 0x62c + lVar43);
      puVar42[1] = param_1;
      FUN_003283d0(iVar40);
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

