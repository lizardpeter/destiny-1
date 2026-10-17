
void FUN_00f81dd0(uint *param_1,byte param_2)

{
  *param_1 = (uint)param_2 << 3 | *param_1 & 0xfffffff7;
  return;
}

