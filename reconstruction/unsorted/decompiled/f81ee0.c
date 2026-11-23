
void FUN_00f81ee0(uint *param_1,uint param_2)

{
  *param_1 = (param_2 & 7) << 0xc | *param_1 & 0xffff8fff;
  return;
}

