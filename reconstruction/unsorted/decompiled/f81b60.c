
void FUN_00f81b60(uint *param_1,uint param_2)

{
  *param_1 = *param_1 & 0xffffffbf | (param_2 & 1) << 6;
  return;
}

