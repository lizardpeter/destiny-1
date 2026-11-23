
void FUN_007e16a0(long param_1,undefined4 param_2,undefined4 param_3,undefined8 param_4,
                 undefined4 param_5,undefined8 param_6,undefined4 param_7)

{
  undefined4 extraout_EDX;
  
  if (*(char *)(param_1 + 0x26) != '\0') {
    FUN_00f7f890(*(undefined8 *)(param_1 + 0x50),param_5);
    FUN_007e15d0(param_1,param_2,extraout_EDX,param_7,param_3);
    FUN_00f7f890(*(undefined8 *)(param_1 + 0x50),1);
    return;
  }
  return;
}

