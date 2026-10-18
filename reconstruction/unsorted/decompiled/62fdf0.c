
void FUN_0062fdf0(long param_1)

{
  int *piVar1;
  uint uVar2;
  ulong uVar3;
  long lVar4;
  
  lVar4 = DAT_026be8a0;
  piVar1 = (int *)(DAT_026be8a0 + (long)*(int *)(param_1 + 0x2f8) * 4);
  *piVar1 = *piVar1 + -1;
  uVar2 = *(uint *)(lVar4 + 0xc);
  if (uVar2 == *(uint *)(param_1 + 0x24)) {
    *(undefined4 *)(lVar4 + 0xc) = *(undefined4 *)(param_1 + 0x304);
    *(undefined4 *)(param_1 + 0x304) = 0xffffffff;
    return;
  }
  uVar3 = (ulong)((uVar2 & 0x1fff) * DAT_02689800);
  lVar4 = (uVar3 + DAT_026897f8) - (*(ulong *)(DAT_026897f8 + 8 + uVar3) & (long)DAT_02689818);
  uVar2 = *(uint *)(lVar4 + 0x304);
  while( true ) {
    if (uVar2 == 0xffffffff) {
      return;
    }
    if (uVar2 == *(uint *)(param_1 + 0x24)) break;
    uVar3 = (ulong)((*(uint *)(lVar4 + 0x304) & 0x1fff) * DAT_02689800);
    lVar4 = (uVar3 + DAT_026897f8) - (*(ulong *)(DAT_026897f8 + 8 + uVar3) & (long)DAT_02689818);
    uVar2 = *(uint *)(lVar4 + 0x304);
  }
  *(undefined4 *)(lVar4 + 0x304) = *(undefined4 *)(param_1 + 0x304);
  *(undefined4 *)(param_1 + 0x304) = 0xffffffff;
  return;
}

