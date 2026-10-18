
void FUN_00f7e410(uint *param_1,byte param_2)

{
  *param_1 = (uint)param_2 << 0x1d | *param_1 & 0xdfffffff;
  return;
}

