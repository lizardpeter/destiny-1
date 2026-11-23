
void FUN_00f81ec0(uint *param_1,uint param_2)

{
  *param_1 = (param_2 & 7) << 8 | *param_1 & 0xfffff8ff;
  return;
}

