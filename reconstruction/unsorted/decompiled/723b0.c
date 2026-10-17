
void FUN_000723b0(undefined8 *param_1,undefined4 param_2)

{
  *(undefined4 *)((long)param_1 + 0x14) = param_2;
  *(undefined4 *)(param_1 + 3) = 1;
  *(undefined4 *)(param_1 + 4) = 0;
  *(undefined4 *)((long)param_1 + 0x24) = 0;
  *(undefined4 *)(param_1 + 8) = 0;
  *(undefined1 *)((long)param_1 + 0x1c) = 0;
  param_1[7] = *param_1;
  param_1[5] = 0;
  *(undefined4 *)(param_1 + 6) = 0;
  param_1[0x19] = 0;
  return;
}

