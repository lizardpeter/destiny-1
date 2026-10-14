
void FUN_004098e0(long param_1,uint *param_2)

{
  long lVar1;
  undefined8 uVar2;
  undefined1 uVar3;
  char cVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  ulong uVar8;
  undefined8 *puVar9;
  byte *pbVar10;
  undefined8 uVar11;
  ulong uVar12;
  long lVar13;
  uint uVar14;
  undefined8 *puVar15;
  long extraout_RDX;
  long lVar16;
  long lVar17;
  long lVar18;
  
  iVar5 = FUN_00129570();
  if (iVar5 == -1) {
    return;
  }
  uVar6 = FUN_00129570(param_1);
  lVar18 = DAT_02689588;
  uVar8 = (ulong)((uVar6 & 0x1fff) * DAT_02689590);
  if ((*(byte *)(uVar8 + 0x40 + DAT_02689588) & 1) == 0) {
    return;
  }
  iVar7 = FUN_00108470(param_1);
  if (iVar7 != 0) {
    uVar6 = *(uint *)(uVar8 + 0x50 + lVar18);
    uVar14 = (int)uVar6 >> 0xd;
    lVar13 = (ulong)((uVar14 >> 0x12 | 0x3ff) & uVar14) * 0x40;
    lVar18 = *DAT_01a238a0;
    lVar1 = *(long *)(lVar18 + 0x10 + lVar13);
    uVar8 = (ulong)((uVar6 & 0x1fff) * *(int *)(lVar18 + 0x30 + lVar13));
    lVar18 = (lVar1 + uVar8) -
             ((long)*(int *)(lVar18 + 0x34 + lVar13) & *(ulong *)(lVar1 + 8 + uVar8));
    iVar5 = FUN_00108470(lVar18);
    if (iVar5 != 0) {
      return;
    }
    uVar6 = *(uint *)(lVar18 + 0x208);
    puVar9 = (undefined8 *)0x0;
    puVar15 = (undefined8 *)0x0;
    if (uVar6 != 0xffffffff) {
      lVar16 = (ulong)(((uint)((int)uVar6 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar6 >> 0xd) * 0x40;
      lVar1 = *DAT_01a238a0;
      lVar13 = *(long *)(lVar1 + 0x10 + lVar16);
      uVar8 = (ulong)((uVar6 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar16));
      puVar15 = (undefined8 *)
                (((lVar13 + uVar8) -
                 ((long)*(int *)(lVar1 + 0x34 + lVar16) & *(ulong *)(lVar13 + 8 + uVar8))) +
                *(long *)(lVar18 + 0x210));
    }
    uVar11 = puVar15[3];
    uVar2 = puVar15[4];
    *(undefined8 *)(param_1 + 0x2f8) = puVar15[5];
    *(undefined8 *)(param_1 + 0x2f0) = uVar2;
    *(undefined8 *)(param_1 + 0x2e8) = uVar11;
    *(undefined8 *)(param_1 + 0x2e0) = puVar15[2];
    uVar11 = *puVar15;
    *(undefined8 *)(param_1 + 0x2d8) = puVar15[1];
    *(undefined8 *)(param_1 + 0x2d0) = uVar11;
    uVar6 = *(uint *)(lVar18 + 0x1f8);
    if (uVar6 != 0xffffffff) {
      lVar16 = (ulong)(((uint)((int)uVar6 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar6 >> 0xd) * 0x40;
      lVar1 = *DAT_01a238a0;
      lVar13 = *(long *)(lVar1 + 0x10 + lVar16);
      uVar8 = (ulong)((uVar6 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar16));
      puVar9 = (undefined8 *)
               (((lVar13 + uVar8) -
                ((long)*(int *)(lVar1 + 0x34 + lVar16) & *(ulong *)(lVar13 + 8 + uVar8))) +
               *(long *)(lVar18 + 0x200));
    }
    uVar11 = *puVar9;
    *(undefined8 *)(param_1 + 0x298) = puVar9[1];
    *(undefined8 *)(param_1 + 0x290) = uVar11;
    uVar6 = (int)*(uint *)(lVar18 + 0x318) >> 0xd;
    puVar9 = (undefined8 *)0x0;
    lVar1 = *DAT_01a238a0;
    lVar16 = (ulong)((uVar6 >> 0x12 | 0x3ff) & uVar6) * 0x40;
    lVar13 = *(long *)(lVar1 + 0x10 + lVar16);
    uVar8 = (ulong)((*(uint *)(lVar18 + 0x318) & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar16));
    *(undefined4 *)(param_1 + 0x300) =
         *(undefined4 *)
          (((lVar13 + uVar8) -
           ((long)*(int *)(lVar1 + 0x34 + lVar16) & *(ulong *)(lVar13 + 8 + uVar8))) +
          *(long *)(lVar18 + 800));
    uVar6 = *(uint *)(lVar18 + 0x308);
    if (uVar6 != 0xffffffff) {
      lVar16 = (ulong)(((uint)((int)uVar6 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar6 >> 0xd) * 0x40;
      lVar1 = *DAT_01a238a0;
      lVar13 = *(long *)(lVar1 + 0x10 + lVar16);
      uVar8 = (ulong)((uVar6 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar16));
      puVar9 = (undefined8 *)
               (((lVar13 + uVar8) -
                ((long)*(int *)(lVar1 + 0x34 + lVar16) & *(ulong *)(lVar13 + 8 + uVar8))) +
               *(long *)(lVar18 + 0x310));
    }
    uVar11 = puVar9[4];
    *(undefined8 *)(param_1 + 0x2c8) = puVar9[5];
    *(undefined8 *)(param_1 + 0x2c0) = uVar11;
    *(undefined8 *)(param_1 + 0x2b8) = puVar9[3];
    *(undefined8 *)(param_1 + 0x2b0) = puVar9[2];
    uVar11 = *puVar9;
    *(undefined8 *)(param_1 + 0x2a8) = puVar9[1];
    *(undefined8 *)(param_1 + 0x2a0) = uVar11;
    uVar6 = FUN_00108cb0(param_1);
    lVar18 = *DAT_01a238a0;
    lVar13 = (ulong)(((uint)((int)uVar6 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar6 >> 0xd) * 0x40;
    uVar8 = (ulong)((uVar6 & 0x1fff) * *(int *)(lVar18 + 0x30 + lVar13));
    lVar1 = *(long *)(lVar18 + 0x10 + lVar13);
    lVar18 = param_1 + 0x290 +
             (((long)*(int *)(lVar18 + 0x34 + lVar13) & *(ulong *)(lVar1 + 8 + uVar8)) -
             (lVar1 + uVar8));
    param_2[4] = *(uint *)PTR_DAT_019b2ae0;
    goto LAB_00409e6c;
  }
  uVar6 = *(uint *)(uVar8 + 0x4c + lVar18);
  lVar1 = *(long *)(DAT_0273ea80 + 8);
  *(undefined4 *)(param_1 + 0x304) = *(undefined4 *)(param_1 + 0x28c);
  lVar13 = ((ulong)uVar6 & 0xffff) * 0x2af0;
  *(int *)(param_1 + 0x2c8) = (int)*(char *)(lVar1 + 0x738 + lVar13);
  *(undefined4 *)(param_1 + 0x2c4) = *(undefined4 *)(lVar1 + 0x166c + lVar13);
  pbVar10 = (byte *)FUN_00918200();
  *(byte *)(param_1 + 0x2cd) = *pbVar10 & 1;
  if ((*(int *)(lVar1 + 0x644 + lVar13) == -1) &&
     (iVar7 = FUN_00071f60(lVar1 + 0x3c + lVar13), iVar7 != -1)) {
    *(undefined1 *)(param_1 + 0x29a) = 1;
  }
  else {
    *(undefined1 *)(param_1 + 0x29a) = 0;
  }
  uVar3 = FUN_00919380(iVar5);
  *(undefined1 *)(param_1 + 0x29b) = uVar3;
  uVar3 = FUN_009193b0(iVar5);
  *(undefined1 *)(param_1 + 0x29c) = uVar3;
  uVar11 = FUN_003430b0();
  uVar6 = FUN_00345620(uVar11);
  *(uint *)(param_1 + 0x290) = uVar6;
  if (*(char *)(param_1 + 0x298) == '\0') {
    if ((uVar6 < 0x80) && (cVar4 = FUN_009141f0(), cVar4 == '\0')) {
      *(undefined1 *)(param_1 + 0x298) = 1;
      goto LAB_00409cda;
    }
    *(undefined1 *)(param_1 + 0x298) = 0;
  }
  else {
LAB_00409cda:
    if (((*(char *)(param_1 + 0x299) == '\0') &&
        (*(int *)(param_1 + 0x250) == *(int *)(param_1 + 0x2c8))) &&
       (cVar4 = FUN_0077b920(), cVar4 != '\0')) {
      *(undefined1 *)(param_1 + 0x299) = 1;
    }
  }
  uVar6 = (int)*(uint *)(param_1 + 0x208) >> 0xd;
  lVar16 = (ulong)((uVar6 >> 0x12 | 0x3ff) & uVar6) * 0x40;
  lVar1 = *DAT_01a238a0;
  lVar13 = *(long *)(lVar1 + 0x10 + lVar16);
  uVar12 = (ulong)((*(uint *)(param_1 + 0x208) & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar16));
  uVar6 = FUN_0011e9a0((int)*(char *)(*(long *)(param_1 + 0x210) + 9 +
                                     ((lVar13 + uVar12) -
                                     ((long)*(int *)(lVar1 + 0x34 + lVar16) &
                                     *(ulong *)(lVar13 + 8 + uVar12)))));
  if (uVar6 != 0xffffffff) {
    lVar16 = (ulong)(((uint)((int)uVar6 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar6 >> 0xd) * 0x40;
    lVar1 = *DAT_01a238a0;
    lVar13 = *(long *)(lVar1 + 0x10 + lVar16);
    uVar12 = (ulong)((uVar6 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar16));
    lVar16 = (lVar13 + uVar12) -
             ((long)*(int *)(lVar1 + 0x34 + lVar16) & *(ulong *)(lVar13 + 8 + uVar12));
    uVar6 = *(uint *)(extraout_RDX + lVar16);
    uVar14 = (int)uVar6 >> 0xd;
    lVar17 = (ulong)((uVar14 >> 0x12 | 0x3ff) & uVar14) * 0x40;
    lVar13 = *(long *)(lVar1 + 0x10 + lVar17);
    uVar12 = (ulong)((uVar6 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar17));
    *(undefined4 *)(param_1 + 0x294) =
         *(undefined4 *)
          (*(long *)(extraout_RDX + 8 + lVar16) + 0x6c +
          ((lVar13 + uVar12) -
          ((long)*(int *)(lVar1 + 0x34 + lVar17) & *(ulong *)(lVar13 + 8 + uVar12))));
  }
  uVar3 = FUN_00409e90(uVar8 + 0x10 + lVar18);
  *(undefined1 *)(param_1 + 0x2ce) = uVar3;
  uVar6 = FUN_00108cb0(param_1);
  lVar13 = (ulong)(((uint)((int)uVar6 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar6 >> 0xd) * 0x40;
  lVar18 = *DAT_01a238a0;
  uVar8 = (ulong)((uVar6 & 0x1fff) * *(int *)(lVar18 + 0x30 + lVar13));
  lVar1 = *(long *)(lVar18 + 0x10 + lVar13);
  lVar18 = (((long)*(int *)(lVar18 + 0x34 + lVar13) & *(ulong *)(lVar1 + 8 + uVar8)) +
           param_1 + 0x290) - (lVar1 + uVar8);
  param_2[4] = *(uint *)PTR_DAT_019b2ae0;
LAB_00409e6c:
  param_2[2] = 0;
  param_2[3] = 0;
  param_2[0] = 0;
  param_2[1] = 0;
  *param_2 = uVar6;
  *(long *)(param_2 + 2) = lVar18;
  return;
}

