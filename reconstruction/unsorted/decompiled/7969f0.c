
void FUN_007969f0(long param_1,undefined8 *param_2)

{
  param_2[2] = 0;
  param_2[1] = 0;
  *param_2 = 0;
  param_2[1] = *(undefined8 *)(param_1 + 0x198);
  param_2[2] = *(ulong *)(param_1 + 0x1a8) ^ *(ulong *)(param_1 + 0x198);
  return;
}

