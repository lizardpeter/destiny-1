
void FUN_0073e860(long param_1)

{
  uint uVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  ulong uVar5;
  long lVar6;
  undefined8 uVar7;
  long lVar8;
  long lVar9;
  uint uVar10;
  long lVar11;
  undefined4 uVar12;
  undefined1 local_1130 [24];
  uint local_1118;
  long local_1110;
  undefined1 local_1100 [24];
  uint local_10e8;
  long local_10e0;
  undefined1 local_10d0 [24];
  uint local_10b8;
  long local_10b0;
  long local_38;
  
  lVar11 = DAT_02692228;
  local_38 = *DAT_01a1f100;
  uVar1 = *(uint *)(param_1 + 0x2c);
  uVar10 = (uVar1 & 0x1fff) * DAT_02692230;
  iVar3 = FUN_00913fa0(uVar1);
  lVar11 = lVar11 + (ulong)uVar10;
  FUN_00337fe0(lVar11,*(undefined4 *)PTR_DAT_019b2430,param_1 + 0x50,0);
  FUN_00337fe0(lVar11,*(undefined4 *)PTR_DAT_019b2fd8,param_1 + 0x80,0);
  cVar2 = FUN_00337fe0(lVar11,*(undefined4 *)PTR_DAT_019b4320,local_10d0,0);
  uVar12 = 0xffffffff;
  uVar4 = 0xffffffff;
  if (cVar2 != '\0') {
    lVar8 = (ulong)(((uint)((int)local_10b8 >> 0xd) >> 0x12 | 0x3ff) & (int)local_10b8 >> 0xd) *
            0x40;
    lVar6 = *DAT_01a238a0;
    lVar9 = *(long *)(lVar6 + 0x10 + lVar8);
    uVar5 = (ulong)((local_10b8 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
    uVar4 = *(undefined4 *)
             (local_10b0 + 0x24 +
             ((lVar9 + uVar5) -
             ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar9 + 8 + uVar5))));
  }
  *(undefined4 *)(param_1 + 0xb0) = uVar4;
  FUN_00337fe0(lVar11,*(undefined4 *)PTR_DAT_019b3258,param_1 + 0x118,0);
  FUN_00337fe0(lVar11,*(undefined4 *)PTR_DAT_019b2228,param_1 + 0xb8,0);
  FUN_00337fe0(lVar11,*(undefined4 *)PTR_DAT_019b2348,param_1 + 0xe8,0);
  cVar2 = FUN_00337fe0(lVar11,*(undefined4 *)PTR_DAT_019b3238,local_10d0,0);
  if (cVar2 != '\0') {
    lVar8 = (ulong)(((uint)((int)local_10b8 >> 0xd) >> 0x12 | 0x3ff) & (int)local_10b8 >> 0xd) *
            0x40;
    lVar6 = *DAT_01a238a0;
    lVar9 = *(long *)(lVar6 + 0x10 + lVar8);
    uVar5 = (ulong)((local_10b8 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
    uVar12 = *(undefined4 *)
              (local_10b0 + 0x24 +
              ((lVar9 + uVar5) -
              ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar9 + 8 + uVar5))));
  }
  *(undefined4 *)(param_1 + 0x148) = uVar12;
  cVar2 = FUN_00337fe0(lVar11,*(undefined4 *)PTR_DAT_019b1a68,local_10d0,0);
  uVar12 = 0xffffffff;
  uVar4 = 0xffffffff;
  if (cVar2 != '\0') {
    lVar8 = (ulong)(((uint)((int)local_10b8 >> 0xd) >> 0x12 | 0x3ff) & (int)local_10b8 >> 0xd) *
            0x40;
    lVar6 = *DAT_01a238a0;
    lVar9 = *(long *)(lVar6 + 0x10 + lVar8);
    uVar5 = (ulong)((local_10b8 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
    uVar4 = *(undefined4 *)
             (local_10b0 + 0x24 +
             ((lVar9 + uVar5) -
             ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar9 + 8 + uVar5))));
  }
  *(undefined4 *)(param_1 + 0x14c) = uVar4;
  cVar2 = FUN_00337fe0(lVar11,*(undefined4 *)PTR_DAT_019b1b60,local_10d0,0);
  if (cVar2 != '\0') {
    lVar8 = (ulong)(((uint)((int)local_10b8 >> 0xd) >> 0x12 | 0x3ff) & (int)local_10b8 >> 0xd) *
            0x40;
    lVar6 = *DAT_01a238a0;
    lVar9 = *(long *)(lVar6 + 0x10 + lVar8);
    uVar5 = (ulong)((local_10b8 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
    uVar12 = *(undefined4 *)
              (local_10b0 + 0x24 +
              ((lVar9 + uVar5) -
              ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar9 + 8 + uVar5))));
  }
  *(undefined4 *)(param_1 + 0x150) = uVar12;
  uVar10 = FUN_006eda20(*(undefined4 *)(param_1 + 0x24));
  uVar5 = (ulong)((uVar10 & 0x1fff) * DAT_02689800);
  lVar6 = (uVar5 + DAT_026897f8) - (*(ulong *)(DAT_026897f8 + 8 + uVar5) & (long)DAT_02689818);
  if (((3U >> (*(byte *)(lVar6 + 0x42) & 0x1f) & 1) != 0) &&
     (uVar5 = (ulong)((*(uint *)(lVar6 + 0x68) & 0x1fff) * DAT_02689800),
     *(int *)(((DAT_026897f8 + uVar5) - ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar5)))
             + 0x9d8) != -1)) {
    uVar7 = FUN_0066ae60();
    FUN_0104c3c0(local_10d0,uVar7);
    FUN_0104f3a0(param_1 + 0x158,local_10d0);
  }
  if ((*(uint *)(&DAT_0267fe58 + (ulong)(uVar1 >> 5 & 0xff) * 4) >> (uVar1 & 0x1f) & 1) == 0)
  goto LAB_0073ec63;
  uVar10 = FUN_00913fa0(uVar1);
  if (uVar10 == 0xffffffff) {
switchD_0073ec26_caseD_2:
    uVar4 = FUN_0052b3e0();
    goto LAB_0073ec34;
  }
  switch(*(undefined4 *)(*(long *)(DAT_0273ea80 + 8) + 0x5b0 + (ulong)(uVar10 & 0xffff) * 0x2af0)) {
  case 0:
    uVar4 = FUN_0052b320();
    break;
  case 1:
    uVar4 = FUN_0052b380();
    break;
  case 2:
    goto switchD_0073ec26_caseD_2;
  case 3:
    uVar4 = FUN_0052b440();
    break;
  default:
    goto switchD_0073ec26_caseD_4;
  case 5:
    uVar4 = FUN_0052b4a0();
  }
LAB_0073ec34:
  *(undefined1 *)(param_1 + 0x141a) = 1;
  *(undefined4 *)(param_1 + 0x13f8) = uVar4;
  FUN_0073f000(param_1,uVar4);
switchD_0073ec26_caseD_4:
  cVar2 = FUN_005c4590();
  if (cVar2 != '\0') {
    FUN_0073e520(param_1,1);
  }
LAB_0073ec63:
  FUN_00628150(&DAT_00001318 + param_1,uVar1,*(undefined4 *)(param_1 + 0x24),0);
  FUN_00628150(param_1 + 0x1230,uVar1,*(undefined4 *)(param_1 + 0x24),0);
  cVar2 = FUN_00337fe0(lVar11,*(undefined4 *)PTR_DAT_019b1a58,local_10d0,0);
  if (cVar2 != '\0') {
    lVar8 = (ulong)(((uint)((int)local_10b8 >> 0xd) >> 0x12 | 0x3ff) & (int)local_10b8 >> 0xd) *
            0x40;
    lVar6 = *DAT_01a238a0;
    lVar9 = *(long *)(lVar6 + 0x10 + lVar8);
    uVar5 = (ulong)((local_10b8 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
    uVar10 = *(uint *)(local_10b0 + 0x24 +
                      ((lVar9 + uVar5) -
                      ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar9 + 8 + uVar5))));
    if (uVar10 != 0xffffffff) {
      uVar5 = (ulong)((uVar10 & 0x1fff) * DAT_02689800);
      FUN_004bab90((DAT_026897f8 + uVar5) -
                   ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar5)));
    }
  }
  cVar2 = FUN_00337fe0(lVar11,*(undefined4 *)PTR_DAT_019b3478,local_1100,0);
  if (cVar2 != '\0') {
    lVar8 = (ulong)(((uint)((int)local_10e8 >> 0xd) >> 0x12 | 0x3ff) & (int)local_10e8 >> 0xd) *
            0x40;
    lVar6 = *DAT_01a238a0;
    lVar9 = *(long *)(lVar6 + 0x10 + lVar8);
    uVar5 = (ulong)((local_10e8 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
    uVar10 = *(uint *)(local_10e0 + 0x24 +
                      ((lVar9 + uVar5) -
                      ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar9 + 8 + uVar5))));
    if (uVar10 != 0xffffffff) {
      uVar5 = (ulong)((uVar10 & 0x1fff) * DAT_02689800);
      FUN_00498040((DAT_026897f8 + uVar5) -
                   ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar5)));
    }
  }
  cVar2 = FUN_00337fe0(lVar11,*(undefined4 *)PTR_DAT_019b2928,local_1130,0);
  if (cVar2 != '\0') {
    lVar9 = (ulong)(((uint)((int)local_1118 >> 0xd) >> 0x12 | 0x3ff) & (int)local_1118 >> 0xd) *
            0x40;
    lVar11 = *DAT_01a238a0;
    lVar6 = *(long *)(lVar11 + 0x10 + lVar9);
    uVar5 = (ulong)((local_1118 & 0x1fff) * *(int *)(lVar11 + 0x30 + lVar9));
    uVar10 = *(uint *)(local_1110 + 0x24 +
                      ((lVar6 + uVar5) -
                      ((long)*(int *)(lVar11 + 0x34 + lVar9) & *(ulong *)(lVar6 + 8 + uVar5))));
    if (uVar10 != 0xffffffff) {
      uVar5 = (ulong)((uVar10 & 0x1fff) * DAT_02689800);
      FUN_003a84d0((DAT_026897f8 + uVar5) -
                   ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar5)));
    }
  }
  if ((iVar3 != -1) && (cVar2 = FUN_00918960(), cVar2 != '\0')) {
    FUN_006757a0(uVar1);
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

