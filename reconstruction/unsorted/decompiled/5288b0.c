
long FUN_005288b0(void)

{
  long lVar1;
  long lVar2;
  ulong uVar3;
  long lVar4;
  
  FUN_000ae550();
  if (DAT_026b0a4c == 0xffffffff) {
    return 0;
  }
  lVar4 = (ulong)(((uint)((int)DAT_026b0a4c >> 0xd) >> 0x12 | 0x3ff) & (int)DAT_026b0a4c >> 0xd) *
          0x40;
  lVar1 = *DAT_01a238a0;
  lVar2 = *(long *)(lVar1 + 0x10 + lVar4);
  uVar3 = (ulong)((DAT_026b0a4c & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar4));
  return ((lVar2 + uVar3) - ((long)*(int *)(lVar1 + 0x34 + lVar4) & *(ulong *)(lVar2 + 8 + uVar3)))
         + 0x18;
}

