
undefined4 FUN_00923110(int param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0xffffffff;
  if (param_1 != -1) {
    uVar1 = *(undefined4 *)(DAT_0273eb80 + 8 + (long)param_1 * 4);
  }
  return uVar1;
}

