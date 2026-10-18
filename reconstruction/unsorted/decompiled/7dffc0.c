
void FUN_007dffc0(undefined8 param_1,long param_2)

{
  long *plVar1;
  undefined1 local_60 [48];
  long local_30;
  
  plVar1 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  FUN_00f826f0(local_60,param_2 + 0xb4,0);
  FUN_00c2e290(local_60,*(ulong *)(param_2 + 0x48) >> 8);
  FUN_007e0040(param_1,param_2 + 0x88,local_60);
  if (*plVar1 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

