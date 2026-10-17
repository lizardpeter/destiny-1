
void FUN_00f81d60(uint *param_1,uint param_2,uint param_3)

{
  *param_1 = *param_1 & 0xffffff8b | (param_3 & 7) << 4 | (param_2 & 1) << 2;
  return;
}

