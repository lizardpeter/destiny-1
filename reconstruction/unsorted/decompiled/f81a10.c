
void FUN_00f81a10(uint *param_1,uint param_2,uint param_3,uint param_4)

{
  *param_1 = (param_4 & 0x1f) << 8 | (param_3 & 7) << 5 | param_2 & 0x1f | *param_1 & 0xffffe000;
  return;
}

