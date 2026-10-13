
void FUN_0006cf80(long param_1,undefined8 param_2,undefined8 *param_3,char param_4)

{
  FUN_0006cc60();
  *(undefined4 *)(param_1 + 0x1a) = *(undefined4 *)(param_3 + 1);
  *(undefined8 *)(param_1 + 0x12) = *param_3;
  *(undefined4 *)(param_1 + 0x26) = *(undefined4 *)(param_3 + 1);
  *(undefined8 *)(param_1 + 0x1e) = *param_3;
  if (param_4 == '\0') {
    *(byte *)(param_1 + 0x1d) = *(byte *)(param_1 + 0x1d) ^ 1;
  }
  else {
    *(byte *)(param_1 + 0x29) = *(byte *)(param_1 + 0x29) ^ 1;
  }
  return;
}

