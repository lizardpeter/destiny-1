
long FUN_00ac5e40(void)

{
  long lVar1;
  uint uVar2;
  ulong uVar3;
  long lVar4;
  long lVar5;
  
  lVar5 = 0;
  if ((DAT_0279d290 != '\0') && (uVar2 = FUN_00ac5790(&DAT_0279d158), uVar2 != 0xffffffff)) {
    lVar4 = (ulong)(((uint)((int)uVar2 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar2 >> 0xd) * 0x40;
    lVar5 = *DAT_01a238a0;
    lVar1 = *(long *)(lVar5 + 0x10 + lVar4);
    uVar3 = (ulong)((uVar2 & 0x1fff) * *(int *)(lVar5 + 0x30 + lVar4));
    lVar5 = (lVar1 + uVar3) - ((long)*(int *)(lVar5 + 0x34 + lVar4) & *(ulong *)(lVar1 + 8 + uVar3))
    ;
  }
  return lVar5;
}

