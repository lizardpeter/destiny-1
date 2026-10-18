
void FUN_007dee30(long param_1,uint param_2)

{
  int iVar1;
  long lVar2;
  undefined8 uVar3;
  long lVar4;
  long lVar5;
  ulong uVar6;
  undefined8 uVar7;
  
  if (*(uint *)(param_1 + 0x1d68) == param_2) {
    return;
  }
  *(uint *)(param_1 + 0x1d68) = param_2;
  lVar4 = (ulong)(((uint)((int)param_2 >> 0xd) >> 0x12 | 0x3ff) & (int)param_2 >> 0xd) * 0x40;
  lVar5 = *DAT_01a238a0;
  lVar2 = *(long *)(lVar5 + 0x10 + lVar4);
  uVar6 = (ulong)((param_2 & 0x1fff) * *(int *)(lVar5 + 0x30 + lVar4));
  lVar5 = (lVar2 + uVar6) - ((long)*(int *)(lVar5 + 0x34 + lVar4) & *(ulong *)(lVar2 + 8 + uVar6));
  *(long *)(param_1 + 0x1d70) = lVar5;
  iVar1 = *(int *)(lVar5 + 0x38);
  uVar3 = *(undefined8 *)(param_1 + 0x50);
  FUN_00f7f790(uVar3,iVar1);
  if (*(char *)(param_1 + 0x27c0) != '\0') {
    if (iVar1 == 0) {
      uVar7 = 0xffff;
    }
    else {
      uVar7 = 0xffffffff;
    }
    FUN_00f80730(uVar3,uVar7);
  }
  FUN_00f7f840(uVar3,*(undefined4 *)(*(long *)(param_1 + 0x1d70) + 0x3c));
  FUN_00f7f7e0(uVar3,*(undefined8 *)(*(long *)(param_1 + 0x1d70) + 0x30));
  return;
}

