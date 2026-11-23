
undefined8 FUN_001191e0(uint param_1)

{
  undefined8 uVar1;
  
  if (param_1 == 0xffffffff) {
    return 0;
  }
  uVar1 = FUN_00119210((ulong)((param_1 & 0x1fff) * DAT_02689590) + DAT_02689588);
  return uVar1;
}

