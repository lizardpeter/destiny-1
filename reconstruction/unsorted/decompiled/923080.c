
void FUN_00923080(uint param_1,int param_2)

{
  int iVar1;
  ulong uVar2;
  
  uVar2 = (ulong)(param_1 & 0xffff);
  iVar1 = *(int *)(DAT_0273eb80 + 0x1c + uVar2 * 4);
  if (iVar1 != param_2) {
    if (param_2 == -1) {
      *(undefined4 *)(DAT_0273eb80 + 0xc + (long)iVar1 * 4) = 0xffffffff;
      *(undefined4 *)(DAT_0273eb80 + 0x1c + uVar2 * 4) = 0xffffffff;
      *(short *)(DAT_0273eb80 + 2) = *(short *)(DAT_0273eb80 + 2) + -1;
      return;
    }
    if (iVar1 != -1) {
      *(undefined4 *)(DAT_0273eb80 + 0xc + (long)iVar1 * 4) = 0xffffffff;
      *(undefined4 *)(DAT_0273eb80 + 0x1c + uVar2 * 4) = 0xffffffff;
      *(short *)(DAT_0273eb80 + 2) = *(short *)(DAT_0273eb80 + 2) + -1;
    }
    *(int *)(DAT_0273eb80 + 0x1c + uVar2 * 4) = param_2;
    *(uint *)(DAT_0273eb80 + 0xc + (long)param_2 * 4) = param_1;
    *(short *)(DAT_0273eb80 + 2) = *(short *)(DAT_0273eb80 + 2) + 1;
  }
  return;
}

