
long FUN_0056dc80(long param_1,int param_2,int param_3)

{
  ulong uVar1;
  
  uVar1 = (ulong)*(uint *)((long)param_3 * 0x10 + 0x4fd90 + (long)param_2 * 0x60 + param_1);
  if (*(long *)(param_1 + 0x40a0 + uVar1) != 0) {
    return param_1 + 0x40a0 + uVar1;
  }
  return 0;
}

