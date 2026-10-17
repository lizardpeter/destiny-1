
void FUN_00f81b80(uint *param_1,byte param_2)

{
  *param_1 = (uint)param_2 << 7 | *param_1 & 0xffffff7f;
  return;
}

