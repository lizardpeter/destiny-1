
undefined8 FUN_009237b0(int param_1)

{
  undefined8 uVar1;
  
  if (param_1 == -1) {
    uVar1 = 0;
    if (*(int *)(DAT_0273eb80 + 0xc0) == -1) {
      uVar1 = 0xffffffff;
    }
    return uVar1;
  }
  return 0xffffffff;
}

