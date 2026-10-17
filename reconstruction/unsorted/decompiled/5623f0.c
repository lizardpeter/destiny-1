
void FUN_005623f0(long param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4,int param_5,
                 undefined4 *param_6)

{
  long *plVar1;
  char cVar2;
  undefined1 local_58 [24];
  undefined4 local_40;
  long local_38;
  
  plVar1 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  FUN_000a2c20(local_58,param_4,(long)param_5);
  cVar2 = FUN_000a2c80(local_58,*(undefined8 *)(param_1 + 8),param_3);
  if (cVar2 != '\0') {
    *param_6 = local_40;
  }
  if (*plVar1 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

