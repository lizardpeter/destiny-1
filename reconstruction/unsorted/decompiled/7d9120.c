
long FUN_007d9120(ulong param_1,int param_2,long param_3)

{
  uint uVar1;
  long lVar2;
  long lVar3;
  ulong uVar4;
  long lVar5;
  
  if (param_3 != 0) {
    lVar3 = 0;
    do {
      if (((&DAT_015d12c0)[lVar3 * 2] == *(int *)(&DAT_015d10d0 + (param_1 & 0xffffffff) * 4)) &&
         ((&DAT_015d12c4)[lVar3 * 2] == param_2)) {
        if ((int)lVar3 == -1) {
          return 0;
        }
        uVar1 = *(uint *)(param_3 + 8 + lVar3 * 4);
        if (uVar1 == 0xffffffff) {
          return 0;
        }
        lVar5 = (ulong)(((uint)((int)uVar1 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar1 >> 0xd) * 0x40;
        lVar3 = *DAT_01a238a0;
        lVar2 = *(long *)(lVar3 + 0x10 + lVar5);
        uVar4 = (ulong)((uVar1 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar5));
        return (lVar2 + uVar4) -
               ((long)*(int *)(lVar3 + 0x34 + lVar5) & *(ulong *)(lVar2 + 8 + uVar4));
      }
      lVar3 = lVar3 + 1;
    } while ((int)lVar3 < 0x1b);
  }
  return 0;
}

