
void FUN_00f81c80(uint *param_1,byte param_2)

{
  uint uVar1;
  
  uVar1 = param_2 ^ 1;
  *param_1 = (uVar1 << 10 | uVar1 << 8 |
             uVar1 << 5 | uVar1 * 8 | uVar1 * 2 | uVar1 << 4 | uVar1 * 4 | uVar1 |
             *param_1 & 0xfffffac0) ^ 0x100;
  return;
}

