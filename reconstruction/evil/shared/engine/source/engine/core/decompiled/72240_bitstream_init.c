
void FUN_00072240(long *param_1,long param_2,int param_3)

{
  *param_1 = param_2;
  param_1[1] = param_2 + param_3;
  *(int *)(param_1 + 2) = param_3;
  *(undefined1 *)(param_1 + 0x1a) = 1;
  *(undefined4 *)(param_1 + 3) = 0;
  *(undefined4 *)(param_1 + 4) = 0;
  *(undefined4 *)((long)param_1 + 0x24) = 0;
  *(undefined4 *)(param_1 + 8) = 0;
  *(undefined1 *)((long)param_1 + 0x1c) = 0;
  param_1[7] = param_2;
  param_1[5] = 0;
  *(undefined4 *)(param_1 + 6) = 0;
  return;
}

