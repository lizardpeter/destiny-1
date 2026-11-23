
void FUN_007db260(undefined8 param_1,undefined8 param_2,undefined4 param_3,undefined8 param_4,
                 undefined8 *param_5,undefined8 *param_6,long param_7)

{
  *(undefined8 *)(param_7 + 8) = param_1;
  *(undefined8 *)(param_7 + 0x10) = param_2;
  *(undefined4 *)(param_7 + 0x18) = param_3;
  *(undefined8 *)(param_7 + 0x20) = param_4;
  *(undefined8 *)(param_7 + 0x28) = *param_5;
  *(undefined8 *)(param_7 + 0x30) = *param_6;
  return;
}

