
undefined8 FUN_001192b0(uint param_1)

{
  undefined8 uVar1;
  
  if (param_1 == 0xffffffff) {
    return 0;
  }
  uVar1 = FUN_001192e0((ulong)((param_1 & 0x1fff) * DAT_02689590) + DAT_02689588);
  return uVar1;
}

