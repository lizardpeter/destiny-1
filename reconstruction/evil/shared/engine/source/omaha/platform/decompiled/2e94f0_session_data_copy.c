
void FUN_002e94f0(int *param_1,undefined8 *param_2)

{
  *(undefined2 *)((long)param_2 + 0x4c) = 0;
  *(undefined4 *)(param_2 + 9) = 0;
  param_2[8] = 0;
  param_2[7] = 0;
  param_2[6] = 0;
  param_2[5] = 0;
  param_2[4] = 0;
  param_2[3] = 0;
  param_2[2] = 0;
  param_2[1] = 0;
  *param_2 = 0;
  if (*param_1 == 0x4e) {
    thunk_FUN_012aa7c6(param_2,param_1 + 1,0x4e);
  }
  return;
}

