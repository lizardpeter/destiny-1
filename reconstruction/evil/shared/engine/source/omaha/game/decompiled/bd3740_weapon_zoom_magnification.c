
ulong FUN_00bd3740(undefined8 param_1,short param_2)

{
  long lVar1;
  long lVar2;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  long lVar6;
  ulong uVar7;
  
  if (param_2 != -1) {
    uVar3 = FUN_00bd3820();
    uVar7 = (ulong)((uVar3 & 0x1fff) * DAT_02689800);
    uVar5 = 0xffffffff;
    uVar3 = *(uint *)(((uVar7 + DAT_026897f8) -
                      (*(ulong *)(DAT_026897f8 + 8 + uVar7) & (long)DAT_02689818)) + 0x68);
    if (uVar3 != 0xffffffff) {
      uVar7 = (ulong)((uVar3 & 0x1fff) * DAT_02689800);
      iVar4 = FUN_007397f0((DAT_026897f8 + uVar7) -
                           (*(ulong *)(DAT_026897f8 + 8 + uVar7) & (long)DAT_02689818));
      if (iVar4 != -1) {
        uVar5 = FUN_006ed9f0(iVar4);
      }
    }
    uVar3 = FUN_006fc510(uVar5);
    if (uVar3 != 0xffffffff) {
      lVar6 = (ulong)(((uint)((int)uVar3 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar3 >> 0xd) * 0x40;
      lVar1 = *DAT_01a238a0;
      lVar2 = *(long *)(lVar1 + 0x10 + lVar6);
      uVar7 = (ulong)((uVar3 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar6));
      uVar7 = FUN_006f8ec0((lVar2 + uVar7) -
                           ((long)*(int *)(lVar1 + 0x34 + lVar6) & *(ulong *)(lVar2 + 8 + uVar7)));
      return uVar7;
    }
  }
  return (ulong)DAT_01699a38;
}

