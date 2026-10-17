
long FUN_0025cd60(long *param_1)

{
  long lVar1;
  long lVar2;
  long lVar3;
  ulong uVar4;
  uint uVar5;
  long lVar6;
  
  lVar3 = (**(code **)(*param_1 + 8))();
  if (DAT_02652808 == 0) {
    uVar5 = (int)*(uint *)(lVar3 + 0x28) >> 0xd;
    lVar1 = *DAT_01a238a0;
    lVar6 = (ulong)((uVar5 >> 0x12 | 0x3ff) & uVar5) * 0x40;
    lVar2 = *(long *)(lVar1 + 0x10 + lVar6);
    uVar4 = (ulong)((*(uint *)(lVar3 + 0x28) & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar6));
    DAT_02652808 = (lVar2 + uVar4) -
                   ((long)*(int *)(lVar1 + 0x34 + lVar6) & *(ulong *)(lVar2 + 8 + uVar4));
  }
  lVar3 = DAT_02652808 + 8;
  if (DAT_02652808 == 0) {
    lVar3 = 0;
  }
  return lVar3;
}

