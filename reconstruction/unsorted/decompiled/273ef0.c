
void FUN_00273ef0(long param_1)

{
  long lVar1;
  short *psVar2;
  int iVar3;
  
  *(undefined4 *)(param_1 + 0x10) = 0;
  *(undefined1 *)(param_1 + 0x14) = 0;
  lVar1 = *(long *)(param_1 + 8);
  if (0 < *(int *)(lVar1 + 0x3660)) {
    psVar2 = (short *)(lVar1 + 0x3670);
    iVar3 = 0;
    do {
      if (*psVar2 != -1) {
        *(undefined1 *)(param_1 + 0x14) = 1;
        return;
      }
      iVar3 = iVar3 + 1;
      *(int *)(param_1 + 0x10) = iVar3;
      psVar2 = psVar2 + 8;
    } while (iVar3 < *(int *)(lVar1 + 0x3660));
  }
  return;
}

