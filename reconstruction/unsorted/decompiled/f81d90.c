
void FUN_00f81d90(uint *param_1,uint param_2)

{
  *param_1 = (param_2 & 7) << 0x14 | *param_1 & 0xff8fffff;
  return;
}

