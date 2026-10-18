
void FUN_0055cbf0(undefined8 param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4,
                 int param_5,undefined4 *param_6)

{
  long *plVar1;
  undefined1 local_50 [24];
  undefined4 local_38;
  long local_30;
  
  plVar1 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  FUN_000a2c20(local_50,param_4,(long)param_5);
  FUN_000a2c80(local_50,&DAT_015ba500,param_3);
  *param_6 = local_38;
  if (*plVar1 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

