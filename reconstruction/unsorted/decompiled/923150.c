
undefined4 FUN_00923150(uint param_1)

{
  uint uVar1;
  undefined4 uVar2;
  ulong uVar3;
  
  uVar2 = 0xffffffff;
  if (param_1 != 0xffffffff) {
    uVar3 = (ulong)((param_1 & 0x1fff) * DAT_02689800);
    uVar3 = (ulong)((*(uint *)(((uVar3 + DAT_026897f8) -
                               (*(ulong *)(DAT_026897f8 + 8 + uVar3) & (long)DAT_02689818)) + 0x68)
                    & 0x1fff) * DAT_02689800);
    uVar1 = *(uint *)(((DAT_026897f8 + uVar3) -
                      ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar3))) + 0x9d8);
    if (uVar1 != 0xffffffff) {
      uVar2 = *(undefined4 *)(DAT_0273eb80 + 0x6c + (ulong)(uVar1 & 0xffff) * 4);
    }
  }
  return uVar2;
}

