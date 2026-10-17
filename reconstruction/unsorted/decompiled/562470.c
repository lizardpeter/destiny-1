
void FUN_00562470(long param_1,undefined8 param_2,int param_3,undefined8 param_4,int *param_5,
                 undefined8 param_6)

{
  long *plVar1;
  char cVar2;
  undefined1 local_58 [16];
  int local_48;
  long local_38;
  
  plVar1 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  FUN_000a1470(local_58,param_2,(long)param_3);
  cVar2 = FUN_000a2020(local_58,*(undefined8 *)(param_1 + 8),param_6);
  if (cVar2 != '\0') {
    *param_5 = param_3 - local_48;
  }
  if (*plVar1 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

