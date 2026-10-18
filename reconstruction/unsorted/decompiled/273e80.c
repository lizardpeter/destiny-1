
void FUN_00273e80(long param_1)

{
  long lVar1;
  int iVar2;
  short *psVar3;
  
  iVar2 = *(int *)(param_1 + 0x10) + 1;
  *(int *)(param_1 + 0x10) = iVar2;
  *(undefined1 *)(param_1 + 0x14) = 0;
  lVar1 = *(long *)(param_1 + 8);
  if (iVar2 < *(int *)(lVar1 + 0x3660)) {
    psVar3 = (short *)((long)iVar2 * 0x10 + 0x3670 + lVar1);
    do {
      if (*psVar3 != -1) {
        *(undefined1 *)(param_1 + 0x14) = 1;
        return;
      }
      iVar2 = iVar2 + 1;
      *(int *)(param_1 + 0x10) = iVar2;
      psVar3 = psVar3 + 8;
    } while (iVar2 < *(int *)(lVar1 + 0x3660));
  }
  return;
}

