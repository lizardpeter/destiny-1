
void FUN_00f81b40(uint *param_1,byte param_2)

{
  *param_1 = (uint)param_2 * 2 | *param_1 & 0xfffffffd;
  return;
}

