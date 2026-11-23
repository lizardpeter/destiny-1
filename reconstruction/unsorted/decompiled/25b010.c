
long FUN_0025b010(long *param_1,short param_2)

{
  uint uVar1;
  long lVar2;
  int iVar3;
  int *piVar4;
  undefined8 uVar5;
  long lVar6;
  ulong uVar7;
  long lVar8;
  
  piVar4 = (int *)(**(code **)(*param_1 + 0x168))();
  uVar7 = (ulong)param_2;
  lVar8 = 0;
  if ((uVar7 < (ulong)(long)*piVar4) &&
     ((long)piVar4 + uVar7 * 0x18 + *(long *)(piVar4 + 2) + 0x18 != 0)) {
    uVar1 = *(uint *)((long)piVar4 + uVar7 * 0x18 + *(long *)(piVar4 + 2) + 0x28);
    iVar3 = (**(code **)(*param_1 + 0x18))(param_1);
    if (1 < iVar3 - 3U) {
      if (iVar3 != 2) {
        return 0;
      }
      uVar5 = FUN_00346d20();
      iVar3 = FUN_00349c10(uVar5,uVar1);
      if (iVar3 != 2) {
        return 0;
      }
    }
    lVar6 = (ulong)(((uint)((int)uVar1 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar1 >> 0xd) * 0x40;
    lVar8 = *DAT_01a238a0;
    lVar2 = *(long *)(lVar8 + 0x10 + lVar6);
    uVar7 = (ulong)((uVar1 & 0x1fff) * *(int *)(lVar8 + 0x30 + lVar6));
    lVar8 = (lVar2 + uVar7) - ((long)*(int *)(lVar8 + 0x34 + lVar6) & *(ulong *)(lVar2 + 8 + uVar7))
    ;
  }
  return lVar8;
}

