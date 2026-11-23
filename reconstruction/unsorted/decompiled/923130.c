
undefined4 FUN_00923130(uint param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0xffffffff;
  if (param_1 != 0xffffffff) {
    uVar1 = *(undefined4 *)(DAT_0273eb80 + 0x6c + (ulong)(param_1 & 0xffff) * 4);
  }
  return uVar1;
}

