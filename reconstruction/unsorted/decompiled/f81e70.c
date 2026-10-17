
void FUN_00f81e70(uint *param_1,uint param_2,uint param_3,uint param_4)

{
  *param_1 = (param_4 & 0xf) << 0x14 | (param_3 & 0xf) << 0x10 | (param_2 & 0xf) << 0xc |
             *param_1 & 0xff000fff;
  return;
}

