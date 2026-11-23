
void FUN_00f81b30(uint *param_1,byte param_2)

{
  *param_1 = *param_1 & 0xfffffffe | (uint)param_2;
  return;
}

