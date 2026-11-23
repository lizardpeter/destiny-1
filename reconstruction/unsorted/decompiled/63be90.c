
void FUN_0063be90(undefined1 *param_1,uint param_2,int param_3)

{
  short *psVar1;
  long lVar2;
  ulong uVar3;
  
  uVar3 = (ulong)((param_2 & 0x1fff) * *(int *)(param_1 + 0x20));
  lVar2 = *(long *)(param_1 + 0x18);
  if (lVar2 + uVar3 != 0) {
    if (param_3 == 1) {
      psVar1 = (short *)(uVar3 + 0x12a + lVar2);
      *psVar1 = *psVar1 + -1;
    }
    else if (param_3 == 0) {
      psVar1 = (short *)(uVar3 + 0x128 + lVar2);
      *psVar1 = *psVar1 + -1;
    }
    if ((*(short *)(uVar3 + 0x128 + lVar2) == 0) && (*(short *)(uVar3 + 0x12a + lVar2) == 0)) {
      *(undefined1 *)(uVar3 + 0x10c + lVar2) = 1;
      *param_1 = 1;
    }
  }
  return;
}

