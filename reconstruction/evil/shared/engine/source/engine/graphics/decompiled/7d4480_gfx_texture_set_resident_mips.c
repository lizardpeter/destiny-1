
void FUN_007d4480(uint param_1,ulong param_2,ulong param_3)

{
  int iVar1;
  long lVar2;
  ushort uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  long lVar7;
  ushort uVar8;
  long lVar9;
  ushort uVar10;
  ulong uVar11;
  int iVar12;
  undefined4 uVar13;
  
  lVar7 = (ulong)(((uint)((int)param_1 >> 0xd) >> 0x12 | 0x3ff) & (int)param_1 >> 0xd) * 0x40;
  lVar9 = *DAT_01a238a0;
  lVar2 = *(long *)(lVar9 + 0x10 + lVar7);
  uVar11 = (ulong)((param_1 & 0x1fff) * *(int *)(lVar9 + 0x30 + lVar7));
  lVar9 = (lVar2 + uVar11) - ((long)*(int *)(lVar9 + 0x34 + lVar7) & *(ulong *)(lVar2 + 8 + uVar11))
  ;
  if (lVar9 == 0) {
    return;
  }
  FUN_00f82e30(lVar9);
  FUN_00f841f0(lVar9);
  FUN_00f841d0(lVar9);
  uVar4 = FUN_00f846b0(lVar9);
  uVar5 = FUN_00f84620(lVar9);
  uVar6 = FUN_00f84690(lVar9);
  uVar3 = *(ushort *)(lVar9 + 0x28);
  iVar1 = *(int *)(lVar9 + 0x40);
  if (param_3 == 0) {
    uVar8 = *(ushort *)(lVar9 + 0x2a) >> 1;
    uVar10 = uVar3 >> 1;
    if (uVar3 < 4) {
      uVar10 = 1;
    }
    if (uVar8 < 2) {
      uVar8 = 1;
    }
    if (*(char *)(lVar9 + 0x35) != '\0') {
      uVar8 = uVar8 + 3 & 0xfffc;
      uVar10 = uVar10 + 3 & 0xfffc;
    }
    iVar12 = *(byte *)(lVar9 + 0x31) - 1;
    if (iVar1 == 2) {
      uVar13 = 1;
      uVar6 = 0;
LAB_007d4632:
      FUN_00f83530(lVar9,uVar10,uVar8,1,iVar12,uVar4,uVar5,uVar6,uVar13);
    }
    else {
      if (iVar1 != 3) {
        uVar13 = 0;
        goto LAB_007d4632;
      }
      uVar3 = 1;
      if (3 < *(ushort *)(lVar9 + 0x2c)) {
        uVar3 = *(ushort *)(lVar9 + 0x2c) >> 1;
      }
      FUN_00f83ab0(lVar9,uVar10,uVar8,uVar3,iVar12,uVar4,uVar5);
    }
    param_3 = param_2 >> 8;
    goto LAB_007d464c;
  }
  if (iVar1 == 2) {
    uVar13 = 1;
    uVar6 = 0;
LAB_007d4606:
    FUN_00f83530(lVar9,uVar3,*(ushort *)(lVar9 + 0x2a),1,*(undefined1 *)(lVar9 + 0x31),uVar4,uVar5,
                 uVar6,uVar13);
  }
  else {
    if (iVar1 != 3) {
      uVar13 = 0;
      goto LAB_007d4606;
    }
    FUN_00f83ab0(lVar9);
  }
  param_3 = param_3 >> 8;
LAB_007d464c:
  FUN_00f841b0(lVar9,param_3 & 0xffffffff);
  return;
}

