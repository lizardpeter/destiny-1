
void FUN_00273e40(undefined8 *param_1,undefined8 param_2)

{
  *param_1 = &PTR_FUN_0190fb60;
  param_1[1] = param_2;
  *(undefined4 *)(param_1 + 2) = 0xffffffff;
  *(undefined1 *)((long)param_1 + 0x14) = 0;
  return;
}

