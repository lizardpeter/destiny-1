
undefined1 FUN_005a9b20(long param_1)

{
  undefined1 uVar1;
  uint uVar2;
  ulong uVar3;
  
  uVar1 = 0;
  if (((*(int *)(param_1 + 0x9c8) != 0) && (*(int *)(param_1 + 0x9c8) != -1)) &&
     (*(int *)(param_1 + 0x9d0) != -1)) {
    uVar2 = FUN_00352ee0(param_1 + 0x9c8);
    if (uVar2 != 0xffffffff) {
      uVar3 = (ulong)((uVar2 & 0x1fff) * DAT_02689800);
      uVar1 = FUN_002f78e0((DAT_026897f8 + uVar3) -
                           ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar3)));
    }
  }
  return uVar1;
}

