
void FUN_008e3de0(undefined8 *param_1,undefined4 param_2)

{
  *param_1 = &DAT_0194a130;
  thunk_FUN_012aa986(param_1 + 0x2a,0,500);
  *(undefined4 *)(param_1 + 0x69) = param_2;
  *(undefined4 *)((long)param_1 + 0x34c) = 0xffffffff;
  *(undefined1 *)((long)param_1 + 0x354) = 0;
  *(undefined4 *)(param_1 + 0x6a) = 0xffffffff;
  *(undefined4 *)((long)param_1 + 0x344) = 0x3f800000;
  FUN_008deaa0(param_1 + 2);
  param_1[2] = &PTR_FUN_0194a2b0;
  return;
}

