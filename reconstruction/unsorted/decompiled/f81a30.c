
void FUN_00f81a30(uint *param_1,uint param_2,uint param_3,uint param_4)

{
  *param_1 = (param_4 & 0x1f) << 0x18 | (param_3 & 7) << 0x15 | (param_2 & 0x1f) << 0x10 |
             *param_1 & 0xe000ffff;
  return;
}

