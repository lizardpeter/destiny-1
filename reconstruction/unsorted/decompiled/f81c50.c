
void FUN_00f81c50(uint *param_1,uint param_2,uint param_3)

{
  *param_1 = (param_3 & 1) << 0x1b | (param_2 & 1) << 0x1a | *param_1 & 0xf3ffffff;
  return;
}

