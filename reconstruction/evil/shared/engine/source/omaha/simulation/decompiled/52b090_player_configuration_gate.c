
ulong FUN_0052b090(void)

{
  int iVar1;
  long lVar2;
  ulong uVar3;
  long lVar4;
  long lVar5;
  
  uVar3 = (ulong)DAT_026b0db0;
  if (DAT_026b0db0 != 0xffffffff) {
    lVar4 = (ulong)(((uint)((int)DAT_026b0db0 >> 0xd) >> 0x12 | 0x3ff) & (int)DAT_026b0db0 >> 0xd) *
            0x40;
    lVar5 = *DAT_01a238a0;
    lVar2 = *(long *)(lVar5 + 0x10 + lVar4);
    uVar3 = (ulong)((DAT_026b0db0 & 0x1fff) * *(int *)(lVar5 + 0x30 + lVar4));
    lVar5 = (lVar2 + uVar3) - ((long)*(int *)(lVar5 + 0x34 + lVar4) & *(ulong *)(lVar2 + 8 + uVar3))
    ;
    if (lVar5 != 0) {
      iVar1 = *(int *)(lVar5 + 0x18);
      return (ulong)CONCAT31((int3)((uint)iVar1 >> 8),iVar1 != -0x7ee3623b);
    }
  }
  return uVar3 & 0xffffffffffffff00;
}

