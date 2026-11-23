
void FUN_0055eba0(undefined8 param_1,undefined8 param_2,int param_3,undefined8 param_4,
                 undefined4 *param_5,undefined8 param_6)

{
  long *plVar1;
  char cVar2;
  undefined1 local_50 [32];
  long local_30;
  
  plVar1 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  FUN_000a1470(local_50,param_2,(long)param_3);
  cVar2 = FUN_000a2020(local_50,&DAT_019421b0,param_6);
  if (cVar2 != '\0') {
    *param_5 = 0x2290;
  }
  if (*plVar1 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

