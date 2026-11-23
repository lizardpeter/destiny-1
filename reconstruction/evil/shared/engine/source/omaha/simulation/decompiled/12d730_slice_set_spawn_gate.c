
undefined4 FUN_0012d730(uint *param_1)

{
  uint uVar1;
  
  uVar1 = *param_1;
  return CONCAT31((int3)(uVar1 >> 8),(uVar1 & 7) == 0 && uVar1 != 0xffffffff);
}

