
void FUN_00f81a90(uint *param_1,uint param_2,uint param_3)

{
  *param_1 = *param_1 & 0xfffff807 |
             (uint)(param_3 != 2 || param_2 != 2) << 3 | (param_3 & 7) << 8 | (param_2 & 7) << 5;
  return;
}

