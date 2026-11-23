
void FUN_00f81e50(uint *param_1,uint param_2,uint param_3,uint param_4)

{
  *param_1 = (param_4 & 0xf) << 8 | (param_3 & 0xf) << 4 | param_2 & 0xf | *param_1 & 0xfffff000;
  return;
}

