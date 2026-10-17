
void FUN_00f819f0(uint *param_1,byte param_2)

{
  *param_1 = (uint)param_2 << 0x1e | *param_1 & 0xbfffffff;
  return;
}

