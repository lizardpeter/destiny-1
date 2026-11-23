
void FUN_00f81b70(uint *param_1,uint param_2)

{
  *param_1 = *param_1 & 0xffffffdf | (param_2 & 1) << 5;
  return;
}

