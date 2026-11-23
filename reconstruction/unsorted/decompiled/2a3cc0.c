
void FUN_002a3cc0(undefined8 *param_1,undefined8 param_2)

{
  *param_1 = param_2;
  *(undefined4 *)(param_1 + 1) = 0xffffffff;
  return;
}

