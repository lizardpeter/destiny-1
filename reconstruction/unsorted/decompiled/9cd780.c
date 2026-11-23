
void FUN_009cd780(undefined8 param_1)

{
  long *plVar1;
  undefined4 local_28 [2];
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  FUN_009438f0();
  local_28[0] = DAT_0274c044;
  FUN_0098a980(local_28,param_1);
  if (*plVar1 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

