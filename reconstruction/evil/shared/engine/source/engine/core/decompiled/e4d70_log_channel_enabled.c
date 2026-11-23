
undefined8 FUN_000e4d70(int param_1,int param_2)

{
  ulong uVar1;
  
  uVar1 = 5;
  if (DAT_02587bb0 != 0) {
    uVar1 = (ulong)*(uint *)(DAT_02587bb0 + 0x19808 + (long)param_1 * 4);
  }
  return CONCAT71((int7)(uVar1 >> 8),(int)uVar1 <= param_2);
}

