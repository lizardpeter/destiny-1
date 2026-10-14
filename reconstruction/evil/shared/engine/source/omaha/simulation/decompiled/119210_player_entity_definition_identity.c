
long FUN_00119210(long param_1)

{
  uint uVar1;
  long lVar2;
  long lVar3;
  long lVar4;
  ulong uVar5;
  long lVar6;
  
  uVar1 = *(uint *)(param_1 + 0x50);
  lVar3 = 0;
  if (uVar1 != 0xffffffff) {
    lVar6 = (ulong)(((uint)((int)uVar1 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar1 >> 0xd) * 0x40;
    lVar2 = *DAT_01a238a0;
    lVar4 = *(long *)(lVar2 + 0x10 + lVar6);
    uVar5 = (ulong)((uVar1 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar6));
    lVar4 = (lVar4 + uVar5) - ((long)*(int *)(lVar2 + 0x34 + lVar6) & *(ulong *)(lVar4 + 8 + uVar5))
    ;
    uVar1 = *(uint *)(lVar4 + 0x208);
    if (uVar1 != 0xffffffff) {
      lVar6 = (ulong)(((uint)((int)uVar1 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar1 >> 0xd) * 0x40;
      lVar3 = *(long *)(lVar2 + 0x10 + lVar6);
      uVar5 = (ulong)((uVar1 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar6));
      lVar3 = ((lVar3 + uVar5) -
              ((long)*(int *)(lVar2 + 0x34 + lVar6) & *(ulong *)(lVar3 + 8 + uVar5))) +
              *(long *)(lVar4 + 0x210);
    }
  }
  return lVar3;
}

