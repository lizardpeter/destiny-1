
undefined8 FUN_003f3de0(uint param_1)

{
  uint uVar1;
  long lVar2;
  long lVar3;
  ulong uVar4;
  undefined8 uVar5;
  long lVar6;
  
  if ((param_1 != 0xffffffff) &&
     (uVar1 = *(uint *)((ulong)((param_1 & 0x1fff) * DAT_02689590) + 0x50 + DAT_02689588),
     uVar1 != 0xffffffff)) {
    lVar6 = (ulong)(((uint)((int)uVar1 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar1 >> 0xd) * 0x40;
    lVar2 = *DAT_01a238a0;
    lVar3 = *(long *)(lVar2 + 0x10 + lVar6);
    uVar4 = (ulong)((uVar1 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar6));
    uVar5 = FUN_00409fe0((lVar3 + uVar4) -
                         ((long)*(int *)(lVar2 + 0x34 + lVar6) & *(ulong *)(lVar3 + 8 + uVar4)));
    return uVar5;
  }
  return 0;
}

