
void FUN_00f81ad0(uint *param_1,uint param_2,uint param_3)

{
  *param_1 = (param_3 & 1) << 0xc | (param_2 & 1) << 0xb | *param_1 & 0xffffe7ff;
  return;
}

